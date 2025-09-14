"""
Tests for FundNavService.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.fund.services.fund_nav_service import FundNavService
from src.fund.models import Fund, FundEvent, FundFieldChange
from src.fund.enums import EventType, SortOrder


class TestFundNavService:
    """Test cases for FundNavService."""

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def fund_nav_service(self, mock_session):
        """Create FundNavService instance with mock session."""
        return FundNavService(mock_session)

    @pytest.fixture
    def sample_fund(self):
        """Create a sample fund for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.current_unit_price = 100.0
        fund.current_nav_total = 10000.0
        return fund

    @pytest.fixture
    def sample_nav_event(self):
        """Create a sample NAV update event."""
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': 105.0,
            'units_owned': 100.0
        }
        event.previous_nav_per_share = None
        event.nav_change_absolute = None
        event.nav_change_percentage = None
        return event

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_with_events(self, mock_repo, fund_nav_service, sample_fund, sample_nav_event, mock_session):
        """Test updating NAV fields when NAV events exist."""
        # Arrange
        mock_repo.get_by_fund.return_value = [sample_nav_event]
        
        # Act
        result = fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)
        
        # Assert
        assert result is not None
        assert len(result) == 2
        
        # Check current_unit_price change
        unit_price_change = next((change for change in result if change.field_name == 'current_unit_price'), None)
        assert unit_price_change is not None
        assert unit_price_change.old_value == 100.0
        assert unit_price_change.new_value == 105.0
        
        # Check current_nav_total change
        nav_total_change = next((change for change in result if change.field_name == 'current_nav_total'), None)
        assert nav_total_change is not None
        assert nav_total_change.old_value == 10000.0
        assert nav_total_change.new_value == 10500.0
        
        # Verify repository was called correctly
        mock_repo.get_by_fund.assert_called_once_with(
            sample_fund.id, 
            mock_session,
            event_types=[EventType.NAV_UPDATE],
            sort_order=SortOrder.ASC
        )

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_no_events(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test updating NAV fields when no NAV events exist."""
        # Arrange
        mock_repo.get_by_fund.return_value = []
        
        # Act
        result = fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)
        
        # Assert
        assert result is None
        mock_repo.get_by_fund.assert_called_once()

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_no_changes(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test updating NAV fields when events exist but values don't change."""
        # Arrange
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': 100.0,  # Same as current value
            'units_owned': 100.0
        }
        mock_repo.get_by_fund.return_value = [event]
        
        # Act
        result = fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)
        
        # Assert
        assert result is None

    def test_update_nav_fund_event_fields_single_event(self, fund_nav_service, sample_nav_event):
        """Test updating NAV event fields with single event."""
        # Arrange
        events = [sample_nav_event]
        
        # Act
        fund_nav_service.update_nav_fund_event_fields(events)
        
        # Assert
        # Single event should not have previous values set
        assert sample_nav_event.previous_nav_per_share is None
        assert sample_nav_event.nav_change_absolute is None
        assert sample_nav_event.nav_change_percentage is None

    def test_update_nav_fund_event_fields_multiple_events(self, fund_nav_service):
        """Test updating NAV event fields with multiple events."""
        # Arrange
        event1 = Mock(spec=FundEvent)
        event1.event_data = {'nav_per_share': 100.0}
        event1.previous_nav_per_share = None
        event1.nav_change_absolute = None
        event1.nav_change_percentage = None
        
        event2 = Mock(spec=FundEvent)
        event2.event_data = {'nav_per_share': 105.0}
        event2.previous_nav_per_share = None
        event2.nav_change_absolute = None
        event2.nav_change_percentage = None
        
        events = [event1, event2]
        
        # Act
        fund_nav_service.update_nav_fund_event_fields(events)
        
        # Assert
        # First event should remain unchanged
        assert event1.previous_nav_per_share is None
        assert event1.nav_change_absolute is None
        assert event1.nav_change_percentage is None
        
        # Second event should have calculated values
        assert event2.previous_nav_per_share == 100.0
        assert event2.nav_change_absolute == 5.0
        assert event2.nav_change_percentage == 0.05

    def test_update_nav_fund_event_fields_three_events(self, fund_nav_service):
        """Test updating NAV event fields with three events."""
        # Arrange
        event1 = Mock(spec=FundEvent)
        event1.event_data = {'nav_per_share': 100.0}
        event1.previous_nav_per_share = None
        event1.nav_change_absolute = None
        event1.nav_change_percentage = None
        
        event2 = Mock(spec=FundEvent)
        event2.event_data = {'nav_per_share': 105.0}
        event2.previous_nav_per_share = None
        event2.nav_change_absolute = None
        event2.nav_change_percentage = None
        
        event3 = Mock(spec=FundEvent)
        event3.event_data = {'nav_per_share': 110.0}
        event3.previous_nav_per_share = None
        event3.nav_change_absolute = None
        event3.nav_change_percentage = None
        
        events = [event1, event2, event3]
        
        # Act
        fund_nav_service.update_nav_fund_event_fields(events)
        
        # Assert
        # First event unchanged
        assert event1.previous_nav_per_share is None
        
        # Second event relative to first
        assert event2.previous_nav_per_share == 100.0
        assert event2.nav_change_absolute == 5.0
        assert event2.nav_change_percentage == 0.05
        
        # Third event relative to second
        assert event3.previous_nav_per_share == 105.0
        assert event3.nav_change_absolute == 5.0
        assert event3.nav_change_percentage == pytest.approx(0.047619, rel=1e-5)

    def test_update_nav_fund_event_fields_empty_list(self, fund_nav_service):
        """Test updating NAV event fields with empty event list."""
        # Arrange
        events = []
        
        # Act & Assert - Should not raise any exceptions
        fund_nav_service.update_nav_fund_event_fields(events)

    def test_update_nav_fund_event_fields_negative_change(self, fund_nav_service):
        """Test updating NAV event fields with negative NAV change."""
        # Arrange
        event1 = Mock(spec=FundEvent)
        event1.event_data = {'nav_per_share': 100.0}
        
        event2 = Mock(spec=FundEvent)
        event2.event_data = {'nav_per_share': 95.0}
        
        events = [event1, event2]
        
        # Act
        fund_nav_service.update_nav_fund_event_fields(events)
        
        # Assert
        assert event2.previous_nav_per_share == 100.0
        assert event2.nav_change_absolute == -5.0
        assert event2.nav_change_percentage == -0.05

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_missing_event_data_keys(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test handling when event_data is missing required keys."""
        # Arrange
        event = Mock(spec=FundEvent)
        event.event_data = {'nav_per_share': 105.0}  # Missing 'units_owned'
        mock_repo.get_by_fund.return_value = [event]
        
        # Act & Assert - Should raise KeyError
        with pytest.raises(KeyError):
            fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_none_values(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test handling when event_data contains None values."""
        # Arrange
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': None,
            'units_owned': 100.0
        }
        mock_repo.get_by_fund.return_value = [event]
        
        # Act & Assert - Should raise TypeError
        with pytest.raises(TypeError):
            fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)

    def test_update_nav_fund_event_fields_zero_previous_nav(self, fund_nav_service):
        """Test percentage calculation when previous NAV is zero."""
        # Arrange
        event1 = Mock(spec=FundEvent)
        event1.event_data = {'nav_per_share': 0.0}
        
        event2 = Mock(spec=FundEvent)
        event2.event_data = {'nav_per_share': 100.0}
        
        events = [event1, event2]
        
        # Act & Assert - Should raise ZeroDivisionError
        with pytest.raises(ZeroDivisionError):
            fund_nav_service.update_nav_fund_event_fields(events)

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_repository_error(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test handling when repository throws an exception."""
        # Arrange
        mock_repo.get_by_fund.side_effect = Exception("Database connection failed")
        
        # Act & Assert - Should propagate the exception
        with pytest.raises(Exception, match="Database connection failed"):
            fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_large_numbers(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test with very large NAV values."""
        # Arrange
        sample_fund.current_unit_price = 1e6  # 1 million
        sample_fund.current_nav_total = 1e9   # 1 billion
        
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': 1.5e6,  # 1.5 million
            'units_owned': 1000.0
        }
        mock_repo.get_by_fund.return_value = [event]
        
        # Act
        result = fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)
        
        # Assert
        assert result is not None
        assert len(result) == 2
        
        unit_price_change = next((change for change in result if change.field_name == 'current_unit_price'), None)
        assert unit_price_change.old_value == 1e6
        assert unit_price_change.new_value == 1.5e6
        
        nav_total_change = next((change for change in result if change.field_name == 'current_nav_total'), None)
        assert nav_total_change.old_value == 1e9
        assert nav_total_change.new_value == 1.5e9

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_precision(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test precision with very small NAV changes."""
        # Arrange
        sample_fund.current_unit_price = 100.0
        sample_fund.current_nav_total = 10000.0
        
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': 100.000001,  # Very small change
            'units_owned': 100.0
        }
        mock_repo.get_by_fund.return_value = [event]
        
        # Act
        result = fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)
        
        # Assert
        assert result is not None
        assert len(result) == 2
        
        unit_price_change = next((change for change in result if change.field_name == 'current_unit_price'), None)
        assert unit_price_change.old_value == 100.0
        assert unit_price_change.new_value == 100.000001
        
        nav_total_change = next((change for change in result if change.field_name == 'current_nav_total'), None)
        assert nav_total_change.old_value == 10000.0
        assert nav_total_change.new_value == 10000.0001

    @patch('src.fund.services.fund_nav_service.FundEventRepository')
    def test_update_nav_fund_fields_string_values(self, mock_repo, fund_nav_service, sample_fund, mock_session):
        """Test handling when event_data contains string values."""
        # Arrange
        event = Mock(spec=FundEvent)
        event.event_data = {
            'nav_per_share': '105.0',  # String instead of float
            'units_owned': 100.0
        }
        mock_repo.get_by_fund.return_value = [event]
        
        # Act & Assert - Should raise TypeError during arithmetic operations
        with pytest.raises(TypeError):
            fund_nav_service.update_nav_fund_fields(sample_fund, mock_session)

    def test_update_nav_fund_event_fields_large_dataset(self, fund_nav_service):
        """Test performance with large number of events."""
        # Arrange
        events = []
        for i in range(100):  # 100 events
            event = Mock(spec=FundEvent)
            event.event_data = {'nav_per_share': 100.0 + i}
            event.previous_nav_per_share = None
            event.nav_change_absolute = None
            event.nav_change_percentage = None
            events.append(event)
        
        # Act
        fund_nav_service.update_nav_fund_event_fields(events)
        
        # Assert
        # First event should remain unchanged
        assert events[0].previous_nav_per_share is None
        assert events[0].nav_change_absolute is None
        assert events[0].nav_change_percentage is None
        
        # Last event should have calculated values
        assert events[-1].previous_nav_per_share == 198.0  # 100 + 98 = 198
        assert events[-1].nav_change_absolute == 1.0
        assert events[-1].nav_change_percentage == pytest.approx(0.005050505050505051, rel=1e-10)
