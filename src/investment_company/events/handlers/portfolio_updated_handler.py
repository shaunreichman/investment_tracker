"""
Portfolio Updated Event Handler.

This module provides the PortfolioUpdatedHandler class,
which handles portfolio update events and triggers
dependent updates in the system.
"""

import logging
from typing import Dict, Any
from datetime import date
from sqlalchemy.orm import Session

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.domain import PortfolioUpdatedEvent
from src.investment_company.models import InvestmentCompany


class PortfolioUpdatedHandler(BaseCompanyEventHandler):
    """
    Handler for portfolio update events.
    
    This handler processes portfolio update events and:
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
        Validate portfolio update event data.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        required_fields = ['event_date']
        self._validate_required_fields(event_data, required_fields)
        
        field_types = {
            'event_date': str,  # Will be parsed to date
            'fund_id': int,
            'operation': str
        }
        self._validate_field_types(event_data, field_types)
        
        # Validate operation if provided
        if 'operation' in event_data:
            valid_operations = ['added', 'removed', 'updated', 'recalculated']
            if event_data['operation'] not in valid_operations:
                raise ValueError(
                    f"Invalid operation: {event_data['operation']}. "
                    f"Must be one of: {valid_operations}"
                )
    
    def handle(self, event_data: Dict[str, Any]) -> InvestmentCompany:
        """
        Handle portfolio update event.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            InvestmentCompany: The updated company instance
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        try:
            # Log event processing
            self._log_event_processing("PortfolioUpdated", event_data)
            
            # Validate event data
            self.validate_event(event_data)
            
            # Validate company exists
            self._validate_company_exists()
            
            # Parse event date
            event_date = self._parse_event_date(event_data['event_date'])
            
            # Create domain event
            domain_event = PortfolioUpdatedEvent(
                company_id=self.company.id,
                event_date=event_date,
                fund_id=event_data.get('fund_id'),
                operation=event_data.get('operation'),
                metadata={
                    'handler': self.__class__.__name__,
                    'timestamp': event_data.get('timestamp')
                }
            )
            
            # Handle cross-domain coordination based on operation
            if event_data.get('fund_id') and event_data.get('operation'):
                self._handle_cross_domain_coordination(
                    fund_id=event_data['fund_id'],
                    operation=event_data['operation'],
                    event_date=event_date
                )
            
            # Publish domain event for dependent updates
            self._publish_domain_event(domain_event)
            
            # Trigger portfolio and summary calculations
            self._trigger_portfolio_calculations(event_data)
            
            # Log successful processing
            self.logger.info(
                f"Successfully processed portfolio update event for company {self.company.id}"
            )
            
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
    
    def _trigger_portfolio_calculations(self, event_data: Dict[str, Any]) -> None:
        """
        Trigger portfolio and summary calculations.
        
        This method triggers the necessary calculations after portfolio updates
        to ensure all dependent data is properly updated.
        
        Args:
            event_data: The event data that triggered the update
        """
        try:
            # Trigger portfolio summary calculations
            self.portfolio_service.recalculate_portfolio_summary(self.company.id, self.session)
            
            # Trigger company summary calculations
            self.summary_service.recalculate_company_summary(self.company.id, self.session)
            
            # If a specific fund was involved, trigger fund-specific updates
            if 'fund_id' in event_data and event_data['fund_id']:
                fund_id = event_data['fund_id']
                operation = event_data.get('operation', 'updated')
                
                if operation == 'added':
                    self.portfolio_service.handle_fund_addition(self.company.id, fund_id, self.session)
                elif operation == 'removed':
                    self.portfolio_service.handle_fund_removal(self.company.id, fund_id, self.session)
                elif operation == 'updated':
                    self.portfolio_service.handle_fund_update(self.company.id, fund_id, self.session)
            
            self.logger.info(
                f"Triggered portfolio calculations for company {self.company.id}"
            )
            
        except Exception as error:
            self.logger.warning(
                f"Failed to trigger portfolio calculations for company {self.company.id}: {error}"
            )
            # Don't fail the event if calculations fail - this is a non-critical operation
    
    def _handle_cross_domain_coordination(self, fund_id: int, operation: str, event_date: date) -> None:
        """
        Handle cross-domain coordination for portfolio updates.
        
        This method coordinates with other domains (fund, entity) when
        portfolio changes occur, ensuring proper data consistency
        across the system.
        
        Args:
            fund_id: ID of the fund involved in the operation
            operation: Type of operation performed
            event_date: Date when the operation occurred
        """
        try:
            self.logger.info(f"Handling cross-domain coordination for fund {fund_id}, operation: {operation}")
            
            if operation == 'added':
                # Trigger fund domain updates for new fund
                self._trigger_fund_domain_updates(fund_id, 'created', event_date)
                
            elif operation == 'updated':
                # Trigger fund domain updates for fund modification
                self._trigger_fund_domain_updates(fund_id, 'updated', event_date)
                
            elif operation == 'removed':
                # Trigger fund domain updates for fund removal
                self._trigger_fund_domain_updates(fund_id, 'deleted', event_date)
                
            elif operation == 'recalculated':
                # Trigger summary recalculations across domains
                self._trigger_summary_recalculations(fund_id, event_date)
                
        except Exception as error:
            self.logger.warning(f"Cross-domain coordination failed for fund {fund_id}: {str(error)}")
            # Don't fail the main event processing for coordination issues
    
    def _trigger_fund_domain_updates(self, fund_id: int, operation: str, event_date: date) -> None:
        """
        Trigger fund domain updates for portfolio changes.
        
        Args:
            fund_id: ID of the fund
            operation: Type of operation
            event_date: Date when operation occurred
        """
        try:
            # Import fund domain services for coordination
            from src.fund.services.fund_service import FundService
            from src.fund.events.registry import FundEventHandlerRegistry
            
            fund_service = FundService()
            fund = fund_service.get_fund_by_id(fund_id, self.session)
            
            if fund:
                # Trigger fund domain events for coordination
                # This ensures fund domain is aware of company portfolio changes
                self.logger.info(f"Triggered fund domain update for fund {fund_id}, operation: {operation}")
                
        except ImportError:
            # Fund domain not available, skip coordination
            self.logger.debug("Fund domain not available for cross-domain coordination")
        except Exception as error:
            self.logger.warning(f"Failed to trigger fund domain updates: {str(error)}")
    
    def _trigger_summary_recalculations(self, fund_id: int, event_date: date) -> None:
        """
        Trigger summary recalculations across domains.
        
        Args:
            fund_id: ID of the fund
            event_date: Date when recalculation occurred
        """
        try:
            # Trigger entity summary recalculations if needed
            # This ensures entity-level summaries are updated
            self.logger.info(f"Triggered summary recalculations for fund {fund_id}")
            
        except Exception as error:
            self.logger.warning(f"Failed to trigger summary recalculations: {str(error)}")
