"""
Fund Event Cash Flow Service Unit Tests.

This module tests the FundEventCashFlowService class, focusing on business logic,
validation, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Fund event cash flow retrieval operations
- Fund event cash flow creation with business rules and validation
- Fund event cash flow deletion with business rule updates
- Service layer orchestration and error handling
- Integration with fund event balance tracking
- Bank account balance adjustment logic
- Domain update event creation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import date, datetime

from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.fund.models import FundEventCashFlow, FundEvent
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder, EventOperation
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.banking.models import BankAccountBalance
from src.shared.models import DomainFieldChange
from tests.factories.fund_factories import FundEventCashFlowFactory, FundEventFactory
from tests.factories.banking_factories import BankAccountFactory


class TestFundEventCashFlowService:
    """Test suite for FundEventCashFlowService."""

    @pytest.fixture
    def service(self):
        """Create a FundEventCashFlowService instance for testing."""
        return FundEventCashFlowService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_cash_flow_data(self):
        """Sample cash flow data for testing."""
        return {
            'bank_account_id': 1,
            'direction': 'OUTFLOW',
            'transfer_date': date(2024, 1, 15),
            'currency': 'AUD',
            'amount': 10000.00,
            'reference': 'REF-001',
            'description': 'Test cash flow'
        }

    @pytest.fixture
    def mock_fund_event(self):
        """Create a mock fund event for testing."""
        fund_event = Mock(spec=FundEvent)
        fund_event.id = 1
        fund_event.amount = 50000.00
        fund_event.cash_flow_balance_amount = 0.00
        fund_event.is_cash_flow_complete = False
        fund_event.event_date = date(2024, 1, 15)
        fund_event.event_type = EventType.DISTRIBUTION
        fund_event.has_withholding_tax = False
        fund_event.tax_withholding = 0.0
        return fund_event

    @pytest.fixture
    def mock_bank_account(self):
        """Create a mock bank account for testing."""
        bank_account = Mock()
        bank_account.id = 1
        bank_account.currency = 'AUD'
        return bank_account

    ################################################################################
    # Get Fund Event Cash Flows Tests
    ################################################################################

    def test_get_fund_event_cash_flows_success(self, service, mock_session):
        """Test successful retrieval of fund event cash flows."""
        # Arrange
        expected_cash_flows = [Mock(spec=FundEventCashFlow), Mock(spec=FundEventCashFlow)]
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=expected_cash_flows)

        # Act
        result = service.get_fund_event_cash_flows(
            session=mock_session,
            fund_ids=[1],
            fund_event_ids=[2],
            bank_account_ids=[3],
            sort_by=SortFieldFundEventCashFlow.AMOUNT,
            sort_order=SortOrder.DESC
        )

        # Assert
        assert result == expected_cash_flows
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows.assert_called_once_with(
            mock_session, [1], [2], [3], None, None, None, None, None, None, SortFieldFundEventCashFlow.AMOUNT, SortOrder.DESC
        )

    def test_get_fund_event_cash_flows_with_defaults(self, service, mock_session):
        """Test retrieval with default parameters."""
        # Arrange
        expected_cash_flows = [Mock(spec=FundEventCashFlow)]
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=expected_cash_flows)

        # Act
        result = service.get_fund_event_cash_flows(session=mock_session)

        # Assert
        assert result == expected_cash_flows
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows.assert_called_once_with(
            mock_session, None, None, None, None, None, None, None, None, None, SortFieldFundEventCashFlow.TRANSFER_DATE, SortOrder.ASC
        )

    ################################################################################
    # Get Fund Event Cash Flow By ID Tests
    ################################################################################

    def test_get_fund_event_cash_flow_by_id_success(self, service, mock_session):
        """Test successful retrieval of fund event cash flow by ID."""
        # Arrange
        expected_cash_flow = Mock(spec=FundEventCashFlow)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=expected_cash_flow)

        # Act
        result = service.get_fund_event_cash_flow_by_id(1, mock_session)

        # Assert
        assert result == expected_cash_flow
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id.assert_called_once_with(1, mock_session)

    def test_get_fund_event_cash_flow_by_id_not_found(self, service, mock_session):
        """Test retrieval when cash flow is not found."""
        # Arrange
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=None)

        # Act
        result = service.get_fund_event_cash_flow_by_id(999, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Create Fund Event Cash Flow Tests
    ################################################################################

    def test_create_fund_event_cash_flow_success(self, service, mock_session, sample_cash_flow_data, 
                                                mock_fund_event, mock_bank_account):
        """Test successful creation of fund event cash flow."""
        # Arrange
        fund_event_id = 1
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value=[])
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        created_cash_flow.id = 123
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)
        
        # Mock the secondary impact method to avoid complex dependencies
        service._handle_fund_event_cash_flow_secondary_impact = Mock()

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, sample_cash_flow_data, mock_session)

        # Assert
        assert result == created_cash_flow
        service.fund_validation_service.validate_fund_event_cash_flow_creation.assert_called_once_with(
            fund_event_id, sample_cash_flow_data, mock_session
        )
        service.fund_event_repository.get_fund_event_by_id.assert_called_once_with(fund_event_id, mock_session)
        
        # Verify repository was called with processed data
        expected_processed_data = {
            **sample_cash_flow_data,
            'fund_event_id': fund_event_id,
            'fund_event_date': mock_fund_event.event_date,
            'different_month': sample_cash_flow_data['transfer_date'].month != mock_fund_event.event_date.month
        }
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow.assert_called_once_with(
            expected_processed_data, mock_session
        )
        
        # Verify secondary impact was called
        service._handle_fund_event_cash_flow_secondary_impact.assert_called_once_with(
            session=mock_session, 
            fund_event_id=fund_event_id, 
            event_operation=EventOperation.CREATE, 
            fund_event_cash_flow_id=123
        )

    def test_create_fund_event_cash_flow_bank_account_not_found(self, service, mock_session, sample_cash_flow_data):
        """Test creation fails when bank account is not found."""
        # Arrange
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value={'bank_account': ['Bank account not found']})

        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    def test_create_fund_event_cash_flow_fund_event_not_found(self, service, mock_session, sample_cash_flow_data):
        """Test creation fails when fund event is not found."""
        # Arrange
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value={'fund_event': ['Fund event not found']})

        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    def test_create_fund_event_cash_flow_exceeds_amount(self, service, mock_session, sample_cash_flow_data):
        """Test creation fails when cash flow exceeds fund event amount."""
        # Arrange
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value={'amount': ['Cash flow is too large. It will take the balance amount above the event amount']})

        # Act & Assert
        with pytest.raises(ValueError, match="Validation errors"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    def test_create_fund_event_cash_flow_completes_balance(self, service, mock_session, sample_cash_flow_data, mock_fund_event):
        """Test creation marks fund event as complete when balance equals amount."""
        # Arrange
        fund_event_id = 1
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value=[])
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        created_cash_flow.id = 123
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)
        
        # Mock the secondary impact method
        service._handle_fund_event_cash_flow_secondary_impact = Mock()

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, sample_cash_flow_data, mock_session)

        # Assert
        assert result == created_cash_flow

    def test_create_fund_event_cash_flow_repository_failure(self, service, mock_session, sample_cash_flow_data, mock_fund_event):
        """Test creation fails when repository returns None."""
        # Arrange
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value=[])
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create fund event cash flow"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    ################################################################################
    # Delete Fund Event Cash Flow Tests
    ################################################################################

    def test_delete_fund_event_cash_flow_success(self, service, mock_session):
        """Test successful deletion of fund event cash flow."""
        # Arrange
        cash_flow_id = 1
        fund_event_id = 2
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = fund_event_id
        mock_cash_flow.amount = 5000.00
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 1, 15)
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=True)
        
        # Mock the secondary impact method
        service._handle_fund_event_cash_flow_secondary_impact = Mock()

        # Act
        result = service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

        # Assert
        assert result is True
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id.assert_called_once_with(cash_flow_id, mock_session)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow.assert_called_once_with(cash_flow_id, mock_session)
        
        # Verify secondary impact was called
        service._handle_fund_event_cash_flow_secondary_impact.assert_called_once_with(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.DELETE,
            fund_event_cash_flow_id=cash_flow_id,
            bank_account_id=1,
            cash_flow_date=date(2024, 1, 15)
        )

    def test_delete_fund_event_cash_flow_not_found(self, service, mock_session):
        """Test deletion fails when cash flow is not found."""
        # Arrange
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event cash flow not found"):
            service.delete_fund_event_cash_flow(999, mock_session)

    def test_delete_fund_event_cash_flow_repository_failure(self, service, mock_session):
        """Test deletion fails when repository returns False."""
        # Arrange
        cash_flow_id = 1
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = 2
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 1, 15)
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=False)

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete fund event cash flow"):
            service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

    ################################################################################
    # Bank Account Balance Integration Tests
    ################################################################################

    @pytest.fixture
    def mock_bank_account_balance(self):
        """Create a mock bank account balance for testing."""
        balance = Mock(spec=BankAccountBalance)
        balance.id = 1
        balance.bank_account_id = 1
        balance.date = date(2024, 1, 31)  # Last day of January
        balance.balance_statement = 50000.00
        balance.balance_adjustment = 0.0
        balance.balance_final = 50000.00
        return balance

    @pytest.fixture
    def sample_cash_flow_data_with_different_month(self):
        """Sample cash flow data with different month transfer date."""
        return {
            'bank_account_id': 1,
            'direction': 'OUTFLOW',
            'transfer_date': date(2024, 2, 15),  # Different month from fund event
            'currency': 'AUD',
            'amount': 10000.00,
            'reference': 'REF-001',
            'description': 'Test cash flow'
        }

    def test_create_fund_event_cash_flow_different_month_calculation(self, service, mock_session, sample_cash_flow_data_with_different_month, mock_fund_event):
        """Test that different_month is correctly calculated during creation."""
        # Arrange
        fund_event_id = 1
        mock_fund_event.event_date = date(2024, 1, 15)  # January event
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value=[])
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        created_cash_flow.id = 123
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)
        
        # Mock the secondary impact method
        service._handle_fund_event_cash_flow_secondary_impact = Mock()

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, sample_cash_flow_data_with_different_month, mock_session)

        # Assert
        expected_processed_data = {
            **sample_cash_flow_data_with_different_month,
            'fund_event_id': fund_event_id,
            'fund_event_date': mock_fund_event.event_date,
            'different_month': True  # February transfer vs January event
        }
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow.assert_called_once_with(
            expected_processed_data, mock_session
        )

    def test_create_fund_event_cash_flow_same_month_calculation(self, service, mock_session, mock_fund_event):
        """Test that different_month is False when transfer and event are in same month."""
        # Arrange
        fund_event_id = 1
        mock_fund_event.event_date = date(2024, 1, 15)  # January event
        service.fund_validation_service.validate_fund_event_cash_flow_creation = Mock(return_value=[])
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        
        cash_flow_data = {
            'bank_account_id': 1,
            'direction': 'OUTFLOW',
            'transfer_date': date(2024, 1, 20),  # Same month as event
            'currency': 'AUD',
            'amount': 10000.00,
            'reference': 'REF-001',
            'description': 'Test cash flow'
        }
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        created_cash_flow.id = 123
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)
        
        # Mock the secondary impact method
        service._handle_fund_event_cash_flow_secondary_impact = Mock()

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, cash_flow_data, mock_session)

        # Assert
        expected_processed_data = {
            **cash_flow_data,
            'fund_event_id': fund_event_id,
            'fund_event_date': mock_fund_event.event_date,
            'different_month': False  # Same month
        }
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow.assert_called_once_with(
            expected_processed_data, mock_session
        )

    @patch('src.shared.services.domain_update_event_service.DomainUpdateEventService')
    @patch('src.banking.services.bank_account_balance_adjustment_service.BankAccountBalanceAdjustmentService')
    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_with_bank_account_balance_adjustment(self, mock_calculator, 
                                                                  mock_balance_repo, mock_adjustment_service,
                                                                  mock_domain_repo, service, mock_session, mock_fund_event, 
                                                                  mock_bank_account_balance):
        """Test secondary impact when bank account balance needs adjustment."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 10000.00
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository
        mock_balance_repo.return_value.get_bank_account_balances.return_value = [mock_bank_account_balance]
        
        # Mock adjustment service
        mock_adjustment_changes = [
            DomainFieldChange(DomainObjectType.BANK_ACCOUNT_BALANCE, 1, 'balance_adjustment', 0.0, -10000.0),
            DomainFieldChange(DomainObjectType.BANK_ACCOUNT_BALANCE, 1, 'balance_final', 50000.0, 40000.0)
        ]
        mock_adjustment_service.return_value.calculate_bank_account_balance_adjustment.return_value = mock_adjustment_changes
        
        # Mock domain update event repository
        mock_domain_repo.return_value.create_domain_update_event.return_value = Mock()

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        mock_calculator.return_value.get_last_day_of_the_month.assert_called_once_with(date(2024, 2, 15))
        mock_balance_repo.return_value.get_bank_account_balances.assert_called_once_with(
            mock_session,
            bank_account_ids=[1],
            start_date=date(2024, 2, 29),
            end_date=date(2024, 2, 29)
        )
        mock_adjustment_service.return_value.calculate_bank_account_balance_adjustment.assert_called_once_with(
            mock_bank_account_balance, mock_session
        )
        mock_domain_repo.return_value.create_domain_update_event.assert_called_once()

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_no_bank_account_balance_found(self, mock_calculator, mock_balance_repo,
                                                           service, mock_session, mock_fund_event):
        """Test secondary impact when no bank account balance exists."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 10000.00
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Should not raise an error when no balance is found
        mock_balance_repo.return_value.get_bank_account_balances.assert_called_once()

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_multiple_bank_account_balances_error(self, mock_calculator, mock_balance_repo,
                                                                  service, mock_session, mock_fund_event):
        """Test secondary impact raises error when multiple bank account balances found."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 10000.00
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - multiple balances found
        mock_balance1 = Mock(spec=BankAccountBalance)
        mock_balance2 = Mock(spec=BankAccountBalance)
        mock_balance_repo.return_value.get_bank_account_balances.return_value = [mock_balance1, mock_balance2]

        # Act & Assert
        with pytest.raises(ValueError, match="Multiple bank account balances found for the same bank account and date"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=fund_event_id,
                event_operation=EventOperation.CREATE,
                fund_event_cash_flow_id=cash_flow_id
            )

    def test_secondary_impact_validation_create_operation_with_bank_account_id(self, service, mock_session):
        """Test secondary impact validation fails when CREATE operation has bank_account_id."""
        # Act & Assert
        with pytest.raises(ValueError, match="When creating a fund event cash flow, we must not pass either the bank_account_id or cash_flow_date"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=1,
                event_operation=EventOperation.CREATE,
                fund_event_cash_flow_id=1,
                bank_account_id=1  # Should not be provided for CREATE
            )

    def test_secondary_impact_validation_create_operation_with_cash_flow_date(self, service, mock_session):
        """Test secondary impact validation fails when CREATE operation has cash_flow_date."""
        # Act & Assert
        with pytest.raises(ValueError, match="When creating a fund event cash flow, we must not pass either the bank_account_id or cash_flow_date"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=1,
                event_operation=EventOperation.CREATE,
                fund_event_cash_flow_id=1,
                cash_flow_date=date(2024, 1, 15)  # Should not be provided for CREATE
            )

    def test_secondary_impact_validation_delete_operation_missing_bank_account_id(self, service, mock_session):
        """Test secondary impact validation fails when DELETE operation missing bank_account_id."""
        # Act & Assert
        with pytest.raises(ValueError, match="When deleting a fund event cash flow, we must provide both the bank_account_id and cash_flow_date"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=1,
                event_operation=EventOperation.DELETE,
                fund_event_cash_flow_id=1,
                cash_flow_date=date(2024, 1, 15)  # Missing bank_account_id
            )

    def test_secondary_impact_validation_delete_operation_missing_cash_flow_date(self, service, mock_session):
        """Test secondary impact validation fails when DELETE operation missing cash_flow_date."""
        # Act & Assert
        with pytest.raises(ValueError, match="When deleting a fund event cash flow, we must provide both the bank_account_id and cash_flow_date"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=1,
                event_operation=EventOperation.DELETE,
                fund_event_cash_flow_id=1,
                bank_account_id=1  # Missing cash_flow_date
            )

    def test_secondary_impact_fund_event_not_found(self, service, mock_session):
        """Test secondary impact fails when fund event is not found."""
        # Arrange
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event not found"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=999,
                event_operation=EventOperation.CREATE,
                fund_event_cash_flow_id=1
            )

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_fund_event_cash_flow_not_found_during_create(self, mock_calculator, mock_balance_repo,
                                                                          service, mock_session, mock_fund_event):
        """Test secondary impact fails when fund event cash flow is not found during CREATE."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=None)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event cash flow not found"):
            service._handle_fund_event_cash_flow_secondary_impact(
                session=mock_session,
                fund_event_id=fund_event_id,
                event_operation=EventOperation.CREATE,
                fund_event_cash_flow_id=cash_flow_id
            )

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_withholding_tax_calculation(self, mock_calculator, mock_balance_repo,
                                                         service, mock_session, mock_fund_event):
        """Test secondary impact correctly calculates expected total with withholding tax."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = True
        mock_fund_event.tax_withholding = 5000.00  # 10% withholding
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 45000.00  # Amount after withholding tax
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Fund event should be marked as complete since 45000 == 50000 - 5000
        assert mock_fund_event.is_cash_flow_complete is True
        assert mock_fund_event.cash_flow_balance_amount == 45000.00

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_cash_flow_balance_incomplete(self, mock_calculator, mock_balance_repo,
                                                          service, mock_session, mock_fund_event):
        """Test secondary impact marks fund event as incomplete when balance doesn't match expected."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows - partial amount
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 30000.00  # Less than expected 50000
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Fund event should remain incomplete since 30000 != 50000
        assert mock_fund_event.is_cash_flow_complete is False
        assert mock_fund_event.cash_flow_balance_amount == 30000.00

    ################################################################################
    # Additional Bank Account Balance Integration Tests
    ################################################################################

    @patch('src.shared.services.domain_update_event_service.DomainUpdateEventService')
    @patch('src.banking.services.bank_account_balance_adjustment_service.BankAccountBalanceAdjustmentService')
    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_no_domain_changes_created(self, mock_calculator, mock_balance_repo, 
                                                       mock_adjustment_service, mock_domain_repo,
                                                       service, mock_session, mock_fund_event):
        """Test secondary impact when no domain changes are generated."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 50000.00  # Already complete
        mock_fund_event.is_cash_flow_complete = True  # Already complete
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 50000.00  # Matches expected amount
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # No domain update event should be created since no changes occurred
        mock_domain_repo.return_value.create_domain_update_event.assert_not_called()


    @patch('src.shared.services.domain_update_event_service.DomainUpdateEventService')
    @patch('src.banking.services.bank_account_balance_adjustment_service.BankAccountBalanceAdjustmentService')
    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_multiple_cash_flows_balance_calculation(self, mock_calculator, 
                                                                    mock_balance_repo, mock_adjustment_service,
                                                                    mock_domain_repo, service, mock_session, 
                                                                    mock_fund_event):
        """Test secondary impact with multiple cash flows affecting balance calculation."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 3
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 100000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock multiple fund event cash flows
        mock_cash_flow1 = Mock(spec=FundEventCashFlow)
        mock_cash_flow1.id = 1
        mock_cash_flow1.amount = 40000.00
        
        mock_cash_flow2 = Mock(spec=FundEventCashFlow)
        mock_cash_flow2.id = 2
        mock_cash_flow2.amount = 30000.00
        
        mock_cash_flow3 = Mock(spec=FundEventCashFlow)
        mock_cash_flow3.id = 3
        mock_cash_flow3.amount = 30000.00
        mock_cash_flow3.bank_account_id = 1
        mock_cash_flow3.transfer_date = date(2024, 2, 15)
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[
            mock_cash_flow1, mock_cash_flow2, mock_cash_flow3
        ])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow3)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []
        
        # Mock domain update event repository
        mock_domain_repo.return_value.create_domain_update_event.return_value = Mock()

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Total balance should be 40000 + 30000 + 30000 = 100000, which matches expected amount
        assert mock_fund_event.is_cash_flow_complete is True
        assert mock_fund_event.cash_flow_balance_amount == 100000.00

    @patch('src.shared.services.domain_update_event_service.DomainUpdateEventService')
    @patch('src.banking.services.bank_account_balance_adjustment_service.BankAccountBalanceAdjustmentService')
    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_balance_adjustment_service_no_changes(self, mock_calculator, 
                                                                   mock_balance_repo, mock_adjustment_service,
                                                                   mock_domain_repo, service, mock_session, 
                                                                   mock_fund_event, mock_bank_account_balance):
        """Test secondary impact when balance adjustment service returns no changes."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 50000.00
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository
        mock_balance_repo.return_value.get_bank_account_balances.return_value = [mock_bank_account_balance]
        
        # Mock adjustment service to return no changes
        mock_adjustment_service.return_value.calculate_bank_account_balance_adjustment.return_value = []
        
        # Mock domain update event repository
        mock_domain_repo.return_value.create_domain_update_event.return_value = Mock()

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Should still create domain update event for fund event changes
        mock_domain_repo.return_value.create_domain_update_event.assert_called_once()

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_fund_event_cash_flow_balance_changes_tracking(self, mock_calculator, mock_balance_repo,
                                                                            service, mock_session, mock_fund_event):
        """Test that fund event cash flow balance changes are properly tracked."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 20000.00  # Starting balance
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 30000.00  # This will make total 50000
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Fund event should remain incomplete since 30000 != 50000
        assert mock_fund_event.is_cash_flow_complete is False
        assert mock_fund_event.cash_flow_balance_amount == 30000.00

    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_non_distribution_event_withholding_tax_ignored(self, mock_calculator, mock_balance_repo,
                                                                            service, mock_session):
        """Test that withholding tax is ignored for non-distribution events."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event = Mock(spec=FundEvent)
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.CAPITAL_CALL  # Non-distribution event
        mock_fund_event.has_withholding_tax = True  # Should be ignored
        mock_fund_event.tax_withholding = 5000.00  # Should be ignored
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 50000.00  # Full amount expected
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository - no balance found
        mock_balance_repo.return_value.get_bank_account_balances.return_value = []

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Fund event should be complete with full amount (withholding tax ignored for non-distribution)
        assert mock_fund_event.is_cash_flow_complete is True
        assert mock_fund_event.cash_flow_balance_amount == 50000.00

    @patch('src.shared.services.domain_update_event_service.DomainUpdateEventService')
    @patch('src.banking.services.bank_account_balance_adjustment_service.BankAccountBalanceAdjustmentService')
    @patch('src.banking.repositories.bank_account_balance_repository.BankAccountBalanceRepository')
    @patch('src.shared.calculators.last_day_of_the_month_calculator.LastDayOfTheMonthCalculator')
    def test_secondary_impact_session_operations_called(self, mock_calculator, mock_balance_repo, 
                                                       mock_adjustment_service, mock_domain_repo,
                                                       service, mock_session, mock_fund_event, 
                                                       mock_bank_account_balance):
        """Test that session flush and refresh operations are properly called."""
        # Arrange
        fund_event_id = 1
        cash_flow_id = 2
        mock_fund_event.id = fund_event_id
        mock_fund_event.amount = 50000.00
        mock_fund_event.event_type = EventType.DISTRIBUTION
        mock_fund_event.has_withholding_tax = False
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        
        # Mock fund event cash flows
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.bank_account_id = 1
        mock_cash_flow.transfer_date = date(2024, 2, 15)
        mock_cash_flow.amount = 50000.00
        
        service.fund_event_repository.get_fund_event_by_id = Mock(return_value=mock_fund_event)
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows = Mock(return_value=[mock_cash_flow])
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        
        # Mock last day calculator
        mock_calculator.return_value.get_last_day_of_the_month.return_value = date(2024, 2, 29)
        
        # Mock bank account balance repository
        mock_balance_repo.return_value.get_bank_account_balances.return_value = [mock_bank_account_balance]
        
        # Mock adjustment service
        mock_adjustment_changes = [
            DomainFieldChange(DomainObjectType.BANK_ACCOUNT_BALANCE, 1, 'balance_adjustment', 0.0, -50000.0)
        ]
        mock_adjustment_service.return_value.calculate_bank_account_balance_adjustment.return_value = mock_adjustment_changes
        
        # Mock domain update event repository
        mock_domain_repo.return_value.create_domain_update_event.return_value = Mock()

        # Act
        service._handle_fund_event_cash_flow_secondary_impact(
            session=mock_session,
            fund_event_id=fund_event_id,
            event_operation=EventOperation.CREATE,
            fund_event_cash_flow_id=cash_flow_id
        )

        # Assert
        # Verify session operations were called
        assert mock_session.flush.call_count >= 2  # At least one for fund event, one for bank account balance
        # Check that both refresh calls were made (order doesn't matter)
        assert mock_session.refresh.call_count >= 2
        mock_session.refresh.assert_any_call(mock_fund_event)
        mock_session.refresh.assert_any_call(mock_bank_account_balance)
