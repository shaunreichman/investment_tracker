"""
Fund Event Secondary Service Unit Tests.

This module tests the FundEventSecondaryService class, focusing on business logic,
service orchestration, and secondary impact handling. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Service initialization and dependency injection
- Event secondary impact handling for different event types
- Service orchestration and method routing
- Error handling for invalid fund scenarios
- Change tracking and return value validation
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_event_secondary_service import FundEventSecondaryService
from src.fund.models import Fund, FundFieldChange
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation
from tests.factories.fund_factories import FundFactory


class TestFundEventSecondaryService:
    """Test suite for FundEventSecondaryService."""

    @pytest.fixture
    def service(self):
        """Create a FundEventSecondaryService instance for testing."""
        return FundEventSecondaryService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance."""
        return FundFactory.build(
            id=1,
            name='Test Fund',
            current_equity_balance=10000.0
        )

    @pytest.fixture
    def mock_field_change(self):
        """Mock FundFieldChange instance."""
        return FundFieldChange(
            object='FUND',
            object_id=1,
            field_name='current_equity_balance',
            old_value=10000.0,
            new_value=12000.0
        )

    def test_service_initialization(self, service):
        """Test that service initializes all dependencies correctly."""
        # Assert all services are initialized
        assert service.fund_equity_service is not None
        assert service.fund_status_service is not None
        assert service.fund_date_service is not None
        assert service.fund_irr_service is not None
        assert service.fund_pnl_service is not None
        assert service.fund_nav_service is not None
        assert service.fund_repository is not None

    def test_handle_event_secondary_impact_fund_not_found(self, service, mock_session):
        """Test that ValueError is raised when fund is not found."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=None)
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund not found"):
            service.handle_event_secondary_impact(
                fund_id=999,
                fund_event_type=EventType.CAPITAL_CALL,
                fund_event_operation=EventOperation.CREATE,
                session=mock_session,
                event_id=1
            )

    def test_handle_event_secondary_impact_capital_call_create(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for capital call creation."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.CAPITAL_CALL,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Should have 7 changes for capital call create
        
        # Verify fund repository was called
        service.fund_repository.get_fund_by_id.assert_called_once_with(1, mock_session)
        
        # Verify date service calls
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, event_id=1, fund_event_operation=EventOperation.CREATE, session=mock_session
        )
        service.fund_date_service.update_fund_duration.assert_called_once_with(mock_fund, mock_session)
        
        # Verify equity service calls (called twice - once for current, once for other balances)
        assert service.fund_equity_service.update_fund_equity_fields.call_count == 2
        
        # Verify status service call
        service.fund_status_service.update_status_after_equity_event.assert_called_once_with(mock_fund, mock_session)
        
        # Verify IRR service call
        service.fund_irr_service.update_irrs.assert_called_once_with(mock_fund, mock_session)
        
        # Verify PNL service call
        service.fund_pnl_service.update_fund_pnl.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_capital_call_delete(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for capital call deletion."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.CAPITAL_CALL,
            fund_event_operation=EventOperation.DELETE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Should have 7 changes for capital call delete
        
        # Verify date service call for delete (no event_id parameter)
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, fund_event_operation=EventOperation.DELETE, session=mock_session
        )

    def test_handle_event_secondary_impact_return_of_capital(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for return of capital."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_end_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.RETURN_OF_CAPITAL,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Should have 7 changes for return of capital
        
        # Verify end date update was called
        service.fund_date_service.update_fund_end_date.assert_called_once_with(fund=mock_fund, session=mock_session)
        
        # Verify equity service calls
        assert service.fund_equity_service.update_fund_equity_fields.call_count == 2

    def test_handle_event_secondary_impact_nav_update(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for NAV update."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_nav_service.update_nav_fund_fields = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.NAV_UPDATE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3  # Should have 3 changes for NAV update
        
        # Verify NAV service call
        service.fund_nav_service.update_nav_fund_fields.assert_called_once_with(mock_fund, mock_session)
        
        # Verify IRR service call
        service.fund_irr_service.update_irrs.assert_called_once_with(mock_fund, mock_session)
        
        # Verify PNL service call
        service.fund_pnl_service.update_fund_pnl.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_tax_payment(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for tax payment."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_status_service.update_status_after_tax_statement = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.TAX_PAYMENT,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3  # Should have 3 changes for tax payment
        
        # Verify tax statement status update
        service.fund_status_service.update_status_after_tax_statement.assert_called_once_with(mock_fund, mock_session)
        
        # Verify IRR service call
        service.fund_irr_service.update_irrs.assert_called_once_with(mock_fund, mock_session)
        
        # Verify PNL service call
        service.fund_pnl_service.update_fund_pnl.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_distribution(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for distribution (non-equity event)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2  # Should have 2 changes for distribution (IRR + PNL)
        
        # Verify IRR service call
        service.fund_irr_service.update_irrs.assert_called_once_with(mock_fund, mock_session)
        
        # Verify PNL service call
        service.fund_pnl_service.update_fund_pnl.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_unit_purchase(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for unit purchase (equity call event)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.UNIT_PURCHASE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Should have 7 changes for unit purchase
        
        # Verify start date update was called for equity call event
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, event_id=1, fund_event_operation=EventOperation.CREATE, session=mock_session
        )

    def test_handle_event_secondary_impact_unit_sale(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for unit sale (equity return event)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_end_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.UNIT_SALE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Should have 7 changes for unit sale
        
        # Verify end date update was called for equity return event
        service.fund_date_service.update_fund_end_date.assert_called_once_with(fund=mock_fund, session=mock_session)

    def test_handle_event_secondary_impact_no_changes_returned(self, service, mock_session, mock_fund):
        """Test that service handles cases where services return None (no changes)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock all service methods to return None (no changes)
        service.fund_irr_service.update_irrs = Mock(return_value=None)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=None)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Should have 0 changes for distribution when services return None

    def test_handle_event_secondary_impact_mixed_changes(self, service, mock_session, mock_fund, mock_field_change):
        """Test that service handles mix of changes and None values correctly."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        
        # Mock services to return mix of changes and None
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=None)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 1  # Should have 1 change (IRR) and 0 None values (PNL returns None but not added)
        assert result[0] == mock_field_change  # First item should be the field change