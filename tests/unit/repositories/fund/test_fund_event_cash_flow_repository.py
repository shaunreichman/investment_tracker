"""
Test FundEventCashFlowRepository functionality.

This module tests the FundEventCashFlowRepository that provides
data access operations for FundEventCashFlow entities.

Testing Focus:
- Bank account relationship queries (used by banking services)
- Cash flow counting and existence checks
- Basic CRUD operations
- Caching behavior

Testing Approach: Mock-Based Testing (Unit Tests)
- Use mocks for database session and query results
- Test repository logic in isolation
- Focus on methods used by banking services
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session

from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from src.fund.models import FundEventCashFlow
from src.fund.enums import CashFlowDirection


class TestFundEventCashFlowRepository:
    """Test cases for FundEventCashFlowRepository."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.repository = FundEventCashFlowRepository()
        self.mock_session = Mock(spec=Session)
        self.mock_query = Mock()
        self.mock_session.query.return_value = self.mock_query
        
        # Sample cash flow data
        self.sample_cash_flow = FundEventCashFlow(
            id=1,
            fund_event_id=100,
            bank_account_id=200,
            direction=CashFlowDirection.INFLOW,
            transfer_date=date(2024, 1, 15),
            currency="USD",
            amount=1000.0,
            reference="TEST-REF-001",
            description="Test cash flow"
        )
    
    def test_count_by_bank_account_returns_count(self):
        """Test count_by_bank_account returns correct count."""
        # Arrange
        bank_account_id = 200
        expected_count = 3
        self.mock_query.filter.return_value.count.return_value = expected_count
        
        # Act
        result = self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert result == expected_count
        self.mock_session.query.assert_called_once_with(FundEventCashFlow)
        self.mock_query.filter.assert_called_once()
        self.mock_query.filter.return_value.count.assert_called_once()
    
    def test_count_by_bank_account_uses_cache(self):
        """Test count_by_bank_account uses cache on second call."""
        # Arrange
        bank_account_id = 200
        expected_count = 5
        self.mock_query.filter.return_value.count.return_value = expected_count
        
        # Act - First call
        result1 = self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        # Second call should use cache
        result2 = self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert result1 == expected_count
        assert result2 == expected_count
        # Should only query database once due to caching
        self.mock_session.query.assert_called_once()
    
    def test_has_cash_flows_for_bank_account_returns_true_when_exists(self):
        """Test has_cash_flows_for_bank_account returns True when cash flows exist."""
        # Arrange
        bank_account_id = 200
        self.mock_query.filter.return_value.count.return_value = 2  # Non-zero count
        
        # Act
        result = self.repository.has_cash_flows_for_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert result is True
        self.mock_session.query.assert_called_once_with(FundEventCashFlow)
    
    def test_has_cash_flows_for_bank_account_returns_false_when_none(self):
        """Test has_cash_flows_for_bank_account returns False when no cash flows exist."""
        # Arrange
        bank_account_id = 200
        self.mock_query.filter.return_value.count.return_value = 0  # Zero count
        
        # Act
        result = self.repository.has_cash_flows_for_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert result is False
    
    def test_get_by_bank_account_returns_cash_flows(self):
        """Test get_by_bank_account returns list of cash flows."""
        # Arrange
        bank_account_id = 200
        expected_cash_flows = [self.sample_cash_flow]
        self.mock_query.filter.return_value.order_by.return_value.all.return_value = expected_cash_flows
        
        # Act
        result = self.repository.get_by_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert result == expected_cash_flows
        self.mock_session.query.assert_called_once_with(FundEventCashFlow)
        self.mock_query.filter.assert_called_once()
        self.mock_query.filter.return_value.order_by.assert_called_once()
    
    def test_get_by_id_returns_cash_flow(self):
        """Test get_by_id returns correct cash flow."""
        # Arrange
        cash_flow_id = 1
        self.mock_query.filter.return_value.first.return_value = self.sample_cash_flow
        
        # Act
        result = self.repository.get_by_id(cash_flow_id, self.mock_session)
        
        # Assert
        assert result == self.sample_cash_flow
        self.mock_session.query.assert_called_once_with(FundEventCashFlow)
        self.mock_query.filter.assert_called_once()
    
    def test_get_by_id_returns_none_when_not_found(self):
        """Test get_by_id returns None when cash flow not found."""
        # Arrange
        cash_flow_id = 999
        self.mock_query.filter.return_value.first.return_value = None
        
        # Act
        result = self.repository.get_by_id(cash_flow_id, self.mock_session)
        
        # Assert
        assert result is None
    
    def test_create_adds_cash_flow_to_session(self):
        """Test create adds cash flow to session and flushes."""
        # Arrange
        cash_flow = self.sample_cash_flow
        
        # Act
        result = self.repository.create(cash_flow, self.mock_session)
        
        # Assert
        assert result == cash_flow
        self.mock_session.add.assert_called_once_with(cash_flow)
        self.mock_session.flush.assert_called_once()
    
    def test_count_by_bank_account_clears_cache_after_create(self):
        """Test count_by_bank_account cache is cleared after create operation."""
        # Arrange
        bank_account_id = 200
        cash_flow = self.sample_cash_flow
        cash_flow.bank_account_id = bank_account_id
        
        # Mock the count method to track calls
        self.mock_query.filter.return_value.count.return_value = 1
        
        # Act - First call to populate cache
        count1 = self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        # Create operation should clear cache
        self.repository.create(cash_flow, self.mock_session)
        # Second call should hit database again (cache cleared)
        count2 = self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        
        # Assert
        assert count1 == 1
        assert count2 == 1
        # Should query database twice (once before create, once after)
        assert self.mock_session.query.call_count == 2
    
    def test_get_by_fund_event_returns_cash_flows(self):
        """Test get_by_fund_event returns cash flows for fund event."""
        # Arrange
        fund_event_id = 100
        expected_cash_flows = [self.sample_cash_flow]
        self.mock_query.filter.return_value.all.return_value = expected_cash_flows
        
        # Act
        result = self.repository.get_by_fund_event(fund_event_id, self.mock_session)
        
        # Assert
        assert result == expected_cash_flows
        self.mock_session.query.assert_called_once_with(FundEventCashFlow)
        self.mock_query.filter.assert_called_once()
    
    def test_clear_cache_clears_all_caches(self):
        """Test clear_cache removes all cached data."""
        # Arrange
        bank_account_id = 200
        self.mock_query.filter.return_value.count.return_value = 5
        
        # Act - Populate cache
        self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        # Clear cache
        self.repository.clear_cache()
        # Call again - should hit database
        self.repository.count_by_bank_account(bank_account_id, self.mock_session)
        
        # Assert - Should query database twice (before and after clear)
        assert self.mock_session.query.call_count == 2
