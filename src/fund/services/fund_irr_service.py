"""
Fund IRR Service.

This service handles IRR calculations for funds, providing a clean interface
between the pure calculation logic and business operations.

Key principles:
- Stateless service with no session management
- Uses shared IRRCalculator for pure calculation math
- Provides orchestration for complex IRR workflows
- Manages risk-free rate charges and tax calculations
- Delegates database operations to repositories
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from sqlalchemy.orm import Session

from src.shared.calculations.irr_calculator import IRRCalculator
from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums import EventType, FundStatus

logger = logging.getLogger(__name__)


class FundIrRService:
    """
    Service for handling IRR calculations.
    
    This service provides a clean interface for IRR calculations,
    delegating database operations to repositories and maintaining
    stateless operation for better testability and composability.
    """
    
    def __init__(self):
        """
        Initialize the FundIrRService.
        
        This service is stateless and does not store database sessions.
        """
        pass

    def update_irrs(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[List[FundFieldChange]]:
        """
        Calculate and store IRRs for a specific fund status.
                
        Args:
            fund: The fund object
            session: Database session (optional)
        """
        old_completed_irr_gross = fund.completed_irr_gross
        old_completed_irr_after_tax = fund.completed_irr_after_tax
        old_completed_irr_real = fund.completed_irr_real
        
        if fund.status == FundStatus.ACTIVE:
            # ACTIVE: No IRRs meaningful (fund has capital at risk)
            fund.completed_irr_gross = None
            fund.completed_irr_after_tax = None
            fund.completed_irr_real = None
            logger.info(f"IRRs reset to None for active fund {fund.name}")
            
        elif fund.status == FundStatus.REALIZED:
            # REALIZED: Only gross IRR is meaningful (all capital returned)
            fund.completed_irr_gross = self.calculate_completed_irr(fund, session)
            fund.completed_irr_after_tax = None  # Not meaningful until completed
            fund.completed_irr_real = None       # Not meaningful until completed
            logger.info(f"IRR Gross calculated and stored for realized fund {fund.name}")

        elif fund.status == FundStatus.COMPLETED:
            # COMPLETED: All IRRs are meaningful (tax obligations complete)
            fund.completed_irr_gross = self.calculate_completed_irr(fund, session)
            fund.completed_irr_after_tax = self.calculate_completed_after_tax_irr(fund, session)
            fund.completed_irr_real = self.calculate_completed_real_irr(fund, session)
            logger.info(f"All IRRs calculated and stored for completed fund {fund.name}")

        irr_changes = []
        if old_completed_irr_gross != fund.completed_irr_gross:
            irr_changes.append(FundFieldChange(field_name='completed_irr_gross', old_value=old_completed_irr_gross, new_value=fund.completed_irr_gross))
        if old_completed_irr_after_tax != fund.completed_irr_after_tax:
            irr_changes.append(FundFieldChange(field_name='completed_irr_after_tax', old_value=old_completed_irr_after_tax, new_value=fund.completed_irr_after_tax))
        if old_completed_irr_real != fund.completed_irr_real:
            irr_changes.append(FundFieldChange(field_name='completed_irr_real', old_value=old_completed_irr_real, new_value=fund.completed_irr_real))
        return irr_changes if irr_changes else None
    
    # ============================================================================
    # CORE IRR CALCULATION METHODS
    # ============================================================================
    
    def calculate_completed_irr(self, fund: Fund, session: Session) -> Optional[float]:
        """
        Calculate the completed pre-tax IRR for the fund using all relevant cash flows.
        
        Only calculates for REALIZED and COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            session: Database session for data access
            
        Returns:
            float or None: The completed pre-tax IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return None
        
        events = self._get_fund_events(fund, session)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=False,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
    
    def calculate_completed_after_tax_irr(self, fund: Fund, session: Session) -> Optional[float]:
        """
        Calculate the completed after-tax IRR for the fund.
        
        Only calculates for COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            session: Database session for data access
            
        Returns:
            float or None: The completed after-tax IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.COMPLETED]:
            return None
        
        events = self._get_fund_events(fund, session)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=True,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
    
    def calculate_completed_real_irr(self, fund: Fund, session: Session, risk_free_rate_currency: Optional[str] = None) -> Optional[float]:
        """
        Calculate the completed real IRR for the fund.
        
        Only calculates for COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            session: Database session for data access
            risk_free_rate_currency: Currency for risk-free rate calculations
            
        Returns:
            float or None: The completed real IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.COMPLETED]:
            return None
        
        events = self._get_fund_events(fund, session)
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
            is_valid = IRRCalculator.validate_cash_flows(cash_flows, days_from_start)
            
            if not is_valid:
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
    # DATABASE OPERATIONS
    # ============================================================================    
    
    def _get_fund_events(self, fund: Fund, session: Session) -> List[FundEvent]:
        """
        Get all events for a fund from the database in chronological order.
        
        Args:
            fund: The fund to get events for
            session: Database session for data access
            
        Returns:
            List[FundEvent]: List of fund events sorted by date (ascending)
        """
        from src.fund.repositories import FundEventRepository
        from src.shared.enums import SortOrder
        event_repository = FundEventRepository()
        return event_repository.get_by_fund(fund.id, session, sort_order=SortOrder.ASC)