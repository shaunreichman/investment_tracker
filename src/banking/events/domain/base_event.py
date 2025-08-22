"""
Base Banking Domain Event.

This module provides the base class for all banking domain events,
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


class BankingDomainEvent(ABC):
    """
    Base class for all banking domain events.
    
    Domain events represent significant state changes in the banking system
    and enable loose coupling between components. Each event contains
    the data needed for other components to react appropriately.
    
    Attributes:
        banking_entity_id (int): ID of the banking entity that generated this event
        entity_type (str): Type of banking entity (bank or bank_account)
        event_date (date): Date when the event occurred
        timestamp (datetime): Exact timestamp when the event was created
        event_id (str): Unique identifier for this event instance
        metadata (Dict[str, Any]): Additional event-specific data
    """
    
    def __init__(
        self,
        banking_entity_id: int,
        entity_type: str,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new domain event.
        
        Args:
            banking_entity_id: ID of the banking entity that generated this event
            entity_type: Type of banking entity (bank or bank_account)
            event_date: Date when the event occurred
            metadata: Additional event-specific data
        """
        self.banking_entity_id = banking_entity_id
        self.entity_type = entity_type
        self.event_date = event_date
        self.timestamp = datetime.now()
        self.event_id = str(uuid.uuid4())
        self.metadata = metadata or {}
    
    @property
    @abstractmethod
    def event_type(self) -> str:
        """
        Get the type of this event.
        
        Returns:
            String identifier for the event type
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
            'event_type': self.event_type,
            'banking_entity_id': self.banking_entity_id,
            'entity_type': self.entity_type,
            'event_date': self.event_date.isoformat(),
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"banking_entity_id={self.banking_entity_id}, "
            f"entity_type='{self.entity_type}', "
            f"event_date={self.event_date}, "
            f"event_type='{self.event_type}')"
        )
    
    def __eq__(self, other: Any) -> bool:
        """Check if two events are equal based on event_id."""
        if not isinstance(other, BankingDomainEvent):
            return False
        return self.event_id == other.event_id
    
    def __hash__(self) -> int:
        """Hash based on event_id."""
        return hash(self.event_id)
