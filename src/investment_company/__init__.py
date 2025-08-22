"""
Investment Company Module.

This module provides investment company management functionality,
including models, services, repositories, API controllers, and event handling.

Key responsibilities:
- Investment company data models
- Business logic services
- Data access repositories
- API endpoint controllers
- Event-driven architecture
"""

from .models import InvestmentCompany, Contact
from .services import (
    CompanyPortfolioService,
    CompanySummaryService,
    ContactManagementService,
    CompanyValidationService
)
from .repositories import CompanyRepository, ContactRepository
from .api import CompanyController
from .events import (
    BaseCompanyEventHandler,
    CompanyEventHandlerRegistry,
    CompanyUpdateOrchestrator,
    CompanyDomainEvent,
    CompanyCreatedEvent,
    ContactAddedEvent,
    PortfolioUpdatedEvent
)

__all__ = [
    'InvestmentCompany',
    'Contact',
    'CompanyPortfolioService',
    'CompanySummaryService',
    'ContactManagementService',
    'CompanyValidationService',
    'CompanyRepository',
    'ContactRepository',
    'CompanyController',
    'BaseCompanyEventHandler',
    'CompanyEventHandlerRegistry',
    'CompanyUpdateOrchestrator',
    'CompanyDomainEvent',
    'CompanyCreatedEvent',
    'ContactAddedEvent',
    'PortfolioUpdatedEvent',
] 