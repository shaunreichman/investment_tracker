"""
Bank Account Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, selectinload

from src.banking.models import BankAccount
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.shared.enums.shared_enums import Currency, SortOrder


class BankAccountRepository:
    """
    Bank Account Repository.
    
    This repository handles all database operations for bank accounts including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    bank account data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the bank account repository.
        
        Args:
            None
        """
        pass


    ################################################################################
    # Get Bank Account
    ################################################################################

    def get_bank_accounts(self, session: Session,
            bank_ids: Optional[List[int]] = None,
            entity_ids: Optional[List[int]] = None,
            account_names: Optional[List[str]] = None,
            currencies: Optional[List[Currency]] = None,
            statuses: Optional[List[BankAccountStatus]] = None,
            account_types: Optional[List[BankAccountType]] = None,
            sort_by: Optional[SortFieldBankAccount] = SortFieldBankAccount.CREATED_AT,
            sort_order: Optional[SortOrder] = SortOrder.ASC,
            include_bank_account_balances: Optional[bool] = False
    ) -> List[BankAccount]:
        """
        Get all bank accounts.
        
        Args:
            session: Database session
            bank_ids: IDs of the bank to retrieve (optional)
            entity_ids: IDs of the entity to retrieve (optional)
            account_names: Name of the bank accounts to retrieve (optional)
            currencies: Currency of the bank accounts to retrieve (optional)
            statuses: Status of the bank accounts to retrieve (optional)
            account_types: Type of the bank accounts to retrieve (optional)
            sort_by: Sort field (optional)
            sort_order: Sort order (optional)
            include_bank_account_balances: Whether to include bank account balances (optional)

        Returns:
            List of bank accounts
        """
        # Use defaults if None is explicitly passed (overrides function default)
        if sort_by is None:
            sort_by = SortFieldBankAccount.CREATED_AT
        if sort_order is None:
            sort_order = SortOrder.ASC
        
        # Validate sort field
        if sort_by not in SortFieldBankAccount:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Get all bank accounts
        query = session.query(BankAccount)

        # Add eager loading for relationships if requested
        if include_bank_account_balances:
            query = query.options(selectinload(BankAccount.bank_account_balances))

        if bank_ids:
            query = query.filter(BankAccount.bank_id.in_(bank_ids))
        if entity_ids:
            query = query.filter(BankAccount.entity_id.in_(entity_ids))
        if account_names:
            query = query.filter(BankAccount.account_name.in_(account_names))
        if currencies:
            query = query.filter(BankAccount.currency.in_([c.value for c in currencies]))
        if statuses:
            query = query.filter(BankAccount.status.in_([s.value for s in statuses]))
        if account_types:
            query = query.filter(BankAccount.account_type.in_([at.value for at in account_types]))

        # Apply sorting
        if sort_by == SortFieldBankAccount.NAME:
            query = query.order_by(BankAccount.account_name.asc() if sort_order == SortOrder.ASC else BankAccount.account_name.desc())
        elif sort_by == SortFieldBankAccount.ACCOUNT_NUMBER:
            query = query.order_by(BankAccount.account_number.asc() if sort_order == SortOrder.ASC else BankAccount.account_number.desc())
        elif sort_by == SortFieldBankAccount.CURRENCY:
            query = query.order_by(BankAccount.currency.asc() if sort_order == SortOrder.ASC else BankAccount.currency.desc())
        elif sort_by == SortFieldBankAccount.STATUS:
            query = query.order_by(BankAccount.status.asc() if sort_order == SortOrder.ASC else BankAccount.status.desc())
        elif sort_by == SortFieldBankAccount.CREATED_AT:
            query = query.order_by(BankAccount.created_at.asc() if sort_order == SortOrder.ASC else BankAccount.created_at.desc())

        bank_accounts = query.all()

        return bank_accounts
    
    def get_bank_account_by_id(self, bank_account_id: int, session: Session, include_bank_account_balances: Optional[bool] = False) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            bank_account_id: ID of the account to retrieve
            session: Database session
            include_bank_account_balances: Whether to include bank account balances (optional)
            
        Returns:
            BankAccount object if found, None otherwise
        """
        # Query database
        query = session.query(BankAccount).filter(BankAccount.id == bank_account_id)

        # Add eager loading for relationships if requested
        if include_bank_account_balances:
            query = query.options(selectinload(BankAccount.bank_account_balances))

        account = query.first()
        
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
        
        return True