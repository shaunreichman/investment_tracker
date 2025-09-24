"""
Fund Event Enums.

This module contains all enum definitions for the fund event system.
"""

from enum import Enum

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
            cls.DAILY_RISK_FREE_INTEREST_CHARGE
        }
        return event_type in system_events

    @classmethod
    def is_equity_call_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is a equity call event."""
        equity_events = {
            cls.CAPITAL_CALL,
            cls.UNIT_PURCHASE,
        }
        return event_type in equity_events

    @classmethod
    def is_equity_return_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is a equity return event."""
        equity_events = {
            cls.RETURN_OF_CAPITAL,
            cls.UNIT_SALE,
        }
        return event_type in equity_events

    @classmethod
    def is_tax_statement_event(cls, event_type: 'EventType') -> bool:
        """Check if an event type is a tax statement event."""
        tax_statement_events = {
            cls.TAX_PAYMENT
        }
        return event_type in tax_statement_events


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


class SortFieldFundEvent(Enum):
    """
    Sort field enum for fund events.
    
    Defines the fields that can be used to sort fund events.
    
    Values:
        EVENT_DATE: Event date
        EVENT_TYPE: Event type
    """
    EVENT_DATE = 'EVENT_DATE'
    EVENT_TYPE = 'EVENT_TYPE'
    
    def __str__(self) -> str:
        """Return the string representation of the enum value."""
        return self.value
    
    @classmethod
    def from_string(cls, value: str) -> 'SortFieldFundEvent':
        """Create enum from string value."""
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid SortFieldFundEvent: {value}. Must be one of: {[s.value for s in cls]}")