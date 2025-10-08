"""
Domain Update Event Repository.
"""

from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session

from src.shared.models import DomainUpdateEvent
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation, SortOrder
from src.shared.enums.domain_update_event_enums import SortFieldDomainUpdateEvent, DomainObjectType


class DomainUpdateEventRepository:
    """
    Domain Update Event Repository.

    This repository handles all database operations for domain update events including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    domain update event data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the repository.
        
        Args:
            None
        """
        pass

    ################################################################################
    # Get Domain Update Event
    ################################################################################

    def get_domain_update_events(self, session: Session,
                domain_object_types: Optional[List[DomainObjectType]] = None,
                domain_object_ids: Optional[List[int]] = None,
                event_operations: Optional[List[EventOperation]] = None,
                fund_event_types: Optional[List[EventType]] = None,
                sort_by: Optional[SortFieldDomainUpdateEvent] = SortFieldDomainUpdateEvent.TIMESTAMP,
                sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[DomainUpdateEvent]:
        """
        Get all domain update events.
        
        Args:
            session: Database session
            domain_object_types: Domain object types to filter by (optional)
            domain_object_ids: Domain object IDs to filter by (optional)
            event_operations: Event operations to filter by (optional)
            fund_event_types: Fund event types to filter by (optional)
            sort_by: Field to sort by (optional)
            sort_order: Sort order (ascending or descending) (optional)

        Returns:
            List of domain update events
        """
        # Validate sort field
        if sort_by not in SortFieldDomainUpdateEvent:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        query = session.query(DomainUpdateEvent)
        
        if domain_object_types:
            query = query.filter(DomainUpdateEvent.domain_object_type.in_([dot.value for dot in domain_object_types]))
        if domain_object_ids:
            query = query.filter(DomainUpdateEvent.domain_object_id.in_(domain_object_ids))
        if event_operations:
            query = query.filter(DomainUpdateEvent.event_operation.in_([eo.value for eo in event_operations]))
        if fund_event_types:
            query = query.filter(DomainUpdateEvent.fund_event_type.in_([fet.value for fet in fund_event_types]))

        # Apply sorting
        if sort_by == SortFieldDomainUpdateEvent.TIMESTAMP:
            query = query.order_by(DomainUpdateEvent.timestamp.asc() if sort_order == SortOrder.ASC else DomainUpdateEvent.timestamp.desc())
        elif sort_by == SortFieldDomainUpdateEvent.DOMAIN_OBJECT_TYPE:
            query = query.order_by(DomainUpdateEvent.domain_object_type.asc() if sort_order == SortOrder.ASC else DomainUpdateEvent.domain_object_type.desc())
        elif sort_by == SortFieldDomainUpdateEvent.DOMAIN_OBJECT_ID:
            query = query.order_by(DomainUpdateEvent.domain_object_id.asc() if sort_order == SortOrder.ASC else DomainUpdateEvent.domain_object_id.desc())
        elif sort_by == SortFieldDomainUpdateEvent.EVENT_OPERATION:
            query = query.order_by(DomainUpdateEvent.event_operation.asc() if sort_order == SortOrder.ASC else DomainUpdateEvent.event_operation.desc())
        elif sort_by == SortFieldDomainUpdateEvent.FUND_EVENT_TYPE:
            query = query.order_by(DomainUpdateEvent.fund_event_type.asc() if sort_order == SortOrder.ASC else DomainUpdateEvent.fund_event_type.desc())
        
        domain_update_events = query.all()
        
        return domain_update_events

    def get_domain_update_event_by_id(self, domain_update_event_id: int, session: Session) -> DomainUpdateEvent:
        """
        Get a domain update event by its ID.
        
        Args:
            domain_update_event_id: ID of the domain update event to retrieve
            session: Database session
            
        Returns:
            DomainUpdateEvent object if found, None otherwise
        """
        domain_update_event = session.query(DomainUpdateEvent).filter(DomainUpdateEvent.id == domain_update_event_id).first()
        return domain_update_event


    ################################################################################
    # Create Domain Update Event
    ################################################################################

    def create_domain_update_event(self, domain_update_event_data: Dict[str, Any], session: Session) -> DomainUpdateEvent:
        """
        Create a domain update event in the database.
        
        Args:
            domain_update_event_data: Dictionary containing domain update event data
            session: Database session
        """
        db_event = DomainUpdateEvent(**domain_update_event_data)
        session.add(db_event)
        session.flush()
        return db_event


    ################################################################################
    # Delete Domain Update Event
    ################################################################################

    def delete_domain_update_event(self, domain_update_event_id: int, session: Session) -> bool:
        """
        Delete a domain update event from the database.
        """
        domain_update_event = self.get_domain_update_event_by_id(domain_update_event_id, session)
        if not domain_update_event:
            return False
        
        session.delete(domain_update_event)
        session.flush()
        return True
    