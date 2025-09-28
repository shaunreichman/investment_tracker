"""
Company Enums.

This module provides enums for investment company operations,
including domain event types and company-specific enums.
"""

from enum import Enum


class CompanyType(Enum):
    """
    Company type enum for database constraints.
    
    Defines the valid types of investment companies that can be stored
    in the database. This enum is used directly in the database model
    to ensure data integrity and type safety.
    
    Values:
        PRIVATE_EQUITY: Private equity investment firm
        VENTURE_CAPITAL: Venture capital investment firm
        REAL_ESTATE: Real estate investment firm
        INFRASTRUCTURE: Infrastructure investment firm
        CREDIT: Credit/debt investment firm
        HEDGE_FUND: Hedge fund management firm
        FAMILY_OFFICE: Family office investment firm
        INVESTMENT_BANK: Investment banking firm
        ASSET_MANAGEMENT: Asset management firm
        OTHER: Other type of investment firm
    """
    PRIVATE_EQUITY = 'Private Equity'
    VENTURE_CAPITAL = 'Venture Capital'
    REAL_ESTATE = 'Real Estate'
    INFRASTRUCTURE = 'Infrastructure'
    CREDIT = 'Credit'
    HEDGE_FUND = 'Hedge Fund'
    FAMILY_OFFICE = 'Family Office'
    INVESTMENT_BANK = 'Investment Bank'
    ASSET_MANAGEMENT = 'Asset Management'
    INVESTMENT_GROUP = 'Investment Group'
    OTHER = 'Other'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'CompanyType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid CompanyType: {value}. Must be one of: {[t.value for t in cls]}")


class CompanyStatus(Enum):
    """
    Company status enum for database constraints.
    
    Defines the possible statuses for investment companies.
    This enum is used directly in the database model to ensure
    data integrity and type safety.
    
    Values:
        ACTIVE: Company is active and operational
        INACTIVE: Company is inactive
        SUSPENDED: Company operations are suspended
        CLOSED: Company has closed operations
    """
    ACTIVE = 'ACTIVE'
    INACTIVE = 'INACTIVE'
    COMPLETED = 'COMPLETED'
    SUSPENDED = 'SUSPENDED'
    CLOSED = 'CLOSED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'CompanyStatus':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid CompanyStatus: {value}. Must be one of: {[s.value for s in cls]}")


class SortFieldCompany(Enum):
    """
    Sort field enum for companies.
    """
    NAME = 'NAME'
    STATUS = 'STATUS'
    START_DATE = 'START_DATE'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> 'SortFieldCompany':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldCompany: {value}. Must be one of: {[t.value for t in cls]}")
