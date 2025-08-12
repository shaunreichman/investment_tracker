"""
Fund Enums Module.

This module contains all enum definitions for the fund system.
Following enterprise best practices for clean separation of concerns.

Enums:
- FundStatus: Fund lifecycle status (ACTIVE, REALIZED, COMPLETED)
- FundType: Fund tracking type (COST_BASED, NAV_BASED)
- EventType: Fund event types (capital_call, distribution, etc.)
- DistributionType: Distribution classification types
"""

from enum import Enum


class FundStatus(Enum):
    """
    Fund lifecycle status enum.
    
    Represents the current state of a fund in its lifecycle.
    
    Values:
        ACTIVE: Fund has capital at risk and is actively managed
        REALIZED: All capital has been returned, fund is realized
        COMPLETED: Fund is realized and all tax obligations are complete
    """
    ACTIVE = 'active'
    REALIZED = 'realized'
    COMPLETED = 'completed'
    
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
    COST_BASED = 'cost_based'
    NAV_BASED = 'nav_based'
    
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
    CAPITAL_CALL = 'capital_call'
    RETURN_OF_CAPITAL = 'return_of_capital'
    DISTRIBUTION = 'distribution'
    UNIT_PURCHASE = 'unit_purchase'
    UNIT_SALE = 'unit_sale'
    NAV_UPDATE = 'nav_update'
    DAILY_RISK_FREE_INTEREST_CHARGE = 'daily_risk_free_interest_charge'
    EOFY_DEBT_COST = 'eofy_debt_cost'
    TAX_PAYMENT = 'tax_payment'
    
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
        CAPITAL_GAINS: Capital gains distribution
        RETURN_OF_CAPITAL: Return of capital distribution
        DIVIDEND: Dividend distribution
        INTEREST: Interest distribution
    """
    INCOME = 'income'
    CAPITAL_GAINS = 'capital_gains'
    RETURN_OF_CAPITAL = 'return_of_capital'
    DIVIDEND = 'dividend'
    INTEREST = 'interest'
    
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
            cls.CAPITAL_GAINS,
            cls.DIVIDEND,
            cls.INTEREST
        }
        return dist_type in taxable_types


class GroupType(Enum):
    """
    Event grouping type enum.
    
    Defines how events can be grouped together for reporting and analysis.
    
    Values:
        TAX_STATEMENT: Group events for tax statement purposes
        PERFORMANCE: Group events for performance calculations
        CASH_FLOW: Group events for cash flow analysis
    """
    TAX_STATEMENT = 'tax_statement'
    PERFORMANCE = 'performance'
    CASH_FLOW = 'cash_flow'
    
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
