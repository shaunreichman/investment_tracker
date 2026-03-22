"""
Company Contact Repository Unit Tests.

This module tests the CompanyContactRepository class, focusing on data access operations
and error handling. Tests are precise and focused on repository
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

from src.company.repositories.company_contact_repository import CompanyContactRepository
from src.company.models import Contact
from src.company.enums.company_contact_enums import SortFieldContact
from src.shared.enums.shared_enums import SortOrder
from tests.factories.company_factories import ContactFactory


class TestCompanyContactRepository:
    """Test suite for CompanyContactRepository."""

    @pytest.fixture
    def repository(self):
        """Create a CompanyContactRepository instance for testing."""
        return CompanyContactRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_contact_data(self):
        """Sample contact data for testing."""
        return {
            'company_id': 1,
            'name': 'John Doe',
            'title': 'Managing Director',
            'direct_number': '+1-555-123-4567',
            'direct_email': 'john.doe@testcompany.com',
            'notes': 'Primary contact for all investment matters'
        }

    ################################################################################
    # Test get_contacts method
    ################################################################################

    def test_get_contacts_returns_all_contacts(self, repository, mock_session):
        """Test that get_contacts returns all contacts when no filters applied."""
        # Arrange
        expected_contacts = [ContactFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_contacts

        # Act
        result = repository.get_contacts(mock_session)

        # Assert
        assert result == expected_contacts
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_with_company_id_filter(self, repository, mock_session):
        """Test that get_contacts filters by company_id correctly."""
        # Arrange
        company_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_contacts(mock_session, company_ids=[company_id])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_sorts_by_name_asc(self, repository, mock_session):
        """Test that get_contacts sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_contacts(mock_session, sort_by=SortFieldContact.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_sorts_by_name_desc(self, repository, mock_session):
        """Test that get_contacts sorts by name in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_contacts(mock_session, sort_by=SortFieldContact.NAME, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_sorts_by_created_at(self, repository, mock_session):
        """Test that get_contacts sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_contacts(mock_session, sort_by=SortFieldContact.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_sorts_by_updated_at(self, repository, mock_session):
        """Test that get_contacts sorts by updated_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_contacts(mock_session, sort_by=SortFieldContact.UPDATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contacts_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_contacts raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_contacts(mock_session, sort_by="INVALID_FIELD")

    def test_get_contacts_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_contacts raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_contacts(mock_session, sort_order="INVALID_ORDER")



    ################################################################################
    # Test get_contact_by_id method
    ################################################################################

    def test_get_contact_by_id_returns_contact_when_found(self, repository, mock_session):
        """Test that get_contact_by_id returns contact when found."""
        # Arrange
        contact_id = 1
        expected_contact = ContactFactory.build(id=contact_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_contact

        # Act
        result = repository.get_contact_by_id(contact_id, mock_session)

        # Assert
        assert result == expected_contact
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Contact)

    def test_get_contact_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_contact_by_id returns None when contact not found."""
        # Arrange
        contact_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_contact_by_id(contact_id, mock_session)

        # Assert
        assert result is None


    ################################################################################
    # Test create_contact method
    ################################################################################

    def test_create_contact_creates_and_returns_contact(self, repository, mock_session, sample_contact_data):
        """Test that create_contact creates and returns a contact."""
        # Arrange
        expected_contact = ContactFactory.build(**sample_contact_data)
        with patch('src.company.repositories.company_contact_repository.Contact', return_value=expected_contact):
            # Act
            result = repository.create_contact(sample_contact_data, mock_session)

            # Assert
            assert result == expected_contact
            mock_session.add.assert_called_once_with(expected_contact)
            mock_session.flush.assert_called_once()


    ################################################################################
    # Test delete_contact method
    ################################################################################

    def test_delete_contact_deletes_existing_contact(self, repository, mock_session):
        """Test that delete_contact deletes an existing contact."""
        # Arrange
        contact_id = 1
        expected_contact = ContactFactory.build(id=contact_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_contact

        # Act
        result = repository.delete_contact(contact_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_contact)
        mock_session.flush.assert_called_once()

    def test_delete_contact_returns_false_for_nonexistent_contact(self, repository, mock_session):
        """Test that delete_contact returns False for nonexistent contact."""
        # Arrange
        contact_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_contact(contact_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()


