"""
Fund Service Unit Tests.

This module tests the FundService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Fund retrieval operations
- Fund creation with business rules and company updates
- Fund deletion with dependency validation and company updates
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_service import FundService
from src.fund.models import Fund
from src.fund.enums.fund_enums import FundStatus, FundTrackingType, SortFieldFund, FundTaxStatementFinancialYearType
from src.shared.enums.shared_enums import Country, SortOrder
from tests.factories.fund_factories import FundFactory


class TestFundService:
    """Test suite for FundService."""

    @pytest.fixture
    def service(self):
        """Create a FundService instance for testing."""
        return FundService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_fund_data(self):
        """Sample fund data for testing."""
        return {
            'name': 'Test Fund',
            'fund_investment_type': 'PRIVATE_EQUITY',
            'tracking_type': 'COST_BASED',
            'description': 'Test fund description',
            'currency': 'AUD',
            'tax_jurisdiction': Country.AU,
            'expected_irr': 15.5,
            'expected_duration_months': 60,
            'commitment_amount': 100000.0,
            'investment_company_id': 1,
            'entity_id': 1
        }

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance."""
        return FundFactory.build(id=1, name='Test Fund', investment_company_id=1)

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        company = Mock()
        company.id = 1
        company.total_funds = 5
        company.total_funds_active = 3
        company.total_commitment_amount = 500000.0
        return company

    ################################################################################
    # Test get_funds method
    ################################################################################

    def test_get_funds_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_funds calls repository with correct parameters."""
        # Arrange
        expected_funds = [FundFactory.build() for _ in range(2)]
        with patch.object(service.fund_repository, 'get_funds', return_value=expected_funds) as mock_repo:
            # Act
            result = service.get_funds(mock_session)

            # Assert
            assert result == expected_funds
            mock_repo.assert_called_once_with(
                mock_session, 
                None, 
                None, 
                None, 
                None,
                SortFieldFund.START_DATE,
                SortOrder.ASC
            )

    def test_get_funds_passes_filters_to_repository(self, service, mock_session):
        """Test that get_funds passes all filters to repository."""
        # Arrange
        company_id = 1
        entity_id = 2
        fund_status = FundStatus.ACTIVE
        fund_tracking_type = FundTrackingType.COST_BASED
        sort_by = SortFieldFund.NAME
        sort_order = SortOrder.DESC
        expected_funds = [FundFactory.build()]
        
        with patch.object(service.fund_repository, 'get_funds', return_value=expected_funds) as mock_repo:
            # Act
            result = service.get_funds(
                mock_session,
                company_ids=[company_id],
                entity_ids=[entity_id],
                fund_statuses=[fund_status],
                fund_tracking_types=[fund_tracking_type],
                sort_by=sort_by,
                sort_order=sort_order
            )

            # Assert
            assert result == expected_funds
            mock_repo.assert_called_once_with(
                mock_session,
                [company_id],
                [entity_id],
                [fund_status],
                [fund_tracking_type],
                sort_by,
                sort_order
            )

    ################################################################################
    # Test get_fund_by_id method
    ################################################################################

    def test_get_fund_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_fund):
        """Test that get_fund_by_id calls repository with correct ID."""
        # Arrange
        fund_id = 1
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_repo:
            # Act
            result = service.get_fund_by_id(fund_id, mock_session)

            # Assert
            assert result == mock_fund
            mock_repo.assert_called_once_with(fund_id, mock_session)

    def test_get_fund_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_fund_by_id returns None when fund not found."""
        # Arrange
        fund_id = 999
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_fund_by_id(fund_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(fund_id, mock_session)

    ################################################################################
    # Test create_fund method
    ################################################################################

    def test_create_fund_sets_tax_statement_financial_year_type_and_status(self, service, mock_session, sample_fund_data, mock_fund, mock_company):
        """Test that create_fund sets tax statement financial year type and status."""
        # Arrange
        with patch.object(service.fund_repository, 'create_fund', return_value=mock_fund) as mock_repo, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=mock_company) as mock_get_company:
            
            # Act
            result = service.create_fund(sample_fund_data, mock_session)

            # Assert
            assert result == mock_fund
            # Verify that tax statement financial year type and status were set
            expected_data = sample_fund_data.copy()
            expected_data['tax_statement_financial_year_type'] = FundTaxStatementFinancialYearType.HALF_YEAR  # AU maps to HALF_YEAR
            expected_data['status'] = FundStatus.ACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    def test_create_fund_raises_error_when_repository_fails(self, service, mock_session, sample_fund_data):
        """Test that create_fund raises ValueError when repository fails."""
        # Arrange
        with patch.object(service.fund_repository, 'create_fund', return_value=None) as mock_repo:
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create fund"):
                service.create_fund(sample_fund_data, mock_session)

    def test_create_fund_updates_company_totals(self, service, mock_session, sample_fund_data, mock_fund, mock_company):
        """Test that create_fund updates company totals correctly."""
        # Arrange
        mock_fund.investment_company_id = 1
        mock_fund.commitment_amount = 100000.0
        
        with patch.object(service.fund_repository, 'create_fund', return_value=mock_fund) as mock_repo, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=mock_company) as mock_get_company:
            
            # Act
            result = service.create_fund(sample_fund_data, mock_session)

            # Assert
            assert result == mock_fund
            # Verify company totals were updated
            assert mock_company.total_funds == 6  # 5 + 1
            assert mock_company.total_funds_active == 4  # 3 + 1
            assert mock_company.total_commitment_amount == 600000.0  # 500000 + 100000

    def test_create_fund_raises_error_when_company_not_found(self, service, mock_session, sample_fund_data, mock_fund):
        """Test that create_fund raises ValueError when company not found."""
        # Arrange
        mock_fund.investment_company_id = 1
        
        with patch.object(service.fund_repository, 'create_fund', return_value=mock_fund) as mock_repo, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=None) as mock_get_company:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.create_fund(sample_fund_data, mock_session)

    def test_create_fund_preserves_original_data(self, service, mock_session, mock_fund, mock_company):
        """Test that create_fund preserves original data while adding required fields."""
        # Arrange
        fund_data = {
            'name': 'Test Fund',
            'fund_investment_type': 'PRIVATE_EQUITY',
            'tracking_type': 'COST_BASED',
            'description': 'Test fund description',
            'currency': 'AUD',
            'tax_jurisdiction': Country.AU,
            'expected_irr': 15.5,
            'expected_duration_months': 60,
            'commitment_amount': 100000.0,
            'investment_company_id': 1,
            'entity_id': 1,
            'custom_field': 'custom_value'
        }
        
        with patch.object(service.fund_repository, 'create_fund', return_value=mock_fund) as mock_repo, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=mock_company) as mock_get_company:
            
            # Act
            result = service.create_fund(fund_data, mock_session)

            # Assert
            assert result == mock_fund
            expected_data = fund_data.copy()
            expected_data['tax_statement_financial_year_type'] = FundTaxStatementFinancialYearType.HALF_YEAR
            expected_data['status'] = FundStatus.ACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    ################################################################################
    # Test delete_fund method
    ################################################################################

    def test_delete_fund_successfully_deletes_fund_and_updates_company(self, service, mock_session, mock_fund, mock_company):
        """Test successful fund deletion with company updates."""
        # Arrange
        fund_id = 1
        mock_fund.investment_company_id = 1
        mock_fund.commitment_amount = 100000.0
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund, \
             patch.object(service.fund_validation_service, 'validate_fund_deletion', return_value={}) as mock_validate, \
             patch.object(service.fund_repository, 'delete_fund', return_value=True) as mock_delete, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=mock_company) as mock_get_company:
            
            # Act
            result = service.delete_fund(fund_id, mock_session)

            # Assert
            assert result is True
            mock_get_fund.assert_called_once_with(fund_id, mock_session)
            mock_validate.assert_called_once_with(mock_fund, mock_session)
            mock_delete.assert_called_once_with(fund_id, mock_session)
            # Verify company totals were updated
            assert mock_company.total_funds == 4  # 5 - 1
            assert mock_company.total_funds_active == 2  # 3 - 1
            assert mock_company.total_commitment_amount == 400000.0  # 500000 - 100000

    def test_delete_fund_raises_error_when_fund_not_found(self, service, mock_session):
        """Test that delete_fund raises ValueError when fund not found."""
        # Arrange
        fund_id = 999
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=None) as mock_get_fund:
            # Act & Assert
            with pytest.raises(ValueError, match="Fund not found"):
                service.delete_fund(fund_id, mock_session)
            
            mock_get_fund.assert_called_once_with(fund_id, mock_session)

    def test_delete_fund_raises_error_when_validation_fails(self, service, mock_session, mock_fund):
        """Test that delete_fund raises ValueError when validation fails."""
        # Arrange
        fund_id = 1
        validation_errors = {'fund_events': ['Cannot delete fund with dependent events']}
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund, \
             patch.object(service.fund_validation_service, 'validate_fund_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_fund(fund_id, mock_session)
            
            mock_get_fund.assert_called_once_with(fund_id, mock_session)
            mock_validate.assert_called_once_with(mock_fund, mock_session)

    def test_delete_fund_raises_error_when_repository_fails(self, service, mock_session, mock_fund):
        """Test that delete_fund raises ValueError when repository deletion fails."""
        # Arrange
        fund_id = 1
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund, \
             patch.object(service.fund_validation_service, 'validate_fund_deletion', return_value={}) as mock_validate, \
             patch.object(service.fund_repository, 'delete_fund', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete fund"):
                service.delete_fund(fund_id, mock_session)
            
            mock_get_fund.assert_called_once_with(fund_id, mock_session)
            mock_validate.assert_called_once_with(mock_fund, mock_session)
            mock_delete.assert_called_once_with(fund_id, mock_session)

    def test_delete_fund_raises_error_when_company_not_found(self, service, mock_session, mock_fund):
        """Test that delete_fund raises ValueError when company not found."""
        # Arrange
        fund_id = 1
        mock_fund.investment_company_id = 1
        
        with patch.object(service.fund_repository, 'get_fund_by_id', return_value=mock_fund) as mock_get_fund, \
             patch.object(service.fund_validation_service, 'validate_fund_deletion', return_value={}) as mock_validate, \
             patch.object(service.fund_repository, 'delete_fund', return_value=True) as mock_delete, \
             patch('src.investment_company.services.company_service.CompanyService') as mock_company_service_class, \
             patch.object(mock_company_service_class.return_value, 'get_company_by_id', return_value=None) as mock_get_company:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.delete_fund(fund_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_validation_service is not None
        assert service.fund_repository is not None
        assert hasattr(service, 'fund_validation_service')
        assert hasattr(service, 'fund_repository')
