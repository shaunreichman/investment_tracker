"""
Investment Company Services.

This module provides business logic services for investment company operations,
implementing clean separation of concerns and enterprise-grade architecture.

Key services:
- CompanyPortfolioService: Portfolio operations and fund coordination
- CompanySummaryService: Portfolio calculations and performance metrics
- ContactManagementService: Contact operations and validation
- CompanyValidationService: Business rule validation and constraints
"""

from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.services.company_service import CompanyService

__all__ = [
    'CompanyPortfolioService',
    'CompanySummaryService', 
    'ContactManagementService',
    'CompanyValidationService',
    'CompanyService',
]
