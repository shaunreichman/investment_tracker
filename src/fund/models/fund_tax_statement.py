"""
Fund Tax Statement Model.

This module provides the tax statement model class,
representing tax statements from funds for specific financial years.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Index, UniqueConstraint, Enum
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_tax_statement_enums import FundTaxStatementFinancialYearType


class FundTaxStatement(Base):
    """Model representing tax statements from funds for specific financial years."""

    __tablename__ = 'fund_tax_statements'

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (MANUAL) foreign key to fund
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)  # (MANUAL) foreign key to entity
    financial_year = Column(String(4), nullable=False, index=True)  # (MANUAL) financial year (e.g., "2023-24")
    financial_year_start_date = Column(Date, nullable=False)  # (CALCULATED) start date of the financial year
    financial_year_end_date = Column(Date, nullable=False)  # (CALCULATED) end date of the financial year

    tax_payment_date = Column(Date)  # (HYBRID) date when additional tax is due (defaults to FY end)
    statement_date = Column(Date)  # (MANUAL) date the tax statement was issued
    
    # --------- INCOME ---------

    # --------- Interest income ---------
    interest_income_amount = Column(Float, default=0.0)  # (CALCULATED) calculated from manual interest fields
    interest_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined interest tax rate (%)
    interest_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated from interest income and rate
    interest_received_in_cash = Column(Float, default=0.0)  # (MANUAL) actual cash flow received this FY
    interest_receivable_this_fy = Column(Float, default=0.0)  # (MANUAL) accounting income for this FY, not yet received
    interest_receivable_prev_fy = Column(Float, default=0.0)  # (MANUAL) accounting income from prev FY, received this FY
    interest_non_resident_withholding_tax_from_statement = Column(Float, default=0.0)  # (MANUAL) withholding tax as reported
    interest_non_resident_withholding_tax_already_withheld = Column(Float, default=0.0)  # (CALCULATED) sum of TAX_PAYMENT events

    # --------- Dividend income ---------
    dividend_franked_income_amount = Column(Float, default=0.0)  # (HYBRID) manual or calculated franked dividends
    dividend_unfranked_income_amount = Column(Float, default=0.0)  # (HYBRID) manual or calculated unfranked dividends
    dividend_franked_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined franked dividend tax rate (%)
    dividend_unfranked_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined unfranked dividend tax rate (%)
    dividend_franked_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated franked dividend tax amount
    dividend_unfranked_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated unfranked dividend tax amount
    dividend_franked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # (CALCULATED) true if amount comes from tax statement
    dividend_unfranked_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # (CALCULATED) true if amount comes from tax statement

    # --------- Capital gain income ---------
    capital_gain_income_amount = Column(Float, default=0.0)  # (HYBRID) manual or calculated capital gains
    capital_gain_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) manually defined capital gain tax rate (%)
    capital_gain_tax_amount = Column(Float, default=0.0)  # (CALCULATED) calculated capital gain tax amount
    capital_gain_discount_amount = Column(Float, default=0.0)  # (CALCULATED) calculated capital gain discount (50% for AU holdings > 12 months)
    capital_gain_income_amount_from_tax_statement_flag = Column(Boolean, default=False)  # (CALCULATED) true if amount comes from tax statement

    # Debt cost tracking for real IRR calculations
    eofy_debt_interest_deduction_sum_of_daily_interest = Column(Float, default=0.0)  # (CALCULATED) total interest expense for the EOFY
    eofy_debt_interest_deduction_rate = Column(Float, default=0.0)  # (MANUAL) tax deduction rate for interest (e.g., 30.0 for 30%)
    eofy_debt_interest_deduction_total_deduction = Column(Float, default=0.0)  # (CALCULATED) calculated tax benefit from interest deduction
    
    # Tax status
    non_resident = Column(Boolean, default=False)  # (MANUAL) whether entity was non-resident for tax purposes in this FY
    
    # Additional fields
    accountant = Column(String(255))  # (MANUAL) name of fund's accountant who prepared the tax statement
    notes = Column(Text)  # (MANUAL) additional notes
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    fund = relationship("Fund", back_populates="tax_statements", lazy='selectin')
    entity = relationship("Entity", back_populates="tax_statements", lazy='selectin')
    
    # Composite unique constraint to ensure one statement per fund/entity/financial year
    __table_args__ = (
        UniqueConstraint('fund_id', 'entity_id', 'financial_year', name='unique_tax_statement'),
        # Performance indexes for common queries
        Index('idx_tax_statements_fund_financial_year', 'fund_id', 'financial_year'),
        Index('idx_tax_statements_entity_financial_year', 'entity_id', 'financial_year'),
    )

    def __repr__(self):
        """Return a string representation of the FundTaxStatement instance for debugging/logging."""
        return f"<FundTaxStatement(id={self.id}, fund_id={self.fund_id}, entity_id={self.entity_id}, fy={self.financial_year})>"