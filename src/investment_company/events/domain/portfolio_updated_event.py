"""
Portfolio Updated Domain Event.

This module provides the PortfolioUpdatedEvent class,
representing when a company's portfolio is updated.
"""

from datetime import date
from typing import Dict, Any

from src.investment_company.events.domain.base_event import CompanyDomainEvent
from src.investment_company.enums import CompanyDomainEventType


class PortfolioUpdatedEvent(CompanyDomainEvent):
    """
    Domain event for when a company's portfolio is updated.
    
    This event is published when portfolio changes occur, such as
    adding/removing funds, updating fund information, or recalculating
    portfolio summaries.
    
    Attributes:
        company_id: ID of the company whose portfolio was updated
        event_date: Date when the portfolio was updated
        fund_id: ID of the fund involved in the update (if applicable)
        operation: Type of portfolio operation performed
        metadata: Additional event-specific data
    """
    
    def __init__(
        self,
        company_id: int,
        event_date: date,
        fund_id: int = None,
        operation: str = None,
        metadata: Dict[str, Any] = None
    ):
        """
        Initialize a new portfolio updated event.
        
        Args:
            company_id: ID of the company whose portfolio was updated
            event_date: Date when the portfolio was updated
            fund_id: ID of the fund involved in the update (if applicable)
            operation: Type of portfolio operation performed
            metadata: Additional event-specific data
        """
        super().__init__(company_id, event_date, metadata)
        self.fund_id = fund_id
        self.operation = operation
        
        # Add portfolio-specific data to metadata
        if metadata is None:
            metadata = {}
        metadata.update({
            'fund_id': fund_id,
            'operation': operation
        })
        self.metadata = metadata
    
    @property
    def event_type(self) -> CompanyDomainEventType:
        """Get the type of this event."""
        return CompanyDomainEventType.PORTFOLIO_UPDATED
    
    def __repr__(self) -> str:
        """String representation of the event."""
        return (
            f"{self.__class__.__name__}("
            f"event_id='{self.event_id}', "
            f"company_id={self.company_id}, "
            f"fund_id={self.fund_id}, "
            f"operation='{self.operation}', "
            f"event_date={self.event_date})"
        )
