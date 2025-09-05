"""
Test CapitalEventRepository functionality.

This module tests the CapitalEventRepository that provides
data access operations for capital-related fund events.

Testing Focus:
- Capital event CRUD operations
- Capital event querying and filtering
- Capital event aggregations
- Data persistence operations
- Caching behavior and invalidation

Testing Approach: Mock-Based Testing (Unit Tests)
- Use mocks for database session and query results
- Test repository logic in isolation
- Focus on data access patterns and validation
- Validate caching behavior and performance
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, func

from src.fund.repositories.capital_event_repository import CapitalEventRepository
from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, DistributionType, TaxPaymentType, GroupType


class TestCapitalEventRepository:
    """Test the CapitalEventRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create repository instance
        self.repository = CapitalEventRepository(cache_ttl=300)
        
        # Create mock session
        self.mock_session = Mock(spec=Session)
        
        # Create mock capital events
        self.mock_capital_call = Mock(spec=FundEvent)
        self.mock_capital_call.id = 1
        self.mock_capital_call.fund_id = 100
        self.mock_capital_call.event_type = EventType.CAPITAL_CALL
        self.mock_capital_call.event_date = date(2024, 1, 15)
        self.mock_capital_call.amount = 100000.0
        
        self.mock_return_of_capital = Mock(spec=FundEvent)
        self.mock_return_of_capital.id = 2
        self.mock_return_of_capital.fund_id = 100
        self.mock_return_of_capital.event_type = EventType.RETURN_OF_CAPITAL
        self.mock_return_of_capital.event_date = date(2024, 6, 15)
        self.mock_return_of_capital.amount = 50000.0
        
        self.mock_capital_events = [self.mock_capital_call, self.mock_return_of_capital]
    
    # ============================================================================
    # CREATE METHODS
    # ============================================================================
    
    def test_create_capital_call_success(self):
        """Test successful creation of capital call event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 1, 15),
            'amount': 100000.0,
            'description': 'Capital call'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.capital_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_capital_call
            result = self.repository.create_capital_call(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_capital_call
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.CAPITAL_CALL
        assert event_data['fund_id'] == fund_id
    
    def test_create_return_of_capital_success(self):
        """Test successful creation of return of capital event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 6, 15),
            'amount': 50000.0,
            'description': 'Return of capital'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.capital_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_return_of_capital
            result = self.repository.create_return_of_capital(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_return_of_capital
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.RETURN_OF_CAPITAL
        assert event_data['fund_id'] == fund_id
    
    # ============================================================================
    # QUERY METHODS
    # ============================================================================
    
    def test_get_capital_events_success(self):
        """Test successful retrieval of capital events."""
        # Arrange
        fund_id = 100
        skip = 0
        limit = 10
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_capital_events
        
        # Act
        result = self.repository.get_capital_events(
            fund_id, self.mock_session, skip, limit, start_date, end_date
        )
        
        # Assert
        assert result == self.mock_capital_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.all.assert_called_once()
    
    def test_get_capital_events_caching(self):
        """Test that get_capital_events uses caching."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_capital_events
        
        # Act - First call
        result1 = self.repository.get_capital_events(fund_id, self.mock_session)
        
        # Act - Second call (should use cache)
        result2 = self.repository.get_capital_events(fund_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        # Query should only be called once due to caching
        self.mock_session.query.assert_called_once()
    
    def test_get_capital_events_by_date_range_success(self):
        """Test successful retrieval of capital events by date range."""
        # Arrange
        fund_id = 100
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = self.mock_capital_events
        
        # Act
        result = self.repository.get_capital_events_by_date_range(
            fund_id, start_date, end_date, self.mock_session
        )
        
        # Assert
        assert result == self.mock_capital_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    # ============================================================================
    # AGGREGATION METHODS
    # ============================================================================
    
    def test_get_total_capital_calls_success(self):
        """Test successful calculation of total capital calls."""
        # Arrange
        fund_id = 100
        expected_total = 100000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_capital_calls(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_capital_calls_zero_result(self):
        """Test calculation of total capital calls when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_capital_calls(fund_id, self.mock_session)
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_capital_returns_success(self):
        """Test successful calculation of total capital returns."""
        # Arrange
        fund_id = 100
        expected_total = 50000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_capital_returns(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_capital_returns_zero_result(self):
        """Test calculation of total capital returns when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_capital_returns(fund_id, self.mock_session)
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    # ============================================================================
    # CACHE MANAGEMENT
    # ============================================================================
    
    def test_clear_fund_cache(self):
        """Test clearing cache for a specific fund."""
        # Arrange
        fund_id = 100
        
        # Add some cache entries
        self.repository._cache = {
            f"fund:{fund_id}:capital_events": self.mock_capital_events,
            f"fund:{fund_id}:total_capital_calls": 100000.0,
            "fund:200:capital_events": [self.mock_capital_call],
            "other:key": "value"
        }
        
        # Act
        self.repository._clear_fund_cache(fund_id)
        
        # Assert
        expected_cache = {
            "fund:200:capital_events": [self.mock_capital_call],
            "other:key": "value"
        }
        assert self.repository._cache == expected_cache
    
    def test_clear_all_cache(self):
        """Test clearing all cache entries."""
        # Arrange
        self.repository._cache = {
            "key1": "value1",
            "key2": "value2"
        }
        
        # Act
        self.repository.clear_all_cache()
        
        # Assert
        assert self.repository._cache == {}
    
    # ============================================================================
    # ERROR HANDLING
    # ============================================================================
    
    def test_repository_initialization(self):
        """Test repository initialization with default cache TTL."""
        # Act
        repository = CapitalEventRepository()
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 300
    
    def test_repository_initialization_custom_ttl(self):
        """Test repository initialization with custom cache TTL."""
        # Act
        repository = CapitalEventRepository(cache_ttl=600)
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 600
