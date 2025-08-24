"""
Base Company Event Handler.

This module provides the base class for all company event handlers,
defining the common interface and shared functionality.

Key responsibilities:
- Common event processing logic
- Event validation and error handling
- Event relationship management
- Event publishing and side effects
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyDomainEventType, CompanyOperationType
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService


class BaseCompanyEventHandler(ABC):
    """
    Abstract base class for all company event handlers.
    
    Each handler is responsible for:
    1. Validating the event data
    2. Processing the event and updating the company
    3. Publishing domain events for dependent updates
    4. Managing transaction boundaries
    
    This class provides common functionality and enforces the contract
    that all handlers must implement.
    """
    
    def __init__(self, session: Session, company: InvestmentCompany):
        """
        Initialize the handler with session and company.
        
        Args:
            session: Database session for all operations
            company: Company instance to operate on
        """
        self.session = session
        self.company = company
        
        # Initialize logger
        self.logger = logging.getLogger(__name__)
        
        # Initialize services for business logic
        self.portfolio_service = CompanyPortfolioService()
        self.summary_service = CompanySummaryService()
        self.contact_service = ContactManagementService()
        self.validation_service = CompanyValidationService()
    
    @abstractmethod
    def handle(self, event_data: Dict[str, Any]) -> Any:
        """
        Handle the event and return the result.
        
        This is the main entry point that all handlers must implement.
        It should:
        1. Validate the event data
        2. Process the event
        3. Update company state as needed
        4. Publish domain events
        5. Return the result
        
        Args:
            event_data: Dictionary containing event parameters
            
        Returns:
            Any: The result of processing the event
            
        Raises:
            ValueError: If event data is invalid
            RuntimeError: If event processing fails
        """
        pass
    
    @abstractmethod
    def validate_event(self, event_data: Dict[str, Any]) -> None:
        """
        Validate event data before processing.
        
        Args:
            event_data: Dictionary containing event parameters
            
        Raises:
            ValueError: If validation fails
        """
        pass
    
    def _get_company(self, company_id: int) -> InvestmentCompany:
        """
        Get company by ID from the current session.
        
        Args:
            company_id: ID of the company to retrieve
            
        Returns:
            InvestmentCompany: Company instance
            
        Raises:
            ValueError: If company not found
        """
        company = self.session.query(InvestmentCompany).filter(
            InvestmentCompany.id == company_id
        ).first()
        
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        return company
    
    def _get_contact(self, contact_id: int) -> Contact:
        """
        Get contact by ID from the current session.
        
        Args:
            contact_id: ID of the contact to retrieve
            
        Returns:
            Contact: Contact instance
            
        Raises:
            ValueError: If contact not found
        """
        contact = self.session.query(Contact).filter(
            Contact.id == contact_id
        ).first()
        
        if not contact:
            raise ValueError(f"Contact with ID {contact_id} not found")
        
        return contact
    
    def _publish_domain_event(self, domain_event: Any) -> None:
        """
        Publish a domain event for dependent updates.
        
        This method will be implemented to integrate with the event bus
        system. For now, it logs the event for debugging purposes.
        
        Args:
            domain_event: Domain event to publish
        """
        self.logger.info(f"Publishing domain event: {domain_event}")
        # TODO: Integrate with event bus system
        # self.event_bus.publish(domain_event)
    
    def _log_event_processing(self, event_type: str, event_data: Dict[str, Any]) -> None:
        """
        Log event processing for debugging and monitoring.
        
        Args:
            event_type: Type of event being processed
            event_data: Event data being processed
        """
        self.logger.info(
            f"Processing {event_type} event for company {self.company.id}: {event_data}"
        )
    
    def _handle_error(self, error: Exception, event_data: Dict[str, Any]) -> None:
        """
        Handle errors during event processing.
        
        Args:
            error: Exception that occurred
            event_data: Event data that caused the error
        """
        self.logger.error(
            f"Error processing event for company {self.company.id}: {error}",
            extra={
                'company_id': self.company.id,
                'event_data': event_data,
                'error': str(error)
            }
        )
        raise error
    
    def _validate_company_exists(self) -> None:
        """
        Validate that the company still exists in the session.
        
        Raises:
            ValueError: If company no longer exists
        """
        if not self.company or self.company.id is None:
            raise ValueError("Company instance is invalid or has no ID")
        
        # Refresh from database to ensure it still exists
        self.session.refresh(self.company)
    
    def _validate_required_fields(self, event_data: Dict[str, Any], required_fields: List[str]) -> None:
        """
        Validate that required fields are present in event data.
        
        Args:
            event_data: Event data to validate
            required_fields: List of required field names
            
        Raises:
            ValueError: If any required fields are missing
        """
        missing_fields = [field for field in required_fields if field not in event_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {missing_fields}")
    
    def _validate_field_types(self, event_data: Dict[str, Any], field_types: Dict[str, type]) -> None:
        """
        Validate that fields have the correct types.
        
        Args:
            event_data: Event data to validate
            field_types: Dictionary mapping field names to expected types
            
        Raises:
            ValueError: If any fields have incorrect types
        """
        for field_name, expected_type in field_types.items():
            if field_name in event_data:
                value = event_data[field_name]
                if not isinstance(value, expected_type):
                    raise ValueError(
                        f"Field '{field_name}' must be of type {expected_type.__name__}, "
                        f"got {type(value).__name__}"
                    )
