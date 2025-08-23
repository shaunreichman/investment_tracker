"""
Bank Created Event Handler.

This module provides the handler for bank creation events,
processing new bank creation and publishing domain events.
"""

from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.banking.models import Bank
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.domain import BankCreatedEvent


class BankCreatedHandler(BaseBankingEventHandler):
    """
    Handler for bank creation events.
    
    This handler processes bank creation events and publishes
    appropriate domain events for dependent updates.
    """
    
    def __init__(self, session: Session, bank: Bank):
        """
        Initialize the bank created handler.
        
        Args:
            session: Database session for all operations
            bank: Bank instance that was created
        """
        super().__init__(session, bank)
        self.bank = bank
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate bank creation event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['name', 'country']
        self._validate_required_fields(event_data, required_fields)
        
        # Validate country code format (ISO 3166-1 alpha-2)
        country = event_data.get('country', '')
        if len(country) != 2 or not country.isalpha():
            raise ValueError("Country must be a 2-letter ISO 3166-1 alpha-2 code")
        
        # Validate name is not empty
        name = event_data.get('name', '').strip()
        if not name:
            raise ValueError("Bank name cannot be empty")
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle bank creation event.
        
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
            self._log_event_processing("bank_created", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Bank is already created at this point, so we just need to
            # publish the domain event and return success
            
            # Create and publish domain event
            domain_event = BankCreatedEvent(
                bank_id=self.bank.id,
                event_date=date.today(),
                metadata={
                    'name': self.bank.name,
                    'country': self.bank.country,
                    'swift_bic': self.bank.swift_bic
                }
            )
            
            self._publish_domain_event("bank_created", domain_event.to_dict())
            
            # Prepare result data
            result = {
                'bank_id': self.bank.id,
                'name': self.bank.name,
                'country': self.bank.country,
                'swift_bic': self.bank.swift_bic,
                'status': 'created',
                'domain_event_published': True
            }
            
            # Log successful processing
            self._log_event_success("bank_created", result)
            
            return result
            
        except ValueError as e:
            self._handle_validation_error("bank_created", e)
            raise
        except Exception as e:
            self._handle_processing_error("bank_created", e)
            raise
