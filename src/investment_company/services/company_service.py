"""
Company Service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.repositories.company_repository import CompanyRepository
from src.investment_company.models import InvestmentCompany
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.enums.company_enums import CompanyType, CompanyStatus, SortFieldCompany
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
        processed_data = company_data.copy()

        # Set the company status to INACTIVE on creation
        processed_data['status'] = CompanyStatus.INACTIVE

        company = self.company_repository.create_company(processed_data, session)
        if not company:
            raise ValueError(f"Failed to create company")
        
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
            raise ValueError(f"Company not found")
        
        # Validate deletion
        validation_errors = self.company_validation_service.validate_company_deletion(company, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")

        success = self.company_repository.delete_company(company_id, session)
        if not success:
            raise ValueError(f"Failed to delete company")

        return success