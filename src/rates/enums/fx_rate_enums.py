"""
FX Rate Enums.

This module provides the FX rate enums,
representing FX rates in the system.
"""

from enum import Enum

class SortFieldFxRate(Enum):
    """Sort Field FX Rate."""
    DATE = "DATE"
    FROM_CURRENCY = "FROM_CURRENCY"
    TO_CURRENCY = "TO_CURRENCY"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
        
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldFxRate':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldFxRate: {value}. Must be one of: {[s.value for s in cls]}")