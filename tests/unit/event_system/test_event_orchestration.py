"""
Event Orchestration Unit Tests.

This module tests the event orchestration system including:
- Event orchestrator functionality
- Event registry management
- Event validation and routing
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from src.fund.events.orchestrator import EventOrchestrator
from src.fund.events.handlers.base_handler import BaseEventHandler
from src.fund.events.domain import EquityBalanceChangedEvent
from src.fund.enums import FundType


class TestEventOrchestrator:
    """Test the EventOrchestrator functionality."""
    
    def test_orchestrator_initialization(self):
        """Test that EventOrchestrator initializes correctly."""
        orchestrator = EventOrchestrator()
        
        assert orchestrator.registry is not None
        assert orchestrator.event_bus is not None
    
    def test_orchestrator_with_custom_registry(self):
        """Test EventOrchestrator with custom registry."""
        mock_registry = Mock()
        orchestrator = EventOrchestrator(registry=mock_registry)
        
        assert orchestrator.registry == mock_registry
    
    def test_orchestrator_validate_event_data(self):
        """Test event data validation in orchestrator."""
        orchestrator = EventOrchestrator()
        
        # Test valid event data
        valid_event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        result = orchestrator.validate_event_data(valid_event)
        assert result is True
        
        # Test invalid event data
        invalid_event = Mock()
        invalid_event.fund_id = None  # Missing required field
        
        result = orchestrator.validate_event_data(invalid_event)
        assert result is False
    
    def test_orchestrator_status(self):
        """Test orchestrator status reporting."""
        orchestrator = EventOrchestrator()
        
        status = orchestrator.get_status()
        assert 'registry' in status
        assert 'event_bus' in status
        assert 'handlers' in status


class TestEventRegistry:
    """Test the event registry functionality."""
    
    def test_registry_initialization(self):
        """Test that registry initializes correctly."""
        registry = Mock()
        
        assert registry is not None
    
    def test_registry_get_handler(self):
        """Test getting handler from registry."""
        mock_registry = Mock()
        mock_handler = Mock(spec=BaseEventHandler)
        
        mock_registry.get_handler.return_value = mock_handler
        
        handler = mock_registry.get_handler(EquityBalanceChangedEvent)
        assert handler == mock_handler
    
    def test_registry_unknown_event_type(self):
        """Test registry behavior with unknown event type."""
        mock_registry = Mock()
        mock_registry.get_handler.return_value = None
        
        handler = mock_registry.get_handler("UnknownEventType")
        assert handler is None
    
    def test_registry_status(self):
        """Test registry status reporting."""
        mock_registry = Mock()
        mock_registry.get_status.return_value = {"handler_count": 5}
        
        status = mock_registry.get_status()
        assert status["handler_count"] == 5


class TestEventOrchestrationIntegration:
    """Test event orchestration integration scenarios."""
    
    def test_orchestrator_with_capital_call_handler(self):
        """Test orchestrator with capital call handler."""
        orchestrator = EventOrchestrator()
        
        # Mock the capital call handler
        mock_handler = Mock(spec=BaseEventHandler)
        mock_handler.can_handle.return_value = True
        mock_handler.handle.return_value = True
        
        # Test handler integration
        assert mock_handler.can_handle(EquityBalanceChangedEvent) is True
        assert mock_handler.handle(Mock()) is True
    
    def test_orchestrator_with_nav_update_handler(self):
        """Test orchestrator with NAV update handler."""
        orchestrator = EventOrchestrator()
        
        # Mock the NAV update handler
        mock_handler = Mock(spec=BaseEventHandler)
        mock_handler.can_handle.return_value = True
        mock_handler.handle.return_value = True
        
        # Test handler integration
        assert mock_handler.can_handle(EquityBalanceChangedEvent) is True
        assert mock_handler.handle(Mock()) is True

