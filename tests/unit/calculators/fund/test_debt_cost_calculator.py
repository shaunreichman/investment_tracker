"""
Tests for DailyDebtCostCalculator.

Tests the pure mathematical calculations for debt cost and opportunity cost calculations.
"""

import pytest
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

from src.fund.calculators.debt_cost_calculator import DailyDebtCostCalculator
from src.fund.models.fund_event import FundEvent
from src.rates.models.risk_free_rate import RiskFreeRate
from src.fund.enums.fund_event_enums import EventType
from src.rates.enums.risk_free_rate_enums import RiskFreeRateType
from src.shared.enums.shared_enums import Currency


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    event_date: date
    event_type: EventType
    current_equity_balance: float = 0.0
    amount: float = None
    description: str = None


@dataclass
class MockRiskFreeRate:
    """Mock risk free rate for testing."""
    date: date
    rate: float
    currency: Currency = Currency.AUD
    rate_type: RiskFreeRateType = RiskFreeRateType.GOVERNMENT_BOND


class TestDailyDebtCostCalculator:
    """Test cases for DailyDebtCostCalculator."""
    
    def test_calculate_debt_cost_basic_single_period(self):
        """Test basic debt cost calculation with single equity and rate period."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0  # 5% annual rate
            )
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0  # Should have daily calculations
        
        # Check that we have calculations for the period
        # The calculation should run from 2023-01-01 to today
        start_date = date(2023, 1, 1)
        today = date.today()
        expected_days = (today - start_date).days + 1
        
        # Verify we have approximately the right number of days
        assert len(result) >= expected_days - 10  # Allow some tolerance
        
        # Check a specific day's calculation
        test_date = date(2023, 1, 15)
        if test_date in result:
            daily_data = result[test_date]
            assert 'debt_cost' in daily_data
            assert 'equity' in daily_data
            assert 'rate' in daily_data
            
            # Verify the calculation: equity * (rate / 365.25)
            expected_daily_cost = 100000.0 * (5.0 / 365.25)
            assert daily_data['debt_cost'] == pytest.approx(expected_daily_cost, rel=1e-6)
            assert daily_data['equity'] == 100000.0
            assert daily_data['rate'] == 5.0
    
    def test_calculate_debt_cost_multiple_equity_periods(self):
        """Test debt cost calculation with multiple equity periods."""
        # Setup - Two capital calls creating different equity periods
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=200000.0,  # Total equity after second call
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0
            )
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check first period (100k equity)
        jan_15 = date(2023, 1, 15)
        if jan_15 in result:
            jan_data = result[jan_15]
            expected_cost = 100000.0 * (5.0 / 365.25)
            assert jan_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert jan_data['equity'] == 100000.0
        
        # Check second period (200k equity)
        feb_15 = date(2023, 2, 15)
        if feb_15 in result:
            feb_data = result[feb_15]
            expected_cost = 200000.0 * (5.0 / 365.25)
            assert feb_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert feb_data['equity'] == 200000.0
    
    def test_calculate_debt_cost_multiple_rate_periods(self):
        """Test debt cost calculation with multiple rate periods."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0
            ),
            MockRiskFreeRate(
                date=date(2023, 2, 1),
                rate=6.0  # Rate increases
            )
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check first rate period (5%)
        jan_15 = date(2023, 1, 15)
        if jan_15 in result:
            jan_data = result[jan_15]
            expected_cost = 100000.0 * (5.0 / 365.25)
            assert jan_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert jan_data['rate'] == 5.0
        
        # Check second rate period (6%)
        feb_15 = date(2023, 2, 15)
        if feb_15 in result:
            feb_data = result[feb_15]
            expected_cost = 100000.0 * (6.0 / 365.25)
            assert feb_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert feb_data['rate'] == 6.0
    
    def test_calculate_debt_cost_with_date_filtering(self):
        """Test debt cost calculation with start and end date filtering."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=200000.0,
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0
            )
        ]
        
        # Execute with date filtering
        start_date = date(2023, 2, 1)
        end_date = date(2023, 2, 28)
        result = DailyDebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date
        )
        
        # Verify
        assert isinstance(result, dict)
        
        # Should only have calculations for February 2023
        for calc_date in result.keys():
            assert start_date <= calc_date <= end_date
        
        # Should use 100k equity (from first event) for February calculations
        feb_15 = date(2023, 2, 15)
        if feb_15 in result:
            feb_data = result[feb_15]
            expected_cost = 100000.0 * (5.0 / 365.25)
            assert feb_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert feb_data['equity'] == 100000.0
    
    def test_calculate_debt_cost_empty_events(self):
        """Test debt cost calculation with empty events list."""
        # Setup
        events = []
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0
            )
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0  # No equity periods = no calculations
    
    def test_calculate_debt_cost_empty_rates(self):
        """Test debt cost calculation with empty rates list."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            )
        ]
        risk_free_rates = []
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) == 0  # No rate periods = no calculations
    
    def test_calculate_debt_cost_zero_equity_balance(self):
        """Test debt cost calculation with zero equity balance events."""
        # Setup - Event with zero equity balance should be skipped
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=0.0,  # Zero equity
                amount=0.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,  # Non-zero equity
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(
                date=date(2023, 1, 1),
                rate=5.0
            )
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0  # Should have calculations for second event
        
        # All calculations should use 100k equity (from second event)
        for calc_date, daily_data in result.items():
            assert daily_data['equity'] == 100000.0
    
    def test_build_rate_periods_basic(self):
        """Test _build_rate_periods method with basic scenario."""
        # Setup
        risk_free_rates = [
            MockRiskFreeRate(date=date(2023, 1, 1), rate=5.0),
            MockRiskFreeRate(date=date(2023, 2, 1), rate=6.0),
            MockRiskFreeRate(date=date(2023, 3, 1), rate=4.0)
        ]
        
        # Execute
        rate_periods = DailyDebtCostCalculator._build_rate_periods(risk_free_rates)
        
        # Verify
        assert len(rate_periods) == 3
        
        # First period: 2023-01-01 to 2023-02-01
        assert rate_periods[0]['start_date'] == date(2023, 1, 1)
        assert rate_periods[0]['end_date'] == date(2023, 2, 1)
        assert rate_periods[0]['rate'] == 5.0
        
        # Second period: 2023-02-01 to 2023-03-01
        assert rate_periods[1]['start_date'] == date(2023, 2, 1)
        assert rate_periods[1]['end_date'] == date(2023, 3, 1)
        assert rate_periods[1]['rate'] == 6.0
        
        # Third period: 2023-03-01 to today
        assert rate_periods[2]['start_date'] == date(2023, 3, 1)
        assert rate_periods[2]['end_date'] == date.today()
        assert rate_periods[2]['rate'] == 4.0
    
    def test_build_rate_periods_with_date_filtering(self):
        """Test _build_rate_periods method with date filtering."""
        # Setup
        risk_free_rates = [
            MockRiskFreeRate(date=date(2023, 1, 1), rate=5.0),
            MockRiskFreeRate(date=date(2023, 2, 1), rate=6.0),
            MockRiskFreeRate(date=date(2023, 3, 1), rate=4.0),
            MockRiskFreeRate(date=date(2023, 4, 1), rate=3.0)
        ]
        
        # Execute with date filtering
        start_date = date(2023, 2, 15)
        end_date = date(2023, 3, 15)
        rate_periods = DailyDebtCostCalculator._build_rate_periods(
            risk_free_rates, start_date, end_date
        )
        
        # Verify
        assert len(rate_periods) == 2  # Only periods that overlap with filter
        
        # First period: 2023-02-01 to 2023-03-01 (overlaps with filter)
        assert rate_periods[0]['start_date'] == date(2023, 2, 1)
        assert rate_periods[0]['end_date'] == date(2023, 3, 1)
        assert rate_periods[0]['rate'] == 6.0
        
        # Second period: 2023-03-01 to 2023-04-01 (overlaps with filter)
        assert rate_periods[1]['start_date'] == date(2023, 3, 1)
        assert rate_periods[1]['end_date'] == date(2023, 4, 1)
        assert rate_periods[1]['rate'] == 4.0
    
    def test_build_equity_periods_basic(self):
        """Test _build_equity_periods method with basic scenario."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=200000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=300000.0,
                amount=100000.0
            )
        ]
        
        # Execute
        equity_periods = DailyDebtCostCalculator._build_equity_periods(events)
        
        # Verify
        assert len(equity_periods) == 3
        
        # First period: 2023-01-01 to 2023-02-01
        assert equity_periods[0]['start_date'] == date(2023, 1, 1)
        assert equity_periods[0]['end_date'] == date(2023, 2, 1)
        assert equity_periods[0]['equity_amount'] == 100000.0
        
        # Second period: 2023-02-01 to 2023-03-01
        assert equity_periods[1]['start_date'] == date(2023, 2, 1)
        assert equity_periods[1]['end_date'] == date(2023, 3, 1)
        assert equity_periods[1]['equity_amount'] == 200000.0
        
        # Third period: 2023-03-01 to today
        assert equity_periods[2]['start_date'] == date(2023, 3, 1)
        assert equity_periods[2]['end_date'] == date.today()
        assert equity_periods[2]['equity_amount'] == 300000.0
    
    def test_build_equity_periods_with_zero_balance(self):
        """Test _build_equity_periods method with zero balance events."""
        # Setup - Events with zero equity balance should be skipped
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=0.0,  # Should be skipped
                amount=0.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,  # Should be included
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=0.0,  # Should be skipped
                amount=0.0
            )
        ]
        
        # Execute
        equity_periods = DailyDebtCostCalculator._build_equity_periods(events)
        
        # Verify
        assert len(equity_periods) == 1  # Only the non-zero balance event
        
        assert equity_periods[0]['start_date'] == date(2023, 2, 1)
        assert equity_periods[0]['end_date'] == date(2023, 3, 1)  # Next event date, not today
        assert equity_periods[0]['equity_amount'] == 100000.0
    
    def test_calculate_daily_debt_costs_basic(self):
        """Test _calculate_daily_debt_costs method with basic scenario."""
        # Setup
        equity_periods = [
            {
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 1, 3),  # 3 days
                'equity_amount': 100000.0
            }
        ]
        
        rate_periods = [
            {
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 1, 5),  # 5 days
                'rate': 5.0
            }
        ]
        
        # Execute
        daily_debt_costs = DailyDebtCostCalculator._calculate_daily_debt_costs(
            equity_periods, rate_periods
        )
        
        # Verify
        assert isinstance(daily_debt_costs, dict)
        assert len(daily_debt_costs) == 3  # 3 days of equity period
        
        # Check each day
        expected_daily_cost = 100000.0 * (5.0 / 365.25)
        
        for i in range(3):
            calc_date = date(2023, 1, 1) + timedelta(days=i)
            assert calc_date in daily_debt_costs
            
            daily_data = daily_debt_costs[calc_date]
            assert daily_data['debt_cost'] == pytest.approx(expected_daily_cost, rel=1e-6)
            assert daily_data['equity'] == 100000.0
            assert daily_data['rate'] == 5.0
    
    def test_calculate_daily_debt_costs_overlapping_periods(self):
        """Test _calculate_daily_debt_costs method with overlapping periods."""
        # Setup - Equity period overlaps with two rate periods
        equity_periods = [
            {
                'start_date': date(2023, 1, 2),
                'end_date': date(2023, 1, 4),  # 3 days
                'equity_amount': 100000.0
            }
        ]
        
        rate_periods = [
            {
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 1, 3),  # 5% rate
                'rate': 5.0
            },
            {
                'start_date': date(2023, 1, 3),
                'end_date': date(2023, 1, 5),  # 6% rate
                'rate': 6.0
            }
        ]
        
        # Execute
        daily_debt_costs = DailyDebtCostCalculator._calculate_daily_debt_costs(
            equity_periods, rate_periods
        )
        
        # Verify
        assert isinstance(daily_debt_costs, dict)
        assert len(daily_debt_costs) == 3  # 3 days of equity period
        
        # Day 1 (2023-01-02): 5% rate
        day1 = date(2023, 1, 2)
        assert day1 in daily_debt_costs
        day1_data = daily_debt_costs[day1]
        expected_cost_5pct = 100000.0 * (5.0 / 365.25)
        assert day1_data['debt_cost'] == pytest.approx(expected_cost_5pct, rel=1e-6)
        assert day1_data['rate'] == 5.0
        
        # Day 2 (2023-01-03): 6% rate (overlap with second rate period)
        day2 = date(2023, 1, 3)
        assert day2 in daily_debt_costs
        day2_data = daily_debt_costs[day2]
        expected_cost_6pct = 100000.0 * (6.0 / 365.25)
        assert day2_data['debt_cost'] == pytest.approx(expected_cost_6pct, rel=1e-6)
        assert day2_data['rate'] == 6.0
        
        # Day 3 (2023-01-04): 6% rate (overlap with second rate period)
        day3 = date(2023, 1, 4)
        assert day3 in daily_debt_costs
        day3_data = daily_debt_costs[day3]
        expected_cost_6pct = 100000.0 * (6.0 / 365.25)
        assert day3_data['debt_cost'] == pytest.approx(expected_cost_6pct, rel=1e-6)
        assert day3_data['rate'] == 6.0
    
    def test_calculate_daily_debt_costs_no_overlap(self):
        """Test _calculate_daily_debt_costs method with no overlapping periods."""
        # Setup - No overlap between equity and rate periods
        equity_periods = [
            {
                'start_date': date(2023, 1, 1),
                'end_date': date(2023, 1, 2),
                'equity_amount': 100000.0
            }
        ]
        
        rate_periods = [
            {
                'start_date': date(2023, 1, 3),  # Starts after equity period ends
                'end_date': date(2023, 1, 5),
                'rate': 5.0
            }
        ]
        
        # Execute
        daily_debt_costs = DailyDebtCostCalculator._calculate_daily_debt_costs(
            equity_periods, rate_periods
        )
        
        # Verify
        assert isinstance(daily_debt_costs, dict)
        assert len(daily_debt_costs) == 0  # No overlap = no calculations
    
    def test_calculate_debt_cost_complex_scenario(self):
        """Test debt cost calculation with complex overlapping periods."""
        # Setup - Complex scenario with multiple equity and rate periods
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=200000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.RETURN_OF_CAPITAL,
                current_equity_balance=150000.0,
                amount=-50000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(date=date(2023, 1, 1), rate=5.0),
            MockRiskFreeRate(date=date(2023, 2, 1), rate=6.0),
            MockRiskFreeRate(date=date(2023, 3, 1), rate=4.0)
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check that we have calculations for different periods with different equity amounts
        # January: 100k equity, 5% rate
        jan_15 = date(2023, 1, 15)
        if jan_15 in result:
            jan_data = result[jan_15]
            expected_cost = 100000.0 * (5.0 / 365.25)
            assert jan_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert jan_data['equity'] == 100000.0
            assert jan_data['rate'] == 5.0
        
        # February: 200k equity, 6% rate
        feb_15 = date(2023, 2, 15)
        if feb_15 in result:
            feb_data = result[feb_15]
            expected_cost = 200000.0 * (6.0 / 365.25)
            assert feb_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert feb_data['equity'] == 200000.0
            assert feb_data['rate'] == 6.0
        
        # March: 150k equity, 4% rate
        mar_15 = date(2023, 3, 15)
        if mar_15 in result:
            mar_data = result[mar_15]
            expected_cost = 150000.0 * (4.0 / 365.25)
            assert mar_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert mar_data['equity'] == 150000.0
            assert mar_data['rate'] == 4.0
    
    def test_calculate_debt_cost_with_real_models(self):
        """Test debt cost calculation using actual model instances."""
        # Setup - Create actual model instances
        fund_event = FundEvent(
            fund_id=1,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2023, 1, 1),
            amount=100000.0,
            current_equity_balance=100000.0
        )
        
        risk_free_rate = RiskFreeRate(
            currency=Currency.AUD,
            date=date(2023, 1, 1),
            rate=5.0,
            rate_type=RiskFreeRateType.GOVERNMENT_BOND
        )
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(
            [fund_event], [risk_free_rate]
        )
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check a specific day's calculation
        test_date = date(2023, 1, 15)
        if test_date in result:
            daily_data = result[test_date]
            expected_cost = 100000.0 * (5.0 / 365.25)
            assert daily_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert daily_data['equity'] == 100000.0
            assert daily_data['rate'] == 5.0
    
    def test_calculate_debt_cost_edge_case_same_dates(self):
        """Test debt cost calculation with events on the same date."""
        # Setup - Events on the same date
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            ),
            MockFundEvent(
                event_date=date(2023, 1, 1),  # Same date
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=200000.0,  # Different equity balance
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(date=date(2023, 1, 1), rate=5.0)
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Should use the last event's equity balance (200k)
        test_date = date(2023, 1, 15)
        if test_date in result:
            daily_data = result[test_date]
            expected_cost = 200000.0 * (5.0 / 365.25)
            assert daily_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert daily_data['equity'] == 200000.0
    
    def test_calculate_debt_cost_negative_rates(self):
        """Test debt cost calculation with negative interest rates."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                current_equity_balance=100000.0,
                amount=100000.0
            )
        ]
        
        risk_free_rates = [
            MockRiskFreeRate(date=date(2023, 1, 1), rate=-1.0)  # Negative rate
        ]
        
        # Execute
        result = DailyDebtCostCalculator.calculate_debt_cost(events, risk_free_rates)
        
        # Verify
        assert isinstance(result, dict)
        assert len(result) > 0
        
        # Check that negative rates are handled correctly
        test_date = date(2023, 1, 15)
        if test_date in result:
            daily_data = result[test_date]
            expected_cost = 100000.0 * (-1.0 / 365.25)  # Negative cost
            assert daily_data['debt_cost'] == pytest.approx(expected_cost, rel=1e-6)
            assert daily_data['equity'] == 100000.0
            assert daily_data['rate'] == -1.0
