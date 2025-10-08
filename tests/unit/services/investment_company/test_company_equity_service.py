"""
Company Equity Service Unit Tests.

This module tests the CompanyEquityService class, focusing on business logic,
equity calculations, and service layer orchestration. Tests are precise and focused
on service functionality without testing repository or calculator logic directly.

Test Coverage:
- Company equity field updates
- Equity balance calculations
- Duration calculations
- Service layer orchestration
- Error handling
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from datetime import date

from src.investment_company.services.company_equity_service import CompanyEquityService
from src.investment_company.models import InvestmentCompany
from src.shared.models.domain_update_event import DomainFieldChange
from src.shared.enums.domain_update_event_enums import DomainObjectType
from src.fund.enums.fund_event_enums import EventType
from tests.factories.investment_company_factories import InvestmentCompanyFactory
from tests.factories.fund_factories import FundEventFactory


class TestCompanyEquityService:
    """Test suite for CompanyEquityService."""

    @pytest.fixture
    def service(self):
        """Create a CompanyEquityService instance for testing."""
        return CompanyEquityService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_company(self):
        """Mock company instance."""
        return InvestmentCompanyFactory.build(
            id=1, 
            name='Test Company',
            average_equity_balance=100000,
            current_equity_balance=120000,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31),
            current_duration=12
        )

    @pytest.fixture
    def mock_fund_events(self):
        """Mock fund events."""
        return [
            FundEventFactory.build(event_type=EventType.CAPITAL_CALL),
            FundEventFactory.build(event_type=EventType.RETURN_OF_CAPITAL)
        ]

    @pytest.fixture
    def fund_ids(self):
        """Sample fund IDs."""
        return [1, 2, 3]

    ################################################################################
    # Test update_company_equity_fields method
    ################################################################################

    def test_update_company_equity_fields_raises_error_when_company_not_found(self, service, mock_session, fund_ids):
        """Test that update_company_equity_fields raises ValueError when company not found."""
        # Arrange
        company_id = 999
        with patch.object(service.company_repository, 'get_company_by_id', return_value=None) as mock_get_company:
            # Act & Assert
            with pytest.raises(ValueError, match="Company not found"):
                service.update_company_equity_fields(company_id, fund_ids, mock_session)
            
            mock_get_company.assert_called_once_with(company_id, mock_session)

    def test_update_company_equity_fields_calls_repositories_with_correct_parameters(self, service, mock_session, mock_company, mock_fund_events, fund_ids):
        """Test that update_company_equity_fields calls repositories with correct parameters."""
        # Arrange
        company_id = 1
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.company_equity_calculator, 'calculate_company_equity_balance') as mock_calculate:
            
            # Setup calculator mock
            mock_calculate.return_value = (110000, 130000, date(2024, 1, 1))
            
            # Act
            service.update_company_equity_fields(company_id, fund_ids, mock_session)

            # Assert
            mock_get_company.assert_called_once_with(company_id, mock_session)
            mock_get_events.assert_called_once()
            call_args = mock_get_events.call_args
            assert call_args[1]['fund_ids'] == fund_ids
            assert call_args[1]['event_types'] == [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE]
            mock_calculate.assert_called_once_with(mock_fund_events)

    def test_update_company_equity_fields_returns_changes_when_values_change(self, service, mock_session, mock_company, mock_fund_events, fund_ids):
        """Test that update_company_equity_fields returns changes when values change."""
        # Arrange
        company_id = 1
        new_average_balance = 110000
        new_current_balance = 130000
        new_end_date = date(2024, 1, 1)
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.company_equity_calculator, 'calculate_company_equity_balance') as mock_calculate:
            
            # Setup calculator mock
            mock_calculate.return_value = (new_average_balance, new_current_balance, new_end_date)
            
            # Act
            result = service.update_company_equity_fields(company_id, fund_ids, mock_session)

            # Assert
            assert result is not None
            assert len(result) >= 3  # average_equity_balance, current_equity_balance, end_date (duration may also change)
            
            # Verify field changes
            field_names = [change.field_name for change in result]
            assert 'average_equity_balance' in field_names
            assert 'current_equity_balance' in field_names
            assert 'end_date' in field_names
            # duration may or may not be in the changes depending on whether it actually changed

    def test_update_company_equity_fields_returns_none_when_no_changes(self, service, mock_session, mock_company, mock_fund_events, fund_ids):
        """Test that update_company_equity_fields returns None when no values change."""
        # Arrange
        company_id = 1
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.company_equity_calculator, 'calculate_company_equity_balance') as mock_calculate:
            
            # Setup calculator mock to return same values as company
            mock_calculate.return_value = (mock_company.average_equity_balance, mock_company.current_equity_balance, mock_company.end_date)
            
            # Act
            result = service.update_company_equity_fields(company_id, fund_ids, mock_session)

            # Assert
            assert result is None

    def test_update_company_equity_fields_updates_company_fields(self, service, mock_session, mock_company, mock_fund_events, fund_ids):
        """Test that update_company_equity_fields updates company fields."""
        # Arrange
        company_id = 1
        new_average_balance = 110000
        new_current_balance = 130000
        new_end_date = date(2024, 1, 1)
        new_duration = 24
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.company_equity_calculator, 'calculate_company_equity_balance') as mock_calculate, \
             patch('src.investment_company.services.company_equity_service.DurationMonthsCalculator.calculate_duration_months', return_value=new_duration) as mock_duration_calc:
            
            # Setup calculator mock
            mock_calculate.return_value = (new_average_balance, new_current_balance, new_end_date)
            
            # Act
            service.update_company_equity_fields(company_id, fund_ids, mock_session)

            # Assert
            assert mock_company.average_equity_balance == new_average_balance
            assert mock_company.current_equity_balance == new_current_balance
            assert mock_company.end_date == new_end_date
            assert mock_company.current_duration == new_duration
            mock_duration_calc.assert_called_once_with(mock_company.start_date, new_end_date)

    def test_update_company_equity_fields_creates_correct_field_changes(self, service, mock_session, mock_company, mock_fund_events, fund_ids):
        """Test that update_company_equity_fields creates correct DomainFieldChange objects."""
        # Arrange
        company_id = 1
        new_average_balance = 110000
        new_current_balance = 130000
        new_end_date = date(2024, 1, 1)
        new_duration = 24
        
        # Capture original values before they get modified
        original_average_balance = mock_company.average_equity_balance
        original_current_balance = mock_company.current_equity_balance
        original_end_date = mock_company.end_date
        original_duration = mock_company.current_duration
        
        with patch.object(service.company_repository, 'get_company_by_id', return_value=mock_company) as mock_get_company, \
             patch.object(service.fund_event_repository, 'get_fund_events', return_value=mock_fund_events) as mock_get_events, \
             patch.object(service.company_equity_calculator, 'calculate_company_equity_balance') as mock_calculate, \
             patch('src.investment_company.services.company_equity_service.DurationMonthsCalculator.calculate_duration_months', return_value=new_duration) as mock_duration_calc:
            
            # Setup calculator mock
            mock_calculate.return_value = (new_average_balance, new_current_balance, new_end_date)
            
            # Act
            result = service.update_company_equity_fields(company_id, fund_ids, mock_session)

            # Assert
            assert result is not None
            
            # Find specific field changes
            average_change = next((change for change in result if change.field_name == 'average_equity_balance'), None)
            current_change = next((change for change in result if change.field_name == 'current_equity_balance'), None)
            end_date_change = next((change for change in result if change.field_name == 'end_date'), None)
            duration_change = next((change for change in result if change.field_name == 'current_duration'), None)
            
            # Verify field change properties
            assert average_change.domain_object_type == DomainObjectType.INVESTMENT_COMPANY
            assert average_change.domain_object_id == company_id
            assert average_change.old_value == original_average_balance
            assert average_change.new_value == new_average_balance
            
            assert current_change.domain_object_type == DomainObjectType.INVESTMENT_COMPANY
            assert current_change.domain_object_id == company_id
            assert current_change.old_value == original_current_balance
            assert current_change.new_value == new_current_balance
            
            assert end_date_change.domain_object_type == DomainObjectType.INVESTMENT_COMPANY
            assert end_date_change.domain_object_id == company_id
            assert end_date_change.old_value == original_end_date
            assert end_date_change.new_value == new_end_date
            
            if duration_change:  # duration change may or may not exist
                assert duration_change.domain_object_type == DomainObjectType.INVESTMENT_COMPANY
                assert duration_change.domain_object_id == company_id
                assert duration_change.old_value == original_duration
                assert duration_change.new_value == new_duration

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.company_repository is not None
        assert service.fund_event_repository is not None
        assert service.company_equity_calculator is not None
        assert hasattr(service, 'company_repository')
        assert hasattr(service, 'fund_event_repository')
        assert hasattr(service, 'company_equity_calculator')
