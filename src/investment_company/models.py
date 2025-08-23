"""
Investment Company Models.

This module provides the investment company model classes,
representing investment management companies in the system.

Models are now pure data containers with no business logic.
All business logic has been moved to dedicated services.
"""

from typing import Optional, List
from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.models import Fund
from src.fund.enums import FundStatus
from src.investment_company.enums import CompanyType, CompanyStatus

class Contact(Base):
    """Model representing a contact person at an investment company."""
    __tablename__ = 'contacts'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (SYSTEM) foreign key to investment company
    name = Column(String(255), nullable=False)  # (MANUAL) contact person's name
    title = Column(String(255))  # (MANUAL) contact person's job title
    direct_number = Column(String(50))  # (MANUAL) direct phone number
    direct_email = Column(String(255))  # (MANUAL) direct email address
    notes = Column(Text)  # (MANUAL) additional notes about the contact
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="contacts")

class InvestmentCompany(Base):
    """Model representing an investment company/firm.
    
    This is now a pure data container with no business logic.
    All business logic has been moved to dedicated services.
    
    Database Constraints:
    - company_type: Enum constraint using CompanyType enum
    - status: Enum constraint using CompanyStatus enum with default ACTIVE
    """
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False, unique=True)  # (MANUAL) investment company name
    description = Column(Text)  # (MANUAL) company description
    company_type = Column(Enum(CompanyType), nullable=True)  # (MANUAL) type of company using CompanyType enum
    status = Column(Enum(CompanyStatus), default=CompanyStatus.ACTIVE, nullable=False)  # (CALCULATED) company status using CompanyStatus enum
    business_address = Column(Text)  # (MANUAL) business address
    website = Column(String(255))  # (MANUAL) company website URL
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
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