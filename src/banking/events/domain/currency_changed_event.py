"""
Currency Changed Domain Event.

This module provides the domain event for currency changes,
enabling other components to react to account currency modifications.
"""

from datetime import date
from typing import Dict, Any, Optional

from .base_event import BankingDomainEvent


class CurrencyChangedEvent(BankingDomainEvent):
    """
    Domain event for currency changes.
    
    This event is published when a bank account's currency is changed,
    allowing other components to react appropriately.
    """
    
    def __init__(
        self,
        account_id: int,
        event_date: date,
        old_currency: str,
        new_currency: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a new currency changed event.
        
        Args:
            account_id: ID of the bank account whose currency changed
            event_date: Date when the currency change occurred
            old_currency: Previous currency code
            new_currency: New currency code
            metadata: Additional event-specific data
        """
        currency_metadata = {
            'old_currency': old_currency,
            'new_currency': new_currency,
            **(metadata or {})
        }
        
        super().__init__(
            banking_entity_id=account_id,
            entity_type="bank_account",
            event_date=event_date,
            metadata=currency_metadata
        )
    
    @property
    def event_type(self) -> str:
        """Get the type of this event."""
        return "currency_changed"
    
    @property
    def account_id(self) -> int:
        """Get the ID of the bank account."""
        return self.banking_entity_id
    
    @property
    def old_currency(self) -> str:
        """Get the previous currency code."""
        return self.metadata['old_currency']
    
    @property
    def new_currency(self) -> str:
        """Get the new currency code."""
        return self.metadata['new_currency']
