"""
Company Contact Enums.

This module provides enums for company contact operations,
including domain event types and company-specific enums.
"""

from enum import Enum

class SortFieldContact(Enum):
    """
    Sort field enum for contacts.
    """
    NAME = 'NAME'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> 'SortFieldContact':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldContact: {value}. Must be one of: {[t.value for t in cls]}")
