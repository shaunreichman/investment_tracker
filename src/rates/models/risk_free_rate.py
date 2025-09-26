"""
Risk Free Rate Models.

This module provides the RiskFreeRate model class, representing risk free rates in the system.
These rates are used to calculate IRRs for funds
The model handles only data persistence, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, UniqueConstraint

from src.shared.enums.shared_enums import Currency
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType
from src.shared.base import Base

class RiskFreeRate(Base):
    """
    Model representing risk free rates for different currencies over time.
    """
    __tablename__ = 'risk_free_rates'

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    currency = Column(Enum(Currency), nullable=False)  # (MANUAL) currency code (e.g., 'AUD', 'USD', 'EUR')
    date = Column(Date, nullable=False)  # (MANUAL) date of the rate
    rate = Column(Float, nullable=False)  # (MANUAL) risk-free rate as percentage (e.g., 4.5 for 4.5%)
    rate_type = Column(Enum(RiskFreeRateType), default=RiskFreeRateType.GOVERNMENT_BOND)  # (MANUAL) type of rate (e.g., 'government_bond', 'libor', 'sofr')
    source = Column(String(100))  # (MANUAL) source of the rate data
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('currency', 'date', 'rate_type', name='uq_risk_free_rate'),
    )
    
    def __repr__(self):
        return f"<RiskFreeRate(id={self.id}, currency='{self.currency}', date={self.date}, rate={self.rate}%)>"
    