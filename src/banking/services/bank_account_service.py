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

from typing import Optional, Dict, Any, List, Union
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from src.banking.events.orchestrator import BankingUpdateOrchestrator
from src.banking.events.registry import BankingEventHandlerRegistry
from src.banking.enums import Currency, AccountStatus


class BankAccountService:
    """
    Service for handling bank account operations and business logic.
    
    This service provides clean separation of concerns for:
    - Bank account creation with comprehensive validation
    - Bank account updates with validation and business rules
    - Bank account deletion with dependency checking
    - Bank account business rule enforcement
    """
    
    def __init__(self, validation_service: Optional[BankingValidationService] = None, bank_account_repository: Optional[BankAccountRepository] = None, cash_flow_repository: Optional[FundEventCashFlowRepository] = None, event_orchestrator: Optional[BankingUpdateOrchestrator] = None, event_registry: Optional[BankingEventHandlerRegistry] = None):
        """
        Initialize the BankAccountService.
        
        Args:
            validation_service: Validation service to use. If None, creates a new one.
            bank_account_repository: Bank account repository to use. If None, creates a new one.
            cash_flow_repository: Fund event cash flow repository to use. If None, creates a new one.
            event_orchestrator: Event orchestrator to use. If None, creates a new one.
            event_registry: Event handler registry to use. If None, creates a new one.
        """
        self.validation_service = validation_service or BankingValidationService()
        self.bank_account_repository = bank_account_repository or BankAccountRepository()
        self.cash_flow_repository = cash_flow_repository or FundEventCashFlowRepository()
        self.event_orchestrator = event_orchestrator or BankingUpdateOrchestrator()
        self.event_registry = event_registry or BankingEventHandlerRegistry()
    
    # ============================================================================
    # BANK ACCOUNT CREATION
    # ============================================================================
    
    def create_bank_account(
        self,
        *,
        entity_id: int,
        bank_id: int,
        account_name: str,
        account_number: str,
        currency: Union[str, Currency],
        status: AccountStatus = AccountStatus.ACTIVE,
        session: Optional[Session] = None
    ) -> BankAccount:
        """
        Create a new bank account with comprehensive validation.
        
        This method extracts the business logic from BankAccount.create() to provide
        clean separation of concerns and improved testability.
        
        Args:
            entity_id: Owner entity ID
            bank_id: Linked bank ID
            account_name: Human-readable account name/label
            account_number: Account number stored as provided
            currency: ISO-4217 currency code (string or Currency enum)
            status: Account status (AccountStatus enum)
            session: Database session
            
        Returns:
            BankAccount: The created bank account instance
            
        Raises:
            ValueError: If validation fails
        """
        # Validate all input data
        self.validation_service.validate_entity_exists_or_raise(entity_id, session)
        self.validation_service.validate_bank_exists_or_raise(bank_id, session)
        self.validation_service.validate_account_name_or_raise(account_name)
        self.validation_service.validate_account_number_or_raise(account_number)
        self.validation_service.validate_currency_code_or_raise(currency)
        self.validation_service.validate_account_status_or_raise(status)
        
        # Normalize inputs to enums
        normalized_currency = self.validation_service.normalize_currency(currency)
        normalized_status = self.validation_service.normalize_account_status(status)
        
        # Validate uniqueness
        self.validation_service.validate_bank_account_uniqueness_or_raise(
            entity_id, bank_id, account_number, session
        )
        
        # Create bank account instance
        account = BankAccount(
            entity_id=entity_id,
            bank_id=bank_id,
            account_name=account_name.strip(),
            account_number=account_number.strip(),
            currency=normalized_currency,
            status=normalized_status
        )
        
        # Use repository to create account
        created_account = self.bank_account_repository.create(account, session)
        
        # Process through event orchestrator to publish domain events
        event_data = {
            'event_type': 'bank_account_created',
            'entity_id': created_account.entity_id,
            'bank_id': created_account.bank_id,
            'account_name': created_account.account_name,
            'account_number': created_account.account_number,
            'currency': created_account.currency,
            'status': created_account.status
        }
        
        self.event_orchestrator.process_banking_event(event_data, session, created_account)
        
        return created_account
    
    # ============================================================================
    # BANK ACCOUNT UPDATES
    # ============================================================================
    
    def update_bank_account(
        self,
        account_id: int,
        data: Dict[str, Any],
        session: Session
    ) -> BankAccount:
        """
        Update a bank account with comprehensive validation.
        
        This method extracts the business logic from the controller to provide
        clean separation of concerns and improved testability.
        
        Args:
            account_id: ID of the account to update
            data: Update data dictionary
            session: Database session
            
        Returns:
            BankAccount: The updated bank account instance
            
        Raises:
            ValueError: If validation fails
            RuntimeError: If account not found
        """
        # Get existing account
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError("Bank account not found")
        
        # Validate all update data
        self.validation_service.validate_bank_account_data(data, session, exclude_id=account_id)
        
        # Update fields
        if 'account_name' in data:
            account.account_name = data['account_name'].strip()
        
        if 'account_number' in data:
            account.account_number = data['account_number'].strip()
        
        if 'currency' in data:
            # Validate and normalize currency
            self.validation_service.validate_currency_code_or_raise(data['currency'])
            normalized_currency = self.validation_service.normalize_currency(data['currency'])
            account.currency = normalized_currency
        
        if 'status' in data:
            # Validate and normalize account status
            self.validation_service.validate_account_status_or_raise(data['status'])
            normalized_status = self.validation_service.normalize_account_status(data['status'])
            account.status = normalized_status
        
        # Process through event orchestrator to publish domain events
        event_data = {
            'event_type': 'bank_account_updated',
            'account_id': account_id,
            'entity_id': account.entity_id,
            'bank_id': account.bank_id,
            'changes': data,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'currency': account.currency,
            'status': account.status
        }
        
        self.event_orchestrator.process_banking_event(event_data, session, account)
        
        return account
    
    # ============================================================================
    # BANK ACCOUNT DELETION
    # ============================================================================
    
    def delete_bank_account(
        self,
        account_id: int,
        session: Session
    ) -> bool:
        """
        Delete a bank account with dependency checking.
        
        This method extracts the business logic from the controller to provide
        clean separation of concerns and improved testability.
        
        Args:
            account_id: ID of the account to delete
            session: Database session
            
        Returns:
            bool: True if deleted successfully
            
        Raises:
            RuntimeError: If account not found or has dependencies
        """
        # Get existing account
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError("Bank account not found")
        
        # Check for dependent fund events (future enhancement)
        if self._has_dependent_fund_events(account_id, session):
            raise RuntimeError("Cannot delete bank account with dependent fund events")
        
        # Process through event orchestrator to publish domain events BEFORE deletion
        event_data = {
            'event_type': 'bank_account_deleted',
            'account_id': account_id,
            'entity_id': account.entity_id,
            'bank_id': account.bank_id,
            'account_name': account.account_name,
            'account_number': account.account_number,
            'currency': account.currency,
            'status': account.status
        }
        
        self.event_orchestrator.process_banking_event(event_data, session, account)
        
        # Delete account through repository
        self.bank_account_repository.delete(account, session)
        
        return True
    
    # ============================================================================
    # BANK ACCOUNT QUERIES
    # ============================================================================
    
    def get_bank_account_by_id(self, account_id: int, session: Session) -> Optional[BankAccount]:
        """
        Get a bank account by its ID.
        
        Args:
            account_id: ID of the account to retrieve
            session: Database session
            
        Returns:
            BankAccount: Account instance if found, None otherwise
        """
        return self.bank_account_repository.get_by_id(account_id, session)
    
    def get_bank_account_by_unique(
        self,
        *,
        entity_id: int,
        bank_id: int,
        account_number: str,
        session: Session
    ) -> Optional[BankAccount]:
        """
        Get a bank account by unique combination of entity, bank, and account number.
        
        Args:
            entity_id: Owner entity ID
            bank_id: Linked bank ID
            account_number: Account number
            session: Database session
            
        Returns:
            BankAccount: Account instance if found, None otherwise
        """
        return self.bank_account_repository.get_by_unique(entity_id, bank_id, account_number, session)
    
    def get_all_bank_accounts(self, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            List[BankAccount]: List of all bank accounts
        """
        return self.bank_account_repository.get_all(session)
    
    def get_bank_accounts_by_entity(self, entity_id: int, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts for a specific entity.
        
        Args:
            entity_id: Entity ID to filter by
            session: Database session
            
        Returns:
            List[BankAccount]: List of bank accounts for the entity
        """
        return self.bank_account_repository.get_by_entity(entity_id, session)
    
    def get_bank_accounts_by_bank(self, bank_id: int, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts for a specific bank.
        
        Args:
            bank_id: Bank ID to filter by
            session: Database session
            
        Returns:
            List[BankAccount]: List of bank accounts for the bank
        """
        return self.bank_account_repository.get_by_bank(bank_id, session)
    
    def get_bank_accounts_by_currency(self, currency: str, session: Session) -> List[BankAccount]:
        """
        Get all bank accounts with a specific currency.
        
        Args:
            currency: Currency code to filter by
            session: Database session
            
        Returns:
            List[BankAccount]: List of bank accounts with the currency
        """
        return self.bank_account_repository.get_by_currency(currency, session)
    
    def get_active_bank_accounts(self, session: Session) -> List[BankAccount]:
        """
        Get all active bank accounts.
        
        Args:
            session: Database session
            
        Returns:
            List[BankAccount]: List of active bank accounts
        """
        return self.bank_account_repository.get_active_accounts(session)
    
    # ============================================================================
    # DEPENDENCY CHECKING
    # ============================================================================
    
    def _has_dependent_fund_events(self, account_id: int, session: Session) -> bool:
        """
        Check if a bank account has dependent fund events.
        
        Args:
            account_id: Account ID to check
            session: Database session
            
        Returns:
            bool: True if account has dependent fund events
        """
        # Use repository to check for dependent fund events
        return self.cash_flow_repository.has_cash_flows_for_bank_account(account_id, session)
    
    def get_dependent_fund_events_count(self, account_id: int, session: Session) -> int:
        """
        Get the count of dependent fund events for a bank account.
        
        Args:
            account_id: Account ID to check
            session: Database session
            
        Returns:
            int: Number of dependent fund events
        """
        # Use repository to get count of dependent fund events
        return self.cash_flow_repository.count_by_bank_account(account_id, session)
    
    # ============================================================================
    # BUSINESS RULE ENFORCEMENT
    # ============================================================================
    
    def can_delete_bank_account(self, account_id: int, session: Session) -> tuple[bool, str]:
        """
        Check if a bank account can be deleted based on business rules.
        
        Args:
            account_id: Account ID to check
            session: Database session
            
        Returns:
            tuple[bool, str]: (can_delete, reason_if_not)
        """
        # Check if account exists
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            return False, "Bank account not found"
        
        # Check for dependent fund events
        event_count = self.get_dependent_fund_events_count(account_id, session)
        if event_count > 0:
            return False, f"Bank account has {event_count} dependent fund events"
        
        return True, "Bank account can be deleted"
    
    def validate_bank_account_for_update(self, account_id: int, data: Dict[str, Any], session: Session) -> tuple[bool, str]:
        """
        Validate if a bank account can be updated with the given data.
        
        Args:
            account_id: Account ID to validate
            data: Update data to validate
            session: Database session
            
        Returns:
            tuple[bool, str]: (can_update, reason_if_not)
        """
        try:
            # Check if account exists
            account = self.get_bank_account_by_id(account_id, session)
            if not account:
                return False, "Bank account not found"
            
            # Validate update data
            self.validation_service.validate_bank_account_data(data, session, exclude_id=account_id)
            
            return True, "Bank account can be updated"
            
        except ValueError as e:
            return False, str(e)
        except Exception as e:
            return False, f"Validation error: {str(e)}"
    
    # ============================================================================
    # ACCOUNT STATUS MANAGEMENT
    # ============================================================================
    
    def activate_account(self, account_id: int, session: Session) -> BankAccount:
        """
        Activate a bank account.
        
        Args:
            account_id: ID of the account to activate
            session: Database session
            
        Returns:
            BankAccount: The updated account instance
            
        Raises:
            RuntimeError: If account not found
        """
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError("Bank account not found")
        
        account.status = AccountStatus.ACTIVE
        
        return account
    
    def suspend_account(self, account_id: int, session: Session) -> BankAccount:
        """
        Suspend a bank account.
        
        Args:
            account_id: ID of the account to suspend
            session: Database session
            
        Returns:
            BankAccount: The updated account instance
            
        Raises:
            RuntimeError: If account not found
        """
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError("Bank account not found")
        
        account.status = AccountStatus.SUSPENDED
        
        return account
    
    def toggle_account_status(self, account_id: int, session: Session) -> BankAccount:
        """
        Toggle the account status between ACTIVE and SUSPENDED.
        
        Args:
            account_id: ID of the account to toggle
            session: Database session
            
        Returns:
            BankAccount: The updated account instance
            
        Raises:
            RuntimeError: If account not found
        """
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError("Bank account not found")
        
        account.status = AccountStatus.SUSPENDED if account.status == AccountStatus.ACTIVE else AccountStatus.ACTIVE
        
        return account
    
    # ============================================================================
    # BANK ACCOUNT EVENT PROCESSING
    # ============================================================================
    
    def add_bank_account_event(self, account_id: int, event_data: Dict[str, Any], session: Session) -> Dict[str, Any]:
        """
        Add a bank account event using the event handler system.
        
        This method follows the same pattern as fund services for consistency.
        
        Args:
            account_id: ID of the bank account
            event_data: Dictionary containing event data
            session: Database session
            
        Returns:
            Dict[str, Any]: Result data from event processing
            
        Raises:
            ValueError: If required fields are missing
            RuntimeError: If event processing fails
        """
        # Get the account first
        account = self.get_bank_account_by_id(account_id, session)
        if not account:
            raise RuntimeError(f"Bank account with ID {account_id} not found")
        
        # Add account_id to event data
        event_data['account_id'] = account_id
        
        # Process the event through the orchestrator
        try:
            result = self.event_orchestrator.process_banking_event(event_data, session, account)
            return result
            
        except Exception as e:
            raise RuntimeError(f"Failed to process bank account event: {str(e)}")
    
    def add_account_status_change_event(self, account_id: int, old_status: AccountStatus, new_status: AccountStatus, session: Session) -> Dict[str, Any]:
        """
        Add an account status change event.
        
        Args:
            account_id: ID of the bank account
            old_status: Previous account status
            new_status: New account status
            session: Database session
            
        Returns:
            Dict[str, Any]: Result data from event processing
        """
        event_data = {
            'event_type': 'account_status_changed',
            'old_status': old_status,
            'new_status': new_status
        }
        
        return self.add_bank_account_event(account_id, event_data, session)
    
    def add_currency_change_event(self, account_id: int, old_currency: Currency, new_currency: Currency, session: Session) -> Dict[str, Any]:
        """
        Add a currency change event.
        
        Args:
            account_id: ID of the bank account
            old_currency: Previous currency
            new_currency: New currency
            session: Database session
            
        Returns:
            Dict[str, Any]: Result data from event processing
        """
        event_data = {
            'event_type': 'currency_changed',
            'old_currency': old_currency,
            'new_currency': new_currency
        }
        
        return self.add_bank_account_event(account_id, event_data, session)
