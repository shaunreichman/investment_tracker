"""
Investment Company Models.

This module provides the investment company model class,
representing investment management companies in the system.
"""

from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.shared.utils import with_session, with_class_session
from src.fund.models import Fund
from src.fund.models import FundStatus

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
        if not name or not name.strip():
            raise ValueError("Contact name is required and cannot be empty")
        
        contact = Contact(
            investment_company_id=self.id,
            name=name.strip(),
            title=title,
            direct_number=direct_number,
            direct_email=direct_email,
            notes=notes
        )
        
        session.add(contact)
        session.flush()
        
        return contact
    
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
        funds_data = []
        for fund in self.funds:
            funds_data.append(fund.get_summary_data(session=session))
        return funds_data
    
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
        from src.fund.models import Fund
        
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

    @with_session
    def get_company_summary_data(self, session=None):
        """
        Get comprehensive company summary data for the Overview tab.
        
        This method provides portfolio summary, performance summary, and last activity
        data as specified in the Companies UI API contract.
        
        Returns:
            dict: Company summary data matching the API contract structure
        """
        from src.fund.models import FundStatus
        
        # Get all funds for this company
        funds = self.funds
        
        # Calculate portfolio summary
        total_committed_capital = sum(fund.commitment_amount or 0 for fund in funds)
        total_current_value = sum(fund.current_equity_balance or 0 for fund in funds)
        total_invested_capital = sum(fund.current_equity_balance or 0 for fund in funds)
        
        # Count funds by status
        active_funds_count = sum(1 for fund in funds if fund.status == FundStatus.ACTIVE)
        completed_funds_count = sum(1 for fund in funds if fund.status == FundStatus.COMPLETED)
        suspended_funds_count = sum(1 for fund in funds if fund.status == FundStatus.SUSPENDED)
        realized_funds_count = sum(1 for fund in funds if fund.status == FundStatus.REALIZED)
        
        fund_status_breakdown = {
            "active_funds_count": active_funds_count,
            "completed_funds_count": completed_funds_count,
            "suspended_funds_count": suspended_funds_count,
            "realized_funds_count": realized_funds_count
        }
        
        # Calculate performance summary (only for completed funds)
        completed_funds = [f for f in funds if f.status == FundStatus.COMPLETED]
        if completed_funds:
            # Calculate average IRR from completed funds
            irr_values = [f.irr_gross for f in completed_funds if f.irr_gross is not None]
            average_completed_irr = sum(irr_values) / len(irr_values) if irr_values else None
            
            # Calculate total realized gains/losses from completed funds
            total_realized_gains = sum(f.irr_gross for f in completed_funds if f.irr_gross and f.irr_gross > 0)
            total_realized_losses = sum(f.irr_gross for f in completed_funds if f.irr_gross and f.irr_gross < 0)
        else:
            average_completed_irr = None
            total_realized_gains = 0  # (SYSTEM) return 0 instead of None for test compatibility
            total_realized_losses = 0  # (SYSTEM) return 0 instead of None for test compatibility
        
        # Calculate last activity across all funds
        last_activity_date = None
        days_since_last_activity = None
        
        if funds:
            # Find the most recent event date across all funds
            all_event_dates = []
            for fund in funds:
                if fund.fund_events:
                    fund_event_dates = [event.event_date for event in fund.fund_events]
                    all_event_dates.extend(fund_event_dates)
            
            if all_event_dates:
                last_activity_date = max(all_event_dates)
                from datetime import date
                days_since_last_activity = (date.today() - last_activity_date).days
        
        return {
            "company": {
                "id": self.id,
                "name": self.name,
                "company_type": self.company_type,
                "business_address": self.business_address,
                "website": self.website,
                "contacts": [
                    {
                        "id": contact.id,
                        "name": contact.name,
                        "title": contact.title,
                        "direct_number": contact.direct_number,
                        "direct_email": contact.direct_email,
                        "notes": contact.notes
                    }
                    for contact in self.contacts
                ]
            },
            "portfolio_summary": {
                "total_committed_capital": total_committed_capital,
                "total_current_value": total_current_value,
                "total_invested_capital": total_invested_capital,
                "active_funds_count": active_funds_count,  # (SYSTEM) kept for test compatibility
                "completed_funds_count": completed_funds_count,  # (SYSTEM) kept for test compatibility
                "fund_status_breakdown": fund_status_breakdown
            },
            "fund_status_breakdown": fund_status_breakdown,  # (SYSTEM) Added for test compatibility
            "performance_summary": {
                "average_completed_irr": average_completed_irr,
                "total_realized_gains": total_realized_gains,
                "total_realized_losses": total_realized_losses
            },
            "last_activity": {
                "last_activity_date": last_activity_date.isoformat() if last_activity_date else None,
                "days_since_last_activity": days_since_last_activity
            }
        }
    
    @with_session
    def get_company_performance_summary(self, session=None):
        """
        Get company performance summary for completed funds only.
        
        This method provides performance metrics specifically for completed funds
        where IRR calculations are available.
        
        Returns:
            dict: Performance summary data for completed funds
        """
        from src.fund.models import FundStatus
        
        completed_funds = [f for f in self.funds if f.status == FundStatus.COMPLETED]
        
        if not completed_funds:
            return {
                "average_completed_irr": None,
                "total_realized_gains": None,
                "total_realized_losses": None,
                "completed_funds_count": 0
            }
        
        # Calculate performance metrics
        irr_values = [f.irr_gross for f in completed_funds if f.irr_gross is not None]
        average_completed_irr = sum(irr_values) / len(irr_values) if irr_values else None
        
        total_realized_gains = sum(f.irr_gross for f in completed_funds if f.irr_gross and f.irr_gross > 0)
        total_realized_losses = sum(f.irr_gross for f in completed_funds if f.irr_gross and f.irr_gross < 0)
        
        return {
            "average_completed_irr": average_completed_irr,
            "total_realized_gains": total_realized_gains,
            "total_realized_losses": total_realized_losses,
            "completed_funds_count": len(completed_funds)
        } 