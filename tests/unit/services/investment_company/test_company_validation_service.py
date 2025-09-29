"""
Company Validation Service Unit Tests.

This module tests the CompanyValidationService class, focusing on business logic,
validation rules, and service layer orchestration. Tests are precise and focused
on validation functionality without testing repository logic directly.

Test Coverage:
- Company deletion validation
- Business rule validation
- Service layer orchestration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.investment_company.services.company_validation_service import CompanyValidationService
from src.investment_company.models import InvestmentCompany
from src.fund.enums.fund_enums import FundStatus
from tests.factories.investment_company_factories import InvestmentCompanyFactory
from tests.factories.fund_factories import FundFactory


class TestCompanyValidationService:
    """Test suite for CompanyValidationService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyValidationService instance for testing."""
        return CompanyValidationService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        return InvestmentCompanyFactory.build(id=1, name='Test Company')

    @pytest.fixture
    def mock_funds(self):
        """Mock funds instances."""
        return [
            FundFactory.build(id=1, company_id=1, status=FundStatus.ACTIVE),
            FundFactory.build(id=2, company_id=1, status=FundStatus.COMPLETED)
        ]

    ################################################################################
    # Test validate_company_deletion method
    ################################################################################

    def test_validate_company_deletion_allows_deletion_when_no_active_funds(self, service, mock_session, mock_company):
        """Test that validation passes when company has no active funds."""
        # Arrange
        with patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert result == {}
            mock_get_funds.assert_called_once_with(
                session=mock_session, 
                company_id=mock_company.id, 
                fund_status=FundStatus.ACTIVE
            )

    def test_validate_company_deletion_allows_deletion_when_only_completed_funds(self, service, mock_session, mock_company):
        """Test that validation passes when company has only completed funds."""
        # Arrange
        # No active funds should be returned when querying for ACTIVE funds
        with patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert result == {}
            mock_get_funds.assert_called_once_with(
                session=mock_session, 
                company_id=mock_company.id, 
                fund_status=FundStatus.ACTIVE
            )

    def test_validate_company_deletion_prevents_deletion_with_active_funds(self, service, mock_session, mock_company):
        """Test that validation fails when company has active funds."""
        # Arrange
        active_funds = [FundFactory.build(status=FundStatus.ACTIVE) for _ in range(2)]
        with patch.object(service.fund_repository, 'get_funds', return_value=active_funds) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert 'funds' in result
            assert len(result['funds']) == 1
            assert 'Cannot delete company with 2 funds' in result['funds'][0]
            mock_get_funds.assert_called_once_with(
                session=mock_session, 
                company_id=mock_company.id, 
                fund_status=FundStatus.ACTIVE
            )

    def test_validate_company_deletion_prevents_deletion_with_single_active_fund(self, service, mock_session, mock_company):
        """Test that validation fails when company has one active fund."""
        # Arrange
        active_fund = [FundFactory.build(status=FundStatus.ACTIVE)]
        with patch.object(service.fund_repository, 'get_funds', return_value=active_fund) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert 'funds' in result
            assert len(result['funds']) == 1
            assert 'Cannot delete company with 1 funds' in result['funds'][0]
            mock_get_funds.assert_called_once_with(
                session=mock_session, 
                company_id=mock_company.id, 
                fund_status=FundStatus.ACTIVE
            )

    def test_validate_company_deletion_calls_repository_with_correct_parameters(self, service, mock_session, mock_company):
        """Test that validation calls repository with correct parameters."""
        # Arrange
        with patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_get_funds:
            # Act
            service.validate_company_deletion(mock_company, mock_session)

            # Assert
            mock_get_funds.assert_called_once_with(
                session=mock_session, 
                company_id=mock_company.id, 
                fund_status=FundStatus.ACTIVE
            )

    def test_validate_company_deletion_returns_empty_dict_on_success(self, service, mock_session, mock_company):
        """Test that validation returns empty dict when no validation errors."""
        # Arrange
        with patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert isinstance(result, dict)
            assert len(result) == 0

    def test_validate_company_deletion_returns_errors_dict_on_failure(self, service, mock_session, mock_company):
        """Test that validation returns errors dict when validation fails."""
        # Arrange
        active_funds = [FundFactory.build(status=FundStatus.ACTIVE)]
        with patch.object(service.fund_repository, 'get_funds', return_value=active_funds) as mock_get_funds:
            # Act
            result = service.validate_company_deletion(mock_company, mock_session)

            # Assert
            assert isinstance(result, dict)
            assert 'funds' in result
            assert isinstance(result['funds'], list)
            assert len(result['funds']) == 1

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_repository is not None
        assert hasattr(service, 'fund_repository')
