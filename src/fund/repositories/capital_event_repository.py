"""
Capital Event Repository.

This repository provides data access operations for capital-related fund events
(CAPITAL_CALL, RETURN_OF_CAPITAL), implementing the repository pattern for 
clean separation of concerns.

Key responsibilities:
- Capital event CRUD operations
- Capital event querying and filtering
- Capital event aggregations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, SortFieldFund


class CapitalEventRepository:
    """
    Repository for capital event data access operations.
    
    This repository handles all database operations for capital events including
    CRUD operations, bulk operations, and optimized queries for capital event processing.
    It provides a clean interface for business logic components to interact with
    capital event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the capital event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_capital_call(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a capital call event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created capital call event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.CAPITAL_CALL
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_return_of_capital(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a return of capital event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created return of capital event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.RETURN_OF_CAPITAL
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def get_capital_events(self, fund_id: int, session: Session, 
                          skip: int = 0, limit: int = 100,
                          start_date: Optional[date] = None,
                          end_date: Optional[date] = None,
                          sort_by: SortFieldFund = SortFieldFund.EVENT_DATE,
                          sort_order: SortOrder = SortOrder.ASC) -> List[FundEvent]:
        """
        Get capital events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            start_date: Optional start date filter
            end_date: Optional end date filter
            sort_by: Field to sort by
            sort_order: Sort order (ASC or DESC)
            
        Returns:
            List of capital events
        """
        cache_key = f"capital_events:fund:{fund_id}:skip:{skip}:limit:{limit}:start:{start_date}:end:{end_date}:sort:{sort_by.value}:order:{sort_order.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([EventType.CAPITAL_CALL.value, EventType.RETURN_OF_CAPITAL.value])
            )
        )
        
        # Apply date filters
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        # Apply sorting
        if sort_by == SortFieldFund.EVENT_DATE:
            sort_column = FundEvent.event_date
        else:
            sort_column = getattr(FundEvent, sort_by.value)
        if sort_order == SortOrder.DESC:
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        events = query.all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_total_capital_calls(self, fund_id: int, session: Session) -> float:
        """
        Get total capital calls for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total capital calls amount
        """
        cache_key = f"total_capital_calls:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.CAPITAL_CALL.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_total_capital_returns(self, fund_id: int, session: Session) -> float:
        """
        Get total capital returns for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total capital returns amount
        """
        cache_key = f"total_capital_returns:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.RETURN_OF_CAPITAL.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_capital_events_by_date_range(self, fund_id: int, start_date: date, end_date: date, session: Session) -> List[FundEvent]:
        """
        Get capital events for a fund within a date range.
        
        Args:
            fund_id: ID of the fund
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            
        Returns:
            List of capital events in the date range
        """
        cache_key = f"capital_events:fund:{fund_id}:start:{start_date}:end:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([EventType.CAPITAL_CALL.value, EventType.RETURN_OF_CAPITAL.value]),
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for events by fund."""
        for key in list(self._cache.keys()):
            if f"fund:{fund_id}" in key:
                self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
