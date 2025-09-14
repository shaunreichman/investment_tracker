"""
Fund Event Query Repository.

This repository provides complex query operations for fund events,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Complex event queries and filtering
- Event aggregations and calculations
- Search and filtering operations
- Cross-event type operations
- Data analysis operations
"""

from typing import List, Optional, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.models import FundEvent
from src.fund.enums import EventType


class FundEventQueryRepository:
    """
    Repository for complex fund event query operations.
    
    This repository handles complex queries, aggregations, and analysis
    operations for fund events. It provides a clean interface for business
    logic components to perform complex data operations without direct
    database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the fund event query repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_events_by_type(self, fund_id: int, event_type: EventType, session: Session) -> List[FundEvent]:
        """
        Get events of a specific type for a fund.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of event to retrieve
            session: Database session
            
        Returns:
            List of events of the specified type
        """
        cache_key = f"events_by_type:fund:{fund_id}:type:{event_type.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_by_fund(self, fund_id: int, session: Session) -> List[FundEvent]:
        """
        Get all events for a specific fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            List of all events for the fund
        """
        cache_key = f"events_by_fund:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund_id
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_by_date_range(self, fund_id: int, start_date: date, end_date: date, session: Session) -> List[FundEvent]:
        """
        Get events for a fund within a date range.
        
        Args:
            fund_id: ID of the fund
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            
        Returns:
            List of events in the date range
        """
        cache_key = f"events_by_date_range:fund:{fund_id}:start:{start_date}:end:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_by_fund_and_type(self, fund_id: int, event_types: List[EventType], session: Session) -> List[FundEvent]:
        """
        Get events for a fund filtered by multiple event types.
        
        Args:
            fund_id: ID of the fund
            event_types: List of event types to filter by
            session: Database session
            
        Returns:
            List of events matching the event types
        """
        cache_key = f"events_by_fund_and_type:fund:{fund_id}:types:{[t.value for t in event_types]}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([t.value for t in event_types])
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_by_fund_and_date_range(self, fund_id: int, start_date: date, end_date: date, session: Session) -> List[FundEvent]:
        """
        Get events for a fund within a date range.
        
        Args:
            fund_id: ID of the fund
            start_date: Start date for the range
            end_date: End date for the range
            session: Database session
            
        Returns:
            List of events in the date range
        """
        cache_key = f"events_by_fund_and_date_range:fund:{fund_id}:start:{start_date}:end:{end_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_date >= start_date,
                FundEvent.event_date <= end_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_latest_event_by_type(self, fund_id: int, event_type: EventType, session: Session) -> Optional[FundEvent]:
        """
        Get the latest event of a specific type for a fund.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of event to retrieve
            session: Database session
            
        Returns:
            Latest event of the specified type or None
        """
        cache_key = f"latest_event_by_type:fund:{fund_id}:type:{event_type.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        event = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value
            )
        ).order_by(FundEvent.event_date.desc()).first()
        
        # Cache the result
        self._cache[cache_key] = event
        
        return event
    
    def get_events_after_date(self, fund_id: int, event_type: EventType, after_date: date, session: Session) -> List[FundEvent]:
        """
        Get events of a specific type after a given date.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of event to retrieve
            after_date: Date to filter after
            session: Database session
            
        Returns:
            List of events after the date
        """
        cache_key = f"events_after_date:fund:{fund_id}:type:{event_type.value}:after:{after_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value,
                FundEvent.event_date > after_date
            )
        ).order_by(FundEvent.event_date.asc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_before_date(self, fund_id: int, event_type: EventType, before_date: date, session: Session) -> List[FundEvent]:
        """
        Get events of a specific type before a given date.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of event to retrieve
            before_date: Date to filter before
            session: Database session
            
        Returns:
            List of events before the date
        """
        cache_key = f"events_before_date:fund:{fund_id}:type:{event_type.value}:before:{before_date}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value,
                FundEvent.event_date < before_date
            )
        ).order_by(FundEvent.event_date.desc()).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_events_by_fund_and_types_ordered(self, fund_id: int, event_types: List[EventType], 
                                           session: Session, skip: int = 0, limit: int = 100) -> List[FundEvent]:
        """
        Get events for a fund filtered by multiple event types with pagination.
        
        Args:
            fund_id: ID of the fund
            event_types: List of event types to filter by
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of events matching the event types
        """
        cache_key = f"events_by_fund_and_types_ordered:fund:{fund_id}:types:{[t.value for t in event_types]}:skip:{skip}:limit:{limit}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        events = session.query(FundEvent).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type.in_([t.value for t in event_types])
            )
        ).order_by(FundEvent.event_date.asc()).offset(skip).limit(limit).all()
        
        # Cache the result
        self._cache[cache_key] = events
        
        return events
    
    def get_total_by_type(self, fund_id: int, event_type: EventType, session: Session) -> float:
        """
        Get total amount for a specific event type for a fund.
        
        Args:
            fund_id: ID of the fund
            event_type: Type of event to sum
            session: Database session
            
        Returns:
            Total amount for the event type
        """
        cache_key = f"total_by_type:fund:{fund_id}:type:{event_type.value}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == event_type.value
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_total_tax_withheld(self, fund_id: int, session: Session) -> float:
        """
        Get total tax withheld for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total tax withheld amount
        """
        cache_key = f"total_tax_withheld:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        total = session.query(func.sum(FundEvent.tax_withholding)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.tax_withholding.isnot(None)
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_distributions_by_type(self, fund_id: int, session: Session) -> Dict[str, float]:
        """
        Get distributions broken down by type.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Dictionary of distribution amounts by type
        """
        cache_key = f"distributions_by_type:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        results = session.query(
            FundEvent.distribution_type,
            func.sum(FundEvent.amount)
        ).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DISTRIBUTION.value,
                FundEvent.distribution_type.isnot(None)
            )
        ).group_by(FundEvent.distribution_type).all()
        
        # Convert to dictionary
        distributions = {}
        for dist_type, amount in results:
            distributions[dist_type.value if hasattr(dist_type, 'value') else str(dist_type)] = float(amount) if amount else 0.0
        
        # Cache the result
        self._cache[cache_key] = distributions
        
        return distributions
    
    def get_taxable_distributions(self, fund_id: int, session: Session) -> float:
        """
        Get total taxable distributions for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Total taxable distributions amount
        """
        cache_key = f"taxable_distributions:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database - taxable distributions are those with tax withholding
        total = session.query(func.sum(FundEvent.amount)).filter(
            and_(
                FundEvent.fund_id == fund_id,
                FundEvent.event_type == EventType.DISTRIBUTION.value,
                FundEvent.tax_withholding.isnot(None),
                FundEvent.tax_withholding > 0
            )
        ).scalar()
        
        result = float(total) if total else 0.0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def get_event_count_by_fund(self, fund_id: int, session: Session) -> int:
        """
        Get the count of events for a fund.
        
        Args:
            fund_id: ID of the fund
            session: Database session
            
        Returns:
            Number of events for the fund
        """
        cache_key = f"event_count:fund:{fund_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(func.count(FundEvent.id)).filter(
            FundEvent.fund_id == fund_id
        ).scalar()
        
        result = count or 0
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def _clear_fund_cache(self, fund_id: int) -> None:
        """Clear cache for events by fund."""
        for key in list(self._cache.keys()):
            if f"fund:{fund_id}" in key:
                self._cache.pop(key, None)
    
    def clear_all_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
