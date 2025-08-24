"""
Currency Changed Event Handler.

This module provides the handler for currency change events,
processing account currency modifications and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import CurrencyChangedEvent


class CurrencyChangedHandler(BaseBankingEventHandler):
    """
    Handler for currency change events.
    
    This handler processes currency change events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, account: BankAccount):
        """
        Initialize the currency changed handler.
        
        Args:
            session: Database session for all operations
            account: BankAccount instance whose currency changed
        """
        super().__init__(session, account)
        self.account = account
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate currency change event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['old_currency', 'new_currency']
        self._validate_required_fields(event_data, required_fields)
        
        # Validate old currency format
        old_currency = event_data.get('old_currency', '')
        if len(old_currency) != 3 or not old_currency.isalpha():
            raise ValueError("Old currency must be a 3-letter ISO 4217 code")
        
        # Validate new currency format
        new_currency = event_data.get('new_currency', '')
        if len(new_currency) != 3 or not new_currency.isalpha():
            raise ValueError("New currency must be a 3-letter ISO 4217 code")
        
        # Validate that currencies are different
        if old_currency == new_currency:
            raise ValueError("Old and new currencies must be different")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle currency change event.
        
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
            self._log_event_processing("currency_changed", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get currency information from event data
            old_currency = event_data.get('old_currency')
            new_currency = event_data.get('new_currency')
            
            # Create and publish domain event
            domain_event = CurrencyChangedEvent(
                account_id=self.account.id,
                event_date=date.today(),
                old_currency=old_currency,
                new_currency=new_currency,
                metadata={
                    'account_info': {
                        'entity_id': self.account.entity_id,
                        'bank_id': self.account.bank_id,
                        'account_name': self.account.account_name,
                        'account_number': self.account.account_number
                    }
                }
            )
            
            self._publish_domain_event("currency_changed", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'account_id': self.account.id,
                'old_currency': old_currency,
                'new_currency': new_currency,
                'account_info': {
                    'entity_id': self.account.entity_id,
                    'bank_id': self.account.bank_id,
                    'account_name': self.account.account_name,
                    'account_number': self.account.account_number
                },
                'status': 'currency_changed',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("currency_changed", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("currency_changed", e)
            raise
        except Exception as e:
            self._handle_processing_error("currency_changed", e)
            raise
