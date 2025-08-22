"""
Banking Models.

This module provides the banking-related model classes,
representing bank accounts and banking operations in the system.

The models now delegate business logic to dedicated services while maintaining
the exact same public interface for backward compatibility.
"""

from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import relationship

from src.shared.utils import with_session
from src.shared.base import Base


class Bank(Base):
    """Model representing a banking institution."""

    __tablename__ = "banks"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False)  # (MANUAL) bank name
    country = Column(String(2), nullable=False)  # (MANUAL) ISO 3166-1 alpha-2 country code
    swift_bic = Column(String(11), nullable=True)  # (MANUAL) optional SWIFT/BIC identifier

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

    @classmethod
    def get_by_unique(
        cls, *, entity_id: int, bank_id: int, account_number: str, session=None
    ) -> "BankAccount | None":
        """
        Get a bank account by unique combination using the service layer.
        
        This method maintains the exact same interface while delegating
        business logic to the BankAccountService for clean separation of concerns.
        """
        from src.banking.services.bank_account_service import BankAccountService
        
        service = BankAccountService()
        return service.get_bank_account_by_unique(
            entity_id=entity_id,
            bank_id=bank_id,
            account_number=account_number,
            session=session
        )



