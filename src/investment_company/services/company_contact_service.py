"""
Company contact service.

This service provides the main business logic layer for company contact operations,
coordinating between the API controllers and the domain services.

Key responsibilities:
- Company contact CRUD operations coordination
- Service orchestration
- Business logic coordination
- API layer integration
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.repositories import CompanyContactRepository
from src.investment_company.models import Contact
from src.investment_company.services import CompanyValidationService
from src.investment_company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder

class CompanyContactService:
    """
    Main service layer for company contact operations.
    """

    def __init__(self):
        self.company_contact_repository = CompanyContactRepository()
        self.validation_service = CompanyValidationService()

    ################################################################################
    # GET CONTACTS
    ################################################################################

    def get_contacts(self, session: Session,
            company_id: Optional[int] = None,
            sort_by: SortFieldContact = SortFieldContact.NAME,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[Contact]:
        """
        Get all contacts for a company.

        Args:
            session: Database session
            company_id: ID of the company
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            List of contacts
        """
        return self.company_contact_repository.get_contacts(session, company_id, sort_by, sort_order)

    def get_contact_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a contact by its ID.

        Args:
            contact_id: ID of the contact to retrieve
            session: Database session

        Returns:
            Contact: The contact instance
        """
        return self.company_contact_repository.get_contact_by_id(session, contact_id)


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
        from src.investment_company.repositories.company_repository import CompanyRepository
        company_repository = CompanyRepository()
        company = company_repository.get_company_by_id(company_id, session)
        if not company:
            raise ValueError(f"Company not found")

        processed_data = {
            **contact_data,
            'company_id': company_id
        }
        
        # Create the contact
        contact = self.company_contact_repository.create_contact(processed_data, session)
        if not contact:
            raise ValueError(f"Failed to create contact")

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
            raise ValueError(f"Contact not found")

        # Delete the contact
        success = self.company_contact_repository.delete_contact(contact_id, session)
        if not success:
            raise ValueError(f"Failed to delete contact")

        return success