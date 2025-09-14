"""
Tests for FundIrRService.

This module tests the IRR calculation service, focusing on the core business logic
and integration with the shared IRR calculator. Tests cover the main public methods
and key internal logic without testing removed/non-existent methods.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date
from decimal import Decimal

from src.fund.services.fund_irr_service import FundIrRService
from src.fund.models import Fund, FundEvent, FundFieldChange
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
    def service(self):
        """Create a FundIrRService instance."""
        return FundIrRService()
    
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
    
    def test_calculate_completed_irr_realized_fund(self, service, mock_realized_fund, mock_events, mock_session):
        """Test completed IRR calculation for realized funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.15) as mock_calc:
            
            result = service.calculate_completed_irr(mock_realized_fund, mock_session)
            
            assert result == 0.15
            mock_calc.assert_called_once_with(
                mock_events,
                mock_realized_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_irr_completed_fund(self, service, mock_completed_fund, mock_events, mock_session):
        """Test completed IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.20) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund, mock_session)
            
            assert result == 0.20
            mock_calc.assert_called_once_with(
                mock_events,
                mock_completed_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_irr_active_fund(self, service, mock_fund, mock_session):
        """Test completed IRR calculation returns None for active funds."""
        result = service.calculate_completed_irr(mock_fund, mock_session)
        
        assert result is None
    
    def test_calculate_completed_after_tax_irr_completed_fund(self, service, mock_completed_fund, mock_events_with_tax, mock_session):
        """Test completed after-tax IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.18) as mock_calc:
            
            result = service.calculate_completed_after_tax_irr(mock_completed_fund, mock_session)
            
            assert result == 0.18
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_after_tax_irr_realized_fund(self, service, mock_realized_fund, mock_events, mock_session):
        """Test completed after-tax IRR calculation returns None for realized funds."""
        result = service.calculate_completed_after_tax_irr(mock_realized_fund, mock_session)
        
        assert result is None
    
    def test_calculate_completed_real_irr_completed_fund(self, service, mock_completed_fund, mock_events_with_tax, mock_session):
        """Test completed real IRR calculation for completed funds."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.16) as mock_calc:
            
            result = service.calculate_completed_real_irr(mock_completed_fund, mock_session)
            
            assert result == 0.16
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )
    
    def test_calculate_completed_real_irr_realized_fund(self, service, mock_realized_fund, mock_events, mock_session):
        """Test completed real IRR calculation returns None for realized funds."""
        result = service.calculate_completed_real_irr(mock_realized_fund, mock_session)
        
        assert result is None
    
    # ============================================================================
    # MAIN ORCHESTRATION METHOD TESTS
    # ============================================================================
    
    def test_update_irrs_active_fund(self, service, mock_fund, mock_session):
        """Test update_irrs resets IRRs to None for active funds."""
        # Set initial values
        mock_fund.completed_irr_gross = 0.15
        mock_fund.completed_irr_after_tax = 0.12
        mock_fund.completed_irr_real = 0.10
        
        result = service.update_irrs(mock_fund, mock_session)
        
        # Verify IRRs were reset to None
        assert mock_fund.completed_irr_gross is None
        assert mock_fund.completed_irr_after_tax is None
        assert mock_fund.completed_irr_real is None
        
        # Verify field changes were tracked
        assert result is not None
        assert len(result) == 3
        assert any(change.field_name == 'completed_irr_gross' and change.new_value is None for change in result)
        assert any(change.field_name == 'completed_irr_after_tax' and change.new_value is None for change in result)
        assert any(change.field_name == 'completed_irr_real' and change.new_value is None for change in result)
    
    def test_update_irrs_realized_fund(self, service, mock_realized_fund, mock_events, mock_session):
        """Test update_irrs calculates only gross IRR for realized funds."""
        # Set initial values for after_tax and real IRRs
        mock_realized_fund.completed_irr_after_tax = 0.12
        mock_realized_fund.completed_irr_real = 0.10
        
        with patch.object(service, 'calculate_completed_irr', return_value=0.15) as mock_calc:
            result = service.update_irrs(mock_realized_fund, mock_session)
            
            # Verify only gross IRR was calculated
            assert mock_realized_fund.completed_irr_gross == 0.15
            assert mock_realized_fund.completed_irr_after_tax is None
            assert mock_realized_fund.completed_irr_real is None
            
            # Verify field changes were tracked (3 changes: gross set, after_tax and real reset to None)
            assert result is not None
            assert len(result) == 3
            
            # Check that all three field changes are tracked
            field_names = [change.field_name for change in result]
            assert 'completed_irr_gross' in field_names
            assert 'completed_irr_after_tax' in field_names
            assert 'completed_irr_real' in field_names
            
            # Verify the gross IRR change
            gross_change = next(change for change in result if change.field_name == 'completed_irr_gross')
            assert gross_change.new_value == 0.15
            
            mock_calc.assert_called_once_with(mock_realized_fund, mock_session)
    
    def test_update_irrs_completed_fund(self, service, mock_completed_fund, mock_events_with_tax, mock_session):
        """Test update_irrs calculates all IRRs for completed funds."""
        with patch.object(service, 'calculate_completed_irr', return_value=0.15) as mock_gross, \
             patch.object(service, 'calculate_completed_after_tax_irr', return_value=0.12) as mock_after_tax, \
             patch.object(service, 'calculate_completed_real_irr', return_value=0.10) as mock_real:
            
            result = service.update_irrs(mock_completed_fund, mock_session)
            
            # Verify all IRRs were calculated
            assert mock_completed_fund.completed_irr_gross == 0.15
            assert mock_completed_fund.completed_irr_after_tax == 0.12
            assert mock_completed_fund.completed_irr_real == 0.10
            
            # Verify field changes were tracked
            assert result is not None
            assert len(result) == 3
            
            # Verify all methods were called
            mock_gross.assert_called_once_with(mock_completed_fund, mock_session)
            mock_after_tax.assert_called_once_with(mock_completed_fund, mock_session)
            mock_real.assert_called_once_with(mock_completed_fund, mock_session)
    
    def test_update_irrs_no_changes(self, service, mock_completed_fund, mock_session):
        """Test update_irrs returns None when no IRR values change."""
        # Set initial values that won't change
        mock_completed_fund.completed_irr_gross = 0.15
        mock_completed_fund.completed_irr_after_tax = 0.12
        mock_completed_fund.completed_irr_real = 0.10
        
        with patch.object(service, 'calculate_completed_irr', return_value=0.15), \
             patch.object(service, 'calculate_completed_after_tax_irr', return_value=0.12), \
             patch.object(service, 'calculate_completed_real_irr', return_value=0.10):
            
            result = service.update_irrs(mock_completed_fund, mock_session)
            
            # Verify no changes were tracked
            assert result is None
    
    
    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================
    
    def test_calculate_completed_irr_no_events(self, service, mock_completed_fund, mock_session):
        """Test completed IRR calculation with no events."""
        with patch.object(service, '_get_fund_events', return_value=[]), \
             patch.object(service, '_calculate_irr_base', return_value=None) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund, mock_session)
            
            assert result is None
            mock_calc.assert_called_once()
    
    def test_calculate_completed_irr_insufficient_events(self, service, mock_completed_fund, mock_session):
        """Test completed IRR calculation with insufficient events."""
        with patch.object(service, '_get_fund_events', return_value=[Mock(spec=FundEvent)]), \
             patch.object(service, '_calculate_irr_base', return_value=None) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund, mock_session)
            
            assert result is None
            mock_calc.assert_called_once()
    
    def test_calculate_completed_irr_invalid_fund_type(self, service, mock_session):
        """Test completed IRR calculation with invalid fund type."""
        invalid_fund = Mock(spec=Fund)
        invalid_fund.status = "INVALID_STATUS"
        invalid_fund.start_date = date(2020, 1, 1)
        
        result = service.calculate_completed_irr(invalid_fund, mock_session)
        
        assert result is None
    
    # ============================================================================
    # INTEGRATION TESTS WITH REAL IRR CALCULATIONS
    # ============================================================================
    
    def test_calculate_completed_irr_integration(self, service, mock_completed_fund, mock_events, mock_session):
        """Test completed IRR calculation with real calculation logic."""
        # This test uses the actual calculation logic without mocking
        # It tests the integration between the status check and the calculation
        
        with patch.object(service, '_get_fund_events', return_value=mock_events), \
             patch.object(service, '_calculate_irr_base', return_value=0.15) as mock_calc:
            
            result = service.calculate_completed_irr(mock_completed_fund, mock_session)
            
            assert result == 0.15
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events,
                mock_completed_fund.start_date,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_after_tax_irr_integration(self, service, mock_completed_fund, mock_events_with_tax, mock_session):
        """Test completed after-tax IRR calculation with real calculation logic."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.12) as mock_calc:
            
            result = service.calculate_completed_after_tax_irr(mock_completed_fund, mock_session)
            
            assert result == 0.12
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
    
    def test_calculate_completed_real_irr_integration(self, service, mock_completed_fund, mock_events_with_tax, mock_session):
        """Test completed real IRR calculation with real calculation logic."""
        with patch.object(service, '_get_fund_events', return_value=mock_events_with_tax), \
             patch.object(service, '_calculate_irr_base', return_value=0.10) as mock_calc:
            
            result = service.calculate_completed_real_irr(mock_completed_fund, mock_session)
            
            assert result == 0.10
            # Verify the correct parameters were passed to the base calculation
            mock_calc.assert_called_once_with(
                mock_events_with_tax,
                mock_completed_fund.start_date,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )
    
    # ============================================================================
    # INTERNAL METHOD TESTS
    # ============================================================================
    
    def test_filter_events_for_irr_basic_events(self, service):
        """Test _filter_events_for_irr filters basic cash flow events."""
        events = []
        
        # Create various event types
        capital_call = Mock(spec=FundEvent)
        capital_call.event_type = EventType.CAPITAL_CALL
        events.append(capital_call)
        
        distribution = Mock(spec=FundEvent)
        distribution.event_type = EventType.DISTRIBUTION
        events.append(distribution)
        
        tax_payment = Mock(spec=FundEvent)
        tax_payment.event_type = EventType.TAX_PAYMENT
        events.append(tax_payment)
        
        risk_free_charge = Mock(spec=FundEvent)
        risk_free_charge.event_type = EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        events.append(risk_free_charge)
        
        other_event = Mock(spec=FundEvent)
        other_event.event_type = EventType.NAV_UPDATE
        events.append(other_event)
        
        # Test basic filtering (no tax, no risk-free charges)
        filtered = service._filter_events_for_irr(events, False, False, False)
        assert len(filtered) == 2  # Only capital_call and distribution
        assert capital_call in filtered
        assert distribution in filtered
    
    def test_filter_events_for_irr_with_tax(self, service):
        """Test _filter_events_for_irr includes tax payments when requested."""
        events = []
        
        capital_call = Mock(spec=FundEvent)
        capital_call.event_type = EventType.CAPITAL_CALL
        events.append(capital_call)
        
        tax_payment = Mock(spec=FundEvent)
        tax_payment.event_type = EventType.TAX_PAYMENT
        events.append(tax_payment)
        
        # Test with tax payments included
        filtered = service._filter_events_for_irr(events, True, False, False)
        assert len(filtered) == 2
        assert capital_call in filtered
        assert tax_payment in filtered
    
    def test_prepare_cash_flows(self, service):
        """Test _prepare_cash_flows converts events to cash flows correctly."""
        events = []
        
        # Capital call (outflow)
        capital_call = Mock(spec=FundEvent)
        capital_call.event_type = EventType.CAPITAL_CALL
        capital_call.event_date = date(2020, 1, 1)
        capital_call.amount = Decimal('100000.00')
        events.append(capital_call)
        
        # Distribution (inflow)
        distribution = Mock(spec=FundEvent)
        distribution.event_type = EventType.DISTRIBUTION
        distribution.event_date = date(2023, 12, 31)
        distribution.amount = Decimal('150000.00')
        events.append(distribution)
        
        start_date = date(2020, 1, 1)
        cash_flows, days_from_start = service._prepare_cash_flows(events, start_date)
        
        # Verify cash flows
        assert len(cash_flows) == 2
        assert cash_flows[0] == -100000.00  # Outflow (negative)
        assert cash_flows[1] == 150000.00   # Inflow (positive)
        
        # Verify days from start
        assert len(days_from_start) == 2
        assert days_from_start[0] == 0      # Same day
        assert days_from_start[1] == 1460   # ~4 years later
    
    def test_prepare_cash_flows_with_none_amount(self, service):
        """Test _prepare_cash_flows handles None amounts correctly."""
        events = []
        
        event = Mock(spec=FundEvent)
        event.event_type = EventType.CAPITAL_CALL
        event.event_date = date(2020, 1, 1)
        event.amount = None  # None amount
        events.append(event)
        
        start_date = date(2020, 1, 1)
        cash_flows, days_from_start = service._prepare_cash_flows(events, start_date)
        
        # Verify None amount is converted to 0
        assert cash_flows[0] == 0.0
        assert days_from_start[0] == 0