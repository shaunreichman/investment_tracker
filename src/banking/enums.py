"""
Banking Enums Module.

This module contains all enum definitions for the banking system.
Following enterprise best practices for clean separation of concerns.

Core Banking Enums:
- Country: ISO 3166-1 alpha-2 country codes for banking operations
- Currency: ISO 4217 currency codes for banking operations
- AccountStatus: Bank account lifecycle status
- BankType: Banking institution classification
- AccountType: Bank account classification types

System & API Enums:
- SortOrder: Sorting order (ASC, DESC)
- SortField: Sortable fields (name, country, currency, etc.)
- Environment: Deployment environment (development, staging, production)

This module provides comprehensive type safety and business logic
encapsulation for the entire banking system.
"""

from enum import Enum


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
    
    @classmethod
    def has_swift_requirement(cls, country: 'Country') -> bool:
        """Check if country requires SWIFT/BIC codes for banking operations."""
        swift_required_countries = {
            cls.US, cls.UK, cls.CA, cls.DE, cls.FR, cls.JP
        }
        return country in swift_required_countries


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
    def is_major_currency(cls, currency: 'Currency') -> bool:
        """Check if currency is a major world currency."""
        major_currencies = {
            cls.USD, cls.EUR, cls.GBP, cls.JPY, cls.CHF
        }
        return currency in major_currencies
 
    @classmethod
    def get_decimal_places(cls, currency: 'Currency') -> int:
        """Get the number of decimal places for a currency."""
        # Most currencies use 2 decimal places
        if currency in {cls.JPY}:  # Japanese Yen uses 0 decimal places
            return 0
        return 2


class AccountStatus(Enum):
    """
    Bank account status for lifecycle management.
    
    Represents the current operational status of a bank account.
    
    Values:
        ACTIVE: Account is active and can perform transactions
        SUSPENDED: Account is temporarily suspended (no transactions)
        CLOSED: Account is permanently closed
        PENDING_VERIFICATION: Account is awaiting verification
        RESTRICTED: Account has restrictions on certain operations
    """
    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'
    CLOSED = 'CLOSED'
    PENDING_VERIFICATION = 'PENDING_VERIFICATION'
    RESTRICTED = 'RESTRICTED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'AccountStatus':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid AccountStatus: {value}. Must be one of: {[s.value for s in cls]}")
    
    @classmethod
    def can_transact(cls, status: 'AccountStatus') -> bool:
        """Check if account can perform transactions."""
        return status == cls.ACTIVE
    
    @classmethod
    def is_operational(cls, status: 'AccountStatus') -> bool:
        """Check if account is operational (not closed)."""
        return status != cls.CLOSED
    
    @classmethod
    def requires_verification(cls, status: 'AccountStatus') -> bool:
        """Check if account requires verification."""
        return status == cls.PENDING_VERIFICATION


class BankType(Enum):
    """
    Banking institution classification.
    
    Defines the type of banking institution for regulatory and operational purposes.
    
    Values:
        COMMERCIAL: Commercial bank (retail and business banking)
        INVESTMENT: Investment bank (securities and advisory)
        CENTRAL: Central bank (monetary policy and regulation)
        COOPERATIVE: Cooperative bank (member-owned)
        ISLAMIC: Islamic bank (Sharia-compliant banking)
        DIGITAL: Digital-only bank (online banking)
    """
    COMMERCIAL = 'COMMERCIAL'
    INVESTMENT = 'INVESTMENT'
    CENTRAL = 'CENTRAL'
    COOPERATIVE = 'COOPERATIVE'
    ISLAMIC = 'ISLAMIC'
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
    
    @classmethod
    def requires_licensing(cls, bank_type: 'BankType') -> bool:
        """Check if bank type requires special licensing."""
        licensed_types = {
            cls.INVESTMENT, cls.CENTRAL, cls.ISLAMIC
        }
        return bank_type in licensed_types
    
    @classmethod
    def is_digital_native(cls, bank_type: 'BankType') -> bool:
        """Check if bank type is digital-native."""
        return bank_type == cls.DIGITAL


class AccountType(Enum):
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
    def from_string(cls, value: str) -> 'AccountType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid AccountType: {value}. Must be one of: {[t.value for t in t]}")
    
    @classmethod
    def earns_interest(cls, account_type: 'AccountType') -> bool:
        """Check if account type typically earns interest."""
        interest_accounts = {
            cls.SAVINGS, cls.INVESTMENT
        }
        return account_type in interest_accounts
    
    @classmethod
    def requires_kyc(cls, account_type: 'AccountType') -> bool:
        """Check if account type requires KYC verification."""
        kyc_required = {
            cls.BUSINESS, cls.TRUST, cls.INVESTMENT
        }
        return account_type in kyc_required


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


class BankingDomainEventType(Enum):
    """
    Banking domain event type enum.
    
    Defines business domain events that are published when significant
    state changes occur in the banking system.
    
    Values:
        BANK_CREATED: Bank was created
        BANK_UPDATED: Bank was updated
        BANK_DELETED: Bank was deleted
        BANK_ACCOUNT_CREATED: Bank account was created
        BANK_ACCOUNT_UPDATED: Bank account was updated
        BANK_ACCOUNT_DELETED: Bank account was deleted
        CURRENCY_CHANGED: Account currency was changed
        ACCOUNT_STATUS_CHANGED: Account status was changed
    """
    BANK_CREATED = 'BANK_CREATED'
    BANK_UPDATED = 'BANK_UPDATED'
    BANK_DELETED = 'BANK_DELETED'
    BANK_ACCOUNT_CREATED = 'BANK_ACCOUNT_CREATED'
    BANK_ACCOUNT_UPDATED = 'BANK_ACCOUNT_UPDATED'
    BANK_ACCOUNT_DELETED = 'BANK_ACCOUNT_DELETED'
    CURRENCY_CHANGED = 'CURRENCY_CHANGED'
    ACCOUNT_STATUS_CHANGED = 'ACCOUNT_STATUS_CHANGED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


# Convenience functions for common enum operations
def get_all_enum_values(enum_class: type) -> list:
    """Get all values from an enum class."""
    return [e.value for e in enum_class]


def validate_enum_value(enum_class: type, value: str) -> bool:
    """Validate if a string value is valid for an enum class."""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False


def get_enum_display_name(enum_instance: Enum) -> str:
    """Get a human-readable display name for an enum value."""
    return enum_instance.value.replace('_', ' ').title()
