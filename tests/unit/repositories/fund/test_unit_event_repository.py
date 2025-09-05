"""
Test UnitEventRepository functionality.

This module tests the UnitEventRepository that provides
data access operations for unit-related fund events.

Testing Focus:
- Unit event CRUD operations
- Unit event querying and filtering
- Unit event aggregations
- NAV update operations
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

from src.fund.repositories.unit_event_repository import UnitEventRepository
from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, DistributionType, TaxPaymentType, GroupType


class TestUnitEventRepository:
    """Test the UnitEventRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create repository instance
        self.repository = UnitEventRepository(cache_ttl=300)
        
        # Create mock session
        self.mock_session = Mock(spec=Session)
        
        # Create mock unit events
        self.mock_unit_purchase = Mock(spec=FundEvent)
        self.mock_unit_purchase.id = 1
        self.mock_unit_purchase.fund_id = 100
        self.mock_unit_purchase.event_type = EventType.UNIT_PURCHASE
        self.mock_unit_purchase.event_date = date(2024, 1, 15)
        self.mock_unit_purchase.amount = 50000.0
        
        self.mock_unit_sale = Mock(spec=FundEvent)
        self.mock_unit_sale.id = 2
        self.mock_unit_sale.fund_id = 100
        self.mock_unit_sale.event_type = EventType.UNIT_SALE
        self.mock_unit_sale.event_date = date(2024, 6, 15)
        self.mock_unit_sale.amount = 25000.0
        
        self.mock_nav_update = Mock(spec=FundEvent)
        self.mock_nav_update.id = 3
        self.mock_nav_update.fund_id = 100
        self.mock_nav_update.event_type = EventType.NAV_UPDATE
        self.mock_nav_update.event_date = date(2024, 3, 15)
        self.mock_nav_update.amount = 1.25  # NAV value
        
        self.mock_unit_events = [self.mock_unit_purchase, self.mock_unit_sale, self.mock_nav_update]
    
    # ============================================================================
    # CREATE METHODS
    # ============================================================================
    
    def test_create_unit_purchase_success(self):
        """Test successful creation of unit purchase event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 1, 15),
            'amount': 50000.0,
            'description': 'Unit purchase'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.unit_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_unit_purchase
            result = self.repository.create_unit_purchase(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_unit_purchase
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.UNIT_PURCHASE
        assert event_data['fund_id'] == fund_id
    
    def test_create_unit_sale_success(self):
        """Test successful creation of unit sale event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 6, 15),
            'amount': 25000.0,
            'description': 'Unit sale'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.unit_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_unit_sale
            result = self.repository.create_unit_sale(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_unit_sale
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.UNIT_SALE
        assert event_data['fund_id'] == fund_id
    
    def test_create_nav_update_success(self):
        """Test successful creation of NAV update event."""
        # Arrange
        fund_id = 100
        event_data = {
            'event_date': date(2024, 3, 15),
            'amount': 1.25,
            'description': 'NAV update'
        }
        
        # Mock session operations
        self.mock_session.add = Mock()
        self.mock_session.flush = Mock()
        
        # Act
        with patch('src.fund.repositories.unit_event_repository.FundEvent') as mock_fund_event_class:
            mock_fund_event_class.return_value = self.mock_nav_update
            result = self.repository.create_nav_update(fund_id, event_data, self.mock_session)
        
        # Assert
        assert result == self.mock_nav_update
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        
        # Verify event_data was modified correctly
        assert event_data['event_type'] == EventType.NAV_UPDATE
        assert event_data['fund_id'] == fund_id
    
    # ============================================================================
    # QUERY METHODS
    # ============================================================================
    
    def test_get_unit_events_success(self):
        """Test successful retrieval of unit events."""
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
        mock_query.all.return_value = self.mock_unit_events
        
        # Act
        result = self.repository.get_unit_events(
            fund_id, self.mock_session, skip, limit, start_date, end_date
        )
        
        # Assert
        assert result == self.mock_unit_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.offset.assert_called_once_with(skip)
        mock_query.limit.assert_called_once_with(limit)
        mock_query.all.assert_called_once()
    
    def test_get_unit_events_caching(self):
        """Test that get_unit_events uses caching."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = self.mock_unit_events
        
        # Act - First call
        result1 = self.repository.get_unit_events(fund_id, self.mock_session)
        
        # Act - Second call (should use cache)
        result2 = self.repository.get_unit_events(fund_id, self.mock_session)
        
        # Assert
        assert result1 == result2
        # Query should only be called once due to caching
        self.mock_session.query.assert_called_once()
    
    def test_get_unit_events_by_date_range_success(self):
        """Test successful retrieval of unit events by date range."""
        # Arrange
        fund_id = 100
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = self.mock_unit_events
        
        # Act
        result = self.repository.get_unit_events_by_date_range(
            fund_id, start_date, end_date, self.mock_session
        )
        
        # Assert
        assert result == self.mock_unit_events
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    # ============================================================================
    # NAV-SPECIFIC METHODS
    # ============================================================================
    
    def test_get_latest_nav_update_success(self):
        """Test successful retrieval of latest NAV update."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = self.mock_nav_update
        
        # Act
        result = self.repository.get_latest_nav_update(fund_id, self.mock_session)
        
        # Assert
        assert result == self.mock_nav_update
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.first.assert_called_once()
    
    def test_get_latest_nav_update_not_found(self):
        """Test retrieval of latest NAV update when none exists."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.first.return_value = None
        
        # Act
        result = self.repository.get_latest_nav_update(fund_id, self.mock_session)
        
        # Assert
        assert result is None
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.first.assert_called_once()
    
    def test_get_nav_events_before_date_success(self):
        """Test successful retrieval of NAV events before a date."""
        # Arrange
        fund_id = 100
        before_date = date(2024, 6, 1)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_nav_update]
        
        # Act
        result = self.repository.get_nav_events_before_date(fund_id, before_date, self.mock_session)
        
        # Assert
        assert result == [self.mock_nav_update]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    def test_get_nav_events_after_date_success(self):
        """Test successful retrieval of NAV events after a date."""
        # Arrange
        fund_id = 100
        after_date = date(2024, 1, 1)
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [self.mock_nav_update]
        
        # Act
        result = self.repository.get_nav_events_after_date(fund_id, after_date, self.mock_session)
        
        # Assert
        assert result == [self.mock_nav_update]
        self.mock_session.query.assert_called_once_with(FundEvent)
        mock_query.filter.assert_called()
        mock_query.order_by.assert_called_once()
        mock_query.all.assert_called_once()
    
    # ============================================================================
    # AGGREGATION METHODS
    # ============================================================================
    
    def test_get_total_unit_purchases_success(self):
        """Test successful calculation of total unit purchases."""
        # Arrange
        fund_id = 100
        expected_total = 50000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_unit_purchases(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_unit_purchases_zero_result(self):
        """Test calculation of total unit purchases when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_unit_purchases(fund_id, self.mock_session)
        
        # Assert
        assert result == 0.0
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_unit_sales_success(self):
        """Test successful calculation of total unit sales."""
        # Arrange
        fund_id = 100
        expected_total = 25000.0
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = expected_total
        
        # Act
        result = self.repository.get_total_unit_sales(fund_id, self.mock_session)
        
        # Assert
        assert result == expected_total
        self.mock_session.query.assert_called_once()
        mock_query.filter.assert_called_once()
        mock_query.scalar.assert_called_once()
    
    def test_get_total_unit_sales_zero_result(self):
        """Test calculation of total unit sales when result is None."""
        # Arrange
        fund_id = 100
        
        # Mock query chain
        mock_query = Mock()
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.scalar.return_value = None
        
        # Act
        result = self.repository.get_total_unit_sales(fund_id, self.mock_session)
        
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
            f"fund:{fund_id}:unit_events": self.mock_unit_events,
            f"fund:{fund_id}:total_unit_purchases": 50000.0,
            f"fund:{fund_id}:latest_nav": self.mock_nav_update,
            "fund:200:unit_events": [self.mock_unit_purchase],
            "other:key": "value"
        }
        
        # Act
        self.repository._clear_fund_cache(fund_id)
        
        # Assert
        expected_cache = {
            "fund:200:unit_events": [self.mock_unit_purchase],
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
        repository = UnitEventRepository()
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 300
    
    def test_repository_initialization_custom_ttl(self):
        """Test repository initialization with custom cache TTL."""
        # Act
        repository = UnitEventRepository(cache_ttl=600)
        
        # Assert
        assert repository._cache == {}
        assert repository._cache_ttl == 600
