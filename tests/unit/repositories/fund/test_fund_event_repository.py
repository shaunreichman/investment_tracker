"""
Fund Event Repository Unit Tests.

This module tests the FundEventRepository class, focusing on data access operations
and error handling. Tests are precise and focused on repository functionality without
testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Error handling for invalid parameters
- Database session interactions
- Group ID generation
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.fund.repositories.fund_event_repository import FundEventRepository
from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType, SortFieldFundEvent
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundEventFactory


class TestFundEventRepository:
    """Test suite for FundEventRepository."""

    @pytest.fixture
    def repository(self):
        """Create a FundEventRepository instance for testing."""
        return FundEventRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_event_data(self):
        """Sample fund event data for testing."""
        return {
            'fund_id': 1,
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2024, 1, 15),
            'amount': 10000.0,
            'description': 'Test capital call',
            'reference_number': 'CC-001'
        }

    ################################################################################
    # Test get_fund_events method
    ################################################################################

    def test_get_fund_events_returns_all_events(self, repository, mock_session):
        """Test that get_fund_events returns all events when no filters applied."""
        # Arrange
        expected_events = [FundEventFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_events

        # Act
        result = repository.get_fund_events(mock_session)

        # Assert
        assert result == expected_events
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_fund_ids_filter(self, repository, mock_session):
        """Test that get_fund_events filters by fund IDs correctly."""
        # Arrange
        fund_ids = [1, 2, 3]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, fund_ids=fund_ids)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_event_types_filter(self, repository, mock_session):
        """Test that get_fund_events filters by event types correctly."""
        # Arrange
        event_types = [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, event_types=event_types)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_distribution_types_filter(self, repository, mock_session):
        """Test that get_fund_events filters by distribution types correctly."""
        # Arrange
        distribution_types = [DistributionType.DIVIDEND_FRANKED, DistributionType.CAPITAL_GAIN]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, distribution_types=distribution_types)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_tax_payment_types_filter(self, repository, mock_session):
        """Test that get_fund_events filters by tax payment types correctly."""
        # Arrange
        tax_payment_types = [TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING, TaxPaymentType.CAPITAL_GAINS_TAX]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, tax_payment_types=tax_payment_types)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_group_types_filter(self, repository, mock_session):
        """Test that get_fund_events filters by group types correctly."""
        # Arrange
        group_types = [GroupType.INTEREST_WITHHOLDING, GroupType.TAX_STATEMENT]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, group_types=group_types)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_date_range_filter(self, repository, mock_session):
        """Test that get_fund_events filters by date range correctly."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, start_event_date=start_date, end_event_date=end_date)

        # Assert
        assert mock_query.filter.call_count == 2  # Two date filters
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_multiple_filters(self, repository, mock_session):
        """Test that get_fund_events applies multiple filters correctly."""
        # Arrange
        fund_ids = [1, 2]
        event_types = [EventType.CAPITAL_CALL]
        start_date = date(2024, 1, 1)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(
            mock_session, 
            fund_ids=fund_ids, 
            event_types=event_types, 
            start_event_date=start_date
        )

        # Assert
        assert mock_query.filter.call_count == 3  # Three filters applied
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_sorts_by_event_date(self, repository, mock_session):
        """Test that get_fund_events sorts by event date correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, sort_by=SortFieldFundEvent.EVENT_DATE)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_sorts_by_event_type(self, repository, mock_session):
        """Test that get_fund_events sorts by event type correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(mock_session, sort_by=SortFieldFundEvent.EVENT_TYPE)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_fund_events raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_fund_events(mock_session, sort_by="INVALID_FIELD")

    def test_get_fund_events_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_fund_events raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_fund_events(mock_session, sort_order="INVALID_ORDER")

    def test_get_fund_events_with_empty_filter_lists(self, repository, mock_session):
        """Test that get_fund_events handles empty filter lists correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(
            mock_session,
            fund_ids=[],
            event_types=[],
            distribution_types=[],
            tax_payment_types=[],
            group_types=[]
        )

        # Assert
        # Should not apply filters for empty lists
        mock_query.filter.assert_not_called()
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_events_with_none_filters(self, repository, mock_session):
        """Test that get_fund_events handles None filters correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_events(
            mock_session,
            fund_ids=None,
            event_types=None,
            distribution_types=None,
            tax_payment_types=None,
            group_types=None,
            start_event_date=None,
            end_event_date=None
        )

        # Assert
        # Should not apply filters for None values
        mock_query.filter.assert_not_called()
        mock_session.query.assert_called_once_with(FundEvent)

    ################################################################################
    # Test get_fund_event_by_id method
    ################################################################################

    def test_get_fund_event_by_id_returns_event_when_found(self, repository, mock_session):
        """Test that get_fund_event_by_id returns event when found."""
        # Arrange
        event_id = 1
        expected_event = FundEventFactory.build(id=event_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event

        # Act
        result = repository.get_fund_event_by_id(event_id, mock_session)

        # Assert
        assert result == expected_event
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEvent)

    def test_get_fund_event_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_fund_event_by_id returns None when event not found."""
        # Arrange
        event_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_fund_event_by_id(event_id, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Test create_fund_event method
    ################################################################################

    def test_create_fund_event_creates_and_returns_event(self, repository, mock_session, sample_event_data):
        """Test that create_fund_event creates and returns an event."""
        # Arrange
        expected_event = FundEventFactory.build(**sample_event_data)
        with patch('src.fund.repositories.fund_event_repository.FundEvent', return_value=expected_event):
            # Act
            result = repository.create_fund_event(sample_event_data, mock_session)

            # Assert
            assert result == expected_event
            mock_session.add.assert_called_once_with(expected_event)
            mock_session.flush.assert_called_once()

    def test_create_fund_event_raises_type_error_for_invalid_data(self, repository, mock_session):
        """Test that create_fund_event raises TypeError for non-dict data."""
        # Act & Assert
        with pytest.raises(TypeError):
            repository.create_fund_event("invalid_data", mock_session)

    def test_create_fund_event_with_minimal_valid_data(self, repository, mock_session):
        """Test that create_fund_event works with minimal valid data."""
        # Arrange - Minimal valid data (only required fields)
        minimal_event_data = {
            'fund_id': 1,
            'event_type': EventType.CAPITAL_CALL,
            'event_date': date(2024, 1, 15)
        }
        expected_event = FundEventFactory.build(**minimal_event_data)
        
        with patch('src.fund.repositories.fund_event_repository.FundEvent', return_value=expected_event):
            # Act
            result = repository.create_fund_event(minimal_event_data, mock_session)

            # Assert
            assert result == expected_event
            mock_session.add.assert_called_once_with(expected_event)
            mock_session.flush.assert_called_once()

    ################################################################################
    # Test delete_fund_event method
    ################################################################################

    def test_delete_fund_event_deletes_existing_event(self, repository, mock_session):
        """Test that delete_fund_event deletes an existing event."""
        # Arrange
        event_id = 1
        expected_event = FundEventFactory.build(id=event_id, is_grouped=False)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event

        # Act
        result = repository.delete_fund_event(event_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_event)

    def test_delete_fund_event_deletes_grouped_events(self, repository, mock_session):
        """Test that delete_fund_event deletes all events in a group when event is grouped."""
        # Arrange
        event_id = 1
        group_id = 123
        expected_event = FundEventFactory.build(id=event_id, is_grouped=True, group_id=group_id)
        # Include the original event in the group_events since the query finds all events with the same group_id
        group_events = [expected_event] + [FundEventFactory.build(id=i, group_id=group_id) for i in range(2, 5)]
        
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event
        mock_query.all.return_value = group_events

        # Act
        result = repository.delete_fund_event(event_id, mock_session)

        # Assert
        assert result is True
        # Should delete all events in the group (including the original event)
        assert mock_session.delete.call_count == 4  # 1 original + 3 additional group events = 4 total

    def test_delete_fund_event_returns_false_for_nonexistent_event(self, repository, mock_session):
        """Test that delete_fund_event returns False for nonexistent event."""
        # Arrange
        event_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_fund_event(event_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_fund_event_with_none_group_id(self, repository, mock_session):
        """Test that delete_fund_event handles events with None group_id correctly."""
        # Arrange
        event_id = 1
        expected_event = FundEventFactory.build(id=event_id, is_grouped=True, group_id=None)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event

        # Act
        result = repository.delete_fund_event(event_id, mock_session)

        # Assert
        assert result is True
        # Should delete only the single event, not search for group events
        mock_session.delete.assert_called_once_with(expected_event)

    def test_delete_fund_event_with_empty_group_events(self, repository, mock_session):
        """Test that delete_fund_event handles grouped events with empty group results."""
        # Arrange
        event_id = 1
        group_id = 123
        expected_event = FundEventFactory.build(id=event_id, is_grouped=True, group_id=group_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event
        mock_query.all.return_value = []  # No other events in group

        # Act
        result = repository.delete_fund_event(event_id, mock_session)

        # Assert
        assert result is True
        # Should not delete any events since group is empty
        mock_session.delete.assert_not_called()

    ################################################################################
    # Test generate_group_id method
    ################################################################################

    def test_generate_group_id_returns_unique_id(self, repository, mock_session):
        """Test that generate_group_id returns a unique group ID."""
        # Arrange
        expected_group_id = 12345
        mock_result = Mock()
        mock_result.scalar.return_value = expected_group_id
        mock_session.execute.return_value = mock_result

        # Act
        result = repository.generate_group_id(mock_session)

        # Assert
        assert result == expected_group_id
        mock_session.execute.assert_called_once()

    def test_generate_group_id_handles_sequence_reset(self, repository, mock_session):
        """Test that generate_group_id handles sequence reset when approaching limit."""
        # Arrange
        # Mock first call returns value above limit
        mock_result1 = Mock()
        mock_result1.scalar.return_value = 2147483648  # Above PostgreSQL int limit
        # Mock second call after reset (ALTER SEQUENCE)
        mock_result2 = Mock()
        mock_result2.scalar.return_value = None  # ALTER SEQUENCE doesn't return a value
        # Mock third call after reset (SELECT nextval)
        mock_result3 = Mock()
        mock_result3.scalar.return_value = 1
        mock_session.execute.side_effect = [mock_result1, mock_result2, mock_result3]

        # Act
        result = repository.generate_group_id(mock_session)

        # Assert
        assert result == 1
        assert mock_session.execute.call_count == 3  # Called 3 times: SELECT, ALTER, SELECT

    def test_generate_group_id_raises_error_on_failure(self, repository, mock_session):
        """Test that generate_group_id raises RuntimeError on database failure."""
        # Arrange
        mock_session.execute.side_effect = Exception("Database error")

        # Act & Assert
        with pytest.raises(RuntimeError, match="Failed to generate group ID"):
            repository.generate_group_id(mock_session)

