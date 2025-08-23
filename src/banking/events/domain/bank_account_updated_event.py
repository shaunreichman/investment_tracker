"""
Bank Account Updated Domain Event.

This module provides the domain event for bank account updates,
enabling other components to react to account modifications.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankAccountUpdatedEvent(BankingDomainEvent):
    """
    Domain event for bank account updates.
    
    This event is published when a bank account is updated,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        account_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank account updated event.
        
        Args:
            account_id: ID of the updated bank account
            event_date: Date when the account was updated
            metadata: Additional event-specific data including changes made
        """
        super().__init__(
            banking_entity_id=account_id,
            entity_type="bank_account",
            event_date=event_date,
            metadata=metadata or {}
        )
    
    @property
    def event_type(self) -> str:
        """Get the type of this event."""
        return "bank_account_updated"
    
    @property
    def account_id(self) -> int:
        """Get the ID of the updated bank account."""
        return self.banking_entity_id
    
    @property
    def changes(self) -> Dict[str, Any]:
        """Get the changes that were made to the account."""
        return self.metadata.get('changes', {})
