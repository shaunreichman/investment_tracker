"""
Risk Free Rate Enums.

This module provides the risk free rate enums,
representing risk free rates in the system.
"""

from enum import Enum

class RiskFreeRateType(Enum):
    """Risk Free Rate Type."""
    GOVERNMENT_BOND = "GOVERNMENT_BOND"
    LIBOR = "LIBOR"
    SOFR = "SOFR"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value

    @classmethod
    def from_string(cls, value: str) -> 'RiskFreeRateType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid RiskFreeRateType: {value}. Must be one of: {[s.value for s in cls]}")


class SortFieldRiskFreeRate(Enum):
    """Sort Field Risk Free Rate."""
    DATE = "DATE"
    CURRENCY = "CURRENCY"

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
        
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldRiskFreeRate':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldRiskFreeRate: {value}. Must be one of: {[s.value for s in cls]}")