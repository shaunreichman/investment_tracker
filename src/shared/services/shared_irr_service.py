"""
Shared IRR Service.
"""

from typing import Optional, List, Tuple

from src.shared.calculators.irr_calculator import IRRCalculator
from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType


class SharedIrRService:
    """
    Shared IRR Service.
    This service is used to calculate the IRR for a fund or company.

    It delegates the actual calculation to the IRRCalculator class.
    """
    def __init__(self):
        """
        Initialize the SharedIrRService.

        Args:
            irr_calculator: IRR calculator to use. If None, creates a new one.
        """
        self.irr_calculator = IRRCalculator()


    def calculate_irr_base(
        self,
        events: List[FundEvent],
        include_tax_payments: bool = False,
        include_risk_free_charges: bool = False,
        include_eofy_debt_cost: bool = False
    ) -> Optional[float]:
        """
        Calculate IRR using the base calculation method.
        
        Args:
            events: List of fund events sorted by event date
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
            cash_flows, days_from_start = self._prepare_cash_flows(filtered_events)
            
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
    
    def _prepare_cash_flows(self, events: List[FundEvent]) -> Tuple[List[float], List[int]]:
        """
        Prepare cash flows and days from start for IRR calculation.
        
        Args:
            events: List of filtered fund events
            
        Returns:
            Tuple of (cash_flows, days_from_start)
        """
        cash_flows = []
        days_from_start = []

        start_date = events[0].event_date
        
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
    