"""
Bank Account Model.

This module provides the BankAccount model class, representing an investor-owned bank account.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import Optional, Union
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from src.shared.base import Base
from src.banking.enums import Currency, AccountStatus


class BankAccount(Base):
    """Model representing an investor-owned bank account."""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)  # (MANUAL) owner entity
    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False, index=True)  # (MANUAL) linked bank
    account_name = Column(String(255), nullable=False)  # (MANUAL) human-readable account name/label
    account_number = Column(String(64), nullable=False)  # (MANUAL) account number stored as provided
    currency = Column(Enum(Currency), nullable=False)  # (MANUAL) ISO-4217 currency code
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.ACTIVE)  # (MANUAL) account status
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
        currency: Union[str, Currency],
        status: Union[bool, AccountStatus] = AccountStatus.ACTIVE,
        session=None,
    ) -> "BankAccount":
        """
        Create a new bank account using the service layer.
        
        This method maintains the exact same interface while delegating
        business logic to the BankAccountService for clean separation of concerns.
        
        Args:
            entity_id: Owner entity ID
            bank_id: Linked bank ID
            account_name: Human-readable account name/label
            account_number: Account number
            currency: Currency code (3-letter ISO) or Currency enum
            status: Account status (AccountStatus enum)
            session: Database session
        """
        from src.banking.services.bank_account_service import BankAccountService
        
        service = BankAccountService()
        return service.create_bank_account(
            entity_id=entity_id,
            bank_id=bank_id,
            account_name=account_name,
            account_number=account_number,
            currency=currency,
            status=status,
            session=session
        )
