"""
Company Contact service.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.company.repositories.company_contact_repository import CompanyContactRepository
from src.company.models import Contact
from src.company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder

class CompanyContactService:
    """
    Main service layer for company contact operations.

    This module provides the CompanyContactService class, which handles company contact operations and business logic.
    The service provides clean separation of concerns for:
    - Company contact retrieval
    - Company contact creation
    - Company contact deletion

    The service uses the CompanyContactRepository to perform CRUD operations.
    The service is used by the CompanyController to handle company contact operations.
    """

    def __init__(self):
        """
        Initialize the CompanyContactService.

        Args:
            company_contact_repository: Company contact repository to use. If None, creates a new one.
        """
        self.company_contact_repository = CompanyContactRepository()

    ################################################################################
    # GET CONTACTS
    ################################################################################

    def get_contacts(self, session: Session,
            company_ids: Optional[List[int]] = None,
            sort_by: Optional[SortFieldContact] = SortFieldContact.NAME,
            sort_order: Optional[SortOrder] = SortOrder.ASC
    ) -> List[Contact]:
        """
        Get all contacts for a company.

        Args:
            session: Database session
            company_ids: IDs of the companies
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            List of contacts
        """
        return self.company_contact_repository.get_contacts(session, company_ids, sort_by, sort_order)

    def get_contact_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a contact by its ID.

        Args:
            contact_id: ID of the contact to retrieve
            session: Database session

        Returns:
            Contact: The contact instance
        """
        return self.company_contact_repository.get_contact_by_id(contact_id, session)


    ################################################################################
    # Create Contact
    ################################################################################

    def create_contact(self, company_id: int, contact_data: Dict[str, Any], session: Session) -> Contact:
        """
        Create a new contact.

        Args:
            company_id: ID of the company to add contact to
            contact_data: Dictionary containing contact data
            session: Database session

        Returns:
            Contact: The created contact instance
        """
        # Validate Company exists
        from src.company.repositories.company_repository import CompanyRepository
        company_repository = CompanyRepository()
        company = company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")

        processed_data = {
            **contact_data,
            'company_id': company_id
        }
        
        # Create the contact
        contact = self.company_contact_repository.create_contact(processed_data, session)
        if not contact:
            raise ValueError(f"Failed to create contact with name '{processed_data.get('name', 'unknown')}' for company ID {company_id}")

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
            bool: True if contact was deleted, False otherwise
        """
        # Get the contact
        contact = self.company_contact_repository.get_contact_by_id(contact_id, session)
        if not contact:
            raise ValueError(f"Contact with ID {contact_id} not found")

        # Delete the contact
        success = self.company_contact_repository.delete_contact(contact_id, session)
        if not success:
            raise ValueError(f"Failed to delete contact with ID {contact_id}")

        return success