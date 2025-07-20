"""
Fund queries module.

This module contains methods for querying fund data and events.
These methods handle database operations and return data for analysis.
"""

from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_

from .models import Fund, FundEvent, EventType, FundType, DistributionType
from ..shared.utils import with_session


class FundQueryMixin:
    """Mixin class for fund query methods."""
    
    @with_session
    def get_events(self, event_types=None, start_date=None, end_date=None, session=None):
        """Get events for this fund with optional filtering."""
        query = session.query(FundEvent).filter(FundEvent.fund_id == self.id)
        
        if event_types:
            if isinstance(event_types, (list, tuple)):
                query = query.filter(FundEvent.event_type.in_(event_types))
            else:
                query = query.filter(FundEvent.event_type == event_types)
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_distributions_by_type(self, session, distribution_type=None, start_date=None, end_date=None):
        """Get distributions with optional filtering by type and date range."""
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        )
        
        if distribution_type:
            query = query.filter(FundEvent.distribution_type == distribution_type)
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_total_distributions(self, session, start_date=None, end_date=None):
        """Get total distributions for a period."""
        query = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DISTRIBUTION
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.scalar() or 0.0
    
    def get_taxable_distributions(self, session, start_date=None, end_date=None):
        """Get distributions that are taxable (not capital gains)."""
        return self.get_distributions_by_type(
            session, 
            distribution_type=DistributionType.INCOME,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_gross_distributions(self, session, start_date=None, end_date=None):
        """Get gross distributions (before tax) for a period."""
        return self.get_distributions_by_type(
            session,
            start_date=start_date,
            end_date=end_date
        )
    
    def get_total_tax_withheld(self, session, start_date=None, end_date=None):
        """Get total tax withheld for a period."""
        query = session.query(func.sum(FundEvent.amount)).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.scalar() or 0.0
    
    def get_capital_movements(self, session, start_date=None, end_date=None):
        """Get total capital movements (calls + returns) for a period."""
        if self.tracking_type == FundType.COST_BASED:
            # For cost-based funds: capital calls and returns
            calls = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.CAPITAL_CALL
            )
            
            returns = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.RETURN_OF_CAPITAL
            )
            
            if start_date:
                calls = calls.filter(FundEvent.event_date >= start_date)
                returns = returns.filter(FundEvent.event_date >= start_date)
            
            if end_date:
                calls = calls.filter(FundEvent.event_date <= end_date)
                returns = returns.filter(FundEvent.event_date <= end_date)
            
            total_calls = calls.scalar() or 0.0
            total_returns = returns.scalar() or 0.0
            
            return total_calls - total_returns
        else:
            # For NAV-based funds: unit purchases and sales
            purchases = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.UNIT_PURCHASE
            )
            
            sales = session.query(func.sum(FundEvent.amount)).filter(
                FundEvent.fund_id == self.id,
                FundEvent.event_type == EventType.UNIT_SALE
            )
            
            if start_date:
                purchases = purchases.filter(FundEvent.event_date >= start_date)
                sales = sales.filter(FundEvent.event_date >= start_date)
            
            if end_date:
                purchases = purchases.filter(FundEvent.event_date <= end_date)
                sales = sales.filter(FundEvent.event_date <= end_date)
            
            total_purchases = purchases.scalar() or 0.0
            total_sales = sales.scalar() or 0.0
            
            return total_purchases - total_sales
    
    def get_capital_calls(self, session, start_date=None, end_date=None):
        """Get capital calls for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            return []
        
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.CAPITAL_CALL
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_returns_of_capital(self, session, start_date=None, end_date=None):
        """Get returns of capital for cost-based funds."""
        if self.tracking_type != FundType.COST_BASED:
            return []
        
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.RETURN_OF_CAPITAL
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_unit_purchases(self, session, start_date=None, end_date=None):
        """Get unit purchases for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            return []
        
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.UNIT_PURCHASE
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_unit_sales(self, session, start_date=None, end_date=None):
        """Get unit sales for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            return []
        
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.UNIT_SALE
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_nav_updates(self, session, start_date=None, end_date=None):
        """Get NAV updates for NAV-based funds."""
        if self.tracking_type != FundType.NAV_BASED:
            return []
        
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.NAV_UPDATE
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_tax_payments(self, session, tax_payment_type=None, start_date=None, end_date=None):
        """Get tax payments with optional filtering."""
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        )
        
        if tax_payment_type:
            query = query.filter(FundEvent.tax_payment_type == tax_payment_type)
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_daily_risk_free_charges(self, session, start_date=None, end_date=None):
        """Get daily risk-free interest charges for real IRR calculations."""
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_eofy_debt_cost_events(self, session, start_date=None, end_date=None):
        """Get financial year debt cost events for real IRR calculations."""
        query = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id,
            FundEvent.event_type == EventType.EOFY_DEBT_COST
        )
        
        if start_date:
            query = query.filter(FundEvent.event_date >= start_date)
        
        if end_date:
            query = query.filter(FundEvent.event_date <= end_date)
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_fund_period(self, session):
        """Get the start and end dates of the fund based on events."""
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == self.id
        ).order_by(FundEvent.event_date).all()
        
        if not events:
            return None, None
        
        return events[0].event_date, events[-1].event_date
    
    def get_total_investment_duration_months(self, session):
        """Get the total investment duration in months."""
        start_date, end_date = self.get_fund_period(session)
        
        if not start_date or not end_date:
            return 0
        
        # Calculate months between dates
        months = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        
        # Adjust for day of month
        if end_date.day < start_date.day:
            months -= 1
        
        return max(0, months)


# Add mixin to Fund class
Fund.__bases__ = (FundQueryMixin,) + Fund.__bases__


__all__ = [
    'FundQueryMixin',
] 