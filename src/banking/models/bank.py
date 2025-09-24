"""
Bank Model.

This module provides the Bank model class, representing a banking institution.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from sqlalchemy import Column, Integer, String, DateTime, Enum, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.base import Base
from src.banking.enums.bank_enums import BankType, BankStatus
from src.shared.enums.shared_enums import Country


class Bank(Base):
    """Model representing a banking institution."""

    __tablename__ = "banks"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False)  # (MANUAL) bank name
    country = Column(Enum(Country), nullable=False)  # (MANUAL) ISO 3166-1 alpha-2 country code
    bank_type = Column(Enum(BankType), nullable=True)  # (MANUAL) bank type
    swift_bic = Column(String(11), nullable=True)  # (MANUAL) optional SWIFT/BIC identifier
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) last update timestamp

    status = Column(Enum(BankStatus), nullable=True)  # (CALCULATED) bank status

    current_number_of_bank_accounts = Column(Integer, default=0)  # (CALCULATED) total number of bank accounts
    current_balance_in_bank_accounts = Column(Float, default=0.0)  # (CALCULATED) total balance of all bank accounts

    # Relationships
    accounts = relationship("BankAccount", back_populates="bank", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Bank(id={self.id}, name='{self.name}', country='{self.country}', bank_type='{self.bank_type}')>"