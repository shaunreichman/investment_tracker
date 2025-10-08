"""
Bank Account Balance Adjustment Service Unit Tests.

This module tests the BankAccountBalanceAdjustmentService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Balance adjustment calculation logic
- Fund event cash flow processing
- Domain field change tracking
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date, timedelta

from src.banking.services.bank_account_balance_adjustment_service import BankAccountBalanceAdjustmentService
from src.banking.models import BankAccountBalance
from src.fund.models import FundEventCashFlow
from src.shared.models import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_event_cash_flow_enums import CashFlowDirection
from tests.factories.banking_factories import BankAccountBalanceFactory
from tests.factories.fund_factories import FundEventCashFlowFactory


class TestBankAccountBalanceAdjustmentService:
    """Test suite for BankAccountBalanceAdjustmentService."""

    @pytest.fixture
    def service(self):
        """Create a BankAccountBalanceAdjustmentService instance for testing."""
        return BankAccountBalanceAdjustmentService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_bank_account_balance(self):
        """Sample bank account balance for testing."""
        return BankAccountBalanceFactory.build(
            id=1,
            bank_account_id=100,
            date=date(2024, 3, 31),  # Last day of March
            balance_statement=10000.0,
            balance_adjustment=0.0,
            balance_final=10000.0
        )

    @pytest.fixture
    def sample_cash_flows_different_months(self):
        """Sample cash flows with different months for fund event and transfer dates."""
        return [
            FundEventCashFlowFactory.build(
                id=1,
                bank_account_id=100,
                fund_event_date=date(2024, 2, 15),  # February
                transfer_date=date(2024, 3, 5),     # March - different month
                amount=1000.0,
                adjusted_bank_account_balance_id=None
            ),
            FundEventCashFlowFactory.build(
                id=2,
                bank_account_id=100,
                fund_event_date=date(2024, 3, 20),  # March
                transfer_date=date(2024, 2, 10),    # February - different month
                amount=500.0,
                adjusted_bank_account_balance_id=None
            )
        ]

    @pytest.fixture
    def sample_cash_flows_same_month(self):
        """Sample cash flows with same month for fund event and transfer dates."""
        return [
            FundEventCashFlowFactory.build(
                id=3,
                bank_account_id=100,
                fund_event_date=date(2024, 3, 15),  # March
                transfer_date=date(2024, 3, 20),    # March - same month
                amount=2000.0,
                adjusted_bank_account_balance_id=None
            )
        ]

    ################################################################################
    # Test calculate_bank_account_balance_adjustment method
    ################################################################################

    def test_calculate_adjustment_with_different_month_cash_flows(self, service, mock_session, sample_bank_account_balance, sample_cash_flows_different_months):
        """Test balance adjustment calculation with cash flows in different months."""
        # Arrange
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=sample_cash_flows_different_months) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(sample_bank_account_balance, mock_session)

            # Assert
            assert len(result) == 4  # 2 balance changes + 2 cash flow changes
            
            # Check balance adjustment change
            balance_adjustment_change = next((change for change in result if change.field_name == 'balance_adjustment'), None)
            assert balance_adjustment_change is not None
            assert balance_adjustment_change.domain_object_type == DomainObjectType.BANK_ACCOUNT_BALANCE
            assert balance_adjustment_change.domain_object_id == 1
            assert balance_adjustment_change.old_value == 0.0
            assert balance_adjustment_change.new_value == -500.0  # 1000 - 500 = 500, but transfer after fund event = -1000, transfer before fund event = +500

            # Check balance final change
            balance_final_change = next((change for change in result if change.field_name == 'balance_final'), None)
            assert balance_final_change is not None
            assert balance_final_change.domain_object_type == DomainObjectType.BANK_ACCOUNT_BALANCE
            assert balance_final_change.domain_object_id == 1
            assert balance_final_change.old_value == 10000.0
            assert balance_final_change.new_value == 9500.0  # 10000 + (-500) = 9500

            # Check cash flow changes
            cash_flow_changes = [change for change in result if change.domain_object_type == DomainObjectType.FUND_EVENT_CASH_FLOW]
            assert len(cash_flow_changes) == 2
            for change in cash_flow_changes:
                assert change.field_name == 'adjusted_bank_account_balance_id'
                assert change.old_value is None
                assert change.new_value == 1

            # Verify repository was called with correct parameters
            expected_start_date = date(2024, 3, 1)  # Start of March
            expected_end_date = date(2024, 4, 30)   # End of April (March + 1 month)
            mock_repo.assert_called_once_with(
                mock_session,
                bank_account_ids=[100],
                different_month=True,
                start_fund_event_date=expected_start_date,
                end_fund_event_date=expected_end_date,
                start_transfer_date=expected_start_date,
                end_transfer_date=expected_end_date
            )

    def test_calculate_adjustment_with_same_month_cash_flows(self, service, mock_session, sample_bank_account_balance, sample_cash_flows_same_month):
        """Test balance adjustment calculation with cash flows in same month (should be ignored)."""
        # Arrange
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=sample_cash_flows_same_month) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(sample_bank_account_balance, mock_session)

            # Assert
            assert len(result) == 0  # No changes should be made for same month cash flows

    def test_calculate_adjustment_with_no_cash_flows(self, service, mock_session, sample_bank_account_balance):
        """Test balance adjustment calculation with no cash flows."""
        # Arrange
        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(sample_bank_account_balance, mock_session)

            # Assert
            assert len(result) == 0  # No changes should be made

    def test_calculate_adjustment_updates_existing_balance_adjustment(self, service, mock_session):
        """Test balance adjustment calculation when balance already has an adjustment."""
        # Arrange
        bank_account_balance = BankAccountBalanceFactory.build(
            id=1,
            bank_account_id=100,
            date=date(2024, 3, 31),
            balance_statement=10000.0,
            balance_adjustment=200.0,  # Existing adjustment
            balance_final=10200.0
        )
        
        cash_flows = [
            FundEventCashFlowFactory.build(
                id=1,
                bank_account_id=100,
                fund_event_date=date(2024, 2, 15),
                transfer_date=date(2024, 3, 5),
                amount=500.0,
                adjusted_bank_account_balance_id=None
            )
        ]

        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=cash_flows) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(bank_account_balance, mock_session)

            # Assert
            balance_adjustment_change = next((change for change in result if change.field_name == 'balance_adjustment'), None)
            assert balance_adjustment_change is not None
            assert balance_adjustment_change.old_value == 200.0
            assert balance_adjustment_change.new_value == -500.0  # Service resets and recalculates from 0

    def test_calculate_adjustment_handles_existing_cash_flow_balance_id(self, service, mock_session, sample_bank_account_balance):
        """Test balance adjustment calculation when cash flow already has a balance ID."""
        # Arrange
        cash_flows = [
            FundEventCashFlowFactory.build(
                id=1,
                bank_account_id=100,
                fund_event_date=date(2024, 2, 15),
                transfer_date=date(2024, 3, 5),
                amount=1000.0,
                adjusted_bank_account_balance_id=999  # Existing balance ID
            )
        ]

        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=cash_flows) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(sample_bank_account_balance, mock_session)

            # Assert
            cash_flow_change = next((change for change in result if change.domain_object_type == DomainObjectType.FUND_EVENT_CASH_FLOW), None)
            assert cash_flow_change is not None
            assert cash_flow_change.old_value == 999
            assert cash_flow_change.new_value == 1

    def test_calculate_adjustment_skips_cash_flow_with_same_balance_id(self, service, mock_session, sample_bank_account_balance):
        """Test balance adjustment calculation skips cash flow already linked to this balance."""
        # Arrange
        cash_flows = [
            FundEventCashFlowFactory.build(
                id=1,
                bank_account_id=100,
                fund_event_date=date(2024, 2, 15),
                transfer_date=date(2024, 3, 5),
                amount=1000.0,
                adjusted_bank_account_balance_id=1  # Same as balance ID
            )
        ]

        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=cash_flows) as mock_repo:
            # Act
            result = service.calculate_bank_account_balance_adjustment(sample_bank_account_balance, mock_session)

            # Assert
            # Should still process the cash flow for balance calculation but not update the balance ID
            balance_adjustment_change = next((change for change in result if change.field_name == 'balance_adjustment'), None)
            assert balance_adjustment_change is not None
            assert balance_adjustment_change.new_value == -1000.0

            # Should not have a cash flow change since balance ID is already correct
            cash_flow_changes = [change for change in result if change.domain_object_type == DomainObjectType.FUND_EVENT_CASH_FLOW]
            assert len(cash_flow_changes) == 0

    def test_calculate_adjustment_date_range_calculation(self, service, mock_session):
        """Test that the service calculates the correct date range for cash flow queries."""
        # Arrange
        bank_account_balance = BankAccountBalanceFactory.build(
            id=1,
            bank_account_id=100,
            date=date(2024, 12, 31),  # December 31st
            balance_statement=10000.0,
            balance_adjustment=0.0,
            balance_final=10000.0
        )

        with patch.object(service.fund_event_cash_flow_repository, 'get_fund_event_cash_flows', return_value=[]) as mock_repo:
            # Act
            service.calculate_bank_account_balance_adjustment(bank_account_balance, mock_session)

            # Assert
            expected_start_date = date(2024, 12, 1)  # Start of December
            expected_end_date = date(2025, 1, 31)    # End of January (December + 1 month)
            mock_repo.assert_called_once_with(
                mock_session,
                bank_account_ids=[100],
                different_month=True,
                start_fund_event_date=expected_start_date,
                end_fund_event_date=expected_end_date,
                start_transfer_date=expected_start_date,
                end_transfer_date=expected_end_date
            )

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.domain_update_event_service is not None
        assert service.fund_event_cash_flow_repository is not None
        assert hasattr(service, 'domain_update_event_service')
        assert hasattr(service, 'fund_event_cash_flow_repository')
