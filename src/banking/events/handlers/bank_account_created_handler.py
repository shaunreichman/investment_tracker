"""
Bank Account Created Event Handler.

This module provides the handler for bank account creation events,
processing new account creation and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankAccountCreatedEvent


class BankAccountCreatedHandler(BaseBankingEventHandler):
    """
    Handler for bank account creation events.
    
    This handler processes bank account creation events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, account: BankAccount):
        """
        Initialize the bank account created handler.
        
        Args:
            session: Database session for all operations
            account: BankAccount instance that was created
        """
        super().__init__(session, account)
        self.account = account
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank account creation event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['entity_id', 'bank_id', 'account_name', 'account_number', 'currency']
        self._validate_required_fields(event_data, required_fields)
        
        # Validate currency code format (ISO 4217)
        currency = event_data.get('currency', '')
        # Handle both string and enum values
        if hasattr(currency, 'value'):
            currency = currency.value
        if len(currency) != 3 or not currency.isalpha():
            raise ValueError("Currency must be a 3-letter ISO 4217 code")
        
        # Validate account name is not empty
        account_name = event_data.get('account_name', '').strip()
        if not account_name:
            raise ValueError("Account name cannot be empty")
        
        # Validate account number is not empty
        account_number = event_data.get('account_number', '').strip()
        if not account_number:
            raise ValueError("Account number cannot be empty")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank account creation event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            Dict[str, Any]: Result data from event processing
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            # Log event processing
            self._log_event_processing("bank_account_created", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Account is already created at this point, so we just need to
            # publish the domain event and return success
            
            # Create and publish domain event
            domain_event = BankAccountCreatedEvent(
                account_id=self.account.id,
                event_date=date.today(),
                metadata={
                    'entity_id': self.account.entity_id,
                    'bank_id': self.account.bank_id,
                    'account_name': self.account.account_name,
                    'account_number': self.account.account_number,
                    'currency': self.account.currency,
                    'status': self.account.status
                }
            )
            
            self._publish_domain_event("bank_account_created", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'account_id': self.account.id,
                'entity_id': self.account.entity_id,
                'bank_id': self.account.bank_id,
                'account_name': self.account.account_name,
                'account_number': self.account.account_number,
                'currency': self.account.currency,
                'status': 'created',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_account_created", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_account_created", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_account_created", e)
            raise
