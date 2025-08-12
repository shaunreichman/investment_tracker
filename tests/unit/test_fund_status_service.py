"""
Unit tests for FundStatusService.

This module tests the FundStatusService which extracts status management logic
from the Fund model to provide clean separation of concerns and improved testability.

Test coverage: 100% required for Phase 2
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_status_service import FundStatusService
from src.fund.enums import FundStatus, FundType, EventType
from src.fund.models import Fund, FundEvent


class TestFundStatusService:
    """Test suite for FundStatusService."""
    
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
        
        # Use the proper FundStatus enum
        fund.status = FundStatus.ACTIVE
        
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        fund.irr_gross = None
        fund.irr_after_tax = None
        fund.irr_real = None
        fund.completed_irr = None
        fund.completed_after_tax_irr = None
        fund.completed_real_irr = None
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
        """Create mock fund events with positive final equity balance for testing REALIZED to ACTIVE transition."""
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
    
    def test_init(self, service):
        """Test service initialization."""
        assert service is not None
        assert isinstance(service, FundStatusService)
    
    def test_update_status_active_to_realized(self, service, mock_fund, mock_events):
        """Test status update from ACTIVE to REALIZED."""
        # Setup fund with no equity balance (last event has equity_balance = 0.0)
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.get_all_fund_events.return_value = mock_events
        
        # Mock the IRR calculation methods
        mock_fund.calculate_irr.return_value = 0.15
        mock_fund.calculate_after_tax_irr.return_value = 0.12
        mock_fund.calculate_real_irr.return_value = 0.10
        
        # Update status - service should determine it should be REALIZED due to 0 equity balance
        service.update_status(mock_fund)
        
        # Verify status changed to realized (because last event has equity_balance = 0.0)
        assert mock_fund.status == FundStatus.REALIZED
        
        # Verify IRRs were calculated and stored
        assert mock_fund.irr_gross == 0.15
        assert mock_fund.irr_after_tax == 0.12
        assert mock_fund.irr_real == 0.10
    
    def test_update_status_realized_to_active(self, service, mock_fund, mock_events_with_positive_balance):
        """Test status update from REALIZED to ACTIVE."""
        # Setup fund with equity balance (last event has equity_balance = 500.0)
        mock_fund.status = FundStatus.REALIZED
        mock_fund.get_all_fund_events.return_value = mock_events_with_positive_balance
        
        # Update status - service should determine it should be ACTIVE due to positive equity balance
        service.update_status(mock_fund)
        
        # Verify status changed to active (because last event has equity_balance = 500.0)
        assert mock_fund.status == FundStatus.ACTIVE
    
    def test_update_status_after_equity_event(self, service, mock_fund, mock_events):
        """Test status update after equity event."""
        # Setup fund with no equity balance (last event has equity_balance = 0.0)
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.get_all_fund_events.return_value = mock_events
        
        # Mock the IRR calculation methods
        mock_fund.calculate_irr.return_value = 0.15
        mock_fund.calculate_after_tax_irr.return_value = 0.12
        mock_fund.calculate_real_irr.return_value = 0.10
        
        # Update status after equity event - service should determine it should be REALIZED
        service.update_status_after_equity_event(mock_fund)
        
        # Verify status changed to realized (because last event has equity_balance = 0.0)
        assert mock_fund.status == FundStatus.REALIZED
        
        # Verify IRRs were calculated and stored
        assert mock_fund.irr_gross == 0.15
        assert mock_fund.irr_after_tax == 0.12
        assert mock_fund.irr_real == 0.10
    
    def test_update_status_after_tax_statement_completed(self, service, mock_fund, mock_tax_statements):
        """Test status update after tax statement to COMPLETED."""
        # Setup fund as realized
        mock_fund.status = FundStatus.REALIZED
        mock_fund.tax_statements = mock_tax_statements
        
        # Mock end date calculation
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            # Mock the completed IRR calculation methods
            mock_fund.calculate_completed_irr.return_value = 0.15
            mock_fund.calculate_completed_after_tax_irr.return_value = 0.12
            mock_fund.calculate_completed_real_irr.return_value = 0.10
            
            # Update status after tax statement - service should determine it should be COMPLETED
            service.update_status_after_tax_statement(mock_fund)
            
            # Verify status changed to completed (because final tax statement received)
            assert mock_fund.status == FundStatus.COMPLETED
            
            # Verify completed IRRs were calculated
            mock_fund.calculate_completed_irr.assert_called_once()
            mock_fund.calculate_completed_after_tax_irr.assert_called_once()
            mock_fund.calculate_completed_real_irr.assert_called_once()
    
    def test_update_status_after_tax_statement_realized(self, service, mock_fund, mock_tax_statements):
        """Test status update after tax statement to REALIZED."""
        # Setup fund as completed
        mock_fund.status = FundStatus.COMPLETED
        mock_fund.tax_statements = mock_tax_statements
        
        # Mock end date calculation
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            # Mock _is_final_tax_statement_received to return False (no final tax statement)
            with patch.object(service, '_is_final_tax_statement_received', return_value=False):
                # Update status after tax statement - service should determine it should be REALIZED
                service.update_status_after_tax_statement(mock_fund)
                
                # Verify status changed to realized (because no final tax statement received)
                assert mock_fund.status == FundStatus.REALIZED
    
    def test_should_be_active_with_equity(self, service, mock_fund, mock_events):
        """Test should_be_active when fund has equity balance."""
        # Ensure the last event has equity balance > 0
        mock_events[1].current_equity_balance = 1000.0  # Override the 0.0 from fixture
        mock_fund.get_all_fund_events.return_value = mock_events
        
        result = service._should_be_active(mock_fund)
        
        assert result is True
    
    def test_should_be_active_no_equity(self, service, mock_fund, mock_events):
        """Test should_be_active when fund has no equity balance."""
        # Modify events to have zero equity balance
        mock_events[1].current_equity_balance = 0.0
        mock_fund.get_all_fund_events.return_value = mock_events
        
        result = service._should_be_active(mock_fund)
        
        assert result is False
    
    def test_should_be_active_no_events(self, service, mock_fund):
        """Test should_be_active when fund has no events."""
        mock_fund.get_all_fund_events.return_value = []
        
        result = service._should_be_active(mock_fund)
        
        assert result is True
    
    def test_is_final_tax_statement_received_active_fund(self, service, mock_fund):
        """Test is_final_tax_statement_received for active fund."""
        mock_fund.status = FundStatus.ACTIVE
        
        result = service._is_final_tax_statement_received(mock_fund)
        
        assert result is False
    
    def test_is_final_tax_statement_received_with_final_statement(self, service, mock_fund, mock_tax_statements):
        """Test is_final_tax_statement_received when final statement exists."""
        mock_fund.status = FundStatus.REALIZED
        mock_fund.tax_statements = mock_tax_statements
        
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            result = service._is_final_tax_statement_received(mock_fund)
            
            assert result is True
    
    def test_is_final_tax_statement_received_no_final_statement(self, service, mock_fund, mock_tax_statements):
        """Test is_final_tax_statement_received when no final statement exists."""
        mock_fund.status = FundStatus.REALIZED
        # Only tax statements before end date
        mock_fund.tax_statements = [mock_tax_statements[0]]
        
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            result = service._is_final_tax_statement_received(mock_fund)
            
            assert result is False
    
    def test_calculate_end_date_with_equity_events(self, service, mock_fund, mock_events):
        """Test end date calculation with equity events."""
        mock_fund.get_all_fund_events.return_value = mock_events
        
        result = service.calculate_end_date(mock_fund)
        
        assert result == date(2020, 12, 31)  # Last equity event date
    
    def test_calculate_end_date_no_events(self, service, mock_fund):
        """Test end date calculation with no events."""
        mock_fund.get_all_fund_events.return_value = []
        
        result = service.calculate_end_date(mock_fund)
        
        assert result is None
    
    def test_calculate_end_date_no_start_date(self, service, mock_fund):
        """Test end date calculation with no start date."""
        mock_fund.start_date = None
        
        result = service.calculate_end_date(mock_fund)
        
        assert result is None
    
    def test_is_equity_or_distribution_event_capital_call(self, service):
        """Test is_equity_or_distribution_event for capital call."""
        event = Mock()
        event.event_type = EventType.CAPITAL_CALL
        
        result = service._is_equity_or_distribution_event(event)
        
        assert result is True
    
    def test_is_equity_or_distribution_event_distribution(self, service):
        """Test is_equity_or_distribution_event for distribution."""
        event = Mock()
        event.event_type = EventType.DISTRIBUTION
        
        result = service._is_equity_or_distribution_event(event)
        
        assert result is True
    
    def test_is_equity_or_distribution_event_nav_update(self, service):
        """Test is_equity_or_distribution_event for nav update."""
        event = Mock()
        event.event_type = EventType.NAV_UPDATE
        
        result = service._is_equity_or_distribution_event(event)
        
        assert result is False
    
    def test_validate_status_transition_allowed(self, service, mock_fund):
        """Test status transition validation for allowed transitions."""
        mock_fund.status = FundStatus.ACTIVE
        
        result = service.validate_status_transition(mock_fund, FundStatus.REALIZED)
        
        assert result is True
    
    def test_validate_status_transition_not_allowed(self, service, mock_fund):
        """Test status transition validation for not allowed transitions."""
        mock_fund.status = FundStatus.ACTIVE
        
        result = service.validate_status_transition(mock_fund, FundStatus.COMPLETED)
        
        assert result is False
    
    def test_validate_status_transition_invalid_status(self, service, mock_fund):
        """Test status transition validation for invalid status."""
        mock_fund.status = Mock()
        mock_fund.status.value = 'invalid_status'
        
        result = service.validate_status_transition(mock_fund, FundStatus.ACTIVE)
        
        assert result is False
    
    def test_get_status_summary(self, service, mock_fund, mock_events_with_positive_balance):
        """Test get_status_summary method."""
        mock_fund.get_all_fund_events.return_value = mock_events_with_positive_balance
        
        with patch.object(service, 'calculate_end_date', return_value=date(2020, 12, 31)):
            with patch.object(service, '_is_final_tax_statement_received', return_value=True):
                result = service.get_status_summary(mock_fund)
                
                assert result['current_status'] == FundStatus.ACTIVE.value
                assert result['start_date'] == date(2020, 1, 1)
                assert result['end_date'] == date(2020, 12, 31)
                assert result['should_be_active'] is True
                assert result['is_final_tax_statement_received'] is True
                assert 'status_transition_allowed' in result
    
    def test_calculate_and_store_irrs_for_status_realized(self, service, mock_fund):
        """Test IRR calculation and storage for realized status."""
        # Mock the IRR calculation methods
        mock_fund.calculate_irr.return_value = 0.15
        mock_fund.calculate_after_tax_irr.return_value = 0.12
        mock_fund.calculate_real_irr.return_value = 0.10
        
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.REALIZED)
        
        # Verify IRRs were calculated and stored
        assert mock_fund.irr_gross == 0.15
        assert mock_fund.irr_after_tax == 0.12
        assert mock_fund.irr_real == 0.10
    
    def test_calculate_and_store_irrs_for_status_completed(self, service, mock_fund):
        """Test IRR calculation and storage for completed status."""
        # Mock the completed IRR calculation methods
        mock_fund.calculate_completed_irr.return_value = 0.15
        mock_fund.calculate_completed_after_tax_irr.return_value = 0.12
        mock_fund.calculate_completed_real_irr.return_value = 0.10
        
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.COMPLETED)
        
        # Verify completed IRRs were calculated and stored
        assert mock_fund.completed_irr == 0.15
        assert mock_fund.completed_after_tax_irr == 0.12
        assert mock_fund.completed_real_irr == 0.10
    
    def test_calculate_and_store_irrs_for_status_active(self, service, mock_fund):
        """Test IRR calculation and storage for active status."""
        # Mock the IRR calculation methods
        mock_fund.calculate_irr.return_value = 0.15
        mock_fund.calculate_after_tax_irr.return_value = 0.12
        mock_fund.calculate_real_irr.return_value = 0.10
        
        service._calculate_and_store_irrs_for_status(mock_fund, FundStatus.ACTIVE)
        
        # Verify no IRRs were calculated for active status
        assert mock_fund.irr_gross is None
        assert mock_fund.irr_after_tax is None
        assert mock_fund.irr_real is None
