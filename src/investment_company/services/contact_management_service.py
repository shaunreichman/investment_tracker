"""
Contact Management Service.

This service handles contact operations and validation for investment companies,
implementing clean separation of concerns and enterprise-grade architecture.

Key responsibilities:
- Contact operations and validation
- Business rules for contact management
- Contact relationship management
- Contact data validation
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.repositories import CompanyRepository, ContactRepository
from src.investment_company.models import InvestmentCompany, Contact


class ContactManagementService:
    """
    Service for contact management operations and validation.
    
    This service handles all contact-related operations including creation,
    validation, and business rule enforcement for investment company contacts.
    
    Attributes:
        company_repository (CompanyRepository): Repository for company data access
        contact_repository (ContactRepository): Repository for contact data access
    """
    
    def __init__(self):
        """Initialize the contact management service."""
        self.company_repository = CompanyRepository()
        self.contact_repository = ContactRepository()
    
    def add_contact(self, company: InvestmentCompany, name: str, title: str = None, 
                   direct_number: str = None, direct_email: str = None, 
                   notes: str = None, session: Session = None) -> Contact:
        """
        Add a contact person to an investment company.
        
        Args:
            company: InvestmentCompany object
            name: Contact person's name
            title: Contact person's job title
            direct_number: Direct phone number
            direct_email: Direct email address
            notes: Additional notes about the contact
            session: Database session
        
        Returns:
            Contact: The created contact
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        if not name or not name.strip():
            raise ValueError("Contact name is required and cannot be empty")
        
        # Validate email format if provided
        if direct_email and not self._is_valid_email(direct_email):
            raise ValueError("Invalid email format")
        
        # Validate phone number format if provided
        if direct_number and not self._is_valid_phone_number(direct_number):
            raise ValueError("Invalid phone number format")
        
        # Create the contact
        contact = Contact(
            investment_company_id=company.id,
            name=name.strip(),
            title=title.strip() if title else None,
            direct_number=direct_number.strip() if direct_number else None,
            direct_email=direct_email.strip() if direct_email else None,
            notes=notes.strip() if notes else None
        )
        
        # Add to session
        session.add(contact)
        session.flush()  # Get the ID without committing
        
        return contact
    
    def update_contact(self, contact: Contact, name: str = None, title: str = None,
                      direct_number: str = None, direct_email: str = None,
                      notes: str = None, session: Session = None) -> Contact:
        """
        Update an existing contact.
        
        Args:
            contact: Contact object to update
            name: New contact name
            title: New job title
            direct_number: New direct phone number
            direct_email: New direct email address
            notes: New notes
            session: Database session
        
        Returns:
            Contact: The updated contact
            
        Raises:
            ValueError: If validation fails
        """
        # Validate email format if provided
        if direct_email and not self._is_valid_email(direct_email):
            raise ValueError("Invalid email format")
        
        # Validate phone number format if provided
        if direct_number and not self._is_valid_phone_number(direct_number):
            raise ValueError("Invalid phone number format")
        
        # Update fields if provided
        if name is not None:
            if not name.strip():
                raise ValueError("Contact name cannot be empty")
            contact.name = name.strip()
        
        if title is not None:
            contact.title = title.strip() if title else None
        
        if direct_number is not None:
            contact.direct_number = direct_number.strip() if direct_number else None
        
        if direct_email is not None:
            contact.direct_email = direct_email.strip() if direct_email else None
        
        if notes is not None:
            contact.notes = notes.strip() if notes else None
        
        # Update timestamp
        from datetime import datetime, timezone
        contact.updated_at = datetime.now(timezone.utc)
        
        return contact
    
    def delete_contact(self, contact: Contact, session: Session) -> None:
        """
        Delete a contact from an investment company.
        
        Args:
            contact: Contact object to delete
            session: Database session
        """
        session.delete(contact)
        session.flush()
    
    def get_contacts_by_company(self, company: InvestmentCompany, session: Session) -> List[Contact]:
        """
        Get all contacts for a specific investment company.
        
        Args:
            company: InvestmentCompany object
            session: Database session
            
        Returns:
            List of contacts associated with the company
        """
        return self.contact_repository.get_by_company(company.id, session)
    
    def get_contact_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a contact by ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            session: Database session
            
        Returns:
            Contact object if found, None otherwise
        """
        return self.contact_repository.get_by_id(contact_id, session)
    
    def get_contact_by_email(self, email: str, session: Session) -> Optional[Contact]:
        """
        Get a contact by email address.
        
        Args:
            email: Email address to search for
            session: Database session
            
        Returns:
            Contact object if found, None otherwise
        """
        return self.contact_repository.get_by_email(email, session)
    
    def validate_contact_data(self, name: str = None, title: str = None,
                            direct_number: str = None, direct_email: str = None,
                            notes: str = None) -> Dict[str, List[str]]:
        """
        Validate contact data without creating/updating.
        
        Args:
            name: Contact name
            title: Job title
            direct_number: Direct phone number
            direct_email: Direct email address
            notes: Additional notes
            
        Returns:
            dict: Validation errors by field name
        """
        errors = {}
        
        # Validate name
        if name is not None:
            if not name or not name.strip():
                errors['name'] = ['Contact name is required and cannot be empty']
        
        # Validate email format
        if direct_email and not self._is_valid_email(direct_email):
            errors['direct_email'] = ['Invalid email format']
        
        # Validate phone number format
        if direct_number and not self._is_valid_phone_number(direct_number):
            errors['direct_number'] = ['Invalid phone number format']
        
        return errors
    
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
        # Allow various phone number formats
        pattern = r'^[\+]?[1-9][\d]{0,15}$'
        return bool(re.match(pattern, phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')))
