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

    # Manual fields for dividend income
    total_dividends_franked = Column(Float, default=0.0)  # Manual or calculated franked dividends
    total_dividends_unfranked = Column(Float, default=0.0)  # Manual or calculated unfranked dividends
    dividends_franked_taxable_rate = Column(Float, default=0.0)  # Manually defined franked dividend tax rate (%)
    dividends_unfranked_taxable_rate = Column(Float, default=0.0)  # Manually defined unfranked dividend tax rate (%)

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

    def calculate_dividend_totals(self, session=None):
        """Calculate dividend totals from fund events if not manually set.
        Returns a tuple: (total_dividends_franked, total_dividends_unfranked).
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
        if self.total_dividends_franked is None or self.total_dividends_franked == 0.0:
            self.total_dividends_franked = franked_total
        
        if self.total_dividends_unfranked is None or self.total_dividends_unfranked == 0.0:
            self.total_dividends_unfranked = unfranked_total
        
        return self.total_dividends_franked, self.total_dividends_unfranked

    def _create_dividend_tax_payment_event_objects(self):
        """Create dividend tax payment event objects if applicable.
        Returns a list of event objects. No database operations.
        """
        from src.fund.models import FundEvent, EventType, TaxPaymentType
        
        events = []
        
        # Calculate dividend totals if needed
        franked_total, unfranked_total = self.calculate_dividend_totals()
        
        # Create franked dividend tax payment
        if franked_total > 0 and self.dividends_franked_taxable_rate and self.dividends_franked_taxable_rate > 0:
            tax_amount = franked_total * (self.dividends_franked_taxable_rate / 100.0)
            if tax_amount > 0:
                event = FundEvent(
                    fund_id=self.fund_id,
                    event_type=EventType.TAX_PAYMENT,
                    event_date=self.get_tax_payment_date(),
                    amount=tax_amount,
                    description=f"Franked dividend tax (rate: {self.dividends_franked_taxable_rate}%)",
                    reference_number=f"DIV_FRANKED_TAX_{self.financial_year}",
                    tax_payment_type=TaxPaymentType.DIVIDENDS_FRANKED_TAX
                )
                events.append(event)
        
        # Create unfranked dividend tax payment
        if unfranked_total > 0 and self.dividends_unfranked_taxable_rate and self.dividends_unfranked_taxable_rate > 0:
            tax_amount = unfranked_total * (self.dividends_unfranked_taxable_rate / 100.0)
            if tax_amount > 0:
                event = FundEvent(
                    fund_id=self.fund_id,
                    event_type=EventType.TAX_PAYMENT,
                    event_date=self.get_tax_payment_date(),
                    amount=tax_amount,
                    description=f"Unfranked dividend tax (rate: {self.dividends_unfranked_taxable_rate}%)",
                    reference_number=f"DIV_UNFRANKED_TAX_{self.financial_year}",
                    tax_payment_type=TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
                )
                events.append(event)
        
        return events

    def _create_fy_debt_cost_event_object(self):
        """Create a FY debt cost event object for real IRR calculations if a tax benefit exists.
        Returns the event object or None if not applicable. No database operations.
        """
        from src.fund.models import FundEvent, EventType
        
        # Calculate the tax benefit
        tax_benefit = self.calculate_interest_tax_benefit()
        if tax_benefit <= 0:
            return None
        
        # Get the financial year end date
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_end:
            return None
        
        # Create event object
        event = FundEvent(
            fund_id=self.fund_id,
            event_type=EventType.FY_DEBT_COST,
            event_date=fy_end,
            amount=tax_benefit,  # Positive cash flow (tax benefit)
            description=f"FY {self.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})",
            reference_number=f"FY_DEBT_COST_{self.financial_year}"
        )
        
        return event

    def create_fy_debt_cost_event(self, session=None):
        """Create a FY debt cost event for real IRR calculations if a tax benefit exists.
        Commits the event to the database and returns it, or returns None if not applicable.
        """
        from src.fund.models import FundEvent, EventType
        
        # Get the financial year end date
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_end:
            return None
        
        # Check if FY debt cost event already exists for this fund/entity/financial year
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.FY_DEBT_COST,
            FundEvent.event_date == fy_end,
            FundEvent.description.like(f"%FY {self.financial_year}%")
        ).first()
        
        if existing_event:
            # Update existing event
            tax_benefit = self.calculate_interest_tax_benefit()
            existing_event.amount = tax_benefit
            existing_event.description = f"FY {self.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})"
            session.commit()
            return existing_event
        
        # Create new event using business logic method
        event = self._create_fy_debt_cost_event_object()
        if event:
            session.add(event)
            session.commit()
        
        return event
    
    def _create_tax_payment_event_object(self):
        """Create a tax payment event object for this tax statement.
        Returns the event object or None if not applicable. No database operations.
        """
        from src.fund.models import FundEvent, EventType, TaxPaymentType
        
        self.calculate_tax_payable()
        if self.tax_payable > 0.01:
            tax_event = FundEvent(
                fund_id=self.fund_id,
                event_type=EventType.TAX_PAYMENT,
                event_date=self.get_tax_payment_date(),
                amount=self.tax_payable,
                description=f"Tax payment for FY {self.financial_year}",
                reference_number=f"TAX-{self.financial_year}",
                tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
            )
            return tax_event
        return None
    
    def create_tax_payment_event(self, session=None):
        """Create a tax payment event for this tax statement.
        Commits the event to the database and returns it, or returns None if not applicable.
        """
        from src.fund.models import FundEvent, EventType, TaxPaymentType
        
        # Check if tax payment event already exists
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.event_date == self.get_tax_payment_date(),
            FundEvent.amount == self.tax_payable,
            FundEvent.tax_payment_type == TaxPaymentType.EOFY_INTEREST_TAX
        ).first()
        
        if existing_event:
            return existing_event
        
        # Create new event
        tax_event = self._create_tax_payment_event_object()
        if tax_event:
            session.add(tax_event)
            session.commit()
            return tax_event
        
        return None

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
        """Create tax payment events for this fund based on tax statements.
        Used for after-tax IRR calculations. Commits new events to the database.
        Returns a list of created events.
        """
        from src.fund.models import FundEvent, EventType, TaxPaymentType
        
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).all()
        created_events = []
        for tax_statement in tax_statements:
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.TAX_PAYMENT,
                FundEvent.event_date == tax_statement.get_tax_payment_date(),
                FundEvent.amount == tax_statement.tax_payable,
                FundEvent.tax_payment_type == TaxPaymentType.EOFY_INTEREST_TAX
            ).first()
            if not existing_event:
                tax_event = tax_statement._create_tax_payment_event_object()
                if tax_event:
                    session.add(tax_event)
                    created_events.append(tax_event)
        if created_events:
            session.commit()
        return created_events 