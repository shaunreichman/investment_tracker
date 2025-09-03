"""
Fund Equity Calculator.

This module provides pure calculation logic for fund equity operations,
including current equity balance, average equity balance, and cost basis calculations.

Key principles:
- Pure functions with no side effects
- Reusable across handlers, services, and other components
- Single source of truth for equity calculations
- Easy to unit test and maintain
"""

from typing import Optional
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent
from src.fund.enums import EventType, FundType
from src.fund.services.fund_calculation_service import FundCalculationService


class FundEquityCalculator:
    """
    Pure calculation logic for fund equity operations.
    
    This class provides static methods for calculating fund equity metrics
    without any side effects. All calculations are based on the current
    state of the fund and its events.
    """
    
    # ============================================================================
    # CURRENT EQUITY CALCULATION
    # ============================================================================
    
    @staticmethod
    def calculate_current_equity(fund: Fund, session: Session) -> float:
        """
        Calculate current equity balance based on fund type.
        
        Args:
            fund: The fund to calculate equity for
            session: Database session
            
        Returns:
            Current equity balance (cost-based: capital calls - returns, NAV-based: FIFO cost base)
        """
        if fund.tracking_type == FundType.COST_BASED:
            return FundEquityCalculator._calculate_cost_based_current_equity(fund, session)
        elif fund.tracking_type == FundType.NAV_BASED:
            return FundEquityCalculator._calculate_nav_based_current_equity(fund, session)
        else:
            raise ValueError(f"Unsupported fund type: {fund.tracking_type}")
    
    @staticmethod
    def _calculate_cost_based_current_equity(fund: Fund, session: Session) -> float:
        """
        Calculate current equity balance for cost-based funds.
        
        This method calculates the current equity balance by summing
        all capital calls and subtracting all capital returns.
        
        Args:
            fund: The fund to calculate equity for
            session: Database session
            
        Returns:
            Current equity balance (capital calls - capital returns)
        """
        capital_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        total_calls = sum(
            e.amount or 0.0 
            for e in capital_events 
            if e.event_type == EventType.CAPITAL_CALL
        )
        
        total_returns = sum(
            e.amount or 0.0 
            for e in capital_events 
            if e.event_type == EventType.RETURN_OF_CAPITAL
        )
        
        return total_calls - total_returns
    
    @staticmethod
    def _calculate_nav_based_current_equity(fund: Fund, session: Session) -> float:
        """
        Calculate current equity balance for NAV-based funds (FIFO cost base).
        
        This method calculates the FIFO cost base of units still owned,
        which represents the current equity balance for NAV-based funds.
        
        Args:
            fund: The fund to calculate equity for
            session: Database session
            
        Returns:
            Current equity balance (FIFO cost base of units still owned)
        """
        # Get all unit purchase and sale events
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        if not unit_events:
            return 0.0
        
        # Use FIFO method to calculate cost base of remaining units
        from collections import deque
        
        available_units = deque()  # Each entry: (units, cost_per_unit)
        current_units_owned = 0.0
        
        for event in unit_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                units = event.units_purchased or 0.0
                unit_price = event.unit_price or 0.0
                brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
                
                if units > 0 and unit_price > 0:
                    # Calculate cost per unit including brokerage
                    cost_per_unit = unit_price + (brokerage_fee / units)
                    available_units.append((units, cost_per_unit))
                    current_units_owned += units
                    
            elif event.event_type == EventType.UNIT_SALE:
                units_sold = event.units_sold or 0.0
                
                if units_sold > 0:
                    remaining_units_to_sell = units_sold
                    current_units_owned -= units_sold
                    
                    # Process sale using FIFO
                    while remaining_units_to_sell > 0 and available_units:
                        available_units_count, cost_per_unit = available_units[0]
                        units_from_this_purchase = min(remaining_units_to_sell, available_units_count)
                        remaining_units_to_sell -= units_from_this_purchase
                        
                        # Update or remove from available units
                        if units_from_this_purchase == available_units_count:
                            available_units.popleft()
                        else:
                            available_units[0] = (available_units_count - units_from_this_purchase, cost_per_unit)
        
        # Calculate total cost base of remaining units
        total_cost_base = 0.0
        for units, cost_per_unit in available_units:
            total_cost_base += units * cost_per_unit
            
        return total_cost_base
    
    
    # ============================================================================
    # AVERAGE EQUITY CALCULATION
    # ============================================================================
    
    @staticmethod
    def calculate_average_equity(fund: Fund, session: Session) -> float:
        """
        Calculate time-weighted average equity balance based on fund type.
        
        Args:
            fund: The fund to calculate average equity for
            session: Database session
            
        Returns:
            Time-weighted average equity balance
        """
        if fund.tracking_type == FundType.COST_BASED:
            return FundEquityCalculator._calculate_cost_based_average_equity(fund, session)
        elif fund.tracking_type == FundType.NAV_BASED:
            return FundEquityCalculator._calculate_nav_based_average_equity(fund, session)
        else:
            raise ValueError(f"Unsupported fund type: {fund.tracking_type}")
    
    @staticmethod
    def _calculate_cost_based_average_equity(fund: Fund, session: Session) -> float:
        """
        Calculate time-weighted average equity balance for cost-based funds.
        
        This method implements the time-weighted average calculation directly,
        providing a pure domain calculation without service dependencies.
        
        Args:
            fund: The fund to calculate average equity for
            session: Database session
            
        Returns:
            Time-weighted average equity balance
        """
        from datetime import date
        from src.fund.enums import FundStatus
        
        # Get all events for the fund
        all_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        if not all_events:
            return 0.0
        
        # Filter to only equity-adjusting events for performance
        equity_events = [
            event for event in all_events 
            if EventType.is_equity_event(event.event_type)
        ]
        
        if not equity_events:
            return 0.0
        elif len(equity_events) == 1:
            return equity_events[0].current_equity_balance or 0.0
        
        # Time-weighted average: sum(balance * days) / total_days
        total_weighted_equity = 0.0
        total_days = 0
        
        # Calculate weighted equity for periods between equity events
        for i in range(len(equity_events) - 1):
            e = equity_events[i]
            next_e = equity_events[i + 1]
            days = (next_e.event_date - e.event_date).days
            equity = e.current_equity_balance if e.current_equity_balance is not None else 0.0
            total_weighted_equity += equity * days
            total_days += days
        
        # Determine the correct period end: use end_date if present, else today if active
        last_event = equity_events[-1]
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
    
    @staticmethod
    def _calculate_nav_based_average_equity(fund: Fund, session: Session) -> float:
        """
        Calculate time-weighted average equity balance for NAV-based funds.
        
        For NAV-based funds, this calculates the time-weighted average of the
        FIFO cost base over time, which represents the average equity balance.
        
        Args:
            fund: The fund to calculate average equity for
            session: Database session
            
        Returns:
            Time-weighted average equity balance (FIFO cost base)
        """
        from datetime import date
        from src.fund.enums import FundStatus
        
        # Get all unit purchase and sale events
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        if not unit_events:
            return 0.0
        
        # Calculate FIFO cost base at each point in time
        equity_periods = []
        from collections import deque
        
        available_units = deque()  # Each entry: (units, cost_per_unit)
        current_cost_base = 0.0
        
        for i, event in enumerate(unit_events):
            # Calculate cost base before this event
            if i == 0:
                # First event - cost base is 0
                period_start_cost_base = 0.0
            else:
                period_start_cost_base = current_cost_base
            
            # Process the event
            if event.event_type == EventType.UNIT_PURCHASE:
                units = event.units_purchased or 0.0
                unit_price = event.unit_price or 0.0
                brokerage_fee = getattr(event, 'brokerage_fee', 0.0) or 0.0
                
                if units > 0 and unit_price > 0:
                    cost_per_unit = unit_price + (brokerage_fee / units)
                    available_units.append((units, cost_per_unit))
                    current_cost_base += units * cost_per_unit
                    
            elif event.event_type == EventType.UNIT_SALE:
                units_sold = event.units_sold or 0.0
                
                if units_sold > 0:
                    remaining_units_to_sell = units_sold
                    
                    # Process sale using FIFO
                    while remaining_units_to_sell > 0 and available_units:
                        available_units_count, cost_per_unit = available_units[0]
                        units_from_this_purchase = min(remaining_units_to_sell, available_units_count)
                        remaining_units_to_sell -= units_from_this_purchase
                        current_cost_base -= units_from_this_purchase * cost_per_unit
                        
                        # Update or remove from available units
                        if units_from_this_purchase == available_units_count:
                            available_units.popleft()
                        else:
                            available_units[0] = (available_units_count - units_from_this_purchase, cost_per_unit)
            
            # Calculate cost base after this event
            period_end_cost_base = current_cost_base
            
            # Add period to equity periods
            equity_periods.append((event.event_date, period_start_cost_base, period_end_cost_base))
        
        if not equity_periods:
            return 0.0
        
        # Calculate time-weighted average
        total_weighted_equity = 0.0
        total_days = 0
        
        # Calculate weighted equity for periods between events
        for i in range(len(equity_periods) - 1):
            current_date, start_cost_base, end_cost_base = equity_periods[i]
            next_date, _, _ = equity_periods[i + 1]
            
            days = (next_date - current_date).days
            if days > 0:
                # Use average of start and end cost base for the period
                avg_cost_base = (start_cost_base + end_cost_base) / 2
                total_weighted_equity += avg_cost_base * days
                total_days += days
        
        # Handle the last period
        last_date, last_start_cost_base, last_end_cost_base = equity_periods[-1]
        
        # Determine period end
        if fund.end_date is not None:
            period_end = fund.end_date
        elif fund.status == FundStatus.ACTIVE:
            period_end = date.today()
        else:
            period_end = last_date
        
        if period_end and period_end >= last_date:
            days = (period_end - last_date).days
            if days >= 0:
                # Use average of start and end cost base for the period
                avg_cost_base = (last_start_cost_base + last_end_cost_base) / 2
                total_weighted_equity += avg_cost_base * days
                total_days += days
        
        return total_weighted_equity / total_days if total_days > 0 else 0.0
    
    
    # ============================================================================
    # TOTAL COST BASIS CALCULATION
    # ============================================================================
    
    @staticmethod
    def calculate_total_cost_basis(fund: Fund, session: Session) -> float:
        """
        Calculate total cost basis based on fund type.
        
        Args:
            fund: The fund to calculate cost basis for
            session: Database session
            
        Returns:
            Total cost basis (cost-based: sum of capital calls, NAV-based: FIFO cost base)
        """
        if fund.tracking_type == FundType.COST_BASED:
            return FundEquityCalculator._calculate_cost_based_total_cost_basis(fund, session)
        elif fund.tracking_type == FundType.NAV_BASED:
            return FundEquityCalculator._calculate_nav_based_total_cost_basis(fund, session)
        else:
            raise ValueError(f"Unsupported fund type: {fund.tracking_type}")
    
    @staticmethod
    def _calculate_cost_based_total_cost_basis(fund: Fund, session: Session) -> float:
        """
        Calculate total cost basis for cost-based funds.
        
        The cost basis is the total amount of capital called,
        regardless of any returns.
        
        Args:
            fund: The fund to calculate cost basis for
            session: Database session
            
        Returns:
            Total cost basis (sum of all capital calls)
        """
        capital_calls = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).all()
        
        return sum(e.amount or 0.0 for e in capital_calls)
    
    @staticmethod
    def _calculate_nav_based_total_cost_basis(fund: Fund, session: Session) -> float:
        """
        Calculate total cost basis for NAV-based funds (FIFO cost base).
        
        For NAV-based funds, the total cost basis is the FIFO cost base
        of units still owned, which is the same as current equity balance.
        
        Args:
            fund: The fund to calculate cost basis for
            session: Database session
            
        Returns:
            Total cost basis (FIFO cost base of units still owned)
        """
        # For NAV-based funds, total cost basis is the same as current equity balance
        return FundEquityCalculator._calculate_nav_based_current_equity(fund, session)
    
    
    # ============================================================================
    # CONVENIENCE METHODS
    # ============================================================================
    
    @staticmethod
    def recalculate_all_equity_fields(fund: Fund, session: Session) -> dict:
        """
        Recalculate all equity-related fields for a fund based on fund type.
        
        This is a convenience method that calculates all equity fields
        in one call, useful for operations that need to update multiple
        fields at once.
        
        Args:
            fund: The fund to recalculate
            session: Database session
            
        Returns:
            Dictionary containing all calculated equity fields
        """
        result = {
            'current_equity_balance': FundEquityCalculator.calculate_current_equity(fund, session),
            'average_equity_balance': FundEquityCalculator.calculate_average_equity(fund, session),
            'total_cost_basis': FundEquityCalculator.calculate_total_cost_basis(fund, session)
        }
        
        # Add fund type specific fields
        if fund.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, add additional NAV-specific calculations
            result.update({
                'current_units': fund.current_units or 0.0,
                'current_unit_price': fund.current_unit_price or 0.0,
                'current_nav_total': fund.current_nav_total or 0.0
            })
        
        return result
