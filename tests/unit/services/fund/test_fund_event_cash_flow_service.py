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
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.fund.services.fund_event_cash_flow_service import FundEventCashFlowService
from src.fund.models import FundEventCashFlow, FundEvent
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow
from src.shared.enums.shared_enums import SortOrder
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
            'transfer_date': '2024-01-15',
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
            fund_id=1,
            fund_event_id=2,
            bank_account_id=3,
            sort_by=SortFieldFundEventCashFlow.AMOUNT,
            sort_order=SortOrder.DESC
        )

        # Assert
        assert result == expected_cash_flows
        service.fund_event_cash_flow_repository.get_fund_event_cash_flows.assert_called_once_with(
            mock_session, 1, 2, 3, SortFieldFundEventCashFlow.AMOUNT, SortOrder.DESC
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
            mock_session, None, None, None, SortFieldFundEventCashFlow.TRANSFER_DATE, SortOrder.ASC
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

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    @patch('src.fund.repositories.fund_event_repository.FundEventRepository')
    def test_create_fund_event_cash_flow_success(self, mock_fund_event_repo, mock_bank_account_repo, 
                                                service, mock_session, sample_cash_flow_data, 
                                                mock_fund_event, mock_bank_account):
        """Test successful creation of fund event cash flow."""
        # Arrange
        fund_event_id = 1
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = mock_bank_account
        mock_fund_event_repo.return_value.get_fund_event_by_id.return_value = mock_fund_event
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, sample_cash_flow_data, mock_session)

        # Assert
        assert result == created_cash_flow
        mock_bank_account_repo.return_value.get_bank_account_by_id.assert_called_once_with(1, mock_session)
        mock_fund_event_repo.return_value.get_fund_event_by_id.assert_called_once_with(fund_event_id, mock_session)
        
        # Verify fund event balance was updated
        assert mock_fund_event.cash_flow_balance_amount == 10000.00
        assert mock_fund_event.is_cash_flow_complete is False
        
        # Verify repository was called with processed data
        expected_processed_data = {**sample_cash_flow_data, 'fund_event_id': fund_event_id}
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow.assert_called_once_with(
            expected_processed_data, mock_session
        )

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    def test_create_fund_event_cash_flow_bank_account_not_found(self, mock_bank_account_repo, 
                                                               service, mock_session, sample_cash_flow_data):
        """Test creation fails when bank account is not found."""
        # Arrange
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Bank account not found"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    @patch('src.fund.repositories.fund_event_repository.FundEventRepository')
    def test_create_fund_event_cash_flow_fund_event_not_found(self, mock_fund_event_repo, mock_bank_account_repo,
                                                             service, mock_session, sample_cash_flow_data, mock_bank_account):
        """Test creation fails when fund event is not found."""
        # Arrange
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = mock_bank_account
        mock_fund_event_repo.return_value.get_fund_event_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event not found"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    @patch('src.fund.repositories.fund_event_repository.FundEventRepository')
    def test_create_fund_event_cash_flow_exceeds_amount(self, mock_fund_event_repo, mock_bank_account_repo,
                                                       service, mock_session, sample_cash_flow_data, 
                                                       mock_bank_account):
        """Test creation fails when cash flow exceeds fund event amount."""
        # Arrange
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = mock_bank_account
        mock_fund_event = Mock(spec=FundEvent)
        mock_fund_event.amount = 5000.00
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        mock_fund_event_repo.return_value.get_fund_event_by_id.return_value = mock_fund_event

        # Act & Assert
        with pytest.raises(ValueError, match="Cash flow is too large. It will take the balance amount above the event amount"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    @patch('src.fund.repositories.fund_event_repository.FundEventRepository')
    def test_create_fund_event_cash_flow_completes_balance(self, mock_fund_event_repo, mock_bank_account_repo,
                                                          service, mock_session, sample_cash_flow_data, 
                                                          mock_bank_account):
        """Test creation marks fund event as complete when balance equals amount."""
        # Arrange
        fund_event_id = 1
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = mock_bank_account
        mock_fund_event = Mock(spec=FundEvent)
        mock_fund_event.amount = 10000.00
        mock_fund_event.cash_flow_balance_amount = 0.00
        mock_fund_event.is_cash_flow_complete = False
        mock_fund_event_repo.return_value.get_fund_event_by_id.return_value = mock_fund_event
        
        created_cash_flow = Mock(spec=FundEventCashFlow)
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=created_cash_flow)

        # Act
        result = service.create_fund_event_cash_flow(fund_event_id, sample_cash_flow_data, mock_session)

        # Assert
        assert result == created_cash_flow
        assert mock_fund_event.cash_flow_balance_amount == 10000.00
        assert mock_fund_event.is_cash_flow_complete is True

    @patch('src.banking.repositories.bank_account_repository.BankAccountRepository')
    @patch('src.fund.repositories.fund_event_repository.FundEventRepository')
    def test_create_fund_event_cash_flow_repository_failure(self, mock_fund_event_repo, mock_bank_account_repo,
                                                           service, mock_session, sample_cash_flow_data, 
                                                           mock_fund_event, mock_bank_account):
        """Test creation fails when repository returns None."""
        # Arrange
        mock_bank_account_repo.return_value.get_bank_account_by_id.return_value = mock_bank_account
        mock_fund_event_repo.return_value.get_fund_event_by_id.return_value = mock_fund_event
        service.fund_event_cash_flow_repository.create_fund_event_cash_flow = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to create fund event cash flow"):
            service.create_fund_event_cash_flow(1, sample_cash_flow_data, mock_session)

    ################################################################################
    # Delete Fund Event Cash Flow Tests
    ################################################################################

    @patch('src.fund.services.fund_event_service.FundEventService')
    def test_delete_fund_event_cash_flow_success(self, mock_fund_event_service, service, mock_session):
        """Test successful deletion of fund event cash flow."""
        # Arrange
        cash_flow_id = 1
        fund_event_id = 2
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = fund_event_id
        mock_cash_flow.amount = 5000.00
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=True)
        
        mock_fund_event = Mock(spec=FundEvent)
        mock_fund_event.id = fund_event_id
        mock_fund_event.cash_flow_balance_amount = 10000.00
        mock_fund_event.is_cash_flow_complete = True
        mock_fund_event_service.return_value.get_fund_event_by_id.return_value = mock_fund_event

        # Act
        result = service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

        # Assert
        assert result is True
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id.assert_called_once_with(cash_flow_id, mock_session)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow.assert_called_once_with(cash_flow_id, mock_session)
        mock_fund_event_service.return_value.get_fund_event_by_id.assert_called_once_with(fund_event_id, mock_session)
        
        # Verify fund event balance was updated
        assert mock_fund_event.cash_flow_balance_amount == 5000.00
        assert mock_fund_event.is_cash_flow_complete is False

    def test_delete_fund_event_cash_flow_not_found(self, service, mock_session):
        """Test deletion fails when cash flow is not found."""
        # Arrange
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=None)

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event cash flow not found"):
            service.delete_fund_event_cash_flow(999, mock_session)

    @patch('src.fund.services.fund_event_service.FundEventService')
    def test_delete_fund_event_cash_flow_repository_failure(self, mock_fund_event_service, service, mock_session):
        """Test deletion fails when repository returns False."""
        # Arrange
        cash_flow_id = 1
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = 2
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=False)

        # Act & Assert
        with pytest.raises(ValueError, match="Failed to delete fund event cash flow"):
            service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

    @patch('src.fund.services.fund_event_service.FundEventService')
    def test_delete_fund_event_cash_flow_fund_event_not_found(self, mock_fund_event_service, service, mock_session):
        """Test deletion fails when fund event is not found during balance update."""
        # Arrange
        cash_flow_id = 1
        fund_event_id = 2
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = fund_event_id
        mock_cash_flow.amount = 5000.00
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=True)
        mock_fund_event_service.return_value.get_fund_event_by_id.return_value = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fund event not found"):
            service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

    @patch('src.fund.services.fund_event_service.FundEventService')
    def test_delete_fund_event_cash_flow_incomplete_balance(self, mock_fund_event_service, service, mock_session):
        """Test deletion updates fund event when balance becomes incomplete."""
        # Arrange
        cash_flow_id = 1
        fund_event_id = 2
        mock_cash_flow = Mock(spec=FundEventCashFlow)
        mock_cash_flow.id = cash_flow_id
        mock_cash_flow.fund_event_id = fund_event_id
        mock_cash_flow.amount = 5000.00
        
        service.fund_event_cash_flow_repository.get_fund_event_cash_flow_by_id = Mock(return_value=mock_cash_flow)
        service.fund_event_cash_flow_repository.delete_fund_event_cash_flow = Mock(return_value=True)
        
        mock_fund_event = Mock(spec=FundEvent)
        mock_fund_event.id = fund_event_id
        mock_fund_event.cash_flow_balance_amount = 15000.00
        mock_fund_event.is_cash_flow_complete = True
        mock_fund_event_service.return_value.get_fund_event_by_id.return_value = mock_fund_event

        # Act
        result = service.delete_fund_event_cash_flow(cash_flow_id, mock_session)

        # Assert
        assert result is True
        assert mock_fund_event.cash_flow_balance_amount == 10000.00
        assert mock_fund_event.is_cash_flow_complete is False
