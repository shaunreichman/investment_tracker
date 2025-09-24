"""
Company Contact Repository.

This repository provides data access operations for Contact entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Company Contact CRUD operations
- Contact querying and filtering
- Contact relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.investment_company.models import Contact
from src.investment_company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder


class CompanyContactRepository:
    """
    Repository for company contact data access operations.
    
    This repository handles all database operations for contacts including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    company contact data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the contact repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl


    ################################################################################
    # Get Contact
    ################################################################################

    def get_contacts(self, session: Session,
            company_id: Optional[int] = None,
            sort_by: SortFieldContact = SortFieldContact.NAME,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[Contact]:
        """
        Get all contacts for a specific investment company.
        
        Args:
            session: Database session
            company_id: ID of the investment company
            sort_by: Sort field
            sort_order: Sort order
            
        Returns:
            List of contacts associated with the company
        """
        cache_key = f"contacts:company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Validate sort field
        if sort_by not in SortFieldContact:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Query database
        contacts = session.query(Contact)
        if company_id:
            contacts = contacts.filter(Contact.investment_company_id == company_id)

        # Apply sorting
        if sort_by == SortFieldContact.NAME:
            contacts = contacts.order_by(Contact.name.asc() if sort_order == SortOrder.ASC else Contact.name.desc())
        elif sort_by == SortFieldContact.CREATED_AT:
            contacts = contacts.order_by(Contact.created_at.asc() if sort_order == SortOrder.ASC else Contact.created_at.desc())
        elif sort_by == SortFieldContact.UPDATED_AT:
            contacts = contacts.order_by(Contact.updated_at.asc() if sort_order == SortOrder.ASC else Contact.updated_at.desc())

        contacts = contacts.all()
        
        # Cache the result
        self._cache[cache_key] = contacts
        
        return contacts
    
    def get_contact_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a contact by its ID.
        
        Args:
            session: Database session
            contact_id: ID of the contact to retrieve
            
        Returns:
            Contact object if found, None otherwise
        """
        cache_key = f"contact:{contact_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        contact = session.query(Contact).filter(Contact.id == contact_id).first()
    
        # Cache the result
        if contact:
            self._cache[cache_key] = contact
        
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
        
        # Clear cache
        self._clear_cache()
        
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
        
        # Clear specific contact cache and company contacts cache
        self._clear_contact_cache(contact_id)
        
        return True
    
    def _clear_cache(self) -> None:
        """Clear all cached data."""
        self._cache.clear()
    
    def _clear_contact_cache(self, contact_id: int) -> None:
        """Clear cache for a specific contact."""
        cache_keys_to_remove = [
            f"contact:{contact_id}",
            "contacts:all"
        ]
        
        for key in cache_keys_to_remove:
            if key in self._cache:
                del self._cache[key]
