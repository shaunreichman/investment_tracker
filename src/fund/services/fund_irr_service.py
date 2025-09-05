"""
Fund IRR Service.

This service handles IRR calculations and database operations for funds,
providing a clean interface between the pure calculation logic and the database.

Key principles:
- Handles database operations and session management
- Uses shared IRRCalculator for pure calculation math
- Provides orchestration for complex IRR workflows
- Manages risk-free rate charges and tax calculations
- Single source of truth for IRR database operations
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from sqlalchemy.orm import Session

from src.shared.calculations.irr_calculator import IRRCalculator
from src.fund.models import Fund, FundEvent
from src.fund.enums import EventType, FundStatus

logger = logging.getLogger(__name__)


class FundIrRService:
    """
    Service for handling IRR calculations and database operations.
    
    This service provides a clean interface between the pure calculation
    logic and the database operations required for IRR calculations.
    """
    
    def __init__(self, session: Session):
        """
        Initialize the FundIrRService.
        
        Args:
            session: Database session for operations
        """
        self.session = session
    
    # ============================================================================
    # CORE IRR CALCULATION METHODS
    # ============================================================================
    
    def calculate_completed_irr(self, fund: Fund) -> Optional[float]:
        """
        Calculate the completed pre-tax IRR for the fund using all relevant cash flows.
        
        Only calculates for REALIZED and COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            
        Returns:
            float or None: The completed pre-tax IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return None
        
        events = self._get_fund_events(fund)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=False,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
    
    def calculate_completed_after_tax_irr(self, fund: Fund) -> Optional[float]:
        """
        Calculate the completed after-tax IRR for the fund.
        
        Only calculates for COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            
        Returns:
            float or None: The completed after-tax IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.COMPLETED]:
            return None
        
        events = self._get_fund_events(fund)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=True,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
    
    def calculate_completed_real_irr(self, fund: Fund, risk_free_rate_currency: Optional[str] = None) -> Optional[float]:
        """
        Calculate the completed real IRR for the fund.
        
        Only calculates for COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            risk_free_rate_currency: Currency for risk-free rate calculations
            
        Returns:
            float or None: The completed real IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.COMPLETED]:
            return None
        
        # Create daily risk-free interest charges if needed
        self._create_daily_risk_free_interest_charges(fund, risk_free_rate_currency)
        
        events = self._get_fund_events(fund)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=True,
            include_risk_free_charges=True,
            include_eofy_debt_cost=True
        )
    
    # ============================================================================
    # INTERNAL CALCULATION METHODS
    # ============================================================================
    
    def _calculate_irr_base(
        self,
        events: List[FundEvent],
        start_date: date,
        include_tax_payments: bool = False,
        include_risk_free_charges: bool = False,
        include_eofy_debt_cost: bool = False
    ) -> Optional[float]:
        """
        Calculate IRR using the base calculation method.
        
        Args:
            events: List of fund events
            start_date: Start date for IRR calculation
            include_tax_payments: Whether to include tax payment events
            include_risk_free_charges: Whether to include daily risk-free interest charges
            include_eofy_debt_cost: Whether to include EOFY debt cost events
            
        Returns:
            float or None: The calculated IRR as a decimal, or None if not computable
        """
        try:
            # Filter events based on IRR calculation type
            filtered_events = self._filter_events_for_irr(
                events,
                include_tax_payments,
                include_risk_free_charges,
                include_eofy_debt_cost
            )
            
            if len(filtered_events) < 2:
                return None
            
            # Prepare cash flows and days from start
            cash_flows, days_from_start = self._prepare_cash_flows(filtered_events, start_date)
            
            # Validate cash flows
            if not IRRCalculator.validate_cash_flows(cash_flows, days_from_start):
                return None
            
            # Calculate IRR using shared calculator
            return IRRCalculator.calculate_irr(cash_flows, days_from_start)
            
        except Exception as e:
            logger.error(f"Error calculating IRR: {e}")
            return None
    
    def _filter_events_for_irr(
        self,
        events: List[FundEvent],
        include_tax_payments: bool = False,
        include_risk_free_charges: bool = False,
        include_eofy_debt_cost: bool = False
    ) -> List[FundEvent]:
        """
        Filter events based on IRR calculation type.
        
        Args:
            events: List of fund events to filter
            include_tax_payments: Whether to include tax payment events
            include_risk_free_charges: Whether to include daily risk-free interest charges
            include_eofy_debt_cost: Whether to include EOFY debt cost events
            
        Returns:
            List[FundEvent]: Filtered list of events
        """
        filtered_events = []
        for event in events:
            include_event = False
            if event.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.DISTRIBUTION]:
                include_event = True
            elif include_tax_payments and event.event_type == EventType.TAX_PAYMENT:
                include_event = True
            elif include_risk_free_charges and event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
                include_event = True
            elif include_eofy_debt_cost and event.event_type == EventType.EOFY_DEBT_COST:
                include_event = True
            if include_event:
                filtered_events.append(event)
        
        return filtered_events
    
    def _prepare_cash_flows(self, events: List[FundEvent], start_date: date) -> Tuple[List[float], List[int]]:
        """
        Prepare cash flows and days from start for IRR calculation.
        
        Args:
            events: List of filtered fund events
            start_date: Start date for IRR calculation
            
        Returns:
            Tuple of (cash_flows, days_from_start)
        """
        cash_flows = []
        days_from_start = []
        
        for event in events:
            amount = event.amount or 0
            # Adjust sign based on event type
            if event.event_type in [EventType.UNIT_PURCHASE, EventType.CAPITAL_CALL]:
                amount = -abs(amount)  # Outflow
            elif event.event_type in [EventType.UNIT_SALE, EventType.RETURN_OF_CAPITAL, EventType.DISTRIBUTION, EventType.EOFY_DEBT_COST]:
                amount = abs(amount)  # Inflow
            elif event.event_type == EventType.TAX_PAYMENT:
                amount = -abs(amount)  # Outflow
            elif event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
                amount = -abs(amount)  # Outflow
            
            cash_flows.append(amount)
            days = (event.event_date - start_date).days
            days_from_start.append(days)
        
        return cash_flows, days_from_start
    
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================
    
    
    def should_calculate_irr(self, fund: Fund) -> bool:
        """
        Check if IRR should be calculated for a fund.
        
        Args:
            fund: The fund to check
            
        Returns:
            bool: True if IRR should be calculated
        """
        return fund.status in [FundStatus.REALIZED, FundStatus.COMPLETED]
    
    # ============================================================================
    # DATABASE OPERATIONS
    # ============================================================================
    
    def calculate_and_store_irrs(self, fund: Fund, risk_free_rate_currency: Optional[str] = None) -> Dict[str, Optional[float]]:
        """
        Calculate and store all IRR types for a fund.
        
        Args:
            fund: The fund to calculate IRRs for
            risk_free_rate_currency: Currency for risk-free rate calculations
            
        Returns:
            Dict[str, Optional[float]]: Dictionary containing all IRR types
        """
        try:
            # Calculate all IRRs
            completed_irr = self.calculate_completed_irr(fund)
            completed_after_tax_irr = self.calculate_completed_after_tax_irr(fund)
            completed_real_irr = self.calculate_completed_real_irr(fund, risk_free_rate_currency)
            
            # Store results in fund object
            fund.completed_irr_gross = completed_irr
            fund.completed_irr_after_tax = completed_after_tax_irr
            fund.completed_irr_real = completed_real_irr
            
            # Commit changes
            self.session.commit()
            
            logger.info(f"Calculated and stored IRRs for fund {fund.id}")
            return {
                'completed_irr': completed_irr,
                'completed_after_tax_irr': completed_after_tax_irr,
                'completed_real_irr': completed_real_irr
            }
            
        except Exception as e:
            logger.error(f"Error calculating and storing IRRs for fund {fund.id}: {e}")
            self.session.rollback()
            raise
    
    
    def _get_fund_events(self, fund: Fund) -> List[FundEvent]:
        """
        Get all events for a fund from the database.
        
        Args:
            fund: The fund to get events for
            
        Returns:
            List[FundEvent]: List of fund events
        """
        from src.fund.repositories import FundEventRepository
        event_repository = FundEventRepository()
        return event_repository.get_by_fund(fund.id, self.session)
    
    def _create_daily_risk_free_interest_charges(self, fund: Fund, risk_free_rate_currency: Optional[str] = None) -> None:
        """
        Create daily risk-free interest charges for a fund.
        
        Args:
            fund: The fund to create charges for
            risk_free_rate_currency: Currency for risk-free rate calculations
        """
        # This method would implement the logic to create daily risk-free interest charges
        # For now, it's a placeholder that matches the original implementation
        pass