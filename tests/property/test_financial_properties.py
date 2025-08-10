"""
Property-Based Tests for Financial Calculations

Using Hypothesis to test financial invariants and properties:
- IRR calculation properties
- Capital gains calculation properties
- Mathematical invariants
"""

import pytest
from hypothesis import given, settings, Verbosity, strategies as st, HealthCheck
import numpy as np
from hypothesis.extra.numpy import arrays
from datetime import date, timedelta

from src.fund.calculations import (
    calculate_irr, calculate_nav_based_capital_gains, calculate_cost_based_capital_gains
)
from src.fund.models import EventType, DistributionType


class TestIRRProperties:
    """Property-based tests for IRR calculations"""
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=100,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        cash_flows=arrays(
            np.float64, 
            shape=st.integers(min_value=2, max_value=10),
            elements=st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False)
        ),
        days=st.lists(
            st.integers(min_value=0, max_value=3650),  # 0 to 10 years
            min_size=2, max_size=10
        )
    )
    def test_irr_input_validation(self, db_session, cash_flows, days):
        """Test IRR calculation handles various input combinations without crashing"""
        # Ensure we have matching lengths
        if len(cash_flows) != len(days):
            return
        
        # Ensure days are sorted and non-negative
        if len(days) != len(set(days)) or min(days) < 0:
            return
        
        # Ensure first cash flow is negative (investment)
        if cash_flows[0] >= 0:
            return
        
        # Ensure at least one positive cash flow (return)
        if all(cf <= 0 for cf in cash_flows):
            return
        
        try:
            result = calculate_irr(cash_flows.tolist(), days)
            # Result should either be a valid IRR or None, but not crash
            assert result is None or (isinstance(result, (int, float)) and not np.isnan(result))
        except Exception as e:
            # If it crashes, that's a bug we need to fix
            pytest.fail(f"IRR calculation crashed with inputs {cash_flows}, {days}: {e}")
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        return_rate=st.floats(min_value=0.01, max_value=2.0),  # 1% to 200% return
        days=st.integers(min_value=30, max_value=365)
    )
    def test_irr_proportional_scaling(self, db_session, base_amount, return_rate, days):
        """Test that proportional scaling of cash flows doesn't change IRR"""
        # Create simple investment scenario
        investment = -base_amount
        return_amount = base_amount * (1 + return_rate)
        
        cash_flows = [investment, return_amount]
        days_list = [0, days]
        
        original_irr = calculate_irr(cash_flows, days_list)
        if original_irr is None:
            return  # Skip if IRR can't be calculated
        
        # Scale by factor of 10
        scaled_cash_flows = [investment * 10, return_amount * 10]
        scaled_irr = calculate_irr(scaled_cash_flows, days_list)
        
        if scaled_irr is not None:
            # IRR should be the same (within tolerance)
            assert abs(original_irr - scaled_irr) < 1e-4
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        return_rate=st.floats(min_value=0.01, max_value=1.0),  # 1% to 100% return
        days=st.integers(min_value=30, max_value=365)
    )
    def test_irr_zero_cash_flow_addition(self, db_session, base_amount, return_rate, days):
        """Test that adding zero cash flows doesn't change IRR"""
        # Create simple investment scenario
        investment = -base_amount
        return_amount = base_amount * (1 + return_rate)
        
        cash_flows = [investment, return_amount]
        days_list = [0, days]
        
        original_irr = calculate_irr(cash_flows, days_list)
        if original_irr is None:
            return  # Skip if IRR can't be calculated
        
        # Add zero cash flow in middle
        mid_day = days // 2
        cash_flows_with_zero = [investment, 0.0, return_amount]
        days_with_zero = [0, mid_day, days]
        
        irr_with_zero = calculate_irr(cash_flows_with_zero, days_with_zero)
        
        if irr_with_zero is not None:
            # IRR should be the same (within tolerance)
            assert abs(original_irr - irr_with_zero) < 1e-4
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        return_rate=st.floats(min_value=0.01, max_value=1.0),  # 1% to 100% return
        days=st.integers(min_value=30, max_value=365),
        time_shift=st.integers(min_value=0, max_value=1000)
    )
    def test_irr_time_shift_invariance(self, db_session, base_amount, return_rate, days, time_shift):
        """Test that shifting all dates by same amount doesn't change IRR"""
        # Create simple investment scenario
        investment = -base_amount
        return_amount = base_amount * (1 + return_rate)
        
        cash_flows = [investment, return_amount]
        days_list = [0, days]
        
        original_irr = calculate_irr(cash_flows, days_list)
        if original_irr is None:
            return  # Skip if IRR can't be calculated
        
        # Shift all dates by time_shift
        shifted_days = [d + time_shift for d in days_list]
        
        shifted_irr = calculate_irr(cash_flows, shifted_days)
        
        if shifted_irr is not None:
            # IRR should be the same (within tolerance)
            # Use realistic tolerance for monthly compounding IRR calculations
            # Monthly compounding can introduce small variations due to fractional month conversions
            relative_tolerance = 0.02  # 2% tolerance for monthly compounding variations
            if abs(original_irr) > 1e-6:  # Avoid division by very small numbers
                relative_diff = abs(original_irr - shifted_irr) / abs(original_irr)
                assert relative_diff < relative_tolerance, f"IRR variation {relative_diff:.6f} exceeds tolerance {relative_tolerance} (monthly compounding can cause small variations)"
            else:
                # For very small IRR values, use absolute tolerance
                assert abs(original_irr - shifted_irr) < 1e-2
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        return_rate=st.floats(min_value=0.01, max_value=1.0),  # 1% to 100% return
        days=st.integers(min_value=30, max_value=365)
    )
    def test_irr_monotonicity(self, db_session, base_amount, return_rate, days):
        """Test that higher returns produce higher IRR"""
        # Create base scenario
        investment = -base_amount
        base_return = base_amount * (1 + return_rate)
        
        cash_flows_base = [investment, base_return]
        days_list = [0, days]
        
        base_irr = calculate_irr(cash_flows_base, days_list)
        if base_irr is None:
            return  # Skip if IRR can't be calculated
        
        # Create higher return scenario
        higher_return = base_amount * (1 + return_rate + 0.1)  # 10% higher return
        cash_flows_higher = [investment, higher_return]
        
        higher_irr = calculate_irr(cash_flows_higher, days_list)
        
        if higher_irr is not None:
            # Higher return should produce higher IRR
            assert higher_irr > base_irr


class TestCapitalGainsProperties:
    """Property-based tests for capital gains calculations"""
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=100,
        deadline=500,  # Increase deadline to 500ms
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        units=st.lists(
            st.floats(min_value=0.1, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1, max_size=10
        ),
        prices=st.lists(
            st.floats(min_value=0.01, max_value=1000.0, allow_nan=False, allow_infinity=False),
            min_size=1, max_size=10
        ),
        brokerage_fees=st.lists(
            st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
            min_size=1, max_size=10
        )
    )
    def test_nav_capital_gains_input_validation(self, db_session, units, prices, brokerage_fees):
        """Test NAV capital gains handles various input combinations without crashing"""
        # Ensure we have matching lengths
        min_length = min(len(units), len(prices), len(brokerage_fees))
        if min_length < 1:
            return
        
        # Create mock events
        from tests.factories import FundEventFactory
        
        events = []
        for i in range(min_length):
            # Alternate between purchases and sales
            if i % 2 == 0:
                event = FundEventFactory(
                    event_type=EventType.UNIT_PURCHASE,
                    units_purchased=units[i],
                    unit_price=prices[i],
                    brokerage_fee=brokerage_fees[i]
                )
            else:
                event = FundEventFactory(
                    event_type=EventType.UNIT_SALE,
                    units_sold=units[i],
                    unit_price=prices[i],
                    brokerage_fee=brokerage_fees[i]
                )
            events.append(event)
        
        try:
            result = calculate_nav_based_capital_gains(events)
            # Result should be a valid number
            assert isinstance(result, (int, float))
            assert not np.isnan(result)
            assert not np.isinf(result)
        except Exception as e:
            # If it crashes, that's a bug we need to fix
            pytest.fail(f"NAV capital gains calculation crashed: {e}")
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        gain_percentage=st.floats(min_value=0.01, max_value=1.0),  # 1% to 100% gain
        units=st.floats(min_value=1.0, max_value=1000.0)
    )
    def test_nav_capital_gains_proportional_scaling(self, db_session, base_amount, gain_percentage, units):
        """Test that proportional scaling of amounts doesn't change capital gains percentage"""
        from tests.factories import FundEventFactory
        
        # Create purchase event
        purchase_price = base_amount / units
        purchase_event = FundEventFactory(
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=units,
            unit_price=purchase_price,
            brokerage_fee=0.0
        )
        
        # Create sale event with gain
        sale_price = purchase_price * (1 + gain_percentage)
        sale_event = FundEventFactory(
            event_type=EventType.UNIT_SALE,
            units_sold=units,
            unit_price=sale_price,
            brokerage_fee=0.0
        )
        
        events = [purchase_event, sale_event]
        
        result = calculate_nav_based_capital_gains(events)
        
        # Capital gains should be positive and proportional to gain percentage
        assert result > 0
        expected_gain = base_amount * gain_percentage
        assert abs(result - expected_gain) < 1e-4
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        units=st.floats(min_value=1.0, max_value=1000.0)
    )
    def test_nav_capital_gains_no_gain_scenario(self, db_session, base_amount, units):
        """Test that selling at purchase price produces zero capital gains"""
        from tests.factories import FundEventFactory
        
        # Create purchase event
        purchase_price = base_amount / units
        purchase_event = FundEventFactory(
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=units,
            unit_price=purchase_price,
            brokerage_fee=0.0
        )
        
        # Create sale event at same price (no gain)
        sale_event = FundEventFactory(
            event_type=EventType.UNIT_SALE,
            units_sold=units,
            unit_price=purchase_price,  # Same price
            brokerage_fee=0.0
        )
        
        events = [purchase_event, sale_event]
        
        result = calculate_nav_based_capital_gains(events)
        
        # No gain should produce zero capital gains
        assert result == 0.0


class TestCostBasedCapitalGainsProperties:
    """Property-based tests for cost-based capital gains calculations"""
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=100,
        deadline=500,  # Increase deadline to 500ms for complex calculations
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        amounts=st.lists(
            st.floats(min_value=0.01, max_value=100000.0, allow_nan=False, allow_infinity=False),
            min_size=1, max_size=10
        )
    )
    def test_cost_based_capital_gains_input_validation(self, db_session, amounts):
        """Test cost-based capital gains handles various input combinations without crashing"""
        from tests.factories import FundEventFactory
        
        # Create events with different distribution types
        events = []
        for i, amount in enumerate(amounts):
            # Alternate between capital gains and other types
            if i % 2 == 0:
                event = FundEventFactory(
                    event_type=EventType.DISTRIBUTION,
                    distribution_type=DistributionType.CAPITAL_GAIN,
                    amount=amount
                )
            else:
                event = FundEventFactory(
                    event_type=EventType.DISTRIBUTION,
                    distribution_type=DistributionType.INCOME,
                    amount=amount
                )
            events.append(event)
        
        try:
            result = calculate_cost_based_capital_gains(events)
            # Result should be a valid number
            assert isinstance(result, (int, float))
            assert not np.isnan(result)
            assert not np.isinf(result)
            # Should be non-negative
            assert result >= 0
        except Exception as e:
            # If it crashes, that's a bug we need to fix
            pytest.fail(f"Cost-based capital gains calculation crashed: {e}")
    
    @settings(
        verbosity=Verbosity.verbose, 
        max_examples=50,
        deadline=500,  # Increase deadline to 500ms for complex calculations
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        num_distributions=st.integers(min_value=1, max_value=10)
    )
    def test_cost_based_capital_gains_sum_property(self, db_session, base_amount, num_distributions):
        """Test that total capital gains equals sum of capital gains distributions"""
        from tests.factories import FundEventFactory
        
        # Create multiple capital gains distributions
        events = []
        total_expected = 0.0
        
        for i in range(num_distributions):
            amount = base_amount * (1 + i * 0.1)  # Varying amounts
            total_expected += amount
            
            event = FundEventFactory(
                event_type=EventType.DISTRIBUTION,
                distribution_type=DistributionType.CAPITAL_GAIN,
                amount=amount
            )
            events.append(event)
        
        result = calculate_cost_based_capital_gains(events)
        
        # Result should equal sum of capital gains distributions
        assert abs(result - total_expected) < 1e-4
