"""
Bank Account Balance Enums.
"""

from enum import Enum

class SortFieldBankAccountBalance(Enum):
    """
    Sort field enum for bank account balances.
    """
    DATE = 'DATE'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldBankAccountBalance':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldBankAccountBalance: {value}. Must be one of: {[f.value for f in cls]}")