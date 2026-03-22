"""
Bank Account Balance Model.

This module provides the BankAccountBalance model class, representing the balance of a bank account.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Float, Date, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Dict

from src.shared.enums.shared_enums import Currency
from src.shared.base import Base

class BankAccountBalance(Base):
    """Model representing the balance of a bank account."""

    __tablename__ = "bank_account_balances"

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    bank_account_id = Column(Integer, ForeignKey("bank_accounts.id"), nullable=False, index=True)  # (RELATIONSHIP) linked bank account
    currency = Column(Enum(Currency), nullable=False)  # (MANUAL) ISO-4217 currency code
    date = Column(Date, nullable=False)  # (MANUAL) date of the balance - must be the last day of the month
    
    balance_statement = Column(Float, nullable=False)  # (MANUAL) balance of the bank account from the statement
    balance_adjustment = Column(Float, nullable=False, default=0.0)  # (CALCULATED) balance adjustment based on fund event cash flows different to the fund event date
    balance_final = Column(Float, nullable=False)  # (CALCULATED) balance of the bank account after the adjustment

    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) last update timestamp

    # Relationships
    bank_account = relationship("BankAccount", back_populates="bank_account_balances")


    __table_args__ = (
        UniqueConstraint("bank_account_id", "currency", "date", name="uq_bank_account_balance_unique"),  # (SYSTEM) prevent duplicates for same bank account/currency/date
    )

    def __repr__(self) -> str:
        return f"<BankAccountBalance(id={self.id}, bank_account_id={self.bank_account_id}, currency={self.currency}, date={self.date}, balance_statement={self.balance_statement}, balance_adjustment={self.balance_adjustment}, balance_final={self.balance_final})>"

    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the bank account balance model.
        
        Returns:
            Dict[str, str]: Field classification for the bank account balance model
        """
        return {
            'id': 'SYSTEM',
            'bank_account_id': 'RELATIONSHIP',
            'currency': 'MANUAL',
            'date': 'MANUAL',
            'balance_statement': 'MANUAL',
            'balance_adjustment': 'CALCULATED',
            'balance_final': 'CALCULATED',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
        }