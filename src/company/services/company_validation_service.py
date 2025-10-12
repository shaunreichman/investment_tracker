"""
Company Validation Service.
"""

from typing import Dict, List

from src.company.models import Company
from src.fund.enums.fund_enums import FundStatus
from sqlalchemy.orm import Session
from src.fund.repositories.fund_repository import FundRepository


class CompanyValidationService:
    """
    Service for validating company data and business rules.

    This module provides the CompanyValidationService class, which handles company business rule validation.
    The service provides clean separation of concerns for:
    - Company deletion with dependency checking
    
    The service uses the FundRepository to perform CRUD operations.
    The service is used by the CompanyService to validate companies.
    """
    
    def __init__(self):
        """
        Initialize the validation service.

        Args:
            fund_repository: Fund repository to use. If None, creates a new one.
        """
        self.fund_repository = FundRepository()    

    
    def validate_company_deletion(self, company: Company, session: Session) -> Dict[str, List[str]]:
        """
        Validate that the company can be deleted.
        
        Args:
            company: Company to validate for deletion
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Check if company has active funds (business constraint)
        funds_list = self.fund_repository.get_funds(session=session, company_ids=[company.id], fund_statuses=[FundStatus.ACTIVE])
        if funds_list:
            errors['funds'] = [f'Cannot delete company with {len(funds_list)} funds']
        
        return errors
