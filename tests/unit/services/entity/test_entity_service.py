"""
Entity Service Unit Tests.

This module tests the EntityService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Entity retrieval operations
- Entity creation with business rules
- Entity deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.entity.services.entity_service import EntityService
from src.entity.models import Entity
from src.entity.enums.entity_enums import SortFieldEntity, EntityType
from src.shared.enums.shared_enums import Country, SortOrder
from tests.factories.entity_factories import EntityFactory


class TestEntityService:
    """Test suite for EntityService."""

    @pytest.fixture
    def service(self):
        """Create an EntityService instance for testing."""
        return EntityService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_entity_data(self):
        """Sample entity data for testing."""
        return {
            'name': 'Test Entity',
            'entity_type': 'PERSON',
            'description': 'Test description',
            'tax_jurisdiction': 'AU'
        }

    @pytest.fixture
    def mock_entity(self):
        """Mock entity instance."""
        return EntityFactory.build(id=1, name='Test Entity')

    ################################################################################
    # Test get_entities method
    ################################################################################

    def test_get_entities_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_entities calls repository with correct parameters."""
        # Arrange
        expected_entities = [EntityFactory.build() for _ in range(2)]
        with patch.object(service.entity_repository, 'get_entities', return_value=expected_entities) as mock_repo:
            # Act
            result = service.get_entities(mock_session)

            # Assert
            assert result == expected_entities
            mock_repo.assert_called_once_with(
                mock_session, 
                None, 
                None, 
                None, 
                SortFieldEntity.NAME,
                SortOrder.ASC
            )

    def test_get_entities_passes_filters_to_repository(self, service, mock_session):
        """Test that get_entities passes all filters to repository."""
        # Arrange
        entity_type = EntityType.PERSON
        tax_jurisdiction = Country.AU
        name = "Test Entity"
        sort_by = SortFieldEntity.TYPE
        sort_order = SortOrder.DESC
        expected_entities = [EntityFactory.build()]
        
        with patch.object(service.entity_repository, 'get_entities', return_value=expected_entities) as mock_repo:
            # Act
            result = service.get_entities(
                mock_session, 
                entity_type=entity_type,
                tax_jurisdiction=tax_jurisdiction,
                name=name,
                sort_by=sort_by,
                sort_order=sort_order
            )

            # Assert
            assert result == expected_entities
            mock_repo.assert_called_once_with(
                mock_session, 
                entity_type, 
                tax_jurisdiction, 
                name, 
                sort_by,
                sort_order
            )

    ################################################################################
    # Test get_entity_by_id method
    ################################################################################

    def test_get_entity_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_entity):
        """Test that get_entity_by_id calls repository with correct ID."""
        # Arrange
        entity_id = 1
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=mock_entity) as mock_repo:
            # Act
            result = service.get_entity_by_id(entity_id, mock_session)

            # Assert
            assert result == mock_entity
            mock_repo.assert_called_once_with(entity_id, mock_session)

    def test_get_entity_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_entity_by_id returns None when entity not found."""
        # Arrange
        entity_id = 999
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_entity_by_id(entity_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(entity_id, mock_session)

    ################################################################################
    # Test create_entity method
    ################################################################################

    def test_create_entity_calls_repository_with_correct_data(self, service, mock_session, sample_entity_data, mock_entity):
        """Test that create_entity calls repository with correct data."""
        # Arrange
        with patch.object(service.entity_repository, 'create_entity', return_value=mock_entity) as mock_repo:
            # Act
            result = service.create_entity(sample_entity_data, mock_session)

            # Assert
            assert result == mock_entity
            mock_repo.assert_called_once_with(sample_entity_data, mock_session)

    def test_create_entity_raises_error_when_repository_fails(self, service, mock_session, sample_entity_data):
        """Test that create_entity raises ValueError when repository fails."""
        # Arrange
        with patch.object(service.entity_repository, 'create_entity', return_value=None) as mock_repo:
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create entity"):
                service.create_entity(sample_entity_data, mock_session)

    def test_create_entity_preserves_original_data(self, service, mock_session, mock_entity):
        """Test that create_entity preserves original data."""
        # Arrange
        entity_data = {
            'name': 'Test Entity',
            'entity_type': 'PERSON',
            'description': 'Test description',
            'tax_jurisdiction': 'AU',
            'custom_field': 'custom_value'
        }
        
        with patch.object(service.entity_repository, 'create_entity', return_value=mock_entity) as mock_repo:
            # Act
            result = service.create_entity(entity_data, mock_session)

            # Assert
            assert result == mock_entity
            mock_repo.assert_called_once_with(entity_data, mock_session)

    ################################################################################
    # Test delete_entity method
    ################################################################################

    def test_delete_entity_successfully_deletes_entity(self, service, mock_session, mock_entity):
        """Test successful entity deletion."""
        # Arrange
        entity_id = 1
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=mock_entity) as mock_get_entity, \
             patch.object(service.entity_validation_service, 'validate_entity_deletion', return_value={}) as mock_validate, \
             patch.object(service.entity_repository, 'delete_entity', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_entity(entity_id, mock_session)

            # Assert
            assert result is True
            mock_get_entity.assert_called_once_with(entity_id, mock_session)
            mock_validate.assert_called_once_with(entity_id, mock_session)
            mock_delete.assert_called_once_with(entity_id, mock_session)

    def test_delete_entity_raises_error_when_entity_not_found(self, service, mock_session):
        """Test that delete_entity raises ValueError when entity not found."""
        # Arrange
        entity_id = 999
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=None) as mock_get_entity:
            # Act & Assert
            with pytest.raises(ValueError, match="Entity not found"):
                service.delete_entity(entity_id, mock_session)
            
            mock_get_entity.assert_called_once_with(entity_id, mock_session)

    def test_delete_entity_raises_error_when_validation_fails(self, service, mock_session, mock_entity):
        """Test that delete_entity raises ValueError when validation fails."""
        # Arrange
        entity_id = 1
        validation_errors = {'funds': ['Cannot delete entity with dependent funds']}
        
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=mock_entity) as mock_get_entity, \
             patch.object(service.entity_validation_service, 'validate_entity_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_entity(entity_id, mock_session)
            
            mock_get_entity.assert_called_once_with(entity_id, mock_session)
            mock_validate.assert_called_once_with(entity_id, mock_session)

    def test_delete_entity_raises_error_when_repository_fails(self, service, mock_session, mock_entity):
        """Test that delete_entity raises ValueError when repository deletion fails."""
        # Arrange
        entity_id = 1
        with patch.object(service.entity_repository, 'get_entity_by_id', return_value=mock_entity) as mock_get_entity, \
             patch.object(service.entity_validation_service, 'validate_entity_deletion', return_value={}) as mock_validate, \
             patch.object(service.entity_repository, 'delete_entity', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete entity"):
                service.delete_entity(entity_id, mock_session)
            
            mock_get_entity.assert_called_once_with(entity_id, mock_session)
            mock_validate.assert_called_once_with(entity_id, mock_session)
            mock_delete.assert_called_once_with(entity_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.entity_validation_service is not None
        assert service.entity_repository is not None
        assert hasattr(service, 'entity_validation_service')
        assert hasattr(service, 'entity_repository')
