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
        Each service call is wrapped in individual fault isolation to prevent
        failures from cascading.
        """
        # Track which services succeeded/failed for monitoring
        results = {
            'portfolio_summary': {'status': 'pending', 'error': None},
            'company_summary': {'status': 'pending', 'error': None}
        }
        
        # Trigger portfolio calculations with individual fault isolation
        try:
            self.portfolio_service.update_portfolio_summary(self.company, self.session)
            results['portfolio_summary']['status'] = 'success'
            self.logger.info(f"Portfolio calculations triggered for company {self.company.id}")
        except Exception as error:
            results['portfolio_summary']['status'] = 'failed'
            results['portfolio_summary']['error'] = str(error)
            self.logger.warning(
                f"Portfolio calculations failed for company {self.company.id}: {error}"
            )
        
        # Trigger summary calculations with individual fault isolation
        try:
            self.summary_service.update_company_summary(self.company, self.session)
            results['company_summary']['status'] = 'success'
            self.logger.info(f"Company summary calculations triggered for company {self.company.id}")
        except Exception as error:
            results['company_summary']['status'] = 'failed'
            results['company_summary']['error'] = str(error)
            self.logger.warning(
                f"Company summary calculations failed for company {self.company.id}: {error}"
            )
        
        # Log overall results for monitoring and alerting
        self._log_calculation_results(results)
    
    def _log_calculation_results(self, results: Dict[str, Dict]) -> None:
        """
        Log calculation results for monitoring and alerting.
        
        Args:
            results: Dictionary containing results for each service
        """
        success_count = sum(1 for r in results.values() if r['status'] == 'success')
        total_count = len(results)
        
        self.logger.info(
            f"Company {self.company.id} calculations completed: {success_count}/{total_count} successful",
            extra={
                'company_id': self.company.id,
                'calculation_results': results,
                'success_rate': success_count / total_count if total_count > 0 else 0
            }
        )
        
        # Alert if critical calculations failed
        if success_count < total_count:
            self.logger.warning(
                f"Some calculations failed for company {self.company.id}",
                extra={'failed_services': [k for k, v in results.items() if v['status'] == 'failed']}
            )
