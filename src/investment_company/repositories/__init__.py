"""
Investment Company Repositories.

This module provides the data access layer abstraction for the investment company system.
Repositories handle all database operations and provide a clean interface
for business logic components to interact with data.
"""

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.repositories.company_contact_repository import CompanyContactRepository

__all__ = [
    'CompanyRepository',
    'CompanyContactRepository',
]
