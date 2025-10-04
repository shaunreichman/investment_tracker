"""
FX Rate Models.

This module provides the FxRate model class, representing FX rates in the system.
These rates are used to calculate IRRs for funds
The model handles only data persistence, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, DateTime, Date, Enum, UniqueConstraint
from typing import Dict

from src.shared.enums.shared_enums import Currency
from src.shared.base import Base

class FxRate(Base):
    """
    Model representing FX rates for different currencies over time.
    """
    __tablename__ = 'fx_rates'

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    from_currency = Column(Enum(Currency), nullable=False)  # (MANUAL) currency code (e.g., 'AUD', 'USD', 'EUR')
    to_currency = Column(Enum(Currency), nullable=False)  # (MANUAL) currency code (e.g., 'AUD', 'USD', 'EUR')
    date = Column(Date, nullable=False)  # (MANUAL) date of the rate
    fx_rate = Column(Float, nullable=False)  # (MANUAL) FX rate from_currency to to_currency
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated

    # Composite unique constraint
    __table_args__ = (
        UniqueConstraint('from_currency', 'to_currency', 'date', name='uq_fx_rate'),
    )
    
    def __repr__(self):
        return f"<FxRate(id={self.id}, from_currency='{self.from_currency}', to_currency='{self.to_currency}', date={self.date}, fx_rate={self.fx_rate})>"
    
    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the FX rate model.
        
        Returns:
            Dict[str, str]: Field classification for the FX rate model
        """
        return {
            'id': 'SYSTEM',
            'from_currency': 'MANUAL',
            'to_currency': 'MANUAL',
            'date': 'MANUAL',
            'fx_rate': 'MANUAL',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
        }
    
    