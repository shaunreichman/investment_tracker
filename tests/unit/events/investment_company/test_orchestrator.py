"""
Test Investment Company Event Orchestrator.

This module tests the CompanyUpdateOrchestrator class to ensure it properly
coordinates complete update pipelines and maintains data consistency.

Key testing areas:
- Pipeline coordination and sequencing
- Transaction boundary management
- Error handling and rollback
- Service integration and coordination
- Event processing orchestration
- Data consistency validation

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Orchestrator should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from sqlalchemy.exc import SQLAlchemyError

from src.investment_company.events.orchestrator import CompanyUpdateOrchestrator
from src.investment_company.events.registry import CompanyEventHandlerRegistry
from src.investment_company.events.domain import (
    CompanyCreatedEvent,
    CompanyUpdatedEvent,
    CompanyDeletedEvent,
    ContactAddedEvent,
    PortfolioUpdatedEvent
)
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus, CompanyDomainEventType
from src.investment_company.services.company_portfolio_service import CompanyPortfolioService
from src.investment_company.services.company_summary_service import CompanySummaryService
from src.investment_company.services.contact_management_service import ContactManagementService
from src.investment_company.services.company_validation_service import CompanyValidationService


class TestCompanyUpdateOrchestrator:
    """Test the CompanyUpdateOrchestrator class functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock(spec=InvestmentCompany)
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        self.mock_company.company_type = CompanyType.PRIVATE_EQUITY
        self.mock_company.status = CompanyStatus.ACTIVE
        
        # Mock the services with actual methods that exist
        self.mock_portfolio_service = Mock(spec=CompanyPortfolioService)
        self.mock_summary_service = Mock(spec=CompanySummaryService)
        self.mock_contact_service = Mock(spec=ContactManagementService)
        self.mock_validation_service = Mock(spec=CompanyValidationService)
        
        # Mock the actual methods that exist in the services
        self.mock_portfolio_service.recalculate_portfolio_summary = Mock()
        self.mock_portfolio_service.update_portfolio = Mock()
        self.mock_portfolio_service.cleanup_deleted_company_portfolio = Mock()
        self.mock_summary_service.update_company_summary = Mock()
        self.mock_contact_service.update_contact_count = Mock()
        self.mock_contact_service.update_contact_summary = Mock()
        self.mock_contact_service.get_company = Mock()
        self.mock_contact_service.create_company = Mock()
        self.mock_contact_service.update_company = Mock()
        self.mock_contact_service.delete_company = Mock()
        self.mock_contact_service.add_contact = Mock()
        self.mock_contact_service.get_contact = Mock()
        self.mock_contact_service.update_contact = Mock()
        self.mock_validation_service.validate_company_data = Mock()
        self.mock_validation_service.validate_contact_data = Mock()
        self.mock_validation_service.validate_portfolio_data = Mock()
        self.mock_validation_service.validate_company_deletion = Mock()
        
        # Create orchestrator instance
        self.orchestrator = CompanyUpdateOrchestrator()
        
        # Patch the services to use our mocks
        self.orchestrator.portfolio_service = self.mock_portfolio_service
        self.orchestrator.summary_service = self.mock_summary_service
        self.orchestrator.contact_service = self.mock_contact_service
        self.orchestrator.validation_service = self.mock_validation_service
        
        # Mock the session query for _get_company and _get_contact methods
        self.mock_query = Mock()
        self.mock_filter = Mock()
        self.mock_first = Mock()
        
        # Setup the query chain
        self.mock_session.query.return_value = self.mock_query
        self.mock_query.filter.return_value = self.mock_filter
        self.mock_filter.first.return_value = self.mock_company
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes with required dependencies."""
        orchestrator = CompanyUpdateOrchestrator()
        
        assert orchestrator.logger is not None
        assert orchestrator.registry is not None
        assert isinstance(orchestrator.registry, CompanyEventHandlerRegistry)
        assert orchestrator.portfolio_service is not None
        assert orchestrator.summary_service is not None
        assert orchestrator.contact_service is not None
        assert orchestrator.validation_service is not None
    
    def test_create_company_success(self):
        """Test successful company creation pipeline."""
        company_data = {
            'name': 'New Test Company',
            'company_type': CompanyType.VENTURE_CAPITAL,
            'description': 'A new test company',
            'website': 'https://newtest.com'
        }
        
        # Mock successful service calls
        self.mock_validation_service.validate_company_data.return_value = None
        self.mock_contact_service.create_company.return_value = self.mock_company
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_company_created_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_company_creation_updates') as mock_trigger:
            
            result = self.orchestrator.create_company(company_data, self.mock_session)
            
            assert result == self.mock_company
            
            # Verify the pipeline was executed
            mock_process.assert_called_once_with(self.mock_company, company_data, self.mock_session)
            mock_trigger.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_update_company_success(self):
        """Test successful company update pipeline."""
        company_id = 1
        update_data = {
            'name': 'Updated Test Company',
            'description': 'Updated description'
        }
        
        # Mock successful service calls
        self.mock_validation_service.validate_company_data.return_value = None
        self.mock_contact_service.update_company.return_value = self.mock_company
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_company_updated_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_company_update_updates') as mock_trigger:
            
            result = self.orchestrator.update_company(company_id, update_data, self.mock_session)
            
            assert result == self.mock_company
            
            # Verify the pipeline was executed
            mock_process.assert_called_once_with(self.mock_company, update_data, self.mock_session)
            mock_trigger.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_update_company_not_found(self):
        """Test company update fails when company doesn't exist."""
        company_id = 999
        update_data = {'name': 'Updated Name'}
        
        # Mock company not found by setting the session query to return None
        self.mock_filter.first.return_value = None
        
        with pytest.raises(ValueError, match="Company with ID 999 not found"):
            self.orchestrator.update_company(company_id, update_data, self.mock_session)
    
    def test_delete_company_success(self):
        """Test successful company deletion pipeline."""
        company_id = 1
        deletion_reason = "Company closure"
        
        # Mock successful service calls
        self.mock_validation_service.validate_company_deletion.return_value = None
        self.mock_contact_service.delete_company.return_value = None
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_company_deleted_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_company_deletion_updates') as mock_trigger:
            
            result = self.orchestrator.delete_company(company_id, deletion_reason, self.mock_session)
            
            assert result is None
            
            # Verify the pipeline was executed
            mock_process.assert_called_once_with(self.mock_company, deletion_reason, self.mock_session)
            mock_trigger.assert_called_once_with(company_id, self.mock_session)
    
    def test_add_contact_to_company_success(self):
        """Test successful contact addition pipeline."""
        company_id = 1
        contact_data = {
            'name': 'John Doe',
            'email': 'john@test.com',
            'role': 'Manager'
        }
        
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        mock_contact.name = 'John Doe'
        
        # Mock successful service calls
        self.mock_validation_service.validate_contact_data.return_value = None
        self.mock_contact_service.add_contact.return_value = mock_contact
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_contact_added_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_contact_addition_updates') as mock_trigger:
            
            result = self.orchestrator.add_contact_to_company(company_id, contact_data, self.mock_session)
            
            assert result == mock_contact
            
            # Verify the pipeline was executed
            mock_process.assert_called_once_with(self.mock_company, mock_contact, contact_data, self.mock_session)
            mock_trigger.assert_called_once_with(self.mock_company, mock_contact, self.mock_session)
    
    def test_update_contact_success(self):
        """Test successful contact update pipeline."""
        company_id = 1
        contact_id = 100
        update_data = {
            'email': 'updated@test.com',
            'phone': '+1234567890'
        }
        
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        mock_contact.name = 'John Doe'
        
        # Mock successful service calls
        self.mock_validation_service.validate_contact_data.return_value = None
        self.mock_contact_service.update_contact.return_value = mock_contact
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_contact_updated_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_contact_update_updates') as mock_trigger:
            
            # Setup contact query mock to return our mock contact
            # We need to patch the _get_contact method to return our mock contact
            with patch.object(self.orchestrator, '_get_contact', return_value=mock_contact):
                result = self.orchestrator.update_contact(company_id, contact_id, update_data, self.mock_session)
                
                assert result == mock_contact
                
                # Verify the pipeline was executed
                mock_process.assert_called_once_with(self.mock_company, mock_contact, update_data, self.mock_session)
                mock_trigger.assert_called_once_with(self.mock_company, mock_contact, self.mock_session)
    
    def test_update_company_portfolio_success(self):
        """Test successful portfolio update pipeline."""
        company_id = 1
        portfolio_data = {
            'portfolio_value': 1000000.0,
            'fund_count': 5
        }
        
        # Mock successful service calls
        self.mock_validation_service.validate_portfolio_data.return_value = None
        self.mock_portfolio_service.update_portfolio.return_value = self.mock_company
        
        # Mock the private methods
        with patch.object(self.orchestrator, '_process_portfolio_updated_event') as mock_process, \
             patch.object(self.orchestrator, '_trigger_portfolio_update_updates') as mock_trigger:
            
            result = self.orchestrator.update_company_portfolio(company_id, portfolio_data, self.mock_session)
            
            assert result == self.mock_company
            
            # Verify the pipeline was executed
            mock_process.assert_called_once_with(self.mock_company, portfolio_data, self.mock_session)
            mock_trigger.assert_called_once_with(self.mock_company, portfolio_data, self.mock_session)
    
    def test_process_company_created_event(self):
        """Test company created event processing."""
        event_data = {
            'company_name': 'Test Company',
            'event_date': '2024-01-15'
        }
        
        # Mock the registry and handler
        mock_handler = Mock()
        mock_handler.handle.return_value = self.mock_company
        
        with patch.object(self.orchestrator.registry, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value = mock_handler
            
            self.orchestrator._process_company_created_event(self.mock_company, event_data, self.mock_session)
            
            # Verify handler was retrieved and called
            mock_get_handler.assert_called_once()
            # Note: The actual event data will include timestamps and metadata, so we check that handle was called
            mock_handler.handle.assert_called_once()
    
    def test_process_contact_added_event(self):
        """Test contact added event processing."""
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        mock_contact.name = 'John Doe'
        mock_contact.title = 'Manager'
        
        event_data = {
            'contact_id': 100,
            'contact_name': 'John Doe',
            'contact_role': 'Manager',
            'event_date': '2024-01-15'
        }
        
        # Mock the registry and handler
        mock_handler = Mock()
        mock_handler.handle.return_value = self.mock_company
        
        with patch.object(self.orchestrator.registry, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value = mock_handler
            
            self.orchestrator._process_contact_added_event(self.mock_company, mock_contact, event_data, self.mock_session)
            
            # Verify handler was retrieved and called
            mock_get_handler.assert_called_once()
            # Note: The actual event data will include timestamps and metadata, so we check that handle was called
            mock_handler.handle.assert_called_once()
    
    def test_process_portfolio_updated_event(self):
        """Test portfolio updated event processing."""
        event_data = {
            'portfolio_value': 1000000.0,
            'fund_count': 5,
            'event_date': '2024-01-15'
        }
        
        # Mock the registry and handler
        mock_handler = Mock()
        mock_handler.handle.return_value = self.mock_company
        
        with patch.object(self.orchestrator.registry, 'get_handler') as mock_get_handler:
            mock_get_handler.return_value = mock_handler
            
            self.orchestrator._process_portfolio_updated_event(self.mock_company, event_data, self.mock_session)
            
            # Verify handler was retrieved and called
            mock_get_handler.assert_called_once()
            # Note: The actual event data will include timestamps and metadata, so we check that handle was called
            mock_handler.handle.assert_called_once()
    
    def test_trigger_company_creation_updates(self):
        """Test triggering company creation updates."""
        self.orchestrator._trigger_company_creation_updates(self.mock_company, self.mock_session)
        
        # Verify portfolio and summary services were called
        self.mock_portfolio_service.recalculate_portfolio_summary.assert_called_once_with(1, self.mock_session)
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_trigger_contact_addition_updates(self):
        """Test triggering contact addition updates."""
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        
        self.orchestrator._trigger_contact_addition_updates(self.mock_company, mock_contact, self.mock_session)
        
        # Verify contact and summary services were called
        self.mock_contact_service.update_contact_count.assert_called_once_with(1, self.mock_session)
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_trigger_portfolio_update_updates(self):
        """Test triggering portfolio update updates."""
        portfolio_data = {'portfolio_value': 1000000.0}
        
        self.orchestrator._trigger_portfolio_update_updates(self.mock_company, portfolio_data, self.mock_session)
        
        # Verify portfolio and summary services were called
        self.mock_portfolio_service.recalculate_portfolio_summary.assert_called_once_with(1, self.mock_session)
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_trigger_company_update_updates(self):
        """Test triggering company update updates."""
        self.orchestrator._trigger_company_update_updates(self.mock_company, self.mock_session)
        
        # Verify summary service was called
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_trigger_company_deletion_updates(self):
        """Test triggering company deletion updates."""
        company_id = 1
        
        self.orchestrator._trigger_company_deletion_updates(company_id, self.mock_session)
        
        # Verify portfolio cleanup was called
        self.mock_portfolio_service.cleanup_deleted_company_portfolio.assert_called_once_with(company_id, self.mock_session)
    
    def test_trigger_contact_update_updates(self):
        """Test triggering contact update updates."""
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        
        self.orchestrator._trigger_contact_update_updates(self.mock_company, mock_contact, self.mock_session)
        
        # Verify contact and summary services were called
        self.mock_contact_service.update_contact_summary.assert_called_once_with(100, self.mock_session)
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_get_company_success(self):
        """Test successful company retrieval."""
        company = self.orchestrator._get_company(1, self.mock_session)
        
        assert company == self.mock_company
        self.mock_session.query.assert_called_once()
    
    def test_get_company_not_found(self):
        """Test company retrieval when company doesn't exist."""
        self.mock_filter.first.return_value = None
        
        with pytest.raises(ValueError, match="Company with ID 999 not found"):
            self.orchestrator._get_company(999, self.mock_session)
    
    def test_get_contact_success(self):
        """Test successful contact retrieval."""
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        
        # Setup contact query mock
        self.mock_session.query.return_value = self.mock_query
        self.mock_query.filter.return_value = self.mock_filter
        self.mock_filter.first.return_value = mock_contact
        
        contact = self.orchestrator._get_contact(100, self.mock_session)
        
        assert contact == mock_contact
        self.mock_session.query.assert_called()
    
    def test_get_contact_not_found(self):
        """Test contact retrieval when contact doesn't exist."""
        # Setup contact query mock to return None
        self.mock_session.query.return_value = self.mock_query
        self.mock_query.filter.return_value = self.mock_filter
        self.mock_filter.first.return_value = None
        
        with pytest.raises(ValueError, match="Contact with ID 999 not found"):
            self.orchestrator._get_contact(999, self.mock_session)
