"""
Fund Date Service Unit Tests.

This module tests the FundDateService class, focusing on business logic,
date calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or validation logic directly.

Test Coverage:
- Fund start date updates (CREATE operation and general updates)
- Fund end date updates based on fund status and events
- Fund duration calculations with various scenarios
- Financial year generation for different year types
- Error handling and edge cases
- Service layer orchestration
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date, datetime
from sqlalchemy.orm import Session

from src.fund.services.fund_date_service import FundDateService
from src.fund.models import Fund
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_enums import FundStatus, FundTaxStatementFinancialYearType
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation, SortOrder
from tests.factories.fund_factories import FundFactory, FundEventFactory


class TestFundDateService:
    """Test suite for FundDateService."""

    @pytest.fixture
    def service(self):
        """Create a FundDateService instance for testing."""
        service = FundDateService()
        # Mock the repositories
        service.fund_repository = Mock()
        service.fund_event_repository = Mock()
        return service

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def sample_fund(self):
        """Create a sample fund for testing."""
        return FundFactory.build(
            id=1,
            start_date=date(2020, 1, 1),
            end_date=None,
            current_duration=12,
            status=FundStatus.ACTIVE,
            tax_statement_financial_year_type=FundTaxStatementFinancialYearType.CALENDAR_YEAR
        )

    @pytest.fixture
    def sample_event(self):
        """Create a sample fund event for testing."""
        return FundEventFactory.build(
            id=1,
            fund_id=1,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2020, 2, 1)
        )

    ################################################################################
    # Update Fund Start Date Tests
    ################################################################################

    def test_update_fund_start_date_fund_not_found(self, service, mock_session):
        """Test update_fund_start_date returns None when fund is not found."""
        # Arrange
        fund = None  # Simulate fund not found

        # Act
        result = service.update_fund_start_date(fund, mock_session)

        # Assert
        assert result is None

    def test_update_fund_start_date_create_operation_with_valid_event(self, service, mock_session, sample_fund, sample_event):
        """Test update_fund_start_date with CREATE operation and valid event."""
        # Arrange
        sample_fund.start_date = date(2020, 3, 1)  # Later than event date
        service.fund_event_repository.get_fund_event_by_id.return_value = sample_event

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session, fund_event_id=1, fund_event_operation=EventOperation.CREATE)

        # Assert
        assert result is not None
        assert isinstance(result, DomainFieldChange)
        assert result.domain_object_type == DomainObjectType.FUND
        assert result.domain_object_id == 1
        assert result.field_name == 'start_date'
        assert result.old_value == date(2020, 3, 1)
        assert result.new_value == date(2020, 2, 1)
        assert sample_fund.start_date == date(2020, 2, 1)

    def test_update_fund_start_date_create_operation_with_invalid_event(self, service, mock_session, sample_fund):
        """Test update_fund_start_date with CREATE operation and invalid event."""
        # Arrange
        service.fund_event_repository.get_fund_event_by_id.return_value = None

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session, fund_event_id=1, fund_event_operation=EventOperation.CREATE)

        # Assert
        assert result is None

    def test_update_fund_start_date_create_operation_with_wrong_fund_id(self, service, mock_session, sample_fund, sample_event):
        """Test update_fund_start_date with CREATE operation and event for different fund."""
        # Arrange
        sample_event.fund_id = 999  # Different fund ID
        service.fund_event_repository.get_fund_event_by_id.return_value = sample_event

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session, fund_event_id=1, fund_event_operation=EventOperation.CREATE)

        # Assert
        assert result is None

    def test_update_fund_start_date_create_operation_with_non_capital_event(self, service, mock_session, sample_fund):
        """Test update_fund_start_date with CREATE operation and non-capital event."""
        # Arrange
        non_capital_event = FundEventFactory.build(
            id=1,
            fund_id=1,
            event_type=EventType.DISTRIBUTION,  # Not CAPITAL_CALL or UNIT_PURCHASE
            event_date=date(2020, 2, 1)
        )
        service.fund_event_repository.get_fund_event_by_id.return_value = non_capital_event

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session, fund_event_id=1, fund_event_operation=EventOperation.CREATE)

        # Assert
        assert result is None

    def test_update_fund_start_date_create_operation_with_later_date(self, service, mock_session, sample_fund, sample_event):
        """Test update_fund_start_date with CREATE operation and event date later than current start date."""
        # Arrange
        sample_fund.start_date = date(2020, 1, 1)  # Earlier than event date
        service.fund_event_repository.get_fund_event_by_id.return_value = sample_event

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session, fund_event_id=1, fund_event_operation=EventOperation.CREATE)

        # Assert
        assert result is None  # No change because event date is not earlier

    def test_update_fund_start_date_general_operation_with_events(self, service, mock_session, sample_fund):
        """Test update_fund_start_date with general operation and existing events."""
        # Arrange
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2019, 12, 1)
            ),
            FundEventFactory.build(
                id=2,
                fund_id=1,
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2020, 1, 15)
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session)

        # Assert
        assert result is not None
        assert result.old_value == date(2020, 1, 1)
        assert result.new_value == date(2019, 12, 1)
        assert sample_fund.start_date == date(2019, 12, 1)

    def test_update_fund_start_date_general_operation_no_events(self, service, mock_session, sample_fund):
        """Test update_fund_start_date with general operation and no events."""
        # Arrange
        service.fund_event_repository.get_fund_events.return_value = []

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session)

        # Assert
        assert result is None

    def test_update_fund_start_date_no_change(self, service, mock_session, sample_fund):
        """Test update_fund_start_date when no change is needed."""
        # Arrange
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2020, 1, 1)  # Same as current start date
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Update Fund End Date Tests
    ################################################################################

    def test_update_fund_end_date_fund_not_found(self, service, mock_session):
        """Test update_fund_end_date returns None when fund is not found."""
        # Arrange
        service.fund_repository.get_fund_by_id.return_value = None

        # Act
        result = service.update_fund_end_date(None, mock_session)

        # Assert
        assert result is None

    def test_update_fund_end_date_with_realized_status(self, service, mock_session):
        """Test update_fund_end_date with REALIZED status."""
        # Arrange
        fund = FundFactory.build(
            id=1,
            status=FundStatus.REALIZED,
            end_date=None
        )
        service.fund_repository.get_fund_by_id.return_value = fund
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2023, 12, 31)
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_end_date(fund, mock_session)

        # Assert
        assert result is not None
        assert result.field_name == 'end_date'
        assert result.old_value is None
        assert result.new_value == date(2023, 12, 31)
        assert fund.end_date == date(2023, 12, 31)

    def test_update_fund_end_date_with_completed_status(self, service, mock_session):
        """Test update_fund_end_date with COMPLETED status."""
        # Arrange
        fund = FundFactory.build(
            id=1,
            status=FundStatus.COMPLETED,
            end_date=None
        )
        service.fund_repository.get_fund_by_id.return_value = fund
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 6, 30)
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_end_date(fund, mock_session)

        # Assert
        assert result is not None
        assert result.field_name == 'end_date'
        assert result.new_value == date(2023, 6, 30)
        assert fund.end_date == date(2023, 6, 30)

    def test_update_fund_end_date_with_active_status(self, service, mock_session):
        """Test update_fund_end_date with ACTIVE status (no change)."""
        # Arrange
        fund = FundFactory.build(
            id=1,
            status=FundStatus.ACTIVE,
            end_date=None
        )
        service.fund_repository.get_fund_by_id.return_value = fund

        # Act
        result = service.update_fund_end_date(fund, mock_session)

        # Assert
        assert result is None
        assert fund.end_date is None

    def test_update_fund_end_date_with_existing_end_date(self, service, mock_session):
        """Test update_fund_end_date with existing end date that gets updated."""
        # Arrange
        fund = FundFactory.build(
            id=1,
            status=FundStatus.REALIZED,
            end_date=date(2023, 6, 30)
        )
        service.fund_repository.get_fund_by_id.return_value = fund
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2023, 12, 31)  # Later than existing end date
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_end_date(fund, mock_session)

        # Assert
        assert result is not None
        assert result.old_value == date(2023, 6, 30)
        assert result.new_value == date(2023, 12, 31)
        assert fund.end_date == date(2023, 12, 31)

    def test_update_fund_end_date_no_events(self, service, mock_session):
        """Test update_fund_end_date with no relevant events."""
        # Arrange
        fund = FundFactory.build(
            id=1,
            status=FundStatus.REALIZED,
            end_date=None
        )
        service.fund_repository.get_fund_by_id.return_value = fund
        service.fund_event_repository.get_fund_events.return_value = []

        # Act
        result = service.update_fund_end_date(fund, mock_session)

        # Assert
        assert result is None

    ################################################################################
    # Update Fund Duration Tests
    ################################################################################

    def test_update_fund_duration_with_start_and_end_date(self, service, mock_session, sample_fund):
        """Test update_fund_duration with both start and end dates."""
        # Arrange
        sample_fund.start_date = date(2020, 1, 1)
        sample_fund.end_date = date(2022, 1, 1)
        sample_fund.current_duration = 0

        with patch('src.shared.calculators.duration_months_calculator.DurationMonthsCalculator.calculate_duration_months') as mock_calc:
            mock_calc.return_value = 24

            # Act
            result = service.update_fund_duration(sample_fund, mock_session)

            # Assert
            assert result is not None
            assert result.field_name == 'current_duration'
            assert result.old_value == 0
            assert result.new_value == 24
            assert sample_fund.current_duration == 24
            mock_calc.assert_called_once_with(date(2020, 1, 1), date(2022, 1, 1))

    def test_update_fund_duration_with_start_date_only(self, service, mock_session, sample_fund):
        """Test update_fund_duration with start date only (uses today's date)."""
        # Arrange
        sample_fund.start_date = date(2020, 1, 1)
        sample_fund.end_date = None
        sample_fund.current_duration = 0

        with patch('src.shared.calculators.duration_months_calculator.DurationMonthsCalculator.calculate_duration_months') as mock_calc:
            mock_calc.return_value = 36

            # Act
            result = service.update_fund_duration(sample_fund, mock_session)

            # Assert
            assert result is not None
            assert result.field_name == 'current_duration'
            assert result.old_value == 0
            assert result.new_value == 36
            assert sample_fund.current_duration == 36
            mock_calc.assert_called_once_with(date(2020, 1, 1), date.today())

    def test_update_fund_duration_no_start_date_raises_error(self, service, mock_session, sample_fund):
        """Test update_fund_duration raises ValueError when start date is not set."""
        # Arrange
        sample_fund.start_date = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fund.start_date not set - can't set the current_duration"):
            service.update_fund_duration(sample_fund, mock_session)

    def test_update_fund_duration_no_change(self, service, mock_session, sample_fund):
        """Test update_fund_duration when duration doesn't change."""
        # Arrange
        sample_fund.start_date = date(2020, 1, 1)
        sample_fund.end_date = date(2022, 1, 1)
        sample_fund.current_duration = 24

        with patch('src.shared.calculators.duration_months_calculator.DurationMonthsCalculator.calculate_duration_months') as mock_calc:
            mock_calc.return_value = 24  # Same as current duration

            # Act
            result = service.update_fund_duration(sample_fund, mock_session)

            # Assert
            assert result is None

    ################################################################################
    # Get Fund Financial Years Tests
    ################################################################################

    def test_get_fund_financial_years_calendar_year(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years with calendar year type."""
        # Arrange
        sample_fund.start_date = date(2020, 6, 15)
        sample_fund.tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR

        with patch('src.fund.services.fund_date_service.date') as mock_date:
            mock_date.today.return_value = date(2022, 3, 10)

            # Act
            result = service.get_fund_financial_years(sample_fund)

            # Assert
            assert isinstance(result, set)
            assert '2020' in result
            assert '2021' in result
            assert '2022' in result
            assert len(result) == 3

    def test_get_fund_financial_years_half_year_start_before_june(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years with half year type, start before June."""
        # Arrange
        sample_fund.start_date = date(2020, 3, 15)
        sample_fund.tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR

        with patch('src.fund.services.fund_date_service.date') as mock_date:
            mock_date.today.return_value = date(2022, 3, 10)  # Before June, so end_year should be 2022

            # Act
            result = service.get_fund_financial_years(sample_fund)

            # Assert
            assert isinstance(result, set)
            assert '2020' in result
            assert '2021' in result
            assert '2022' in result
            assert len(result) == 3

    def test_get_fund_financial_years_half_year_start_after_june(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years with half year type, start after June."""
        # Arrange
        sample_fund.start_date = date(2020, 8, 15)
        sample_fund.tax_statement_financial_year_type = FundTaxStatementFinancialYearType.HALF_YEAR

        with patch('src.fund.services.fund_date_service.date') as mock_date:
            mock_date.today.return_value = date(2022, 3, 10)

            # Act
            result = service.get_fund_financial_years(sample_fund)

            # Assert
            assert isinstance(result, set)
            assert '2021' in result
            assert '2022' in result
            assert '2020' not in result  # Should not include 2020 since start is after June
            assert len(result) == 2

    def test_get_fund_financial_years_no_start_date_raises_error(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years raises ValueError when start date is not set."""
        # Arrange
        sample_fund.start_date = None

        # Act & Assert
        with pytest.raises(ValueError, match="Fund.start_date is not set"):
            service.get_fund_financial_years(sample_fund)

    def test_get_fund_financial_years_invalid_year_type_raises_error(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years raises ValueError with invalid year type."""
        # Arrange
        sample_fund.start_date = date(2020, 1, 1)
        sample_fund.tax_statement_financial_year_type = "INVALID_TYPE"

        # Act & Assert
        with pytest.raises(ValueError, match="Invalid financial year type: INVALID_TYPE"):
            service.get_fund_financial_years(sample_fund)

    def test_get_fund_financial_years_single_year(self, service, mock_session, sample_fund):
        """Test get_fund_financial_years with single year range."""
        # Arrange
        sample_fund.start_date = date(2022, 6, 15)
        sample_fund.tax_statement_financial_year_type = FundTaxStatementFinancialYearType.CALENDAR_YEAR

        with patch('src.fund.services.fund_date_service.date') as mock_date:
            mock_date.today.return_value = date(2022, 8, 10)

            # Act
            result = service.get_fund_financial_years(sample_fund)

            # Assert
            assert isinstance(result, set)
            assert '2022' in result
            assert len(result) == 1

    ################################################################################
    # Integration Tests
    ################################################################################

    def test_service_initialization(self, service):
        """Test FundDateService initializes with correct repositories."""
        # Assert
        assert service.fund_repository is not None
        assert service.fund_event_repository is not None

    def test_fund_field_change_creation(self, service, mock_session, sample_fund):
        """Test DomainFieldChange object creation and properties."""
        # Arrange
        events = [
            FundEventFactory.build(
                id=1,
                fund_id=1,
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2019, 12, 1)
            )
        ]
        service.fund_event_repository.get_fund_events.return_value = events

        # Act
        result = service.update_fund_start_date(sample_fund, mock_session)

        # Assert
        assert result is not None
        assert result.domain_object_type == DomainObjectType.FUND
        assert result.domain_object_id == 1
        assert result.field_name == 'start_date'
        assert result.old_value == date(2020, 1, 1)
        assert result.new_value == date(2019, 12, 1)
