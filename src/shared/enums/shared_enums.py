"""
Shared Enums Module.

This module contains all enum definitions for the shared system.
"""

from enum import Enum

class SortOrder(Enum):
    """
    Sort order enum.
    
    Defines the order for sorting operations in APIs and queries.
    
    Values:
        ASC: Ascending order (A-Z, 1-9, oldest to newest)
        DESC: Descending order (Z-A, 9-1, newest to oldest)
    """
    ASC = 'ASC'
    DESC = 'DESC'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortOrder':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortOrder: {value}. Must be one of: {[o.value for o in cls]}")
    
    @classmethod
    def is_reverse(cls, order: 'SortOrder') -> bool:
        """Check if sort order is reverse/descending."""
        return order == cls.DESC


class EventOperation(Enum):
    """
    Event operation enum.
    
    Defines all possible operations that can occur on an event.
    
    Values:
        CREATE: Event creation operation
        DELETE: Event deletion operation
        UPDATE: Event update operation
    """
    CREATE = 'CREATE'
    UPDATE = 'UPDATE'
    DELETE = 'DELETE'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'EventOperation':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid EventOperation: {value}. Must be one of: {[e.value for e in cls]}")


class Country(Enum):
    """
    ISO 3166-1 alpha-2 country codes for banking operations.
    
    Represents countries where banking operations can occur.
    
    Values:
        AU: Australia (with specific banking regulations)
        US: United States (with SWIFT/BIC requirements)
        UK: United Kingdom (with SWIFT/BIC requirements)
        CA: Canada (with SWIFT/BIC requirements)
        NZ: New Zealand (with specific banking regulations)
        SG: Singapore (with specific banking regulations)
        HK: Hong Kong (with specific banking regulations)
        JP: Japan (with specific banking regulations)
        DE: Germany (with SWIFT/BIC requirements)
        FR: France (with SWIFT/BIC requirements)
        CN: China (with SWIFT/BIC requirements)
        KR: Korea (with SWIFT/BIC requirements)
    """
    AU = 'AU'
    US = 'US'
    UK = 'UK'
    CA = 'CA'
    NZ = 'NZ'
    SG = 'SG'
    HK = 'HK'
    JP = 'JP'
    DE = 'DE'
    FR = 'FR'
    CN = 'CN'
    KR = 'KR'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'Country':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid Country: {value}. Must be one of: {[c.value for c in cls]}")


class Currency(Enum):
    """
    ISO 4217 currency codes for banking operations.
    
    Defines supported currencies for banking operations.
    
    Values:
        AUD: Australian Dollar (primary currency)
        USD: US Dollar (major world currency)
        EUR: Euro (major world currency)
        GBP: British Pound (major world currency)
        CAD: Canadian Dollar
        NZD: New Zealand Dollar
        SGD: Singapore Dollar
        HKD: Hong Kong Dollar
        JPY: Japanese Yen (major world currency)
        CHF: Swiss Franc (major world currency)
        CNY: Chinese Yuan (major world currency)
        KRW: Korean Won (major world currency)
    """
    AUD = 'AUD'
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    CAD = 'CAD'
    NZD = 'NZD'
    SGD = 'SGD'
    HKD = 'HKD'
    JPY = 'JPY'
    CHF = 'CHF'
    CNY = 'CNY'
    KRW = 'KRW'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'Currency':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid Currency: {value}. Must be one of: {[c.value for c in cls]}")
    
    @classmethod
    def get_decimal_places(cls, currency: 'Currency') -> int:
        """Get the number of decimal places for a currency."""
        # Most currencies use 2 decimal places
        if currency in {cls.JPY}:  # Japanese Yen uses 0 decimal places
            return 0
        return 2
