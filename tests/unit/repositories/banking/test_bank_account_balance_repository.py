"""
Bank Account Balance Repository Unit Tests.

This module tests the BankAccountBalanceRepository class, focusing on data access operations
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
from datetime import date

from src.banking.repositories.bank_account_balance_repository import BankAccountBalanceRepository
from src.banking.models import BankAccountBalance
from src.banking.enums.bank_account_balance_enums import SortFieldBankAccountBalance
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.banking_factories import BankAccountBalanceFactory


class TestBankAccountBalanceRepository:
    """Test suite for BankAccountBalanceRepository."""

    @pytest.fixture
    def repository(self):
        """Create a BankAccountBalanceRepository instance for testing."""
        return BankAccountBalanceRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_balance_data(self):
        """Sample bank account balance data for testing."""
        return {
            'bank_account_id': 1,
            'currency': Currency.AUD,
            'date': date(2024, 1, 31),
            'balance_statement': 10000.00,
            'balance_adjustment': 500.00,
            'balance_final': 10500.00
        }

    ################################################################################
    # Test get_bank_account_balances method
    ################################################################################

    def test_get_bank_account_balances_returns_all_balances(self, repository, mock_session):
        """Test that get_bank_account_balances returns all balances when no filters applied."""
        # Arrange
        expected_balances = [BankAccountBalanceFactory.build() for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_balances

        # Act
        result = repository.get_bank_account_balances(mock_session)

        # Assert
        assert result == expected_balances
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_bank_account_id_filter(self, repository, mock_session):
        """Test that get_bank_account_balances filters by bank_account_id correctly."""
        # Arrange
        bank_account_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, bank_account_ids=[bank_account_id])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_currency_filter(self, repository, mock_session):
        """Test that get_bank_account_balances filters by currency correctly."""
        # Arrange
        currency = Currency.AUD
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, currencies=[currency])

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_start_date_filter(self, repository, mock_session):
        """Test that get_bank_account_balances filters by start_date correctly."""
        # Arrange
        start_date = date(2024, 1, 1)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, start_date=start_date)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_end_date_filter(self, repository, mock_session):
        """Test that get_bank_account_balances filters by end_date correctly."""
        # Arrange
        end_date = date(2024, 12, 31)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, end_date=end_date)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_multiple_filters(self, repository, mock_session):
        """Test that get_bank_account_balances applies multiple filters correctly."""
        # Arrange
        bank_account_id = 1
        currency = Currency.AUD
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(
            mock_session, 
            bank_account_ids=[bank_account_id], 
            currencies=[currency],
            start_date=start_date,
            end_date=end_date
        )

        # Assert
        assert mock_query.filter.call_count == 4

    def test_get_bank_account_balances_sorts_by_date_asc(self, repository, mock_session):
        """Test that get_bank_account_balances sorts by date in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, sort_by=SortFieldBankAccountBalance.DATE, sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_sorts_by_date_desc(self, repository, mock_session):
        """Test that get_bank_account_balances sorts by date in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(mock_session, sort_by=SortFieldBankAccountBalance.DATE, sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_bank_account_balances raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_bank_account_balances(mock_session, sort_by="INVALID_FIELD")

    def test_get_bank_account_balances_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_bank_account_balances raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_bank_account_balances(mock_session, sort_order="INVALID_ORDER")

    ################################################################################
    # Test get_bank_account_balance_by_id method
    ################################################################################

    def test_get_bank_account_balance_by_id_returns_balance_when_found(self, repository, mock_session):
        """Test that get_bank_account_balance_by_id returns balance when found."""
        # Arrange
        balance_id = 1
        expected_balance = BankAccountBalanceFactory.build(id=balance_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_balance

        # Act
        result = repository.get_bank_account_balance_by_id(balance_id, mock_session)

        # Assert
        assert result == expected_balance
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balance_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_bank_account_balance_by_id returns None when balance not found."""
        # Arrange
        balance_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_bank_account_balance_by_id(balance_id, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Test create_bank_account_balance method
    ################################################################################

    def test_create_bank_account_balance_creates_and_returns_balance(self, repository, mock_session, sample_balance_data):
        """Test that create_bank_account_balance creates and returns a balance."""
        # Arrange
        expected_balance = BankAccountBalanceFactory.build(**sample_balance_data)
        with patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalance', return_value=expected_balance):
            # Act
            result = repository.create_bank_account_balance(sample_balance_data, mock_session)

            # Assert
            assert result == expected_balance
            mock_session.add.assert_called_once_with(expected_balance)
            mock_session.flush.assert_called_once()

    def test_create_bank_account_balance_handles_empty_data(self, repository, mock_session):
        """Test that create_bank_account_balance handles empty data dictionary."""
        # Arrange
        empty_data = {}
        expected_balance = BankAccountBalanceFactory.build()
        with patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalance', return_value=expected_balance):
            # Act
            result = repository.create_bank_account_balance(empty_data, mock_session)

            # Assert
            assert result == expected_balance
            mock_session.add.assert_called_once_with(expected_balance)
            mock_session.flush.assert_called_once()

    ################################################################################
    # Test delete_bank_account_balance method
    ################################################################################

    def test_delete_bank_account_balance_deletes_existing_balance(self, repository, mock_session):
        """Test that delete_bank_account_balance deletes an existing balance."""
        # Arrange
        balance_id = 1
        expected_balance = BankAccountBalanceFactory.build(id=balance_id)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_balance

        # Act
        result = repository.delete_bank_account_balance(balance_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_balance)
        mock_session.flush.assert_called_once()

    def test_delete_bank_account_balance_returns_false_for_nonexistent_balance(self, repository, mock_session):
        """Test that delete_bank_account_balance returns False for nonexistent balance."""
        # Arrange
        balance_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_bank_account_balance(balance_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    ################################################################################
    # Test edge cases and error conditions
    ################################################################################

    def test_get_bank_account_balances_with_none_filters(self, repository, mock_session):
        """Test that get_bank_account_balances handles None filter values correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(
            mock_session,
            bank_account_ids=None,
            currencies=None,
            start_date=None,
            end_date=None
        )

        # Assert
        # Should not call filter when all filters are None
        assert not mock_query.filter.called
        mock_session.query.assert_called_once_with(BankAccountBalance)

    def test_get_bank_account_balances_with_date_range_filtering(self, repository, mock_session):
        """Test that get_bank_account_balances correctly applies date range filtering."""
        # Arrange
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_bank_account_balances(
            mock_session,
            start_date=start_date,
            end_date=end_date
        )

        # Assert
        assert mock_query.filter.call_count == 2  # One for start_date, one for end_date

    def test_create_bank_account_balance_with_complex_data(self, repository, mock_session):
        """Test that create_bank_account_balance handles complex data structures."""
        # Arrange
        complex_data = {
            'bank_account_id': 1,
            'currency': Currency.USD,
            'date': date(2024, 12, 31),
            'balance_statement': 50000.75,
            'balance_adjustment': -2500.25,
            'balance_final': 47500.50
        }
        expected_balance = BankAccountBalanceFactory.build(**complex_data)
        with patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalance', return_value=expected_balance):
            # Act
            result = repository.create_bank_account_balance(complex_data, mock_session)

            # Assert
            assert result == expected_balance
            mock_session.add.assert_called_once_with(expected_balance)
            mock_session.flush.assert_called_once()
