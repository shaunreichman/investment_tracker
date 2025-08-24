"""
Banking Update Orchestrator Unit Tests.

This module tests ONLY the BankingUpdateOrchestrator functionality:
- Event processing pipeline coordination
- Transaction management and rollback
- Dependent updates handling
- Error handling and recovery
- Cross-module event routing
- Bulk event processing

This file focuses exclusively on orchestrator behavior and does NOT test:
- Individual event handlers (covered by test_banking_event_handlers.py)
- Event registry functionality (covered by test_banking_event_registry.py)
- Cross-module registry functionality (covered by test_banking_event_registry.py)
- Event models or business logic (covered by model tests)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.banking.events.orchestrator import BankingUpdateOrchestrator
from src.banking.events.registry import BankingEventHandlerRegistry
from src.banking.events.cross_module_registry import CrossModuleEventRegistry
from src.banking.models import Bank, BankAccount
from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent


class TestBankingUpdateOrchestrator:
    """Test the BankingUpdateOrchestrator functionality."""
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes with default registry."""
        orchestrator = BankingUpdateOrchestrator()
        
        assert orchestrator.registry is not None
        assert isinstance(orchestrator.registry, BankingEventHandlerRegistry)
        assert orchestrator.cross_module_registry is not None
        assert isinstance(orchestrator.cross_module_registry, CrossModuleEventRegistry)
        assert orchestrator.logger is not None
    
    def test_orchestrator_with_custom_registry(self):
        """Test orchestrator with custom registry dependency injection."""
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        assert orchestrator.registry == mock_registry
        assert orchestrator.cross_module_registry is not None
        assert isinstance(orchestrator.cross_module_registry, CrossModuleEventRegistry)
    
    def test_orchestrator_get_registry_info(self):
        """Test orchestrator registry information reporting."""
        orchestrator = BankingUpdateOrchestrator()
        
        info = orchestrator.get_registry_info()
        
        assert 'registered_event_types' in info
        assert 'total_handlers' in info
        assert 'orchestrator_class' in info
        assert info['orchestrator_class'] == 'BankingUpdateOrchestrator'
        assert isinstance(info['registered_event_types'], list)
        assert isinstance(info['total_handlers'], int)


class TestEventProcessingPipeline:
    """Test the main event processing pipeline."""
    
    @patch('src.banking.events.orchestrator.BankingUpdateOrchestrator._handle_dependent_updates')
    def test_process_banking_event_success(self, mock_handle_dependent):
        """Test successful banking event processing through the pipeline."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        
        # Configure registry mock
        mock_result = {'event_type': 'bank_created', 'bank_id': 1}
        mock_registry.handle_event.return_value = mock_result
        
        # Create orchestrator with mock registry
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        event_data = {'event_type': 'bank_created', 'name': 'Test Bank', 'country': 'AU'}
        
        # Execute
        result = orchestrator.process_banking_event(event_data, mock_session, mock_bank)
        
        # Verify
        assert result == mock_result
        mock_registry.handle_event.assert_called_once_with(event_data, mock_session, mock_bank)
        mock_handle_dependent.assert_called_once_with(mock_result, mock_session, mock_bank)
    
    @patch('src.banking.events.orchestrator.BankingUpdateOrchestrator._handle_dependent_updates')
    def test_process_banking_event_with_bank_account(self, mock_handle_dependent):
        """Test successful banking event processing with bank account entity."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        
        # Configure registry mock
        mock_result = {'event_type': 'bank_account_created', 'account_id': 1}
        mock_registry.handle_event.return_value = mock_result
        
        # Create orchestrator with mock registry
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        event_data = {'event_type': 'bank_account_created', 'account_name': 'Test Account'}
        
        # Execute
        result = orchestrator.process_banking_event(event_data, mock_session, mock_account)
        
        # Verify
        assert result == mock_result
        mock_registry.handle_event.assert_called_once_with(event_data, mock_session, mock_account)
        mock_handle_dependent.assert_called_once_with(mock_result, mock_session, mock_account)
    
    def test_process_banking_event_error_propagation(self):
        """Test that errors are properly propagated without transaction management."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        
        # Configure registry to raise error
        mock_registry.handle_event.side_effect = ValueError("Test error")
        
        # Create orchestrator with mock registry
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        event_data = {'event_type': 'bank_created', 'name': 'Test Bank', 'country': 'AU'}
        
        # Execute and verify error is re-raised
        with pytest.raises(ValueError, match="Test error"):
            orchestrator.process_banking_event(event_data, mock_session, mock_bank)
        
        # Verify the error was raised from the registry, not from transaction management
        mock_registry.handle_event.assert_called_once_with(event_data, mock_session, mock_bank)
    
    @patch('src.banking.events.orchestrator.BankingUpdateOrchestrator._handle_dependent_updates')
    def test_process_bulk_events_success(self, mock_handle_dependent):
        """Test successful bulk event processing."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        
        # Configure registry mock
        mock_result1 = {'event_type': 'bank_created', 'bank_id': 1}
        mock_result2 = {'event_type': 'bank_updated', 'bank_id': 1}
        mock_registry.handle_event.side_effect = [mock_result1, mock_result2]
        
        # Create orchestrator with mock registry
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        events_data = [
            {'event_type': 'bank_created', 'name': 'Test Bank 1', 'country': 'AU'},
            {'event_type': 'bank_updated', 'name': 'Test Bank 2', 'country': 'US'}
        ]
        
        # Execute
        result = orchestrator.process_bulk_events(events_data, mock_session, mock_bank)
        
        # Verify
        assert result == [mock_result1, mock_result2]
        assert mock_registry.handle_event.call_count == 2
        assert mock_handle_dependent.call_count == 2
    
    def test_process_bulk_events_empty_list(self):
        """Test bulk processing with empty event list."""
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        orchestrator = BankingUpdateOrchestrator()
        
        result = orchestrator.process_bulk_events([], mock_session, mock_bank)
        
        assert result == []
    
    def test_process_bulk_events_error_propagation(self):
        """Test that bulk processing errors are properly propagated without transaction management."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_registry = Mock(spec=BankingEventHandlerRegistry)
        
        # Configure registry to raise error on second event
        mock_registry.handle_event.side_effect = [
            {'event_type': 'bank_created', 'bank_id': 1},  # First event succeeds
            ValueError("Second event fails")  # Second event fails
        ]
        
        # Create orchestrator with mock registry
        orchestrator = BankingUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        events_data = [
            {'event_type': 'bank_created', 'name': 'Test Bank 1', 'country': 'AU'},
            {'event_type': 'bank_updated', 'name': 'Test Bank 2', 'country': 'US'}
        ]
        
        # Execute and verify error is re-raised
        with pytest.raises(ValueError, match="Second event fails"):
            orchestrator.process_bulk_events(events_data, mock_session, mock_bank)
        
        # Verify the error was raised from the registry, not from transaction management
        assert mock_registry.handle_event.call_count == 2


class TestDependentUpdatesHandling:
    """Test handling of dependent updates triggered by events."""
    
    def test_handle_dependent_updates_bank_created(self):
        """Test that bank creation events trigger appropriate dependencies."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 1
        
        mock_event_result = {'event_type': 'bank_created', 'bank_id': 1}
        
        # Create orchestrator
        orchestrator = BankingUpdateOrchestrator()
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_bank)
        
        # Verify logging occurred (we can't easily test the specific TODO implementation)
        # but we can verify the method doesn't raise errors
    
    @patch('src.banking.events.domain.bank_account_created_event.BankAccountCreatedEvent')
    def test_handle_dependent_updates_account_created(self, mock_event_class):
        """Test that account creation events trigger cross-module dependencies."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.account_name = "Test Account"
        mock_account.account_number = "123456789"
        mock_account.currency = "AUD"
        mock_account.is_active = True
        
        mock_event_result = {'event_type': 'bank_account_created', 'account_id': 1}
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.return_value = {
            'handlers_executed': 2,
            'warnings': [],
            'errors': []
        }
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was created and routed
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
    
    @patch('src.banking.events.domain.bank_account_deleted_event.BankAccountDeletedEvent')
    def test_handle_dependent_updates_account_deleted(self, mock_event_class):
        """Test that account deletion events trigger cross-module dependencies."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.account_name = "Test Account"
        mock_account.account_number = "123456789"
        mock_account.currency = "AUD"
        
        mock_event_result = {'event_type': 'bank_account_deleted', 'account_id': 1}
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.return_value = {
            'handlers_executed': 1,
            'warnings': [],
            'errors': []
        }
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was created and routed
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
    
    @patch('src.banking.events.domain.currency_changed_event.CurrencyChangedEvent')
    def test_handle_dependent_updates_currency_changed(self, mock_event_class):
        """Test that currency change events trigger cross-module dependencies."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.currency = "USD"
        
        mock_event_result = {
            'event_type': 'currency_changed', 
            'account_id': 1,
            'old_currency': 'AUD'
        }
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.return_value = {
            'handlers_executed': 1,
            'warnings': [],
            'errors': []
        }
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was created and routed
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
    
    @patch('src.banking.events.domain.account_status_changed_event.AccountStatusChangedEvent')
    def test_handle_dependent_updates_status_changed(self, mock_event_class):
        """Test that status change events trigger cross-module dependencies."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.is_active = False
        
        mock_event_result = {
            'event_type': 'account_status_changed', 
            'account_id': 1,
            'old_status': True
        }
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.return_value = {
            'handlers_executed': 1,
            'warnings': [],
            'errors': []
        }
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was created and routed
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
    
    def test_handle_dependent_updates_unknown_event_type(self):
        """Test that unknown event types are handled gracefully."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        
        mock_event_result = {'event_type': 'unknown_event', 'bank_id': 1}
        
        # Create orchestrator
        orchestrator = BankingUpdateOrchestrator()
        
        # Execute (should not raise any errors)
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_bank)
    
    @patch('src.banking.events.domain.bank_account_created_event.BankAccountCreatedEvent')
    def test_handle_dependent_updates_cross_module_error(self, mock_event_class):
        """Test that cross-module errors are logged but don't fail the main operation."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.account_name = "Test Account"
        mock_account.account_number = "123456789"
        mock_account.currency = "AUD"
        mock_account.is_active = True
        
        mock_event_result = {'event_type': 'bank_account_created', 'account_id': 1}
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry to raise an error
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.side_effect = Exception("Cross-module error")
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute (should not raise any errors, just log them)
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was attempted
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
    
    def test_handle_bulk_dependent_updates(self):
        """Test handling of dependent updates for bulk event processing."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        
        mock_event_results = [
            {'event_type': 'bank_created', 'bank_id': 1},
            {'event_type': 'bank_updated', 'bank_id': 1}
        ]
        
        # Create orchestrator
        orchestrator = BankingUpdateOrchestrator()
        
        # Mock the _handle_dependent_updates method to track calls
        with patch.object(orchestrator, '_handle_dependent_updates') as mock_handle:
            # Execute
            orchestrator._handle_bulk_dependent_updates(mock_event_results, mock_session, mock_bank)
            
            # Verify each event result was processed
            assert mock_handle.call_count == 2
            mock_handle.assert_any_call(mock_event_results[0], mock_session, mock_bank)
            mock_handle.assert_any_call(mock_event_results[1], mock_session, mock_bank)
    
    def test_handle_bulk_dependent_updates_error(self):
        """Test that bulk dependent updates errors are handled properly."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        
        mock_event_results = [
            {'event_type': 'bank_created', 'bank_id': 1},
            {'event_type': 'bank_updated', 'bank_id': 1}
        ]
        
        # Create orchestrator
        orchestrator = BankingUpdateOrchestrator()
        
        # Mock the _handle_dependent_updates method to raise an error
        with patch.object(orchestrator, '_handle_dependent_updates') as mock_handle:
            mock_handle.side_effect = RuntimeError("Dependency error")
            
            # Execute and verify error is re-raised
            with pytest.raises(RuntimeError, match="Dependency error"):
                orchestrator._handle_bulk_dependent_updates(mock_event_results, mock_session, mock_bank)





class TestCrossModuleIntegration:
    """Test integration with cross-module event registry."""
    
    def test_cross_module_registry_initialization(self):
        """Test that cross-module registry is properly initialized."""
        orchestrator = BankingUpdateOrchestrator()
        
        assert orchestrator.cross_module_registry is not None
        assert isinstance(orchestrator.cross_module_registry, CrossModuleEventRegistry)
    
    def test_cross_module_registry_dependency_injection(self):
        """Test that cross-module registry can be injected."""
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        
        # Create orchestrator and manually set cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        assert orchestrator.cross_module_registry == mock_cross_module_registry
    
    @patch('src.banking.events.domain.bank_account_created_event.BankAccountCreatedEvent')
    def test_cross_module_event_routing_integration(self, mock_event_class):
        """Test that cross-module events are properly routed."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 1
        mock_account.entity_id = 100
        mock_account.bank_id = 200
        mock_account.account_name = "Test Account"
        mock_account.account_number = "123456789"
        mock_account.currency = "AUD"
        mock_account.is_active = True
        
        mock_event_result = {'event_type': 'bank_account_created', 'account_id': 1}
        
        # Mock the event class to avoid constructor issues
        mock_event = Mock()
        mock_event_class.return_value = mock_event
        
        # Mock cross-module registry with specific return values
        mock_cross_module_registry = Mock(spec=CrossModuleEventRegistry)
        mock_cross_module_registry.route_event.return_value = {
            'handlers_executed': ['fund_handler', 'entity_handler'],
            'results': {
                'fund_handler': {'status': 'success'},
                'entity_handler': {'status': 'success'}
            },
            'warnings': ['Minor warning'],
            'errors': []
        }
        
        # Create orchestrator with mocked cross-module registry
        orchestrator = BankingUpdateOrchestrator()
        orchestrator.cross_module_registry = mock_cross_module_registry
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event_result, mock_session, mock_account)
        
        # Verify cross-module event was routed with correct parameters
        mock_cross_module_registry.route_event.assert_called_once_with(mock_event, mock_session)
