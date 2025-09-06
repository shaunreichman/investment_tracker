"""
Bank Account Updated Event Handler.

This module provides the handler for bank account update events,
processing account modifications and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankAccountUpdatedEvent


class BankAccountUpdatedHandler(BaseBankingEventHandler):
    """
    Handler for bank account update events.
    
    This handler processes bank account update events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, account: BankAccount):
        """
        Initialize the bank account updated handler.
        
        Args:
            session: Database session for all operations
            account: BankAccount instance that was updated
        """
        super().__init__(session, account)
        self.account = account
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank account update event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['changes']
        self._validate_required_fields(event_data, required_fields)
        
        changes = event_data.get('changes', {})
        if not isinstance(changes, dict):
            raise ValueError("Changes must be a dictionary")
        
        # Validate specific field changes if present
        if 'currency' in changes:
            currency = changes['currency']
            if len(currency) != 3 or not currency.isalpha():
                raise ValueError("Currency must be a 3-letter ISO 4217 code")
        
        if 'account_name' in changes:
            account_name = changes['account_name'].strip()
            if not account_name:
                raise ValueError("Account name cannot be empty")
        
        if 'account_number' in changes:
            account_number = changes['account_number'].strip()
            if not account_number:
                raise ValueError("Account number cannot be empty")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank account update event.
        
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
            self._log_event_processing("bank_account_updated", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get changes from event data
            changes = event_data.get('changes', {})
            
            # Create and publish domain event
            domain_event = BankAccountUpdatedEvent(
                account_id=self.account.id,
                event_date=date.today(),
                metadata={
                    'changes': changes,
                    'current_state': {
                        'entity_id': self.account.entity_id,
                        'bank_id': self.account.bank_id,
                        'account_name': self.account.account_name,
                        'account_number': self.account.account_number,
                        'currency': self.account.currency,
                        'status': self.account.status
                    }
                }
            )
            
            self._publish_domain_event("bank_account_updated", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'account_id': self.account.id,
                'changes_applied': changes,
                'current_state': {
                    'entity_id': self.account.entity_id,
                    'bank_id': self.account.bank_id,
                    'account_name': self.account.account_name,
                    'account_number': self.account.account_number,
                    'currency': self.account.currency,
                    'status': self.account.status
                },
                'status': 'updated',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_account_updated", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_account_updated", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_account_updated", e)
            raise
