"""
Tests for DebtCostCalculator.

Tests the pure mathematical calculations for debt cost and opportunity cost.
"""

import pytest
from datetime import date, timedelta
from dataclasses import dataclass
from unittest.mock import Mock

from src.fund.calculators.debt_cost_calculator import DebtCostCalculator, DebtCostResult
from src.fund.enums import EventType, FundType


@dataclass
class MockRiskFreeRate:
    """Mock risk-free rate for testing."""
    rate_date: date
    rate: float


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    event_date: date
    event_type: EventType
    amount: float = None
    units_purchased: float = None
    units_sold: float = None
    unit_price: float = None
    fund: Mock = None


class TestDebtCostCalculator:
    """Test cases for DebtCostCalculator."""
    
    def test_calculate_debt_cost_basic(self):
        """Test basic debt cost calculation."""
        # Setup test data
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        currency = "USD"
        
        # Mock risk-free rates
        risk_free_rates = [
            MockRiskFreeRate(date(2023, 1, 1), 5.0),
            MockRiskFreeRate(date(2023, 7, 1), 4.5)
        ]
        
        # Mock fund with tracking type
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Mock events
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                fund=mock_fund
            ),
            MockFundEvent(
                event_date=date(2023, 6, 30),
                event_type=EventType.RETURN_OF_CAPITAL,
                amount=50000.0,
                fund=mock_fund
            )
        ]
        
        # Calculate debt cost
        result = DebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date, currency
        )
        
        # Verify result structure
        assert isinstance(result, DebtCostResult)
        assert result.total_debt_cost >= 0
        assert result.average_risk_free_rate > 0
        assert result.total_days > 0
        assert result.investment_duration_years > 0
    
    def test_calculate_debt_cost_nav_based(self):
        """Test debt cost calculation for NAV-based fund."""
        # Setup test data
        start_date = date(2023, 1, 1)
        end_date = date(2023, 6, 30)
        currency = "USD"
        
        # Mock risk-free rates
        risk_free_rates = [
            MockRiskFreeRate(date(2023, 1, 1), 5.0)
        ]
        
        # Mock fund with NAV-based tracking type
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.NAV_BASED
        
        # Mock NAV-based events
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=1000.0,
                unit_price=100.0,
                fund=mock_fund
            ),
            MockFundEvent(
                event_date=date(2023, 3, 31),
                event_type=EventType.UNIT_SALE,
                units_sold=500.0,
                unit_price=110.0,
                fund=mock_fund
            )
        ]
        
        # Calculate debt cost
        result = DebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date, currency
        )
        
        # Verify result
        assert isinstance(result, DebtCostResult)
        assert result.total_debt_cost >= 0
        assert result.average_equity >= 0
    
    def test_calculate_debt_cost_empty_events(self):
        """Test debt cost calculation with no events."""
        # Setup test data
        start_date = date(2023, 1, 1)
        end_date = date(2023, 12, 31)
        currency = "USD"
        
        # Mock risk-free rates
        risk_free_rates = [
            MockRiskFreeRate(date(2023, 1, 1), 5.0)
        ]
        
        # Empty events list
        events = []
        
        # Calculate debt cost
        result = DebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date, currency
        )
        
        # Verify result
        assert isinstance(result, DebtCostResult)
        assert result.total_debt_cost == 0
        assert result.average_equity == 0
        # When no events, there's still a period from start_date to end_date
        assert result.total_days == 364  # 2023-12-31 - 2023-01-01 = 364 days
    
    def test_calculate_debt_cost_single_day(self):
        """Test debt cost calculation for single day period."""
        # Setup test data
        start_date = date(2023, 1, 1)
        end_date = date(2023, 1, 1)  # Same day
        currency = "USD"
        
        # Mock risk-free rates
        risk_free_rates = [
            MockRiskFreeRate(date(2023, 1, 1), 5.0)
        ]
        
        # Mock fund
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Mock events
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                fund=mock_fund
            )
        ]
        
        # Calculate debt cost
        result = DebtCostCalculator.calculate_debt_cost(
            events, risk_free_rates, start_date, end_date, currency
        )
        
        # Verify result
        assert isinstance(result, DebtCostResult)
        assert result.total_days >= 1  # Should be at least 1 day
    
    def test_build_rate_periods(self):
        """Test rate periods building."""
        # Setup test data
        end_date = date(2023, 12, 31)
        risk_free_rates = [
            MockRiskFreeRate(date(2023, 1, 1), 5.0),
            MockRiskFreeRate(date(2023, 7, 1), 4.5)
        ]
        
        # Build rate periods
        rate_periods = DebtCostCalculator._build_rate_periods(risk_free_rates, end_date)
        
        # Verify result
        assert len(rate_periods) == 2
        assert rate_periods[0] == (date(2023, 1, 1), date(2023, 7, 1), 5.0)
        assert rate_periods[1] == (date(2023, 7, 1), date(2024, 1, 1), 4.5)  # end_date + 1 day
    
    def test_calculate_equity_change_capital_call(self):
        """Test equity change calculation for capital call."""
        # Mock fund
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Mock event
        event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.CAPITAL_CALL,
            amount=100000.0,
            fund=mock_fund
        )
        
        # Calculate equity change
        change = DebtCostCalculator._calculate_equity_change(event)
        
        # Verify result
        assert change == 100000.0
    
    def test_calculate_equity_change_return_of_capital(self):
        """Test equity change calculation for return of capital."""
        # Mock fund
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.COST_BASED
        
        # Mock event
        event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=50000.0,
            fund=mock_fund
        )
        
        # Calculate equity change
        change = DebtCostCalculator._calculate_equity_change(event)
        
        # Verify result
        assert change == -50000.0
    
    def test_calculate_equity_change_unit_purchase(self):
        """Test equity change calculation for unit purchase."""
        # Mock fund
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.NAV_BASED
        
        # Mock event
        event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=1000.0,
            unit_price=100.0,
            fund=mock_fund
        )
        
        # Calculate equity change
        change = DebtCostCalculator._calculate_equity_change(event)
        
        # Verify result
        assert change == 100000.0  # 1000 * 100
    
    def test_calculate_equity_change_unit_sale(self):
        """Test equity change calculation for unit sale."""
        # Mock fund
        mock_fund = Mock()
        mock_fund.tracking_type = FundType.NAV_BASED
        
        # Mock event
        event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_SALE,
            units_sold=500.0,
            unit_price=110.0,
            fund=mock_fund
        )
        
        # Calculate equity change
        change = DebtCostCalculator._calculate_equity_change(event)
        
        # Verify result
        assert change == -55000.0  # -(500 * 110)
    
    def test_find_applicable_rate(self):
        """Test finding applicable rate for a period."""
        # Setup rate periods
        rate_periods = [
            (date(2023, 1, 1), date(2023, 7, 1), 5.0),
            (date(2023, 7, 1), date(2024, 1, 1), 4.5)
        ]
        
        # Test finding rate for period within first rate period
        rate = DebtCostCalculator._find_applicable_rate(
            date(2023, 3, 1), date(2023, 4, 1), rate_periods
        )
        assert rate == 5.0
        
        # Test finding rate for period within second rate period
        rate = DebtCostCalculator._find_applicable_rate(
            date(2023, 8, 1), date(2023, 9, 1), rate_periods
        )
        assert rate == 4.5
        
        # Test finding rate for period not covered
        rate = DebtCostCalculator._find_applicable_rate(
            date(2024, 1, 1), date(2024, 2, 1), rate_periods
        )
        assert rate is None
