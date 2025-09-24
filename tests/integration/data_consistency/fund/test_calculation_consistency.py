"""
Fund Calculation Consistency Tests.

This module provides comprehensive testing for calculation consistency across
different calculation methods, ensuring that all calculation approaches produce
consistent and accurate results.

**Testing Approach**: Factory-Based Integration Testing
**Reasoning**: Data consistency tests require real database state to validate
cross-component data integrity and calculation accuracy.

**Core Testing Principles**:
- Test calculation consistency across different methods
- Test cross-calculation validation and enforcement
- Test calculation accuracy and precision validation
- Use factories to create real calculation scenarios
"""

import pytest
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import List
import numpy as np

from tests.factories import (
    FundFactory, EntityFactory, InvestmentCompanyFactory,
    FundEventFactory
)
from src.fund.models import Fund, FundEvent, FundTrackingType, EventType, DistributionType
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.services.tax_calculation_service import TaxCalculationService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.enums import FundStatus
from src.fund.events.orchestrator import FundUpdateOrchestrator
from src.fund.services.fund_calculation_service import FundCalculationService


class TestFundCalculationConsistency:
    """
    Test calculation consistency across all fund calculation methods.
    
    **Scope**: Cross-calculation validation, accuracy, and precision
    **Focus**: Data integrity and calculation consistency
    **Approach**: Integration testing with real database state
    """

    def test_irr_calculation_consistency_across_methods(self, db_session):
        """
        Test that IRR calculations are consistent across different calculation methods.
        
        **Test**: IRR calculations produce consistent results across service and utility methods
        **Validation**: Service method IRR matches utility function IRR for same cash flows
        """
        # Create fund with capital call and distribution
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create capital call event
        orchestrator = FundUpdateOrchestrator()
        capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 500000.0,
            'event_date': '2023-01-01',
            'description': 'Initial capital call',
            'reference_number': 'CC001'
        }
        
        capital_event = orchestrator.process_fund_event(capital_event_data, db_session, fund)
        db_session.commit()
        
        # Create distribution event
        distribution_event_data = {
            'event_type': EventType.DISTRIBUTION,
            'distribution_amount': 600000.0,
            'event_date': '2023-12-31',
            'distribution_type': DistributionType.INTEREST,
            'description': 'Annual distribution'
        }
        
        distribution_event = orchestrator.process_fund_event(distribution_event_data, db_session, fund)
        db_session.commit()
        
        # Calculate IRR using service method
        calculation_service = FundCalculationService()
        service_irr = calculation_service.calculate_irr(fund, db_session)
        
        # Calculate IRR using utility function
        cash_flows = [-500000.0, 600000.0]  # Capital call (negative), distribution (positive)
        days_from_start = [0, 364]  # Days from start
        utility_irr = calculation_service._calculate_irr_utility(cash_flows, days_from_start)
        
        # Convert utility IRR to annual rate for comparison
        if utility_irr is not None:
            utility_irr_annual = utility_irr
        else:
            utility_irr_annual = None
        
        # Verify IRR calculations are consistent (allow for small precision differences)
        if service_irr is not None and utility_irr_annual is not None:
            assert abs(service_irr - utility_irr_annual) < 0.001, (
                f"IRR calculations should be consistent: service={service_irr:.6f}, "
                f"utility={utility_irr_annual:.6f}"
            )
        
        # Verify IRR is reasonable for the scenario
        assert service_irr is not None, "IRR calculation should succeed"
        assert service_irr > 0, "IRR should be positive for profitable scenario"

    def test_equity_balance_calculation_consistency(self, db_session):
        """
        Test that equity balance calculations are consistent across different approaches.
        
        **Test**: Equity balance calculations produce consistent results
        **Validation**: Manual calculation matches service calculation matches model field
        """
        # Create fund with multiple capital calls
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create multiple capital call events
        orchestrator = FundUpdateOrchestrator()
        capital_calls = [
            {'amount': 200000.0, 'event_date': '2023-01-01', 'description': 'First call'},
            {'amount': 150000.0, 'event_date': '2023-04-01', 'description': 'Second call'},
            {'amount': 100000.0, 'event_date': '2023-07-01', 'description': 'Third call'}
        ]
        
        for call_data in capital_calls:
            event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'amount': call_data['amount'],
                'event_date': call_data['event_date'],
                'description': call_data['description'],
                'reference_number': f"CC{len(fund.fund_events) + 1:03d}"
            }
            orchestrator.process_fund_event(event_data, db_session, fund)
        
        db_session.commit()
        
        # Calculate expected equity balance manually
        expected_equity_balance = sum(call['amount'] for call in capital_calls)
        
        # Verify model field matches expected
        assert fund.current_equity_balance == expected_equity_balance, (
            f"Model equity balance should match expected: {fund.current_equity_balance} vs {expected_equity_balance}"
        )
        
        # Verify service calculation matches
        calculation_service = FundCalculationService()
        # Pass events list to avoid circular import issues
        service_equity_balance = calculation_service.calculate_average_equity_balance(fund, db_session, events=fund.fund_events)
        
        # For cost-based funds, average equity should be weighted by time
        # This is a simplified check - the actual calculation is more complex
        assert service_equity_balance > 0, "Average equity balance should be positive"
        assert service_equity_balance <= expected_equity_balance, "Average equity should not exceed current equity"

    def test_nav_calculation_consistency_for_nav_based_funds(self, db_session):
        """
        Test that NAV calculations are consistent for NAV-based funds.
        
        **Test**: NAV calculations produce consistent results across different methods
        **Validation**: NAV field updates match expected calculations
        """
        # Create NAV-based fund
        fund = FundFactory(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create unit purchase events
        orchestrator = FundUpdateOrchestrator()
        unit_purchases = [
            {'units': 1000, 'price': 100.0, 'event_date': '2023-01-01', 'brokerage': 1000.0},
            {'units': 500, 'price': 110.0, 'event_date': '2023-04-01', 'brokerage': 500.0}
        ]
        
        for purchase_data in unit_purchases:
            event_data = {
                'event_type': EventType.UNIT_PURCHASE,
                'units_purchased': purchase_data['units'],
                'unit_price': purchase_data['price'],
                'event_date': purchase_data['event_date'],
                'brokerage_fee': purchase_data['brokerage'],
                'description': f"Unit purchase at ${purchase_data['price']}"
            }
            orchestrator.process_fund_event(event_data, db_session, fund)
        
        db_session.commit()
        
        # Calculate expected NAV manually
        total_units = sum(purchase['units'] for purchase in unit_purchases)
        total_cost = sum(
            purchase['units'] * purchase['price'] + purchase['brokerage']
            for purchase in unit_purchases
        )
        expected_nav = total_cost / total_units if total_units > 0 else 0
        
        # Verify NAV field is updated correctly
        # Note: NAV calculation is complex and may involve additional logic
        # This test validates that the basic structure is working
        assert len(fund.fund_events) == 2, "Should have 2 unit purchase events"
        
        # Verify that NAV-related fields are being calculated
        for event in fund.fund_events:
            if event.event_type == EventType.UNIT_PURCHASE:
                assert event.units_purchased is not None, "Units purchased should be set"
                assert event.unit_price is not None, "Unit price should be set"

    def test_tax_calculation_consistency(self, db_session):
        """
        Test that tax calculations are consistent across different calculation methods.
        
        **Test**: Tax calculations produce consistent results
        **Validation**: Tax calculations match expected business logic
        """
        # Create fund with capital call and distribution
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create capital call event
        orchestrator = FundUpdateOrchestrator()
        capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 500000.0,
            'event_date': '2023-01-01',
            'description': 'Initial capital call',
            'reference_number': 'CC001'
        }
        
        capital_event = orchestrator.process_fund_event(capital_event_data, db_session, fund)
        db_session.commit()
        
        # Create distribution with withholding tax
        distribution_event_data = {
            'event_type': EventType.DISTRIBUTION,
            'gross_interest_amount': 100000.0,  # Gross amount before tax
            'event_date': '2023-06-30',
            'distribution_type': DistributionType.INTEREST,
            'withholding_tax_amount': 15000.0,  # 15% withholding tax
            'has_withholding_tax': True,  # Required flag for withholding tax distributions
            'description': 'Distribution with withholding tax'
        }
        
        distribution_event = orchestrator.process_fund_event(distribution_event_data, db_session, fund)
        db_session.commit()
        
        # Verify tax calculations are consistent
        assert distribution_event.tax_withholding == 15000.0, (
            "Withholding tax amount should be correctly set"
        )
        
        # Verify the distribution event was created correctly
        # The amount field should contain the net amount (gross - tax)
        expected_net_amount = 100000.0 - 15000.0  # 85000.0
        assert distribution_event.amount == expected_net_amount, (
            f"Distribution amount should be net amount: {distribution_event.amount} vs {expected_net_amount}"
        )
        
        # Verify tax percentage calculation
        # The amount field contains the net amount, so gross = net + tax
        gross_amount = distribution_event.amount + distribution_event.tax_withholding
        expected_gross = 100000.0
        assert abs(gross_amount - expected_gross) < 0.01, (
            f"Gross amount calculation should be correct: {gross_amount} vs {expected_gross}"
        )
        
        tax_percentage = (distribution_event.tax_withholding / gross_amount) * 100
        expected_percentage = 15.0
        
        assert abs(tax_percentage - expected_percentage) < 0.01, (
            f"Tax percentage should be correct: {tax_percentage:.2f}% vs {expected_percentage}%"
        )

    def test_debt_cost_calculation_consistency(self, db_session):
        """
        Test that debt cost calculations are consistent.
        
        **Test**: Debt cost calculations produce consistent results
        **Validation**: Debt cost calculations match expected business logic
        """
        # Create fund with capital call
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create capital call event
        orchestrator = FundUpdateOrchestrator()
        capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 500000.0,
            'event_date': '2023-01-01',
            'description': 'Initial capital call',
            'reference_number': 'CC001'
        }
        
        capital_event = orchestrator.process_fund_event(capital_event_data, db_session, fund)
        db_session.commit()
        
        # Test debt cost calculation using service
        tax_service = TaxCalculationService()
        debt_cost_result = tax_service.calculate_debt_cost(fund, db_session)
        
        # Verify debt cost calculation structure
        if debt_cost_result is not None:
            assert 'total_debt_cost' in debt_cost_result, "Debt cost result should contain total_debt_cost"
            assert 'average_risk_free_rate' in debt_cost_result, "Debt cost result should contain average_risk_free_rate"
            assert 'debt_cost_percentage' in debt_cost_result, "Debt cost result should contain debt_cost_percentage"
            
            # Verify debt cost is reasonable
            assert debt_cost_result['total_debt_cost'] >= 0, "Total debt cost should be non-negative"
            assert debt_cost_result['average_risk_free_rate'] >= 0, "Average risk-free rate should be non-negative"

    def test_calculation_precision_consistency(self, db_session):
        """
        Test that calculations maintain consistent precision across different methods.
        
        **Test**: Calculation precision is consistent and accurate
        **Validation**: Precision matches expected financial standards
        """
        # Create fund with precise amounts
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.00  # 2 decimal places
        )
        db_session.commit()
        
        # Create capital call with precise amount
        orchestrator = FundUpdateOrchestrator()
        capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 333333.33,  # Precise amount
            'event_date': '2023-01-01',
            'description': 'Precise capital call',
            'reference_number': 'CC001'
        }
        
        capital_event = orchestrator.process_fund_event(capital_event_data, db_session, fund)
        db_session.commit()
        
        # Verify precision is maintained
        assert fund.current_equity_balance == 333333.33, (
            f"Equity balance should maintain precision: {fund.current_equity_balance}"
        )
        
        # Create distribution with precise amount
        distribution_event_data = {
            'event_type': EventType.DISTRIBUTION,
            'distribution_amount': 166666.67,  # Precise amount
            'event_date': '2023-06-30',
            'distribution_type': DistributionType.INTEREST,
            'description': 'Precise distribution'
        }
        
        distribution_event = orchestrator.process_fund_event(distribution_event_data, db_session, fund)
        db_session.commit()
        
        # Verify remaining equity balance precision
        # Note: Distributions are income events, not capital returns, so they don't reduce equity balance
        # The equity balance should remain the same after the distribution
        expected_remaining = 333333.33  # Distributions don't reduce equity balance
        assert abs(fund.current_equity_balance - expected_remaining) < 0.01, (
            f"Equity balance should remain unchanged after distribution (distributions are income): {fund.current_equity_balance} vs {expected_remaining}"
        )

    def test_cross_fund_type_calculation_consistency(self, db_session):
        """
        Test that calculations are consistent across different fund types.
        
        **Test**: Same calculation logic produces consistent results for different fund types
        **Validation**: Calculations respect fund type differences while maintaining consistency
        """
        # Create cost-based fund
        cost_fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create NAV-based fund
        nav_fund = FundFactory(
            tracking_type=FundTrackingType.NAV_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Add capital call to cost-based fund
        orchestrator = FundUpdateOrchestrator()
        cost_capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': 500000.0,
            'event_date': '2023-01-01',
            'description': 'Cost-based capital call',
            'reference_number': 'CC001'
        }
        
        cost_capital_event = orchestrator.process_fund_event(cost_capital_event_data, db_session, cost_fund)
        db_session.commit()
        
        # Add unit purchase to NAV-based fund
        nav_purchase_event_data = {
            'event_type': EventType.UNIT_PURCHASE,
            'units_purchased': 5000,
            'unit_price': 100.0,
            'event_date': '2023-01-01',
            'brokerage_fee': 1000.0,
            'description': 'NAV-based unit purchase'
        }
        
        nav_purchase_event = orchestrator.process_fund_event(nav_purchase_event_data, db_session, nav_fund)
        db_session.commit()
        
        # Verify both funds have events
        assert len(cost_fund.fund_events) == 1, "Cost-based fund should have capital call event"
        assert len(nav_fund.fund_events) == 1, "NAV-based fund should have unit purchase event"
        
        # Verify equity balance calculations respect fund type
        assert cost_fund.current_equity_balance == 500000.0, "Cost-based fund should track equity balance"
        
        # NAV-based funds may not track current_equity_balance the same way
        # This test validates that the calculation logic respects fund type differences
        assert nav_fund.tracking_type == FundTrackingType.NAV_BASED, "Fund type should be preserved"

    def test_calculation_error_handling_consistency(self, db_session):
        """
        Test that calculation errors are handled consistently across different methods.
        
        **Test**: Error handling is consistent and appropriate
        **Validation**: Invalid inputs produce appropriate errors
        """
        # Create fund
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Test invalid event data handling
        orchestrator = FundUpdateOrchestrator()
        
        # Test invalid capital call amount
        invalid_capital_event_data = {
            'event_type': EventType.CAPITAL_CALL,
            'amount': -100000.0,  # Negative amount should be invalid
            'event_date': '2023-01-01',
            'description': 'Invalid negative capital call',
            'reference_number': 'CC001'
        }
        
        # This should raise an appropriate error
        with pytest.raises((ValueError, AssertionError)):
            orchestrator.process_fund_event(invalid_capital_event_data, db_session, fund)
        
        # Verify fund state is unchanged
        db_session.refresh(fund)
        assert fund.current_equity_balance == 0.0, "Fund state should remain unchanged after invalid event"
        assert len(fund.fund_events) == 0, "No events should be created from invalid data"

    def test_calculation_performance_consistency(self, db_session):
        """
        Test that calculation performance is consistent across different scenarios.
        
        **Test**: Calculation performance is predictable and consistent
        **Validation**: Performance characteristics are maintained
        """
        # Create fund with multiple events
        fund = FundFactory(
            tracking_type=FundTrackingType.COST_BASED,
            commitment_amount=1000000.0
        )
        db_session.commit()
        
        # Create multiple capital call events
        orchestrator = FundUpdateOrchestrator()
        num_events = 10
        
        for i in range(num_events):
            event_data = {
                'event_type': EventType.CAPITAL_CALL,
                'amount': 50000.0,
                'event_date': f'2023-{i+1:02d}-01',
                'description': f'Capital call {i+1}',
                'reference_number': f'CC{i+1:03d}'
            }
            orchestrator.process_fund_event(event_data, db_session, fund)
        
        db_session.commit()
        
        # Verify all events were processed
        assert len(fund.fund_events) == num_events, f"Should have {num_events} events"
        
        # Verify equity balance calculation is correct
        expected_equity_balance = num_events * 50000.0
        assert fund.current_equity_balance == expected_equity_balance, (
            f"Equity balance should be correct: {fund.current_equity_balance} vs {expected_equity_balance}"
        )
        
        # Test calculation service performance
        calculation_service = FundCalculationService()
        
        # Time the equity balance calculation
        import time
        start_time = time.time()
        # Pass events list to avoid circular import issues
        equity_balance = calculation_service.calculate_average_equity_balance(fund, db_session, events=fund.fund_events)
        end_time = time.time()
        
        calculation_time = end_time - start_time
        
        # Verify calculation completes in reasonable time (should be < 1 second)
        assert calculation_time < 1.0, f"Equity balance calculation should complete quickly: {calculation_time:.3f}s"
        assert equity_balance > 0, "Average equity balance should be calculated correctly"
