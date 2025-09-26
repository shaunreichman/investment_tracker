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
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            List of bank accounts
        """
        return self.bank_account_repository.get_bank_accounts(session, bank_id, entity_id, account_name, currency, status, account_type, sort_by, sort_order)

    def get_bank_account_by_id(self, account_id: int, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            account_id: ID of the account to retrieve
            session: Database session

        Returns:
            BankAccount: Bank account instance if found, None otherwise
        """
        return self.bank_account_repository.get_bank_account_by_id(account_id, session)


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
        """
        # Validate Bank exists
        from src.banking.repositories.bank_repository import BankRepository
        bank_repository = BankRepository()
        bank = bank_repository.get_bank_by_id(bank_id, session)
        if not bank:
            raise ValueError(f"Bank not found")

        # Validate Entity exists
        from src.entity.repositories.entity_repository import EntityRepository
        entity_repository = EntityRepository()
        entity = entity_repository.get_entity_by_id(bank_account_data['entity_id'], session)
        if not entity:
            raise ValueError(f"Entity not found")

        processed_data = {
            **bank_account_data,
            'bank_id': bank_id
        }

        # Set the bank account status to INACTIVE on creation
        processed_data['status'] = BankAccountStatus.INACTIVE

        bank_account = self.bank_account_repository.create_bank_account(processed_data, session)
        if not bank_account:
            raise ValueError(f"Failed to create bank account")

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
            raise ValueError(f"Bank account not found")

        # Check for dependent fund event cash flows
        validation_errors = self.banking_validation_service.validate_bank_account_deletion(bank_account_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")

        # Delete bank account through repository
        success = self.bank_account_repository.delete_bank_account(bank_account_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank account")

        return success