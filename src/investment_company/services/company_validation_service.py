"""
Company Validation Service.

This service handles all business rule validation and constraint checking
for investment companies, ensuring data integrity and business rule compliance.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.orm import Session

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus


class CompanyValidationService:
    """
    Service for validating investment company data and business rules.
    
    Responsibilities:
    - Business rule validation
    - Data integrity checking
    - Constraint validation
    - Business rule documentation
    """
    
    def __init__(self):
        """Initialize the validation service."""
        pass
    
    def validate_company_creation(self, name: str, description: str = None,
                                website: str = None, company_type: str = None,
                                business_address: str = None) -> Dict[str, List[str]]:
        """
        Validate company creation data.
        
        Args:
            name: Company name
            description: Company description
            website: Company website URL
            company_type: Type of company
            business_address: Business address
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate required fields
        if not name or not name.strip():
            errors['name'] = ['Company name is required']
        elif len(name.strip()) > 255:
            errors['name'] = ['Company name must be 255 characters or less']
        
        # Validate company type
        if company_type and not self._is_valid_company_type(company_type):
            errors['company_type'] = ['Invalid company type']
        
        # Validate website if provided
        if website and not self._is_valid_website(website):
            errors['website'] = ['Invalid website URL format']
        
        return errors
    
    def validate_company_update(self, company: InvestmentCompany, name: str = None,
                              description: str = None, website: str = None,
                              company_type: str = None, business_address: str = None,
                              status: str = None) -> Dict[str, List[str]]:
        """
        Validate company update data.
        
        Args:
            company: Existing company object
            name: New company name
            description: New company description
            website: New company website URL
            company_type: New company type
            business_address: New business address
            status: New company status
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate name if provided
        if name is not None:
            if not name.strip():
                errors['name'] = ['Company name is required']
            elif len(name.strip()) > 255:
                errors['name'] = ['Company name must be 255 characters or less']
        
        # Validate company type if provided
        if company_type is not None and not self._is_valid_company_type(company_type):
            errors['company_type'] = ['Invalid company type']
        
        # Validate status if provided
        if status is not None and not self._is_valid_company_status(status):
            errors['status'] = ['Invalid company status']
        
        # Validate website if provided
        if website is not None and not self._is_valid_website(website):
            errors['website'] = ['Invalid website URL format']
        
        return errors
    
    def validate_contact_creation(self, name: str, title: str = None,
                                direct_number: str = None, direct_email: str = None,
                                notes: str = None) -> Dict[str, List[str]]:
        """
        Validate contact creation data.
        
        Args:
            name: Contact name
            title: Contact title
            direct_number: Direct phone number
            direct_email: Direct email address
            notes: Additional notes
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate required fields
        if not name or not name.strip():
            errors['name'] = ['Contact name is required']
        elif len(name.strip()) > 255:
            errors['name'] = ['Contact name must be 255 characters or less']
        
        # Validate email format if provided
        if direct_email and not self._is_valid_email(direct_email):
            errors['direct_email'] = ['Invalid email format']
        
        # Validate phone number format if provided
        if direct_number and not self._is_valid_phone_number(direct_number):
            errors['direct_number'] = ['Invalid phone number format']
        
        return errors
    
    def validate_contact_update(self, contact: Contact, name: str = None,
                              title: str = None, direct_number: str = None,
                              direct_email: str = None, notes: str = None) -> Dict[str, List[str]]:
        """
        Validate contact update data.
        
        Args:
            contact: Existing contact object
            name: New contact name
            title: New contact title
            direct_number: New direct phone number
            direct_email: New direct email address
            notes: New additional notes
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate name if provided
        if name is not None:
            if not name.strip():
                errors['name'] = ['Contact name is required']
            elif len(name.strip()) > 255:
                errors['name'] = ['Contact name must be 255 characters or less']
        
        # Validate email format if provided
        if direct_email is not None and not self._is_valid_email(direct_email):
            errors['direct_email'] = ['Invalid email format']
        
        # Validate phone number format if provided
        if direct_number is not None and not self._is_valid_phone_number(direct_number):
            errors['direct_number'] = ['Invalid phone number format']
        
        return errors
    
    def validate_company_deletion(self, company: InvestmentCompany, session: Session) -> Dict[str, List[str]]:
        """
        Validate if a company can be deleted.
        
        Args:
            company: Company to validate for deletion
            session: Database session
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Check if company has active funds
        active_funds = [fund for fund in company.funds if fund.status.value in ['ACTIVE', 'SUSPENDED']]
        if active_funds:
            errors['funds'] = [f'Cannot delete company with {len(active_funds)} active funds']
        
        # Check if company has contacts
        if company.contacts:
            errors['contacts'] = [f'Cannot delete company with {len(company.contacts)} contacts']
        
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
                "Company status must be from approved list",
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
    
    def _is_valid_company_status(self, status: str) -> bool:
        """
        Validate company status using CompanyStatus enum.
        
        Args:
            status: Company status to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            CompanyStatus(status)
            return True
        except ValueError:
            return False
    
    def _is_valid_email(self, email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _is_valid_phone_number(self, phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        import re
        # Basic phone validation - allows digits, spaces, dashes, parentheses, and plus
        pattern = r'^[\+]?[0-9\s\-\(\)]{7,20}$'
        return bool(re.match(pattern, phone))

    def validate_company_data(self, company_data: Dict[str, Any]) -> None:
        """
        Validate company data for updates.
        
        Args:
            company_data: Dictionary containing company data to validate
            
        Raises:
            ValueError: If company data is invalid
        """
        errors = []
        
        # Validate name if provided
        if 'name' in company_data:
            if not company_data['name'] or not company_data['name'].strip():
                errors.append("Company name is required")
            elif len(company_data['name'].strip()) > 255:
                errors.append("Company name must be 255 characters or less")
        
        # Validate company type if provided
        if 'company_type' in company_data and company_data['company_type']:
            if not self._is_valid_company_type(company_data['company_type']):
                errors.append("Invalid company type")
        
        # Validate website if provided
        if 'website' in company_data and company_data['website']:
            if not self._is_valid_website(company_data['website']):
                errors.append("Invalid website URL format")
        
        if errors:
            raise ValueError(f"Company data validation failed: {'; '.join(errors)}")

    def validate_contact_data(self, contact_data: Dict[str, Any]) -> None:
        """
        Validate contact data.
        
        Args:
            contact_data: Dictionary containing contact data to validate
            
        Raises:
            ValueError: If contact data is invalid
        """
        errors = []
        
        # Validate required fields
        if not contact_data.get('name') or not contact_data['name'].strip():
            errors.append("Contact name is required")
        
        # Validate email if provided
        if 'email' in contact_data and contact_data['email']:
            if not self._is_valid_email(contact_data['email']):
                errors.append("Invalid email format")
        
        # Validate phone if provided
        if 'phone' in contact_data and contact_data['phone']:
            if not self._is_valid_phone_number(contact_data['phone']):
                errors.append("Invalid phone number format")
        
        if errors:
            raise ValueError(f"Contact data validation failed: {'; '.join(errors)}")

    def validate_portfolio_data(self, portfolio_data: Dict[str, Any]) -> None:
        """
        Validate portfolio update data.
        
        Args:
            portfolio_data: Dictionary containing portfolio data to validate
            
        Raises:
            ValueError: If portfolio data is invalid
        """
        errors = []
        
        # Validate required fields
        if 'operation' not in portfolio_data:
            errors.append("Operation is required")
        else:
            valid_operations = ['added', 'removed', 'updated']
            if portfolio_data['operation'] not in valid_operations:
                errors.append(f"Invalid operation. Must be one of: {', '.join(valid_operations)}")
        
        # Validate fund_id if operation requires it
        if portfolio_data.get('operation') in ['added', 'removed']:
            if 'fund_id' not in portfolio_data or not portfolio_data['fund_id']:
                errors.append("Fund ID is required for add/remove operations")
        
        if errors:
            raise ValueError(f"Portfolio data validation failed: {'; '.join(errors)}")
