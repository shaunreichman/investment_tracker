"""
Company Updated Event Handler.

This module provides the handler for company update events in the investment company system.
It handles the business logic for updating company information and triggers appropriate
domain events for dependent updates.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain.company_updated_event import CompanyUpdatedEvent
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums import CompanyDomainEventType


class CompanyUpdatedHandler(BaseCompanyEventHandler):
    """
    Handler for company update events.
    
    This handler processes company update operations and ensures:
    1. Company information is properly updated
    2. Portfolio summaries are recalculated if needed
    3. Appropriate domain events are published
    4. Data consistency is maintained across related entities
    """
    
    def __init__(self, session, company: InvestmentCompany):
        """
        Initialize the company updated handler.
        
        Args:
            session: Database session for operations
            company: InvestmentCompany instance being updated
        """
        super().__init__(session, company)
        self.logger = logging.getLogger(__name__)
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the company update event.
        
        Args:
            event_data: Dictionary containing update data including:
                - company_id: ID of the company being updated
                - update_fields: Dictionary of fields to update
                - previous_values: Dictionary of previous values (for audit)
        
        Returns:
            dict: Result of the update operation
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If update operation fails
        """
        try:
            self.logger.info(f"Processing company update event for company {self.company.id}")
            
            # Validate event data
            self._validate_event_data(event_data)
            
            # Extract update information
            company_id = event_data['company_id']
            update_fields = event_data.get('update_fields', {})
            previous_values = event_data.get('previous_values', {})
            
            # Verify company ID matches
            if company_id != self.company.id:
                raise ValueError(f"Company ID mismatch: expected {self.company.id}, got {company_id}")
            
            # Update company information
            updated_company = self._update_company(update_fields)
            
            # Update portfolio summary if needed
            self._update_portfolio_summary()
            
            # Update company summary
            self._update_company_summary()
            
            # Publish domain event
            self._publish_domain_event(updated_company, previous_values)
            
            # Log successful update
            self.logger.info(f"Successfully updated company {company_id}")
            
            return {
                'success': True,
                'company_id': company_id,
                'updated_fields': list(update_fields.keys()),
                'message': 'Company updated successfully'
            }
            
        except Exception as error:
            self.logger.error(f"Failed to process company update event: {error}")
            raise RuntimeError(f"Company update failed: {error}")
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate company update event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['company_id']
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
        required_fields = ['company_id']
        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Required field '{field}' missing from event data")
        
        if 'update_fields' not in event_data or not event_data['update_fields']:
            raise ValueError("Event data must contain non-empty 'update_fields'")
    
    def _update_company(self, update_fields: Dict[str, Any]) -> InvestmentCompany:
        """
        Update the company with new information.
        
        Args:
            update_fields: Dictionary of fields to update
            
        Returns:
            InvestmentCompany: Updated company instance
        """
        # Update company fields
        for field, value in update_fields.items():
            if hasattr(self.company, field):
                setattr(self.company, field, value)
        
        # Update timestamp
        self.company.updated_at = datetime.now(timezone.utc)
        
        # Commit changes
        self.session.commit()
        
        return self.company
    
    def _update_portfolio_summary(self) -> None:
        """
        Update portfolio summary if company changes affect portfolio.
        
        This method ensures portfolio-level summaries are updated
        when company information changes.
        """
        try:
            # Update portfolio summary through service
            self.portfolio_service.update_portfolio_summary(self.company, self.session)
            self.logger.debug(f"Updated portfolio summary for company {self.company.id}")
        except Exception as error:
            self.logger.warning(f"Failed to update portfolio summary: {error}")
            # Don't fail the main operation for summary update failures
    
    def _update_company_summary(self) -> None:
        """
        Update company summary fields.
        
        This method ensures company-level summaries are updated
        when company information changes.
        """
        try:
            # Update company summary through service
            self.summary_service.update_company_summary(self.company, self.session)
            self.logger.debug(f"Updated company summary for company {self.company.id}")
        except Exception as error:
            self.logger.warning(f"Failed to update company summary: {error}")
            # Don't fail the main operation for summary update failures
    
    def _publish_domain_event(self, updated_company: InvestmentCompany, previous_values: Dict[str, Any]) -> None:
        """
        Publish domain event for company update.
        
        Args:
            updated_company: Updated company instance
            previous_values: Previous values for audit purposes
        """
        try:
            event = CompanyUpdatedEvent(
                company_id=updated_company.id,
                event_date=datetime.now(timezone.utc).date(),
                previous_values=previous_values,
                updated_fields=list(previous_values.keys())
            )
            
            # Publish event through orchestrator
            self.orchestrator.publish_domain_event(event)
            self.logger.debug(f"Published CompanyUpdatedEvent for company {updated_company.id}")
            
        except Exception as error:
            self.logger.warning(f"Failed to publish domain event: {error}")
            # Don't fail the main operation for event publishing failures
