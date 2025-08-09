"""
Banking domain models.

This module contains models for Bank and BankAccount, which represent
investor-owned banking institutions and accounts used to fund cash-flow events.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ..shared.base import Base


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



