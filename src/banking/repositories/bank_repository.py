"""
Bank Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.banking.enums.bank_enums import BankType, SortFieldBank
from src.shared.enums.shared_enums import SortOrder
from src.banking.models import Bank
from src.shared.enums.shared_enums import Country


class BankRepository:
    """
    Bank Repository.
    
    This repository handles all database operations for banks including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    bank data without direct database access.
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the bank repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl

    ################################################################################
    # Get Banks
    ################################################################################

    def get_banks(self, session: Session,
                    name: Optional[str] = None,
                    country: Optional[Country] = None,
                    bank_type: Optional[BankType] = None,
                    sort_by: SortFieldBank = SortFieldBank.NAME,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List[Bank]:
        """
        Get all banks.

        Args:
            session: Database session
            name: Bank name (optional)
            country: Country code (optional)
            bank_type: Bank type (optional)
            sort_by: Sort field (optional)
            sort_order: Sort order (optional)

        Returns:
            List of banks
            
        Raises:
            ValueError: If sort field is invalid
        """
        cache_key = f"banks:name:{name}:country:{country}:bank_type:{bank_type}:sort_by:{sort_by.value}:sort_order:{sort_order.value}"

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Validate sort field
        if sort_by not in SortFieldBank:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Get all banks
        banks = session.query(Bank)
        if name:
            banks = banks.filter(Bank.name == name)
        if country:
            banks = banks.filter(Bank.country == country)
        if bank_type:
            banks = banks.filter(Bank.bank_type == bank_type.value)

        # Apply sorting
        if sort_by == SortFieldBank.NAME:
            banks = banks.order_by(Bank.name.asc() if sort_order == SortOrder.ASC else Bank.name.desc())
        elif sort_by == SortFieldBank.COUNTRY:
            banks = banks.order_by(Bank.country.asc() if sort_order == SortOrder.ASC else Bank.country.desc())
        elif sort_by == SortFieldBank.TYPE:
            banks = banks.order_by(Bank.bank_type.asc() if sort_order == SortOrder.ASC else Bank.bank_type.desc())
        elif sort_by == SortFieldBank.CREATED_AT:
            banks = banks.order_by(Bank.created_at.asc() if sort_order == SortOrder.ASC else Bank.created_at.desc())

        banks = banks.all()

        # Cache the result
        self._cache[cache_key] = banks
        return banks
    
    def get_bank_by_id(self, bank_id: int, session: Session) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            
        Returns:
            Bank object if found, None otherwise
        """
        cache_key = f"bank:id:{bank_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        bank = session.query(Bank).filter(Bank.id == bank_id).first()
        
        # Cache the result
        if bank:
            self._cache[cache_key] = bank
        
        return bank


    ################################################################################
    # Create Bank
    ################################################################################
    
    def create_bank(self, bank_data: Dict[str, Any], session: Session) -> Bank:
        """
        Create a new bank.
        
        Args:
            bank_data: Dictionary containing bank data
            session: Database session
            
        Returns:
            Created bank instance
        """
        # Create bank object
        bank = Bank(**bank_data)
        session.add(bank)
        session.flush()  # Get the ID without committing
        
        # Clear relevant caches
        self._clear_bank_caches(bank_data.get('id'))
        
        return bank


    ################################################################################
    # Delete Bank
    ################################################################################
    
    def delete_bank(self, bank_id: int, session: Session) -> bool:
        """
        Delete a bank.
        
        Args:
            bank_id: ID of the bank to delete
            session: Database session
        """
        bank = self.get_bank_by_id(bank_id, session)
        if not bank:
            return False
        
        session.delete(bank)
        session.flush()
        
        # Clear relevant caches
        self._clear_bank_caches(bank_id)

        return True
        
    
    def _clear_bank_caches(self, bank_id: int) -> None:
        """Clear all bank-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('bank') and key != f"bank:id:{bank_id}"]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
