"""
Company Created Event Handler.

This module provides the CompanyCreatedHandler class,
which handles company creation events and triggers
dependent updates in the system.
"""

import logging
from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain import CompanyCreatedEvent
from src.investment_company.models import InvestmentCompany


class CompanyCreatedHandler(BaseCompanyEventHandler):
    """
    Handler for company creation events.
    
    This handler processes company creation events and:
    1. Validates the event data
    2. Updates company state if needed
    3. Publishes domain events for dependent updates
    4. Triggers portfolio and summary calculations
    """
    
    def __init__(self, session: Session, company: InvestmentCompany):
        """Initialize the handler with session and company."""
        super().__init__(session, company)
        self.logger = logging.getLogger(__name__)
    
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate company creation event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['company_name', 'event_date']
        self._validate_required_fields(event_data, required_fields)
        
        field_types = {
            'company_name': str,
            'event_date': str  # Will be parsed to date
        }
        self._validate_field_types(event_data, field_types)
        
        # Validate company name is not empty
        if not event_data['company_name'].strip():
            raise ValueError("Company name cannot be empty")
    
    def handle(self, event_data: Dict[str, Any]) -> InvestmentCompany:
        """
        Handle company creation event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            InvestmentCompany: The created company instance
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            # Log event processing
            self._log_event_processing("CompanyCreated", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Validate company exists
            self._validate_company_exists()
            
            # Parse event date
            event_date = self._parse_event_date(event_data['event_date'])
            
            # Create domain event
            domain_event = CompanyCreatedEvent(
                company_id=self.company.id,
                event_date=event_date,
                company_name=event_data['company_name'],
                company_type=event_data.get('company_type'),
                metadata={
                    'handler': self.__class__.__name__,
                    'timestamp': event_data.get('timestamp')
                }
            )
            
            # Publish domain event for dependent updates
            self._publish_domain_event(domain_event)
            
            # Trigger portfolio and summary calculations
            self._trigger_company_calculations()
            
            # Log successful processing
            self.logger.info(f"Successfully processed company creation event for company {self.company.id}")
            
            return self.company
            
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
    
    def _trigger_company_calculations(self) -> None:
        """
        Trigger company portfolio and summary calculations.
        
        This method triggers the necessary calculations after company creation
        to ensure all dependent data is properly initialized.
        """
        try:
            # Trigger portfolio calculations
            self.portfolio_service.recalculate_portfolio_summary(self.company.id, self.session)
            
            # Trigger summary calculations
            self.summary_service.recalculate_company_summary(self.company.id, self.session)
            
            self.logger.info(f"Triggered calculations for newly created company {self.company.id}")
            
        except Exception as error:
            self.logger.warning(
                f"Failed to trigger calculations for company {self.company.id}: {error}"
            )
            # Don't fail the event if calculations fail - this is a non-critical operation
