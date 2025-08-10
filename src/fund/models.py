"""
Fund domain models.

This module contains the core fund models including Fund, FundEvent, and related enums.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint, func
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date, timezone
from dateutil.relativedelta import relativedelta
import enum
from sqlalchemy import func
import numpy as np
import numpy_financial as npf
from sqlalchemy import event
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.orm import Session
from sqlalchemy.orm import object_session

# Import the Base from shared
from ..shared.base import Base

# Import utilities and calculations
from ..shared.utils import with_session, with_class_session
from .calculations import (
    calculate_irr,
    calculate_debt_cost
)
from ..shared.calculations import orchestrate_irr_base
from ..shared.utils import with_session

# Import models from other domains
from ..rates.models import RiskFreeRate
from ..entity.models import Entity
# Note: TaxStatement is imported as a string reference to avoid circular imports

# Import shared calculations
from ..shared.calculations import get_equity_change_for_event
from ..entity.calculations import get_financial_years_for_fund_period
from ..rates.calculations import get_risk_free_rate_for_date
from ..banking.models import BankAccount


class CashFlowDirection(enum.Enum):
    INFLOW = "inflow"  # (SYSTEM) persisted enum value indicating money received by investor
    OUTFLOW = "outflow"  # (SYSTEM) persisted enum value indicating money paid out by investor


class FundEventCashFlow(Base):
    """Actual cash transfer(s) linked to a FundEvent via investor bank accounts."""

    __tablename__ = 'fund_event_cash_flows'

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_event_id = Column(Integer, ForeignKey('fund_events.id'), nullable=False, index=True)  # (SYSTEM) link to parent event
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False, index=True)  # (MANUAL) account where the transfer occurred
    direction = Column(Enum(CashFlowDirection), nullable=False)  # (SYSTEM) inflow/outflow from investor perspective
    transfer_date = Column(Date, nullable=False, index=True)  # (MANUAL) date of transaction on bank statement
    currency = Column(String(3), nullable=False)  # (MANUAL) ISO-4217; must equal BankAccount.currency
    amount = Column(Float, nullable=False)  # (MANUAL) transfer amount in currency
    reference = Column(String(255))  # (MANUAL) free-text bank reference
    notes = Column(Text)  # (MANUAL) additional notes

    # Relationships
    fund_event = relationship('FundEvent', back_populates='cash_flows')
    bank_account = relationship('BankAccount')

    def __repr__(self) -> str:
        return (
            f"<FundEventCashFlow(id={self.id}, event_id={self.fund_event_id}, acct_id={self.bank_account_id}, "
            f"dir={self.direction.value}, date={self.transfer_date}, {self.currency} {self.amount})>"
        )

    @staticmethod
    def _is_same_currency(session, bank_account_id: int, currency: str) -> bool:
        acct: BankAccount | None = session.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
        return bool(acct and acct.currency.upper() == currency.upper())


class EventType(enum.Enum):
    """Enumeration for all fund event types.
    
    - CAPITAL_CALL: Capital call (cost-based funds)
    - RETURN_OF_CAPITAL: Return of capital (cost-based funds)
    - DISTRIBUTION: Distribution (income, interest, etc.)
    - TAX_PAYMENT: Tax payment event
    - DAILY_RISK_FREE_INTEREST_CHARGE: Daily risk-free interest charge (for real IRR)
    - EOFY_DEBT_COST: End of financial year debt cost tax benefit (for real IRR)
    - NAV_UPDATE: NAV update (NAV-based funds)
    - UNIT_PURCHASE: Unit purchase (NAV-based funds)
    - UNIT_SALE: Unit sale (NAV-based funds)
    (Removed: MANAGEMENT_FEE, CARRIED_INTEREST, OTHER)
    """
    CAPITAL_CALL = "capital_call"
    RETURN_OF_CAPITAL = "return_of_capital"
    DISTRIBUTION = "distribution"
    TAX_PAYMENT = "tax_payment"
    DAILY_RISK_FREE_INTEREST_CHARGE = "daily_risk_free_interest_charge"
    EOFY_DEBT_COST = "eofy_debt_cost"
    NAV_UPDATE = "nav_update"
    UNIT_PURCHASE = "unit_purchase"
    UNIT_SALE = "unit_sale"
    # Removed: management_fee, carried_interest, other


class FundType(enum.Enum):
    """Enumeration for fund types."""
    NAV_BASED = "nav_based"  # Funds with NAV updates and unit tracking
    COST_BASED = "cost_based"  # Funds held at cost


class DistributionType(enum.Enum):
    """Enumeration for income distribution types (affects tax treatment).
    
    Australian tax considerations:
    - DIVIDEND_FRANKED: Dividend with franking credits (reduces tax liability)
    - DIVIDEND_UNFRANKED: Dividend without franking credits (fully taxable)
    - INTEREST: Interest income (fully taxable)
    - CAPITAL_GAIN: Capital gains (may have CGT discount)
    """
    INCOME = "income"  # Ordinary income
    DIVIDEND_FRANKED = "dividend_franked"  # Dividend with franking credits
    DIVIDEND_UNFRANKED = "dividend_unfranked"  # Dividend without franking credits
    INTEREST = "interest"  # Interest income
    RENT = "rent"  # Rental income
    CAPITAL_GAIN = "capital_gain"  # Capital gains income
    # Removed generic OTHER to enforce explicit types


class TaxPaymentType(enum.Enum):
    """Enumeration for tax payment types."""
    NON_RESIDENT_INTEREST_WITHHOLDING = "non_resident_interest_withholding"
    NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE = "non_resident_interest_withholding_difference"
    CAPITAL_GAINS_TAX = "capital_gains_tax"
    EOFY_INTEREST_TAX = "eofy_interest_tax"
    DIVIDENDS_FRANKED_TAX = "dividends_franked_tax"
    DIVIDENDS_UNFRANKED_TAX = "dividends_unfranked_tax"
    # Keep other tax payment types as defined; no generic OTHER needed


class FundStatus(enum.Enum):
    """Enumeration for fund status types.
    
    Business definitions:
    - ACTIVE: Equity balance > 0 (fund still invested, has capital at risk)
    - REALIZED: Equity balance = 0 (all capital returned, may still receive distributions)
    - COMPLETED: Final tax statement received after equity balance = 0 (fully realized AND all tax obligations complete)
    """
    ACTIVE = "active"
    REALIZED = "realized"
    COMPLETED = "completed"


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
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (MANUAL) foreign key to investment company
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)  # (MANUAL) foreign key to entity
    name = Column(String(255), nullable=False)  # (MANUAL) fund name
    fund_type = Column(String(100))  # (MANUAL) type of fund (e.g., 'Private Equity', 'Venture Capital')
    
    # Fund tracking type
    tracking_type = Column(Enum(FundType), nullable=False, default=FundType.NAV_BASED)  # (MANUAL) NAV_BASED or COST_BASED
    
    # Investment tracking fields (common)
    commitment_amount = Column(Float, nullable=True)  # (MANUAL) total amount committed to the fund
    current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital movements
    average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance
    expected_irr = Column(Float)  # (MANUAL) expected IRR as percentage
    expected_duration_months = Column(Integer)  # (MANUAL) expected fund duration in months
    
    # IRR storage fields (CALCULATED)
    irr_gross = Column(Float, nullable=True)  # (CALCULATED) Gross IRR when realized/completed
    irr_after_tax = Column(Float, nullable=True)  # (CALCULATED) After-tax IRR when completed
    irr_real = Column(Float, nullable=True)  # (CALCULATED) Real IRR when completed
    
    # NAV-based fund specific fields (CALCULATED)
    current_units = Column(Float, default=0.0)  # (CALCULATED) current number of units owned
    current_unit_price = Column(Float, default=0.0)  # (CALCULATED) current unit price from latest NAV update
    current_nav_total = Column(Float, default=0.0)  # (CALCULATED) current NAV total (units * unit price)
    
    # Cost-based fund specific fields (CALCULATED)
    
    # Status and metadata

    status = Column(Enum(FundStatus), default=FundStatus.ACTIVE)  # (CALCULATED) fund status (ACTIVE/REALIZED/COMPLETED)
    end_date = Column(Date, nullable=True)  # (CALCULATED) fund end date based on last equity/distribution event after equity balance reached zero
    description = Column(Text)  # (MANUAL) fund description
    currency = Column(String(10), default="AUD")  # (MANUAL) currency code for the fund
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="funds", lazy='selectin')
    entity = relationship("Entity", back_populates="funds", lazy='selectin')
    fund_events = relationship("FundEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    tax_statements = relationship("TaxStatement", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    
    @classmethod
    def create(cls, investment_company_id, entity_id, name, fund_type, tracking_type, 
               currency="AUD", description=None, commitment_amount=None, 
               expected_irr=None, expected_duration_months=None, session=None):
        """
        Create a new fund with validation and business logic.
        
        Args:
            investment_company_id (int): ID of the investment company
            entity_id (int): ID of the entity
            name (str): Fund name
            fund_type (str): Type of fund (e.g., "Private Debt", "Equity")
            tracking_type (FundType): Tracking type (COST_BASED or NAV_BASED)
            currency (str): Currency code (default: "AUD")
            description (str, optional): Fund description
            commitment_amount (float, optional): Commitment amount for cost-based funds
            expected_irr (float, optional): Expected IRR percentage
            expected_duration_months (int, optional): Expected duration in months
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            Fund: The created fund
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if not investment_company_id:
            raise ValueError("investment_company_id is required")
        if not entity_id:
            raise ValueError("entity_id is required")
        if not name or not name.strip():
            raise ValueError("Fund name is required and cannot be empty")
        if not fund_type:
            raise ValueError("fund_type is required")
        if not tracking_type:
            raise ValueError("tracking_type is required")
        
        name = name.strip()
        
        # Validate tracking type
        if not isinstance(tracking_type, FundType):
            try:
                tracking_type = FundType(tracking_type)
            except ValueError:
                raise ValueError(f"Invalid tracking_type: {tracking_type}. Must be one of: {[t.value for t in FundType]}")
        
        # Check for existing fund with same name in the same investment company
        existing = session.query(cls).filter(
            cls.name == name,
            cls.investment_company_id == investment_company_id
        ).first()
        if existing:
            raise ValueError(f"Fund with name '{name}' already exists in this investment company")
        
        # Create the fund
        fund = cls(
            investment_company_id=investment_company_id,
            entity_id=entity_id,
            name=name,
            fund_type=fund_type,
            tracking_type=tracking_type,
            currency=currency,
            description=description,
            commitment_amount=commitment_amount,
            expected_irr=expected_irr,
            expected_duration_months=expected_duration_months
        )
        
        session.add(fund)
        session.flush()  # Get the ID without committing
        
        return fund
    
    @classmethod
    def get_by_id(cls, fund_id, session=None):
        """
        Get a fund by ID.
        
        Args:
            fund_id (int): Fund ID
            session (Session): Database session
        
        Returns:
            Fund or None: The fund if found, None otherwise
        """
        return session.query(cls).filter(cls.id == fund_id).first()
    
    @classmethod
    def get_by_investment_company(cls, investment_company_id, session=None):
        """
        Get all funds for a specific investment company.
        
        Args:
            investment_company_id (int): Investment company ID
            session (Session): Database session
        
        Returns:
            list: List of funds for the investment company
        """
        return session.query(cls).filter(cls.investment_company_id == investment_company_id).all()
    
    @classmethod
    def get_all(cls, session=None):
        """
        Get all funds.
        
        Args:
            session (Session): Database session
        
        Returns:
            list: List of all funds
        """
        return session.query(cls).all()
    
    @with_session
    def get_recent_events(self, limit=10, exclude_system_events=True, session=None):
        """
        Get recent events for this fund.
        
        Args:
            limit (int): Maximum number of events to return (default: 10)
            exclude_system_events (bool): Whether to exclude system-generated events (default: True)
            session (Session): Database session
        
        Returns:
            list: List of recent FundEvent objects
        """
        query = session.query(FundEvent).filter(FundEvent.fund_id == self.id)
        
        if exclude_system_events:
            # Exclude system-generated events
            system_events = [
                EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                EventType.EOFY_DEBT_COST
            ]
            query = query.filter(~FundEvent.event_type.in_(system_events))
        
        return query.order_by(FundEvent.event_date.desc()).limit(limit).all()
    
    @with_session
    def get_all_fund_events(self, exclude_system_events=True, session=None):
        """
        Get all events for this fund (excluding system events by default).
        
        Args:
            exclude_system_events (bool): Whether to exclude system-generated events (default: True)
            session (Session): Database session
        
        Returns:
            list: List of all FundEvent objects for this fund
        """
        query = session.query(FundEvent).filter(FundEvent.fund_id == self.id)
        
        if exclude_system_events:
            # Exclude system-generated events
            system_events = [
                EventType.DAILY_RISK_FREE_INTEREST_CHARGE
            ]
            query = query.filter(~FundEvent.event_type.in_(system_events))
        
        return query.order_by(FundEvent.event_date.asc()).all()
    
    @with_session
    def get_summary_data(self, session=None):
        """
        Get summary data for this fund.
        
        Args:
            session (Session): Database session
        
        Returns:
            dict: Summary data including equity balances, event counts, etc.
        """
        # Get all events count (excluding system events)
        all_events = self.get_all_fund_events(session=session)
        total_events_count = len(all_events)
        

        
        # Get last event date from all events
        last_event = max(all_events, key=lambda x: x.event_date) if all_events else None
        
        # Calculate new fields for fund detail redesign
        current_nav_fund_value = self.get_current_nav_fund_value(session=session)
        total_tax_payments = self.get_total_tax_payments(session=session)
        total_daily_interest_charges = self.get_total_daily_interest_charges(session=session)
        total_unit_purchases = self.get_total_unit_purchases(session=session)
        total_unit_sales = self.get_total_unit_sales(session=session)
        total_capital_calls = self.get_total_capital_calls(session=session)
        total_capital_returns = self.get_total_capital_returns(session=session)
        total_distributions = self.get_total_distributions(session=session)
        actual_duration_months = self.calculate_actual_duration_months(session=session)
        completed_irr = self.calculate_completed_irr(session=session)
        completed_after_tax_irr = self.calculate_completed_after_tax_irr(session=session)
        completed_real_irr = self.calculate_completed_real_irr(session=session)
        
        return {
            "id": self.id,
            "name": self.name,
            "fund_type": self.fund_type,
            "tracking_type": self.tracking_type.value if self.tracking_type else None,
            "currency": self.currency,
            "current_equity_balance": float(self.current_equity_balance) if self.current_equity_balance else 0.0,
            "average_equity_balance": float(self.average_equity_balance) if self.average_equity_balance else 0.0,

            "status": self.status.value if self.status else FundStatus.ACTIVE.value,
            "commitment_amount": float(self.commitment_amount) if self.commitment_amount else None,
            "expected_irr": float(self.expected_irr) if self.expected_irr else None,
            "expected_duration_months": self.expected_duration_months,
            "description": self.description,
            "investment_company": self.investment_company.name if self.investment_company else "Unknown",
            "investment_company_id": self.investment_company_id,
            "entity": self.entity.name if self.entity else "Unknown",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            # New fields for fund detail redesign
            "current_nav_fund_value": current_nav_fund_value,
            "total_tax_payments": total_tax_payments,
            "total_daily_interest_charges": total_daily_interest_charges,
            "total_unit_purchases": total_unit_purchases,
            "total_unit_sales": total_unit_sales,
            "total_capital_calls": total_capital_calls,
            "total_capital_returns": total_capital_returns,
            "total_distributions": total_distributions,
            "actual_duration_months": actual_duration_months,
            "completed_irr": completed_irr,
            "completed_after_tax_irr": completed_after_tax_irr,
            "completed_real_irr": completed_real_irr,
            # NAV-based fund specific fields
            "current_units": float(self.current_units) if self.current_units else None,
            "current_unit_price": float(self.current_unit_price) if self.current_unit_price else None,
            "current_nav_total": float(self.current_nav_total) if self.current_nav_total else None,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None
        }
    
    def __repr__(self):
        """Return a string representation of the Fund instance for debugging/logging."""
        return f"<Fund(id={self.id}, name='{self.name}', company='{self.investment_company.name if self.investment_company else 'Unknown'}')>"
    
    @with_session
    def _create_or_update_tax_statement_object(self, entity_id, financial_year, **kwargs):
        """Create or update a tax statement object.
        Returns the TaxStatement object. No database operations.
        """
        from ..tax.models import TaxStatement
        # Try to find existing statement
        statement = self.get_tax_statement_for_entity_financial_year(entity_id, financial_year)
        
        if statement is None:
            # Create new statement
            # Remove session from kwargs if present
            kwargs.pop('session', None)
            statement = TaxStatement(
                fund_id=self.id,
                entity_id=entity_id,
                financial_year=financial_year,
                **kwargs
            )
        else:
            # Update existing statement
            for key, value in kwargs.items():
                if hasattr(statement, key):
                    setattr(statement, key, value)
        
        # Calculate interest income amount (including total_interest_income)
        statement.calculate_interest_income_amount()

        return statement

    @with_session
    def create_or_update_tax_statement(self, entity_id, financial_year, **kwargs):
        """Create or update a tax statement for a specific entity and financial year.
        If a statement exists, updates its fields; otherwise, creates a new one.
        Commits the change to the database.
        Returns the TaxStatement instance.
        """
        from src.tax.models import TaxStatement
        from sqlalchemy.orm import object_session
        session = object_session(self)
        
        # Create or update statement object using business logic method
        statement = self._create_or_update_tax_statement_object(entity_id, financial_year, **kwargs)
        
        # Add to session if it's a new statement
        if statement.id is None:
            session.add(statement)
        
        session.commit()
        
        # Update fund status after tax statement creation/update
        self.update_status_after_tax_statement(session=session)
        
        return statement
    
    @with_session
    def get_tax_statement_for_entity_financial_year(self, entity_id, financial_year, session=None):
        """Return the tax statement for a specific entity and financial year, or None if not found."""
        from src.tax.models import TaxStatement
        if session is None:
            session = object_session(self)
        return session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id,
            TaxStatement.entity_id == entity_id,
            TaxStatement.financial_year == financial_year
        ).first()
    
    @with_session
    def calculate_debt_cost(self, session=None, risk_free_rate_currency=None):
        """Calculate the debt cost (opportunity cost) for the fund using daily or period-by-period accuracy.
        Uses risk-free rates for the fund's currency. Returns None if required data is missing.
        """
        if risk_free_rate_currency is None:
            risk_free_rate_currency = self.currency
        start_date = self.start_date
        end_date = self.end_date
        if not start_date or not end_date:
            return None
        events = [e for e in self.fund_events if e.event_date >= start_date and e.event_date <= end_date]
        risk_free_rates = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == risk_free_rate_currency,
            RiskFreeRate.rate_date <= end_date
        ).order_by(RiskFreeRate.rate_date).all()
        if not risk_free_rates:
            return None
        return calculate_debt_cost(events, risk_free_rates, start_date, end_date, self.currency)
    
    def _calculate_daily_interest_charge_objects(self, start_date, end_date, risk_free_rates, existing_dates, cash_flow_events):
        """Calculate daily interest charge events for the fund period.
        Returns a list of FundEvent objects. No database operations.
        """
        from datetime import timedelta
        from sqlalchemy.orm import object_session
        session = object_session(self)
        created_events = []
        current_date = start_date
        # Pre-fetch all capital events with their current_equity_balance
        capital_event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE] if self.tracking_type == FundType.NAV_BASED else [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
        capital_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_(capital_event_types)
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        # Build a list of (date, equity_balance) tuples
        equity_by_date = []
        for e in capital_events:
            equity_by_date.append((e.event_date, e.current_equity_balance if e.current_equity_balance is not None else 0.0))
        # For each day, find the most recent capital event on or before that day
        while current_date <= end_date:
            rate = None
            if current_date not in existing_dates:
                # Find risk-free rate for this date
                rate = get_risk_free_rate_for_date(current_date, risk_free_rates)
            # Find latest equity balance as of this date
            equity = 0.0
            for event_date, eq in reversed(equity_by_date):
                if event_date <= current_date:
                    equity = eq
                    break
            if rate is not None and equity > 0:
                daily_interest = equity * (rate / 100) / 365.25
                interest_event = FundEvent(
                    fund_id=self.id,
                    event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                    event_date=current_date,
                    amount=daily_interest,
                    description=f"Daily risk-free interest charge ({rate:.2f}% p.a.)",
                    reference_number=f"RFR-{current_date.strftime('%Y%m%d')}"
                )
                created_events.append(interest_event)
            current_date += timedelta(days=1)
        return created_events
    
    @with_session
    def create_daily_risk_free_interest_charges(self, session=None, risk_free_rate_currency=None):
        """Create daily risk-free interest charge events for the fund for real IRR calculations.
        Commits new events to the database.
        Returns a list of created events.
        """
        # Use fund currency if not specified
        if risk_free_rate_currency is None:
            risk_free_rate_currency = self.currency
        
        # Get start and end dates
        start_date = self.start_date
        end_date = self.end_date
        
        if not start_date or not end_date:
            return []
        
        # Get risk-free rates for the period - get all rates <= end_date
        # The get_risk_free_rate_for_date function will find the most recent rate <= target_date
        risk_free_rates = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == risk_free_rate_currency,
            RiskFreeRate.rate_date <= end_date
        ).order_by(RiskFreeRate.rate_date).all()
        
        if not risk_free_rates:
            print(f"Warning: No risk-free rates found for {risk_free_rate_currency} <= {end_date}")
            return []
        
        # Get all existing interest charge events to avoid duplicates
        existing_charges = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).all()
        existing_dates = {event.event_date for event in existing_charges}
        
        # Get all cash flow events to track equity balance
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.UNIT_PURCHASE,
                EventType.RETURN_OF_CAPITAL,
                EventType.UNIT_SALE
            ])
        ).order_by(FundEvent.event_date).all()
        
        # Calculate daily interest charge events using business logic method
        created_events = self._calculate_daily_interest_charge_objects(
            start_date, end_date, risk_free_rates, existing_dates, cash_flow_events
        )
        
        # Add events to session
        for event in created_events:
            session.add(event)
        
        if created_events:
            session.commit()
            print(f"Created {len(created_events)} daily risk-free interest charge events for {self.name}")
        
        return created_events
    
    @with_session
    def calculate_eofy_debt_interest_deduction_sum_of_daily_interest(self, financial_year, session=None):
        """Calculate the total interest expense for a given financial year for the fund.
        Used for tax deduction calculations. Returns the total expense as a float.
        """
        # Get financial year dates
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return 0.0
        
        # Parse financial year (e.g., "2023-24" or "2023-2024")
        if '-' in financial_year:
            start_year, end_year = financial_year.split('-')
            start_year = int(start_year)
            if len(end_year) == 2:
                end_year = int(f"20{end_year}")
            else:
                end_year = int(end_year)
            
            if entity.tax_jurisdiction == "AU":
                # Australian FY: July 1 to June 30
                fy_start = date(start_year, 7, 1)
                fy_end = date(end_year, 6, 30)
            else:
                # Default to calendar year
                fy_start = date(start_year, 1, 1)
                fy_end = date(start_year, 12, 31)
        else:
            # Single year format (e.g., "2023")
            year = int(financial_year)
            if entity.tax_jurisdiction == "AU":
                fy_start = date(year, 7, 1)
                fy_end = date(year + 1, 6, 30)
            else:
                fy_start = date(year, 1, 1)
                fy_end = date(year, 12, 31)
        
        # Sum all daily interest charges for this financial year
        total_interest = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end
        ).scalar()
        
        return abs(total_interest) if total_interest else 0.0
    
    @with_session
    def _process_financial_year_for_debt_cost(self, fy, session=None):
        """Process a single financial year for debt cost events.
        Returns a list of created events. No database operations.
        """
        created_events = []
        
        # Only proceed if a TaxStatement exists for this FY
        tax_statement = self.get_tax_statement_for_entity_financial_year(self.entity_id, fy, session=session)
        if not tax_statement:
            return created_events  # Skip years with no TaxStatement
        
        # Calculate interest expense for this FY
        eofy_debt_interest_deduction_sum_of_daily_interest = self.calculate_eofy_debt_interest_deduction_sum_of_daily_interest(fy, session=session)
        
        # Set the interest expense on the tax statement
        tax_statement.eofy_debt_interest_deduction_sum_of_daily_interest = eofy_debt_interest_deduction_sum_of_daily_interest
        
        # Calculate tax benefit and create event
        eofy_debt_interest_deduction_total_deduction = tax_statement.calculate_eofy_debt_interest_deduction_total_deduction()
        if eofy_debt_interest_deduction_total_deduction > 0:
            from src.tax.events import TaxEventFactory
            event = TaxEventFactory.create_eofy_debt_cost_event(tax_statement, session=session)
            if event:
                created_events.append(event)
        
        return created_events
    
    @with_session
    def create_eofy_debt_cost_events(self, session=None):
        """Create financial year debt cost events for the fund for real IRR calculations.
        Commits new events to the database.
        Returns a list of created events.
        """
        created_events = []
        
        # Get all financial years where the fund had activity
        start_date = self.start_date
        end_date = self.end_date or date.today()
        if not start_date:
            return created_events
        
        # Get entity to determine jurisdiction
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return created_events
        
        # Generate financial years from start to end
        financial_years = get_financial_years_for_fund_period(start_date, end_date, entity)
        
        # Process each financial year
        for fy in sorted(financial_years):
            events = self._process_financial_year_for_debt_cost(fy, session=session)
            for event in events:
                session.add(event)
            created_events.extend(events)
        
        if created_events:
            session.commit()
            print(f"Created {len(created_events)} FY debt cost events for {self.name}")
        
        return created_events
    
    @with_session
    def _delete_debt_cost_events(self, session=None):
        """Delete all daily risk-free interest charges and FY debt cost events for this fund.
        Returns a tuple of (deleted_daily_count, deleted_fy_count).
        No database operations.
        """
        # Delete all DAILY_RISK_FREE_INTEREST_CHARGE and EOFY_DEBT_COST events for this fund
        deleted_daily = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).delete()
        deleted_fy = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.EOFY_DEBT_COST
        ).delete()
        return deleted_daily, deleted_fy
    
    @with_session
    def recalculate_debt_costs(self, session=None, risk_free_rate_currency=None):
        """Recalculate all daily risk-free interest charges and FY debt cost events for this fund.
        Deletes existing events of these types and recreates them.
        Commits all changes to the database.
        """
        # Delete existing debt cost events
        deleted_daily, deleted_fy = self._delete_debt_cost_events(session=session)
        session.commit()
        
        # Recreate daily risk-free interest charges
        self.create_daily_risk_free_interest_charges(session=session, risk_free_rate_currency=risk_free_rate_currency)
        # Recreate FY debt cost events
        self.create_eofy_debt_cost_events(session)
        session.commit()
        print(f"Recalculated debt costs for fund '{self.name}': deleted {deleted_daily} daily interest charges, {deleted_fy} FY debt cost events, and recreated them.")
    
    @with_session
    def get_distributions_by_type(self, session=None):
        """Return a dictionary of total distributions grouped by type (for tax analysis).
        Keys are DistributionType enums, values are summed amounts.
        """
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.DISTRIBUTION])
        ).all()
        
        # Group by distribution type
        distributions_by_type = {}
        for event in distribution_events:
            dist_type = event.distribution_type  # None when unspecified; treat as missing
            if dist_type not in distributions_by_type:
                distributions_by_type[dist_type] = 0
            distributions_by_type[dist_type] += event.amount or 0
        
        return distributions_by_type
    
    @with_session
    def get_total_distributions(self, session=None):
        """Return the total amount of all distributions for the fund (regardless of type).
        Used for fund comparison and reporting.
        """
        from sqlalchemy import func
        
        # Sum all distribution events
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).scalar() or 0
        
        return total
    
    @with_session
    def get_taxable_distributions(self, session=None):
        """Return the total taxable distributions (gross minus tax withheld).
        Used for tax reporting. Returns 0 if no distributions exist.
        """
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.DISTRIBUTION])
        ).all()
        
        # Sum up the net amounts (amount - tax_withheld)
        total_taxable = sum(
            (event.amount or 0) - (event.tax_withheld or 0)
            for event in distribution_events
        )
        
        return total_taxable
    
    @with_session
    def get_gross_distributions(self, session=None):
        """Return the total gross distributions (including tax withheld).
        Sums the amount field of all distribution events.
        """
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.DISTRIBUTION])
        ).all()
        
        # Sum up the gross amounts (amount field contains gross amount)
        total_gross = sum(event.amount or 0 for event in distribution_events)
        
        return total_gross
    
    def get_net_distributions(self, session=None):
        """Return the total net distributions (gross minus tax withheld).
        Uses get_gross_distributions and get_total_tax_withheld.
        """
        gross = self.get_gross_distributions(session)
        tax_withheld = self.get_total_tax_withheld(session)
        return gross - tax_withheld
    
    @with_session
    def get_total_tax_withheld(self, session=None):
        """Return the total tax withheld across all tax payment events for this fund.
        Sums the amount field of all TAX_PAYMENT events.
        """
        from sqlalchemy import func
        # Get all tax payment events
        total_tax_withheld = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).scalar() or 0
        
        return total_tax_withheld
    
    @with_session
    def get_distributions_with_tax_details(self, session=None):
        """Return a dictionary of distributions by type, including gross, tax withheld, net, and event details.
        Useful for detailed tax analysis and reporting.
        """
        from sqlalchemy import func

        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).order_by(FundEvent.event_date).all()
        
        # Get all tax payment events for this fund
        tax_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).all()
        
        # Create a mapping of distribution dates to tax amounts
        tax_by_date = {}
        for tax_event in tax_events:
            date_key = tax_event.event_date
            if date_key not in tax_by_date:
                tax_by_date[date_key] = 0
            tax_by_date[date_key] += tax_event.amount or 0
        
        # Group by distribution type
        distributions_by_type = {}
        
        for event in distribution_events:
            dist_type = event.distribution_type.value if event.distribution_type else "unknown"
            
            if dist_type not in distributions_by_type:
                distributions_by_type[dist_type] = {
                    'gross_amount': 0,
                    'tax_withheld': 0,
                    'net_amount': 0,
                    'events': []
                }
            
            gross_amount = event.amount or 0
            tax_withheld = tax_by_date.get(event.event_date, 0)
            net_amount = gross_amount - tax_withheld
            
            distributions_by_type[dist_type]['gross_amount'] += gross_amount
            distributions_by_type[dist_type]['tax_withheld'] += tax_withheld
            distributions_by_type[dist_type]['net_amount'] += net_amount
            distributions_by_type[dist_type]['events'].append({
                'date': event.event_date,
                'gross_amount': gross_amount,
                'tax_withheld': tax_withheld,
                'net_amount': net_amount,
                'description': event.description
            })
        
        return distributions_by_type
    
    def _add_distribution_validate_distribution_parameters(
        self,
        event_date,
        distribution_type,
        distribution_amount=None,
        has_withholding_tax=False,
        gross_interest_amount=None,
        net_interest_amount=None,
        withholding_tax_amount=None,
        withholding_tax_rate=None,
        session=None
    ):
        """
        Validate all parameters for add_distribution method.
        
        This method implements the three-tier validation system:
        - Group A: General validations (always run)
        - Group B: Withholding tax validations (when has_withholding_tax=True)
        - Group C: Simple distribution validations (when has_withholding_tax=False)
        
        Args:
            event_date: Distribution date
            distribution_type: Type of distribution (DistributionType enum)
            distribution_amount: Simple distribution amount (when has_withholding_tax=False)
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount (when has_withholding_tax=True)
            net_interest_amount: Net interest amount (when has_withholding_tax=True)
            withholding_tax_amount: Tax amount withheld (when has_withholding_tax=True)
            withholding_tax_rate: Tax rate percentage (when has_withholding_tax=True)
            session: Database session
            
        Raises:
            ValueError: If any validation fails with specific error message
        """
        # Group A: General validations (always run)
        if not event_date:
            raise ValueError("event_date is required")
        if not distribution_type:
            raise ValueError("distribution_type is required")
        if session is None:
            raise ValueError("session parameter is required for database operations")
        
        # Type validations
        if not isinstance(distribution_type, DistributionType):
            raise ValueError(f"Invalid distribution_type: {distribution_type}. Must be a valid DistributionType enum value.")
        if not isinstance(event_date, date):
            raise ValueError("event_date must be a valid date")
        
        # Group B or C: Scenario-specific validations
        if has_withholding_tax:
            # Group B: Validations when has_withholding_tax=True
            if distribution_type != DistributionType.INTEREST:
                raise ValueError(f"Withholding tax (has_withholding_tax=True) is only valid for INTEREST distributions, not {distribution_type}")
            
            # Amount parameter validation - must use gross/net interest amounts
            if distribution_amount is not None:
                raise ValueError("When has_withholding_tax=True, distribution_amount must be None (use gross_interest_amount or net_interest_amount)")
            
            # Exactly one of gross_interest_amount or net_interest_amount
            interest_params = [gross_interest_amount, net_interest_amount]
            provided_interest = [p for p in interest_params if p is not None]
            if len(provided_interest) != 1:
                raise ValueError("When has_withholding_tax=True, must provide exactly one of gross_interest_amount or net_interest_amount")
            
            # Exactly one of withholding_tax_amount or withholding_tax_rate
            withholding_params = [withholding_tax_amount, withholding_tax_rate]
            provided_withholding = [p for p in withholding_params if p is not None]
            if len(provided_withholding) != 1:
                raise ValueError("When has_withholding_tax=True, must provide exactly one of withholding_tax_amount or withholding_tax_rate")
            
            # Value validations
            if gross_interest_amount is not None and gross_interest_amount <= 0:
                raise ValueError("gross_interest_amount must be a positive number")
            if net_interest_amount is not None and net_interest_amount <= 0:
                raise ValueError("net_interest_amount must be a positive number")
            if withholding_tax_amount is not None and withholding_tax_amount <= 0:
                raise ValueError("withholding_tax_amount must be a positive number")
            if withholding_tax_rate is not None and withholding_tax_rate <= 0:
                raise ValueError("withholding_tax_rate must be a positive number")
            if withholding_tax_rate is not None and withholding_tax_rate > 100:
                raise ValueError("withholding_tax_rate must be between 0 and 100")
        else:
            # Group C: Validations when has_withholding_tax=False
            # Must use distribution_amount (not gross/net interest amounts)
            if gross_interest_amount is not None or net_interest_amount is not None:
                raise ValueError("gross_interest_amount and net_interest_amount are only valid when has_withholding_tax=True")
            
            # Must not provide withholding tax parameters
            if withholding_tax_amount is not None or withholding_tax_rate is not None:
                raise ValueError("withholding_tax_amount and withholding_tax_rate are only valid when has_withholding_tax=True")
            
            # distribution_amount is required and must be positive
            if distribution_amount is None:
                raise ValueError("distribution_amount is required when has_withholding_tax=False")
            if distribution_amount <= 0:
                raise ValueError("distribution_amount must be a positive number")

    @with_session
    def add_distribution(
        self,
        event_date,
        distribution_type,
        distribution_amount=None,
        has_withholding_tax=False,
        gross_interest_amount=None,
        net_interest_amount=None,
        withholding_tax_amount=None,
        withholding_tax_rate=None,
        description=None,
        reference_number=None,
        session=None
    ):
        """
        Unified method to add distribution events.
        
        Handles all distribution scenarios:
        - Simple distributions (amount + type)
        - Interest distributions with withholding tax (gross/net + tax amount/rate)
        - Interest distributions without withholding tax
        
        **IDEMPOTENT BEHAVIOR**: If a distribution with the same date, type, amount, and reference_number already exists,
        the existing event is returned without creating duplicates.
        
        Args:
            event_date: Distribution date
            distribution_type: Type of distribution (DistributionType enum)
            distribution_amount: Simple distribution amount (when has_withholding_tax=False)
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount (when has_withholding_tax=True)
            net_interest_amount: Net interest amount (when has_withholding_tax=True)
            withholding_tax_amount: Tax amount withheld (when has_withholding_tax=True)
            withholding_tax_rate: Tax rate percentage (when has_withholding_tax=True)
            description: Event description
            reference_number: External reference number
            session: Database session
            
        Returns:
            tuple: (distribution_event, tax_event) where tax_event may be None
        """
        # Validate all parameters before proceeding with business logic
        self._add_distribution_validate_distribution_parameters(
            event_date=event_date,
            distribution_type=distribution_type,
            distribution_amount=distribution_amount,
            has_withholding_tax=has_withholding_tax,
            gross_interest_amount=gross_interest_amount,
            net_interest_amount=net_interest_amount,
            withholding_tax_amount=withholding_tax_amount,
            withholding_tax_rate=withholding_tax_rate,
            session=session
        )
        
        # Check for existing duplicate event (idempotent behavior)
        if has_withholding_tax:
            # For withholding tax distributions, check by date, type, and reference
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.DISTRIBUTION,
                FundEvent.event_date == event_date,
                FundEvent.distribution_type == DistributionType.INTEREST,
                FundEvent.reference_number == reference_number,
                FundEvent.has_withholding_tax == True
            ).first()
        else:
            # For simple distributions, check by date, type, amount, and reference
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.DISTRIBUTION,
                FundEvent.event_date == event_date,
                FundEvent.distribution_type == distribution_type,
                FundEvent.amount == distribution_amount,
                FundEvent.reference_number == reference_number
            ).first()
        
        if existing_event:
            # Return existing event without creating duplicate
            # For withholding tax distributions, also find and return the tax event
            if has_withholding_tax:
                tax_event = session.query(FundEvent).filter(
                    FundEvent.fund_id == self.id,
                    FundEvent.event_type == EventType.TAX_PAYMENT,
                    FundEvent.event_date == event_date,
                    FundEvent.reference_number == f"{reference_number}_TAX" if reference_number else None
                ).first()
                return existing_event, tax_event
            else:
                return existing_event, None
        
        # Business logic implementation
        if has_withholding_tax:
            # Calculate missing values using exact logic from add_interest_distribution_with_withholding_tax
            if gross_interest_amount is not None:
                gross_amount = float(gross_interest_amount)
                if withholding_tax_amount is not None:
                    tax_withheld = float(withholding_tax_amount)
                    net_amount = gross_amount - tax_withheld
                    tax_rate = (tax_withheld / gross_amount) * 100 if gross_amount else 0.0
                else:
                    tax_rate = float(withholding_tax_rate)
                    tax_withheld = (gross_amount * tax_rate) / 100
                    net_amount = gross_amount - tax_withheld
            else:
                net_amount = float(net_interest_amount)
                if withholding_tax_amount is not None:
                    tax_withheld = float(withholding_tax_amount)
                    gross_amount = net_amount + tax_withheld
                    tax_rate = (tax_withheld / gross_amount) * 100 if gross_amount else 0.0
                else:
                    tax_rate = float(withholding_tax_rate)
                    gross_amount = (net_amount * 100) / (100 - tax_rate) if tax_rate != 100 else 0.0
                    tax_withheld = gross_amount - net_amount
            
            # Create distribution event
            distribution_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.DISTRIBUTION,
                event_date=event_date,
                amount=gross_amount,
                distribution_type=DistributionType.INTEREST,
                description=description or f"Distribution: ${gross_amount:,.2f}",
                reference_number=reference_number,
                has_withholding_tax=True  # Set flag to true since this method creates withholding tax
            )
            session.add(distribution_event)
            
            # Create tax payment event if there's tax withheld
            tax_event = None
            if tax_withheld > 0:
                from .models import TaxPaymentType
                tax_event = FundEvent(
                    fund_id=self.id,
                    event_type=EventType.TAX_PAYMENT,
                    event_date=event_date,
                    amount=tax_withheld,
                    description=f"Tax withheld on distribution: ${tax_withheld:,.2f}",
                    reference_number=f"{reference_number}_TAX" if reference_number else None,
                    tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
                )
                session.add(tax_event)
            
            # Calculate end_date (may affect status)
            self.calculate_end_date(session=session)
            
            return distribution_event, tax_event
        else:
            # Simple distribution without withholding tax
            distribution_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.DISTRIBUTION,
                event_date=event_date,
                amount=float(distribution_amount),
                distribution_type=distribution_type,
                description=description or f"Distribution: ${distribution_amount:,.2f}",
                reference_number=reference_number,
                has_withholding_tax=False
            )
            session.add(distribution_event)
            session.flush()
            
            # Calculate end_date (may affect status)
            self.calculate_end_date(session=session)
            
            return distribution_event, None
    
    def _calculate_nav_change_fields(self, nav_per_share, date, session):
        """
        Calculate NAV change fields for a NAV_UPDATE event.
        Returns (previous_nav_per_share, nav_change_absolute, nav_change_percentage)
        """
        # Find the most recent NAV_UPDATE event before this date
        previous_nav_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE,
            FundEvent.event_date < date
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        
        previous_nav_per_share = previous_nav_event.nav_per_share if previous_nav_event else None
        
        if previous_nav_per_share is not None:
            nav_change_absolute = nav_per_share - previous_nav_per_share
            nav_change_percentage = (nav_change_absolute / previous_nav_per_share) * 100
        else:
            nav_change_absolute = None
            nav_change_percentage = None
            
        return previous_nav_per_share, nav_change_absolute, nav_change_percentage

    def _update_subsequent_nav_change_fields(self, new_nav_event, session):
        """
        Update NAV change fields for the next NAV_UPDATE event after the new one.
        """
        # Find the next NAV_UPDATE event after this one
        next_nav_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE,
            FundEvent.event_date > new_nav_event.event_date
        ).order_by(FundEvent.event_date, FundEvent.id).first()
        
        if next_nav_event:
            # Recalculate the next event's NAV change fields
            prev_nav, abs_change, pct_change = self._calculate_nav_change_fields(
                next_nav_event.nav_per_share, next_nav_event.event_date, session
            )
            next_nav_event.previous_nav_per_share = prev_nav
            next_nav_event.nav_change_absolute = abs_change
            next_nav_event.nav_change_percentage = pct_change

    @with_session
    def add_nav_update(self, nav_per_share, date, description=None, reference_number=None, session=None):
        """
        Add a NAV update event. If this is the latest NAV_UPDATE event, update NAV-specific fund summary fields.
        
        **IDEMPOTENT BEHAVIOR**: If a NAV update with the same date and reference_number already exists,
        the existing event is returned without creating duplicates.
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("NAV updates are only applicable for NAV-based funds")
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE,
            FundEvent.event_date == date,
            FundEvent.reference_number == reference_number
        ).first()
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Calculate NAV change fields
        previous_nav_per_share, nav_change_absolute, nav_change_percentage = self._calculate_nav_change_fields(
            nav_per_share, date, session
        )
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.NAV_UPDATE,
            event_date=date,
            nav_per_share=nav_per_share,
            previous_nav_per_share=previous_nav_per_share,
            nav_change_absolute=nav_change_absolute,
            nav_change_percentage=nav_change_percentage,
            description=description or f"NAV update: ${nav_per_share:.4f}",
            reference_number=reference_number
        )
        session.add(event)
        session.flush()
        
        # Update the next NAV_UPDATE event's change fields if it exists
        self._update_subsequent_nav_change_fields(event, session)
        
        # Check if this is the latest NAV_UPDATE event
        latest_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        if latest_event and latest_event.id == event.id:
            self.current_unit_price = nav_per_share
            # current_units should be updated elsewhere (unit purchase/sale), not here
            self.current_nav_total = (self.current_units or 0.0) * nav_per_share
            session.commit()
        return event



    @with_session
    def get_events(self, event_types=None, start_date=None, end_date=None, session=None):
        """Get events for this fund with optional filtering.
        
        Args:
            event_types (list): List of EventType to filter by
            start_date (date): Start date for filtering
            end_date (date): End date for filtering
            session: Database session
            
        Returns:
            list: List of FundEvent objects
        """
        query = session.query(FundEvent).filter(FundEvent.fund_id == self.id)
        
        if event_types:
            query = query.filter(FundEvent.event_type.in_(event_types))
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()

    @with_session
    def delete_event(self, event_id, session=None):
        """Delete a specific event and recalculate affected fields.
        
        Args:
            event_id (int): ID of the event to delete
            session: Database session
            
        Returns:
            bool: True if event was deleted, False if not found
        """
        event = session.query(FundEvent).filter(
            FundEvent.id == event_id,
            FundEvent.fund_id == self.id
        ).first()
        
        if not event:
            return False
        
        # Store event type for recalculation
        event_type = event.event_type
        
        # For withholding interest distributions, also delete the related tax payment event
        if (event.event_type == EventType.DISTRIBUTION and 
            event.distribution_type == DistributionType.INTEREST):
            
            # Find and delete the corresponding tax payment event
            tax_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_date == event.event_date,
                FundEvent.event_type == EventType.TAX_PAYMENT,
                FundEvent.tax_payment_type == TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
            ).first()
            
            if tax_event:
                session.delete(tax_event)
        
        # Delete the main event
        session.delete(event)
        session.flush()  # Ensure deletion is reflected in queries

        # For capital events, trigger recalculation from the previous event
        if event.event_type in [
            EventType.CAPITAL_CALL,
            EventType.RETURN_OF_CAPITAL,
            EventType.UNIT_PURCHASE,
            EventType.UNIT_SALE
        ]:
            # Find the previous capital event (by date and id)
            prev_event = (
                session.query(FundEvent)
                .filter(
                    FundEvent.fund_id == self.id,
                    FundEvent.event_type.in_([
                        EventType.CAPITAL_CALL,
                        EventType.RETURN_OF_CAPITAL,
                        EventType.UNIT_PURCHASE,
                        EventType.UNIT_SALE
                    ]),
                    (FundEvent.event_date < event.event_date) |
                    ((FundEvent.event_date == event.event_date) & (FundEvent.id < event.id))
                )
                .order_by(FundEvent.event_date.desc(), FundEvent.id.desc())
                .first()
            )
            if prev_event:
                self.recalculate_capital_chain_from(prev_event, session=session)
            else:
                # No previous event, recalculate from the first capital event
                first_event = (
                    session.query(FundEvent)
                    .filter(
                        FundEvent.fund_id == self.id,
                        FundEvent.event_type.in_([
                            EventType.CAPITAL_CALL,
                            EventType.RETURN_OF_CAPITAL,
                            EventType.UNIT_PURCHASE,
                            EventType.UNIT_SALE
                        ])
                    )
                    .order_by(FundEvent.event_date.asc(), FundEvent.id.asc())
                    .first()
                )
                if first_event:
                    self.recalculate_capital_chain_from(first_event, session=session)
                else:
                    # No capital events left, just update end_date and status
                    self.calculate_end_date(session=session)
                    self.update_status_after_equity_event(session=session)
        else:
            # For non-capital events (distributions, etc.), just update end_date and status
            self.calculate_end_date(session=session)
            self.update_status_after_equity_event(session=session)
        
        return True

    def _create_bulk_event_objects(self, events_data):
        """Create FundEvent objects from event data.
        Returns a list of FundEvent objects. No database operations.
        """
        created_events = []
        
        for event_data in events_data:
            event = FundEvent(
                fund_id=self.id,
                **event_data
            )
            created_events.append(event)
        
        return created_events

    @with_session
    def bulk_add_events(self, events_data, session=None):
        """Add multiple events in a single operation.
        
        Args:
            events_data (list): List of dictionaries with event data
            session: Database session
            
        Returns:
            list: List of created FundEvent objects
        """
        # Create event objects using business logic method
        created_events = self._create_bulk_event_objects(events_data)
        
        # Add events to session
        for event in created_events:
            session.add(event)
        
        # Recalculate all fields after bulk operation
        self.recalculate_all_fields(session=session)
        
        return created_events


    @with_session
    def update_status(self, session=None):
        """Update the fund's status based on current state.
        Commits the change to the database if the status changes.
        Also calculates and stores IRRs based on the new status.
        """
        from sqlalchemy.orm import object_session
        if session is None:
            session = object_session(self)
        
        # Determine what the status should be based on current equity balance
        if self.tracking_type == FundType.NAV_BASED:
            has_equity = self.current_units is not None and self.current_units > 0
        elif self.tracking_type == FundType.COST_BASED:
            has_equity = self.current_equity_balance is not None and self.current_equity_balance > 0
        else:
            has_equity = False
        
        if has_equity:
            new_status = FundStatus.ACTIVE
        else:
            # Fund is realized (equity balance = 0)
            # Check if it should be COMPLETED based on tax statements
            if self.is_final_tax_statement_received(session=session):
                new_status = FundStatus.COMPLETED
            else:
                new_status = FundStatus.REALIZED
        
        if self.status != new_status:
            old_status = self.status
            self.status = new_status
            
            # Calculate and store IRRs based on new status
            self._calculate_and_store_irrs_for_status(new_status, session=session)
            
            session.commit()
            print(f"Fund '{self.name}' status updated: {old_status.value} → {new_status.value}")
        else:
            # Status didn't change, but we still need to recalculate IRRs if the fund is REALIZED or COMPLETED
            # (events may have been modified that affect IRR calculations)
            if self.status in [FundStatus.REALIZED, FundStatus.COMPLETED]:
                self._calculate_and_store_irrs_for_status(self.status, session=session)
                session.commit()
                print(f"Fund '{self.name}' status unchanged ({self.status.value}) but IRRs recalculated")

    def _calculate_and_store_irrs_for_status(self, status, session=None):
        """Calculate and store IRRs based on fund status.
        
        Business rules:
        - ACTIVE: All IRRs = None (fund has capital at risk)
        - REALIZED: irr_gross only, others = None (all capital returned)
        - COMPLETED: All IRRs calculated (all tax obligations complete)
        """
        # Reset all IRRs to None initially
        self.irr_gross = None
        self.irr_after_tax = None
        self.irr_real = None
        
        if status == FundStatus.ACTIVE:
            # ACTIVE: No IRRs meaningful (fund has capital at risk)
            print(f"  [IRR] Fund '{self.name}' is ACTIVE - no IRRs calculated")
            return
        
        elif status == FundStatus.REALIZED:
            # REALIZED: Calculate gross IRR only
            try:
                self.irr_gross = self.calculate_irr(session=session)
                print(f"  [IRR] Fund '{self.name}' REALIZED - gross IRR: {self.irr_gross:.2%}" if self.irr_gross else f"  [IRR] Fund '{self.name}' REALIZED - gross IRR: None")
            except Exception as e:
                print(f"  [IRR] Error calculating gross IRR for '{self.name}': {e}")
                self.irr_gross = None
        
        elif status == FundStatus.COMPLETED:
            # COMPLETED: Calculate all IRRs
            try:
                # Ensure daily interest charges exist for real IRR calculation
                self.create_daily_risk_free_interest_charges(session=session)
                
                # Calculate all IRRs
                self.irr_gross = self.calculate_irr(session=session)
                self.irr_after_tax = self.calculate_after_tax_irr(session=session)
                self.irr_real = self.calculate_real_irr(session=session)
                
                print(f"  [IRR] Fund '{self.name}' COMPLETED - gross: {self.irr_gross:.2%}, after-tax: {self.irr_after_tax:.2%}, real: {self.irr_real:.2%}" if all([self.irr_gross, self.irr_after_tax, self.irr_real]) else f"  [IRR] Fund '{self.name}' COMPLETED - some IRRs could not be calculated")
            except Exception as e:
                print(f"  [IRR] Error calculating IRRs for '{self.name}': {e}")
                self.irr_gross = None
                self.irr_after_tax = None
                self.irr_real = None

    @with_session
    def update_status_after_equity_event(self, session=None):
        """Update status after equity balance changes (capital calls, returns, unit purchases/sales).
        This is the primary method for automatic status updates.
        """
        self.update_status(session=session)

    @with_session
    def update_status_after_tax_statement(self, session=None):
        """Update status after tax statement is added or removed.
        This checks if the fund should transition between REALIZED and COMPLETED.
        Also recalculates IRRs when tax statements change.
        """
        # Only update if fund is not ACTIVE (i.e., REALIZED or COMPLETED)
        if self.status == FundStatus.ACTIVE:
            print(f"Fund '{self.name}' tax statement added, but remains {self.status.value}")
            return
        
        # Check if this tax statement makes the fund COMPLETED
        if self.is_final_tax_statement_received(session=session):
            if self.status == FundStatus.REALIZED:
                # Transition from REALIZED to COMPLETED
                old_status = self.status
                self.status = FundStatus.COMPLETED
                # Calculate and store IRRs for COMPLETED status
                self._calculate_and_store_irrs_for_status(FundStatus.COMPLETED, session=session)
                session.commit()
                print(f"Fund '{self.name}' status updated: {old_status.value} → {self.status.value} (final tax statement received)")
            else:
                # Already COMPLETED, but tax statement may have changed - recalculate IRRs
                self._calculate_and_store_irrs_for_status(FundStatus.COMPLETED, session=session)
                session.commit()
                print(f"Fund '{self.name}' tax statement added, but already {self.status.value} - IRRs recalculated")
        else:
            if self.status == FundStatus.COMPLETED:
                # Transition from COMPLETED back to REALIZED (tax statement was deleted)
                old_status = self.status
                self.status = FundStatus.REALIZED
                # Calculate and store IRRs for REALIZED status
                self._calculate_and_store_irrs_for_status(FundStatus.REALIZED, session=session)
                session.commit()
                print(f"Fund '{self.name}' status updated: {old_status.value} → {self.status.value} (final tax statement removed)")
            else:
                # Already REALIZED, but tax statement may have changed - recalculate IRRs
                self._calculate_and_store_irrs_for_status(FundStatus.REALIZED, session=session)
                session.commit()
                print(f"Fund '{self.name}' tax statement added, but remains {self.status.value} - IRRs recalculated")

    @with_session
    def is_final_tax_statement_received(self, session=None):
        """Check if the fund has received its final tax statement.
        
        A fund is considered to have received its final tax statement when:
        1. Fund is REALIZED (equity balance = 0)
        2. We have a tax statement after the fund end_date
        
        Returns:
            bool: True if final tax statement criteria are met
        """
        from datetime import date
        
        # Only check if fund is not ACTIVE (i.e., REALIZED or COMPLETED)
        if self.status == FundStatus.ACTIVE:
            return False
        
        # Get fund end date (last event date)
        end_date = self.end_date
        if not end_date:
            return False
        
        # Get all tax statements for this fund
        from ..tax.models import TaxStatement
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).all()
        
        if not tax_statements:
            return False
        
        # Check if any tax statement has a tax_payment_date after the fund end_date
        # This indicates the final tax statement has been received
        for statement in tax_statements:
            tax_payment_date = statement.get_tax_payment_date()
            if tax_payment_date and tax_payment_date > end_date:
                return True
        
        return False



    @property
    def start_date(self):
        """Return the date of the first capital call event (cost-based) or unit purchase event (NAV-based), or None if not available.
        Used as the fund's effective start date for calculations.
        """
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return None
        
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, use the first unit purchase event
            first_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.UNIT_PURCHASE
            ).order_by(FundEvent.event_date).first()
        elif self.tracking_type == FundType.COST_BASED:
            # For cost-based funds, use the first capital call event
            first_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.CAPITAL_CALL
            ).order_by(FundEvent.event_date).first()
        
        if first_event and not isinstance(first_event.event_date, (Column, ColumnElement)):
            return first_event.event_date
        return None

    @property
    def total_capital_called(self):
        """Return the total amount of capital calls for cost-based funds."""
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return 0.0
        
        if self.tracking_type != FundType.COST_BASED:
            return 0.0
            
        call_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).all()
        
        return sum(event.amount for event in call_events if event.amount)

    @property
    def remaining_commitment(self):
        """Return the remaining commitment amount for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED or not self.commitment_amount:
            return 0.0
        
        return self.commitment_amount - self.total_capital_called

    def calculate_end_date(self, session=None):
        """Calculate and set the fund's end date based on current events.
        
        Sets self.end_date to the date of the final equity or distribution event.
        Only calculates when fund's equity balance is 0.
        """
        from sqlalchemy.orm import object_session
        
        # Check if fund has equity balance > 0
        has_equity = False
        if self.tracking_type == FundType.NAV_BASED:
            has_equity = self.current_units is not None and self.current_units > 0
        elif self.tracking_type == FundType.COST_BASED:
            has_equity = self.current_equity_balance is not None and self.current_equity_balance > 0
        
        # If fund still has equity balance > 0, no end date yet
        if has_equity:
            self.end_date = None
            return
        
        session = object_session(self) if session is None else session
        if session is None:
            self.end_date = None
            return
        
        # Get all equity and distribution events, ordered by date (newest first)
        relevant_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL,
                EventType.RETURN_OF_CAPITAL, 
                EventType.UNIT_PURCHASE,
                EventType.UNIT_SALE,
                EventType.DISTRIBUTION
            ])
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).all()
        
        if not relevant_events:
            self.end_date = None
            return
        
        # Set end_date to the date of the final equity or distribution event
        self.end_date = relevant_events[0].event_date

    @with_session
    def _calculate_irr_base(self, include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False, session=None, return_cashflows=False):
        """Base IRR calculation method for the fund.
        Delegates to orchestrate_irr_base in calculations.py.
        """
        from datetime import date
        # Only calculate IRR for completed funds (not active)
        if self.status == FundStatus.ACTIVE:
            if return_cashflows:
                return {'cash_flows': [], 'days_from_start': [], 'labels': [], 'irr': None}
            return None
        # Get start and end dates
        start_date = self.start_date
        end_date = self.end_date
        if not start_date or not end_date:
            if return_cashflows:
                return {'cash_flows': [], 'days_from_start': [], 'labels': [], 'irr': None}
            return None
        # Define event types to include (handled by orchestrate_irr_base)
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date).all()
        # Add final value as last cash flow (only for completed funds)
        # This logic is still handled here for now
        result = orchestrate_irr_base(
            cash_flow_events,
            start_date,
            include_tax_payments=include_tax_payments,
            include_risk_free_charges=include_risk_free_charges,
            include_eofy_debt_cost=include_eofy_debt_cost,
            return_cashflows=return_cashflows
        )
        return result

    def calculate_irr(self, session=None):
        """Calculate the pre-tax IRR for the fund using all relevant cash flows.
        Returns a float (IRR) or None if not computable.
        """
        return self._calculate_irr_base(include_tax_payments=False, include_risk_free_charges=False, include_eofy_debt_cost=False, session=session)

    def calculate_after_tax_irr(self, session=None):
        """Calculate the after-tax IRR for the fund, including tax payment events.
        Returns a float (IRR) or None if not computable.
        """
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=False, include_eofy_debt_cost=False, session=session)

    def calculate_real_irr(self, session=None, risk_free_rate_currency=None):
        """Calculate the real IRR for the fund, including debt cost and tax effects.
        Returns a float (IRR) or None if not computable.
        """
        self.create_daily_risk_free_interest_charges(session=session, risk_free_rate_currency=risk_free_rate_currency)
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_eofy_debt_cost=True, session=session)


    def calculate_average_equity_balance(self, session=None, events=None):
        """
        [NEW FLOW] Calculate average equity balance for the fund, regardless of FundType.
        Uses per-event current_equity_balance values and time-weighting.
        Accepts an in-memory events list for efficiency.
        """
        # Use provided events list if available, otherwise query
        if events is None:
            if self.tracking_type == FundType.NAV_BASED:
                event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
            elif self.tracking_type == FundType.COST_BASED:
                event_types = [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
            events = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type.in_(event_types)
            ).order_by(FundEvent.event_date, FundEvent.id).all()
        if not events:
            return 0.0
        elif len(events) == 1:
            return events[0].current_equity_balance
        # Time-weighted average: sum(balance * days) / total_days
        total_weighted_equity = 0.0
        total_days = 0
        for i in range(len(events) - 1):
            e = events[i]
            next_e = events[i + 1]
            days = (next_e.event_date - e.event_date).days
            equity = e.current_equity_balance if e.current_equity_balance is not None else 0.0
            total_weighted_equity += equity * days
            total_days += days
        # Determine the correct period end: use end_date if present, else today if active
        from datetime import date
        last_event = events[-1]
        period_end = None
        if self.end_date is not None:
            period_end = self.end_date
        elif self.status == FundStatus.ACTIVE:
            period_end = date.today()
        else:
            period_end = last_event.event_date
        # Include the last period if period_end is after or equal to the last event
        if period_end:
            days = (period_end - last_event.event_date).days
            if days >= 0:  # Include even if days = 0 (realized funds)
                equity = last_event.current_equity_balance if last_event.current_equity_balance is not None else 0.0
                total_weighted_equity += equity * days
                total_days += days
        return total_weighted_equity / total_days if total_days > 0 else 0.0

    @with_session
    def update_average_equity_balance(self, session=None):
        """Update the stored average equity balance with the calculated value for the fund type.
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        calculated_average = self.calculate_average_equity_balance(session=session)
        self.average_equity_balance = calculated_average
        # No session.commit() here

    def add_unit_purchase(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """
        Add a unit purchase event and update all relevant calculated fields using the unified capital recalculation flow.
        
        This method is part of the unified capital event handling system for NAV-based funds. It creates a unit purchase
        event and automatically recalculates all subsequent capital events to maintain data consistency.
        
        Args:
            units (float): Number of units to purchase (must be positive)
            price (float): Price per unit (must be positive)
            date (date): Date of the unit purchase
            brokerage_fee (float, optional): Brokerage fee for the transaction (default: 0.0)
            description (str, optional): Description of the purchase (auto-generated if not provided)
            reference_number (str, optional): External reference number for the transaction
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            FundEvent: The created unit purchase event
            
        Raises:
            ValueError: If fund is not NAV-based, or if units/price are invalid
            TypeError: If required parameters are missing or of wrong type
            
        Example:
            >>> fund = Fund.get_by_id(1, session=session)
            >>> event = fund.add_unit_purchase(
            ...     units=100.0,
            ...     price=10.50,
            ...     date=date(2024, 1, 15),
            ...     brokerage_fee=25.0,
            ...     description="Initial unit purchase",
            ...     session=session
            ... )
            >>> print(f"Created event: {event.id}, Amount: ${event.amount}")
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit purchases are only applicable for NAV-based funds")
        
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        amount = (units * price) + brokerage_fee
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date,
            units_purchased=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            description=description or f"Unit purchase: {units} units @ ${price:,.2f}",
            reference_number=reference_number
        )
        session.add(event)
        session.flush()
        self.recalculate_capital_chain_from(event, session=session)
        return event



    def add_unit_sale(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """
        Add a unit sale event and update all relevant calculated fields using the unified capital recalculation flow.
        
        This method is part of the unified capital event handling system for NAV-based funds. It creates a unit sale
        event and automatically recalculates all subsequent capital events to maintain data consistency.
        
        Args:
            units (float): Number of units to sell (must be positive)
            price (float): Price per unit (must be positive)
            date (date): Date of the unit sale
            brokerage_fee (float, optional): Brokerage fee for the transaction (default: 0.0)
            description (str, optional): Description of the sale (auto-generated if not provided)
            reference_number (str, optional): External reference number for the transaction
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            FundEvent: The created unit sale event
            
        Raises:
            ValueError: If fund is not NAV-based, or if units/price are invalid
            TypeError: If required parameters are missing or of wrong type
            
        Example:
            >>> fund = Fund.get_by_id(1, session=session)
            >>> event = fund.add_unit_sale(
            ...     units=50.0,
            ...     price=12.00,
            ...     date=date(2024, 6, 15),
            ...     brokerage_fee=15.0,
            ...     description="Partial unit sale",
            ...     session=session
            ... )
            >>> print(f"Created event: {event.id}, Amount: ${event.amount}")
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit sales are only applicable for NAV-based funds")
        
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        amount = (units * price) - brokerage_fee
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_SALE,
            event_date=date,
            units_sold=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            amount=amount,
            description=description or f"Unit sale: {units} units @ ${price:,.2f}",
            reference_number=reference_number
        )
        session.add(event)
        session.flush()
        self.recalculate_capital_chain_from(event, session=session)
        return event



    def add_capital_call(self, amount, date, description=None, reference_number=None, session=None):
        """
        Add a capital call event and update all relevant calculated fields using the unified capital recalculation flow.
        
        This method is part of the unified capital event handling system for cost-based funds. It creates a capital call
        event and automatically recalculates all subsequent capital events to maintain data consistency.
        
        **IDEMPOTENT BEHAVIOR**: If a capital call with the same date, amount, and reference_number already exists,
        the existing event is returned without creating duplicates.
        
        Args:
            amount (float): Capital call amount (must be positive)
            date (date): Date of the capital call
            description (str, optional): Description of the capital call (auto-generated if not provided)
            reference_number (str, optional): External reference number for the transaction
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            FundEvent: The created capital call event (or existing event if duplicate)
            
        Raises:
            ValueError: If fund is not cost-based, or if amount is invalid
            TypeError: If required parameters are missing or of wrong type
            
        Example:
            >>> fund = Fund.get_by_id(1, session=session)
            >>> event = fund.add_capital_call(
            ...     amount=100000.0,
            ...     date=date(2024, 1, 15),
            ...     description="Initial capital call for new investment",
            ...     session=session
            ... )
            >>> print(f"Created capital call: ${event.amount:,.2f}")
        """
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Capital calls are only applicable for cost-based funds")
        
        if not amount or amount <= 0:
            raise ValueError("Capital call amount must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Check for existing duplicate event (idempotent behavior)
        existing_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL,
            FundEvent.event_date == date,
            FundEvent.amount == amount,
            FundEvent.reference_number == reference_number
        ).first()
        
        if existing_event:
            # Return existing event without creating duplicate
            return existing_event
        
        # Create new event if no duplicate exists
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date,
            amount=amount,
            description=description or f"Capital call: ${amount:,.2f}",
            reference_number=reference_number
        )
        session.add(event)
        session.flush()
        self.recalculate_capital_chain_from(event, session=session)
        return event



    def add_return_of_capital(self, amount, date, description=None, reference_number=None, session=None):
        """
        [NEW FLOW] Add a return of capital event and update all relevant calculated fields using the unified capital recalculation flow.
        """
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Returns of capital are only applicable for cost-based funds")
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.RETURN_OF_CAPITAL,
            event_date=date,
            amount=amount,
            description=description or f"Return of capital: ${amount:,.2f}",
            reference_number=reference_number
        )
        session.add(event)
        session.flush()
        self.recalculate_capital_chain_from(event, session=session)
        return event



    def recalculate_capital_chain_from(self, event, session=None):
        """
        [NEW FLOW] Unified entry point: Recalculate all capital-related fields for this event and all subsequent capital events.
        Delegates to fund-type-specific logic as needed.
        """
        # Get all capital events for this fund, ordered by (event_date, id)
        CAPITAL_EVENT_TYPES = [
            EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL
        ]
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_(CAPITAL_EVENT_TYPES)
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        if not events:
            return
        # Find the index of the given event
        idx = None
        for i, e in enumerate(events):
            if e.id == event.id:
                idx = i
                break
        if idx is None:
            return
        # Recalculate all fields from this event forward
        self._recalculate_subsequent_capital_fund_events_after_capital_event(events, idx, session=session)
        # Update fund-level summary fields (includes end_date and average calculation)
        self.update_fund_summary_fields_after_capital_event(session=session)
        # Update fund status after equity event
        self.update_status_after_equity_event(session=session)
        # Commit session
        session.commit()

    def _recalculate_subsequent_capital_fund_events_after_capital_event(self, events, start_idx, session=None):
        """
        [NEW FLOW] Efficiently recalculate all relevant per-event fields for all subsequent events in a single pass.
        Delegates to fund-type-specific single-pass calculators.
        """
        if self.tracking_type == FundType.NAV_BASED:
            self._calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(events, start_idx, session)
        elif self.tracking_type == FundType.COST_BASED:
            self._calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(events, start_idx, session)

    def _calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(self, events, start_idx, session=None):
        """
        [NEW FLOW] Efficiently recalculate NAV-based fields (units_owned, current_equity_balance, amount, etc.) for all subsequent events in a single pass.
        Builds FIFO and units up to start_idx, then processes all subsequent events.
        """
        # Build FIFO and cumulative units up to (but not including) start_idx
        # Each FIFO entry: (units, unit_price, effective_price, event_date, brokerage_fee)
        fifo = []
        cumulative_units = 0.0
        for i in range(start_idx):
            e = events[i]
            if e.event_type == EventType.UNIT_PURCHASE:
                units = e.units_purchased or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                if units > 0:
                    effective_price = unit_price + (brokerage_fee / units)
                    fifo.append((units, unit_price, effective_price, e.event_date, brokerage_fee))
                cumulative_units += units
            elif e.event_type == EventType.UNIT_SALE:
                units = e.units_sold or 0
                remaining = units
                while remaining > 0 and fifo:
                    oldest_units, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage = fifo[0]
                    if oldest_units <= remaining:
                        fifo.pop(0)
                        remaining -= oldest_units
                    else:
                        fifo[0] = (oldest_units - remaining, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage)
                        remaining = 0
                cumulative_units -= units
        # Now process all subsequent events in a single pass
        for i in range(start_idx, len(events)):
            e = events[i]
            if e.event_type == EventType.UNIT_PURCHASE:
                # Update the FIFO and cumulative units
                units = e.units_purchased or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                e.amount = (units * unit_price) + brokerage_fee
                if units > 0:
                    effective_price = unit_price + (brokerage_fee / units)
                    fifo.append((units, unit_price, effective_price, e.event_date, brokerage_fee))
                cumulative_units += units
                e.units_owned = cumulative_units
                # For equity balance, exclude brokerage: only units * unit_price
                total_equity = sum(u * p for u, p, _, _, _ in fifo)
                e.current_equity_balance = total_equity
            elif e.event_type == EventType.UNIT_SALE:
                units = e.units_sold or 0
                unit_price = e.unit_price or 0
                brokerage_fee = e.brokerage_fee or 0
                e.amount = (units * unit_price) - brokerage_fee
                remaining = units
                while remaining > 0 and fifo:
                    oldest_units, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage = fifo[0]
                    if oldest_units <= remaining:
                        fifo.pop(0)
                        remaining -= oldest_units
                    else:
                        fifo[0] = (oldest_units - remaining, oldest_unit_price, oldest_effective_price, oldest_date, oldest_brokerage)
                        remaining = 0
                cumulative_units -= units
                e.units_owned = cumulative_units
                # For equity balance, exclude brokerage: only units * unit_price
                total_equity = sum(u * p for u, p, _, _, _ in fifo)
                e.current_equity_balance = total_equity
            else:
                # Not a capital event we care about for NAV-based
                e.units_owned = cumulative_units
                e.current_equity_balance = sum(u * p for u, p, _, _, _ in fifo)
        # End of single-pass NAV recalculation

    def _calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(self, events, start_idx, session=None):
        """
        [NEW FLOW] Efficiently recalculate cost-based fields (current_equity_balance, amount, etc.) for all subsequent events in a single pass.
        Builds running balance up to start_idx, then processes all subsequent events.
        """
        balance = 0.0
        for i in range(start_idx):
            e = events[i]
            if e.event_type == EventType.CAPITAL_CALL:
                balance += e.amount or 0.0
            elif e.event_type == EventType.RETURN_OF_CAPITAL:
                balance -= e.amount or 0.0
        for i in range(start_idx, len(events)):
            e = events[i]
            if e.event_type == EventType.CAPITAL_CALL:
                balance += e.amount or 0.0
                e.current_equity_balance = balance
            elif e.event_type == EventType.RETURN_OF_CAPITAL:
                balance -= e.amount or 0.0
                e.current_equity_balance = balance
            else:
                e.current_equity_balance = balance
        # End of single-pass cost-based recalculation

    def update_fund_summary_fields_after_capital_event(self, session=None):
        """
        [NEW FLOW] Update fund-level fields: current_equity_balance, current_units, average_equity_balance, total_cost_basis, etc.
        Delegates to fund-type-specific summary updaters.
        """
        if self.tracking_type == FundType.NAV_BASED:
            self._update_nav_fund_summary_after_capital_event(session)
        elif self.tracking_type == FundType.COST_BASED:
            self._update_cost_based_fund_summary_after_capital_event(session)

    def _update_nav_fund_summary_after_capital_event(self, session):
        """
        [NEW FLOW] Set current_units, current_equity_balance, average_equity_balance, current_unit_price, current_nav_total, etc. for NAV-based funds.
        Uses the latest event values.
        """
        # Get all unit purchase/sale events ordered by date
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        if events:
            latest_unit_event = events[-1]
            self.current_units = latest_unit_event.units_owned if latest_unit_event.units_owned is not None else 0.0
            self.current_equity_balance = latest_unit_event.current_equity_balance if latest_unit_event.current_equity_balance is not None else 0.0
        else:
            self.current_units = 0.0
            self.current_equity_balance = 0.0
        # Find the most recent NAV_UPDATE or UNIT_PURCHASE/UNIT_SALE event
        # We want to use the most recent NAV_UPDATE or UNIT_PURCHASE/UNIT_SALE event to set current_unit_price
        latest_nav_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date.desc(), FundEvent.id.desc()).first()
        latest_unit_event = events[-1] if events else None
        # Compare recency
        nav_date = latest_nav_event.event_date if latest_nav_event else None
        nav_id = latest_nav_event.id if latest_nav_event else None
        unit_date = latest_unit_event.event_date if latest_unit_event else None
        unit_id = latest_unit_event.id if latest_unit_event else None
        use_nav = False
        if latest_nav_event and (not latest_unit_event or (nav_date, nav_id) >= (unit_date, unit_id)):
            use_nav = True
        if use_nav:
            self.current_unit_price = latest_nav_event.nav_per_share if latest_nav_event and latest_nav_event.nav_per_share is not None else 0.0
        elif latest_unit_event:
            self.current_unit_price = latest_unit_event.unit_price if latest_unit_event.unit_price is not None else 0.0
        else:
            self.current_unit_price = 0.0
        # Set current_nav_total
        self.current_nav_total = (self.current_units or 0.0) * (self.current_unit_price or 0.0)
        
        # Calculate end_date before average equity balance calculation
        self.calculate_end_date(session=session)
        
        # Average equity balance (unified method)
        self.average_equity_balance = self.calculate_average_equity_balance(session=session)

    def _update_cost_based_fund_summary_after_capital_event(self, session):
        """
        [NEW FLOW] Set current_equity_balance, total_cost_basis, average_equity_balance, etc. for cost-based funds.
        Uses the latest event values.
        """
        # Get all capital call/return events ordered by date
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL])
        ).order_by(FundEvent.event_date, FundEvent.id).all()
        
        if events:
            latest_event = events[-1]
            self.current_equity_balance = latest_event.current_equity_balance if latest_event.current_equity_balance is not None else 0.0
        else:
            self.current_equity_balance = 0.0
        
        # Total cost basis = sum of capital calls - sum of returns
        total_calls = sum(e.amount or 0.0 for e in events if e.event_type == EventType.CAPITAL_CALL)
        total_returns = sum(e.amount or 0.0 for e in events if e.event_type == EventType.RETURN_OF_CAPITAL)
        self.total_cost_basis = total_calls - total_returns
        
        # Calculate end_date before average equity balance calculation
        self.calculate_end_date(session=session)
        
        # Average equity balance (unified method)
        calculated_avg = self.calculate_average_equity_balance(session=session)
        old_avg = self.average_equity_balance
        self.average_equity_balance = calculated_avg
        


    @with_session
    def create_tax_payment_events(self, session=None):
        """Create tax payment events for this fund based on tax statements using the new event management framework.
        Commits new events to the database. Returns a list of created events.
        """
        from src.tax.models import TaxStatement
        from src.tax.events import TaxEventManager
        # Get all tax statements for this fund
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).all()
        created_events = []
        for tax_statement in tax_statements:
            events = TaxEventManager.create_or_update_tax_events(tax_statement, session=session)
            created_events.extend(events)
        return created_events





    @with_session
    def get_current_nav_fund_value(self, session=None):
        """
        Get the current NAV fund value (same as current_nav_total).
        For NAV-based funds, this is units * unit price.
        For cost-based funds, this is the current equity balance.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Current NAV fund value
        """
        if self.tracking_type == FundType.NAV_BASED:
            return float(self.current_nav_total) if self.current_nav_total else 0.0
        else:
            # For cost-based funds, use current equity balance
            return float(self.current_equity_balance) if self.current_equity_balance else 0.0

    @with_session
    def get_total_tax_payments(self, session=None):
        """
        Get the total amount of tax payments for this fund.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Total tax payments amount
        """
        tax_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).all()
        
        return sum(event.amount for event in tax_events if event.amount)

    @with_session
    def get_total_daily_interest_charges(self, session=None):
        """
        Get the total amount of daily interest charges for this fund.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Total daily interest charges amount
        """
        interest_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).all()
        
        return sum(event.amount for event in interest_events if event.amount)

    @with_session
    def get_total_unit_purchases(self, session=None):
        """
        Get the total amount of unit purchases for NAV-based funds.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Total unit purchases amount
        """
        if self.tracking_type != FundType.NAV_BASED:
            return 0.0
            
        purchase_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.UNIT_PURCHASE
        ).all()
        
        return sum(event.amount for event in purchase_events if event.amount)

    @with_session
    def get_total_unit_sales(self, session=None):
        """
        Get total units sold across all unit sale events.
        
        Returns:
            float: Total units sold
        """
        unit_sale_events = [event for event in self.fund_events if event.event_type == EventType.UNIT_SALE]
        return sum(event.units_sold or 0 for event in unit_sale_events)
    
    @with_session
    def get_enhanced_fund_metrics(self, session=None):
        """
        Get enhanced fund metrics for Companies UI as specified in the API contract.
        
        This method provides the performance metrics needed for fund comparison:
        - unrealized_gains_losses
        - realized_gains_losses  
        - total_profit_loss
        
        Returns:
            dict: Enhanced fund metrics matching the API contract structure
        """
        # Calculate unrealized gains/losses
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds: current NAV value - total cost basis
            total_cost_basis = self.get_total_unit_purchases(session=session)
            current_nav_value = self.get_current_nav_fund_value(session=session)
            unrealized_gains_losses = (current_nav_value or 0) - (total_cost_basis or 0)
        else:
            # For cost-based funds: current equity balance - total capital called
            total_capital_called = self.get_total_capital_calls(session=session)
            current_equity = self.current_equity_balance or 0
            unrealized_gains_losses = current_equity - (total_capital_called or 0)
        
        # Calculate realized gains/losses from distributions
        total_distributions = self.get_total_distributions(session=session) or 0
        
        # Calculate total profit/loss
        total_profit_loss = unrealized_gains_losses + total_distributions
        
        return {
            "unrealized_gains_losses": unrealized_gains_losses,
            "realized_gains_losses": total_distributions,
            "total_profit_loss": total_profit_loss
        }
    
    @with_session
    def get_distribution_summary(self, session=None):
        """
        Get distribution summary for Companies UI as specified in the API contract.
        
        Returns:
            dict: Distribution summary data
        """
        # Get all distribution events
        distribution_events = [event for event in self.fund_events if event.event_type == EventType.DISTRIBUTION]
        
        if not distribution_events:
            return {
                "distribution_count": 0,
                "total_distribution_amount": 0,
                "last_distribution_date": None,
                "distribution_frequency_months": None
            }
        
        # Calculate distribution metrics
        distribution_count = len(distribution_events)
        total_distribution_amount = sum(event.amount or 0 for event in distribution_events)
        
        # Find last distribution date
        last_distribution_date = max(event.event_date for event in distribution_events)
        
        # Calculate distribution frequency (months between first and last distribution)
        if distribution_count > 1:
            first_distribution_date = min(event.event_date for event in distribution_events)
            from dateutil.relativedelta import relativedelta
            delta = relativedelta(last_distribution_date, first_distribution_date)
            distribution_frequency_months = delta.months + (delta.years * 12)
        else:
            distribution_frequency_months = None
        
        return {
            "distribution_count": distribution_count,
            "total_distribution_amount": total_distribution_amount,
            "last_distribution_date": last_distribution_date.isoformat() if last_distribution_date else None,
            "distribution_frequency_months": distribution_frequency_months
        }

    @with_session
    def get_total_capital_calls(self, session=None):
        """
        Get the total amount of capital calls for cost-based funds.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Total capital calls amount
        """
        if self.tracking_type != FundType.COST_BASED:
            return 0.0
            
        call_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).all()
        
        return sum(event.amount for event in call_events if event.amount)

    @with_session
    def get_total_capital_returns(self, session=None):
        """
        Get the total amount of capital returns for cost-based funds.
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Total capital returns amount
        """
        if self.tracking_type != FundType.COST_BASED:
            return 0.0
            
        return_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        ).all()
        
        return sum(event.amount for event in return_events if event.amount)

    @with_session
    def calculate_actual_duration_months(self, session=None):
        """
        Calculate the actual duration of the fund in months.
        
        Args:
            session (Session): Database session
        
        Returns:
            int: Duration in months, or None if not calculable
        """
        start_date = self.start_date
        end_date = self.end_date
        
        if not start_date:
            return None
            
        # If fund is still active, use current date
        if not end_date:
            from datetime import date
            end_date = date.today()
        
        # Calculate months difference
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        # Adjust for day of month
        if end_date.day < start_date.day:
            months -= 1
            
        return max(0, months)

    @with_session
    def calculate_completed_irr(self, session=None):
        """
        Calculate IRR for completed funds (status = COMPLETED).
        
        Args:
            session (Session): Database session
        
        Returns:
            float: IRR percentage, or None if not calculable
        """
        if self.status == FundStatus.ACTIVE:
            return None
            
        return self.calculate_irr(session=session)

    @with_session
    def calculate_completed_after_tax_irr(self, session=None):
        """
        Calculate after-tax IRR for completed funds (status = COMPLETED).
        
        Args:
            session (Session): Database session
        
        Returns:
            float: After-tax IRR percentage, or None if not calculable
        """
        if self.status == FundStatus.ACTIVE:
            return None
            
        return self.calculate_after_tax_irr(session=session)

    @with_session
    def calculate_completed_real_irr(self, session=None):
        """
        Calculate real IRR for completed funds (status = COMPLETED).
        
        Args:
            session (Session): Database session
        
        Returns:
            float: Real IRR percentage, or None if not calculable
        """
        if self.status == FundStatus.ACTIVE:
            return None
            
        return self.calculate_real_irr(session=session)


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
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (MANUAL) foreign key to fund
    event_type = Column(Enum(EventType), nullable=False, index=True)  # (MANUAL) type of event (CAPITAL_CALL, DISTRIBUTION, etc.)
    event_date = Column(Date, nullable=False, index=True)  # (MANUAL) date of the event
    amount = Column(Float)  # (HYBRID) cash flow amount, can be manual or calculated based on event type
    nav_per_share = Column(Float)  # (MANUAL) NAV per share for NAV_UPDATE events
    previous_nav_per_share = Column(Float)  # (CALCULATED) previous NAV per share for NAV_UPDATE events
    nav_change_absolute = Column(Float)  # (CALCULATED) absolute change in NAV for NAV_UPDATE events
    nav_change_percentage = Column(Float)  # (CALCULATED) percentage change in NAV for NAV_UPDATE events
    units_owned = Column(Float)  # (CALCULATED) cumulative units owned after this event
    distribution_type = Column(Enum(DistributionType))  # (MANUAL) type of distribution (DIVIDEND, INTEREST, etc.)
    tax_payment_type = Column(Enum(TaxPaymentType))  # (MANUAL) type of tax payment (INTEREST, CAPITAL_GAINS, etc.)
    tax_statement_id = Column(Integer, ForeignKey('tax_statements.id'), nullable=True, index=True)  # (MANUAL) foreign key to tax statement for TAX_PAYMENT events
    units_purchased = Column(Float)  # (MANUAL) units purchased in this event
    units_sold = Column(Float)  # (MANUAL) units sold in this event
    unit_price = Column(Float)  # (MANUAL) unit price for this transaction
    brokerage_fee = Column(Float, default=0.0)  # (MANUAL) brokerage fee for unit transactions
    description = Column(Text)  # (MANUAL) event description
    reference_number = Column(String(100))  # (MANUAL) external reference number
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    current_equity_balance = Column(Float, nullable=True)  # (CALCULATED) For NAV-based funds: FIFO cost base after this event (set only on capital events). For cost-based funds: net capital after this event (set only on capital events).
    has_withholding_tax = Column(Boolean, default=False)  # (MANUAL) flag for distributions with associated withholding tax
    is_cash_flow_complete = Column(Boolean, default=False)  # (SYSTEM) auto-managed flag set by reconciliation logic
    
    # Relationships
    fund = relationship("Fund", back_populates="fund_events", lazy='selectin')  # Eager load for fund event lists
    tax_statement = relationship("TaxStatement", lazy='selectin')  # Eager load for tax statement data
    cash_flows = relationship("FundEventCashFlow", back_populates="fund_event", cascade="all, delete-orphan", lazy='selectin')
    
    def __repr__(self):
        """Return a string representation of the FundEvent instance for debugging/logging."""
        return f"<FundEvent(id={self.id}, fund_id={self.fund_id}, type={self.event_type.value}, date={self.event_date}, amount={self.amount})>"
    
    def infer_distribution_type(self):
        """Infer the distribution type based on the event description or other fields.
        Returns a DistributionType enum value.
        
        Australian tax considerations:
        - Looks for 'franked' or 'unfranked' in description for dividend classification
        - Falls back to generic dividend if no franking information is available
        """
        if not self.description:
            return None
        
        desc_lower = self.description.lower()
        
        # Check for dividend types first (most specific)
        if 'dividend' in desc_lower:
            if 'franked' in desc_lower or 'fully franked' in desc_lower:
                return DistributionType.DIVIDEND_FRANKED
            elif 'unfranked' in desc_lower:
                return DistributionType.DIVIDEND_UNFRANKED
            else:
                return None
        
        # Check for other distribution types
        if 'interest' in desc_lower:
            return DistributionType.INTEREST
        elif 'rent' in desc_lower:
            return DistributionType.RENT
        elif 'capital gain' in desc_lower or 'capital_gain' in desc_lower:
            return DistributionType.CAPITAL_GAIN
        elif 'income' in desc_lower:
            return DistributionType.INCOME
        else:
            return None
    
    def set_event_type_and_infer_distribution(self, event_type):
        """Set the event type and infer the distribution type if applicable."""
        self.event_type = event_type
        
        # Infer distribution type for distribution events
        if event_type == EventType.DISTRIBUTION:
            self.distribution_type = self.infer_distribution_type()
    
    # ------- Cash Flow domain helpers (Phase 2) -------
    @with_session
    def add_cash_flow(
        self,
        *,
        bank_account_id: int,
        transfer_date: date,
        currency: str,
        amount: float,
        reference: str | None = None,
        notes: str | None = None,
        session=None,
    ) -> "FundEventCashFlow":
        """Add a cash flow to this event with validation per spec.

        Direction is derived automatically from the event type and persisted.
        """
        # Validate required args
        if not bank_account_id:
            raise ValueError("bank_account_id is required")
        if not transfer_date:
            raise ValueError("transfer_date is required")
        if not currency or len(currency) != 3:
            raise ValueError("currency must be ISO-4217 3-letter code")
        if amount is None:
            raise ValueError("amount is required")

        # Enforce bank account currency match
        if not FundEventCashFlow._is_same_currency(session, bank_account_id, currency):
            raise ValueError("Cash flow currency must equal BankAccount.currency")

        # Ensure this event has an id (in case caller adds flows immediately after creation)
        if not self.id:
            session.flush()

        # Infer direction from event type
        outflow_types = {EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE}
        inflow_types = {EventType.RETURN_OF_CAPITAL, EventType.DISTRIBUTION, EventType.UNIT_SALE}
        if self.event_type in outflow_types:
            direction_value = CashFlowDirection.OUTFLOW
        elif self.event_type in inflow_types:
            direction_value = CashFlowDirection.INFLOW
        else:
            raise ValueError("Cash flows are not applicable for this event type")

        cf = FundEventCashFlow(
            fund_event_id=self.id,
            bank_account_id=bank_account_id,
            direction=direction_value,
            transfer_date=transfer_date,
            currency=currency.upper(),
            amount=float(amount),
            reference=reference,
            notes=notes,
        )
        session.add(cf)
        session.flush()

        # Auto-manage completion flag
        self._recompute_cash_flow_completion(session=session)
        session.flush()
        return cf

    @with_session
    def remove_cash_flow(self, cash_flow_id: int, session=None) -> None:
        cf = next((c for c in self.cash_flows if c.id == cash_flow_id), None)
        if not cf:
            # Attempt fetch in case relationship not loaded
            cf = session.query(FundEventCashFlow).filter(
                FundEventCashFlow.id == cash_flow_id,
                FundEventCashFlow.fund_event_id == self.id,
            ).first()
        if not cf:
            raise ValueError("Cash flow not found for this event")
        session.delete(cf)
        session.flush()
        self._recompute_cash_flow_completion(session=session)

    def _recompute_cash_flow_completion(self, session=None) -> None:
        """Recompute is_cash_flow_complete according to same-currency reconciliation rules.

        - If any cash flow currency differs from fund currency: mark False
        - If no cash flows: mark False
        - If same currency for all: require sum to match target within 0.01
        """
        flows = list(self.cash_flows)
        if not flows:
            self.is_cash_flow_complete = False
            return

        # Determine fund currency from the Fund
        fund_currency = (self.fund.currency or "").upper() if self.fund and self.fund.currency else ""
        if not fund_currency:
            # If fund has no currency set, cannot reconcile
            self.is_cash_flow_complete = False
            return

        # Cross-currency rule: any flow not in fund currency => False
        for cf in flows:
            if (cf.currency or "").upper() != fund_currency:
                self.is_cash_flow_complete = False
                return

        # All same currency as fund; compute target
        target = float(self.amount or 0.0)

        # Interest distribution withholding adjustment
        if self.event_type == EventType.DISTRIBUTION and self.distribution_type == DistributionType.INTEREST:
            # Same-date NON_RESIDENT_INTEREST_WITHHOLDING payments for same fund
            withholding_sum = 0.0
            same_day_tax = session.query(FundEvent).filter(
                FundEvent.fund_id == self.fund_id,
                FundEvent.event_date == self.event_date,
                FundEvent.event_type == EventType.TAX_PAYMENT,
                FundEvent.tax_payment_type == TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
            ).all()
            for t in same_day_tax:
                withholding_sum += float(t.amount or 0.0)
            target = target - withholding_sum

        total = sum(float(cf.amount or 0.0) for cf in flows)
        self.is_cash_flow_complete = abs(total - target) <= 0.01
    


