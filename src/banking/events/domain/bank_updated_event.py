"""
Bank Updated Domain Event.

This module provides the domain event for bank updates,
enabling other components to react to bank modifications.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankUpdatedEvent(BankingDomainEvent):
    """
    Domain event for bank updates.
    
    This event is published when a bank is updated,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        bank_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank updated event.
        
        Args:
            bank_id: ID of the updated bank
            event_date: Date when the bank was updated
            metadata: Additional event-specific data including changes made
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
        return "bank_updated"
    
    @property
    def bank_id(self) -> int:
        """Get the ID of the updated bank."""
        return self.banking_entity_id
    
    @property
    def changes(self) -> Dict[str, Any]:
        """Get the changes that were made to the bank."""
        return self.metadata.get('changes', {})
