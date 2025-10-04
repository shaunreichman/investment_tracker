"""
FX Rate Repository Unit Tests.

This module tests the FxRateRepository class, focusing on data access operations
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
from datetime import date

from src.rates.repositories.fx_rate_repository import FxRateRepository
from src.rates.models import FxRate
from src.rates.enums.fx_rate_enums import SortFieldFxRate
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.rates_factories import FxRateFactory


class TestFxRateRepository:
    """Test suite for FxRateRepository."""

    @pytest.fixture
    def repository(self):
        """Create a FxRateRepository instance for testing."""
        return FxRateRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_fx_rate_data(self):
        """Sample FX rate data for testing."""
        return {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 1, 15),
            'fx_rate': 0.6523
        }

    @pytest.fixture
    def sample_fx_rates(self):
        """Create sample FX rates for testing."""
        return [
            FxRateFactory.build(
                id=1,
                from_currency=Currency.AUD,
                to_currency=Currency.USD,
                date=date(2024, 1, 15),
                fx_rate=0.6523
            ),
            FxRateFactory.build(
                id=2,
                from_currency=Currency.USD,
                to_currency=Currency.EUR,
                date=date(2024, 1, 16),
                fx_rate=0.9234
            ),
            FxRateFactory.build(
                id=3,
                from_currency=Currency.AUD,
                to_currency=Currency.EUR,
                date=date(2024, 1, 17),
                fx_rate=0.6012
            )
        ]

    ################################################################################
    # Test get_fx_rates
    ################################################################################

    def test_get_fx_rates_all(self, repository, mock_session, sample_fx_rates):
        """Test getting all FX rates."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_fx_rates

        # Act
        result = repository.get_fx_rates(mock_session)

        # Assert
        assert result == sample_fx_rates
        mock_session.query.assert_called_once_with(FxRate)
        mock_query.order_by.assert_called_once()

    def test_get_fx_rates_with_from_currency_filter(self, repository, mock_session, sample_fx_rates):
        """Test getting FX rates filtered by from currency."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fx_rates[0], sample_fx_rates[2]]

        # Act
        result = repository.get_fx_rates(mock_session, from_currency=Currency.AUD)

        # Assert
        assert len(result) == 2
        assert mock_query.filter.call_count == 1

    def test_get_fx_rates_with_to_currency_filter(self, repository, mock_session, sample_fx_rates):
        """Test getting FX rates filtered by to currency."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fx_rates[1]]

        # Act
        result = repository.get_fx_rates(mock_session, to_currency=Currency.EUR)

        # Assert
        assert len(result) == 1
        assert mock_query.filter.call_count == 1

    def test_get_fx_rates_with_date_range_filter(self, repository, mock_session, sample_fx_rates):
        """Test getting FX rates filtered by date range."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fx_rates[1], sample_fx_rates[2]]

        # Act
        result = repository.get_fx_rates(
            mock_session,
            start_date=date(2024, 1, 16),
            end_date=date(2024, 1, 17)
        )

        # Assert
        assert len(result) == 2
        assert mock_query.filter.call_count == 2

    def test_get_fx_rates_with_multiple_filters(self, repository, mock_session, sample_fx_rates):
        """Test getting FX rates with multiple filters."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_fx_rates[0]]

        # Act
        result = repository.get_fx_rates(
            mock_session,
            from_currency=Currency.AUD,
            to_currency=Currency.USD
        )

        # Assert
        assert len(result) == 1
        assert mock_query.filter.call_count == 2

    def test_get_fx_rates_sort_by_date_asc(self, repository, mock_session, sample_fx_rates):
        """Test sorting FX rates by date in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_fx_rates

        # Act
        repository.get_fx_rates(
            mock_session,
            sort_by=SortFieldFxRate.DATE,
            sort_order=SortOrder.ASC
        )

        # Assert
        assert mock_query.order_by.call_count == 1

    def test_get_fx_rates_sort_by_from_currency_desc(self, repository, mock_session, sample_fx_rates):
        """Test sorting FX rates by from currency in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_fx_rates

        # Act
        repository.get_fx_rates(
            mock_session,
            sort_by=SortFieldFxRate.FROM_CURRENCY,
            sort_order=SortOrder.DESC
        )

        # Assert
        assert mock_query.order_by.call_count == 1

    def test_get_fx_rates_sort_by_to_currency_asc(self, repository, mock_session, sample_fx_rates):
        """Test sorting FX rates by to currency in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_fx_rates

        # Act
        repository.get_fx_rates(
            mock_session,
            sort_by=SortFieldFxRate.TO_CURRENCY,
            sort_order=SortOrder.ASC
        )

        # Assert
        assert mock_query.order_by.call_count == 1

    def test_get_fx_rates_invalid_sort_field(self, repository, mock_session):
        """Test that invalid sort field raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_fx_rates(mock_session, sort_by="INVALID_FIELD")

    def test_get_fx_rates_invalid_sort_order(self, repository, mock_session):
        """Test that invalid sort order raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_fx_rates(mock_session, sort_order="INVALID_ORDER")

    ################################################################################
    # Test get_fx_rate_by_id
    ################################################################################

    def test_get_fx_rate_by_id_found(self, repository, mock_session, sample_fx_rates):
        """Test getting an FX rate by ID when found."""
        # Arrange
        target_rate = sample_fx_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate

        # Act
        result = repository.get_fx_rate_by_id(1, mock_session)

        # Assert
        assert result == target_rate
        mock_session.query.assert_called_once_with(FxRate)
        assert mock_query.filter.call_count == 1

    def test_get_fx_rate_by_id_not_found(self, repository, mock_session):
        """Test getting an FX rate by ID when not found."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_fx_rate_by_id(999, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Test create_fx_rate
    ################################################################################

    def test_create_fx_rate_success(self, repository, mock_session, sample_fx_rate_data):
        """Test creating an FX rate successfully."""
        # Arrange
        created_rate = FxRateFactory.build(**sample_fx_rate_data)
        mock_session.add = Mock()
        mock_session.flush = Mock()

        with patch('src.rates.repositories.fx_rate_repository.FxRate') as mock_model:
            mock_model.return_value = created_rate

            # Act
            result = repository.create_fx_rate(sample_fx_rate_data, mock_session)

            # Assert
            assert result == created_rate
            mock_session.add.assert_called_once_with(created_rate)
            mock_session.flush.assert_called_once()

    ################################################################################
    # Test delete_fx_rate
    ################################################################################

    def test_delete_fx_rate_success(self, repository, mock_session, sample_fx_rates):
        """Test deleting an FX rate successfully."""
        # Arrange
        target_rate = sample_fx_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate
        mock_session.delete = Mock()
        mock_session.flush = Mock()

        # Act
        result = repository.delete_fx_rate(1, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(target_rate)
        mock_session.flush.assert_called_once()

    def test_delete_fx_rate_not_found(self, repository, mock_session):
        """Test deleting an FX rate that doesn't exist."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_fx_rate(999, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()
