"""
Test Base Company Event Handler.

This module tests the BaseCompanyEventHandler base class functionality,
focusing on common methods and shared logic that all handlers inherit.

Key testing areas:
- Common validation methods
- Event creation and management
- Domain event publishing
- Company validation and error handling
- Date parsing and validation
- Service initialization

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Base handler should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.enums import CompanyType, CompanyStatus, CompanyDomainEventType
from src.investment_company.models import InvestmentCompany, Contact


class ConcreteTestHandler(BaseCompanyEventHandler):
    """Concrete implementation of BaseCompanyEventHandler for testing."""
    
    def handle(self, event_data):
        """Implement abstract method for testing."""
        self.validate_event(event_data)
        return self._create_test_event(**event_data)
    
    def validate_event(self, event_data):
        """Implement abstract method for testing."""
        if 'company_name' not in event_data:
            raise ValueError("Company name is required")
    
    def _create_test_event(self, **kwargs):
        """Create a test event for testing purposes."""
        return {
            'company_id': self.company.id,
            'event_type': 'TEST_EVENT',
            'data': kwargs
        }


class TestBaseCompanyEventHandler:
    """Test the BaseCompanyEventHandler base class functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock(spec=InvestmentCompany)
        self.mock_company.id = 1
        self.mock_company.company_type = CompanyType.PRIVATE_EQUITY
        self.mock_company.status = CompanyStatus.ACTIVE
        self.mock_company.name = "Test Company"
        
        # Create concrete handler instance for testing
        self.handler = ConcreteTestHandler(self.mock_session, self.mock_company)
        
        # Mock the logger methods
        self.handler.logger.info = Mock()
        self.handler.logger.error = Mock()
    
    def test_handler_initialization(self):
        """Test that handler initializes with correct dependencies."""
        assert self.handler.session == self.mock_session
        assert self.handler.company == self.mock_company
        assert self.handler.portfolio_service is not None
        assert self.handler.summary_service is not None
        assert self.handler.contact_service is not None
        assert self.handler.validation_service is not None
        assert self.handler.logger is not None
    
    def test_get_company_success(self):
        """Test successful company retrieval by ID."""
        mock_company = Mock(spec=InvestmentCompany)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_company
        
        result = self.handler._get_company(1)
        
        assert result == mock_company
        self.mock_session.query.assert_called_once()
    
    def test_get_company_not_found(self):
        """Test company retrieval when company doesn't exist."""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Company with ID 1 not found"):
            self.handler._get_company(1)
    
    def test_get_contact_success(self):
        """Test successful contact retrieval by ID."""
        mock_contact = Mock(spec=Contact)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_contact
        
        result = self.handler._get_contact(1)
        
        assert result == mock_contact
        self.mock_session.query.assert_called_once()
    
    def test_get_contact_not_found(self):
        """Test contact retrieval when contact doesn't exist."""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Contact with ID 1 not found"):
            self.handler._get_contact(1)
    
    def test_publish_domain_event(self):
        """Test domain event publishing (currently just logging)."""
        mock_event = Mock()
        mock_event.__repr__ = Mock(return_value="TestEvent")
        
        # Should not raise an exception
        self.handler._publish_domain_event(mock_event)
        
        # Verify logging occurred
        assert self.handler.logger.info.called
    
    def test_log_event_processing(self):
        """Test event processing logging."""
        event_data = {'company_name': 'Test Company', 'event_date': '2024-01-15'}
        
        self.handler._log_event_processing("CompanyCreated", event_data)
        
        # Verify logging occurred
        assert self.handler.logger.info.called
    
    def test_handle_error(self):
        """Test error handling during event processing."""
        event_data = {'company_name': 'Test Company'}
        test_error = ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            self.handler._handle_error(test_error, event_data)
        
        # Verify error logging occurred
        assert self.handler.logger.error.called
    
    def test_validate_company_exists_success(self):
        """Test successful company existence validation."""
        # Should not raise an exception
        self.handler._validate_company_exists()
        
        # Verify session refresh was called
        self.mock_session.refresh.assert_called_once_with(self.mock_company)
    
    def test_validate_company_exists_no_company(self):
        """Test company existence validation when company is None."""
        self.handler.company = None
        
        with pytest.raises(ValueError, match="Company instance is invalid or has no ID"):
            self.handler._validate_company_exists()
    
    def test_validate_company_exists_no_id(self):
        """Test company existence validation when company has no ID."""
        self.handler.company.id = None
        
        with pytest.raises(ValueError, match="Company instance is invalid or has no ID"):
            self.handler._validate_company_exists()
    
    def test_validate_required_fields_success(self):
        """Test successful required field validation."""
        event_data = {'company_name': 'Test Company', 'event_date': '2024-01-15'}
        required_fields = ['company_name', 'event_date']
        
        # Should not raise an exception
        self.handler._validate_required_fields(event_data, required_fields)
    
    def test_validate_required_fields_missing(self):
        """Test required field validation when fields are missing."""
        event_data = {'company_name': 'Test Company'}
        required_fields = ['company_name', 'event_date']
        
        with pytest.raises(ValueError, match="Missing required fields: \\['event_date'\\]"):
            self.handler._validate_required_fields(event_data, required_fields)
    
    def test_validate_field_types_success(self):
        """Test successful field type validation."""
        event_data = {'company_name': 'Test Company', 'amount': 1000}
        field_types = {'company_name': str, 'amount': int}
        
        # Should not raise an exception
        self.handler._validate_field_types(event_data, field_types)
    
    def test_validate_field_types_incorrect_type(self):
        """Test field type validation when types are incorrect."""
        event_data = {'company_name': 'Test Company', 'amount': 'invalid'}
        field_types = {'company_name': str, 'amount': int}
        
        with pytest.raises(ValueError, match="Field 'amount' must be of type int, got str"):
            self.handler._validate_field_types(event_data, field_types)
    
    def test_validate_field_types_missing_field(self):
        """Test field type validation when field is missing (should pass)."""
        event_data = {'company_name': 'Test Company'}
        field_types = {'company_name': str, 'amount': int}
        
        # Should not raise an exception - missing fields are not validated
        self.handler._validate_field_types(event_data, field_types)
    
    def test_handler_abstract_methods(self):
        """Test that abstract methods are properly defined."""
        # Verify abstract methods exist
        assert hasattr(self.handler, 'handle')
        assert hasattr(self.handler, 'validate_event')
        
        # Verify they are callable
        assert callable(self.handler.handle)
        assert callable(self.handler.validate_event)
    
    def test_handler_service_initialization(self):
        """Test that all required services are properly initialized."""
        # Verify all services are initialized
        assert hasattr(self.handler, 'portfolio_service')
        assert hasattr(self.handler, 'summary_service')
        assert hasattr(self.handler, 'contact_service')
        assert hasattr(self.handler, 'validation_service')
        
        # Verify they are not None
        assert self.handler.portfolio_service is not None
        assert self.handler.summary_service is not None
        assert self.handler.contact_service is not None
        assert self.handler.validation_service is not None
    
    def test_handler_logger_initialization(self):
        """Test that logger is properly initialized."""
        assert hasattr(self.handler, 'logger')
        assert self.handler.logger is not None
        assert self.handler.logger.name == 'src.investment_company.events.base_handler'
    
    def test_concrete_handler_implementation(self):
        """Test that concrete handler properly implements abstract methods."""
        event_data = {'company_name': 'Test Company'}
        
        # Should not raise an exception
        result = self.handler.handle(event_data)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'company_id' in result
        assert 'event_type' in result
        assert 'data' in result
        assert result['company_id'] == 1
        assert result['event_type'] == 'TEST_EVENT'
    
    def test_concrete_handler_validation_failure(self):
        """Test that concrete handler validation properly fails."""
        event_data = {}  # Missing company_name
        
        with pytest.raises(ValueError, match="Company name is required"):
            self.handler.handle(event_data)
