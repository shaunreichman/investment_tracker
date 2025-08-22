"""
Investment Company Repositories.

This package provides repository classes for clean data access abstraction
in the investment company domain, following the repository pattern established
in the fund refactor.
"""

from .company_repository import CompanyRepository
from .contact_repository import ContactRepository

__all__ = [
    'CompanyRepository',
    'ContactRepository',
]
