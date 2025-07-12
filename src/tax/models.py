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
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (MANUAL) foreign key to fund
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)  # (MANUAL) foreign key to entity
    financial_year = Column(String(10), nullable=False, index=True)  # (MANUAL) financial year (e.g., "2023-24")
    

    
    # After-tax IRR fields
    tax_payment_date = Column(Date)  # (MANUAL) date when additional tax is due (defaults to FY end)
    
    # --------- INCOME ---------

    # --------- Interest income ---------
    interest_income_amount = Column(Float, default=0.0)  # (CALCULATED) calculated from manual interest fields
    interest_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined interest tax rate (%)
    interest_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated from interest income and rate
    interest_received_in_cash = Column(Float, default=0.0)  # (MANUAL) actual cash flow received this FY
    interest_receivable_this_fy = Column(Float, default=0.0)  # (MANUAL) accounting income for this FY, not yet received
    interest_receivable_prev_fy = Column(Float, default=0.0)  # (MANUAL) accounting income from prev FY, received this FY
    interest_non_resident_withholding_tax_from_statement = Column(Float, default=0.0)  # (MANUAL) withholding tax as reported
    interest_non_resident_withholding_tax_already_withheld = Column(Float, default=0.0)  # (CALCULATED) sum of TAX_PAYMENT events

    # --------- Dividend income ---------
    dividend_franked_income_amount = Column(Float, default=0.0)  # (HYBRID) manual or calculated franked dividends
    dividend_unfranked_income_amount = Column(Float, default=0.0)  # (HYBRID) manual or calculated unfranked dividends
    dividend_franked_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined franked dividend tax rate (%)
    dividend_unfranked_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined unfranked dividend tax rate (%)
    dividend_franked_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated franked dividend tax amount
    dividend_unfranked_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated unfranked dividend tax amount
    dividend_franked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # (CALCULATED) true if amount comes from tax statement
    dividend_unfranked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # (CALCULATED) true if amount comes from tax statement

    # Debt cost tracking for real IRR calculations
    fy_debt_interest_deduction_sum_of_daily_interest = Column(Float, default=0.0)  # (CALCULATED) total interest expense for the FY
    fy_debt_interest_deduction_rate = Column(Float, default=0.0)  # (MANUAL) tax deduction rate for interest (e.g., 30.0 for 30%)
    fy_debt_interest_deduction_total_deduction = Column(Float, default=0.0)  # (CALCULATED) calculated tax benefit from interest deduction
    
    # Tax status
    non_resident = Column(Boolean, default=False)  # (MANUAL) whether entity was non-resident for tax purposes in this FY
    
    # Additional fields
    accountant = Column(String(255))  # (MANUAL) name of fund's accountant who prepared the tax statement
    notes = Column(Text)  # (MANUAL) additional notes
    statement_date = Column(Date)  # (MANUAL) date the tax statement was issued
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) timestamp when record was last updated
    
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

    def calculate_interest_tax_amount(self):
        """Calculate interest tax amount as (interest_income_amount * interest_income_tax_rate / 100) - interest_non_resident_withholding_tax_from_statement.
        Updates the interest_tax_amount field.
        Returns the tax amount as a float.
        """
        from .calculations import tax_payable
        self.interest_tax_amount = tax_payable(self.interest_income_amount, self.interest_income_tax_rate, self.interest_non_resident_withholding_tax_from_statement)
        return self.interest_tax_amount

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
        return (self.interest_non_resident_withholding_tax_from_statement or 0.0) - (self.interest_non_resident_withholding_tax_already_withheld or 0.0)
    
    def calculate_interest_income_amount(self, session=None):
        """Calculate interest income amount from manual inputs."""
        self.interest_income_amount = (
            (self.interest_receivable_this_fy or 0.0) +
            (self.interest_receivable_prev_fy or 0.0) +
            (self.interest_received_in_cash or 0.0)
        )
        return self.interest_income_amount

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
            interest_income_amount=gross_income,  # Map gross_income to interest_income_amount
            
            interest_tax_amount=tax_payable
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
        statement.calculate_interest_income_amount()
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