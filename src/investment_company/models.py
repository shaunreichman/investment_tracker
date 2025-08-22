"""
Investment Company Models.

This module provides the investment company model class,
representing investment management companies in the system.
"""

from typing import Optional, List
from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.shared.utils import with_session, with_class_session
from src.fund.models import Fund
from src.fund.enums import FundStatus

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
    """Model representing an investment company/firm."""
    __tablename__ = 'investment_companies'
    
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    name = Column(String(255), nullable=False, unique=True)  # (MANUAL) investment company name
    description = Column(Text)  # (MANUAL) company description
    company_type = Column(String(100))  # (MANUAL) type of company (e.g., "Private Equity", "Venture Capital")
    business_address = Column(Text)  # (MANUAL) business address
    website = Column(String(255))  # (MANUAL) company website URL
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) creation timestamp
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) last update timestamp
    
    # Relationships
    funds = relationship("Fund", back_populates="investment_company", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="investment_company", cascade="all, delete-orphan")
    
    @classmethod
    def create(cls, name, description=None, website=None, 
               company_type=None, business_address=None, session=None):
        """
        Create a new investment company with validation and business logic.
        
        Args:
            name (str): Company name (must be unique)
            description (str, optional): Company description
            website (str, optional): Company website URL
            company_type (str, optional): Type of company (e.g., 'Private Equity', 'Venture Capital')
            business_address (str, optional): Business address
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            InvestmentCompany: The created investment company
            
        Raises:
            ValueError: If name is empty or company already exists
        """
        from src.investment_company.services import CompanyValidationService
        validation_service = CompanyValidationService()
        
        # Validate company data
        validation_errors = validation_service.validate_company_creation(
            name=name,
            description=description,
            website=website,
            company_type=company_type,
            business_address=business_address,
            session=session
        )
        
        if validation_errors:
            raise ValueError(f"Validation failed: {validation_errors}")
        
        name = name.strip()
        
        # Create the company
        company = cls(
            name=name,
            description=description,
            website=website,
            company_type=company_type,
            business_address=business_address
        )
        
        session.add(company)
        session.flush()  # Get the ID without committing
        
        return company
    
    def add_contact(self, name, title=None, direct_number=None, direct_email=None, notes=None, session=None):
        """
        Add a contact person to this investment company.
        
        Args:
            name (str): Contact person's name
            title (str, optional): Contact person's job title
            direct_number (str, optional): Direct phone number
            direct_email (str, optional): Direct email address
            notes (str, optional): Additional notes about the contact
            session (Session): Database session (required - managed by outermost backend layer)
        
        Returns:
            Contact: The created contact
        """
        from src.investment_company.services import ContactManagementService
        contact_service = ContactManagementService()
        return contact_service.add_contact(
            company=self,
            name=name,
            title=title,
            direct_number=direct_number,
            direct_email=direct_email,
            notes=notes,
            session=session
        )
    
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
    
    @classmethod
    def get_by_id(cls, company_id, session=None):
        """
        Get an investment company by ID.
        
        Args:
            company_id (int): Company ID
            session (Session): Database session
        
        Returns:
            InvestmentCompany or None: The investment company if found, None otherwise
        """
        return session.query(cls).filter(cls.id == company_id).first()
    
    @with_session
    def get_funds_with_summary(self, session=None):
        """
        Get all funds for this investment company with summary data.
        
        Args:
            session (Session): Database session
        
        Returns:
            list: List of fund summary data dictionaries
        """
        from src.investment_company.services import CompanyPortfolioService
        portfolio_service = CompanyPortfolioService()
        return portfolio_service.get_funds_with_summary(self, session)
    
    def get_total_funds_under_management(self, session):
        """Get the total number of funds managed by this investment company.
        
        Args:
            session: Database session
        
        Returns:
            int: Total number of funds
        """
        from src.investment_company.services import CompanyPortfolioService
        portfolio_service = CompanyPortfolioService()
        return portfolio_service.get_total_funds_under_management(self, session)
    
    def get_total_commitments(self, session):
        """Get the total commitments across all funds managed by this investment company.
        
        Args:
            session: Database session
        
        Returns:
            float: Total commitments across all funds
        """
        from src.investment_company.services import CompanyPortfolioService
        portfolio_service = CompanyPortfolioService()
        return portfolio_service.get_total_commitments(self, session)
    
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
        from src.investment_company.services import CompanyPortfolioService
        portfolio_service = CompanyPortfolioService()
        return portfolio_service.create_fund(
            company=self,
            entity=entity,
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

    @with_session
    def get_company_summary_data(self, session=None):
        """
        Get comprehensive company summary data for the Overview tab.
        
        This method provides portfolio summary, performance summary, and last activity
        data as specified in the Companies UI API contract.
        
        Returns:
            dict: Company summary data matching the API contract structure
        """
        from src.investment_company.services import CompanySummaryService
        summary_service = CompanySummaryService()
        return summary_service.get_company_summary_data(self, session)
    
    @with_session
    def get_company_performance_summary(self, session=None):
        """
        Get company performance summary for completed funds only.
        
        This method provides performance metrics specifically for completed funds
        where IRR calculations are available.
        
        Returns:
            dict: Performance summary data for completed funds
        """
        from src.investment_company.services import CompanySummaryService
        summary_service = CompanySummaryService()
        return summary_service.get_company_performance_summary(self, session) 