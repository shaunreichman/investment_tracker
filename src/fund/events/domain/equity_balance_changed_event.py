"""
Equity Balance Changed Domain Event.

This event is published when a fund's equity balance changes,
enabling loose coupling between equity balance updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class EquityBalanceChangedEvent(FundDomainEvent):
    """
    Domain event for when a fund's equity balance changes.
    
    This event is published whenever the equity balance of a fund changes,
    typically due to capital calls, returns of capital, or distributions.
    The event contains the old and new balance values along with the
    reason for the change.
    
    Attributes:
        old_balance (Decimal): Previous equity balance
        new_balance (Decimal): New equity balance after the change
        change_reason (str): Reason for the balance change
        change_amount (Decimal): Absolute amount of the change
        event_type (DomainEventType): Type identifier for this event
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        old_balance: Decimal,
        new_balance: Decimal,
        change_reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize an equity balance changed event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the balance changed
            old_balance: Previous equity balance
            new_balance: New equity balance
            change_reason: Reason for the change
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.old_balance = old_balance
        self.new_balance = new_balance
        self.change_reason = change_reason
        self.change_amount = new_balance - old_balance
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the event type identifier."""
        return DomainEventType.EQUITY_BALANCE_CHANGED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'old_balance': str(self.old_balance),
            'new_balance': str(self.new_balance),
            'change_reason': self.change_reason,
            'change_amount': str(self.change_amount)
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with balance change details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"old_balance={self.old_balance}, "
            f"new_balance={self.new_balance}, "
            f"change_reason='{self.change_reason}')"
        )
