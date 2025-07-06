"""
Fund creation module.

This module contains methods for creating fund events and managing fund state.
These methods handle database operations and update calculated fields.
"""

from datetime import date, datetime, timedelta
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
        """Add a distribution event and update calculated fields.
        
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
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        
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
            description=description or f"NAV update: ${nav_per_share:.4f}",
            reference_number=reference_number
        )
        
        session.add(event)
        
        # Update calculated fields
        self._update_current_units_and_price(session)
        
        return event
    
    def add_tax_payment(self, session, event_date, amount, tax_payment_type, 
                       description=None, reference_number=None):
        """Add a tax payment event.
        
        Args:
            session: Database session
            event_date (date): Tax payment date
            amount (float): Tax payment amount
            tax_payment_type (TaxPaymentType): Type of tax payment
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            FundEvent: The created tax payment event
        """
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=amount,
            tax_payment_type=tax_payment_type,
            description=description or f"Tax payment: ${amount:,.2f}",
            reference_number=reference_number
        )
        
        session.add(event)
        return event
    
    def add_daily_risk_free_interest_charge(self, session, event_date, amount, description=None):
        """Add a daily risk-free interest charge event.
        
        Args:
            session: Database session
            event_date (date): Charge date
            amount (float): Interest charge amount
            description (str): Event description
            
        Returns:
            FundEvent: The created interest charge event
        """
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
            event_date=event_date,
            amount=amount,
            description=description or f"Daily interest charge: ${amount:.2f}"
        )
        
        session.add(event)
        return event
    
    def add_fy_debt_cost_event(self, session, event_date, amount, description=None):
        """Add a financial year debt cost event.
        
        Args:
            session: Database session
            event_date (date): Event date
            amount (float): Debt cost amount
            description (str): Event description
            
        Returns:
            FundEvent: The created debt cost event
        """
        event = FundEvent(
            fund_id=self.id,
            event_type=EventType.FY_DEBT_COST,
            event_date=event_date,
            amount=amount,
            description=description or f"FY debt cost: ${amount:,.2f}"
        )
        
        session.add(event)
        return event
    
    @with_session
    def add_distribution_with_tax_rate(self, event_date, gross_amount, tax_rate, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution with calculated tax withholding.
        
        Args:
            event_date (date): Distribution date
            gross_amount (float): Gross distribution amount
            tax_rate (float): Tax rate as percentage
            distribution_type (DistributionType): Type of distribution
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            tuple: (distribution_event, tax_event) or (distribution_event, None) if no tax
        """
        # Calculate tax withheld
        tax_withheld = gross_amount * (tax_rate / 100)
        net_amount = gross_amount - tax_withheld
        
        # Create distribution event
        dist_event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=net_amount,
            distribution_type=distribution_type or DistributionType.INTEREST,
            description=description or f"Distribution: ${gross_amount:,.2f} (net: ${net_amount:,.2f})",
            reference_number=reference_number
        )
        
        session.add(dist_event)
        
        # Create tax withholding event if applicable
        tax_event = None
        if tax_withheld > 0.01:  # Allow for small rounding differences
            tax_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.TAX_PAYMENT,
                event_date=event_date,
                amount=tax_withheld,
                tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
                description=f"Tax withheld: ${tax_withheld:,.2f}",
                reference_number=reference_number
            )
            session.add(tax_event)
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        
        return dist_event, tax_event
    
    @with_session
    def add_distribution_with_tax(self, event_date, gross_amount, tax_withheld=0.0, tax_rate=None, distribution_type=None, description=None, reference_number=None, session=None):
        """Add a distribution with specified tax withholding.
        
        Args:
            event_date (date): Distribution date
            gross_amount (float): Gross distribution amount
            tax_withheld (float): Tax withheld amount
            tax_rate (float): Tax rate as percentage (for reference)
            distribution_type (DistributionType): Type of distribution
            description (str): Event description
            reference_number (str): External reference number
            
        Returns:
            tuple: (distribution_event, tax_event) or (distribution_event, None) if no tax
        """
        net_amount = gross_amount - tax_withheld
        
        # Create distribution event
        dist_event = FundEvent(
            fund_id=self.id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=net_amount,
            distribution_type=distribution_type or DistributionType.INTEREST,
            description=description or f"Distribution: ${gross_amount:,.2f} (net: ${net_amount:,.2f})",
            reference_number=reference_number
        )
        
        session.add(dist_event)
        
        # Create tax withholding event if applicable
        tax_event = None
        if tax_withheld > 0.01:  # Allow for small rounding differences
            tax_event = FundEvent(
                fund_id=self.id,
                event_type=EventType.TAX_PAYMENT,
                event_date=event_date,
                amount=tax_withheld,
                tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
                description=f"Tax withheld: ${tax_withheld:,.2f}",
                reference_number=reference_number
            )
            session.add(tax_event)
        
        # Update calculated fields
        self._update_current_equity_balance(session)
        
        return dist_event, tax_event


class FundUpdateMixin:
    """Mixin class for fund update and recalculation methods."""
    
    def _update_current_units_and_price(self, session):
        """Update current units and unit price for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            return
        
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
    
    def _update_current_equity_balance(self, session):
        """Update current equity balance based on fund type."""
        if self.tracking_type == FundType.NAV_BASED:
            # For NAV-based funds, use cost_of_units from the latest unit event
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
    
    def _update_average_equity_balance(self, session):
        """Update average equity balance."""
        if self.tracking_type == FundType.NAV_BASED:
            calculated_average = calculate_average_equity_balance_nav(self, session)
        else:
            calculated_average = calculate_average_equity_balance_cost(self, session)
        
        self.average_equity_balance = calculated_average
    
    def _update_is_active(self, session):
        """Update the fund's active status."""
        # Simple logic: fund is active if it has recent activity
        latest_event = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date.desc()).first()
        
        if latest_event:
            # Consider fund active if last event was within the last 2 years
            two_years_ago = date.today() - timedelta(days=730)
            self.is_active = latest_event.event_date >= two_years_ago
        else:
            self.is_active = False
    
    def _update_total_cost_basis(self, session):
        """Update total cost basis for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            return
        
        capital_movements = self.get_capital_movements(session=session)
        self._total_cost_basis = capital_movements['calls'] - capital_movements['returns']
    
    def recalculate_all_fields(self, session):
        """Recalculate all derived fields for the fund."""
        self._update_current_equity_balance(session)
        self._update_average_equity_balance(session)
        self._update_is_active(session)
        
        if self.tracking_type == FundType.NAV_BASED:
            self._update_current_units_and_price(session)
        else:
            self._update_total_cost_basis(session)
        
        session.commit()


# Add mixins to Fund class
Fund.__bases__ = (FundCreationMixin, FundUpdateMixin) + Fund.__bases__


__all__ = [
    'FundCreationMixin',
    'FundUpdateMixin',
] 