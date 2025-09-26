"""
Fund Event Cash Flow Model.

This module provides the FundEventCashFlow model class, representing actual cash transfers linked to fund events.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, Text, Enum, Index, DateTime
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_event_cash_flow_enums import CashFlowDirection


class FundEventCashFlow(Base):
    """Model representing actual cash transfer(s) linked to a FundEvent via investor bank accounts.
    
    Responsibilities:
    - Data persistence and relationships
    - Basic validation and constraints
    - Cash flow record keeping
    
    Business Logic: Handled by fund event services
    Calculations: Managed by calculation services
    """
    
    __tablename__ = 'fund_event_cash_flows'
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_event_id = Column(Integer, ForeignKey('fund_events.id'), nullable=False, index=True)  # (SYSTEM) link to parent event
    bank_account_id = Column(Integer, ForeignKey('bank_accounts.id'), nullable=False, index=True)  # (MANUAL) account where the transfer occurred
    
    # Cash flow details
    direction = Column(Enum(CashFlowDirection), nullable=False)  # (SYSTEM) inflow/outflow from investor perspective
    transfer_date = Column(Date, nullable=False, index=True)  # (MANUAL) date of transaction on bank statement
    currency = Column(String(3), nullable=False)  # (MANUAL) ISO-4217; must equal BankAccount.currency
    amount = Column(Float, nullable=False)  # (MANUAL) transfer amount in currency
    reference = Column(String(255))  # (MANUAL) free-text bank reference
    description = Column(Text)  # (MANUAL) additional notes/description
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    fund_event = relationship("FundEvent", back_populates="cash_flows")
    bank_account = relationship("BankAccount")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_fund_event_cash_flows_fund_event_id', 'fund_event_id'),
        Index('idx_fund_event_cash_flows_bank_account_id', 'bank_account_id'),
        Index('idx_fund_event_cash_flows_transfer_date', 'transfer_date'),
        Index('idx_fund_event_cash_flows_currency', 'currency'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<FundEventCashFlow(id={self.id}, event_id={self.fund_event_id}, "
            f"acct_id={self.bank_account_id}, dir={self.direction.value}, "
            f"date={self.transfer_date}, {self.currency} {self.amount})>"
        )
    
    def validate_basic_constraints(self) -> bool:
        """Basic data validation only.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.fund_event_id:
            raise ValueError("Fund event ID is required")
        
        if not self.bank_account_id:
            raise ValueError("Bank account ID is required")
        
        if not self.direction:
            raise ValueError("Cash flow direction is required")
        
        if not self.transfer_date:
            raise ValueError("Transfer date is required")
        
        if not self.currency:
            raise ValueError("Currency is required")
        
        if not self.amount or self.amount <= 0:
            raise ValueError("Amount must be a positive number")
        
        if len(self.currency) != 3:
            raise ValueError("Currency must be 3 characters (ISO-4217)")
        
        return True
    
    @staticmethod
    def validate_currency_match(bank_account_currency: str, cash_flow_currency: str) -> bool:
        """Validate that bank account and cash flow currencies match.
        
        Args:
            bank_account_currency: Currency from bank account
            cash_flow_currency: Currency from cash flow
            
        Returns:
            bool: True if currencies match
            
        Raises:
            ValueError: If currencies don't match
        """
        if bank_account_currency.upper() != cash_flow_currency.upper():
            raise ValueError(
                f"Currency mismatch: bank account uses {bank_account_currency}, "
                f"cash flow uses {cash_flow_currency}"
            )
        return True
