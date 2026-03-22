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
from src.fund.models import Fund
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
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
        from src.fund.enums.fund_enums import FundTrackingType
        return FundFactory.build(
            id=1,
            name='Test Fund',
            current_equity_balance=10000.0,
            tracking_type=FundTrackingType.NAV_BASED
        )

    @pytest.fixture
    def mock_field_change(self):
        """Mock DomainFieldChange instance."""
        return DomainFieldChange(
            domain_object_type=DomainObjectType.FUND,
            domain_object_id=1,
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
        assert service.fund_units_service is not None
        assert service.domain_update_event_service is not None

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
                fund_event_id=1
            )

    def test_handle_event_secondary_impact_capital_call_create(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for capital call creation."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.CAPITAL_CALL,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify fund repository was called
        service.fund_repository.get_fund_by_id.assert_called_once_with(1, mock_session)
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 8
        
        # Verify date service calls
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, fund_event_id=1, fund_event_operation=EventOperation.CREATE, session=mock_session
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
        
        # Verify units service call
        service.fund_units_service.update_fund_units.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_capital_call_delete(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for capital call deletion."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.CAPITAL_CALL,
            fund_event_operation=EventOperation.DELETE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 8
        
        # Verify date service call for delete (no fund_event_id parameter)
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, fund_event_operation=EventOperation.DELETE, session=mock_session
        )

    def test_handle_event_secondary_impact_return_of_capital(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for return of capital."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_end_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.RETURN_OF_CAPITAL,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 8
        
        # Verify end date update was called
        service.fund_date_service.update_fund_end_date.assert_called_once_with(fund=mock_fund, session=mock_session)
        
        # Verify equity service calls
        assert service.fund_equity_service.update_fund_equity_fields.call_count == 2

    def test_handle_event_secondary_impact_nav_update(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for NAV update."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_nav_service.update_nav_fund_fields = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.NAV_UPDATE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 4
        
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
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_status_service.update_status_after_tax_statement = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.TAX_PAYMENT,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 4
        
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
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 3
        
        # Verify IRR service call
        service.fund_irr_service.update_irrs.assert_called_once_with(mock_fund, mock_session)
        
        # Verify PNL service call
        service.fund_pnl_service.update_fund_pnl.assert_called_once_with(mock_fund, mock_session)

    def test_handle_event_secondary_impact_unit_purchase(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for unit purchase (equity call event)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_start_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.UNIT_PURCHASE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 8
        
        # Verify start date update was called for equity call event
        service.fund_date_service.update_fund_start_date.assert_called_once_with(
            fund=mock_fund, fund_event_id=1, fund_event_operation=EventOperation.CREATE, session=mock_session
        )

    def test_handle_event_secondary_impact_unit_sale(self, service, mock_session, mock_fund, mock_field_change):
        """Test secondary impact handling for unit sale (equity return event)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return field changes
        service.fund_date_service.update_fund_end_date = Mock(return_value=mock_field_change)
        service.fund_date_service.update_fund_duration = Mock(return_value=mock_field_change)
        service.fund_equity_service.update_fund_equity_fields = Mock(return_value=mock_field_change)
        service.fund_status_service.update_status_after_equity_event = Mock(return_value=mock_field_change)
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=mock_field_change)
        service.fund_units_service.update_fund_units = Mock(return_value=mock_field_change)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.UNIT_SALE,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called for each change
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 8
        
        # Verify end date update was called for equity return event
        service.fund_date_service.update_fund_end_date.assert_called_once_with(fund=mock_fund, session=mock_session)

    def test_handle_event_secondary_impact_no_changes_returned(self, service, mock_session, mock_fund):
        """Test that service handles cases where services return None (no changes)."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock all service methods to return None (no changes)
        service.fund_irr_service.update_irrs = Mock(return_value=None)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=None)
        service.fund_units_service.update_fund_units = Mock(return_value=None)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was not called since no changes were returned
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 0

    def test_handle_event_secondary_impact_mixed_changes(self, service, mock_session, mock_fund, mock_field_change):
        """Test that service handles mix of changes and None values correctly."""
        # Arrange
        service.fund_repository.get_fund_by_id = Mock(return_value=mock_fund)
        service.domain_update_event_service.add_domain_field_changes_to_list = Mock()
        
        # Mock services to return mix of changes and None
        service.fund_irr_service.update_irrs = Mock(return_value=mock_field_change)
        service.fund_pnl_service.update_fund_pnl = Mock(return_value=None)
        service.fund_units_service.update_fund_units = Mock(return_value=None)
        
        # Act
        result = service.handle_event_secondary_impact(
            fund_id=1,
            fund_event_type=EventType.DISTRIBUTION,
            fund_event_operation=EventOperation.CREATE,
            session=mock_session,
            fund_event_id=1
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 0  # Result list starts empty, changes are added via domain_update_event_services
        
        # Verify domain update event services was called only once (for IRR change)
        assert service.domain_update_event_service.add_domain_field_changes_to_list.call_count == 1