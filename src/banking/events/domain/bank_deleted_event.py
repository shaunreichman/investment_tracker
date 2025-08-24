"""
Bank Deleted Domain Event.

This module provides the domain event for bank deletion,
enabling other components to react to bank removal.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankDeletedEvent(BankingDomainEvent):
    """
    Domain event for bank deletion.
    
    This event is published when a bank is deleted,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        bank_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank deleted event.
        
        Args:
            bank_id: ID of the deleted bank
            event_date: Date when the bank was deleted
            metadata: Additional event-specific data including deletion reason
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
        return "bank_deleted"
    
    @property
    def bank_id(self) -> int:
        """Get the ID of the deleted bank."""
        return self.banking_entity_id
    
    @property
    def deletion_reason(self) -> str:
        """Get the reason for bank deletion."""
        return self.metadata.get('deletion_reason', 'Unknown')
