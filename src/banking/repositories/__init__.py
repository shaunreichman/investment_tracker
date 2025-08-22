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

from .bank_repository import BankRepository
from .bank_account_repository import BankAccountRepository
from .banking_summary_repository import BankingSummaryRepository

__all__ = [
    "BankRepository",
    "BankAccountRepository", 
    "BankingSummaryRepository"
]
