"""
Fund Enums Module.

This module contains all enum definitions for the fund system.
Following enterprise best practices for clean separation of concerns.

Core Fund Enums:
- FundStatus: Fund lifecycle status (ACTIVE, REALIZED, COMPLETED)
- FundType: Fund tracking type (COST_BASED, NAV_BASED)
- EventType: Fund event types (capital_call, distribution, etc.)
- DistributionType: Distribution classification types (including franking credits)
- CashFlowDirection: Cash flow direction (INFLOW, OUTFLOW)
- TaxPaymentType: Tax payment classification types
- GroupType: Event grouping for reporting and analysis
- TaxJurisdiction: Tax jurisdiction for entities and funds

System & API Enums:
- SortOrder: Sorting order (ASC, DESC)
- SortField: Sortable fields (name, date, amount, etc.)
- Environment: Deployment environment (development, staging, production)
- Currency: Supported currencies (AUD, USD, EUR, etc.)

This module provides comprehensive type safety and business logic
encapsulation for the entire investment tracking system.
"""

from enum import Enum


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


class FundType(Enum):
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
    def from_string(cls, value: str) -> 'FundType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid FundType: {value}. Must be one of: {[t.value for t in cls]}")


class EventType(Enum):
    """
    Fund event type enum.
    
    Defines all possible types of events that can occur in a fund.
    
    Values:
        CAPITAL_CALL: Capital call event
        RETURN_OF_CAPITAL: Return of capital event
        DISTRIBUTION: Distribution event
        UNIT_PURCHASE: Unit purchase event
        UNIT_SALE: Unit sale event
        NAV_UPDATE: NAV update event
        DAILY_RISK_FREE_INTEREST_CHARGE: Daily interest charge
        EOFY_DEBT_COST: End of financial year debt cost
        TAX_PAYMENT: Tax payment event
    """
    CAPITAL_CALL = 'CAPITAL_CALL'
    RETURN_OF_CAPITAL = 'RETURN_OF_CAPITAL'
    DISTRIBUTION = 'DISTRIBUTION'
    UNIT_PURCHASE = 'UNIT_PURCHASE'
    UNIT_SALE = 'UNIT_SALE'
    NAV_UPDATE = 'NAV_UPDATE'
    DAILY_RISK_FREE_INTEREST_CHARGE = 'DAILY_RISK_FREE_INTEREST_CHARGE'
    EOFY_DEBT_COST = 'EOFY_DEBT_COST'
    TAX_PAYMENT = 'TAX_PAYMENT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'EventType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid EventType: {value}. Must be one of: {[e.value for e in cls]}")
    
    @classmethod
    def is_equity_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is an equity event."""
        equity_events = {
            cls.CAPITAL_CALL,
            cls.RETURN_OF_CAPITAL,
            cls.UNIT_PURCHASE,
            cls.UNIT_SALE
        }
        return event_type in equity_events
    
    @classmethod
    def is_distribution_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is a distribution event."""
        return event_type == cls.DISTRIBUTION
    
    @classmethod
    def is_system_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is a system-generated event."""
        system_events = {
            cls.DAILY_RISK_FREE_INTEREST_CHARGE,
            cls.EOFY_DEBT_COST,
            cls.TAX_PAYMENT
        }
        return event_type in system_events


class DistributionType(Enum):
    """
    Distribution type enum.
    
    Classifies distributions for tax and reporting purposes.
    
    Values:
        INCOME: Ordinary income distribution
        DIVIDEND_FRANKED: Dividend with franking credits (reduces tax liability)
        DIVIDEND_UNFRANKED: Dividend without franking credits (fully taxable)
        INTEREST: Interest income (fully taxable)
        RENT: Rental income
        CAPITAL_GAIN: Capital gains (may have CGT discount)
    """
    INCOME = 'INCOME'
    DIVIDEND_FRANKED = 'DIVIDEND_FRANKED'
    DIVIDEND_UNFRANKED = 'DIVIDEND_UNFRANKED'
    INTEREST = 'INTEREST'
    RENT = 'RENT'
    CAPITAL_GAIN = 'CAPITAL_GAIN'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'DistributionType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid DistributionType: {value}. Must be one of: {[d.value for d in cls]}")
    
    @classmethod
    def is_taxable(cls, dist_type: 'DistributionType') -> bool:
        """Check if a distribution type is taxable."""
        taxable_types = {
            cls.INCOME,
            cls.DIVIDEND_FRANKED,
            cls.DIVIDEND_UNFRANKED,
            cls.INTEREST,
            cls.RENT,
            cls.CAPITAL_GAIN
        }
        return dist_type in taxable_types
    
    @classmethod
    def has_franking_credits(cls, dist_type: 'DistributionType') -> bool:
        """Check if a distribution type has franking credits."""
        return dist_type == cls.DIVIDEND_FRANKED


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


class TaxPaymentType(Enum):
    """
    Tax payment type enum.
    
    Classifies different types of tax payments for reporting and calculations.
    
    Values:
        NON_RESIDENT_INTEREST_WITHHOLDING: Non-resident interest withholding tax
        NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE: Adjustment for withholding tax differences
        CAPITAL_GAINS_TAX: Capital gains tax payments
        EOFY_INTEREST_TAX: End of financial year interest tax
        DIVIDENDS_FRANKED_TAX: Tax on franked dividends
        DIVIDENDS_UNFRANKED_TAX: Tax on unfranked dividends
    """
    NON_RESIDENT_INTEREST_WITHHOLDING = 'NON_RESIDENT_INTEREST_WITHHOLDING'
    NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE = 'NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE'
    CAPITAL_GAINS_TAX = 'CAPITAL_GAINS_TAX'
    EOFY_INTEREST_TAX = 'EOFY_INTEREST_TAX'
    DIVIDENDS_FRANKED_TAX = 'DIVIDENDS_FRANKED_TAX'
    DIVIDENDS_UNFRANKED_TAX = 'DIVIDENDS_UNFRANKED_TAX'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'TaxPaymentType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid TaxPaymentType: {value}. Must be one of: {[t.value for t in cls]}")
    
    @classmethod
    def is_withholding_tax(cls, tax_type: 'TaxPaymentType') -> bool:
        """Check if tax payment type is a withholding tax."""
        withholding_types = {
            cls.NON_RESIDENT_INTEREST_WITHHOLDING,
            cls.NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE
        }
        return tax_type in withholding_types
    
    @classmethod
    def is_dividend_tax(cls, tax_type: 'TaxPaymentType') -> bool:
        """Check if tax payment type is related to dividends."""
        dividend_tax_types = {
            cls.DIVIDENDS_FRANKED_TAX,
            cls.DIVIDENDS_UNFRANKED_TAX
        }
        return tax_type in dividend_tax_types


class GroupType(Enum):
    """
    Event grouping type enum.
    
    Defines how events can be grouped together for reporting and analysis.
    
    Values:
        INTEREST_WITHHOLDING: Interest distribution events paired with withholding tax events
        TAX_STATEMENT: Tax statement events grouped by financial year (future implementation)
    """
    INTEREST_WITHHOLDING = 'INTEREST_WITHHOLDING'
    TAX_STATEMENT = 'TAX_STATEMENT'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'GroupType':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid GroupType: {value}. Must be one of: {[g.value for g in cls]}")


class TaxJurisdiction(Enum):
    """
    Tax jurisdiction enum.
    
    Defines the tax jurisdiction for entities and funds.
    
    Values:
        AU: Australia (with specific tax rules like franking credits)
        US: United States
        UK: United Kingdom
        OTHER: Other jurisdictions
    """
    AU = 'AU'
    US = 'US'
    UK = 'UK'
    OTHER = 'OTHER'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'TaxJurisdiction':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid TaxJurisdiction: {value}. Must be one of: {[j.value for j in cls]}")
    
    @classmethod
    def has_franking_credits(cls, jurisdiction: 'TaxJurisdiction') -> bool:
        """Check if jurisdiction supports franking credits (Australia-specific)."""
        return jurisdiction == cls.AU
    
    @classmethod
    def has_cgt_discount(cls, jurisdiction: 'TaxJurisdiction') -> bool:
        """Check if jurisdiction has capital gains tax discount rules."""
        return jurisdiction in {cls.AU, cls.UK}


class SortOrder(Enum):
    """
    Sort order enum.
    
    Defines the order for sorting operations in APIs and queries.
    
    Values:
        ASC: Ascending order (A-Z, 1-9, oldest to newest)
        DESC: Descending order (Z-A, 9-1, newest to oldest)
    """
    ASC = 'ASC'
    DESC = 'DESC'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortOrder':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortOrder: {value}. Must be one of: {[o.value for o in cls]}")
    
    @classmethod
    def is_reverse(cls, order: 'SortOrder') -> bool:
        """Check if sort order is reverse/descending."""
        return order == cls.DESC


class SortField(Enum):
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
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortField':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortField: {value}. Must be one of: {[f.value for f in cls]}")
    
    @classmethod
    def is_numeric_field(cls, field: 'SortField') -> bool:
        """Check if sort field contains numeric values."""
        numeric_fields = {
            cls.COMMITMENT_AMOUNT,
            cls.CURRENT_EQUITY_BALANCE,
            cls.CREATED_AT,
            cls.UPDATED_AT
        }
        return field in numeric_fields


class Environment(Enum):
    """
    Environment enum.
    
    Defines the deployment environment for configuration management.
    
    Values:
        DEVELOPMENT: Development environment
        STAGING: Staging/testing environment
        PRODUCTION: Production environment
    """
    DEVELOPMENT = 'DEVELOPMENT'
    STAGING = 'STAGING'
    PRODUCTION = 'PRODUCTION'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'Environment':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid Environment: {value}. Must be one of: {[e.value for e in cls]}")
    
    @classmethod
    def is_production(cls, env: 'Environment') -> bool:
        """Check if environment is production."""
        return env == cls.PRODUCTION
    
    @classmethod
    def is_development(cls, env: 'Environment') -> bool:
        """Check if environment is development."""
        return env == cls.DEVELOPMENT


class DomainEventType(Enum):
    """
    Domain event type enum.
    
    Defines business domain events that are published when significant
    state changes occur in the fund system.
    
    Values:
        EQUITY_BALANCE_CHANGED: Fund equity balance changed
        DISTRIBUTION_RECORDED: Distribution was recorded
        NAV_UPDATED: Fund NAV was updated
        UNITS_CHANGED: Fund units changed
        TAX_STATEMENT_UPDATED: Tax statement was updated
        FUND_SUMMARY_UPDATED: Fund summary fields were updated
    """
    EQUITY_BALANCE_CHANGED = 'EQUITY_BALANCE_CHANGED'
    DISTRIBUTION_RECORDED = 'DISTRIBUTION_RECORDED'
    NAV_UPDATED = 'NAV_UPDATED'
    UNITS_CHANGED = 'UNITS_CHANGED'
    TAX_STATEMENT_UPDATED = 'TAX_STATEMENT_UPDATED'
    FUND_SUMMARY_UPDATED = 'FUND_SUMMARY_UPDATED'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value


class Currency(Enum):
    """
    Currency enum.
    
    Defines supported currencies for financial operations.
    
    Values:
        AUD: Australian Dollar
        USD: US Dollar
        EUR: Euro
        GBP: British Pound
        CAD: Canadian Dollar
        JPY: Japanese Yen
        CHF: Swiss Franc
    """
    AUD = 'AUD'
    USD = 'USD'
    EUR = 'EUR'
    GBP = 'GBP'
    CAD = 'CAD'
    JPY = 'JPY'
    CHF = 'CHF'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'Currency':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid Currency: {value}. Must be one of: {[c.value for c in cls]}")
    
    @classmethod
    def is_major_currency(cls, currency: 'Currency') -> bool:
        """Check if currency is a major world currency."""
        major_currencies = {
            cls.USD, cls.EUR, cls.GBP, cls.JPY, cls.CHF
        }
        return currency in major_currencies
    
    @classmethod
    def is_commonwealth_currency(cls, currency: 'Currency') -> bool:
        """Check if currency is from a Commonwealth country."""
        commonwealth_currencies = {
            cls.AUD, cls.GBP, cls.CAD
        }
        return currency in commonwealth_currencies


# Convenience functions for common enum operations
def get_all_enum_values(enum_class: type) -> list:
    """Get all values from an enum class."""
    return [e.value for e in enum_class]


def validate_enum_value(enum_class: type, value: str) -> bool:
    """Validate if a string value is valid for an enum class."""
    try:
        enum_class(value)
        return True
    except ValueError:
        return False


def get_enum_display_name(enum_instance: Enum) -> str:
    """Get a human-readable display name for an enum value."""
    return enum_instance.value.replace('_', ' ').title()
