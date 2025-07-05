from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import enum
from sqlalchemy import func
import numpy as np
import numpy_financial as npf
from sqlalchemy import event
from src.utils import with_session
from src.calculations import (
    calculate_irr,
    calculate_average_equity_balance_nav,
    calculate_average_equity_balance_cost,
    calculate_debt_cost,
    get_equity_change_for_event,
    calculate_nav_based_capital_gains,
    calculate_cost_based_capital_gains,
    orchestrate_nav_based_average_equity,
    orchestrate_cost_based_average_equity,
    orchestrate_irr_base,
    net_income,
    tax_payable,
    interest_tax_benefit,
    get_risk_free_rate_for_date,
    get_reconciliation_explanation,
    get_financial_years_for_fund_period
)
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.elements import ColumnElement

Base = declarative_base()


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


class InvestmentCompany(Base):
    """Model representing an investment company/firm."""
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    website = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="investment_company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InvestmentCompany(id={self.id}, name='{self.name}')>"


class Entity(Base):
    """Model representing an investing entity (person or company)."""
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    tax_jurisdiction = Column(String(10), default="AU")  # Tax jurisdiction (e.g., 'AU' for Australia, 'US' for United States)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="entity", cascade="all, delete-orphan")
    tax_statements = relationship("TaxStatement", back_populates="entity", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Entity(id={self.id}, name='{self.name}', jurisdiction='{self.tax_jurisdiction}')>"
    
    def get_financial_year(self, date):
        """Get the financial year for a given date based on the entity's tax jurisdiction."""
        if self.tax_jurisdiction == "AU":
            # Australian financial year: July 1 to June 30
            if date.month >= 7:
                # July to December: current year to next year
                return f"{date.year}-{str(date.year + 1)[-2:]}"
            else:
                # January to June: previous year to current year
                return f"{date.year - 1}-{str(date.year)[-2:]}"
        else:
            # Default to calendar year for other jurisdictions
            return str(date.year)


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
    
    @property
    def should_be_active(self):
        """Return True if the fund should be considered active.
        For cost-based funds: checks if current equity balance > 0
        For NAV-based funds: checks if current units > 0
        """
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, check if there are remaining units
            return not isinstance(self._current_units, (Column, ColumnElement)) and self._current_units is not None and self._current_units > 0
        else:
            # For cost-based funds, check if there's remaining equity
            return not isinstance(self.current_equity_balance, (Column, ColumnElement)) and self.current_equity_balance is not None and self.current_equity_balance > 0
    
    @property
    def should_have_final_tax_statement(self):
        """Return True if the fund should have received its final tax statement.
        This checks if the fund is no longer active and if a tax statement exists for the final financial year.
        """
        from sqlalchemy.orm import object_session
        from datetime import date
        
        # If fund is still active, we don't have final tax statement yet
        if not isinstance(self.should_be_active, (Column, ColumnElement)) and self.should_be_active is not None and self.should_be_active:
            return False
        
        session = object_session(self)
        if session is None:
            return False
        
        # Get the fund's end date
        end_date = self.end_date
        if isinstance(end_date, (Column, ColumnElement)) or end_date is None:
            return False
        
        # Get the financial year of the fund's end date
        entity = self.entity
        if isinstance(entity, (Column, ColumnElement)) or entity is None:
            return False
        
        end_financial_year = entity.get_financial_year(end_date)
        
        # Check if we have a tax statement for the final financial year
        final_tax_statement = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id,
            TaxStatement.financial_year == end_financial_year
        ).first()
        
        return final_tax_statement is not None
    
    @with_session
    def update_final_tax_statement_status(self, session=None):
        """Update the final_tax_statement_received flag based on whether the final tax statement is present.
        Commits the change to the database if the status changes.
        """
        new_status = self.should_have_final_tax_statement
        if not isinstance(self.final_tax_statement_received, (Column, ColumnElement)) and self.final_tax_statement_received is not None and self.final_tax_statement_received != new_status:
            self.final_tax_statement_received = new_status
            session.commit()
            print(f"Fund '{self.name}' final tax statement status updated: {'Complete' if new_status else 'Pending'}")
    
    @with_session
    def update_active_status(self, session=None):
        """Update the is_active flag based on the current equity balance.
        Commits the change to the database if the status changes.
        """
        new_active_status = self.should_be_active
        if not isinstance(self.is_active, (Column, ColumnElement)) and self.is_active is not None and self.is_active != new_active_status:
            self.is_active = new_active_status
            session.commit()
            print(f"Fund '{self.name}' status updated: {'Active' if new_active_status else 'Exited'}")
    
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
        else:
            # For cost-based funds, use the first capital call event
            first_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.CAPITAL_CALL
            ).order_by(FundEvent.event_date).first()
        
        if first_event and not isinstance(first_event.event_date, (Column, ColumnElement)):
            return first_event.event_date
        return None
    
    @property
    def end_date(self):
        """Return the date of the last event if the fund is exited (equity balance is zero), else None.
        Used as the fund's effective end date for calculations.
        """
        from sqlalchemy.orm import object_session
        # If fund still has equity balance > 0, no end date yet
        if not isinstance(self.current_equity_balance, (Column, ColumnElement)) and self.current_equity_balance is not None and self.current_equity_balance > 0:
            return None
        session = object_session(self)
        if session is None:
            return None
        last_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date.desc()).first()
        if last_event and not isinstance(last_event.event_date, (Column, ColumnElement)):
            return last_event.event_date
        return None
    
    @property
    def total_investment_duration_months(self):
        """Return the total investment duration in months, from start_date to end_date (or today if still active).
        Returns 0 if dates are not available.
        """
        from dateutil.relativedelta import relativedelta
        start = self.start_date
        if not start or isinstance(start, (Column, ColumnElement)):
            return 0
        if not isinstance(self.current_equity_balance, (Column, ColumnElement)) and self.current_equity_balance is not None and self.current_equity_balance > 0:
            end = datetime.now().date()
        else:
            end = self.end_date
            if not end or isinstance(end, (Column, ColumnElement)):
                return 0
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months
    
    @property
    def current_value(self):
        """Return the current value of the fund.
        - For NAV-based funds: units * unit price (if available), else current equity balance.
        - For cost-based funds: total cost basis (if available), else current equity balance.
        """
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, calculate from units and unit price
            if not isinstance(self._current_units, (Column, ColumnElement)) and not isinstance(self._current_unit_price, (Column, ColumnElement)) and self._current_units is not None and self._current_unit_price is not None and self._current_units != 0 and self._current_unit_price != 0:
                return self._current_units * self._current_unit_price
            return self.current_equity_balance
        else:
            # For cost-based funds, use the cost basis
            return self._total_cost_basis or self.current_equity_balance
    
    @property
    def calculated_average_equity_balance(self):
        """Return the calculated average equity balance for the fund, using the appropriate method for the fund type."""
        return self.calculate_average_equity_balance()
    
    @with_session
    def update_current_equity_balance(self, session=None):
        """Update the current equity balance.
        - For cost-based funds: from capital movements (calls - returns).
        - For NAV-based funds: from cost_of_units of the latest unit event (FIFO cost basis of remaining units).
        Also updates the fund's active status.
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, use cost_of_units from the latest unit event (FIFO cost basis)
            latest_unit_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
            ).order_by(FundEvent.event_date.desc()).first()
            if latest_unit_event and latest_unit_event.cost_of_units is not None:
                self.current_equity_balance = latest_unit_event.cost_of_units
            else:
                self.current_equity_balance = 0.0
        else:
            # For cost-based funds, use capital calls - returns
            capital_movements = self.get_capital_movements(session=session)
            net_capital_invested = capital_movements['calls'] - capital_movements['returns']
            self.current_equity_balance = net_capital_invested
        # Update active status based on new equity balance
        self.update_active_status(session=session)
        # No session.commit() here
    
    @with_session
    def update_average_equity_balance(self, session=None):
        """Update the stored average equity balance with the calculated value for the fund type.
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        calculated_average = self.calculate_average_equity_balance(session=session)
        self.average_equity_balance = calculated_average
        # No session.commit() here
    
    @with_session
    def update_current_units_and_price(self, session=None):
        """Update current units and unit price for NAV-based funds.
        Uses the most recent unit purchase/sale event for current units, and the most recent NAV update for unit price.
        Also calculates amounts for unit purchases/sales and updates units_owned and cost_of_units.
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        if self.tracking_type != FundType.NAV_BASED:
            return
        # First, calculate amounts for unit purchases/sales and update units_owned and cost_of_units
        self._calculate_nav_event_amounts(session=session)
        # Get the most recent unit purchase/sale event for current units
        latest_unit_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date.desc()).first()
        if latest_unit_event:
            self._current_units = latest_unit_event.units_owned
        else:
            self._current_units = 0.0
        # Get the most recent NAV update event for current unit price
        latest_nav_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date.desc()).first()
        if latest_nav_event:
            self._current_unit_price = latest_nav_event.nav_per_share
        else:
            # If no NAV updates, use the latest unit price from purchase/sale events
            if latest_unit_event and latest_unit_event.unit_price:
                self._current_unit_price = latest_unit_event.unit_price
            else:
                self._current_unit_price = 0.0
        # No session.commit() here
    
    @with_session
    def _calculate_nav_event_amounts(self, session=None):
        """Calculate amounts for unit purchases/sales and update units_owned and cost_of_units for NAV updates.
        This method ensures that:
        - Unit purchase/sale amounts = units * unit_price + brokerage_fee
        - units_owned is updated for purchase/sale events
        - cost_of_units is calculated using FIFO for remaining units
        """
        from src.calculations import calculate_nav_event_amounts
        from src.models import FundEvent, EventType
        
        # Get all unit events for this fund
        event_types = [EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.NAV_UPDATE]
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_(event_types)
        ).order_by(FundEvent.event_date).all()
        
        # Calculate amounts using pure function
        calculate_nav_event_amounts(unit_events)
    
    @with_session
    def update_current_units_after_event(self, event, session=None):
        """Update current_units after a unit purchase/sale event.
        This should be called after each UNIT_PURCHASE or UNIT_SALE event is created.
        Similar to how cost-based funds update equity balance after capital events.
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        if self.tracking_type != FundType.NAV_BASED:
            return
        if event.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            # Recalculate all units_owned and cost_of_units for this fund
            self._calculate_nav_event_amounts(session=session)
            # Update current_units to the latest units_owned value
            latest_unit_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
            ).order_by(FundEvent.event_date.desc()).first()
            if latest_unit_event:
                self._current_units = latest_unit_event.units_owned
            else:
                self._current_units = 0.0
            # No session.commit() here
    
    @with_session
    def update_total_cost_basis(self, session=None):
        """Update the total cost basis for cost-based funds (calls - returns).
        Note: This method does NOT commit the session. The caller is responsible for committing.
        """
        if self.tracking_type != FundType.COST_BASED:
            return
        # Calculate from capital calls minus capital returns
        capital_movements = self.get_capital_movements(session=session)
        self._total_cost_basis = capital_movements['calls'] - capital_movements['returns']
        # No session.commit() here
    
    @with_session
    def get_nav_based_cost_basis(self, as_of_date=None, session=None):
        """Get the cost basis for NAV-based funds up to a given date.
        This is used for IRR calculations where we need to know the total amount invested.
        
        Args:
            as_of_date (date, optional): Calculate as of this date. If None, calculates to the end.
            session: Database session
            
        Returns:
            float: Total cost basis (sum of all unit purchases minus unit sales)
        """
        if self.tracking_type != FundType.NAV_BASED:
            return 0.0
            
        from src.calculations import calculate_nav_based_cost_basis_for_irr
        from src.models import FundEvent, EventType
        
        # Get all unit events for this fund
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        
        # Calculate cost basis using pure function
        return calculate_nav_based_cost_basis_for_irr(unit_events, as_of_date)
    
    @with_session
    def update_all_calculated_fields(self, session=None):
        """Update all calculated fields for the fund, including equity balances, units/price or cost basis, and final tax statement status.
        Commits all changes to the database.
        """
        # Update equity balances
        self.update_current_equity_balance(session=session)
        self.update_average_equity_balance(session=session)
        
        # Update fund-type specific fields
        if self.tracking_type == FundType.NAV_BASED:
            self.update_current_units_and_price(session=session)
        else:
            self.update_total_cost_basis(session=session)
        
        # Update final tax statement status
        self.update_final_tax_statement_status(session=session)
        
        session.commit()
    
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
            dist_type = event.distribution_type or DistributionType.OTHER
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
    
    def get_capital_gains(self, session=None):
        """Return the total capital gains for the fund, using the appropriate method for the fund type.
        NAV-based funds use FIFO on unit sales; cost-based funds use explicit events.
        """
        if self.tracking_type == FundType.NAV_BASED:
            return self._calculate_nav_based_capital_gains(session=session)
        else:
            return self._get_cost_based_capital_gains(session=session)
    
    @with_session
    def _calculate_nav_based_capital_gains(self, session=None):
        """Calculate capital gains for NAV-based funds using FIFO on unit sales.
        Delegates to calculate_nav_based_capital_gains in calculations.py.
        """
        from src.calculations import calculate_nav_based_capital_gains
        # Get all unit purchase and sale events in chronological order
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        return calculate_nav_based_capital_gains(events)
    
    @with_session
    def _get_cost_based_capital_gains(self, session=None):
        """Get capital gains for cost-based funds from explicit capital gain events.
        Delegates to calculate_cost_based_capital_gains in calculations.py.
        """
        from src.calculations import calculate_cost_based_capital_gains
        # Get all relevant events (could be filtered further if needed)
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).all()
        return calculate_cost_based_capital_gains(events)
    
    @with_session
    def get_capital_movements(self, session=None):
        """Return a dictionary with total capital calls and returns for the fund.
        Used for calculating net capital invested and cost basis.
        Keys: 'calls', 'returns'.
        """
        # Calculate total capital calls (handles both fund types)
        total_calls = self.get_capital_calls(session=session)
        
        # Calculate total capital returns
        total_returns = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        ).scalar() or 0
        
        return {"calls": total_calls, "returns": total_returns}
    
    @with_session
    def get_capital_calls(self, session=None):
        """Return the total capital calls for the fund, depending on fund type.
        - NAV-based: sum of UNIT_PURCHASE events.
        - Cost-based: sum of CAPITAL_CALL events.
        Returns 0 if no events exist.
        """
        from sqlalchemy import func

        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, sum all unit purchases
            total = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.UNIT_PURCHASE
            ).scalar() or 0
        else:
            # For cost-based funds, sum all capital calls
            total = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.CAPITAL_CALL
            ).scalar() or 0
        
        return total
    
    def calculate_average_equity_balance(self, session=None):
        """Calculate and return the average equity balance for the fund.
        Uses NAV or cost-based method depending on fund type.
        """
        if self.tracking_type == FundType.NAV_BASED:
            return self._calculate_nav_based_average_equity(session=session)
        else:
            return self._calculate_cost_based_average_equity(session=session)
    
    @with_session
    def _calculate_nav_based_average_equity(self, session=None):
        """Calculate average equity balance for NAV-based funds using unit events.
        Delegates to orchestrate_nav_based_average_equity in calculations.py.
        """
        from src.calculations import orchestrate_nav_based_average_equity
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        if not unit_events:
            return 0
        # If fund is still active, use today's date as end_date (handled by caller if needed)
        return orchestrate_nav_based_average_equity(unit_events)
    
    @with_session
    def _calculate_cost_based_average_equity(self, session=None):
        """Calculate average equity balance for cost-based funds using capital events.
        Delegates to orchestrate_cost_based_average_equity in calculations.py.
        """
        from src.calculations import orchestrate_cost_based_average_equity
        capital_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([
                EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE
            ])
        ).order_by(FundEvent.event_date).all()
        if not capital_events:
            return 0
        return orchestrate_cost_based_average_equity(capital_events)
    
    @with_session
    def _calculate_irr_base(self, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=None, return_cashflows=False):
        """Base IRR calculation method for the fund.
        Delegates to orchestrate_irr_base in calculations.py.
        """
        from src.calculations import orchestrate_irr_base
        from datetime import date
        # Only calculate IRR for completed funds
        if self.should_be_active:
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
            include_fy_debt_cost=include_fy_debt_cost,
            return_cashflows=return_cashflows
        )
        return result
    
    def calculate_irr(self, session=None):
        """Calculate the pre-tax IRR for the fund using all relevant cash flows.
        Returns a float (IRR) or None if not computable.
        """
        return self._calculate_irr_base(include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=session)
    
    def calculate_after_tax_irr(self, session=None):
        """Calculate the after-tax IRR for the fund, including tax payment events.
        Returns a float (IRR) or None if not computable.
        """
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=False, include_fy_debt_cost=False, session=session)
    
    def calculate_real_irr(self, session=None, risk_free_rate_currency=None):
        """Calculate the real IRR for the fund, including debt cost and tax effects.
        Returns a float (IRR) or None if not computable.
        """
        self.create_daily_risk_free_interest_charges(session=session, risk_free_rate_currency=risk_free_rate_currency)
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_fy_debt_cost=True, session=session)
    

    
    def get_irr_percentage(self, session=None):
        """Return the IRR as a formatted percentage string, or 'N/A' if not computable."""
        irr = self.calculate_irr(session)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    @with_session
    def get_tax_statements_by_financial_year(self, session=None):
        """Return all tax statements for this fund, grouped by financial year.
        Returns a dict: {financial_year: [TaxStatement, ...]}
        """        
        statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).order_by(TaxStatement.financial_year).all()
        
        # Group by financial year
        grouped = {}
        for statement in statements:
            if statement.financial_year not in grouped:
                grouped[statement.financial_year] = []
            grouped[statement.financial_year].append(statement)
        
        return grouped
    
    @with_session
    def get_tax_statement_for_entity_financial_year(self, entity_id, financial_year, session=None):
        """Return the tax statement for a specific entity and financial year, or None if not found."""
        return session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id,
            TaxStatement.entity_id == entity_id,
            TaxStatement.financial_year == financial_year
        ).first()
    
    def _create_or_update_tax_statement_object(self, entity_id, financial_year, **kwargs):
        """Create or update a tax statement object.
        Returns the TaxStatement object. No database operations.
        """
        # Try to find existing statement
        statement = self.get_tax_statement_for_entity_financial_year(entity_id, financial_year)
        
        if statement is None:
            # Create new statement
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
        
        # Calculate interest income fields (including total_interest_income)
        statement.calculate_interest_income_fields()
        
        # Calculate total income
        statement.calculate_total_income()
        
        return statement

    @with_session
    def create_or_update_tax_statement(self, entity_id, financial_year, session=None, **kwargs):
        """Create or update a tax statement for a specific entity and financial year.
        If a statement exists, updates its fields; otherwise, creates a new one.
        Commits the change to the database.
        Returns the TaxStatement instance.
        """
        # Create or update statement object using business logic method
        statement = self._create_or_update_tax_statement_object(entity_id, financial_year, **kwargs)
        
        # Add to session if it's a new statement
        if statement.id is None:
            session.add(statement)
        
        session.commit()
        return statement
    
    def __repr__(self):
        """Return a string representation of the Fund instance for debugging/logging."""
        return f"<Fund(id={self.id}, name='{self.name}', company='{self.investment_company.name if self.investment_company else 'Unknown'}')>"
    
    def get_after_tax_irr_percentage(self, session=None):
        """Return the after-tax IRR as a formatted percentage string, or 'N/A' if not computable."""
        irr = self.calculate_after_tax_irr(session)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    def get_real_irr_percentage(self, session=None, risk_free_rate_currency=None):
        """Return the real IRR (including debt cost) as a formatted percentage string, or 'N/A' if not computable."""
        irr = self.calculate_real_irr(session, risk_free_rate_currency)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    def _create_tax_payment_event_object(self, tax_statement):
        """Create a tax payment event object for a tax statement.
        Returns the event object or None if not applicable. No database operations.
        """
        # Calculate tax payable if not already calculated
        tax_statement.calculate_tax_payable()
        
        # Only create tax payment event if there's additional tax payable
        if tax_statement.tax_payable > 0.01:  # Allow for small rounding differences
            # Create tax payment event
            tax_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.TAX_PAYMENT,
                event_date=tax_statement.get_tax_payment_date(),
                amount=tax_statement.tax_payable,
                description=f"Tax payment for FY {tax_statement.financial_year}",
                reference_number=f"TAX-{tax_statement.financial_year}",
                tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
            )
            return tax_event
        
        return None
    
    @with_session
    def create_tax_payment_events(self, session=None):
        """Create tax payment events for this fund based on tax statements.
        Used for after-tax IRR calculations. Commits new events to the database.
        Returns a list of created events.
        """
        # Get all tax statements for this fund
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).all()
        
        created_events = []
        
        for tax_statement in tax_statements:
            # Check if tax payment event already exists
            existing_event = session.query(FundEvent).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.TAX_PAYMENT,
                FundEvent.event_date == tax_statement.get_tax_payment_date(),
                FundEvent.amount == tax_statement.tax_payable,
                FundEvent.tax_payment_type == TaxPaymentType.EOFY_INTEREST_TAX
            ).first()
            
            if not existing_event:
                # Create tax payment event using business logic method
                tax_event = self._create_tax_payment_event_object(tax_statement)
                if tax_event:
                    session.add(tax_event)
                    created_events.append(tax_event)
        
        if created_events:
            session.commit()
        
        return created_events
    


    @with_session
    def add_distribution_with_tax(self, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution event with an associated tax payment event.
        Uses a static helper to create both events and updates the fund's equity balance.
        Returns a tuple: (distribution_event, tax_event).
        """
        # Use the static method to create both events
        distribution_event, tax_event = FundEvent.create_distribution_with_tax_static(
            fund_id=self.id,
            event_date=event_date,
            gross_amount=gross_amount,
            tax_withheld=tax_withheld,
            tax_rate=tax_rate,
            distribution_type=distribution_type,
            description=description,
            reference_number=reference_number,
            session=session
        )
        
        # Update fund's current equity balance
        if distribution_event:
            self.update_current_equity_balance(session=session)
        
        return distribution_event, tax_event
    
    def add_distribution_with_tax_rate(self, event_date, gross_amount, tax_rate, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution event with tax withheld calculated from a given rate.
        Returns a tuple: (distribution_event, tax_event).
        """
        tax_withheld = (gross_amount * tax_rate) / 100
        return self.add_distribution_with_tax(
            event_date=event_date,
            gross_amount=gross_amount,
            tax_withheld=tax_withheld,
            tax_rate=tax_rate,
            distribution_type=distribution_type,
            description=description,
            reference_number=reference_number,
            session=session
        )

    def _calculate_daily_interest_charge_objects(self, start_date, end_date, risk_free_rates, existing_dates, cash_flow_events):
        """Calculate daily interest charge events for the fund period.
        Returns a list of FundEvent objects. No database operations.
        """
        from datetime import timedelta
        
        created_events = []
        current_equity = 0
        current_date = start_date
        
        # Process each event and calculate daily interest charges
        for event in cash_flow_events:
            # Add interest charges for each day from current_date to event_date
            while current_date < event.event_date:
                if current_date not in existing_dates:
                    # Find risk-free rate for this date
                    rate = get_risk_free_rate_for_date(current_date, risk_free_rates)
                    if rate is not None and current_equity > 0:
                        # Calculate daily interest charge
                        daily_interest = current_equity * (rate / 100) / 365.25
                        
                        # Create interest charge event object
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
            
            # Update equity balance for the actual event
            current_equity += get_equity_change_for_event(event, self.tracking_type)
            current_date = event.event_date
        
        # Add interest charges for remaining days until end_date
        while current_date <= end_date:
            if current_date not in existing_dates:
                rate = get_risk_free_rate_for_date(current_date, risk_free_rates)
                if rate is not None and current_equity > 0:
                    daily_interest = current_equity * (rate / 100) / 365.25
                    
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
    def calculate_financial_year_interest_expense(self, financial_year, session=None):
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
        interest_expense = self.calculate_financial_year_interest_expense(fy, session=session)
        tax_statement.total_interest_expense = interest_expense
        
        # Calculate tax benefit and create event
        tax_benefit = tax_statement.calculate_interest_tax_benefit()
        if tax_benefit > 0:
            event = tax_statement.create_fy_debt_cost_event(session=session)
            if event:
                created_events.append(event)
        
        return created_events

    @with_session
    def create_fy_debt_cost_events(self, session=None):
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
            created_events.extend(events)
        
        if created_events:
            session.commit()
            print(f"Created {len(created_events)} FY debt cost events for {self.name}")
        
        return created_events

    def _delete_debt_cost_events(self, session=None):
        """Delete all daily risk-free interest charges and FY debt cost events for this fund.
        Returns a tuple of (deleted_daily_count, deleted_fy_count).
        No database operations.
        """
        # Delete all DAILY_RISK_FREE_INTEREST_CHARGE and FY_DEBT_COST events for this fund
        deleted_daily = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).delete()
        deleted_fy = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.FY_DEBT_COST
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
        self.create_fy_debt_cost_events(session)
        session.commit()
        print(f"Recalculated debt costs for fund '{self.name}': deleted {deleted_daily} daily interest charges, {deleted_fy} FY debt cost events, and recreated them.")

    # Direct model methods for common operations
    @with_session
    def add_unit_purchase(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """Add a unit purchase event and update calculated fields.
        
        Args:
            units (float): Number of units purchased
            price (float): Price per unit
            date (date): Purchase date
            brokerage_fee (float): Transaction fee (default 0.0)
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created unit purchase event
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit purchases are only applicable for NAV-based funds")
        
        # Calculate amount
        amount = (units * price) + brokerage_fee
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date,
            units_purchased=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            amount=amount,
            description=description or f"Unit purchase: {units} units at ${price:.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self.update_current_units_and_price(session=session)
        self.update_current_equity_balance(session=session)
        
        return event
    
    @with_session
    def add_unit_sale(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """Add a unit sale event and update calculated fields.
        
        Args:
            units (float): Number of units sold
            price (float): Price per unit
            date (date): Sale date
            brokerage_fee (float): Transaction fee (default 0.0)
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created unit sale event
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit sales are only applicable for NAV-based funds")
        
        # Calculate amount
        amount = (units * price) - brokerage_fee
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_SALE,
            event_date=date,
            units_sold=units,
            unit_price=price,
            brokerage_fee=brokerage_fee,
            amount=amount,
            description=description or f"Unit sale: {units} units at ${price:.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self.update_current_units_and_price(session=session)
        self.update_current_equity_balance(session=session)
        
        return event
    
    @with_session
    def add_nav_update(self, nav_per_share, date, description=None, reference_number=None, session=None):
        """Add a NAV update event and update calculated fields.
        
        Args:
            nav_per_share (float): NAV per share/unit
            date (date): NAV date
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created NAV update event
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("NAV updates are only applicable for NAV-based funds")
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.NAV_UPDATE,
            event_date=date,
            nav_per_share=nav_per_share,
            description=description or f"NAV update: ${nav_per_share:.4f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self.update_current_units_and_price(session=session)
        
        return event
    
    @with_session
    def add_capital_call(self, amount, date, description=None, reference_number=None, session=None):
        """Add a capital call event and update calculated fields.
        
        Args:
            amount (float): Capital call amount
            date (date): Call date
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created capital call event
        """
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Capital calls are only applicable for cost-based funds")
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date,
            amount=amount,
            description=description or f"Capital call: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self.update_current_equity_balance(session=session)
        self.update_total_cost_basis(session=session)
        
        return event
    
    @with_session
    def add_return_of_capital(self, amount, date, description=None, reference_number=None, session=None):
        """Add a return of capital event and update calculated fields.
        
        Args:
            amount (float): Return amount
            date (date): Return date
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created return of capital event
        """
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Returns of capital are only applicable for cost-based funds")
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.RETURN_OF_CAPITAL,
            event_date=date,
            amount=amount,
            description=description or f"Return of capital: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self.update_current_equity_balance(session=session)
        self.update_total_cost_basis(session=session)
        
        return event
    
    @with_session
    def add_distribution(self, amount, date, distribution_type=DistributionType.INTEREST, description=None, reference_number=None, session=None):
        """Add a distribution event.
        
        Args:
            amount (float): Distribution amount
            date (date): Distribution date
            distribution_type (DistributionType): Type of distribution
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created distribution event
        """
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date,
            amount=amount,
            distribution_type=distribution_type,
            description=description or f"Distribution: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        return event
    
    def _create_distribution_with_tax_objects(self, gross_amount, date, tax_withheld=0.0, distribution_type=DistributionType.INTEREST, description=None, reference_number=None):
        """Create distribution and tax payment event objects.
        Returns a tuple of (distribution_event, tax_event) objects. No database operations.
        """
        # Create distribution event object
        distribution_event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date,
            amount=gross_amount,
            distribution_type=distribution_type,
            description=description or f"Distribution: ${gross_amount:,.2f}",
            reference_number=reference_number
        )
        
        # Create tax payment event object if there's tax withheld
        tax_event = None
        if tax_withheld > 0:
            tax_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.TAX_PAYMENT,
                event_date=date,
                amount=tax_withheld,
                description=f"Tax withheld on distribution: ${tax_withheld:,.2f}",
                reference_number=f"{reference_number}_TAX" if reference_number else None,
                tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
            )
        
        return distribution_event, tax_event

    @with_session
    def add_distribution_with_tax_direct(self, gross_amount, date, tax_withheld=0.0, distribution_type=DistributionType.INTEREST, description=None, reference_number=None, session=None):
        """Add a distribution event with associated tax payment using direct model methods.
        
        Args:
            gross_amount (float): Gross distribution amount
            date (date): Distribution date
            tax_withheld (float): Tax withheld from distribution
            distribution_type (DistributionType): Type of distribution
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            tuple: (distribution_event, tax_event)
        """
        # Create event objects using business logic method
        distribution_event, tax_event = self._create_distribution_with_tax_objects(
            gross_amount, date, tax_withheld, distribution_type, description, reference_number
        )
        
        # Add events to session
        session.add(distribution_event)
        if tax_event:
            session.add(tax_event)
        
        return distribution_event, tax_event

    @property
    def current_units(self):
        """Return the current number of units owned (NAV-based funds only).
        For cost-based funds, this should be None.
        For NAV-based funds, returns 0.0 if no units are owned.
        """
        if self.tracking_type == FundType.COST_BASED:
            return None
        return self._current_units if self._current_units is not None else 0.0
    @current_units.setter
    def current_units(self, value):
        """Restrict direct assignment of current_units.
        For cost-based funds, raises ValueError if set.
        For NAV-based funds, raises ValueError if set directly (should be updated via update_current_units_and_price).
        """
        if self.tracking_type == FundType.COST_BASED and value is not None:
            raise ValueError("Cannot set current_units on a cost-based fund.")
        if value is not None:
            raise ValueError("current_units is calculated automatically from NAV events. Use update_current_units_and_price() instead.")
        self._current_units = value

    @property
    def current_unit_price(self):
        """Return the current unit price (NAV-based funds only).
        For cost-based funds, this should be None.
        """
        return self._current_unit_price
    @current_unit_price.setter
    def current_unit_price(self, value):
        """Restrict direct assignment of current_unit_price.
        For cost-based funds, raises ValueError if set.
        For NAV-based funds, raises ValueError if set directly (should be updated via update_current_units_and_price).
        """
        if self.tracking_type == FundType.COST_BASED and value is not None:
            raise ValueError("Cannot set current_unit_price on a cost-based fund.")
        if value is not None:
            raise ValueError("current_unit_price is calculated automatically from NAV events. Use update_current_units_and_price() instead.")
        self._current_unit_price = value

    @property
    def total_cost_basis(self):
        """Return the total cost basis (cost-based funds only).
        For NAV-based funds, this should be None.
        """
        return self._total_cost_basis
    @total_cost_basis.setter
    def total_cost_basis(self, value):
        """Restrict direct assignment of total_cost_basis.
        For NAV-based funds, raises ValueError if set.
        For cost-based funds, raises ValueError if set directly (should be updated via update_total_cost_basis).
        """
        if self.tracking_type == FundType.NAV_BASED and value is not None:
            raise ValueError("Cannot set total_cost_basis on a NAV-based fund.")
        if value is not None:
            raise ValueError("total_cost_basis is calculated automatically from capital movements. Use update_total_cost_basis() instead.")
        self._total_cost_basis = value



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
    
    def _get_recalculation_methods_for_event_type(self, event_type):
        """Get the list of recalculation methods needed for a given event type.
        Returns a list of method names to call.
        """
        if event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            return ['update_current_units_and_price', 'update_current_equity_balance']
        elif event_type == EventType.NAV_UPDATE:
            return ['update_current_units_and_price']
        elif event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]:
            return ['update_current_equity_balance', 'update_total_cost_basis']
        else:
            return []

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
        
        # Delete the event
        session.delete(event)
        
        # Recalculate affected fields based on event type
        recalculation_methods = self._get_recalculation_methods_for_event_type(event_type)
        for method_name in recalculation_methods:
            method = getattr(self, method_name)
            method(session=session)
        
        return True
    
    @with_session
    def recalculate_all_fields(self, session=None):
        """Recalculate all calculated fields for this fund.
        
        Args:
            session: Database session
        """
        if self.tracking_type == FundType.NAV_BASED:
            self.update_current_units_and_price(session=session)
            self.update_current_equity_balance(session=session)
        else:  # COST_BASED
            self.update_current_equity_balance(session=session)
            self.update_total_cost_basis(session=session)
        
        # Recalculate average equity balance
        self.update_average_equity_balance(session=session)
        
        print(f"Recalculated all fields for fund '{self.name}'")
    
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


class TaxPaymentType(enum.Enum):
    NON_RESIDENT_INTEREST_WITHHOLDING = "non_resident_interest_withholding"
    NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE = "non_resident_interest_withholding_difference"
    CAPITAL_GAINS_TAX = "capital_gains_tax"
    EOFY_INTEREST_TAX = "eofy_interest_tax"
    OTHER = "other"


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
        return f"<FundEvent(id={self.id}, fund_id={self.fund_id}, type={self.event_type}, date={self.event_date}, amount={self.amount})>"
    
    def infer_distribution_type(self):
        """Infer the distribution type for this event based on its fields and description.
        Returns a DistributionType enum or None if not inferrable.
        """
        # For the consolidated DISTRIBUTION event type, we need to specify the distribution type
        # This method is now mainly for backward compatibility
        # The distribution_type should be set explicitly when creating DISTRIBUTION events
        return self.distribution_type
    
    def set_event_type_and_infer_distribution(self, event_type):
        """Set the event type and attempt to infer the distribution type if applicable.
        Used when creating or updating events programmatically.
        """
        self.event_type = event_type
        if event_type == EventType.DISTRIBUTION and not self.distribution_type:
            # Default to INTEREST for distributions if not specified
            self.distribution_type = DistributionType.INTEREST
    
    @staticmethod
    def create_distribution_with_tax_static(fund_id, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Create a distribution event and an associated tax payment event for a fund.
        Used by Fund methods to ensure both events are created together.
        Returns a tuple: (distribution_event, tax_event).
        Commits both events to the database.
        """
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(fund_id) if hasattr(fund_id, 'id') else None
        
        # Create the distribution event
        distribution_event = FundEvent(
            fund_id=fund_id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=gross_amount,
            distribution_type=distribution_type or DistributionType.INTEREST,
            description=description or "Distribution",
            reference_number=reference_number
        )
        session.add(distribution_event)
        
        # Create the tax payment event if there's tax withheld
        tax_event = None
        if tax_withheld > 0:
            tax_event = FundEvent(
                fund_id=fund_id,
                event_type=EventType.TAX_PAYMENT,
                event_date=event_date,
                amount=tax_withheld,
                description=f"Tax withheld on distribution (rate: {tax_rate}%)" if tax_rate else "Tax withheld on distribution",
                reference_number=f"{reference_number}_TAX" if reference_number else None,
                tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
            )
            session.add(tax_event)
        
        session.commit()
        return distribution_event, tax_event


class RiskFreeRate(Base):
    """Model representing risk-free rates for different currencies over time.
    
    Field usage:
    - currency: The currency code (e.g., 'AUD', 'USD').
    - rate_date: The date the rate applies to.
    - rate: The risk-free rate as a percentage.
    - rate_type: The type of rate (e.g., government bond, LIBOR).
    - source: The data source for the rate.
    
    Business rules:
    - Each (currency, rate_date) pair should be unique.
    - Used for opportunity cost and real IRR calculations in funds.
    """
    __tablename__ = 'risk_free_rates'
    
    id = Column(Integer, primary_key=True)
    currency = Column(String(10), nullable=False)  # Currency code (e.g., 'AUD', 'USD', 'EUR')
    rate_date = Column(Date, nullable=False)  # Date of the rate
    rate = Column(Float, nullable=False)  # Risk-free rate as percentage (e.g., 4.5 for 4.5%)
    rate_type = Column(String(50), default='government_bond')  # Type of rate (e.g., 'government_bond', 'libor', 'sofr')
    source = Column(String(100))  # Source of the rate data
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('currency', 'rate_date', 'rate_type', name='uq_risk_free_rate'),
    )
    
    def __repr__(self):
        """Return a string representation of the RiskFreeRate instance for debugging/logging."""
        return f"<RiskFreeRate(id={self.id}, currency='{self.currency}', date={self.rate_date}, rate={self.rate}%)>"


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
    
    @property
    def net_interest_income(self):
        """Net interest income is always calculated as total_interest_income - non_resident_withholding_tax_from_statement."""
        from src.calculations import net_income
        return net_income(self.total_interest_income, self.non_resident_withholding_tax_from_statement)

    def get_net_income(self):
        """Calculate net income after non-resident withholding tax from statement.
        Returns the net income as a float.
        """
        from src.calculations import net_income
        return net_income(self.total_income, self.non_resident_withholding_tax_from_statement)

    def calculate_tax_payable(self):
        """Calculate tax payable as (total_interest_income * interest_taxable_rate / 100) - non_resident_withholding_tax_from_statement.
        Updates the tax_payable and tax_already_paid fields.
        Returns the tax payable as a float.
        """
        from src.calculations import tax_payable
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
        from src.calculations import interest_tax_benefit
        self.interest_tax_benefit = interest_tax_benefit(self.total_interest_expense, self.interest_deduction_rate)
        return self.interest_tax_benefit

    def get_financial_year_dates(self):
        """Get the start and end dates for this financial year based on entity jurisdiction.
        Returns a tuple: (start_date, end_date).
        """
        from src.calculations import get_financial_year_dates
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return None, None
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return None, None
        return get_financial_year_dates(self.financial_year, entity.tax_jurisdiction)
    
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
    
    @with_session
    def reconcile_with_actual_distributions(self, session=None):
        """Compare the tax statement to actual distributions received for this fund/entity/financial year.
        Returns a dict with statement values, actuals, and differences, including an explanation.
        """
        # Get financial year dates
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_start or not fy_end:
            return None
        
        # Query actual distributions for this fund/entity/financial year
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end
        ).all()
        
        # Query actual tax payments for this fund/entity/financial year
        tax_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end
        ).all()
        
        # Calculate actual totals
        actual_gross = sum(e.amount for e in distribution_events)
        actual_tax = sum(e.amount for e in tax_events)
        actual_net = actual_gross - actual_tax
        
        # Calculate differences
        gross_diff = (self.total_interest_income or 0.0) - actual_gross
        tax_diff = (self.non_resident_withholding_tax_from_statement or 0.0) - actual_tax
        net_diff = self.net_interest_income - actual_net
        
        return {
            'financial_year': self.financial_year,
            'period': {
                'start': fy_start,
                'end': fy_end
            },
            'statement': {
                'total_interest_income': self.total_interest_income,
                'non_resident_withholding_tax_from_statement': self.non_resident_withholding_tax_from_statement,
                'net_interest_income': self.net_interest_income,
            },
            'actual': {
                'gross_distributed': actual_gross,
                'tax_withheld': actual_tax,
                'net_received': actual_net,
                'distribution_count': len(distribution_events)
            },
            'difference': {
                'gross': gross_diff,
                'tax_withheld': tax_diff,
                'net': net_diff
            },
            'explanation': get_reconciliation_explanation(gross_diff, tax_diff, net_diff)
        }
    

    
    def _create_fy_debt_cost_event_object(self):
        """Create a FY debt cost event object for real IRR calculations if a tax benefit exists.
        Returns the event object or None if not applicable. No database operations.
        """
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
    
    @with_session
    def create_fy_debt_cost_event(self, session=None):
        """Create a FY debt cost event for real IRR calculations if a tax benefit exists.
        Commits the event to the database and returns it, or returns None if not applicable.
        """
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
    def non_resident_withholding_tax_difference(self):
        """Difference between already withheld and statement withholding."""
        return (self.non_resident_withholding_tax_already_withheld or 0.0) - (self.non_resident_withholding_tax_from_statement or 0.0)

    def calculate_interest_income_fields(self, session=None):
        """Calculate and update interest income fields."""
        self.total_interest_income = (
            (self.interest_received_in_cash or 0.0)
            + (self.distribution_receivable_this_fy or 0.0)
            - (self.distribution_received_prev_fy or 0.0)
        )
        # Only calculate tax payments if we have a session
        if session is not None:
            self.non_resident_withholding_tax_already_withheld = self.sum_tax_payments_for_fy(session=session)
        else:
            # Set to 0 if no session available
            self.non_resident_withholding_tax_already_withheld = 0.0

    @with_session
    def sum_tax_payments_for_fy(self, session=None):
        """Sum all TaxPayment events for this fund/entity/financial year with type NON_RESIDENT_INTEREST_WITHHOLDING."""
        from sqlalchemy import func
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_start or not fy_end:
            return 0.0
        from .models import FundEvent, EventType, TaxPaymentType
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.TAX_PAYMENT,
            FundEvent.tax_payment_type == TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end,
        ).scalar() or 0.0
        return total


# Event listeners have been removed in favor of direct model methods.
# All database operations now go through Fund model methods which handle
# validation, event creation, and field updates automatically.