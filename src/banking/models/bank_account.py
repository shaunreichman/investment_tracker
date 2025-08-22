"""
Bank Account Model.

This module provides the BankAccount model class, representing an investor-owned bank account.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import Optional
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.base import Base


class BankAccount(Base):
    """Model representing an investor-owned bank account."""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)  # (MANUAL) owner entity
    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False, index=True)  # (MANUAL) linked bank
    account_name = Column(String(255), nullable=False)  # (MANUAL) human-readable account name/label
    account_number = Column(String(64), nullable=False)  # (MANUAL) account number stored as provided
    currency = Column(String(3), nullable=False)  # (MANUAL) ISO-4217 currency code
    is_active = Column(Boolean, nullable=False, default=True)  # (MANUAL) active status flag
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) last update timestamp

    __table_args__ = (
        UniqueConstraint("entity_id", "bank_id", "account_number", name="uq_bank_account_unique"),  # (SYSTEM) prevent duplicates for same owner/bank/number
    )

    # Relationships
    bank = relationship("Bank", back_populates="accounts")
    entity = relationship("Entity", back_populates="bank_accounts")

    def __repr__(self) -> str:
        return (
            f"<BankAccount(id={self.id}, entity_id={self.entity_id}, bank_id={self.bank_id}, "
            f"name='{self.account_name}', number='{self.account_number}', currency='{self.currency}')>"
        )

    # Domain methods
    @classmethod
    def create(
        cls,
        *,
        entity_id: int,
        bank_id: int,
        account_name: str,
        account_number: str,
        currency: str,
        is_active: bool = True,
        session=None,
    ) -> "BankAccount":
        """
        Create a new bank account using the service layer.
        
        This method maintains the exact same interface while delegating
        business logic to the BankAccountService for clean separation of concerns.
        """
        from src.banking.services.bank_account_service import BankAccountService
        
        service = BankAccountService()
        return service.create_bank_account(
            entity_id=entity_id,
            bank_id=bank_id,
            account_name=account_name,
            account_number=account_number,
            currency=currency,
            is_active=is_active,
            session=session
        )
