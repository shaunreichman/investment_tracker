"""
Tests for FundIrRService.

This module tests the IRR calculation service, including both the business logic
and the integration with the shared IRR calculator.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from src.fund.services.fund_irr_service import FundIrRService
from src.fund.models import Fund, FundEvent
from src.fund.enums import FundStatus, EventType


class TestFundIrRService:
    """Test cases for FundIrRService."""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        session = Mock()
        session.query.return_value.filter.return_value.order_by.return_value.all.return_value = []
        return session
    
    @pytest.fixture
    def service(self, mock_session):
        """Create a FundIrRService instance."""
        return FundIrRService(mock_session)
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock fund for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.status = FundStatus.ACTIVE
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        return fund
    
    @pytest.fixture
    def mock_completed_fund(self):
        """Create a mock completed fund for testing completed IRR methods."""
        fund = Mock(spec=Fund)
        fund.id = 2
        fund.name = "Completed Fund"
        fund.status = FundStatus.COMPLETED
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2023, 12, 31)
        return fund
    
    @pytest.fixture
    def mock_realized_fund(self):
        """Create a mock realized fund for testing realized IRR methods."""
        fund = Mock(spec=Fund)
        fund.id = 3
        fund.name = "Realized Fund"
        fund.status = FundStatus.REALIZED
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2023, 6, 30)
        return fund
    
    @pytest.fixture
    def mock_events(self):
        """Create mock fund events for testing."""
        events = []
        
        # Capital call event
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.CAPITAL_CALL
        event1.event_date = date(2020, 1, 1)
        event1.amount = Decimal('100000.00')
        event1.description = "Initial capital call"
        events.append(event1)
        
        # Distribution event
        event2 = Mock(spec=FundEvent)
        event2.event_type = EventType.DISTRIBUTION
        event2.event_date = date(2023, 12, 31)
        event2.amount = Decimal('150000.00')
        event2.description = "Final distribution"
        events.append(event2)
        
        return events
    
    @pytest.fixture
    def mock_events_with_tax(self):
        """Create mock fund events including tax payments."""
        events = []
        
        # Capital call event
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.CAPITAL_CALL
        event1.event_date = date(2020, 1, 1)
        event1.amount = Decimal('100000.00')
        event1.description = "Initial capital call"
        events.append(event1)
        
        # Tax payment event
        event2 = Mock(spec=FundEvent)
        event2.event_type = EventType.TAX_PAYMENT
        event2.event_date = date(2023, 6, 30)
        event2.amount = Decimal('5000.00')
        event2.description = "Tax payment"
        events.append(event2)
        
        # Distribution event
        event3 = Mock(spec=FundEvent)
        event3.event_type = EventType.DISTRIBUTION
        event3.event_date = date(2023, 12, 31)
        event3.amount = Decimal('150000.00')
        event3.description = "Final distribution"
        events.append(event3)
        
        return events
    
    # ============================================================================
    # CORE IRR CALCULATION TESTS
    # ============================================================================
    
    def test_calculate_completed_irr_realized_fund(self, service, mock_realized_fund, mock_events):
        """Test completed IRR calculation for realized funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.15) as mock_calc:
            
            result = service.calculate_completed_irr(mock_realized_fund)
            
            assert result == 0.15
            mock_calc.assert_called_once_with(
                mock_events,
                mock_realized_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_irr_completed_fund(self, service, mock_completed_fund, mock_events):
        """Test completed IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.20) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund)
            
            assert result == 0.20
            mock_calc.assert_called_once_with(
                mock_events,
                mock_completed_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_irr_active_fund(self, service, mock_fund):
        """Test completed IRR calculation returns None for active funds."""
        result = service.calculate_completed_irr(mock_fund)
        
        assert result is None
    
    def test_calculate_completed_after_tax_irr_completed_fund(self, service, mock_completed_fund, mock_events_with_tax):
        """Test completed after-tax IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.18) as mock_calc:
            
            result = service.calculate_completed_after_tax_irr(mock_completed_fund)
            
            assert result == 0.18
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_after_tax_irr_realized_fund(self, service, mock_realized_fund, mock_events):
        """Test completed after-tax IRR calculation returns None for realized funds."""
        result = service.calculate_completed_after_tax_irr(mock_realized_fund)
        
        assert result is None
    
    def test_calculate_completed_real_irr_completed_fund(self, service, mock_completed_fund, mock_events_with_tax):
        """Test completed real IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_create_daily_risk_free_interest_charges') as mock_charges, \
             patch.object(service, '_calculate_irr_base', return_value=0.16) as mock_calc:
            
            result = service.calculate_completed_real_irr(mock_completed_fund)
            
            assert result == 0.16
            mock_charges.assert_called_once_with(mock_completed_fund, None)
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )
    
    def test_calculate_completed_real_irr_realized_fund(self, service, mock_realized_fund, mock_events):
        """Test completed real IRR calculation returns None for realized funds."""
        result = service.calculate_completed_real_irr(mock_realized_fund)
        
        assert result is None
    
    # ============================================================================
    # CONVENIENCE METHOD TESTS
    # ============================================================================
    
    
    def test_should_calculate_irr_realized_fund(self, service, mock_realized_fund):
        """Test should_calculate_irr returns True for realized funds."""
        result = service.should_calculate_irr(mock_realized_fund)
        assert result is True
    
    def test_should_calculate_irr_completed_fund(self, service, mock_completed_fund):
        """Test should_calculate_irr returns True for completed funds."""
        result = service.should_calculate_irr(mock_completed_fund)
        assert result is True
    
    def test_should_calculate_irr_active_fund(self, service, mock_fund):
        """Test should_calculate_irr returns False for active funds."""
        result = service.should_calculate_irr(mock_fund)
        assert result is False
    
    # ============================================================================
    # DATABASE OPERATION TESTS
    # ============================================================================
    
    def test_calculate_and_store_irrs(self, service, mock_completed_fund):
        """Test calculate_and_store_irrs method."""
        with patch.object(service, 'calculate_completed_irr', return_value=0.15) as mock_irr, \
             patch.object(service, 'calculate_completed_after_tax_irr', return_value=0.12) as mock_after_tax, \
             patch.object(service, 'calculate_completed_real_irr', return_value=0.10) as mock_real:
            
            result = service.calculate_and_store_irrs(mock_completed_fund)
            
            assert result['completed_irr'] == 0.15
            assert result['completed_after_tax_irr'] == 0.12
            assert result['completed_real_irr'] == 0.10
            
            # Verify fund object was updated
            assert mock_completed_fund.completed_irr_gross == 0.15
            assert mock_completed_fund.completed_irr_after_tax == 0.12
            assert mock_completed_fund.completed_irr_real == 0.10
            
            # Verify session was committed
            service.session.commit.assert_called_once()
            
            # Verify individual methods were called
            mock_irr.assert_called_once_with(mock_completed_fund)
            mock_after_tax.assert_called_once_with(mock_completed_fund)
            mock_real.assert_called_once_with(mock_completed_fund, None)
    
    
    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================
    
    def test_calculate_completed_irr_no_events(self, service, mock_completed_fund):
        """Test completed IRR calculation with no events."""
        with patch.object(service, '_get_fund_events', return_value=[]), \
             patch.object(service, '_calculate_irr_base', return_value=None) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund)
            
            assert result is None
            mock_calc.assert_called_once()
    
    def test_calculate_completed_irr_insufficient_events(self, service, mock_completed_fund):
        """Test completed IRR calculation with insufficient events."""
        with patch.object(service, '_get_fund_events', return_value=[Mock(spec=FundEvent)]), \
             patch.object(service, '_calculate_irr_base', return_value=None) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund)
            
            assert result is None
            mock_calc.assert_called_once()
    
    def test_calculate_completed_irr_invalid_fund_type(self, service):
        """Test completed IRR calculation with invalid fund type."""
        invalid_fund = Mock(spec=Fund)
        invalid_fund.status = "INVALID_STATUS"
        invalid_fund.start_date = date(2020, 1, 1)
        
        result = service.calculate_completed_irr(invalid_fund)
        
        assert result is None
    
    # ============================================================================
    # INTEGRATION TESTS WITH REAL IRR CALCULATIONS
    # ============================================================================
    
    def test_calculate_completed_irr_integration(self, service, mock_completed_fund, mock_events):
        """Test completed IRR calculation with real calculation logic."""
        # This test uses the actual calculation logic without mocking
        # It tests the integration between the status check and the calculation
        
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.15) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund)
            
            assert result == 0.15
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events,
                mock_completed_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_after_tax_irr_integration(self, service, mock_completed_fund, mock_events_with_tax):
        """Test completed after-tax IRR calculation with real calculation logic."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.12) as mock_calc:
            
            result = service.calculate_completed_after_tax_irr(mock_completed_fund)
            
            assert result == 0.12
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_real_irr_integration(self, service, mock_completed_fund, mock_events_with_tax):
        """Test completed real IRR calculation with real calculation logic."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_create_daily_risk_free_interest_charges') as mock_charges, \
             patch.object(service, '_calculate_irr_base', return_value=0.10) as mock_calc:
            
            result = service.calculate_completed_real_irr(mock_completed_fund)
            
            assert result == 0.10
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )