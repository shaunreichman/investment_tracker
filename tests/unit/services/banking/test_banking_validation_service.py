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
from datetime import date


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
            mock_get_accounts.assert_called_once_with(mock_session, bank_ids=[bank_id])

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
            mock_get_accounts.assert_called_once_with(mock_session, bank_ids=[bank_id])

    def test_validate_bank_deletion_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_deletion calls repository with correct parameters."""
        # Arrange
        bank_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_get_accounts:
            # Act
            service.validate_bank_deletion(bank_id, mock_session)

            # Assert
            mock_get_accounts.assert_called_once_with(mock_session, bank_ids=[bank_id])

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
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_events.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])
            mock_get_balances.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])

    def test_validate_bank_account_deletion_returns_error_when_dependent_fund_events_exist(self, service, mock_session):
        """Test that validate_bank_account_deletion returns error when account has dependent fund events."""
        # Arrange
        bank_account_id = 1
        dependent_events = [MockObject() for _ in range(2)]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=dependent_events) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'fund_events' in errors
            assert errors['fund_events'] == ["Cannot delete bank account with dependent fund events"]
            mock_get_events.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])
            mock_get_balances.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])

    def test_validate_bank_account_deletion_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_account_deletion calls repository with correct parameters."""
        # Arrange
        bank_account_id = 1
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            # Act
            service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            mock_get_events.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])
            mock_get_balances.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])

    def test_validate_bank_account_deletion_handles_multiple_dependent_events(self, service, mock_session):
        """Test that validate_bank_account_deletion handles multiple dependent events correctly."""
        # Arrange
        bank_account_id = 1
        dependent_events = [MockObject() for _ in range(5)]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=dependent_events) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'fund_events' in errors
            assert errors['fund_events'] == ["Cannot delete bank account with dependent fund events"]
            # The error message should be the same regardless of number of events
            assert len(errors['fund_events']) == 1

    def test_validate_bank_account_deletion_returns_error_when_dependent_balances_exist(self, service, mock_session):
        """Test that validate_bank_account_deletion returns error when account has dependent bank account balances."""
        # Arrange
        bank_account_id = 1
        dependent_balances = [MockObject() for _ in range(2)]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=dependent_balances) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'bank_account_balances' in errors
            assert errors['bank_account_balances'] == ["Cannot delete bank account with dependent bank account balances"]
            mock_get_events.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])
            mock_get_balances.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])

    def test_validate_bank_account_deletion_returns_multiple_errors_when_both_dependencies_exist(self, service, mock_session):
        """Test that validate_bank_account_deletion returns multiple errors when both fund events and balances exist."""
        # Arrange
        bank_account_id = 1
        dependent_events = [MockObject()]
        dependent_balances = [MockObject()]
        
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=dependent_events) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=dependent_balances) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert 'fund_events' in errors
            assert 'bank_account_balances' in errors
            assert errors['fund_events'] == ["Cannot delete bank account with dependent fund events"]
            assert errors['bank_account_balances'] == ["Cannot delete bank account with dependent bank account balances"]

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
            mock_get_accounts.assert_called_once_with(mock_session, bank_ids=[bank_id])

    def test_validate_bank_account_deletion_with_none_account_id(self, service, mock_session):
        """Test that validate_bank_account_deletion handles None account_id gracefully."""
        # Arrange
        bank_account_id = None
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_get_events, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_get_balances:
            # Act
            errors = service.validate_bank_account_deletion(bank_account_id, mock_session)

            # Assert
            assert errors == {}
            mock_get_events.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])
            mock_get_balances.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id])

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

    ################################################################################
    # Test validate_bank_account_balance_creation method
    ################################################################################

    def test_validate_bank_account_balance_creation_returns_empty_errors_when_valid(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns empty errors when data is valid."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),  # Last day of January
            'balance': 1000.00,
            'currency': 'USD'
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert errors == {}
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)
            mock_calculator.assert_called_once_with(balance_data['date'])
            mock_repo.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id], start_date=balance_data['date'], end_date=balance_data['date'])

    def test_validate_bank_account_balance_creation_returns_error_when_date_missing(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when date is missing."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        # Act
        errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

        # Assert
        assert 'date' in errors
        assert errors['date'] == ["Bank account balance date is required"]

    def test_validate_bank_account_balance_creation_returns_error_when_date_not_last_day_of_month(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when date is not last day of month."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 15),  # Not last day of month
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=False) as mock_calculator:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'date' in errors
            assert errors['date'] == ["Bank account balance date must be the last day of the month"]
            mock_calculator.assert_called_once_with(balance_data['date'])

    def test_validate_bank_account_balance_creation_handles_string_date(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles string date conversion."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': '2024-01-31',  # String date
            'balance': 1000.00,
            'currency': 'USD'
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert errors == {}
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)
            # Verify the calculator was called with the converted date object
            expected_date = date(2024, 1, 31)
            mock_calculator.assert_called_once_with(expected_date)
            mock_repo.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id], start_date=expected_date, end_date=expected_date)

    def test_validate_bank_account_balance_creation_returns_error_when_balance_already_exists(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when balance already exists for date."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        existing_balances = [MockObject()]  # Simulate existing balance
        
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=existing_balances) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'bank_account_balances' in errors
            assert errors['bank_account_balances'] == ["Bank account balance must be unique for the bank account and date"]
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)
            mock_calculator.assert_called_once_with(balance_data['date'])
            mock_repo.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id], start_date=balance_data['date'], end_date=balance_data['date'])

    def test_validate_bank_account_balance_creation_skips_uniqueness_check_when_date_invalid(self, service, mock_session):
        """Test that validate_bank_account_balance_creation skips uniqueness check when date is invalid."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 15),  # Not last day of month
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=False) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances') as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'date' in errors
            assert 'bank_account_balances' not in errors  # Should not check uniqueness
            mock_calculator.assert_called_once_with(balance_data['date'])
            mock_repo.assert_not_called()  # Should not call repository when date is invalid

    def test_validate_bank_account_balance_creation_with_multiple_errors(self, service, mock_session):
        """Test that validate_bank_account_balance_creation can return multiple errors."""
        # Arrange
        bank_account_id = 1
        balance_data = {}  # Missing date and other fields
        
        # Act
        errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

        # Assert
        assert 'date' in errors
        assert errors['date'] == ["Bank account balance date is required"]

    def test_validate_bank_account_balance_creation_calls_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_account_balance_creation calls repository with correct parameters."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)
            mock_calculator.assert_called_once_with(balance_data['date'])
            mock_repo.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id], start_date=balance_data['date'], end_date=balance_data['date'])

    def test_validate_bank_account_balance_creation_with_repository_exception(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles repository exceptions gracefully."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', side_effect=Exception("Database error")) as mock_repo:
            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

    def test_validate_bank_account_balance_creation_with_calculator_exception(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles calculator exceptions gracefully."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', side_effect=Exception("Calculator error")) as mock_calculator:
            # Act & Assert
            with pytest.raises(Exception, match="Calculator error"):
                service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

    def test_validate_bank_account_balance_creation_with_none_bank_account_id(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles None bank_account_id gracefully."""
        # Arrange
        bank_account_id = None
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert errors == {}
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)
            mock_calculator.assert_called_once_with(balance_data['date'])
            mock_repo.assert_called_once_with(mock_session, bank_account_ids=[bank_account_id], start_date=balance_data['date'], end_date=balance_data['date'])

    def test_validate_bank_account_balance_creation_with_empty_balance_data(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles empty balance data."""
        # Arrange
        bank_account_id = 1
        balance_data = {}
        
        # Act
        errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

        # Assert
        assert 'date' in errors
        assert errors['date'] == ["Bank account balance date is required"]

    ################################################################################
    # Test service initialization with new dependencies
    ################################################################################

    def test_service_initializes_with_bank_account_balance_repository(self, service):
        """Test that service initializes with bank account balance repository."""
        # Assert
        assert service.bank_account_balance_repository is not None
        assert hasattr(service, 'bank_account_balance_repository')

    ################################################################################
    # Test bank account validation in balance creation
    ################################################################################

    def test_validate_bank_account_balance_creation_returns_error_when_bank_account_not_found(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when bank account doesn't exist."""
        # Arrange
        bank_account_id = 999  # Non-existent bank account
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=None) as mock_get_bank_account:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'bank_account' in errors
            assert errors['bank_account'] == ["Bank account not found"]
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)

    def test_validate_bank_account_balance_creation_returns_error_when_currency_missing(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when currency is missing."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00
            # currency missing
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'currency' in errors
            assert errors['currency'] == ["Bank account balance currency is required"]

    def test_validate_bank_account_balance_creation_returns_error_when_currency_mismatch(self, service, mock_session):
        """Test that validate_bank_account_balance_creation returns error when currency doesn't match bank account."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'EUR'  # Different from bank account currency
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'currency' in errors
            assert errors['currency'] == ["Bank account balance currency must be the same as the bank account currency"]

    def test_validate_bank_account_balance_creation_handles_currency_validation_when_bank_account_none(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles currency validation when bank account is None."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=None) as mock_get_bank_account:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'bank_account' in errors
            assert errors['bank_account'] == ["Bank account not found"]
            # Currency validation should not cause AttributeError when bank_account is None
            assert 'currency' not in errors  # Currency validation should be skipped

    def test_validate_bank_account_balance_creation_with_multiple_validation_errors(self, service, mock_session):
        """Test that validate_bank_account_balance_creation can return multiple validation errors simultaneously."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 15),  # Not last day of month
            'balance': 1000.00,
            'currency': 'EUR'  # Different from bank account currency
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=False) as mock_calculator:
            # Act
            errors = service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            assert 'date' in errors
            assert errors['date'] == ["Bank account balance date must be the last day of the month"]
            assert 'currency' in errors
            assert errors['currency'] == ["Bank account balance currency must be the same as the bank account currency"]

    def test_validate_bank_account_balance_creation_calls_bank_account_repository_with_correct_parameters(self, service, mock_session):
        """Test that validate_bank_account_balance_creation calls bank account repository with correct parameters."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        mock_bank_account = MockObject()
        mock_bank_account.currency = 'USD'
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', return_value=mock_bank_account) as mock_get_bank_account, \
             patch.object(service.last_day_of_the_month_calculator, 'is_last_day_of_the_month', return_value=True) as mock_calculator, \
             patch.object(service.bank_account_balance_repository, 'get_bank_account_balances', return_value=[]) as mock_repo:
            # Act
            service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)

            # Assert
            mock_get_bank_account.assert_called_once_with(bank_account_id, mock_session)

    def test_validate_bank_account_balance_creation_with_bank_account_repository_exception(self, service, mock_session):
        """Test that validate_bank_account_balance_creation handles bank account repository exceptions gracefully."""
        # Arrange
        bank_account_id = 1
        balance_data = {
            'date': date(2024, 1, 31),
            'balance': 1000.00,
            'currency': 'USD'
        }
        
        with patch.object(service.bank_account_repository, 'get_bank_account_by_id', side_effect=Exception("Database error")) as mock_get_bank_account:
            # Act & Assert
            with pytest.raises(Exception, match="Database error"):
                service.validate_bank_account_balance_creation(bank_account_id, balance_data, mock_session)
