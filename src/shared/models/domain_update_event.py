"""
Domain Update Event Model.

This module provides the DomainUpdateEvent model class, representing domain update events in the fund system.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import Any, Dict
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation
from src.shared.enums.domain_update_event_enums import DomainObjectType

class DomainUpdateEvent(Base):
    """
    Model representing a domain update event in the fund system.
    This is used to track secondary changes to the fund that are a result of a fund event.
    """
    
    __tablename__ = 'domain_update_events'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key

    domain_object_type = Column(Enum(DomainObjectType), nullable=False)  # (SYSTEM) type of domain object
    domain_object_id = Column(Integer, nullable=False)  # (SYSTEM) ID of the domain object
    event_operation = Column(Enum(EventOperation), nullable=False)  # (SYSTEM) operation on the fund event

    fund_event_type = Column(Enum(EventType), nullable=True)  # (SYSTEM) type of fund event if the Domain Object is a Fund Event
    
    event_data = Column(JSON, nullable=True)  # (SYSTEM) event-specific data payload
    
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # (SYSTEM) when event occurred
    

    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the domain update event model.
        
        Returns:
            Dict[str, str]: Field classification for the domain fund event model
        """
        return {
            'id': 'SYSTEM',
            'domain_object_type': 'SYSTEM',
            'domain_object_id': 'SYSTEM',
            'event_operation': 'SYSTEM',
            'fund_event_type': 'SYSTEM',
            'event_data': 'SYSTEM',
            'timestamp': 'SYSTEM',
        }


class DomainFieldChange:
    """
    Model representing a domain field change in the overall system.
    This will not be stored in the database, but will be used to create the domain event.

    Attributes:
        object: Whether the event is related to a fund or a company or a fund event (FUND/COMPANY/FUND_EVENT)
        object_id: The ID of the object that changed
        field_name: The name of the field that changed
        old_value: The old value of the field
        new_value: The new value of the field
    """
    
    def __init__(self, domain_object_type: DomainObjectType, domain_object_id: int, field_name: str, old_value: Any, new_value: Any):
        self.domain_object_type = domain_object_type
        self.domain_object_id = domain_object_id
        self.field_name = field_name
        self.old_value = old_value
        self.new_value = new_value

    def to_dict(self) -> dict:
        def serialize_value(value):
            """Convert non-serializable values to strings."""
            if value is None:
                return None
            elif hasattr(value, 'isoformat'):  # datetime, date objects
                return value.isoformat()
            elif hasattr(value, 'value'):  # enum objects
                return value.value
            else:
                return value
        
        return {
            'domain_object_type': serialize_value(self.domain_object_type),
            'domain_object_id': self.domain_object_id,
            'field_name': self.field_name,
            'old_value': serialize_value(self.old_value),
            'new_value': serialize_value(self.new_value)
        }