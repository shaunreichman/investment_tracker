"""
Domain Update Event Services.
"""

from src.shared.repositories import DomainUpdateEventRepository
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from src.shared.enums.domain_update_event_enums import DomainObjectType, SortFieldDomainUpdateEvent
from src.shared.enums.shared_enums import EventOperation, SortOrder
from src.shared.models import DomainUpdateEvent
from src.fund.enums.fund_event_enums import EventType



class DomainUpdateEventService:
    """
    Domain Update Event Services.

    This module provides the DomainUpdateEventService class, which handles domain update event operations and business logic.
    The service provides clean separation of concerns for:
    - Domain update event retrieval
    - Domain update event creation
    - Domain update event deletion

    The service uses the DomainUpdateEventRepository to perform CRUD operations.
    """
    def __init__(self):
        """
        Initialize the domain update event service.
        
        Args:
            None
        """
        self.domain_update_event_repository = DomainUpdateEventRepository()


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
            domain_object_types: List of domain object types
            domain_object_ids: List of domain object ids
            event_operations: List of event operations
            fund_event_types: List of fund event types
            sort_by: Sort field
            sort_order: Sort order
        """
        return self.domain_update_event_repository.get_domain_update_events(session, domain_object_types, domain_object_ids, event_operations, fund_event_types, sort_by, sort_order)

    def get_domain_update_event_by_id(self, domain_update_event_id: int, session: Session) -> Optional[DomainUpdateEvent]:
        """
        Get a Domain Update Event by its ID.

        Args:
            domain_update_event_id: ID of the domain update event to retrieve
            session: Database session

        Returns:
            DomainUpdateEvent: DomainUpdateEvent instance if found, None otherwise
        """
        return self.domain_update_event_repository.get_domain_update_event_by_id(domain_update_event_id, session)


    ################################################################################
    # Create Domain Update Event
    ################################################################################

    def create_domain_update_event(self, session: Session, 
                domain_object_type: DomainObjectType,
                domain_object_id: int,
                event_operation: EventOperation,
                event_data: Dict[str, Any],
                fund_event_type: Optional[EventType] = None
    ) -> DomainUpdateEvent:
        """
        Create a Domain Update Event.

        Args:
            session: Database session
            domain_object_type: Domain object type
            domain_object_id: Domain object id
            event_operation: Event operation
            event_data: Event data
            fund_event_type: Fund event type

        Returns:
            DomainUpdateEvent: DomainUpdateEvent instance
        """

        domain_update_event_data = {
            'domain_object_type': domain_object_type,
            'domain_object_id': domain_object_id,
            'event_operation': event_operation,
            'event_data': event_data,
            'fund_event_type': fund_event_type
        }
        
        domain_update_event = self.domain_update_event_repository.create_domain_update_event(domain_update_event_data, session)
        if not domain_update_event:
            raise ValueError(f"Failed to create domain update event for {domain_object_type} with ID {domain_object_id}")
        
        return domain_update_event
    

    ################################################################################
    # Delete Domain Update Event
    ################################################################################
    
    def delete_domain_update_event(self, domain_update_event_id: int, session: Session) -> bool:
        """
        Delete a Domain Update Event.

        Args:
            domain_update_event_id: ID of the domain update event to delete
            session: Database session

        Returns:
            bool: True if domain update event was deleted, False otherwise
        """
        domain_update_event = self.get_domain_update_event_by_id(domain_update_event_id, session)
        if not domain_update_event:
            raise ValueError(f"Domain update event with ID {domain_update_event_id} not found")
        
        success = self.domain_update_event_repository.delete_domain_update_event(domain_update_event_id, session)
        if not success:
            raise ValueError(f"Failed to delete domain update event with ID {domain_update_event_id}")
        
        return success



    def add_domain_field_changes_to_list(self, all_changes: list, changes) -> None:
        """
        Add changes to the all_changes list, handling both single objects and lists.

        Args:
            all_changes: List to add changes to
            changes: Either a single DomainFieldChange object, a list of DomainFieldChange objects, or None
        """
        if changes:
            if isinstance(changes, list):
                all_changes.extend(changes)
            else:
                all_changes.append(changes)


    