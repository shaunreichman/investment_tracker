"""
Fund Event Cash Flow Repository.

This repository provides data access operations for FundEventCashFlow entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- FundEventCashFlow CRUD operations
- Cash flow querying and filtering
- Bank account relationship queries
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEventCashFlow
from src.fund.enums import CashFlowDirection


class FundEventCashFlowRepository:
    """
    Repository for fund event cash flow data access operations.
    
    This repository handles all database operations for fund event cash flows including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    cash flow data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund event cash flow repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, cash_flow_id: int, session: Session) -> Optional[FundEventCashFlow]:
        """
        Get a fund event cash flow by its ID.
        
        Args:
            cash_flow_id: ID of the cash flow to retrieve
            session: Database session
            
        Returns:
            FundEventCashFlow object if found, None otherwise
        """
        cache_key = f"fund_event_cash_flow:{cash_flow_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flow = session.query(FundEventCashFlow).filter(FundEventCashFlow.id == cash_flow_id).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = cash_flow
        
        return cash_flow
    
    def get_by_fund_event(self, fund_event_id: int, session: Session) -> List[FundEventCashFlow]:
        """
        Get all cash flows for a specific fund event.
        
        Args:
            fund_event_id: ID of the fund event
            session: Database session
            
        Returns:
            List of FundEventCashFlow objects for the fund event
        """
        cache_key = f"fund_event_cash_flows:fund_event:{fund_event_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flows = session.query(FundEventCashFlow).filter(
            FundEventCashFlow.fund_event_id == fund_event_id
        ).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def get_by_bank_account(self, bank_account_id: int, session: Session) -> List[FundEventCashFlow]:
        """
        Get all cash flows for a specific bank account.
        
        Args:
            bank_account_id: ID of the bank account
            session: Database session
            
        Returns:
            List of FundEventCashFlow objects for the bank account
        """
        cache_key = f"fund_event_cash_flows:bank_account:{bank_account_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flows = session.query(FundEventCashFlow).filter(
            FundEventCashFlow.bank_account_id == bank_account_id
        ).order_by(FundEventCashFlow.transfer_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def count_by_bank_account(self, bank_account_id: int, session: Session) -> int:
        """
        Count cash flows for a specific bank account.
        
        Args:
            bank_account_id: ID of the bank account
            session: Database session
            
        Returns:
            Number of cash flows for the bank account
        """
        cache_key = f"fund_event_cash_flows:count:bank_account:{bank_account_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(FundEventCashFlow).filter(
            FundEventCashFlow.bank_account_id == bank_account_id
        ).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def has_cash_flows_for_bank_account(self, bank_account_id: int, session: Session) -> bool:
        """
        Check if a bank account has any cash flows.
        
        Args:
            bank_account_id: ID of the bank account
            session: Database session
            
        Returns:
            True if bank account has cash flows, False otherwise
        """
        count = self.count_by_bank_account(bank_account_id, session)
        return count > 0
    
    def get_by_date_range(self, start_date: date, end_date: date, session: Session) -> List[FundEventCashFlow]:
        """
        Get cash flows within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            session: Database session
            
        Returns:
            List of FundEventCashFlow objects within the date range
        """
        cache_key = f"fund_event_cash_flows:date_range:{start_date}:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flows = session.query(FundEventCashFlow).filter(
            and_(
                FundEventCashFlow.transfer_date >= start_date,
                FundEventCashFlow.transfer_date <= end_date
            )
        ).order_by(FundEventCashFlow.transfer_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def get_by_currency(self, currency: str, session: Session) -> List[FundEventCashFlow]:
        """
        Get cash flows for a specific currency.
        
        Args:
            currency: Currency code
            session: Database session
            
        Returns:
            List of FundEventCashFlow objects for the currency
        """
        cache_key = f"fund_event_cash_flows:currency:{currency}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flows = session.query(FundEventCashFlow).filter(
            FundEventCashFlow.currency == currency
        ).order_by(FundEventCashFlow.transfer_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def get_by_direction(self, direction: CashFlowDirection, session: Session) -> List[FundEventCashFlow]:
        """
        Get cash flows for a specific direction.
        
        Args:
            direction: Cash flow direction (inflow/outflow)
            session: Database session
            
        Returns:
            List of FundEventCashFlow objects for the direction
        """
        cache_key = f"fund_event_cash_flows:direction:{direction.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        cash_flows = session.query(FundEventCashFlow).filter(
            FundEventCashFlow.direction == direction
        ).order_by(FundEventCashFlow.transfer_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def create(self, cash_flow: FundEventCashFlow, session: Session) -> FundEventCashFlow:
        """
        Create a new fund event cash flow.
        
        Args:
            cash_flow: FundEventCashFlow instance to create
            session: Database session
            
        Returns:
            Created FundEventCashFlow instance
        """
        session.add(cash_flow)
        session.flush()
        
        # Clear relevant caches
        self._clear_cash_flow_caches(cash_flow.fund_event_id, cash_flow.bank_account_id)
        
        return cash_flow
    
    def update(self, cash_flow: FundEventCashFlow, session: Session) -> FundEventCashFlow:
        """
        Update an existing fund event cash flow.
        
        Args:
            cash_flow: FundEventCashFlow instance to update
            session: Database session
            
        Returns:
            Updated FundEventCashFlow instance
        """
        session.flush()
        
        # Clear relevant caches
        self._clear_cash_flow_caches(cash_flow.fund_event_id, cash_flow.bank_account_id)
        
        return cash_flow
    
    def delete(self, cash_flow: FundEventCashFlow, session: Session) -> None:
        """
        Delete a fund event cash flow.
        
        Args:
            cash_flow: FundEventCashFlow instance to delete
            session: Database session
        """
        fund_event_id = cash_flow.fund_event_id
        bank_account_id = cash_flow.bank_account_id
        
        session.delete(cash_flow)
        session.flush()
        
        # Clear relevant caches
        self._clear_cash_flow_caches(fund_event_id, bank_account_id)
    
    def get_total_count(self, session: Session) -> int:
        """
        Get total count of all cash flows.
        
        Args:
            session: Database session
            
        Returns:
            Total number of cash flows
        """
        cache_key = "fund_event_cash_flows:total_count"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(FundEventCashFlow).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def search(self, search_term: str, session: Session) -> List[FundEventCashFlow]:
        """
        Search cash flows by reference or description.
        
        Args:
            search_term: Search term
            session: Database session
            
        Returns:
            List of matching FundEventCashFlow objects
        """
        if not search_term:
            return []
        
        cache_key = f"fund_event_cash_flows:search:{search_term}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with search
        cash_flows = session.query(FundEventCashFlow).filter(
            or_(
                FundEventCashFlow.reference.ilike(f"%{search_term}%"),
                FundEventCashFlow.description.ilike(f"%{search_term}%")
            )
        ).order_by(FundEventCashFlow.transfer_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = cash_flows
        
        return cash_flows
    
    def _clear_cash_flow_caches(self, fund_event_id: Optional[int] = None, bank_account_id: Optional[int] = None) -> None:
        """Clear cash flow-related caches."""
        keys_to_remove = []
        
        for key in self._cache.keys():
            if key.startswith('fund_event_cash_flow'):
                # Clear specific cash flow
                if fund_event_id and f":{fund_event_id}" in key:
                    keys_to_remove.append(key)
                # Clear bank account related caches
                if bank_account_id and f":bank_account:{bank_account_id}" in key:
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
