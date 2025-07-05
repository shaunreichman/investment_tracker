"""
Entity domain models.

This module contains the core entity models including Entity, InvestmentCompany, and RiskFreeRate.
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, date
import enum

# Import the Base from shared
from ..shared.base import Base


class EntityType(enum.Enum):
    """Enumeration for entity types."""
    INDIVIDUAL = "individual"
    COMPANY = "company"
    TRUST = "trust"
    PARTNERSHIP = "partnership"


class Entity(Base):
    """Model representing an investing entity (person or company).
    
    Relationships:
    - funds: All funds this entity has invested in.
    - risk_free_rates: Risk-free rates for this entity's currency.
    
    Business rules:
    - Each entity can have multiple funds.
    - Financial year calculation is based on entity type and jurisdiction.
    """
    __tablename__ = 'entities'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    entity_type = Column(Enum(EntityType), nullable=False, default=EntityType.INDIVIDUAL)
    tax_file_number = Column(String(20))  # Australian TFN or similar
    abn = Column(String(20))  # Australian Business Number or similar
    address = Column(Text)
    email = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="entity", lazy='selectin')
    risk_free_rates = relationship("RiskFreeRate", back_populates="entity", lazy='selectin')
    
    def __repr__(self):
        """Return a string representation of the Entity instance for debugging/logging."""
        return f"<Entity(id={self.id}, name='{self.name}', type={self.entity_type.value})>"
    
    def get_financial_year(self, target_date):
        """Get the financial year string for a given date.
        For Australian entities, financial year runs from July 1 to June 30.
        Returns format like '2022-23' for the year ending June 30, 2023.
        """
        if target_date.month >= 7:
            # July to December: financial year is current year + 1
            fy_start = target_date.year
            fy_end = target_date.year + 1
        else:
            # January to June: financial year is previous year + 1
            fy_start = target_date.year - 1
            fy_end = target_date.year
        
        return f"{fy_start}-{str(fy_end)[-2:]}"
    
    def get_financial_year_dates(self, financial_year):
        """Get the start and end dates for a financial year.
        Args:
            financial_year: String like '2022-23'
        Returns:
            tuple: (start_date, end_date) where end_date is exclusive
        """
        # Parse financial year like '2022-23'
        start_year = int(financial_year.split('-')[0])
        end_year = start_year + 1
        
        start_date = date(start_year, 7, 1)  # July 1
        end_date = date(end_year, 7, 1)      # July 1 (exclusive)
        
        return start_date, end_date


class InvestmentCompany(Base):
    """Model representing an investment company that manages funds.
    
    Relationships:
    - funds: All funds managed by this company.
    
    Business rules:
    - Each investment company can manage multiple funds.
    - Company details are used for reporting and documentation.
    """
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    abn = Column(String(20))  # Australian Business Number or similar
    address = Column(Text)
    email = Column(String(255))
    phone = Column(String(50))
    website = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="investment_company", lazy='selectin')
    
    def __repr__(self):
        """Return a string representation of the InvestmentCompany instance for debugging/logging."""
        return f"<InvestmentCompany(id={self.id}, name='{self.name}')>"


class RiskFreeRate(Base):
    """Model representing risk-free interest rates for different currencies and dates.
    
    Relationships:
    - entity: The entity this rate applies to (for currency context).
    
    Business rules:
    - Rates are used for real IRR calculations.
    - Rates are typically updated monthly or quarterly.
    - Each entity can have multiple rates for different dates.
    """
    __tablename__ = 'risk_free_rates'
    
    id = Column(Integer, primary_key=True)
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False, index=True)
    currency = Column(String(10), nullable=False, default="AUD")  # Currency code
    rate_date = Column(Date, nullable=False, index=True)  # Date the rate applies from
    rate = Column(Float, nullable=False)  # Rate as a percentage (e.g., 4.5 for 4.5%)
    description = Column(Text)  # Description of the rate (e.g., "RBA Cash Rate")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    entity = relationship("Entity", back_populates="risk_free_rates", lazy='selectin')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('entity_id', 'currency', 'rate_date', name='unique_entity_currency_date'),
    )
    
    def __repr__(self):
        """Return a string representation of the RiskFreeRate instance for debugging/logging."""
        return f"<RiskFreeRate(id={self.id}, entity_id={self.entity_id}, currency='{self.currency}', date={self.rate_date}, rate={self.rate}%)>" 