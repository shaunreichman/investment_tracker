"""
Tests for FifoCapitalGainsCalculator.

Tests the pure mathematical calculations for FIFO-based capital gains calculations.
"""

import pytest
from datetime import date
from dataclasses import dataclass
from unittest.mock import Mock
from collections import deque

from src.fund.calculators.fifo_capital_gains_calculator import (
    FifoCapitalGainsCalculator, 
    FifoUnit, 
    CapitalGainResult,
    CapitalGainSaleDetail
)
from src.fund.enums import EventType
from src.shared.enums.shared_enums import Country


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    event_date: date
    event_type: EventType
    units_purchased: float = None
    units_sold: float = None
    unit_price: float = None
    brokerage_fee: float = 0.0
    amount: float = None


class TestFifoCapitalGainsCalculator:
    """Test cases for FifoCapitalGainsCalculator."""
    
    def test_process_purchase_event_basic(self):
        """Test basic purchase event processing."""
        # Setup
        purchase_event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=5.0
        )
        
        # Execute
        fifo_unit = FifoCapitalGainsCalculator.process_purchase_event(purchase_event)
        
        # Verify
        assert fifo_unit.units == 100.0
        assert fifo_unit.unit_price == 10.0
        assert fifo_unit.effective_price == 10.05  # 10.0 + (5.0 / 100.0)
        assert fifo_unit.purchase_date == date(2023, 1, 1)
        assert fifo_unit.brokerage_fee == 5.0
    
    def test_process_purchase_event_no_brokerage(self):
        """Test purchase event processing with no brokerage fee."""
        # Setup
        purchase_event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=50.0,
            unit_price=20.0,
            brokerage_fee=0.0
        )
        
        # Execute
        fifo_unit = FifoCapitalGainsCalculator.process_purchase_event(purchase_event)
        
        # Verify
        assert fifo_unit.units == 50.0
        assert fifo_unit.unit_price == 20.0
        assert fifo_unit.effective_price == 20.0  # No brokerage fee
        assert fifo_unit.brokerage_fee == 0.0
    
    def test_process_purchase_event_invalid_units(self):
        """Test purchase event processing with invalid units."""
        # Setup
        purchase_event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=0.0,  # Invalid
            unit_price=10.0,
            brokerage_fee=5.0
        )
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Units purchased must be positive"):
            FifoCapitalGainsCalculator.process_purchase_event(purchase_event)
    
    def test_process_purchase_event_invalid_price(self):
        """Test purchase event processing with invalid price."""
        # Setup
        purchase_event = MockFundEvent(
            event_date=date(2023, 1, 1),
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=0.0,  # Invalid
            brokerage_fee=5.0
        )
        
        # Execute & Verify
        with pytest.raises(ValueError, match="Unit price must be positive"):
            FifoCapitalGainsCalculator.process_purchase_event(purchase_event)
    
    def test_calculate_capital_gains_for_sale_basic(self):
        """Test basic capital gains calculation for a sale."""
        # Setup
        sale_event = MockFundEvent(
            event_date=date(2023, 2, 1),
            event_type=EventType.UNIT_SALE,
            units_sold=50.0,
            unit_price=15.0,
            brokerage_fee=2.0
        )
        
        fifo_queue = deque([
            FifoUnit(
                units=100.0,
                unit_price=10.0,
                effective_price=10.05,  # 10.0 + (5.0 / 100.0)
                purchase_date=date(2023, 1, 1),
                brokerage_fee=5.0
            )
        ])
        
        # Execute
        capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue, tax_jurisdiction=None
        )
        
        # Verify
        expected_capital_gain = 50.0 * (15.0 - 2.0/50.0 - 10.05)  # 50 * (14.96 - 10.05) = 245.5
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert discountable_capital_gain == pytest.approx(0.0, rel=1e-6)  # No discount for non-AU
        assert sale_proceeds == pytest.approx(50.0 * (15.0 - 2.0/50.0), rel=1e-6)
        assert brokerage_fee == 2.0
        assert avg_holding_period_days == 31.0  # 31 days from Jan 1 to Feb 1
        assert qualified_for_discount == False  # No discount for non-AU
        
        # Verify FIFO queue was updated
        assert len(fifo_queue) == 1
        assert fifo_queue[0].units == 50.0  # 100 - 50
    
    def test_calculate_capital_gains_for_sale_multiple_purchases(self):
        """Test capital gains calculation with multiple purchases in FIFO."""
        # Setup
        sale_event = MockFundEvent(
            event_date=date(2023, 3, 1),
            event_type=EventType.UNIT_SALE,
            units_sold=150.0,
            unit_price=20.0,
            brokerage_fee=3.0
        )
        
        fifo_queue = deque([
            FifoUnit(units=100.0, unit_price=10.0, effective_price=10.05, 
                    purchase_date=date(2023, 1, 1), brokerage_fee=5.0),
            FifoUnit(units=100.0, unit_price=12.0, effective_price=12.02, 
                    purchase_date=date(2023, 2, 1), brokerage_fee=2.0)
        ])
        
        # Execute
        capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue, tax_jurisdiction=None
        )
        
        # Verify
        # First 100 units: 100 * (20.0 - 3.0/150.0 - 10.05) = 100 * (19.98 - 10.05) = 993.0
        # Next 50 units: 50 * (20.0 - 3.0/150.0 - 12.02) = 50 * (19.98 - 12.02) = 398.0
        expected_capital_gain = 993.0 + 398.0
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert sale_proceeds == pytest.approx(150.0 * (20.0 - 3.0/150.0), rel=1e-6)
        assert brokerage_fee == 3.0
        
        # Verify FIFO queue was updated
        assert len(fifo_queue) == 1
        assert fifo_queue[0].units == 50.0  # 100 - 50 from second purchase
    
    def test_calculate_capital_gains_for_sale_insufficient_units(self):
        """Test capital gains calculation when there aren't enough units in FIFO."""
        # Setup
        sale_event = MockFundEvent(
            event_date=date(2023, 2, 1),
            event_type=EventType.UNIT_SALE,
            units_sold=150.0,  # More than available
            unit_price=15.0,
            brokerage_fee=2.0
        )
        
        fifo_queue = deque([
            FifoUnit(units=100.0, unit_price=10.0, effective_price=10.05, 
                    purchase_date=date(2023, 1, 1), brokerage_fee=5.0)
        ])
        
        # Execute
        capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue, tax_jurisdiction=None
        )
        
        # Verify - should only process available units
        expected_capital_gain = 100.0 * (15.0 - 2.0/150.0 - 10.05)  # Only 100 units available
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert sale_proceeds == pytest.approx(100.0 * (15.0 - 2.0/150.0), rel=1e-6)
        assert brokerage_fee == 2.0
        
        # Verify FIFO queue is empty
        assert len(fifo_queue) == 0
    
    def test_calculate_capital_gains_complete_workflow(self):
        """Test complete capital gains calculation workflow."""
        # Setup - Multiple purchases and sales
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=75.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 4, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify
        assert isinstance(result, CapitalGainResult)
        assert result.units_sold == 125.0  # 75 + 50
        assert result.brokerage_fees_paid == 4.0  # 3 + 1
        assert result.capital_gains_total > 0  # Should have positive gains
        assert result.remaining_units == 25.0  # 150 - 125
    
    def test_calculate_capital_gains_no_events(self):
        """Test capital gains calculation with no events."""
        # Setup
        events = []
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify
        assert result.capital_gains_total == 0.0
        assert result.units_sold == 0.0
        assert result.brokerage_fees_paid == 0.0
        assert result.remaining_units == 0.0
    
    def test_calculate_capital_gains_purchases_only(self):
        """Test capital gains calculation with only purchases."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            )
        ]
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify
        assert result.capital_gains_total == 0.0  # No sales
        assert result.units_sold == 0.0
        assert result.brokerage_fees_paid == 0.0
        assert result.remaining_units == 100.0
    
    def test_build_fifo_queue(self):
        """Test building FIFO queue from events."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,  # Should be ignored
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            )
        ]
        
        # Execute
        fifo_units = FifoCapitalGainsCalculator.build_fifo_queue(events)
        
        # Verify
        assert len(fifo_units) == 2  # Only purchases
        assert fifo_units[0].units == 100.0
        assert fifo_units[0].unit_price == 10.0
        assert fifo_units[1].units == 50.0
        assert fifo_units[1].unit_price == 12.0
    
    def test_calculate_remaining_units_after_sales(self):
        """Test calculating remaining units after processing sales."""
        # Setup
        purchase_events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            )
        ]
        
        sale_events = [
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=75.0,
                unit_price=15.0,
                brokerage_fee=3.0
            )
        ]
        
        # Execute
        remaining_units = FifoCapitalGainsCalculator.calculate_remaining_units_after_sales(
            purchase_events, sale_events
        )
        
        # Verify
        assert len(remaining_units) == 2  # 25 from first purchase + 50 from second
        assert remaining_units[0].units == 25.0  # 100 - 75
        assert remaining_units[1].units == 50.0  # Unchanged
    
    def test_validate_events_valid(self):
        """Test event validation with valid events."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            )
        ]
        
        # Execute
        errors = FifoCapitalGainsCalculator.validate_events(events)
        
        # Verify
        assert len(errors) == 0
    
    def test_validate_events_invalid(self):
        """Test event validation with invalid events."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=0.0,  # Invalid
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=0.0,  # Invalid
                brokerage_fee=3.0
            )
        ]
        
        # Execute
        errors = FifoCapitalGainsCalculator.validate_events(events)
        
        # Verify
        assert len(errors) == 2
        assert "units_purchased must be positive" in errors[0]
        assert "unit_price must be positive" in errors[1]
    
    def test_calculate_capital_gains_with_distribution_events(self):
        """Test capital gains calculation with non-unit events (should be ignored)."""
        # Setup - Include distribution events that should be ignored
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.DISTRIBUTION,  # Should be ignored
                amount=1000.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            )
        ]
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify
        assert result.units_sold == 50.0  # Only the sale
        assert result.capital_gains_total > 0
        assert result.remaining_units == 50.0  # 100 - 50
    
    def test_calculate_capital_gains_chronological_order(self):
        """Test that events are processed in chronological order."""
        # Setup - Events out of chronological order
        events = [
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            )
        ]
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify - Should work correctly despite out-of-order input
        assert result.units_sold == 50.0
        assert result.capital_gains_total > 0
        assert result.remaining_units == 100.0  # 150 - 50

    def test_calculate_capital_gains_with_cg_start_date_filtering(self):
        """Test capital gains calculation with cg_start_date filtering."""
        # Setup - Multiple purchases and sales across different dates
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 4, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=25.0,
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with start date filter (should exclude the first sale on 2023-02-01)
        cg_start_date = date(2023, 3, 1)
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, cg_start_date=cg_start_date)
        
        # Verify - Only the sale on 2023-04-01 should be included
        assert result.units_sold == 25.0  # Only the second sale
        assert result.brokerage_fees_paid == 1.0  # Only the second sale's brokerage
        assert result.capital_gains_total > 0  # Should have positive gains from the second sale
        assert result.remaining_units == 75.0  # 100 - 50 (first sale) + 50 - 25 (second sale) = 75 (FIFO processes all sales)

    def test_calculate_capital_gains_with_cg_end_date_filtering(self):
        """Test capital gains calculation with cg_end_date filtering."""
        # Setup - Multiple purchases and sales across different dates
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 4, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=25.0,
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with end date filter (should exclude the sale on 2023-04-01)
        cg_end_date = date(2023, 2, 28)
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, cg_end_date=cg_end_date)
        
        # Verify - Only the sale on 2023-02-01 should be included
        assert result.units_sold == 50.0  # Only the first sale
        assert result.brokerage_fees_paid == 2.0  # Only the first sale's brokerage
        assert result.capital_gains_total > 0  # Should have positive gains from the first sale
        assert result.remaining_units == 75.0  # 100 - 50 (first sale) + 50 - 25 (second sale) = 75 (FIFO processes all sales)

    def test_calculate_capital_gains_with_date_range_filtering(self):
        """Test capital gains calculation with both start and end date filtering."""
        # Setup - Multiple purchases and sales across different dates
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=30.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 15),
                event_type=EventType.UNIT_SALE,
                units_sold=20.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2023, 4, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=18.0,
                brokerage_fee=4.0
            ),
            MockFundEvent(
                event_date=date(2023, 5, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=25.0,
                unit_price=20.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with date range filter (only March 2023 sales should be included)
        cg_start_date = date(2023, 3, 1)
        cg_end_date = date(2023, 3, 31)
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, cg_start_date=cg_start_date, cg_end_date=cg_end_date)
        
        # Verify - Only the sale on 2023-03-15 should be included
        assert result.units_sold == 20.0  # Only the March sale
        assert result.brokerage_fees_paid == 3.0  # Only the March sale's brokerage
        assert result.capital_gains_total > 0  # Should have positive gains from the March sale
        # Remaining units account for all purchases and all sales (FIFO processes all events)
        assert result.remaining_units == 75.0  # 100 - 30 - 20 + 50 - 25 = 75

    def test_calculate_capital_gains_date_filtering_edge_cases(self):
        """Test date filtering edge cases - exact boundary dates."""
        # Setup - Events on specific dates
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 15),  # Exact start date
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 3, 15),  # Exact end date
                event_type=EventType.UNIT_SALE,
                units_sold=25.0,
                unit_price=15.0,
                brokerage_fee=3.0
            )
        ]
        
        # Execute with exact boundary dates
        cg_start_date = date(2023, 2, 15)
        cg_end_date = date(2023, 3, 15)
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, cg_start_date=cg_start_date, cg_end_date=cg_end_date)
        
        # Verify - Both boundary sales should be included (inclusive boundaries)
        assert result.units_sold == 75.0  # 50 + 25
        assert result.brokerage_fees_paid == 5.0  # 2 + 3
        assert result.capital_gains_total > 0  # Should have positive gains
        assert result.remaining_units == 25.0  # 100 - 50 - 25

    def test_calculate_capital_gains_date_filtering_no_matching_sales(self):
        """Test date filtering when no sales fall within the date range."""
        # Setup - Events with sales outside the filter range
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 4, 1),
                event_type=EventType.UNIT_SALE,
                units_sold=25.0,
                unit_price=15.0,
                brokerage_fee=3.0
            )
        ]
        
        # Execute with date range that excludes all sales
        cg_start_date = date(2023, 3, 1)
        cg_end_date = date(2023, 3, 31)
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, cg_start_date=cg_start_date, cg_end_date=cg_end_date)
        
        # Verify - No sales should be included
        assert result.units_sold == 0.0  # No sales in date range
        assert result.brokerage_fees_paid == 0.0  # No sales in date range
        assert result.capital_gains_total == 0.0  # No sales in date range
        assert result.remaining_units == 25.0  # 100 - 50 - 25 = 25 (FIFO processes all sales)


class TestFifoUnit:
    """Test cases for FifoUnit dataclass."""
    
    def test_fifo_unit_creation(self):
        """Test FifoUnit creation."""
        # Setup
        fifo_unit = FifoUnit(
            units=100.0,
            unit_price=10.0,
            effective_price=10.05,
            purchase_date=date(2023, 1, 1),
            brokerage_fee=5.0
        )
        
        # Verify
        assert fifo_unit.units == 100.0
        assert fifo_unit.unit_price == 10.0
        assert fifo_unit.effective_price == 10.05
        assert fifo_unit.purchase_date == date(2023, 1, 1)
        assert fifo_unit.brokerage_fee == 5.0


class TestCapitalGainResult:
    """Test cases for CapitalGainResult dataclass."""
    
    def test_capital_gain_result_creation(self):
        """Test CapitalGainResult creation."""
        # Setup
        result = CapitalGainResult(
            capital_gains_total=1000.0,
            capital_gains_discounting_total=500.0,
            capital_gains_discounting_taxable_total=250.0,
            capital_gains_taxable_total=750.0,
            units_sold=100.0,
            average_cost_per_unit=10.0,
            average_sale_price_per_unit=15.0,
            brokerage_fees_paid=50.0,
            remaining_units=25.0,
            sale_details=[],
            tax_jurisdiction=Country.AU
        )
        
        # Verify
        assert result.capital_gains_total == 1000.0
        assert result.capital_gains_discounting_total == 500.0
        assert result.capital_gains_discounting_taxable_total == 250.0
        assert result.capital_gains_taxable_total == 750.0
        assert result.units_sold == 100.0
        assert result.average_cost_per_unit == 10.0
        assert result.average_sale_price_per_unit == 15.0
        assert result.brokerage_fees_paid == 50.0
        assert result.remaining_units == 25.0
        assert result.sale_details == []
        assert result.tax_jurisdiction == Country.AU


class TestFifoCapitalGainsDiscount:
    """Test cases for Australian capital gains discount functionality."""
    
    def test_calculate_holding_period_days(self):
        """Test holding period calculation."""
        # Test normal case
        purchase_date = date(2023, 1, 1)
        sale_date = date(2023, 2, 1)
        holding_period = FifoCapitalGainsCalculator.calculate_holding_period_days(purchase_date, sale_date)
        assert holding_period == 31
        
        # Test exactly 365 days (should NOT qualify for discount)
        sale_date_365 = date(2024, 1, 1)  # Exactly 365 days later
        holding_period_365 = FifoCapitalGainsCalculator.calculate_holding_period_days(purchase_date, sale_date_365)
        assert holding_period_365 == 365
        
        # Test 366 days (should qualify for discount)
        sale_date_366 = date(2024, 1, 2)  # 366 days later
        holding_period_366 = FifoCapitalGainsCalculator.calculate_holding_period_days(purchase_date, sale_date_366)
        assert holding_period_366 == 366
        
        # Test leap year
        purchase_date_leap = date(2020, 2, 29)  # Leap year
        sale_date_leap = date(2021, 2, 28)
        holding_period_leap = FifoCapitalGainsCalculator.calculate_holding_period_days(purchase_date_leap, sale_date_leap)
        assert holding_period_leap == 365  # Should still be 365 days
    
    def test_calculate_holding_period_days_invalid(self):
        """Test holding period calculation with invalid dates."""
        purchase_date = date(2023, 2, 1)
        sale_date = date(2023, 1, 1)  # Before purchase
        
        with pytest.raises(ValueError, match="Sale date cannot be before purchase date"):
            FifoCapitalGainsCalculator.calculate_holding_period_days(purchase_date, sale_date)
    
    def test_qualifies_for_australian_discount(self):
        """Test Australian discount qualification logic."""
        # Test exactly 365 days (should NOT qualify)
        assert FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(365, Country.AU) == False
        
        # Test 366 days (should qualify)
        assert FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(366, Country.AU) == True
        
        # Test 400 days (should qualify)
        assert FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(400, Country.AU) == True
        
        # Test less than 365 days (should NOT qualify)
        assert FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(364, Country.AU) == False
        assert FifoCapitalGainsCalculator.qualifies_for_capital_gains_discount(30, Country.AU) == False
    
    def test_calculate_discounted_capital_gain(self):
        """Test discounted capital gain calculation."""
        # Test Australian jurisdiction with positive gain
        capital_gain = 1000.0
        discounted_gain = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(capital_gain, Country.AU)
        assert discounted_gain == 500.0  # 50% discount
        
        # Test non-Australian jurisdiction
        discounted_gain_non_au = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(capital_gain, Country.US)
        assert discounted_gain_non_au == 1000.0  # No discount
        
        # Test None jurisdiction
        discounted_gain_none = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(capital_gain, None)
        assert discounted_gain_none == 1000.0  # No discount
        
        # Test zero gain
        discounted_gain_zero = FifoCapitalGainsCalculator.calculate_discounted_capital_gain(0.0, Country.AU)
        assert discounted_gain_zero == 0.0  # No change for zero
    
    def test_calculate_capital_gains_for_sale_with_discount_qualified(self):
        """Test capital gains calculation with Australian discount applied."""
        # Setup - Sale after 13 months (qualified for discount)
        sale_event = MockFundEvent(
            event_date=date(2024, 2, 15),  # 13+ months after purchase
            event_type=EventType.UNIT_SALE,
            units_sold=50.0,
            unit_price=15.0,
            brokerage_fee=2.0
        )
        
        fifo_queue = deque([
            FifoUnit(
                units=100.0,
                unit_price=10.0,
                effective_price=10.05,
                purchase_date=date(2023, 1, 1),  # Purchase date
                brokerage_fee=5.0
            )
        ])
        
        # Execute with Australian tax jurisdiction
        capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue, tax_jurisdiction=Country.AU
        )
        
        # Verify
        expected_capital_gain = 50.0 * (15.0 - 2.0/50.0 - 10.05)  # 50 * (14.96 - 10.05) = 245.5
        expected_discounted_gain = expected_capital_gain * 0.5  # 50% discount
        
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert discountable_capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)  # Full amount qualifies for discount
        assert sale_proceeds == pytest.approx(50.0 * (15.0 - 2.0/50.0), rel=1e-6)
        assert brokerage_fee == 2.0
        assert avg_holding_period_days == 410.0  # 410 days from Jan 1, 2023 to Feb 15, 2024
        assert qualified_for_discount == True
    
    def test_calculate_capital_gains_for_sale_with_discount_not_qualified(self):
        """Test capital gains calculation with Australian discount NOT applied (insufficient holding period)."""
        # Setup - Sale after 11 months (NOT qualified for discount)
        sale_event = MockFundEvent(
            event_date=date(2023, 12, 1),  # 11 months after purchase
            event_type=EventType.UNIT_SALE,
            units_sold=50.0,
            unit_price=15.0,
            brokerage_fee=2.0
        )
        
        fifo_queue = deque([
            FifoUnit(
                units=100.0,
                unit_price=10.0,
                effective_price=10.05,
                purchase_date=date(2023, 1, 1),
                brokerage_fee=5.0
            )
        ])
        
        # Execute with Australian tax jurisdiction
        capital_gain, sale_proceeds, brokerage_fee, avg_holding_period_days, qualified_for_discount, discountable_capital_gain = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue, tax_jurisdiction=Country.AU
        )
        
        # Verify
        expected_capital_gain = 50.0 * (15.0 - 2.0/50.0 - 10.05)  # 50 * (14.96 - 10.05) = 245.5
        
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert discountable_capital_gain == pytest.approx(0.0, rel=1e-6)  # No discount applied
        assert sale_proceeds == pytest.approx(50.0 * (15.0 - 2.0/50.0), rel=1e-6)
        assert brokerage_fee == 2.0
        assert avg_holding_period_days == 334.0  # 334 days from Jan 1 to Dec 1
        assert qualified_for_discount == False  # Less than 365 days
    
    def test_calculate_capital_gains_complete_workflow_with_discount(self):
        """Test complete capital gains calculation workflow with Australian discount."""
        # Setup - Multiple purchases and sales with mixed holding periods
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 2, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2023, 6, 1),  # 5 months - no discount
                event_type=EventType.UNIT_SALE,
                units_sold=30.0,
                unit_price=15.0,
                brokerage_fee=3.0
            ),
            MockFundEvent(
                event_date=date(2024, 2, 15),  # 13+ months - qualified for discount
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with Australian tax jurisdiction
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, tax_jurisdiction=Country.AU)
        
        # Verify
        assert isinstance(result, CapitalGainResult)
        assert result.units_sold == 80.0  # 30 + 50
        assert result.brokerage_fees_paid == 4.0  # 3 + 1
        assert result.capital_gains_total > 0
        assert result.capital_gains_taxable_total < result.capital_gains_total  # Discount applied
        assert result.remaining_units == 70.0  # 150 - 80
        assert result.tax_jurisdiction == Country.AU
        assert len(result.sale_details) == 2  # Two sales
        
        # Verify sale details
        first_sale = result.sale_details[0]  # June sale
        assert first_sale.qualified_for_discount == False
        assert first_sale.units_sold == 30.0
        
        second_sale = result.sale_details[1]  # February sale
        assert second_sale.qualified_for_discount == True
        assert second_sale.units_sold == 50.0
        assert second_sale.discounted_capital_gain < second_sale.capital_gain
    
    def test_calculate_capital_gains_multiple_purchases_mixed_discount(self):
        """Test capital gains calculation with multiple purchases where some qualify for discount."""
        # Setup - Complex scenario with multiple purchases and sales
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2023, 6, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=2.0
            ),
            MockFundEvent(
                event_date=date(2024, 2, 15),  # Sale that spans both purchases
                event_type=EventType.UNIT_SALE,
                units_sold=75.0,  # 75 units sold (50 from first purchase + 25 from second)
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with Australian tax jurisdiction
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, tax_jurisdiction=Country.AU)
        
        # Verify
        assert result.units_sold == 75.0
        assert len(result.sale_details) == 1
        
        sale_detail = result.sale_details[0]
        # The sale spans both purchases - first 50 units qualify for discount (410+ days),
        # next 25 units do not qualify (260+ days)
        # So the overall sale should have mixed qualification
        assert sale_detail.qualified_for_discount == True  # At least some units qualified
        assert sale_detail.units_sold == 75.0
        assert sale_detail.discounted_capital_gain < sale_detail.capital_gain  # Some discount applied
    
    def test_calculate_capital_gains_non_australian_jurisdiction(self):
        """Test capital gains calculation with non-Australian tax jurisdiction."""
        # Setup
        events = [
            MockFundEvent(
                event_date=date(2023, 1, 1),
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_date=date(2024, 2, 15),  # 13+ months - would qualify for AU discount
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=18.0,
                brokerage_fee=1.0
            )
        ]
        
        # Execute with US tax jurisdiction
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events, tax_jurisdiction=Country.US)
        
        # Verify - No discount should be applied
        assert result.capital_gains_total == result.capital_gains_taxable_total  # No discount
        assert result.tax_jurisdiction == Country.US
        assert len(result.sale_details) == 1
        
        sale_detail = result.sale_details[0]
        assert sale_detail.qualified_for_discount == False  # No discount for US
        assert sale_detail.discounted_capital_gain == sale_detail.capital_gain  # No discount applied


class TestCapitalGainSaleDetail:
    """Test cases for CapitalGainSaleDetail dataclass."""
    
    def test_capital_gain_sale_detail_creation(self):
        """Test CapitalGainSaleDetail creation."""
        # Setup
        sale_detail = CapitalGainSaleDetail(
            sale_date=date(2023, 2, 1),
            units_sold=50.0,
            capital_gain=245.5,
            discounted_capital_gain=122.75,
            holding_period_days=31.0,
            qualified_for_discount=False
        )
        
        # Verify
        assert sale_detail.sale_date == date(2023, 2, 1)
        assert sale_detail.units_sold == 50.0
        assert sale_detail.capital_gain == 245.5
        assert sale_detail.discounted_capital_gain == 122.75
        assert sale_detail.holding_period_days == 31.0
        assert sale_detail.qualified_for_discount == False
