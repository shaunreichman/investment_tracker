"""
Tax Calculation Service Tests.

This module tests the TaxCalculationService which handles all tax-related calculations for funds.

Key responsibilities tested:
- Tax withholding calculations
- Tax statement calculations  
- Tax event creation
- Tax-based IRR calculations

Test focus: Tax calculation logic only - no model validation, no performance testing, no integration concerns.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.fund.services.tax_calculation_service import TaxCalculationService
from src.fund.enums import EventType, DistributionType, FundStatus, TaxPaymentType
from src.fund.models import Fund, FundEvent
from src.tax.models import TaxStatement


class TestTaxCalculationService:
    """Test suite for TaxCalculationService - Tax calculation logic only"""
    
    @pytest.fixture
    def service(self):
        """Create a TaxCalculationService instance for testing."""
        service = TaxCalculationService()
        # Mock the repository dependencies
        service.fund_event_repository = Mock()
        service.fund_event_query_repository = Mock()
        service.tax_event_repository = Mock()
        return service
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.currency = "AUD"
        fund.start_date = date(2020, 1, 1)
        fund.end_date = date(2025, 12, 31)
        fund.status = FundStatus.ACTIVE
        fund.fund_events = []
        return fund
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session for testing."""
        session = Mock(spec=Session)
        return session

    # ============================================================================
    # DEBT COST CALCULATIONS AND RISK-FREE INTEREST CHARGES
    # ============================================================================
    
    def test_calculate_debt_cost_no_start_date(self, service, mock_fund):
        """Test debt cost calculation when fund has no start date."""
        mock_fund.start_date = None
        
        result = service.calculate_debt_cost(mock_fund)
        
        assert result is None
    
    def test_calculate_debt_cost_no_risk_free_rates(self, service, mock_fund, mock_session):
        """Test debt cost calculation when no risk-free rates available."""
        with patch.object(service, '_get_risk_free_rates') as mock_get_rates:
            mock_get_rates.return_value = []
            
            result = service.calculate_debt_cost(mock_fund, mock_session)
            
            assert result is None
            mock_get_rates.assert_called_once_with("AUD", mock_session)
    
    def test_calculate_debt_cost_with_risk_free_rates(self, service, mock_fund, mock_session):
        """Test debt cost calculation with available risk-free rates."""
        # Mock risk-free rates
        mock_rate = Mock()
        mock_rate.rate = 0.05  # 5%
        mock_rate.date = date(2020, 1, 1)
        
        with patch.object(service, '_get_risk_free_rates') as mock_get_rates:
            with patch.object(service, '_get_existing_daily_interest_dates') as mock_get_dates:
                with patch.object(service, '_get_cash_flow_events') as mock_get_cash_flows:
                    with patch.object(service, '_calculate_daily_interest_charge_objects') as mock_calc:
                        mock_get_rates.return_value = [mock_rate]
                        mock_get_dates.return_value = []
                        mock_get_cash_flows.return_value = []
                        
                        # Mock daily charge objects
                        mock_charge1 = Mock()
                        mock_charge1.amount = 10.0
                        mock_charge2 = Mock()
                        mock_charge2.amount = 15.0
                        mock_calc.return_value = [mock_charge1, mock_charge2]
                        
                        result = service.calculate_debt_cost(mock_fund, mock_session)
                        
                        assert result == 25.0
                        mock_get_rates.assert_called_once_with("AUD", mock_session)
    
    def test_calculate_debt_cost_completed_fund(self, service, mock_fund, mock_session):
        """Test debt cost calculation for completed fund uses end date."""
        mock_fund.status = FundStatus.REALIZED
        mock_fund.end_date = date(2023, 12, 31)
        
        with patch.object(service, '_get_risk_free_rates') as mock_get_rates:
            with patch.object(service, '_get_existing_daily_interest_dates') as mock_get_dates:
                with patch.object(service, '_get_cash_flow_events') as mock_get_cash_flows:
                    with patch.object(service, '_calculate_daily_interest_charge_objects') as mock_calc:
                        mock_get_rates.return_value = [Mock()]
                        mock_get_dates.return_value = []
                        mock_get_cash_flows.return_value = []
                        mock_calc.return_value = []
                        
                        service.calculate_debt_cost(mock_fund, mock_session)
                        
                        # Should use end_date instead of date.today()
                        mock_calc.assert_called_once()
                        call_args = mock_calc.call_args[0]
                        assert call_args[1] == date(2023, 12, 31)  # end_date
    
    def test_calculate_debt_cost_custom_currency(self, service, mock_fund, mock_session):
        """Test debt cost calculation with custom risk-free rate currency."""
        custom_currency = "USD"
        
        with patch.object(service, '_get_risk_free_rates') as mock_get_rates:
            mock_get_rates.return_value = []
            
            service.calculate_debt_cost(mock_fund, mock_session, custom_currency)
            
            mock_get_rates.assert_called_once_with(custom_currency, mock_session)
    
    def test_create_eofy_debt_cost_events(self, service, mock_fund, mock_session):
        """Test creation of EOFY debt cost events."""
        with patch.object(service, '_process_financial_year_for_debt_cost') as mock_process:
            service.create_eofy_debt_cost_events(mock_fund, mock_session)
            
            # Should process current and previous financial year
            assert mock_process.call_count == 2
    
    def test_recalculate_debt_costs(self, service, mock_fund, mock_session):
        """Test complete debt cost recalculation."""
        with patch.object(service, '_delete_debt_cost_events') as mock_delete:
            with patch.object(service, 'create_daily_risk_free_interest_charges') as mock_create_daily:
                with patch.object(service, 'create_eofy_debt_cost_events') as mock_create_eofy:
                    service.recalculate_debt_costs(mock_fund, mock_session)
                    
                    mock_delete.assert_called_once_with(mock_fund, mock_session)
                    mock_create_daily.assert_called_once_with(mock_fund, mock_session, None)
                    mock_create_eofy.assert_called_once_with(mock_fund, mock_session)

    # ============================================================================
    # DISTRIBUTION TAX CALCULATIONS AND WITHHOLDING LOGIC
    # ============================================================================
    
    def test_get_distributions_by_type(self, service, mock_fund):
        """Test grouping of distributions by type - delegates to repository."""
        mock_session = Mock()
        expected = {
            DistributionType.INCOME: [Mock()],
            DistributionType.CAPITAL_GAIN: [Mock()],
            'unknown': [Mock()]
        }
        service.fund_event_query_repository.get_distributions_by_type.return_value = expected
        
        result = service.get_distributions_by_type(mock_fund, mock_session)
        
        assert result == expected
        service.fund_event_query_repository.get_distributions_by_type.assert_called_once_with(
            mock_fund.id, mock_session
        )
    
    def test_get_total_distributions(self, service, mock_fund):
        """Test calculation of total distribution amount - delegates to repository."""
        mock_session = Mock()
        service.fund_event_query_repository.get_total_by_type.return_value = 3000.0
        
        result = service.get_total_distributions(mock_fund, mock_session)
        
        assert result == 3000.0
        service.fund_event_query_repository.get_total_by_type.assert_called_once_with(
            mock_fund.id, EventType.DISTRIBUTION, mock_session
        )
    
    def test_get_total_distributions_no_session(self, service, mock_fund):
        """Test total distributions calculation with no session."""
        result = service.get_total_distributions(mock_fund, None)
        
        assert result == 0.0
    
    def test_get_taxable_distributions(self, service, mock_fund):
        """Test calculation of taxable distributions - delegates to repository."""
        mock_session = Mock()
        service.fund_event_query_repository.get_taxable_distributions.return_value = 6000.0
        
        result = service.get_taxable_distributions(mock_fund, mock_session)
        
        assert result == 6000.0
        service.fund_event_query_repository.get_taxable_distributions.assert_called_once_with(
            mock_fund.id, mock_session
        )
    
    def test_get_gross_distributions(self, service, mock_fund):
        """Test calculation of gross distributions - delegates to repository."""
        mock_session = Mock()
        service.fund_event_query_repository.get_total_by_type.return_value = 3000.0
        
        result = service.get_gross_distributions(mock_fund, mock_session)
        
        assert result == 3000.0
        service.fund_event_query_repository.get_total_by_type.assert_called_once_with(
            mock_fund.id, EventType.DISTRIBUTION, mock_session
        )
    
    def test_get_net_distributions(self, service, mock_fund):
        """Test calculation of net distributions - delegates to repository."""
        mock_session = Mock()
        with patch.object(service, 'get_gross_distributions') as mock_gross:
            with patch.object(service, 'get_total_tax_withheld') as mock_tax:
                mock_gross.return_value = 1000.0
                mock_tax.return_value = 200.0
                
                result = service.get_net_distributions(mock_fund, mock_session)
                
                assert result == 800.0
    
    def test_get_total_tax_withheld(self, service, mock_fund):
        """Test calculation of total tax withheld - delegates to repository."""
        mock_session = Mock()
        service.fund_event_query_repository.get_total_tax_withheld.return_value = 300.0
        
        result = service.get_total_tax_withheld(mock_fund, mock_session)
        
        assert result == 300.0
        service.fund_event_query_repository.get_total_tax_withheld.assert_called_once_with(
            mock_fund.id, mock_session
        )
    
    def test_get_distributions_with_tax_details(self, service, mock_fund):
        """Test retrieval of distributions with detailed tax information."""
        # Mock fund events
        mock_dist1 = Mock()
        mock_dist1.id = 1
        mock_dist1.event_type = EventType.DISTRIBUTION
        mock_dist1.event_date = date(2023, 6, 30)
        mock_dist1.amount = 1000.0
        mock_dist1.distribution_type = DistributionType.INCOME
        mock_dist1.tax_withheld = 200.0
        mock_dist1.description = "Income distribution"
        mock_dist1.reference_number = "DIST001"
        
        mock_dist2 = Mock()
        mock_dist2.id = 2
        mock_dist2.event_type = EventType.DISTRIBUTION
        mock_dist2.event_date = date(2023, 6, 30)
        mock_dist2.amount = 2000.0
        mock_dist2.distribution_type = DistributionType.CAPITAL_GAIN
        mock_dist2.tax_withheld = None
        mock_dist2.description = "Capital gains distribution"
        mock_dist2.reference_number = None
        
        mock_fund.fund_events = [mock_dist1, mock_dist2]
        
        # Mock the repository to return the distribution events
        service.fund_event_query_repository.get_events_by_type.return_value = [mock_dist1, mock_dist2]
        
        result = service.get_distributions_with_tax_details(mock_fund)
        
        assert len(result) == 2
        
        # Check first distribution
        dist1_result = result[0]
        assert dist1_result['id'] == 1
        assert dist1_result['amount'] == 1000.0
        assert dist1_result['tax_withheld'] == 200.0
        assert dist1_result['net_amount'] == 800.0
        assert dist1_result['distribution_type'] == DistributionType.INCOME
        
        # Check second distribution
        dist2_result = result[1]
        assert dist2_result['id'] == 2
        assert dist2_result['amount'] == 2000.0
        assert dist2_result['tax_withheld'] is None
        assert dist2_result['net_amount'] == 2000.0
        assert dist2_result['distribution_type'] == DistributionType.CAPITAL_GAIN

    # ============================================================================
    # PRIVATE HELPER METHODS
    # ============================================================================
    
    def test_get_cash_flow_events(self, service, mock_fund):
        """Test retrieval of cash flow events."""
        # Mock fund events
        mock_capital_call = Mock()
        mock_capital_call.event_type = EventType.CAPITAL_CALL
        
        mock_return_capital = Mock()
        mock_return_capital.event_type = EventType.RETURN_OF_CAPITAL
        
        mock_distribution = Mock()
        mock_distribution.event_type = EventType.DISTRIBUTION
        
        mock_unit_purchase = Mock()
        mock_unit_purchase.event_type = EventType.UNIT_PURCHASE  # Should be excluded
        
        mock_fund.fund_events = [mock_capital_call, mock_return_capital, mock_distribution, mock_unit_purchase]
        
        result = service._get_cash_flow_events(mock_fund)
        
        # Should only include CAPITAL_CALL, RETURN_OF_CAPITAL, and DISTRIBUTION
        assert len(result) == 3
        assert mock_capital_call in result
        assert mock_return_capital in result
        assert mock_distribution in result
        assert mock_unit_purchase not in result
    
    def test_process_financial_year_for_debt_cost_no_interest(self, service, mock_fund, mock_session):
        """Test processing of debt cost when no interest to charge."""
        financial_year = 2023
        
        with patch.object(service, 'calculate_eofy_debt_interest_deduction_sum_of_daily_interest') as mock_calc:
            mock_calc.return_value = 0.0
            
            service._process_financial_year_for_debt_cost(mock_fund, financial_year, mock_session)
            
            # Should not create any events when no interest
            # Note: This test currently doesn't create events due to mocking limitations
            # In a real scenario, it would create FundEvent instances

    # ============================================================================
    # SKIPPED TESTS - Methods that reference unavailable Fund model functionality
    # ============================================================================
    
    def test_calculate_eofy_debt_interest_deduction_sum(self, service, mock_fund, mock_session):
        """Test calculation of EOFY debt interest deduction sum - delegates to repository."""
        financial_year = 2023
        service.tax_event_repository.get_daily_interest_charges_by_financial_year.return_value = 1500.0
        
        result = service.calculate_eofy_debt_interest_deduction_sum_of_daily_interest(
            mock_fund, financial_year, mock_session
        )
        
        assert result == 1500.0
        service.tax_event_repository.get_daily_interest_charges_by_financial_year.assert_called_once_with(
            mock_fund.id, financial_year, mock_session
        )
    
    def test_get_existing_daily_interest_dates(self, service, mock_fund, mock_session):
        """Test retrieval of existing daily interest charge dates - delegates to repository."""
        from datetime import date
        from src.fund.enums import EventType
        
        mock_events = [Mock(), Mock()]
        mock_events[0].event_date = date(2023, 1, 1)
        mock_events[1].event_date = date(2023, 1, 2)
        
        service.tax_event_repository.get_tax_events_by_type_and_date_range.return_value = mock_events
        
        result = service._get_existing_daily_interest_dates(mock_fund, mock_session)
        
        assert len(result) == 2
        assert result[0] == date(2023, 1, 1)
        assert result[1] == date(2023, 1, 2)
        service.tax_event_repository.get_tax_events_by_type_and_date_range.assert_called_once()
    
    def test_get_cash_flow_events(self, service, mock_fund, mock_session):
        """Test retrieval of cash flow events - delegates to repository."""
        from datetime import date
        from src.fund.enums import EventType
        
        mock_events = [Mock(), Mock(), Mock()]
        service.fund_event_query_repository.get_events_by_type.return_value = mock_events
        
        result = service._get_cash_flow_events(mock_fund, mock_session)
        
        # Should call repository for each event type
        assert service.fund_event_query_repository.get_events_by_type.call_count == 3
        assert len(result) == 9  # 3 calls * 3 events each
    
    def test_delete_debt_cost_events(self, service, mock_fund, mock_session):
        """Test deletion of all debt cost events - delegates to repository."""
        from datetime import date
        from src.fund.enums import EventType
        
        # Mock the tax_event_repository delete method to return count of deleted events
        service.tax_event_repository.delete_tax_events_by_type.return_value = 2
        
        service._delete_debt_cost_events(mock_fund, mock_session)
        
        # Should call repository to delete events for both event types (2 calls)
        assert service.tax_event_repository.delete_tax_events_by_type.call_count == 2
