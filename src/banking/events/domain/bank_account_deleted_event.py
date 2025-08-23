"""
Bank Account Deleted Domain Event.

This module provides the domain event for bank account deletion,
enabling other components to react to account removal.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankAccountDeletedEvent(BankingDomainEvent):
    """
    Domain event for bank account deletion.
    
    This event is published when a bank account is deleted,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        account_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank account deleted event.
        
        Args:
            account_id: ID of the deleted bank account
            event_date: Date when the account was deleted
            metadata: Additional event-specific data including deletion reason
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
        return "bank_account_deleted"
    
    @property
    def account_id(self) -> int:
        """Get the ID of the deleted bank account."""
        return self.banking_entity_id
    
    @property
    def deletion_reason(self) -> str:
        """Get the reason for account deletion."""
        return self.metadata.get('deletion_reason', 'Unknown')
