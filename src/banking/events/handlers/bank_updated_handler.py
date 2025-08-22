"""
Bank Updated Event Handler.

This module provides the handler for bank update events,
processing bank modifications and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import Bank
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankUpdatedEvent


class BankUpdatedHandler(BaseBankingEventHandler):
    """
    Handler for bank update events.
    
    This handler processes bank update events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, bank: Bank):
        """
        Initialize the bank updated handler.
        
        Args:
            session: Database session for all operations
            bank: Bank instance that was updated
        """
        super().__init__(session, bank)
        self.bank = bank
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank update event data.
        
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
        if 'country' in changes:
            country = changes['country']
            if len(country) != 2 or not country.isalpha():
                raise ValueError("Country must be a 2-letter ISO 3166-1 alpha-2 code")
        
        if 'name' in changes:
            name = changes['name'].strip()
            if not name:
                raise ValueError("Bank name cannot be empty")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank update event.
        
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
            self._log_event_processing("bank_updated", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get changes from event data
            changes = event_data.get('changes', {})
            
            # Create and publish domain event
            domain_event = BankUpdatedEvent(
                bank_id=self.bank.id,
                event_date=date.today(),
                metadata={
                    'changes': changes,
                    'current_state': {
                        'name': self.bank.name,
                        'country': self.bank.country,
                        'swift_bic': self.bank.swift_bic
                    }
                }
            )
            
            self._publish_domain_event("bank_updated", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'bank_id': self.bank.id,
                'changes_applied': changes,
                'current_state': {
                    'name': self.bank.name,
                    'country': self.bank.country,
                    'swift_bic': self.bank.swift_bic
                },
                'status': 'updated',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_updated", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_updated", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_updated", e)
            raise
