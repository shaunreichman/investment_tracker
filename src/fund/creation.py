"""
Fund creation module.

This module contains methods for creating fund events and managing fund state.
These methods handle database operations and update calculated fields.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Fund, FundEvent, EventType, FundType, DistributionType, TaxPaymentType
from ..shared.utils import with_session
from .calculations import (
    calculate_average_equity_balance_nav,
    calculate_average_equity_balance_cost,
    orchestrate_nav_based_average_equity,
    orchestrate_cost_based_average_equity
)
from ..shared.calculations import (
    calculate_nav_event_amounts,
    get_unit_events_for_fund,
    calculate_nav_based_cost_basis_for_irr,
    get_equity_change_for_event
)


class FundCreationMixin:
    """Mixin class for fund creation and event management methods."""
    
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
        self._update_current_equity_balance(session)
        self._update_total_cost_basis(session)
        
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
        self._update_current_equity_balance(session)
        self._update_total_cost_basis(session)
        
        return event
    
    @with_session
    def add_unit_purchase(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """Add a unit purchase event and update calculated fields.
        
        Args:
            units (float): Number of units purchased
            price (float): Unit price
            date (date): Purchase date
            brokerage_fee (float): Brokerage fee
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created unit purchase event
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit purchases are only applicable for NAV-based funds")
        
        # Calculate total amount
        amount = units * price + brokerage_fee
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date,
            units_purchased=units,
            unit_price=price,
            amount=amount,
            brokerage_fee=brokerage_fee,
            description=description or f"Unit purchase: {units:,.2f} units @ ${price:.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self._update_current_units_and_price(session)
        self._update_current_equity_balance(session)
        
        return event
    
    @with_session
    def add_unit_sale(self, units, price, date, brokerage_fee=0.0, description=None, reference_number=None, session=None):
        """Add a unit sale event and update calculated fields.
        
        Args:
            units (float): Number of units sold
            price (float): Unit price
            date (date): Sale date
            brokerage_fee (float): Brokerage fee
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created unit sale event
        """
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit sales are only applicable for NAV-based funds")
        
        # Calculate total amount
        amount = units * price - brokerage_fee
        
        # Create event
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_SALE,
            event_date=date,
            units_sold=units,
            unit_price=price,
            amount=amount,
            brokerage_fee=brokerage_fee,
            description=description or f"Unit sale: {units:,.2f} units @ ${price:.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self._update_current_units_and_price(session)
        self._update_current_equity_balance(session)
        
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
    
    @with_session
    def add_nav_update(self, nav_per_share, date, description=None, reference_number=None, session=None):
        """Add a NAV update event and update calculated fields.
        
        Args:
            nav_per_share (float): NAV per share
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
            description=description or f"NAV update: ${nav_per_share:.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self._update_current_units_and_price(session)
        self._update_current_equity_balance(session)
        
        return event
    
    def add_tax_payment(self, session, event_date, amount, tax_payment_type, 
                       description=None, reference_number=None):
        """Add a tax payment event."""
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=amount,
            tax_payment_type=tax_payment_type,
            description=description,
            reference_number=reference_number
        )
        
        session.add(event)
        session.flush()
        
        return event
    
    def add_daily_risk_free_interest_charge(self, session, event_date, amount, description=None):
        """Add a daily risk-free interest charge event for real IRR calculations."""
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
            event_date=event_date,
            amount=amount,
            description=description
        )
        
        session.add(event)
        session.flush()
        
        return event
    
    def add_fy_debt_cost_event(self, session, event_date, amount, description=None):
        """Add a financial year debt cost event for real IRR calculations."""
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.FY_DEBT_COST,
            event_date=event_date,
            amount=amount,
            description=description
        )
        
        session.add(event)
        session.flush()
        
        return event
    
    @with_session
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
    
    @with_session
    def add_distribution_with_tax(self, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution event with associated tax payment.
        
        Args:
            event_date (date): Distribution date
            gross_amount (float): Gross distribution amount
            tax_withheld (float): Tax withheld from distribution
            tax_rate (float): Tax rate used (for reference)
            distribution_type (DistributionType): Type of distribution
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            tuple: (distribution_event, tax_event)
        """
        # Create distribution event
        distribution_event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=gross_amount,
            distribution_type=distribution_type,
            description=description or f"Distribution: ${gross_amount:,.2f}",
            reference_number=reference_number
        )
        
        session.add(distribution_event)
        
        # Create tax payment event if there's tax withheld
        tax_event = None
        if tax_withheld > 0:
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
        
        return distribution_event, tax_event


class FundUpdateMixin:
    """Mixin class for fund update and calculation methods."""
    
    def _update_current_units_and_price(self, session):
        """Update NAV-based fund fields (current_units, current_unit_price)."""
        if self.tracking_type != FundType.NAV_BASED:
            return
        
        # Get all unit purchase/sale events
        unit_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type.in_([EventType.UNIT_PURCHASE, EventType.UNIT_SALE])
        ).order_by(FundEvent.event_date).all()
        
        # Calculate current units
        current_units = 0.0
        for event in unit_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                current_units += event.units_purchased
            elif event.event_type == EventType.UNIT_SALE:
                current_units -= event.units_sold
        
        self._current_units = current_units
        
        # Get latest NAV update for current unit price
        latest_nav = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date.desc()).first()
        
        self._current_unit_price = latest_nav.nav_per_share if latest_nav else None
    
    def _update_current_equity_balance(self, session):
        """Update the current equity balance based on all events."""
        # Get all events for this fund
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date).all()
        
        current_equity = 0.0
        for event in events:
            current_equity += get_equity_change_for_event(event, self.tracking_type)
        
        self.current_equity_balance = current_equity
    
    def _update_average_equity_balance(self, session):
        """Update the average equity balance over the fund's lifetime."""
        # Get fund start and end dates
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date).all()
        
        if not events:
            self.average_equity_balance = 0.0
            return
        
        start_date = events[0].event_date
        end_date = events[-1].event_date
        
        # Calculate average equity based on fund type
        if self.tracking_type == FundType.NAV_BASED:
            avg_equity = orchestrate_nav_based_average_equity(events, start_date, end_date)
        else:
            avg_equity = orchestrate_cost_based_average_equity(events, start_date, end_date)
        
        self.average_equity_balance = avg_equity
    
    def _update_is_active(self, session):
        """Update the is_active status based on current equity balance."""
        self.is_active = self.current_equity_balance > 0.01
    
    def _update_total_cost_basis(self, session):
        """Update the total cost basis for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            return
        
        # Get capital calls and returns
        capital_calls = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        ).scalar() or 0.0
        
        returns = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        ).scalar() or 0.0
        
        self._total_cost_basis = capital_calls - returns
    
    def recalculate_all_fields(self, session):
        """Recalculate all calculated fields for the fund."""
        self._update_nav_fields(session)
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        self._update_total_cost_basis(session)


# Add mixins to Fund class
Fund.__bases__ = (FundCreationMixin, FundUpdateMixin) + Fund.__bases__


__all__ = [
    'FundCreationMixin',
    'FundUpdateMixin',
] 