"""
Banking Repositories.

This module provides data access operations for banking entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Bank data access operations
- Bank account data access operations
- Banking summary data and aggregated calculations
- Caching strategies for performance optimization
"""

from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository

__all__ = [
    "BankRepository",
    "BankAccountRepository", 
]
