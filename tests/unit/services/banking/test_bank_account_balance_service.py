"""
Bank Account Balance Service Unit Tests.

This module tests the BankAccountBalanceService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Bank account balance creation with validation
- Bank account balance retrieval operations
- Bank account balance deletion with cleanup
- Service layer orchestration
- Error handling and validation integration
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.banking.services.bank_account_balance_service import BankAccountBalanceService
from src.banking.models import BankAccountBalance, BankAccount
from src.shared.enums.shared_enums import Currency, SortOrder
from src.banking.enums.bank_account_balance_enums import SortFieldBankAccountBalance
from tests.factories.banking_factories import BankAccountBalanceFactory, BankAccountFactory


class TestBankAccountBalanceService:
    """Test suite for BankAccountBalanceService."""

    @pytest.fixture
    def service(self):
        """Create a BankAccountBalanceService instance for testing."""
        return BankAccountBalanceService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_bank_account_balance_data(self):
        """Sample bank account balance data for testing."""
        return {
            'currency': 'AUD',
            'date': '2024-01-31',  # Last day of month
            'balance_statement': 10000.50
        }

    @pytest.fixture
    def mock_bank_account(self):
        """Mock bank account instance."""
        return BankAccountFactory.build(id=1, account_name='Test Account')

    @pytest.fixture
    def mock_bank_account_balance(self):
        """Mock bank account balance instance."""
        return BankAccountBalanceFactory.build(id=1, bank_account_id=1)

    ################################################################################
    # Test create_bank_account_balance method
    ################################################################################

    def test_create_bank_account_balance_success(self, service, mock_session, sample_bank_account_balance_data, mock_bank_account, mock_bank_account_balance):
        """Test successful bank account balance creation."""
        # Arrange
        bank_account_id = 1
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_balance_creation', return_value={}) as mock_validate, \
             patch.object(service.bank_account_balance_repository, 'create_bank_account_balance', return_value=mock_bank_account_balance) as mock_create, \
             patch.object(service.bank_account_balance_adjustment_service, 'calculate_bank_account_balance_adjustment', return_value=[]) as mock_adjustment, \
             patch.object(service.domain_update_event_service, 'add_domain_field_changes_to_list') as mock_domain_events, \
             patch.object(service, '_update_bank_account_balance', return_value=None) as mock_update_balance:
            
            # Act
            result = service.create_bank_account_balance(bank_account_id, sample_bank_account_balance_data, mock_session)

            # Assert
            assert result == mock_bank_account_balance
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_validate.assert_called_once_with(bank_account_id, sample_bank_account_balance_data, mock_session)
            
            # Verify processed data includes bank_account_id
            expected_data = sample_bank_account_balance_data.copy()
            expected_data['bank_account_id'] = bank_account_id
            mock_create.assert_called_once_with(expected_data, mock_session)
            
            # Verify session operations
            assert mock_session.flush.call_count == 1  # Once after create
            mock_session.refresh.assert_not_called()  # No refresh when no adjustment changes

    def test_create_bank_account_balance_raises_error_when_bank_account_not_found(self, service, mock_session, sample_bank_account_balance_data):
        """Test that create_bank_account_balance raises ValueError when bank account not found."""
        # Arrange
        bank_account_id = 999
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=None) as mock_get_account:
            # Act & Assert
            with pytest.raises(ValueError, match="Bank account not found"):
                service.create_bank_account_balance(bank_account_id, sample_bank_account_balance_data, mock_session)
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)

    def test_create_bank_account_balance_raises_error_when_validation_fails(self, service, mock_session, sample_bank_account_balance_data, mock_bank_account):
        """Test that create_bank_account_balance raises ValueError when validation fails."""
        # Arrange
        bank_account_id = 1
        validation_errors = {'date': ['Bank account balance date must be the last day of the month']}
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_balance_creation', return_value=validation_errors) as mock_validate:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Validation errors"):
                service.create_bank_account_balance(bank_account_id, sample_bank_account_balance_data, mock_session)
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_validate.assert_called_once_with(bank_account_id, sample_bank_account_balance_data, mock_session)

    def test_create_bank_account_balance_raises_error_when_repository_fails(self, service, mock_session, sample_bank_account_balance_data, mock_bank_account):
        """Test that create_bank_account_balance raises ValueError when repository fails."""
        # Arrange
        bank_account_id = 1
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_balance_creation', return_value={}) as mock_validate, \
             patch.object(service.bank_account_balance_repository, 'create_bank_account_balance', return_value=None) as mock_create:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to create bank account balance"):
                service.create_bank_account_balance(bank_account_id, sample_bank_account_balance_data, mock_session)
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_validate.assert_called_once_with(bank_account_id, sample_bank_account_balance_data, mock_session)

    def test_create_bank_account_balance_with_adjustment_changes(self, service, mock_session, sample_bank_account_balance_data, mock_bank_account, mock_bank_account_balance):
        """Test bank account balance creation with balance adjustment changes."""
        # Arrange
        bank_account_id = 1
        adjustment_changes = [{'field': 'balance_adjustment', 'old_value': 0.0, 'new_value': 100.0}]
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.banking_validation_service, 'validate_bank_account_balance_creation', return_value={}) as mock_validate, \
             patch.object(service.bank_account_balance_repository, 'create_bank_account_balance', return_value=mock_bank_account_balance) as mock_create, \
             patch.object(service.bank_account_balance_adjustment_service, 'calculate_bank_account_balance_adjustment', return_value=adjustment_changes) as mock_adjustment, \
             patch.object(service.domain_update_event_service, 'add_domain_field_changes_to_list') as mock_domain_events, \
             patch.object(service, '_update_bank_account_balance', return_value=None) as mock_update_balance:
            
            # Act
            result = service.create_bank_account_balance(bank_account_id, sample_bank_account_balance_data, mock_session)

            # Assert
            assert result == mock_bank_account_balance
            mock_adjustment.assert_called_once_with(mock_bank_account_balance, mock_session)
            mock_domain_events.assert_called_once()
            assert mock_session.flush.call_count == 2  # Once after create, once after adjustment
            mock_session.refresh.assert_called_once_with(mock_bank_account_balance)

    ################################################################################
    # Test get_bank_account_balance_by_id method
    ################################################################################

    def test_get_bank_account_balance_by_id_success(self, service, mock_session, mock_bank_account_balance):
        """Test successful retrieval of bank account balance by ID."""
        # Arrange
        balance_id = 1
        
        with patch.object(service.bank_account_balance_repository, 'get_bank_account_balance_by_id', return_value=mock_bank_account_balance) as mock_get:
            # Act
            result = service.get_bank_account_balance_by_id(balance_id, mock_session)

            # Assert
            assert result == mock_bank_account_balance
            mock_get.assert_called_once_with(balance_id, mock_session)

    def test_get_bank_account_balance_by_id_returns_none_when_not_found(self, service, mock_session):
        """Test that get_bank_account_balance_by_id returns None when not found."""
        # Arrange
        balance_id = 999
        
        with patch.object(service.bank_account_balance_repository, 'get_bank_account_balance_by_id', return_value=None) as mock_get:
            # Act
            result = service.get_bank_account_balance_by_id(balance_id, mock_session)

            # Assert
            assert result is None
            mock_get.assert_called_once_with(balance_id, mock_session)

    ################################################################################
    # Test delete_bank_account_balance method
    ################################################################################

    def test_delete_bank_account_balance_success(self, service, mock_session, mock_bank_account_balance):
        """Test successful bank account balance deletion."""
        # Arrange
        balance_id = 1
        
        with patch.object(service.bank_account_balance_repository, 'get_bank_account_balance_by_id', return_value=mock_bank_account_balance) as mock_get, \
             patch.object(service.bank_account_balance_repository, 'delete_bank_account_balance', return_value=True) as mock_delete, \
             patch('src.fund.services.fund_event_cash_flow_service.FundEventCashFlowService') as mock_cash_flow_service_class, \
             patch.object(service, '_update_bank_account_balance', return_value=None) as mock_update_balance:
            
            # Mock the cash flow service and its methods
            mock_cash_flow_service = Mock()
            mock_cash_flow_service_class.return_value = mock_cash_flow_service
            mock_cash_flow_service.get_fund_event_cash_flows.return_value = []
            
            # Act
            result = service.delete_bank_account_balance(balance_id, mock_session)

            # Assert
            assert result is True
            mock_get.assert_called_once_with(balance_id, mock_session)
            mock_delete.assert_called_once_with(balance_id, mock_session)
            mock_session.flush.assert_called_once()

    def test_delete_bank_account_balance_raises_error_when_not_found(self, service, mock_session):
        """Test that delete_bank_account_balance raises ValueError when balance not found."""
        # Arrange
        balance_id = 999
        
        with patch.object(service.bank_account_balance_repository, 'get_bank_account_balance_by_id', return_value=None) as mock_get:
            # Act & Assert
            with pytest.raises(ValueError, match="Bank account balance not found"):
                service.delete_bank_account_balance(balance_id, mock_session)
            
            mock_get.assert_called_once_with(balance_id, mock_session)

    def test_delete_bank_account_balance_raises_error_when_repository_fails(self, service, mock_session, mock_bank_account_balance):
        """Test that delete_bank_account_balance raises ValueError when repository fails."""
        # Arrange
        balance_id = 1
        
        with patch.object(service.bank_account_balance_repository, 'get_bank_account_balance_by_id', return_value=mock_bank_account_balance) as mock_get, \
             patch.object(service.bank_account_balance_repository, 'delete_bank_account_balance', return_value=False) as mock_delete:
            
            # Act & Assert
            with pytest.raises(ValueError, match="Failed to delete bank account balance"):
                service.delete_bank_account_balance(balance_id, mock_session)
            
            mock_get.assert_called_once_with(balance_id, mock_session)
            mock_delete.assert_called_once_with(balance_id, mock_session)

    ################################################################################
    # Test _update_bank_account_balance method
    ################################################################################

    def test_update_bank_account_balance_with_balance_change(self, service, mock_session):
        """Test _update_bank_account_balance when current balance changes."""
        # Arrange
        bank_account_id = 1
        old_balance = 5000.0
        new_balance = 7500.0
        
        mock_bank_account = BankAccountFactory.build(id=bank_account_id, current_balance=old_balance)
        mock_latest_balance = BankAccountBalanceFactory.build(balance_final=new_balance)
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[mock_latest_balance]) as mock_get_balances:
            
            # Act
            result = service._update_bank_account_balance(bank_account_id, mock_session)
            
            # Assert
            assert result is not None
            assert result.domain_object_id == bank_account_id
            assert result.field_name == 'current_balance'
            assert result.old_value == old_balance
            assert result.new_value == new_balance  # Should be the balance_final value, not the object
            assert mock_bank_account.current_balance == new_balance  # Should be the balance_final value
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_get_balances.assert_called_once()

    def test_update_bank_account_balance_no_change(self, service, mock_session):
        """Test _update_bank_account_balance when balance doesn't change."""
        # Arrange
        bank_account_id = 1
        current_balance = 5000.0
        
        mock_bank_account = BankAccountFactory.build(id=bank_account_id, current_balance=current_balance)
        mock_latest_balance = BankAccountBalanceFactory.build(balance_final=current_balance)
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[mock_latest_balance]) as mock_get_balances:
            
            # Act
            result = service._update_bank_account_balance(bank_account_id, mock_session)
            
            # Assert
            # When balances are equal, no change should be detected and None should be returned
            assert result is None  # No change detected, should return None
            assert mock_bank_account.current_balance == current_balance  # Balance unchanged
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_get_balances.assert_called_once()

    def test_update_bank_account_balance_handles_empty_balances_list(self, service, mock_session):
        """Test _update_bank_account_balance handles empty balances list gracefully."""
        # Arrange
        bank_account_id = 1
        current_balance = 5000.0
        
        mock_bank_account = BankAccountFactory.build(id=bank_account_id, current_balance=current_balance)
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            
            # Act
            result = service._update_bank_account_balance(bank_account_id, mock_session)
            
            # Assert
            # Service now handles empty list by setting new_current_balance = 0.0
            assert result is not None
            assert result.old_value == current_balance
            assert result.new_value == 0.0
            assert mock_bank_account.current_balance == 0.0
            
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_get_balances.assert_called_once()

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.bank_account_balance_repository is not None
        assert service.bank_account_repository is not None
        assert service.banking_validation_service is not None
        assert service.bank_account_balance_adjustment_service is not None
        assert service.domain_update_event_service is not None

    ################################################################################
    # Focused test for _update_bank_account_balance method
    ################################################################################

    def test_update_bank_account_balance_core_logic(self, service, mock_session):
        """Focused test for _update_bank_account_balance core logic - balance calculation and update."""
        # Arrange
        bank_account_id = 1
        old_balance = 1000.0
        new_balance = 2500.0
        
        mock_bank_account = BankAccountFactory.build(id=bank_account_id, current_balance=old_balance)
        mock_latest_balance = BankAccountBalanceFactory.build(balance_final=new_balance)
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_account, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[mock_latest_balance]) as mock_get_balances:
            
            # Act
            result = service._update_bank_account_balance(bank_account_id, mock_session)
            
            # Assert - Core functionality verification
            assert result is not None, "Should return DomainFieldChange when balance changes"
            assert result.domain_object_id == bank_account_id
            assert result.field_name == 'current_balance'
            assert result.old_value == old_balance
            assert result.new_value == new_balance, "Should use balance_final value, not entire object"
            assert mock_bank_account.current_balance == new_balance, "Bank account current_balance should be updated"
            
            # Verify repository calls
            mock_get_account.assert_called_once_with(bank_account_id, mock_session)
            mock_get_balances.assert_called_once_with(
                mock_session, 
                bank_account_ids=[bank_account_id], 
                sort_by=SortFieldBankAccountBalance.DATE, 
                sort_order=SortOrder.DESC
            )
