"""
Company Service.

This service provides the main business logic layer for investment company operations,
coordinating between the API controllers and the domain services.

Key responsibilities:
- Company CRUD operations coordination
- Service orchestration
- Business logic coordination
- API layer integration
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.repositories import CompanyRepository, ContactRepository
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.enums import CompanyType, CompanyStatus


class CompanyService:
    """
    Main service layer for investment company operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    company-related business operations.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        contact_repository (ContactRepository): Repository for contact data access
        portfolio_service (CompanyPortfolioService): Service for portfolio operations
        summary_service (CompanySummaryService): Service for summary calculations
        contact_service (ContactManagementService): Service for contact management
        validation_service (CompanyValidationService): Service for validation
    """
    
    def __init__(self):
        """Initialize the company service with all required components."""
        self.company_repository = CompanyRepository()
        self.contact_repository = ContactRepository()
        self.portfolio_service = CompanyPortfolioService()
        self.summary_service = CompanySummaryService()
        self.contact_service = ContactManagementService()
        self.validation_service = CompanyValidationService()
    
    def create_company(self, name: str, description: str = None, website: str = None, 
                      company_type: str = None, business_address: str = None, 
                      status: str = None, session: Session = None) -> InvestmentCompany:
        """
        Create a new investment company.
        
        Args:
            name: Company name (required)
            description: Company description (optional)
            website: Company website URL (optional)
            company_type: Type of company (optional)
            business_address: Business address (optional)
            status: Company status (optional, defaults to ACTIVE)
            session: Database session (required)
            
        Returns:
            InvestmentCompany: The created company object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate company data
        validation_errors = self.validation_service.validate_company_creation(
            name=name,
            description=description,
            website=website,
            company_type=company_type,
            business_address=business_address
        )
        
        if validation_errors:
            raise ValueError(f"Validation failed: {validation_errors}")
        
        # Set default status if not provided
        if status is None:
            status = CompanyStatus.ACTIVE.value
        
        # Create the company directly
        company = InvestmentCompany(
            name=name.strip(),
            description=description,
            website=website,
            company_type=company_type,
            status=status,
            business_address=business_address
        )
        
        session.add(company)
        session.flush()  # Get the ID without committing
        
        return company
    
    def update_company(self, company_id: int, company_data: Dict[str, Any], 
                      session: Session) -> Optional[Dict[str, Any]]:
        """
        Update an existing investment company.
        
        Args:
            company_id: ID of the company to update
            company_data: Dictionary containing updated company data
            session: Database session
            
        Returns:
            Dictionary containing the updated company information, None if not found
            
        Raises:
            ValueError: If validation fails
        """
        # Get existing company
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return None
        
        # Validate update data
        validation_errors = self.validation_service.validate_company_update(
            company=company,
            name=company_data.get('name'),
            description=company_data.get('description'),
            website=company_data.get('website'),
            company_type=company_data.get('company_type'),
            business_address=company_data.get('business_address'),
            status=company_data.get('status')
        )
        
        if validation_errors:
            raise ValueError(f"Validation failed: {validation_errors}")
        
        # Update company fields
        if 'name' in company_data:
            company.name = company_data['name']
        if 'description' in company_data:
            company.description = company_data['description']
        if 'website' in company_data:
            company.website = company_data['website']
        if 'company_type' in company_data:
            company.company_type = company_data['company_type']
        if 'status' in company_data:
            company.status = company_data['status']
        if 'business_address' in company_data:
            company.business_address = company_data['business_address']
        
        # Update timestamp
        from datetime import datetime, timezone
        company.updated_at = datetime.now(timezone.utc)
        
        # Return updated company information
        return {
            'id': company.id,
            'name': company.name,
            'description': company.description,
            'website': company.website,
            'company_type': company.company_type.value if company.company_type else None,
            'status': company.status.value if company.status else None,
            'business_address': company.business_address,
            'updated_at': company.updated_at.isoformat() if company.updated_at else None
        }
    
    def delete_company(self, company_id: int, session: Session) -> bool:
        """
        Delete an investment company.
        
        Args:
            company_id: ID of the company to delete
            session: Database session
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            ValueError: If company cannot be deleted
        """
        # Get existing company
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return False
        
        # Validate deletion
        validation_errors = self.validation_service.validate_company_deletion(company, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete the company
        session.delete(company)
        session.flush()
        
        return True
    
    def get_company_summary(self, company_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive company summary data.
        
        Args:
            company_id: ID of the company
            session: Database session
            
        Returns:
            Company summary data if found, None otherwise
        """
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return None
        
        return self.summary_service.get_company_summary_data(company, session)
    
    def get_company_performance(self, company_id: int, session: Session) -> Optional[Dict[str, Any]]:
        """
        Get company performance summary for completed funds only.
        
        Args:
            company_id: ID of the company
            session: Database session
            
        Returns:
            Dictionary containing performance summary, None if not found
        """
        # Get existing company
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return None
        
        # Get performance summary using summary service
        return self.summary_service.get_company_performance_summary(company, session)
    
    def get_all_companies(self, session: Session) -> List[InvestmentCompany]:
        """
        Get all investment companies.
        
        Args:
            session: Database session
            
        Returns:
            List of all investment companies
        """
        return self.company_repository.get_all(session)
    
    def get_company_by_id(self, company_id: int, session: Session) -> Optional[InvestmentCompany]:
        """
        Get an investment company by ID.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            InvestmentCompany if found, None otherwise
        """
        return self.company_repository.get_by_id(company_id, session)
    
    def add_contact_to_company(self, company_id: int, contact_data: Dict[str, Any], 
                              session: Session) -> Optional[Dict[str, Any]]:
        """
        Add a contact to an investment company.
        
        Args:
            company_id: ID of the company
            contact_data: Dictionary containing contact data
            session: Database session
            
        Returns:
            Created contact information if successful, None if company not found
            
        Raises:
            ValueError: If contact data is invalid
        """
        # Get existing company
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return None
        
        # Add contact using contact service
        contact = self.contact_service.add_contact(
            company=company,
            name=contact_data['name'],
            title=contact_data.get('title'),
            direct_number=contact_data.get('direct_number'),
            direct_email=contact_data.get('direct_email'),
            notes=contact_data.get('notes'),
            session=session
        )
        
        # Return contact information
        return {
            'id': contact.id,
            'name': contact.name,
            'title': contact.title,
            'direct_number': contact.direct_number,
            'direct_email': contact.direct_email,
            'notes': contact.notes,
            'created_at': contact.created_at.isoformat() if contact.created_at else None
        }
    
    def create_fund_for_company(self, company_id: int, fund_data: Dict[str, Any], 
                               session: Session) -> Optional[Dict[str, Any]]:
        """
        Create a fund for an investment company.
        
        Args:
            company_id: ID of the company
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Created fund information if successful, None if company not found
            
        Raises:
            ValueError: If fund data is invalid
        """
        # Get existing company
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return None
        
        # Create fund using portfolio service
        fund = self.portfolio_service.create_fund(
            company=company,
            entity=fund_data['entity'],
            name=fund_data['name'],
            fund_type=fund_data['fund_type'],
            tracking_type=fund_data['tracking_type'],
            currency=fund_data.get('currency', 'AUD'),
            description=fund_data.get('description'),
            commitment_amount=fund_data.get('commitment_amount'),
            expected_irr=fund_data.get('expected_irr'),
            expected_duration_months=fund_data.get('expected_duration_months'),
            session=session
        )
        
        # Return fund information
        return {
            'id': fund.id,
            'name': fund.name,
            'fund_type': fund.fund_type,
            'tracking_type': fund.tracking_type.value if hasattr(fund.tracking_type, 'value') else fund.tracking_type,
            'entity_id': fund.entity_id,
            'investment_company_id': fund.investment_company_id,
            'created_at': fund.created_at.isoformat() if fund.created_at else None
        }
