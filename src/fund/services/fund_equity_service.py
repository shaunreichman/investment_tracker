"""
Fund Equity Service.
"""

from typing import Optional, List
from sqlalchemy.orm import Session

from src.fund.models import Fund, FundFieldChange
from src.fund.calculators.fund_equity_calculator import FundEquityCalculator
from src.fund.repositories import FundEventRepository
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from src.fund.enums.fund_enums import FundTrackingType


class FundEquityService:
    """
    Fund Equity Service.

    This module provides the FundEquityService class, which handles fund equity operations and business logic.
    The service provides clean separation of concerns for:
    - Update the equity fields of a fund

    The service uses the FundEventRepository and FundEquityCalculator to perform operations.
    The service is used by the FundEventSecondaryService to update the equity fields of a fund.
    """
    
    def __init__(self):
        """
        Initialize the FundEquityService.
        
        Args:
            fund_event_repository: Fund event repository to use. If None, creates a new one.
            fund_equity_calculator: Fund equity calculator to use. If None, creates a new one.
        """
        self.fund_event_repository = FundEventRepository()
        self.fund_equity_calculator = FundEquityCalculator()
    
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
            session: Database session
            current_equity_flag: Flag to update the current equity balance
            average_equity_flag: Flag to update the average equity balance
            total_cost_basis_flag: Flag to update the total cost basis

        Returns:
            List[FundFieldChange] with updated values and metadata
            
        Raises:
            ValueError: If the fund is not found
        """
        old_current_equity_balance = fund.current_equity_balance
        old_average_equity_balance = fund.average_equity_balance
        old_total_cost_basis = fund.total_cost_basis
        
        # SINGLE COMPUTATION: Get events and calculate balances once
        events = self.fund_event_repository.get_fund_events(session, fund_ids=[fund.id], 
                    event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                    sort_order=SortOrder.ASC)
        event_balances = self.fund_equity_calculator.calculate_event_equity_balances(fund, events)
        
        # DERIVED CALCULATIONS: All other values calculated from pre-computed balances
        if current_equity_flag:
            current_equity = self.fund_equity_calculator.calculate_current_equity_from_balances(event_balances)
            fund.current_equity_balance = current_equity
        if average_equity_flag:
            average_equity = self.fund_equity_calculator.calculate_average_equity_from_balances(events, event_balances)
            fund.average_equity_balance = average_equity
        if total_cost_basis_flag:
            total_cost_basis = self.fund_equity_calculator.calculate_total_cost_basis_from_balances(event_balances, fund, events)
            fund.total_cost_basis = total_cost_basis
        
        equity_changes = []

        # Update event balances and track changes
        for event, balance in zip(events, event_balances):
            if event.current_equity_balance != balance:
                old_equity_balance = event.current_equity_balance
                event.current_equity_balance = balance
                equity_changes.append(FundFieldChange(object='FUND_EVENT', object_id=event.id, field_name='current_equity_balance', old_value=old_equity_balance, new_value=event.current_equity_balance))
            
        if old_current_equity_balance != fund.current_equity_balance:
            equity_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='current_equity_balance', old_value=old_current_equity_balance, new_value=fund.current_equity_balance))
        if old_average_equity_balance != fund.average_equity_balance:
            equity_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='average_equity_balance', old_value=old_average_equity_balance, new_value=fund.average_equity_balance))
        if old_total_cost_basis != fund.total_cost_basis:
            equity_changes.append(FundFieldChange(object='FUND', object_id=fund.id, field_name='total_cost_basis', old_value=old_total_cost_basis, new_value=fund.total_cost_basis))
        
        return equity_changes if equity_changes else None