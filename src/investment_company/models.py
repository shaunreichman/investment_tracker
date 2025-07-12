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
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False, unique=True)  # (MANUAL) investment company name
    description = Column(Text)  # (MANUAL) investment company description
    website = Column(String(255))  # (MANUAL) company website URL
    contact_email = Column(String(255))  # (MANUAL) contact email address
    contact_phone = Column(String(50))  # (MANUAL) contact phone number
    created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    funds = relationship("Fund", back_populates="investment_company", cascade="all, delete-orphan")
    
    @classmethod
    def create(cls, name, description=None, website=None, contact_email=None, contact_phone=None, session=None):
        """
        Create a new investment company with validation and business logic.
        
        Args:
            name (str): Company name (must be unique)
            description (str, optional): Company description
            website (str, optional): Company website URL
            contact_email (str, optional): Contact email address
            contact_phone (str, optional): Contact phone number
            session (Session): Database session (required - managed by outermost backend layer)
        
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
    
    @classmethod
    def get_by_name(cls, name, session=None):
        """
        Get an investment company by name.
        
        Args:
            name (str): Company name
            session (Session): Database session
        
        Returns:
            InvestmentCompany or None: The investment company if found, None otherwise
        """
        return session.query(cls).filter(cls.name == name).first()
    
    @classmethod
    def get_all(cls, session=None):
        """
        Get all investment companies.
        
        Args:
            session (Session): Database session
        
        Returns:
            list: List of all investment companies
        """
        return session.query(cls).all()
    
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
    
    @with_session
    def create_fund(self, entity, name, fund_type, tracking_type, 
                   currency="AUD", description=None, commitment_amount=None, 
                   expected_irr=None, expected_duration_months=None, session=None):
        """
        Create a new fund for this investment company.
        
        This method follows the direct object method pattern, consistent with how
        fund events work (e.g., fund.add_capital_call()). It encapsulates the fund
        creation logic and handles the relationship between the investment company
        and the fund.
        
        Args:
            entity (Entity): The entity that will invest in the fund
            name (str): Fund name
            fund_type (str): Type of fund (e.g., "Private Debt", "Equity")
            tracking_type (FundType): Tracking type (COST_BASED or NAV_BASED)
            currency (str): Currency code (default: "AUD")
            description (str, optional): Fund description
            commitment_amount (float, optional): Commitment amount for cost-based funds
            expected_irr (float, optional): Expected IRR percentage
            expected_duration_months (int, optional): Expected duration in months
            session (Session): Database session (managed by @with_session decorator)
        
        Returns:
            Fund: The created fund
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        from ..fund.models import Fund
        
        # Validate entity
        if entity is None:
            raise ValueError("Entity is required")
        
        # Create the fund using the domain method
        fund = Fund.create(
            investment_company_id=self.id,  # Use self.id
            entity_id=entity.id,           # Use entity.id
            name=name,
            fund_type=fund_type,
            tracking_type=tracking_type,
            currency=currency,
            description=description,
            commitment_amount=commitment_amount,
            expected_irr=expected_irr,
            expected_duration_months=expected_duration_months,
            session=session
        )
        
        return fund 