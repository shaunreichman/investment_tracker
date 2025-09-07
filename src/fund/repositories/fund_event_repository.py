"""
Fund Event Repository.

This repository provides data access operations for FundEvent entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- FundEvent CRUD operations
- Event querying and filtering
- Event relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, SortField


class FundEventRepository:
    """
    Repository for fund event data access operations.
    
    This repository handles all database operations for fund events including
    CRUD operations, bulk operations, and optimized queries for event processing.
    It provides a clean interface for business logic components to interact with
    fund event data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund event repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, event_id: int, session: Session) -> Optional[FundEvent]:
        """
        Get a fund event by its ID.
        
        Args:
            event_id: ID of the event to retrieve
            session: Database session
            
        Returns:
            FundEvent object if found, None otherwise
        """
        cache_key = f"event:{event_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        event = session.query(FundEvent).filter(FundEvent.id == event_id).first()
        
        # Cache the result
        if event:
            self._cache[cache_key] = event
        
        return event
    
    def get_by_fund(self, fund_id: int, session: Session, 
                    event_types: Optional[List[EventType]] = None,
                    skip: int = 0,
                    limit: int = 100,
                    sort_order: SortOrder = SortOrder.ASC) -> List[FundEvent]:
        """
        Get all events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            event_types: Optional list of event types to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            sort_order: Sort order (ascending or descending)
            
        Returns:
            List of fund events for the specified fund
        """
        cache_key = f"events:fund:{fund_id}:types:{event_types}:skip:{skip}:limit:{limit}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(FundEvent.fund_id == fund_id)
        
        # Apply event type filter if specified
        if event_types:
            query = query.filter(FundEvent.event_type.in_([et.value for et in event_types]))
        
        # Apply sorting (default to newest first)
        if sort_order == SortOrder.ASC:
            query = query.order_by(FundEvent.event_date.asc(), FundEvent.id.asc())
        else:
            query = query.order_by(FundEvent.event_date.desc(), FundEvent.id.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        events = query.all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_by_date_range(self, start_date: date, end_date: date, 
                         session: Session,
                         fund_id: Optional[int] = None) -> List[FundEvent]:
        """
        Get all events within a date range.
        
        Args:
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            fund_id: Optional fund ID to filter by
            
        Returns:
            List of fund events within the date range
        """
        cache_key = f"events:date_range:{start_date}:{end_date}:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(
            and_(
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        )
        
        # Apply fund filter if specified
        if fund_id:
            query = query.filter(FundEvent.fund_id == fund_id)
        
        # Order by date and ID
        query = query.order_by(FundEvent.event_date.asc(), FundEvent.id.asc())
        
        events = query.all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_by_type(self, event_type: EventType, session: Session,
                    fund_id: Optional[int] = None,
                    skip: int = 0,
                    limit: int = 100) -> List[FundEvent]:
        """
        Get all events of a specific type.
        
        Args:
            event_type: Type of event to retrieve
            session: Database session
            fund_id: Optional fund ID to filter by
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of fund events of the specified type
        """
        cache_key = f"events:type:{event_type.value}:fund:{fund_id}:skip:{skip}:limit:{limit}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(FundEvent.event_type == event_type.value)
        
        # Apply fund filter if specified
        if fund_id:
            query = query.filter(FundEvent.fund_id == fund_id)
        
        # Order by date and ID
        query = query.order_by(FundEvent.event_date.desc(), FundEvent.id.desc())
        
        # Apply pagination
        query = query.offset(skip).limit(limit)
        
        events = query.all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def create(self, event_data: Dict[str, Any], session: Session) -> FundEvent:
        """
        Create a new fund event.
        
        Args:
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            Created FundEvent object
            
        Raises:
            TypeError: If event_data is not a dictionary
            ValueError: If required fields are missing
        """
        # Type validation - ensure event_data is a dictionary
        if not isinstance(event_data, dict):
            raise TypeError(f"event_data must be a dictionary, got {type(event_data).__name__}")
        
        # Validate required fields
        required_fields = ['fund_id', 'event_type', 'event_date', 'amount']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' is missing")
        
        # Create event object
        event = FundEvent(**event_data)
        session.add(event)
        session.flush()  # Get the ID without committing
        
        # Clear relevant caches
        self._clear_fund_cache(event_data.get('fund_id'))
        self._clear_date_cache(event_data.get('event_date'))
        self._clear_type_cache(event_data.get('event_type'))
        
        return event
    
    def update(self, event_id: int, event_data: Dict[str, Any], session: Session) -> Optional[FundEvent]:
        """
        Update an existing fund event.
        
        Args:
            event_id: ID of the event to update
            event_data: Dictionary containing updated event data
            session: Database session
            
        Returns:
            Updated FundEvent object if found, None otherwise
            
        Raises:
            TypeError: If event_data is not a dictionary
        """
        # Type validation - ensure event_data is a dictionary
        if not isinstance(event_data, dict):
            raise TypeError(f"event_data must be a dictionary, got {type(event_data).__name__}")
        
        event = self.get_by_id(event_id, session)
        if not event:
            return None
        
        # Store old values for cache clearing
        old_fund_id = event.fund_id
        old_event_date = event.event_date
        old_event_type = event.event_type
        
        # Update fields
        for key, value in event_data.items():
            if hasattr(event, key):
                setattr(event, key, value)
        
        # Clear relevant caches
        self._clear_fund_cache(old_fund_id)
        self._clear_date_cache(old_event_date)
        self._clear_type_cache(old_event_type)
        
        # Clear caches for new values
        self._clear_fund_cache(event.fund_id)
        self._clear_date_cache(event.event_date)
        self._clear_type_cache(event.event_type)
        
        session.flush()
        return event
    
    def delete(self, event_id: int, session: Session) -> bool:
        """
        Delete a fund event.
        
        Args:
            event_id: ID of the event to delete
            session: Database session
            
        Returns:
            True if event was deleted, False if not found
        """
        event = self.get_by_id(event_id, session)
        if not event:
            return False
        
        # Store values for cache clearing
        fund_id = event.fund_id
        event_date = event.event_date
        event_type = event.event_type
        
        # If this event is grouped, delete all events in the same group
        if event.is_grouped and event.group_id:
            # Find all events in the same group
            group_events = session.query(FundEvent).filter(
                FundEvent.group_id == event.group_id
            ).all()
            
            # Delete all events in the group
            for group_event in group_events:
                session.delete(group_event)
                self._clear_event_cache(group_event.id)
        else:
            # Delete just this single event
            session.delete(event)
            self._clear_event_cache(event_id)
        
        # Clear relevant caches
        self._clear_fund_cache(fund_id)
        self._clear_date_cache(event_date)
        self._clear_type_cache(event_type)
        
        return True
    
    def bulk_create(self, events_data: List[Dict[str, Any]], session: Session) -> List[FundEvent]:
        """
        Create multiple fund events in bulk.
        
        Args:
            events_data: List of dictionaries containing event data
            session: Database session
            
        Returns:
            List of created FundEvent objects
            
        Raises:
            TypeError: If events_data is not a list
            ValueError: If any event is missing required fields
        """
        # Type validation - ensure events_data is a list
        if not isinstance(events_data, list):
            raise TypeError(f"events_data must be a list, got {type(events_data).__name__}")
        
        if not events_data:
            return []
        
        # Validate all events have required fields
        required_fields = ['fund_id', 'event_type', 'event_date', 'amount']
        for i, event_data in enumerate(events_data):
            # Additional validation that each item is a dictionary
            if not isinstance(event_data, dict):
                raise TypeError(f"Event {i} must be a dictionary, got {type(event_data).__name__}")
            
            for field in required_fields:
                if field not in event_data:
                    raise ValueError(f"Event {i} is missing required field '{field}'")
        
        # Create all events
        events = []
        for event_data in events_data:
            event = FundEvent(**event_data)
            events.append(event)
            session.add(event)
        
        session.flush()  # Get all IDs without committing
        
        # Clear relevant caches
        fund_ids = set(event_data.get('fund_id') for event_data in events_data)
        event_dates = set(event_data.get('event_date') for event_data in events_data)
        event_types = set(event_data.get('event_type') for event_data in events_data)
        
        for fund_id in fund_ids:
            self._clear_fund_cache(fund_id)
        for event_date in event_dates:
            self._clear_date_cache(event_date)
        for event_type in event_types:
            self._clear_type_cache(event_type)
        
        return events
    
    def get_events_for_recalculation(self, fund_id: int, from_event_id: int, 
                                   session: Session) -> List[FundEvent]:
        """
        Get events for recalculation from a specific event onwards.
        
        Args:
            fund_id: ID of the fund
            from_event_id: ID of the event to start recalculation from
            session: Database session
            
        Returns:
            List of fund events for recalculation
        """
        cache_key = f"events:recalc:{fund_id}:from:{from_event_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database for events after the specified event
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.id >= from_event_id
            )
        ).order_by(FundEvent.event_date.asc(), FundEvent.id.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_event_count_by_fund(self, fund_id: int, session: Session) -> int:
        """
        Get the total count of events for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total count of events for the fund
        """
        cache_key = f"event_count:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(func.count(FundEvent.id)).filter(
            FundEvent.fund_id == fund_id
        ).scalar()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def _clear_event_cache(self, event_id: int) -> None:
        """Clear cache for a specific event."""
        cache_key = f"event:{event_id}"
        self._cache.pop(cache_key, None)
    
    def _clear_fund_cache(self, fund_id: Optional[int]) -> None:
        """Clear cache for events by fund."""
        if fund_id:
            # Clear all fund-related caches
            for key in list(self._cache.keys()):
                if f"events:fund:{fund_id}" in key or f"event_count:fund:{fund_id}" in key:
                    self._cache.pop(key, None)
    
    def _clear_date_cache(self, event_date: Optional[date]) -> None:
        """Clear cache for events by date."""
        if event_date:
            for key in list(self._cache.keys()):
                if f"events:date_range" in key:
                    self._cache.pop(key, None)
    
    def _clear_type_cache(self, event_type: Optional[str]) -> None:
        """Clear cache for events by type."""
        if event_type:
            for key in list(self._cache.keys()):
                if f"events:type:{event_type}" in key:
                    self._cache.pop(key, None)
    

    def get_by_fund_and_types(self, fund_id: int, event_types: List[EventType], 
                             session: Session, skip: int = 0, limit: int = 100) -> List[FundEvent]:
        """
        Get fund events filtered by event types.
        
        Args:
            fund_id: ID of the fund
            event_types: List of event types to filter by
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of filtered fund events
        """
        cache_key = f"events:fund:{fund_id}:types:{sorted([t.value for t in event_types])}:skip:{skip}:limit:{limit}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_(event_types)
            )
        ).order_by(FundEvent.event_date.asc(), FundEvent.id.asc()).offset(skip).limit(limit).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_by_fund_after_date(self, fund_id: int, after_date: date, 
                              session: Session, event_types: Optional[List[EventType]] = None) -> List[FundEvent]:
        """
        Get fund events after a specific date.
        
        Args:
            fund_id: ID of the fund
            after_date: Date to filter after
            session: Database session
            event_types: Optional list of event types to filter by
            
        Returns:
            List of fund events after the specified date
        """
        cache_key = f"events:fund:{fund_id}:after:{after_date}:types:{sorted([t.value for t in event_types]) if event_types else 'all'}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_date > after_date
            )
        )
        
        # Add event type filter if specified
        if event_types:
            query = query.filter(FundEvent.event_type.in_(event_types))
        
        events = query.order_by(FundEvent.event_date.asc(), FundEvent.id.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events

    def generate_group_id(self, session: Session) -> int:
        """
        Generate a unique group ID using database sequence for enterprise-grade uniqueness.
        
        This method uses a PostgreSQL sequence to ensure thread-safe, unique group IDs
        for event grouping functionality. The sequence is created via database migration.
        
        Args:
            session: Database session for sequence access
            
        Returns:
            int: Unique group ID from the sequence
            
        Raises:
            RuntimeError: If sequence access fails
        """
        from sqlalchemy import text
        
        try:
            # Get next value from sequence
            result = session.execute(text("SELECT nextval('group_id_seq')"))
            group_id = result.scalar()
            
            # Ensure we stay within PostgreSQL Integer limits
            if group_id > 2147483647:
                # Reset sequence if we're getting close to the limit
                session.execute(text("ALTER SEQUENCE group_id_seq RESTART WITH 1"))
                result = session.execute(text("SELECT nextval('group_id_seq')"))
                group_id = result.scalar()
            
            return group_id
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate group ID: {e}") from e

    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
