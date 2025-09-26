"""
Domain Fund Event Enums.

This module contains all enum definitions for the domain fund event system.
"""

from enum import Enum

class SortFieldDomainFundEvent(Enum):
    """
    Sort field enum for domain fund events.
    """
    TIMESTAMP = "TIMESTAMP"
    EVENT_TYPE = "EVENT_TYPE"
    EVENT_OPERATION = "EVENT_OPERATION"
    FUND_EVENT_ID = "FUND_EVENT_ID"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldDomainFundEvent':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldDomainFundEvent: {value}. Must be one of: {[f.value for f in cls]}")
