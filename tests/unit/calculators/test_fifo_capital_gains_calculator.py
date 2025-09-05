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
    CapitalGainResult
)
from src.fund.enums import EventType


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
        capital_gain, sale_proceeds, brokerage_fee = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue
        )
        
        # Verify
        expected_capital_gain = 50.0 * (15.0 - 2.0/50.0 - 10.05)  # 50 * (14.96 - 10.05) = 245.5
        assert capital_gain == pytest.approx(expected_capital_gain, rel=1e-6)
        assert sale_proceeds == pytest.approx(50.0 * (15.0 - 2.0/50.0), rel=1e-6)
        assert brokerage_fee == 2.0
        
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
        capital_gain, sale_proceeds, brokerage_fee = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue
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
        capital_gain, sale_proceeds, brokerage_fee = FifoCapitalGainsCalculator.calculate_capital_gains_for_sale(
            sale_event, fifo_queue
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
        assert result.total_capital_gains > 0  # Should have positive gains
        assert result.remaining_units == 25.0  # 150 - 125
    
    def test_calculate_capital_gains_no_events(self):
        """Test capital gains calculation with no events."""
        # Setup
        events = []
        
        # Execute
        result = FifoCapitalGainsCalculator.calculate_capital_gains(events)
        
        # Verify
        assert result.total_capital_gains == 0.0
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
        assert result.total_capital_gains == 0.0  # No sales
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
        assert result.total_capital_gains > 0
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
        assert result.total_capital_gains > 0
        assert result.remaining_units == 100.0  # 150 - 50


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
            total_capital_gains=1000.0,
            units_sold=100.0,
            average_cost_per_unit=10.0,
            average_sale_price_per_unit=15.0,
            brokerage_fees_paid=50.0,
            remaining_units=25.0
        )
        
        # Verify
        assert result.total_capital_gains == 1000.0
        assert result.units_sold == 100.0
        assert result.average_cost_per_unit == 10.0
        assert result.average_sale_price_per_unit == 15.0
        assert result.brokerage_fees_paid == 50.0
        assert result.remaining_units == 25.0
