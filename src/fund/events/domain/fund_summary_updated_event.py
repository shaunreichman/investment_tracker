"""
Fund Summary Updated Domain Event.

This event is published when a fund's summary information is updated,
enabling loose coupling between summary updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class FundSummaryUpdatedEvent(FundDomainEvent):
    """
    Domain event for when fund summary fields are updated.
    
    This event is published whenever fund summary fields like
    equity balance, cost basis, or NAV values are updated.
    
    Attributes:
        event_type (str): Type of summary update (e.g., 'CAPITAL_EVENT_PROCESSED', 'NAV_UPDATE')
        metadata (dict): Additional event data including original event details
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        summary_type: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a fund summary updated event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the summary was updated
            summary_type: Type of summary update that occurred
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.summary_type = summary_type
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the domain event type identifier."""
        return DomainEventType.FUND_SUMMARY_UPDATED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'event_type': self.event_type
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with fund summary update details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"event_type='{self.event_type}', "
            f"date={self.event_date})"
        )
