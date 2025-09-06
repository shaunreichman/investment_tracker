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
from src.investment_company.services.company_calculation_service import CompanyCalculationService
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund


class CompanyService:
    """
    Main service layer for investment company operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    company-related business operations.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        contact_repository (ContactRepository): Repository for contact data access
        calculation_service (CompanyCalculationService): Service for calculations
        portfolio_service (CompanyPortfolioService): Service for portfolio operations
        summary_service (CompanySummaryService): Service for summary calculations
        contact_service (ContactManagementService): Service for contact management
        validation_service (CompanyValidationService): Service for validation
    """
    
    def __init__(self):
        """Initialize the company service with all required components."""
        self.company_repository = CompanyRepository()
        self.contact_repository = ContactRepository()
        self.calculation_service = CompanyCalculationService()
        self.portfolio_service = CompanyPortfolioService(calculation_service=self.calculation_service)
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
        
        # Prepare company data for creation
        company_data = {
            'name': name.strip(),
            'description': description,
            'website': website,
            'company_type': company_type,
            'status': status,
            'business_address': business_address
        }
        
        # Delegate creation to repository (follows services layer rules)
        company = self.company_repository.create(company_data, session)
        
        return company
    
    def update_company(self, company_id: int, company_data: Dict[str, Any], 
                      session: Session) -> Optional[InvestmentCompany]:
        """
        Update an existing investment company.
        
        Args:
            company_id: ID of the company to update
            company_data: Dictionary containing updated company data
            session: Database session
            
        Returns:
            Updated InvestmentCompany object if found, None otherwise
            
        Raises:
            ValueError: If validation fails
        """
        # Get existing company for validation
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
        
        # Delegate update to repository (follows services layer rules)
        updated_company = self.company_repository.update(company_id, company_data, session)
        
        return updated_company
    
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
        # Get existing company for validation
        company = self.company_repository.get_by_id(company_id, session)
        if not company:
            return False
        
        # Validate deletion
        validation_errors = self.validation_service.validate_company_deletion(company, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delegate deletion to repository (follows services layer rules)
        return self.company_repository.delete(company_id, session)
    
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
                              session: Session) -> Optional[Contact]:
        """
        Add a contact to an investment company.
        
        Args:
            company_id: ID of the company
            contact_data: Dictionary containing contact data
            session: Database session
            
        Returns:
            Created Contact object if successful, None if company not found
            
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
        
        return contact
    
    def create_fund_for_company(self, company_id: int, fund_data: Dict[str, Any], 
                               session: Session) -> Optional[Fund]:
        """
        Create a fund for an investment company.
        
        Args:
            company_id: ID of the company
            fund_data: Dictionary containing fund data
            session: Database session
            
        Returns:
            Created Fund object if successful, None if company not found
            
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
        
        return fund
