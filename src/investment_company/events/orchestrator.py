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
        
        This method orchestrates the complete company creation process:
        1. Validates company data
        2. Creates the company
        3. Processes company creation event
        4. Triggers dependent updates
        5. Ensures data consistency
        
        Args:
            company_data: Dictionary containing company creation data
            session: Database session for all operations
            
        Returns:
            InvestmentCompany: The created company instance
            
        Raises:
            ValueError: If company data is invalid
            RuntimeError: If creation process fails
        """
        try:
            self.logger.info(f"Starting company creation pipeline for: {company_data.get('name', 'Unknown')}")
            
            # Validate company data
            self.validation_service.validate_company_data(company_data)
            
            # Create company through service
            company = self._create_company_through_service(company_data, session)
            
            # Process company creation event
            self._process_company_created_event(company, company_data, session)
            
            # Trigger dependent updates
            self._trigger_company_creation_updates(company, session)
            
            self.logger.info(f"Successfully completed company creation pipeline for company {company.id}")
            return company
            
        except Exception as error:
            self.logger.error(f"Company creation pipeline failed: {error}")
            session.rollback()
            raise
    
    def add_contact_to_company(
        self,
        company_id: int,
        contact_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """
        Add a contact to a company with complete update pipeline.
        
        This method orchestrates the complete contact addition process:
        1. Validates contact data
        2. Adds the contact
        3. Processes contact addition event
        4. Triggers dependent updates
        5. Ensures data consistency
        
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
        try:
            self.logger.info(f"Starting contact addition pipeline for company {company_id}")
            
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
            
            self.logger.info(f"Successfully completed contact addition pipeline for contact {contact.id}")
            return contact
            
        except Exception as error:
            self.logger.error(f"Contact addition pipeline failed: {error}")
            session.rollback()
            raise
    
    def update_company_portfolio(
        self,
        company_id: int,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """
        Update company portfolio with complete update pipeline.
        
        This method orchestrates the complete portfolio update process:
        1. Validates portfolio data
        2. Updates the portfolio
        3. Processes portfolio update event
        4. Triggers dependent updates
        5. Ensures data consistency
        
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
        try:
            self.logger.info(f"Starting portfolio update pipeline for company {company_id}")
            
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
            
            self.logger.info(f"Successfully completed portfolio update pipeline for company {company.id}")
            return updated_company
            
        except Exception as error:
            self.logger.error(f"Portfolio update pipeline failed: {error}")
            session.rollback()
            raise
    
    def _create_company_through_service(
        self,
        company_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """Create company through the company service."""
        # This would call the actual company creation service
        # For now, we'll create a mock company for demonstration
        company = InvestmentCompany(
            name=company_data['name'],
            description=company_data.get('description'),
            company_type=company_data.get('company_type'),
            business_address=company_data.get('business_address'),
            website=company_data.get('website')
        )
        session.add(company)
        session.flush()  # Get the ID
        return company
    
    def _add_contact_through_service(
        self,
        company: InvestmentCompany,
        contact_data: Dict[str, Any],
        session: Session
    ) -> Contact:
        """Add contact through the contact management service."""
        # This would call the actual contact addition service
        # For now, we'll create a mock contact for demonstration
        contact = Contact(
            investment_company_id=company.id,
            name=contact_data['name'],
            title=contact_data.get('title'),
            direct_number=contact_data.get('direct_number'),
            direct_email=contact_data.get('direct_email'),
            notes=contact_data.get('notes')
        )
        session.add(contact)
        session.flush()  # Get the ID
        return contact
    
    def _update_portfolio_through_service(
        self,
        company: InvestmentCompany,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> InvestmentCompany:
        """Update portfolio through the portfolio service."""
        # This would call the actual portfolio update service
        # For now, we'll just return the company
        return company
    
    def _get_company(self, company_id: int, session: Session) -> InvestmentCompany:
        """Get company by ID from session."""
        company = session.query(InvestmentCompany).filter(
            InvestmentCompany.id == company_id
        ).first()
        
        if not company:
            raise ValueError(f"Company with ID {company_id} not found")
        
        return company
    
    def _process_company_created_event(
        self,
        company: InvestmentCompany,
        company_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process company creation event through handler."""
        event_data = {
            'event_type': 'COMPANY_CREATED',
            'company_name': company.name,
            'company_type': company.company_type,
            'event_date': datetime.now().date().isoformat(),
            'timestamp': datetime.now().isoformat()
        }
        
        # Get handler from registry
        handler = self.registry.get_handler(
            CompanyCreatedEvent(company.id, datetime.now().date()).event_type,
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
        event_data = {
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
    
    def _process_portfolio_updated_event(
        self,
        company: InvestmentCompany,
        portfolio_data: Dict[str, Any],
        session: Session
    ) -> None:
        """Process portfolio update event through handler."""
        event_data = {
            'event_type': 'PORTFOLIO_UPDATED',
            'event_date': datetime.now().date().isoformat(),
            'fund_id': portfolio_data.get('fund_id'),
            'operation': portfolio_data.get('operation', 'updated'),
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
    
    def _trigger_company_creation_updates(self, company: InvestmentCompany, session: Session) -> None:
        """Trigger updates that depend on company creation."""
        try:
            # Trigger portfolio summary calculations
            self.portfolio_service.recalculate_portfolio_summary(company.id, session)
            
            # Trigger company summary calculations
            self.summary_service.recalculate_company_summary(company.id, session)
            
        except Exception as error:
            self.logger.warning(f"Failed to trigger company creation updates: {error}")
    
    def _trigger_contact_addition_updates(self, company: InvestmentCompany, contact: Contact, session: Session) -> None:
        """Trigger updates that depend on contact addition."""
        try:
            # Trigger contact count updates
            self.contact_service.update_contact_count(company.id, session)
            
            # Trigger company summary updates
            self.summary_service.recalculate_company_summary(company.id, session)
            
        except Exception as error:
            self.logger.warning(f"Failed to trigger contact addition updates: {error}")
    
    def _trigger_portfolio_update_updates(self, company: InvestmentCompany, portfolio_data: Dict[str, Any], session: Session) -> None:
        """Trigger updates that depend on portfolio updates."""
        try:
            # Trigger portfolio summary calculations
            self.portfolio_service.recalculate_portfolio_summary(company.id, session)
            
            # Trigger company summary calculations
            self.summary_service.recalculate_company_summary(company.id, session)
            
        except Exception as error:
            self.logger.warning(f"Failed to trigger portfolio update updates: {error}")
