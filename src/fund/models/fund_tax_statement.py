"""
Fund Tax Statement Model.

This module provides the tax statement model class, representing tax statements from funds for specific financial years.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, ForeignKey, Text, Index, UniqueConstraint, Enum
from sqlalchemy.orm import relationship
from typing import Dict

from src.shared.base import Base
# from src.fund.enums.fund_tax_statement_enums import FundTaxStatementFinancialYearType


class FundTaxStatement(Base):
    """Model representing tax statements from funds for specific financial years."""

    __tablename__ = 'fund_tax_statements'

    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (RELATIONSHIP) foreign key to fund
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)  # (RELATIONSHIP) foreign key to entity
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
    capital_gain_discount_applicable_flag = Column(Boolean, default=True)  # (MANUAL) Set to false by user to disable discount (eg if non resident and no discount available)

    # Debt cost tracking for real IRR calculations
    eofy_debt_interest_deduction_sum_of_daily_interest = Column(Float, default=0.0)  # (CALCULATED) total interest expense for the EOFY
    eofy_debt_interest_deduction_rate = Column(Float, default=0.0)  # (MANUAL) tax deduction rate for interest (e.g., 30.0 for 30%)
    eofy_debt_interest_deduction_total_deduction = Column(Float, default=0.0)  # (CALCULATED) calculated tax benefit from interest deduction
    
    # Additional fields
    accountant = Column(String(255))  # (MANUAL) name of fund's accountant who prepared the tax statement
    notes = Column(Text)  # (MANUAL) additional notes
    
    # Metadata
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


    def get_field_classification(self) -> Dict[str, str]:
        """
        Field classification for the fund tax statement model.
        
        Returns:
            Dict[str, str]: Field classification for the fund tax statement model
        """
        return {
            'id': 'SYSTEM',
            'fund_id': 'RELATIONSHIP',
            'entity_id': 'RELATIONSHIP',
            'financial_year': 'MANUAL',
            'financial_year_start_date': 'CALCULATED',
            'financial_year_end_date': 'CALCULATED',
            'tax_payment_date': 'HYBRID',
            'statement_date': 'MANUAL',
            'interest_income_amount': 'CALCULATED',
            'interest_income_tax_rate': 'MANUAL',
            'interest_tax_amount': 'CALCULATED',
            'interest_received_in_cash': 'MANUAL',
            'interest_receivable_this_fy': 'MANUAL',
            'interest_receivable_prev_fy': 'MANUAL',
            'interest_non_resident_withholding_tax_from_statement': 'MANUAL',
            'interest_non_resident_withholding_tax_already_withheld': 'CALCULATED',
            'dividend_franked_income_amount': 'HYBRID',
            'dividend_unfranked_income_amount': 'HYBRID',
            'dividend_franked_income_tax_rate': 'MANUAL',
            'dividend_unfranked_income_tax_rate': 'MANUAL',
            'dividend_franked_tax_amount': 'CALCULATED',
            'dividend_unfranked_tax_amount': 'CALCULATED',
            'dividend_franked_income_amount_from_tax_statement_flag': 'CALCULATED',
            'dividend_unfranked_income_amount_from_tax_statement_flag': 'CALCULATED',
            'capital_gain_income_amount': 'HYBRID',
            'capital_gain_income_tax_rate': 'MANUAL',
            'capital_gain_tax_amount': 'CALCULATED',
            'capital_gain_discount_amount': 'CALCULATED',
            'capital_gain_income_amount_from_tax_statement_flag': 'CALCULATED',
            'capital_gain_discount_applicable_flag': 'MANUAL',
            'eofy_debt_interest_deduction_sum_of_daily_interest': 'CALCULATED',
            'eofy_debt_interest_deduction_rate': 'MANUAL',
            'eofy_debt_interest_deduction_total_deduction': 'CALCULATED',
            'accountant': 'MANUAL',
            'notes': 'MANUAL',
            'created_at': 'SYSTEM',
            'updated_at': 'SYSTEM',
        }