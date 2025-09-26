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

from src.banking.models import BankAccount
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.shared.enums.shared_enums import Currency, SortOrder


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


    ################################################################################
    # Get Bank Account
    ################################################################################

    def get_bank_accounts(self, session: Session,
            bank_id: Optional[int] = None,
            entity_id: Optional[int] = None,
            account_name: Optional[str] = None,
            currency: Optional[Currency] = None,
            status: Optional[BankAccountStatus] = None,
            account_type: Optional[BankAccountType] = None,
            sort_by: SortFieldBankAccount = SortFieldBankAccount.CREATED_AT,
            sort_order: SortOrder = SortOrder.ASC
    ) -> List[BankAccount]:
        """
        Get all bank accounts.
        
        Args:
            session: Database session
            bank_id: ID of the bank to retrieve
            entity_id: ID of the entity to retrieve
            account_name: Name of the bank accounts to retrieve
            currency: Currency of the bank accounts to retrieve
            status: Status of the bank accounts to retrieve
            account_type: Type of the bank accounts to retrieve
        Returns:
            List of bank accounts
        """
        cache_key = f"bank_accounts:bank_id:{bank_id}:entity_id:{entity_id}:account_name:{account_name}:currency:{currency}:status:{status}:account_type:{account_type}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Validate sort field
        if sort_by not in SortFieldBankAccount:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Get all bank accounts
        bank_accounts = session.query(BankAccount)
        if bank_id:
            bank_accounts = bank_accounts.filter(BankAccount.bank_id == bank_id)
        if entity_id:
            bank_accounts = bank_accounts.filter(BankAccount.entity_id == entity_id)
        if account_name:
            bank_accounts = bank_accounts.filter(BankAccount.account_name.ilike(f"%{account_name}%"))
        if currency:
            bank_accounts = bank_accounts.filter(BankAccount.currency == currency.value)
        if status:
            bank_accounts = bank_accounts.filter(BankAccount.status == status.value)
        if account_type:
            bank_accounts = bank_accounts.filter(BankAccount.account_type == account_type.value)

        # Apply sorting
        if sort_by == SortFieldBankAccount.NAME:
            bank_accounts = bank_accounts.order_by(BankAccount.account_name.asc() if sort_order == SortOrder.ASC else BankAccount.account_name.desc())
        elif sort_by == SortFieldBankAccount.ACCOUNT_NUMBER:
            bank_accounts = bank_accounts.order_by(BankAccount.account_number.asc() if sort_order == SortOrder.ASC else BankAccount.account_number.desc())
        elif sort_by == SortFieldBankAccount.CURRENCY:
            bank_accounts = bank_accounts.order_by(BankAccount.currency.asc() if sort_order == SortOrder.ASC else BankAccount.currency.desc())
        elif sort_by == SortFieldBankAccount.STATUS:
            bank_accounts = bank_accounts.order_by(BankAccount.status.asc() if sort_order == SortOrder.ASC else BankAccount.status.desc())
        elif sort_by == SortFieldBankAccount.CREATED_AT:
            bank_accounts = bank_accounts.order_by(BankAccount.created_at.asc() if sort_order == SortOrder.ASC else BankAccount.created_at.desc())

        bank_accounts = bank_accounts.all()

        # Cache the result
        self._cache[cache_key] = bank_accounts

        return bank_accounts
    
    def get_bank_account_by_id(self, bank_account_id: int, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            bank_account_id: ID of the account to retrieve
            session: Database session
            
        Returns:
            BankAccount object if found, None otherwise
        """
        cache_key = f"bank_account:{bank_account_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        account = session.query(BankAccount).filter(BankAccount.id == bank_account_id).first()
        
        # Cache the result
        if account:
            self._cache[cache_key] = account
        
        return account


    ################################################################################
    # Create Bank Account
    ################################################################################
    
    def create_bank_account(self, bank_account_data: Dict[str, Any], session: Session) -> BankAccount:
        """
        Create a new bank account.
        
        Args:
            bank_account_data: Dictionary containing bank account data
            session: Database session
        """
        bank_account = BankAccount(**bank_account_data)
        session.add(bank_account)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_account_caches()
        
        return bank_account


    ################################################################################
    # Delete Bank Account
    ################################################################################
    
    def delete_bank_account(self, bank_account_id: int, session: Session) -> bool:
        """
        Delete a bank account.
        
        Args:
            bank_account_id: ID of the bank account to delete
            session: Database session
        """
        bank_account = self.get_bank_account_by_id(bank_account_id, session)
        if not bank_account:
            return False

        session.delete(bank_account)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_account_caches()

        return True


    ################################################################################
    # Clear Cache
    ################################################################################
    
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
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
