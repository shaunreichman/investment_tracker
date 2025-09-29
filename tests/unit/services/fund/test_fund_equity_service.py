"""
Fund Equity Service Unit Tests.

This module tests the FundEquityService class, focusing on business logic,
equity calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Equity fund field updates with change tracking
- Equity fund event field calculations
- Service layer orchestration
- Error handling and edge cases
- Flag-based selective field updates
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_equity_service import FundEquityService
from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundFactory, FundEventFactory


class TestFundEquityService:
    """Test suite for FundEquityService."""

    @pytest.fixture
    def service(self):
        """Create a FundEquityService instance for testing."""
        return FundEquityService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance with equity fields."""
        from src.fund.enums.fund_enums import FundTrackingType
        fund = FundFactory.build(
            id=1,
            current_equity_balance=5000.0,
            average_equity_balance=4500.0,
            total_cost_basis=10000.0,
            tracking_type=FundTrackingType.COST_BASED
        )
        return fund

    @pytest.fixture
    def mock_equity_events(self):
        """Mock equity-related events."""
        return [
            FundEventFactory.build(
                id=1,
                event_type=EventType.CAPITAL_CALL,
                amount=2000.0,
                current_equity_balance=2000.0
            ),
            FundEventFactory.build(
                id=2,
                event_type=EventType.UNIT_PURCHASE,
                amount=1500.0,
                current_equity_balance=3500.0
            ),
            FundEventFactory.build(
                id=3,
                event_type=EventType.RETURN_OF_CAPITAL,
                amount=500.0,
                current_equity_balance=3000.0
            )
        ]

    @pytest.fixture
    def mock_event_balances(self):
        """Mock event balances from calculator."""
        return [
            (2000.0, True),   # (balance, has_changed)
            (3500.0, True),
            (3000.0, False)
        ]

    ################################################################################
    # Test update_fund_equity_fields method
    ################################################################################

    def test_update_fund_equity_fields_with_changes_returns_field_changes(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields returns field changes when equity values change."""
        # Arrange
        old_current_equity = mock_fund.current_equity_balance
        old_average_equity = mock_fund.average_equity_balance
        old_total_cost_basis = mock_fund.total_cost_basis
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=6000.0) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=5500.0) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=12000.0) as mock_calc_cost_basis:
            
            # Act
            result = service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert
            assert result is not None
            assert len(result) == 3  # All three fields changed
            
            # Verify field changes
            current_equity_change = next((change for change in result if change.field_name == 'current_equity_balance'), None)
            assert current_equity_change is not None
            assert current_equity_change.old_value == old_current_equity
            assert current_equity_change.new_value == 6000.0
            assert current_equity_change.object_id == mock_fund.id
            assert current_equity_change.fund_or_company == 'FUND'
            
            average_equity_change = next((change for change in result if change.field_name == 'average_equity_balance'), None)
            assert average_equity_change is not None
            assert average_equity_change.old_value == old_average_equity
            assert average_equity_change.new_value == 5500.0
            
            cost_basis_change = next((change for change in result if change.field_name == 'total_cost_basis'), None)
            assert cost_basis_change is not None
            assert cost_basis_change.old_value == old_total_cost_basis
            assert cost_basis_change.new_value == 12000.0
            
            # Verify fund fields were updated
            assert mock_fund.current_equity_balance == 6000.0
            assert mock_fund.average_equity_balance == 5500.0
            assert mock_fund.total_cost_basis == 12000.0
            
            # Verify repository and calculator calls
            mock_repo.assert_called_once_with(
                mock_session, 
                fund_ids=[mock_fund.id],
                event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                sort_order=SortOrder.ASC
            )
            mock_calc_balances.assert_called_once_with(mock_fund, mock_equity_events)
            mock_calc_current.assert_called_once_with(mock_event_balances)
            mock_calc_average.assert_called_once_with(mock_equity_events, mock_event_balances)
            mock_calc_cost_basis.assert_called_once_with(mock_event_balances, mock_fund, mock_equity_events)

    def test_update_fund_equity_fields_no_changes_returns_none(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields returns None when no equity values change."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=mock_fund.current_equity_balance) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=mock_fund.average_equity_balance) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=mock_fund.total_cost_basis) as mock_calc_cost_basis:
            
            # Act
            result = service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert
            assert result is None
            # Verify fund fields remain unchanged
            assert mock_fund.current_equity_balance == 5000.0
            assert mock_fund.average_equity_balance == 4500.0
            assert mock_fund.total_cost_basis == 10000.0

    def test_update_fund_equity_fields_with_selective_flags(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields respects flag parameters for selective updates."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=6000.0) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=5500.0) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=12000.0) as mock_calc_cost_basis:
            
            # Act - Only update current equity and total cost basis
            result = service.update_fund_equity_fields(
                mock_fund, 
                mock_session,
                current_equity_flag=True,
                average_equity_flag=False,
                total_cost_basis_flag=True
            )
            
            # Assert
            assert result is not None
            assert len(result) == 2  # Only two fields changed
            
            # Verify only current equity and total cost basis changed
            current_equity_change = next((change for change in result if change.field_name == 'current_equity_balance'), None)
            assert current_equity_change is not None
            assert current_equity_change.new_value == 6000.0
            
            cost_basis_change = next((change for change in result if change.field_name == 'total_cost_basis'), None)
            assert cost_basis_change is not None
            assert cost_basis_change.new_value == 12000.0
            
            # Verify average equity was not updated
            average_equity_change = next((change for change in result if change.field_name == 'average_equity_balance'), None)
            assert average_equity_change is None
            assert mock_fund.average_equity_balance == 4500.0  # Original value
            
            # Verify only current equity and cost basis calculators were called
            mock_calc_current.assert_called_once()
            mock_calc_cost_basis.assert_called_once()
            mock_calc_average.assert_not_called()

    def test_update_fund_equity_fields_all_flags_false_returns_none(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields returns None when all flags are False."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances:
            
            # Act - All flags False
            result = service.update_fund_equity_fields(
                mock_fund, 
                mock_session,
                current_equity_flag=False,
                average_equity_flag=False,
                total_cost_basis_flag=False
            )
            
            # Assert
            assert result is None
            # Verify fund fields remain unchanged
            assert mock_fund.current_equity_balance == 5000.0
            assert mock_fund.average_equity_balance == 4500.0
            assert mock_fund.total_cost_basis == 10000.0
            
            # Verify only repository and balance calculation were called
            mock_repo.assert_called_once()
            mock_calc_balances.assert_called_once()

    def test_update_fund_equity_fields_updates_event_balances_when_changed(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields updates event balances when they have changed."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=6000.0) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=5500.0) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=12000.0) as mock_calc_cost_basis:
            
            # Act
            service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert - Only events with has_changed=True should be updated
            assert mock_equity_events[0].current_equity_balance == 2000.0  # has_changed=True
            assert mock_equity_events[1].current_equity_balance == 3500.0  # has_changed=True
            assert mock_equity_events[2].current_equity_balance == 3000.0  # has_changed=False, but was already 3000.0

    def test_update_fund_equity_fields_partial_changes_returns_correct_changes(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields returns only the fields that actually changed."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=6000.0) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=mock_fund.average_equity_balance) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=12000.0) as mock_calc_cost_basis:
            
            # Act
            result = service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert
            assert result is not None
            assert len(result) == 2  # Only current equity and total cost basis changed
            
            # Verify only changed fields are in result
            field_names = [change.field_name for change in result]
            assert 'current_equity_balance' in field_names
            assert 'total_cost_basis' in field_names
            assert 'average_equity_balance' not in field_names
            
            # Verify fund fields
            assert mock_fund.current_equity_balance == 6000.0
            assert mock_fund.average_equity_balance == 4500.0  # Unchanged
            assert mock_fund.total_cost_basis == 12000.0

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initialization_creates_dependencies(self, service):
        """Test that service initializes with proper dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert service.fund_equity_calculator is not None
        assert hasattr(service.fund_event_repository, 'get_fund_events')
        assert hasattr(service.fund_equity_calculator, 'calculate_event_equity_balances')
        assert hasattr(service.fund_equity_calculator, 'calculate_current_equity_from_balances')
        assert hasattr(service.fund_equity_calculator, 'calculate_average_equity_from_balances')
        assert hasattr(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances')

    ################################################################################
    # Test edge cases
    ################################################################################

    def test_update_fund_equity_fields_with_empty_events_list(self, service, mock_session, mock_fund):
        """Test that update_fund_equity_fields handles empty events list correctly."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=[]) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=0.0) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=0.0) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=0.0) as mock_calc_cost_basis:
            
            # Act
            result = service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert
            assert result is not None
            assert len(result) == 3  # All fields changed to 0.0
            assert mock_fund.current_equity_balance == 0.0
            assert mock_fund.average_equity_balance == 0.0
            assert mock_fund.total_cost_basis == 0.0

    def test_update_fund_equity_fields_preserves_original_values_when_calculations_fail(self, service, mock_session, mock_fund, mock_equity_events, mock_event_balances):
        """Test that update_fund_equity_fields preserves original values when calculations return same values."""
        # Arrange
        original_current = mock_fund.current_equity_balance
        original_average = mock_fund.average_equity_balance
        original_cost_basis = mock_fund.total_cost_basis
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_equity_events) as mock_repo, \
             patch.object(service.fund_equity_calculator, 'calculate_event_equity_balances', return_value=mock_event_balances) as mock_calc_balances, \
             patch.object(service.fund_equity_calculator, 'calculate_current_equity_from_balances', return_value=original_current) as mock_calc_current, \
             patch.object(service.fund_equity_calculator, 'calculate_average_equity_from_balances', return_value=original_average) as mock_calc_average, \
             patch.object(service.fund_equity_calculator, 'calculate_total_cost_basis_from_balances', return_value=original_cost_basis) as mock_calc_cost_basis:
            
            # Act
            result = service.update_fund_equity_fields(mock_fund, mock_session)
            
            # Assert
            assert result is None  # No changes
            assert mock_fund.current_equity_balance == original_current
            assert mock_fund.average_equity_balance == original_average
            assert mock_fund.total_cost_basis == original_cost_basis
