"""
Fund Status Service Tests

This module tests the FundStatusService status transition logic and business rules.
Focus: Status management, transitions, and business logic only.

Other aspects covered elsewhere:
- Model validation: test_fund_model.py
- Event processing: test_fund_event_service.py
- Calculations: test_fund_calculation_services.py
- Tax processing: test_tax_calculation_service.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_status_service import FundStatusService
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent


class TestFundStatusService:
    """Test suite for FundStatusService - Status transition logic only"""
    
    @pytest.fixture
    def service(self):
        """Create a FundStatusService instance for testing."""
        return FundStatusService()
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.tracking_type = FundType.NAV_BASED
        fund.status = FundStatus.ACTIVE
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        fund.current_equity_balance = 1000.0
        fund.irr_gross = None
        fund.irr_after_tax = None
        fund.irr_real = None
        return fund
    
    @pytest.fixture
    def mock_events(self):
        """Create mock fund events for testing."""
        events = []
        
        # Event 0: Capital call
        event0 = Mock(spec=FundEvent)
        event0.id = 1
        event0.event_type = EventType.CAPITAL_CALL
        event0.event_date = date(2020, 1, 1)
        event0.amount = 1000.0
        event0.current_equity_balance = 1000.0
        events.append(event0)
        
        # Event 1: Return of capital
        event1 = Mock(spec=FundEvent)
        event1.id = 2
        event1.event_type = EventType.RETURN_OF_CAPITAL
        event1.event_date = date(2020, 12, 31)
        event1.amount = 1000.0
        event1.current_equity_balance = 0.0
        events.append(event1)
        
        return events
    
    @pytest.fixture
    def mock_events_with_positive_balance(self):
        """Create mock fund events with positive final equity balance."""
        events = []
        
        # Event 0: Capital call
        event0 = Mock(spec=FundEvent)
        event0.id = 1
        event0.event_type = EventType.CAPITAL_CALL
        event0.event_date = date(2020, 1, 1)
        event0.amount = 1000.0
        event0.current_equity_balance = 1000.0
        events.append(event0)
        
        # Event 1: Return of capital (partial)
        event1 = Mock(spec=FundEvent)
        event1.id = 2
        event1.event_type = EventType.RETURN_OF_CAPITAL
        event1.event_date = date(2020, 12, 31)
        event1.amount = 500.0
        event1.current_equity_balance = 500.0  # Still has positive balance
        events.append(event1)
        
        return events
    
    @pytest.fixture
    def mock_tax_statements(self):
        """Create mock tax statements for testing."""
        tax_statements = []
        
        # Tax statement 1: Before fund end date
        ts1 = Mock()
        ts1.financial_year = 2020
        tax_statements.append(ts1)
        
        # Tax statement 2: After fund end date
        ts2 = Mock()
        ts2.financial_year = 2021
        tax_statements.append(ts2)
        
        return tax_statements
    
    def test_service_initialization(self, service):
        """Test FundStatusService initialization."""
        assert isinstance(service, FundStatusService)
    
    def test_update_status_active_to_realized(self, service, mock_fund):
        """Test status update from ACTIVE to REALIZED."""
        # Setup fund with no equity balance
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 0.0
        
        # Mock the _should_be_active method to return False
        with patch.object(service, '_should_be_active', return_value=False):
            service.update_status(mock_fund)
            
            # Verify status was updated
            assert mock_fund.status == FundStatus.REALIZED
    
    def test_update_status_realized_to_active(self, service, mock_fund):
        """Test status update from REALIZED to ACTIVE."""
        # Setup fund with equity balance
        mock_fund.status = FundStatus.REALIZED
        mock_fund.current_equity_balance = 500.0
        
        # Mock the _should_be_active method to return True
        with patch.object(service, '_should_be_active', return_value=True):
            service.update_status(mock_fund)
            
            # Verify status was updated
            assert mock_fund.status == FundStatus.ACTIVE
    
    def test_update_status_no_change_needed(self, service, mock_fund):
        """Test status update when no change is needed."""
        # Setup fund as active with equity balance
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 1000.0
        
        # Mock the _should_be_active method to return True
        with patch.object(service, '_should_be_active', return_value=True):
            service.update_status(mock_fund)
            
            # Verify status remained the same
            assert mock_fund.status == FundStatus.ACTIVE
    
    def test_update_status_after_equity_event(self, service, mock_fund):
        """Test status update after equity event."""
        # Setup fund with no equity balance
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 0.0
        
        # Mock the _should_be_active method to return False
        with patch.object(service, '_should_be_active', return_value=False):
            service.update_status_after_equity_event(mock_fund)
            
            # Verify status was updated
            assert mock_fund.status == FundStatus.REALIZED
    
    def test_update_status_after_tax_statement(self, service, mock_fund):
        """Test status update after tax statement."""
        # Setup fund as realized
        mock_fund.status = FundStatus.REALIZED
        
        # Mock the _is_final_tax_statement_received method to return True
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            service.update_status_after_tax_statement(mock_fund)
            
            # Verify status was updated to completed
            assert mock_fund.status == FundStatus.COMPLETED
    
    def test_update_status_after_tax_statement_no_change(self, service, mock_fund):
        """Test status update after tax statement when no change is needed."""
        # Setup fund as active
        mock_fund.status = FundStatus.ACTIVE
        
        # Mock the _is_final_tax_statement_received method to return False
        with patch.object(service, '_is_final_tax_statement_received', return_value=False):
            service.update_status_after_tax_statement(mock_fund)
            
            # Verify status remained the same
            assert mock_fund.status == FundStatus.ACTIVE
    
    def test_should_be_active_with_equity(self, service, mock_fund):
        """Test should_be_active when fund has equity balance."""
        # Setup fund with positive equity balance
        mock_fund.current_equity_balance = 1000.0
        
        # Test the method
        result = service._should_be_active(mock_fund)
        assert result is True
    
    def test_should_be_active_no_equity(self, service, mock_fund):
        """Test should_be_active when fund has no equity balance."""
        # Setup fund with zero equity balance
        mock_fund.current_equity_balance = 0.0
        
        # Test the method
        result = service._should_be_active(mock_fund)
        assert result is False
    
    def test_should_be_active_negative_equity(self, service, mock_fund):
        """Test should_be_active when fund has negative equity balance."""
        # Setup fund with negative equity balance
        mock_fund.current_equity_balance = -100.0
        
        # Test the method
        result = service._should_be_active(mock_fund)
        assert result is False
    
    def test_calculate_end_date_with_equity_events(self, service, mock_fund, mock_events):
        """Test end date calculation with equity events."""
        # Mock the fund events relationship
        mock_fund.fund_events = mock_events
        
        # Test the method
        result = service.calculate_end_date(mock_fund)
        
        # Should return the date of the last event
        assert result == date(2020, 12, 31)
    
    def test_calculate_end_date_no_events(self, service, mock_fund):
        """Test end date calculation with no events."""
        # Setup fund with no events
        mock_fund.fund_events = []
        
        # Test the method
        result = service.calculate_end_date(mock_fund)
        
        # Should return None when no events exist
        assert result is None
    
    def test_calculate_end_date_single_event(self, service, mock_fund):
        """Test end date calculation with single event."""
        # Setup fund with single event
        single_event = Mock(spec=FundEvent)
        single_event.event_date = date(2020, 6, 15)
        mock_fund.fund_events = [single_event]
        
        # Test the method
        result = service.calculate_end_date(mock_fund)
        
        # Should return the date of the single event
        assert result == date(2020, 6, 15)
    
    def test_is_final_tax_statement_received(self, service, mock_fund, mock_tax_statements):
        """Test final tax statement check."""
        # Mock the fund tax statements relationship
        mock_fund.tax_statements = mock_tax_statements
        
        # Mock the calculate_end_date method
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            # Test the method
            result = service._is_final_tax_statement_received(mock_fund)
            
            # Should return True if tax statement is after end date
            assert result is True
    
    def test_is_final_tax_statement_not_received(self, service, mock_fund, mock_tax_statements):
        """Test final tax statement check when not received."""
        # Mock the fund tax statements relationship
        mock_fund.tax_statements = mock_tax_statements
        
        # Mock the calculate_end_date method to return a later date
        with patch.object(service, 'calculate_end_date', return_value=date(2022, 12, 31)):
            # Test the method
            result = service._is_final_tax_statement_received(mock_fund)
            
            # Should return False if tax statement is before end date
            assert result is False
    
    def test_calculate_and_store_irrs_for_status_realized(self, service, mock_fund):
        """Test IRR calculation and storage for realized status."""
        # Mock the fund IRR calculation methods
        mock_fund.calculate_irr = Mock(return_value=0.15)
        mock_fund.calculate_after_tax_irr = Mock(return_value=0.12)
        mock_fund.calculate_real_irr = Mock(return_value=0.10)
        
        # Test the method
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.REALIZED)
        
        # Verify IRRs were calculated and stored
        assert mock_fund.irr_gross == 0.15
        assert mock_fund.irr_after_tax == 0.12
        assert mock_fund.irr_real == 0.10
    
    def test_calculate_and_store_irrs_for_status_completed(self, service, mock_fund):
        """Test IRR calculation and storage for completed status."""
        # Mock the fund completed IRR calculation methods
        mock_fund.calculate_completed_irr = Mock(return_value=0.18)
        mock_fund.calculate_completed_after_tax_irr = Mock(return_value=0.15)
        mock_fund.calculate_completed_real_irr = Mock(return_value=0.13)
        
        # Test the method
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.COMPLETED)
        
        # Verify completed IRRs were calculated and stored
        assert mock_fund.completed_irr == 0.18
        assert mock_fund.completed_after_tax_irr == 0.15
        assert mock_fund.completed_real_irr == 0.13
    
    def test_calculate_and_store_irrs_for_status_active(self, service, mock_fund):
        """Test IRR calculation and storage for active status."""
        # Mock the fund IRR calculation methods
        mock_fund.calculate_irr = Mock(return_value=0.20)
        mock_fund.calculate_after_tax_irr = Mock(return_value=0.17)
        mock_fund.calculate_real_irr = Mock(return_value=0.15)
        
        # Test the method
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.ACTIVE)
        
        # Verify IRRs were calculated and stored
        assert mock_fund.irr_gross == 0.20
        assert mock_fund.irr_after_tax == 0.17
        assert mock_fund.irr_real == 0.15
    
    def test_calculate_and_store_irrs_for_unknown_status(self, service, mock_fund):
        """Test IRR calculation and storage for unknown status."""
        # Test the method with an unknown status
        service._calculate_and_store_irrs_for_status(mock_fund, "UNKNOWN_STATUS")
        
        # Should not raise an error and should not calculate IRRs
        # (This tests the robustness of the method)
    
    def test_get_status_summary(self, service, mock_fund):
        """Test get_status_summary method."""
        # Setup fund with known values
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 1000.0
        mock_fund.start_date = date(2020, 1, 1)
        mock_fund.end_date = None
        
        # Test the method
        summary = service.get_status_summary(mock_fund)
        
        # Verify summary contains expected information
        assert summary['status'] == FundStatus.ACTIVE
        assert summary['equity_balance'] == 1000.0
        assert summary['start_date'] == date(2020, 1, 1)
        assert summary['end_date'] is None
    
    def test_get_status_summary_with_end_date(self, service, mock_fund):
        """Test get_status_summary method with end date."""
        # Setup fund with end date
        mock_fund.status = FundStatus.REALIZED
        mock_fund.current_equity_balance = 0.0
        mock_fund.start_date = date(2020, 1, 1)
        mock_fund.end_date = date(2020, 12, 31)
        
        # Test the method
        summary = service.get_status_summary(mock_fund)
        
        # Verify summary contains expected information
        assert summary['status'] == FundStatus.REALIZED
        assert summary['equity_balance'] == 0.0
        assert summary['start_date'] == date(2020, 1, 1)
        assert summary['end_date'] == date(2020, 12, 31)
    
    def test_status_transition_validation(self, service, mock_fund):
        """Test status transition validation logic."""
        # Test valid transition: ACTIVE -> REALIZED
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 0.0
        
        with patch.object(service, '_should_be_active', return_value=False):
            service.update_status(mock_fund)
            assert mock_fund.status == FundStatus.REALIZED
        
        # Test valid transition: REALIZED -> COMPLETED
        mock_fund.status = FundStatus.REALIZED
        
        with patch.object(service, '_is_final_tax_statement_received', return_value=True):
            service.update_status_after_tax_statement(mock_fund)
            assert mock_fund.status == FundStatus.COMPLETED
    
    def test_status_transition_edge_cases(self, service, mock_fund):
        """Test status transition edge cases."""
        # Test transition when equity balance is exactly zero
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 0.0
        
        with patch.object(service, '_should_be_active', return_value=False):
            service.update_status(mock_fund)
            assert mock_fund.status == FundStatus.REALIZED
        
        # Test transition when equity balance is very small positive number
        mock_fund.status = FundStatus.REALIZED
        mock_fund.current_equity_balance = 0.01
        
        with patch.object(service, '_should_be_active', return_value=True):
            service.update_status(mock_fund)
            assert mock_fund.status == FundStatus.ACTIVE
