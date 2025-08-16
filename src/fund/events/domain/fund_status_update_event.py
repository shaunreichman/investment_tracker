"""
Fund Status Update Event.

This module defines the domain event that is published when a fund's
status is updated, enabling loose coupling between components.
"""

from datetime import date
from typing import Optional, Dict, Any

from .base_event import FundDomainEvent
from ...enums import DomainEventType


class FundStatusUpdateEvent(FundDomainEvent):
    """
    Domain event published when a fund's status is updated.
    
    This event enables loose coupling by allowing other components to
    react to status changes without direct dependencies.
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        old_status: str,
        new_status: str,
        update_reason: str,
        trigger_event_id: Optional[int] = None,
        trigger_event_type: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the fund status update event.
        
        Args:
            fund_id: ID of the fund whose status was updated
            event_date: Date when the status update occurred
            old_status: Previous status of the fund
            new_status: New status of the fund
            update_reason: Reason for the status update
            trigger_event_id: ID of the event that triggered the status update
            trigger_event_type: Type of event that triggered the status update
            metadata: Additional metadata about the status update
        """
        super().__init__(
            fund_id=fund_id,
            event_date=event_date,
            metadata=metadata or {}
        )
        
        self.old_status = old_status
        self.new_status = new_status
        self.update_reason = update_reason
        self.trigger_event_id = trigger_event_id
        self.trigger_event_type = trigger_event_type
    
    @property
    def event_type(self) -> DomainEventType:
        """
        Get the type of this event.
        
        Returns:
            DomainEventType enum value for the event type
        """
        return DomainEventType.FUND_STATUS_UPDATED
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the event to a dictionary representation.
        
        Returns:
            Dictionary representation of the event
        """
        base_dict = super().to_dict()
        base_dict.update({
            'old_status': self.old_status,
            'new_status': self.new_status,
            'update_reason': self.update_reason,
            'trigger_event_id': self.trigger_event_id,
            'trigger_event_type': self.trigger_event_type
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"FundStatusUpdateEvent("
            f"fund_id={self.fund_id}, "
            f"event_date={self.event_date}, "
            f"old_status='{self.old_status}', "
            f"new_status='{self.new_status}', "
            f"update_reason='{self.update_reason}')"
        )
