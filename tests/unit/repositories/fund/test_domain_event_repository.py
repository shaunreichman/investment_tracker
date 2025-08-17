"""
Domain Event Repository Tests.

This module tests the DomainEventRepository class, ensuring proper data access
operations, query performance, and data consistency.

Testing Scope:
- Repository CRUD operations
- Query methods and filtering
- Data persistence and retrieval
- Error handling and edge cases

Testing Approach: Unit Tests with Mocked Dependencies
- Mock database session and query results
- Test repository logic in isolation
- Validate data access patterns
- Ensure proper error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime, timezone
from typing import List, Optional

from src.fund.repositories.domain_event_repository import DomainEventRepository
from src.fund.models.domain_event import DomainEvent
from src.fund.events.domain.base_event import FundDomainEvent
from src.fund.enums import DomainEventType


class MockFundDomainEvent(FundDomainEvent):
    """Mock domain event for testing."""
    
    @property
    def event_type(self) -> DomainEventType:
        return DomainEventType.EQUITY_BALANCE_CHANGED


class TestDomainEventRepository:
    """Test suite for DomainEventRepository."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.mock_session = Mock()
        self.repository = DomainEventRepository(self.mock_session)
        
        # Create mock domain event data
        self.mock_domain_event = MockFundDomainEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            metadata={"amount": 1000.0, "reason": "test"}
        )
        
        # Create mock database event
        self.mock_db_event = Mock(spec=DomainEvent)
        self.mock_db_event.id = 1
        self.mock_db_event.fund_id = 1
        self.mock_db_event.event_type = "EQUITY_BALANCE_CHANGED"
        self.mock_db_event.event_data = {"amount": 1000.0, "reason": "test"}
        self.mock_db_event.timestamp = datetime.now(timezone.utc)
        self.mock_db_event.source = "mockfunddomainevent"
        self.mock_db_event.processed = "PENDING"
    
    def test_init(self):
        """Test repository initialization."""
        # Arrange & Act
        repo = DomainEventRepository(self.mock_session)
        
        # Assert
        assert repo.session == self.mock_session
    
    def test_store_domain_event_success(self):
        """Test successful storage of a single domain event."""
        # Arrange
        mock_db_event = Mock(spec=DomainEvent)
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Act
        result = self.repository.store_domain_event(self.mock_domain_event)
        
        # Assert
        self.mock_session.add.assert_called_once()
        self.mock_session.flush.assert_called_once()
        assert result.fund_id == 1
        assert result.event_type == "EQUITY_BALANCE_CHANGED"
        assert result.event_data == {"amount": 1000.0, "reason": "test"}
        assert result.source == "mockfunddomainevent"
    
    def test_store_domain_events_success(self):
        """Test successful storage of multiple domain events."""
        # Arrange
        events = [self.mock_domain_event, self.mock_domain_event]
        self.mock_session.add.return_value = None
        self.mock_session.flush.return_value = None
        
        # Act
        result = self.repository.store_domain_events(events)
        
        # Assert
        assert self.mock_session.add.call_count == 2
        assert self.mock_session.flush.call_count == 2
        assert len(result) == 2
        assert all(event.fund_id == 1 for event in result)
    
    def test_get_by_id_found(self):
        """Test successful retrieval of domain event by ID."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = self.mock_db_event
        
        # Act
        result = self.repository.get_by_id(1)
        
        # Assert
        self.mock_session.query.assert_called_once_with(DomainEvent)
        mock_query.filter.assert_called_once()
        mock_filter.first.assert_called_once()
        assert result == self.mock_db_event
    
    def test_get_by_id_not_found(self):
        """Test retrieval of domain event by ID when not found."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        # Act
        result = self.repository.get_by_id(999)
        
        # Assert
        assert result is None
    
    def test_get_by_fund_success(self):
        """Test successful retrieval of domain events by fund ID."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_fund(1)
        
        # Assert
        self.mock_session.query.assert_called_once_with(DomainEvent)
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_order_by.all.assert_called_once()
        assert result == [self.mock_db_event]
    
    def test_get_by_fund_no_limit(self):
        """Test retrieval of domain events by fund ID (no limit parameter)."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_fund(1)
        
        # Assert
        mock_order_by.all.assert_called_once()
        assert result == [self.mock_db_event]
    
    def test_get_by_type_success(self):
        """Test successful retrieval of domain events by type."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_type("EQUITY_BALANCE_CHANGED", fund_id=1, limit=5)
        
        # Assert
        assert mock_query.filter.call_count == 2  # event_type and fund_id
        mock_order_by.limit.assert_called_once_with(5)
        assert result == [self.mock_db_event]
    
    def test_get_by_type_no_fund_filter(self):
        """Test retrieval of domain events by type without fund filter."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_type("EQUITY_BALANCE_CHANGED", limit=5)
        
        # Assert
        assert mock_query.filter.call_count == 1  # only event_type
        assert result == [self.mock_db_event]
    
    def test_get_by_date_range_success(self):
        """Test successful retrieval of domain events by date range."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_date_range(start_date, end_date, fund_id=1)
        
        # Assert
        assert mock_query.filter.call_count == 2  # date range and fund_id
        mock_order_by.all.assert_called_once()
        assert result == [self.mock_db_event]
    
    def test_get_by_date_range_no_fund_filter(self):
        """Test retrieval of domain events by date range without fund filter."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_by_date_range(start_date, end_date)
        
        # Assert
        assert mock_query.filter.call_count == 1  # only date range
        assert result == [self.mock_db_event]
    
    def test_get_recent_events_success(self):
        """Test successful retrieval of recent domain events."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_recent_events(fund_id=1, limit=50)
        
        # Assert
        mock_query.filter.assert_called_once()
        mock_query.order_by.assert_called_once()
        mock_order_by.limit.assert_called_once_with(50)
        mock_limit.all.assert_called_once()
        assert result == [self.mock_db_event]
    
    def test_get_recent_events_no_fund_filter(self):
        """Test retrieval of recent domain events without fund filter."""
        # Arrange
        mock_query = Mock()
        mock_order_by = Mock()
        mock_limit = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.limit.return_value = mock_limit
        mock_limit.all.return_value = [self.mock_db_event]
        
        # Act
        result = self.repository.get_recent_events(limit=100)
        
        # Assert
        mock_query.order_by.assert_called_once()
        mock_order_by.limit.assert_called_once_with(100)
        assert result == [self.mock_db_event]
    
    def test_delete_by_fund_success(self):
        """Test successful deletion of domain events by fund ID."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.delete.return_value = 5  # 5 events deleted
        
        # Act
        result = self.repository.delete_by_fund(1)
        
        # Assert
        self.mock_session.query.assert_called_once_with(DomainEvent)
        mock_query.filter.assert_called_once()
        mock_filter.delete.assert_called_once()
        assert result == 5
    
    def test_get_event_count_by_fund_success(self):
        """Test successful count of domain events by fund ID."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.count.return_value = 10
        
        # Act
        result = self.repository.get_event_count_by_fund(1)
        
        # Assert
        self.mock_session.query.assert_called_once_with(DomainEvent)
        mock_query.filter.assert_called_once()
        mock_filter.count.assert_called_once()
        assert result == 10
    
    def test_get_event_summary_success(self):
        """Test successful retrieval of event summary by type."""
        # Arrange
        mock_query = Mock()
        mock_filter = Mock()
        mock_group_by = Mock()
        
        # Mock the complex query structure
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.group_by.return_value = mock_group_by
        mock_group_by.all.return_value = [
            ("EQUITY_BALANCE_CHANGED", 5),
            ("DISTRIBUTION_RECORDED", 3)
        ]
        
        # Act
        result = self.repository.get_event_summary(fund_id=1)
        
        # Assert
        expected = {
            "EQUITY_BALANCE_CHANGED": 5,
            "DISTRIBUTION_RECORDED": 3
        }
        assert result == expected
    
    def test_get_event_summary_no_fund_filter(self):
        """Test retrieval of event summary without fund filter."""
        # Arrange
        mock_query = Mock()
        mock_group_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.group_by.return_value = mock_group_by
        mock_group_by.all.return_value = [
            ("EQUITY_BALANCE_CHANGED", 10),
            ("DISTRIBUTION_RECORDED", 7)
        ]
        
        # Act
        result = self.repository.get_event_summary()
        
        # Assert
        expected = {
            "EQUITY_BALANCE_CHANGED": 10,
            "DISTRIBUTION_RECORDED": 7
        }
        assert result == expected
    
    def test_store_domain_event_with_empty_list(self):
        """Test storage of empty list of domain events."""
        # Act
        result = self.repository.store_domain_events([])
        
        # Assert
        assert result == []
    
    def test_get_by_date_range_invalid_dates(self):
        """Test date range query with invalid date parameters."""
        # Arrange
        start_date = date(2024, 1, 31)
        end_date = date(2024, 1, 1)  # End before start
        
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = []
        
        # Act
        result = self.repository.get_by_date_range(start_date, end_date)
        
        # Assert
        # Repository should handle invalid date ranges gracefully
        # The actual filtering logic is handled by SQLAlchemy
        assert result == []
    
    def test_repository_session_management(self):
        """Test that repository properly uses the provided session."""
        # Arrange
        custom_session = Mock()
        repo = DomainEventRepository(custom_session)
        
        # Act
        repo.get_by_id(1)
        
        # Assert
        custom_session.query.assert_called_once()
        assert repo.session == custom_session
