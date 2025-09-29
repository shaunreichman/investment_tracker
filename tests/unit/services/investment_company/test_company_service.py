"""
Company Service Unit Tests.

This module tests the CompanyService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Company retrieval operations
- Company creation with business rules
- Company deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.investment_company.services.company_service import CompanyService
from src.investment_company.models import InvestmentCompany
from src.investment_company.enums.company_enums import CompanyType, CompanyStatus, SortFieldCompany
from src.shared.enums.shared_enums import SortOrder
from tests.factories.investment_company_factories import InvestmentCompanyFactory


class TestCompanyService:
    """Test suite for CompanyService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyService instance for testing."""
        return CompanyService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_company_data(self):
        """Sample company data for testing."""
        return {
            'name': 'Test Company',
            'description': 'A test investment company',
            'website': 'https://testcompany.com',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'business_address': '123 Test Street, Test City'
        }

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        return InvestmentCompanyFactory.build(id=1, name='Test Company')

    ################################################################################
    # Test get_companies method
    ################################################################################

    def test_get_companies_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_companies calls repository with correct parameters."""
        # Arrange
        expected_companies = [InvestmentCompanyFactory.build() for _ in range(2)]
        with patch.object(service.company_repository, 'get_companies', return_value=expected_companies) as mock_repo:
            # Act
            result = service.get_companies(mock_session)

            # Assert
            assert result == expected_companies
            mock_repo.assert_called_once_with(
                mock_session, 
                None, 
                None, 
                None, 
                None,
                None
            )

    def test_get_companies_passes_filters_to_repository(self, service, mock_session):
        """Test that get_companies passes all filters to repository."""
        # Arrange
        name = "Test Company"
        company_type = CompanyType.PRIVATE_EQUITY
        status = CompanyStatus.ACTIVE
        sort_by = SortFieldCompany.NAME
        sort_order = SortOrder.DESC
        expected_companies = [InvestmentCompanyFactory.build()]
        
        with patch.object(service.company_repository, 'get_companies', return_value=expected_companies) as mock_repo:
            # Act
            result = service.get_companies(
                mock_session, 
                company_type=company_type,
                status=status,
                name=name,
                sort_by=sort_by,
                sort_order=sort_order
            )

            # Assert
            assert result == expected_companies
            mock_repo.assert_called_once_with(
                mock_session, 
                company_type, 
                status, 
                name, 
                sort_by,
                sort_order
            )

    ################################################################################
    # Test get_company_by_id method
    ################################################################################

    def test_get_company_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_company):
        """Test that get_company_by_id calls repository with correct ID."""
        # Arrange
        company_id = 1
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_repo:
            # Act
            result = service.get_company_by_id(company_id, mock_session)

            # Assert
            assert result == mock_company
            mock_repo.assert_called_once_with(company_id, mock_session)

    def test_get_company_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_company_by_id returns None when company not found."""
        # Arrange
        company_id = 999
        with patch.object(service.company_repository, 'get_company_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_company_by_id(company_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(company_id, mock_session)

    ################################################################################
    # Test create_company method
    ################################################################################

    def test_create_company_sets_status_to_inactive(self, service, mock_session, sample_company_data, mock_company):
        """Test that create_company sets status to INACTIVE by default."""
        # Arrange
        with patch.object(service.company_repository, 'create_company', return_value=mock_company) as mock_repo:
            # Act
            result = service.create_company(sample_company_data, mock_session)

            # Assert
            assert result == mock_company
            # Verify that status was set to INACTIVE
            expected_data = sample_company_data.copy()
            expected_data['status'] = CompanyStatus.INACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    def test_create_company_raises_error_when_repository_fails(self, service, mock_session, sample_company_data):
        """Test that create_company raises ValueError when repository fails."""
        # Arrange
        with patch.object(service.company_repository, 'create_company', return_value=None) as mock_repo:
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create company"):
                service.create_company(sample_company_data, mock_session)

    def test_create_company_preserves_original_data(self, service, mock_session, mock_company):
        """Test that create_company preserves original data while adding status."""
        # Arrange
        company_data = {
            'name': 'Test Company',
            'description': 'A test company',
            'website': 'https://test.com',
            'company_type': CompanyType.PRIVATE_EQUITY,
            'business_address': '123 Test Street',
            'custom_field': 'custom_value'
        }
        
        with patch.object(service.company_repository, 'create_company', return_value=mock_company) as mock_repo:
            # Act
            result = service.create_company(company_data, mock_session)

            # Assert
            assert result == mock_company
            expected_data = company_data.copy()
            expected_data['status'] = CompanyStatus.INACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    ################################################################################
    # Test delete_company method
    ################################################################################

    def test_delete_company_successfully_deletes_company(self, service, mock_session, mock_company):
        """Test successful company deletion."""
        # Arrange
        company_id = 1
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.company_validation_service, 'validate_company_deletion', return_value={}) as mock_validate, \
             patch.object(service.company_repository, 'delete_company', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_company(company_id, mock_session)

            # Assert
            assert result is True
            mock_get_company.assert_called_once_with(company_id, mock_session)
            mock_validate.assert_called_once_with(mock_company, mock_session)
            mock_delete.assert_called_once_with(company_id, mock_session)

    def test_delete_company_raises_error_when_company_not_found(self, service, mock_session):
        """Test that delete_company raises ValueError when company not found."""
        # Arrange
        company_id = 999
        with patch.object(service.company_repository, 'get_company_by_id', return_value=None) as mock_get_company:
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.delete_company(company_id, mock_session)
            
            mock_get_company.assert_called_once_with(company_id, mock_session)

    def test_delete_company_raises_error_when_validation_fails(self, service, mock_session, mock_company):
        """Test that delete_company raises ValueError when validation fails."""
        # Arrange
        company_id = 1
        validation_errors = {'funds': ['Cannot delete company with 2 funds']}
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.company_validation_service, 'validate_company_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_company(company_id, mock_session)
            
            mock_get_company.assert_called_once_with(company_id, mock_session)
            mock_validate.assert_called_once_with(mock_company, mock_session)

    def test_delete_company_raises_error_when_repository_fails(self, service, mock_session, mock_company):
        """Test that delete_company raises ValueError when repository deletion fails."""
        # Arrange
        company_id = 1
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.company_validation_service, 'validate_company_deletion', return_value={}) as mock_validate, \
             patch.object(service.company_repository, 'delete_company', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete company"):
                service.delete_company(company_id, mock_session)
            
            mock_get_company.assert_called_once_with(company_id, mock_session)
            mock_validate.assert_called_once_with(mock_company, mock_session)
            mock_delete.assert_called_once_with(company_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.company_validation_service is not None
        assert service.company_repository is not None
        assert hasattr(service, 'company_validation_service')
        assert hasattr(service, 'company_repository')
