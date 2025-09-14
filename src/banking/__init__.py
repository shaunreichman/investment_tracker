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
from src.banking.enums import Country, Currency, AccountStatus, BankType, AccountType, BankingDomainEventType
from src.shared.enums import SortOrder

# Export main components
__all__ = [
    # Models
    'Bank',
    'BankAccount',
    
    # Enums
    'Country',
    'Currency', 
    'AccountStatus',
    'BankType',
    'AccountType',
    'SortOrder',
    'BankingDomainEventType',
]
