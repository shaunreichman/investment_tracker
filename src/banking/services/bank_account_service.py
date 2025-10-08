"""
Bank Account Service.
"""

from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.shared.enums.shared_enums import SortOrder, Currency


class BankAccountService:
    """
    Service for handling bank account operations and business logic.
    This module provides the BankAccountService class, which handles bank account operations and business logic.
    The service provides clean separation of concerns for:
    - Bank account retrieval
    - Bank account creation
    - Bank account deletion with dependency checking

    The service uses the BankingValidationService to validate bank accounts and the BankAccountRepository to perform CRUD operations.
    The service also uses the BankAccountBalanceService to update the balance of a bank account.

    The service is used by the BankingController to handle bank account operations.
    """
    
    def __init__(self):
        """
        Initialize the BankAccountService.
        
        Args:
            banking_validation_service: Banking validation service to use. If None, creates a new one.
            bank_account_repository: Bank account repository to use. If None, creates a new one.
        """
        self.banking_validation_service = BankingValidationService()
        self.bank_account_repository = BankAccountRepository()


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
            sort_by: SortFieldBankAccount = SortFieldBankAccount.CREATED_AT,
            sort_order: SortOrder = SortOrder.ASC,
            include_bank_account_balances: Optional[bool] = False
    ) -> List[BankAccount]:
        """
        Get all bank accounts.
        
        Args:
            session: Database session
            bank_ids: List of IDs of the bank to retrieve
            entity_ids: List of IDs of the entity to retrieve
            account_names: Names of the bank accounts to retrieve
            currencies: Currencies of the bank accounts to retrieve
            statuses: Statuses of the bank accounts to retrieve
            account_types: Types of the bank accounts to retrieve
            sort_by: Sort field
            sort_order: Sort order
            include_bank_account_balances: Whether to include bank account balances

        Returns:
            List of bank accounts
        """
        return self.bank_account_repository.get_bank_accounts(session, bank_ids, entity_ids, account_names, currencies, statuses, account_types, sort_by, sort_order, include_bank_account_balances)

    def get_bank_account_by_id(self, account_id: int, session: Session, include_bank_account_balances: Optional[bool] = False) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            account_id: ID of the account to retrieve
            session: Database session
            include_bank_account_balances: Whether to include bank account balances

        Returns:
            BankAccount: Bank account instance if found, None otherwise
        """
        return self.bank_account_repository.get_bank_account_by_id(account_id, session, include_bank_account_balances)


    ################################################################################
    # Create Bank Account
    ################################################################################

    def create_bank_account(self, bank_id: int, bank_account_data: Dict[str, Any], session: Session) -> BankAccount:
        """
        Create a new bank account.
        
        Args:
            bank_id: ID of the bank to add bank account to
            bank_account_data: Dictionary containing bank account data
            session: Database session

        Returns:
            BankAccount: The created bank account instance

        Raises:
            ValueError: If validation fails
        """
        # Validate Bank exists
        from src.banking.repositories.bank_repository import BankRepository
        bank_repository = BankRepository()
        bank = bank_repository.get_bank_by_id(bank_id, session)
        if not bank:
            raise ValueError(f"Bank with ID {bank_id} not found")

        # Validate Entity exists
        from src.entity.repositories.entity_repository import EntityRepository
        entity_repository = EntityRepository()
        entity = entity_repository.get_entity_by_id(bank_account_data['entity_id'], session)
        if not entity:
            raise ValueError(f"Entity with ID {bank_account_data['entity_id']} not found")

        processed_data = {
            **bank_account_data,
            'bank_id': bank_id,
            'status': BankAccountStatus.INACTIVE # Set the bank account status to INACTIVE on creation
        }

        bank_account = self.bank_account_repository.create_bank_account(processed_data, session)
        if not bank_account:
            raise ValueError(f"Failed to create bank account with name '{processed_data.get('account_name', 'unknown')}' for bank ID {bank_id}")

        # Update bank current count

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

        Returns:
            bool: True if bank account was deleted, False otherwise
        """
        bank_account = self.bank_account_repository.get_bank_account_by_id(bank_account_id, session)
        if not bank_account:
            raise ValueError(f"Bank account with ID {bank_account_id} not found")

        # Check for dependent fund event cash flows
        validation_errors = self.banking_validation_service.validate_bank_account_deletion(bank_account_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed for bank account with ID {bank_account_id}: {validation_errors}")

        # Delete bank account through repository
        success = self.bank_account_repository.delete_bank_account(bank_account_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank account with ID {bank_account_id}")
        
        # Update bank current count

        return success