"""
Investment Company Events.

This module provides the event-driven architecture for the investment company system,
enabling loose coupling between components through domain events and handlers.

Key responsibilities:
- Domain event definitions
- Event handler implementations
- Event routing and orchestration
- Cross-domain coordination
"""

from .base_handler import BaseCompanyEventHandler
from .registry import CompanyEventHandlerRegistry
from .orchestrator import CompanyUpdateOrchestrator
from .domain import (
    CompanyDomainEvent,
    CompanyCreatedEvent,
    CompanyUpdatedEvent,
    CompanyDeletedEvent,
    ContactAddedEvent,
    PortfolioUpdatedEvent
)

__all__ = [
    'BaseCompanyEventHandler',
    'CompanyEventHandlerRegistry',
    'CompanyUpdateOrchestrator',
    'CompanyDomainEvent',
    'CompanyCreatedEvent',
    'CompanyUpdatedEvent',
    'CompanyDeletedEvent',
    'ContactAddedEvent',
    'PortfolioUpdatedEvent',
]
