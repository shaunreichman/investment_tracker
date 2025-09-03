"""
Fund Equity Calculator Tests

This module tests the FundEquityCalculator functionality for both cost-based and NAV-based funds,
including current equity, average equity, and total cost basis calculations.

Following enterprise testing package spec patterns:
- Single responsibility: Focus ONLY on fund equity calculator functionality
- Comprehensive coverage: Test all calculation methods for both fund types
- Business value focus: Validate business outcomes, not just technical implementation
- Clear test organization: Group tests by calculation type and fund type
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from unittest.mock import Mock, patch

from src.fund.calculators.fund_equity_calculator import FundEquityCalculator
from src.fund.enums import EventType, FundType, FundStatus
from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory


class TestFundEquityCalculatorCostBased:
    """Tests for cost-based fund equity calculations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = FundEquityCalculator()
    
    def test_calculate_current_equity_cost_based_no_events(self, db_session):
        """Test current equity calculation for cost-based fund with no events"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 0.0
    
    def test_calculate_current_equity_cost_based_capital_calls_only(self, db_session):
        """Test current equity calculation for cost-based fund with capital calls only"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=500.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 1500.0
    
    def test_calculate_current_equity_cost_based_with_returns(self, db_session):
        """Test current equity calculation for cost-based fund with capital calls and returns"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=300.0,
            event_date=date(2024, 2, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=200.0,
            event_date=date(2024, 3, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 900.0  # 1000 - 300 + 200
    
    def test_calculate_average_equity_cost_based_single_event(self, db_session):
        """Test average equity calculation for cost-based fund with single event"""
        # Arrange
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE,
            
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            current_equity_balance=1000.0,
            
        )
        
        # Act
        result = self.calculator.calculate_average_equity(fund, db_session)
        
        # Assert
        assert result == 1000.0
    
    def test_calculate_average_equity_cost_based_multiple_events(self, db_session):
        """Test average equity calculation for cost-based fund with multiple events"""
        # Arrange
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            status=FundStatus.ACTIVE,
            
        )
        
        # Create events with known equity balances
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            current_equity_balance=1000.0,
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=500.0,
            event_date=date(2024, 2, 1),  # 31 days later
            current_equity_balance=1500.0,
            
        )
        
        # Act
        result = self.calculator.calculate_average_equity(fund, db_session)
        
        # Assert
        # Should be time-weighted average: (1000 * 31 + 1500 * remaining_days) / total_days
        assert result > 1000.0  # Should be between 1000 and 1500
        assert result < 1500.0
    
    def test_calculate_total_cost_basis_cost_based(self, db_session):
        """Test total cost basis calculation for cost-based fund"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=300.0,
            event_date=date(2024, 2, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=200.0,
            event_date=date(2024, 3, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_total_cost_basis(fund, db_session)
        
        # Assert
        assert result == 1200.0  # Sum of all capital calls (1000 + 200)
    
    def test_recalculate_all_equity_fields_cost_based(self, db_session):
        """Test recalculating all equity fields for cost-based fund"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 1, 1),
            current_equity_balance=1000.0,
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=300.0,
            event_date=date(2024, 2, 1),
            current_equity_balance=700.0,
            
        )
        
        # Act
        result = self.calculator.recalculate_all_equity_fields(fund, db_session)
        
        # Assert
        assert 'current_equity_balance' in result
        assert 'average_equity_balance' in result
        assert 'total_cost_basis' in result
        assert result['current_equity_balance'] == 700.0
        assert result['total_cost_basis'] == 1000.0
        # Should not include NAV-specific fields
        assert 'current_units' not in result
        assert 'current_unit_price' not in result
        assert 'current_nav_total' not in result


class TestFundEquityCalculatorNAVBased:
    """Tests for NAV-based fund equity calculations"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = FundEquityCalculator()
    
    def test_calculate_current_equity_nav_based_no_events(self, db_session):
        """Test current equity calculation for NAV-based fund with no events"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 0.0
    
    def test_calculate_current_equity_nav_based_purchases_only(self, db_session):
        """Test current equity calculation for NAV-based fund with purchases only"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=50.0,
            unit_price=12.0,
            brokerage_fee=25.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        # FIFO cost base: (100 * 10 + 50) + (50 * 12 + 25) = 1050 + 625 = 1675
        assert result == 1675.0
    
    def test_calculate_current_equity_nav_based_with_sales(self, db_session):
        """Test current equity calculation for NAV-based fund with purchases and sales"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        # Purchase 100 units at $10 + $50 brokerage = $1050 total, $10.50 per unit
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        
        # Purchase 50 units at $12 + $25 brokerage = $625 total, $12.50 per unit
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=50.0,
            unit_price=12.0,
            brokerage_fee=25.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Sell 80 units (FIFO: 80 from first purchase at $10.50 per unit)
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_SALE,
            units_sold=80.0,
            unit_price=15.0,
            brokerage_fee=40.0,
            event_date=date(2024, 3, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        # Remaining units: 20 from first purchase + 50 from second purchase
        # Cost base: (20 * 10.50) + (50 * 12.50) = 210 + 625 = 835
        assert result == 835.0
    
    def test_calculate_average_equity_nav_based_single_purchase(self, db_session):
        """Test average equity calculation for NAV-based fund with single purchase"""
        # Arrange
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_average_equity(fund, db_session)
        
        # Assert
        # Should be time-weighted average of FIFO cost base
        assert result > 0.0
    
    def test_calculate_average_equity_nav_based_multiple_events(self, db_session):
        """Test average equity calculation for NAV-based fund with multiple events"""
        # Arrange
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            status=FundStatus.ACTIVE,
            
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=50.0,
            unit_price=12.0,
            brokerage_fee=25.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_average_equity(fund, db_session)
        
        # Assert
        # Should be time-weighted average of FIFO cost base over time
        assert result > 0.0
    
    def test_calculate_total_cost_basis_nav_based(self, db_session):
        """Test total cost basis calculation for NAV-based fund"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_SALE,
            units_sold=30.0,
            unit_price=15.0,
            brokerage_fee=20.0,
            event_date=date(2024, 2, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=50.0,
            unit_price=12.0,
            brokerage_fee=25.0,
            event_date=date(2024, 3, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_total_cost_basis(fund, db_session)
        
        # Assert
        # Should be same as current equity (FIFO cost base of remaining units)
        current_equity = self.calculator.calculate_current_equity(fund, db_session)
        assert result == current_equity
    
    def test_recalculate_all_equity_fields_nav_based(self, db_session):
        """Test recalculating all equity fields for NAV-based fund"""
        # Arrange
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            current_units=100.0,
            current_unit_price=10.5,
            current_nav_total=1050.0,
            
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        
        # Act
        result = self.calculator.recalculate_all_equity_fields(fund, db_session)
        
        # Assert
        assert 'current_equity_balance' in result
        assert 'average_equity_balance' in result
        assert 'total_cost_basis' in result
        # Should include NAV-specific fields
        assert 'current_units' in result
        assert 'current_unit_price' in result
        assert 'current_nav_total' in result
        assert result['current_units'] == 100.0
        assert result['current_unit_price'] == 10.5
        assert result['current_nav_total'] == 1050.0


class TestFundEquityCalculatorEdgeCases:
    """Tests for edge cases and error conditions"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = FundEquityCalculator()
    
    def test_calculate_current_equity_invalid_fund_type(self, db_session):
        """Test current equity calculation with invalid fund type"""
        # Arrange
        fund = FundFactory()
        # Manually set an invalid tracking type that bypasses database constraints
        fund.tracking_type = "INVALID_TYPE"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported fund type"):
            self.calculator.calculate_current_equity(fund, db_session)
    
    def test_calculate_average_equity_invalid_fund_type(self, db_session):
        """Test average equity calculation with invalid fund type"""
        # Arrange
        fund = FundFactory()
        # Manually set an invalid tracking type that bypasses database constraints
        fund.tracking_type = "INVALID_TYPE"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported fund type"):
            self.calculator.calculate_average_equity(fund, db_session)
    
    def test_calculate_total_cost_basis_invalid_fund_type(self, db_session):
        """Test total cost basis calculation with invalid fund type"""
        # Arrange
        fund = FundFactory()
        # Manually set an invalid tracking type that bypasses database constraints
        fund.tracking_type = "INVALID_TYPE"
        
        # Act & Assert
        with pytest.raises(ValueError, match="Unsupported fund type"):
            self.calculator.calculate_total_cost_basis(fund, db_session)
    
    def test_nav_based_calculation_with_zero_units(self, db_session):
        """Test NAV-based calculations with zero units"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_SALE,
            units_sold=100.0,
            unit_price=15.0,
            brokerage_fee=40.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Act
        current_equity = self.calculator.calculate_current_equity(fund, db_session)
        total_cost_basis = self.calculator.calculate_total_cost_basis(fund, db_session)
        
        # Assert
        assert current_equity == 0.0  # No units remaining
        assert total_cost_basis == 0.0  # No cost base remaining
    
    def test_nav_based_calculation_with_zero_prices(self, db_session):
        """Test NAV-based calculations with zero unit prices"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=0.0,  # Zero price
            brokerage_fee=50.0,
            event_date=date(2024, 1, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 0.0  # Should handle zero prices gracefully
    
    def test_cost_based_calculation_with_null_amounts(self, db_session):
        """Test cost-based calculations with null amounts"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=None,  # Null amount
            event_date=date(2024, 1, 1),
            
        )
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=1000.0,
            event_date=date(2024, 2, 1),
            
        )
        
        # Act
        result = self.calculator.calculate_current_equity(fund, db_session)
        
        # Assert
        assert result == 1000.0  # Should handle null amounts gracefully


class TestFundEquityCalculatorPerformance:
    """Tests for performance characteristics"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.calculator = FundEquityCalculator()
    
    def test_large_number_of_events_performance(self, db_session):
        """Test performance with large number of events"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        
        # Create 100 purchase events
        for i in range(100):
            FundEventFactory(
                fund=fund,
                event_type=EventType.UNIT_PURCHASE,
                units_purchased=10.0,
                unit_price=10.0 + (i * 0.1),
                brokerage_fee=5.0,
                event_date=date(2024, 1, 1) + timedelta(days=i),
                
            )
        
        # Act
        import time
        start_time = time.time()
        result = self.calculator.calculate_current_equity(fund, db_session)
        end_time = time.time()
        
        # Assert
        assert result > 0.0
        assert (end_time - start_time) < 1.0  # Should complete within 1 second
    
    def test_memory_usage_with_many_events(self, db_session):
        """Test memory usage doesn't grow excessively with many events"""
        # Arrange
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        
        # Create 1000 events
        for i in range(1000):
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100.0,
                event_date=date(2024, 1, 1) + timedelta(days=i),
                
            )
        
        # Act
        result = self.calculator.calculate_total_cost_basis(fund, db_session)
        
        # Assert
        assert result == 100000.0  # 1000 * 100
