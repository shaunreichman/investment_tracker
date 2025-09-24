"""
Banking Module.

This module provides comprehensive banking functionality with enterprise-grade architecture.
Following the exact patterns established in the fund refactor for consistency and maintainability.

Core Components:
- Models: Bank and BankAccount with clean data persistence
- Services: Business logic and validation services
- Repositories: Data access abstraction layer
- Events: Event-driven architecture for banking updates
- Enums: Type-safe enums for countries, currencies, and statuses

Architecture Features:
- Clean separation of concerns
- Event-driven updates
- Comprehensive validation
- Repository pattern
- Service layer business logic
- Cross-module integration
"""

# Import core components
from src.banking.models import Bank, BankAccount
from src.banking.enums.bank_enums import BankType, SortFieldBank, BankStatus
from src.banking.enums.bank_account_enums import BankAccountType, SortFieldBankAccount, BankAccountStatus

# Export main components
__all__ = [
    # Models
    'Bank',
    'BankAccount',
    
    # Enums
    'BankType',
    'BankStatus',
    'BankAccountType',
    'SortFieldBank',
    'SortFieldBankAccount',
    'BankAccountStatus',
]
