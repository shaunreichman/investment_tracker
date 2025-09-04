"""
Fund Equity Service.

This service handles database operations for fund equity calculations,
using the pure FundEquityCalculator for all calculation logic.

Key principles:
- Service layer handles database operations
- Calculator layer handles pure calculations
- Clean separation of concerns
- Single computation approach for performance
"""

from typing import List
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundEvent
from src.fund.calculators.fund_equity_calculator import FundEquityCalculator


class FundEquityService:
    """
    Service layer for fund equity operations with database updates.
    
    This service handles database operations while using the pure
    FundEquityCalculator for all calculation logic. Provides efficient
    single computation approach with change detection for database updates.
    """
    
    def __init__(self, session: Session):
        """
        Initialize service with database session.
        
        Args:
            session: Database session for operations
        """
        self.session = session
        self.calculator = FundEquityCalculator()
    
    def update_fund_equity_fields(self, fund: Fund) -> dict:
        """
        Update all equity fields for a fund with single computation - EFFICIENT.
        
        This method uses the single computation approach to calculate all
        equity fields once, then updates only the events that actually changed.
        
        Args:
            fund: The fund to update
            
        Returns:
            Dictionary with updated values and metadata
        """
        # SINGLE COMPUTATION: Get events and calculate balances once
        events = self._get_relevant_events(fund)
        event_balances = self.calculator.calculate_event_equity_balances(fund, events)
        
        # DERIVED CALCULATIONS: All other values calculated from pre-computed balances
        current_equity = self.calculator.calculate_current_equity_from_balances(event_balances)
        average_equity = self.calculator.calculate_average_equity_from_balances(events, event_balances)
        total_cost_basis = self.calculator.calculate_total_cost_basis_from_balances(event_balances, fund, events)
        
        # Update fund fields
        fund.current_equity_balance = current_equity
        fund.average_equity_balance = average_equity
        fund.total_cost_basis = total_cost_basis
        
        # Update only changed events for efficiency
        updated_events_count = 0
        for event, (balance, has_changed) in zip(events, event_balances):
            if has_changed:
                event.current_equity_balance = balance
                updated_events_count += 1
        
        return {
            'current_equity_balance': current_equity,
            'average_equity_balance': average_equity,
            'total_cost_basis': total_cost_basis,
            'updated_events': updated_events_count
        }
    
    def _get_relevant_events(self, fund: Fund) -> List[FundEvent]:
        """
        Get relevant events for the fund type.
        
        Args:
            fund: The fund to get events for
            
        Returns:
            List of relevant events
        """
        return FundEquityCalculator._get_relevant_events(fund, self.session)
