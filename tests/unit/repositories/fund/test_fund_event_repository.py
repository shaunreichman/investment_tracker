"""
Test FundEventRepository functionality.

This module tests the FundEventRepository that provides
data access operations for FundEvent entities.

Testing Focus:
- Event query operations and performance
- Event filtering and sorting capabilities  
- Event relationship and constraint validation
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

from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.models import FundEvent
from src.fund.enums import EventType, SortOrder, DistributionType, TaxPaymentType, GroupType


class TestFundEventRepository:
    """Test the FundEventRepository class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Create repository instance
        self.repository = FundEventRepository(cache_ttl=300)
        
        # Create mock session
        self.mock_session = Mock(spec=Session)
        
        # Create mock fund event
        self.mock_event = Mock(spec=FundEvent)
        self.mock_event.id = 1
        self.mock_event.fund_id = 100
        self.mock_event.event_type = EventType.CAPITAL_CALL
        self.mock_event.event_date = date(2024, 1, 15)
        self.mock_event.amount = 50000.0
        self.mock_event.description = "Test capital call"
        self.mock_event.reference_number = "CC001"
        self.mock_event.nav_per_share = None
        self.mock_event.distribution_type = None
        self.mock_event.tax_withholding = None
        self.mock_event.has_withholding_tax = False
        self.mock_event.tax_payment_type = None
        self.mock_event.tax_statement_id = None
        self.mock_event.units_purchased = None
        self.mock_event.units_sold = None
        self.mock_event.unit_price = None
        self.mock_event.brokerage_fee = None
        self.mock_event.current_equity_balance = None
        self.mock_event.is_cash_flow_complete = False
        self.mock_event.is_grouped = False
        self.mock_event.group_id = None
        self.mock_event.group_type = None
        self.mock_event.group_position = None
        self.mock_event.created_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
        self.mock_event.updated_at = datetime(2024, 1, 15, 10, 0, 0, tzinfo=timezone.utc)
    
    def test_initialization(self):
        """Test repository initialization."""
        repo = FundEventRepository()
        assert repo._cache == {}
        assert repo._cache_ttl == 300
        
        # Test custom cache TTL
        repo = FundEventRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
    
    def test_get_by_id_cache_miss(self):
        """Test get_by_id with cache miss."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = self.mock_event
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_id(1, self.mock_session)
        
        # Verify
        assert result == self.mock_event
        assert self.mock_session.query.called
        assert f"event:1" in self.repository._cache
        assert self.repository._cache[f"event:1"] == self.mock_event
    
    def test_get_by_id_cache_hit(self):
        """Test get_by_id with cache hit."""
        # Setup cache
        self.repository._cache["event:1"] = self.mock_event
        
        # Execute
        result = self.repository.get_by_id(1, self.mock_session)
        
        # Verify
        assert result == self.mock_event
        assert not self.mock_session.query.called  # Should not query database
    
    def test_get_by_id_not_found(self):
        """Test get_by_id when event not found."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_id(999, self.mock_session)
        
        # Verify
        assert result is None
        assert f"event:999" not in self.repository._cache
    
    def test_get_by_fund_basic(self):
        """Test get_by_fund basic functionality."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_fund(100, self.mock_session)
        
        # Verify
        assert result == [self.mock_event]
        assert self.mock_session.query.called
        cache_key = f"events:fund:100:types:None:skip:0:limit:100"
        assert cache_key in self.repository._cache
    
    def test_get_by_fund_with_event_types_filter(self):
        """Test get_by_fund with event type filtering."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        event_types = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]
        result = self.repository.get_by_fund(100, self.mock_session, event_types=event_types)
        
        # Verify
        assert result == [self.mock_event]
        # Verify filter was applied
        mock_query.filter.assert_called()
        cache_key = f"events:fund:100:types:{event_types}:skip:0:limit:100"
        assert cache_key in self.repository._cache
    
    def test_get_by_fund_with_pagination(self):
        """Test get_by_fund with pagination."""
        # Setup mock query with proper chaining
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_fund(100, self.mock_session, skip=10, limit=20)
        
        # Verify
        assert result == [self.mock_event]
        # Verify pagination was applied
        mock_query.offset.assert_called_with(10)
        mock_query.limit.assert_called_with(20)
        cache_key = f"events:fund:100:types:None:skip:10:limit:20"
        assert cache_key in self.repository._cache
    
    def test_get_by_fund_ascending_sort(self):
        """Test get_by_fund with ascending sort order."""
        # Setup mock query with proper chaining
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_fund(100, self.mock_session, sort_order=SortOrder.ASC)
        
        # Verify
        assert result == [self.mock_event]
        # Verify ascending sort was applied
        mock_query.order_by.assert_called()
        cache_key = f"events:fund:100:types:None:skip:0:limit:100"
        assert cache_key in self.repository._cache
    
    def test_get_by_date_range_basic(self):
        """Test get_by_date_range basic functionality."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = self.repository.get_by_date_range(start_date, end_date, self.mock_session)
        
        # Verify
        assert result == [self.mock_event]
        assert self.mock_session.query.called
        cache_key = f"events:date_range:{start_date}:{end_date}:fund:None"
        assert cache_key in self.repository._cache
    
    def test_get_by_date_range_with_fund_filter(self):
        """Test get_by_date_range with fund filtering."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.order_by.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        result = self.repository.get_by_date_range(start_date, end_date, self.mock_session, fund_id=100)
        
        # Verify
        assert result == [self.mock_event]
        # Verify fund filter was applied
        mock_query.filter.assert_called()
        cache_key = f"events:date_range:{start_date}:{end_date}:fund:100"
        assert cache_key in self.repository._cache
    
    def test_get_by_type_basic(self):
        """Test get_by_type basic functionality."""
        # Setup mock query with proper chaining
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_type(EventType.CAPITAL_CALL, self.mock_session)
        
        # Verify
        assert result == [self.mock_event]
        assert self.mock_session.query.called
        cache_key = f"events:type:{EventType.CAPITAL_CALL.value}:fund:None:skip:0:limit:100"
        assert cache_key in self.repository._cache
    
    def test_get_by_type_with_fund_filter(self):
        """Test get_by_type with fund filtering."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_by_type(EventType.CAPITAL_CALL, self.mock_session, fund_id=100)
        
        # Verify
        assert result == [self.mock_event]
        # Verify fund filter was applied
        mock_query.filter.assert_called()
        cache_key = f"events:type:{EventType.CAPITAL_CALL.value}:fund:100:skip:0:limit:100"
        assert cache_key in self.repository._cache
    
    def test_create_success(self):
        """Test create method with valid data."""
        # Setup mock event data
        event_data = {
            'fund_id': 100,
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2024, 1, 15),
            'amount': 50000.0,
            'description': 'Test capital call'
        }
        
        # Execute
        result = self.repository.create(event_data, self.mock_session)
        
        # Verify
        assert self.mock_session.add.called
        assert self.mock_session.flush.called
        # Verify cache clearing - fund, date, and type caches should be cleared
        # but no event cache exists yet since we're creating
    
    def test_create_missing_required_field(self):
        """Test create method with missing required field."""
        # Setup mock event data missing required field
        event_data = {
            'fund_id': 100,
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2024, 1, 15)
            # Missing 'amount' field
        }
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Required field 'amount' is missing"):
            self.repository.create(event_data, self.mock_session)
    
    def test_update_success(self):
        """Test update method with valid data."""
        # Setup mock query for get_by_id
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = self.mock_event
        self.mock_session.query.return_value = mock_query
        
        # Setup update data
        update_data = {'amount': 75000.0, 'description': 'Updated description'}
        
        # Execute
        result = self.repository.update(1, update_data, self.mock_session)
        
        # Verify
        assert result == self.mock_event
        assert self.mock_event.amount == 75000.0
        assert self.mock_event.description == 'Updated description'
        assert self.mock_session.flush.called
        # Verify cache clearing - note that get_by_id caches the event, so it remains
        # but fund, date, and type caches should be cleared
        assert 'event:1' in self.repository._cache  # Event cache remains
        # Fund, date, and type caches should be cleared by the clear methods
    
    def test_update_event_not_found(self):
        """Test update method when event not found."""
        # Setup mock query for get_by_id
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.update(999, {'amount': 75000.0}, self.mock_session)
        
        # Verify
        assert result is None
    
    def test_delete_success(self):
        """Test delete method with valid event."""
        # Setup mock query for get_by_id
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = self.mock_event
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.delete(1, self.mock_session)
        
        # Verify
        assert result is True
        assert self.mock_session.delete.called
        # Verify cache clearing - fund, date, and type caches should be cleared
        # but event cache may remain depending on implementation
    
    def test_delete_event_not_found(self):
        """Test delete method when event not found."""
        # Setup mock query for get_by_id
        mock_query = Mock()
        mock_query.filter.return_value.first.return_value = None
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.delete(999, self.mock_session)
        
        # Verify
        assert result is False
        assert not self.mock_session.delete.called
    
    def test_bulk_create_success(self):
        """Test bulk_create method with valid data."""
        # Setup mock events data
        events_data = [
            {
                'fund_id': 100,
                'event_type': EventType.CAPITAL_CALL,
                'event_date': date(2024, 1, 15),
                'amount': 50000.0
            },
            {
                'fund_id': 100,
                'event_type': EventType.DISTRIBUTION,
                'event_date': date(2024, 1, 20),
                'amount': -25000.0
            }
        ]
        
        # Execute
        result = self.repository.bulk_create(events_data, self.mock_session)
        
        # Verify
        assert len(result) == 2
        assert self.mock_session.add.call_count == 2
        assert self.mock_session.flush.called
        # Verify cache clearing - fund, date, and type caches should be cleared
        # but no event caches exist yet since we're creating
    
    def test_bulk_create_empty_list(self):
        """Test bulk_create method with empty list."""
        result = self.repository.bulk_create([], self.mock_session)
        assert result == []
        assert not self.mock_session.add.called
        assert not self.mock_session.flush.called
    
    def test_bulk_create_missing_required_field(self):
        """Test bulk_create method with missing required field."""
        # Setup mock events data with missing required field
        events_data = [
            {
                'fund_id': 100,
                'event_type': EventType.CAPITAL_CALL,
                'event_date': date(2024, 1, 15)
                # Missing 'amount' field
            }
        ]
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Event 0 is missing required field 'amount'"):
            self.repository.bulk_create(events_data, self.mock_session)
    
    def test_get_events_for_recalculation(self):
        """Test get_events_for_recalculation method."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_events_for_recalculation(100, 50, self.mock_session)
        
        # Verify
        assert result == [self.mock_event]
        assert self.mock_session.query.called
        cache_key = f"events:recalc:100:from:50"
        assert cache_key in self.repository._cache
    
    def test_get_event_count_by_fund(self):
        """Test get_event_count_by_fund method."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.scalar.return_value = 5
        self.mock_session.query.return_value = mock_query
        
        # Execute
        result = self.repository.get_event_count_by_fund(100, self.mock_session)
        
        # Verify
        assert result == 5
        assert self.mock_session.query.called
        cache_key = f"event_count:fund:100"
        assert cache_key in self.repository._cache
    
    def test_cache_clearing_methods(self):
        """Test cache clearing methods."""
        # Setup some cache data
        self.repository._cache = {
            'event:1': 'data1',
            'events:fund:100:types:None:skip:0:limit:100': 'data2',
            'events:date_range:2024-01-01:2024-01-31:fund:None': 'data3',
            'events:type:CAPITAL_CALL:fund:None:skip:0:limit:100': 'data4',
            'event_count:fund:100': 'data5',
            'other_data': 'data6'
        }
        
        # Test _clear_event_cache
        self.repository._clear_event_cache(1)
        assert 'event:1' not in self.repository._cache
        assert 'other_data' in self.repository._cache  # Should remain
        
        # Test _clear_fund_cache
        self.repository._clear_fund_cache(100)
        assert 'events:fund:100:types:None:skip:0:limit:100' not in self.repository._cache
        assert 'event_count:fund:100' not in self.repository._cache
        assert 'other_data' in self.repository._cache  # Should remain
        
        # Test _clear_date_cache
        self.repository._clear_date_cache(date(2024, 1, 15))
        assert 'events:date_range:2024-01-01:2024-01-31:fund:None' not in self.repository._cache
        assert 'other_data' in self.repository._cache  # Should remain
        
        # Test _clear_type_cache
        self.repository._clear_type_cache('CAPITAL_CALL')
        assert 'events:type:CAPITAL_CALL:fund:None:skip:0:limit:100' not in self.repository._cache
        assert 'other_data' in self.repository._cache  # Should remain
    
    def test_clear_all_cache(self):
        """Test clear_all_cache method."""
        # Setup some cache data
        self.repository._cache = {
            'event:1': 'data1',
            'events:fund:100:types:None:skip:0:limit:100': 'data2',
            'other_data': 'data3'
        }
        
        # Execute
        self.repository.clear_all_cache()
        
        # Verify
        assert self.repository._cache == {}
    
    def test_cache_ttl_behavior(self):
        """Test that cache TTL is properly set."""
        # Test default TTL
        repo = FundEventRepository()
        assert repo._cache_ttl == 300
        
        # Test custom TTL
        repo = FundEventRepository(cache_ttl=600)
        assert repo._cache_ttl == 600
        
        # Test zero TTL
        repo = FundEventRepository(cache_ttl=0)
        assert repo._cache_ttl == 0
    
    def test_repository_method_count(self):
        """Test that repository has the expected number of public methods."""
        # Count public methods (excluding private methods starting with _)
        public_methods = [
            method for method in dir(self.repository) 
            if callable(getattr(self.repository, method)) 
            and not method.startswith('_')
            and method not in ['_cache', '_cache_ttl']  # Exclude attributes
        ]
        
        # Expected methods based on the repository implementation
        expected_methods = {
            'get_by_id', 'get_by_fund', 'get_by_date_range', 'get_by_type',
            'create', 'update', 'delete', 'bulk_create', 'get_events_for_recalculation',
            'get_event_count_by_fund', 'clear_all_cache'
        }
        
        assert set(public_methods) == expected_methods, f"Expected methods: {expected_methods}, got: {set(public_methods)}"
    
    def test_repository_attributes(self):
        """Test that repository has the expected attributes."""
        assert hasattr(self.repository, '_cache')
        assert hasattr(self.repository, '_cache_ttl')
        assert isinstance(self.repository._cache, dict)
        assert isinstance(self.repository._cache_ttl, int)
    
    def test_error_handling_in_create(self):
        """Test error handling in create method."""
        # Test with None event_data
        with pytest.raises(TypeError, match="event_data must be a dictionary, got NoneType"):
            self.repository.create(None, self.mock_session)
        
        # Test with empty event_data
        with pytest.raises(ValueError, match="Required field 'fund_id' is missing"):
            self.repository.create({}, self.mock_session)
    
    def test_error_handling_in_bulk_create(self):
        """Test error handling in bulk_create method."""
        # Test with None events_data - should raise TypeError (not return empty list)
        with pytest.raises(TypeError, match="events_data must be a list, got NoneType"):
            self.repository.bulk_create(None, self.mock_session)
        
        # Test with invalid events_data type - should raise TypeError first
        with pytest.raises(TypeError, match="events_data must be a list, got str"):
            self.repository.bulk_create("invalid", self.mock_session)
    
    def test_enhanced_type_validation(self):
        """Test enhanced type validation for all methods."""
        # Test create method with various invalid types
        invalid_types = [None, "string", 123, [1, 2, 3], True, 3.14]
        for invalid_type in invalid_types:
            if isinstance(invalid_type, dict):
                continue  # Skip dict type as it's valid
            with pytest.raises(TypeError, match=f"event_data must be a dictionary, got {type(invalid_type).__name__}"):
                self.repository.create(invalid_type, self.mock_session)
        
        # Test update method with various invalid types
        for invalid_type in invalid_types:
            if isinstance(invalid_type, dict):
                continue  # Skip dict type as it's valid
            with pytest.raises(TypeError, match=f"event_data must be a dictionary, got {type(invalid_type).__name__}"):
                self.repository.update(1, invalid_type, self.mock_session)
        
        # Test bulk_create method with various invalid types
        invalid_types = [None, "string", 123, {"key": "value"}, True, 3.14]
        for invalid_type in invalid_types:
            if isinstance(invalid_type, list):
                continue  # Skip list type as it's valid
            with pytest.raises(TypeError, match=f"events_data must be a list, got {type(invalid_type).__name__}"):
                self.repository.bulk_create(invalid_type, self.mock_session)
    
    def test_bulk_create_item_type_validation(self):
        """Test that bulk_create validates each item is a dictionary."""
        # Test with list containing non-dictionary items
        invalid_events_data = [
            {"fund_id": 100, "event_type": EventType.CAPITAL_CALL, "event_date": date(2024, 1, 15), "amount": 50000.0},  # Valid
            "not a dict",  # Invalid
            {"fund_id": 200, "event_type": EventType.DISTRIBUTION, "event_date": date(2024, 1, 20), "amount": -25000.0}  # Valid
        ]
        
        with pytest.raises(TypeError, match="Event 1 must be a dictionary, got str"):
            self.repository.bulk_create(invalid_events_data, self.mock_session)
    
    def test_cache_key_uniqueness(self):
        """Test that cache keys are unique for different parameters."""
        # Setup mock query
        mock_query = Mock()
        mock_query.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = [self.mock_event]
        self.mock_session.query.return_value = mock_query
        
        # Execute different queries to generate different cache keys
        self.repository.get_by_fund(100, self.mock_session, skip=0, limit=10)
        self.repository.get_by_fund(100, self.mock_session, skip=10, limit=10)
        self.repository.get_by_fund(100, self.mock_session, skip=0, limit=20)
        
        # Verify different cache keys exist
        assert f"events:fund:100:types:None:skip:0:limit:10" in self.repository._cache
        assert f"events:fund:100:types:None:skip:10:limit:10" in self.repository._cache
        assert f"events:fund:100:types:None:skip:0:limit:20" in self.repository._cache
        
        # Verify they contain different data (same in this case due to mock)
        assert len(self.repository._cache) == 3
