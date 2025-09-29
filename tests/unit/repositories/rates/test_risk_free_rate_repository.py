"""
Risk Free Rate Repository Unit Tests.

This module tests the RiskFreeRateRepository class, focusing on data access operations,
caching behavior, and error handling. Tests are precise and focused on repository
functionality without testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Caching behavior and cache invalidation
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.rates.repositories.risk_free_rate_repository import RiskFreeRateRepository
from src.rates.models import RiskFreeRate
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType, SortFieldRiskFreeRate
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.rates_factories import RiskFreeRateFactory


class TestRiskFreeRateRepository:
    """Test suite for RiskFreeRateRepository."""

    @pytest.fixture
    def repository(self):
        """Create a RiskFreeRateRepository instance for testing."""
        return RiskFreeRateRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_risk_free_rate_data(self):
        """Sample risk free rate data for testing."""
        return {
            'currency': Currency.AUD,
            'date': date(2024, 1, 15),
            'rate': 4.25,
            'rate_type': RiskFreeRateType.GOVERNMENT_BOND,
            'source': 'RBA'
        }

    @pytest.fixture
    def sample_risk_free_rates(self):
        """Create sample risk free rates for testing."""
        return [
            RiskFreeRateFactory.build(
                id=1,
                currency=Currency.AUD,
                date=date(2024, 1, 15),
                rate=4.25,
                rate_type=RiskFreeRateType.GOVERNMENT_BOND
            ),
            RiskFreeRateFactory.build(
                id=2,
                currency=Currency.USD,
                date=date(2024, 1, 16),
                rate=5.10,
                rate_type=RiskFreeRateType.LIBOR
            ),
            RiskFreeRateFactory.build(
                id=3,
                currency=Currency.AUD,
                date=date(2024, 1, 17),
                rate=4.30,
                rate_type=RiskFreeRateType.GOVERNMENT_BOND
            )
        ]

    ################################################################################
    # Test get_risk_free_rates
    ################################################################################

    def test_get_risk_free_rates_all(self, repository, mock_session, sample_risk_free_rates):
        """Test getting all risk free rates."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_risk_free_rates

        # Act
        result = repository.get_risk_free_rates(mock_session)

        # Assert
        assert result == sample_risk_free_rates
        mock_session.query.assert_called_once_with(RiskFreeRate)
        mock_query.order_by.assert_called_once()

    def test_get_risk_free_rates_with_currency_filter(self, repository, mock_session, sample_risk_free_rates):
        """Test getting risk free rates filtered by currency."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_risk_free_rates[0], sample_risk_free_rates[2]]

        # Act
        result = repository.get_risk_free_rates(mock_session, currency=Currency.AUD)

        # Assert
        assert len(result) == 2
        assert mock_query.filter.call_count == 1

    def test_get_risk_free_rates_with_rate_type_filter(self, repository, mock_session, sample_risk_free_rates):
        """Test getting risk free rates filtered by rate type."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_risk_free_rates[1]]

        # Act
        result = repository.get_risk_free_rates(mock_session, rate_type=RiskFreeRateType.LIBOR)

        # Assert
        assert len(result) == 1
        assert mock_query.filter.call_count == 1

    def test_get_risk_free_rates_with_multiple_filters(self, repository, mock_session, sample_risk_free_rates):
        """Test getting risk free rates with multiple filters."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = [sample_risk_free_rates[0]]

        # Act
        result = repository.get_risk_free_rates(
            mock_session,
            currency=Currency.AUD,
            rate_type=RiskFreeRateType.GOVERNMENT_BOND
        )

        # Assert
        assert len(result) == 1
        assert mock_query.filter.call_count == 2

    def test_get_risk_free_rates_sort_by_currency_asc(self, repository, mock_session, sample_risk_free_rates):
        """Test sorting risk free rates by currency in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_risk_free_rates

        # Act
        repository.get_risk_free_rates(
            mock_session,
            sort_by=SortFieldRiskFreeRate.CURRENCY,
            sort_order=SortOrder.ASC
        )

        # Assert
        assert mock_query.order_by.call_count == 1

    def test_get_risk_free_rates_sort_by_date_desc(self, repository, mock_session, sample_risk_free_rates):
        """Test sorting risk free rates by date in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_risk_free_rates

        # Act
        repository.get_risk_free_rates(
            mock_session,
            sort_by=SortFieldRiskFreeRate.DATE,
            sort_order=SortOrder.DESC
        )

        # Assert
        assert mock_query.order_by.call_count == 1

    def test_get_risk_free_rates_caching(self, repository, mock_session, sample_risk_free_rates):
        """Test that get_risk_free_rates uses caching."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = sample_risk_free_rates

        # Act - First call
        result1 = repository.get_risk_free_rates(mock_session)
        
        # Act - Second call (should use cache)
        result2 = repository.get_risk_free_rates(mock_session)

        # Assert
        assert result1 == result2
        assert mock_session.query.call_count == 1  # Only called once due to caching

    def test_get_risk_free_rates_invalid_sort_field(self, repository, mock_session):
        """Test that invalid sort field raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_risk_free_rates(mock_session, sort_by="INVALID_FIELD")

    def test_get_risk_free_rates_invalid_sort_order(self, repository, mock_session):
        """Test that invalid sort order raises ValueError."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_risk_free_rates(mock_session, sort_order="INVALID_ORDER")

    ################################################################################
    # Test get_risk_free_rate_by_id
    ################################################################################

    def test_get_risk_free_rate_by_id_found(self, repository, mock_session, sample_risk_free_rates):
        """Test getting a risk free rate by ID when found."""
        # Arrange
        target_rate = sample_risk_free_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate

        # Act
        result = repository.get_risk_free_rate_by_id(1, mock_session)

        # Assert
        assert result == target_rate
        mock_session.query.assert_called_once_with(RiskFreeRate)
        assert mock_query.filter.call_count == 1

    def test_get_risk_free_rate_by_id_not_found(self, repository, mock_session):
        """Test getting a risk free rate by ID when not found."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_risk_free_rate_by_id(999, mock_session)

        # Assert
        assert result is None

    def test_get_risk_free_rate_by_id_caching(self, repository, mock_session, sample_risk_free_rates):
        """Test that get_risk_free_rate_by_id uses caching."""
        # Arrange
        target_rate = sample_risk_free_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate

        # Act - First call
        result1 = repository.get_risk_free_rate_by_id(1, mock_session)
        
        # Act - Second call (should use cache)
        result2 = repository.get_risk_free_rate_by_id(1, mock_session)

        # Assert
        assert result1 == result2
        assert mock_session.query.call_count == 1  # Only called once due to caching

    ################################################################################
    # Test create_risk_free_rate
    ################################################################################

    def test_create_risk_free_rate_success(self, repository, mock_session, sample_risk_free_rate_data):
        """Test creating a risk free rate successfully."""
        # Arrange
        created_rate = RiskFreeRateFactory.build(**sample_risk_free_rate_data)
        mock_session.add = Mock()
        mock_session.flush = Mock()

        with patch('src.rates.repositories.risk_free_rate_repository.RiskFreeRate') as mock_model:
            mock_model.return_value = created_rate

            # Act
            result = repository.create_risk_free_rate(sample_risk_free_rate_data, mock_session)

            # Assert
            assert result == created_rate
            mock_session.add.assert_called_once_with(created_rate)
            mock_session.flush.assert_called_once()

    def test_create_risk_free_rate_clears_cache(self, repository, mock_session, sample_risk_free_rate_data):
        """Test that creating a risk free rate clears relevant caches."""
        # Arrange
        created_rate = RiskFreeRateFactory.build(**sample_risk_free_rate_data)
        mock_session.add = Mock()
        mock_session.flush = Mock()

        # Add some data to cache
        repository._cache['risk_free_rate:1'] = created_rate
        repository._cache['risk_free_rates:currency:AUD'] = [created_rate]

        with patch('src.rates.repositories.risk_free_rate_repository.RiskFreeRate') as mock_model:
            mock_model.return_value = created_rate

            # Act
            repository.create_risk_free_rate(sample_risk_free_rate_data, mock_session)

            # Assert
            assert 'risk_free_rate:1' not in repository._cache
            assert 'risk_free_rates:currency:AUD' not in repository._cache

    ################################################################################
    # Test delete_risk_free_rate
    ################################################################################

    def test_delete_risk_free_rate_success(self, repository, mock_session, sample_risk_free_rates):
        """Test deleting a risk free rate successfully."""
        # Arrange
        target_rate = sample_risk_free_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate
        mock_session.delete = Mock()
        mock_session.flush = Mock()

        # Act
        result = repository.delete_risk_free_rate(1, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(target_rate)
        mock_session.flush.assert_called_once()

    def test_delete_risk_free_rate_not_found(self, repository, mock_session):
        """Test deleting a risk free rate that doesn't exist."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_risk_free_rate(999, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()

    def test_delete_risk_free_rate_clears_cache(self, repository, mock_session, sample_risk_free_rates):
        """Test that deleting a risk free rate clears relevant caches."""
        # Arrange
        target_rate = sample_risk_free_rates[0]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = target_rate
        mock_session.delete = Mock()
        mock_session.flush = Mock()

        # Add some data to cache
        repository._cache['risk_free_rate:1'] = target_rate
        repository._cache['risk_free_rates:currency:AUD'] = [target_rate]

        # Act
        repository.delete_risk_free_rate(1, mock_session)

        # Assert
        assert 'risk_free_rate:1' not in repository._cache
        assert 'risk_free_rates:currency:AUD' not in repository._cache

    ################################################################################
    # Test cache management
    ################################################################################

    def test_clear_risk_free_rate_caches(self, repository):
        """Test clearing all risk free rate caches."""
        # Arrange
        repository._cache = {
            'risk_free_rate:1': 'data1',
            'risk_free_rates:currency:AUD': 'data2',
            'other_data': 'data3'
        }

        # Act
        repository._clear_risk_free_rate_caches()

        # Assert
        assert repository._cache == {'other_data': 'data3'}

    def test_clear_uniqueness_cache(self, repository):
        """Test clearing specific uniqueness cache."""
        # Arrange
        cache_key = 'risk_free_rate:unique:AUD:date:2024-01-15:rate_type:GOVERNMENT_BOND'
        repository._cache = {
            cache_key: 'data1',
            'other_data': 'data2'
        }

        # Act
        repository.clear_uniqueness_cache(Currency.AUD, date(2024, 1, 15), RiskFreeRateType.GOVERNMENT_BOND)

        # Assert
        assert cache_key not in repository._cache
        assert 'other_data' in repository._cache

    def test_clear_cache(self, repository):
        """Test clearing all caches."""
        # Arrange
        repository._cache = {
            'risk_free_rate:1': 'data1',
            'other_data': 'data2'
        }

        # Act
        repository.clear_cache()

        # Assert
        assert repository._cache == {}

    ################################################################################
    # Test repository initialization
    ################################################################################

    def test_repository_initialization_default_cache_ttl(self):
        """Test repository initialization with default cache TTL."""
        # Act
        repo = RiskFreeRateRepository()

        # Assert
        assert repo._cache_ttl == 300
        assert repo._cache == {}

    def test_repository_initialization_custom_cache_ttl(self):
        """Test repository initialization with custom cache TTL."""
        # Act
        repo = RiskFreeRateRepository(cache_ttl=600)

        # Assert
        assert repo._cache_ttl == 600
        assert repo._cache == {}
