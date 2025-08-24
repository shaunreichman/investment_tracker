"""
Company Updated Domain Event.

This module provides the CompanyUpdatedEvent class,
representing when an investment company's information is updated.
"""

from datetime import date
from typing import Dict, Any

from src.investment_company.events.domain.base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class CompanyUpdatedEvent(CompanyDomainEvent):
    """
    Domain event for when an investment company's information is updated.
    
    This event is published when company details are modified,
    such as name, description, company type, or address changes.
    
    Attributes:
        company_id: ID of the company that was updated
        event_date: Date when the company was updated
        updated_fields: List of fields that were updated
        metadata: Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        updated_fields: list = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new company updated event.
        
        Args:
            company_id: ID of the company that was updated
            event_date: Date when the company was updated
            updated_fields: List of fields that were updated
            metadata: Additional event-specific data
        """
        super().__init__(company_id, event_date, metadata)
        self.updated_fields = updated_fields or []
        
        # Add company update-specific data to metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            'updated_fields': updated_fields or []
        })
        self.metadata = metadata
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.COMPANY_UPDATED
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"updated_fields={self.updated_fields}, "
            f"event_date={self.event_date})"
        )
