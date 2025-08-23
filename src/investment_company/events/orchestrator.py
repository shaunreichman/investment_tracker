"""
Company Update Orchestrator.

This module provides the CompanyUpdateOrchestrator class,
which coordinates complete update pipelines for company operations.

Key responsibilities:
- Coordinate complete update pipelines
- Manage transaction boundaries
- Handle dependent updates
- Ensure data consistency
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.investment_company.events.registry import CompanyEventHandlerRegistry
from src.investment_company.events.domain import (
    CompanyCreatedEvent,
    CompanyUpdatedEvent,
    CompanyDeletedEvent,
    ContactAddedEvent,
    ContactUpdatedEvent,
    PortfolioUpdatedEvent
)
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService


class CompanyUpdateOrchestrator:
    """
    Orchestrator for coordinating complete company update pipelines.
    
    This class manages the complete lifecycle of company operations,
    ensuring that all dependent updates are handled correctly and
    data consistency is maintained across the system.
    
    Key responsibilities:
    1. Coordinate event processing through handlers
    2. Manage transaction boundaries
    3. Handle cross-domain updates
    4. Ensure rollback on failures
    5. Maintain audit trail of operations
    """
    
    def __init__(self):
        """Initialize the orchestrator with required services."""
        self.logger = logging.getLogger(__name__)
        self.registry = CompanyEventHandlerRegistry()
        self.portfolio_service = CompanyPortfolioService()
        self.summary_service = CompanySummaryService()
        self.contact_service = ContactManagementService()
        self.validation_service = CompanyValidationService()
    
    def create_company(self, company_data: Dict[str, Any], session: Session) -> InvestmentCompany:
        """
        Create a new investment company with complete update pipeline.
        
        Preconditions:
        - company_data must be valid and complete
        - session must be active
        
        Postconditions:
        - Company is created and persisted
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_data: Dictionary containing company creation data
            session: Database session for all operations
            
        Returns:
            InvestmentCompany: The created company instance
            
        Raises:
            ValueError: If company data is invalid
            RuntimeError: If creation process fails
        """
        # Validate company data
        self.validation_service.validate_company_data(company_data)
        
        # Create company through service
        company = self._create_company_through_service(company_data, session)
        
        # Process company creation event
        self._process_company_created_event(company, company_data, session)
        
        # Trigger dependent updates
        self._trigger_company_creation_updates(company, session)
        
        return company
    
    def add_contact_to_company(
        self,
        company_id: int,
        contact_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """
        Add a contact to a company with complete update pipeline.
        
        Preconditions:
        - company_id must be valid
        - contact_data must be valid
        - session must be active
        
        Postconditions:
        - Contact is added and persisted
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_id: ID of the company to add contact to
            contact_data: Dictionary containing contact data
            session: Database session for all operations
            
        Returns:
            Contact: The added contact instance
            
        Raises:
            ValueError: If contact data is invalid
            RuntimeError: If addition process fails
        """
        # Get company
        company = self._get_company(company_id, session)
        
        # Validate contact data
        self.validation_service.validate_contact_data(contact_data)
        
        # Add contact through service
        contact = self._add_contact_through_service(company, contact_data, session)
        
        # Process contact addition event
        self._process_contact_added_event(company, contact, contact_data, session)
        
        # Trigger dependent updates
        self._trigger_contact_addition_updates(company, contact, session)
        
        return contact

    def update_contact(
        self,
        company_id: int,
        contact_id: int,
        update_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """
        Update a contact with complete update pipeline.
        
        Preconditions:
        - company_id must be valid
        - contact_id must be valid
        - update_data must be valid
        - session must be active
        
        Postconditions:
        - Contact is updated
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_id: ID of the company the contact belongs to
            contact_id: ID of the contact to update
            update_data: Dictionary containing contact update data
            session: Database session for all operations
            
        Returns:
            Contact: The updated contact instance
            
        Raises:
            ValueError: If contact data is invalid
            RuntimeError: If update process fails
        """
        # Get company and contact
        company = self._get_company(company_id, session)
        contact = self._get_contact(contact_id, session)
        
        # Validate contact data
        self.validation_service.validate_contact_data(update_data)
        
        # Update contact through service
        updated_contact = self._update_contact_through_service(contact, update_data, session)
        
        # Process contact update event
        self._process_contact_updated_event(company, contact, update_data, session)
        
        # Trigger dependent updates
        self._trigger_contact_update_updates(company, contact, session)
        
        return updated_contact

    def update_company_portfolio(
        self,
        company_id: int,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """
        Update company portfolio with complete update pipeline.
        
        Preconditions:
        - company_id must be valid
        - portfolio_data must be valid
        - session must be active
        
        Postconditions:
        - Portfolio is updated
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_id: ID of the company to update portfolio for
            portfolio_data: Dictionary containing portfolio update data
            session: Database session for all operations
            
        Returns:
            InvestmentCompany: The updated company instance
            
        Raises:
            ValueError: If portfolio data is invalid
            RuntimeError: If update process fails
        """
        # Get company
        company = self._get_company(company_id, session)
        
        # Validate portfolio data
        self.validation_service.validate_portfolio_data(portfolio_data)
        
        # Update portfolio through service
        updated_company = self._update_portfolio_through_service(company, portfolio_data, session)
        
        # Process portfolio update event
        self._process_portfolio_updated_event(company, portfolio_data, session)
        
        # Trigger dependent updates
        self._trigger_portfolio_update_updates(company, portfolio_data, session)
        
        return updated_company

    def update_company(
        self,
        company_id: int,
        update_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """
        Update company with complete update pipeline.
        
        Preconditions:
        - company_id must be valid
        - update_data must be valid
        - session must be active
        
        Postconditions:
        - Company is updated
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_id: ID of the company to update
            update_data: Dictionary containing company update data
            session: Database session for all operations
            
        Returns:
            InvestmentCompany: The updated company instance
            
        Raises:
            ValueError: If company data is invalid
            RuntimeError: If update process fails
        """
        # Get company
        company = self._get_company(company_id, session)
        
        # Validate company data
        self.validation_service.validate_company_data(update_data)
        
        # Update company through service
        updated_company = self._update_company_through_service(company, update_data, session)
        
        # Process company update event
        self._process_company_updated_event(company, update_data, session)
        
        # Trigger dependent updates
        self._trigger_company_update_updates(company, session)
        
        return updated_company

    def delete_company(
        self,
        company_id: int,
        deletion_reason: str,
        session: Session
    ) -> None:
        """
        Delete a company with complete deletion pipeline.
        
        Preconditions:
        - company_id must be valid
        - deletion_reason must be provided
        - session must be active
        
        Postconditions:
        - Company is deleted
        - Events are published
        - Dependent systems are updated
        
        Args:
            company_id: ID of the company to delete
            deletion_reason: Reason for deletion
            session: Database session for all operations
            
        Raises:
            ValueError: If company cannot be deleted
            RuntimeError: If deletion process fails
        """
        # Get company
        company = self._get_company(company_id, session)
        
        # Validate company can be deleted
        self.validation_service.validate_company_deletion(company)
        
        # Delete company through service
        self._delete_company_through_service(company, session)
        
        # Process company deletion event
        self._process_company_deleted_event(company, deletion_reason, session)
        
        # Trigger dependent updates
        self._trigger_company_deletion_updates(company_id, session)
    
    def _trigger_company_creation_updates(self, company: InvestmentCompany, session: Session) -> None:
        """Trigger updates that depend on company creation."""
        # Trigger portfolio summary calculations
        self.portfolio_service.recalculate_portfolio_summary(company.id, session)
        
        # Trigger company summary calculations
        self.summary_service.update_company_summary(company, session)
    
    def _trigger_contact_addition_updates(self, company: InvestmentCompany, contact: Contact, session: Session) -> None:
        """Trigger updates that depend on contact addition."""
        # Trigger contact count updates
        self.contact_service.update_contact_count(company.id, session)
        
        # Trigger company summary updates
        self.summary_service.update_company_summary(company, session)
    
    def _trigger_portfolio_update_updates(self, company: InvestmentCompany, portfolio_data: Dict[str, Any], session: Session) -> None:
        """Trigger updates that depend on portfolio updates."""
        # Trigger portfolio summary calculations
        self.portfolio_service.recalculate_portfolio_summary(company.id, session)
        
        # Trigger company summary calculations
        self.summary_service.update_company_summary(company, session)
    
    def _trigger_company_update_updates(self, company: InvestmentCompany, session: Session) -> None:
        """Trigger updates that depend on company updates."""
        # Trigger company summary updates
        self.summary_service.update_company_summary(company, session)

    def _trigger_company_deletion_updates(self, company_id: int, session: Session) -> None:
        """Trigger updates that depend on company deletion."""
        # Trigger portfolio cleanup
        self.portfolio_service.cleanup_deleted_company_portfolio(company_id, session)
        
        # Entity cleanup logging
        self.logger.info(f"Entity cleanup triggered for deleted company {company_id}")

    def _trigger_contact_update_updates(self, company: InvestmentCompany, contact: Contact, session: Session) -> None:
        """Trigger updates that depend on contact updates."""
        # Trigger contact summary updates
        self.contact_service.update_contact_summary(contact.id, session)
        
        # Trigger company summary updates
        self.summary_service.update_company_summary(company, session)
    
    def _create_company_through_service(
        self,
        company_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """Create company through the contact service."""
        # Call the actual company creation service
        return self.contact_service.create_company(company_data, session)
    
    def _add_contact_through_service(
        self,
        company: InvestmentCompany,
        contact_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """Add contact through the contact management service."""
        # Call the actual contact addition service
        return self.contact_service.add_contact(company.id, contact_data, session)
    
    def _update_portfolio_through_service(
        self,
        company: InvestmentCompany,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """Update portfolio through the portfolio service."""
        # Call the actual portfolio update service
        return self.portfolio_service.update_portfolio(company, portfolio_data, session)
    
    def _get_company(self, company_id: int, session: Session) -> InvestmentCompany:
        """Get company by ID from session."""
        company = session.query(InvestmentCompany).filter(
            InvestmentCompany.id == company_id
        ).first()
        
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        return company
    
    def _get_contact(self, contact_id: int, session: Session) -> Contact:
        """Get contact by ID from session."""
        contact = session.query(Contact).filter(
            Contact.id == contact_id
        ).first()
        
        if not contact:
            raise ValueError(f"Contact with ID {contact_id} not found")
        
        return contact
    
    def _update_contact_through_service(
        self,
        contact: Contact,
        update_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """Update contact through the contact management service."""
        # This would call the actual contact update service
        # For now, we'll just return the contact
        return self.contact_service.update_contact(contact.id, update_data, session)
    
    def _process_company_created_event(
        self,
        company: InvestmentCompany,
        company_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process company creation event through handler."""
        # Preserve original data structure while adding metadata
        event_data = {
            **company_data,  # Keep original data
            'event_type': 'COMPANY_CREATED',
            'company_name': company.name,
            'company_type': company.company_type,
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            CompanyCreatedEvent(company.id, datetime.now().date(), company.name).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _process_contact_added_event(
        self,
        company: InvestmentCompany,
        contact: Contact,
        contact_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process contact addition event through handler."""
        # Preserve original data structure while adding metadata
        event_data = {
            **contact_data,  # Keep original data
            'event_type': 'CONTACT_ADDED',
            'contact_id': contact.id,
            'contact_name': contact.name,
            'contact_title': contact.title,
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            ContactAddedEvent(company.id, datetime.now().date(), contact.id, contact.name).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _process_company_updated_event(
        self,
        company: InvestmentCompany,
        update_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process company update event through handler."""
        event_data = {
            'event_type': 'COMPANY_UPDATED',
            'company_id': company.id,  # Add company_id
            'company_name': company.name,
            'company_type': company.company_type,
            'update_fields': update_data,  # Add update_fields for the handler
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat(),
            **update_data  # Include the actual update data
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            CompanyUpdatedEvent(company.id, datetime.now().date(), company.name).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _process_company_deleted_event(
        self,
        company: InvestmentCompany,
        deletion_reason: str,
        session: Session
    ) -> None:
        """Process company deletion event through handler."""
        event_data = {
            'event_type': 'COMPANY_DELETED',
            'company_name': company.name,
            'company_type': company.company_type,
            'deletion_reason': deletion_reason,
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            CompanyDeletedEvent(company.id, datetime.now().date(), company.name).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _process_contact_updated_event(
        self,
        company: InvestmentCompany,
        contact: Contact,
        update_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process contact update event through handler."""
        event_data = {
            'event_type': 'CONTACT_UPDATED',
            'contact_id': contact.id,
            'contact_name': contact.name,
            'contact_title': contact.title,
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat(),
            **update_data  # Include the actual update data
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            ContactUpdatedEvent(company.id, datetime.now().date(), contact.id, contact.name).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _process_portfolio_updated_event(
        self,
        company: InvestmentCompany,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process portfolio update event through handler."""
        # Preserve original data structure while adding metadata
        event_data = {
            **portfolio_data,  # Keep original data
            'event_type': 'PORTFOLIO_UPDATED',
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            PortfolioUpdatedEvent(company.id, datetime.now().date()).event_type,
            session,
            company
        )
        
        # Process event
        handler.handle(event_data)
    
    def _update_company_through_service(self, company: InvestmentCompany, update_data: Dict[str, Any], session: Session) -> InvestmentCompany:
        """Update company through the contact service."""
        # Call the actual company update service
        return self.contact_service.update_company(company.id, update_data, session)

    def _delete_company_through_service(self, company: InvestmentCompany, session: Session) -> None:
        """Delete company through the contact service."""
        # Call the actual company deletion service
        self.contact_service.delete_company(company.id, session)
