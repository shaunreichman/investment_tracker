"""
Account Status Changed Domain Event.

This module provides the domain event for account status changes,
enabling other components to react to account status modifications.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class AccountStatusChangedEvent(BankingDomainEvent):
    """
    Domain event for account status changes.
    
    This event is published when a bank account's status is changed,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        account_id: int,
        event_date: date,
        old_status: bool,
        new_status: bool,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new account status changed event.
        
        Args:
            account_id: ID of the bank account whose status changed
            event_date: Date when the status change occurred
            old_status: Previous active status
            new_status: New active status
            metadata: Additional event-specific data
        """
        status_metadata = {
            'old_status': old_status,
            'new_status': new_status,
            **(metadata or {})
        }
        
        super().__init__(
            banking_entity_id=account_id,
            entity_type="bank_account",
            event_date=event_date,
            metadata=status_metadata
        )
    
    @property
    def event_type(self) -> str:
        """Get the type of this event."""
        return "account_status_changed"
    
    @property
    def account_id(self) -> int:
        """Get the ID of the bank account."""
        return self.banking_entity_id
    
    @property
    def old_status(self) -> bool:
        """Get the previous active status."""
        return self.metadata['old_status']
    
    @property
    def new_status(self) -> bool:
        """Get the new active status."""
        return self.metadata['new_status']
    
    @property
    def status_description(self) -> str:
        """Get a human-readable description of the status change."""
        if self.old_status and not self.new_status:
            return "Account deactivated"
        elif not self.old_status and self.new_status:
            return "Account activated"
        else:
            return "Status unchanged"
