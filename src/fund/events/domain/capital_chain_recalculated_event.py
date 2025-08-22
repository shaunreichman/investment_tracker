"""
Capital Chain Recalculated Domain Event.

This event is published when a fund's capital chain is recalculated,
enabling loose coupling between capital chain updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class CapitalChainRecalculatedEvent(FundDomainEvent):
    """
    Domain event published when a fund's capital chain is recalculated.
    
    This event enables loose coupling by allowing other components to
    react to capital chain changes without direct dependencies.
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        trigger_event_id: int,
        trigger_event_type: str,
        old_equity_balance: Optional[Decimal] = None,
        new_equity_balance: Optional[Decimal] = None,
        change_reason: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the capital chain recalculated event.
        
        Args:
            fund_id: ID of the fund whose capital chain was recalculated
            event_date: Date when the recalculation occurred
            trigger_event_id: ID of the event that triggered the recalculation
            trigger_event_type: Type of event that triggered the recalculation
            old_equity_balance: Previous equity balance before recalculation
            new_equity_balance: New equity balance after recalculation
            change_reason: Reason for the capital chain recalculation
            metadata: Additional metadata about the recalculation
        """
        super().__init__(
            fund_id=fund_id,
            event_date=event_date,
            metadata=metadata or {}
        )
        
        self.trigger_event_id = trigger_event_id
        self.trigger_event_type = trigger_event_type
        self.old_equity_balance = old_equity_balance
        self.new_equity_balance = new_equity_balance
        self.change_reason = change_reason or f"Capital chain recalculated after {trigger_event_type}"
    
    @property
    def event_type(self) -> DomainEventType:
        """
        Get the type of this event.
        
        Returns:
            DomainEventType enum value for the event type
        """
        return DomainEventType.CAPITAL_CHAIN_RECALCULATED
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        base_dict = super().to_dict()
        base_dict.update({
            'trigger_event_id': self.trigger_event_id,
            'trigger_event_type': self.trigger_event_type,
            'old_equity_balance': float(self.old_equity_balance) if self.old_equity_balance else None,
            'new_equity_balance': float(self.new_equity_balance) if self.new_equity_balance else None,
            'change_reason': self.change_reason
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"CapitalChainRecalculatedEvent("
            f"fund_id={self.fund_id}, "
            f"event_date={self.event_date}, "
            f"trigger_event_type='{self.trigger_event_type}', "
            f"change_reason='{self.change_reason}')"
        )
