"""
Fund IRR Service.
"""

from typing import Optional, List, Tuple
from datetime import date
from sqlalchemy.orm import Session

from src.shared.calculations.irr_calculator import IRRCalculator
from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.fund.enums.fund_enums import FundStatus
from src.fund.repositories import FundEventRepository


class FundIrRService:
    """
    Fund IRR Service.

    This module provides the FundIrRService class, which handles fund IRR operations and business logic.
    The service provides clean separation of concerns for:
    - Update the IRRs of a fund
        - Update the completed IRRs of a fund
        - Update the completed after-tax IRRs of a fund
        - Update the completed real IRRs of a fund
    - Calculate the completed IRRs of a fund
    - Calculate the completed after-tax IRRs of a fund
    - Calculate the completed real IRRs of a fund

    The service uses the FundEventRepository and IRRCalculator to perform operations.
    The service is used by the FundEventSecondaryService to update the IRRs of a fund.
    """
    
    def __init__(self):
        """
        Initialize the FundIrRService.
        
        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            irr_calculator: IRR calculator to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.irr_calculator = IRRCalculator()

    def update_irrs(self, fund: Fund, session: Optional[Session] = None) -> Optional[List[FundFieldChange]]:
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
            
        elif fund.status == FundStatus.REALIZED:
            # REALIZED: Only gross IRR is meaningful (all capital returned)
            fund.completed_irr_gross = self.calculate_completed_irr(fund, session)
            fund.completed_irr_after_tax = None  # Not meaningful until completed
            fund.completed_irr_real = None       # Not meaningful until completed

        elif fund.status == FundStatus.COMPLETED:
            # COMPLETED: All IRRs are meaningful (tax obligations complete)
            fund.completed_irr_gross = self.calculate_completed_irr(fund, session)
            fund.completed_irr_after_tax = self.calculate_completed_after_tax_irr(fund, session)
            fund.completed_irr_real = self.calculate_completed_real_irr(fund, session)

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
        
        events = self.fund_event_repository.get_fund_events(session, fund.id)
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
        
        events = self.fund_event_repository.get_fund_events(session, fund.id)
        return self._calculate_irr_base(
            events,
            fund.start_date,
            include_tax_payments=True,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
    
    def calculate_completed_real_irr(self, fund: Fund, session: Session) -> Optional[float]:
        """
        Calculate the completed real IRR for the fund.
        
        Only calculates for COMPLETED funds as per business rules.
        
        Args:
            fund: The fund object
            session: Database session for data access
            
        Returns:
            float or None: The completed real IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.COMPLETED]:
            return None
        
        events = self.fund_event_repository.get_fund_events(session, fund.id)
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
            is_valid = self.irr_calculator.validate_cash_flows(cash_flows, days_from_start)
            
            if not is_valid:
                return None
            
            # Calculate IRR using shared calculator
            return self.irr_calculator.calculate_irr(cash_flows, days_from_start)
            
        except Exception as e:
            raise ValueError(f"Error calculating IRR: {e}")
    
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
    