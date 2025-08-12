"""
Unit tests for FundCalculationService.

This module tests the FundCalculationService which extracts complex calculation logic
from the Fund model to provide clean separation of concerns and improved testability.

Test coverage: 100% required for Phase 2
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.models import Fund, FundEvent, EventType, FundType, FundStatus


class TestFundCalculationService:
    """Test suite for FundCalculationService."""
    
    @pytest.fixture
    def service(self):
        """Create a FundCalculationService instance for testing."""
        return FundCalculationService()
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.tracking_type = FundType.NAV_BASED
        fund.status = Mock()
        fund.status.value = 'active'
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        return fund
    
    @pytest.fixture
    def mock_cost_based_fund(self):
        """Create a mock cost-based Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 2
        fund.tracking_type = FundType.COST_BASED
        fund.status = Mock()
        fund.status.value = 'active'
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        return fund
    
    @pytest.fixture
    def mock_events(self):
        """Create mock fund events for testing."""
        events = []
        
        # Event 0: Unit purchase
        event0 = Mock(spec=FundEvent)
        event0.id = 1
        event0.event_type = EventType.UNIT_PURCHASE
        event0.event_date = date(2020, 1, 1)
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Unit sale
        event1 = Mock(spec=FundEvent)
        event1.id = 2
        event1.event_type = EventType.UNIT_SALE
        event1.event_date = date(2020, 2, 1)
        event1.units_sold = 50.0
        event1.unit_price = 12.0
        event1.brokerage_fee = 25.0
        event1.amount = None
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        # Event 2: Unit purchase
        event2 = Mock(spec=FundEvent)
        event2.id = 3
        event2.event_type = EventType.UNIT_PURCHASE
        event2.event_date = date(2020, 3, 1)
        event2.units_purchased = 75.0
        event2.unit_price = 11.0
        event2.brokerage_fee = 37.5
        event2.amount = None
        event2.units_owned = None
        event2.current_equity_balance = None
        events.append(event2)
        
        return events
    
    @pytest.fixture
    def mock_cost_based_events(self):
        """Create mock cost-based fund events for testing."""
        events = []
        
        # Event 0: Capital call
        event0 = Mock(spec=FundEvent)
        event0.id = 1
        event0.event_type = EventType.CAPITAL_CALL
        event0.event_date = date(2020, 1, 1)
        event0.amount = 1000.0
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Return of capital
        event1 = Mock(spec=FundEvent)
        event1.id = 2
        event1.event_type = EventType.RETURN_OF_CAPITAL
        event1.event_date = date(2020, 2, 1)
        event1.amount = 200.0
        event1.current_equity_balance = None
        events.append(event1)
        
        # Event 2: Capital call
        event2 = Mock(spec=FundEvent)
        event2.id = 3
        event2.event_type = EventType.CAPITAL_CALL
        event2.event_date = date(2020, 3, 1)
        event2.amount = 500.0
        event2.current_equity_balance = None
        events.append(event2)
        
        return events
    
    # ============================================================================
    # FIFO CALCULATIONS FOR NAV-BASED FUNDS
    # ============================================================================
    
    def test_calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
        self, service, mock_fund, mock_events
    ):
        """Test NAV field calculations for subsequent capital events."""
        # Test starting from index 1 (after first purchase)
        start_idx = 1
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, mock_events, start_idx
        )
        
        # Verify Event 1 (unit sale) calculations
        assert mock_events[1].amount == 575.0  # (50 * 12) - 25
        assert mock_events[1].units_owned == 50.0  # 100 - 50
        assert mock_events[1].current_equity_balance == 500.0  # 50 * 10 (remaining units)
        
        # Verify Event 2 (unit purchase) calculations
        assert mock_events[2].amount == 862.5  # (75 * 11) + 37.5
        assert mock_events[2].units_owned == 125.0  # 50 + 75
        assert mock_events[2].current_equity_balance == 1325.0  # (50 * 10) + (75 * 11)
    
    def test_calculate_nav_fields_with_zero_start_idx(self, service, mock_fund, mock_events):
        """Test NAV field calculations starting from the beginning."""
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, mock_events, start_idx
        )
        
        # Verify Event 0 (first purchase) calculations
        assert mock_events[0].amount == 1050.0  # (100 * 10) + 50
        assert mock_events[0].units_owned == 100.0
        assert mock_events[0].current_equity_balance == 1000.0  # 100 * 10
        
        # Verify Event 1 (sale) calculations
        assert mock_events[1].amount == 575.0  # (50 * 12) - 25
        assert mock_events[1].units_owned == 50.0  # 100 - 50
        assert mock_events[1].current_equity_balance == 500.0  # 50 * 10
        
        # Verify Event 2 (second purchase) calculations
        assert mock_events[2].amount == 862.5  # (75 * 11) + 37.5
        assert mock_events[2].units_owned == 125.0  # 50 + 75
        assert mock_events[2].current_equity_balance == 1325.0  # (50 * 10) + (75 * 11)
    
    def test_calculate_nav_fields_with_partial_fifo_consumption(self, service, mock_fund):
        """Test NAV field calculations with partial FIFO consumption."""
        events = []
        
        # Event 0: Purchase 100 units at $10
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Sell 30 units at $12
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.UNIT_SALE
        event1.units_sold = 30.0
        event1.unit_price = 12.0
        event1.brokerage_fee = 15.0
        event1.amount = None
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 1 calculations
        assert events[1].amount == 345.0  # (30 * 12) - 15
        assert events[1].units_owned == 70.0  # 100 - 30
        assert events[1].current_equity_balance == 700.0  # 70 * 10
    
    def test_calculate_nav_fields_with_zero_units_purchase(self, service, mock_fund):
        """Test NAV field calculations with zero units purchase."""
        events = []
        
        # Event 0: Purchase 0 units (edge case)
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 0.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 0.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 0 calculations
        assert events[0].amount == 0.0  # (0 * 10) + 0
        assert events[0].units_owned == 0.0
        assert events[0].current_equity_balance == 0.0
    
    def test_calculate_nav_fields_with_zero_units_sale(self, service, mock_fund):
        """Test NAV field calculations with zero units sale."""
        events = []
        
        # Event 0: Purchase 100 units
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Sell 0 units (edge case)
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.UNIT_SALE
        event1.units_sold = 0.0
        event1.unit_price = 12.0
        event1.brokerage_fee = 0.0
        event1.amount = None
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 1 calculations
        assert events[1].amount == 0.0  # (0 * 12) - 0
        assert events[1].units_owned == 100.0  # 100 - 0
        assert events[1].current_equity_balance == 1000.0  # 100 * 10
    
    def test_calculate_nav_fields_with_non_capital_event(self, service, mock_fund):
        """Test NAV field calculations with non-capital event."""
        events = []
        
        # Event 0: Purchase 100 units
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Distribution (non-capital event)
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.DISTRIBUTION
        event1.amount = 500.0
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 1 calculations for non-capital event
        assert events[1].units_owned == 100.0  # Should inherit from previous event
        assert events[1].current_equity_balance == 1000.0  # Should inherit from previous event
    
    def test_calculate_nav_fields_with_empty_fifo(self, service, mock_fund):
        """Test NAV field calculations when FIFO is empty (all units sold)."""
        events = []
        
        # Event 0: Purchase 100 units
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Sell all 100 units
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.UNIT_SALE
        event1.units_sold = 100.0
        event1.unit_price = 12.0
        event1.brokerage_fee = 25.0
        event1.amount = None
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        # Event 2: Another sale (should have 0 units and 0 equity)
        event2 = Mock(spec=FundEvent)
        event2.event_type = EventType.UNIT_SALE
        event2.units_sold = 50.0
        event2.unit_price = 15.0
        event2.brokerage_fee = 30.0
        event2.amount = None
        event2.units_owned = None
        event2.current_equity_balance = None
        events.append(event2)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 2 calculations when FIFO is empty
        assert events[2].amount == 720.0  # (50 * 15) - 30
        assert events[2].units_owned == -50.0  # 0 - 50 (negative units)
        assert events[2].current_equity_balance == 0.0  # Empty FIFO
    
    def test_calculate_nav_fields_with_exact_fifo_match(self, service, mock_fund):
        """Test NAV field calculations when sale exactly matches FIFO entry."""
        events = []
        
        # Event 0: Purchase 100 units
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.UNIT_PURCHASE
        event0.units_purchased = 100.0
        event0.unit_price = 10.0
        event0.brokerage_fee = 50.0
        event0.amount = None
        event0.units_owned = None
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Sell exactly 100 units (exact match)
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.UNIT_SALE
        event1.units_sold = 100.0
        event1.unit_price = 12.0
        event1.brokerage_fee = 25.0
        event1.amount = None
        event1.units_owned = None
        event1.current_equity_balance = None
        events.append(event1)
        
        start_idx = 0
        
        service.calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_fund, events, start_idx
        )
        
        # Verify Event 1 calculations
        assert events[1].amount == 1175.0  # (100 * 12) - 25
        assert events[1].units_owned == 0.0  # 100 - 100
        assert events[1].current_equity_balance == 0.0  # FIFO is empty
    
    def test_calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(
        self, service, mock_cost_based_fund, mock_cost_based_events
    ):
        """Test cost-based field calculations for subsequent capital events."""
        start_idx = 1
        
        service.calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_cost_based_fund, mock_cost_based_events, start_idx
        )
        
        # Verify Event 1 (return of capital) calculations
        assert mock_cost_based_events[1].current_equity_balance == 800.0  # 1000 - 200
        
        # Verify Event 2 (capital call) calculations
        assert mock_cost_based_events[2].current_equity_balance == 1300.0  # 800 + 500
    
    def test_calculate_cost_based_fields_with_zero_start_idx(self, service, mock_cost_based_fund, mock_cost_based_events):
        """Test cost-based field calculations starting from the beginning."""
        start_idx = 0
        
        service.calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_cost_based_fund, mock_cost_based_events, start_idx
        )
        
        # Verify Event 0 (first capital call) calculations
        assert mock_cost_based_events[0].current_equity_balance == 1000.0
        
        # Verify Event 1 (return of capital) calculations
        assert mock_cost_based_events[1].current_equity_balance == 800.0  # 1000 - 200
        
        # Verify Event 2 (second capital call) calculations
        assert mock_cost_based_events[2].current_equity_balance == 1300.0  # 800 + 500
    
    def test_calculate_cost_based_fields_with_non_capital_event(self, service, mock_cost_based_fund):
        """Test cost-based field calculations with non-capital event."""
        events = []
        
        # Event 0: Capital call
        event0 = Mock(spec=FundEvent)
        event0.event_type = EventType.CAPITAL_CALL
        event0.amount = 1000.0
        event0.current_equity_balance = None
        events.append(event0)
        
        # Event 1: Distribution (non-capital event)
        event1 = Mock(spec=FundEvent)
        event1.event_type = EventType.DISTRIBUTION
        event1.amount = 500.0
        event1.current_equity_balance = None
        events.append(event1)
        
        start_idx = 0
        
        service.calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event(
            mock_cost_based_fund, events, start_idx
        )
        
        # Verify Event 1 calculations for non-capital event
        assert events[1].current_equity_balance == 1000.0  # Should inherit from previous event
    
    # ============================================================================
    # IRR CALCULATIONS
    # ============================================================================
    
    @patch('src.fund.services.fund_calculation_service.orchestrate_irr_base')
    def test_calculate_irr(self, mock_orchestrate, service, mock_fund):
        """Test pre-tax IRR calculation."""
        mock_orchestrate.return_value = 0.15
        
        result = service.calculate_irr(mock_fund)
        
        assert result == 0.15
        mock_orchestrate.assert_called_once_with(
            mock_fund,
            include_tax_payments=False,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False,
            session=None
        )
    
    @patch('src.fund.services.fund_calculation_service.orchestrate_irr_base')
    def test_calculate_after_tax_irr(self, mock_orchestrate, service, mock_fund):
        """Test after-tax IRR calculation."""
        mock_orchestrate.return_value = 0.12
        
        result = service.calculate_after_tax_irr(mock_fund)
        
        assert result == 0.12
        mock_orchestrate.assert_called_once_with(
            mock_fund,
            include_tax_payments=True,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False,
            session=None
        )
    
    @patch('src.fund.services.fund_calculation_service.orchestrate_irr_base')
    def test_calculate_real_irr(self, mock_orchestrate, service, mock_fund):
        """Test real IRR calculation."""
        mock_orchestrate.return_value = 0.10
        
        result = service.calculate_real_irr(mock_fund, risk_free_rate_currency='USD')
        
        assert result == 0.10
        mock_orchestrate.assert_called_once_with(
            mock_fund,
            include_tax_payments=True,
            include_risk_free_charges=True,
            include_eofy_debt_cost=True,
            session=None
        )
    
    def test_calculate_completed_irr_active_fund(self, service, mock_fund):
        """Test completed IRR calculation for active fund (should return None)."""
        mock_fund.status.value = 'active'
        
        result = service.calculate_completed_irr(mock_fund)
        
        assert result is None
    
    def test_calculate_completed_irr_realized_fund(self, service, mock_fund):
        """Test completed IRR calculation for realized fund."""
        mock_fund.status.value = 'realized'
        
        with patch.object(service, 'calculate_irr', return_value=0.15):
            result = service.calculate_completed_irr(mock_fund)
        
        assert result == 0.15
    
    def test_calculate_completed_after_tax_irr_completed_fund(self, service, mock_fund):
        """Test completed after-tax IRR calculation for completed fund."""
        mock_fund.status.value = 'completed'
        
        with patch.object(service, 'calculate_after_tax_irr', return_value=0.12):
            result = service.calculate_completed_after_tax_irr(mock_fund)
        
        assert result == 0.12
    
    def test_calculate_completed_real_irr_completed_fund(self, service, mock_fund):
        """Test completed real IRR calculation for completed fund."""
        mock_fund.status.value = 'completed'
        
        with patch.object(service, 'calculate_real_irr', return_value=0.10):
            result = service.calculate_completed_real_irr(mock_fund)
        
        assert result == 0.10
    
    # ============================================================================
    # EQUITY BALANCE CALCULATIONS
    # ============================================================================
    
    def test_calculate_average_equity_balance_no_events(self, service, mock_fund):
        """Test average equity balance calculation with no events."""
        # Pass empty events list to avoid circular import issues
        result = service.calculate_average_equity_balance(mock_fund, events=[])
        
        assert result == 0.0
    
    def test_calculate_average_equity_balance_single_event(self, service, mock_fund):
        """Test average equity balance calculation with single event."""
        mock_event = Mock()
        mock_event.current_equity_balance = 1000.0
        events = [mock_event]
        
        result = service.calculate_average_equity_balance(mock_fund, events=events)
        
        assert result == 1000.0
    
    def test_calculate_average_equity_balance_multiple_events(self, service, mock_fund):
        """Test average equity balance calculation with multiple events."""
        # Create events with known equity balances and dates
        events = []
        
        event1 = Mock()
        event1.event_date = date(2020, 1, 1)
        event1.current_equity_balance = 1000.0
        events.append(event1)
        
        event2 = Mock()
        event2.event_date = date(2020, 2, 1)  # 31 days later
        event2.current_equity_balance = 1200.0
        events.append(event2)
        
        event3 = Mock()
        event3.event_date = date(2020, 3, 1)  # 29 days later
        event3.current_equity_balance = 1100.0
        events.append(event3)
        
        # Mock today's date for active fund
        with patch('src.fund.services.fund_calculation_service.date') as mock_date:
            mock_date.today.return_value = date(2020, 3, 15)  # 14 days after last event
            
            result = service.calculate_average_equity_balance(mock_fund, events=events)
        
        # Expected calculation:
        # Period 1: 1000 * 31 = 31000
        # Period 2: 1200 * 29 = 34800
        # Period 3: 1100 * 14 = 15400
        # Total weighted: 31000 + 34800 + 15400 = 81200
        # Total days: 31 + 29 + 14 = 74
        # Average: 81200 / 74 ≈ 1097.30
        expected_result = 81200 / 74
        assert abs(result - expected_result) < 0.01
    
    def test_calculate_average_equity_balance_with_end_date(self, service, mock_fund):
        """Test average equity balance calculation with fund end date."""
        mock_fund.end_date = date(2020, 3, 10)
        
        events = []
        event1 = Mock()
        event1.event_date = date(2020, 1, 1)
        event1.current_equity_balance = 1000.0
        events.append(event1)
        
        event2 = Mock()
        event2.event_date = date(2020, 2, 1)
        event2.current_equity_balance = 1200.0
        events.append(event2)
        
        result = service.calculate_average_equity_balance(mock_fund, events=events)
        
        # Expected calculation:
        # Period 1: 1000 * 31 = 31000
        # Period 2: 1200 * 38 = 45600 (from Feb 1 to Mar 10)
        # Total weighted: 31000 + 45600 = 76600
        # Total days: 31 + 38 = 69
        # Average: 76600 / 69 ≈ 1110.14
        expected_result = 76600 / 69
        assert abs(result - expected_result) < 0.01
    
    def test_calculate_average_equity_balance_cost_based_fund(self, service, mock_cost_based_fund):
        """Test average equity balance calculation for cost-based fund."""
        # Pass empty events list to avoid circular import issues
        result = service.calculate_average_equity_balance(mock_cost_based_fund, events=[])
        
        # Should return 0.0 for empty events list
        assert result == 0.0
    
    def test_calculate_average_equity_balance_with_zero_days(self, service, mock_fund):
        """Test average equity balance calculation with zero days (edge case)."""
        events = []
        event1 = Mock()
        event1.event_date = date(2020, 1, 1)
        event1.current_equity_balance = 1000.0
        events.append(event1)
        
        # Mock today's date to be the same as the event date
        with patch('src.fund.services.fund_calculation_service.date') as mock_date:
            mock_date.today.return_value = date(2020, 1, 1)  # Same day
            
            result = service.calculate_average_equity_balance(mock_fund, events=events)
        
        # For single events, the method returns the equity balance directly
        # regardless of the time period (special case in the logic)
        assert result == 1000.0
    
    def test_calculate_average_equity_balance_with_none_equity_balance(self, service, mock_fund):
        """Test average equity balance calculation with None equity balance values."""
        events = []
        
        event1 = Mock()
        event1.event_date = date(2020, 1, 1)
        event1.current_equity_balance = None  # None value
        events.append(event1)
        
        event2 = Mock()
        event2.event_date = date(2020, 2, 1)  # 31 days later
        event2.current_equity_balance = 1200.0
        events.append(event2)
        
        # Mock today's date
        with patch('src.fund.services.fund_calculation_service.date') as mock_date:
            mock_date.today.return_value = date(2020, 2, 15)  # 14 days after last event
            
            result = service.calculate_average_equity_balance(mock_fund, events=events)
        
        # Expected calculation:
        # Period 1: 0 * 31 = 0 (None becomes 0.0)
        # Period 2: 1200 * 14 = 16800
        # Total weighted: 0 + 16800 = 16800
        # Total days: 31 + 14 = 45
        # Average: 16800 / 45 ≈ 373.33
        expected_result = 16800 / 45
        assert abs(result - expected_result) < 0.01
    
    def test_calculate_actual_duration_months_no_start_date(self, service, mock_fund):
        """Test duration calculation with no start date."""
        mock_fund.start_date = None
        
        result = service.calculate_actual_duration_months(mock_fund)
        
        assert result is None
    
    def test_calculate_actual_duration_months_with_end_date(self, service, mock_fund):
        """Test duration calculation with end date."""
        mock_fund.end_date = date(2020, 12, 31)
        
        result = service.calculate_actual_duration_months(mock_fund)
        
        # Expected: 365 days / 30.44 ≈ 11.99 months
        expected_result = 365 / 30.44
        assert abs(result - expected_result) < 0.01
    
    def test_calculate_actual_duration_months_active_fund(self, service, mock_fund):
        """Test duration calculation for active fund (uses today's date)."""
        with patch('src.fund.services.fund_calculation_service.date') as mock_date:
            mock_date.today.return_value = date(2020, 6, 30)  # 181 days after start
            
            result = service.calculate_actual_duration_months(mock_fund)
        
        # Expected: 181 days / 30.44 ≈ 5.95 months
        expected_result = 181 / 30.44
        assert abs(result - expected_result) < 0.01
    
    def test_calculate_actual_duration_months_realized_fund(self, service, mock_fund):
        """Test duration calculation for realized fund (no end date, not active)."""
        mock_fund.status.value = 'realized'
        mock_fund.end_date = None
        
        # For realized funds with no end date, the method should return None
        # since it can't determine the end date (not active, no end_date)
        result = service.calculate_actual_duration_months(mock_fund)
        
        assert result is None
    
    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    @patch('src.fund.services.fund_calculation_service.orchestrate_irr_base')
    def test_calculate_irr_base(self, mock_orchestrate, service, mock_fund):
        """Test the base IRR calculation method."""
        mock_orchestrate.return_value = 0.18
        mock_session = Mock()
        
        result = service._calculate_irr_base(
            mock_fund,
            include_tax_payments=True,
            include_risk_free_charges=True,
            include_eofy_debt_cost=True,
            session=mock_session
        )
        
        assert result == 0.18
        mock_orchestrate.assert_called_once_with(
            mock_fund,
            include_tax_payments=True,
            include_risk_free_charges=True,
            include_eofy_debt_cost=True,
            session=mock_session
        )
    
    def test_create_daily_risk_free_interest_charges_placeholder(self, service, mock_fund):
        """Test the placeholder method for daily risk-free interest charges."""
        # This method is a placeholder that will be implemented in TaxCalculationService
        # It should not raise any exceptions
        service._create_daily_risk_free_interest_charges(mock_fund, risk_free_rate_currency='USD')
        
        # No assertions needed - just ensuring no exceptions are raised
