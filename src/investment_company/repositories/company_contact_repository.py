"""
Company Contact Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.models import Contact
from src.investment_company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder


class CompanyContactRepository:
    """
    Company Contact Repository.

    This repository handles all database operations for company contacts including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    company contact data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the company contact repository.
        
        Args:
            None
        """
        pass


    ################################################################################
    # Get Company Contacts
    ################################################################################

    def get_contacts(self, session: Session,
            company_ids: Optional[List[int]] = None,
            sort_by: SortFieldContact = SortFieldContact.NAME,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[Contact]:
        """
        Get all company contacts.
        
        Args:
            session: Database session
            company_ids: IDs of the investment companies (optional)
            sort_by: Sort field
            sort_order: Sort order
            
        Returns:
            List of company contacts
        """
        # Validate sort field
        if sort_by not in SortFieldContact:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Query database
        contacts = session.query(Contact)
        if company_ids:
            contacts = contacts.filter(Contact.investment_company_id.in_(company_ids))

        # Apply sorting
        if sort_by == SortFieldContact.NAME:
            contacts = contacts.order_by(Contact.name.asc() if sort_order == SortOrder.ASC else Contact.name.desc())
        elif sort_by == SortFieldContact.CREATED_AT:
            contacts = contacts.order_by(Contact.created_at.asc() if sort_order == SortOrder.ASC else Contact.created_at.desc())
        elif sort_by == SortFieldContact.UPDATED_AT:
            contacts = contacts.order_by(Contact.updated_at.asc() if sort_order == SortOrder.ASC else Contact.updated_at.desc())

        contacts = contacts.all()
        
        return contacts
    
    def get_contact_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a company contact by its ID.
        
        Args:
            session: Database session
            contact_id: ID of the contact to retrieve
            
        Returns:
            Contact object if found, None otherwise
        """
        # Query database
        contact = session.query(Contact).filter(Contact.id == contact_id).first()
    
        return contact
    

    ################################################################################
    # Create Contact
    ################################################################################

    def create_contact(self, contact_data: Dict[str, Any], session: Session) -> Contact:
        """
        Create a new contact.
        
        Args:
            contact_data: Dictionary containing contact data
            session: Database session
            
        Returns:
            The created Contact object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """

        # Create the contact
        contact = Contact(**contact_data)
        session.add(contact)
        session.flush()  # Get the ID without committing
        
        return contact
    

    ################################################################################
    # Delete Contact
    ################################################################################

    def delete_contact(self, contact_id: int, session: Session) -> bool:
        """
        Delete a contact.
        
        Args:
            contact_id: ID of the contact to delete
            session: Database session
            
        Returns:
            True if contact was deleted, False if not found
        """
        contact = self.get_contact_by_id(contact_id, session)
        if not contact:
            return False
        
        session.delete(contact)
        session.flush()
        
        return True
