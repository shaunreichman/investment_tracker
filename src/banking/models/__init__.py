"""
Banking Models Package.

This package contains the banking models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.
"""

# Import banking models
from src.banking.models.bank import Bank
from src.banking.models.bank_account import BankAccount

__all__ = [
    'Bank',
    'BankAccount'
]

# Version information
__version__ = '2.0.0'

# Architecture information
__architecture__ = 'service-oriented'
__pattern__ = 'event-driven'
__responsibility__ = 'data-persistence-only'
