"""
Bank Account Model.

This module provides the BankAccount model class, representing an investor-owned bank account.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Enum, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict

from src.shared.base import Base
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus
from src.shared.enums.shared_enums import Currency


class BankAccount(Base):
    """Model representing an investor-owned bank account."""

    __tablename__ = "bank_accounts"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    entity_id = Column(Integer, ForeignKey("entities.id"), nullable=False, index=True)  # (RELATIONSHIP) owner entity
    bank_id = Column(Integer, ForeignKey("banks.id"), nullable=False, index=True)  # (RELATIONSHIP) linked bank
    account_name = Column(String(255), nullable=False)  # (MANUAL) human-readable account name/label
    account_number = Column(String(64), nullable=False)  # (MANUAL) account number stored as provided
    currency = Column(Enum(Currency), nullable=False)  # (MANUAL) ISO-4217 currency code
    account_type = Column(Enum(BankAccountType), nullable=True)  # (MANUAL) account type
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) last update timestamp

    status = Column(Enum(BankAccountStatus), nullable=True)  # (CALCULATED) account status
    current_balance = Column(Float, default=0.0)  # (CALCULATED) current balance of the account in the currency of the account

    __table_args__ = (
        UniqueConstraint("entity_id", "bank_id", "account_number", name="uq_bank_account_unique"),  # (SYSTEM) prevent duplicates for same owner/bank/number
        UniqueConstraint("bank_id", "account_number", name="uq_bank_account_number_unique"),  # (SYSTEM) prevent duplicate account numbers across all entities at same bank
    )

    # Relationships
    bank = relationship("Bank", back_populates="bank_accounts")
    entity = relationship("Entity", back_populates="bank_accounts")
    bank_account_balances = relationship("BankAccountBalance", back_populates="bank_account")

    def __repr__(self) -> str:
        return (
            f"<BankAccount(id={self.id}, entity_id={self.entity_id}, bank_id={self.bank_id}, "
            f"name='{self.account_name}', number='{self.account_number}', currency='{self.currency}', type='{self.account_type}')>"
        )


    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the bank account model.
        
        Returns:
            Dict[str, str]: Field classification for the bank account model
        """
        return {
            'id': 'SYSTEM',
            'entity_id': 'RELATIONSHIP',
            'bank_id': 'RELATIONSHIP',
            'account_name': 'MANUAL',
            'account_number': 'MANUAL',
            'currency': 'MANUAL',
            'account_type': 'MANUAL',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
            'status': 'CALCULATED',
            'current_balance': 'CALCULATED',
        }