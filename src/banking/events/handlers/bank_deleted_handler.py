"""
Bank Deleted Event Handler.

This module provides the handler for bank deletion events,
processing bank removal and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import Bank
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankDeletedEvent


class BankDeletedHandler(BaseBankingEventHandler):
    """
    Handler for bank deletion events.
    
    This handler processes bank deletion events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, bank: Bank):
        """
        Initialize the bank deleted handler.
        
        Args:
            session: Database session for all operations
            bank: Bank instance that was deleted
        """
        super().__init__(session, bank)
        self.bank = bank
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank deletion event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        # For deletion, we typically don't need additional validation
        # as the bank is already deleted at this point
        pass
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank deletion event.
        
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
            self._log_event_processing("bank_deleted", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Get deletion reason from event data
            deletion_reason = event_data.get('deletion_reason', 'Manual deletion')
            
            # Create and publish domain event
            domain_event = BankDeletedEvent(
                bank_id=self.bank.id,
                event_date=date.today(),
                metadata={
                    'deletion_reason': deletion_reason,
                    'deleted_bank_info': {
                        'name': self.bank.name,
                        'country': self.bank.country,
                        'swift_bic': self.bank.swift_bic
                    }
                }
            )
            
            self._publish_domain_event("bank_deleted", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'bank_id': self.bank.id,
                'deletion_reason': deletion_reason,
                'deleted_bank_info': {
                    'name': self.bank.name,
                    'country': self.bank.country,
                    'swift_bic': self.bank.swift_bic
                },
                'status': 'deleted',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_deleted", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_deleted", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_deleted", e)
            raise
