"""
Tests for CompanyEquityBalanceCalculator.

Tests the pure mathematical calculations for company equity balance operations,
including current equity balance, average equity balance, and time-weighted calculations.
"""

import pytest
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Optional

from src.investment_company.calculators.company_equity_balance_calculator import CompanyEquityBalanceCalculator
from src.fund.models.fund_event import FundEvent
from src.fund.enums.fund_event_enums import EventType


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    id: int = 1
    fund_id: int = 1
    event_type: EventType = EventType.CAPITAL_CALL
    event_date: date = date(2023, 1, 1)
    amount: Optional[float] = None
    current_equity_balance: Optional[float] = None


class TestCompanyEquityBalanceCalculator:
    """Test cases for CompanyEquityBalanceCalculator."""
    
    def test_calculate_company_equity_balance_empty_events(self):
        """Test company equity balance calculation with empty events list."""
        # Setup
        fund_events = []
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert average_equity == 0
        assert current_equity == 0
        assert last_event_date is None
    
    def test_calculate_company_equity_balance_single_event(self):
        """Test company equity balance calculation with single event."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 100000.0
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_multiple_events_same_fund(self):
        """Test company equity balance calculation with multiple events from same fund."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 2, 1),
                current_equity_balance=150000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 3, 1),
                current_equity_balance=120000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 120000.0  # Last event's balance
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_multiple_funds(self):
        """Test company equity balance calculation with events from multiple funds."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 2, 1),
                current_equity_balance=200000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 3, 1),
                current_equity_balance=150000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 350000.0  # 150000 (fund 1) + 200000 (fund 2)
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_zero_balance(self):
        """Test company equity balance calculation when final balance is zero."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 2, 1),
                current_equity_balance=0.0  # Zero balance
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 0.0
        assert last_event_date == date(2023, 2, 1)  # Should be last event date, not today
        assert average_equity > 0  # Should still have positive average from first period
    
    def test_calculate_company_equity_balance_time_weighted_calculation(self):
        """Test time-weighted average calculation accuracy."""
        # Setup - Create events with known time periods for precise testing
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 31),  # 30 days later
                current_equity_balance=200000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 200000.0
        
        # Calculate expected time-weighted average
        # Period 1: 100000 for 30 days
        # Period 2: 200000 for remaining days to today
        days_to_today = (date.today() - date(2023, 1, 31)).days
        total_days = (date.today() - date(2023, 1, 1)).days
        
        expected_weighted = (100000.0 * 30 + 200000.0 * days_to_today) / total_days
        assert average_equity == pytest.approx(expected_weighted, rel=1e-6)
    
    def test_calculate_company_equity_balance_negative_balance(self):
        """Test company equity balance calculation with negative balance."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 2, 1),
                current_equity_balance=-50000.0  # Negative balance
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == -50000.0
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity != 0  # Should have some average value
    
    def test_calculate_company_equity_balance_fund_balance_updates(self):
        """Test that fund balance updates are correctly tracked."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 2, 1),
                current_equity_balance=200000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 3, 1),
                current_equity_balance=150000.0  # Fund 1 balance updated
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 4, 1),
                current_equity_balance=180000.0  # Fund 2 balance updated
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 330000.0  # 150000 (fund 1) + 180000 (fund 2)
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_single_day_events(self):
        """Test company equity balance calculation with events on same day."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 1, 1),  # Same day
                current_equity_balance=200000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 300000.0  # 100000 + 200000
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_large_time_gap(self):
        """Test company equity balance calculation with large time gap."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2020, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),  # 3 years later
                current_equity_balance=200000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 200000.0
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_future_dates(self):
        """Test company equity balance calculation with future event dates."""
        # Setup
        future_date = date.today() + timedelta(days=30)
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=future_date,
                current_equity_balance=200000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 200000.0
        assert last_event_date == future_date  # Should be the future date, not today
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_none_equity_balance(self):
        """Test company equity balance calculation with None equity balance."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=None  # None balance
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 0.0  # None should be treated as 0
        assert last_event_date == date(2023, 1, 1)  # Should be event date since balance is 0
        assert average_equity == 0.0  # Should be 0 since balance is 0
    
    def test_calculate_company_equity_balance_mixed_none_balances(self):
        """Test company equity balance calculation with mixed None and valid balances."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 2, 1),
                current_equity_balance=None  # None balance
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 3, 1),
                current_equity_balance=150000.0
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 150000.0  # Only fund 1's balance (fund 2 is 0)
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_precision(self):
        """Test company equity balance calculation precision with decimal values."""
        # Setup
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.50
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 2, 1),
                current_equity_balance=200000.75
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 200000.75
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_calculate_company_equity_balance_integration_complex_scenario(self):
        """Test complete integration scenario with complex fund events."""
        # Setup - Complex scenario with multiple funds and varying balances
        fund_events = [
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 1, 1),
                current_equity_balance=100000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 1, 15),
                current_equity_balance=200000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 2, 1),
                current_equity_balance=150000.0
            ),
            MockFundEvent(
                fund_id=3,
                event_date=date(2023, 2, 15),
                current_equity_balance=300000.0
            ),
            MockFundEvent(
                fund_id=2,
                event_date=date(2023, 3, 1),
                current_equity_balance=180000.0
            ),
            MockFundEvent(
                fund_id=1,
                event_date=date(2023, 3, 15),
                current_equity_balance=0.0  # Fund 1 closed
            )
        ]
        
        # Execute
        result = CompanyEquityBalanceCalculator.calculate_company_equity_balance(fund_events)
        
        # Verify
        average_equity, current_equity, last_event_date = result
        assert current_equity == 480000.0  # 0 (fund 1) + 180000 (fund 2) + 300000 (fund 3)
        assert last_event_date == date.today()  # Should be today since balance != 0
        assert average_equity > 0  # Should be positive time-weighted average
        
        # Verify that the calculation handles the complex scenario correctly
        assert average_equity < current_equity  # Average should be less than current due to time weighting
