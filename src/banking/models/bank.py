"""
Bank Model.

This module provides the Bank model class, representing a banking institution.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.base import Base


class Bank(Base):
    """Model representing a banking institution."""

    __tablename__ = "banks"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False)  # (MANUAL) bank name
    country = Column(String(2), nullable=False)  # (MANUAL) ISO 3166-1 alpha-2 country code
    swift_bic = Column(String(11), nullable=True)  # (MANUAL) optional SWIFT/BIC identifier
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) last update timestamp

    # Relationships
    accounts = relationship("BankAccount", back_populates="bank", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Bank(id={self.id}, name='{self.name}', country='{self.country}')>"

    # Domain methods
    @classmethod
    def create(
        cls,
        name: str,
        country: str,
        swift_bic: str | None = None,
        session=None,
    ) -> "Bank":
        """
        Create a new bank using the service layer.
        
        This method maintains the exact same interface while delegating
        business logic to the BankService for clean separation of concerns.
        """
        from src.banking.services.bank_service import BankService
        
        service = BankService()
        return service.create_bank(name, country, swift_bic, session)
