"""
Bank Account Repository Unit Tests.

This module tests the BankAccountRepository class, focusing on data access operations
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

from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.models import BankAccount
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.banking_factories import BankAccountFactory


class TestBankAccountRepository:
    """Test suite for BankAccountRepository."""

    @pytest.fixture
    def repository(self):
        """Create a BankAccountRepository instance for testing."""
        return BankAccountRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_bank_account_data(self):
        """Sample bank account data for testing."""
        return {
            'bank_id': 1,
            'entity_id': 1,
            'account_name': 'Test Account',
            'account_number': '1234-5678-9012-3456',
            'currency': 'AUD',
            'account_type': 'CHECKING',
            'status': 'ACTIVE'
        }

    ################################################################################
    # Test get_bank_accounts method
    ################################################################################

    def test_get_bank_accounts_returns_all_accounts(self, repository, mock_session):
        """Test that get_bank_accounts returns all accounts when no filters applied."""
        # Arrange
        expected_accounts = [BankAccountFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_accounts

        # Act
        result = repository.get_bank_accounts(mock_session)

        # Assert
        assert result == expected_accounts
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_bank_id_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by bank_id correctly."""
        # Arrange
        bank_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, bank_id=bank_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_entity_id_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by entity_id correctly."""
        # Arrange
        entity_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, entity_id=entity_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_account_name_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by account_name correctly."""
        # Arrange
        account_name = "Test Account"
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, account_name=account_name)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_currency_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by currency correctly."""
        # Arrange
        currency = Currency.AUD
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, currency=currency)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_status_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by status correctly."""
        # Arrange
        status = BankAccountStatus.ACTIVE
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, status=status)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_account_type_filter(self, repository, mock_session):
        """Test that get_bank_accounts filters by account_type correctly."""
        # Arrange
        account_type = BankAccountType.CHECKING
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, account_type=account_type)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_with_multiple_filters(self, repository, mock_session):
        """Test that get_bank_accounts applies multiple filters correctly."""
        # Arrange
        bank_id = 1
        entity_id = 1
        currency = Currency.AUD
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, bank_id=bank_id, entity_id=entity_id, currency=currency)

        # Assert
        assert mock_query.filter.call_count == 3

    def test_get_bank_accounts_sorts_by_name_asc(self, repository, mock_session):
        """Test that get_bank_accounts sorts by name in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.NAME, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_sorts_by_name_desc(self, repository, mock_session):
        """Test that get_bank_accounts sorts by name in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.NAME, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_sorts_by_account_number(self, repository, mock_session):
        """Test that get_bank_accounts sorts by account_number correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.ACCOUNT_NUMBER, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_sorts_by_currency(self, repository, mock_session):
        """Test that get_bank_accounts sorts by currency correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.CURRENCY, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_sorts_by_status(self, repository, mock_session):
        """Test that get_bank_accounts sorts by status correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.STATUS, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_sorts_by_created_at(self, repository, mock_session):
        """Test that get_bank_accounts sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_accounts(mock_session, sort_by=SortFieldBankAccount.CREATED_AT, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_accounts_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_bank_accounts raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_bank_accounts(mock_session, sort_by="INVALID_FIELD")

    def test_get_bank_accounts_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_bank_accounts raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_bank_accounts(mock_session, sort_order="INVALID_ORDER")


    ################################################################################
    # Test get_bank_account_by_id method
    ################################################################################

    def test_get_bank_account_by_id_returns_account_when_found(self, repository, mock_session):
        """Test that get_bank_account_by_id returns account when found."""
        # Arrange
        account_id = 1
        expected_account = BankAccountFactory.build(id=account_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_account

        # Act
        result = repository.get_bank_account_by_id(account_id, mock_session)

        # Assert
        assert result == expected_account
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccount)

    def test_get_bank_account_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_bank_account_by_id returns None when account not found."""
        # Arrange
        account_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_bank_account_by_id(account_id, mock_session)

        # Assert
        assert result is None


    ################################################################################
    # Test create_bank_account method
    ################################################################################

    def test_create_bank_account_creates_and_returns_account(self, repository, mock_session, sample_bank_account_data):
        """Test that create_bank_account creates and returns an account."""
        # Arrange
        expected_account = BankAccountFactory.build(**sample_bank_account_data)
        with patch('src.banking.repositories.bank_account_repository.BankAccount', return_value=expected_account):
            # Act
            result = repository.create_bank_account(sample_bank_account_data, mock_session)

            # Assert
            assert result == expected_account
            mock_session.add.assert_called_once_with(expected_account)
            mock_session.flush.assert_called_once()


    ################################################################################
    # Test delete_bank_account method
    ################################################################################

    def test_delete_bank_account_deletes_existing_account(self, repository, mock_session):
        """Test that delete_bank_account deletes an existing account."""
        # Arrange
        account_id = 1
        expected_account = BankAccountFactory.build(id=account_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_account

        # Act
        result = repository.delete_bank_account(account_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_account)
        mock_session.flush.assert_called_once()

    def test_delete_bank_account_returns_false_for_nonexistent_account(self, repository, mock_session):
        """Test that delete_bank_account returns False for nonexistent account."""
        # Arrange
        account_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_bank_account(account_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()


