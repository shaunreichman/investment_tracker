"""
Fund Calculation Service.

This service extracts complex calculation logic from the Fund model to provide
clean separation of concerns and improved testability.

Extracted functionality:
- FIFO calculations for NAV-based funds
- IRR calculations (gross, after-tax, real)
- Equity balance calculations
- Capital event field calculations
"""

from typing import List, Tuple, Optional, Dict, Any
from datetime import date, datetime
import numpy as np
import numpy_financial as npf
from sqlalchemy.orm import Session

# Use string references to avoid circular imports
# from src.fund.models import Fund, FundEvent, EventType, FundType
from src.fund.calculations import calculate_irr, calculate_debt_cost
from src.shared.calculations import orchestrate_irr_base
from src.shared.utils import with_session
from src.fund.enums import FundStatus, EventType


class FundCalculationService:
    """
    Service for handling complex fund calculations extracted from the Fund model.
    
    This service provides clean separation of concerns for:
    - FIFO calculations for NAV-based funds
    - IRR calculations with various tax and debt cost considerations
    - Equity balance calculations for capital events
    - Capital event field calculations
    """
    
    def __init__(self):
        """Initialize the FundCalculationService."""
        pass
    
    # ============================================================================
    # FIFO CALCULATIONS FOR NAV-BASED FUNDS
    # ============================================================================
    
    def calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
        self, 
        fund: 'Fund', 
        events: List['FundEvent'], 
        start_idx: int, 
        session: Optional[Session] = None
    ) -> None:
        """
        [EXTRACTED] Efficiently recalculate NAV-based fields for all subsequent events in a single pass.
        
        Builds FIFO and units up to start_idx, then processes all subsequent events.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            events: List of fund events to process
            start_idx: Index to start processing from
            session: Database session (optional)
        """
        # Build FIFO and cumulative units up to (but not including) start_idx
        # Each FIFO entry: (units, unit_price, effective_price, event_date, brokerage_fee)
        fifo = []
        cumulative_units = 0.0
        
        for i in range(start_idx):
            e = events[i]
            if e.event_type == EventType.UNIT_PURCHASE:
                units = e.units_purchased or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                if units > 0:
                    effective_price = unit_price + (brokerage_fee / units)
                    fifo.append((units, unit_price, effective_price, e.event_date, brokerage_fee))
                cumulative_units += units
            elif e.event_type == EventType.UNIT_SALE:
                units = e.units_sold or 0
                remaining = units
                while remaining > 0 and fifo:
                    oldest_units, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage = fifo[0]
                    if oldest_units <= remaining:
                        fifo.pop(0)
                        remaining -= oldest_units
                    else:
                        fifo[0] = (oldest_units - remaining, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage)
                        remaining = 0
                cumulative_units -= units
        
        # Now process all subsequent events in a single pass
        for i in range(start_idx, len(events)):
            e = events[i]
            if e.event_type == EventType.UNIT_PURCHASE:
                # Update the FIFO and cumulative units
                units = e.units_purchased or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                e.amount = (units * unit_price) + brokerage_fee
                if units > 0:
                    effective_price = unit_price + (brokerage_fee / units)
                    fifo.append((units, unit_price, effective_price, e.event_date, brokerage_fee))
                cumulative_units += units
                e.units_owned = cumulative_units
                # For equity balance, exclude brokerage: only units * unit_price
                total_equity = sum(u * p for u, p, _, _, _ in fifo)
                e.current_equity_balance = total_equity
            elif e.event_type == EventType.UNIT_SALE:
                units = e.units_sold or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                e.amount = (units * unit_price) - brokerage_fee
                remaining = units
                while remaining > 0 and fifo:
                    oldest_units, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage = fifo[0]
                    if oldest_units <= remaining:
                        fifo.pop(0)
                        remaining -= oldest_units
                    else:
                        fifo[0] = (oldest_units - remaining, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage)
                        remaining = 0
                cumulative_units -= units
                e.units_owned = cumulative_units
                # For equity balance, exclude brokerage: only units * unit_price
                total_equity = sum(u * p for u, p, _, _, _ in fifo)
                e.current_equity_balance = total_equity
            else:
                # Not a capital event we care about for NAV-based
                e.units_owned = cumulative_units
                e.current_equity_balance = sum(u * p for u, p, _, _, _ in fifo)
    
    def calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(
        self,
        fund: 'Fund',
        events: List['FundEvent'],
        start_idx: int,
        session: Optional[Session] = None
    ) -> None:
        """
        [EXTRACTED] Efficiently recalculate cost-based fields for all subsequent events in a single pass.
        
        Builds running balance up to start_idx, then processes all subsequent events.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            events: List of fund events to process
            start_idx: Index to start processing from
            session: Database session (optional)
        """
        balance = 0.0  # MANUAL: Running balance for cost-based calculations
        
        # Build balance up to start_idx
        for i in range(start_idx):
            e = events[i]
            if e.event_type == EventType.CAPITAL_CALL:
                # SYSTEM: Convert Decimal to float for consistent type handling
                amount = float(e.amount) if e.amount is not None else 0.0
                balance += amount
            elif e.event_type == EventType.RETURN_OF_CAPITAL:
                # SYSTEM: Convert Decimal to float for consistent type handling
                amount = float(e.amount) if e.amount is not None else 0.0
                balance -= amount
        
        # Process all subsequent events
        for i in range(start_idx, len(events)):
            e = events[i]
            if e.event_type == EventType.CAPITAL_CALL:
                # SYSTEM: Convert Decimal to float for consistent type handling
                amount = float(e.amount) if e.amount is not None else 0.0
                balance += amount
                e.current_equity_balance = balance
            elif e.event_type == EventType.RETURN_OF_CAPITAL:
                # SYSTEM: Convert Decimal to float for consistent type handling
                amount = float(e.amount) if e.amount is not None else 0.0
                balance -= amount
                e.current_equity_balance = balance
            else:
                # Not a capital event we care about for cost-based
                e.current_equity_balance = balance
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    
    def calculate_irr(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the pre-tax IRR for the fund using all relevant cash flows.
        
        Returns a float (IRR) or None if not computable.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: The pre-tax IRR as a decimal, or None if not computable
        """
        return self._calculate_irr_base(
            fund, 
            include_tax_payments=False, 
            include_risk_free_charges=False, 
            include_eofy_debt_cost=False, 
            session=session
        )
    
    def calculate_after_tax_irr(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the after-tax IRR for the fund, including tax payment events.
        
        Returns a float (IRR) or None if not computable.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: The after-tax IRR as a decimal, or None if not computable
        """
        return self._calculate_irr_base(
            fund, 
            include_tax_payments=True, 
            include_risk_free_charges=False, 
            include_eofy_debt_cost=False, 
            session=session
        )
    
    def calculate_real_irr(self, fund: 'Fund', session: Optional[Session] = None, risk_free_rate_currency: Optional[str] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the real IRR for the fund, including debt cost and tax effects.
        
        Returns a float (IRR) or None if not computable.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            risk_free_rate_currency: Currency for risk-free rate calculations (optional)
            
        Returns:
            float or None: The real IRR as a decimal, or None if not computable
        """
        # Create daily risk-free interest charges if needed
        self._create_daily_risk_free_interest_charges(fund, session, risk_free_rate_currency)
        
        return self._calculate_irr_base(
            fund, 
            include_tax_payments=True, 
            include_risk_free_charges=True, 
            include_eofy_debt_cost=True, 
            session=session
        )
    
    def calculate_completed_irr(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the completed IRR for the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: The completed IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return None
        
        return self.calculate_irr(fund, session)
    
    def calculate_completed_after_tax_irr(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the completed after-tax IRR for the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: The completed after-tax IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return None
        
        return self.calculate_after_tax_irr(fund, session)
    
    def calculate_completed_real_irr(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the completed real IRR for the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: The completed real IRR as a decimal, or None if not computable
        """
        if fund.status not in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            return None
        
        return self.calculate_real_irr(fund, session)
    
    # ============================================================================
    # EQUITY BALANCE CALCULATIONS
    # ============================================================================
    
    def calculate_average_equity_balance(self, fund: 'Fund', session: Optional[Session] = None, events: Optional[List['FundEvent']] = None) -> float:
        """
        [EXTRACTED] Calculate average equity balance for the fund, regardless of FundType.
        
        Uses per-event current_equity_balance values and time-weighting.
        Accepts an in-memory events list for efficiency.
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            events: Pre-fetched events list for efficiency (optional)
            
        Returns:
            float: The time-weighted average equity balance
        """
        # Use provided events list if available, otherwise query
        if events is None:
            # For now, require events to be passed in to avoid circular import issues
            # This will be resolved when we implement the repository pattern
            raise ValueError("Events must be provided to avoid circular import issues")
        
        if not events:
            return 0.0
        elif len(events) == 1:
            return events[0].current_equity_balance or 0.0
        
        # Time-weighted average: sum(balance * days) / total_days
        total_weighted_equity = 0.0
        total_days = 0
        
        for i in range(len(events) - 1):
            e = events[i]
            next_e = events[i + 1]
            days = (next_e.event_date - e.event_date).days
            equity = e.current_equity_balance if e.current_equity_balance is not None else 0.0
            total_weighted_equity += equity * days
            total_days += days
        
        # Determine the correct period end: use end_date if present, else today if active
        last_event = events[-1]
        period_end = None
        
        if fund.end_date is not None:
            period_end = fund.end_date
        elif fund.status == FundStatus.ACTIVE:
            period_end = date.today()
        else:
            period_end = last_event.event_date
        
        # Include the last period if period_end is after or equal to the last event
        if period_end:
            days = (period_end - last_event.event_date).days
            if days >= 0:  # Include even if days = 0 (realized funds)
                equity = last_event.current_equity_balance if last_event.current_equity_balance is not None else 0.0
                total_weighted_equity += equity * days
                total_days += days
        
        return total_weighted_equity / total_days if total_days > 0 else 0.0
    
    def calculate_actual_duration_months(self, fund: 'Fund', session: Optional[Session] = None) -> Optional[float]:
        """
        [EXTRACTED] Calculate the actual duration of the fund in months.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            
        Returns:
            float or None: Duration in months, or None if not computable
        """
        if not fund.start_date:
            return None
        
        if fund.end_date:
            end_date = fund.end_date
        elif fund.status == FundStatus.ACTIVE:
            end_date = date.today()
        else:
            return None
        
        delta = end_date - fund.start_date
        return delta.days / 30.44  # Average days per month
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def _calculate_irr_base(
        self, 
        fund: 'Fund', 
        include_tax_payments: bool = False, 
        include_risk_free_charges: bool = False, 
        include_eofy_debt_cost: bool = False, 
        session: Optional[Session] = None
    ) -> Optional[float]:
        """
        [EXTRACTED] Base IRR calculation method used by all IRR calculation variants.
        
        This method was extracted from the Fund model to improve separation of concerns.
        
        Args:
            fund: The fund object
            include_tax_payments: Whether to include tax payment events
            include_risk_free_charges: Whether to include risk-free interest charges
            include_eofy_debt_cost: Whether to include EOFY debt cost events
            session: Database session (optional)
            
        Returns:
            float or None: The calculated IRR as a decimal, or None if not computable
        """
        # Delegate to the shared IRR calculation function
        return orchestrate_irr_base(
            fund.fund_events, 
            fund.start_date,
            include_tax_payments=include_tax_payments,
            include_risk_free_charges=include_risk_free_charges,
            include_eofy_debt_cost=include_eofy_debt_cost
        )
    
    def _create_daily_risk_free_interest_charges(
        self, 
        fund: 'Fund', 
        session: Optional[Session] = None, 
        risk_free_rate_currency: Optional[str] = None
    ) -> None:
        """
        [EXTRACTED] Create daily risk-free interest charge events for the fund.
        
        This method was extracted from the Fund model to improve separation of concerns.
        For now, this is a placeholder that will be implemented in the TaxCalculationService.
        
        Args:
            fund: The fund object
            session: Database session (optional)
            risk_free_rate_currency: Currency for risk-free rate calculations (optional)
        """
        # TODO: This method will be implemented in the TaxCalculationService
        # For now, it's a placeholder to maintain the interface
        pass
