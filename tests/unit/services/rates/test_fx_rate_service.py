"""
FX Rate Service Unit Tests.

This module tests the FxRateService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- FX rate retrieval operations
- FX rate creation with business rules
- FX rate deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.rates.services.fx_rate_service import FxRateService
from src.rates.models import FxRate
from src.rates.enums.fx_rate_enums import SortFieldFxRate
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.rates_factories import FxRateFactory


class TestFxRateService:
    """Test suite for FxRateService."""

    @pytest.fixture
    def service(self):
        """Create a FxRateService instance for testing."""
        return FxRateService()

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
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 0.6523
        }

    @pytest.fixture
    def sample_fx_rate(self, sample_fx_rate_data):
        """Create a sample FxRate instance."""
        return FxRateFactory.build(**sample_fx_rate_data)

    ################################################################################
    # Get FX Rates Tests
    ################################################################################

    def test_get_fx_rates_success(self, service, mock_session):
        """Test successful retrieval of FX rates."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(3)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        # Act
        result = service.get_fx_rates(mock_session)
        
        # Assert
        assert result == expected_rates
        service.fx_rate_repository.get_fx_rates.assert_called_once_with(
            mock_session, None, None, None, None, SortFieldFxRate.DATE, SortOrder.ASC
        )

    def test_get_fx_rates_with_filters(self, service, mock_session):
        """Test retrieval of FX rates with filters."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        from_currency = Currency.AUD
        to_currency = Currency.USD
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        sort_by = SortFieldFxRate.FROM_CURRENCY
        sort_order = SortOrder.DESC
        
        # Act
        result = service.get_fx_rates(
            mock_session, from_currency, to_currency, start_date, end_date, sort_by, sort_order
        )
        
        # Assert
        assert result == expected_rates
        service.fx_rate_repository.get_fx_rates.assert_called_once_with(
            mock_session, from_currency, to_currency, start_date, end_date, sort_by, sort_order
        )

    def test_get_fx_rates_with_currency_filters_only(self, service, mock_session):
        """Test retrieval of FX rates with only currency filters."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        from_currency = Currency.EUR
        to_currency = Currency.GBP
        
        # Act
        result = service.get_fx_rates(mock_session, from_currency, to_currency)
        
        # Assert
        assert result == expected_rates
        service.fx_rate_repository.get_fx_rates.assert_called_once_with(
            mock_session, from_currency, to_currency, None, None, SortFieldFxRate.DATE, SortOrder.ASC
        )

    def test_get_fx_rates_with_date_range_only(self, service, mock_session):
        """Test retrieval of FX rates with only date range filters."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 31)
        
        # Act
        result = service.get_fx_rates(mock_session, start_date=start_date, end_date=end_date)
        
        # Assert
        assert result == expected_rates
        service.fx_rate_repository.get_fx_rates.assert_called_once_with(
            mock_session, None, None, start_date, end_date, SortFieldFxRate.DATE, SortOrder.ASC
        )

    def test_get_fx_rate_by_id_success(self, service, mock_session, sample_fx_rate):
        """Test successful retrieval of FX rate by ID."""
        # Arrange
        rate_id = 1
        service.fx_rate_repository.get_fx_rate_by_id = Mock(return_value=sample_fx_rate)
        
        # Act
        result = service.get_fx_rate_by_id(rate_id, mock_session)
        
        # Assert
        assert result == sample_fx_rate
        service.fx_rate_repository.get_fx_rate_by_id.assert_called_once_with(rate_id, mock_session)

    def test_get_fx_rate_by_id_not_found(self, service, mock_session):
        """Test retrieval of non-existent FX rate by ID."""
        # Arrange
        rate_id = 999
        service.fx_rate_repository.get_fx_rate_by_id = Mock(return_value=None)
        
        # Act
        result = service.get_fx_rate_by_id(rate_id, mock_session)
        
        # Assert
        assert result is None
        service.fx_rate_repository.get_fx_rate_by_id.assert_called_once_with(rate_id, mock_session)

    ################################################################################
    # Create FX Rate Tests
    ################################################################################

    def test_create_fx_rate_success(self, service, mock_session, sample_fx_rate_data, sample_fx_rate):
        """Test successful creation of FX rate."""
        # Arrange
        service.fx_rate_repository.create_fx_rate = Mock(return_value=sample_fx_rate)
        
        # Act
        result = service.create_fx_rate(sample_fx_rate_data, mock_session)
        
        # Assert
        assert result == sample_fx_rate
        service.fx_rate_repository.create_fx_rate.assert_called_once_with(
            sample_fx_rate_data, mock_session
        )

    def test_create_fx_rate_repository_failure(self, service, mock_session, sample_fx_rate_data):
        """Test repository creation failure raises ValueError."""
        # Arrange
        service.fx_rate_repository.create_fx_rate = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create FX rate"):
            service.create_fx_rate(sample_fx_rate_data, mock_session)

    def test_create_fx_rate_with_different_currencies(self, service, mock_session):
        """Test creation of FX rate with different currency pairs."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.EUR,
            'to_currency': Currency.JPY,
            'date': date(2024, 2, 29),  # Valid last day of month (leap year)
            'fx_rate': 160.25
        }
        created_rate = FxRateFactory.build(**fx_rate_data)
        service.fx_rate_repository.create_fx_rate = Mock(return_value=created_rate)
        
        # Act
        result = service.create_fx_rate(fx_rate_data, mock_session)
        
        # Assert
        assert result == created_rate
        service.fx_rate_repository.create_fx_rate.assert_called_once_with(fx_rate_data, mock_session)

    ################################################################################
    # Delete FX Rate Tests
    ################################################################################

    def test_delete_fx_rate_success(self, service, mock_session, sample_fx_rate):
        """Test successful deletion of FX rate."""
        # Arrange
        rate_id = 1
        service.fx_rate_repository.delete_fx_rate = Mock(return_value=True)
        
        # Act
        result = service.delete_fx_rate(rate_id, mock_session)
        
        # Assert
        assert result is True
        service.fx_rate_repository.delete_fx_rate.assert_called_once_with(rate_id, mock_session)

    def test_delete_fx_rate_repository_failure(self, service, mock_session):
        """Test repository deletion failure raises ValueError."""
        # Arrange
        rate_id = 1
        service.fx_rate_repository.delete_fx_rate = Mock(return_value=False)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete FX rate"):
            service.delete_fx_rate(rate_id, mock_session)

    def test_delete_fx_rate_with_different_ids(self, service, mock_session):
        """Test deletion of FX rates with different IDs."""
        # Arrange
        rate_ids = [1, 2, 3]
        service.fx_rate_repository.delete_fx_rate = Mock(return_value=True)
        
        # Act & Assert
        for rate_id in rate_ids:
            result = service.delete_fx_rate(rate_id, mock_session)
            assert result is True
        
        # Assert all calls were made
        assert service.fx_rate_repository.delete_fx_rate.call_count == len(rate_ids)

    ################################################################################
    # Service Initialization Tests
    ################################################################################

    def test_service_initialization(self):
        """Test service initializes with repository."""
        # Act
        service = FxRateService()
        
        # Assert
        assert hasattr(service, 'fx_rate_repository')
        assert service.fx_rate_repository is not None

    def test_service_initialization_with_custom_repository(self):
        """Test service can be initialized with custom repository."""
        # Arrange
        custom_repository = Mock()
        
        # Act
        service = FxRateService()
        service.fx_rate_repository = custom_repository
        
        # Assert
        assert service.fx_rate_repository == custom_repository

    ################################################################################
    # Integration Tests
    ################################################################################

    def test_service_repository_integration(self, service, mock_session):
        """Test service properly delegates to repository methods."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        # Act
        result = service.get_fx_rates(mock_session)
        
        # Assert
        assert result == expected_rates
        # Verify the repository method was called with correct parameters
        service.fx_rate_repository.get_fx_rates.assert_called_once()

    def test_create_and_delete_workflow(self, service, mock_session, sample_fx_rate_data, sample_fx_rate):
        """Test complete create and delete workflow."""
        # Arrange
        service.fx_rate_repository.create_fx_rate = Mock(return_value=sample_fx_rate)
        service.fx_rate_repository.delete_fx_rate = Mock(return_value=True)
        
        # Act - Create
        created_rate = service.create_fx_rate(sample_fx_rate_data, mock_session)
        
        # Act - Delete
        delete_result = service.delete_fx_rate(created_rate.id, mock_session)
        
        # Assert
        assert created_rate == sample_fx_rate
        assert delete_result is True
        service.fx_rate_repository.create_fx_rate.assert_called_once()
        service.fx_rate_repository.delete_fx_rate.assert_called_once()

    def test_get_rates_with_all_sort_options(self, service, mock_session):
        """Test retrieval with all available sort field options."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        sort_fields = [SortFieldFxRate.DATE, SortFieldFxRate.FROM_CURRENCY, SortFieldFxRate.TO_CURRENCY]
        
        # Act & Assert
        for sort_field in sort_fields:
            result = service.get_fx_rates(mock_session, sort_by=sort_field)
            assert result == expected_rates
        
        # Assert all calls were made
        assert service.fx_rate_repository.get_fx_rates.call_count == len(sort_fields)

    def test_get_rates_with_both_sort_orders(self, service, mock_session):
        """Test retrieval with both ascending and descending sort orders."""
        # Arrange
        expected_rates = [FxRateFactory.build() for _ in range(2)]
        service.fx_rate_repository.get_fx_rates = Mock(return_value=expected_rates)
        
        sort_orders = [SortOrder.ASC, SortOrder.DESC]
        
        # Act & Assert
        for sort_order in sort_orders:
            result = service.get_fx_rates(mock_session, sort_order=sort_order)
            assert result == expected_rates
        
        # Assert all calls were made
        assert service.fx_rate_repository.get_fx_rates.call_count == len(sort_orders)

    ################################################################################
    # Validation Integration Tests
    ################################################################################

    def test_create_fx_rate_validation_invalid_date_not_last_day(self, service, mock_session):
        """Test validation fails for dates that are not last day of month."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 1, 30),  # Invalid: not last day of month
            'fx_rate': 0.6523
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_invalid_rate_zero(self, service, mock_session):
        """Test validation fails for zero rate."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': 0  # Invalid: zero rate
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_invalid_rate_negative(self, service, mock_session):
        """Test validation fails for negative rate."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 1, 31),  # Valid last day of month
            'fx_rate': -1.5  # Invalid: negative rate
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_missing_date(self, service, mock_session):
        """Test validation fails when date is missing."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            # Missing 'date' field
            'fx_rate': 0.6523
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_missing_rate(self, service, mock_session):
        """Test validation fails when rate is missing."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 1, 31),  # Valid last day of month
            # Missing 'fx_rate' field
        }
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_leap_year_valid(self, service, mock_session):
        """Test validation passes for leap year February 29th."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2024, 2, 29),  # Valid last day of month in leap year
            'fx_rate': 0.6523
        }
        service.fx_rate_repository.create_fx_rate = Mock(return_value=FxRateFactory.build(**fx_rate_data))
        
        # Act
        result = service.create_fx_rate(fx_rate_data, mock_session)
        
        # Assert
        assert result is not None
        service.fx_rate_repository.create_fx_rate.assert_called_once_with(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_non_leap_year_valid(self, service, mock_session):
        """Test validation passes for non-leap year February 28th."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': date(2023, 2, 28),  # Valid last day of month in non-leap year
            'fx_rate': 0.6523
        }
        service.fx_rate_repository.create_fx_rate = Mock(return_value=FxRateFactory.build(**fx_rate_data))
        
        # Act
        result = service.create_fx_rate(fx_rate_data, mock_session)
        
        # Assert
        assert result is not None
        service.fx_rate_repository.create_fx_rate.assert_called_once_with(fx_rate_data, mock_session)

    def test_create_fx_rate_validation_string_date_valid(self, service, mock_session):
        """Test validation passes for string date format."""
        # Arrange
        fx_rate_data = {
            'from_currency': Currency.AUD,
            'to_currency': Currency.USD,
            'date': '2024-01-31',  # Valid last day of month as string
            'fx_rate': 0.6523
        }
        service.fx_rate_repository.create_fx_rate = Mock(return_value=FxRateFactory.build(**fx_rate_data))
        
        # Act
        result = service.create_fx_rate(fx_rate_data, mock_session)
        
        # Assert
        assert result is not None
        service.fx_rate_repository.create_fx_rate.assert_called_once_with(fx_rate_data, mock_session)

    ################################################################################
    # Error Handling Tests
    ################################################################################

    def test_create_fx_rate_with_empty_data(self, service, mock_session):
        """Test creation with empty data raises validation error."""
        # Arrange
        empty_data = {}
        
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(empty_data, mock_session)

    def test_create_fx_rate_with_none_data(self, service, mock_session):
        """Test creation with None data raises validation error."""
        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fx_rate(None, mock_session)

    def test_delete_fx_rate_with_invalid_id(self, service, mock_session):
        """Test deletion with invalid ID raises appropriate error."""
        # Arrange
        invalid_id = -1
        service.fx_rate_repository.delete_fx_rate = Mock(return_value=False)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete FX rate"):
            service.delete_fx_rate(invalid_id, mock_session)
