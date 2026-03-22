"""
Bank Account Enums.

This module contains all enum definitions for the banking account system.
"""

from enum import Enum

class BankAccountType(Enum):
    """
    Bank account classification types.
    
    Defines the type of bank account for regulatory and operational purposes.
    
    Values:
        CHECKING: Checking/current account (daily transactions)
        SAVINGS: Savings account (interest-bearing)
        INVESTMENT: Investment account (securities trading)
        BUSINESS: Business account (commercial operations)
        TRUST: Trust account (fiduciary operations)
        JOINT: Joint account (multiple owners)
    """
    CHECKING = 'CHECKING'
    SAVINGS = 'SAVINGS'
    INVESTMENT = 'INVESTMENT'
    BUSINESS = 'BUSINESS'
    TRUST = 'TRUST'
    JOINT = 'JOINT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'BankAccountType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid BankAccountType: {value}. Must be one of: {[t.value for t in cls]}")

class BankAccountStatus(Enum):
    """
    Bank account status enum.
    """
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    CLOSED = 'CLOSED'
    SUSPENDED = 'SUSPENDED'
    OVERDRAFT = 'OVERDRAFT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'BankAccountStatus':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid BankAccountStatus: {value}. Must be one of: {[s.value for s in cls]}")

class SortFieldBankAccount(Enum):
    """
    Sort field enum for bank accounts.
    """
    NAME = 'NAME'
    ACCOUNT_NUMBER = 'ACCOUNT_NUMBER'
    CURRENCY = 'CURRENCY'
    STATUS = 'STATUS'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldBankAccount':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldBankAccount: {value}. Must be one of: {[f.value for f in cls]}")