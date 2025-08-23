"""
Contact Updated Domain Event.

This module provides the domain event for contact updates in the investment company system.
It represents the business event when contact information is updated.
"""

from typing import Dict, Any, List
from datetime import date, datetime, timezone
import uuid

from .base_event import CompanyDomainEvent


class ContactUpdatedEvent(CompanyDomainEvent):
    """
    Domain event for contact updates.
    
    This event is published when contact information is updated,
    providing audit trail and enabling dependent updates.
    """
    
    def __init__(self, company_id: int, contact_id: int, event_date: date, 
                 previous_values: Dict[str, Any], updated_fields: List[str]):
        """
        Initialize the contact updated event.
        
        Args:
            company_id: ID of the company the contact belongs to
            contact_id: ID of the contact being updated
            event_date: Date when the update occurred
            previous_values: Dictionary of previous values for audit
            updated_fields: List of field names that were updated
        """
        super().__init__(
            company_id=company_id,
            event_date=event_date,
            timestamp=datetime.now(timezone.utc),
            event_id=str(uuid.uuid4())
        )
        
        # Contact-specific fields
        self.contact_id = contact_id  # (SYSTEM) ID of the updated contact
        self.previous_values = previous_values  # (SYSTEM) Previous values for audit
        self.updated_fields = updated_fields  # (SYSTEM) List of updated field names
        
        # Event metadata
        self.event_type = 'CONTACT_UPDATED'  # (SYSTEM) Event type identifier
        self.audit_trail = {
            'contact_id': contact_id,
            'previous_values': previous_values,
            'updated_fields': updated_fields,
            'update_timestamp': self.timestamp.isoformat()
        }
    
    def __str__(self) -> str:
        """Return string representation of the event."""
        return (f"ContactUpdatedEvent(company_id={self.company_id}, "
                f"contact_id={self.contact_id}, fields={self.updated_fields})")
    
    def __repr__(self) -> str:
        """Return detailed string representation of the event."""
        return (f"ContactUpdatedEvent(company_id={self.company_id}, "
                f"contact_id={self.contact_id}, event_date={self.event_date}, "
                f"timestamp={self.timestamp}, event_id={self.event_id}, "
                f"previous_values={self.previous_values}, updated_fields={self.updated_fields})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert event to dictionary representation.
        
        Returns:
            dict: Dictionary representation of the event
        """
        base_dict = super().to_dict()
        base_dict.update({
            'contact_id': self.contact_id,
            'previous_values': self.previous_values,
            'updated_fields': self.updated_fields,
            'event_type': self.event_type,
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
