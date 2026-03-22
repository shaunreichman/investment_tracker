"""
Fund Units Service Unit Tests.

This module tests the FundUnitsService class, focusing on units calculation logic,
unit price tracking, and field change tracking. Tests are precise and focused
on service functionality without testing repository logic directly.

Test Coverage:
- Units calculation from purchase/sale events
- Unit price tracking from various event types
- NAV total calculation (units * unit price)
- Field change tracking for fund and fund event updates
- Edge cases and error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_units_service import FundUnitsService
from src.fund.models import Fund, FundEvent
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundFactory, FundEventFactory


class TestFundUnitsService:
    """Test suite for FundUnitsService."""

    @pytest.fixture
    def service(self):
        """Create a FundUnitsService instance for testing."""
        return FundUnitsService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance with initial units data."""
        return FundFactory.build(
            id=1,
            name='Test Fund',
            current_units=0.0,
            current_unit_price=0.0,
            current_nav_total=0.0
        )

    @pytest.fixture
    def unit_purchase_event(self):
        """Mock unit purchase event."""
        return FundEventFactory.build(
            id=1,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            units_sold=None,
            unit_price=10.0,
            nav_per_share=None,
            units_owned=None
        )

    @pytest.fixture
    def unit_sale_event(self):
        """Mock unit sale event."""
        return FundEventFactory.build(
            id=2,
            event_type=EventType.UNIT_SALE,
            units_purchased=None,
            units_sold=50.0,
            unit_price=12.0,
            nav_per_share=None,
            units_owned=None
        )

    @pytest.fixture
    def nav_update_event(self):
        """Mock NAV update event."""
        return FundEventFactory.build(
            id=3,
            event_type=EventType.NAV_UPDATE,
            units_purchased=None,
            units_sold=None,
            unit_price=None,
            nav_per_share=15.0,
            units_owned=None
        )

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initialization(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert hasattr(service, 'fund_event_repository')

    ################################################################################
    # Test update_fund_units method - basic functionality
    ################################################################################

    def test_update_fund_units_single_purchase(self, service, mock_session, mock_fund, unit_purchase_event):
        """Test units calculation with single unit purchase."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[unit_purchase_event]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 4  # 3 fund changes + 1 fund event change
            
            # Verify fund updates
            assert mock_fund.current_units == 100.0
            assert mock_fund.current_unit_price == 10.0
            assert mock_fund.current_nav_total == 1000.0  # 100 * 10
            
            # Verify fund event update
            assert unit_purchase_event.units_owned == 100.0
            
            # Verify repository call
            mock_get_events.assert_called_once_with(
                mock_session, 
                fund_ids=[1], 
                event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.NAV_UPDATE],
                sort_order=SortOrder.ASC
            )

    def test_update_fund_units_purchase_and_sale(self, service, mock_session, mock_fund, unit_purchase_event, unit_sale_event):
        """Test units calculation with purchase followed by sale."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        events = [unit_purchase_event, unit_sale_event]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=events) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 5  # 3 fund changes + 2 fund event changes
            
            # Verify fund updates (net units: 100 - 50 = 50)
            assert mock_fund.current_units == 50.0
            assert mock_fund.current_unit_price == 12.0  # Latest unit price from sale
            assert mock_fund.current_nav_total == 600.0  # 50 * 12
            
            # Verify fund event updates
            assert unit_purchase_event.units_owned == 100.0
            assert unit_sale_event.units_owned == 50.0

    def test_update_fund_units_with_nav_update(self, service, mock_session, mock_fund, unit_purchase_event, nav_update_event):
        """Test units calculation with NAV update affecting unit price."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        events = [unit_purchase_event, nav_update_event]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=events) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 5  # 3 fund changes + 2 fund event changes (both events get units_owned updated)
            
            # Verify fund updates
            assert mock_fund.current_units == 100.0
            assert mock_fund.current_unit_price == 15.0  # Latest price from NAV update
            assert mock_fund.current_nav_total == 1500.0  # 100 * 15
            
            # Verify fund event update
            assert unit_purchase_event.units_owned == 100.0

    ################################################################################
    # Test update_fund_units method - edge cases
    ################################################################################

    def test_update_fund_units_no_events(self, service, mock_session, mock_fund):
        """Test units calculation with no events."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result == []  # No changes when no events
            assert mock_fund.current_units == 0.0
            assert mock_fund.current_unit_price == 0.0
            assert mock_fund.current_nav_total == 0.0

    def test_update_fund_units_no_changes_needed(self, service, mock_session, mock_fund, unit_purchase_event):
        """Test units calculation when no changes are needed."""
        # Arrange
        mock_fund.current_units = 100.0
        mock_fund.current_unit_price = 10.0
        mock_fund.current_nav_total = 1000.0
        unit_purchase_event.units_owned = 100.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[unit_purchase_event]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result == []  # No changes when values are already correct
            assert mock_fund.current_units == 100.0
            assert mock_fund.current_unit_price == 10.0
            assert mock_fund.current_nav_total == 1000.0

    def test_update_fund_units_partial_changes(self, service, mock_session, mock_fund, unit_purchase_event):
        """Test units calculation when only some values need updating."""
        # Arrange
        mock_fund.current_units = 100.0  # Already correct
        mock_fund.current_unit_price = 5.0  # Needs updating
        mock_fund.current_nav_total = 500.0  # Needs updating
        unit_purchase_event.units_owned = 100.0  # Already correct
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[unit_purchase_event]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 2  # Only unit price and NAV total changes
            
            # Verify fund updates
            assert mock_fund.current_units == 100.0  # Unchanged
            assert mock_fund.current_unit_price == 10.0  # Updated
            assert mock_fund.current_nav_total == 1000.0  # Updated
            
            # Verify fund event unchanged
            assert unit_purchase_event.units_owned == 100.0

    ################################################################################
    # Test update_fund_units method - complex scenarios
    ################################################################################

    def test_update_fund_units_multiple_events_sequence(self, service, mock_session, mock_fund):
        """Test units calculation with multiple events in sequence."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        events = [
            FundEventFactory.build(
                id=1, event_type=EventType.UNIT_PURCHASE, 
                units_purchased=100.0, unit_price=10.0, units_owned=None
            ),
            FundEventFactory.build(
                id=2, event_type=EventType.UNIT_PURCHASE, 
                units_purchased=50.0, unit_price=12.0, units_owned=None
            ),
            FundEventFactory.build(
                id=3, event_type=EventType.UNIT_SALE, 
                units_sold=30.0, unit_price=15.0, units_owned=None
            ),
            FundEventFactory.build(
                id=4, event_type=EventType.NAV_UPDATE, 
                nav_per_share=18.0, units_owned=None
            )
        ]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=events) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 7  # 3 fund changes + 4 fund event changes
            
            # Verify fund updates (net units: 100 + 50 - 30 = 120)
            assert mock_fund.current_units == 120.0
            assert mock_fund.current_unit_price == 18.0  # Latest from NAV update
            assert mock_fund.current_nav_total == 2160.0  # 120 * 18
            
            # Verify fund event updates
            assert events[0].units_owned == 100.0
            assert events[1].units_owned == 150.0
            assert events[2].units_owned == 120.0
            assert events[3].units_owned == 120.0

    def test_update_fund_units_negative_units(self, service, mock_session, mock_fund, unit_sale_event):
        """Test units calculation with sale exceeding purchases (negative units)."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        unit_sale_event.units_sold = 50.0  # Sale without prior purchase
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[unit_sale_event]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 4  # 3 fund changes + 1 fund event change
            
            # Verify fund updates (negative units: 0 - 50 = -50)
            assert mock_fund.current_units == -50.0
            assert mock_fund.current_unit_price == 12.0
            assert mock_fund.current_nav_total == -600.0  # -50 * 12
            
            # Verify fund event update
            assert unit_sale_event.units_owned == -50.0

    ################################################################################
    # Test update_fund_units method - field change structure
    ################################################################################

    def test_field_change_structure(self, service, mock_session, mock_fund, unit_purchase_event):
        """Test that field changes are created with correct structure."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[unit_purchase_event]) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 4
            
            # Check fund field changes
            fund_changes = [change for change in result if change.domain_object_type == DomainObjectType.FUND]
            assert len(fund_changes) == 3
            
            for change in fund_changes:
                assert isinstance(change, DomainFieldChange)
                assert change.domain_object_type == DomainObjectType.FUND
                assert change.domain_object_id == 1
                assert change.field_name in ['current_units', 'current_unit_price', 'current_nav_total']
                assert change.old_value == 0.0
                assert change.new_value in [100.0, 10.0, 1000.0]
            
            # Check fund event field change
            event_changes = [change for change in result if change.domain_object_type == DomainObjectType.FUND_EVENT]
            assert len(event_changes) == 1
            
            event_change = event_changes[0]
            assert isinstance(event_change, DomainFieldChange)
            assert event_change.domain_object_type == DomainObjectType.FUND_EVENT
            assert event_change.domain_object_id == 1
            assert event_change.field_name == 'units_owned'
            assert event_change.old_value is None
            assert event_change.new_value == 100.0

    ################################################################################
    # Test update_fund_units method - unit price priority
    ################################################################################

    def test_unit_price_priority_from_events(self, service, mock_session, mock_fund):
        """Test that unit price is updated from the latest relevant event."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        events = [
            FundEventFactory.build(
                id=1, event_type=EventType.UNIT_PURCHASE, 
                units_purchased=100.0, unit_price=10.0, units_owned=None
            ),
            FundEventFactory.build(
                id=2, event_type=EventType.UNIT_SALE, 
                units_sold=50.0, unit_price=12.0, units_owned=None
            ),
            FundEventFactory.build(
                id=3, event_type=EventType.NAV_UPDATE, 
                nav_per_share=15.0, units_owned=None
            )
        ]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=events) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            # Unit price should be from the last event (NAV_UPDATE with nav_per_share=15.0)
            assert mock_fund.current_unit_price == 15.0

    def test_unit_price_ignores_none_values(self, service, mock_session, mock_fund):
        """Test that unit price ignores None values from events."""
        # Arrange
        mock_fund.current_units = 0.0
        mock_fund.current_unit_price = 0.0
        mock_fund.current_nav_total = 0.0
        
        events = [
            FundEventFactory.build(
                id=1, event_type=EventType.UNIT_PURCHASE, 
                units_purchased=100.0, unit_price=None, units_owned=None  # None unit_price
            ),
            FundEventFactory.build(
                id=2, event_type=EventType.NAV_UPDATE, 
                nav_per_share=None, units_owned=None  # None nav_per_share
            ),
            FundEventFactory.build(
                id=3, event_type=EventType.UNIT_SALE, 
                units_sold=50.0, unit_price=12.0, units_owned=None
            )
        ]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=events) as mock_get_events:
            # Act
            result = service.update_fund_units(mock_fund, mock_session)

            # Assert
            # Unit price should be from the last event with valid price (unit_sale with unit_price=12.0)
            assert mock_fund.current_unit_price == 12.0
