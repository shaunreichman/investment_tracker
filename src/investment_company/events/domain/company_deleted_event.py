"""
Company Deleted Domain Event.

This module provides the CompanyDeletedEvent class,
representing when an investment company is deleted.
"""

from datetime import date
from typing import Dict, Any

from src.investment_company.events.domain.base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class CompanyDeletedEvent(CompanyDomainEvent):
    """
    Domain event for when an investment company is deleted.
    
    This event is published when a company is successfully deleted
    and can trigger cleanup operations in other parts of the system.
    
    Attributes:
        company_id: ID of the deleted company
        event_date: Date when the company was deleted
        company_name: Name of the deleted company
        metadata: Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        company_name: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new company deleted event.
        
        Args:
            company_id: ID of the deleted company
            event_date: Date when the company was deleted
            company_name: Name of the deleted company
            metadata: Additional event-specific data
        """
        super().__init__(company_id, event_date, metadata)
        self.company_name = company_name
        
        # Add company deletion-specific data to metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            'company_name': company_name
        })
        self.metadata = metadata
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.COMPANY_DELETED
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"company_name='{self.company_name}', "
            f"event_date={self.event_date})"
        )
