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

Base = declarative_base()


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
                return f"{date.year}-{date.year + 1}"
            else:
                # January to June: previous year to current year
                return f"{date.year - 1}-{date.year}"
        else:
            # Default to calendar year for other jurisdictions
            return str(date.year)


class Fund(Base):
    """Model representing an investment fund."""
    __tablename__ = 'funds'
    
    id = Column(Integer, primary_key=True)
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    name = Column(String(255), nullable=False)
    fund_type = Column(String(100))  # e.g., 'Private Equity', 'Venture Capital', 'Real Estate', etc.
    vintage_year = Column(Integer)  # Year the fund was established
    
    # Fund tracking type
    tracking_type = Column(Enum(FundType), nullable=False, default=FundType.NAV_BASED)
    
    # Investment tracking fields
    commitment_amount = Column(Float, nullable=False)  # Total amount committed to the fund
    current_equity_balance = Column(Float, default=0.0)  # Current equity balance
    average_equity_balance = Column(Float, default=0.0)  # Average equity balance over time
    expected_irr = Column(Float)  # Expected Internal Rate of Return (as percentage)
    expected_duration_months = Column(Integer)  # Expected fund duration in months
    
    # NAV-based fund specific fields
    current_units = Column(Float)  # Current number of units owned
    current_unit_price = Column(Float)  # Current unit price
    
    # Cost-based fund specific fields
    total_cost_basis = Column(Float)  # Total cost basis for cost-based funds
    
    # Status and metadata
    is_active = Column(Boolean, default=True)  # Whether the fund is still active
    description = Column(Text)
    currency = Column(String(10), default="AUD")  # Currency code for the fund
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="funds")
    entity = relationship("Entity", back_populates="funds")
    fund_events = relationship("FundEvent", back_populates="fund", cascade="all, delete-orphan")
    tax_statements = relationship("TaxStatement", back_populates="fund", cascade="all, delete-orphan")
    
    @property
    def should_be_active(self):
        """Determine if fund should be considered active based on equity balance."""
        return self.current_equity_balance > 0
    
    def update_active_status(self, session=None):
        """Update the is_active flag based on current equity balance."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return
        
        new_active_status = self.should_be_active
        if self.is_active != new_active_status:
            self.is_active = new_active_status
            session.commit()
            print(f"Fund '{self.name}' status updated: {'Active' if new_active_status else 'Exited'}")
    
    @property
    def start_date(self):
        """Calculate start date from the first capital call event."""
        from sqlalchemy.orm import object_session
        
        session = object_session(self)
        if session is None:
            return None
            
        first_capital_call = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).order_by(FundEvent.event_date).first()
        
        return first_capital_call.event_date if first_capital_call else None
    
    @property
    def end_date(self):
        """Calculate end date when current_equity_balance goes to 0 (fund exit)."""
        from sqlalchemy.orm import object_session
        
        # If fund still has equity balance > 0, no end date yet
        if self.current_equity_balance > 0:
            return None
            
        session = object_session(self)
        if session is None:
            return None
            
        # Find the last event where equity balance went to 0
        # This would typically be a capital return or distribution that zeroes out the balance
        last_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date.desc()).first()
        
        # Use the last event date as end date when fund has zero equity balance
        return last_event.event_date if last_event else None
    
    @property
    def total_investment_duration_months(self):
        """Calculate total investment duration in months."""
        from dateutil.relativedelta import relativedelta
        
        start = self.start_date
        if not start:
            return 0
            
        if self.current_equity_balance > 0:
            # Fund still has equity balance, calculate current duration
            end = datetime.now().date()
        else:
            # Fund has zero equity balance (exited), use end date
            end = self.end_date
            if not end:
                return 0
        
        # Calculate months between start and end
        delta = relativedelta(end, start)
        return delta.years * 12 + delta.months
    
    @property
    def current_value(self):
        """Calculate current value based on fund type."""
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, calculate from units and unit price
            if self.current_units and self.current_unit_price:
                return self.current_units * self.current_unit_price
            return self.current_equity_balance
        else:
            # For cost-based funds, use the cost basis
            return self.total_cost_basis or self.current_equity_balance
    
    @property
    def calculated_average_equity_balance(self):
        """Calculate and return the average equity balance."""
        return self.calculate_average_equity_balance()
    
    def update_current_equity_balance(self, session=None):
        """Update current equity balance from capital movements and update active status."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return
        
        # Calculate current equity balance from capital movements
        capital_movements = self.get_capital_movements(session)
        net_capital_invested = capital_movements['calls'] - capital_movements['returns']
        
        # Update the equity balance
        self.current_equity_balance = net_capital_invested
        
        # Update active status based on new equity balance
        self.update_active_status(session)
        
        session.commit()
    
    def update_average_equity_balance(self, session=None):
        """Update the stored average equity balance with the calculated value."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return
        
        calculated_average = self.calculate_average_equity_balance(session)
        self.average_equity_balance = calculated_average
        session.commit()
    
    def calculate_debt_cost(self, session=None, risk_free_rate_currency=None):
        """Calculate debt cost (opportunity cost) using daily/period-by-period accuracy."""
        from sqlalchemy.orm import object_session
        from datetime import date, timedelta
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None
        
        # Use fund currency if not specified
        if risk_free_rate_currency is None:
            risk_free_rate_currency = self.currency
        
        # Get fund start and end dates
        start_date = self.start_date
        end_date = self.end_date
        if not start_date or not end_date:
            return None
        
        # Get all equity change events, sorted by date
        events = [e for e in self.fund_events if e.event_date >= start_date and e.event_date <= end_date]
        events.sort(key=lambda e: e.event_date)
        
        # Get all risk-free rates for the period, sorted by date
        risk_free_rates = session.query(RiskFreeRate).filter(
            RiskFreeRate.currency == risk_free_rate_currency,
            RiskFreeRate.rate_date <= end_date
        ).order_by(RiskFreeRate.rate_date).all()
        if not risk_free_rates:
            return None
        
        # Build a list of (date, equity_balance) tuples for each period
        equity_periods = []
        current_equity = 0
        last_date = start_date
        for event in events:
            if event.event_date > last_date:
                equity_periods.append((last_date, event.event_date, current_equity))
            # Update equity for this event if it affects equity balance
            equity_change = self._get_equity_change_for_event(event)
            current_equity += equity_change
            last_date = event.event_date
        
        # Add final period if needed
        if last_date < end_date:
            equity_periods.append((last_date, end_date, current_equity))
        
        # Build a list of (date, rate) tuples for each risk-free rate period
        rate_periods = []
        for i, rate in enumerate(risk_free_rates):
            rate_start = rate.rate_date
            if i + 1 < len(risk_free_rates):
                rate_end = risk_free_rates[i + 1].rate_date
            else:
                rate_end = end_date + timedelta(days=1)
            rate_periods.append((rate_start, rate_end, rate.rate))
        
        # For each equity period, break into sub-periods where the risk-free rate is constant
        total_debt_cost = 0
        total_days = 0
        weighted_rfr_sum = 0
        weighted_equity_days = 0  # Track equity-weighted days for rate calculation
        for eq_start, eq_end, equity in equity_periods:
            period_start = eq_start
            while period_start < eq_end:
                # Find the risk-free rate for this day
                rate = None
                for r_start, r_end, r_value in rate_periods:
                    if r_start <= period_start < r_end:
                        rate = r_value
                        sub_period_end = min(eq_end, r_end)
                        break
                if rate is None:
                    # Use the most recent available rate
                    rate = rate_periods[-1][2]
                    sub_period_end = eq_end
                days = (sub_period_end - period_start).days
                if days > 0 and equity != 0:
                    cost = equity * (rate / 100) * (days / 365.25)
                    total_debt_cost += cost
                    weighted_rfr_sum += rate * days * equity  # Equity-weighted rate calculation
                    weighted_equity_days += days * equity  # Equity-weighted days
                    total_days += days
                period_start = sub_period_end
        
        avg_risk_free_rate = weighted_rfr_sum / weighted_equity_days if weighted_equity_days > 0 else 0
        avg_equity = sum((eq[2] * (eq[1] - eq[0]).days for eq in equity_periods)) / total_days if total_days > 0 else 0
        investment_duration_years = total_days / 365.25
        debt_cost_percentage = (total_debt_cost / avg_equity) * 100 if avg_equity else 0
        fund_irr = self.calculate_irr(session)
        if fund_irr is not None:
            fund_return = avg_equity * (fund_irr / 100) * investment_duration_years
            excess_return = fund_return - total_debt_cost
        else:
            excess_return = None
        return {
            'total_debt_cost': total_debt_cost,
            'average_risk_free_rate': avg_risk_free_rate,
            'debt_cost_percentage': debt_cost_percentage,
            'excess_return': excess_return,
            'investment_duration_years': investment_duration_years,
            'average_equity': avg_equity,
            'total_days': total_days
        }
    
    def _get_equity_change_for_event(self, event):
        """Determine the equity change for a given event, regardless of fund type."""
        # Events that increase equity (money going into the fund)
        equity_increase_events = [
            EventType.CAPITAL_CALL,      # Cost-based: capital calls
            EventType.UNIT_PURCHASE,     # NAV-based: unit purchases
            'contribution',              # Generic contributions
        ]
        
        # Events that decrease equity (money coming out of the fund)
        equity_decrease_events = [
            EventType.RETURN_OF_CAPITAL, # Cost-based: returns of capital
            EventType.UNIT_SALE,         # NAV-based: unit sales
            'withdrawal',                # Generic withdrawals
        ]
        
        # Events that don't affect equity (distributions, fees, NAV updates, etc.)
        no_equity_change_events = [
            EventType.DISTRIBUTION,      # Distributions (income, not capital)
            EventType.NAV_UPDATE,        # NAV updates (value changes, not cash flow)
            EventType.MANAGEMENT_FEE,    # Fees (already reflected in NAV/returns)
            EventType.CARRIED_INTEREST,  # Carried interest (already reflected)
            EventType.OTHER,             # Other events
        ]
        
        if event.event_type in equity_increase_events:
            return event.amount or 0
        elif event.event_type in equity_decrease_events:
            return -(event.amount or 0)
        elif event.event_type in no_equity_change_events:
            return 0
        else:
            # Unknown event type - assume no equity change unless amount is specified
            # This allows for future extensibility
            return 0
    
    def get_distributions_by_type(self, session=None):
        """Get distributions grouped by type for tax analysis."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return {}
        
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
    
    def get_total_distributions(self, session=None):
        """Get total distributions regardless of type for fund comparison."""
        from sqlalchemy.orm import object_session
        from sqlalchemy import func
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Sum all distribution events
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).scalar() or 0
        
        return total
    
    def get_taxable_distributions(self, session=None):
        """Get total taxable distributions (excluding tax withheld)."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
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
    
    def get_gross_distributions(self, session=None):
        """Get total gross distributions (including tax withheld)."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.DISTRIBUTION])
        ).all()
        
        # Sum up the gross amounts (amount field contains gross amount)
        total_gross = sum(event.amount or 0 for event in distribution_events)
        
        return total_gross
    
    def get_net_distributions(self, session=None):
        """Get total net distributions (gross minus tax withheld)."""
        gross = self.get_gross_distributions(session)
        tax_withheld = self.get_total_tax_withheld(session)
        return gross - tax_withheld
    
    def get_total_tax_withheld(self, session=None):
        """Get total tax withheld across all distributions."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.DISTRIBUTION])
        ).all()
        
        # Sum up the tax withheld
        total_tax_withheld = sum(event.tax_withheld or 0 for event in distribution_events)
        
        return total_tax_withheld
    
    def get_distributions_with_tax_details(self, session=None):
        """Get distributions with tax withholding details."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return {}
        
        # Get all distribution events
        distribution_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).order_by(FundEvent.event_date).all()
        
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
            tax_withheld = event.tax_withheld or 0
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
        """Get capital gains based on fund type."""
        if self.tracking_type == FundType.NAV_BASED:
            return self._calculate_nav_based_capital_gains(session)
        else:
            return self._get_cost_based_capital_gains(session)
    
    def _calculate_nav_based_capital_gains(self, session=None):
        """Calculate capital gains for NAV-based funds using FIFO methodology."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Get all unit purchase and sale events in chronological order
        purchase_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.UNIT_PURCHASE  # Only unit purchases for NAV-based
        ).order_by(FundEvent.event_date).all()
        
        sale_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.UNIT_SALE
        ).order_by(FundEvent.event_date).all()
        
        # FIFO calculation
        total_capital_gains = 0
        available_units = []  # List of (units, cost_basis_per_unit, date)
        
        # Process all events chronologically
        all_events = sorted(purchase_events + sale_events, key=lambda x: x.event_date)
        
        for event in all_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                # Purchase event - add units to available pool
                units = event.units_purchased or 0
                cost_per_unit = event.unit_price or 0
                if units > 0 and cost_per_unit > 0:
                    available_units.append((units, cost_per_unit, event.event_date))
            
            elif event.event_type == EventType.UNIT_SALE:
                # Sale event - calculate capital gains using FIFO
                units_to_sell = event.units_sold or 0
                sale_price_per_unit = event.unit_price or 0
                
                while units_to_sell > 0 and available_units:
                    available_units_count, cost_per_unit, purchase_date = available_units[0]
                    
                    units_from_this_purchase = min(units_to_sell, available_units_count)
                    
                    # Calculate capital gain for these units
                    capital_gain = (sale_price_per_unit - cost_per_unit) * units_from_this_purchase
                    total_capital_gains += capital_gain
                    
                    # Update available units
                    units_to_sell -= units_from_this_purchase
                    remaining_units = available_units_count - units_from_this_purchase
                    
                    if remaining_units > 0:
                        available_units[0] = (remaining_units, cost_per_unit, purchase_date)
                    else:
                        available_units.pop(0)
        
        return total_capital_gains
    
    def _get_cost_based_capital_gains(self, session=None):
        """Get capital gains for cost-based funds from explicit events."""
        from sqlalchemy.orm import object_session
        from sqlalchemy import func
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Sum all capital gain income events
        total = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        ).scalar() or 0
        
        return total
    
    def get_capital_movements(self, session=None):
        """Get total capital movements (calls and returns)."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return {"calls": 0, "returns": 0}
        
        # Calculate total capital calls (handles both fund types)
        total_calls = self.get_capital_calls(session)
        
        # Calculate total capital returns
        total_returns = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        ).scalar() or 0
        
        return {"calls": total_calls, "returns": total_returns}
    
    def get_capital_calls(self, session=None):
        """Get total capital calls regardless of fund type."""
        from sqlalchemy.orm import object_session
        from sqlalchemy import func
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
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
        """Calculate average equity balance based on fund type."""
        if self.tracking_type == FundType.NAV_BASED:
            return self._calculate_nav_based_average_equity(session)
        else:
            return self._calculate_cost_based_average_equity(session)
    
    def _calculate_nav_based_average_equity(self, session=None):
        """Calculate average equity balance for NAV-based funds using FIFO cost basis."""
        from sqlalchemy.orm import object_session
        from datetime import date, timedelta
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Get all unit purchase and sale events for this fund
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        
        if not unit_events:
            return 0
        
        # Determine the date range
        start_date = min(event.event_date for event in unit_events)
        end_date = max(event.event_date for event in unit_events)
        
        # If fund is still active, use today as end date
        if self.should_be_active:
            end_date = date.today()
        
        # Calculate daily cost basis using FIFO methodology
        daily_cost_basis = {}
        available_units = []  # List of (units, cost_per_unit, date)
        
        # Initialize with 0 cost basis before first event
        current_date = start_date
        while current_date <= end_date:
            daily_cost_basis[current_date] = 0
            current_date += timedelta(days=1)
        
        # Process each unit event
        for event in unit_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                # Purchase event - add units to available pool
                units = event.units_purchased or 0
                cost_per_unit = event.unit_price or 0
                if units > 0 and cost_per_unit > 0:
                    available_units.append((units, cost_per_unit, event.event_date))
            
            elif event.event_type == EventType.UNIT_SALE:
                # Sale event - remove units using FIFO
                units_to_sell = event.units_sold or 0
                
                while units_to_sell > 0 and available_units:
                    available_units_count, cost_per_unit, purchase_date = available_units[0]
                    
                    units_from_this_purchase = min(units_to_sell, available_units_count)
                    
                    # Update available units
                    units_to_sell -= units_from_this_purchase
                    remaining_units = available_units_count - units_from_this_purchase
                    
                    if remaining_units > 0:
                        available_units[0] = (remaining_units, cost_per_unit, purchase_date)
                    else:
                        available_units.pop(0)
            
            # Calculate current cost basis after this event
            current_cost_basis = sum(units * cost_per_unit for units, cost_per_unit, _ in available_units)
            
            # Update daily cost basis from this date forward
            current_date = event.event_date
            while current_date <= end_date:
                daily_cost_basis[current_date] = current_cost_basis
                current_date += timedelta(days=1)
        
        # Calculate average
        total_cost_basis = sum(daily_cost_basis.values())
        total_days = len(daily_cost_basis)
        
        return total_cost_basis / total_days if total_days > 0 else 0
    
    def _calculate_cost_based_average_equity(self, session=None):
        """Calculate average equity balance for cost-based funds using weighted periods."""
        from sqlalchemy.orm import object_session
        from datetime import date, timedelta
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0
        
        # Get all equity-changing events for this fund
        capital_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        
        if not capital_events:
            return 0
        
        # Calculate weighted average using periods
        total_weighted_equity = 0
        total_days = 0
        current_equity = 0
        current_date = None
        
        for i, event in enumerate(capital_events):
            # For the first event, start from the event date
            if i == 0:
                current_date = event.event_date
                current_equity += self._get_equity_change_for_event(event)
                continue
            
            # Calculate duration of the previous period
            duration_days = (event.event_date - current_date).days
            weighted_equity = current_equity * duration_days
            
            total_weighted_equity += weighted_equity
            total_days += duration_days
            
            # Update equity for next period using generic method
            current_equity += self._get_equity_change_for_event(event)
            
            current_date = event.event_date
        
        # Calculate average
        return total_weighted_equity / total_days if total_days > 0 else 0
    
    def _calculate_irr_base(self, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=None):
        """Base IRR calculation method that can include or exclude tax payments, risk-free charges, and FY debt cost."""
        from sqlalchemy.orm import object_session
        from datetime import date, timedelta
        import numpy_financial as npf
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None
        
        # Only calculate IRR for completed funds
        if self.should_be_active:
            return None
        
        # Get start and end dates
        start_date = self.start_date
        end_date = self.end_date
        
        if not start_date or not end_date:
            return None
        
        # Define event types to include
        event_types = [
            EventType.CAPITAL_CALL,
            EventType.UNIT_PURCHASE,
            EventType.RETURN_OF_CAPITAL,
            EventType.DISTRIBUTION,
            EventType.MANAGEMENT_FEE,
            EventType.CARRIED_INTEREST
        ]
        if include_fy_debt_cost:
            event_types.append(EventType.FY_DEBT_COST)
        # Add tax payments if requested
        if include_tax_payments:
            event_types.append(EventType.TAX_PAYMENT)
        # Add risk-free charges if requested
        if include_risk_free_charges:
            event_types.append(EventType.DAILY_RISK_FREE_INTEREST_CHARGE)
        
        # Get all cash flow events with dates
        cash_flow_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_(event_types)
        ).order_by(FundEvent.event_date).all()
        
        if not cash_flow_events:
            return None
        
        # Prepare cash flows with daily precision
        cash_flows = []
        days_from_start = []
        
        for event in cash_flow_events:
            # Calculate days from start
            days = (event.event_date - start_date).days
            days_from_start.append(days)
            
            # Handle each event type appropriately
            if event.event_type == EventType.CAPITAL_CALL:
                cash_flows.append(-event.amount)
            elif event.event_type == EventType.RETURN_OF_CAPITAL:
                cash_flows.append(event.amount)
            elif event.event_type == EventType.DISTRIBUTION:
                cash_flows.append(event.amount)
            elif event.event_type == EventType.TAX_PAYMENT:
                cash_flows.append(-event.amount)
            elif event.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE:
                cash_flows.append(-event.amount)
            elif event.event_type == EventType.MANAGEMENT_FEE:
                cash_flows.append(-event.amount)
            elif event.event_type == EventType.CARRIED_INTEREST:
                cash_flows.append(-event.amount)
            elif event.event_type == EventType.FY_DEBT_COST:
                cash_flows.append(event.amount)
            else:
                equity_change = self._get_equity_change_for_event(event)
                cash_flows.append(-equity_change)
        
        # Add final value as last cash flow (only for completed funds)
        if not self.should_be_active and cash_flows:
            final_value = self.current_value or 0
            if final_value > 0:
                cash_flows[-1] += final_value
                if days_from_start:
                    days_from_start[-1] = days_from_start[-1]
        
        try:
            monthly_irr = self._calculate_daily_irr(cash_flows, days_from_start)
            if monthly_irr is None:
                return None
            annual_irr = (1 + monthly_irr) ** 12 - 1
            return annual_irr
        except Exception:
            return None

    def calculate_irr(self, session=None):
        """Calculate gross IRR (excluding tax payments and FY debt cost)."""
        return self._calculate_irr_base(include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, session=session)
    
    def calculate_after_tax_irr(self, session=None):
        """Calculate after-tax IRR (including tax payments, excluding FY debt cost)."""
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=False, include_fy_debt_cost=False, session=session)
    
    def calculate_real_irr(self, session=None, risk_free_rate_currency=None):
        """Calculate real IRR including debt cost (opportunity cost of capital and tax benefit)."""
        self.create_daily_risk_free_interest_charges(session, risk_free_rate_currency)
        return self._calculate_irr_base(include_tax_payments=True, include_risk_free_charges=True, include_fy_debt_cost=True, session=session)
    
    def _get_risk_free_rate_for_date(self, target_date, risk_free_rates):
        """Get the risk-free rate for a specific date, using the most recent available rate."""
        if not risk_free_rates:
            return None
        
        # Find the most recent rate that's <= target_date
        applicable_rate = None
        for rate in risk_free_rates:
            if rate.rate_date <= target_date:
                applicable_rate = rate
            else:
                break
        
        return applicable_rate.rate if applicable_rate else None
    
    def _calculate_daily_irr(self, cash_flows, days_from_start, tolerance=1e-10, max_iterations=200):
        """Calculate monthly IRR using daily precision with Newton-Raphson method."""
        import numpy as np
        
        # Initial guess: simple rate of return
        total_investment = abs(cash_flows[0]) if cash_flows[0] < 0 else 0
        total_return = sum(cf for cf in cash_flows[1:] if cf > 0)
        if total_investment == 0:
            return None
        
        # Simple annual return as initial guess
        simple_return = (total_return - total_investment) / total_investment
        # Convert to monthly rate (rough approximation)
        monthly_guess = (1 + simple_return) ** (1/12) - 1
        
        # Ensure reasonable initial guess
        monthly_guess = max(-0.99, min(monthly_guess, 2.0))
        
        # Newton-Raphson iteration
        for iteration in range(max_iterations):
            # Calculate NPV and derivative
            npv = 0
            derivative = 0
            
            for i, (cf, days) in enumerate(zip(cash_flows, days_from_start)):
                # Convert days to months (30.44 days per month)
                months = days / 30.44
                discount_factor = (1 + monthly_guess) ** months
                
                npv += cf / discount_factor
                if months > 0:  # Avoid division by zero
                    derivative -= cf * months / (discount_factor * (1 + monthly_guess))
            
            # Check convergence
            if abs(npv) < tolerance:
                return monthly_guess
            
            # Update guess
            if abs(derivative) < 1e-12:  # Avoid division by zero
                break
                
            monthly_guess = monthly_guess - npv / derivative
            
            # Ensure reasonable bounds
            if monthly_guess < -0.99 or monthly_guess > 2.0:
                return None
        
        return None
    
    def get_irr_percentage(self, session=None):
        """Get IRR as a percentage string."""
        irr = self.calculate_irr(session)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    def get_tax_statements_by_financial_year(self, session=None):
        """Get all tax statements for this fund, grouped by financial year."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return {}
        
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
    
    def get_tax_statement_for_entity_financial_year(self, entity_id, financial_year, session=None):
        """Get a specific tax statement for an entity and financial year."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None
        
        return session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id,
            TaxStatement.entity_id == entity_id,
            TaxStatement.financial_year == financial_year
        ).first()
    
    def create_or_update_tax_statement(self, entity_id, financial_year, **kwargs):
        """Create or update a tax statement for a specific entity and financial year."""
        from sqlalchemy.orm import object_session
        
        session = object_session(self)
        if session is None:
            return None
        
        # Try to find existing statement
        statement = self.get_tax_statement_for_entity_financial_year(entity_id, financial_year, session)
        
        if statement is None:
            # Create new statement
            statement = TaxStatement(
                fund_id=self.id,
                entity_id=entity_id,
                financial_year=financial_year,
                **kwargs
            )
            session.add(statement)
        else:
            # Update existing statement
            for key, value in kwargs.items():
                if hasattr(statement, key):
                    setattr(statement, key, value)
        
        # Calculate total income
        statement.calculate_total_income()
        
        session.commit()
        return statement
    
    def __repr__(self):
        return f"<Fund(id={self.id}, name='{self.name}', company='{self.investment_company.name if self.investment_company else 'Unknown'}')>"

    def get_after_tax_irr_percentage(self, session=None):
        """Get after-tax IRR as a percentage string."""
        irr = self.calculate_after_tax_irr(session)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    def get_real_irr_percentage(self, session=None, risk_free_rate_currency=None):
        """Get real IRR (including debt cost) as a percentage string."""
        irr = self.calculate_real_irr(session, risk_free_rate_currency)
        return f"{irr * 100:.2f}%" if irr is not None else "N/A"
    
    def create_tax_payment_events(self, session=None):
        """Create tax payment events based on tax statements for after-tax IRR calculations."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return []
        
        # Get all tax statements for this fund
        tax_statements = session.query(TaxStatement).filter(
            TaxStatement.fund_id == self.id
        ).all()
        
        created_events = []
        
        for tax_statement in tax_statements:
            # Calculate tax payable if not already calculated
            if tax_statement.tax_payable_rate > 0:
                tax_statement.calculate_tax_payable()
            
            # Only create tax payment event if there's additional tax payable
            if tax_statement.tax_payable > 0.01:  # Allow for small rounding differences
                # Check if tax payment event already exists
                existing_event = session.query(FundEvent).filter(
                    FundEvent.fund_id == self.id,
                    FundEvent.event_type == EventType.TAX_PAYMENT,
                    FundEvent.event_date == tax_statement.get_tax_payment_date(),
                    FundEvent.amount == tax_statement.tax_payable
                ).first()
                
                if not existing_event:
                    # Create tax payment event
                    tax_event = FundEvent(
                        fund_id=self.id,
                        event_type=EventType.TAX_PAYMENT,
                        event_date=tax_statement.get_tax_payment_date(),
                        amount=tax_statement.tax_payable,
                        description=f"Tax payment for FY {tax_statement.financial_year}",
                        reference_number=f"TAX-{tax_statement.financial_year}"
                    )
                    session.add(tax_event)
                    created_events.append(tax_event)
        
        if created_events:
            session.commit()
        
        return created_events

    def add_distribution_with_tax(self, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution with automatic tax payment event."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None, None
        
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
            self.update_current_equity_balance(session)
        
        return distribution_event, tax_event
    
    def add_distribution_with_tax_rate(self, event_date, gross_amount, tax_rate, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution with tax calculated from rate."""
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

    def create_daily_risk_free_interest_charges(self, session=None, risk_free_rate_currency=None):
        """Create daily risk-free interest charge events for real IRR calculations."""
        from sqlalchemy.orm import object_session
        from datetime import date, timedelta
        
        if session is None:
            session = object_session(self)
        if session is None:
            return []
        
        # Use fund currency if not specified
        if risk_free_rate_currency is None:
            risk_free_rate_currency = self.currency
        
        # Get start and end dates
        start_date = self.start_date
        end_date = self.end_date
        
        if not start_date or not end_date:
            return []
        
        # Get risk-free rates for the period - get all rates <= end_date
        # The _get_risk_free_rate_for_date method will find the most recent rate <= target_date
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
                EventType.DISTRIBUTION,
                EventType.MANAGEMENT_FEE,
                EventType.CARRIED_INTEREST,
                EventType.TAX_PAYMENT
            ])
        ).order_by(FundEvent.event_date).all()
        
        created_events = []
        current_equity = 0
        current_date = start_date
        
        # Process each event and calculate daily interest charges
        for event in cash_flow_events:
            # Add interest charges for each day from current_date to event_date
            while current_date < event.event_date:
                if current_date not in existing_dates:
                    # Find risk-free rate for this date
                    rate = self._get_risk_free_rate_for_date(current_date, risk_free_rates)
                    if rate is not None and current_equity > 0:
                        # Calculate daily interest charge
                        daily_interest = current_equity * (rate / 100) / 365.25
                        
                        # Create interest charge event
                        interest_event = FundEvent(
                            fund_id=self.id,
                            event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                            event_date=current_date,
                            amount=daily_interest,
                            description=f"Daily risk-free interest charge ({rate:.2f}% p.a.)",
                            reference_number=f"RFR-{current_date.strftime('%Y%m%d')}"
                        )
                        session.add(interest_event)
                        created_events.append(interest_event)
                
                current_date += timedelta(days=1)
            
            # Update equity balance for the actual event
            current_equity += self._get_equity_change_for_event(event)
            current_date = event.event_date
        
        # Add interest charges for remaining days until end_date
        while current_date <= end_date:
            if current_date not in existing_dates:
                rate = self._get_risk_free_rate_for_date(current_date, risk_free_rates)
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
                    session.add(interest_event)
                    created_events.append(interest_event)
            
            current_date += timedelta(days=1)
        
        if created_events:
            session.commit()
            print(f"Created {len(created_events)} daily risk-free interest charge events for {self.name}")
        
        return created_events

    def calculate_financial_year_interest_expense(self, financial_year, session=None):
        """Calculate total interest expense for a specific financial year."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return 0.0
        
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
    
    def create_fy_debt_cost_events(self, session=None):
        """Create FY debt cost events for all financial years with interest expenses."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return []
        
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
        current_date = start_date
        financial_years = set()
        
        while current_date <= end_date:
            fy = entity.get_financial_year(current_date)
            financial_years.add(fy)
            
            # Move to next month
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 1)
            else:
                current_date = date(current_date.year, current_date.month + 1, 1)
        
        # Process each financial year
        for fy in sorted(financial_years):
            # Calculate interest expense for this FY
            interest_expense = self.calculate_financial_year_interest_expense(fy, session)
            
            if interest_expense > 0:
                # Get or create tax statement for this FY
                tax_statement = self.get_tax_statement_for_entity_financial_year(
                    self.entity_id, fy, session
                )
                
                if not tax_statement:
                    # Create a basic tax statement
                    tax_statement = self.create_or_update_tax_statement(
                        self.entity_id, fy,
                        total_interest_expense=interest_expense,
                        interest_deduction_rate=30.0  # Default 30% deduction rate
                    )
                else:
                    # Update existing tax statement
                    tax_statement.total_interest_expense = interest_expense
                    if not tax_statement.interest_deduction_rate:
                        tax_statement.interest_deduction_rate = 30.0  # Default 30% deduction rate
                
                # Calculate tax benefit and create event
                tax_benefit = tax_statement.calculate_interest_tax_benefit()
                if tax_benefit > 0:
                    event = tax_statement.create_fy_debt_cost_event(session)
                    if event:
                        created_events.append(event)
        
        if created_events:
            session.commit()
            print(f"Created {len(created_events)} FY debt cost events for {self.name}")
        
        return created_events

    def recalculate_debt_costs(self, session=None, risk_free_rate_currency=None):
        """
        Recalculate all daily risk-free interest charges and FY debt cost events for this fund.
        Deletes existing events of these types and recreates them.
        """
        from sqlalchemy.orm import object_session
        if session is None:
            session = object_session(self)
        if session is None:
            return []
        # Delete all DAILY_RISK_FREE_INTEREST_CHARGE and FY_DEBT_COST events for this fund
        deleted_daily = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        ).delete()
        deleted_fy = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.FY_DEBT_COST
        ).delete()
        session.commit()
        # Recreate daily risk-free interest charges
        self.create_daily_risk_free_interest_charges(session, risk_free_rate_currency)
        # Recreate FY debt cost events
        self.create_fy_debt_cost_events(session)
        session.commit()
        print(f"Recalculated debt costs for fund '{self.name}': deleted {deleted_daily} daily interest charges, {deleted_fy} FY debt cost events, and recreated them.")


class FundEvent(Base):
    """Model representing various dated events for a fund."""
    __tablename__ = 'fund_events'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    event_type = Column(String(50), nullable=False)  # 'capital_call', 'capital_return', 'nav_update', 'dividend', etc.
    event_date = Column(Date, nullable=False)
    amount = Column(Float)  # Amount for the event (can be None for some event types)
    
    # Event-specific fields
    nav_per_share = Column(Float)  # For NAV updates
    shares_owned = Column(Float)  # For NAV updates
    call_percentage = Column(Float)  # For capital calls (percentage of commitment)
    return_percentage = Column(Float)  # For capital returns (percentage of commitment)
    
    # Distribution type for tax purposes
    distribution_type = Column(Enum(DistributionType))  # Type of distribution (for tax treatment)
    
    # Tax withholding for distributions
    tax_withheld = Column(Float, default=0.0)  # Tax withheld on distributions
    tax_withholding_rate = Column(Float, default=0.0)  # Tax withholding rate as percentage (e.g., 15.0 for 15%)
    
    # NAV-based fund event fields
    units_purchased = Column(Float)  # Units purchased in this event
    units_sold = Column(Float)  # Units sold in this event
    unit_price = Column(Float)  # Unit price for this event
    
    # Metadata
    description = Column(Text)
    reference_number = Column(String(100))  # External reference number
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    fund = relationship("Fund", back_populates="fund_events")
    
    def __repr__(self):
        return f"<FundEvent(id={self.id}, fund_id={self.fund_id}, type='{self.event_type}', date='{self.event_date}', amount={self.amount})>"
    
    def calculate_tax_from_rate(self):
        """Calculate tax_withheld from tax_withholding_rate."""
        if self.tax_withholding_rate and self.amount:
            return (self.amount * self.tax_withholding_rate) / 100
        return 0.0
    
    def calculate_rate_from_tax(self):
        """Calculate tax_withholding_rate from tax_withheld."""
        if self.tax_withheld and self.amount and self.amount > 0:
            return (self.tax_withheld / self.amount) * 100
        return 0.0
    
    def update_tax_calculations(self, provided_field='rate'):
        """
        Update tax calculations based on provided field.
        Note: This method is kept for backward compatibility but tax withholding
        should now be handled via separate tax payment events.
        """
        if provided_field == 'rate' and self.tax_withholding_rate:
            self.calculate_tax_from_rate()
        elif provided_field == 'amount' and self.tax_withheld:
            self.calculate_rate_from_tax()
        else:
            # For distributions, tax withholding should be handled via separate events
            # Clear any existing tax withholding fields
            self.tax_withheld = 0.0
            self.tax_withholding_rate = 0.0
    
    def infer_distribution_type(self):
        """Automatically infer distribution type from event type."""
        # For the consolidated DISTRIBUTION event type, we need to specify the distribution type
        # This method is now mainly for backward compatibility
        # The distribution_type should be set explicitly when creating DISTRIBUTION events
        return self.distribution_type
    
    def set_event_type_and_infer_distribution(self, event_type):
        """Set event type and automatically infer distribution type if applicable."""
        self.event_type = event_type
        if event_type == EventType.DISTRIBUTION:
            self.infer_distribution_type()

    def create_distribution_with_tax(self, fund_id, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Create a distribution event with automatic tax payment event."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None, None
        
        # Create the distribution event (gross amount)
        distribution_event = FundEvent(
            fund_id=fund_id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=gross_amount,
            distribution_type=distribution_type,
            description=description,
            reference_number=reference_number
        )
        
        # Infer distribution type if not provided
        if not distribution_type:
            distribution_event.infer_distribution_type()
        
        session.add(distribution_event)
        
        # Create tax payment event if there's tax withheld
        tax_event = None
        if tax_withheld > 0.01:
            tax_event = FundEvent(
                fund_id=fund_id,
                event_type=EventType.TAX_PAYMENT,
                event_date=event_date,
                amount=tax_withheld,
                description=f"Tax withheld on distribution",
                reference_number=f"TAX-WITHHELD-{distribution_event.id if distribution_event.id else 'NEW'}"
            )
            session.add(tax_event)
        
        return distribution_event, tax_event
    
    @classmethod
    def create_distribution_with_tax_static(cls, fund_id, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Static method to create a distribution event with automatic tax payment event."""
        if session is None:
            return None, None
        
        # Create the distribution event (gross amount)
        distribution_event = cls(
            fund_id=fund_id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=gross_amount,
            distribution_type=distribution_type,
            description=description,
            reference_number=reference_number
        )
        
        # Infer distribution type if not provided
        if not distribution_type:
            distribution_event.infer_distribution_type()
        
        session.add(distribution_event)
        
        # Create tax payment event if there's tax withheld
        tax_event = None
        if tax_withheld > 0.01:
            tax_event = cls(
                fund_id=fund_id,
                event_type=EventType.TAX_PAYMENT,
                event_date=event_date,
                amount=tax_withheld,
                description=f"Tax withheld on distribution",
                reference_number=f"TAX-WITHHELD-{distribution_event.id if distribution_event.id else 'NEW'}"
            )
            session.add(tax_event)
        
        return distribution_event, tax_event


class RiskFreeRate(Base):
    """Model representing risk-free rates for different currencies over time."""
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
        return f"<RiskFreeRate(id={self.id}, currency='{self.currency}', date={self.rate_date}, rate={self.rate}%)>"


class TaxStatement(Base):
    """Model representing tax statements from funds for specific financial years."""
    __tablename__ = 'tax_statements'
    
    id = Column(Integer, primary_key=True)
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
    financial_year = Column(String(10), nullable=False)  # e.g., "2023-24" for Australian FY
    
    # Tax components from fund statement
    gross_interest_income = Column(Float, default=0.0)
    net_interest_income = Column(Float, default=0.0)
    foreign_income = Column(Float, default=0.0)
    capital_gains = Column(Float, default=0.0)
    other_income = Column(Float, default=0.0)
    total_income = Column(Float, default=0.0)
    
    # Tax withheld/credits
    tax_withheld = Column(Float, default=0.0)
    foreign_tax_credits = Column(Float, default=0.0)
    
    # After-tax IRR fields
    tax_already_paid = Column(Float, default=0.0)  # Tax already withheld/paid (no additional cash flow)
    tax_payable = Column(Float, default=0.0)  # Additional tax payable (creates cash outflow)
    tax_payable_rate = Column(Float, default=0.0)  # Tax rate for additional tax payable (e.g., 15.0 for 15%)
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
    fund = relationship("Fund", back_populates="tax_statements")
    entity = relationship("Entity", back_populates="tax_statements")
    
    # Composite unique constraint to ensure one statement per fund/entity/financial year
    __table_args__ = (
        UniqueConstraint('fund_id', 'entity_id', 'financial_year', name='unique_tax_statement'),
    )
    
    def __repr__(self):
        return f"<TaxStatement(id={self.id}, fund_id={self.fund_id}, entity_id={self.entity_id}, fy={self.financial_year})>"
    
    def calculate_total_income(self):
        """Calculate total income from all components, treating None as 0.0."""
        self.total_income = (
            (self.gross_interest_income or 0.0) +
            (self.foreign_income or 0.0) +
            (self.capital_gains or 0.0) +
            (self.other_income or 0.0)
        )
        return self.total_income
    
    def get_net_income(self):
        """Calculate net income after tax withheld."""
        return self.total_income - self.tax_withheld
    
    def calculate_tax_payable(self):
        """Calculate additional tax payable based on tax_payable_rate."""
        if self.tax_payable_rate and self.total_income > 0:
            total_tax_liability = (self.total_income * self.tax_payable_rate) / 100
            self.tax_payable = max(0, total_tax_liability - self.tax_withheld - self.foreign_tax_credits)
            self.tax_already_paid = self.tax_withheld + self.foreign_tax_credits
        return self.tax_payable
    
    def get_tax_payment_date(self):
        """Get the tax payment date, defaulting to financial year end if not specified."""
        if self.tax_payment_date:
            return self.tax_payment_date
        
        # Default to financial year end
        fy_start, fy_end = self.get_financial_year_dates()
        return fy_end
    
    def get_financial_year_dates(self):
        """Get the start and end dates for this financial year based on entity jurisdiction."""
        # Get the entity to determine jurisdiction
        from sqlalchemy.orm import object_session
        session = object_session(self)
        if session is None:
            return None, None
        
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return None, None
        
        # Parse financial year (e.g., "2023-24" or "2023-2024")
        if '-' in self.financial_year:
            start_year, end_year = self.financial_year.split('-')
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
            year = int(self.financial_year)
            if entity.tax_jurisdiction == "AU":
                fy_start = date(year, 7, 1)
                fy_end = date(year + 1, 6, 30)
            else:
                fy_start = date(year, 1, 1)
                fy_end = date(year, 12, 31)
        
        return fy_start, fy_end
    
    def reconcile_with_actual_distributions(self, session=None):
        """
        Compare the tax statement to actual distributions received for this fund/entity/financial year.
        Returns a dict with statement values, actuals, and differences.
        """
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None
        
        # Get financial year dates
        fy_start, fy_end = self.get_financial_year_dates()
        if not fy_start or not fy_end:
            return None
        
        # Query actual distributions for this fund/entity/financial year
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.fund_id,
            FundEvent.event_type == EventType.DISTRIBUTION,
            FundEvent.event_date >= fy_start,
            FundEvent.event_date <= fy_end
        ).all()
        
        # Calculate actual totals
        actual_gross = sum(e.amount for e in events)
        actual_tax = sum(e.tax_withheld for e in events)
        actual_net = actual_gross - actual_tax
        
        # Calculate differences
        gross_diff = self.gross_interest_income - actual_gross
        tax_diff = self.tax_withheld - actual_tax
        net_diff = self.net_interest_income - actual_net
        
        return {
            'financial_year': self.financial_year,
            'period': {
                'start': fy_start,
                'end': fy_end
            },
            'statement': {
                'gross_interest_income': self.gross_interest_income,
                'tax_withheld': self.tax_withheld,
                'net_interest_income': self.net_interest_income,
            },
            'actual': {
                'gross_distributed': actual_gross,
                'tax_withheld': actual_tax,
                'net_received': actual_net,
                'distribution_count': len(events)
            },
            'difference': {
                'gross': gross_diff,
                'tax_withheld': tax_diff,
                'net': net_diff
            },
            'explanation': self._get_reconciliation_explanation(gross_diff, tax_diff, net_diff)
        }
    
    def _get_reconciliation_explanation(self, gross_diff, tax_diff, net_diff):
        """Generate an explanation for the reconciliation differences."""
        explanations = []
        
        if abs(gross_diff) > 0.01:  # Allow for small rounding differences
            if gross_diff > 0:
                explanations.append(f"${gross_diff:,.2f} of interest was accrued but not yet distributed")
            else:
                explanations.append(f"${abs(gross_diff):,.2f} more was distributed than reported in tax statement")
        
        if abs(tax_diff) > 0.01:
            if tax_diff > 0:
                explanations.append(f"${tax_diff:,.2f} more tax was withheld than actually deducted")
            else:
                explanations.append(f"${abs(tax_diff):,.2f} less tax was withheld than actually deducted")
        
        if abs(net_diff) > 0.01:
            if net_diff > 0:
                explanations.append(f"${net_diff:,.2f} more net income reported than actually received")
            else:
                explanations.append(f"${abs(net_diff):,.2f} more net income received than reported")
        
        if not explanations:
            explanations.append("Tax statement matches actual distributions perfectly")
        
        return "; ".join(explanations)
    
    def calculate_interest_tax_benefit(self):
        """Calculate the tax benefit from interest expense deduction."""
        if self.total_interest_expense and self.interest_deduction_rate:
            self.interest_tax_benefit = (self.total_interest_expense * self.interest_deduction_rate) / 100
        else:
            self.interest_tax_benefit = 0.0
        return self.interest_tax_benefit
    
    def create_fy_debt_cost_event(self, session=None):
        """Create a FY debt cost event for real IRR calculations."""
        from sqlalchemy.orm import object_session
        
        if session is None:
            session = object_session(self)
        if session is None:
            return None
        
        # Calculate the tax benefit
        tax_benefit = self.calculate_interest_tax_benefit()
        if tax_benefit <= 0:
            return None
        
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
            existing_event.amount = tax_benefit
            existing_event.description = f"FY {self.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})"
            session.commit()
            return existing_event
        
        # Create new event
        event = FundEvent(
            fund_id=self.fund_id,
            event_type=EventType.FY_DEBT_COST,
            event_date=fy_end,
            amount=tax_benefit,  # Positive cash flow (tax benefit)
            description=f"FY {self.financial_year} Interest Tax Benefit (${tax_benefit:,.2f})",
            reference_number=f"FY_DEBT_COST_{self.financial_year}"
        )
        
        session.add(event)
        session.commit()
        return event


# Event type constants for consistency
class EventType:
    # Capital movements
    CAPITAL_CALL = "capital_call"
    RETURN_OF_CAPITAL = "return_of_capital"
    
    # Distributions (consolidated - use distribution_type for tax classification)
    DISTRIBUTION = "distribution"
    
    # Tax payments for after-tax IRR calculations
    TAX_PAYMENT = "tax_payment"
    
    # Risk-free interest charges for real IRR calculations
    DAILY_RISK_FREE_INTEREST_CHARGE = "daily_risk_free_interest_charge"
    
    # Financial year debt cost tax benefits for real IRR calculations
    FY_DEBT_COST = "fy_debt_cost"
    
    # NAV-based fund events
    NAV_UPDATE = "nav_update"
    UNIT_PURCHASE = "unit_purchase"
    UNIT_SALE = "unit_sale"
    
    # Fees and other
    MANAGEMENT_FEE = "management_fee"
    CARRIED_INTEREST = "carried_interest"
    OTHER = "other"


# Add event listeners for automatic average equity balance recalculation
@event.listens_for(FundEvent, 'after_insert')
def recalculate_average_equity_after_insert(mapper, connection, target):
    """Automatically recalculate average equity balance after a new event is inserted."""
    from sqlalchemy.orm import sessionmaker
    
    # Get the session from the connection
    Session = sessionmaker(bind=connection)
    session = Session()
    
    try:
        # Get the fund and recalculate
        fund = session.query(Fund).filter(Fund.id == target.fund_id).first()
        if fund:
            fund.update_average_equity_balance(session)
            print(f"Auto-recalculated average equity balance for {fund.name} after new event")
    except Exception as e:
        print(f"Error auto-recalculating average equity balance: {e}")
    finally:
        session.close()


@event.listens_for(FundEvent, 'after_update')
def recalculate_average_equity_after_update(mapper, connection, target):
    """Automatically recalculate average equity balance after an event is updated."""
    from sqlalchemy.orm import sessionmaker
    
    # Get the session from the connection
    Session = sessionmaker(bind=connection)
    session = Session()
    
    try:
        # Get the fund and recalculate
        fund = session.query(Fund).filter(Fund.id == target.fund_id).first()
        if fund:
            fund.update_average_equity_balance(session)
            print(f"Auto-recalculated average equity balance for {fund.name} after event update")
    except Exception as e:
        print(f"Error auto-recalculating average equity balance: {e}")
    finally:
        session.close()


@event.listens_for(FundEvent, 'after_delete')
def recalculate_average_equity_after_delete(mapper, connection, target):
    """Automatically recalculate average equity balance after an event is deleted."""
    from sqlalchemy.orm import sessionmaker
    
    # Get the session from the connection
    Session = sessionmaker(bind=connection)
    session = Session()
    
    try:
        # Get the fund and recalculate
        fund = session.query(Fund).filter(Fund.id == target.fund_id).first()
        if fund:
            fund.update_average_equity_balance(session)
            print(f"Auto-recalculated average equity balance for {fund.name} after event deletion")
    except Exception as e:
        print(f"Error auto-recalculating average equity balance: {e}")
    finally:
        session.close() 