"""
Fund Tax Statement Enums.

This module contains all enum definitions for the fund tax statement system.
"""

from enum import Enum



class SortFieldFundTaxStatement(Enum):
    """
    Sort field enum for fund tax statements.
    """
    TAX_PAYMENT_DATE = 'TAX_PAYMENT_DATE'
    FINANCIAL_YEAR = 'FINANCIAL_YEAR'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldFundTaxStatement':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldFundTaxStatement: {value}. Must be one of: {[f.value for f in cls]}")