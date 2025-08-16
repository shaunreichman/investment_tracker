"""
Test NewFundManager functionality.

This module tests the enhanced NewFundManager that provides
a comprehensive API for fund operations.
"""

import pytest
from datetime import date
from unittest.mock import Mock, MagicMock

from src.fund.new_fund_manager import NewFundManager
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType, EventType


class TestNewFundManager:
    """Test the NewFundManager class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create a mock fund
        self.mock_fund = Mock(spec=Fund)
        self.mock_fund.id = 1
        self.mock_fund.name = "Test Fund"
        self.mock_fund.status = FundStatus.ACTIVE
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.commitment_amount = 1000000.0
        self.mock_fund.current_equity_balance = 500000.0
        
        # Create the NewFundManager
        self.fund_manager = NewFundManager(self.mock_fund)
    
    def test_initialization(self):
        """Test NewFundManager initialization."""
        assert self.fund_manager.fund == self.mock_fund
        assert self.fund_manager.orchestrator is not None
    
    def test_is_active(self):
        """Test is_active method."""
        assert self.fund_manager.is_active() is True
        
        # Test inactive status
        self.mock_fund.status = FundStatus.COMPLETED
        assert self.fund_manager.is_active() is False
    
    def test_is_completed(self):
        """Test is_completed method."""
        assert self.fund_manager.is_completed() is False
        
        # Test completed status
        self.mock_fund.status = FundStatus.COMPLETED
        assert self.fund_manager.is_completed() is True
    
    def test_is_realized(self):
        """Test is_realized method."""
        assert self.fund_manager.is_realized() is False
        
        # Test realized status
        self.mock_fund.status = FundStatus.REALIZED
        assert self.fund_manager.is_realized() is True
    
    def test_has_equity_balance(self):
        """Test has_equity_balance method."""
        assert self.fund_manager.has_equity_balance() is True
        
        # Test no equity balance
        self.mock_fund.current_equity_balance = 0.0
        assert self.fund_manager.has_equity_balance() is False
    
    def test_get_commitment_utilization(self):
        """Test get_commitment_utilization method."""
        utilization = self.fund_manager.get_commitment_utilization()
        assert utilization == 50.0  # 500k / 1M = 50%
        
        # Test no commitment amount
        self.mock_fund.commitment_amount = None
        assert self.fund_manager.get_commitment_utilization() == 0.0
    
    def test_get_remaining_commitment(self):
        """Test get_remaining_commitment method."""
        remaining = self.fund_manager.get_remaining_commitment()
        assert remaining == 500000.0  # 1M - 500k = 500k
        
        # Test no commitment amount
        self.mock_fund.commitment_amount = None
        assert self.fund_manager.get_remaining_commitment() == 0.0
    
    def test_method_count(self):
        """Test that NewFundManager has the expected number of methods."""
        # Count public methods (excluding private methods starting with _)
        public_methods = [
            method for method in dir(self.fund_manager) 
            if callable(getattr(self.fund_manager, method)) 
            and not method.startswith('_')
            and method not in ['orchestrator', 'fund']  # Exclude attributes
        ]
        
        # We expect at least 35+ methods based on our implementation
        assert len(public_methods) >= 35, f"Expected at least 35 methods, got {len(public_methods)}"
        
        # Verify key method categories exist
        method_names = [method for method in public_methods]
        
        # Core event methods
        assert 'add_capital_call' in method_names
        assert 'add_distribution' in method_names
        assert 'add_nav_update' in method_names
        
        # Calculation methods
        assert 'calculate_irr' in method_names
        assert 'calculate_average_equity_balance' in method_names
        
        # Status methods
        assert 'get_summary_data' in method_names
        assert 'update_status' in method_names
        
        # Query methods
        assert 'get_recent_events' in method_names
        assert 'get_all_fund_events' in method_names
        
        # Utility methods
        assert 'is_active' in method_names
        assert 'has_equity_balance' in method_names
        assert 'get_commitment_utilization' in method_names
    
    def test_orchestrator_integration(self):
        """Test that methods are properly routed to orchestrator."""
        # Mock the orchestrator services
        mock_calculation_service = Mock()
        mock_status_service = Mock()
        mock_event_service = Mock()
        mock_tax_service = Mock()
        
        self.fund_manager.orchestrator.calculation_service = mock_calculation_service
        self.fund_manager.orchestrator.status_service = mock_status_service
        self.fund_manager.orchestrator.event_service = mock_event_service
        self.fund_manager.orchestrator.tax_service = mock_tax_service
        
        # Test calculation method routing
        self.fund_manager.calculate_irr()
        mock_calculation_service.calculate_irr.assert_called_once_with(
            fund=self.mock_fund, session=None
        )
        
        # Test status method routing
        self.fund_manager.get_summary_data()
        mock_status_service.get_summary_data.assert_called_once_with(
            fund=self.mock_fund, session=None
        )
        
        # Test event method routing
        self.fund_manager.get_recent_events()
        mock_event_service.get_recent_events.assert_called_once_with(
            fund=self.mock_fund, limit=10, exclude_system_events=True, session=None
        )
        
        # Test tax method routing
        self.fund_manager.get_total_distributions()
        mock_tax_service.get_total_distributions.assert_called_once_with(
            fund=self.mock_fund, session=None
        )
