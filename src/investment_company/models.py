"""
Investment company domain models.

This module contains the core investment company models including InvestmentCompany.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the Base from shared
from ..shared.base import Base

class InvestmentCompany(Base):
    """Model representing an investment company/firm."""
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    website = Column(String(255))
    contact_email = Column(String(255))
    contact_phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    funds = relationship("Fund", back_populates="investment_company", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<InvestmentCompany(id={self.id}, name='{self.name}')>"
    
    def get_total_funds_under_management(self, session):
        """Get the total number of funds managed by this investment company.
        
        Args:
            session: Database session
        
        Returns:
            int: Total number of funds
        """
        from .calculations import calculate_total_funds_under_management
        return calculate_total_funds_under_management(self, session)
    
    def get_total_commitments(self, session):
        """Get the total commitments across all funds managed by this investment company.
        
        Args:
            session: Database session
        
        Returns:
            float: Total commitments across all funds
        """
        from .calculations import calculate_total_commitments
        return calculate_total_commitments(self, session) 