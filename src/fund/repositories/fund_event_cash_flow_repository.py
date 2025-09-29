"""
Fund Event Cash Flow Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.fund.models import FundEventCashFlow
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.shared.enums.shared_enums import SortOrder


class FundEventCashFlowRepository:
    """
    Fund Event Cash Flow Repository.
    
    This repository handles all database operations for fund event cash flows including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    cash flow data without direct database access.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund event cash flow repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl


    ################################################################################
    # Get Fund Event Cash Flow
    ################################################################################

    def get_fund_event_cash_flows(self, session: Session,
                                    fund_id: int = None,
                                    fund_event_id: int = None,
                                    bank_account_id: int = None,
                                    sort_by: SortFieldFundEventCashFlow = SortFieldFundEventCashFlow.TRANSFER_DATE,
                                    sort_order: SortOrder = SortOrder.ASC) -> List[FundEventCashFlow]:
        """
        Get all fund event cash flows.

        Args:
            session: Database session
            fund_id: ID of the fund to filter by (optional) - filters through fund_event relationship
            fund_event_id: ID of the event to filter by (optional)
            bank_account_id: ID of the bank account to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)

        Returns:
            List of fund event cash flows
        """
        # Validate sort field
        if sort_by not in SortFieldFundEventCashFlow:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        cache_key = f"fund_event_cash_flows:fund:{fund_id}:event:{fund_event_id}:bank:{bank_account_id}"

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        query = session.query(FundEventCashFlow)

        if fund_id:
            # Filter by fund_id through the fund_event relationship
            query = query.join(FundEventCashFlow.fund_event).filter(FundEventCashFlow.fund_event.has(fund_id=fund_id))
        if fund_event_id:
            query = query.filter(FundEventCashFlow.fund_event_id == fund_event_id)
        if bank_account_id:
            query = query.filter(FundEventCashFlow.bank_account_id == bank_account_id)
        
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
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
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
        cache_key = f"fund_event_cash_flow:{fund_event_cash_flow_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flow = session.query(FundEventCashFlow).filter(FundEventCashFlow.id == fund_event_cash_flow_id).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = cash_flow
        
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
        
        # Clear relevant caches
        self._clear_cash_flow_caches(cash_flow.fund_event_id, cash_flow.bank_account_id)
        
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
        
        # Store IDs for cache clearing
        fund_event_id = cash_flow.fund_event_id
        bank_account_id = cash_flow.bank_account_id
        
        session.delete(cash_flow)
        session.flush()
        
        # Clear relevant caches
        self._clear_cash_flow_caches(fund_event_id, bank_account_id)

        return True
    

    ################################################################################
    # Clear Cache
    ################################################################################

    def _clear_cash_flow_caches(self, fund_event_id: Optional[int] = None, bank_account_id: Optional[int] = None) -> None:
        """Clear cash flow-related caches."""
        keys_to_remove = []
        
        for key in self._cache.keys():
            if key.startswith('fund_event_cash_flow'):
                # Clear specific cash flow
                if fund_event_id and f":event:{fund_event_id}" in key:
                    keys_to_remove.append(key)
                # Clear bank account related caches
                if bank_account_id and f":bank:{bank_account_id}" in key:
                    keys_to_remove.append(key)
                # Clear general caches
                if key in ['fund_event_cash_flows:total_count']:
                    keys_to_remove.append(key)
        
        for key in keys_to_remove:
            if key in self._cache:
                del self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
