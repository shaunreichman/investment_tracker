"""
Contact Added Event Handler.

This module provides the ContactAddedHandler class,
which handles contact addition events and triggers
dependent updates in the system.
"""

import logging
from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain import ContactAddedEvent
from src.investment_company.models import InvestmentCompany, Contact


class ContactAddedHandler(BaseCompanyEventHandler):
    """
    Handler for contact addition events.
    
    This handler processes contact addition events and:
    1. Validates the event data
    2. Updates company state if needed
    3. Publishes domain events for dependent updates
    4. Triggers contact-related calculations
    """
    
    def __init__(self, session: Session, company: InvestmentCompany):
        """Initialize the handler with session and company."""
        super().__init__(session, company)
        self.logger = logging.getLogger(__name__)
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate contact addition event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['contact_id', 'contact_name', 'event_date']
        self._validate_required_fields(event_data, required_fields)
        
        field_types = {
            'contact_id': int,
            'contact_name': str,
            'event_date': str,  # Will be parsed to date
            'contact_title': str
        }
        self._validate_field_types(event_data, field_types)
        
        # Validate contact name is not empty
        if not event_data['contact_name'].strip():
            raise ValueError("Contact name cannot be empty")
        
        # Validate contact ID is positive
        if event_data['contact_id'] <= 0:
            raise ValueError("Contact ID must be positive")
    
    def handle(self, event_data: Dict[str, Any]) -> Contact:
        """
        Handle contact addition event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            Contact: The added contact instance
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            # Log event processing
            self._log_event_processing("ContactAdded", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Validate company exists
            self._validate_company_exists()
            
            # Get the contact from the session
            contact = self._get_contact(event_data['contact_id'])
            
            # Validate contact belongs to this company
            if contact.investment_company_id != self.company.id:
                raise ValueError(
                    f"Contact {contact.id} does not belong to company {self.company.id}"
                )
            
            # Parse event date
            event_date = self._parse_event_date(event_data['event_date'])
            
            # Create domain event
            domain_event = ContactAddedEvent(
                company_id=self.company.id,
                event_date=event_date,
                contact_id=contact.id,
                contact_name=contact.name,
                contact_title=contact.title,
                metadata={
                    'handler': self.__class__.__name__,
                    'timestamp': event_data.get('timestamp')
                }
            )
            
            # Publish domain event for dependent updates
            self._publish_domain_event(domain_event)
            
            # Trigger contact-related calculations
            self._trigger_contact_calculations(contact)
            
            # Log successful processing
            self.logger.info(
                f"Successfully processed contact addition event for contact {contact.id} "
                f"in company {self.company.id}"
            )
            
            return contact
            
        except Exception as error:
            self._handle_error(error, event_data)
            raise
    
    def _parse_event_date(self, date_str: str) -> date:
        """
        Parse event date from string.
        
        Args:
            date_str: Date string in ISO format
            
        Returns:
            date: Parsed date object
            
        Raises:
            ValueError: If date string is invalid
        """
        try:
            return date.fromisoformat(date_str)
        except ValueError:
            raise ValueError(f"Invalid date format: {date_str}. Expected ISO format (YYYY-MM-DD)")
    
    def _trigger_contact_calculations(self, contact: Contact) -> None:
        """
        Trigger contact-related calculations.
        
        This method triggers the necessary calculations after contact addition
        to ensure all dependent data is properly updated.
        
        Args:
            contact: The contact that was added
        """
        try:
            # Trigger contact count updates
            self.contact_service.update_contact_count(self.company.id, self.session)
            
            # Trigger company summary updates if needed
            self.summary_service.recalculate_company_summary(self.company.id, self.session)
            
            self.logger.info(
                f"Triggered contact calculations for contact {contact.id} "
                f"in company {self.company.id}"
            )
            
        except Exception as error:
            self.logger.warning(
                f"Failed to trigger contact calculations for contact {contact.id} "
                f"in company {self.company.id}: {error}"
            )
            # Don't fail the event if calculations fail - this is a non-critical operation
