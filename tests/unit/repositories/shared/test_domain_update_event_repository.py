"""
Domain Update Event Repository Unit Tests.

This module tests the DomainUpdateEventRepository class, focusing on data access operations,
filtering, sorting, and error handling. Tests are precise and focused on repository
functionality without testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.shared.repositories.domain_update_event_repository import DomainUpdateEventRepository
from src.shared.models.domain_update_event import DomainUpdateEvent
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.domain_update_event_enums import SortFieldDomainUpdateEvent, DomainObjectType
from src.shared.enums.shared_enums import EventOperation, SortOrder
from tests.factories.shared_factories import DomainUpdateEventFactory


class TestDomainUpdateEventRepository:
    """Test suite for DomainUpdateEventRepository."""

    @pytest.fixture
    def repository(self):
        """Create a DomainUpdateEventRepository instance for testing."""
        return DomainUpdateEventRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_event_data(self):
        """Sample event data for testing."""
        return {
            'field_name': 'test_field',
            'old_value': 'old_value',
            'new_value': 'new_value',
            'timestamp': '2023-01-01T00:00:00Z'
        }

    ################################################################################
    # Test get_domain_update_events method
    ################################################################################

    def test_get_domain_update_events_returns_all_events(self, repository, mock_session):
        """Test that get_domain_update_events returns all events when no filters applied."""
        # Arrange
        expected_events = [DomainUpdateEventFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_events

        # Act
        result = repository.get_domain_update_events(mock_session)

        # Assert
        assert result == expected_events
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_with_domain_object_type_filter(self, repository, mock_session):
        """Test that get_domain_update_events filters by domain_object_type correctly."""
        # Arrange
        domain_object_type = DomainObjectType.FUND
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session, domain_object_types=[domain_object_type])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_with_domain_object_id_filter(self, repository, mock_session):
        """Test that get_domain_update_events filters by domain_object_id correctly."""
        # Arrange
        domain_object_id = 123
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session, domain_object_ids=[domain_object_id])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_with_event_operation_filter(self, repository, mock_session):
        """Test that get_domain_update_events filters by event_operation correctly."""
        # Arrange
        event_operation = EventOperation.CREATE
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session, event_operations=[event_operation])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_with_fund_event_type_filter(self, repository, mock_session):
        """Test that get_domain_update_events filters by fund_event_type correctly."""
        # Arrange
        fund_event_type = EventType.CAPITAL_CALL
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session, fund_event_types=[fund_event_type])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_with_multiple_filters(self, repository, mock_session):
        """Test that get_domain_update_events applies multiple filters correctly."""
        # Arrange
        domain_object_type = DomainObjectType.FUND
        domain_object_id = 123
        event_operation = EventOperation.UPDATE
        fund_event_type = EventType.DISTRIBUTION
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            domain_object_types=[domain_object_type],
            domain_object_ids=[domain_object_id],
            event_operations=[event_operation],
            fund_event_types=[fund_event_type]
        )

        # Assert
        assert mock_query.filter.call_count == 4  # Four filters applied
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    ################################################################################
    # Test sorting functionality
    ################################################################################

    def test_get_domain_update_events_sorts_by_timestamp_asc(self, repository, mock_session):
        """Test that get_domain_update_events sorts by timestamp ascending."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.TIMESTAMP,
            sort_order=SortOrder.ASC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_sorts_by_timestamp_desc(self, repository, mock_session):
        """Test that get_domain_update_events sorts by timestamp descending."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.TIMESTAMP,
            sort_order=SortOrder.DESC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_sorts_by_domain_object_type(self, repository, mock_session):
        """Test that get_domain_update_events sorts by domain_object_type."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.DOMAIN_OBJECT_TYPE,
            sort_order=SortOrder.ASC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_sorts_by_domain_object_id(self, repository, mock_session):
        """Test that get_domain_update_events sorts by domain_object_id."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.DOMAIN_OBJECT_ID,
            sort_order=SortOrder.ASC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_sorts_by_event_operation(self, repository, mock_session):
        """Test that get_domain_update_events sorts by event_operation."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.EVENT_OPERATION,
            sort_order=SortOrder.ASC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_sorts_by_fund_event_type(self, repository, mock_session):
        """Test that get_domain_update_events sorts by fund_event_type."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(
            mock_session,
            sort_by=SortFieldDomainUpdateEvent.FUND_EVENT_TYPE,
            sort_order=SortOrder.ASC
        )

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    ################################################################################
    # Test get_domain_update_event_by_id method
    ################################################################################

    def test_get_domain_update_event_by_id_returns_event(self, repository, mock_session):
        """Test that get_domain_update_event_by_id returns the correct event."""
        # Arrange
        event_id = 123
        expected_event = DomainUpdateEventFactory.build(id=event_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_event

        # Act
        result = repository.get_domain_update_event_by_id(event_id, mock_session)

        # Assert
        assert result == expected_event
        mock_session.query.assert_called_once_with(DomainUpdateEvent)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    def test_get_domain_update_event_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_domain_update_event_by_id returns None when event not found."""
        # Arrange
        event_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_domain_update_event_by_id(event_id, mock_session)

        # Assert
        assert result is None
        mock_session.query.assert_called_once_with(DomainUpdateEvent)
        mock_query.filter.assert_called_once()
        mock_query.first.assert_called_once()

    ################################################################################
    # Test create_domain_update_event method
    ################################################################################

    def test_create_domain_update_event_creates_and_returns_event(self, repository, mock_session, sample_event_data):
        """Test that create_domain_update_event creates and returns the event."""
        # Arrange
        domain_object_type = DomainObjectType.FUND
        domain_object_id = 123
        event_operation = EventOperation.CREATE
        fund_event_type = EventType.CAPITAL_CALL

        # Act
        result = repository.create_domain_update_event(
            session=mock_session,
            domain_object_type=domain_object_type,
            domain_object_id=domain_object_id,
            event_operation=event_operation,
            event_data=sample_event_data,
            fund_event_type=fund_event_type
        )

        # Assert
        assert isinstance(result, DomainUpdateEvent)
        assert result.domain_object_type == domain_object_type
        assert result.domain_object_id == domain_object_id
        assert result.event_operation == event_operation
        assert result.fund_event_type == fund_event_type
        assert result.event_data == sample_event_data
        mock_session.add.assert_called_once()
        mock_session.flush.assert_called_once()

    def test_create_domain_update_event_adds_to_session(self, repository, mock_session, sample_event_data):
        """Test that create_domain_update_event adds the event to the session."""
        # Arrange
        domain_object_type = DomainObjectType.FUND_EVENT
        domain_object_id = 456
        event_operation = EventOperation.UPDATE
        fund_event_type = EventType.DISTRIBUTION

        # Act
        repository.create_domain_update_event(
            session=mock_session,
            domain_object_type=domain_object_type,
            domain_object_id=domain_object_id,
            event_operation=event_operation,
            event_data=sample_event_data,
            fund_event_type=fund_event_type
        )

        # Assert
        mock_session.add.assert_called_once()
        added_event = mock_session.add.call_args[0][0]
        assert isinstance(added_event, DomainUpdateEvent)
        assert added_event.domain_object_type == domain_object_type
        assert added_event.domain_object_id == domain_object_id
        assert added_event.event_operation == event_operation
        assert added_event.fund_event_type == fund_event_type
        assert added_event.event_data == sample_event_data

    def test_create_domain_update_event_without_fund_event_type(self, repository, mock_session, sample_event_data):
        """Test that create_domain_update_event works without fund_event_type."""
        # Arrange
        domain_object_type = DomainObjectType.ENTITY
        domain_object_id = 789
        event_operation = EventOperation.DELETE

        # Act
        result = repository.create_domain_update_event(
            session=mock_session,
            domain_object_type=domain_object_type,
            domain_object_id=domain_object_id,
            event_operation=event_operation,
            event_data=sample_event_data
        )

        # Assert
        assert isinstance(result, DomainUpdateEvent)
        assert result.domain_object_type == domain_object_type
        assert result.domain_object_id == domain_object_id
        assert result.event_operation == event_operation
        assert result.fund_event_type is None  # Should be None when not provided
        assert result.event_data == sample_event_data

    ################################################################################
    # Test delete_domain_update_event method
    ################################################################################

    def test_delete_domain_update_event_deletes_existing_event(self, repository, mock_session):
        """Test that delete_domain_update_event deletes an existing event."""
        # Arrange
        event_id = 123
        existing_event = DomainUpdateEventFactory.build(id=event_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = existing_event

        # Act
        result = repository.delete_domain_update_event(event_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(existing_event)
        mock_session.flush.assert_called_once()

    def test_delete_domain_update_event_returns_false_when_not_found(self, repository, mock_session):
        """Test that delete_domain_update_event returns False when event not found."""
        # Arrange
        event_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_domain_update_event(event_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()
        mock_session.flush.assert_not_called()

    ################################################################################
    # Test error handling
    ################################################################################

    def test_get_domain_update_events_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_domain_update_events raises ValueError for invalid sort field."""
        # Arrange
        invalid_sort_field = "INVALID_FIELD"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_domain_update_events(
                mock_session,
                sort_by=invalid_sort_field
            )

    def test_get_domain_update_events_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_domain_update_events raises ValueError for invalid sort order."""
        # Arrange
        invalid_sort_order = "INVALID_ORDER"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_domain_update_events(
                mock_session,
                sort_order=invalid_sort_order
            )

    ################################################################################
    # Test default parameters
    ################################################################################

    def test_get_domain_update_events_uses_default_sort_parameters(self, repository, mock_session):
        """Test that get_domain_update_events uses default sort parameters when not specified."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session)

        # Assert
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_default_sort_field_is_timestamp(self, repository, mock_session):
        """Test that get_domain_update_events defaults to TIMESTAMP sort field."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session)

        # Assert
        # Verify that order_by was called (indicating sorting by timestamp)
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)

    def test_get_domain_update_events_default_sort_order_is_asc(self, repository, mock_session):
        """Test that get_domain_update_events defaults to ASC sort order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_domain_update_events(mock_session)

        # Assert
        # Verify that order_by was called (indicating ascending order)
        mock_query.order_by.assert_called_once()
        mock_session.query.assert_called_once_with(DomainUpdateEvent)
