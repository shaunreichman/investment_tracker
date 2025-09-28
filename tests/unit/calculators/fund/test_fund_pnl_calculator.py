"""
Tests for FundPnlCalculator.

Tests the PNL calculation logic for both NAV-based and cost-based funds,
including capital gains, distributions, and various edge cases.
"""

import pytest
from datetime import date
from dataclasses import dataclass
from typing import List, Optional
from unittest.mock import Mock, patch

from src.fund.calculators.fund_pnl_calculator import FundPnlCalculator
from src.fund.models.fund_event import FundEvent
from src.fund.models.fund import Fund
from src.fund.enums.fund_enums import FundTrackingType
from src.fund.enums.fund_event_enums import EventType, DistributionType
from src.shared.enums.shared_enums import Currency, Country


@dataclass
class MockFund:
    """Mock fund for testing."""
    id: int = 1
    tracking_type: FundTrackingType = FundTrackingType.NAV_BASED
    current_units: float = 1000.0
    current_unit_price: float = 1.50


@dataclass
class MockFundEvent:
    """Mock fund event for testing."""
    id: int = 1
    fund_id: int = 1
    event_type: EventType = EventType.CAPITAL_CALL
    event_date: date = date(2023, 1, 1)
    amount: float = 1000.0
    distribution_type: Optional[DistributionType] = None
    units_purchased: Optional[float] = None
    units_sold: Optional[float] = None
    unit_price: Optional[float] = None
    brokerage_fee: Optional[float] = None


class TestFundPnlCalculator:
    """Test cases for FundPnlCalculator."""
    
    def test_initialization(self):
        """Test calculator initialization."""
        calculator = FundPnlCalculator()
        assert calculator.fund_event_repository is not None
    
    def test_calculate_pnl_nav_based_fund_basic(self):
        """Test PNL calculation for NAV-based fund with basic scenario."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=1000.0,
            current_unit_price=1.50
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00,
                brokerage_fee=10.0
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 6, 1),
                units_sold=200.0,
                unit_price=1.20,
                brokerage_fee=5.0
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 1000.0  # Match fund.current_units
            mock_result.total_capital_gains = 40.0  # 200 units * (1.20 - 1.01) = 38, plus some rounding
            mock_result.average_cost_per_unit = 1.01
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            result = calculator.calculate_pnl(events, fund)
            
            # Verify
            assert isinstance(result, dict)
            assert 'pnl' in result
            assert 'realized_pnl' in result
            assert 'unrealized_pnl' in result
            assert 'realized_pnl_capital_gain' in result
            assert 'unrealized_pnl_capital_gain' in result
            assert 'realized_pnl_dividend' in result
            assert 'realized_pnl_interest' in result
            assert 'realized_pnl_distribution' in result
            
            # Check that FIFO calculator was called
            mock_calc.return_value.calculate_capital_gains.assert_called_once_with(events)
    
    def test_calculate_pnl_nav_based_fund_with_distributions(self):
        """Test PNL calculation for NAV-based fund with distributions."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=1000.0,
            current_unit_price=1.50
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 6, 1),
                amount=50.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 12, 1),
                amount=30.0,
                distribution_type=DistributionType.INTEREST
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 1000.0
            mock_result.total_capital_gains = 0.0
            mock_result.average_cost_per_unit = 1.00
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            result = calculator.calculate_pnl(events, fund)
            
            # Verify
            assert result['realized_pnl_dividend'] == 50.0
            assert result['realized_pnl_interest'] == 30.0
            assert result['realized_pnl_distribution'] == 80.0  # 50 + 30
            assert result['realized_pnl'] == 80.0  # Only distributions, no capital gains
            assert result['unrealized_pnl'] == 500.0  # 1000 * (1.50 - 1.00)
            assert result['pnl'] == 580.0  # 80 + 500
    
    def test_calculate_pnl_cost_based_fund(self):
        """Test PNL calculation for cost-based fund."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.COST_BASED,
            current_units=0.0,  # Cost-based funds don't use units
            current_unit_price=0.0
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=1000.0
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 6, 1),
                amount=50.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            )
        ]
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert result['realized_pnl_capital_gain'] is None
        assert result['unrealized_pnl_capital_gain'] is None
        assert result['realized_pnl_dividend'] == 50.0
        assert result['realized_pnl_interest'] == 0.0
        assert result['realized_pnl_distribution'] == 50.0
        assert result['realized_pnl'] == 50.0
        assert result['unrealized_pnl'] == 0.0  # No unrealized PNL for cost-based
        assert result['pnl'] == 50.0
    
    def test_calculate_pnl_empty_events(self):
        """Test PNL calculation with empty events list."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)  # Use cost-based to get None values
        events = []
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert result['pnl'] == 0.0
        assert result['realized_pnl'] == 0.0
        assert result['unrealized_pnl'] == 0.0
        assert result['realized_pnl_capital_gain'] is None
        assert result['unrealized_pnl_capital_gain'] is None
        assert result['realized_pnl_dividend'] == 0.0
        assert result['realized_pnl_interest'] == 0.0
        assert result['realized_pnl_distribution'] == 0.0
    
    def test_calculate_pnl_different_distribution_types(self):
        """Test PNL calculation with different distribution types."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        
        events = [
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 1, 1),
                amount=100.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 2, 1),
                amount=50.0,
                distribution_type=DistributionType.DIVIDEND_UNFRANKED
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 3, 1),
                amount=75.0,
                distribution_type=DistributionType.INTEREST
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 4, 1),
                amount=25.0,
                distribution_type=DistributionType.CAPITAL_GAIN
            )
        ]
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert result['realized_pnl_dividend'] == 150.0  # 100 + 50
        assert result['realized_pnl_interest'] == 75.0
        assert result['realized_pnl_distribution'] == 225.0  # 150 + 75
        # Note: CAPITAL_GAIN distributions are not counted in dividend/interest categories
    
    def test_calculate_pnl_nav_based_units_mismatch_error(self):
        """Test PNL calculation raises error when remaining units don't match current units."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=1000.0,
            current_unit_price=1.50
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator to return mismatched units
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 800.0  # Different from fund.current_units
            mock_result.total_capital_gains = 0.0
            mock_result.average_cost_per_unit = 1.00
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            
            # Verify that ValueError is raised
            with pytest.raises(ValueError, match="Remaining units do not match current units"):
                calculator.calculate_pnl(events, fund)
    
    def test_calculate_pnl_nav_based_complex_scenario(self):
        """Test PNL calculation with complex NAV-based scenario."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=500.0,
            current_unit_price=2.00
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00,
                brokerage_fee=10.0
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 6, 1),
                units_sold=200.0,
                unit_price=1.50,
                brokerage_fee=5.0
            ),
            MockFundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2023, 9, 1),
                units_sold=300.0,
                unit_price=1.80,
                brokerage_fee=8.0
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 12, 1),
                amount=100.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 500.0  # Matches fund.current_units
            mock_result.total_capital_gains = 200.0  # Total from both sales
            mock_result.average_cost_per_unit = 1.01  # Average cost per unit
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            result = calculator.calculate_pnl(events, fund)
            
            # Verify
            assert result['realized_pnl_capital_gain'] == 200.0
            assert result['unrealized_pnl_capital_gain'] == 495.0  # 500 * (2.00 - 1.01)
            assert result['realized_pnl_dividend'] == 100.0
            assert result['realized_pnl_interest'] == 0.0
            assert result['realized_pnl_distribution'] == 100.0
            assert result['realized_pnl'] == 300.0  # 200 + 100
            assert result['unrealized_pnl'] == 495.0
            assert result['pnl'] == 795.0  # 300 + 495
    
    def test_calculate_pnl_no_distributions(self):
        """Test PNL calculation with no distribution events."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        
        events = [
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2023, 1, 1),
                amount=1000.0
            )
        ]
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert result['realized_pnl_dividend'] == 0.0
        assert result['realized_pnl_interest'] == 0.0
        assert result['realized_pnl_distribution'] == 0.0
        assert result['realized_pnl'] == 0.0
        assert result['unrealized_pnl'] == 0.0
        assert result['pnl'] == 0.0
    
    def test_calculate_pnl_mixed_distribution_types(self):
        """Test PNL calculation with mixed distribution types."""
        # Setup
        fund = MockFund(tracking_type=FundTrackingType.COST_BASED)
        
        events = [
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 1, 1),
                amount=100.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 2, 1),
                amount=50.0,
                distribution_type=DistributionType.DIVIDEND_UNFRANKED
            ),
            MockFundEvent(
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 3, 1),
                amount=75.0,
                distribution_type=DistributionType.INTEREST
            ),
            MockFundEvent(
                event_type=EventType.CAPITAL_CALL,  # Non-distribution event
                event_date=date(2023, 4, 1),
                amount=200.0
            )
        ]
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert result['realized_pnl_dividend'] == 150.0  # 100 + 50
        assert result['realized_pnl_interest'] == 75.0
        assert result['realized_pnl_distribution'] == 225.0  # 150 + 75
        assert result['realized_pnl'] == 225.0
        assert result['unrealized_pnl'] == 0.0
        assert result['pnl'] == 225.0
    
    def test_calculate_pnl_nav_based_no_capital_gains(self):
        """Test PNL calculation for NAV-based fund with no capital gains."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=1000.0,
            current_unit_price=1.00
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 1000.0
            mock_result.total_capital_gains = 0.0
            mock_result.average_cost_per_unit = 1.00
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            result = calculator.calculate_pnl(events, fund)
            
            # Verify
            assert result['realized_pnl_capital_gain'] == 0.0
            assert result['unrealized_pnl_capital_gain'] == 0.0  # 1000 * (1.00 - 1.00)
            assert result['realized_pnl'] == 0.0
            assert result['unrealized_pnl'] == 0.0
            assert result['pnl'] == 0.0
    
    def test_calculate_pnl_negative_unrealized_pnl(self):
        """Test PNL calculation with negative unrealized PNL."""
        # Setup
        fund = MockFund(
            tracking_type=FundTrackingType.NAV_BASED,
            current_units=1000.0,
            current_unit_price=0.80  # Lower than cost
        )
        
        events = [
            MockFundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2023, 1, 1),
                units_purchased=1000.0,
                unit_price=1.00
            )
        ]
        
        # Mock the FifoCapitalGainsCalculator
        with patch('src.fund.calculators.fund_pnl_calculator.FifoCapitalGainsCalculator') as mock_calc:
            mock_result = Mock()
            mock_result.remaining_units = 1000.0
            mock_result.total_capital_gains = 0.0
            mock_result.average_cost_per_unit = 1.00
            mock_calc.return_value.calculate_capital_gains.return_value = mock_result
            
            calculator = FundPnlCalculator()
            result = calculator.calculate_pnl(events, fund)
            
            # Verify
            assert result['unrealized_pnl_capital_gain'] == pytest.approx(-200.0, rel=1e-6)  # 1000 * (0.80 - 1.00)
            assert result['unrealized_pnl'] == pytest.approx(-200.0, rel=1e-6)
            assert result['pnl'] == pytest.approx(-200.0, rel=1e-6)
    
    def test_calculate_pnl_with_real_models(self):
        """Test PNL calculation using actual model instances."""
        # Setup - Create actual model instances
        fund = Fund(
            id=1,
            investment_company_id=1,
            entity_id=1,
            name="Test Fund",
            tracking_type=FundTrackingType.COST_BASED,
            currency=Currency.AUD,
            tax_jurisdiction=Country.AU
        )
        
        events = [
            FundEvent(
                fund_id=1,
                event_type=EventType.DISTRIBUTION,
                event_date=date(2023, 1, 1),
                amount=100.0,
                distribution_type=DistributionType.DIVIDEND_FRANKED
            )
        ]
        
        calculator = FundPnlCalculator()
        result = calculator.calculate_pnl(events, fund)
        
        # Verify
        assert isinstance(result, dict)
        assert result['realized_pnl_dividend'] == 100.0
        assert result['realized_pnl_distribution'] == 100.0
        assert result['realized_pnl'] == 100.0
        assert result['pnl'] == 100.0
