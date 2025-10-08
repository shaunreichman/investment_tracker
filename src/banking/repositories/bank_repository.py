"""
Bank Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload

from src.banking.enums.bank_enums import BankType, SortFieldBank
from src.shared.enums.shared_enums import SortOrder
from src.banking.models import Bank, BankAccount
from src.shared.enums.shared_enums import Country


class BankRepository:
    """
    Bank Repository.
    
    This repository handles all database operations for banks including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    bank data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the bank repository.
        
        Args:
            None
        """
        pass

    ################################################################################
    # Get Banks
    ################################################################################

    def get_banks(self, session: Session,
                    names: Optional[List[str]] = None,
                    countries: Optional[List[Country]] = None,
                    bank_types: Optional[List[BankType]] = None,
                    sort_by: SortFieldBank = SortFieldBank.NAME,
                    sort_order: SortOrder = SortOrder.ASC,
                    include_bank_accounts: Optional[bool] = False,
                    include_bank_account_balances: Optional[bool] = False
    ) -> List[Bank]:
        """
        Get all banks.

        Args:
            session: Database session
            names: Bank names (optional)
            countries: Country codes (optional)
            bank_types: Bank types (optional)
            sort_by: Sort field (optional)
            sort_order: Sort order (optional)
            include_bank_accounts: Whether to include bank accounts (optional)
            include_bank_account_balances: Whether to include bank account balances (optional, requires include_bank_accounts=True)

        Returns:
            List of banks
            
        Raises:
            ValueError: If sort field is invalid
        """
        # Validate sort field
        if sort_by not in SortFieldBank:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Validate parameter dependencies
        if include_bank_account_balances and not include_bank_accounts:
            raise ValueError("include_bank_account_balances requires include_bank_accounts to be True")

        # Get all banks
        query = session.query(Bank)
        
        # Add eager loading for relationships if requested
        if include_bank_accounts:
            query = query.options(selectinload(Bank.bank_accounts))
        if include_bank_account_balances:
            query = query.options(selectinload(Bank.bank_accounts).selectinload(BankAccount.bank_account_balances))

        if names:
            query = query.filter(Bank.name.in_(names))
        if countries:
            query = query.filter(Bank.country.in_([c.value for c in countries]))
        if bank_types:
            query = query.filter(Bank.bank_type.in_([bt.value for bt in bank_types]))

        # Apply sorting
        if sort_by == SortFieldBank.NAME:
            query = query.order_by(Bank.name.asc() if sort_order == SortOrder.ASC else Bank.name.desc())
        elif sort_by == SortFieldBank.COUNTRY:
            query = query.order_by(Bank.country.asc() if sort_order == SortOrder.ASC else Bank.country.desc())
        elif sort_by == SortFieldBank.TYPE:
            query = query.order_by(Bank.bank_type.asc() if sort_order == SortOrder.ASC else Bank.bank_type.desc())
        elif sort_by == SortFieldBank.CREATED_AT:
            query = query.order_by(Bank.created_at.asc() if sort_order == SortOrder.ASC else Bank.created_at.desc())

        banks = query.all()

        return banks
    
    def get_bank_by_id(self, bank_id: int, session: Session, include_bank_accounts: Optional[bool] = False, include_bank_account_balances: Optional[bool] = False) -> Optional[Bank]:
        """
        Get a bank by its ID.
        
        Args:
            bank_id: ID of the bank to retrieve
            session: Database session
            include_bank_accounts: Whether to include bank accounts (optional)
            include_bank_account_balances: Whether to include bank account balances (optional, requires include_bank_accounts=True)

        Returns:
            Bank object if found, None otherwise
        """
        # Validate parameter dependencies
        if include_bank_account_balances and not include_bank_accounts:
            raise ValueError("include_bank_account_balances requires include_bank_accounts to be True")

        # Query database
        query = session.query(Bank).filter(Bank.id == bank_id)
        
        # Add eager loading for relationships if requested
        if include_bank_accounts:
            query = query.options(selectinload(Bank.bank_accounts))
        if include_bank_account_balances:
            query = query.options(selectinload(Bank.bank_accounts).selectinload(BankAccount.bank_account_balances))

        bank = query.first()

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
        
        return True