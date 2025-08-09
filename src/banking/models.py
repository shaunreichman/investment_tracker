"""
Banking domain models.

This module contains models for Bank and BankAccount, which represent
investor-owned banking institutions and accounts used to fund cash-flow events.
"""

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from ..shared.utils import with_session

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

    # Domain methods
    @classmethod
    @with_session
    def create(
        cls,
        name: str,
        country: str,
        swift_bic: str | None = None,
        session=None,
    ) -> "Bank":
        if not name or not name.strip():
            raise ValueError("Bank name is required and cannot be empty")
        if not country or len(country) != 2:
            raise ValueError("country must be a 2-letter ISO code")
        bank = cls(name=name.strip(), country=country.upper(), swift_bic=swift_bic)
        session.add(bank)
        session.flush()
        return bank


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
    @with_session
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
        if not entity_id:
            raise ValueError("entity_id is required")
        if not bank_id:
            raise ValueError("bank_id is required")
        if not account_name or not account_name.strip():
            raise ValueError("account_name is required")
        if not account_number or not account_number.strip():
            raise ValueError("account_number is required")
        if not currency or len(currency) != 3:
            raise ValueError("currency must be a 3-letter ISO-4217 code")

        # Enforce uniqueness: (entity_id, bank_id, account_number)
        existing = (
            session.query(cls)
            .filter(
                cls.entity_id == entity_id,
                cls.bank_id == bank_id,
                cls.account_number == account_number.strip(),
            )
            .first()
        )
        if existing:
            raise ValueError("Bank account already exists for this entity/bank/account_number")

        acct = cls(
            entity_id=entity_id,
            bank_id=bank_id,
            account_name=account_name.strip(),
            account_number=account_number.strip(),
            currency=currency.upper(),
            is_active=bool(is_active),
        )
        session.add(acct)
        session.flush()
        return acct

    @classmethod
    @with_session
    def get_by_unique(
        cls, *, entity_id: int, bank_id: int, account_number: str, session=None
    ) -> "BankAccount | None":
        return (
            session.query(cls)
            .filter(
                cls.entity_id == entity_id,
                cls.bank_id == bank_id,
                cls.account_number == account_number,
            )
            .first()
        )



