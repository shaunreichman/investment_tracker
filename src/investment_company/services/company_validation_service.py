"""
Company Validation Service.

This service handles all business rule validation and constraint checking
for companies, ensuring data integrity and business rule compliance.
"""

from typing import Dict, List, Any

from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyType
from src.fund.enums import FundStatus
from sqlalchemy.orm import Session


class CompanyValidationService:
    """
    Service for validating company data and business rules.
    
    Responsibilities:
    - Business rule validation
    - Data integrity checking
    - Constraint validation
    - Business rule documentation
    """
    
    def __init__(self):
        """Initialize the validation service."""
        pass
    
    def validate_company_creation(self, company_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate company creation data.
        
        Args:
            company_data: Dictionary containing company data
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        # Validate required fields
        required_fields = ['name', 'company_type']
        for field in required_fields:
            if field not in company_data:
                errors[field] = [f'{field} is required']
            elif not company_data[field].strip():
                errors[field] = [f'{field} is required']
        
        # Validate company type
        if company_data['company_type'] and not self._is_valid_company_type(company_data['company_type']):
            errors['company_type'] = ['Invalid company type']
        
        return errors
    
    def validate_company_deletion(self, company: InvestmentCompany, session: Session) -> Dict[str, List[str]]:
        """
        Validate that the company can be deleted.
        
        Args:
            company: Company to validate for deletion
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Check if company has active funds (business constraint)
        from src.fund.repositories.fund_repository import FundRepository
        fund_repository = FundRepository()
        funds_list = fund_repository.get_funds(session=session, company_id=company.id, fund_status=FundStatus.ACTIVE)
        if funds_list:
            errors['funds'] = [f'Cannot delete company with {len(funds_list)} funds']
        
        return errors

    
    def validate_contact_creation(self, contact_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Validate contact creation data.
        
        Args:
            contact_data: Dictionary containing contact data
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate required fields
        required_fields = ['name']
        for field in required_fields:
            if field not in contact_data:
                errors[field] = [f'{field} is required']
            elif not contact_data[field].strip():
                errors[field] = [f'{field} is required']
        
        return errors
    
    
    def _is_valid_company_type(self, company_type: str) -> bool:
        """
        Validate company type using CompanyType enum.
        
        Args:
            company_type: Company type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            CompanyType(company_type)
            return True
        except ValueError:
            return False
    