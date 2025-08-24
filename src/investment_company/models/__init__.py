"""
Investment Company Models Package.

This package contains the investment company models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.

Architecture mirrors the successful fund refactor pattern.
"""

# Import models
from .contact import Contact
from .investment_company import InvestmentCompany

__all__ = [
    'Contact',
    'InvestmentCompany',
]

# Version information
__version__ = '2.0.0'

# Architecture information
__architecture__ = 'service-oriented'
__pattern__ = 'event-driven'
__responsibility__ = 'data-persistence-only'
__structure__ = 'separated-models'
