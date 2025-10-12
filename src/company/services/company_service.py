"""
Company Service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.company.repositories.company_repository import CompanyRepository
from src.company.models import Company
from src.company.services.company_validation_service import CompanyValidationService
from src.company.enums.company_enums import CompanyType, CompanyStatus, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder


class CompanyService:
    """
    Main service layer for company operations.

    This module provides the CompanyService class, which handles company operations and business logic.
    The service provides clean separation of concerns for:
    - Company retrieval
    - Company creation
    - Company deletion with dependency checking

    The service uses the CompanyRepository to perform CRUD operations and the CompanyValidationService to validate companies.
    The service is used by the CompanyController to handle company operations.
    """
    
    def __init__(self):
        """
        Initialize the company service with all required components.

        Args:
            company_repository: Company repository to use. If None, creates a new one.
            company_validation_service: Company validation service to use. If None, creates a new one.
        """
        self.company_repository = CompanyRepository()
        self.company_validation_service = CompanyValidationService()

    ################################################################################
    # GET COMPANIES
    ################################################################################

    def get_companies(self, session: Session,
            company_types: Optional[List[CompanyType]] = None,
            statuses: Optional[List[CompanyStatus]] = None,
            names: Optional[List[str]] = None,
            sort_by: Optional[SortFieldCompany] = None,
            sort_order: Optional[SortOrder] = None,
            include_contacts: Optional[bool] = False,
    ) -> List[Company]:
        """
        Get all companies.

        Args:
            session: Database session
            company_types: Types of company to filter by
            statuses: Statuses to filter by
            names: Names to filter by
            sort_by: Field to sort by
            sort_order: Order to sort by
            include_contacts: Whether to eager load contacts relationship

        Returns:
            List of companies
        """
        return self.company_repository.get_companies(session, company_types, statuses, names, sort_by, sort_order, include_contacts)
    
    def get_company_by_id(self, company_id: int, session: Session, include_contacts: Optional[bool] = False) -> Optional[Company]:
        """
        Get a company by ID.
        
        Args:
            company_id: Company ID
            session: Database session
            include_contacts: Whether to eager load contacts relationship
            
        Returns:
            Company if found, None otherwise
        """
        return self.company_repository.get_company_by_id(company_id, session, include_contacts)


    ################################################################################
    # CREATE COMPANY
    ################################################################################

    def create_company(self, company_data: Dict[str, Any], session: Session) -> Company:
        """
        Create a new company.

        Args:
            company_data: Dictionary containing company data
            session: Database session
            
        Returns:
            Company: The created company object
        """
        processed_data = company_data.copy()

        # Set the company status to INACTIVE on creation
        processed_data['status'] = CompanyStatus.INACTIVE

        company = self.company_repository.create_company(processed_data, session)
        if not company:
            raise ValueError(f"Failed to create company with name '{processed_data.get('name', 'unknown')}'")
        
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
            raise ValueError(f"Company with ID {company_id} not found")
        
        # Validate deletion
        validation_errors = self.company_validation_service.validate_company_deletion(company, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed for company with ID {company_id}: {validation_errors}")

        success = self.company_repository.delete_company(company_id, session)
        if not success:
            raise ValueError(f"Failed to delete company with ID {company_id}")

        return success