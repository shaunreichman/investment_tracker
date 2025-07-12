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
from ..shared.utils import with_session, with_class_session


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
    fy_debt_interest_deduction_sum_of_daily_interest = Column(Float, default=0.0)  # Total interest expense for the financial year
    fy_debt_interest_deduction_rate = Column(Float, default=0.0)  # Tax deduction rate for interest (e.g., 30.0 for 30%)
    fy_debt_interest_deduction_total_deduction = Column(Float, default=0.0)  # Calculated tax benefit from interest deduction
    
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

    # Dividend income
    dividend_franked_income_amount = Column(Float, default=0.0)  # Manual or calculated franked dividends
    dividend_unfranked_income_amount = Column(Float, default=0.0)  # Manual or calculated unfranked dividends
    dividend_franked_income_tax_rate = Column(Float, default=0.0)  # Manually defined franked dividend tax rate (%)
    dividend_unfranked_income_tax_rate = Column(Float, default=0.0)  # Manually defined unfranked dividend tax rate (%)
    dividend_franked_tax_amount = Column(Float, default=0.0)  # Calculated franked dividend tax amount
    dividend_unfranked_tax_amount = Column(Float, default=0.0)  # Calculated unfranked dividend tax amount
    dividend_franked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # True if amount comes from tax statement
    dividend_unfranked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # True if amount comes from tax statement
    
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

    def calculate_fy_debt_interest_deduction_total_deduction(self):
        """
        Calculate the interest tax benefit based on total interest expense and deduction rate.
        Updates the fy_debt_interest_deduction_total_deduction field and returns the value.
        """
        from .calculations import calculate_fy_debt_interest_deduction_total_deduction
        self.fy_debt_interest_deduction_total_deduction = calculate_fy_debt_interest_deduction_total_deduction(self.fy_debt_interest_deduction_sum_of_daily_interest, self.fy_debt_interest_deduction_rate)
        return self.fy_debt_interest_deduction_total_deduction

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

    def calculate_dividend_totals(self, session=None):
        """
        Calculate total franked and unfranked dividends from fund distributions.
        Updates the dividend_franked_income_amount and dividend_unfranked_income_amount fields.
        Returns a tuple: (dividend_franked_income_amount, dividend_unfranked_income_amount).
        """
        from sqlalchemy.orm import object_session
        from src.fund.models import FundEvent, EventType, DistributionType
        
        if session is None:
            session = object_session(self)
        
        if session is None:
            return 0.0, 0.0
        
        # Get financial year dates
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_start or not fy_end:
            return 0.0, 0.0
        
        # Query fund events for this financial year
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end
        ).all()
        
        # Calculate totals
        franked_total = 0.0
        unfranked_total = 0.0
        
        for event in events:
            if event.distribution_type == DistributionType.DIVIDEND_FRANKED:
                franked_total += event.amount or 0.0
            elif event.distribution_type == DistributionType.DIVIDEND_UNFRANKED:
                unfranked_total += event.amount or 0.0
        
        # Update fields if not manually set
        if self.dividend_franked_income_amount is None or self.dividend_franked_income_amount == 0.0:
            self.dividend_franked_income_amount = franked_total
            self.dividend_franked_income_amount_from_tax_statement_flag = False
        else:
            self.dividend_franked_income_amount_from_tax_statement_flag = True
        
        if self.dividend_unfranked_income_amount is None or self.dividend_unfranked_income_amount == 0.0:
            self.dividend_unfranked_income_amount = unfranked_total
            self.dividend_unfranked_income_amount_from_tax_statement_flag = False
        else:
            self.dividend_unfranked_income_amount_from_tax_statement_flag = True
        
        return self.dividend_franked_income_amount, self.dividend_unfranked_income_amount

    def calculate_dividend_franked_tax_amount(self):
        """
        Calculate the franked dividend tax amount based on income amount and tax rate.
        Updates the dividend_franked_tax_amount field and returns the value.
        """
        if self.dividend_franked_income_amount and self.dividend_franked_income_tax_rate:
            self.dividend_franked_tax_amount = (self.dividend_franked_income_amount * self.dividend_franked_income_tax_rate) / 100.0
        else:
            self.dividend_franked_tax_amount = 0.0
        return self.dividend_franked_tax_amount

    def calculate_dividend_unfranked_tax_amount(self):
        """
        Calculate the unfranked dividend tax amount based on income amount and tax rate.
        Updates the dividend_unfranked_tax_amount field and returns the value.
        """
        if self.dividend_unfranked_income_amount and self.dividend_unfranked_income_tax_rate:
            self.dividend_unfranked_tax_amount = (self.dividend_unfranked_income_amount * self.dividend_unfranked_income_tax_rate) / 100.0
        else:
            self.dividend_unfranked_tax_amount = 0.0
        return self.dividend_unfranked_tax_amount

    # Removed methods:
    # - _create_tax_payment_event_object
    # - _create_dividend_tax_payment_event_objects
    # - _create_fy_debt_cost_event_object
    # - create_tax_payment_event
    # - create_fy_debt_cost_event
    # All event creation is now handled by TaxEventManager and TaxEventFactory.
    # If any usages remain, update them to use create_tax_payment_events or the new manager/factory methods.
    # (No code to insert here, just removing the old methods.)

    @classmethod
    def create(cls, fund_id, entity_id, financial_year, gross_income=0.0, 
               deductions=0.0, tax_payable=0.0, session=None):
        """
        Create a new tax statement with validation and business logic.
        
        Args:
            fund_id (int): ID of the fund
            entity_id (int): ID of the entity
            financial_year (str): Financial year (e.g., "2023-24")
            gross_income (float): Gross income amount
            deductions (float): Deductions amount
            tax_payable (float): Tax payable amount
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            TaxStatement: The created tax statement
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validation
        if not fund_id:
            raise ValueError("Fund ID is required")
        
        if not entity_id:
            raise ValueError("Entity ID is required")
        
        if not financial_year:
            raise ValueError("Financial year is required")
        
        # Check for existing tax statement for same fund/entity/financial year
        existing = session.query(cls).filter(
            cls.fund_id == fund_id,
            cls.entity_id == entity_id,
            cls.financial_year == financial_year
        ).first()
        if existing:
            raise ValueError(f"Tax statement already exists for fund {fund_id}, entity {entity_id}, FY {financial_year}")
        
        # Create the tax statement
        statement = cls(
            fund_id=fund_id,
            entity_id=entity_id,
            financial_year=financial_year,
            total_interest_income=gross_income,  # Map gross_income to total_interest_income
            other_income=0.0,  # Default other income fields
            foreign_income=0.0,
            capital_gains=0.0,
            tax_payable=tax_payable
        )
        
        # Calculate total income
        statement.calculate_total_income()
        
        session.add(statement)
        session.flush()  # Get the ID without committing
        
        return statement
    
    def _create_or_update_tax_statement_object(self, entity_id, financial_year, **kwargs):
        """Create or update a tax statement object.
        Returns the TaxStatement object. No database operations.
        """
        from sqlalchemy.orm import object_session
        session = object_session(self)
        
        statement = self.get_tax_statement_for_entity_financial_year(entity_id, financial_year)
        if statement is None:
            statement = TaxStatement(
                fund_id=self.id,
                entity_id=entity_id,
                financial_year=financial_year,
                **kwargs
            )
        else:
            for key, value in kwargs.items():
                if hasattr(statement, key):
                    setattr(statement, key, value)
        statement.calculate_interest_income_fields()
        statement.calculate_total_income()
        return statement
    
    def create_or_update_tax_statement(self, entity_id, financial_year, session=None, **kwargs):
        """Create or update a tax statement for a specific entity and financial year.
        If a statement exists, updates its fields; otherwise, creates a new one.
        Commits the change to the database.
        Returns the TaxStatement instance.
        """
        statement = self._create_or_update_tax_statement_object(entity_id, financial_year, **kwargs)
        if statement.id is None:
            session.add(statement)
        session.commit()
        return statement
    
    def create_tax_payment_events(self, session=None):
        """Create tax payment events for this tax statement using the new event management framework.
        Commits new events to the database. Returns a list of created events.
        """
        from src.tax.events import TaxEventManager
        if session is None:
            from sqlalchemy.orm import object_session
            session = object_session(self)
        if session is None:
            raise ValueError("A valid session is required to create tax payment events.")
        # Use the new TaxEventManager to create or update all tax events for this statement
        created_events = TaxEventManager.create_or_update_tax_events(self, session)
        return created_events 