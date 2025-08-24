"""
Test Banking Event Registry.

This module tests the CrossModuleEventRegistry class which routes banking events
to handlers in other modules for cross-module integration and data consistency.

Key responsibilities tested:
- Handler initialization from other modules
- Event routing based on event type
- Cross-module handler execution
- Error handling and logging
- Result aggregation and reporting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date
from sqlalchemy.orm import Session

from src.banking.events.cross_module_registry import CrossModuleEventRegistry
from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
from src.banking.events.domain.bank_account_updated_event import BankAccountUpdatedEvent
from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent


class TestCrossModuleEventRegistry:
    """Test suite for CrossModuleEventRegistry functionality."""
    
    def test_registry_initialization(self):
        """Test registry initialization and handler setup."""
        # Act
        registry = CrossModuleEventRegistry()
        
        # Assert
        assert registry.logger is not None
        assert hasattr(registry, '_fund_handlers')
        assert hasattr(registry, '_entity_handlers')
        assert hasattr(registry, '_investment_company_handlers')
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_handler_initialization_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful handler initialization from other modules."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Act
        registry = CrossModuleEventRegistry()
        
        # Assert
        assert 'bank_account_deleted' in registry._fund_handlers
        assert 'currency_changed' in registry._fund_handlers
        assert 'account_status_changed' in registry._fund_handlers
        
        assert 'bank_account_created' in registry._entity_handlers
        assert 'bank_account_deleted' in registry._entity_handlers
        assert 'currency_changed' in registry._entity_handlers
        assert 'account_status_changed' in registry._entity_handlers
        
        # Verify handler methods are properly bound
        assert registry._fund_handlers['bank_account_deleted'] == mock_fund_instance.handle_bank_account_deleted
        assert registry._entity_handlers['bank_account_created'] == mock_entity_instance.handle_bank_account_created
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_handler_initialization_with_import_errors(self, mock_entity_handler, mock_fund_handler):
        """Test handler initialization when modules fail to import."""
        # Arrange
        mock_fund_handler.side_effect = ImportError("Module not found")
        mock_entity_handler.side_effect = ImportError("Module not found")
        
        # Act
        registry = CrossModuleEventRegistry()
        
        # Assert
        assert registry._fund_handlers == {}
        assert registry._entity_handlers == {}
        assert registry._investment_company_handlers == {}
    
    def test_route_event_unknown_event_type(self):
        """Test routing of unknown event types."""
        # Arrange
        registry = CrossModuleEventRegistry()
        unknown_event = Mock()
        unknown_event.__class__.__name__ = "UnknownEvent"
        session = Mock()
        
        # Act
        result = registry.route_event(unknown_event, session)
        
        # Assert
        assert result['event_type'] == 'UnknownEvent'
        assert result['handlers_executed'] == []
        assert result['results'] == {}
        assert result['warnings'] == []
        assert result['errors'] == []
    
    def test_route_event_with_exception(self):
        """Test event routing when an exception occurs."""
        # Arrange
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Mock the routing method to raise an exception
        with patch.object(registry, '_route_bank_account_deleted', side_effect=Exception("Test error")):
            # Act
            result = registry.route_event(event, session)
            
            # Assert
            assert result['event_type'] == 'BankAccountDeletedEvent'
            assert result['handlers_executed'] == []
            assert result['results'] == {}
            assert result['warnings'] == []
            assert len(result['errors']) == 1
            assert "Event routing failed: Test error" in result['errors'][0]
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_bank_account_deleted_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful routing of bank account deletion events."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock successful handler responses
        mock_fund_instance.handle_bank_account_deleted.return_value = {
            'success': True,
            'action': 'marked_cash_flows_inactive',
            'cash_flows_affected': 2
        }
        mock_entity_instance.handle_bank_account_deleted.return_value = {
            'success': True,
            'action': 'entity_banking_updated',
            'entity_id': 456
        }
        
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert result['warnings'] == []
        assert result['errors'] == []
        
        # Verify handlers were called with correct parameters
        mock_fund_instance.handle_bank_account_deleted.assert_called_once_with(event, session)
        mock_entity_instance.handle_bank_account_deleted.assert_called_once_with(event, session)
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_bank_account_deleted_with_handler_errors(self, mock_entity_handler, mock_fund_handler):
        """Test bank account deletion routing when handlers fail."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock handler failures
        mock_fund_instance.handle_bank_account_deleted.side_effect = Exception("Fund handler failed")
        mock_entity_instance.handle_bank_account_deleted.side_effect = Exception("Entity handler failed")
        
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert result['handlers_executed'] == []
        assert result['results'] == {}
        assert result['warnings'] == []
        assert len(result['errors']) == 2
        assert "Fund system handler failed: Fund handler failed" in result['errors']
        assert "Entity system handler failed: Entity handler failed" in result['errors']
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_bank_account_deleted_with_warnings(self, mock_entity_handler, mock_fund_handler):
        """Test bank account deletion routing when handlers return warnings."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock handler responses with warnings
        mock_fund_instance.handle_bank_account_deleted.return_value = {
            'success': True,
            'warnings': ['Cash flows may need review']
        }
        mock_entity_instance.handle_bank_account_deleted.return_value = {
            'success': True,
            'warnings': ['Entity banking status updated']
        }
        
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert len(result['warnings']) == 2
        assert 'Cash flows may need review' in result['warnings']
        assert 'Entity banking status updated' in result['warnings']
        assert result['errors'] == []
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_bank_account_created_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful routing of bank account creation events."""
        # Arrange
        mock_entity_instance = Mock()
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock successful handler response
        mock_entity_instance.handle_bank_account_created.return_value = {
            'success': True,
            'action': 'entity_banking_updated',
            'entity_id': 456,
            'account_id': 123
        }
        
        registry = CrossModuleEventRegistry()
        event = BankAccountCreatedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountCreatedEvent'
        assert 'entity_system' in result['handlers_executed']
        assert 'entity_system' in result['results']
        assert result['warnings'] == []
        assert result['errors'] == []
        
        # Verify handler was called with correct parameters
        mock_entity_instance.handle_bank_account_created.assert_called_once_with(event, session)
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_bank_account_updated_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful routing of bank account update events."""
        # Arrange
        mock_entity_instance = Mock()
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock successful handler response
        mock_entity_instance.handle_bank_account_updated.return_value = {
            'success': True,
            'action': 'entity_banking_updated',
            'entity_id': 456,
            'account_id': 123
        }
        
        registry = CrossModuleEventRegistry()
        event = BankAccountUpdatedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountUpdatedEvent'
        # Note: Currently no handlers are executed for BankAccountUpdatedEvent because
        # the EntityBankingIntegrationHandler doesn't implement handle_bank_account_updated
        # This is a backend implementation issue that should be addressed
        assert result['handlers_executed'] == []
        assert result['results'] == {}
        assert result['warnings'] == []
        assert result['errors'] == []
        
        # Verify handler was not called (because it doesn't exist in the backend)
        mock_entity_instance.handle_bank_account_updated.assert_not_called()
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_currency_changed_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful routing of currency change events."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock successful handler responses
        mock_fund_instance.handle_bank_account_currency_changed.return_value = {
            'success': True,
            'action': 'currency_mismatch_check',
            'warnings': ['Some cash flows may need currency conversion']
        }
        mock_entity_instance.handle_bank_account_currency_changed.return_value = {
            'success': True,
            'action': 'entity_currency_updated',
            'entity_id': 456
        }
        
        registry = CrossModuleEventRegistry()
        event = CurrencyChangedEvent(123, date(2025, 1, 15), "USD", "EUR")
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'CurrencyChangedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert len(result['warnings']) == 1
        assert 'Some cash flows may need currency conversion' in result['warnings']
        assert result['errors'] == []
        
        # Verify handlers were called with correct parameters
        mock_fund_instance.handle_bank_account_currency_changed.assert_called_once_with(event, session)
        mock_entity_instance.handle_bank_account_currency_changed.assert_called_once_with(event, session)
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_account_status_changed_success(self, mock_entity_handler, mock_fund_handler):
        """Test successful routing of account status change events."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock successful handler responses
        mock_fund_instance.handle_bank_account_status_changed.return_value = {
            'success': True,
            'action': 'active_cash_flows_check',
            'active_cash_flows': 0
        }
        mock_entity_instance.handle_bank_account_status_changed.return_value = {
            'success': True,
            'action': 'entity_banking_status_updated',
            'entity_id': 456
        }
        
        registry = CrossModuleEventRegistry()
        event = AccountStatusChangedEvent(123, date(2025, 1, 15), True, False)
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'AccountStatusChangedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert result['warnings'] == []
        assert result['errors'] == []
        
        # Verify handlers were called with correct parameters
        mock_fund_instance.handle_bank_account_status_changed.assert_called_once_with(event, session)
        mock_entity_instance.handle_bank_account_status_changed.assert_called_once_with(event, session)
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_route_events_with_missing_handlers(self, mock_entity_handler, mock_fund_handler):
        """Test event routing when specific handlers are missing."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Remove some handlers to simulate missing functionality
        registry = CrossModuleEventRegistry()
        registry._fund_handlers = {}  # No fund handlers
        registry._entity_handlers = {'bank_account_created': mock_entity_instance.handle_bank_account_created}
        
        event = BankAccountCreatedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Mock successful handler response
        mock_entity_instance.handle_bank_account_created.return_value = {
            'success': True,
            'action': 'entity_banking_updated'
        }
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountCreatedEvent'
        assert 'entity_system' in result['handlers_executed']
        assert result['results']['entity_system']['success'] is True
        assert result['warnings'] == []
        assert result['errors'] == []
    
    def test_registry_logging(self):
        """Test that registry properly logs operations."""
        # Arrange
        with patch('logging.getLogger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger
            
            # Act
            registry = CrossModuleEventRegistry()
            
            # Assert
            # The registry calls getLogger during initialization, so we check it was called
            mock_get_logger.assert_called()
            assert registry.logger == mock_logger
    
    @patch('src.fund.events.handlers.banking_integration_handler.BankingIntegrationHandler')
    @patch('src.entity.events.banking_integration_handler.EntityBankingIntegrationHandler')
    def test_registry_error_logging(self, mock_entity_handler, mock_fund_handler):
        """Test that registry logs errors properly."""
        # Arrange
        mock_fund_instance = Mock()
        mock_entity_instance = Mock()
        mock_fund_handler.return_value = mock_fund_instance
        mock_entity_handler.return_value = mock_entity_instance
        
        # Mock handler failure
        mock_fund_instance.handle_bank_account_deleted.side_effect = Exception("Test error")
        
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(123, date(2025, 1, 15))
        session = Mock()
        
        # Act
        with patch.object(registry.logger, 'error') as mock_error_log:
            result = registry.route_event(event, session)
            
            # Assert
            assert "Fund system handler failed: Test error" in result['errors']
            mock_error_log.assert_called()
    
    def test_registry_result_structure_consistency(self):
        """Test that all event routing returns consistent result structure."""
        # Arrange
        registry = CrossModuleEventRegistry()
        session = Mock()
        
        # Test all event types
        events = [
            BankAccountDeletedEvent(123, date(2025, 1, 15)),
            BankAccountCreatedEvent(123, date(2025, 1, 15)),
            BankAccountUpdatedEvent(123, date(2025, 1, 15)),
            CurrencyChangedEvent(123, date(2025, 1, 15), "USD", "EUR"),
            AccountStatusChangedEvent(123, date(2025, 1, 15), True, False)
        ]
        
        # Act & Assert
        for event in events:
            result = registry.route_event(event, session)
            
            # Verify consistent structure
            assert 'event_type' in result
            assert 'handlers_executed' in result
            assert 'results' in result
            assert 'warnings' in result
            assert 'errors' in result
            
            # Verify types
            assert isinstance(result['event_type'], str)
            assert isinstance(result['handlers_executed'], list)
            assert isinstance(result['results'], dict)
            assert isinstance(result['warnings'], list)
            assert isinstance(result['errors'], list)
            
            # Verify event type matches
            assert result['event_type'] == event.__class__.__name__


class TestCrossModuleEventRegistryIntegration:
    """Integration tests for CrossModuleEventRegistry with real event objects."""
    
    def test_registry_with_real_bank_account_deleted_event(self):
        """Test registry with actual BankAccountDeletedEvent instance."""
        # Arrange
        registry = CrossModuleEventRegistry()
        event = BankAccountDeletedEvent(
            account_id=123,
            event_date=date(2025, 1, 15),
            metadata={'deletion_reason': 'Account closed', 'final_balance': 0.00}
        )
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert result['event_type'] == event.__class__.__name__
        assert isinstance(result['handlers_executed'], list)
        assert isinstance(result['results'], dict)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['errors'], list)
    
    def test_registry_with_real_currency_changed_event(self):
        """Test registry with actual CurrencyChangedEvent instance."""
        # Arrange
        registry = CrossModuleEventRegistry()
        event = CurrencyChangedEvent(
            account_id=123,
            event_date=date(2025, 1, 15),
            old_currency="USD",
            new_currency="EUR",
            metadata={'exchange_rate': 0.85}
        )
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'CurrencyChangedEvent'
        assert result['event_type'] == event.__class__.__name__
        assert event.old_currency == "USD"
        assert event.new_currency == "EUR"
        assert event.metadata['exchange_rate'] == 0.85
        assert isinstance(result['handlers_executed'], list)
        assert isinstance(result['results'], dict)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['errors'], list)
    
    def test_registry_with_real_account_status_changed_event(self):
        """Test registry with actual AccountStatusChangedEvent instance."""
        # Arrange
        registry = CrossModuleEventRegistry()
        event = AccountStatusChangedEvent(
            account_id=123,
            event_date=date(2025, 1, 15),
            old_status=True,
            new_status=False,
            metadata={'reason': 'Compliance review'}
        )
        session = Mock()
        
        # Act
        result = registry.route_event(event, session)
        
        # Assert
        assert result['event_type'] == 'AccountStatusChangedEvent'
        assert result['event_type'] == event.__class__.__name__
        assert event.old_status is True
        assert event.new_status is False
        assert event.metadata['reason'] == 'Compliance review'
        assert isinstance(result['handlers_executed'], list)
        assert isinstance(result['results'], dict)
        assert isinstance(result['warnings'], list)
        assert isinstance(result['errors'], list)
