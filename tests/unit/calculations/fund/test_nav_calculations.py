"""
NAV Calculation Tests

This module tests NAV-based calculation functionality for funds,
including capital gains calculations and NAV-related business logic.

Following enterprise testing package spec patterns:
- Single responsibility: Focus ONLY on NAV-based calculations
- Comprehensive coverage: Test all NAV calculation scenarios
- Business value focus: Validate business outcomes, not just technical implementation
- Clear test organization: Group tests by calculation type and scenario
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from src.fund.calculations import calculate_nav_based_capital_gains
from src.fund.enums import EventType, FundType
from tests.factories import FundEventFactory, FundFactory


class TestNAVBasedCapitalGainsCalculations:
    """Tests for NAV-based capital gains calculations using FIFO method"""
    
    def test_nav_based_capital_gains_no_events(self):
        """Test NAV-based capital gains with no events"""
        events = []
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0
    
    def test_nav_based_capital_gains_only_purchases(self):
        """Test NAV-based capital gains with only purchase events"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=50.0,
                unit_price=12.0,
                brokerage_fee=25.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0  # No sales, so no capital gains
    
    def test_nav_based_capital_gains_simple_sale_profit(self):
        """Test NAV-based capital gains with simple profitable sale"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=25.0,
                event_date=date(2024, 3, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # Purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Sale: proceeds per unit = 15.0 - (25.0 / 50.0) = 14.5
        # Capital gain per unit = 14.5 - 10.5 = 4.0
        # Total capital gain = 50.0 * 4.0 = 200.0
        expected_gain = 200.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_simple_sale_loss(self):
        """Test NAV-based capital gains with simple loss-making sale"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=15.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=10.0,
                brokerage_fee=25.0,
                event_date=date(2024, 3, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # Purchase: cost per unit = 15.0 + (50.0 / 100.0) = 15.5
        # Sale: proceeds per unit = 10.0 - (25.0 / 50.0) = 9.5
        # Capital loss per unit = 9.5 - 15.5 = -6.0
        # Total capital loss = 50.0 * (-6.0) = -300.0
        expected_loss = -300.0
        assert abs(result - expected_loss) < 0.01
    
    def test_nav_based_capital_gains_fifo_ordering(self):
        """Test NAV-based capital gains with FIFO ordering (first in, first out)"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=12.0,
                brokerage_fee=50.0,
                event_date=date(2024, 2, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=150.0,
                unit_price=15.0,
                brokerage_fee=75.0,
                event_date=date(2024, 3, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # First purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Second purchase: cost per unit = 12.0 + (50.0 / 100.0) = 12.5
        # Sale: proceeds per unit = 15.0 - (75.0 / 150.0) = 14.5
        # First 100 units: gain = 100 * (14.5 - 10.5) = 400.0
        # Next 50 units: gain = 50 * (14.5 - 12.5) = 100.0
        # Total capital gain = 400.0 + 100.0 = 500.0
        expected_gain = 500.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_partial_fifo_consumption(self):
        """Test NAV-based capital gains with partial FIFO consumption"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=30.0,
                unit_price=15.0,
                brokerage_fee=15.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # Purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Sale: proceeds per unit = 15.0 - (15.0 / 30.0) = 14.5
        # Capital gain per unit = 14.5 - 10.5 = 4.0
        # Total capital gain = 30.0 * 4.0 = 120.0
        expected_gain = 120.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_multiple_sales_fifo(self):
        """Test NAV-based capital gains with multiple sales maintaining FIFO order"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=12.0,
                brokerage_fee=50.0,
                event_date=date(2024, 2, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=25.0,
                event_date=date(2024, 3, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=80.0,
                unit_price=16.0,
                brokerage_fee=40.0,
                event_date=date(2024, 4, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # First purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Second purchase: cost per unit = 12.0 + (50.0 / 100.0) = 12.5
        # First sale: proceeds per unit = 15.0 - (25.0 / 50.0) = 14.5
        # First sale gain = 50.0 * (14.5 - 10.5) = 200.0
        # Second sale: proceeds per unit = 16.0 - (40.0 / 80.0) = 15.5
        # Second sale: first 50 units from first purchase = 50.0 * (15.5 - 10.5) = 250.0
        # Second sale: next 30 units from second purchase = 30.0 * (15.5 - 12.5) = 90.0
        # Total capital gain = 200.0 + 250.0 + 90.0 = 540.0
        expected_gain = 540.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_zero_units_purchase(self):
        """Test NAV-based capital gains with zero units purchase"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=0.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0
    
    def test_nav_based_capital_gains_zero_units_sale(self):
        """Test NAV-based capital gains with zero units sale"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=0.0,
                unit_price=15.0,
                brokerage_fee=25.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0
    
    def test_nav_based_capital_gains_zero_unit_price_purchase(self):
        """Test NAV-based capital gains with zero unit price purchase"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=0.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0
    
    def test_nav_based_capital_gains_zero_unit_price_sale(self):
        """Test NAV-based capital gains with zero unit price sale"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=0.0,
                brokerage_fee=25.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        assert result == 0.0
    
    def test_nav_based_capital_gains_no_brokerage_fees(self):
        """Test NAV-based capital gains with no brokerage fees"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=0.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=0.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation:
        # Purchase: cost per unit = 10.0 + (0.0 / 100.0) = 10.0
        # Sale: proceeds per unit = 15.0 - (0.0 / 50.0) = 15.0
        # Capital gain per unit = 15.0 - 10.0 = 5.0
        # Total capital gain = 50.0 * 5.0 = 250.0
        expected_gain = 250.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_validation_enforcement(self):
        """Test that validation prevents negative brokerage fees from being processed"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        # Create events with valid brokerage fees
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,  # Valid positive brokerage
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=25.0,  # Valid positive brokerage
                event_date=date(2024, 2, 1)
            )
        ]
        
        # Validate all events before calculation
        for event in events:
            event.validate_basic_constraints()
        
        # Now calculate capital gains (should work with valid data)
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation with valid brokerage fees:
        # Purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Sale: proceeds per unit = 15.0 - (25.0 / 50.0) = 14.5
        # Capital gain per unit = 14.5 - 10.5 = 4.0
        # Total capital gain = 50.0 * 4.0 = 200.0
        expected_gain = 200.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_mixed_event_types(self):
        """Test NAV-based capital gains with mixed event types (only purchases/sales count)"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=1000.0,
                event_date=date(2024, 2, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=25.0,
                event_date=date(2024, 3, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=5000.0,
                event_date=date(2024, 4, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation: Only purchase and sale events count
        # Purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Sale: proceeds per unit = 15.0 - (25.0 / 50.0) = 14.5
        # Capital gain per unit = 14.5 - 10.5 = 4.0
        # Total capital gain = 50.0 * 4.0 = 200.0
        expected_gain = 200.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_high_precision_calculations(self):
        """Test NAV-based capital gains with high precision calculations"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.123,
                unit_price=10.456,
                brokerage_fee=50.789,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.456,
                unit_price=15.789,
                brokerage_fee=25.123,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation with high precision:
        # Purchase: cost per unit = 10.456 + (50.789 / 100.123) = 10.963
        # Sale: proceeds per unit = 15.789 - (25.123 / 50.456) = 15.291
        # Capital gain per unit = 15.291 - 10.963 = 4.328
        # Total capital gain = 50.456 * 4.328 = 218.364
        expected_gain = 218.364
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_edge_case_very_small_amounts(self):
        """Test NAV-based capital gains with very small amounts"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=0.001,
                unit_price=0.01,
                brokerage_fee=0.001,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=0.001,
                unit_price=0.02,
                brokerage_fee=0.001,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation with very small amounts:
        # Purchase: cost per unit = 0.01 + (0.001 / 0.001) = 1.01
        # Sale: proceeds per unit = 0.02 - (0.001 / 0.001) = -0.98
        # Capital loss per unit = -0.98 - 1.01 = -1.99
        # Total capital loss = 0.001 * (-1.99) = -0.00199
        expected_loss = -0.00199
        assert abs(result - expected_loss) < 0.00001


class TestNAVCalculationEdgeCases:
    """Tests for NAV calculation edge cases and boundary conditions"""
    
    def test_nav_based_capital_gains_insufficient_units_for_sale(self):
        """Test NAV-based capital gains when sale exceeds available units"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=50.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=150.0,  # More than available
                unit_price=15.0,
                brokerage_fee=75.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation: Only 100 units can be sold
        # Purchase: cost per unit = 10.0 + (50.0 / 100.0) = 10.5
        # Sale: proceeds per unit = 15.0 - (75.0 / 150.0) = 14.5
        # Capital gain per unit = 14.5 - 10.5 = 4.0
        # Total capital gain = 100.0 * 4.0 = 400.0
        expected_gain = 400.0
        assert abs(result - expected_gain) < 0.01
    
    def test_nav_based_capital_gains_negative_brokerage_fees_validation(self):
        """Test that negative brokerage fees are not allowed (validation should prevent this)"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        # Test that creating events with negative brokerage fees raises validation error
        with pytest.raises(ValueError, match="Brokerage fee cannot be negative"):
            event = FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=100.0,
                unit_price=10.0,
                brokerage_fee=-50.0,  # Negative brokerage should fail validation
                event_date=date(2024, 1, 1)
            )
            event.validate_basic_constraints()
        
        with pytest.raises(ValueError, match="Brokerage fee cannot be negative"):
            event = FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=50.0,
                unit_price=15.0,
                brokerage_fee=-25.0,  # Negative brokerage should fail validation
                event_date=date(2024, 2, 1)
            )
            event.validate_basic_constraints()
    
    def test_nav_based_capital_gains_very_large_numbers(self):
        """Test NAV-based capital gains with very large numbers"""
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=1000000.0,
                unit_price=1000000.0,
                brokerage_fee=50000.0,
                event_date=date(2024, 1, 1)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_SALE,
                units_sold=500000.0,
                unit_price=1100000.0,
                brokerage_fee=25000.0,
                event_date=date(2024, 2, 1)
            )
        ]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Expected calculation with large numbers:
        # Purchase: cost per unit = 1000000.0 + (50000.0 / 1000000.0) = 1000000.05
        # Sale: proceeds per unit = 1100000.0 - (25000.0 / 500000.0) = 1099999.95
        # Capital gain per unit = 1099999.95 - 1000000.05 = 99999.9
        # Total capital gain = 500000.0 * 99999.9 = 49999950000.0
        expected_gain = 49999950000.0
        assert abs(result - expected_gain) < 0.01
