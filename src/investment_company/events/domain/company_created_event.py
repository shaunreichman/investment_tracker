"""
Company Created Domain Event.

This module provides the CompanyCreatedEvent class,
representing when a new investment company is created.
"""

from datetime import date
from typing import Dict, Any

from src.investment_company.events.domain.base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class CompanyCreatedEvent(CompanyDomainEvent):
    """
    Domain event for when a new investment company is created.
    
    This event is published when a new company is successfully created
    and can trigger dependent updates in other parts of the system.
    
    Attributes:
        company_id: ID of the newly created company
        event_date: Date when the company was created
        company_name: Name of the created company
        company_type: Type of the created company
        metadata: Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        company_name: str,
        company_type: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new company created event.
        
        Args:
            company_id: ID of the newly created company
            event_date: Date when the company was created
            company_name: Name of the created company
            company_type: Type of the created company
            metadata: Additional event-specific data
        """
        super().__init__(company_id, event_date, metadata)
        self.company_name = company_name
        self.company_type = company_type
        
        # Add company-specific data to metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            'company_name': company_name,
            'company_type': company_type
        })
        self.metadata = metadata
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.COMPANY_CREATED
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"company_name='{self.company_name}', "
            f"event_date={self.event_date})"
        )
