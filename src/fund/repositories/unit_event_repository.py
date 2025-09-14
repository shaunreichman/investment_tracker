"""
Unit Event Repository.

This repository provides data access operations for unit-related fund events
(UNIT_PURCHASE, UNIT_SALE, NAV_UPDATE), implementing the repository pattern for 
clean separation of concerns.

Key responsibilities:
- Unit event CRUD operations
- Unit event querying and filtering
- Unit event aggregations
- NAV update operations
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType, SortFieldFund
from src.shared.enums import SortOrder

class UnitEventRepository:
    """
    Repository for unit event data access operations.
    
    This repository handles all database operations for unit events including
    CRUD operations, bulk operations, and optimized queries for unit event processing.
    It provides a clean interface for business logic components to interact with
    unit event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the unit event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def create_unit_purchase(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a unit purchase event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.UNIT_PURCHASE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_unit_sale(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a unit sale event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.UNIT_SALE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def create_nav_update(self, fund_id: int, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a NAV update event.
        
        Args:
            fund_id: ID of the fund
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
        """
        # Ensure event_type is set correctly
        event_data['event_type'] = EventType.NAV_UPDATE
        event_data['fund_id'] = fund_id
        
        # Create the event
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        
        return event
    
    def get_unit_events(self, fund_id: int, session: Session, 
                       skip: int = 0, limit: int = 100,
                       start_date: Optional[date] = None,
                       end_date: Optional[date] = None,
                       sort_by: SortFieldFund = SortFieldFund.EVENT_DATE,
                       sort_order: SortOrder = SortOrder.ASC) -> List[FundEvent]:
        """
        Get unit events for a specific fund.
        
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
            List of unit events
        """
        cache_key = f"unit_events:fund:{fund_id}:skip:{skip}:limit:{limit}:start:{start_date}:end:{end_date}:sort:{sort_by.value}:order:{sort_order.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE.value, EventType.UNIT_SALE.value, EventType.NAV_UPDATE.value])
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
    
    def get_total_unit_purchases(self, fund_id: int, session: Session) -> float:
        """
        Get total unit purchases for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total unit purchases amount
        """
        cache_key = f"total_unit_purchases:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.UNIT_PURCHASE.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_total_unit_sales(self, fund_id: int, session: Session) -> float:
        """
        Get total unit sales for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total unit sales amount
        """
        cache_key = f"total_unit_sales:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.UNIT_SALE.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_latest_nav_update(self, fund_id: int, session: Session) -> Optional[FundEvent]:
        """
        Get the latest NAV update for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Latest NAV update event or None
        """
        cache_key = f"latest_nav:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        event = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.NAV_UPDATE.value
            )
        ).order_by(FundEvent.event_date.desc()).first()
        
        # Cache the result
        self._cache[cache_key] = event
        
        return event
    
    def get_nav_events_before_date(self, fund_id: int, before_date: date, session: Session) -> List[FundEvent]:
        """
        Get NAV events before a specific date.
        
        Args:
            fund_id: ID of the fund
            before_date: Date to filter before
            session: Database session
            
        Returns:
            List of NAV events before the date
        """
        cache_key = f"nav_events_before:fund:{fund_id}:date:{before_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.NAV_UPDATE.value,
                FundEvent.event_date < before_date
            )
        ).order_by(FundEvent.event_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_nav_events_after_date(self, fund_id: int, after_date: date, session: Session) -> List[FundEvent]:
        """
        Get NAV events after a specific date.
        
        Args:
            fund_id: ID of the fund
            after_date: Date to filter after
            session: Database session
            
        Returns:
            List of NAV events after the date
        """
        cache_key = f"nav_events_after:fund:{fund_id}:date:{after_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.NAV_UPDATE.value,
                FundEvent.event_date > after_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_unit_events_by_date_range(self, fund_id: int, start_date: date, end_date: date, session: Session) -> List[FundEvent]:
        """
        Get unit events for a fund within a date range.
        
        Args:
            fund_id: ID of the fund
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            
        Returns:
            List of unit events in the date range
        """
        cache_key = f"unit_events:fund:{fund_id}:start:{start_date}:end:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE.value, EventType.UNIT_SALE.value, EventType.NAV_UPDATE.value]),
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
