"""
Bank Account Repository.

This repository provides data access operations for BankAccount entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Bank account CRUD operations
- Bank account querying and filtering
- Bank account relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import joinedload

from src.banking.models import BankAccount
from src.banking.enums import AccountStatus


class BankAccountRepository:
    """
    Repository for bank account data access operations.
    
    This repository handles all database operations for bank accounts including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    bank account data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the bank account repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl
    
    def get_by_id(self, account_id: int, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            account_id: ID of the account to retrieve
            session: Database session
            
        Returns:
            BankAccount object if found, None otherwise
        """
        cache_key = f"bank_account:{account_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        account = session.query(BankAccount).filter(BankAccount.id == account_id).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = account
        
        return account
    
    def get_by_unique(self, entity_id: int, bank_id: int, account_number: str, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by unique combination.
        
        Args:
            entity_id: Owner entity ID
            bank_id: Linked bank ID
            account_number: Account number
            session: Database session
            
        Returns:
            BankAccount object if found, None otherwise
        """
        cache_key = f"bank_account:unique:{entity_id}:{bank_id}:{account_number}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        account = session.query(BankAccount).filter(
            and_(
                BankAccount.entity_id == entity_id,
                BankAccount.bank_id == bank_id,
                BankAccount.account_number == account_number
            )
        ).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = account
        
        return account
    
    def get_by_bank_and_number(self, bank_id: int, account_number: str, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by bank ID and account number (across all entities).
        
        Args:
            bank_id: Linked bank ID
            account_number: Account number
            session: Database session
            
        Returns:
            BankAccount object if found, None otherwise
        """
        cache_key = f"bank_account:bank_number:{bank_id}:{account_number}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        account = session.query(BankAccount).filter(
            and_(
                BankAccount.bank_id == bank_id,
                BankAccount.account_number == account_number
            )
        ).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = account
        
        return account
    
    def get_by_entity(self, entity_id: int, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts for a specific entity.
        
        Args:
            entity_id: Owner entity ID
            session: Database session
            
        Returns:
            List of BankAccount objects
        """
        cache_key = f"bank_accounts:entity:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with bank relationship loaded
        accounts = session.query(BankAccount).options(
            joinedload(BankAccount.bank)
        ).filter(BankAccount.entity_id == entity_id).all()
        
        # Cache the result
        if accounts:
            self._cache[cache_key] = accounts
        
        return accounts
    
    def get_bank_accounts_paginated(self, session: Session, page: int = 1, page_size: int = 50) -> tuple[List[BankAccount], int]:
        """
        Get bank accounts with pagination support.
        
        Args:
            session: Database session
            page: Page number (1-based)
            page_size: Number of items per page
            
        Returns:
            Tuple of (accounts_list, total_count)
        """
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get total count
        total_count = session.query(func.count(BankAccount.id)).scalar()
        
        # Get paginated results with bank relationship loaded
        accounts = session.query(BankAccount).options(
            joinedload(BankAccount.bank)
        ).order_by(BankAccount.account_name).offset(offset).limit(page_size).all()
        
        return accounts, total_count
    
    def get_by_bank(self, bank_id: int, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts for a specific bank.
        
        Args:
            bank_id: Bank ID
            session: Database session
            
        Returns:
            List of bank accounts at the specified bank
        """
        cache_key = f"bank_accounts:bank:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        accounts = session.query(BankAccount).filter(BankAccount.bank_id == bank_id).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def get_by_currency(self, currency: str, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts with a specific currency.
        
        Args:
            currency: Currency code
            session: Database session
            
        Returns:
            List of bank accounts with the specified currency
        """
        cache_key = f"bank_accounts:currency:{currency}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        accounts = session.query(BankAccount).filter(BankAccount.currency == currency).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def get_active_accounts(self, session: Session) -> List[BankAccount]:
        """
        Get all active bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            List of active bank accounts
        """
        cache_key = "bank_accounts:active"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        accounts = session.query(BankAccount).filter(BankAccount.status == AccountStatus.ACTIVE).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def get_inactive_accounts(self, session: Session) -> List[BankAccount]:
        """
        Get all inactive bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            List of inactive bank accounts
        """
        cache_key = "bank_accounts:inactive"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        accounts = session.query(BankAccount).filter(BankAccount.status != AccountStatus.ACTIVE).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def get_all(self, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            List of all bank accounts
        """
        cache_key = "bank_accounts:all"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        accounts = session.query(BankAccount).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def get_with_bank_info(self, session: Session) -> List[Dict[str, Any]]:
        """
        Get all bank accounts with bank information.
        
        Args:
            session: Database session
            
        Returns:
            List of bank accounts with bank details
        """
        cache_key = "bank_accounts:with_bank_info"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with join
        result = session.query(
            BankAccount,
            BankAccount.bank
        ).join(BankAccount.bank).all()
        
        # Format result
        accounts_data = []
        for account, bank in result:
            account_data = {
                'id': account.id,
                'entity_id': account.entity_id,
                'bank_id': account.bank_id,
                'account_name': account.account_name,
                'account_number': account.account_number,
                'currency': account.currency,
                'is_active': account.status == AccountStatus.ACTIVE,
                'bank_name': bank.name,
                'bank_country': bank.country,
                'bank_swift_bic': bank.swift_bic
            }
            accounts_data.append(account_data)
        
        # Cache the result
        self._cache[cache_key] = accounts_data
        
        return accounts_data
    
    def get_by_entity_with_bank_info(self, entity_id: int, session: Session) -> List[Dict[str, Any]]:
        """
        Get bank accounts for an entity with bank information.
        
        Args:
            entity_id: Owner entity ID
            session: Database session
            
        Returns:
            List of bank accounts with bank details for the entity
        """
        cache_key = f"bank_accounts:entity_with_bank_info:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with join
        result = session.query(
            BankAccount,
            BankAccount.bank
        ).join(BankAccount.bank).filter(BankAccount.entity_id == entity_id).all()
        
        # Format result
        accounts_data = []
        for account, bank in result:
            account_data = {
                'id': account.id,
                'entity_id': account.entity_id,
                'bank_id': account.bank_id,
                'account_name': account.account_name,
                'account_number': account.account_number,
                'currency': account.currency,
                'is_active': account.status == AccountStatus.ACTIVE,
                'bank_name': bank.name,
                'bank_country': bank.country,
                'bank_swift_bic': bank.swift_bic
            }
            accounts_data.append(account_data)
        
        # Cache the result
        self._cache[cache_key] = accounts_data
        
        return accounts_data
    
    def create(self, account: BankAccount, session: Session) -> BankAccount:
        """
        Create a new bank account.
        
        Args:
            account: BankAccount instance to create
            session: Database session
            
        Returns:
            Created bank account instance
        """
        session.add(account)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_account_caches()
        
        return account
    
    def update(self, account: BankAccount, session: Session) -> BankAccount:
        """
        Update an existing bank account.
        
        Args:
            account: BankAccount instance to update
            session: Database session
            
        Returns:
            Updated bank account instance
        """
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_account_caches()
        
        return account
    
    def delete(self, account: BankAccount, session: Session) -> None:
        """
        Delete a bank account.
        
        Args:
            account: BankAccount instance to delete
            session: Database session
        """
        session.delete(account)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_account_caches()
    
    def exists(self, account_id: int, session: Session) -> bool:
        """
        Check if a bank account exists.
        
        Args:
            account_id: ID of the account to check
            session: Database session
            
        Returns:
            True if account exists, False otherwise
        """
        cache_key = f"bank_account:exists:{account_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        exists = session.query(BankAccount).filter(BankAccount.id == account_id).first() is not None
        
        # Cache the result
        self._cache[cache_key] = exists
        
        return exists
    
    def count_by_entity(self, entity_id: int, session: Session) -> int:
        """
        Count bank accounts for a specific entity.
        
        Args:
            entity_id: Owner entity ID
            session: Database session
            
        Returns:
            Number of bank accounts owned by the entity
        """
        cache_key = f"bank_accounts:count:entity:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(BankAccount).filter(BankAccount.entity_id == entity_id).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def count_by_bank(self, bank_id: int, session: Session) -> int:
        """
        Count bank accounts for a specific bank.
        
        Args:
            bank_id: Bank ID
            session: Database session
            
        Returns:
            Number of bank accounts at the specified bank
        """
        cache_key = f"bank_accounts:count:bank:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(BankAccount).filter(BankAccount.bank_id == bank_id).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def count_by_currency(self, currency: str, session: Session) -> int:
        """
        Count bank accounts with a specific currency.
        
        Args:
            currency: Currency code
            session: Database session
            
        Returns:
            Number of bank accounts with the specified currency
        """
        cache_key = f"bank_accounts:count:currency:{currency}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(BankAccount).filter(BankAccount.currency == currency).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def get_total_count(self, session: Session) -> int:
        """
        Get total count of all bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            Total number of bank accounts
        """
        cache_key = "bank_accounts:total_count"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(BankAccount).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def search(self, search_term: str, session: Session) -> List[BankAccount]:
        """
        Search bank accounts by name or account number.
        
        Args:
            search_term: Search term
            session: Database session
            
        Returns:
            List of matching bank accounts
        """
        if not search_term:
            return []
        
        cache_key = f"bank_accounts:search:{search_term}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with search
        accounts = session.query(BankAccount).filter(
            or_(
                BankAccount.account_name.ilike(f"%{search_term}%"),
                BankAccount.account_number.ilike(f"%{search_term}%")
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = accounts
        
        return accounts
    
    def _clear_bank_account_caches(self) -> None:
        """Clear all bank account-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('bank_account')]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_uniqueness_cache(self, entity_id: int, bank_id: int, account_number: str) -> None:
        """Clear cache for specific uniqueness check to prevent race conditions."""
        cache_key = f"bank_account:unique:{entity_id}:{bank_id}:{account_number}"
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    def check_uniqueness_direct(self, entity_id: int, bank_id: int, account_number: str, session: Session) -> bool:
        """
        Check uniqueness directly in database without caching.
        
        Args:
            entity_id: Owner entity ID
            bank_id: Linked bank ID
            account_number: Account number
            session: Database session
            
        Returns:
            True if unique, False if duplicate exists
        """
        # Direct database query to check uniqueness
        existing = session.query(BankAccount).filter(
            and_(
                BankAccount.entity_id == entity_id,
                BankAccount.bank_id == bank_id,
                BankAccount.account_number == account_number
            )
        ).first()
        
        return existing is None
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
