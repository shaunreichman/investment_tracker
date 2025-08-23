"""
Test suite for Banking Cross-Module Event Registry.

This test suite validates the CrossModuleEventRegistry's ability to:
1. Initialize handlers from other modules
2. Route banking events to appropriate handlers
3. Handle cross-module integration failures gracefully
4. Maintain data consistency across systems
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
import logging
from datetime import date

from src.banking.events.cross_module_registry import CrossModuleEventRegistry
from src.banking.events.domain.bank_account_deleted_event import BankAccountDeletedEvent
from src.banking.events.domain.bank_account_created_event import BankAccountCreatedEvent
from src.banking.events.domain.bank_account_updated_event import BankAccountUpdatedEvent
from src.banking.events.domain.currency_changed_event import CurrencyChangedEvent
from src.banking.events.domain.account_status_changed_event import AccountStatusChangedEvent


class TestCrossModuleEventRegistry:
    """Test suite for CrossModuleEventRegistry functionality."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = Mock(spec=Session)
        session.commit = Mock()
        session.rollback = Mock()
        return session
    
    @pytest.fixture
    def registry(self):
        """Create a CrossModuleEventRegistry instance."""
        return CrossModuleEventRegistry()
    
    @pytest.fixture
    def mock_fund_handler(self):
        """Create a mock fund system handler."""
        handler = Mock()
        handler.handle_bank_account_deleted = Mock(return_value={
            "success": True,
            "action": "marked_cash_flows_inactive",
            "cash_flows_affected": 2,
            "message": "Cash flows marked inactive"
        })
        handler.handle_bank_account_currency_changed = Mock(return_value={
            "success": True,
            "action": "currency_change_processed",
            "cash_flows_affected": 0,
            "message": "Currency change processed"
        })
        handler.handle_bank_account_status_changed = Mock(return_value={
            "success": True,
            "action": "account_status_updated",
            "cash_flows_affected": 0,
            "message": "Status change processed"
        })
        return handler
    
    @pytest.fixture
    def mock_entity_handler(self):
        """Create a mock entity system handler."""
        handler = Mock()
        handler.handle_bank_account_created = Mock(return_value={
            "success": True,
            "action": "entity_banking_updated",
            "entity_id": 1,
            "account_id": 1,
            "message": "Entity banking status updated"
        })
        handler.handle_bank_account_deleted = Mock(return_value={
            "success": True,
            "action": "entity_accounts_remaining",
            "entity_id": 1,
            "account_id": 1,
            "remaining_accounts": 2,
            "message": "Entity has remaining accounts"
        })
        handler.handle_bank_account_updated = Mock(return_value={
            "success": True,
            "action": "entity_banking_updated",
            "entity_id": 1,
            "account_id": 1,
            "message": "Entity banking status updated"
        })
        handler.handle_bank_account_currency_changed = Mock(return_value={
            "success": True,
            "action": "currency_change_processed_single_currency",
            "entity_id": 1,
            "account_id": 1,
            "new_currency": "USD",
            "message": "Currency change processed"
        })
        handler.handle_bank_account_status_changed = Mock(return_value={
            "success": True,
            "action": "entity_banking_status_updated",
            "entity_id": 1,
            "account_id": 1,
            "account_status": "active",
            "active_accounts": 3,
            "message": "Entity banking status updated"
        })
        return handler
    
    @pytest.fixture
    def sample_events(self):
        """Create sample banking domain events for testing."""
        test_date = date(2025, 1, 15)
        return {
            'bank_account_deleted': BankAccountDeletedEvent(
                account_id=1,
                event_date=test_date,
                metadata={
                    'entity_id': 1,
                    'bank_id': 1,
                    'account_number': "1234567890",
                    'deletion_reason': 'Account closure'
                }
            ),
            'bank_account_created': BankAccountCreatedEvent(
                account_id=1,
                event_date=test_date,
                metadata={
                    'entity_id': 1,
                    'bank_id': 1,
                    'account_number': "1234567890",
                    'currency': "USD"
                }
            ),
            'bank_account_updated': BankAccountUpdatedEvent(
                account_id=1,
                event_date=test_date,
                metadata={
                    'entity_id': 1,
                    'bank_id': 1,
                    'account_number': "1234567890",
                    'changes': {'status': 'active'}
                }
            ),
            'currency_changed': CurrencyChangedEvent(
                account_id=1,
                event_date=test_date,
                old_currency="EUR",
                new_currency="USD"
            ),
            'account_status_changed': AccountStatusChangedEvent(
                account_id=1,
                event_date=test_date,
                old_status=False,
                new_status=True
            )
        }

    def test_registry_initialization(self, registry):
        """Test that the registry initializes correctly."""
        assert registry is not None
        assert hasattr(registry, '_fund_handlers')
        assert hasattr(registry, '_entity_handlers')
        assert hasattr(registry, '_investment_company_handlers')
        assert isinstance(registry.logger, logging.Logger)

    def test_handler_initialization_structure(self, registry):
        """Test that the registry has the expected handler structure."""
        # Verify the registry has the expected handler dictionaries
        assert isinstance(registry._fund_handlers, dict)
        assert isinstance(registry._entity_handlers, dict)
        assert isinstance(registry._investment_company_handlers, dict)
        
        # Verify investment company handlers are empty (placeholder for future)
        assert registry._investment_company_handlers == {}

    def test_route_bank_account_deleted_event(self, registry, mock_session, sample_events):
        """Test routing of bank account deleted events."""
        # Mock the handlers
        registry._fund_handlers = {
            'bank_account_deleted': Mock(return_value={
                "success": True,
                "action": "marked_cash_flows_inactive",
                "cash_flows_affected": 2,
                "message": "Cash flows marked inactive"
            })
        }
        registry._entity_handlers = {
            'bank_account_deleted': Mock(return_value={
                "success": True,
                "action": "entity_accounts_remaining",
                "entity_id": 1,
                "account_id": 1,
                "remaining_accounts": 2,
                "message": "Entity has remaining accounts"
            })
        }
        
        event = sample_events['bank_account_deleted']
        result = registry.route_event(event, mock_session)
        
        # Verify event was routed correctly
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert len(result['errors']) == 0

    def test_route_bank_account_created_event(self, registry, mock_session, sample_events):
        """Test routing of bank account created events."""
        # Mock the entity handler
        registry._entity_handlers = {
            'bank_account_created': Mock(return_value={
                "success": True,
                "action": "entity_banking_updated",
                "entity_id": 1,
                "account_id": 1,
                "message": "Entity banking status updated"
            })
        }
        
        event = sample_events['bank_account_created']
        result = registry.route_event(event, mock_session)
        
        # Verify event was routed correctly
        assert result['event_type'] == 'BankAccountCreatedEvent'
        assert 'entity_system' in result['handlers_executed']
        assert 'entity_system' in result['results']
        assert len(result['errors']) == 0

    def test_route_bank_account_updated_event(self, registry, mock_session, sample_events):
        """Test routing of bank account updated events."""
        # Mock the entity handler
        registry._entity_handlers = {
            'bank_account_updated': Mock(return_value={
                "success": True,
                "action": "entity_banking_updated",
                "entity_id": 1,
                "account_id": 1,
                "message": "Entity banking status updated"
            })
        }
        
        event = sample_events['bank_account_updated']
        result = registry.route_event(event, mock_session)
        
        # Verify event was routed correctly
        assert result['event_type'] == 'BankAccountUpdatedEvent'
        assert 'entity_system' in result['handlers_executed']
        assert 'entity_system' in result['results']
        assert len(result['errors']) == 0

    def test_route_currency_changed_event(self, registry, mock_session, sample_events):
        """Test routing of currency changed events."""
        # Mock the handlers
        registry._fund_handlers = {
            'currency_changed': Mock(return_value={
                "success": True,
                "action": "currency_change_processed",
                "cash_flows_affected": 0,
                "message": "Currency change processed"
            })
        }
        registry._entity_handlers = {
            'currency_changed': Mock(return_value={
                "success": True,
                "action": "currency_change_processed_single_currency",
                "entity_id": 1,
                "account_id": 1,
                "new_currency": "USD",
                "message": "Currency change processed"
            })
        }
        
        event = sample_events['currency_changed']
        result = registry.route_event(event, mock_session)
        
        # Verify event was routed correctly
        assert result['event_type'] == 'CurrencyChangedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert len(result['errors']) == 0

    def test_route_account_status_changed_event(self, registry, mock_session, sample_events):
        """Test routing of account status changed events."""
        # Mock the handlers
        registry._fund_handlers = {
            'account_status_changed': Mock(return_value={
                "success": True,
                "action": "account_status_updated",
                "cash_flows_affected": 0,
                "message": "Status change processed"
            })
        }
        registry._entity_handlers = {
            'account_status_changed': Mock(return_value={
                "success": True,
                "action": "entity_banking_status_updated",
                "entity_id": 1,
                "account_id": 1,
                "account_status": "active",
                "active_accounts": 3,
                "message": "Entity banking status updated"
            })
        }
        
        event = sample_events['account_status_changed']
        result = registry.route_event(event, mock_session)
        
        # Verify event was routed correctly
        assert result['event_type'] == 'AccountStatusChangedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' in result['results']
        assert len(result['errors']) == 0

    def test_route_unknown_event_type(self, registry, mock_session):
        """Test handling of unknown event types."""
        # Create an unknown event type
        class UnknownEvent:
            pass
        
        unknown_event = UnknownEvent()
        result = registry.route_event(unknown_event, mock_session)
        
        # Verify unknown event is handled gracefully
        assert result['event_type'] == 'UnknownEvent'
        assert len(result['handlers_executed']) == 0
        assert len(result['results']) == 0
        assert len(result['errors']) == 0

    def test_handler_execution_failure(self, registry, mock_session, sample_events):
        """Test handling of handler execution failures."""
        # Mock a handler that raises an exception
        registry._fund_handlers = {
            'bank_account_deleted': Mock(side_effect=RuntimeError("Handler failed"))
        }
        registry._entity_handlers = {
            'bank_account_deleted': Mock(return_value={
                "success": True,
                "action": "entity_accounts_remaining",
                "entity_id": 1,
                "account_id": 1,
                "remaining_accounts": 2,
                "message": "Entity has remaining accounts"
            })
        }
        
        event = sample_events['bank_account_deleted']
        result = registry.route_event(event, mock_session)
        
        # Verify failure is handled gracefully
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert 'entity_system' in result['handlers_executed']
        assert 'fund_system' not in result['handlers_executed']
        assert 'entity_system' in result['results']
        assert 'fund_system' not in result['results']
        assert len(result['errors']) == 1
        assert "Fund system handler failed" in result['errors'][0]

    def test_multiple_handler_failures(self, registry, mock_session, sample_events):
        """Test handling of multiple handler failures."""
        # Mock handlers that both raise exceptions
        registry._fund_handlers = {
            'bank_account_deleted': Mock(side_effect=RuntimeError("Fund handler failed"))
        }
        registry._entity_handlers = {
            'bank_account_deleted': Mock(side_effect=RuntimeError("Entity handler failed"))
        }
        
        event = sample_events['bank_account_deleted']
        result = registry.route_event(event, mock_session)
        
        # Verify all failures are captured
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert len(result['handlers_executed']) == 0
        assert len(result['results']) == 0
        assert len(result['errors']) == 2
        assert any("Fund system handler failed" in error for error in result['errors'])
        assert any("Entity system handler failed" in error for error in result['errors'])

    def test_warning_aggregation(self, registry, mock_session, sample_events):
        """Test that warnings from handlers are properly aggregated."""
        # Mock handlers that return warnings
        registry._fund_handlers = {
            'currency_changed': Mock(return_value={
                "success": True,
                "action": "currency_mismatch_detected",
                "cash_flows_affected": 3,
                "warnings": ["Currency mismatch detected in cash flows"],
                "message": "Currency change processed with warnings"
            })
        }
        registry._entity_handlers = {
            'currency_changed': Mock(return_value={
                "success": True,
                "action": "currency_change_processed_multi_currency",
                "entity_id": 1,
                "account_id": 1,
                "new_currency": "USD",
                "warnings": ["Multi-currency entity detected"],
                "message": "Currency change processed"
            })
        }
        
        event = sample_events['currency_changed']
        result = registry.route_event(event, mock_session)
        
        # Verify warnings are aggregated
        assert len(result['warnings']) == 2
        assert "Currency mismatch detected in cash flows" in result['warnings']
        assert "Multi-currency entity detected" in result['warnings']

    def test_event_routing_with_missing_handlers(self, registry, mock_session, sample_events):
        """Test event routing when some handlers are missing."""
        # Only provide fund handlers, no entity handlers
        registry._fund_handlers = {
            'bank_account_deleted': Mock(return_value={
                "success": True,
                "action": "marked_cash_flows_inactive",
                "cash_flows_affected": 2,
                "message": "Cash flows marked inactive"
            })
        }
        registry._entity_handlers = {}
        
        event = sample_events['bank_account_deleted']
        result = registry.route_event(event, mock_session)
        
        # Verify only available handlers are executed
        assert result['event_type'] == 'BankAccountDeletedEvent'
        assert 'fund_system' in result['handlers_executed']
        assert 'entity_system' not in result['handlers_executed']
        assert 'fund_system' in result['results']
        assert 'entity_system' not in result['results']
        assert len(result['errors']) == 0

    def test_registry_exception_handling(self, registry, mock_session, sample_events):
        """Test that registry exceptions are handled gracefully."""
        # Test that the registry can handle events without crashing
        event = sample_events['bank_account_deleted']
        
        # This should work normally
        result = registry.route_event(event, mock_session)
        
        # Verify the result has the expected structure
        assert 'event_type' in result
        assert 'handlers_executed' in result
        assert 'results' in result
        assert 'warnings' in result
        assert 'errors' in result

    def test_investment_company_handlers_placeholder(self, registry):
        """Test that investment company handlers are properly initialized as placeholders."""
        # Verify investment company handlers are initialized (currently empty)
        assert registry._investment_company_handlers == {}
        
        # This is expected behavior for the current implementation
        # Future enhancement will add actual investment company handlers

    def test_handler_method_signatures(self, registry):
        """Test that all handler methods have the correct signatures."""
        # Test fund handler method signatures
        if registry._fund_handlers:
            for event_type, handler_method in registry._fund_handlers.items():
                assert callable(handler_method)
                # Verify method can be called with event and session parameters
                # (We can't easily test the actual signature without the real handlers)
        
        # Test entity handler method signatures
        if registry._entity_handlers:
            for event_type, handler_method in registry._entity_handlers.items():
                assert callable(handler_method)
                # Verify method can be called with event and session parameters

    def test_logging_functionality(self, registry):
        """Test that logging is properly configured."""
        assert registry.logger is not None
        assert isinstance(registry.logger, logging.Logger)
        assert registry.logger.name == 'src.banking.events.cross_module_registry'

    def test_result_structure_consistency(self, registry, mock_session, sample_events):
        """Test that all event routing results have consistent structure."""
        # Mock handlers for all event types
        registry._fund_handlers = {
            'bank_account_deleted': Mock(return_value={"success": True}),
            'currency_changed': Mock(return_value={"success": True}),
            'account_status_changed': Mock(return_value={"success": True})
        }
        registry._entity_handlers = {
            'bank_account_created': Mock(return_value={"success": True}),
            'bank_account_deleted': Mock(return_value={"success": True}),
            'bank_account_updated': Mock(return_value={"success": True}),
            'currency_changed': Mock(return_value={"success": True}),
            'account_status_changed': Mock(return_value={"success": True})
        }
        
        # Test all event types
        for event_name, event in sample_events.items():
            result = registry.route_event(event, mock_session)
            
            # Verify consistent result structure
            assert 'event_type' in result
            assert 'handlers_executed' in result
            assert 'results' in result
            assert 'warnings' in result
            assert 'errors' in result
            
            # Verify all fields are lists or dicts as expected
            assert isinstance(result['handlers_executed'], list)
            assert isinstance(result['results'], dict)
            assert isinstance(result['warnings'], list)
            assert isinstance(result['errors'], list)
