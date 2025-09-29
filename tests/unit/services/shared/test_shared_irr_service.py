"""
Shared IRR Service Unit Tests.

This module tests the SharedIrRService class, focusing on IRR calculation logic,
event filtering, and cash flow preparation. Tests are precise and focused on
service functionality without testing calculator logic directly.

Test Coverage:
- IRR calculation with different event types and filtering options
- Event filtering logic for various IRR calculation types
- Cash flow preparation and sign adjustment
- Error handling and edge cases
- Integration with IRRCalculator
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date

from src.shared.services.shared_irr_service import SharedIrRService
from src.fund.models import FundEvent
from src.fund.enums.fund_event_enums import EventType
from tests.factories.fund_factories import FundEventFactory


class TestSharedIrRService:
    """Test suite for SharedIrRService."""

    @pytest.fixture
    def service(self):
        """Create a SharedIrRService instance for testing."""
        return SharedIrRService()

    @pytest.fixture
    def sample_events(self):
        """Create sample fund events for testing."""
        return [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=date(2023, 1, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=120000.0,
                event_date=date(2023, 12, 31)
            )
        ]

    @pytest.fixture
    def complex_events(self):
        """Create complex fund events for testing various scenarios."""
        return [
            FundEventFactory.build(
                event_type=EventType.UNIT_PURCHASE,
                amount=100000.0,
                event_date=date(2023, 1, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=50000.0,
                event_date=date(2023, 6, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=20000.0,
                event_date=date(2023, 9, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.RETURN_OF_CAPITAL,
                amount=80000.0,
                event_date=date(2023, 12, 31)
            ),
            FundEventFactory.build(
                event_type=EventType.TAX_PAYMENT,
                amount=5000.0,
                event_date=date(2024, 1, 15)
            ),
            FundEventFactory.build(
                event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                amount=1000.0,
                event_date=date(2024, 2, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.EOFY_DEBT_COST,
                amount=2000.0,
                event_date=date(2024, 6, 30)
            )
        ]

    ################################################################################
    # Test calculate_irr_base method
    ################################################################################

    def test_calculate_irr_base_basic_gross_irr(self, service, sample_events):
        """Test basic gross IRR calculation (no tax, no risk-free charges)."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', return_value=0.15):
            
            result = service.calculate_irr_base(
                sample_events,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
            
            assert result == 0.15

    def test_calculate_irr_base_with_tax_payments(self, service, complex_events):
        """Test IRR calculation including tax payments."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', return_value=0.12):
            
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=True,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
            
            assert result == 0.12

    def test_calculate_irr_base_with_risk_free_charges(self, service, complex_events):
        """Test IRR calculation including risk-free charges."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', return_value=0.10):
            
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=False,
                include_risk_free_charges=True,
                include_eofy_debt_cost=False
            )
            
            assert result == 0.10

    def test_calculate_irr_base_with_eofy_debt_cost(self, service, complex_events):
        """Test IRR calculation including EOFY debt cost."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', return_value=0.08):
            
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=True
            )
            
            assert result == 0.08

    def test_calculate_irr_base_all_inclusive(self, service, complex_events):
        """Test IRR calculation with all options enabled."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', return_value=0.05):
            
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )
            
            assert result == 0.05

    def test_calculate_irr_base_insufficient_events(self, service):
        """Test IRR calculation with insufficient events (less than 2)."""
        single_event = [FundEventFactory.build(
            event_type=EventType.CAPITAL_CALL,
            amount=100000.0,
            event_date=date(2023, 1, 1)
        )]
        
        result = service.calculate_irr_base(single_event)
        assert result is None

    def test_calculate_irr_base_empty_events(self, service):
        """Test IRR calculation with empty events list."""
        result = service.calculate_irr_base([])
        assert result is None

    def test_calculate_irr_base_invalid_cash_flows(self, service, sample_events):
        """Test IRR calculation when cash flows are invalid."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=False):
            result = service.calculate_irr_base(sample_events)
            assert result is None

    def test_calculate_irr_base_calculator_exception(self, service, sample_events):
        """Test IRR calculation when calculator raises exception."""
        with patch.object(service.irr_calculator, 'validate_cash_flows', return_value=True), \
             patch.object(service.irr_calculator, 'calculate_irr', side_effect=ValueError("Calculation failed")):
            
            with pytest.raises(ValueError, match="Error calculating IRR: Calculation failed"):
                service.calculate_irr_base(sample_events)

    ################################################################################
    # Test _filter_events_for_irr method
    ################################################################################

    def test_filter_events_for_irr_basic_events(self, service, complex_events):
        """Test filtering of basic investment events."""
        filtered = service._filter_events_for_irr(
            complex_events,
            include_tax_payments=False,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
        
        # Should include: UNIT_PURCHASE, CAPITAL_CALL, DISTRIBUTION, RETURN_OF_CAPITAL
        # Should exclude: TAX_PAYMENT, DAILY_RISK_FREE_INTEREST_CHARGE, EOFY_DEBT_COST
        assert len(filtered) == 4
        event_types = [event.event_type for event in filtered]
        assert EventType.UNIT_PURCHASE in event_types
        assert EventType.CAPITAL_CALL in event_types
        assert EventType.DISTRIBUTION in event_types
        assert EventType.RETURN_OF_CAPITAL in event_types

    def test_filter_events_for_irr_with_tax_payments(self, service, complex_events):
        """Test filtering with tax payments included."""
        filtered = service._filter_events_for_irr(
            complex_events,
            include_tax_payments=True,
            include_risk_free_charges=False,
            include_eofy_debt_cost=False
        )
        
        # Should include basic events plus TAX_PAYMENT
        assert len(filtered) == 5
        event_types = [event.event_type for event in filtered]
        assert EventType.TAX_PAYMENT in event_types

    def test_filter_events_for_irr_with_risk_free_charges(self, service, complex_events):
        """Test filtering with risk-free charges included."""
        filtered = service._filter_events_for_irr(
            complex_events,
            include_tax_payments=False,
            include_risk_free_charges=True,
            include_eofy_debt_cost=False
        )
        
        # Should include basic events plus DAILY_RISK_FREE_INTEREST_CHARGE
        assert len(filtered) == 5
        event_types = [event.event_type for event in filtered]
        assert EventType.DAILY_RISK_FREE_INTEREST_CHARGE in event_types

    def test_filter_events_for_irr_with_eofy_debt_cost(self, service, complex_events):
        """Test filtering with EOFY debt cost included."""
        filtered = service._filter_events_for_irr(
            complex_events,
            include_tax_payments=False,
            include_risk_free_charges=False,
            include_eofy_debt_cost=True
        )
        
        # Should include basic events plus EOFY_DEBT_COST
        assert len(filtered) == 5
        event_types = [event.event_type for event in filtered]
        assert EventType.EOFY_DEBT_COST in event_types

    def test_filter_events_for_irr_all_inclusive(self, service, complex_events):
        """Test filtering with all options enabled."""
        filtered = service._filter_events_for_irr(
            complex_events,
            include_tax_payments=True,
            include_risk_free_charges=True,
            include_eofy_debt_cost=True
        )
        
        # Should include all events
        assert len(filtered) == 7

    def test_filter_events_for_irr_empty_list(self, service):
        """Test filtering with empty events list."""
        filtered = service._filter_events_for_irr([])
        assert filtered == []

    def test_filter_events_for_irr_unit_sale_included(self, service):
        """Test that UNIT_SALE events are included in basic filtering."""
        events = [
            FundEventFactory.build(event_type=EventType.UNIT_SALE, amount=1000.0),
            FundEventFactory.build(event_type=EventType.TAX_PAYMENT, amount=100.0)
        ]
        
        filtered = service._filter_events_for_irr(events, include_tax_payments=False)
        assert len(filtered) == 1
        assert filtered[0].event_type == EventType.UNIT_SALE

    ################################################################################
    # Test _prepare_cash_flows method
    ################################################################################

    def test_prepare_cash_flows_basic_events(self, service):
        """Test cash flow preparation for basic investment events."""
        events = [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=date(2023, 1, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=120000.0,
                event_date=date(2023, 12, 31)
            )
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        # CAPITAL_CALL should be negative (outflow)
        assert cash_flows[0] == -100000.0
        # DISTRIBUTION should be positive (inflow)
        assert cash_flows[1] == 120000.0
        
        # Days calculation
        assert days_from_start[0] == 0
        assert days_from_start[1] == 364  # Dec 31 - Jan 1 = 364 days

    def test_prepare_cash_flows_sign_adjustments(self, service):
        """Test correct sign adjustments for different event types."""
        events = [
            FundEventFactory.build(event_type=EventType.UNIT_PURCHASE, amount=1000.0, event_date=date(2023, 1, 1)),
            FundEventFactory.build(event_type=EventType.CAPITAL_CALL, amount=2000.0, event_date=date(2023, 1, 2)),
            FundEventFactory.build(event_type=EventType.UNIT_SALE, amount=3000.0, event_date=date(2023, 1, 3)),
            FundEventFactory.build(event_type=EventType.RETURN_OF_CAPITAL, amount=4000.0, event_date=date(2023, 1, 4)),
            FundEventFactory.build(event_type=EventType.DISTRIBUTION, amount=5000.0, event_date=date(2023, 1, 5)),
            FundEventFactory.build(event_type=EventType.TAX_PAYMENT, amount=600.0, event_date=date(2023, 1, 6)),
            FundEventFactory.build(event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE, amount=700.0, event_date=date(2023, 1, 7)),
            FundEventFactory.build(event_type=EventType.EOFY_DEBT_COST, amount=800.0, event_date=date(2023, 1, 8))
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        # Outflows (negative)
        assert cash_flows[0] == -1000.0  # UNIT_PURCHASE
        assert cash_flows[1] == -2000.0  # CAPITAL_CALL
        assert cash_flows[5] == -600.0   # TAX_PAYMENT
        assert cash_flows[6] == -700.0   # DAILY_RISK_FREE_INTEREST_CHARGE
        
        # Inflows (positive)
        assert cash_flows[2] == 3000.0   # UNIT_SALE
        assert cash_flows[3] == 4000.0   # RETURN_OF_CAPITAL
        assert cash_flows[4] == 5000.0   # DISTRIBUTION
        assert cash_flows[7] == 800.0    # EOFY_DEBT_COST

    def test_prepare_cash_flows_risk_free_interest_charge_coverage(self, service):
        """Test specific coverage for DAILY_RISK_FREE_INTEREST_CHARGE event type."""
        events = [
            FundEventFactory.build(
                event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
                amount=500.0,
                event_date=date(2023, 1, 1)
            )
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        # DAILY_RISK_FREE_INTEREST_CHARGE should be negative (outflow)
        assert cash_flows[0] == -500.0
        assert days_from_start[0] == 0

    def test_prepare_cash_flows_negative_amounts(self, service):
        """Test handling of negative amounts in events."""
        events = [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=-1000.0,  # Already negative
                event_date=date(2023, 1, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=-2000.0,  # Negative distribution
                event_date=date(2023, 1, 2)
            )
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        # Should use abs() for CAPITAL_CALL then negate
        assert cash_flows[0] == -1000.0  # -abs(-1000) = -1000
        # Should use abs() for DISTRIBUTION
        assert cash_flows[1] == 2000.0   # abs(-2000) = 2000

    def test_prepare_cash_flows_none_amounts(self, service):
        """Test handling of None amounts in events."""
        events = [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=None,
                event_date=date(2023, 1, 1)
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=1000.0,
                event_date=date(2023, 1, 2)
            )
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        # None amount should be treated as 0
        assert cash_flows[0] == 0.0
        assert cash_flows[1] == 1000.0

    def test_prepare_cash_flows_days_calculation(self, service):
        """Test accurate days calculation from start date."""
        events = [
            FundEventFactory.build(
                event_type=EventType.CAPITAL_CALL,
                amount=1000.0,
                event_date=date(2023, 1, 15)  # Start date
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=1100.0,
                event_date=date(2023, 1, 16)  # 1 day later
            ),
            FundEventFactory.build(
                event_type=EventType.DISTRIBUTION,
                amount=1200.0,
                event_date=date(2023, 2, 15)  # 31 days later
            )
        ]
        
        cash_flows, days_from_start = service._prepare_cash_flows(events)
        
        assert days_from_start[0] == 0    # Start date
        assert days_from_start[1] == 1    # 1 day later
        assert days_from_start[2] == 31   # 31 days later

    ################################################################################
    # Test integration scenarios
    ################################################################################

    def test_calculate_irr_base_integration_flow(self, service, complex_events):
        """Test complete integration flow from events to IRR result."""
        with patch.object(service.irr_calculator, 'validate_cash_flows') as mock_validate, \
             patch.object(service.irr_calculator, 'calculate_irr') as mock_calculate:
            
            mock_validate.return_value = True
            mock_calculate.return_value = 0.1234
            
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=True,
                include_risk_free_charges=True,
                include_eofy_debt_cost=True
            )
            
            # Verify the flow: filter -> prepare -> validate -> calculate
            mock_validate.assert_called_once()
            mock_calculate.assert_called_once()
            assert result == 0.1234
            
            # Verify validate was called with prepared cash flows
            validate_args = mock_validate.call_args[0]
            cash_flows, days_from_start = validate_args
            assert len(cash_flows) == len(days_from_start)
            assert len(cash_flows) == 7  # All events included

    def test_calculate_irr_base_filtering_integration(self, service, complex_events):
        """Test that filtering works correctly in integration."""
        with patch.object(service.irr_calculator, 'validate_cash_flows') as mock_validate, \
             patch.object(service.irr_calculator, 'calculate_irr') as mock_calculate:
            
            mock_validate.return_value = True
            mock_calculate.return_value = 0.10
            
            # Test with only basic events
            result = service.calculate_irr_base(
                complex_events,
                include_tax_payments=False,
                include_risk_free_charges=False,
                include_eofy_debt_cost=False
            )
            
            # Verify validate was called with filtered cash flows (4 basic events)
            validate_args = mock_validate.call_args[0]
            cash_flows, days_from_start = validate_args
            assert len(cash_flows) == 4  # Only basic events

    def test_service_initialization(self, service):
        """Test that service initializes correctly with IRR calculator."""
        assert service.irr_calculator is not None
        assert hasattr(service.irr_calculator, 'calculate_irr')
        assert hasattr(service.irr_calculator, 'validate_cash_flows')
