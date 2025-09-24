"""
Investment Company Models Package.

This package contains the investment company models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.

Architecture mirrors the successful fund refactor pattern.
"""

# Import models
from src.investment_company.models.contact import Contact
from src.investment_company.models.investment_company import InvestmentCompany

__all__ = [
    'Contact',
    'InvestmentCompany',
]