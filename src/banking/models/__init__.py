"""
Banking Models Package.

This package contains all banking-related models following enterprise best practices
for clean separation of concerns and maintainability.

Models:
- Bank: Banking institution model
- BankAccount: Bank account model

Enums:
- Country: ISO 3166-1 alpha-2 country codes
- Currency: ISO 4217 currency codes
- AccountStatus: Bank account lifecycle status
- BankType: Banking institution classification
- BankAccountType: Bank account classification types

All models delegate business logic to services for clean separation of concerns.
"""

from src.banking.models.bank import Bank
from src.banking.models.bank_account import BankAccount

# Export models
__all__ = [
    'Bank',
    'BankAccount',
]

# Version information
__version__ = '2.0.0'

# Architecture information
__architecture__ = 'service-oriented'
__pattern__ = 'event-driven'
__responsibility__ = 'data-persistence-only'
