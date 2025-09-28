"""
Tests for FundEquityCalculator.

Tests the pure mathematical calculations for fund equity operations,
including current equity balance, average equity balance, and cost basis calculations.
"""

import pytest
from datetime import date, timedelta
from dataclasses import dataclass
from typing import List, Optional

from src.fund.calculators.fund_equity_calculator import FundEquityCalculator
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent
from src.fund.enums.fund_enums import FundTrackingType, FundStatus, FundInvestmentType
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import Currency, Country


@dataclass
class MockFund:
    """Mock fund for testing."""
    id: int = 1
    tracking_type: FundTrackingType = FundTrackingType.COST_BASED
    status: FundStatus = FundStatus.ACTIVE
    end_date: Optional[date] = None


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    id: int = 1
    fund_id: int = 1
    event_type: EventType = EventType.CAPITAL_CALL
    event_date: date = date(2023, 1, 1)
    amount: Optional[float] = None
    units_purchased: Optional[float] = None
    units_sold: Optional[float] = None
    unit_price: Optional[float] = None
    fund: Optional[MockFund] = None


class TestFundEquityCalculator:
    """Test cases for FundEquityCalculator."""
    
    def test_calculate_event_equity_balances_cost_based_single_call(self):
        """Test cost-based equity balance calculation with single capital call."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 1
        balance, has_changed = result[0]
        assert balance == 100000.0
        assert has_changed is True
    
    def test_calculate_event_equity_balances_cost_based_multiple_calls(self):
        """Test cost-based equity balance calculation with multiple capital calls."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 2, 1),
                amount=50000.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 2
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        
        assert balance1 == 100000.0
        assert has_changed1 is True
        assert balance2 == 150000.0
        assert has_changed2 is True
    
    def test_calculate_event_equity_balances_cost_based_with_returns(self):
        """Test cost-based equity balance calculation with capital calls and returns."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2023, 2, 1),
                amount=30000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 3, 1),
                amount=20000.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 100000.0
        assert has_changed1 is True
        assert balance2 == 70000.0  # 100000 - 30000
        assert has_changed2 is True
        assert balance3 == 90000.0  # 70000 + 20000
        assert has_changed3 is True
    
    def test_calculate_event_equity_balances_cost_based_non_equity_events(self):
        """Test cost-based equity balance calculation with non-equity events."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,  # Non-equity event
                event_date=date(2023, 2, 1),
                amount=5000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 3, 1),
                amount=20000.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 100000.0
        assert has_changed1 is True
        assert balance2 == 100000.0  # Unchanged for non-equity event
        assert has_changed2 is False
        assert balance3 == 120000.0  # 100000 + 20000
        assert has_changed3 is True
    
    def test_calculate_event_equity_balances_nav_based_single_purchase(self):
        """Test NAV-based equity balance calculation with single unit purchase."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 1
        balance, has_changed = result[0]
        assert balance == 100000.0  # 1000 * 100
        assert has_changed is True
    
    def test_calculate_event_equity_balances_nav_based_multiple_purchases(self):
        """Test NAV-based equity balance calculation with multiple unit purchases."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=500.0,
                unit_price=110.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 2
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        
        assert balance1 == 100000.0  # 1000 * 100
        assert has_changed1 is True
        assert balance2 == 155000.0  # 100000 + (500 * 110)
        assert has_changed2 is True
    
    def test_calculate_event_equity_balances_nav_based_with_sales(self):
        """Test NAV-based equity balance calculation with unit purchases and sales using FIFO."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=500.0,
                unit_price=110.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 3, 1),
                units_sold=300.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 100000.0  # 1000 * 100
        assert has_changed1 is True
        assert balance2 == 155000.0  # 100000 + (500 * 110)
        assert has_changed2 is True
        assert balance3 == 125000.0  # 155000 - (300 * 100) - FIFO from first purchase
        assert has_changed3 is True
    
    def test_calculate_event_equity_balances_nav_based_fifo_complex(self):
        """Test NAV-based equity balance calculation with complex FIFO scenario."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=500.0,
                unit_price=110.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 3, 1),
                units_sold=1200.0,  # Sells all from first purchase + 200 from second
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 4, 1),
                units_purchased=300.0,
                unit_price=120.0,
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 4
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        balance4, has_changed4 = result[3]
        
        assert balance1 == 100000.0  # 1000 * 100
        assert has_changed1 is True
        assert balance2 == 155000.0  # 100000 + (500 * 110)
        assert has_changed2 is True
        assert balance3 == 33000.0   # 155000 - (1000 * 100) - (200 * 110) = 155000 - 100000 - 22000
        assert has_changed3 is True
        assert balance4 == 69000.0   # 33000 + (300 * 120)
        assert has_changed4 is True
    
    def test_calculate_event_equity_balances_nav_based_invalid_units(self):
        """Test NAV-based equity balance calculation with invalid unit values."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=0.0,  # Invalid: zero units
                unit_price=110.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 3, 1),
                units_purchased=500.0,
                unit_price=0.0,  # Invalid: zero price
                fund=fund
            )
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 100000.0
        assert has_changed1 is True
        assert balance2 == 100000.0  # Unchanged due to invalid units
        assert has_changed2 is False
        assert balance3 == 100000.0  # Unchanged due to invalid price
        assert has_changed3 is False
    
    def test_calculate_event_equity_balances_unsupported_fund_type(self):
        """Test equity balance calculation with unsupported fund type."""
        # Setup
        fund = MockFund(tracking_type="INVALID_TYPE")  # Invalid tracking type
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            )
        ]
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Unsupported fund type"):
            FundEquityCalculator.calculate_event_equity_balances(fund, events)
    
    def test_calculate_current_equity_from_balances_empty(self):
        """Test current equity calculation with empty balances."""
        # Setup
        event_balances = []
        
        # Execute
        result = FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
        
        # Verify
        assert result == 0.0
    
    def test_calculate_current_equity_from_balances_single(self):
        """Test current equity calculation with single balance."""
        # Setup
        event_balances = [(100000.0, True)]
        
        # Execute
        result = FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
        
        # Verify
        assert result == 100000.0
    
    def test_calculate_current_equity_from_balances_multiple(self):
        """Test current equity calculation with multiple balances."""
        # Setup
        event_balances = [
            (100000.0, True),
            (150000.0, True),
            (120000.0, True)
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
        
        # Verify
        assert result == 120000.0  # Last balance
    
    def test_calculate_average_equity_from_balances_empty(self):
        """Test average equity calculation with empty data."""
        # Setup
        events = []
        event_balances = []
        
        # Execute
        result = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Verify
        assert result == 0.0
    
    def test_calculate_average_equity_from_balances_mismatched_lengths(self):
        """Test average equity calculation with mismatched event and balance lengths."""
        # Setup
        fund = MockFund()
        events = [
            MockFundEvent(event_date=date(2023, 1, 1), fund=fund),
            MockFundEvent(event_date=date(2023, 2, 1), fund=fund)
        ]
        event_balances = [(100000.0, True)]  # Only one balance for two events
        
        # Execute
        result = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Verify
        assert result == 0.0
    
    def test_calculate_average_equity_from_balances_single_event(self):
        """Test average equity calculation with single event."""
        # Setup
        fund = MockFund(status=FundStatus.ACTIVE)
        events = [
            MockFundEvent(event_date=date(2023, 1, 1), fund=fund)
        ]
        event_balances = [(100000.0, True)]
        
        # Execute
        result = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Verify
        # Should calculate from event date to today
        expected_days = (date.today() - date(2023, 1, 1)).days
        expected_average = 100000.0  # Same balance for all days
        assert result == pytest.approx(expected_average, rel=1e-6)
    
    def test_calculate_average_equity_from_balances_multiple_events(self):
        """Test average equity calculation with multiple events."""
        # Setup
        fund = MockFund(status=FundStatus.ACTIVE)
        events = [
            MockFundEvent(event_date=date(2023, 1, 1), fund=fund),
            MockFundEvent(event_date=date(2023, 1, 31), fund=fund),  # 30 days later
            MockFundEvent(event_date=date(2023, 2, 28), fund=fund)   # 28 days later
        ]
        event_balances = [
            (100000.0, True),   # 30 days
            (150000.0, True),   # 28 days
            (120000.0, True)    # Remaining days to today
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Verify
        # Weighted average: (100000 * 30 + 150000 * 28 + 120000 * remaining_days) / total_days
        total_days = (date.today() - date(2023, 1, 1)).days
        remaining_days = total_days - 30 - 28
        
        expected_weighted = (100000.0 * 30 + 150000.0 * 28 + 120000.0 * remaining_days) / total_days
        assert result == pytest.approx(expected_weighted, rel=1e-6)
    
    def test_calculate_average_equity_from_balances_with_end_date(self):
        """Test average equity calculation with fund end date."""
        # Setup
        fund = MockFund(status=FundStatus.COMPLETED, end_date=date(2023, 3, 31))
        events = [
            MockFundEvent(event_date=date(2023, 1, 1), fund=fund),
            MockFundEvent(event_date=date(2023, 2, 1), fund=fund)  # 31 days later
        ]
        event_balances = [
            (100000.0, True),   # 31 days
            (150000.0, True)    # 58 days to end date
        ]
        
        # Execute
        result = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Verify
        # Weighted average: (100000 * 31 + 150000 * 58) / 89
        total_days = 89
        expected_weighted = (100000.0 * 31 + 150000.0 * 58) / total_days
        assert result == pytest.approx(expected_weighted, rel=1e-6)
    
    def test_calculate_total_cost_basis_from_balances_cost_based(self):
        """Test cost basis calculation for cost-based fund."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 2, 1),
                amount=50000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.RETURN_OF_CAPITAL,  # Should not be included
                event_date=date(2023, 3, 1),
                amount=30000.0,
                fund=fund
            )
        ]
        event_balances = [(100000.0, True), (150000.0, True), (120000.0, True)]
        
        # Execute
        result = FundEquityCalculator.calculate_total_cost_basis_from_balances(
            event_balances, fund, events
        )
        
        # Verify
        assert result == 150000.0  # Sum of capital calls only
    
    def test_calculate_total_cost_basis_from_balances_nav_based(self):
        """Test cost basis calculation for NAV-based fund."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED)
        events = []  # Not used for NAV-based
        event_balances = [(100000.0, True), (150000.0, True)]
        
        # Execute
        result = FundEquityCalculator.calculate_total_cost_basis_from_balances(
            event_balances, fund, events
        )
        
        # Verify
        assert result == 150000.0  # Current equity balance (last balance)
    
    def test_calculate_total_cost_basis_from_balances_unsupported_fund_type(self):
        """Test cost basis calculation with unsupported fund type."""
        # Setup
        fund = MockFund(tracking_type="INVALID_TYPE")
        events = []
        event_balances = [(100000.0, True)]
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Unsupported fund type"):
            FundEquityCalculator.calculate_total_cost_basis_from_balances(
                event_balances, fund, events
            )
    
    def test_calculate_total_cost_basis_from_balances_cost_based_with_none_amounts(self):
        """Test cost basis calculation with None amounts in events."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 2, 1),
                amount=None,  # None amount
                fund=fund
            )
        ]
        event_balances = [(100000.0, True), (100000.0, False)]
        
        # Execute
        result = FundEquityCalculator.calculate_total_cost_basis_from_balances(
            event_balances, fund, events
        )
        
        # Verify
        assert result == 100000.0  # Only the first capital call
    
    def test_process_cost_based_events_empty(self):
        """Test cost-based event processing with empty events."""
        # Setup
        events = []
        
        # Execute
        result = FundEquityCalculator._process_cost_based_events(events)
        
        # Verify
        assert result == []
    
    def test_process_cost_based_events_with_none_amounts(self):
        """Test cost-based event processing with None amounts."""
        # Setup
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=None
            ),
            MockFundEvent(
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2023, 2, 1),
                amount=None
            )
        ]
        
        # Execute
        result = FundEquityCalculator._process_cost_based_events(events)
        
        # Verify
        assert len(result) == 2
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        
        assert balance1 == 0.0  # None amount treated as 0
        assert has_changed1 is True
        assert balance2 == 0.0  # None amount treated as 0
        assert has_changed2 is True
    
    def test_process_nav_based_events_empty(self):
        """Test NAV-based event processing with empty events."""
        # Setup
        events = []
        
        # Execute
        result = FundEquityCalculator._process_nav_based_events(events)
        
        # Verify
        assert result == []
    
    def test_process_nav_based_events_with_none_values(self):
        """Test NAV-based event processing with None values."""
        # Setup
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=None,
                unit_price=100.0
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=500.0,
                unit_price=None
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 3, 1),
                units_sold=None
            )
        ]
        
        # Execute
        result = FundEquityCalculator._process_nav_based_events(events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 0.0  # None values treated as 0
        assert has_changed1 is False
        assert balance2 == 0.0  # None values treated as 0
        assert has_changed2 is False
        assert balance3 == 0.0  # None values treated as 0
        assert has_changed3 is False
    
    def test_process_nav_based_events_fifo_edge_cases(self):
        """Test NAV-based event processing with FIFO edge cases."""
        # Setup
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 2, 1),
                units_sold=1000.0  # Sell all units
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 3, 1),
                units_sold=100.0  # Try to sell more than available
            )
        ]
        
        # Execute
        result = FundEquityCalculator._process_nav_based_events(events)
        
        # Verify
        assert len(result) == 3
        balance1, has_changed1 = result[0]
        balance2, has_changed2 = result[1]
        balance3, has_changed3 = result[2]
        
        assert balance1 == 100000.0  # 1000 * 100
        assert has_changed1 is True
        assert balance2 == 0.0  # All units sold
        assert has_changed2 is True
        assert balance3 == 0.0  # No units left to sell
        assert has_changed3 is True  # Sale event is recorded even if no units available
    
    def test_integration_cost_based_complete_workflow(self):
        """Test complete workflow for cost-based fund equity calculations."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED, status=FundStatus.ACTIVE)
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=100000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 2, 1),
                amount=50000.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2023, 3, 1),
                amount=30000.0,
                fund=fund
            )
        ]
        
        # Execute - Step 1: Calculate event balances
        event_balances = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Execute - Step 2: Calculate current equity
        current_equity = FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
        
        # Execute - Step 3: Calculate average equity
        average_equity = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Execute - Step 4: Calculate cost basis
        cost_basis = FundEquityCalculator.calculate_total_cost_basis_from_balances(event_balances, fund, events)
        
        # Verify
        assert len(event_balances) == 3
        assert event_balances[0] == (100000.0, True)
        assert event_balances[1] == (150000.0, True)
        assert event_balances[2] == (120000.0, True)
        
        assert current_equity == 120000.0
        assert cost_basis == 150000.0  # Sum of capital calls
        assert average_equity > 0  # Should be positive time-weighted average
    
    def test_integration_nav_based_complete_workflow(self):
        """Test complete workflow for NAV-based fund equity calculations."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.NAV_BASED, status=FundStatus.ACTIVE)
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=100.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 2, 1),
                units_purchased=500.0,
                unit_price=110.0,
                fund=fund
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 3, 1),
                units_sold=300.0,
                fund=fund
            )
        ]
        
        # Execute - Step 1: Calculate event balances
        event_balances = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        
        # Execute - Step 2: Calculate current equity
        current_equity = FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
        
        # Execute - Step 3: Calculate average equity
        average_equity = FundEquityCalculator.calculate_average_equity_from_balances(events, event_balances)
        
        # Execute - Step 4: Calculate cost basis
        cost_basis = FundEquityCalculator.calculate_total_cost_basis_from_balances(event_balances, fund, events)
        
        # Verify
        assert len(event_balances) == 3
        assert event_balances[0] == (100000.0, True)  # 1000 * 100
        assert event_balances[1] == (155000.0, True)  # 100000 + (500 * 110)
        assert event_balances[2] == (125000.0, True)  # 155000 - (300 * 100) - FIFO
        
        assert current_equity == 125000.0
        assert cost_basis == 125000.0  # Same as current equity for NAV-based
        assert average_equity > 0  # Should be positive time-weighted average
