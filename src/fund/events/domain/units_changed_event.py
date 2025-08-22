"""
Units Changed Domain Event.

This event is published when a fund's units change,
enabling loose coupling between unit updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class UnitsChangedEvent(FundDomainEvent):
    """
    Domain event for when fund units change.
    
    This event is published whenever the number of units in a fund changes,
    typically due to unit purchases, sales, or other unit-related transactions.
    The event contains the old and new unit counts along with the reason
    for the change.
    
    Attributes:
        old_units (Decimal): Previous number of units
        new_units (Decimal): New number of units after the change
        change_reason (str): Reason for the units change
        change_amount (Decimal): Absolute change in units
        unit_price (Decimal): Price per unit at the time of change
        event_type (str): Type identifier for this event
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        old_units: Decimal,
        new_units: Decimal,
        change_reason: str,
        unit_price: Optional[Decimal] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a units changed event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the units changed
            old_units: Previous number of units
            new_units: New number of units
            change_reason: Reason for the units change
            unit_price: Price per unit at the time of change
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.old_units = old_units
        self.new_units = new_units
        self.change_reason = change_reason
        self.unit_price = unit_price
        self.change_amount = new_units - old_units
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the event type identifier."""
        return DomainEventType.UNITS_CHANGED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'old_units': str(self.old_units),
            'new_units': str(self.new_units),
            'change_reason': self.change_reason,
            'change_amount': str(self.change_amount),
            'unit_price': str(self.unit_price) if self.unit_price else None
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with units change details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"old_units={self.old_units}, "
            f"new_units={self.new_units}, "
            f"change_reason='{self.change_reason}')"
        )
