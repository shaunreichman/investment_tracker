"""
Domain Event Repository.

This repository provides data access operations for domain events,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Domain event CRUD operations
- Event querying and filtering
- Event relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func

from src.fund.models import DomainEvent, DomainFundEvent
from src.fund.enums import FundEventOperation, EventType


class DomainEventRepository:
    """
    Repository for managing domain events in the database.
    
    This repository handles:
    1. Storing domain events for audit trails
    2. Querying events by various criteria
    3. Supporting event replay and debugging
    4. Managing event lifecycle
    """
    
    def __init__(self, session: Session):
        """
        Initialize the repository.
        
        Args:
            session: Database session for all operations
        """
        self.session = session
    
    def store_domain_event(self, domain_event: DomainFundEvent) -> DomainEvent:
        """
        Store a domain event in the database.
        
        Args:
            domain_event: DomainFundEvent instance to store
            
        Returns:
            DomainEvent: Stored database record
        """
        # Create a new DomainEvent instance from the domain event
        db_event = DomainEvent(
            fund_id=domain_event.fund_id,
            event_type=domain_event.event_type.value,
            event_data=domain_event.metadata,
            timestamp=domain_event.timestamp,
            source=domain_event.__class__.__name__.lower()
        )
        
        self.session.add(db_event)
        self.session.flush()  # Get the ID without committing
        return db_event
    
    def store_domain_events(self, domain_events: List[DomainFundEvent]) -> List[DomainEvent]:
        """
        Store multiple domain events in the database.
        
        Args:
            domain_events: List of DomainFundEvent instances to store
            
        Returns:
            List[DomainEvent]: List of stored database records
        """
        db_events = []
        for domain_event in domain_events:
            db_event = self.store_domain_event(domain_event)
            db_events.append(db_event)
        return db_events

    def store_domain_fund_event(self, fund_id: int, event_type: EventType, event_operation: FundEventOperation, event_id: int, event_data: Dict[str, Any], session: Session) -> DomainFundEvent:
        """
        Store a domain fund event in the database.
        
        Args:
            fund_id: Fund ID
            event_type: Event type
            event_operation: Event operation
            event_id: Event ID
            event_data: Event data
            session: Session
        """
        db_event = DomainFundEvent(
            fund_id=fund_id,
            event_type=event_type,
            event_operation=event_operation,
            event_id=event_id,
            event_data=event_data
        )
        session.add(db_event)
        session.flush()
        return db_event

    
    def get_by_id(self, event_id: int) -> Optional[DomainEvent]:
        """
        Get a domain event by its primary key ID.
        
        Args:
            event_id: Primary key identifier
            
        Returns:
            DomainEvent: Found event or None
        """
        return self.session.query(DomainEvent).filter(
            DomainEvent.id == event_id
        ).first()
    
    def get_by_fund(self, fund_id: int) -> List[DomainEvent]:
        """
        Get all domain events for a specific fund.
        
        Args:
            fund_id: Fund ID to get events for
            
        Returns:
            List[DomainEvent]: List of domain events ordered by timestamp (newest first)
        """
        return self.session.query(DomainEvent).filter(
            DomainEvent.fund_id == fund_id
        ).order_by(desc(DomainEvent.timestamp)).all()
    
    def get_by_type(self, event_type: str, fund_id: Optional[int] = None, limit: Optional[int] = None) -> List[DomainEvent]:
        """
        Get domain events by type, optionally filtered by fund.
        
        Args:
            event_type: Type of events to retrieve
            fund_id: Optional fund ID filter
            limit: Maximum number of events to return
            
        Returns:
            List[DomainEvent]: List of domain events
        """
        query = self.session.query(DomainEvent).filter(
            DomainEvent.event_type == event_type
        )
        
        if fund_id:
            query = query.filter(DomainEvent.fund_id == fund_id)
        
        query = query.order_by(desc(DomainEvent.timestamp))
        
        if limit:
            query = query.limit(limit)
        
        return query.all()
    
    def get_by_date_range(self, start_date: date, end_date: date, fund_id: Optional[int] = None) -> List[DomainEvent]:
        """
        Get domain events within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            fund_id: Optional fund ID filter
            
        Returns:
            List[DomainEvent]: List of domain events
        """
        query = self.session.query(DomainEvent).filter(
            and_(
                func.date(DomainEvent.timestamp) >= start_date,
                func.date(DomainEvent.timestamp) <= end_date
            )
        )
        
        if fund_id:
            query = query.filter(DomainEvent.fund_id == fund_id)
        
        return query.order_by(desc(DomainEvent.timestamp)).all()
    
    def delete_by_fund(self, fund_id: int) -> int:
        """
        Delete all domain events for a specific fund.
        
        Args:
            fund_id: Fund ID to delete events for
            
        Returns:
            int: Number of events deleted
        """
        result = self.session.query(DomainEvent).filter(
            DomainEvent.fund_id == fund_id
        ).delete()
        
        return result
    
    def get_event_count_by_fund(self, fund_id: int, session: Optional[Session] = None) -> int:
        """
        Get the count of domain events for a specific fund.
        
        Args:
            fund_id: Fund ID to count events for
            session: Database session (optional, uses instance session if not provided)
            
        Returns:
            int: Number of domain events
        """
        db_session = session or self.session
        return db_session.query(DomainEvent).filter(
            DomainEvent.fund_id == fund_id
        ).count()
    
    def get_event_summary(self, fund_id: Optional[int] = None) -> Dict[str, int]:
        """
        Get a summary of domain events by type.
        
        Args:
            fund_id: Optional fund ID filter
            
        Returns:
            Dict[str, int]: Event type counts
        """
        query = self.session.query(
            DomainEvent.event_type,
            func.count(DomainEvent.id).label('count')
        )
        
        if fund_id:
            query = query.filter(DomainEvent.fund_id == fund_id)
        
        results = query.group_by(DomainEvent.event_type).all()
        
        return {event_type: count for event_type, count in results}
