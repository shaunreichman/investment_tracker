"""
Contact Added Domain Event.

This module provides the ContactAddedEvent class,
representing when a new contact is added to an investment company.
"""

from datetime import date
from typing import Dict, Any

from src.investment_company.events.domain.base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class ContactAddedEvent(CompanyDomainEvent):
    """
    Domain event for when a new contact is added to an investment company.
    
    This event is published when a new contact is successfully added
    and can trigger dependent updates in other parts of the system.
    
    Attributes:
        company_id: ID of the company that received the new contact
        event_date: Date when the contact was added
        contact_id: ID of the newly added contact
        contact_name: Name of the added contact
        contact_title: Title of the added contact
        metadata: Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        contact_id: int,
        contact_name: str,
        contact_title: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new contact added event.
        
        Args:
            company_id: ID of the company that received the new contact
            event_date: Date when the contact was added
            contact_id: ID of the newly added contact
            contact_name: Name of the added contact
            contact_title: Title of the added contact
            metadata: Additional event-specific data
        """
        super().__init__(company_id, event_date, metadata)
        self.contact_id = contact_id
        self.contact_name = contact_name
        self.contact_title = contact_title
        
        # Add contact-specific data to metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            'contact_id': contact_id,
            'contact_name': contact_name,
            'contact_title': contact_title
        })
        self.metadata = metadata
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.CONTACT_ADDED
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"contact_id={self.contact_id}, "
            f"contact_name='{self.contact_name}', "
            f"event_date={self.event_date})"
        )
