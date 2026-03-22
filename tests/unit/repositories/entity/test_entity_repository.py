"""
Entity Repository Unit Tests.

This module tests the EntityRepository class, focusing on data access operations
and error handling. Tests are precise and focused on repository functionality
without testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.entity.repositories.entity_repository import EntityRepository
from src.entity.models import Entity
from src.entity.enums.entity_enums import EntityType, SortFieldEntity
from src.shared.enums.shared_enums import Country, SortOrder
from tests.factories.entity_factories import EntityFactory


class TestEntityRepository:
    """Test suite for EntityRepository."""

    @pytest.fixture
    def repository(self):
        """Create an EntityRepository instance for testing."""
        return EntityRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_entity_data(self):
        """Sample entity data for testing."""
        return {
            'name': 'Test Entity',
            'entity_type': 'COMPANY',
            'description': 'Test entity description',
            'tax_jurisdiction': 'AU'
        }

    ################################################################################
    # Test get_entities method
    ################################################################################

    def test_get_entities_returns_all_entities(self, repository, mock_session):
        """Test that get_entities returns all entities when no filters applied."""
        # Arrange
        expected_entities = [EntityFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_entities

        # Act
        result = repository.get_entities(mock_session)

        # Assert
        assert result == expected_entities
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_with_entity_type_filter(self, repository, mock_session):
        """Test that get_entities filters by entity_type correctly."""
        # Arrange
        entity_type = EntityType.COMPANY
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, entity_types=[entity_type])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_with_tax_jurisdiction_filter(self, repository, mock_session):
        """Test that get_entities filters by tax_jurisdiction correctly."""
        # Arrange
        tax_jurisdiction = Country.AU
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, tax_jurisdictions=[tax_jurisdiction])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_with_name_filter(self, repository, mock_session):
        """Test that get_entities filters by name correctly."""
        # Arrange
        name = "Test Entity"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, names=[name])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_with_multiple_filters(self, repository, mock_session):
        """Test that get_entities applies multiple filters correctly."""
        # Arrange
        entity_type = EntityType.COMPANY
        tax_jurisdiction = Country.AU
        name = "Test Entity"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, entity_types=[entity_type], 
                              tax_jurisdictions=[tax_jurisdiction], names=[name])

        # Assert
        assert mock_query.filter.call_count == 3

    def test_get_entities_sorts_by_name_asc(self, repository, mock_session):
        """Test that get_entities sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_sorts_by_name_desc(self, repository, mock_session):
        """Test that get_entities sorts by name in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.NAME, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_sorts_by_type(self, repository, mock_session):
        """Test that get_entities sorts by type correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.TYPE, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_sorts_by_tax_jurisdiction(self, repository, mock_session):
        """Test that get_entities sorts by tax_jurisdiction correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.TAX_JURISDICTION, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_sorts_by_created_at(self, repository, mock_session):
        """Test that get_entities sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_sorts_by_updated_at(self, repository, mock_session):
        """Test that get_entities sorts by updated_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_entities(mock_session, sort_by=SortFieldEntity.UPDATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entities_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_entities raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_entities(mock_session, sort_by="INVALID_FIELD")

    def test_get_entities_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_entities raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_entities(mock_session, sort_order="INVALID_ORDER")


    ################################################################################
    # Test get_entity_by_id method
    ################################################################################

    def test_get_entity_by_id_returns_entity_when_found(self, repository, mock_session):
        """Test that get_entity_by_id returns entity when found."""
        # Arrange
        entity_id = 1
        expected_entity = EntityFactory.build(id=entity_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_entity

        # Act
        result = repository.get_entity_by_id(entity_id, mock_session)

        # Assert
        assert result == expected_entity
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Entity)

    def test_get_entity_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_entity_by_id returns None when entity not found."""
        # Arrange
        entity_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_entity_by_id(entity_id, mock_session)

        # Assert
        assert result is None


    ################################################################################
    # Test create_entity method
    ################################################################################

    def test_create_entity_creates_and_returns_entity(self, repository, mock_session, sample_entity_data):
        """Test that create_entity creates and returns an entity."""
        # Arrange
        expected_entity = EntityFactory.build(**sample_entity_data)
        with patch('src.entity.repositories.entity_repository.Entity', return_value=expected_entity):
            # Act
            result = repository.create_entity(sample_entity_data, mock_session)

            # Assert
            assert result == expected_entity
            mock_session.add.assert_called_once_with(expected_entity)
            mock_session.flush.assert_called_once()


    ################################################################################
    # Test delete_entity method
    ################################################################################

    def test_delete_entity_deletes_existing_entity(self, repository, mock_session):
        """Test that delete_entity deletes an existing entity."""
        # Arrange
        entity_id = 1
        expected_entity = EntityFactory.build(id=entity_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_entity

        # Act
        result = repository.delete_entity(entity_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_entity)
        mock_session.flush.assert_called_once()

    def test_delete_entity_returns_false_for_nonexistent_entity(self, repository, mock_session):
        """Test that delete_entity returns False for nonexistent entity."""
        # Arrange
        entity_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_entity(entity_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()


