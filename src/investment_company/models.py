"""
Investment company domain models.

This module contains the core investment company models including InvestmentCompany.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

# Import the Base from shared
from ..shared.base import Base
from ..shared.utils import with_session, with_class_session

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
    
    @classmethod
    @with_class_session
    def create(cls, name, description=None, website=None, contact_email=None, contact_phone=None, session=None):
        """
        Create a new investment company with validation and business logic.
        
        Args:
            name (str): Company name (must be unique)
            description (str, optional): Company description
            website (str, optional): Company website URL
            contact_email (str, optional): Contact email address
            contact_phone (str, optional): Contact phone number
            session (Session): Database session (managed by @with_session decorator)
        
        Returns:
            InvestmentCompany: The created investment company
            
        Raises:
            ValueError: If name is empty or company already exists
        """
        # Validation
        if not name or not name.strip():
            raise ValueError("Company name is required and cannot be empty")
        
        name = name.strip()
        
        # Check for existing company with same name
        existing = session.query(cls).filter(cls.name == name).first()
        if existing:
            raise ValueError(f"Investment company with name '{name}' already exists")
        
        # Create the company
        company = cls(
            name=name,
            description=description,
            website=website,
            contact_email=contact_email,
            contact_phone=contact_phone
        )
        
        session.add(company)
        session.flush()  # Get the ID without committing
        
        return company
    
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