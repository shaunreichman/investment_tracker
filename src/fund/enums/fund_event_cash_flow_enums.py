"""
Fund Event Cash Flow Enums.

This module contains all enum definitions for the fund event cash flow system.
"""

from enum import Enum


class CashFlowDirection(Enum):
    """
    Cash flow direction enum.
    
    Indicates the direction of money flow from the investor's perspective.
    
    Values:
        INFLOW: Money received by investor (e.g., distributions, returns)
        OUTFLOW: Money paid out by investor (e.g., capital calls, fees)
    """
    INFLOW = 'INFLOW'
    OUTFLOW = 'OUTFLOW'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'CashFlowDirection':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid CashFlowDirection: {value}. Must be one of: {[d.value for d in cls]}")
    
    @classmethod
    def is_incoming(cls, direction: 'CashFlowDirection') -> bool:
        """Check if cash flow direction is incoming to investor."""
        return direction == cls.INFLOW
    
    @classmethod
    def is_outgoing(cls, direction: 'CashFlowDirection') -> bool:
        """Check if cash flow direction is outgoing from investor."""
        return direction == cls.OUTFLOW


class SortFieldFundEventCashFlow(Enum):
    """
    Sort field enum.
    
    Defines the fields that can be used for sorting in APIs and queries.

    Values:
        TRANSFER_DATE: Sort by transfer date
        AMOUNT: Sort by amount
        CREATED_AT: Sort by creation timestamp
        UPDATED_AT: Sort by last update timestamp
    """

    TRANSFER_DATE = 'TRANSFER_DATE'
    AMOUNT = 'AMOUNT'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldFundEventCashFlow':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldFundEventCashFlow: {value}. Must be one of: {[f.value for f in cls]}")
