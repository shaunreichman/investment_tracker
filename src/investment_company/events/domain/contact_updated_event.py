"""
Contact Updated Domain Event.

This module provides the domain event for contact updates in the investment company system.
It represents the business event when contact information is updated.
"""

from typing import Dict, Any, List
from datetime import date, datetime, timezone
import uuid

from .base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class ContactUpdatedEvent(CompanyDomainEvent):
    """
    Domain event for contact updates.
    
    This event is published when contact information is updated,
    providing audit trail and enabling dependent updates.
    """
    
    def __init__(self, company_id: int, contact_id: int, event_date: date, 
                 updated_fields: List[str], new_values: Dict[str, Any] = None):
        """
        Initialize the contact updated event.
        
        Args:
            company_id: ID of the company the contact belongs to
            contact_id: ID of the contact being updated
            event_date: Date when the update occurred
            updated_fields: List of field names that were updated
            new_values: Dictionary of new values being applied (optional)
        """
        super().__init__(
            company_id=company_id,
            event_date=event_date
        )
        
        # Contact-specific fields
        self.contact_id = contact_id  # (SYSTEM) ID of the updated contact
        self.updated_fields = updated_fields  # (SYSTEM) List of updated field names
        self.new_values = new_values or {}  # (SYSTEM) New values being applied
        
        # Event metadata
        self.audit_trail = {
            'contact_id': contact_id,
            'updated_fields': updated_fields,
            'new_values': self.new_values,
            'update_timestamp': self.timestamp.isoformat()
        }
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.CONTACT_UPDATED
    
    def __str__(self) -> str:
        """Return string representation of the event."""
        return (f"ContactUpdatedEvent(company_id={self.company_id}, "
                f"contact_id={self.contact_id}, fields={self.updated_fields})")
    
    def __repr__(self) -> str:
        """Return detailed string representation of the event."""
        return (f"ContactUpdatedEvent(company_id={self.company_id}, "
                f"contact_id={self.contact_id}, event_date={self.event_date}, "
                f"timestamp={self.timestamp}, event_id={self.event_id}, "
                f"updated_fields={self.updated_fields}, new_values={self.new_values})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the event
        """
        base_dict = super().to_dict()
        base_dict.update({
            'contact_id': self.contact_id,
            'updated_fields': self.updated_fields,
            'new_values': self.new_values,
            'event_type': self.event_type.value,
            'audit_trail': self.audit_trail
        })
        return base_dict
    
    def get_affected_entities(self) -> List[str]:
        """
        Get list of entity IDs affected by this event.
        
        Returns:
            list: List of affected entity identifiers
        """
        return [
            f"company:{self.company_id}",
            f"contact:{self.contact_id}"
        ]
    
    def get_event_summary(self) -> str:
        """
        Get human-readable summary of the event.
        
        Returns:
            str: Event summary
        """
        field_count = len(self.updated_fields)
        field_list = ', '.join(self.updated_fields)
        return f"Contact {self.contact_id} updated with {field_count} field(s): {field_list}"
