"""
Fund NAV Service Unit Tests.

This module tests the FundNavService class, focusing on business logic,
NAV calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- NAV fund field updates with change tracking
- NAV fund event field calculations
- Service layer orchestration
- Error handling and edge cases
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_nav_service import FundNavService
from src.fund.models import Fund, FundEvent
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import SortOrder
from tests.factories.fund_factories import FundFactory, FundEventFactory


class TestFundNavService:
    """Test suite for FundNavService."""

    @pytest.fixture
    def service(self):
        """Create a FundNavService instance for testing."""
        return FundNavService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_fund(self):
        """Mock fund instance with NAV fields."""
        from src.fund.enums.fund_enums import FundTrackingType
        fund = FundFactory.build(
            id=1,
            current_unit_price=10.50,
            current_nav_total=10500.0,
            tracking_type=FundTrackingType.NAV_BASED
        )
        return fund

    @pytest.fixture
    def mock_nav_events(self):
        """Mock NAV update events."""
        return [
            FundEventFactory.build(
                id=1,
                event_type=EventType.NAV_UPDATE,
                nav_per_share=12.75,
                units_owned=1000.0
            ),
            FundEventFactory.build(
                id=2,
                event_type=EventType.NAV_UPDATE,
                nav_per_share=13.25,
                units_owned=1000.0
            )
        ]

    ################################################################################
    # Test update_nav_fund_fields method
    ################################################################################

    def test_update_nav_fund_fields_with_changes_returns_field_changes(self, service, mock_session, mock_fund, mock_nav_events):
        """Test that update_nav_fund_fields returns field changes when NAV values change."""
        # Arrange
        old_unit_price = mock_fund.current_unit_price
        old_nav_total = mock_fund.current_nav_total
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_nav_events) as mock_repo:
            # Act
            result = service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 5  # 2 fund changes + 3 event changes (previous_nav_per_share, nav_change_absolute, nav_change_percentage)
            
            # Check unit price change
            unit_price_change = next((change for change in result if change.field_name == 'current_unit_price'), None)
            assert unit_price_change is not None
            assert unit_price_change.domain_object_type == DomainObjectType.FUND
            assert unit_price_change.domain_object_id == mock_fund.id
            assert unit_price_change.old_value == old_unit_price
            assert unit_price_change.new_value == 13.25  # Last event's nav_per_share
            
            # Check NAV total change
            nav_total_change = next((change for change in result if change.field_name == 'current_nav_total'), None)
            assert nav_total_change is not None
            assert nav_total_change.domain_object_type == DomainObjectType.FUND
            assert nav_total_change.domain_object_id == mock_fund.id
            assert nav_total_change.old_value == old_nav_total
            assert nav_total_change.new_value == 13250.0  # 13.25 * 1000
            
            # Verify fund was updated
            assert mock_fund.current_unit_price == 13.25
            assert mock_fund.current_nav_total == 13250.0
            
            # Verify repository was called correctly (twice: NAV events and unit events)
            assert mock_repo.call_count == 2
            # First call for NAV events
            mock_repo.assert_any_call(
                mock_session, 
                fund_ids=[mock_fund.id], 
                event_types=[EventType.NAV_UPDATE],
                sort_order=SortOrder.ASC
            )
            # Second call for unit events
            mock_repo.assert_any_call(
                mock_session, 
                fund_ids=[mock_fund.id], 
                event_types=[EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
                sort_order=SortOrder.ASC
            )

    def test_update_nav_fund_fields_no_changes_returns_none(self, service, mock_session, mock_fund):
        """Test that update_nav_fund_fields returns None when no changes occur."""
        # Arrange
        mock_fund.current_unit_price = 12.75
        mock_fund.current_nav_total = 12750.0
        
        nav_events = [FundEventFactory.build(
            event_type=EventType.NAV_UPDATE,
            nav_per_share=12.75,  # Same as current
            units_owned=1000.0
        )]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=nav_events) as mock_repo:
            # Act
            result = service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            assert result is None
            assert mock_fund.current_unit_price == 12.75
            assert mock_fund.current_nav_total == 12750.0

    def test_update_nav_fund_fields_no_events_updates_nothing(self, service, mock_session, mock_fund):
        """Test that update_nav_fund_fields handles no events gracefully."""
        # Arrange
        old_unit_price = mock_fund.current_unit_price
        old_nav_total = mock_fund.current_nav_total
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_repo:
            # Act
            result = service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            assert result is None
            assert mock_fund.current_unit_price == old_unit_price
            assert mock_fund.current_nav_total == old_nav_total

    def test_update_nav_fund_fields_only_unit_price_changes(self, service, mock_session, mock_fund):
        """Test that update_nav_fund_fields handles only unit price changes."""
        # Arrange
        old_unit_price = mock_fund.current_unit_price
        old_nav_total = mock_fund.current_nav_total
        
        nav_events = [FundEventFactory.build(
            event_type=EventType.NAV_UPDATE,
            nav_per_share=15.00,  # Different unit price
            units_owned=1000.0  # Same units, so NAV total changes too
        )]
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=nav_events) as mock_repo:
            # Act
            result = service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            assert result is not None
            assert len(result) == 2  # Both unit price and NAV total change
            
            # Verify both changes are tracked
            unit_price_change = next((change for change in result if change.field_name == 'current_unit_price'), None)
            nav_total_change = next((change for change in result if change.field_name == 'current_nav_total'), None)
            
            assert unit_price_change.old_value == old_unit_price
            assert unit_price_change.new_value == 15.00
            assert nav_total_change.old_value == old_nav_total
            assert nav_total_change.new_value == 15000.0

    def test_update_nav_fund_fields_calls_update_nav_fund_event_fields(self, service, mock_session, mock_fund, mock_nav_events):
        """Test that update_nav_fund_fields calls _update_nav_fund_event_fields."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_nav_events) as mock_repo, \
             patch.object(service, '_update_nav_fund_event_fields') as mock_update_events:
            
            # Act
            service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            mock_update_events.assert_called_once_with(mock_nav_events)

    ################################################################################
    # Test update_nav_fund_event_fields method
    ################################################################################

    def test_update_nav_fund_event_fields_multiple_events_calculates_changes(self, service, mock_nav_events):
        """Test that _update_nav_fund_event_fields calculates changes for multiple events."""
        # Arrange
        events = [
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=10.00
            ),
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=12.50
            ),
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=15.00
            )
        ]
        
        # Act
        service._update_nav_fund_event_fields(events)

        # Assert
        # First event should have no previous values
        assert events[0].previous_nav_per_share is None
        assert events[0].nav_change_absolute is None
        assert events[0].nav_change_percentage is None
        
        # Second event should have previous values from first event
        assert events[1].previous_nav_per_share == 10.00
        assert events[1].nav_change_absolute == 2.50  # 12.50 - 10.00
        assert events[1].nav_change_percentage == 0.25  # 2.50 / 10.00
        
        # Third event should have previous values from second event
        assert events[2].previous_nav_per_share == 12.50
        assert events[2].nav_change_absolute == 2.50  # 15.00 - 12.50
        assert events[2].nav_change_percentage == 0.20  # 2.50 / 12.50

    def test_update_nav_fund_event_fields_single_event_no_calculations(self, service):
        """Test that _update_nav_fund_event_fields handles single event correctly."""
        # Arrange
        events = [FundEventFactory.build(
            event_type=EventType.NAV_UPDATE,
            nav_per_share=10.00
        )]
        
        # Act
        service._update_nav_fund_event_fields(events)

        # Assert
        assert events[0].previous_nav_per_share is None
        assert events[0].nav_change_absolute is None
        assert events[0].nav_change_percentage is None

    def test_update_nav_fund_event_fields_empty_list_no_error(self, service):
        """Test that _update_nav_fund_event_fields handles empty list gracefully."""
        # Arrange
        events = []
        
        # Act & Assert - should not raise any errors
        service._update_nav_fund_event_fields(events)

    def test_update_nav_fund_event_fields_negative_change_calculations(self, service):
        """Test that _update_nav_fund_event_fields handles negative NAV changes correctly."""
        # Arrange
        events = [
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=15.00
            ),
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=12.00
            )
        ]
        
        # Act
        service._update_nav_fund_event_fields(events)

        # Assert
        assert events[1].previous_nav_per_share == 15.00
        assert events[1].nav_change_absolute == -3.00  # 12.00 - 15.00
        assert events[1].nav_change_percentage == -0.20  # -3.00 / 15.00

    def test_update_nav_fund_event_fields_zero_previous_nav_handles_division_by_zero(self, service):
        """Test that _update_nav_fund_event_fields handles zero previous NAV gracefully."""
        # Arrange
        events = [
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=0.0
            ),
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=10.00
            )
        ]
        
        # Act
        service._update_nav_fund_event_fields(events)

        # Assert
        assert events[1].previous_nav_per_share == 0.0
        assert events[1].nav_change_absolute == 10.00  # 10.00 - 0.0
        # Should handle division by zero gracefully - percentage should be None
        assert events[1].nav_change_percentage is None  # Cannot calculate percentage from zero

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.fund_event_repository is not None
        assert hasattr(service, 'fund_event_repository')

    def test_service_initializes_with_custom_repository(self):
        """Test that service can be initialized with custom repository."""
        # Arrange
        custom_repository = Mock()
        
        # Act
        service = FundNavService()
        service.fund_event_repository = custom_repository
        
        # Assert
        assert service.fund_event_repository == custom_repository

    ################################################################################
    # Test edge cases and error handling
    ################################################################################

    def test_update_nav_fund_fields_with_none_events_handles_gracefully(self, service, mock_session, mock_fund):
        """Test that update_nav_fund_fields handles None events gracefully."""
        # Arrange
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=None) as mock_repo:
            # Act & Assert - should not raise error
            result = service.update_nav_fund_fields(mock_fund, mock_session)
            assert result is None

    def test_update_nav_fund_fields_preserves_original_values_when_no_events(self, service, mock_session, mock_fund):
        """Test that update_nav_fund_fields preserves original values when no events."""
        # Arrange
        original_unit_price = mock_fund.current_unit_price
        original_nav_total = mock_fund.current_nav_total
        
        with patch.object(service.fund_event_repository, 'get_fund_events', return_value=[]) as mock_repo:
            # Act
            result = service.update_nav_fund_fields(mock_fund, mock_session)

            # Assert
            assert result is None
            assert mock_fund.current_unit_price == original_unit_price
            assert mock_fund.current_nav_total == original_nav_total

    def test_update_nav_fund_event_fields_with_mixed_event_types_processes_all(self, service):
        """Test that _update_nav_fund_event_fields processes all events in sequence."""
        # Arrange
        events = [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                nav_per_share=10.00
            ),
            FundEventFactory.build(
                event_type=EventType.NAV_UPDATE,
                nav_per_share=12.00
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                nav_per_share=15.00
            )
        ]
        
        # Act
        service._update_nav_fund_event_fields(events)

        # Assert
        # First event should have no previous values
        assert events[0].previous_nav_per_share is None  # CAPITAL_CALL (first)
        # Second event should have previous values from first event
        assert events[1].previous_nav_per_share == 10.00  # NAV_UPDATE (second)
        assert events[1].nav_change_absolute == 2.00  # 12.00 - 10.00
        assert events[1].nav_change_percentage == 0.20  # 2.00 / 10.00
        # Third event should have previous values from second event
        assert events[2].previous_nav_per_share == 12.00  # DISTRIBUTION (third)
        assert events[2].nav_change_absolute == 3.00  # 15.00 - 12.00
        assert events[2].nav_change_percentage == 0.25  # 3.00 / 12.00
