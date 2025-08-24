"""
Base Company Domain Event.

This module provides the base class for all company domain events,
defining the common interface and shared functionality.

Key responsibilities:
- Common event structure and validation
- Event metadata and relationships
- Event serialization and persistence
- Event type classification
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
import uuid
from abc import ABC, abstractmethod

from src.investment_company.enums import CompanyDomainEventType


class CompanyDomainEvent(ABC):
    """
    Base class for all company domain events.
    
    Domain events represent significant state changes in the investment company system
    and enable loose coupling between components. Each event contains
    the data needed for other components to react appropriately.
    
    Attributes:
        company_id (int): ID of the company that generated this event
        event_date (date): Date when the event occurred
        timestamp (datetime): Exact timestamp when the event was created
        event_id (str): Unique identifier for this event instance
        metadata (Dict[str, Any]): Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new domain event.
        
        Args:
            company_id: ID of the company that generated this event
            event_date: Date when the event occurred
            metadata: Additional event-specific data
        """
        self.company_id = company_id
        self.event_date = event_date
        self.timestamp = datetime.now()
        self.event_id = str(uuid.uuid4())
        self.metadata = metadata or {}
    
    @property
    @abstractmethod
    def event_type(self) -> CompanyDomainEventType:
        """
        Get the type of this event.
        
        Returns:
            CompanyDomainEventType enum value for the event type
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,  # Use .value here for serialization
            'company_id': self.company_id,
            'event_date': self.event_date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"event_date={self.event_date}, "
            f"event_type='{self.event_type}')"
        )
    
    def __eq__(self, other: Any) -> bool:
        """Check if two events are equal based on event_id."""
        if not isinstance(other, CompanyDomainEvent):
            return False
        return self.event_id == other.event_id
