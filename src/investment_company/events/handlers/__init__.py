"""
Investment Company Event Handlers.

This module provides event handlers for the investment company system,
implementing the event-driven architecture for company operations.

Key responsibilities:
- Event processing and validation
- Business logic execution
- Domain event publishing
- Dependent update coordination
"""

from .company_created_handler import CompanyCreatedHandler
from .contact_added_handler import ContactAddedHandler
from .portfolio_updated_handler import PortfolioUpdatedHandler

__all__ = [
    'CompanyCreatedHandler',
    'ContactAddedHandler',
    'PortfolioUpdatedHandler',
]
