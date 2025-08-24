"""
Test Investment Company Event Handlers.

This module tests each individual event handler to ensure they work
correctly and maintain the expected contracts.

Each handler is tested for:
- Event validation logic
- Event processing and state updates
- Error handling and edge cases
- Business rule enforcement
- Domain event publishing
- Service integration

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Handlers should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from src.investment_company.events.handlers import (
    CompanyCreatedHandler,
    CompanyUpdatedHandler,
    CompanyDeletedHandler,
    ContactAddedHandler,
    ContactUpdatedHandler,
    PortfolioUpdatedHandler
)
from src.investment_company.enums import CompanyType, CompanyStatus, CompanyDomainEventType
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.events.domain import (
    CompanyCreatedEvent,
    CompanyUpdatedEvent,
    CompanyDeletedEvent,
    ContactAddedEvent,
    ContactUpdatedEvent,
    PortfolioUpdatedEvent
)


class TestCompanyCreatedHandler:
    """Test the company created handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        self.mock_company.company_type = CompanyType.PRIVATE_EQUITY
        self.mock_company.status = CompanyStatus.ACTIVE
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        self.handler = CompanyCreatedHandler(self.mock_session, self.mock_company)
        
        # Patch the services to use our mocks
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'company_name': 'Test Company',
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_missing_company_name(self):
        """Test validation rejects missing company name."""
        event_data = {
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['company_name'\\]"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_event_date(self):
        """Test validation rejects missing event date."""
        event_data = {
            'company_name': 'Test Company'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['event_date'\\]"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_empty_company_name(self):
        """Test validation rejects empty company name."""
        event_data = {
            'company_name': '   ',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Company name cannot be empty"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_field_types(self):
        """Test validation rejects invalid field types."""
        event_data = {
            'company_name': 123,  # Should be string
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Field 'company_name' must be of type str"):
            self.handler.validate_event(event_data)
    
    def test_parse_event_date_success(self):
        """Test successful date parsing."""
        date_str = '2024-01-15'
        result = self.handler._parse_event_date(date_str)
        
        assert result == date(2024, 1, 15)
    
    def test_parse_event_date_invalid_format(self):
        """Test date parsing with invalid format."""
        date_str = 'invalid-date'
        
        with pytest.raises(ValueError, match="Invalid date format: invalid-date. Expected ISO format"):
            self.handler._parse_event_date(date_str)
    
    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'company_name': 'Test Company',
            'event_date': '2024-01-15',
            'company_type': 'Private Equity'
        }
        
        # Mock the domain event creation
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result == self.mock_company
            mock_publish.assert_called_once()
            
            # Verify the published event
            published_event = mock_publish.call_args[0][0]
            assert isinstance(published_event, CompanyCreatedEvent)
            assert published_event.company_id == 1
            assert published_event.company_name == 'Test Company'
    
    def test_handle_validation_failure(self):
        """Test event handling fails on validation error."""
        event_data = {
            'event_date': '2024-01-15'  # Missing company_name
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['company_name'\\]"):
            self.handler.handle(event_data)
    
    def test_trigger_company_calculations_success(self):
        """Test successful triggering of company calculations."""
        # Mock successful service calls
        self.mock_portfolio_service.update_portfolio_summary.return_value = None
        self.mock_summary_service.update_company_summary.return_value = None
        
        self.handler._trigger_company_calculations()
        
        # Verify services were called
        self.mock_portfolio_service.update_portfolio_summary.assert_called_once_with(self.mock_company, self.mock_session)
        self.mock_summary_service.update_company_summary.assert_called_once_with(self.mock_company, self.mock_session)
    
    def test_trigger_company_calculations_failure(self):
        """Test that calculation failures don't break the event."""
        # Mock service failures
        self.mock_portfolio_service.update_portfolio_summary.side_effect = Exception("Service error")
        self.mock_summary_service.update_company_summary.side_effect = Exception("Service error")
        
        # Should not raise an exception
        self.handler._trigger_company_calculations()
        
        # Verify services were still called (even though they failed)
        # Use call_count instead of assert_called_once_with for methods that raise exceptions
        assert self.mock_portfolio_service.update_portfolio_summary.call_count == 1
        assert self.mock_summary_service.update_company_summary.call_count == 1


class TestCompanyUpdatedHandler:
    """Test the company updated handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        self.handler = CompanyUpdatedHandler(self.mock_session, self.mock_company)
        
        # Patch the services
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'company_id': 1,
            'update_fields': {'name': 'Updated Name', 'description': 'Updated Description'},
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)

    def test_validate_event_missing_company_id(self):
        """Test validation rejects missing company ID."""
        event_data = {
            'update_fields': ['name', 'description'],
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['company_id'\\]"):
            self.handler.validate_event(event_data)

    def test_validate_event_missing_update_fields(self):
        """Test validation rejects missing update fields."""
        event_data = {
            'company_id': 1,
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Event data must contain non-empty 'update_fields'"):
            self.handler.validate_event(event_data)

    def test_validate_event_empty_update_fields(self):
        """Test validation rejects empty update fields list."""
        event_data = {
            'company_id': 1,
            'update_fields': {},
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Event data must contain non-empty 'update_fields'"):
            self.handler.validate_event(event_data)

    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'company_id': 1,
            'update_fields': {'name': 'Updated Name', 'description': 'Updated Description'},
            'event_date': '2024-01-15'
        }
        
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result is not None
            assert result['success'] is True
            assert result['company_id'] == 1
            assert 'name' in result['updated_fields']
            assert 'description' in result['updated_fields']
            mock_publish.assert_called_once()


class TestCompanyDeletedHandler:
    """Test the company deleted handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        # Mock funds as empty list so deletion validation passes
        self.mock_company.funds = []
        self.mock_company.contacts = []
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        self.handler = CompanyDeletedHandler(self.mock_session, self.mock_company)
        
        # Patch the services
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'company_id': 1,
            'deletion_reason': 'Company closure',
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)

    def test_validate_event_missing_company_id(self):
        """Test validation rejects missing company ID."""
        event_data = {
            'deletion_reason': 'Company closure',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['company_id'\\]"):
            self.handler.validate_event(event_data)

    def test_validate_event_missing_deletion_reason(self):
        """Test validation accepts missing deletion reason (optional field)."""
        event_data = {
            'company_id': 1,
            'event_date': '2024-01-15'
        }
        
        # Should not raise since deletion_reason is optional
        self.handler.validate_event(event_data)

    def test_validate_event_empty_deletion_reason(self):
        """Test validation accepts empty deletion reason (optional field)."""
        event_data = {
            'company_id': 1,
            'deletion_reason': '   ',
            'event_date': '2024-01-15'
        }
        
        # Should not raise since deletion_reason is optional
        self.handler.validate_event(event_data)

    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'company_id': 1,
            'deletion_reason': 'Company closure',
            'event_date': '2024-01-15'
        }
        
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result is not None
            assert result['success'] is True
            assert result['company_id'] == 1
            assert result['deletion_reason'] == 'Company closure'
            mock_publish.assert_called_once()


class TestContactAddedHandler:
    """Test the contact added handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        
        # Mock the contact with correct company ID
        self.mock_contact = Mock()
        self.mock_contact.id = 100
        self.mock_contact.name = 'John Doe'
        self.mock_contact.title = 'Manager'
        self.mock_contact.investment_company_id = 1  # Same as company ID
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        # Mock the session query chain for _get_contact
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        mock_first.return_value = self.mock_contact
        mock_filter.first = mock_first
        mock_query.filter.return_value = mock_filter
        self.mock_session.query.return_value = mock_query
        
        self.handler = ContactAddedHandler(self.mock_session, self.mock_company)
        
        # Patch the services
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'contact_id': 100,
            'contact_name': 'John Doe',
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)

    def test_validate_event_missing_contact_id(self):
        """Test validation rejects missing contact ID."""
        event_data = {
            'contact_name': 'John Doe',
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['contact_id'\\]"):
            self.handler.validate_event(event_data)

    def test_validate_event_missing_contact_name(self):
        """Test validation rejects missing contact name."""
        event_data = {
            'contact_id': 100,
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['contact_name'\\]"):
            self.handler.validate_event(event_data)

    def test_validate_event_missing_contact_title(self):
        """Test validation rejects missing contact title."""
        event_data = {
            'contact_id': 100,
            'contact_name': 'John Doe',
            'event_date': '2024-01-15'
        }
        
        # contact_title is not required, so this should not raise
        self.handler.validate_event(event_data)

    def test_validate_event_empty_contact_name(self):
        """Test validation rejects empty contact name."""
        event_data = {
            'contact_id': 100,
            'contact_name': '   ',
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Contact name cannot be empty"):
            self.handler.validate_event(event_data)

    def test_validate_event_invalid_contact_id(self):
        """Test validation rejects invalid contact ID."""
        event_data = {
            'contact_id': 0,
            'contact_name': 'John Doe',
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Contact ID must be positive"):
            self.handler.validate_event(event_data)

    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'contact_id': 100,
            'contact_name': 'John Doe',
            'contact_title': 'Manager',
            'event_date': '2024-01-15'
        }
        
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result is not None
            assert result.id == 100
            assert result.name == 'John Doe'
            assert result.title == 'Manager'
            mock_publish.assert_called_once()


class TestContactUpdatedHandler:
    """Test the contact updated handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        
        # Mock the contact with correct company ID
        self.mock_contact = Mock()
        self.mock_contact.id = 100
        self.mock_contact.name = 'John Doe'
        self.mock_contact.title = 'Manager'
        self.mock_contact.investment_company_id = 1  # Same as company ID
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        self.handler = ContactUpdatedHandler(self.mock_session, self.mock_company, self.mock_contact)
        
        # Patch the services
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'contact_id': 100,
            'update_fields': {'email': 'new@test.com', 'phone': '123-456-7890'},
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_missing_contact_id(self):
        """Test validation rejects missing contact ID."""
        event_data = {
            'update_fields': {'email': 'new@test.com', 'phone': '123-456-7890'},
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Missing required fields: \\['contact_id'\\]"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_update_fields(self):
        """Test validation rejects missing update fields."""
        event_data = {
            'contact_id': 100,
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Event data must contain non-empty 'update_fields'"):
            self.handler.validate_event(event_data)

    def test_validate_event_empty_update_fields(self):
        """Test validation rejects empty update fields list."""
        event_data = {
            'contact_id': 100,
            'update_fields': {},
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Event data must contain non-empty 'update_fields'"):
            self.handler.validate_event(event_data)
    
    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'contact_id': 100,
            'update_fields': {'email': 'new@test.com', 'phone': '123-456-7890'},
            'event_date': '2024-01-15'
        }
        
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result is not None
            assert result['success'] is True
            assert result['contact_id'] == 100
            assert 'email' in result['updated_fields']
            assert 'phone' in result['updated_fields']
            mock_publish.assert_called_once()


class TestPortfolioUpdatedHandler:
    """Test the portfolio updated handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_company = Mock()
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        
        # Mock the services
        self.mock_portfolio_service = Mock()
        self.mock_summary_service = Mock()
        self.mock_contact_service = Mock()
        self.mock_validation_service = Mock()
        
        self.handler = PortfolioUpdatedHandler(self.mock_session, self.mock_company)
        
        # Patch the services
        self.handler.portfolio_service = self.mock_portfolio_service
        self.handler.summary_service = self.mock_summary_service
        self.handler.contact_service = self.mock_contact_service
        self.handler.validation_service = self.mock_validation_service
    
    def test_validate_event_success(self):
        """Test successful event validation."""
        event_data = {
            'fund_id': 200,
            'operation': 'added',
            'event_date': '2024-01-15'
        }
        
        # Should not raise
        self.handler.validate_event(event_data)

    def test_validate_event_missing_fund_id(self):
        """Test validation accepts missing fund ID (optional field)."""
        event_data = {
            'operation': 'added',
            'event_date': '2024-01-15'
        }
        
        # Should not raise since fund_id is optional
        self.handler.validate_event(event_data)

    def test_validate_event_missing_operation(self):
        """Test validation accepts missing operation (optional field)."""
        event_data = {
            'fund_id': 200,
            'event_date': '2024-01-15'
        }
        
        # Should not raise since operation is optional
        self.handler.validate_event(event_data)

    def test_validate_event_invalid_fund_id_type(self):
        """Test validation rejects invalid fund ID type."""
        event_data = {
            'fund_id': 'invalid',
            'operation': 'added',
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Field 'fund_id' must be of type"):
            self.handler.validate_event(event_data)

    def test_validate_event_invalid_operation_type(self):
        """Test validation rejects invalid operation type."""
        event_data = {
            'fund_id': 200,
            'operation': 123,
            'event_date': '2024-01-15'
        }
        
        with pytest.raises(ValueError, match="Field 'operation' must be of type"):
            self.handler.validate_event(event_data)

    def test_handle_success(self):
        """Test successful event handling."""
        event_data = {
            'fund_id': 200,
            'operation': 'added',
            'event_date': '2024-01-15'
        }
        
        with patch.object(self.handler, '_publish_domain_event') as mock_publish:
            result = self.handler.handle(event_data)
            
            assert result == self.mock_company
            mock_publish.assert_called_once()
            
            # Verify the published event
            published_event = mock_publish.call_args[0][0]
            assert isinstance(published_event, PortfolioUpdatedEvent)
            assert published_event.company_id == 1
            assert published_event.fund_id == 200
            assert published_event.operation == 'added'


class TestEventHandlersIntegration:
    """Test integration between different event handlers."""
    
    def test_all_handlers_implement_required_methods(self):
        """Test that all handlers implement the required abstract methods."""
        mock_session = Mock()
        mock_company = Mock()
        mock_company.id = 1
        
        # Test handlers that don't require additional parameters
        handlers = [
            CompanyCreatedHandler(mock_session, mock_company),
            CompanyUpdatedHandler(mock_session, mock_company),
            CompanyDeletedHandler(mock_session, mock_company),
            ContactAddedHandler(mock_session, mock_company),
            PortfolioUpdatedHandler(mock_session, mock_company)
        ]
        
        for handler in handlers:
            # All handlers should have the required methods
            assert hasattr(handler, 'handle')
            assert hasattr(handler, 'validate_event')
            
            # All handlers should be callable
            assert callable(handler.handle)
            assert callable(handler.validate_event)
        
        # Test ContactUpdatedHandler separately as it requires a contact parameter
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        contact_handler = ContactUpdatedHandler(mock_session, mock_company, mock_contact)
        assert hasattr(contact_handler, 'handle')
        assert hasattr(contact_handler, 'validate_event')
        assert callable(contact_handler.handle)
        assert callable(contact_handler.validate_event)
    
    def test_handler_validation_consistency(self):
        """Test that all handlers follow consistent validation patterns."""
        mock_session = Mock()
        mock_company = Mock()
        mock_company.id = 1
        
        # Test handlers that don't require additional parameters
        handlers = [
            CompanyCreatedHandler(mock_session, mock_company),
            CompanyUpdatedHandler(mock_session, mock_company),
            CompanyDeletedHandler(mock_session, mock_company),
            ContactAddedHandler(mock_session, mock_company),
            PortfolioUpdatedHandler(mock_session, mock_company)
        ]
        
        for handler in handlers:
            # All handlers should validate required fields
            with pytest.raises(ValueError):
                handler.validate_event({})
        
        # Test ContactUpdatedHandler separately
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        contact_handler = ContactUpdatedHandler(mock_session, mock_company, mock_contact)
        with pytest.raises(ValueError):
            contact_handler.validate_event({})
    
    def test_handler_event_publishing_consistency(self):
        """Test that all handlers publish domain events consistently."""
        mock_session = Mock()
        mock_company = Mock()
        mock_company.id = 1
        
        # Test handlers that don't require additional parameters
        handlers = [
            CompanyCreatedHandler(mock_session, mock_company),
            CompanyUpdatedHandler(mock_session, mock_company),
            CompanyDeletedHandler(mock_session, mock_company),
            ContactAddedHandler(mock_session, mock_company),
            PortfolioUpdatedHandler(mock_session, mock_company)
        ]
        
        for handler in handlers:
            # All handlers should have the _publish_domain_event method
            assert hasattr(handler, '_publish_domain_event')
            assert callable(handler._publish_domain_event)
        
        # Test ContactUpdatedHandler separately
        mock_contact = Mock(spec=Contact)
        mock_contact.id = 100
        contact_handler = ContactUpdatedHandler(mock_session, mock_company, mock_contact)
        assert hasattr(contact_handler, '_publish_domain_event')
        assert callable(contact_handler._publish_domain_event)
