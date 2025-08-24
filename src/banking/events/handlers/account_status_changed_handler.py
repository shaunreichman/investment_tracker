"""
Account Status Changed Event Handler.

This module provides the handler for account status change events,
processing account status modifications and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import AccountStatusChangedEvent


class AccountStatusChangedHandler(BaseBankingEventHandler):
    """
    Handler for account status change events.
    
    This handler processes account status change events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, account: BankAccount):
        """
        Initialize the account status changed handler.
        
        Args:
            session: Database session for all operations
            account: BankAccount instance whose status changed
        """
        super().__init__(session, account)
        self.account = account
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate account status change event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['old_status', 'new_status']
        self._validate_required_fields(event_data, required_fields)
        
        # Validate status values are boolean
        old_status = event_data.get('old_status')
        new_status = event_data.get('new_status')
        
        if not isinstance(old_status, bool):
            raise ValueError("Old status must be a boolean value")
        
        if not isinstance(new_status, bool):
            raise ValueError("New status must be a boolean value")
        
        # Validate that status actually changed
        if old_status == new_status:
            raise ValueError("Old and new status must be different")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle account status change event.
        
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
            self._log_event_processing("account_status_changed", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get status information from event data
            old_status = event_data.get('old_status')
            new_status = event_data.get('new_status')
            
            # Create and publish domain event
            domain_event = AccountStatusChangedEvent(
                account_id=self.account.id,
                event_date=date.today(),
                old_status=old_status,
                new_status=new_status,
                metadata={
                    'account_info': {
                        'entity_id': self.account.entity_id,
                        'bank_id': self.account.bank_id,
                        'account_name': self.account.account_name,
                        'account_number': self.account.account_number,
                        'currency': self.account.currency
                    },
                    'status_description': 'Account activated' if new_status else 'Account deactivated'
                }
            )
            
            self._publish_domain_event("account_status_changed", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'account_id': self.account.id,
                'old_status': old_status,
                'new_status': new_status,
                'status_description': 'Account activated' if new_status else 'Account deactivated',
                'account_info': {
                    'entity_id': self.account.entity_id,
                    'bank_id': self.account.bank_id,
                    'account_name': self.account.account_name,
                    'account_number': self.account.account_number,
                    'currency': self.account.currency
                },
                'status': 'status_changed',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("account_status_changed", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("account_status_changed", e)
            raise
        except Exception as e:
            self._handle_processing_error("account_status_changed", e)
            raise
