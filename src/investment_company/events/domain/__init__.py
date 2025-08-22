"""
Investment Company Domain Events.

This module provides domain events for the investment company system,
enabling loose coupling between components through event-driven architecture.

Key responsibilities:
- Domain event definitions for company operations
- Event publishing and consumption
- Cross-domain coordination
"""

from .base_event import CompanyDomainEvent
from .company_created_event import CompanyCreatedEvent
from .company_updated_event import CompanyUpdatedEvent
from .company_deleted_event import CompanyDeletedEvent
from .contact_added_event import ContactAddedEvent
from .portfolio_updated_event import PortfolioUpdatedEvent

__all__ = [
    'CompanyDomainEvent',
    'CompanyCreatedEvent',
    'CompanyUpdatedEvent',
    'CompanyDeletedEvent',
    'ContactAddedEvent',
    'PortfolioUpdatedEvent',
]
