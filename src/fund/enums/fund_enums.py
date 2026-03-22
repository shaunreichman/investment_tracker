"""
Fund Enums.

This module contains all enum definitions for the fund system.
"""

from enum import Enum
from src.shared.enums.shared_enums import Country

class FundStatus(Enum):
    """
    Fund lifecycle status enum.
    
    Represents the current state of a fund in its lifecycle.
    
    Values:
        ACTIVE: Fund has capital at risk and is actively managed
        SUSPENDED: Fund temporarily suspended/on hold (equity balance may be > 0 but no new activity)
        REALIZED: All capital has been returned, fund is realized
        COMPLETED: Fund is realized and all tax obligations are complete
    """
    ACTIVE = 'ACTIVE'
    SUSPENDED = 'SUSPENDED'
    REALIZED = 'REALIZED'
    COMPLETED = 'COMPLETED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'FundStatus':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FundStatus: {value}. Must be one of: {[s.value for s in cls]}")


class FundTrackingType(Enum):
    """
    Fund tracking type enum.
    
    Determines how the fund tracks and calculates values.
    
    Values:
        COST_BASED: Fund tracks cost basis and commitment amounts
        NAV_BASED: Fund tracks NAV per share and unit-based calculations
    """
    COST_BASED = 'COST_BASED'
    NAV_BASED = 'NAV_BASED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'FundTrackingType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FundTrackingType: {value}. Must be one of: {[t.value for t in cls]}")

class FundInvestmentType(Enum):
    """
    Fund investment type enum.
    
    Determines the type of investment for a fund.
    """
    PRIVATE_EQUITY = 'PRIVATE_EQUITY'
    VENTURE_CAPITAL = 'VENTURE_CAPITAL'
    PRIVATE_DEBT = 'PRIVATE_DEBT'
    REAL_ESTATE = 'REAL_ESTATE'
    INFRASTRUCTURE = 'INFRASTRUCTURE'
    OTHER = 'OTHER'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'FundInvestmentType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FundInvestmentType: {value}. Must be one of: {[t.value for t in cls]}")


class FundTaxStatementFinancialYearType(Enum):
    """
    Fund tax statement financial year type enum.
    """
    CALENDAR_YEAR = 'CALENDAR_YEAR'
    HALF_YEAR = 'HALF_YEAR'

    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'FundTaxStatementFinancialYearType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FundTaxStatementFinancialYearType: {value}. Must be one of: {[f.value for f in cls]}")
    
TAX_JURISDICTION_TO_FINANCIAL_YEAR_TYPE_MAP = {
    Country.AU: FundTaxStatementFinancialYearType.HALF_YEAR,
    Country.SG: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.NZ: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.HK: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.UK: FundTaxStatementFinancialYearType.HALF_YEAR,
    Country.US: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.CA: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.JP: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.KR: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
    Country.CN: FundTaxStatementFinancialYearType.CALENDAR_YEAR,
}

# Capital gains discounting is enabled for Australia only
TAX_JURISDICTION_TO_CAPITAL_GAINS_DISCOUNTING = {
    Country.AU: {
        'enabled': True,
        'duration_months': 12,
        'percentage': 50,
    },
    Country.SG: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.NZ: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.HK: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.UK: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.US: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.CA: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.JP: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.KR: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
    Country.CN: {
        'enabled': False,
        'duration_months': 0,
        'percentage': 0,
    },
}

class SortFieldFund(Enum):
    """
    Sort field enum.
    
    Defines the fields that can be used for sorting in APIs and queries.
    
    Values:
        START_DATE: Sort by fund start date
        NAME: Sort by fund name
        STATUS: Sort by fund status
        COMMITMENT_AMOUNT: Sort by commitment amount
        CURRENT_EQUITY_BALANCE: Sort by current equity balance
        CREATED_AT: Sort by creation timestamp
        UPDATED_AT: Sort by last update timestamp
    """
    START_DATE = 'START_DATE'
    NAME = 'NAME'
    STATUS = 'STATUS'
    COMMITMENT_AMOUNT = 'COMMITMENT_AMOUNT'
    CURRENT_EQUITY_BALANCE = 'CURRENT_EQUITY_BALANCE'
    CREATED_AT = 'CREATED_AT'
    UPDATED_AT = 'UPDATED_AT'
    EVENT_DATE = 'EVENT_DATE'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldFund':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldFund: {value}. Must be one of: {[f.value for f in cls]}")
