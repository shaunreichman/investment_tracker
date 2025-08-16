"""
Debt Cost Calculation Tests

This module tests the debt cost calculation functionality for funds,
including edge cases and boundary conditions.
"""

import pytest
from datetime import date
from src.fund.calculations import calculate_debt_cost
from src.fund.enums import EventType, FundType


class TestDebtCostCalculation:
    """Tests for debt cost calculation function"""
    
    def test_debt_cost_no_events(self):
        """Test debt cost calculation with no events"""
        events = []
        risk_free_rates = []
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        currency = "AUD"
    
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
    
        assert result['total_debt_cost'] == 0.0
        assert result['average_risk_free_rate'] == 0.0
        assert result['debt_cost_percentage'] == 0.0
        # When no events, the function can't calculate equity periods, so duration is 0
        # This is the correct behavior - no events means no investment activity to measure
        assert result['investment_duration_years'] == 0.0
        assert result['total_days'] == 0  # No equity periods to calculate
    
    def test_debt_cost_no_risk_free_rates(self):
        """Test debt cost calculation with no risk-free rates"""
        from tests.factories import FundEventFactory, FundFactory
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        events = [
            FundEventFactory(fund=fund, event_type=EventType.CAPITAL_CALL, amount=100000.0, event_date=date(2024, 1, 1))
        ]
        risk_free_rates = []
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        currency = "AUD"
        
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
        
        assert result['total_debt_cost'] == 0.0
        assert result['average_risk_free_rate'] == 0.0
    
    def test_debt_cost_events_outside_period(self):
        """Test debt cost calculation with events outside calculation period"""
        from tests.factories import FundEventFactory, FundFactory
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        events = [
            FundEventFactory(fund=fund, event_type=EventType.CAPITAL_CALL, amount=100000.0, event_date=date(2023, 1, 1)),
            FundEventFactory(fund=fund, event_type=EventType.RETURN_OF_CAPITAL, amount=50000.0, event_date=date(2025, 1, 1))
        ]
        risk_free_rates = []
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        currency = "AUD"
        
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
        
        assert result['total_debt_cost'] == 0.0
        assert result['average_equity'] == 0.0
    
    def test_debt_cost_single_day_period(self):
        """Test debt cost calculation with single day period"""
        from tests.factories import FundEventFactory, FundFactory
    
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        events = [
            FundEventFactory(fund=fund, event_type=EventType.CAPITAL_CALL, amount=100000.0, event_date=date(2024, 1, 1))
        ]
        risk_free_rates = []
        start_date = date(2024, 1, 1)
        end_date = date(2024, 1, 1)
        currency = "AUD"
    
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
    
        # For single day, we expect at least 1 day of calculation
        assert result['total_days'] >= 1
        assert result['investment_duration_years'] > 0
    
    def test_debt_cost_very_high_rates(self):
        """Test debt cost calculation with very high risk-free rates"""
        from tests.factories import FundEventFactory, FundFactory, RiskFreeRateFactory
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        events = [
            FundEventFactory(fund=fund, event_type=EventType.CAPITAL_CALL, amount=100000.0, event_date=date(2024, 1, 1))
        ]
        risk_free_rates = [
            RiskFreeRateFactory(rate_date=date(2024, 1, 1), rate=50.0, currency="AUD")  # 50% rate
        ]
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        currency = "AUD"
        
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
        
        assert result['total_debt_cost'] > 0
        assert result['average_risk_free_rate'] == 50.0
    
    def test_debt_cost_negative_equity(self):
        """Test debt cost calculation with negative equity (should handle gracefully)"""
        from tests.factories import FundEventFactory, FundFactory, RiskFreeRateFactory
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        events = [
            FundEventFactory(fund=fund, event_type=EventType.CAPITAL_CALL, amount=100000.0, event_date=date(2024, 1, 1)),
            FundEventFactory(fund=fund, event_type=EventType.DISTRIBUTION, amount=150000.0, event_date=date(2024, 6, 1))  # Over-distribution
        ]
        risk_free_rates = [
            RiskFreeRateFactory(rate_date=date(2024, 1, 1), rate=5.0, currency="AUD")
        ]
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        currency = "AUD"
        
        result = calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)
        
        # Should handle negative equity gracefully
        assert 'total_debt_cost' in result
        assert 'average_equity' in result
