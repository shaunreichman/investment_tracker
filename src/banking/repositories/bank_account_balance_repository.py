"""
Bank Account Balance Repository.
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccountBalance, BankAccount
from src.banking.enums.bank_account_balance_enums import SortFieldBankAccountBalance
from src.shared.enums.shared_enums import SortOrder, Currency


class BankAccountBalanceRepository:
    """
    Bank Account Balance Repository.

    This repository handles all database operations for bank account balances including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    bank account balance data without direct database access.
    """

    def __init__(self):
        """
        Initialize the bank account balance repository.

        Args:
            None
        """
        pass


    ################################################################################
    # Get Bank Account Balance
    ################################################################################

    def get_bank_account_balances(self, session: Session,
            bank_ids: Optional[List[int]] = None,
            bank_account_ids: Optional[List[int]] = None,
            currencies: Optional[List[Currency]] = None,
            start_date: Optional[date] = None,
            end_date: Optional[date] = None,
            sort_by: SortFieldBankAccountBalance = SortFieldBankAccountBalance.DATE,
            sort_order: SortOrder = SortOrder.ASC) -> List[BankAccountBalance]:
        """
        Get all bank account balances.

        Args:
            session: Database session
            bank_ids: IDs of the bank to filter by (optional)
            bank_account_ids: IDs of the bank account to filter by (optional)
            currencies: Currencies of the bank account balances to filter by (optional)
            start_date: Start date of the bank account balances to filter by (optional)
            end_date: End date of the bank account balances to filter by (optional)
            sort_by: Sort field (optional)
            sort_order: Sort order (optional)

        Returns:
            List of bank account balances
        """
        # Validate sort field
        if sort_by not in SortFieldBankAccountBalance:
            raise ValueError(f"Invalid sort field: {sort_by}")

        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Get all bank account balances
        query = session.query(BankAccountBalance)

        if bank_ids:
            # Filter by bank_id through the bank_account relationship - need to get the bank_account_id from the bank_account relationship
            query = query.filter(BankAccountBalance.bank_account_id.in_(session.query(BankAccount.id).filter(BankAccount.bank_id.in_(bank_ids))))
        if bank_account_ids:
            query = query.filter(BankAccountBalance.bank_account_id.in_(bank_account_ids))
        if currencies:
            query = query.filter(BankAccountBalance.currency.in_([c.value for c in currencies]))
        if start_date:  
            query = query.filter(BankAccountBalance.date >= start_date)
        if end_date:
            query = query.filter(BankAccountBalance.date <= end_date)

        # Apply sorting
        if sort_by == SortFieldBankAccountBalance.DATE:
            query = query.order_by(BankAccountBalance.date.asc() if sort_order == SortOrder.ASC else BankAccountBalance.date.desc())

        bank_account_balances = query.all()

        return bank_account_balances

    def get_bank_account_balance_by_id(self, bank_account_balance_id: int, session: Session) -> Optional[BankAccountBalance]:
        """
        Get a bank account balance by its ID.

        Args:
            bank_account_balance_id: ID of the bank account balance to retrieve
            session: Database session
            
        Returns:
            BankAccountBalance object if found, None otherwise
        """
        # Query database
        bank_account_balance = session.query(BankAccountBalance).filter(BankAccountBalance.id == bank_account_balance_id).first()
        
        return bank_account_balance


    ################################################################################
    # Create Bank Account Balance
    ################################################################################

    def create_bank_account_balance(self, bank_account_balance_data: Dict[str, Any], session: Session) -> BankAccountBalance:
        """
        Create a new bank account balance.

        Args:
            bank_account_balance_data: Dictionary containing bank account balance data
            session: Database session
            
        Returns:
            BankAccountBalance object
        """
        bank_account_balance = BankAccountBalance(**bank_account_balance_data)
        session.add(bank_account_balance)
        session.flush()
        
        return bank_account_balance


    ################################################################################
    # Delete Bank Account Balance
    ################################################################################

    def delete_bank_account_balance(self, bank_account_balance_id: int, session: Session) -> bool:
        """
        Delete a bank account balance.

        Args:
            bank_account_balance_id: ID of the bank account balance to delete
            session: Database session
            
        Returns:
            True if the bank account balance was deleted, False otherwise
        """
        bank_account_balance = self.get_bank_account_balance_by_id(bank_account_balance_id, session)
        if not bank_account_balance:
            return False

        session.delete(bank_account_balance)
        session.flush()
        
        return True