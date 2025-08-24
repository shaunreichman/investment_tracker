"""
Contact Updated Event Handler.

This module provides the handler for contact update events in the investment company system.
It handles the business logic for updating contact information and triggers appropriate
domain events for dependent updates.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain.contact_updated_event import ContactUpdatedEvent
from src.investment_company.models import Contact
from src.investment_company.enums import CompanyDomainEventType


class ContactUpdatedHandler(BaseCompanyEventHandler):
    """
    Handler for contact update events.
    
    This handler processes contact update operations and ensures:
    1. Contact information is properly updated
    2. Company summary fields are recalculated if needed
    3. Appropriate domain events are published
    4. Data consistency is maintained
    """
    
    def __init__(self, session, company, contact: Contact):
        """
        Initialize the contact updated handler.
        
        Args:
            session: Database session for operations
            company: InvestmentCompany instance
            contact: Contact instance being updated
        """
        super().__init__(session, company)
        self.contact = contact
        self.logger = logging.getLogger(__name__)
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the contact update event.
        
        Args:
            event_data: Dictionary containing update data including:
                - contact_id: ID of the contact being updated
                - update_fields: Dictionary of fields to update
                - previous_values: Dictionary of previous values (for audit)
        
        Returns:
            dict: Result of the update operation
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If update operation fails
        """
        try:
            self.logger.info(f"Processing contact update event for contact {self.contact.id}")
            
            # Validate event data
            self._validate_event_data(event_data)
            
            # Extract update information
            contact_id = event_data['contact_id']
            update_fields = event_data.get('update_fields', {})
            previous_values = event_data.get('previous_values', {})
            
            # Verify contact belongs to company
            if self.contact.investment_company_id != self.company.id:
                raise ValueError(f"Contact {contact_id} does not belong to company {self.company.id}")
            
            # Update contact information
            updated_contact = self._update_contact(update_fields)
            
            # Update company summary if needed
            self._update_company_summary()
            
            # Publish domain event
            self._publish_domain_event(updated_contact, previous_values)
            
            # Log successful update
            self.logger.info(f"Successfully updated contact {contact_id} for company {self.company.id}")
            
            return {
                'success': True,
                'contact_id': contact_id,
                'updated_fields': list(update_fields.keys()),
                'message': 'Contact updated successfully'
            }
            
        except Exception as error:
            self.logger.error(f"Failed to process contact update event: {error}")
            raise RuntimeError(f"Contact update failed: {error}")
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate contact update event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['contact_id']
        self._validate_required_fields(event_data, required_fields)
        
        if 'update_fields' not in event_data or not event_data['update_fields']:
            raise ValueError("Event data must contain non-empty 'update_fields'")
    
    def _validate_event_data(self, event_data: Dict[str, Any]) -> None:
        """
        Validate the event data structure.
        
        Args:
            event_data: Event data to validate
            
        Raises:
            ValueError: If event data is invalid
        """
        required_fields = ['contact_id']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' missing from event data")
        
        if 'update_fields' not in event_data or not event_data['update_fields']:
            raise ValueError("Event data must contain non-empty 'update_fields'")
    
    def _update_contact(self, update_fields: Dict[str, Any]) -> Contact:
        """
        Update the contact with new information.
        
        Args:
            update_fields: Dictionary of fields to update
            
        Returns:
            Contact: Updated contact instance
        """
        # Update contact fields
        for field, value in update_fields.items():
            if hasattr(self.contact, field):
                setattr(self.contact, field, value)
        
        # Update timestamp
        self.contact.updated_at = datetime.now(timezone.utc)
        
        # Commit changes
        self.session.commit()
        
        return self.contact
    
    def _update_company_summary(self) -> None:
        """
        Update company summary fields if needed.
        
        This method ensures company-level summaries are updated
        when contact information changes.
        """
        try:
            # Update company summary through service
            self.summary_service.update_company_summary(self.company, self.session)
            self.logger.debug(f"Updated company summary for company {self.company.id}")
        except Exception as error:
            self.logger.warning(f"Failed to update company summary: {error}")
            # Don't fail the main operation for summary update failures
    
    def _publish_domain_event(self, updated_contact: Contact, previous_values: Dict[str, Any]) -> None:
        """
        Publish domain event for contact update.
        
        Args:
            updated_contact: Updated contact instance
            previous_values: Previous values for audit purposes
        """
        try:
            event = ContactUpdatedEvent(
                company_id=self.company.id,
                contact_id=updated_contact.id,
                event_date=datetime.now(timezone.utc).date(),
                previous_values=previous_values,
                updated_fields=list(previous_values.keys())
            )
            
            # Publish event through orchestrator
            self.orchestrator.publish_domain_event(event)
            self.logger.debug(f"Published ContactUpdatedEvent for contact {updated_contact.id}")
            
        except Exception as error:
            self.logger.warning(f"Failed to publish domain event: {error}")
            # Don't fail the main operation for event publishing failures
