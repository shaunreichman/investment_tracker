"""
Risk Free Rate Service Unit Tests.

This module tests the RiskFreeRateService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Risk free rate retrieval operations
- Risk free rate creation with business rules
- Risk free rate deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.rates.services.risk_free_rate_service import RiskFreeRateService
from src.rates.models import RiskFreeRate
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType, SortFieldRiskFreeRate
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.rates_factories import RiskFreeRateFactory


class TestRiskFreeRateService:
    """Test suite for RiskFreeRateService."""

    @pytest.fixture
    def service(self):
        """Create a RiskFreeRateService instance for testing."""
        return RiskFreeRateService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_risk_free_rate_data(self):
        """Sample risk free rate data for testing."""
        return {
            'currency': Currency.AUD,
            'date': '2024-01-15',
            'rate': 4.25,
            'rate_type': RiskFreeRateType.GOVERNMENT_BOND,
            'source': 'RBA'
        }

    @pytest.fixture
    def sample_risk_free_rate(self, sample_risk_free_rate_data):
        """Create a sample RiskFreeRate instance."""
        return RiskFreeRateFactory.build(**sample_risk_free_rate_data)

    ################################################################################
    # Get Risk Free Rates Tests
    ################################################################################

    def test_get_risk_free_rates_success(self, service, mock_session):
        """Test successful retrieval of risk free rates."""
        # Arrange
        expected_rates = [RiskFreeRateFactory.build() for _ in range(3)]
        service.risk_free_rate_repository.get_risk_free_rates = Mock(return_value=expected_rates)
        
        # Act
        result = service.get_risk_free_rates(mock_session)
        
        # Assert
        assert result == expected_rates
        service.risk_free_rate_repository.get_risk_free_rates.assert_called_once_with(
            mock_session, None, None, SortFieldRiskFreeRate.DATE, SortOrder.ASC
        )

    def test_get_risk_free_rates_with_filters(self, service, mock_session):
        """Test retrieval of risk free rates with filters."""
        # Arrange
        expected_rates = [RiskFreeRateFactory.build() for _ in range(2)]
        service.risk_free_rate_repository.get_risk_free_rates = Mock(return_value=expected_rates)
        
        currency = Currency.USD
        rate_type = RiskFreeRateType.LIBOR
        sort_by = SortFieldRiskFreeRate.CURRENCY
        sort_order = SortOrder.DESC
        
        # Act
        result = service.get_risk_free_rates(
            mock_session, currency, rate_type, sort_by, sort_order
        )
        
        # Assert
        assert result == expected_rates
        service.risk_free_rate_repository.get_risk_free_rates.assert_called_once_with(
            mock_session, currency, rate_type, sort_by, sort_order
        )

    def test_get_risk_free_rate_by_id_success(self, service, mock_session, sample_risk_free_rate):
        """Test successful retrieval of risk free rate by ID."""
        # Arrange
        rate_id = 1
        service.risk_free_rate_repository.get_risk_free_rate_by_id = Mock(return_value=sample_risk_free_rate)
        
        # Act
        result = service.get_risk_free_rate_by_id(rate_id, mock_session)
        
        # Assert
        assert result == sample_risk_free_rate
        service.risk_free_rate_repository.get_risk_free_rate_by_id.assert_called_once_with(rate_id, mock_session)

    def test_get_risk_free_rate_by_id_not_found(self, service, mock_session):
        """Test retrieval of non-existent risk free rate by ID."""
        # Arrange
        rate_id = 999
        service.risk_free_rate_repository.get_risk_free_rate_by_id = Mock(return_value=None)
        
        # Act
        result = service.get_risk_free_rate_by_id(rate_id, mock_session)
        
        # Assert
        assert result is None
        service.risk_free_rate_repository.get_risk_free_rate_by_id.assert_called_once_with(rate_id, mock_session)

    ################################################################################
    # Create Risk Free Rate Tests
    ################################################################################

    def test_create_risk_free_rate_success(self, service, mock_session, sample_risk_free_rate_data, sample_risk_free_rate):
        """Test successful creation of risk free rate."""
        # Arrange
        service.risk_free_rate_repository.create_risk_free_rate = Mock(return_value=sample_risk_free_rate)
        
        # Act
        result = service.create_risk_free_rate(sample_risk_free_rate_data, mock_session)
        
        # Assert
        assert result == sample_risk_free_rate
        service.risk_free_rate_repository.create_risk_free_rate.assert_called_once_with(
            sample_risk_free_rate_data, mock_session
        )

    def test_create_risk_free_rate_failure(self, service, mock_session, sample_risk_free_rate_data):
        """Test creation failure raises ValueError."""
        # Arrange
        service.risk_free_rate_repository.create_risk_free_rate = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create risk free rate"):
            service.create_risk_free_rate(sample_risk_free_rate_data, mock_session)

    ################################################################################
    # Delete Risk Free Rate Tests
    ################################################################################

    def test_delete_risk_free_rate_success(self, service, mock_session, sample_risk_free_rate):
        """Test successful deletion of risk free rate."""
        # Arrange
        rate_id = 1
        service.get_risk_free_rate_by_id = Mock(return_value=sample_risk_free_rate)
        service.risk_free_rate_repository.delete_risk_free_rate = Mock(return_value=True)
        
        # Act
        result = service.delete_risk_free_rate(rate_id, mock_session)
        
        # Assert
        assert result is True
        service.get_risk_free_rate_by_id.assert_called_once_with(rate_id, mock_session)
        service.risk_free_rate_repository.delete_risk_free_rate.assert_called_once_with(rate_id, mock_session)

    def test_delete_risk_free_rate_not_found(self, service, mock_session):
        """Test deletion of non-existent risk free rate raises ValueError."""
        # Arrange
        rate_id = 999
        service.get_risk_free_rate_by_id = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Risk free rate not found"):
            service.delete_risk_free_rate(rate_id, mock_session)

    def test_delete_risk_free_rate_repository_failure(self, service, mock_session, sample_risk_free_rate):
        """Test repository deletion failure raises ValueError."""
        # Arrange
        rate_id = 1
        service.get_risk_free_rate_by_id = Mock(return_value=sample_risk_free_rate)
        service.risk_free_rate_repository.delete_risk_free_rate = Mock(return_value=False)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete risk free rate"):
            service.delete_risk_free_rate(rate_id, mock_session)

    ################################################################################
    # Service Initialization Tests
    ################################################################################

    def test_service_initialization(self):
        """Test service initializes with repository."""
        # Act
        service = RiskFreeRateService()
        
        # Assert
        assert hasattr(service, 'risk_free_rate_repository')
        assert service.risk_free_rate_repository is not None

    ################################################################################
    # Integration Tests
    ################################################################################

    def test_service_repository_integration(self, service, mock_session):
        """Test service properly delegates to repository methods."""
        # Arrange
        expected_rates = [RiskFreeRateFactory.build() for _ in range(2)]
        service.risk_free_rate_repository.get_risk_free_rates = Mock(return_value=expected_rates)
        
        # Act
        result = service.get_risk_free_rates(mock_session)
        
        # Assert
        assert result == expected_rates
        # Verify the repository method was called with correct parameters
        service.risk_free_rate_repository.get_risk_free_rates.assert_called_once()

    def test_create_and_delete_workflow(self, service, mock_session, sample_risk_free_rate_data, sample_risk_free_rate):
        """Test complete create and delete workflow."""
        # Arrange
        service.risk_free_rate_repository.create_risk_free_rate = Mock(return_value=sample_risk_free_rate)
        service.get_risk_free_rate_by_id = Mock(return_value=sample_risk_free_rate)
        service.risk_free_rate_repository.delete_risk_free_rate = Mock(return_value=True)
        
        # Act - Create
        created_rate = service.create_risk_free_rate(sample_risk_free_rate_data, mock_session)
        
        # Act - Delete
        delete_result = service.delete_risk_free_rate(created_rate.id, mock_session)
        
        # Assert
        assert created_rate == sample_risk_free_rate
        assert delete_result is True
        service.risk_free_rate_repository.create_risk_free_rate.assert_called_once()
        service.risk_free_rate_repository.delete_risk_free_rate.assert_called_once()
