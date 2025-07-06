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