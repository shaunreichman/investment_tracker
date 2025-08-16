"""
NAV Updated Domain Event.

This event is published when a fund's NAV is updated,
enabling loose coupling between NAV updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class NAVUpdatedEvent(FundDomainEvent):
    """
    Domain event for when a fund's NAV is updated.
    
    This event is published whenever the NAV of a fund changes. It contains
    the old and new NAV values along with the reason for the change and
    any subsequent updates that may be required.
    
    Attributes:
        old_nav (Decimal): Previous NAV value
        new_nav (Decimal): New NAV value after the update
        change_reason (str): Reason for the NAV change
        change_amount (Decimal): Absolute amount of the NAV change
        change_percentage (Decimal): Percentage change in NAV
        event_type (str): Type identifier for this event
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        old_nav: Decimal,
        new_nav: Decimal,
        change_reason: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a NAV updated event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the NAV was updated
            old_nav: Previous NAV value
            new_nav: New NAV value
            change_reason: Reason for the NAV change
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.old_nav = old_nav
        self.new_nav = new_nav
        self.change_reason = change_reason
        self.change_amount = new_nav - old_nav
        
        # Calculate percentage change (avoid division by zero)
        if old_nav != 0:
            self.change_percentage = (self.change_amount / old_nav) * 100
        else:
            self.change_percentage = Decimal('0')
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the event type identifier."""
        return DomainEventType.NAV_UPDATED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'old_nav': str(self.old_nav),
            'new_nav': str(self.new_nav),
            'change_reason': self.change_reason,
            'change_amount': str(self.change_amount),
            'change_percentage': str(self.change_percentage)
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with NAV change details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"old_nav={self.old_nav}, "
            f"new_nav={self.new_nav}, "
            f"change_reason='{self.change_reason}')"
        )
