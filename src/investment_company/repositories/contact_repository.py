"""
Contact Repository.

This repository provides data access operations for Contact entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Contact CRUD operations
- Contact querying and filtering
- Contact relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.investment_company.models import Contact, InvestmentCompany


class ContactRepository:
    """
    Repository for contact data access operations.
    
    This repository handles all database operations for contacts including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    contact data without direct database access.
    
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
    
    def get_by_id(self, contact_id: int, session: Session) -> Optional[Contact]:
        """
        Get a contact by its ID.
        
        Args:
            contact_id: ID of the contact to retrieve
            session: Database session
            
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
    
    def get_by_company(self, company_id: int, session: Session) -> List[Contact]:
        """
        Get all contacts for a specific investment company.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            List of contacts associated with the company
        """
        cache_key = f"contacts:company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        contacts = session.query(Contact).filter(Contact.investment_company_id == company_id).all()
        
        # Cache the result
        self._cache[cache_key] = contacts
        
        return contacts
    
    def get_by_email(self, email: str, session: Session) -> Optional[Contact]:
        """
        Get a contact by email address.
        
        Args:
            email: Email address to search for
            session: Database session
            
        Returns:
            Contact object if found, None otherwise
        """
        cache_key = f"contact:email:{email}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        contact = session.query(Contact).filter(Contact.direct_email == email).first()
        
        # Cache the result
        if contact:
            self._cache[cache_key] = contact
        
        return contact
    
    def get_by_name(self, name: str, session: Session) -> List[Contact]:
        """
        Get contacts by name (partial match).
        
        Args:
            name: Name to search for
            session: Database session
            
        Returns:
            List of contacts matching the name
        """
        cache_key = f"contacts:name:{name}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with partial match
        search_pattern = f"%{name}%"
        contacts = session.query(Contact).filter(Contact.name.ilike(search_pattern)).all()
        
        # Cache the result
        self._cache[cache_key] = contacts
        
        return contacts
    
    def create(self, contact_data: Dict[str, Any], session: Session) -> Contact:
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
        # Validate required fields
        if 'name' not in contact_data or not contact_data['name']:
            raise ValueError("Contact name is required")
        
        if 'investment_company_id' not in contact_data:
            raise ValueError("Investment company ID is required")
        
        # Create the contact
        contact = Contact(**contact_data)
        session.add(contact)
        session.flush()  # Get the ID without committing
        
        # Clear cache
        self._clear_cache()
        
        return contact
    
    def update(self, contact_id: int, contact_data: Dict[str, Any], session: Session) -> Optional[Contact]:
        """
        Update an existing contact.
        
        Args:
            contact_id: ID of the contact to update
            contact_data: Dictionary containing updated contact data
            session: Database session
            
        Returns:
            Updated Contact object if found, None otherwise
        """
        contact = self.get_by_id(contact_id, session)
        if not contact:
            return None
        
        # Update fields
        for key, value in contact_data.items():
            if hasattr(contact, key):
                setattr(contact, key, value)
        
        # Update timestamp
        from datetime import datetime, timezone
        contact.updated_at = datetime.now(timezone.utc)
        
        session.flush()
        
        # Clear cache
        self._clear_cache()
        
        return contact
    
    def delete(self, contact_id: int, session: Session) -> bool:
        """
        Delete a contact.
        
        Args:
            contact_id: ID of the contact to delete
            session: Database session
            
        Returns:
            True if contact was deleted, False if not found
        """
        contact = self.get_by_id(contact_id, session)
        if not contact:
            return False
        
        session.delete(contact)
        session.flush()
        
        # Clear cache
        self._clear_cache()
        
        return True
    
    def get_contacts_with_company_info(self, company_id: int, session: Session) -> List[Dict[str, Any]]:
        """
        Get contacts with company information for a specific company.
        
        Args:
            company_id: ID of the investment company
            session: Database session
            
        Returns:
            List of contacts with company information
        """
        cache_key = f"contacts:with_company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with JOIN
        contacts_data = session.query(
            Contact,
            InvestmentCompany.name.label('company_name'),
            InvestmentCompany.company_type.label('company_type')
        ).join(InvestmentCompany).filter(Contact.investment_company_id == company_id).all()
        
        # Format results
        result = []
        for contact, company_name, company_type in contacts_data:
            result.append({
                "id": contact.id,
                "name": contact.name,
                "title": contact.title,
                "direct_number": contact.direct_number,
                "direct_email": contact.direct_email,
                "notes": contact.notes,
                "company_name": company_name,
                "company_type": company_type,
                "created_at": contact.created_at.isoformat() if contact.created_at else None,
                "updated_at": contact.updated_at.isoformat() if contact.updated_at else None
            })
        
        # Cache the result
        self._cache[cache_key] = result
        
        return result
    
    def search_contacts(self, search_term: str, company_id: Optional[int] = None, session: Session = None) -> List[Contact]:
        """
        Search contacts by name, title, or email.
        
        Args:
            search_term: Search term to look for
            company_id: Optional company ID to filter by
            session: Database session
            
        Returns:
            List of contacts matching the search term
        """
        cache_key = f"contacts:search:{search_term}:company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(Contact)
        
        # Add company filter if specified
        if company_id:
            query = query.filter(Contact.investment_company_id == company_id)
        
        # Add search filter
        search_pattern = f"%{search_term}%"
        query = query.filter(
            or_(
                Contact.name.ilike(search_pattern),
                Contact.title.ilike(search_pattern),
                Contact.direct_email.ilike(search_pattern)
            )
        )
        
        # Execute query
        contacts = query.all()
        
        # Cache the result
        self._cache[cache_key] = contacts
        
        return contacts
    
    def get_contacts_by_title(self, title: str, company_id: Optional[int] = None, session: Session = None) -> List[Contact]:
        """
        Get contacts by job title.
        
        Args:
            title: Job title to filter by
            company_id: Optional company ID to filter by
            session: Database session
            
        Returns:
            List of contacts with the specified title
        """
        cache_key = f"contacts:title:{title}:company:{company_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Build query
        query = session.query(Contact).filter(Contact.title == title)
        
        # Add company filter if specified
        if company_id:
            query = query.filter(Contact.investment_company_id == company_id)
        
        # Execute query
        contacts = query.all()
        
        # Cache the result
        self._cache[cache_key] = contacts
        
        return contacts
    
    def bulk_create_contacts(self, contacts_data: List[Dict[str, Any]], session: Session) -> List[Contact]:
        """
        Create multiple contacts in a single operation.
        
        Args:
            contacts_data: List of dictionaries containing contact data
            session: Database session
            
        Returns:
            List of created Contact objects
        """
        contacts = []
        
        for contact_data in contacts_data:
            # Validate required fields
            if 'name' not in contact_data or not contact_data['name']:
                raise ValueError("Contact name is required")
            
            if 'investment_company_id' not in contact_data:
                raise ValueError("Investment company ID is required")
            
            # Create contact
            contact = Contact(**contact_data)
            contacts.append(contact)
            session.add(contact)
        
        session.flush()
        
        # Clear cache
        self._clear_cache()
        
        return contacts
    
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
    
    def _clear_company_contacts_cache(self, company_id: int) -> None:
        """Clear cache for contacts of a specific company."""
        cache_keys_to_remove = [
            f"contacts:company:{company_id}",
            f"contacts:with_company:{company_id}"
        ]
        
        for key in cache_keys_to_remove:
            if key in self._cache:
                del self._cache[key]
