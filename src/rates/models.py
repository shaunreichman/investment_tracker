"""
Rates domain models.

This module contains market data models including RiskFreeRate and future rate types.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date, UniqueConstraint
from datetime import datetime

# Import the Base from shared
from ..shared.base import Base

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
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    currency = Column(String(10), nullable=False)  # (MANUAL) currency code (e.g., 'AUD', 'USD', 'EUR')
    rate_date = Column(Date, nullable=False)  # (MANUAL) date of the rate
    rate = Column(Float, nullable=False)  # (MANUAL) risk-free rate as percentage (e.g., 4.5 for 4.5%)
    rate_type = Column(String(50), default='government_bond')  # (MANUAL) type of rate (e.g., 'government_bond', 'libor', 'sofr')
    source = Column(String(100))  # (MANUAL) source of the rate data
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) timestamp when record was created
    
    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('currency', 'rate_date', 'rate_type', name='uq_risk_free_rate'),
    )
    
    def __repr__(self):
        return f"<RiskFreeRate(id={self.id}, currency='{self.currency}', date={self.rate_date}, rate={self.rate}%)>"
    
    @classmethod
    def create(cls, currency, rate_date, rate, rate_type='government_bond', source=None, session=None):
        """
        Create a new risk-free rate.
        
        Args:
            currency (str): Currency code (e.g., 'AUD', 'USD', 'EUR')
            rate_date (date): Date the rate applies to
            rate (float): Risk-free rate as percentage (e.g., 4.5 for 4.5%)
            rate_type (str): Type of rate (e.g., 'government_bond', 'libor', 'sofr')
            source (str, optional): Source of the rate data
            session (Session, optional): Database session
        
        Returns:
            RiskFreeRate: The created risk-free rate
        """
        risk_free_rate = cls(
            currency=currency,
            rate_date=rate_date,
            rate=rate,
            rate_type=rate_type,
            source=source
        )
        
        if session:
            session.add(risk_free_rate)
            session.commit()
        
        return risk_free_rate
    
    @classmethod
    def get_for_currency(cls, currency, session, start_date=None, end_date=None):
        """
        Get risk-free rates for a specific currency within an optional date range.
        
        Args:
            currency (str): Currency code
            session (Session): Database session
            start_date (date, optional): Start date for filtering
            end_date (date, optional): End date for filtering
        
        Returns:
            list: List of RiskFreeRate objects, sorted by date
        """
        query = session.query(cls).filter(cls.currency == currency)
        
        if start_date:
            query = query.filter(cls.rate_date >= start_date)
        
        if end_date:
            query = query.filter(cls.rate_date <= end_date)
        
        return query.order_by(cls.rate_date).all()
    
    @classmethod
    def get_all(cls, session, currency=None, start_date=None, end_date=None):
        """
        Get all risk-free rates with optional filtering.
        
        Args:
            session (Session): Database session
            currency (str, optional): Currency code to filter by
            start_date (date, optional): Start date for filtering
            end_date (date, optional): End date for filtering
        
        Returns:
            list: List of RiskFreeRate objects, sorted by currency and date
        """
        query = session.query(cls)
        
        if currency:
            query = query.filter(cls.currency == currency)
        
        if start_date:
            query = query.filter(cls.rate_date >= start_date)
        
        if end_date:
            query = query.filter(cls.rate_date <= end_date)
        
        return query.order_by(cls.currency, cls.rate_date).all()
    
    @staticmethod
    def get_rate_for_date(target_date, risk_free_rates):
        """Get the risk-free rate for a specific date from a list of rates.
        
        Args:
            target_date (date): The date to find a rate for
            risk_free_rates (list): List of RiskFreeRate objects, sorted by date
        
        Returns:
            float or None: The risk-free rate as a percentage, or None if not found
        """
        from .calculations import get_risk_free_rate_for_date
        return get_risk_free_rate_for_date(target_date, risk_free_rates) 