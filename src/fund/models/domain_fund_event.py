"""
Domain Fund Event Model.

This module provides the DomainFundEvent model class, representing domain fund events in the fund system.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import Any
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation

class DomainFundEvent(Base):
    """
    Model representing a domain fund event in the fund system.
    This is used to track secondary changes to the fund that are a result of a fund event.
    """
    
    __tablename__ = 'domain_fund_events'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (SYSTEM) link to fund
    event_type = Column(Enum(EventType), nullable=False)  # (SYSTEM) type of event
    event_operation = Column(Enum(EventOperation), nullable=False)  # (SYSTEM) operation on the fund event
    fund_event_id = Column(Integer, ForeignKey('fund_events.id'), nullable=False, index=True)  # (SYSTEM) link to fund event
    event_data = Column(JSON, nullable=True)  # (SYSTEM) event-specific data payload
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # (SYSTEM) when event occurred
    
    # Relationships
    fund = relationship("Fund", back_populates="domain_fund_events")


class FundFieldChange:
    """
    Model representing a fund field change in the fund system.
    This will not be stored in the database, but will be used to create the domain event.

    Attributes:
        field_name: The name of the field that changed
        old_value: The old value of the field
        new_value: The new value of the field
    """
    
    def __init__(self, field_name: str, old_value: Any, new_value: Any):
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value

    def to_dict(self) -> dict:
        return {
            'field_name': self.field_name,
            'old_value': self.old_value,
            'new_value': self.new_value
        }