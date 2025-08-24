"""
Test Investment Company Event Handler Registry.

This module tests the CompanyEventHandlerRegistry class to ensure it properly
manages handler registration, routing, and lifecycle management.

Key testing areas:
- Handler registration and discovery
- Handler routing by event type
- Handler validation and error handling
- Handler lifecycle management
- Dynamic handler registration
- Registry state consistency

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Registry should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from src.investment_company.events.registry import CompanyEventHandlerRegistry
from src.investment_company.events.base_handler import BaseCompanyEventHandler
from src.investment_company.events.handlers import (
    CompanyCreatedHandler,
    CompanyUpdatedHandler,
    CompanyDeletedHandler,
    ContactAddedHandler,
    ContactUpdatedHandler,
    PortfolioUpdatedHandler
)
from src.investment_company.enums import CompanyDomainEventType, CompanyOperationType
from src.investment_company.models import InvestmentCompany, Contact


class TestCompanyEventHandlerRegistry:
    """Test the CompanyEventHandlerRegistry class functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_company = Mock(spec=InvestmentCompany)
        self.mock_company.id = 1
        self.mock_company.name = "Test Company"
        
        # Create registry instance
        self.registry = CompanyEventHandlerRegistry()
    
    def test_registry_initialization(self):
        """Test that registry initializes with required dependencies."""
        registry = CompanyEventHandlerRegistry()
        
        assert registry.logger is not None
        assert registry._handlers is not None
        assert registry._operation_handlers is not None
        assert isinstance(registry._handlers, dict)
        assert isinstance(registry._operation_handlers, dict)
    
    def test_default_handler_registration(self):
        """Test that default handlers are automatically registered."""
        # Verify that default handlers are registered
        assert CompanyDomainEventType.COMPANY_CREATED in self.registry._handlers
        assert CompanyDomainEventType.COMPANY_UPDATED in self.registry._handlers
        assert CompanyDomainEventType.COMPANY_DELETED in self.registry._handlers
        assert CompanyDomainEventType.CONTACT_ADDED in self.registry._handlers
        assert CompanyDomainEventType.CONTACT_UPDATED in self.registry._handlers
        assert CompanyDomainEventType.PORTFOLIO_UPDATED in self.registry._handlers
        
        # Verify handler classes are correct
        assert self.registry._handlers[CompanyDomainEventType.COMPANY_CREATED] == CompanyCreatedHandler
        assert self.registry._handlers[CompanyDomainEventType.COMPANY_UPDATED] == CompanyUpdatedHandler
        assert self.registry._handlers[CompanyDomainEventType.COMPANY_DELETED] == CompanyDeletedHandler
        assert self.registry._handlers[CompanyDomainEventType.CONTACT_ADDED] == ContactAddedHandler
        assert self.registry._handlers[CompanyDomainEventType.CONTACT_UPDATED] == ContactUpdatedHandler
        assert self.registry._handlers[CompanyDomainEventType.PORTFOLIO_UPDATED] == PortfolioUpdatedHandler
    
    def test_register_handler_success(self):
        """Test successful handler registration."""
        # Create a custom test handler
        class CustomTestHandler(BaseCompanyEventHandler):
            def handle(self, event_data):
                return "custom_result"
            
            def validate_event(self, event_data):
                pass
        
        # Register the custom handler
        self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, CustomTestHandler)
        
        # Verify handler was registered
        assert self.registry._handlers[CompanyDomainEventType.COMPANY_CREATED] == CustomTestHandler
        
        # Verify handler can be retrieved
        handler = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        assert isinstance(handler, CustomTestHandler)
    
    def test_register_handler_invalid_class(self):
        """Test handler registration fails with invalid handler class."""
        class InvalidHandler:
            """Invalid handler that doesn't inherit from BaseCompanyEventHandler."""
            pass
        
        with pytest.raises(ValueError, match="Handler class InvalidHandler must inherit from BaseCompanyEventHandler"):
            self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, InvalidHandler)
    
    def test_get_handler_success(self):
        """Test successful handler retrieval by event type."""
        handler = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        
        assert handler is not None
        assert isinstance(handler, CompanyCreatedHandler)
        assert handler.session == self.mock_session
        assert handler.company == self.mock_company
    
    def test_get_handler_not_registered(self):
        """Test handler retrieval fails when no handler is registered."""
        # Create a new event type that's not registered
        unregistered_event_type = CompanyDomainEventType.COMPANY_CREATED  # Use existing type for testing
        
        # Temporarily remove the handler
        original_handler = self.registry._handlers[unregistered_event_type]
        del self.registry._handlers[unregistered_event_type]
        
        try:
            with pytest.raises(ValueError, match=f"No handler registered for event type: {unregistered_event_type}"):
                self.registry.get_handler(unregistered_event_type, self.mock_session, self.mock_company)
        finally:
            # Restore the handler
            self.registry._handlers[unregistered_event_type] = original_handler
    
    def test_handler_instance_creation(self):
        """Test that handler instances are properly created with dependencies."""
        handler = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        
        # Verify handler has correct dependencies
        assert handler.session == self.mock_session
        assert handler.company == self.mock_company
        
        # Verify handler has required services
        assert hasattr(handler, 'portfolio_service')
        assert hasattr(handler, 'summary_service')
        assert hasattr(handler, 'contact_service')
        assert hasattr(handler, 'validation_service')
        assert hasattr(handler, 'logger')
    
    def test_handler_registry_consistency(self):
        """Test that handler registry maintains consistency across operations."""
        # Verify all registered event types have handlers
        for event_type in CompanyDomainEventType:
            if event_type in self.registry._handlers:
                handler_class = self.registry._handlers[event_type]
                assert issubclass(handler_class, BaseCompanyEventHandler)
    
    def test_handler_lifecycle_management(self):
        """Test that handlers are properly managed throughout their lifecycle."""
        # Get a handler instance
        handler1 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        
        # Get another handler instance (should be a new instance)
        handler2 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        
        # Verify they are different instances
        assert handler1 is not handler2
        
        # Verify both have correct dependencies
        assert handler1.session == self.mock_session
        assert handler1.company == self.mock_company
        assert handler2.session == self.mock_session
        assert handler2.company == self.mock_company
    
    def test_registry_error_handling(self):
        """Test that registry properly handles errors during handler operations."""
        # Test with invalid handler class
        class InvalidHandler:
            pass
        
        with pytest.raises(ValueError):
            self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, InvalidHandler)
        
        # Test with unregistered event type - use a type that doesn't exist
        # Create a mock event type that's not registered
        class MockEventType:
            def __init__(self, value):
                self.value = value
        
        mock_event_type = MockEventType("UNREGISTERED_EVENT")
        
        with pytest.raises(ValueError):
            self.registry.get_handler(mock_event_type, self.mock_session, self.mock_company)
    
    def test_registry_handler_validation(self):
        """Test that registry validates handlers before registration."""
        # Test with None handler
        with pytest.raises(TypeError, match="issubclass\\(\\) arg 1 must be a class"):
            self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, None)
        
        # Test with string instead of class
        with pytest.raises(TypeError, match="issubclass\\(\\) arg 1 must be a class"):
            self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, "not_a_class")
    
    def test_registry_handler_override(self):
        """Test that handlers can be overridden by re-registration."""
        # Create a custom test handler
        class OverrideTestHandler(BaseCompanyEventHandler):
            def handle(self, event_data):
                return "override_result"
            
            def validate_event(self, event_data):
                pass
        
        # Register the override handler
        self.registry.register_handler(CompanyDomainEventType.COMPANY_CREATED, OverrideTestHandler)
        
        # Verify handler was overridden
        assert self.registry._handlers[CompanyDomainEventType.COMPANY_CREATED] == OverrideTestHandler
        
        # Verify new handler is used
        handler = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        assert isinstance(handler, OverrideTestHandler)
    
    def test_registry_handler_retrieval_with_different_sessions(self):
        """Test that handlers work with different session instances."""
        mock_session1 = Mock()
        mock_session2 = Mock()
        mock_company1 = Mock(spec=InvestmentCompany)
        mock_company1.id = 1
        mock_company2 = Mock(spec=InvestmentCompany)
        mock_company2.id = 2
        
        # Get handlers with different sessions and companies
        handler1 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, mock_session1, mock_company1)
        handler2 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, mock_session2, mock_company2)
        
        # Verify they are different instances
        assert handler1 is not handler2
        
        # Verify they have correct dependencies
        assert handler1.session == mock_session1
        assert handler1.company == mock_company1
        assert handler2.session == mock_session2
        assert handler2.company == mock_company2
    
    def test_registry_handler_retrieval_with_different_companies(self):
        """Test that handlers work with different company instances."""
        mock_company1 = Mock(spec=InvestmentCompany)
        mock_company1.id = 1
        mock_company1.name = "Company 1"
        
        mock_company2 = Mock(spec=InvestmentCompany)
        mock_company2.id = 2
        mock_company2.name = "Company 2"
        
        # Get handlers with different companies
        handler1 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, mock_company1)
        handler2 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, mock_company2)
        
        # Verify they are different instances
        assert handler1 is not handler2
        
        # Verify they have correct company references
        assert handler1.company == mock_company1
        assert handler2.company == mock_company2
        assert handler1.company.id == 1
        assert handler2.company.id == 2
    
    def test_registry_handler_methods_availability(self):
        """Test that all registered handlers have required methods."""
        # Test all event type handlers
        for event_type in CompanyDomainEventType:
            if event_type in self.registry._handlers:
                # Provide additional context for handlers that need it
                context_kwargs = {}
                
                # ContactUpdatedHandler needs a contact
                if event_type == CompanyDomainEventType.CONTACT_UPDATED:
                    mock_contact = Mock(spec=Contact)
                    mock_contact.id = 1
                    mock_contact.investment_company_id = self.mock_company.id
                    context_kwargs['contact'] = mock_contact
                
                handler = self.registry.get_handler(event_type, self.mock_session, self.mock_company, **context_kwargs)
                
                # Verify required methods exist
                assert hasattr(handler, 'handle')
                assert hasattr(handler, 'validate_event')
                
                # Verify methods are callable
                assert callable(handler.handle)
                assert callable(handler.validate_event)
    
    def test_registry_handler_inheritance_validation(self):
        """Test that all registered handlers properly inherit from BaseCompanyEventHandler."""
        # Test all event type handlers
        for event_type in CompanyDomainEventType:
            if event_type in self.registry._handlers:
                handler_class = self.registry._handlers[event_type]
                assert issubclass(handler_class, BaseCompanyEventHandler)
    
    def test_registry_handler_retrieval_performance(self):
        """Test that handler retrieval is performant and doesn't create unnecessary objects."""
        # Get the same handler multiple times
        handler1 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        handler2 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        handler3 = self.registry.get_handler(CompanyDomainEventType.COMPANY_CREATED, self.mock_session, self.mock_company)
        
        # Each call should create a new instance (this is the expected behavior)
        assert handler1 is not handler2
        assert handler2 is not handler3
        assert handler1 is not handler3
        
        # But all should be of the same class
        assert type(handler1) == type(handler2) == type(handler3)
        assert isinstance(handler1, CompanyCreatedHandler)
        assert isinstance(handler2, CompanyCreatedHandler)
        assert isinstance(handler3, CompanyCreatedHandler)
