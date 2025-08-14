"""
Base Domain Event for Fund System.

This module provides the foundation for all domain events in the fund system.
Domain events represent significant state changes and enable loose coupling
between components.
"""

from abc import ABC, abstractmethod
from datetime import datetime, date
from typing import Any, Dict, Optional, Union
import uuid

from ...enums import DomainEventType


class FundDomainEvent(ABC):
    """
    Base class for all fund domain events.
    
    Domain events represent significant state changes in the fund system
    and enable loose coupling between components. Each event contains
    the data needed for other components to react appropriately.
    
    Attributes:
        fund_id (int): ID of the fund that generated this event
        event_date (date): Date when the event occurred
        timestamp (datetime): Exact timestamp when the event was created
        event_id (str): Unique identifier for this event instance
        metadata (Dict[str, Any]): Additional event-specific data
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new domain event.
        
        Args:
            fund_id: ID of the fund that generated this event
            event_date: Date when the event occurred
            metadata: Additional event-specific data
        """
        self.fund_id = fund_id
        self.event_date = event_date
        self.timestamp = datetime.now()
        self.event_id = str(uuid.uuid4())
        self.metadata = metadata or {}
    
    @property
    @abstractmethod
    def event_type(self) -> DomainEventType:
        """
        Get the type of this event.
        
        Returns:
            DomainEventType enum value for the event type
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
            'fund_id': self.fund_id,
            'event_date': self.event_date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"fund_id={self.fund_id}, "
            f"event_date={self.event_date}, "
            f"event_type='{self.event_type}')"
        )
    
    def __eq__(self, other: Any) -> bool:
        """Check if two events are equal based on event_id."""
        if not isinstance(other, FundDomainEvent):
            return False
        return self.event_id == other.event_id
    
    def __hash__(self) -> int:
        """Hash based on event_id."""
        return hash(self.event_id)
