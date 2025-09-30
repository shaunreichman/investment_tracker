"""
Fund Event Cash Flow Repository Unit Tests.

This module tests the FundEventCashFlowRepository class, focusing on data access operations
and error handling. Tests are precise and focused on repository functionality without
testing business logic or validation.

Test Coverage:
- CRUD operations (Create, Read, Delete)
- Filtering and sorting functionality
- Error handling for invalid parameters
- Database session interactions
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.fund.repositories.fund_event_cash_flow_repository import FundEventCashFlowRepository
from src.fund.models import FundEventCashFlow
from src.fund.enums.fund_event_cash_flow_enums import SortFieldFundEventCashFlow, CashFlowDirection
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundEventCashFlowFactory


class TestFundEventCashFlowRepository:
    """Test suite for FundEventCashFlowRepository."""

    @pytest.fixture
    def repository(self):
        """Create a FundEventCashFlowRepository instance for testing."""
        return FundEventCashFlowRepository()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_cash_flow_data(self):
        """Sample cash flow data for testing."""
        return {
            'fund_event_id': 1,
            'bank_account_id': 1,
            'direction': CashFlowDirection.INFLOW,
            'transfer_date': date(2024, 1, 15),
            'currency': 'AUD',
            'amount': 5000.0,
            'reference': 'REF-12345',
            'description': 'Test cash flow'
        }

    ################################################################################
    # Test get_fund_event_cash_flows method
    ################################################################################

    def test_get_fund_event_cash_flows_returns_all_cash_flows(self, repository, mock_session):
        """Test that get_fund_event_cash_flows returns all cash flows when no filters applied."""
        # Arrange
        expected_cash_flows = [Mock(spec=FundEventCashFlow) for _ in range(3)]
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = expected_cash_flows

        # Act
        result = repository.get_fund_event_cash_flows(mock_session)

        # Assert
        assert result == expected_cash_flows
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_with_fund_id_filter(self, repository, mock_session):
        """Test that get_fund_event_cash_flows filters by fund_id correctly."""
        # Arrange
        fund_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, fund_id=fund_id)

        # Assert
        assert mock_query.join.called
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_with_fund_event_id_filter(self, repository, mock_session):
        """Test that get_fund_event_cash_flows filters by fund_event_id correctly."""
        # Arrange
        fund_event_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, fund_event_id=fund_event_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_with_bank_account_id_filter(self, repository, mock_session):
        """Test that get_fund_event_cash_flows filters by bank_account_id correctly."""
        # Arrange
        bank_account_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, bank_account_id=bank_account_id)

        # Assert
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_with_multiple_filters(self, repository, mock_session):
        """Test that get_fund_event_cash_flows applies multiple filters correctly."""
        # Arrange
        fund_id = 1
        fund_event_id = 1
        bank_account_id = 1
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.join.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           fund_id=fund_id,
                                           fund_event_id=fund_event_id,
                                           bank_account_id=bank_account_id)

        # Assert
        # fund_id uses join + filter, fund_event_id and bank_account_id use filter
        assert mock_query.join.called
        assert mock_query.filter.call_count == 3  # fund_id (after join), fund_event_id and bank_account_id
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_sorts_by_transfer_date_asc(self, repository, mock_session):
        """Test that get_fund_event_cash_flows sorts by transfer_date in ascending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           sort_by=SortFieldFundEventCashFlow.TRANSFER_DATE,
                                           sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_sorts_by_transfer_date_desc(self, repository, mock_session):
        """Test that get_fund_event_cash_flows sorts by transfer_date in descending order."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           sort_by=SortFieldFundEventCashFlow.TRANSFER_DATE,
                                           sort_order=SortOrder.DESC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_sorts_by_amount(self, repository, mock_session):
        """Test that get_fund_event_cash_flows sorts by amount correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           sort_by=SortFieldFundEventCashFlow.AMOUNT,
                                           sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_sorts_by_created_at(self, repository, mock_session):
        """Test that get_fund_event_cash_flows sorts by created_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           sort_by=SortFieldFundEventCashFlow.CREATED_AT,
                                           sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_sorts_by_updated_at(self, repository, mock_session):
        """Test that get_fund_event_cash_flows sorts by updated_at correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           sort_by=SortFieldFundEventCashFlow.UPDATED_AT,
                                           sort_order=SortOrder.ASC)

        # Assert
        assert mock_query.order_by.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flows_raises_error_for_invalid_sort_field(self, repository, mock_session):
        """Test that get_fund_event_cash_flows raises ValueError for invalid sort field."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort field"):
            repository.get_fund_event_cash_flows(mock_session, sort_by="INVALID_FIELD")

    def test_get_fund_event_cash_flows_raises_error_for_invalid_sort_order(self, repository, mock_session):
        """Test that get_fund_event_cash_flows raises ValueError for invalid sort order."""
        # Act & Assert
        with pytest.raises(ValueError, match="Invalid sort order"):
            repository.get_fund_event_cash_flows(mock_session, sort_order="INVALID_ORDER")

    ################################################################################
    # Test get_fund_event_cash_flow_by_id method
    ################################################################################

    def test_get_fund_event_cash_flow_by_id_returns_cash_flow_when_found(self, repository, mock_session):
        """Test that get_fund_event_cash_flow_by_id returns cash flow when found."""
        # Arrange
        cash_flow_id = 1
        expected_cash_flow = Mock(spec=FundEventCashFlow)
        expected_cash_flow.id = cash_flow_id
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_cash_flow

        # Act
        result = repository.get_fund_event_cash_flow_by_id(cash_flow_id, mock_session)

        # Assert
        assert result == expected_cash_flow
        assert mock_query.filter.called
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_get_fund_event_cash_flow_by_id_returns_none_when_not_found(self, repository, mock_session):
        """Test that get_fund_event_cash_flow_by_id returns None when cash flow not found."""
        # Arrange
        cash_flow_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.get_fund_event_cash_flow_by_id(cash_flow_id, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Test create_fund_event_cash_flow method
    ################################################################################

    def test_create_fund_event_cash_flow_creates_and_returns_cash_flow(self, repository, mock_session, sample_cash_flow_data):
        """Test that create_fund_event_cash_flow creates and returns a cash flow."""
        # Arrange
        expected_cash_flow = Mock(spec=FundEventCashFlow)
        expected_cash_flow.fund_event_id = sample_cash_flow_data['fund_event_id']
        expected_cash_flow.bank_account_id = sample_cash_flow_data['bank_account_id']
        with patch('src.fund.repositories.fund_event_cash_flow_repository.FundEventCashFlow', return_value=expected_cash_flow):
            # Act
            result = repository.create_fund_event_cash_flow(sample_cash_flow_data, mock_session)

            # Assert
            assert result == expected_cash_flow
            mock_session.add.assert_called_once_with(expected_cash_flow)
            mock_session.flush.assert_called_once()

    ################################################################################
    # Test delete_fund_event_cash_flow method
    ################################################################################

    def test_delete_fund_event_cash_flow_deletes_existing_cash_flow(self, repository, mock_session):
        """Test that delete_fund_event_cash_flow deletes an existing cash flow."""
        # Arrange
        cash_flow_id = 1
        expected_cash_flow = Mock(spec=FundEventCashFlow)
        expected_cash_flow.id = cash_flow_id
        expected_cash_flow.fund_event_id = 1
        expected_cash_flow.bank_account_id = 2
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = expected_cash_flow

        # Act
        result = repository.delete_fund_event_cash_flow(cash_flow_id, mock_session)

        # Assert
        assert result is True
        mock_session.delete.assert_called_once_with(expected_cash_flow)
        mock_session.flush.assert_called_once()

    def test_delete_fund_event_cash_flow_returns_false_for_nonexistent_cash_flow(self, repository, mock_session):
        """Test that delete_fund_event_cash_flow returns False for nonexistent cash flow."""
        # Arrange
        cash_flow_id = 999
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None

        # Act
        result = repository.delete_fund_event_cash_flow(cash_flow_id, mock_session)

        # Assert
        assert result is False
        mock_session.delete.assert_not_called()


    ################################################################################
    # Test edge cases and error handling
    ################################################################################

    def test_get_fund_event_cash_flows_with_none_filters(self, repository, mock_session):
        """Test that get_fund_event_cash_flows handles None filters correctly."""
        # Arrange
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = []

        # Act
        repository.get_fund_event_cash_flows(mock_session, 
                                           fund_id=None,
                                           fund_event_id=None,
                                           bank_account_id=None)

        # Assert
        # Should not apply any filters
        mock_query.filter.assert_not_called()
        mock_session.query.assert_called_once_with(FundEventCashFlow)

    def test_create_fund_event_cash_flow_with_empty_data(self, repository, mock_session):
        """Test that create_fund_event_cash_flow handles empty data correctly."""
        # Arrange
        empty_data = {}
        expected_cash_flow = Mock(spec=FundEventCashFlow)
        with patch('src.fund.repositories.fund_event_cash_flow_repository.FundEventCashFlow', return_value=expected_cash_flow):
            # Act
            result = repository.create_fund_event_cash_flow(empty_data, mock_session)

            # Assert
            assert result == expected_cash_flow
            mock_session.add.assert_called_once_with(expected_cash_flow)
            mock_session.flush.assert_called_once()

