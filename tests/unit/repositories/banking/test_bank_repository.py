"""
Bank Repository Unit Tests.

This module tests the BankRepository class, focusing on data access operations
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

from src.banking.repositories.bank_repository import BankRepository
from src.banking.models import Bank
from src.banking.enums.bank_enums import BankType, SortFieldBank
from src.shared.enums.shared_enums import Country, SortOrder
from tests.factories.banking_factories import BankFactory


class TestBankRepository:
    """Test suite for BankRepository."""

    @pytest.fixture
    def repository(self):
        """Create a BankRepository instance for testing."""
        return BankRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_bank_data(self):
        """Sample bank data for testing."""
        return {
            'name': 'Test Bank',
            'country': 'AU',
            'bank_type': 'COMMERCIAL',
            'swift_bic': 'TESTAU2X'
        }

    ################################################################################
    # Test get_banks method
    ################################################################################

    def test_get_banks_returns_all_banks(self, repository, mock_session):
        """Test that get_banks returns all banks when no filters applied."""
        # Arrange
        expected_banks = [BankFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_banks

        # Act
        result = repository.get_banks(mock_session)

        # Assert
        assert result == expected_banks
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_with_name_filter(self, repository, mock_session):
        """Test that get_banks filters by name correctly."""
        # Arrange
        bank_name = "Test Bank"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, name=bank_name)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_with_country_filter(self, repository, mock_session):
        """Test that get_banks filters by country correctly."""
        # Arrange
        country = Country.AU
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, country=country)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_with_bank_type_filter(self, repository, mock_session):
        """Test that get_banks filters by bank type correctly."""
        # Arrange
        bank_type = BankType.COMMERCIAL
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, bank_type=bank_type)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_with_multiple_filters(self, repository, mock_session):
        """Test that get_banks applies multiple filters correctly."""
        # Arrange
        bank_name = "Test Bank"
        country = Country.AU
        bank_type = BankType.COMMERCIAL
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, name=bank_name, country=country, bank_type=bank_type)

        # Assert
        assert mock_query.filter.call_count == 3

    def test_get_banks_sorts_by_name_asc(self, repository, mock_session):
        """Test that get_banks sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, sort_by=SortFieldBank.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_sorts_by_name_desc(self, repository, mock_session):
        """Test that get_banks sorts by name in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, sort_by=SortFieldBank.NAME, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_sorts_by_country(self, repository, mock_session):
        """Test that get_banks sorts by country correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, sort_by=SortFieldBank.COUNTRY, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_sorts_by_type(self, repository, mock_session):
        """Test that get_banks sorts by bank type correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, sort_by=SortFieldBank.TYPE, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_sorts_by_created_at(self, repository, mock_session):
        """Test that get_banks sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_banks(mock_session, sort_by=SortFieldBank.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_banks_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_banks raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_banks(mock_session, sort_by="INVALID_FIELD")

    def test_get_banks_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_banks raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_banks(mock_session, sort_order="INVALID_ORDER")


    ################################################################################
    # Test get_bank_by_id method
    ################################################################################

    def test_get_bank_by_id_returns_bank_when_found(self, repository, mock_session):
        """Test that get_bank_by_id returns bank when found."""
        # Arrange
        bank_id = 1
        expected_bank = BankFactory.build(id=bank_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_bank

        # Act
        result = repository.get_bank_by_id(bank_id, mock_session)

        # Assert
        assert result == expected_bank
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(Bank)

    def test_get_bank_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_bank_by_id returns None when bank not found."""
        # Arrange
        bank_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_bank_by_id(bank_id, mock_session)

        # Assert
        assert result is None


    ################################################################################
    # Test create_bank method
    ################################################################################

    def test_create_bank_creates_and_returns_bank(self, repository, mock_session, sample_bank_data):
        """Test that create_bank creates and returns a bank."""
        # Arrange
        expected_bank = BankFactory.build(**sample_bank_data)
        with patch('src.banking.repositories.bank_repository.Bank', return_value=expected_bank):
            # Act
            result = repository.create_bank(sample_bank_data, mock_session)

            # Assert
            assert result == expected_bank
            mock_session.add.assert_called_once_with(expected_bank)
            mock_session.flush.assert_called_once()


    ################################################################################
    # Test delete_bank method
    ################################################################################

    def test_delete_bank_deletes_existing_bank(self, repository, mock_session):
        """Test that delete_bank deletes an existing bank."""
        # Arrange
        bank_id = 1
        expected_bank = BankFactory.build(id=bank_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_bank

        # Act
        result = repository.delete_bank(bank_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_bank)
        mock_session.flush.assert_called_once()

    def test_delete_bank_returns_false_for_nonexistent_bank(self, repository, mock_session):
        """Test that delete_bank returns False for nonexistent bank."""
        # Arrange
        bank_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_bank(bank_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()


