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
from src.fund.enums import EventType
from src.shared.enums.shared_enums import EventOperation



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

    def store_domain_fund_event(self, fund_id: int, event_type: EventType, event_operation: EventOperation, event_id: int, event_data: Dict[str, Any], session: Session) -> DomainFundEvent:
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
