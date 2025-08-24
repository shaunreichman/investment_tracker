"""
Event-Driven Workflows Integration Tests.

This module tests the event-driven architecture of the investment company system,
ensuring that events properly flow through the complete pipeline and trigger
appropriate state changes and dependent updates.

Key testing areas:
- Event-driven company creation workflow
- Event-driven contact management workflows
- Event-driven company updates and deletion
- Event system integration and coordination
- Event handler coordination and rollback scenarios
- System robustness and error handling

These tests focus on the EVENT SYSTEM specifically, not business logic
(which is covered by other workflow test files).
"""

import pytest
from datetime import datetime, timezone, date
from sqlalchemy.orm import Session
from typing import Dict, Any
from decimal import Decimal
from unittest.mock import patch, MagicMock

from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.services import CompanyService
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.events.orchestrator import CompanyUpdateOrchestrator
from src.investment_company.events.registry import CompanyEventHandlerRegistry
from src.investment_company.events.handlers import (
    CompanyCreatedHandler,
    ContactAddedHandler,
    ContactUpdatedHandler,
    CompanyUpdatedHandler,
    PortfolioUpdatedHandler,
    CompanyDeletedHandler
)
from src.investment_company.events.domain import (
    CompanyCreatedEvent,
    ContactAddedEvent,
    ContactUpdatedEvent,
    CompanyUpdatedEvent,
    PortfolioUpdatedEvent,
    CompanyDeletedEvent
)
from src.investment_company.enums import CompanyType, CompanyStatus, CompanyDomainEventType
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType
from src.entity.models import Entity
from tests.factories import InvestmentCompanyFactory, ContactFactory, FundFactory, EntityFactory


class TestEventDrivenWorkflows:
    """Test event-driven workflows through the complete event system."""
    
    def test_event_driven_company_creation_workflow(self, db_session: Session):
        """Test complete event-driven company creation workflow."""
        # Arrange: Prepare company data
        company_data = {
            'name': 'Event-Driven Test Company',
            'description': 'Company for testing event-driven workflows',
            'website': 'https://eventdriven.com',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'business_address': '123 Event Street, Test City',
            'status': CompanyStatus.ACTIVE
        }
        
        # Act: Create company through orchestrator (event-driven)
        orchestrator = CompanyUpdateOrchestrator()
        company = orchestrator.create_company(company_data, db_session)
        
        # Assert: Verify company was created through event system
        assert company is not None
        assert company.id is not None
        assert company.name == company_data['name']
        
        # Verify event was processed (check that handler was called)
        # The orchestrator should have triggered the complete event pipeline
        db_session.refresh(company)
        assert company.created_at is not None
        assert company.updated_at is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_driven_contact_addition_workflow(self, db_session: Session):
        """Test event-driven contact addition workflow."""
        # Arrange: Create company and prepare contact data
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        contact_data = {
            'name': 'Event Test Contact',
            'email': 'contact@eventdriven.com',
            'phone': '+1234567890',
            'title': 'Test Manager',
            'is_primary': True
        }
        
        # Act: Add contact through orchestrator (event-driven)
        orchestrator = CompanyUpdateOrchestrator()
        contact = orchestrator.add_contact_to_company(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        
        # Assert: Verify contact was added through event system
        assert contact is not None
        assert contact.id is not None
        assert contact.name == contact_data['name']
        assert contact.investment_company_id == company.id  # Fixed: use correct attribute name
        
        # Verify event was processed
        db_session.refresh(contact)
        assert contact.created_at is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_driven_company_update_workflow(self, db_session: Session):
        """Test event-driven company update workflow."""
        # Arrange: Create company and update data
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        update_data = {
            'description': 'Updated company description through event system',
            'website': 'https://updated-eventdriven.com',
            'status': CompanyStatus.ACTIVE
        }
        
        # Act: Update company through orchestrator (event-driven)
        orchestrator = CompanyUpdateOrchestrator()
        updated_company_result = orchestrator.update_company(
            company_id=company.id,
            update_data=update_data,
            session=db_session
        )
        
        # Assert: Verify company was updated through event system
        # Fixed: Company update returns a dict, not the company object
        assert updated_company_result is not None
        assert isinstance(updated_company_result, dict)
        assert updated_company_result['description'] == update_data['description']
        assert updated_company_result['website'] == update_data['website']
        
        # Verify event was processed by checking the original company object
        db_session.refresh(company)
        assert company.updated_at is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_integration_workflow(self, db_session: Session):
        """Test complete event system integration workflow."""
        # Arrange: Prepare comprehensive test data
        company_data = {
            'name': 'Event Integration Test Company',
            'description': 'Company for testing complete event system integration',
            'company_type': CompanyType.VENTURE_CAPITAL,
            'status': CompanyStatus.ACTIVE
        }
        
        contact_data = {
            'name': 'Integration Test Contact',
            'email': 'integration@eventtest.com',
            'title': 'Integration Manager'
        }
        
        # Act: Execute complete workflow through event system
        orchestrator = CompanyUpdateOrchestrator()
        
        # 1. Create company (triggers CompanyCreatedEvent)
        company = orchestrator.create_company(company_data, db_session)
        
        # 2. Add contact (triggers ContactAddedEvent)
        contact = orchestrator.add_contact_to_company(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        
        # 3. Update company (triggers CompanyUpdatedEvent)
        update_data = {'description': 'Updated through integration test'}
        updated_company_result = orchestrator.update_company(
            company_id=company.id,
            update_data=update_data,
            session=db_session
        )
        
        # Assert: Verify complete event system integration
        assert company is not None
        assert contact is not None
        assert updated_company_result is not None
        
        # Verify all events were processed
        db_session.refresh(company)
        db_session.refresh(contact)
        # Fixed: Don't refresh dict result
        
        assert company.created_at is not None
        assert contact.created_at is not None
        assert company.updated_at is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_handler_coordination_workflow(self, db_session: Session):
        """Test event handler coordination workflow."""
        # Arrange: Create company and prepare multiple operations
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        # Act: Execute multiple operations that trigger different handlers
        orchestrator = CompanyUpdateOrchestrator()
        
        # 1. Add contact (triggers ContactAddedHandler)
        # Fixed: Include title field to avoid validation error
        contact_data = {
            'name': 'Coordinated Contact', 
            'email': 'coord@test.com',
            'title': 'Coordinator'  # Required field
        }
        contact = orchestrator.add_contact_to_company(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        
        # 2. Update company (triggers CompanyUpdatedHandler)
        update_data = {'description': 'Coordinated company update'}
        updated_company_result = orchestrator.update_company(
            company_id=company.id,
            update_data=update_data,
            session=db_session
        )
        
        # Assert: Verify all handlers coordinated correctly
        assert contact is not None
        assert updated_company_result is not None
        
        # Verify coordination through event system
        db_session.refresh(company)
        db_session.refresh(contact)
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_error_handling_workflow(self, db_session: Session):
        """Test event system error handling and rollback workflow."""
        # Arrange: Create company
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        # Act & Assert: Test error handling in event system
        orchestrator = CompanyUpdateOrchestrator()
        
        # Test with invalid data that should trigger validation errors
        invalid_contact_data = {
            'name': '',  # Invalid: empty name
            'email': 'invalid-email',  # Invalid: malformed email
            'title': 'Test Manager'
        }
        
        # This should raise a validation error
        with pytest.raises((ValueError, RuntimeError)):
            orchestrator.add_contact_to_company(
                company_id=company.id,
                contact_data=invalid_contact_data,
                session=db_session
            )
        
        # Verify system state is consistent after error
        db_session.refresh(company)
        # Company should still exist and be in valid state
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_performance_workflow(self, db_session: Session):
        """Test event system performance under load."""
        # Arrange: Create multiple companies for performance testing
        companies = []
        for i in range(5):  # Test with 5 companies
            company = InvestmentCompanyFactory(
                name=f'Performance Test Company {i}',
                description=f'Company {i} for performance testing'
            )
            companies.append(company)
        
        db_session.add_all(companies)
        db_session.flush()
        
        # Act: Execute event-driven operations on all companies
        orchestrator = CompanyUpdateOrchestrator()
        start_time = datetime.now()
        
        for company in companies:
            # Update each company through event system
            update_data = {
                'description': f'Updated description for {company.name}',
                'status': CompanyStatus.ACTIVE
            }
            
            orchestrator.update_company(
                company_id=company.id,
                update_data=update_data,
                session=db_session
            )
        
        end_time = datetime.now()
        execution_time = (end_time - start_time).total_seconds()
        
        # Assert: Verify performance is acceptable
        # Event system should handle multiple operations efficiently
        assert execution_time < 5.0  # Should complete within 5 seconds
        
        # Verify all updates were processed
        for company in companies:
            db_session.refresh(company)
            assert company.updated_at is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_data_consistency_workflow(self, db_session: Session):
        """Test event system data consistency across operations."""
        # Arrange: Create company with initial state
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        initial_company_state = {
            'name': company.name,
            'description': company.description,
            'status': company.status
        }
        
        # Act: Execute multiple event-driven operations
        orchestrator = CompanyUpdateOrchestrator()
        
        # 1. Add contact
        # Fixed: Include title field to avoid validation error
        contact_data = {
            'name': 'Consistency Contact', 
            'email': 'consistency@test.com',
            'title': 'Consistency Manager'  # Required field
        }
        contact = orchestrator.add_contact_to_company(
            company_id=company.id,
            contact_data=contact_data,
            session=db_session
        )
        
        # 2. Update company
        update_data = {'description': 'Updated for consistency testing'}
        updated_company_result = orchestrator.update_company(
            company_id=company.id,
            update_data=update_data,
            session=db_session
        )
        
        # Assert: Verify data consistency maintained through event system
        assert contact is not None
        assert updated_company_result is not None
        
        # Verify company state is consistent
        db_session.refresh(company)
        assert company.name == initial_company_state['name']  # Name unchanged
        assert company.description == update_data['description']  # Description updated
        assert company.status == initial_company_state['status']  # Status unchanged
        
        # Verify contact relationship maintained
        assert contact.investment_company_id == company.id  # Fixed: use correct attribute name
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_cross_domain_coordination_workflow(self, db_session: Session):
        """Test event system cross-domain coordination workflow."""
        # Arrange: Create company and entity for cross-domain testing
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        db_session.add_all([company, entity])
        db_session.flush()
        
        # Act: Execute cross-domain operations through event system
        orchestrator = CompanyUpdateOrchestrator()
        
        # 1. Create company (triggers company domain events)
        company_data = {
            'name': 'Cross-Domain Test Company',
            'description': 'Company for testing cross-domain coordination',
            'company_type': CompanyType.PRIVATE_EQUITY
        }
        
        new_company = orchestrator.create_company(company_data, db_session)
        
        # 2. Add contact (triggers contact domain events)
        # Fixed: Include title field to avoid validation error
        contact_data = {
            'name': 'Cross-Domain Contact',
            'email': 'crossdomain@test.com',
            'title': 'Cross-Domain Manager'  # Required field
        }
        
        contact = orchestrator.add_contact_to_company(
            company_id=new_company.id,
            contact_data=contact_data,
            session=db_session
        )
        
        # 3. Update company (triggers company update events)
        update_data = {'description': 'Cross-domain coordination test'}
        updated_company_result = orchestrator.update_company(
            company_id=new_company.id,
            update_data=update_data,
            session=db_session
        )
        
        # Assert: Verify cross-domain coordination through event system
        assert new_company is not None
        assert contact is not None
        assert updated_company_result is not None
        
        # Verify cross-domain relationships maintained
        assert contact.investment_company_id == new_company.id  # Fixed: use correct attribute name
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_registry_integration(self, db_session: Session):
        """Test event system registry integration and handler discovery."""
        # Arrange: Create company for testing
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        # Act: Test event registry functionality
        registry = CompanyEventHandlerRegistry()
        
        # Test that handlers are properly registered
        assert registry.get_handler(
            CompanyDomainEventType.COMPANY_CREATED,
            db_session,
            company
        ) is not None
        
        assert registry.get_handler(
            CompanyDomainEventType.CONTACT_ADDED,
            db_session,
            company
        ) is not None
        
        # Cleanup
        db_session.rollback()
    
    def test_event_system_handler_validation(self, db_session: Session):
        """Test event system handler validation and error handling."""
        # Arrange: Create company
        company = InvestmentCompanyFactory()
        db_session.add(company)
        db_session.flush()
        
        # Act: Test handler validation
        registry = CompanyEventHandlerRegistry()
        
        # Test that invalid event types raise appropriate errors
        with pytest.raises((ValueError, KeyError)):
            # This should fail as the event type doesn't exist
            registry.get_handler(
                "INVALID_EVENT_TYPE",
                db_session,
                company
            )
        
        # Cleanup
        db_session.rollback()
