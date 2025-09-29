"""
Banking Validation Service Unit Tests.

This module tests the BankingValidationService class, focusing on business rule
validation logic. Tests are precise and focused on validation functionality
without testing repository logic directly.

Test Coverage:
- Bank deletion validation
- Bank account deletion validation
- Dependency checking logic
- Error message generation
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.banking.services.banking_validation_service import BankingValidationService
from tests.factories.banking_factories import BankAccountFactory
from tests.factories.fund_factories import FundEventCashFlowFactory
from unittest.mock import Mock as MockObject


class TestBankingValidationService:
    """Test suite for BankingValidationService."""

    @pytest.fixture
    def service(self):
        """Create a BankingValidationService instance for testing."""
        return BankingValidationService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    ################################################################################
    # Test validate_bank_deletion method
    ################################################################################

    def test_validate_bank_deletion_returns_empty_errors_when_no_dependencies(self, service, mock_session):
        """Test that validate_bank_deletion returns empty errors when bank has no dependent accounts."""
        # Arrange
        bank_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_get_accounts:
            # Act
            errors = service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_accounts.assert_called_once_with(mock_session, bank_id=bank_id)

    def test_validate_bank_deletion_returns_error_when_dependent_accounts_exist(self, service, mock_session):
        """Test that validate_bank_deletion returns error when bank has dependent accounts."""
        # Arrange
        bank_id = 1
        dependent_accounts = [BankAccountFactory.build() for _ in range(2)]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=dependent_accounts) as mock_get_accounts:
            # Act
            errors = service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            assert 'bank_accounts' in errors
            assert errors['bank_accounts'] == ["Cannot delete bank with dependent bank accounts"]
            mock_get_accounts.assert_called_once_with(mock_session, bank_id=bank_id)

    def test_validate_bank_deletion_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_deletion calls repository with correct parameters."""
        # Arrange
        bank_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_get_accounts:
            # Act
            service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            mock_get_accounts.assert_called_once_with(mock_session, bank_id=bank_id)

    def test_validate_bank_deletion_handles_multiple_dependent_accounts(self, service, mock_session):
        """Test that validate_bank_deletion handles multiple dependent accounts correctly."""
        # Arrange
        bank_id = 1
        dependent_accounts = [BankAccountFactory.build() for _ in range(5)]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=dependent_accounts) as mock_get_accounts:
            # Act
            errors = service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            assert 'bank_accounts' in errors
            assert errors['bank_accounts'] == ["Cannot delete bank with dependent bank accounts"]
            # The error message should be the same regardless of number of accounts
            assert len(errors['bank_accounts']) == 1

    ################################################################################
    # Test validate_bank_account_deletion method
    ################################################################################

    def test_validate_bank_account_deletion_returns_empty_errors_when_no_dependencies(self, service, mock_session):
        """Test that validate_bank_account_deletion returns empty errors when account has no dependent fund events."""
        # Arrange
        bank_account_id = 1
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_events.assert_called_once_with(mock_session, bank_account_id=bank_account_id)

    def test_validate_bank_account_deletion_returns_error_when_dependent_fund_events_exist(self, service, mock_session):
        """Test that validate_bank_account_deletion returns error when account has dependent fund events."""
        # Arrange
        bank_account_id = 1
        dependent_events = [MockObject() for _ in range(2)]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=dependent_events) as mock_get_events:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'fund_events' in errors
            assert errors['fund_events'] == ["Cannot delete bank account with dependent fund events"]
            mock_get_events.assert_called_once_with(mock_session, bank_account_id=bank_account_id)

    def test_validate_bank_account_deletion_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_account_deletion calls repository with correct parameters."""
        # Arrange
        bank_account_id = 1
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events:
            # Act
            service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            mock_get_events.assert_called_once_with(mock_session, bank_account_id=bank_account_id)

    def test_validate_bank_account_deletion_handles_multiple_dependent_events(self, service, mock_session):
        """Test that validate_bank_account_deletion handles multiple dependent events correctly."""
        # Arrange
        bank_account_id = 1
        dependent_events = [MockObject() for _ in range(5)]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=dependent_events) as mock_get_events:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'fund_events' in errors
            assert errors['fund_events'] == ["Cannot delete bank account with dependent fund events"]
            # The error message should be the same regardless of number of events
            assert len(errors['fund_events']) == 1

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.bank_account_repository is not None
        assert service.fund_event_cash_flow_repository is not None
        assert hasattr(service, 'bank_account_repository')
        assert hasattr(service, 'fund_event_cash_flow_repository')

    ################################################################################
    # Test edge cases and error handling
    ################################################################################

    def test_validate_bank_deletion_with_none_bank_id(self, service, mock_session):
        """Test that validate_bank_deletion handles None bank_id gracefully."""
        # Arrange
        bank_id = None
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_get_accounts:
            # Act
            errors = service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_accounts.assert_called_once_with(mock_session, bank_id=bank_id)

    def test_validate_bank_account_deletion_with_none_account_id(self, service, mock_session):
        """Test that validate_bank_account_deletion handles None account_id gracefully."""
        # Arrange
        bank_account_id = None
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_events.assert_called_once_with(mock_session, bank_account_id=bank_account_id)

    def test_validate_bank_deletion_with_repository_exception(self, service, mock_session):
        """Test that validate_bank_deletion handles repository exceptions gracefully."""
        # Arrange
        bank_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_accounts', side_effect=Exception("Database error")) as mock_get_accounts:
            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                service.validate_bank_deletion(bank_id, mock_session)

    def test_validate_bank_account_deletion_with_repository_exception(self, service, mock_session):
        """Test that validate_bank_account_deletion handles repository exceptions gracefully."""
        # Arrange
        bank_account_id = 1
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', side_effect=Exception("Database error")) as mock_get_events:
            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                service.validate_bank_account_deletion(bank_account_id, mock_session)
