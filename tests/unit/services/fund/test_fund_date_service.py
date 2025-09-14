"""
Fund Date Service Tests

This module tests the FundDateService's date calculation and update functionality.
Focus: Testing date-related business logic and field updates for the refactored service.

What we test here:
- Fund start date updates (CREATE vs other operations)
- Fund end date updates for realized/completed funds
- Fund duration calculations
- Financial years retrieval
- Field change tracking
- Error handling and validation

What we DON'T test here (tested elsewhere):
- Repository data access patterns (test_fund_repository.py)
- Model validation (test_fund_model.py)
- Calculator logic (test_fund_duration_calculator.py)
- Entity calculations (test_entity_calculations.py)
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
from src.shared.enums import EventOperation
from src.fund.services.fund_date_service import FundDateService
from src.fund.enums import EventType, FundStatus
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent
from src.fund.models.domain_event import FundFieldChange



@pytest.fixture
def service(db_session):
    """Create a FundDateService instance for testing."""
    service = FundDateService(session=db_session)
    # Replace repositories with mocks
    service.fund_repository = Mock()
    service.fund_event_repository = Mock()
    service.entity_repository = Mock()
    return service


@pytest.fixture
def sample_fund():
    """Create a sample fund for testing."""
    fund = Mock(spec=Fund)
    fund.id = 1
    fund.start_date = date(2023, 1, 1)
    fund.end_date = None
    fund.current_duration = 12
    fund.status = FundStatus.ACTIVE
    fund.entity_id = 1
    return fund


@pytest.fixture
def sample_capital_call_event():
    """Create a sample capital call event for testing."""
    event = Mock(spec=FundEvent)
    event.id = 1
    event.fund_id = 1
    event.event_type = EventType.CAPITAL_CALL
    event.event_date = date(2023, 1, 15)
    return event


class TestFundDateService:
    """Test suite for FundDateService date calculation and update functionality"""


class TestUpdateFundStartDate:
    """Test suite for update_fund_start_date method"""
    
    def test_update_start_date_create_operation_with_capital_call(self, service, sample_fund, sample_capital_call_event, db_session):
        """Test start date update during CREATE operation with capital call event."""
        # Arrange
        sample_fund.start_date = date(2023, 2, 1)  # Set fund start date later than event
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_id.return_value = sample_capital_call_event
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is not None
        assert result.field_name == 'start_date'
        assert result.old_value == date(2023, 2, 1)
        assert result.new_value == date(2023, 1, 15)
        assert sample_fund.start_date == date(2023, 1, 15)
        
        # Verify repository calls
        service.fund_repository.get_by_id.assert_called_once_with(1, db_session)
        service.fund_event_repository.get_by_id.assert_called_once_with(1, db_session)
    
    def test_update_start_date_create_operation_with_unit_purchase(self, service, sample_fund, db_session):
        """Test start date update during CREATE operation with unit purchase event."""
        # Arrange
        sample_fund.start_date = None  # No existing start date
        service.fund_repository.get_by_id.return_value = sample_fund
        
        unit_purchase_event = Mock(spec=FundEvent)
        unit_purchase_event.id = 1
        unit_purchase_event.fund_id = 1
        unit_purchase_event.event_type = EventType.UNIT_PURCHASE
        unit_purchase_event.event_date = date(2023, 2, 1)
        service.fund_event_repository.get_by_id.return_value = unit_purchase_event
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is not None
        assert result.field_name == 'start_date'
        assert result.old_value is None
        assert result.new_value == date(2023, 2, 1)
        assert sample_fund.start_date == date(2023, 2, 1)
    
    def test_update_start_date_create_operation_no_change_when_event_date_later(self, service, sample_fund, sample_capital_call_event, db_session):
        """Test that start date doesn't change when event date is later than existing start date."""
        # Arrange
        sample_capital_call_event.event_date = date(2023, 2, 1)  # Later than fund's start date
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_id.return_value = sample_capital_call_event
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None
        assert sample_fund.start_date == date(2023, 1, 1)  # Unchanged
    
    def test_update_start_date_non_create_operation(self, service, sample_fund, db_session):
        """Test start date update during non-CREATE operation."""
        # Arrange
        sample_fund.start_date = date(2023, 3, 1)  # Later start date
        
        earliest_event = Mock(spec=FundEvent)
        earliest_event.event_date = date(2023, 1, 15)
        
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = [earliest_event]
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=None, 
            fund_event_operation=EventOperation.UPDATE
        )
        
        # Assert
        assert result is not None
        assert result.field_name == 'start_date'
        assert result.old_value == date(2023, 3, 1)
        assert result.new_value == date(2023, 1, 15)
        assert sample_fund.start_date == date(2023, 1, 15)
    
    def test_update_start_date_fund_not_found(self, service, db_session):
        """Test that None is returned when fund is not found."""
        # Arrange
        service.fund_repository.get_by_id.return_value = None
        
        # Act
        result = service.update_fund_start_date(
            fund_id=999, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None
    
    def test_update_start_date_event_not_found_or_wrong_fund(self, service, sample_fund, db_session):
        """Test that None is returned when event is not found or belongs to different fund."""
        # Arrange
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_id.return_value = None
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=999, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None
    
    def test_update_start_date_create_operation_wrong_event_fund_id(self, service, sample_fund, db_session):
        """Test that None is returned when event belongs to different fund."""
        # Arrange
        service.fund_repository.get_by_id.return_value = sample_fund
        
        wrong_fund_event = Mock(spec=FundEvent)
        wrong_fund_event.id = 1
        wrong_fund_event.fund_id = 999  # Different fund ID
        wrong_fund_event.event_type = EventType.CAPITAL_CALL
        wrong_fund_event.event_date = date(2023, 1, 15)
        service.fund_event_repository.get_by_id.return_value = wrong_fund_event
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None
        assert sample_fund.start_date == date(2023, 1, 1)  # Unchanged
    
    def test_update_start_date_non_create_operation_no_events(self, service, sample_fund, db_session):
        """Test start date update during non-CREATE operation when no events exist."""
        # Arrange
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = []
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=None, 
            fund_event_operation=EventOperation.UPDATE
        )
        
        # Assert
        assert result is None
        assert sample_fund.start_date == date(2023, 1, 1)  # Unchanged
    
    def test_update_start_date_create_operation_ignores_non_equity_events(self, service, sample_fund, db_session):
        """Test that CREATE operation ignores events that aren't CAPITAL_CALL or UNIT_PURCHASE."""
        # Arrange
        sample_fund.start_date = date(2023, 2, 1)
        service.fund_repository.get_by_id.return_value = sample_fund
        
        distribution_event = Mock(spec=FundEvent)
        distribution_event.id = 1
        distribution_event.fund_id = 1
        distribution_event.event_type = EventType.DISTRIBUTION  # Not an equity event
        distribution_event.event_date = date(2023, 1, 15)
        service.fund_event_repository.get_by_id.return_value = distribution_event
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=1, 
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None
        assert sample_fund.start_date == date(2023, 2, 1)  # Unchanged
    
    def test_update_start_date_create_operation_no_event_id(self, service, sample_fund, db_session):
        """Test CREATE operation when event_id is None - should return None."""
        # Arrange
        sample_fund.start_date = date(2023, 3, 1)
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_id.return_value = None  # No event found
        
        # Act
        result = service.update_fund_start_date(
            fund_id=1, 
            session=db_session,
            event_id=None,  # None event_id with CREATE operation
            fund_event_operation=EventOperation.CREATE
        )
        
        # Assert
        assert result is None  # Should return None when event_id is None
        assert sample_fund.start_date == date(2023, 3, 1)  # Unchanged


class TestUpdateFundEndDate:
    """Test suite for update_fund_end_date method"""
    
    def test_update_end_date_realized_fund(self, service, sample_fund, db_session):
        """Test end date update for realized fund."""
        # Arrange
        sample_fund.status = FundStatus.REALIZED
        sample_fund.end_date = None
        
        latest_event = Mock(spec=FundEvent)
        latest_event.event_date = date(2023, 12, 31)
        
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = [latest_event]
        
        # Act
        result = service.update_fund_end_date(fund_id=1, session=db_session)
        
        # Assert
        assert result is not None
        assert result.field_name == 'end_date'
        assert result.old_value is None
        assert result.new_value == date(2023, 12, 31)
        assert sample_fund.end_date == date(2023, 12, 31)
    
    def test_update_end_date_completed_fund(self, service, sample_fund, db_session):
        """Test end date update for completed fund."""
        # Arrange
        sample_fund.status = FundStatus.COMPLETED
        sample_fund.end_date = date(2023, 6, 1)
        
        latest_event = Mock(spec=FundEvent)
        latest_event.event_date = date(2023, 12, 31)
        
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = [latest_event]
        
        # Act
        result = service.update_fund_end_date(fund_id=1, session=db_session)
        
        # Assert
        assert result is not None
        assert result.field_name == 'end_date'
        assert result.old_value == date(2023, 6, 1)
        assert result.new_value == date(2023, 12, 31)
        assert sample_fund.end_date == date(2023, 12, 31)
    
    def test_update_end_date_active_fund_no_change(self, service, sample_fund, db_session):
        """Test that end date doesn't change for active fund."""
        # Arrange
        sample_fund.status = FundStatus.ACTIVE
        service.fund_repository.get_by_id.return_value = sample_fund
        
        # Act
        result = service.update_fund_end_date(fund_id=1, session=db_session)
        
        # Assert
        assert result is None
        service.fund_event_repository.get_by_fund.assert_not_called()
    
    def test_update_end_date_no_events(self, service, sample_fund, db_session):
        """Test end date update when no relevant events exist."""
        # Arrange
        sample_fund.status = FundStatus.REALIZED
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = []
        
        # Act
        result = service.update_fund_end_date(fund_id=1, session=db_session)
        
        # Assert
        assert result is None
    
    def test_update_end_date_fund_not_found(self, service, db_session):
        """Test that None is returned when fund is not found."""
        # Arrange
        service.fund_repository.get_by_id.return_value = None
        
        # Act
        result = service.update_fund_end_date(fund_id=999, session=db_session)
        
        # Assert
        assert result is None
    
    def test_update_end_date_existing_end_date_earlier_than_event(self, service, sample_fund, db_session):
        """Test that end date doesn't change when existing end date is later than event date."""
        # Arrange
        sample_fund.status = FundStatus.REALIZED
        sample_fund.end_date = date(2024, 1, 1)  # Later than event date
        
        latest_event = Mock(spec=FundEvent)
        latest_event.event_date = date(2023, 12, 31)  # Earlier than existing end date
        
        service.fund_repository.get_by_id.return_value = sample_fund
        service.fund_event_repository.get_by_fund.return_value = [latest_event]
        
        # Act
        result = service.update_fund_end_date(fund_id=1, session=db_session)
        
        # Assert
        assert result is None
        assert sample_fund.end_date == date(2024, 1, 1)  # Unchanged


class TestUpdateFundDuration:
    """Test suite for update_fund_duration method"""
    
    @patch('src.fund.calculators.fund_duration_calculator.FundDurationCalculator')
    def test_update_duration_with_end_date(self, mock_calculator, service, sample_fund, db_session):
        """Test duration update when fund has end date."""
        # Arrange
        sample_fund.end_date = date(2023, 12, 31)
        sample_fund.current_duration = 10
        mock_calculator.calculate_duration_months.return_value = 12
        
        # Act
        result = service.update_fund_duration(sample_fund, db_session)
        
        # Assert
        assert result is not None
        assert result.field_name == 'current_duration'
        assert result.old_value == 10
        assert result.new_value == 12
        assert sample_fund.current_duration == 12
        mock_calculator.calculate_duration_months.assert_called_once_with(
            sample_fund.start_date, 
            sample_fund.end_date
        )
    
    @patch('src.fund.calculators.fund_duration_calculator.FundDurationCalculator')
    @patch('src.fund.services.fund_date_service.date')
    def test_update_duration_without_end_date_uses_today(self, mock_date, mock_calculator, service, sample_fund, db_session):
        """Test duration update when fund has no end date (uses today's date)."""
        # Arrange
        sample_fund.end_date = None
        sample_fund.current_duration = 10
        mock_date.today.return_value = date(2023, 12, 31)
        mock_calculator.calculate_duration_months.return_value = 12
        
        # Act
        result = service.update_fund_duration(sample_fund, db_session)
        
        # Assert
        assert result is not None
        assert result.field_name == 'current_duration'
        assert result.old_value == 10
        assert result.new_value == 12
        assert sample_fund.current_duration == 12
        mock_calculator.calculate_duration_months.assert_called_once_with(
            sample_fund.start_date, 
            date(2023, 12, 31)
        )
    
    def test_update_duration_no_start_date_raises_error(self, service, sample_fund, db_session):
        """Test that ValueError is raised when fund has no start date."""
        # Arrange
        sample_fund.start_date = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund.start_date not set"):
            service.update_fund_duration(sample_fund, db_session)
    
    @patch('src.fund.calculators.fund_duration_calculator.FundDurationCalculator')
    def test_update_duration_no_change_when_same_value(self, mock_calculator, service, sample_fund, db_session):
        """Test that no field change is returned when duration doesn't change."""
        # Arrange
        sample_fund.current_duration = 12
        mock_calculator.calculate_duration_months.return_value = 12
        
        # Act
        result = service.update_fund_duration(sample_fund, db_session)
        
        # Assert
        assert result is None
        assert sample_fund.current_duration == 12
    
    @patch('src.fund.calculators.fund_duration_calculator.FundDurationCalculator')
    def test_update_duration_with_none_current_duration(self, mock_calculator, service, sample_fund, db_session):
        """Test duration update when fund.current_duration is None."""
        # Arrange
        sample_fund.current_duration = None
        mock_calculator.calculate_duration_months.return_value = 12
        
        # Act
        result = service.update_fund_duration(sample_fund, db_session)
        
        # Assert
        assert result is not None
        assert result.field_name == 'current_duration'
        assert result.old_value is None
        assert result.new_value == 12
        assert sample_fund.current_duration == 12


class TestGetFundFinancialYears:
    """Test suite for get_fund_financial_years method"""
    
    @patch('src.entity.calculations.get_financial_years_for_fund_period')
    def test_get_financial_years_success(self, mock_get_years, service, sample_fund, db_session):
        """Test successful retrieval of financial years."""
        # Arrange
        mock_entity = Mock()
        mock_entity.id = 1
        mock_get_years.return_value = {'2023', '2022', '2021'}
        
        service.entity_repository.get_by_id.return_value = mock_entity
        
        # Act
        result = service.get_fund_financial_years(sample_fund, db_session)
        
        # Assert
        assert result == ['2023', '2022', '2021']  # Sorted in descending order
        service.entity_repository.get_by_id.assert_called_once_with(sample_fund.entity_id, db_session)
        mock_get_years.assert_called_once()
    
    def test_get_financial_years_no_start_date_raises_error(self, service, sample_fund, db_session):
        """Test that ValueError is raised when fund has no start date."""
        # Arrange
        sample_fund.start_date = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Fund.start_date is not set"):
            service.get_fund_financial_years(sample_fund, db_session)
    
    def test_get_financial_years_no_entity_raises_error(self, service, sample_fund, db_session):
        """Test that ValueError is raised when entity is not found."""
        # Arrange
        service.entity_repository.get_by_id.return_value = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="Entity is not set"):
            service.get_fund_financial_years(sample_fund, db_session)
    
    @patch('src.entity.calculations.get_financial_years_for_fund_period')
    def test_get_financial_years_empty_result_from_calculations(self, mock_get_years, service, sample_fund, db_session):
        """Test when entity calculations return empty set."""
        # Arrange
        mock_entity = Mock()
        mock_entity.id = 1
        mock_get_years.return_value = set()  # Empty set
        
        service.entity_repository.get_by_id.return_value = mock_entity
        
        # Act
        result = service.get_fund_financial_years(sample_fund, db_session)
        
        # Assert
        assert result == []  # Empty list
        service.entity_repository.get_by_id.assert_called_once_with(sample_fund.entity_id, db_session)
        mock_get_years.assert_called_once()
