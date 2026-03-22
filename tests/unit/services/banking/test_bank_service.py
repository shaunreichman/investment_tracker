"""
Bank Service Unit Tests.

This module tests the BankService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Bank retrieval operations
- Bank creation with business rules
- Bank deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.banking.services.bank_service import BankService
from src.banking.models import Bank
from src.banking.enums.bank_enums import BankType, BankStatus, SortFieldBank
from src.shared.enums.shared_enums import Country, SortOrder
from tests.factories.banking_factories import BankFactory


class TestBankService:
    """Test suite for BankService."""

    @pytest.fixture
    def service(self):
        """Create a BankService instance for testing."""
        return BankService()

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

    @pytest.fixture
    def mock_bank(self):
        """Mock bank instance."""
        return BankFactory.build(id=1, name='Test Bank')

    ################################################################################
    # Test get_banks method
    ################################################################################

    def test_get_banks_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_banks calls repository with correct parameters."""
        # Arrange
        expected_banks = [BankFactory.build() for _ in range(2)]
        with patch.object(service.bank_repository, 'get_banks', return_value=expected_banks) as mock_repo:
            # Act
            result = service.get_banks(mock_session)

            # Assert
            assert result == expected_banks
            mock_repo.assert_called_once_with(
                mock_session, 
                None, 
                None, 
                None, 
                SortFieldBank.NAME,
                SortOrder.ASC
            )

    def test_get_banks_passes_filters_to_repository(self, service, mock_session):
        """Test that get_banks passes all filters to repository."""
        # Arrange
        name = "Test Bank"
        country = Country.AU
        bank_type = BankType.COMMERCIAL
        expected_banks = [BankFactory.build()]
        
        with patch.object(service.bank_repository, 'get_banks', return_value=expected_banks) as mock_repo:
            # Act
            result = service.get_banks(
                mock_session, 
                names=[name], 
                countries=[country], 
                bank_types=[bank_type]
            )

            # Assert
            assert result == expected_banks
            mock_repo.assert_called_once_with(
                mock_session, 
                [name], 
                [country], 
                [bank_type], 
                SortFieldBank.NAME,
                SortOrder.ASC
            )

    ################################################################################
    # Test get_bank_by_id method
    ################################################################################

    def test_get_bank_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_bank):
        """Test that get_bank_by_id calls repository with correct ID."""
        # Arrange
        bank_id = 1
        with patch.object(service.bank_repository, 'get_bank_by_id', return_value=mock_bank) as mock_repo:
            # Act
            result = service.get_bank_by_id(bank_id, mock_session)

            # Assert
            assert result == mock_bank
            mock_repo.assert_called_once_with(bank_id, mock_session)

    def test_get_bank_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_bank_by_id returns None when bank not found."""
        # Arrange
        bank_id = 999
        with patch.object(service.bank_repository, 'get_bank_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_bank_by_id(bank_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(bank_id, mock_session)

    ################################################################################
    # Test create_bank method
    ################################################################################

    def test_create_bank_sets_status_to_inactive(self, service, mock_session, sample_bank_data, mock_bank):
        """Test that create_bank sets status to INACTIVE by default."""
        # Arrange
        with patch.object(service.bank_repository, 'create_bank', return_value=mock_bank) as mock_repo:
            # Act
            result = service.create_bank(sample_bank_data, mock_session)

            # Assert
            assert result == mock_bank
            # Verify that status was set to INACTIVE
            expected_data = sample_bank_data.copy()
            expected_data['status'] = BankStatus.INACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    def test_create_bank_raises_error_when_repository_fails(self, service, mock_session, sample_bank_data):
        """Test that create_bank raises ValueError when repository fails."""
        # Arrange
        with patch.object(service.bank_repository, 'create_bank', return_value=None) as mock_repo:
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create bank"):
                service.create_bank(sample_bank_data, mock_session)

    def test_create_bank_preserves_original_data(self, service, mock_session, mock_bank):
        """Test that create_bank preserves original data while adding status."""
        # Arrange
        bank_data = {
            'name': 'Test Bank',
            'country': 'AU',
            'bank_type': 'COMMERCIAL',
            'swift_bic': 'TESTAU2X',
            'custom_field': 'custom_value'
        }
        
        with patch.object(service.bank_repository, 'create_bank', return_value=mock_bank) as mock_repo:
            # Act
            result = service.create_bank(bank_data, mock_session)

            # Assert
            assert result == mock_bank
            expected_data = bank_data.copy()
            expected_data['status'] = BankStatus.INACTIVE
            mock_repo.assert_called_once_with(expected_data, mock_session)

    ################################################################################
    # Test delete_bank method
    ################################################################################

    def test_delete_bank_successfully_deletes_bank(self, service, mock_session, mock_bank):
        """Test successful bank deletion."""
        # Arrange
        bank_id = 1
        with patch.object(service, 'get_bank_by_id', return_value=mock_bank) as mock_get_bank, \
             patch.object(service.banking_validation_service, 'validate_bank_deletion', return_value={}) as mock_validate, \
             patch.object(service.bank_repository, 'delete_bank', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_bank(bank_id, mock_session)

            # Assert
            assert result is True
            mock_get_bank.assert_called_once_with(bank_id, mock_session)
            mock_validate.assert_called_once_with(bank_id, mock_session)
            mock_delete.assert_called_once_with(bank_id, mock_session)

    def test_delete_bank_raises_error_when_bank_not_found(self, service, mock_session):
        """Test that delete_bank raises ValueError when bank not found."""
        # Arrange
        bank_id = 999
        with patch.object(service, 'get_bank_by_id', return_value=None) as mock_get_bank:
            # Act & Assert
            with pytest.raises(ValueError, match="Bank not found"):
                service.delete_bank(bank_id, mock_session)
            
            mock_get_bank.assert_called_once_with(bank_id, mock_session)

    def test_delete_bank_raises_error_when_validation_fails(self, service, mock_session, mock_bank):
        """Test that delete_bank raises ValueError when validation fails."""
        # Arrange
        bank_id = 1
        validation_errors = {'bank_accounts': ['Cannot delete bank with dependent bank accounts']}
        
        with patch.object(service, 'get_bank_by_id', return_value=mock_bank) as mock_get_bank, \
             patch.object(service.banking_validation_service, 'validate_bank_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_bank(bank_id, mock_session)
            
            mock_get_bank.assert_called_once_with(bank_id, mock_session)
            mock_validate.assert_called_once_with(bank_id, mock_session)

    def test_delete_bank_raises_error_when_repository_fails(self, service, mock_session, mock_bank):
        """Test that delete_bank raises ValueError when repository deletion fails."""
        # Arrange
        bank_id = 1
        with patch.object(service, 'get_bank_by_id', return_value=mock_bank) as mock_get_bank, \
             patch.object(service.banking_validation_service, 'validate_bank_deletion', return_value={}) as mock_validate, \
             patch.object(service.bank_repository, 'delete_bank', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete bank"):
                service.delete_bank(bank_id, mock_session)
            
            mock_get_bank.assert_called_once_with(bank_id, mock_session)
            mock_validate.assert_called_once_with(bank_id, mock_session)
            mock_delete.assert_called_once_with(bank_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.banking_validation_service is not None
        assert service.bank_repository is not None
        assert hasattr(service, 'banking_validation_service')
        assert hasattr(service, 'bank_repository')
