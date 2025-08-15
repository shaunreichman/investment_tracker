"""
Test Event Handler Architecture.

This module tests the event handler architecture to ensure it works
correctly and maintains the expected contracts.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from src.fund.events import (
    BaseFundEventHandler,
    FundEventHandlerRegistry,
    FundUpdateOrchestrator
)
from src.fund.events.handlers import (
    CapitalCallHandler,
    ReturnOfCapitalHandler,
    DistributionHandler,
    NAVUpdateHandler,
    UnitPurchaseHandler,
    UnitSaleHandler
)
from src.fund.enums import EventType, FundType, DistributionType
from src.fund.models import Fund, FundEvent


class TestEventHandlerArchitecture:
    """Test the event handler architecture components."""
    
    def test_base_handler_initialization(self):
        """Test that base handler initializes correctly."""
        mock_session = Mock()
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Test that we can't instantiate the abstract base class
        with pytest.raises(TypeError):
            BaseFundEventHandler(mock_session, mock_fund)
    
    def test_capital_call_handler_initialization(self):
        """Test that capital call handler initializes correctly."""
        mock_session = Mock()
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        handler = CapitalCallHandler(mock_session, mock_fund)
        assert handler.session == mock_session
        assert handler.fund == mock_fund
        assert handler.calculation_service is not None
        assert handler.status_service is not None
        assert handler.tax_service is not None
    
    def test_registry_initialization(self):
        """Test that registry initializes with all handlers."""
        registry = FundEventHandlerRegistry()
        
        # Check that all expected handlers are registered
        assert registry.is_handler_registered(EventType.CAPITAL_CALL)
        assert registry.is_handler_registered(EventType.RETURN_OF_CAPITAL)
        assert registry.is_handler_registered(EventType.DISTRIBUTION)
        assert registry.is_handler_registered(EventType.NAV_UPDATE)
        assert registry.is_handler_registered(EventType.UNIT_PURCHASE)
        assert registry.is_handler_registered(EventType.UNIT_SALE)
        
        # Check total count
        assert len(registry.get_registered_event_types()) == 6
    
    def test_registry_get_handler(self):
        """Test that registry returns correct handler instances."""
        registry = FundEventHandlerRegistry()
        mock_session = Mock()
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Test getting capital call handler
        handler = registry.get_handler(EventType.CAPITAL_CALL, mock_session, mock_fund)
        assert isinstance(handler, CapitalCallHandler)
        
        # Test getting NAV update handler
        mock_fund.tracking_type = FundType.NAV_BASED
        handler = registry.get_handler(EventType.NAV_UPDATE, mock_session, mock_fund)
        assert isinstance(handler, NAVUpdateHandler)
    
    def test_registry_unknown_event_type(self):
        """Test that registry raises error for unknown event types."""
        registry = FundEventHandlerRegistry()
        mock_session = Mock()
        mock_fund = Mock()
        
        # Test with unregistered event type
        with pytest.raises(ValueError, match="No handler registered for event type"):
            registry.get_handler(EventType.DAILY_RISK_FREE_INTEREST_CHARGE, mock_session, mock_fund)
    
    def test_orchestrator_initialization(self):
        """Test that orchestrator initializes correctly."""
        orchestrator = FundUpdateOrchestrator()
        assert orchestrator.registry is not None
        assert isinstance(orchestrator.registry, FundEventHandlerRegistry)
    
    def test_orchestrator_with_custom_registry(self):
        """Test that orchestrator can use custom registry."""
        custom_registry = FundEventHandlerRegistry()
        orchestrator = FundUpdateOrchestrator(custom_registry)
        assert orchestrator.registry == custom_registry
    
    def test_orchestrator_validate_event_data(self):
        """Test that orchestrator validates event data correctly."""
        orchestrator = FundUpdateOrchestrator()
        
        # Test valid event data
        valid_data = {
            'event_type': 'CAPITAL_CALL',
            'amount': 1000.0,
            'date': '2024-01-15'
        }
        assert orchestrator.validate_event_data(valid_data) is True
        
        # Test missing event_type
        invalid_data = {'amount': 1000.0, 'date': '2024-01-15'}
        with pytest.raises(ValueError, match="Required field 'event_type' is missing"):
            orchestrator.validate_event_data(invalid_data)
        
        # Test invalid event_type
        invalid_data = {'event_type': 'invalid_type', 'amount': 1000.0, 'date': '2024-01-15'}
        with pytest.raises(ValueError, match="Invalid event_type"):
            orchestrator.validate_event_data(invalid_data)
        
        # Test invalid date format
        invalid_data = {'event_type': 'CAPITAL_CALL', 'amount': 1000.0, 'date': 'invalid-date'}
        with pytest.raises(ValueError, match="Invalid date format"):
            orchestrator.validate_event_data(invalid_data)
        
        # Test negative amount
        invalid_data = {'event_type': 'CAPITAL_CALL', 'amount': -1000.0, 'date': '2024-01-15'}
        with pytest.raises(ValueError, match="Amount cannot be negative"):
            orchestrator.validate_event_data(invalid_data)
    
    def test_registry_status(self):
        """Test that orchestrator provides registry status."""
        orchestrator = FundUpdateOrchestrator()
        status = orchestrator.get_registry_status()
        
        assert 'registered_event_types' in status
        assert 'total_handlers' in status
        assert 'registry_initialized' in status
        assert status['total_handlers'] == 6
        assert status['registry_initialized'] is True
        assert len(status['registered_event_types']) == 6


class TestCapitalCallHandler:
    """Test the capital call handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.id = 1
        
        self.handler = CapitalCallHandler(self.mock_session, self.mock_fund)
    
    def test_validate_event_cost_based_fund(self):
        """Test validation for cost-based funds."""
        event_data = {
            'amount': 1000.0,
            'date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation rejects NAV-based funds."""
        self.mock_fund.tracking_type = FundType.NAV_BASED
        
        event_data = {
            'amount': 1000.0,
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires COST_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_amount(self):
        """Test validation rejects missing amount."""
        event_data = {
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'amount': 1000.0
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_amount(self):
        """Test validation rejects invalid amount."""
        event_data = {
            'amount': 'invalid',
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)


class TestNAVUpdateHandler:
    """Test the NAV update handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.NAV_BASED
        self.mock_fund.id = 1
        
        self.handler = NAVUpdateHandler(self.mock_session, self.mock_fund)
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation for NAV-based funds."""
        event_data = {
            'nav_per_share': 10.50,
            'date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_cost_based_fund(self):
        """Test validation rejects cost-based funds."""
        self.mock_fund.tracking_type = FundType.COST_BASED
        
        event_data = {
            'nav_per_share': 10.50,
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_nav(self):
        """Test validation rejects missing NAV."""
        event_data = {
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_nav(self):
        """Test validation rejects invalid NAV."""
        event_data = {
            'nav_per_share': 'invalid',
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_nav(self):
        """Test validation rejects negative NAV."""
        event_data = {
            'nav_per_share': -10.50,
            'date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share must be a valid positive number"):
            self.handler.validate_event(event_data)
