"""
Investment Company Repositories.

This package provides repository classes for clean data access abstraction
in the investment company domain, following the repository pattern established
in the fund refactor.
"""

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.repositories.company_contact_repository import CompanyContactRepository

__all__ = [
    'CompanyRepository',
    'CompanyContactRepository',
]
