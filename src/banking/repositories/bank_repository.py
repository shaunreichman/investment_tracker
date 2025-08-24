"""
Bank Repository.

This repository provides data access operations for Bank entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Bank CRUD operations
- Bank querying and filtering
- Bank relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.banking.models import Bank


class BankRepository:
    """
    Repository for bank data access operations.
    
    This repository handles all database operations for banks including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    bank data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the bank repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, bank_id: int, session: Session) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            
        Returns:
            Bank object if found, None otherwise
        """
        cache_key = f"bank:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        
        # Cache the result
        if bank:
            self._cache[cache_key] = bank
        
        return bank
    
    def get_by_name_and_country(self, name: str, country: str, session: Session) -> Optional[Bank]:
        """
        Get a bank by name and country combination.
        
        Args:
            name: Bank name
            country: Country code
            session: Database session
            
        Returns:
            Bank object if found, None otherwise
        """
        cache_key = f"bank:name_country:{name}:{country}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        bank = session.query(Bank).filter(
            and_(
                Bank.name == name,
                Bank.country == country
            )
        ).first()
        
        # Cache the result
        if bank:
            self._cache[cache_key] = bank
        
        return bank
    
    def get_by_swift_bic(self, swift_bic: str, session: Session) -> Optional[Bank]:
        """
        Get a bank by SWIFT/BIC code.
        
        Args:
            swift_bic: SWIFT/BIC identifier
            session: Database session
            
        Returns:
            Bank object if found, None otherwise
        """
        cache_key = f"bank:swift_bic:{swift_bic}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        bank = session.query(Bank).filter(Bank.swift_bic == swift_bic).first()
        
        # Cache the result
        if bank:
            self._cache[cache_key] = bank
        
        return bank
    
    def get_banks_paginated(self, session: Session, page: int = 1, page_size: int = 50) -> tuple[List[Bank], int]:
        """
        Get banks with pagination support.
        
        Args:
            session: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple of (banks_list, total_count)
        """
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = session.query(func.count(Bank.id)).scalar()
        
        # Get paginated results
        banks = session.query(Bank).order_by(Bank.name).offset(offset).limit(page_size).all()
        
        return banks, total_count
    
    def get_by_country(self, country: str, session: Session) -> List[Bank]:
        """
        Get all banks for a specific country.
        
        Args:
            country: Country code
            session: Database session
            
        Returns:
            List of banks in the specified country
        """
        cache_key = f"banks:country:{country}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        banks = session.query(Bank).filter(Bank.country == country).all()
        
        # Cache the result
        self._cache[cache_key] = banks
        
        return banks
    
    def get_all(self, session: Session) -> List[Bank]:
        """
        Get all banks.
        
        Args:
            session: Database session
            
        Returns:
            List of all banks
        """
        cache_key = "banks:all"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        banks = session.query(Bank).all()
        
        # Cache the result
        self._cache[cache_key] = banks
        
        return banks
    
    def get_with_accounts_count(self, session: Session) -> List[Dict[str, Any]]:
        """
        Get all banks with their account counts.
        
        Args:
            session: Database session
            
        Returns:
            List of banks with account count information
        """
        cache_key = "banks:with_accounts_count"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with join and aggregation
        result = session.query(
            Bank,
            func.count(Bank.accounts).label('accounts_count')
        ).outerjoin(Bank.accounts).group_by(Bank.id).all()
        
        # Format result
        banks_data = []
        for bank, accounts_count in result:
            bank_data = {
                'id': bank.id,
                'name': bank.name,
                'country': bank.country,
                'swift_bic': bank.swift_bic,
                'accounts_count': accounts_count
            }
            banks_data.append(bank_data)
        
        # Cache the result
        self._cache[cache_key] = banks_data
        
        return banks_data
    
    def create(self, bank: Bank, session: Session) -> Bank:
        """
        Create a new bank.
        
        Args:
            bank: Bank instance to create
            session: Database session
            
        Returns:
            Created bank instance
        """
        session.add(bank)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_caches()
        
        return bank
    
    def update(self, bank: Bank, session: Session) -> Bank:
        """
        Update an existing bank.
        
        Args:
            bank: Bank instance to update
            session: Database session
            
        Returns:
            Updated bank instance
        """
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_caches()
        
        return bank
    
    def delete(self, bank: Bank, session: Session) -> None:
        """
        Delete a bank.
        
        Args:
            bank: Bank instance to delete
            session: Database session
        """
        session.delete(bank)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_caches()
    
    def exists(self, bank_id: int, session: Session) -> bool:
        """
        Check if a bank exists.
        
        Args:
            bank_id: ID of the bank to check
            session: Database session
            
        Returns:
            True if bank exists, False otherwise
        """
        cache_key = f"bank:exists:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        exists = session.query(Bank).filter(Bank.id == bank_id).first() is not None
        
        # Cache the result
        self._cache[cache_key] = exists
        
        return exists
    
    def count_by_country(self, country: str, session: Session) -> int:
        """
        Count banks in a specific country.
        
        Args:
            country: Country code
            session: Database session
            
        Returns:
            Number of banks in the country
        """
        cache_key = f"banks:count:country:{country}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(Bank).filter(Bank.country == country).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def get_total_count(self, session: Session) -> int:
        """
        Get total count of all banks.
        
        Args:
            session: Database session
            
        Returns:
            Total number of banks
        """
        cache_key = "banks:total_count"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(Bank).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def search(self, search_term: str, session: Session) -> List[Bank]:
        """
        Search banks by name or SWIFT/BIC.
        
        Args:
            search_term: Search term
            session: Database session
            
        Returns:
            List of matching banks
        """
        if not search_term:
            return []
        
        cache_key = f"banks:search:{search_term}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with search
        banks = session.query(Bank).filter(
            or_(
                Bank.name.ilike(f"%{search_term}%"),
                Bank.swift_bic.ilike(f"%{search_term}%")
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = banks
        
        return banks
    
    def _clear_bank_caches(self) -> None:
        """Clear all bank-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('bank')]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
