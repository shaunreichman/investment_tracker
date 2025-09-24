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

from typing import Optional, List
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundFieldChange
from src.fund.calculators.fund_equity_calculator import FundEquityCalculator
from src.fund.repositories import FundEventRepository
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder


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
    
    def update_fund_equity_fields(self, fund: Fund, session: Session,
                                  current_equity_flag: bool = True,
                                  average_equity_flag: bool = True,
                                  total_cost_basis_flag: bool = True) -> Optional[List[FundFieldChange]]:
        """
        Update all equity fields for a fund with single computation - EFFICIENT.
        
        This method uses the single computation approach to calculate all
        equity fields once, then updates only the events that actually changed.
        
        Args:
            fund: The fund to update
            
        Returns:
            Dictionary with updated values and metadata
        """
        old_current_equity_balance = fund.current_equity_balance
        old_average_equity_balance = fund.average_equity_balance
        old_total_cost_basis = fund.total_cost_basis
        # SINGLE COMPUTATION: Get events and calculate balances once
        events = FundEventRepository.get_fund_events(session, fund.id, 
                    event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                    sort_order=SortOrder.ASC)
        event_balances = self.calculator.calculate_event_equity_balances(fund, events)
        
        # DERIVED CALCULATIONS: All other values calculated from pre-computed balances
        if current_equity_flag:
            current_equity = self.calculator.calculate_current_equity_from_balances(event_balances)
            fund.current_equity_balance = current_equity
        if average_equity_flag:
            average_equity = self.calculator.calculate_average_equity_from_balances(events, event_balances)
            fund.average_equity_balance = average_equity
        if total_cost_basis_flag:
            total_cost_basis = self.calculator.calculate_total_cost_basis_from_balances(event_balances, fund, events)
            fund.total_cost_basis = total_cost_basis
        
        # Update only changed events for efficiency
        for event, (balance, has_changed) in zip(events, event_balances):
            if has_changed:
                event.current_equity_balance = balance

        equity_changes = []
        if old_current_equity_balance != fund.current_equity_balance:
            equity_changes.append(FundFieldChange(field_name='current_equity_balance', old_value=old_current_equity_balance, new_value=fund.current_equity_balance))
        if old_average_equity_balance != fund.average_equity_balance:
            equity_changes.append(FundFieldChange(field_name='average_equity_balance', old_value=old_average_equity_balance, new_value=fund.average_equity_balance))
        if old_total_cost_basis != fund.total_cost_basis:
            equity_changes.append(FundFieldChange(field_name='total_cost_basis', old_value=old_total_cost_basis, new_value=fund.total_cost_basis))
        
        return equity_changes if equity_changes else None