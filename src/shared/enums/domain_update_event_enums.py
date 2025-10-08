"""
Domain Update Event Enums.

This module contains all enum definitions for the domain update event system.
"""

from enum import Enum

class DomainObjectType(Enum):
    """
    Domain object type enum.
    """
    # Banking
    BANK = "BANK"
    BANK_ACCOUNT = "BANK_ACCOUNT"
    BANK_ACCOUNT_BALANCE = "BANK_ACCOUNT_BALANCE"

    # Entity
    ENTITY = "ENTITY"

    # Fund
    FUND = "FUND"
    FUND_EVENT = "FUND_EVENT"
    FUND_EVENT_CASH_FLOW = "FUND_EVENT_CASH_FLOW"
    FUND_TAX_STATEMENT = "FUND_TAX_STATEMENT"

    # Investment Company
    INVESTMENT_COMPANY = "INVESTMENT_COMPANY"
    CONTACT = "CONTACT"

    # Rates
    FX_RATE = "FX_RATE"
    RISK_FREE_RATE = "RISK_FREE_RATE"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'DomainObjectType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid DomainObjectType: {value}. Must be one of: {[f.value for f in cls]}")


class SortFieldDomainUpdateEvent(Enum):
    """
    Sort field enum for domain update events.
    """
    TIMESTAMP = "TIMESTAMP"
    DOMAIN_OBJECT_TYPE = "DOMAIN_OBJECT_TYPE"
    DOMAIN_OBJECT_ID = "DOMAIN_OBJECT_ID"
    EVENT_OPERATION = "EVENT_OPERATION"
    FUND_EVENT_TYPE = "FUND_EVENT_TYPE"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldDomainUpdateEvent':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldDomainUpdateEvent: {value}. Must be one of: {[f.value for f in cls]}")
