"""
Test FundEventQueryRepository functionality.

This module tests the FundEventQueryRepository that provides
complex query operations for fund events.

Testing Focus:
- Complex event queries and filtering
- Event aggregations and calculations
- Search and filtering operations
- Cross-event type operations
- Data analysis operations
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

from src.fund.repositories.fund_event_query_repository import FundEventQueryRepository
from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, DistributionType, TaxPaymentType, GroupType


class TestFundEventQueryRepository:
    """Test the FundEventQueryRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create repository instance
        self.repository = FundEventQueryRepository(cache_ttl=300)
        
        # Create mock session
        self.mock_session = Mock(spec=Session)
        
        # Create mock fund events
        self.mock_event1 = Mock(spec=FundEvent)
        self.mock_event1.id = 1
        self.mock_event1.fund_id = 100
        self.mock_event1.event_type = EventType.CAPITAL_CALL
        self.mock_event1.event_date = date(2024, 1, 15)
        self.mock_event1.amount = 50000.0
        
        self.mock_event2 = Mock(spec=FundEvent)
        self.mock_event2.id = 2
        self.mock_event2.fund_id = 100
        self.mock_event2.event_type = EventType.DISTRIBUTION
        self.mock_event2.event_date = date(2024, 2, 15)
        self.mock_event2.amount = 10000.0
        self.mock_event2.tax_withholding = 2000.0
        self.mock_event2.distribution_type = DistributionType.INCOME
        
        self.mock_events = [self.mock_event1, self.mock_event2]
    
    # ============================================================================
    # EVENT QUERY METHODS
    # ============================================================================
    
    def test_get_events_by_type_success(self):
        """Test successful retrieval of events by type."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_event1]
        
        # Act
        result = self.repository.get_events_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == [self.mock_event1]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_events_by_type_caching(self):
        """Test that get_events_by_type uses caching."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_event1]
        
        # Act - First call
        result1 = self.repository.get_events_by_type(fund_id, event_type, self.mock_session)
        
        # Act - Second call (should use cache)
        result2 = self.repository.get_events_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result1 == result2
        # Query should only be called once due to caching
        self.mock_session.query.assert_called_once()
    
    def test_get_events_by_date_range_success(self):
        """Test successful retrieval of events by date range."""
        # Arrange
        fund_id = 100
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = self.mock_events
        
        # Act
        result = self.repository.get_events_by_date_range(fund_id, start_date, end_date, self.mock_session)
        
        # Assert
        assert result == self.mock_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_events_by_fund_and_type_success(self):
        """Test successful retrieval of events by fund and multiple types."""
        # Arrange
        fund_id = 100
        event_types = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = self.mock_events
        
        # Act
        result = self.repository.get_events_by_fund_and_type(fund_id, event_types, self.mock_session)
        
        # Assert
        assert result == self.mock_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_latest_event_by_type_success(self):
        """Test successful retrieval of latest event by type."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = self.mock_event1
        
        # Act
        result = self.repository.get_latest_event_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == self.mock_event1
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.first.assert_called_once()
    
    def test_get_latest_event_by_type_not_found(self):
        """Test retrieval of latest event by type when none exists."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act
        result = self.repository.get_latest_event_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result is None
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.first.assert_called_once()
    
    def test_get_events_after_date_success(self):
        """Test successful retrieval of events after a date."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        after_date = date(2024, 1, 1)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_event1]
        
        # Act
        result = self.repository.get_events_after_date(fund_id, event_type, after_date, self.mock_session)
        
        # Assert
        assert result == [self.mock_event1]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_events_before_date_success(self):
        """Test successful retrieval of events before a date."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        before_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_event1]
        
        # Act
        result = self.repository.get_events_before_date(fund_id, event_type, before_date, self.mock_session)
        
        # Assert
        assert result == [self.mock_event1]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_events_by_fund_and_types_ordered_success(self):
        """Test successful retrieval of events by fund and types with pagination."""
        # Arrange
        fund_id = 100
        event_types = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]
        skip = 0
        limit = 10
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_events
        
        # Act
        result = self.repository.get_events_by_fund_and_types_ordered(
            fund_id, event_types, self.mock_session, skip, limit
        )
        
        # Assert
        assert result == self.mock_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.all.assert_called_once()
    
    # ============================================================================
    # AGGREGATION METHODS
    # ============================================================================
    
    def test_get_total_by_type_success(self):
        """Test successful calculation of total by event type."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        expected_total = 50000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_by_type_zero_result(self):
        """Test calculation of total by event type when result is None."""
        # Arrange
        fund_id = 100
        event_type = EventType.CAPITAL_CALL
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_by_type(fund_id, event_type, self.mock_session)
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_tax_withheld_success(self):
        """Test successful calculation of total tax withheld."""
        # Arrange
        fund_id = 100
        expected_total = 2000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_tax_withheld(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_distributions_by_type_success(self):
        """Test successful calculation of distributions by type."""
        # Arrange
        fund_id = 100
        expected_distributions = {
            DistributionType.INCOME.value: 10000.0,
            DistributionType.CAPITAL_GAIN.value: 5000.0
        }
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_query
        mock_query.all.return_value = [
            (DistributionType.INCOME, 10000.0),
            (DistributionType.CAPITAL_GAIN, 5000.0)
        ]
        
        # Act
        result = self.repository.get_distributions_by_type(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_distributions
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.group_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_taxable_distributions_success(self):
        """Test successful calculation of taxable distributions."""
        # Arrange
        fund_id = 100
        expected_total = 10000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_taxable_distributions(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_event_count_by_fund_success(self):
        """Test successful calculation of event count by fund."""
        # Arrange
        fund_id = 100
        expected_count = 5
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_count
        
        # Act
        result = self.repository.get_event_count_by_fund(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_count
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_event_count_by_fund_zero_result(self):
        """Test calculation of event count when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_event_count_by_fund(fund_id, self.mock_session)
        
        # Assert
        assert result == 0
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
            f"fund:{fund_id}:type:capital_call": [self.mock_event1],
            f"fund:{fund_id}:type:distribution": [self.mock_event2],
            "fund:200:type:capital_call": [self.mock_event1],
            "other:key": "value"
        }
        
        # Act
        self.repository._clear_fund_cache(fund_id)
        
        # Assert
        expected_cache = {
            "fund:200:type:capital_call": [self.mock_event1],
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
        repository = FundEventQueryRepository()
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 300
    
    def test_repository_initialization_custom_ttl(self):
        """Test repository initialization with custom cache TTL."""
        # Act
        repository = FundEventQueryRepository(cache_ttl=600)
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 600
