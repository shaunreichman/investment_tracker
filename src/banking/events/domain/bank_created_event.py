"""
Bank Created Domain Event.

This module provides the domain event for bank creation,
enabling other components to react to new bank creation.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankCreatedEvent(BankingDomainEvent):
    """
    Domain event for bank creation.
    
    This event is published when a new bank is created,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        bank_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank created event.
        
        Args:
            bank_id: ID of the newly created bank
            event_date: Date when the bank was created
            metadata: Additional event-specific data
        """
        super().__init__(
            banking_entity_id=bank_id,
            entity_type="bank",
            event_date=event_date,
            metadata=metadata or {}
        )
    
    @property
    def event_type(self) -> str:
        """Get the type of this event."""
        return "bank_created"
    
    @property
    def bank_id(self) -> int:
        """Get the ID of the created bank."""
        return self.banking_entity_id
