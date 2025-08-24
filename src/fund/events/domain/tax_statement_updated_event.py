"""
Tax Statement Updated Domain Event.

This event is published when a tax statement is updated for a fund,
enabling loose coupling between tax statement updates and dependent components.
"""

from typing import Dict, Any, Optional
from datetime import date, datetime
from decimal import Decimal

from src.fund.enums import DomainEventType
from src.fund.events.domain.base_event import FundDomainEvent


class TaxStatementUpdatedEvent(FundDomainEvent):
    """
    Domain event for when a tax statement is updated.
    
    This event is published whenever a tax statement is updated in the
    fund system. It contains information about the tax statement that
    was updated and the type of update that occurred.
    
    Attributes:
        tax_statement_id (int): ID of the updated tax statement
        update_type (str): Type of update (e.g., 'created', 'modified', 'finalized')
        financial_year (str): Financial year of the tax statement
        entity_id (int): ID of the entity associated with the tax statement
        event_type (str): Type identifier for this event
    """
    
    def __init__(
        self,
        fund_id: int,
        event_date: date,
        tax_statement_id: int,
        update_type: str,
        financial_year: str,
        entity_id: int,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize a tax statement updated event.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when the tax statement was updated
            tax_statement_id: ID of the updated tax statement
            update_type: Type of update that occurred
            financial_year: Financial year of the tax statement
            entity_id: ID of the entity associated with the tax statement
            metadata: Additional event data
        """
        super().__init__(fund_id, event_date, metadata)
        self.tax_statement_id = tax_statement_id
        self.update_type = update_type
        self.financial_year = financial_year
        self.entity_id = entity_id
    
    @property
    def event_type(self) -> DomainEventType:
        """Get the event type identifier."""
        return DomainEventType.TAX_STATEMENT_UPDATED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary with event-specific data."""
        base_dict = super().to_dict()
        base_dict.update({
            'tax_statement_id': self.tax_statement_id,
            'update_type': self.update_type,
            'financial_year': self.financial_year,
            'entity_id': self.entity_id
        })
        return base_dict
    
    def __repr__(self) -> str:
        """String representation with tax statement update details."""
        return (
            f"{self.__class__.__name__}("
            f"fund_id={self.fund_id}, "
            f"tax_statement_id={self.tax_statement_id}, "
            f"update_type='{self.update_type}', "
            f"financial_year='{self.financial_year}')"
        )
