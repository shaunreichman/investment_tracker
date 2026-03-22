"""
Bank Enums.

This module contains all enum definitions for the banking system.
"""

from enum import Enum

class BankType(Enum):
    """
    Banking institution classification.
    
    Defines the type of banking institution for regulatory and operational purposes.
    
    Values:
        COMMERCIAL: Commercial bank (retail and business banking)
        INVESTMENT: Investment bank (securities and advisory)
        CENTRAL: Central bank (monetary policy and regulation)
        COOPERATIVE: Cooperative bank (member-owned)
        DIGITAL: Digital-only bank (online banking)
    """
    COMMERCIAL = 'COMMERCIAL'
    INVESTMENT = 'INVESTMENT'
    CENTRAL = 'CENTRAL'
    COOPERATIVE = 'COOPERATIVE'
    DIGITAL = 'DIGITAL'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'BankType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid BankType: {value}. Must be one of: {[t.value for t in cls]}")

class BankStatus(Enum):
    """
    Bank status enum.
    """
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    CLOSED = 'CLOSED'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'BankStatus':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid BankStatus: {value}. Must be one of: {[s.value for s in cls]}")

class SortFieldBank(Enum):
    """
    Sort field enum for banks.
    """
    NAME = 'NAME'
    COUNTRY = 'COUNTRY'
    CURRENCY = 'CURRENCY'
    TYPE = 'TYPE'
    STATUS = 'STATUS'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldBank':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldBank: {value}. Must be one of: {[f.value for f in cls]}")
