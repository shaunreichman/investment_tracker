"""
Company Deleted Event Handler.

This module provides the handler for company deletion events in the investment company system.
It handles the business logic for deleting companies and triggers appropriate
domain events for dependent updates.
"""

from typing import Dict, Any, Optional
from datetime import datetime, timezone
import logging

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain.company_deleted_event import CompanyDeletedEvent
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums import CompanyDomainEventType


class CompanyDeletedHandler(BaseCompanyEventHandler):
    """
    Handler for company deletion events.
    
    This handler processes company deletion aftermath and ensures:
    1. Portfolio and fund relationships are cleaned up correctly
    2. Contact cleanup is performed
    3. Appropriate domain events are published
    4. Data consistency is maintained across the system
    
    Note: The actual company deletion is performed by the service layer,
    this handler manages the cleanup and event coordination.
    """
    
    def __init__(self, session, company: InvestmentCompany):
        """
        Initialize the company deleted handler.
        
        Args:
            session: Database session for operations
            company: InvestmentCompany instance being deleted
        """
        super().__init__(session, company)
        self.logger = logging.getLogger(__name__)
    
    def handle(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle the company deletion event.
        
        Args:
            event_data: Dictionary containing deletion data including:
                - company_id: ID of the company being deleted
                - deletion_reason: Optional reason for deletion
                - cascade_delete: Whether to cascade delete related entities
        
        Returns:
            dict: Result of the deletion operation
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If deletion operation fails
        """
        try:
            self.logger.info(f"Processing company deletion event for company {self.company.id}")
            
            # Validate event data
            self._validate_event_data(event_data)
            
            # Extract deletion information
            company_id = event_data['company_id']
            deletion_reason = event_data.get('deletion_reason', 'No reason provided')
            cascade_delete = event_data.get('cascade_delete', False)
            
            # Verify company ID matches
            if company_id != self.company.id:
                raise ValueError(f"Company ID mismatch: expected {self.company.id}, got {company_id}")
            
            # Check if company can be deleted
            self._validate_deletion_allowed()
            
            # Handle portfolio cleanup
            self._cleanup_portfolio(cascade_delete)
            
            # Handle contact cleanup
            self._cleanup_contacts()
            
            # Store company info for event publishing (company was already deleted by service)
            deleted_company = self.company
            
            # Publish domain event
            self._publish_domain_event(deleted_company, deletion_reason)
            
            # Log successful deletion
            self.logger.info(f"Successfully deleted company {company_id}")
            
            return {
                'success': True,
                'company_id': company_id,
                'deletion_reason': deletion_reason,
                'cascade_delete': cascade_delete,
                'message': 'Company deleted successfully'
            }
            
        except Exception as error:
            self.logger.error(f"Failed to process company deletion event: {error}")
            raise RuntimeError(f"Company deletion failed: {error}")
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate company deletion event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['company_id']
        self._validate_required_fields(event_data, required_fields)
    
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
    
    def _validate_deletion_allowed(self) -> None:
        """
        Validate that the company can be deleted.
        
        This method checks business rules to ensure deletion is allowed.
        
        Raises:
            ValueError: If deletion is not allowed
        """
        # Check if company has active funds
        active_funds = [f for f in self.company.funds if f.status.value == 'ACTIVE']
        if active_funds:
            fund_names = [f.name for f in active_funds]
            raise ValueError(
                f"Cannot delete company with active funds: {', '.join(fund_names)}"
            )
        
        # Check if company has pending transactions
        # This would be implemented based on business rules
        # For now, we'll allow deletion if no active funds
        
        self.logger.debug(f"Company {self.company.id} deletion validation passed")
    
    def _cleanup_portfolio(self, cascade_delete: bool) -> None:
        """
        Clean up company portfolio before deletion.
        
        Args:
            cascade_delete: Whether to cascade delete related funds
        """
        try:
            if cascade_delete:
                # Delete all funds associated with the company
                fund_count = len(self.company.funds)
                for fund in self.company.funds:
                    self.session.delete(fund)
                self.logger.info(f"Deleted {fund_count} funds for company {self.company.id}")
            else:
                # Just log the portfolio state
                fund_count = len(self.company.funds)
                self.logger.info(f"Company {self.company.id} has {fund_count} funds (not cascading)")
                
        except Exception as error:
            self.logger.warning(f"Failed to cleanup portfolio: {error}")
            # Don't fail the main operation for cleanup failures
    
    def _cleanup_contacts(self) -> None:
        """
        Clean up company contacts before deletion.
        """
        try:
            contact_count = len(self.company.contacts)
            for contact in self.company.contacts:
                self.session.delete(contact)
            self.logger.info(f"Deleted {contact_count} contacts for company {self.company.id}")
            
        except Exception as error:
            self.logger.warning(f"Failed to cleanup contacts: {error}")
            # Don't fail the main operation for cleanup failures
    

    
    def _publish_domain_event(self, deleted_company: InvestmentCompany, deletion_reason: str) -> None:
        """
        Publish domain event for company deletion.
        
        Args:
            deleted_company: Deleted company instance
            deletion_reason: Reason for deletion
        """
        try:
            event = CompanyDeletedEvent(
                company_id=deleted_company.id,
                event_date=datetime.now(timezone.utc).date(),
                deletion_reason=deletion_reason,
                company_name=deleted_company.name
            )
            
            # Publish event through orchestrator
            self.orchestrator.publish_domain_event(event)
            self.logger.debug(f"Published CompanyDeletedEvent for company {deleted_company.id}")
            
        except Exception as error:
            self.logger.warning(f"Failed to publish domain event: {error}")
            # Don't fail the main operation for event publishing failures
