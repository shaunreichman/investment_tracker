"""
Bank Account Deleted Event Handler.

This module provides the handler for bank account deletion events,
processing account removal and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankAccountDeletedEvent


class BankAccountDeletedHandler(BaseBankingEventHandler):
    """
    Handler for bank account deletion events.
    
    This handler processes bank account deletion events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, account: BankAccount):
        """
        Initialize the bank account deleted handler.
        
        Args:
            session: Database session for all operations
            account: BankAccount instance that was deleted
        """
        super().__init__(session, account)
        self.account = account
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank account deletion event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # For deletion, we typically don't need additional validation
        # as the account is already deleted at this point
        pass
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank account deletion event.
        
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
            self._log_event_processing("bank_account_deleted", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get deletion reason from event data
            deletion_reason = event_data.get('deletion_reason', 'Manual deletion')
            
            # Create and publish domain event
            domain_event = BankAccountDeletedEvent(
                account_id=self.account.id,
                event_date=date.today(),
                metadata={
                    'deletion_reason': deletion_reason,
                    'deleted_account_info': {
                        'entity_id': self.account.entity_id,
                        'bank_id': self.account.bank_id,
                        'account_name': self.account.account_name,
                        'account_number': self.account.account_number,
                        'currency': self.account.currency,
                        'is_active': self.account.is_active
                    }
                }
            )
            
            self._publish_domain_event("bank_account_deleted", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'account_id': self.account.id,
                'deletion_reason': deletion_reason,
                'deleted_account_info': {
                    'entity_id': self.account.entity_id,
                    'bank_id': self.account.bank_id,
                    'account_name': self.account.account_name,
                    'account_number': self.account.account_number,
                    'currency': self.account.currency,
                    'is_active': self.account.is_active
                },
                'status': 'deleted',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_account_deleted", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_account_deleted", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_account_deleted", e)
            raise
