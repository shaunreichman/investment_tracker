"""
Bank Account Service.

This service extracts bank account operations and business logic from the BankAccount model
to provide clean separation of concerns and improved testability.

Extracted functionality:
- Bank account creation with validation
- Bank account updates with validation
- Bank account deletion with validation
- Bank account business rule enforcement
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
    
    This service provides clean separation of concerns for:
    - Bank account creation with comprehensive validation
    - Bank account updates with validation and business rules
    - Bank account deletion with dependency checking
    - Bank account business rule enforcement
    """
    
    def __init__(self, validation_service: Optional[BankingValidationService] = None, bank_account_repository: Optional[BankAccountRepository] = None):
        """
        Initialize the BankAccountService.
        
        Args:
            validation_service: Validation service to use. If None, creates a new one.
            bank_account_repository: Bank account repository to use. If None, creates a new one.
        """
        self.validation_service = validation_service or BankingValidationService()
        self.bank_account_repository = bank_account_repository or BankAccountRepository()


    ################################################################################
    # Get Bank Account
    ################################################################################

    def get_bank_accounts(self, session: Session,
            bank_id: Optional[int] = None,
            entity_id: Optional[int] = None,
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
            currency: Currency of the bank accounts to retrieve
            status: Status of the bank accounts to retrieve
            account_type: Type of the bank accounts to retrieve
            sort_by: Sort field
            sort_order: Sort order

        Returns:
            List of bank accounts
        """
        return self.bank_account_repository.get_bank_accounts(session, bank_id, entity_id, currency, status, account_type, sort_by, sort_order)

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

    def create_bank_account(self, bank_account_data: Dict[str, Any], session: Session) -> BankAccount:
        """
        Create a new bank account.
        
        Args:
            bank_account_data: Dictionary containing bank account data
            session: Database session
        """
        required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number', 'currency']
        for field in required_fields:
            if field not in bank_account_data:
                raise ValueError(f"Required field '{field}' is missing")

        # Validate Bank exists
        from src.banking.repositories.bank_repository import BankRepository
        bank_repository = BankRepository()
        bank = bank_repository.get_bank_by_id(bank_account_data['bank_id'], session)
        if not bank:
            raise ValueError(f"Bank not found")

        # Validate Entity exists
        from src.entity.repositories.entity_repository import EntityRepository
        entity_repository = EntityRepository()
        entity = entity_repository.get_entity_by_id(bank_account_data['entity_id'], session)
        if not entity:
            raise ValueError(f"Entity not found")

        processed_data = bank_account_data.copy()
        if 'currency' in processed_data and isinstance(processed_data['currency'], str):
            try:
                processed_data['currency'] = Currency(processed_data['currency'])
            except ValueError:
                raise ValueError(f"Invalid currency: {processed_data['currency']}. Must be one of: {[c.value for c in Currency]}")
        if 'account_type' in processed_data and isinstance(processed_data['account_type'], str):
            try:
                processed_data['account_type'] = BankAccountType(processed_data['account_type'])
            except ValueError:
                raise ValueError(f"Invalid account type: {processed_data['account_type']}. Must be one of: {[t.value for t in BankAccountType]}")

        # Set the bank account status to INACTIVE on creation
        processed_data['status'] = BankAccountStatus.INACTIVE

        bank_account = self.bank_account_repository.create_bank_account(bank_account_data, session)
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
        validation_errors = self.validation_service.validate_bank_account_deletion(bank_account_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")

        # Delete bank account through repository
        success = self.bank_account_repository.delete_bank_account(bank_account_id, session)
        if not success:
            raise ValueError(f"Failed to delete bank account")

        return True