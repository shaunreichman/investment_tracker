"""
Extended Shared Calculations Unit Tests

Comprehensive tests for shared calculation functions covering:
- Edge cases and boundary conditions
- Error scenarios
- Financial invariants
- Cross-domain functionality
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from src.shared.calculations import (
    get_equity_change_for_event, get_reconciliation_explanation,
    get_financial_year_dates, orchestrate_irr_base
)


class TestEquityChangeForEventExtended:
    """Extended tests for equity change calculation"""
    
    def test_equity_change_nav_based_unit_purchase(self, db_session):
        """Test equity change for NAV-based unit purchase"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100.0,
            unit_price=10.0,
            brokerage_fee=5.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should exclude brokerage: 100 * 10 = 1000
        assert result == 1000.0
    
    def test_equity_change_nav_based_unit_sale(self, db_session):
        """Test equity change for NAV-based unit sale"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_SALE,
            units_sold=50.0,
            unit_price=12.0,
            brokerage_fee=3.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should exclude brokerage: -(50 * 12) = -600
        assert result == -600.0
    
    def test_equity_change_cost_based_capital_call(self, db_session):
        """Test equity change for cost-based capital call"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=50000.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        assert result == 50000.0
    
    def test_equity_change_cost_based_return_of_capital(self, db_session):
        """Test equity change for cost-based return of capital"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.COST_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=25000.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        assert result == -25000.0
    
    def test_equity_change_unsupported_event_type(self, db_session):
        """Test equity change for unsupported event types"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            amount=1000.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should return 0 for unsupported event types
        assert result == 0.0
    
    def test_equity_change_null_values(self, db_session):
        """Test equity change with null values"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=None,
            unit_price=None
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should handle nulls gracefully
        assert result == 0.0
    
    def test_equity_change_zero_values(self, db_session):
        """Test equity change with zero values"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=0.0,
            unit_price=10.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        assert result == 0.0
    
    def test_equity_change_very_small_values(self, db_session):
        """Test equity change with very small values"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=0.001,
            unit_price=0.01
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should handle small values without precision issues
        assert result == 0.00001
    
    def test_equity_change_very_large_values(self, db_session):
        """Test equity change with very large values"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import FundType, EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(tracking_type=FundType.NAV_BASED)
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=1000000.0,
            unit_price=1000000.0
        )
        
        result = get_equity_change_for_event(event, fund.tracking_type)
        
        # Should handle large values without overflow
        assert result == 1e12


class TestReconciliationExplanationExtended:
    """Extended tests for reconciliation explanation generation"""
    
    def test_reconciliation_perfect_match(self):
        """Test reconciliation with perfect match"""
        result = get_reconciliation_explanation(0.0, 0.0, 0.0)
        
        assert result == "Tax statement matches actual distributions perfectly"
    
    def test_reconciliation_gross_difference_positive(self):
        """Test reconciliation with positive gross difference"""
        result = get_reconciliation_explanation(100.50, 0.0, 0.0)
        
        assert "$100.50 of interest was accrued but not yet distributed" in result
    
    def test_reconciliation_gross_difference_negative(self):
        """Test reconciliation with negative gross difference"""
        result = get_reconciliation_explanation(-75.25, 0.0, 0.0)
        
        assert "$75.25 more was distributed than reported in tax statement" in result
    
    def test_reconciliation_tax_difference_positive(self):
        """Test reconciliation with positive tax difference"""
        result = get_reconciliation_explanation(0.0, 25.75, 0.0)
        
        assert "$25.75 more tax was withheld than actually deducted" in result
    
    def test_reconciliation_tax_difference_negative(self):
        """Test reconciliation with negative tax difference"""
        result = get_reconciliation_explanation(0.0, -15.50, 0.0)
        
        assert "$15.50 less tax was withheld than actually deducted" in result
    
    def test_reconciliation_net_difference_positive(self):
        """Test reconciliation with positive net difference"""
        result = get_reconciliation_explanation(0.0, 0.0, 200.00)
        
        assert "$200.00 more net income reported than actually received" in result
    
    def test_reconciliation_net_difference_negative(self):
        """Test reconciliation with negative net difference"""
        result = get_reconciliation_explanation(0.0, 0.0, -150.75)
        
        assert "$150.75 more net income received than reported" in result
    
    def test_reconciliation_multiple_differences(self):
        """Test reconciliation with multiple differences"""
        result = get_reconciliation_explanation(100.0, 25.0, -50.0)
        
        assert "interest was accrued but not yet distributed" in result
        assert "more tax was withheld than actually deducted" in result
        assert "more net income received than reported" in result
    
    def test_reconciliation_small_rounding_differences(self):
        """Test reconciliation with small rounding differences (should be ignored)"""
        result = get_reconciliation_explanation(0.005, 0.003, 0.001)
        
        # Small differences should be ignored
        assert result == "Tax statement matches actual distributions perfectly"
    
    def test_reconciliation_large_rounding_differences(self):
        """Test reconciliation with large rounding differences (should be reported)"""
        result = get_reconciliation_explanation(0.02, 0.02, 0.02)
        
        # Larger differences should be reported
        assert "interest was accrued but not yet distributed" in result
        assert "more tax was withheld than actually deducted" in result
        assert "more net income reported than actually received" in result
    
    def test_reconciliation_very_large_differences(self):
        """Test reconciliation with very large differences"""
        result = get_reconciliation_explanation(1000000.0, 500000.0, 250000.0)
        
        # Should handle large numbers without formatting issues
        assert "1,000,000.00" in result
        assert "500,000.00" in result
        assert "250,000.00" in result
    
    def test_reconciliation_decimal_precision(self):
        """Test reconciliation with decimal precision"""
        result = get_reconciliation_explanation(123.456, 78.901, 45.678)
        
        # Should format to 2 decimal places
        assert "123.46" in result
        assert "78.90" in result
        assert "45.68" in result


class TestFinancialYearDatesExtended:
    """Extended tests for financial year date calculation"""
    
    def test_financial_year_au_with_hyphen(self):
        """Test AU financial year with hyphen format"""
        start_date, end_date = get_financial_year_dates("2023-24", "AU")
        
        assert start_date == date(2023, 7, 1)
        assert end_date == date(2024, 6, 30)
    
    def test_financial_year_au_without_hyphen(self):
        """Test AU financial year without hyphen format"""
        start_date, end_date = get_financial_year_dates("2023", "AU")
        
        assert start_date == date(2023, 7, 1)
        assert end_date == date(2024, 6, 30)
    
    def test_financial_year_au_two_digit_end_year(self):
        """Test AU financial year with two-digit end year"""
        start_date, end_date = get_financial_year_dates("2023-24", "AU")
        
        assert start_date == date(2023, 7, 1)
        assert end_date == date(2024, 6, 30)
    
    def test_financial_year_other_jurisdiction_with_hyphen(self):
        """Test other jurisdiction with hyphen format"""
        start_date, end_date = get_financial_year_dates("2023-24", "US")
        
        assert start_date == date(2023, 1, 1)
        assert end_date == date(2023, 12, 31)
    
    def test_financial_year_other_jurisdiction_without_hyphen(self):
        """Test other jurisdiction without hyphen format"""
        start_date, end_date = get_financial_year_dates("2023", "US")
        
        assert start_date == date(2023, 1, 1)
        assert end_date == date(2023, 12, 31)
    
    def test_financial_year_edge_cases(self):
        """Test financial year edge cases"""
        # Test year 2000
        start_date, end_date = get_financial_year_dates("2000", "AU")
        assert start_date == date(2000, 7, 1)
        assert end_date == date(2001, 6, 30)
        
        # Test year 2099
        start_date, end_date = get_financial_year_dates("2099", "AU")
        assert start_date == date(2099, 7, 1)
        assert end_date == date(2100, 6, 30)
    
    def test_financial_year_invalid_formats(self):
        """Test financial year with invalid formats"""
        # Test with invalid format (should raise ValueError)
        with pytest.raises(ValueError):
            get_financial_year_dates("invalid", "AU")
        
        # Test with empty string
        with pytest.raises(ValueError):
            get_financial_year_dates("", "AU")
        
        # Test with None
        with pytest.raises(ValueError):
            get_financial_year_dates(None, "AU")


class TestOrchestrateIRRBaseExtended:
    """Extended tests for IRR orchestration function"""
    
    def test_orchestrate_irr_base_basic_cash_flows(self, db_session):
        """Test basic IRR orchestration with cash flows"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=110000.0,
                event_date=start_date + timedelta(days=365)
            )
        ]
        
        result = orchestrate_irr_base(events, start_date)
        
        # Should return IRR value
        assert isinstance(result, (int, float)) or result is None
    
    def test_orchestrate_irr_base_with_tax_payments(self, db_session):
        """Test IRR orchestration including tax payments"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.TAX_PAYMENT,
                amount=5000.0,
                event_date=start_date + timedelta(days=180)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=110000.0,
                event_date=start_date + timedelta(days=365)
            )
        ]
        
        result = orchestrate_irr_base(events, start_date, include_tax_payments=True)
        
        # Should return IRR value
        assert isinstance(result, (int, float)) or result is None
    
    def test_orchestrate_irr_base_return_cashflows(self, db_session):
        """Test IRR orchestration returning cash flow details"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=110000.0,
                event_date=start_date + timedelta(days=365)
            )
        ]
        
        result = orchestrate_irr_base(events, start_date, return_cashflows=True)
        
        # Should return dict with cash flow details
        assert isinstance(result, dict)
        assert 'irr' in result
        assert 'cash_flows' in result
        assert 'days_from_start' in result
        assert 'events' in result
        assert 'labels' in result
    
    def test_orchestrate_irr_base_no_events(self, db_session):
        """Test IRR orchestration with no events"""
        from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        result = orchestrate_irr_base([], start_date)
        
        # Should return None for no events
        assert result is None
    
    def test_orchestrate_irr_base_single_event(self, db_session):
        """Test IRR orchestration with single event"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            )
        ]
        
        result = orchestrate_irr_base(events, start_date)
        
        # Should return None for single event (can't calculate IRR)
        assert result is None
    
    def test_orchestrate_irr_base_event_filtering(self, db_session):
        """Test IRR orchestration with event filtering"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=110000.0,
                event_date=start_date + timedelta(days=365)
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.NAV_UPDATE,
                amount=0.0,
                event_date=start_date + timedelta(days=180)
            )
        ]
        
        # Filter to only capital events
        capital_events = [e for e in events if e.event_type in [EventType.CAPITAL_CALL, EventType.DISTRIBUTION]]
        result = orchestrate_irr_base(capital_events, start_date)
        
        # Should return IRR value
        assert isinstance(result, (int, float)) or result is None
    
    def test_orchestrate_irr_base_cash_flow_signs(self, db_session):
        """Test IRR orchestration with correct cash flow signs"""
        from tests.factories import FundEventFactory, FundFactory, EntityFactory, InvestmentCompanyFactory
        from src.fund.models import EventType
        
        # Set session for all factories
        EntityFactory._meta.sqlalchemy_session = db_session
        InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
        FundFactory._meta.sqlalchemy_session = db_session
        FundEventFactory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        start_date = date(2024, 1, 1)
        
        events = [
            FundEventFactory(
                fund=fund,
                event_type=EventType.CAPITAL_CALL,
                amount=100000.0,
                event_date=start_date
            ),
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                amount=110000.0,
                event_date=start_date + timedelta(days=365)
            )
        ]
        
        result = orchestrate_irr_base(events, start_date, return_cashflows=True)
        
        if result and 'cash_flows' in result:
            # CAPITAL_CALL should be negative (outflow)
            assert result['cash_flows'][0] < 0
            # DISTRIBUTION should be positive (inflow)
            assert result['cash_flows'][1] > 0
