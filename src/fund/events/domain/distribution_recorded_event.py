"""
Distribution Recorded Domain Event.

This event is published when a distribution is recorded for a fund,
enabling loose coupling between distribution updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType, DistributionType
from src.fund.events.domain.base_event import FundDomainEvent


class DistributionRecordedEvent(FundDomainEvent):
    """
    Domain event for when a distribution is recorded.
    
    This event is published whenever a distribution is recorded in the
    fund system. It contains information about the distribution amount,
    type, tax withholding, and other relevant details.
    
    Attributes:
        distribution_type (str): Type of distribution (e.g., 'dividend', 'return_of_capital')
        amount (Decimal): Gross distribution amount
        tax_withheld (Decimal): Amount of tax withheld
        net_amount (Decimal): Net amount after tax withholding
        event_type (str): Type identifier for this event
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        distribution_type: str,
        amount: Decimal,
        tax_withheld: Decimal = Decimal('0'),
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a distribution recorded event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the distribution was recorded
            distribution_type: Type of distribution
            amount: Gross distribution amount
            tax_withheld: Amount of tax withheld
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.distribution_type = distribution_type
        self.amount = amount
        self.tax_withheld = tax_withheld
        self.net_amount = amount - tax_withheld
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the event type identifier."""
        return DomainEventType.DISTRIBUTION_RECORDED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'distribution_type': self.distribution_type,
            'amount': str(self.amount),
            'tax_withheld': str(self.tax_withheld),
            'net_amount': str(self.net_amount)
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with distribution details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"distribution_type='{self.distribution_type}', "
            f"amount={self.amount}, "
            f"net_amount={self.net_amount})"
        )
