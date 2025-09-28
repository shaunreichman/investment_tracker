"""
Investment Company Model.

This module provides the InvestmentCompany model class representing investment companies which manage funds.
The model handles only data persistence, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, Index, Float, Date
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.investment_company.enums.company_enums import CompanyType, CompanyStatus

class InvestmentCompany(Base):
    """
    Model representing an investment company which manages funds.
    """
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False)  # (MANUAL) investment company name
    description = Column(Text, nullable=True)  # (MANUAL) company description
    company_type = Column(Enum(CompanyType), nullable=True)  # (MANUAL) type of company using CompanyType enum
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
    # Company information
    business_address = Column(Text, nullable=True)  # (MANUAL) business address
    website = Column(String(255), nullable=True)  # (MANUAL) company website URL

    # Fund Information
    total_funds = Column(Integer, default=0)  # (CALCULATED) total number of funds
    total_funds_active = Column(Integer, default=0)  # (CALCULATED) total number of active funds
    total_funds_completed = Column(Integer, default=0)  # (CALCULATED) total number of completed funds
    total_funds_realized = Column(Integer, default=0)  # (CALCULATED) total number of realized funds
    
    # Equity storage fields (CALCULATED)
    total_commitment_amount = Column(Float, default=0.0)  # (CALCULATED) total commitment amount from funds
    current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital movements
    average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance

    # IRR storage fields (CALCULATED)
    completed_irr_gross = Column(Float, nullable=True)  # (CALCULATED) Completed gross IRR only of realized/completed funds
    completed_irr_after_tax = Column(Float, nullable=True)  # (CALCULATED) Completed after-tax IRR only of realized/completed funds
    completed_irr_real = Column(Float, nullable=True)  # (CALCULATED) Completed real IRR only of realized/completed funds

    # Profitability storage fields (CALCULATED)
    pnl = Column(Float, default=0.0)  # (CALCULATED) PNL
    realized_pnl = Column(Float, default=0.0)  # (CALCULATED) Realized PNL
    unrealized_pnl = Column(Float, default=0.0)  # (CALCULATED) Unrealized PNL
    realized_pnl_capital_gain = Column(Float, default=0.0)  # (CALCULATED) Realized Capital Gain PNL
    unrealized_pnl_capital_gain = Column(Float, default=0.0)  # (CALCULATED) Unrealized Capital Gain PNL
    realized_pnl_dividend = Column(Float, default=0.0)  # (CALCULATED) Realized Dividend PNL
    realized_pnl_interest = Column(Float, default=0.0)  # (CALCULATED) Realized Interest PNL
    realized_pnl_distribution = Column(Float, default=0.0)  # (CALCULATED) Realized Distribution PNL

    # Additional information
    status = Column(Enum(CompanyStatus), nullable=True)  # (CALCULATED) company status using CompanyStatus enum
    start_date = Column(Date, nullable=True)  # (CALCULATED) company start date
    end_date = Column(Date, nullable=True)  # (CALCULATED) company end date
    current_duration = Column(Integer, nullable=True)  # (CALCULATED) current company duration in months based on status

    # Relationships
    funds = relationship("Fund", back_populates="investment_company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="investment_company", cascade="all, delete-orphan")
    
    # Critical indexes for production performance
    __table_args__ = (
        # Foreign key indexes for JOIN performance
        Index('idx_investment_companies_company_type', 'company_type'),
        Index('idx_investment_companies_status', 'status'),
        # Composite indexes for common query patterns
        Index('idx_investment_companies_type_status', 'company_type', 'status'),
        Index('idx_investment_companies_name_status', 'name', 'status'),
    )
    
    def __repr__(self):
        return f"<InvestmentCompany(id={self.id}, name='{self.name}', company_type={self.company_type.value if self.company_type else None}, status={self.status.value})>"
