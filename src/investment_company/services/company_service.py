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

from src.investment_company.repositories import CompanyRepository, CompanyContactRepository
from src.investment_company.models import InvestmentCompany
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.enums.company_enums import CompanyType, CompanyStatus, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder


class CompanyService:
    """
    Main service layer for company operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    company-related business operations.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        company_contact_repository (CompanyContactRepository): Repository for contact data access
        company_validation_service (CompanyValidationService): Service for validation
    """
    
    def __init__(self):
        """Initialize the company service with all required components."""
        self.company_repository = CompanyRepository()
        self.company_contact_repository = CompanyContactRepository()
        self.company_validation_service = CompanyValidationService()

    ################################################################################
    # GET COMPANIES
    ################################################################################

    def get_companies(self, session: Session,
            company_type: Optional[CompanyType] = None,
            status: Optional[CompanyStatus] = None,
            name: Optional[str] = None,
            sort_by: Optional[SortFieldCompany] = None,
            sort_order: Optional[SortOrder] = None,
    ) -> List[InvestmentCompany]:
        """
        Get all companies.

        Args:
            session: Database session
            company_type: Type of company to filter by
            status: Status to filter by
            name: Name to filter by
            sort_by: Field to sort by
            sort_order: Order to sort by

        Returns:
            List of companies
        """
        return self.company_repository.get_companies(session, company_type, status, name, sort_by, sort_order)
    
    def get_company_by_id(self, company_id: int, session: Session) -> Optional[InvestmentCompany]:
        """
        Get a company by ID.
        
        Args:
            company_id: Company ID
            session: Database session
            
        Returns:
            InvestmentCompany if found, None otherwise
        """
        return self.company_repository.get_company_by_id(company_id, session)


    ################################################################################
    # CREATE COMPANY
    ################################################################################

    def create_company(self, company_data: Dict[str, Any], session: Session) -> InvestmentCompany:
        """
        Create a new company.

        Args:
            company_data: Dictionary containing company data
            session: Database session
            
        Returns:
            InvestmentCompany: The created company object
        """
        required_fields = ['name']
        for field in required_fields:
            if field not in company_data:
                raise ValueError(f"Required field '{field}' is missing")

        processed_data = company_data.copy()
        if 'company_type' in processed_data and isinstance(processed_data['company_type'], str):
            try:
                processed_data['company_type'] = CompanyType(processed_data['company_type'])
            except ValueError:
                raise ValueError(f"Invalid company type: {processed_data['company_type']}. Must be one of: {[c.value for c in CompanyType]}")
        
        company = self.company_repository.create_company(processed_data, session)
        if not company:
            raise ValueError(f"Failed to create company")
        
        # Set the company status to INACTIVE on creation
        company.status = CompanyStatus.INACTIVE

        return company


    ################################################################################
    # DELETE COMPANY
    ################################################################################

    def delete_company(self, company_id: int, session: Session) -> bool:
        """
        Delete a company.
        
        Args:
            company_id: ID of the company to delete
            session: Database session
            
        Returns:
            True if deleted successfully, False if not found
            
        Raises:
            ValueError: If company cannot be deleted
        """
        # Get existing company for validation
        company = self.company_repository.get_company_by_id(company_id, session)
        if not company:
            return False
        
        # Validate deletion
        validation_errors = self.company_validation_service.validate_company_deletion(company, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")

        success = self.company_repository.delete_company(company_id, session)
        if not success:
            raise ValueError(f"Failed to delete company")

        return success