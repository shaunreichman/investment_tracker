"""
Tax domain models.

This module contains the core tax models including TaxStatement.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql.elements import ColumnElement
from datetime import datetime, date
import enum

# Import the Base from shared
from ..shared.base import Base


class TaxStatement(Base):
    """Model representing tax statements from funds for specific financial years.
    
    Field usage:
    - fund_id, entity_id, financial_year: Uniquely identify the statement.
    - Various income and tax fields: Populated from fund-provided tax statements.
    - Calculated fields: Used for reconciliation and after-tax IRR calculations.
    
    Relationships:
    - fund: The Fund this statement belongs to.
    - entity: The Entity this statement is for.
    
    Business rules:
    - Only one statement per (fund, entity, financial year).
    - Used for tax reconciliation, reporting, and IRR calculations.
    """
    __tablename__ = 'tax_statements'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # Indexed for fast fund queries
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)  # Indexed for fast entity queries
    financial_year = Column(String(10), nullable=False, index=True)  # Indexed for fast year queries
    
    # Tax components from fund statement
    foreign_income = Column(Float, default=0.0)
    capital_gains = Column(Float, default=0.0)
    other_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    
    # Tax withheld/credits
    foreign_tax_credits = Column(Float, default=0.0)
    
    # After-tax IRR fields
    tax_already_paid = Column(Float, default=0.0)  # Tax already withheld/paid (no additional cash flow)
    tax_payable = Column(Float, default=0.0)  # Additional tax payable (creates cash outflow)
    tax_payment_date = Column(Date)  # Date when additional tax is due (defaults to FY end)
    
    # Debt cost tracking for real IRR calculations
    total_interest_expense = Column(Float, default=0.0)  # Total interest expense for the financial year
    interest_deduction_rate = Column(Float, default=0.0)  # Tax deduction rate for interest (e.g., 30.0 for 30%)
    interest_tax_benefit = Column(Float, default=0.0)  # Calculated tax benefit from interest deduction
    
    # Tax status
    non_resident = Column(Boolean, default=False)  # Whether entity was non-resident for tax purposes in this FY
    
    # Additional fields
    accountant = Column(String(255))  # Name of fund's accountant who prepared the tax statement
    notes = Column(Text)
    statement_date = Column(Date)  # Date the tax statement was issued
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund", back_populates="tax_statements", lazy='selectin')
    entity = relationship("Entity", back_populates="tax_statements", lazy='selectin')
    
    # Composite unique constraint to ensure one statement per fund/entity/financial year
    __table_args__ = (
        UniqueConstraint('fund_id', 'entity_id', 'financial_year', name='unique_tax_statement'),
    )
    
    def __repr__(self):
        """Return a string representation of the TaxStatement instance for debugging/logging."""
        return f"<TaxStatement(id={self.id}, fund_id={self.fund_id}, entity_id={self.entity_id}, fy={self.financial_year})>"
    
    # Manual fields for interest income reconciliation
    distribution_receivable_this_fy = Column(Float, default=0.0)
    distribution_received_prev_fy = Column(Float, default=0.0)
    interest_received_in_cash = Column(Float, default=0.0)
    non_resident_withholding_tax_from_statement = Column(Float, default=0.0)
    # New manual field for interest taxable rate
    interest_taxable_rate = Column(Float, default=0.0)  # Manually defined interest tax rate (%)

    # Calculated fields
    total_interest_income = Column(Float, default=0.0)  # Renamed from gross_total_interest_income
    non_resident_withholding_tax_already_withheld = Column(Float, default=0.0)
    
    @property
    def net_interest_income(self):
        """Net interest income is always calculated as total_interest_income - non_resident_withholding_tax_from_statement."""
        from .calculations import net_income
        return net_income(self.total_interest_income, self.non_resident_withholding_tax_from_statement)

    def get_net_income(self):
        """Calculate net income after non-resident withholding tax from statement.
        Returns the net income as a float.
        """
        from .calculations import net_income
        return net_income(self.total_income, self.non_resident_withholding_tax_from_statement)

    def calculate_tax_payable(self):
        """Calculate tax payable as (total_interest_income * interest_taxable_rate / 100) - non_resident_withholding_tax_from_statement.
        Updates the tax_payable and tax_already_paid fields.
        Returns the tax payable as a float.
        """
        from .calculations import tax_payable
        from sqlalchemy.sql.schema import Column
        from sqlalchemy.sql.elements import ColumnElement
        self.tax_payable = tax_payable(self.total_interest_income, self.interest_taxable_rate, self.non_resident_withholding_tax_from_statement)
        if (self.interest_taxable_rate is not None and not isinstance(self.interest_taxable_rate, (Column, ColumnElement)) and self.interest_taxable_rate != 0) and (self.total_interest_income is not None and not isinstance(self.total_interest_income, (Column, ColumnElement)) and self.total_interest_income > 0):
            self.tax_already_paid = (self.non_resident_withholding_tax_from_statement or 0.0)
        else:
            self.tax_already_paid = 0.0
        return self.tax_payable

    def calculate_interest_tax_benefit(self):
        """Calculate the tax benefit from interest expense deduction.
        Updates the interest_tax_benefit field and returns the value.
        """
        from .calculations import interest_tax_benefit
        self.interest_tax_benefit = interest_tax_benefit(self.total_interest_expense, self.interest_deduction_rate)
        return self.interest_tax_benefit

    def get_financial_year_dates(self):
        """Get the start and end dates for this financial year based on entity jurisdiction.
        Returns a tuple: (start_date, end_date).
        """
        from ..shared.calculations import get_financial_year_dates
        from sqlalchemy.orm import object_session
        from src.entity.models import Entity
        session = object_session(self)
        if session is None:
            return None, None
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return None, None
        return get_financial_year_dates(self.financial_year, entity.tax_jurisdiction)
    
    def calculate_total_income(self):
        """Calculate total income from all components, treating None as 0.0.
        Updates the total_income field and returns the value.
        """
        self.total_income = (
            (self.total_interest_income or 0.0) +
            (self.foreign_income or 0.0) +
            (self.capital_gains or 0.0) +
            (self.other_income or 0.0)
        )
        return self.total_income
    
    def get_net_income(self):
        """Calculate net income after non-resident withholding tax from statement.
        Returns the net income as a float.
        """
        return self.total_income - (self.non_resident_withholding_tax_from_statement or 0.0)
    
    def get_tax_payment_date(self):
        """Get the tax payment date, defaulting to financial year end if not specified.
        Returns a date object.
        """
        if not isinstance(self.tax_payment_date, (Column, ColumnElement)) and self.tax_payment_date is not None:
            return self.tax_payment_date
        # Default to financial year end
        fy_start, fy_end = self.get_financial_year_dates()
        return fy_end
    
    @property
    def non_resident_withholding_tax_difference(self):
        """Calculate the difference between tax withheld from statement and already withheld."""
        return (self.non_resident_withholding_tax_from_statement or 0.0) - (self.non_resident_withholding_tax_already_withheld or 0.0)
    
    def calculate_interest_income_fields(self, session=None):
        """Calculate interest income fields from manual inputs."""
        # Calculate total interest income
        self.total_interest_income = (
            (self.distribution_receivable_this_fy or 0.0) +
            (self.distribution_received_prev_fy or 0.0) +
            (self.interest_received_in_cash or 0.0)
        )
        
        # Note: net_interest_income is a property, so we don't set it directly
        # It will be calculated automatically when accessed
        
        return self.total_interest_income, self.net_interest_income 

    def _create_fy_debt_cost_event_object(self):
        """Create a FY debt cost event object for real IRR calculations if a tax benefit exists.
        Returns the event object or None if not applicable. No database operations.
        """
        from .creation import create_fy_debt_cost_event_object
        return create_fy_debt_cost_event_object(self)

    def create_fy_debt_cost_event(self, session=None):
        """Create a FY debt cost event for real IRR calculations if a tax benefit exists.
        Commits the event to the database and returns it, or returns None if not applicable.
        """
        from .creation import create_fy_debt_cost_event
        return create_fy_debt_cost_event(self, session) 