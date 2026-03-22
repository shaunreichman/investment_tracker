"""
Bank Account Service Unit Tests.

This module tests the BankAccountService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Bank account retrieval operations
- Bank account creation with business rules
- Bank account deletion with dependency validation
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.banking.services.bank_account_service import BankAccountService
from src.banking.models import BankAccount
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus, SortFieldBankAccount
from src.shared.enums.shared_enums import Currency, SortOrder
from tests.factories.banking_factories import BankAccountFactory


class TestBankAccountService:
    """Test suite for BankAccountService."""

    @pytest.fixture
    def service(self):
        """Create a BankAccountService instance for testing."""
        return BankAccountService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_bank_account_data(self):
        """Sample bank account data for testing."""
        return {
            'entity_id': 1,
            'account_name': 'Test Account',
            'account_number': '1234-5678-9012-3456',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }

    @pytest.fixture
    def mock_bank_account(self):
        """Mock bank account instance."""
        return BankAccountFactory.build(id=1, account_name='Test Account')

    @pytest.fixture
    def mock_bank(self):
        """Mock bank instance."""
        from tests.factories.banking_factories import BankFactory
        return BankFactory.build(id=1, name='Test Bank')

    @pytest.fixture
    def mock_entity(self):
        """Mock entity instance."""
        from tests.factories.entity_factories import EntityFactory
        return EntityFactory.build(id=1, name='Test Entity')

    ################################################################################
    # Test get_bank_accounts method
    ################################################################################

    def test_get_bank_accounts_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that get_bank_accounts calls repository with correct parameters."""
        # Arrange
        expected_accounts = [BankAccountFactory.build() for _ in range(2)]
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=expected_accounts) as mock_repo:
            # Act
            result = service.get_bank_accounts(mock_session)

            # Assert
            assert result == expected_accounts
            mock_repo.assert_called_once_with(
                mock_session,
                None,
                None,
                None,
                None,
                None,
                None,
                SortFieldBankAccount.CREATED_AT,
                SortOrder.ASC
            )

    def test_get_bank_accounts_passes_filters_to_repository(self, service, mock_session):
        """Test that get_bank_accounts passes all filters to repository."""
        # Arrange
        bank_id = 1
        entity_id = 2
        account_name = "Test Account"
        currency = Currency.AUD
        status = BankAccountStatus.ACTIVE
        account_type = BankAccountType.CHECKING
        expected_accounts = [BankAccountFactory.build()]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=expected_accounts) as mock_repo:
            # Act
            result = service.get_bank_accounts(
                mock_session,
                bank_ids=[bank_id],
                entity_ids=[entity_id],
                account_names=[account_name],
                currencies=[currency],
                statuses=[status],
                account_types=[account_type]
            )

            # Assert
            assert result == expected_accounts
            mock_repo.assert_called_once_with(
                mock_session,
                [bank_id],
                [entity_id],
                [account_name],
                [currency],
                [status],
                [account_type],
                SortFieldBankAccount.CREATED_AT,
                SortOrder.ASC
            )

    ################################################################################
    # Test get_bank_account_by_id method
    ################################################################################

    def test_get_bank_account_by_id_calls_repository_with_correct_id(self, service, mock_session, mock_bank_account):
        """Test that get_bank_account_by_id calls repository with correct ID."""
        # Arrange
        account_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_repo:
            # Act
            result = service.get_bank_account_by_id(account_id, mock_session)

            # Assert
            assert result == mock_bank_account
            mock_repo.assert_called_once_with(account_id, mock_session)

    def test_get_bank_account_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_bank_account_by_id returns None when account not found."""
        # Arrange
        account_id = 999
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=None) as mock_repo:
            # Act
            result = service.get_bank_account_by_id(account_id, mock_session)

            # Assert
            assert result is None
            mock_repo.assert_called_once_with(account_id, mock_session)

    ################################################################################
    # Test create_bank_account method
    ################################################################################

    def test_create_bank_account_validates_bank_exists(self, service, mock_session, sample_bank_account_data, mock_bank, mock_bank_account):
        """Test that create_bank_account validates bank exists before creation."""
        # Arrange
        bank_id = 1
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class, \
             patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(service.bank_account_repository, 'create_bank_account', return_value=mock_bank_account) as mock_repo:
            
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = mock_bank
            
            mock_entity_repo = mock_entity_repo_class.return_value
            mock_entity_repo.get_entity_by_id.return_value = Mock()  # Mock entity
            
            # Act
            result = service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

            # Assert
            assert result == mock_bank_account
            mock_bank_repo.get_bank_by_id.assert_called_once_with(bank_id, mock_session)

    def test_create_bank_account_validates_entity_exists(self, service, mock_session, sample_bank_account_data, mock_bank, mock_bank_account):
        """Test that create_bank_account validates entity exists before creation."""
        # Arrange
        bank_id = 1
        entity_id = sample_bank_account_data['entity_id']
        
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class, \
             patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(service.bank_account_repository, 'create_bank_account', return_value=mock_bank_account) as mock_repo:
            
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = mock_bank
            
            mock_entity_repo = mock_entity_repo_class.return_value
            mock_entity_repo.get_entity_by_id.return_value = Mock()  # Mock entity
            
            # Act
            result = service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

            # Assert
            assert result == mock_bank_account
            mock_entity_repo.get_entity_by_id.assert_called_once_with(entity_id, mock_session)

    def test_create_bank_account_raises_error_when_bank_not_found(self, service, mock_session, sample_bank_account_data):
        """Test that create_bank_account raises ValueError when bank not found."""
        # Arrange
        bank_id = 999
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class:
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError, match="Bank not found"):
                service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

    def test_create_bank_account_raises_error_when_entity_not_found(self, service, mock_session, sample_bank_account_data, mock_bank):
        """Test that create_bank_account raises ValueError when entity not found."""
        # Arrange
        bank_id = 1
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class, \
             patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class:
            
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = mock_bank
            
            mock_entity_repo = mock_entity_repo_class.return_value
            mock_entity_repo.get_entity_by_id.return_value = None
            
            # Act & Assert
            with pytest.raises(ValueError, match="Entity not found"):
                service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

    def test_create_bank_account_sets_status_to_inactive(self, service, mock_session, sample_bank_account_data, mock_bank, mock_bank_account):
        """Test that create_bank_account sets status to INACTIVE by default."""
        # Arrange
        bank_id = 1
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class, \
             patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(service.bank_account_repository, 'create_bank_account', return_value=mock_bank_account) as mock_repo:
            
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = mock_bank
            
            mock_entity_repo = mock_entity_repo_class.return_value
            mock_entity_repo.get_entity_by_id.return_value = Mock()  # Mock entity
            
            # Act
            result = service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

            # Assert
            assert result == mock_bank_account
            # Verify that status was set to INACTIVE and bank_id was added
            expected_data = sample_bank_account_data.copy()
            expected_data['status'] = BankAccountStatus.INACTIVE
            expected_data['bank_id'] = bank_id
            mock_repo.assert_called_once_with(expected_data, mock_session)

    def test_create_bank_account_raises_error_when_repository_fails(self, service, mock_session, sample_bank_account_data, mock_bank):
        """Test that create_bank_account raises ValueError when repository fails."""
        # Arrange
        bank_id = 1
        with patch('src.banking.repositories.bank_repository.BankRepository') as mock_bank_repo_class, \
             patch('src.entity.repositories.entity_repository.EntityRepository') as mock_entity_repo_class, \
             patch.object(service.bank_account_repository, 'create_bank_account', return_value=None) as mock_repo:
            
            mock_bank_repo = mock_bank_repo_class.return_value
            mock_bank_repo.get_bank_by_id.return_value = mock_bank
            
            mock_entity_repo = mock_entity_repo_class.return_value
            mock_entity_repo.get_entity_by_id.return_value = Mock()  # Mock entity
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create bank account"):
                service.create_bank_account(bank_id, sample_bank_account_data, mock_session)

    ################################################################################
    # Test delete_bank_account method
    ################################################################################

    def test_delete_bank_account_successfully_deletes_account(self, service, mock_session, mock_bank_account):
        """Test successful bank account deletion."""
        # Arrange
        account_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_deletion', return_value={}) as mock_validate, \
             patch.object(service.bank_account_repository, 'delete_bank_account', return_value=True) as mock_delete:
            
            # Act
            result = service.delete_bank_account(account_id, mock_session)

            # Assert
            assert result is True
            mock_get_account.assert_called_once_with(account_id, mock_session)
            mock_validate.assert_called_once_with(account_id, mock_session)
            mock_delete.assert_called_once_with(account_id, mock_session)

    def test_delete_bank_account_raises_error_when_account_not_found(self, service, mock_session):
        """Test that delete_bank_account raises ValueError when account not found."""
        # Arrange
        account_id = 999
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=None) as mock_get_account:
            # Act & Assert
            with pytest.raises(ValueError, match="Bank account not found"):
                service.delete_bank_account(account_id, mock_session)
            
            mock_get_account.assert_called_once_with(account_id, mock_session)

    def test_delete_bank_account_raises_error_when_validation_fails(self, service, mock_session, mock_bank_account):
        """Test that delete_bank_account raises ValueError when validation fails."""
        # Arrange
        account_id = 1
        validation_errors = {'fund_events': ['Cannot delete bank account with dependent fund events']}
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_deletion', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Deletion validation failed"):
                service.delete_bank_account(account_id, mock_session)
            
            mock_get_account.assert_called_once_with(account_id, mock_session)
            mock_validate.assert_called_once_with(account_id, mock_session)

    def test_delete_bank_account_raises_error_when_repository_fails(self, service, mock_session, mock_bank_account):
        """Test that delete_bank_account raises ValueError when repository deletion fails."""
        # Arrange
        account_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_deletion', return_value={}) as mock_validate, \
             patch.object(service.bank_account_repository, 'delete_bank_account', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete bank account"):
                service.delete_bank_account(account_id, mock_session)
            
            mock_get_account.assert_called_once_with(account_id, mock_session)
            mock_validate.assert_called_once_with(account_id, mock_session)
            mock_delete.assert_called_once_with(account_id, mock_session)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.banking_validation_service is not None
        assert service.bank_account_repository is not None
        assert hasattr(service, 'banking_validation_service')
        assert hasattr(service, 'bank_account_repository')
