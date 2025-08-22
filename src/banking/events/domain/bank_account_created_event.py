"""
Bank Account Created Domain Event.

This module provides the domain event for bank account creation,
enabling other components to react to new account creation.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class BankAccountCreatedEvent(BankingDomainEvent):
    """
    Domain event for bank account creation.
    
    This event is published when a new bank account is created,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        account_id: int,
        event_date: date,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new bank account created event.
        
        Args:
            account_id: ID of the newly created bank account
            event_date: Date when the account was created
            metadata: Additional event-specific data
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
        return "bank_account_created"
    
    @property
    def account_id(self) -> int:
        """Get the ID of the created bank account."""
        return self.banking_entity_id
