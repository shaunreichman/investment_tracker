"""
Fund IRR Service Unit Tests.

This module tests the FundIrRService class, focusing on IRR calculation logic,
fund status handling, and field change tracking. Tests are precise and focused
on service functionality without testing repository or calculator logic directly.

Test Coverage:
- IRR updates for different fund statuses (ACTIVE, REALIZED, COMPLETED)
- IRR calculation logic for each status type
- Field change tracking and return values
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_irr_service import FundIrRService
from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums.fund_enums import FundStatus
from src.fund.enums.fund_event_enums import EventType
from tests.factories.fund_factories import FundFactory, FundEventFactory


class TestFundIrRService:
    """Test suite for FundIrRService."""

    @pytest.fixture
    def service(self):
        """Create a FundIrRService instance for testing."""
        return FundIrRService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance with initial IRR values."""
        fund = FundFactory.build(
            id=1,
            status=FundStatus.ACTIVE,
            completed_irr_gross=0.15,
            completed_irr_after_tax=0.12,
            completed_irr_real=0.10
        )
        return fund

    @pytest.fixture
    def mock_events(self):
        """Mock fund events for IRR calculation."""
        return [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date='2023-01-01'
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=120000.0,
                event_date='2023-12-31'
            )
        ]

    ################################################################################
    # Test update_irrs method - ACTIVE status
    ################################################################################

    def test_update_irrs_active_status_sets_irrs_to_none(self, service, mock_session, mock_fund):
        """Test that ACTIVE status sets all IRRs to None."""
        # Arrange
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10

        # Act
        result = service.update_irrs(mock_fund, mock_session)

        # Assert
        assert mock_fund.completed_irr_gross is None
        assert mock_fund.completed_irr_after_tax is None
        assert mock_fund.completed_irr_real is None
        
        # Should return field changes for all three IRR fields
        assert result is not None
        assert len(result) == 3
        
        # Check field changes
        field_names = [change.field_name for change in result]
        assert 'completed_irr_gross' in field_names
        assert 'completed_irr_after_tax' in field_names
        assert 'completed_irr_real' in field_names
        
        # Check field change values
        for change in result:
            assert change.object == 'FUND'
            assert change.object_id == 1
            assert change.new_value is None

    def test_update_irrs_active_status_no_changes_when_already_none(self, service, mock_session, mock_fund):
        """Test that ACTIVE status returns None when IRRs are already None."""
        # Arrange
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.completed_irr_gross = None
        mock_fund.completed_irr_after_tax = None
        mock_fund.completed_irr_real = None

        # Act
        result = service.update_irrs(mock_fund, mock_session)

        # Assert
        assert result is None
        assert mock_fund.completed_irr_gross is None
        assert mock_fund.completed_irr_after_tax is None
        assert mock_fund.completed_irr_real is None

    ################################################################################
    # Test update_irrs method - REALIZED status
    ################################################################################

    def test_update_irrs_realized_status_calculates_gross_irr_only(self, service, mock_session, mock_fund, mock_events):
        """Test that REALIZED status calculates only gross IRR."""
        # Arrange
        mock_fund.status = FundStatus.REALIZED
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', return_value=0.20) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert mock_fund.completed_irr_gross == 0.20
            assert mock_fund.completed_irr_after_tax is None
            assert mock_fund.completed_irr_real is None
            
            # Verify repository call
            mock_get_events.assert_called_once_with(mock_session, fund_ids=[1])
            
            # Verify IRR calculation call
            mock_calculate.assert_called_once_with(
                mock_events, 
                include_tax_payments=False, 
                include_risk_free_charges=False, 
                include_eofy_debt_cost=False
            )
            
            # Should return field changes for all three IRR fields (gross changes, after_tax and real set to None)
            assert result is not None
            assert len(result) == 3
            
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names
            
            # Check gross IRR change
            gross_change = next(change for change in result if change.field_name == 'completed_irr_gross')
            assert gross_change.old_value == 0.15
            assert gross_change.new_value == 0.20

    def test_update_irrs_realized_status_no_changes_when_gross_irr_same(self, service, mock_session, mock_fund, mock_events):
        """Test that REALIZED status returns None when gross IRR doesn't change."""
        # Arrange
        mock_fund.status = FundStatus.REALIZED
        mock_fund.completed_irr_gross = 0.20
        mock_fund.completed_irr_after_tax = None  # Already None
        mock_fund.completed_irr_real = None       # Already None
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', return_value=0.20) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert result is None
            assert mock_fund.completed_irr_gross == 0.20
            assert mock_fund.completed_irr_after_tax is None
            assert mock_fund.completed_irr_real is None

    ################################################################################
    # Test update_irrs method - COMPLETED status
    ################################################################################

    def test_update_irrs_completed_status_calculates_all_irrs(self, service, mock_session, mock_fund, mock_events):
        """Test that COMPLETED status calculates all three IRR types."""
        # Arrange
        mock_fund.status = FundStatus.COMPLETED
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', side_effect=[0.20, 0.18, 0.16]) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert mock_fund.completed_irr_gross == 0.20
            assert mock_fund.completed_irr_after_tax == 0.18
            assert mock_fund.completed_irr_real == 0.16
            
            # Verify repository call
            mock_get_events.assert_called_once_with(mock_session, fund_ids=[1])
            
            # Verify IRR calculation calls
            assert mock_calculate.call_count == 3
            calls = mock_calculate.call_args_list
            
            # Gross IRR call
            assert calls[0][0] == (mock_events,)
            assert calls[0][1] == {
                'include_tax_payments': False,
                'include_risk_free_charges': False,
                'include_eofy_debt_cost': False
            }
            
            # After-tax IRR call
            assert calls[1][0] == (mock_events,)
            assert calls[1][1] == {
                'include_tax_payments': True,
                'include_risk_free_charges': False,
                'include_eofy_debt_cost': False
            }
            
            # Real IRR call
            assert calls[2][0] == (mock_events,)
            assert calls[2][1] == {
                'include_tax_payments': True,
                'include_risk_free_charges': True,
                'include_eofy_debt_cost': True
            }
            
            # Should return field changes for all three IRR fields
            assert result is not None
            assert len(result) == 3
            
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names

    def test_update_irrs_completed_status_partial_changes(self, service, mock_session, mock_fund, mock_events):
        """Test that COMPLETED status returns only changed fields."""
        # Arrange
        mock_fund.status = FundStatus.COMPLETED
        mock_fund.completed_irr_gross = 0.20  # Same as calculated
        mock_fund.completed_irr_after_tax = 0.12  # Different from calculated
        mock_fund.completed_irr_real = 0.10  # Different from calculated
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', side_effect=[0.20, 0.18, 0.16]) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert mock_fund.completed_irr_gross == 0.20
            assert mock_fund.completed_irr_after_tax == 0.18
            assert mock_fund.completed_irr_real == 0.16
            
            # Should return field changes for only changed fields
            assert result is not None
            assert len(result) == 2
            
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' not in field_names  # No change
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names

    ################################################################################
    # Test update_irrs method - edge cases
    ################################################################################

    def test_update_irrs_handles_none_irr_calculation(self, service, mock_session, mock_fund, mock_events):
        """Test that update_irrs handles None IRR calculation results."""
        # Arrange
        mock_fund.status = FundStatus.REALIZED
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_events) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', return_value=None) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert mock_fund.completed_irr_gross is None
            assert mock_fund.completed_irr_after_tax is None
            assert mock_fund.completed_irr_real is None
            
            # Should return field changes for all three IRR fields (all set to None)
            assert result is not None
            assert len(result) == 3
            
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names
            
            # Check gross IRR change
            gross_change = next(change for change in result if change.field_name == 'completed_irr_gross')
            assert gross_change.old_value == 0.15
            assert gross_change.new_value is None

    def test_update_irrs_handles_empty_events_list(self, service, mock_session, mock_fund):
        """Test that update_irrs handles empty events list."""
        # Arrange
        mock_fund.status = FundStatus.REALIZED
        mock_fund.completed_irr_gross = 0.15
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events, \
             patch.object(service.shared_irr_service, 'calculate_irr_base', return_value=None) as mock_calculate:
            
            # Act
            result = service.update_irrs(mock_fund, mock_session)

            # Assert
            assert mock_fund.completed_irr_gross is None
            mock_get_events.assert_called_once_with(mock_session, fund_ids=[1])
            mock_calculate.assert_called_once()

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert service.shared_irr_service is not None
        assert hasattr(service, 'fund_event_repository')
        assert hasattr(service, 'shared_irr_service')

    ################################################################################
    # Test field change creation
    ################################################################################

    def test_field_change_creation_has_correct_structure(self, service, mock_session, mock_fund):
        """Test that field changes are created with correct structure."""
        # Arrange
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10

        # Act
        result = service.update_irrs(mock_fund, mock_session)

        # Assert
        assert result is not None
        assert len(result) == 3
        
        for change in result:
            assert isinstance(change, FundFieldChange)
            assert change.object == 'FUND'
            assert change.object_id == 1
            assert change.field_name in ['completed_irr_gross', 'completed_irr_after_tax', 'completed_irr_real']
            assert change.new_value is None
            assert change.old_value in [0.15, 0.12, 0.10]
