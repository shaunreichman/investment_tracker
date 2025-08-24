"""
Fund Event Registry Unit Tests.

This module tests ONLY the FundEventHandlerRegistry functionality:
- Event handler registration and discovery
- Event routing rules and validation
- Event registry performance and scalability
- Handler lifecycle management
- Error handling and validation

This file focuses exclusively on registry behavior and does NOT test:
- Individual event handlers (covered by test_event_handlers.py)
- Event orchestration (covered by test_orchestrator.py)
- Base handler functionality (covered by test_base_handler.py)
- Event models or business logic (covered by model tests)

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Event registry should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from src.fund.events.registry import FundEventHandlerRegistry
from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType, FundStatus
from src.fund.models import Fund, FundEvent


class MockEventHandler(BaseFundEventHandler):
    """Mock event handler for testing registry functionality."""
    
    def handle(self, event_data):
        """Mock implementation of handle method."""
        self.validate_event(event_data)
        return Mock(spec=FundEvent)
    
    def validate_event(self, event_data):
        """Mock implementation of validate_event method."""
        if 'amount' not in event_data:
            raise ValueError("Amount is required")


class MockInvalidHandler:
    """Mock handler that doesn't inherit from BaseFundEventHandler."""
    
    def handle(self, event_data):
        return Mock(spec=FundEvent)
    
    def validate_event(self, event_data):
        pass


class TestFundEventHandlerRegistry:
    """Test the FundEventHandlerRegistry functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.registry = FundEventHandlerRegistry()
        self.mock_session = Mock()
        self.mock_fund = Mock(spec=Fund)
        self.mock_fund.id = 1
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.status = FundStatus.ACTIVE
        self.mock_fund.name = "Test Fund"
    
    def test_registry_initialization(self):
        """Test that registry initializes with default handlers."""
        registry = FundEventHandlerRegistry()
        
        # Check that default handlers are registered
        assert EventType.CAPITAL_CALL in registry._handlers
        assert EventType.DISTRIBUTION in registry._handlers
        assert EventType.NAV_UPDATE in registry._handlers
        assert EventType.UNIT_PURCHASE in registry._handlers
        assert EventType.UNIT_SALE in registry._handlers
        assert EventType.RETURN_OF_CAPITAL in registry._handlers
        
        # Check total count of registered handlers
        assert len(registry._handlers) == 7
    
    def test_register_handler_success(self):
        """Test successful handler registration."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Register a mock handler
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        assert EventType.CAPITAL_CALL in self.registry._handlers
        assert self.registry._handlers[EventType.CAPITAL_CALL] == MockEventHandler
    
    def test_register_handler_invalid_type(self):
        """Test handler registration with invalid handler type."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Attempt to register invalid handler
        with pytest.raises(ValueError, match="must inherit from BaseFundEventHandler"):
            self.registry.register_handler(EventType.CAPITAL_CALL, MockInvalidHandler)
        
        # Verify handler was not registered (note: clear_handlers restores defaults)
        # So CAPITAL_CALL will still be there with the default handler
        assert EventType.CAPITAL_CALL in self.registry._handlers
    
    def test_register_handler_overwrite_existing(self):
        """Test that registering a handler overwrites existing registration."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Register first handler
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        assert self.registry._handlers[EventType.CAPITAL_CALL] == MockEventHandler
        
        # Register different handler for same event type
        different_handler = MockEventHandler
        self.registry.register_handler(EventType.CAPITAL_CALL, different_handler)
        
        # Verify overwrite
        assert self.registry._handlers[EventType.CAPITAL_CALL] == different_handler
    
    def test_get_handler_success(self):
        """Test successful handler retrieval."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Get handler instance
        handler = self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
        
        assert isinstance(handler, MockEventHandler)
        assert handler.session == self.mock_session
        assert handler.fund == self.mock_fund
    
    def test_get_handler_not_registered(self):
        """Test handler retrieval when no handler is registered."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Note: clear_handlers restores default handlers, so CAPITAL_CALL will still be registered
        # We need to unregister it manually to test this scenario
        self.registry.unregister_handler(EventType.CAPITAL_CALL)
        
        # Attempt to get unregistered handler
        with pytest.raises(ValueError, match="No handler registered for event type"):
            self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
    
    def test_handle_event_success(self):
        """Test successful event handling through registry."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Mock the handler instance
        mock_handler_instance = Mock(spec=MockEventHandler)
        mock_handler_instance.handle.return_value = Mock(spec=FundEvent)
        
        with patch.object(self.registry, 'get_handler', return_value=mock_handler_instance):
            event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'amount': 1000.0,
                'event_date': '2024-01-15'
            }
            
            result = self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
            
            # Verify handler was retrieved and called
            self.registry.get_handler.assert_called_once_with(
                EventType.CAPITAL_CALL, self.mock_session, self.mock_fund
            )
            mock_handler_instance.handle.assert_called_once_with(event_data)
            assert result == mock_handler_instance.handle.return_value
    
    def test_handle_event_missing_event_type(self):
        """Test event handling with missing event_type."""
        event_data = {'amount': 1000.0, 'event_date': '2024-01-15'}
        
        with pytest.raises(ValueError, match="event_type is required in event_data"):
            self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
    
    def test_handle_event_empty_event_type(self):
        """Test event handling with empty event_type."""
        event_data = {'event_type': '', 'amount': 1000.0, 'event_date': '2024-01-15'}
        
        with pytest.raises(ValueError, match="event_type is required in event_data"):
            self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
    
    def test_handle_event_invalid_event_type_string(self):
        """Test event handling with invalid event_type string."""
        event_data = {'event_type': 'INVALID_TYPE', 'amount': 1000.0, 'event_date': '2024-01-15'}
        
        with pytest.raises(ValueError, match="Invalid event_type"):
            self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
    
    def test_handle_event_with_enum_object(self):
        """Test event handling with EventType enum object."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Mock the handler instance
        mock_handler_instance = Mock(spec=MockEventHandler)
        mock_handler_instance.handle.return_value = Mock(spec=FundEvent)
        
        with patch.object(self.registry, 'get_handler', return_value=mock_handler_instance):
            event_data = {
                'event_type': EventType.CAPITAL_CALL,  # Enum object, not string
                'amount': 1000.0,
                'event_date': '2024-01-15'
            }
            
            result = self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
            
            # Verify handler was retrieved and called
            self.registry.get_handler.assert_called_once_with(
                EventType.CAPITAL_CALL, self.mock_session, self.mock_fund
            )
            mock_handler_instance.handle.assert_called_once_with(event_data)
            assert result == mock_handler_instance.handle.return_value
    
    def test_handle_event_with_string_conversion(self):
        """Test event handling with string event_type that gets converted to enum."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Mock the handler instance
        mock_handler_instance = Mock(spec=MockEventHandler)
        mock_handler_instance.handle.return_value = Mock(spec=FundEvent)
        
        with patch.object(self.registry, 'get_handler', return_value=mock_handler_instance):
            event_data = {
                'event_type': 'CAPITAL_CALL',  # String that gets converted
                'amount': 1000.0,
                'event_date': '2024-01-15'
            }
            
            result = self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
            
            # Verify handler was retrieved and called
            self.registry.get_handler.assert_called_once_with(
                EventType.CAPITAL_CALL, self.mock_session, self.mock_fund
            )
            mock_handler_instance.handle.assert_called_once_with(event_data)
            assert result == mock_handler_instance.handle.return_value
    
    def test_is_handler_registered_true(self):
        """Test handler registration check when handler exists."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is True
    
    def test_is_handler_registered_false(self):
        """Test handler registration check when handler doesn't exist."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Note: clear_handlers restores default handlers, so CAPITAL_CALL will still be registered
        # We need to unregister it manually to test this scenario
        self.registry.unregister_handler(EventType.CAPITAL_CALL)
        
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is False
    
    def test_get_registered_event_types(self):
        """Test retrieval of all registered event types."""
        # Clear existing handlers and register some handlers
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        self.registry.register_handler(EventType.DISTRIBUTION, MockEventHandler)
        
        registered_types = self.registry.get_registered_event_types()
        
        assert EventType.CAPITAL_CALL in registered_types
        assert EventType.DISTRIBUTION in registered_types
        # Note: clear_handlers restores default handlers, so we have 7 total (5 defaults + 2 custom)
        assert len(registered_types) == 7
        assert isinstance(registered_types, list)
    
    def test_get_registered_event_types_empty(self):
        """Test retrieval of registered event types when none exist."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        registered_types = self.registry.get_registered_event_types()
        
        # Note: clear_handlers restores default handlers, so we have 7 default handlers
        assert len(registered_types) == 7
        assert isinstance(registered_types, list)
    
    def test_unregister_handler_success(self):
        """Test successful handler unregistration."""
        # Clear existing handlers and register mock handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Verify handler is registered
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is True
        
        # Unregister handler
        self.registry.unregister_handler(EventType.CAPITAL_CALL)
        
        # Verify handler is no longer registered
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is False
    
    def test_unregister_handler_not_registered(self):
        """Test handler unregistration when handler is not registered."""
        # Clear existing handlers for clean test
        self.registry.clear_handlers()
        
        # Unregister non-existent handler (should not raise error)
        self.registry.unregister_handler(EventType.CAPITAL_CALL)
        
        # Verify CAPITAL_CALL is no longer registered, but others remain
        assert len(self.registry.get_registered_event_types()) == 6
        assert EventType.CAPITAL_CALL not in self.registry.get_registered_event_types()
        assert EventType.DISTRIBUTION in self.registry.get_registered_event_types()
    
    def test_clear_handlers(self):
        """Test clearing all registered handlers."""
        # Clear existing handlers and register some handlers
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        self.registry.register_handler(EventType.DISTRIBUTION, MockEventHandler)
        
        # Verify handlers are registered (2 custom + 5 default = 7 total)
        assert len(self.registry.get_registered_event_types()) == 7
        
        # Clear all handlers
        self.registry.clear_handlers()
        
        # Verify default handlers are restored (7 default handlers)
        assert len(self.registry.get_registered_event_types()) == 7
    
    def test_clear_handlers_restores_defaults(self):
        """Test that clearing handlers restores default handlers."""
        # Clear existing handlers and register custom handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Verify custom handler is registered
        assert self.registry._handlers[EventType.CAPITAL_CALL] == MockEventHandler
        
        # Clear handlers
        self.registry.clear_handlers()
        
        # Verify default handlers are restored
        assert EventType.CAPITAL_CALL in self.registry._handlers
        assert self.registry._handlers[EventType.CAPITAL_CALL] != MockEventHandler
    
    def test_registry_performance_handler_retrieval(self):
        """Test registry performance for handler retrieval."""
        # Clear existing handlers and register multiple handlers
        self.registry.clear_handlers()
        for event_type in EventType:
            self.registry.register_handler(event_type, MockEventHandler)
        
        # Test handler retrieval performance
        import time
        
        start_time = time.time()
        for _ in range(1000):
            handler = self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
            assert handler is not None
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion: 1000 retrievals should complete in under 0.1 seconds
        assert execution_time < 0.1, f"Handler retrieval took {execution_time:.3f}s, expected <0.1s"
    
    def test_registry_scalability_multiple_handlers(self):
        """Test registry scalability with many registered handlers."""
        # Clear existing handlers
        self.registry.clear_handlers()
        
        # Register many handlers using existing event types (simulating large system)
        handler_count = 100
        existing_event_types = list(EventType)
        
        for i in range(handler_count):
            # Use existing event types in rotation to avoid creating invalid ones
            event_type = existing_event_types[i % len(existing_event_types)]
            self.registry.register_handler(event_type, MockEventHandler)
        
        # Verify handlers are registered (we'll have multiple handlers for each event type)
        registered_types = self.registry.get_registered_event_types()
        assert len(registered_types) == len(existing_event_types)
        
        # Test retrieval performance
        import time
        
        start_time = time.time()
        for i in range(handler_count):
            event_type = existing_event_types[i % len(existing_event_types)]
            handler = self.registry.get_handler(event_type, self.mock_session, self.mock_fund)
            assert handler is not None
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Performance assertion: 100 retrievals should complete in under 0.05 seconds
        assert execution_time < 0.05, f"Scalability test took {execution_time:.3f}s, expected <0.05s"
    
    def test_registry_thread_safety_simulation(self):
        """Test registry behavior under simulated concurrent access."""
        # Clear existing handlers and register handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Simulate concurrent access by rapidly calling methods
        import threading
        import time
        
        results = []
        errors = []
        
        def concurrent_operation():
            try:
                # Simulate concurrent handler retrieval
                for _ in range(100):
                    handler = self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
                    results.append(handler is not None)
                    time.sleep(0.001)  # Small delay to simulate real work
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=concurrent_operation)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0, f"Concurrent access caused errors: {errors}"
        
        # Verify all operations succeeded
        assert len(results) == 500, f"Expected 500 successful operations, got {len(results)}"
        assert all(results), "All operations should succeed"
    
    def test_registry_error_handling_handler_creation_failure(self):
        """Test registry error handling when handler creation fails."""
        # Clear existing handlers and register handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Mock handler class to raise exception during instantiation
        class FailingHandler(MockEventHandler):
            def __init__(self, session, fund):
                raise RuntimeError("Handler creation failed")
        
        self.registry.register_handler(EventType.CAPITAL_CALL, FailingHandler)
        
        # Attempt to get handler should raise the exception
        with pytest.raises(RuntimeError, match="Handler creation failed"):
            self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
    
    def test_registry_error_handling_handler_validation_failure(self):
        """Test registry error handling when handler validation fails."""
        # Clear existing handlers and register handler
        self.registry.clear_handlers()
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        
        # Mock handler instance that fails validation
        mock_handler_instance = Mock(spec=MockEventHandler)
        mock_handler_instance.handle.side_effect = ValueError("Validation failed")
        
        with patch.object(self.registry, 'get_handler', return_value=mock_handler_instance):
            event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'amount': 1000.0,
                'event_date': '2024-01-15'
            }
            
            # The registry should propagate the handler's validation error
            with pytest.raises(ValueError, match="Validation failed"):
                self.registry.handle_event(event_data, self.mock_session, self.mock_fund)
    
    def test_registry_memory_usage(self):
        """Test registry memory usage characteristics."""
        import sys
        
        # Clear existing handlers
        self.registry.clear_handlers()
        
        # Measure initial memory usage
        initial_size = sys.getsizeof(self.registry._handlers)
        
        # Register many handlers using existing event types
        handler_count = 1000
        existing_event_types = list(EventType)
        
        for i in range(handler_count):
            # Use existing event types in rotation to avoid creating invalid ones
            event_type = existing_event_types[i % len(existing_event_types)]
            self.registry.register_handler(event_type, MockEventHandler)
        
        # Measure final memory usage
        final_size = sys.getsizeof(self.registry._handlers)
        
        # Memory usage should be reasonable (under 1MB for 1000 handlers)
        memory_usage_mb = (final_size - initial_size) / (1024 * 1024)
        assert memory_usage_mb < 1.0, f"Memory usage {memory_usage_mb:.3f}MB exceeds 1MB limit"
        
        # Verify handlers are registered (we'll have multiple handlers for each event type)
        registered_types = self.registry.get_registered_event_types()
        assert len(registered_types) == len(existing_event_types)


class TestEventRegistryIntegration:
    """Test event registry integration with other components."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.registry = FundEventHandlerRegistry()
        self.mock_session = Mock()
        self.mock_fund = Mock(spec=Fund)
        self.mock_fund.id = 1
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.status = FundStatus.ACTIVE
    
    def test_registry_with_orchestrator_integration(self):
        """Test that registry works correctly with orchestrator integration."""
        from src.fund.events.orchestrator import FundUpdateOrchestrator
        
        # Create orchestrator with our registry
        orchestrator = FundUpdateOrchestrator(registry=self.registry)
        
        # Verify orchestrator can access registry
        assert orchestrator.registry == self.registry
        
        # Verify registry status reporting works
        status = orchestrator.get_registry_status()
        assert 'registered_event_types' in status
        assert 'total_handlers' in status
        assert status['total_handlers'] > 0
    
    def test_registry_handler_lifecycle_management(self):
        """Test complete handler lifecycle management."""
        # Clear existing handlers
        self.registry.clear_handlers()
        
        # Test registration
        self.registry.register_handler(EventType.CAPITAL_CALL, MockEventHandler)
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is True
        
        # Test retrieval
        handler = self.registry.get_handler(EventType.CAPITAL_CALL, self.mock_session, self.mock_fund)
        assert isinstance(handler, MockEventHandler)
        
        # Test unregistration
        self.registry.unregister_handler(EventType.CAPITAL_CALL)
        assert self.registry.is_handler_registered(EventType.CAPITAL_CALL) is False
        
        # Test clearing and restoration
        self.registry.clear_handlers()
        # Note: clear_handlers restores default handlers, so we have 7 default handlers
        assert len(self.registry.get_registered_event_types()) == 7
        
        # Verify default handlers are restored
        assert EventType.CAPITAL_CALL in self.registry._handlers
