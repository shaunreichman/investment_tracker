"""
Fund creation module.

This module contains methods for creating fund events and managing fund state.
These methods handle database operations and update calculated fields.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from .models import Fund, FundEvent, EventType, FundType, DistributionType
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
    
    def add_capital_call(self, session, event_date, amount, description=None, reference_number=None):
        """Add a capital call event for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Capital calls are only applicable to cost-based funds")
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=event_date,
            amount=amount,
            description=description,
            reference_number=reference_number
        )
        
        session.add(event)
        session.flush()  # Get the event ID
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        return event
    
    def add_return_of_capital(self, session, event_date, amount, description=None, reference_number=None):
        """Add a return of capital event for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            raise ValueError("Returns of capital are only applicable to cost-based funds")
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.RETURN_OF_CAPITAL,
            event_date=event_date,
            amount=amount,
            description=description,
            reference_number=reference_number
        )
        
        session.add(event)
        session.flush()
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        return event
    
    def add_unit_purchase(self, session, event_date, units_purchased, unit_price, amount, 
                         brokerage_fee=0.0, description=None, reference_number=None):
        """Add a unit purchase event for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit purchases are only applicable to NAV-based funds")
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=event_date,
            units_purchased=units_purchased,
            unit_price=unit_price,
            amount=amount,
            brokerage_fee=brokerage_fee,
            description=description,
            reference_number=reference_number
        )
        
        session.add(event)
        session.flush()
        
        # Update calculated fields
        self._update_nav_fields(session)
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        return event
    
    def add_unit_sale(self, session, event_date, units_sold, unit_price, amount,
                      brokerage_fee=0.0, description=None, reference_number=None):
        """Add a unit sale event for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("Unit sales are only applicable to NAV-based funds")
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.UNIT_SALE,
            event_date=event_date,
            units_sold=units_sold,
            unit_price=unit_price,
            amount=amount,
            brokerage_fee=brokerage_fee,
            description=description,
            reference_number=reference_number
        )
        
        session.add(event)
        session.flush()
        
        # Update calculated fields
        self._update_nav_fields(session)
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        return event
    
    def add_distribution(self, session, event_date, amount, distribution_type=None, 
                        description=None, reference_number=None):
        """Add a distribution event for any fund type."""
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=amount,
            distribution_type=distribution_type,
            description=description,
            reference_number=reference_number
        )
        
        # Infer distribution type if not provided
        if not distribution_type:
            event.distribution_type = event.infer_distribution_type()
        
        session.add(event)
        session.flush()
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        return event
    
    def add_nav_update(self, session, event_date, nav_per_share, units_owned, description=None):
        """Add a NAV update event for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            raise ValueError("NAV updates are only applicable to NAV-based funds")
        
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.NAV_UPDATE,
            event_date=event_date,
            nav_per_share=nav_per_share,
            units_owned=units_owned,
            description=description
        )
        
        session.add(event)
        session.flush()
        
        # Update calculated fields
        self._update_nav_fields(session)
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        
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


class FundUpdateMixin:
    """Mixin class for fund update and calculation methods."""
    
    def _update_nav_fields(self, session):
        """Update NAV-based fund fields (current_units, current_unit_price)."""
        if self.tracking_type != FundType.NAV_BASED:
            return
        
        # Get NAV events
        nav_events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        ).order_by(FundEvent.event_date).all()
        
        # Calculate NAV amounts
        nav_amounts = calculate_nav_event_amounts(nav_events)
        
        self._current_units = nav_amounts['current_units']
        self._current_unit_price = nav_amounts['current_unit_price']
    
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