"""
Base Banking Event Handler.

This module provides the base class for all banking event handlers,
defining the common interface and shared functionality.

Key responsibilities:
- Common event processing logic
- Event validation and error handling
- Event relationship management
- Event publishing and side effects
"""

import logging
from typing import Dict, Any, Optional, List, TYPE_CHECKING
from datetime import date, datetime
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from src.banking.models import Bank, BankAccount

if TYPE_CHECKING:
    from src.banking.services.bank_service import BankService
    from src.banking.services.bank_account_service import BankAccountService
    from src.banking.services.banking_validation_service import BankingValidationService


class BaseBankingEventHandler(ABC):
    """
    Abstract base class for all banking event handlers.
    
    Each handler is responsible for:
    1. Validating the event data
    2. Processing the event and updating banking entities
    3. Publishing domain events for dependent updates
    4. Managing transaction boundaries
    
    This class provides common functionality and enforces the contract
    that all handlers must implement.
    """
    
    def __init__(self, session: Session, banking_entity: 'Bank | BankAccount'):
        """
        Initialize the handler with session and banking entity.
        
        Args:
            session: Database session for all operations
            banking_entity: Bank or BankAccount instance to operate on
        """
        self.session = session
        self.banking_entity = banking_entity
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize services for business logic
        from src.banking.services.bank_service import BankService
        from src.banking.services.bank_account_service import BankAccountService
        from src.banking.services.banking_validation_service import BankingValidationService
        
        self.bank_service = BankService()
        self.bank_account_service = BankAccountService()
        self.validation_service = BankingValidationService()
    
    @abstractmethod
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the event and return the result data.
        
        This is the main entry point that all handlers must implement.
        It should:
        1. Validate the event data
        2. Process the banking event
        3. Update banking state as needed
        4. Publish domain events
        5. Return the result data
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            Dict[str, Any]: The result data from event processing
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        pass
    
    @abstractmethod
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate event data before processing.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def _get_bank(self, bank_id: int) -> Bank:
        """
        Get bank by ID from the current session.
        
        Args:
            bank_id: ID of the bank to retrieve
            
        Returns:
            Bank: Bank instance
            
        Raises:
            ValueError: If bank not found
        """
        bank = self.bank_service.get_bank(bank_id, self.session)
        if not bank:
            raise ValueError(f"Bank with ID {bank_id} not found")
        return bank
    
    def _get_bank_account(self, account_id: int) -> BankAccount:
        """
        Get bank account by ID from the current session.
        
        Args:
            account_id: ID of the account to retrieve
            
        Returns:
            BankAccount: BankAccount instance
            
        Raises:
            ValueError: If account not found
        """
        account = self.bank_account_service.get_bank_account_by_id(account_id, self.session)
        if not account:
            raise ValueError(f"Bank account with ID {account_id} not found")
        return account
    
    def _publish_domain_event(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Publish a domain event for dependent updates.
        
        This method will be implemented to integrate with the domain event system.
        For now, it logs the event for debugging purposes.
        
        Args:
            event_type: Type of domain event
            event_data: Event data to publish
        """
        self.logger.info(f"Publishing domain event: {event_type} with data: {event_data}")
        # TODO: Integrate with domain event system
        # self.event_bus.publish(event_type, event_data)
    
    def _validate_required_fields(self, event_data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present in event data.
        
        Args:
            event_data: Dictionary containing event parameters
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required field is missing
        """
        missing_fields = [field for field in required_fields if field not in event_data or event_data[field] is None]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
    
    def _log_event_processing(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Log event processing for debugging and monitoring.
        
        Args:
            event_type: Type of event being processed
            event_data: Event data being processed
        """
        self.logger.info(f"Processing {event_type} event: {event_data}")
    
    def _log_event_success(self, event_type: str, result: Dict[str, Any]) -> None:
        """
        Log successful event processing.
        
        Args:
            event_type: Type of event that was processed
            result: Result data from event processing
        """
        self.logger.info(f"Successfully processed {event_type} event. Result: {result}")
    
    def _log_event_error(self, event_type: str, error: Exception) -> None:
        """
        Log event processing errors.
        
        Args:
            event_type: Type of event that failed
            error: Exception that occurred
        """
        self.logger.error(f"Error processing {event_type} event: {str(error)}")
    
    def _handle_validation_error(self, event_type: str, error: ValueError) -> None:
        """
        Handle validation errors during event processing.
        
        Args:
            event_type: Type of event that failed validation
            error: Validation error that occurred
        """
        self.logger.warning(f"Validation failed for {event_type} event: {str(error)}")
        raise error
    
    def _handle_processing_error(self, event_type: str, error: Exception) -> None:
        """
        Handle processing errors during event execution.
        
        Args:
            event_type: Type of event that failed processing
            error: Processing error that occurred
        """
        self.logger.error(f"Processing failed for {event_type} event: {str(error)}")
        raise RuntimeError(f"Failed to process {event_type} event: {str(error)}") from error
