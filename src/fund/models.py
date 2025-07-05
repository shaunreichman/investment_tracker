"""
Fund domain models.

This module contains the core fund models including Fund, FundEvent, and related enums.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum
from sqlalchemy import func
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.elements import ColumnElement

# Import the Base from shared
from ..shared.base import Base


class EventType(enum.Enum):
    """Enumeration for all fund event types.
    
    - CAPITAL_CALL: Capital call (cost-based funds)
    - RETURN_OF_CAPITAL: Return of capital (cost-based funds)
    - DISTRIBUTION: Distribution (income, interest, etc.)
    - TAX_PAYMENT: Tax payment event
    - DAILY_RISK_FREE_INTEREST_CHARGE: Daily risk-free interest charge (for real IRR)
    - FY_DEBT_COST: Financial year debt cost tax benefit (for real IRR)
    - NAV_UPDATE: NAV update (NAV-based funds)
    - UNIT_PURCHASE: Unit purchase (NAV-based funds)
    - UNIT_SALE: Unit sale (NAV-based funds)
    - MANAGEMENT_FEE: Management fee
    - CARRIED_INTEREST: Carried interest
    - OTHER: Other event types
    """
    CAPITAL_CALL = "capital_call"
    RETURN_OF_CAPITAL = "return_of_capital"
    DISTRIBUTION = "distribution"
    TAX_PAYMENT = "tax_payment"
    DAILY_RISK_FREE_INTEREST_CHARGE = "daily_risk_free_interest_charge"
    FY_DEBT_COST = "fy_debt_cost"
    NAV_UPDATE = "nav_update"
    UNIT_PURCHASE = "unit_purchase"
    UNIT_SALE = "unit_sale"
    MANAGEMENT_FEE = "management_fee"
    CARRIED_INTEREST = "carried_interest"
    OTHER = "other"


class FundType(enum.Enum):
    """Enumeration for fund types."""
    NAV_BASED = "nav_based"  # Funds with NAV updates and unit tracking
    COST_BASED = "cost_based"  # Funds held at cost


class DistributionType(enum.Enum):
    """Enumeration for income distribution types (affects tax treatment)."""
    INCOME = "income"  # Ordinary income
    DIVIDEND = "dividend"  # Dividend income
    INTEREST = "interest"  # Interest income
    RENT = "rent"  # Rental income
    CAPITAL_GAIN = "capital_gain"  # Capital gains income (cost-based funds only)
    OTHER = "other"  # Other income types


class TaxPaymentType(enum.Enum):
    """Enumeration for tax payment types."""
    NON_RESIDENT_INTEREST_WITHHOLDING = "non_resident_interest_withholding"
    NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE = "non_resident_interest_withholding_difference"
    CAPITAL_GAINS_TAX = "capital_gains_tax"
    EOFY_INTEREST_TAX = "eofy_interest_tax"
    OTHER = "other"


class Fund(Base):
    """Model representing an investment fund.
    
    Field usage:
    - NAV-based funds (tracking_type=NAV_BASED):
        * current_units, current_unit_price: Calculated from NAV update events.
        * total_cost_basis: Not used (should be None).
    - Cost-based funds (tracking_type=COST_BASED):
        * total_cost_basis: Calculated from capital calls - capital returns.
        * current_units, current_unit_price: Not used (should be None).
    - Common fields: commitment_amount (manual), current_equity_balance (calculated), average_equity_balance (calculated), etc.
    
    Relationships:
    - investment_company: The investment company managing the fund.
    - entity: The investing entity (person or company).
    - fund_events: All events (capital calls, returns, distributions, etc.) for this fund.
    - tax_statements: Tax statements for this fund/entity/financial year.
    
    Business rules:
    - Only one tracking type (NAV or cost) is active per fund.
    - Calculated fields are updated via explicit update methods, not direct assignment.
    - Session handling is required for all DB queries and updates.
    """
    __tablename__ = 'funds'
    
    id = Column(Integer, primary_key=True)
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    name = Column(String(255), nullable=False)
    fund_type = Column(String(100))  # e.g., 'Private Equity', 'Venture Capital', 'Real Estate', etc.
    
    # Fund tracking type
    tracking_type = Column(Enum(FundType), nullable=False, default=FundType.NAV_BASED)
    
    # Investment tracking fields (common)
    commitment_amount = Column(Float, nullable=True)  # Total amount committed to the fund (MANUAL) - not applicable for NAV-based funds
    current_equity_balance = Column(Float, default=0.0)  # Current equity balance (CALCULATED)
    average_equity_balance = Column(Float, default=0.0)  # Average equity balance over time (CALCULATED)
    expected_irr = Column(Float)  # Expected Internal Rate of Return (as percentage) (MANUAL) - not applicable for NAV-based funds
    expected_duration_months = Column(Integer)  # Expected fund duration in months (MANUAL) - not applicable for NAV-based funds
    
    # NAV-based fund specific fields (CALCULATED)
    _current_units = Column('current_units', Float)  # (NAV-based only) Current number of units owned
    _current_unit_price = Column('current_unit_price', Float)  # (NAV-based only) Current unit price
    
    # Cost-based fund specific fields (CALCULATED)
    _total_cost_basis = Column('total_cost_basis', Float)  # (Cost-based only) Total cost basis for cost-based funds
    
    # Status and metadata
    is_active = Column(Boolean, default=True)  # Whether the fund is still active (CALCULATED)
    final_tax_statement_received = Column(Boolean, default=False)  # Whether all expected tax statements have been received (CALCULATED)
    description = Column(Text)  # (MANUAL)
    currency = Column(String(10), default="AUD")  # Currency code for the fund (MANUAL)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="funds", lazy='selectin')
    entity = relationship("Entity", back_populates="funds", lazy='selectin')
    fund_events = relationship("FundEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    tax_statements = relationship("TaxStatement", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    
    def __repr__(self):
        """Return a string representation of the Fund instance for debugging/logging."""
        return f"<Fund(id={self.id}, name='{self.name}', company='{self.investment_company.name if self.investment_company else 'Unknown'}')>"


class FundEvent(Base):
    """Model representing various dated events for a fund.
    
    Field usage:
    - NAV-based funds: NAV updates, unit purchases/sales, distributions, etc.
    - Cost-based funds: capital calls, returns, distributions, etc.
    - No capital call/return percentages: only use the amount field for all events.
    
    Relationships:
    - fund: The Fund this event belongs to.
    
    Business rules:
    - Each event is associated with a specific fund and date.
    - Event type and related fields determine how the event is processed in calculations.
    - Distribution and tax payment types affect tax treatment and reporting.
    """
    __tablename__ = 'fund_events'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # Indexed for fast fund queries
    event_type = Column(Enum(EventType), nullable=False, index=True)  # Indexed for fast event type queries
    event_date = Column(Date, nullable=False, index=True)  # Indexed for fast date queries
    amount = Column(Float)  # Amount for the event (can be None for some event types)
    
    # Event-specific fields
    nav_per_share = Column(Float)  # For NAV updates
    units_owned = Column(Float)  # For NAV updates and unit purchases/sales
    cost_of_units = Column(Float)  # For NAV-based funds: FIFO cost of remaining units after this event
    
    # Distribution type for tax purposes
    distribution_type = Column(Enum(DistributionType))  # Type of distribution (for tax treatment)
    # Tax payment type for tax payment events
    tax_payment_type = Column(Enum(TaxPaymentType))  # Type of tax payment (for tax treatment)
    
    # NAV-based fund event fields
    units_purchased = Column(Float)  # Units purchased in this event
    units_sold = Column(Float)  # Units sold in this event
    unit_price = Column(Float)  # Unit price for this event
    brokerage_fee = Column(Float, default=0.0)  # Brokerage fee for unit purchases/sales (optional)
    
    # Metadata
    description = Column(Text)
    reference_number = Column(String(100))  # External reference number
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund", back_populates="fund_events", lazy='selectin')  # Eager load for fund event lists
    
    def __repr__(self):
        """Return a string representation of the FundEvent instance for debugging/logging."""
        return f"<FundEvent(id={self.id}, fund_id={self.fund_id}, type={self.event_type.value}, date={self.event_date}, amount={self.amount})>"
    
    def infer_distribution_type(self):
        """Infer the distribution type based on the event description or other fields.
        Returns a DistributionType enum value.
        """
        if not self.description:
            return DistributionType.OTHER
        
        desc_lower = self.description.lower()
        if 'interest' in desc_lower:
            return DistributionType.INTEREST
        elif 'dividend' in desc_lower:
            return DistributionType.DIVIDEND
        elif 'rent' in desc_lower:
            return DistributionType.RENT
        elif 'capital gain' in desc_lower or 'capital_gain' in desc_lower:
            return DistributionType.CAPITAL_GAIN
        elif 'income' in desc_lower:
            return DistributionType.INCOME
        else:
            return DistributionType.OTHER
    
    def set_event_type_and_infer_distribution(self, event_type):
        """Set the event type and infer the distribution type if it's a distribution event.
        This is a convenience method for creating distribution events.
        """
        self.event_type = event_type
        if event_type == EventType.DISTRIBUTION:
            self.distribution_type = self.infer_distribution_type() 