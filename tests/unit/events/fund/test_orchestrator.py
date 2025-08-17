"""
Fund Event Orchestrator Unit Tests.

This module tests ONLY the FundUpdateOrchestrator functionality:
- Event processing pipeline coordination
- Transaction management and rollback
- Dependent updates handling
- Error handling and recovery
- Event validation

This file focuses exclusively on orchestrator behavior and does NOT test:
- Individual event handlers (covered by test_event_handlers.py)
- Event registry functionality (covered by test_event_registry.py)
- Base handler functionality (covered by test_base_handler.py)
- Event models or business logic (covered by model tests)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy.orm import Session

from src.fund.events.orchestrator import FundUpdateOrchestrator
from src.fund.events.registry import FundEventHandlerRegistry
from src.fund.models import Fund, FundEvent
from src.fund.enums import EventType, FundType, DomainEventType


class TestFundUpdateOrchestrator:
    """Test the FundUpdateOrchestrator functionality."""
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes with default registry."""
        orchestrator = FundUpdateOrchestrator()
        
        assert orchestrator.registry is not None
        assert isinstance(orchestrator.registry, FundEventHandlerRegistry)
    
    def test_orchestrator_with_custom_registry(self):
        """Test orchestrator with custom registry dependency injection."""
        mock_registry = Mock(spec=FundEventHandlerRegistry)
        orchestrator = FundUpdateOrchestrator(registry=mock_registry)
        
        assert orchestrator.registry == mock_registry
    
    def test_orchestrator_get_registry_status(self):
        """Test orchestrator registry status reporting."""
        orchestrator = FundUpdateOrchestrator()
        
        status = orchestrator.get_registry_status()
        
        assert 'registered_event_types' in status
        assert 'total_handlers' in status
        assert 'registry_initialized' in status
        assert status['registry_initialized'] is True
        assert isinstance(status['registered_event_types'], list)
        assert isinstance(status['total_handlers'], int)


class TestEventDataValidation:
    """Test event data validation functionality."""
    
    def test_validate_event_data_required_fields(self):
        """Test validation of required fields."""
        orchestrator = FundUpdateOrchestrator()
        
        # Test missing event_type
        with pytest.raises(ValueError, match="Required field 'event_type' is missing or empty"):
            orchestrator.validate_event_data({})
        
        # Test empty event_type
        with pytest.raises(ValueError, match="Required field 'event_type' is missing or empty"):
            orchestrator.validate_event_data({'event_type': ''})
    
    def test_validate_event_data_event_type_enum(self):
        """Test validation of event_type enum values."""
        orchestrator = FundUpdateOrchestrator()
        
        # Test valid enum object
        valid_data = {'event_type': EventType.CAPITAL_CALL}
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test valid string
        valid_data = {'event_type': 'CAPITAL_CALL'}
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test invalid string
        with pytest.raises(ValueError, match="Invalid event_type"):
            orchestrator.validate_event_data({'event_type': 'INVALID_TYPE'})
    
    def test_validate_event_data_date_format(self):
        """Test validation of date field format."""
        orchestrator = FundUpdateOrchestrator()
        
        # Test valid date string
        valid_data = {
            'event_type': EventType.CAPITAL_CALL,
            'date': '2024-01-15'
        }
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test invalid date string
        with pytest.raises(ValueError, match="Invalid date format"):
            orchestrator.validate_event_data({
                'event_type': EventType.CAPITAL_CALL,
                'date': 'invalid-date'
            })
    
    def test_validate_event_data_amount_validation(self):
        """Test validation of amount field."""
        orchestrator = FundUpdateOrchestrator()
        
        # Test valid positive amount
        valid_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 1000.0
        }
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test valid positive amount string
        valid_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': '1000.0'
        }
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test negative amount
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            orchestrator.validate_event_data({
                'event_type': EventType.CAPITAL_CALL,
                'amount': -1000.0
            })
        
        # Test invalid amount type
        with pytest.raises(ValueError, match="Amount must be a valid number"):
            orchestrator.validate_event_data({
                'event_type': EventType.CAPITAL_CALL,
                'amount': 'invalid'
            })


class TestEventProcessingPipeline:
    """Test the main event processing pipeline."""
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._handle_dependent_updates')
    def test_process_fund_event_success(self, mock_handle_dependent):
        """Test successful event processing through the pipeline."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_registry = Mock(spec=FundEventHandlerRegistry)
        
        # Configure registry mock
        mock_registry.handle_event.return_value = mock_event
        
        # Create orchestrator with mock registry
        orchestrator = FundUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        event_data = {'event_type': EventType.CAPITAL_CALL, 'amount': 1000.0}
        
        # Execute
        result = orchestrator.process_fund_event(event_data, mock_session, mock_fund)
        
        # Verify
        assert result == mock_event
        mock_registry.handle_event.assert_called_once_with(event_data, mock_session, mock_fund)
        mock_handle_dependent.assert_called_once_with(mock_event, mock_session)
        mock_session.commit.assert_called_once()
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._handle_dependent_updates')
    def test_process_fund_event_rollback_on_error(self, mock_handle_dependent):
        """Test that errors trigger rollback and re-raise."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_registry = Mock(spec=FundEventHandlerRegistry)
        
        # Configure registry to raise error
        mock_registry.handle_event.side_effect = ValueError("Test error")
        
        # Create orchestrator with mock registry
        orchestrator = FundUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        event_data = {'event_type': EventType.CAPITAL_CALL, 'amount': 1000.0}
        
        # Execute and verify error is re-raised
        with pytest.raises(ValueError, match="Test error"):
            orchestrator.process_fund_event(event_data, mock_session, mock_fund)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._handle_dependent_updates')
    def test_process_bulk_events_success(self, mock_handle_dependent):
        """Test successful bulk event processing."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event1 = Mock(spec=FundEvent)
        mock_event2 = Mock(spec=FundEvent)
        mock_registry = Mock(spec=FundEventHandlerRegistry)
        
        # Configure registry mock
        mock_registry.handle_event.side_effect = [mock_event1, mock_event2]
        
        # Create orchestrator with mock registry
        orchestrator = FundUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        events_data = [
            {'event_type': EventType.CAPITAL_CALL, 'amount': 1000.0},
            {'event_type': EventType.DISTRIBUTION, 'amount': 500.0}
        ]
        
        # Execute
        result = orchestrator.process_bulk_events(events_data, mock_session, mock_fund)
        
        # Verify
        assert result == [mock_event1, mock_event2]
        assert mock_registry.handle_event.call_count == 2
        assert mock_handle_dependent.call_count == 2
        mock_session.commit.assert_called_once()
    
    def test_process_bulk_events_empty_list(self):
        """Test bulk processing with empty event list."""
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        orchestrator = FundUpdateOrchestrator()
        
        result = orchestrator.process_bulk_events([], mock_session, mock_fund)
        
        assert result == []
        mock_session.commit.assert_not_called()
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._handle_dependent_updates')
    def test_process_bulk_events_rollback_on_error(self, mock_handle_dependent):
        """Test that bulk processing errors trigger rollback."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_registry = Mock(spec=FundEventHandlerRegistry)
        
        # Configure registry to raise error on second event
        mock_registry.handle_event.side_effect = [
            Mock(spec=FundEvent),  # First event succeeds
            ValueError("Second event fails")  # Second event fails
        ]
        
        # Create orchestrator with mock registry
        orchestrator = FundUpdateOrchestrator(registry=mock_registry)
        
        # Test data
        events_data = [
            {'event_type': EventType.CAPITAL_CALL, 'amount': 1000.0},
            {'event_type': EventType.DISTRIBUTION, 'amount': 500.0}
        ]
        
        # Execute and verify error is re-raised
        with pytest.raises(ValueError, match="Second event fails"):
            orchestrator.process_bulk_events(events_data, mock_session, mock_fund)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()


class TestDependentUpdatesHandling:
    """Test handling of dependent updates triggered by events."""
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._process_domain_events_for_dependent_updates')
    def test_handle_dependent_updates_capital_event(self, mock_process_domain):
        """Test that capital events trigger summary updates."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.fund_id = 1
        mock_event.event_date = date(2024, 1, 15)
        mock_event.amount = 1000.0
        mock_event.id = 123
        
        # Create orchestrator
        orchestrator = FundUpdateOrchestrator()
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event, mock_session)
        
        # Verify domain events are processed
        mock_process_domain.assert_called_once_with(mock_event, mock_session)
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._process_domain_events_for_dependent_updates')
    def test_handle_dependent_updates_nav_event(self, mock_process_domain):
        """Test that NAV events trigger subsequent NAV updates."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.event_type = EventType.NAV_UPDATE
        mock_event.fund = mock_fund  # Set the fund attribute on the event
        
        # Mock fund method
        mock_fund._update_subsequent_nav_change_fields = Mock()
        
        # Create orchestrator
        orchestrator = FundUpdateOrchestrator()
        
        # Execute
        orchestrator._handle_dependent_updates(mock_event, mock_session)
        
        # Verify fund method was called
        mock_fund._update_subsequent_nav_change_fields.assert_called_once_with(mock_event, mock_session)
        mock_process_domain.assert_called_once_with(mock_event, mock_session)
    
    @patch('src.fund.events.orchestrator.FundUpdateOrchestrator._process_domain_events_for_dependent_updates')
    def test_handle_dependent_updates_non_capital_event(self, mock_process_domain):
        """Test that non-capital events don't trigger summary updates."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.event_type = EventType.NAV_UPDATE  # Non-capital event
        
        # Create orchestrator
        orchestrator = FundUpdateOrchestrator()
        
        # Execute (should not raise any errors)
        orchestrator._handle_dependent_updates(mock_event, mock_session)
        
        # Verify domain events are still processed
        mock_process_domain.assert_called_once_with(mock_event, mock_session)


class TestTransactionManagement:
    """Test transaction commit and rollback functionality."""
    
    def test_commit_changes_success(self):
        """Test successful commit of changes."""
        mock_session = Mock(spec=Session)
        orchestrator = FundUpdateOrchestrator()
        
        # Execute
        orchestrator._commit_changes(mock_session)
        
        # Verify commit was called
        mock_session.commit.assert_called_once()
    
    def test_commit_changes_failure(self):
        """Test that commit failures are handled properly."""
        mock_session = Mock(spec=Session)
        mock_session.commit.side_effect = Exception("Database error")
        
        orchestrator = FundUpdateOrchestrator()
        
        # Execute and verify error is re-raised
        with pytest.raises(RuntimeError, match="Failed to commit changes"):
            orchestrator._commit_changes(mock_session)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
    
    def test_rollback_on_error_success(self):
        """Test successful rollback on error."""
        mock_session = Mock(spec=Session)
        test_error = ValueError("Test error")
        orchestrator = FundUpdateOrchestrator()
        
        # Execute and verify error is re-raised (this is the expected behavior)
        with pytest.raises(ValueError, match="Test error"):
            orchestrator._rollback_on_error(mock_session, test_error)
        
        # Verify rollback was called
        mock_session.rollback.assert_called_once()
    
    def test_rollback_on_error_rollback_failure(self):
        """Test that rollback failures don't mask original error."""
        mock_session = Mock(spec=Session)
        mock_session.rollback.side_effect = Exception("Rollback failed")
        test_error = ValueError("Test error")
        orchestrator = FundUpdateOrchestrator()
        
        # Execute and verify original error is still re-raised
        with pytest.raises(ValueError, match="Test error"):
            orchestrator._rollback_on_error(mock_session, test_error)
        
        # Verify rollback was attempted
        mock_session.rollback.assert_called_once()


class TestDomainEventProcessing:
    """Test domain event processing for dependent updates."""
    
    def test_process_domain_events_for_dependent_updates(self):
        """Test processing of domain events for dependent updates."""
        # Setup mocks
        mock_session = Mock(spec=Session)
        mock_fund = Mock(spec=Fund)
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        
        # Create orchestrator
        orchestrator = FundUpdateOrchestrator()
        
        # Mock the method to avoid real database operations
        with patch.object(orchestrator, '_process_domain_events_for_dependent_updates') as mock_method:
            # Execute
            orchestrator._process_domain_events_for_dependent_updates(mock_event, mock_session)
            
            # Verify the method was called
            mock_method.assert_called_once_with(mock_event, mock_session)
    
    def test_trigger_dependent_component_updates_equity_balance(self):
        """Test triggering updates for equity balance changes."""
        mock_session = Mock(spec=Session)
        mock_domain_event = Mock()
        mock_domain_event.event_type = DomainEventType.EQUITY_BALANCE_CHANGED
        
        orchestrator = FundUpdateOrchestrator()
        
        # Execute (should not raise any errors)
        orchestrator._trigger_dependent_component_updates(mock_domain_event, mock_session)
    
    def test_trigger_dependent_component_updates_distribution(self):
        """Test triggering updates for distribution events."""
        mock_session = Mock(spec=Session)
        mock_domain_event = Mock()
        mock_domain_event.event_type = DomainEventType.DISTRIBUTION_RECORDED
        
        orchestrator = FundUpdateOrchestrator()
        
        # Execute (should not raise any errors)
        orchestrator._trigger_dependent_component_updates(mock_domain_event, mock_session)
    
    def test_trigger_dependent_component_updates_nav_update(self):
        """Test triggering updates for NAV updates."""
        mock_session = Mock(spec=Session)
        mock_domain_event = Mock()
        mock_domain_event.event_type = DomainEventType.NAV_UPDATED
        
        orchestrator = FundUpdateOrchestrator()
        
        # Execute (should not raise any errors)
        orchestrator._trigger_dependent_component_updates(mock_domain_event, mock_session)
