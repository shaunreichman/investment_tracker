"""
Fund Event Cash Flow Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import date

from src.fund.models import FundEventCashFlow, FundEvent
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.shared.enums.shared_enums import SortOrder, Currency


class FundEventCashFlowRepository:
    """
    Fund Event Cash Flow Repository.
    
    This repository handles all database operations for fund event cash flows including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    cash flow data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the fund event cash flow repository.
        
        Args:
            None
        """
        pass


    ################################################################################
    # Get Fund Event Cash Flow
    ################################################################################

    def get_fund_event_cash_flows(self, session: Session,
                                    fund_ids: Optional[List[int]] = None,
                                    fund_event_ids: Optional[List[int]] = None,
                                    bank_account_ids: Optional[List[int]] = None,
                                    different_month: Optional[bool] = None,
                                    adjusted_bank_account_balance_ids: Optional[List[int]] = None,
                                    currencies: Optional[List[Currency]] = None,
                                    start_transfer_date: Optional[date] = None,
                                    end_transfer_date: Optional[date] = None,
                                    start_fund_event_date: Optional[date] = None,
                                    end_fund_event_date: Optional[date] = None,
                                    sort_by: Optional[SortFieldFundEventCashFlow] = SortFieldFundEventCashFlow.TRANSFER_DATE,
                                    sort_order: Optional[SortOrder] = SortOrder.ASC) -> List[FundEventCashFlow]:
        """
        Get all fund event cash flows.

        Args:
            session: Database session
            fund_ids: List of fund IDs to filter by (optional) - filters through fund_event relationship
            fund_event_ids: List of event IDs to filter by (optional)
            bank_account_ids: List of bank account IDs to filter by (optional)
            different_month: Whether the transfer date is in a different month to the fund event date (optional)
            adjusted_bank_account_balance_ids: List of bank account balance IDs to filter by (optional)
            currencies: List of currencies to filter by (optional)
            start_transfer_date: Start date of the transfer date to filter by (optional)
            end_transfer_date: End date of the transfer date to filter by (optional)
            start_fund_event_date: Start date of the fund event date to filter by (optional)
            end_fund_event_date: End date of the fund event date to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)

        Returns:
            List of fund event cash flows
        """
        # Use defaults if None is explicitly passed (overrides function default)
        if sort_by is None:
            sort_by = SortFieldFundEventCashFlow.TRANSFER_DATE
        if sort_order is None:
            sort_order = SortOrder.ASC
        
        # Validate sort field
        if sort_by not in SortFieldFundEventCashFlow:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        query = session.query(FundEventCashFlow)

        if fund_ids and any(fund_ids):  # Filter out zero values
            # Filter by fund_id through the fund_event relationship - need to get the fund_event_id from the fund_event relationship
            query = query.filter(FundEventCashFlow.fund_event_id.in_(session.query(FundEvent.id).filter(FundEvent.fund_id.in_(fund_ids))))
        if fund_event_ids and any(fund_event_ids):  # Filter out zero values
            query = query.filter(FundEventCashFlow.fund_event_id.in_(fund_event_ids))
        if bank_account_ids and any(bank_account_ids):  # Filter out zero values
            query = query.filter(FundEventCashFlow.bank_account_id.in_(bank_account_ids))
        if different_month is not None:
            query = query.filter(FundEventCashFlow.different_month == different_month)
        if adjusted_bank_account_balance_ids and any(adjusted_bank_account_balance_ids):  # Filter out zero values
            query = query.filter(FundEventCashFlow.adjusted_bank_account_balance_id.in_(adjusted_bank_account_balance_ids))
        if currencies and any(currencies):  # Filter out zero values
            query = query.filter(FundEventCashFlow.currency.in_([c.value for c in currencies]))
        if start_transfer_date:
            query = query.filter(FundEventCashFlow.transfer_date >= start_transfer_date)
        if end_transfer_date:
            query = query.filter(FundEventCashFlow.transfer_date <= end_transfer_date)
        if start_fund_event_date:
            query = query.filter(FundEventCashFlow.fund_event_date >= start_fund_event_date)
        if end_fund_event_date:
            query = query.filter(FundEventCashFlow.fund_event_date <= end_fund_event_date)
        
        if sort_by == SortFieldFundEventCashFlow.TRANSFER_DATE:
            query = query.order_by(FundEventCashFlow.transfer_date.asc() if sort_order == SortOrder.ASC else FundEventCashFlow.transfer_date.desc())
        elif sort_by == SortFieldFundEventCashFlow.AMOUNT:
            query = query.order_by(FundEventCashFlow.amount.asc() if sort_order == SortOrder.ASC else FundEventCashFlow.amount.desc())
        elif sort_by == SortFieldFundEventCashFlow.CREATED_AT:
            query = query.order_by(FundEventCashFlow.created_at.asc() if sort_order == SortOrder.ASC else FundEventCashFlow.created_at.desc())
        elif sort_by == SortFieldFundEventCashFlow.UPDATED_AT:
            query = query.order_by(FundEventCashFlow.updated_at.asc() if sort_order == SortOrder.ASC else FundEventCashFlow.updated_at.desc())
        
        # Query database
        cash_flows = query.all()

        return cash_flows
    
    def get_fund_event_cash_flow_by_id(self, fund_event_cash_flow_id: int, session: Session) -> Optional[FundEventCashFlow]:
        """
        Get a fund event cash flow by its ID.
        
        Args:
            fund_event_cash_flow_id: ID of the cash flow to retrieve
            session: Database session
            
        Returns:
            FundEventCashFlow object if found, None otherwise
        """
        # Query database
        cash_flow = session.query(FundEventCashFlow).filter(FundEventCashFlow.id == fund_event_cash_flow_id).first()

        return cash_flow
    

    ################################################################################
    # Create Fund Event Cash Flow
    ################################################################################

    def create_fund_event_cash_flow(self, cash_flow_data: Dict[str, Any], session: Session) -> FundEventCashFlow:
        """
        Create a new fund event cash flow.
        
        Args:
            cash_flow_data: Dictionary containing cash flow data
            session: Database session
            
        Returns:
            Created FundEventCashFlow instance
        """
        cash_flow = FundEventCashFlow(**cash_flow_data)
        session.add(cash_flow)
        session.flush()
        
        return cash_flow
    

    ################################################################################
    # Delete Fund Event Cash Flow
    ################################################################################

    def delete_fund_event_cash_flow(self, fund_event_cash_flow_id: int, session: Session) -> None:
        """
        Delete a fund event cash flow.
        
        Args:
            fund_event_cash_flow_id: ID of the cash flow to delete
            session: Database session

        Returns:
            True if cash flow event was deleted, False if not found
        """
        cash_flow = self.get_fund_event_cash_flow_by_id(fund_event_cash_flow_id, session)
        if not cash_flow:
            return False
        
        session.delete(cash_flow)
        session.flush()

        return True