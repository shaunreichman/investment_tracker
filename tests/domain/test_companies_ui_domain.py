import pytest
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    InvestmentCompanyFactory, FundFactory, FundEventFactory, 
    ContactFactory, EntityFactory
)
from src.fund.models import FundStatus, FundType, EventType, DistributionType
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund


class TestCompanyPortfolioCalculations:
    """Test company portfolio calculation methods"""
    
    def test_get_company_summary_data_empty_portfolio(self, db_session):
        """Test company summary with no funds"""
        company = InvestmentCompanyFactory()
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        # Verify portfolio summary
        portfolio = summary_data['portfolio_summary']
        assert portfolio['total_committed_capital'] == 0
        assert portfolio['total_current_value'] == 0
        assert portfolio['total_invested_capital'] == 0
        
        # Verify fund status breakdown
        status_breakdown = summary_data['fund_status_breakdown']
        assert status_breakdown['active_funds_count'] == 0
        assert status_breakdown['completed_funds_count'] == 0
        assert status_breakdown['suspended_funds_count'] == 0
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == 0
        assert portfolio['completed_funds_count'] == 0
        
        # Verify performance summary
        performance = summary_data['performance_summary']
        assert performance['average_completed_irr'] is None
        assert performance['total_realized_gains'] == 0
        assert performance['total_realized_losses'] == 0
    
    def test_get_company_summary_data_single_fund(self, db_session):
        """Test company summary with single fund"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        portfolio = summary_data['portfolio_summary']
        assert portfolio['total_committed_capital'] == 100000
        assert portfolio['total_current_value'] == 95000
        assert portfolio['total_invested_capital'] == 95000
        
        status_breakdown = summary_data['fund_status_breakdown']
        assert status_breakdown['active_funds_count'] == 1
        assert status_breakdown['completed_funds_count'] == 0
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == 1
        assert portfolio['completed_funds_count'] == 0
    
    def test_get_company_summary_data_multiple_funds(self, db_session):
        """Test company summary with multiple funds"""
        company = InvestmentCompanyFactory()
        
        # Active fund
        fund1 = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        # Completed fund
        fund2 = FundFactory(
            investment_company=company,
            status=FundStatus.COMPLETED,
            commitment_amount=200000,
            current_equity_balance=220000,
            irr_gross=15.5
        )
        
        # Suspended fund
        fund3 = FundFactory(
            investment_company=company,
            status=FundStatus.REALIZED,
            commitment_amount=150000,
            current_equity_balance=140000
        )
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        portfolio = summary_data['portfolio_summary']
        assert portfolio['total_committed_capital'] == 450000
        assert portfolio['total_current_value'] == 455000
        assert portfolio['total_invested_capital'] == 455000
        
        status_breakdown = summary_data['fund_status_breakdown']
        assert status_breakdown['active_funds_count'] == 1
        assert status_breakdown['completed_funds_count'] == 1
        assert status_breakdown['realized_funds_count'] == 1  # Note: this fund has REALIZED status, not suspended
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == 1
        assert portfolio['completed_funds_count'] == 1
        
        performance = summary_data['performance_summary']
        assert performance['average_completed_irr'] == 15.5
    
    def test_get_company_summary_data_mixed_status_funds(self, db_session):
        """Test company summary with mixed status funds"""
        company = InvestmentCompanyFactory()
        
        # Create funds with different statuses and performance
        ACTIVE_funds = []
        completed_funds = []
        
        for i in range(5):
            # Active funds
            fund = FundFactory(
                investment_company=company,
                status=FundStatus.ACTIVE,
                commitment_amount=100000 + i * 10000,
                current_equity_balance=95000 + i * 10000
            )
            ACTIVE_funds.append(fund)
        
        for i in range(3):
            # Completed funds with different IRRs
            fund = FundFactory(
                investment_company=company,
                status=FundStatus.COMPLETED,
                commitment_amount=200000 + i * 50000,
                current_equity_balance=220000 + i * 60000,
                irr_gross=10.0 + i * 5.0  # 10%, 15%, 20%
            )
            completed_funds.append(fund)
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        portfolio = summary_data['portfolio_summary']
        expected_committed = sum(f.commitment_amount for f in ACTIVE_funds + completed_funds)
        expected_current = sum(f.current_equity_balance for f in ACTIVE_funds + completed_funds)
        
        assert portfolio['total_committed_capital'] == expected_committed
        assert portfolio['total_current_value'] == expected_current
        assert portfolio['total_invested_capital'] == expected_current
        
        status_breakdown = summary_data['fund_status_breakdown']
        assert status_breakdown['active_funds_count'] == 5
        assert status_breakdown['completed_funds_count'] == 3
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == 5
        assert portfolio['completed_funds_count'] == 3
        
        performance = summary_data['performance_summary']
        # Average IRR: (10 + 15 + 20) / 3 = 15.0
        assert performance['average_completed_irr'] == 15.0
    
    def test_get_company_summary_data_performance_calculations(self, db_session):
        """Test company performance calculations"""
        company = InvestmentCompanyFactory()
        
        # Create funds with known performance
        fund1 = FundFactory(
            investment_company=company,
            status=FundStatus.COMPLETED,
            commitment_amount=100000,
            current_equity_balance=120000,  # 20% gain
            irr_gross=20.0
        )
        
        fund2 = FundFactory(
            investment_company=company,
            status=FundStatus.COMPLETED,
            commitment_amount=200000,
            current_equity_balance=180000,  # 10% loss
            irr_gross=-10.0
        )
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        performance = summary_data['performance_summary']
        # Average IRR: (20 + (-10)) / 2 = 5.0
        assert performance['average_completed_irr'] == 5.0
        
        # Verify portfolio totals
        portfolio = summary_data['portfolio_summary']
        assert portfolio['total_committed_capital'] == 300000
        assert portfolio['total_current_value'] == 300000  # 120k + 180k
        assert portfolio['total_invested_capital'] == 300000
    
    def test_get_company_summary_data_edge_cases(self, db_session):
        """Test company summary with edge cases"""
        company = InvestmentCompanyFactory()
        
        # Fund with no commitment amount
        fund1 = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=None,
            current_equity_balance=50000
        )
        
        # Fund with no current equity balance
        fund2 = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=None
        )
        
        # Fund with zero values
        fund3 = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=0,
            current_equity_balance=0
        )
        
        summary_data = company.get_company_summary_data(session=db_session)
        
        portfolio = summary_data['portfolio_summary']
        # Should handle None values gracefully
        assert portfolio['total_committed_capital'] == 100000  # 0 + 100k + 0
        assert portfolio['total_current_value'] == 50000      # 50k + 0 + 0
        assert portfolio['total_invested_capital'] == 50000


class TestFundEnhancementMethods:
    """Test fund enhancement calculation methods"""
    
    def test_get_enhanced_fund_metrics_new_fund(self, db_session):
        """Test enhanced metrics for new fund with no events"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        metrics = fund.get_enhanced_fund_metrics()
        
        # New fund should have no realized gains/losses
        assert metrics['unrealized_gains_losses'] == -5000  # 95k - 100k
        assert metrics['realized_gains_losses'] == 0
        assert metrics['total_profit_loss'] == -5000
    
    def test_get_enhanced_fund_metrics_completed_fund(self, db_session):
        """Test enhanced metrics for completed fund"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.COMPLETED,
            commitment_amount=100000,
            current_equity_balance=120000,  # 20% gain
            irr_gross=20.0
        )
        
        metrics = fund.get_enhanced_fund_metrics()
        
        # Completed fund should have realized gains
        assert metrics['unrealized_gains_losses'] == 0  # Completed = no unrealized
        assert metrics['realized_gains_losses'] == 20000  # 120k - 100k
        assert metrics['total_profit_loss'] == 20000
    
    def test_get_enhanced_fund_metrics_with_events(self, db_session):
        """Test enhanced metrics for fund with events"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        # Add some distribution events using proper fund method
        fund.add_distribution(
            event_date=date.today() - timedelta(days=30),
            distribution_type=DistributionType.INCOME,
            distribution_amount=5000,
            session=db_session
        )
        
        fund.add_distribution(
            event_date=date.today() - timedelta(days=60),
            distribution_type=DistributionType.INCOME,
            distribution_amount=3000,
            session=db_session
        )
        
        metrics = fund.get_enhanced_fund_metrics()
        
        # Should still show unrealized gains/losses
        assert metrics['unrealized_gains_losses'] == -5000  # 95k - 100k
        assert metrics['realized_gains_losses'] == 0  # Distributions don't affect this calculation
        assert metrics['total_profit_loss'] == -5000
    
    def test_get_distribution_summary_no_distributions(self, db_session):
        """Test distribution summary for fund with no distributions"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(investment_company=company)
        
        summary = fund.get_distribution_summary()
        
        assert summary['distribution_count'] == 0
        assert summary['total_distribution_amount'] == 0
        assert summary['last_distribution_date'] is None
        assert summary['distribution_frequency_months'] is None
    
    def test_get_distribution_summary_multiple_distributions(self, db_session):
        """Test distribution summary for fund with multiple distributions"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(investment_company=company)
        
        # Add distribution events using proper fund method
        fund.add_distribution(
            event_date=date(2023, 1, 15),
            distribution_type=DistributionType.INCOME,
            distribution_amount=5000,
            session=db_session
        )
        
        fund.add_distribution(
            event_date=date(2023, 4, 15),
            distribution_type=DistributionType.INCOME,
            distribution_amount=3000,
            session=db_session
        )
        
        fund.add_distribution(
            event_date=date(2023, 7, 15),
            distribution_type=DistributionType.INCOME,
            distribution_amount=4000,
            session=db_session
        )
        
        # Commit the session to persist the distribution events
        db_session.commit()
        
        summary = fund.get_distribution_summary()
        
        assert summary['distribution_count'] == 3
        assert summary['total_distribution_amount'] == 12000  # 5k + 3k + 4k
        assert summary['last_distribution_date'] == date(2023, 7, 15)
        
        # Frequency: ~3 months between distributions
        assert summary['distribution_frequency_months'] is not None
        assert 2.5 <= summary['distribution_frequency_months'] <= 3.5
    
    def test_get_distribution_summary_frequency_calculation(self, db_session):
        """Test distribution frequency calculation accuracy"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(investment_company=company)
        
        # Create distributions with known intervals
        base_date = date(2023, 1, 1)
        
        for i in range(6):  # 6 distributions
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                distribution_type=DistributionType.INCOME,
                amount=1000,
                event_date=base_date + timedelta(days=i * 90)  # Every 90 days = 3 months
            )
        
        summary = fund.get_distribution_summary()
        
        assert summary['distribution_count'] == 6
        assert summary['total_distribution_amount'] == 6000
        
        # Should calculate ~3 months frequency
        frequency = summary['distribution_frequency_months']
        assert frequency is not None
        assert 2.8 <= frequency <= 3.2  # Allow small rounding differences
    
    def test_fund_activity_tracking(self, db_session):
        """Test fund activity tracking calculations"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(investment_company=company)
        
        # Add events with different dates
        FundEventFactory(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            event_date=date.today() - timedelta(days=30)
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            event_date=date.today() - timedelta(days=10)
        )
        
        # Get enhanced metrics to trigger activity calculation
        metrics = fund.get_enhanced_fund_metrics()
        
        # The activity tracking is done in the API layer, but we can verify
        # that the fund has events and they can be accessed
        assert len(fund.fund_events) == 2
        
        # Verify event dates are accessible
        event_dates = [event.event_date for event in fund.fund_events if event.event_date]
        assert len(event_dates) == 2
        assert max(event_dates) == date.today() - timedelta(days=10)
