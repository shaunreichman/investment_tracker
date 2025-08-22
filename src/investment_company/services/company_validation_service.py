"""
Company Validation Service.

This service handles business rule validation and constraint checking for investment companies,
implementing clean separation of concerns and enterprise-grade architecture.

Key responsibilities:
- Business rule validation and constraint checking
- Company data validation
- Company creation and update validation
- Business rule enforcement
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.repositories import CompanyRepository, ContactRepository
from src.investment_company.models import InvestmentCompany, Contact


class CompanyValidationService:
    """
    Service for company business rule validation and constraint checking.
    
    This service handles all validation logic including business rules,
    data constraints, and validation for company operations.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        contact_repository (ContactRepository): Repository for contact data access
    """
    
    def __init__(self):
        """Initialize the company validation service."""
        self.company_repository = CompanyRepository()
        self.contact_repository = ContactRepository()
    
    def validate_company_creation(self, name: str, description: str = None, 
                                website: str = None, company_type: str = None,
                                business_address: str = None, session: Session = None) -> Dict[str, List[str]]:
        """
        Validate company creation data.
        
        Args:
            name: Company name
            description: Company description
            website: Company website URL
            company_type: Type of company
            business_address: Business address
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate name
        if not name or not name.strip():
            errors['name'] = ['Company name is required and cannot be empty']
        else:
            # Check for existing company with same name
            existing_company = self.company_repository.get_by_name(name.strip(), session)
            if existing_company:
                errors['name'] = [f"Investment company with name '{name}' already exists"]
        
        # Validate website format if provided
        if website and not self._is_valid_website(website):
            errors['website'] = ['Invalid website URL format']
        
        # Validate company type if provided
        if company_type and not self._is_valid_company_type(company_type):
            errors['company_type'] = ['Invalid company type']
        
        return errors
    
    def validate_company_update(self, company: InvestmentCompany, name: str = None,
                              description: str = None, website: str = None,
                              company_type: str = None, business_address: str = None,
                              session: Session = None) -> Dict[str, List[str]]:
        """
        Validate company update data.
        
        Args:
            company: InvestmentCompany object to update
            name: New company name
            description: New company description
            website: New company website URL
            company_type: New company type
            business_address: New business address
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate name if provided
        if name is not None:
            if not name or not name.strip():
                errors['name'] = ['Company name cannot be empty']
            else:
                # Check for existing company with same name (excluding current company)
                existing_company = self.company_repository.get_by_name(name.strip(), session)
                if existing_company and existing_company.id != company.id:
                    errors['name'] = [f"Investment company with name '{name}' already exists"]
        
        # Validate website format if provided
        if website is not None and not self._is_valid_website(website):
            errors['website'] = ['Invalid website URL format']
        
        # Validate company type if provided
        if company_type is not None and not self._is_valid_company_type(company_type):
            errors['company_type'] = ['Invalid company type']
        
        return errors
    
    def validate_company_deletion(self, company: InvestmentCompany, session: Session) -> Dict[str, List[str]]:
        """
        Validate company deletion.
        
        Args:
            company: InvestmentCompany object to delete
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Check if company has active funds
        active_funds = [f for f in company.funds if f.status == 'ACTIVE']
        if active_funds:
            errors['company'] = [f"Cannot delete company with {len(active_funds)} active funds"]
        
        # Check if company has contacts
        if company.contacts:
            errors['company'] = [f"Cannot delete company with {len(company.contacts)} contacts"]
        
        return errors
    
    def validate_company_data_integrity(self, company: InvestmentCompany, session: Session) -> Dict[str, List[str]]:
        """
        Validate company data integrity.
        
        Args:
            company: InvestmentCompany object to validate
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate required fields
        if not company.name or not company.name.strip():
            errors['name'] = ['Company name is required']
        
        # Validate relationships
        if hasattr(company, 'funds'):
            for fund in company.funds:
                if fund.investment_company_id != company.id:
                    errors['funds'] = ['Fund relationship integrity violation']
        
        if hasattr(company, 'contacts'):
            for contact in company.contacts:
                if contact.investment_company_id != company.id:
                    errors['contacts'] = ['Contact relationship integrity violation']
        
        return errors
    
    def get_company_business_rules(self) -> Dict[str, List[str]]:
        """
        Get company business rules for reference.
        
        Returns:
            dict: Business rules by category
        """
        return {
            "naming": [
                "Company name must be unique across the system",
                "Company name cannot be empty or contain only whitespace",
                "Company name should be descriptive and professional"
            ],
            "relationships": [
                "Company can have multiple funds",
                "Company can have multiple contacts",
                "Funds must reference valid company ID",
                "Contacts must reference valid company ID"
            ],
            "deletion": [
                "Company cannot be deleted if it has active funds",
                "Company cannot be deleted if it has contacts",
                "Deletion is permanent and cannot be undone"
            ],
            "validation": [
                "Website URL must be valid format if provided",
                "Company type must be from approved list if specified",
                "All required fields must be provided"
            ]
        }
    
    def _is_valid_website(self, website: str) -> bool:
        """
        Validate website URL format.
        
        Args:
            website: Website URL to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        import re
        # Basic URL validation
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return bool(re.match(pattern, website))
    
    def _is_valid_company_type(self, company_type: str) -> bool:
        """
        Validate company type.
        
        Args:
            company_type: Company type to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = [
            "Private Equity",
            "Venture Capital",
            "Real Estate",
            "Infrastructure",
            "Credit",
            "Hedge Fund",
            "Family Office",
            "Investment Bank",
            "Asset Management",
            "Other"
        ]
        return company_type in valid_types
