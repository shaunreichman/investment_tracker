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


class TestCompaniesUIWorkflows:
    """Test end-to-end Companies UI data workflows"""
    
    def test_company_portfolio_data_consistency(self, db_session):
        """Test that portfolio data is consistent across different calculation methods"""
        company = InvestmentCompanyFactory()
        
        # Create funds with known values
        fund1 = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        fund2 = FundFactory(
            investment_company=company,
            status=FundStatus.COMPLETED,
            commitment_amount=200000,
            current_equity_balance=220000,
            irr_gross=15.5
        )
        
        # Get company summary data
        summary_data = company.get_company_summary_data(session=db_session)
        
        # Verify portfolio totals match individual fund sums
        portfolio = summary_data['portfolio_summary']
        expected_committed = fund1.commitment_amount + fund2.commitment_amount
        expected_current = fund1.current_equity_balance + fund2.current_equity_balance
        
        assert portfolio['total_committed_capital'] == expected_committed
        assert portfolio['total_current_value'] == expected_current
        assert portfolio['total_invested_capital'] == expected_current
        
                # Verify fund status breakdown matches actual fund counts
        status_breakdown = summary_data['fund_status_breakdown']
        ACTIVE_funds = [f for f in company.funds if f.status == FundStatus.ACTIVE]
        completed_funds = [f for f in company.funds if f.status == FundStatus.COMPLETED]
    
        assert status_breakdown['active_funds_count'] == len(ACTIVE_funds)
        assert status_breakdown['completed_funds_count'] == len(completed_funds)
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == len(ACTIVE_funds)
        assert portfolio['completed_funds_count'] == len(completed_funds)
    
    def test_fund_metrics_rollup_to_company(self, db_session):
        """Test that individual fund metrics correctly roll up to company totals"""
        company = InvestmentCompanyFactory()
        
        # Create funds with different performance characteristics
        funds_data = [
            {'status': FundStatus.ACTIVE, 'commitment': 100000, 'current': 95000, 'irr': None},
            {'status': FundStatus.COMPLETED, 'commitment': 200000, 'current': 220000, 'irr': 15.0},
            {'status': FundStatus.COMPLETED, 'commitment': 150000, 'current': 135000, 'irr': 10.0},
            {'status': FundStatus.REALIZED, 'commitment': 300000, 'current': 280000, 'irr': None}
        ]
        
        funds = []
        for fund_data in funds_data:
            fund = FundFactory(
                investment_company=company,
                status=fund_data['status'],
                commitment_amount=fund_data['commitment'],
                current_equity_balance=fund_data['current'],
                irr_gross=fund_data['irr']
            )
            funds.append(fund)
        
        # Get company summary
        summary_data = company.get_company_summary_data(session=db_session)
        
        # Verify portfolio totals
        portfolio = summary_data['portfolio_summary']
        expected_committed = sum(f['commitment'] for f in funds_data)
        expected_current = sum(f['current'] for f in funds_data)
        
        assert portfolio['total_committed_capital'] == expected_committed
        assert portfolio['total_current_value'] == expected_current
        
        # Verify performance calculations
        performance = summary_data['performance_summary']
        completed_funds = [f for f in funds_data if f['irr'] is not None]
        expected_avg_irr = sum(f['irr'] for f in completed_funds) / len(completed_funds)
        
        assert abs(performance['average_completed_irr'] - expected_avg_irr) < 0.01
    
    def test_contact_management_integration(self, db_session):
        """Test contact management integration with company details"""
        company = InvestmentCompanyFactory()
        
        # Create contacts with different information levels
        contact1 = ContactFactory(
            investment_company=company,
            name="John Smith",
            title="Managing Director",
            direct_number="+61 2 1234 5678",
            direct_email="john@company.com",
            notes="Primary contact"
        )
        
        contact2 = ContactFactory(
            investment_company=company,
            name="Jane Doe",
            title="Investment Manager"
            # Minimal contact info
        )
        
        # Verify contacts are properly associated
        assert len(company.contacts) == 2
        assert contact1 in company.contacts
        assert contact2 in company.contacts
        
        # Verify contact data integrity
        assert contact1.investment_company_id == company.id
        assert contact2.investment_company_id == company.id
        
        # Test that contacts can be accessed through company
        company_contacts = company.contacts
        assert len(company_contacts) == 2
        
        # Verify contact details are accessible
        john_contact = next(c for c in company_contacts if c.name == "John Smith")
        assert john_contact.title == "Managing Director"
        assert john_contact.direct_number == "+61 2 1234 5678"
        assert john_contact.notes == "Primary contact"
    
    def test_fund_status_transition_impact(self, db_session):
        """Test how fund status transitions affect company portfolio calculations"""
        company = InvestmentCompanyFactory()
        
        # Create an ACTIVE fund
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        # Get initial company summary
        initial_summary = company.get_company_summary_data(session=db_session)
        initial_portfolio = initial_summary['portfolio_summary']
        initial_status = initial_summary['fund_status_breakdown']
        
        assert initial_portfolio['total_committed_capital'] == 100000
        assert initial_status['active_funds_count'] == 1
        assert initial_portfolio['active_funds_count'] == 1
        assert initial_portfolio['completed_funds_count'] == 0
        
        # Transition fund to completed status
        fund.status = FundStatus.COMPLETED
        fund.irr_gross = 12.5
        db_session.flush()
        
        # Get updated company summary
        updated_summary = company.get_company_summary_data(session=db_session)
        updated_portfolio = updated_summary['portfolio_summary']
        updated_status = updated_summary['fund_status_breakdown']
        
        # Portfolio totals should remain the same
        assert updated_portfolio['total_committed_capital'] == initial_portfolio['total_committed_capital']
        assert updated_portfolio['total_current_value'] == initial_portfolio['total_current_value']
        
        # Status breakdown should change
        assert updated_status['active_funds_count'] == 0
        assert updated_status['completed_funds_count'] == 1
        assert updated_portfolio['active_funds_count'] == 0
        assert updated_portfolio['completed_funds_count'] == 1
        
        # Performance summary should now include IRR
        performance = updated_summary['performance_summary']
        assert performance['average_completed_irr'] == 12.5
    
    def test_large_portfolio_performance(self, db_session):
        """Test performance with large portfolio scenarios"""
        company = InvestmentCompanyFactory()
        
        # Create 100 funds with varying characteristics
        funds = []
        for i in range(100):
            status = FundStatus.ACTIVE if i < 70 else FundStatus.COMPLETED
            commitment = 100000 + (i * 1000)
            current = 95000 + (i * 1000)
            irr = 10.0 + (i * 0.5) if status == FundStatus.COMPLETED else None
            
            fund = FundFactory(
                investment_company=company,
                status=status,
                commitment_amount=commitment,
                current_equity_balance=current,
                irr_gross=irr
            )
            funds.append(fund)
        
        # Test company summary calculation performance
        start_time = pytest.importorskip('time').time()
        summary_data = company.get_company_summary_data(session=db_session)
        end_time = pytest.importorskip('time').time()
        
        # Should complete within reasonable time (under 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify calculations are correct
        portfolio = summary_data['portfolio_summary']
        status_breakdown = summary_data['fund_status_breakdown']
        
        assert status_breakdown['active_funds_count'] == 70
        assert status_breakdown['completed_funds_count'] == 30
        
        # Verify individual counts in portfolio summary
        assert portfolio['active_funds_count'] == 70
        assert portfolio['completed_funds_count'] == 30
        
        # Verify portfolio totals
        expected_committed = sum(f.commitment_amount for f in funds)
        expected_current = sum(f.current_equity_balance for f in funds)
        
        assert portfolio['total_committed_capital'] == expected_committed
        assert portfolio['total_current_value'] == expected_current
        
        # Verify performance calculations
        performance = summary_data['performance_summary']
        completed_funds = [f for f in funds if f.status == FundStatus.COMPLETED]
        expected_avg_irr = sum(f.irr_gross for f in completed_funds) / len(completed_funds)
        
        assert abs(performance['average_completed_irr'] - expected_avg_irr) < 0.01
    
    def test_fund_event_impact_on_metrics(self, db_session):
        """Test how fund events affect enhanced fund metrics"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        # Get initial enhanced metrics
        initial_metrics = fund.get_enhanced_fund_metrics()
        initial_distribution = fund.get_distribution_summary()
        
        assert initial_metrics['unrealized_gains_losses'] == -5000  # 95k - 100k
        assert initial_distribution['distribution_count'] == 0
        
        # Add distribution events
        FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            distribution_type=DistributionType.INCOME,
            amount=5000,
            event_date=date.today() - timedelta(days=30)
        )
        
        FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            distribution_type=DistributionType.INCOME,
            amount=3000,
            event_date=date.today() - timedelta(days=15)
        )
        
        # Refresh fund to get updated events
        db_session.refresh(fund)
        
        # Get updated metrics
        updated_metrics = fund.get_enhanced_fund_metrics()
        updated_distribution = fund.get_distribution_summary()
        
        # Enhanced metrics should remain the same (distributions don't affect unrealized gains)
        assert updated_metrics['unrealized_gains_losses'] == initial_metrics['unrealized_gains_losses']
        
        # Distribution summary should be updated
        assert updated_distribution['distribution_count'] == 2
        assert updated_distribution['total_distribution_amount'] == 8000  # 5k + 3k
        assert updated_distribution['last_distribution_date'] == date.today() - timedelta(days=15)
    
    def test_data_consistency_across_endpoints(self, db_session):
        """Test that data is consistent when accessed through different API endpoints"""
        company = InvestmentCompanyFactory()
        
        # Create funds with known data
        fund1 = FundFactory(
            investment_company=company,
            name="Fund Alpha",
            status=FundStatus.ACTIVE,
            commitment_amount=100000,
            current_equity_balance=95000
        )
        
        fund2 = FundFactory(
            investment_company=company,
            name="Fund Beta",
            status=FundStatus.COMPLETED,
            commitment_amount=200000,
            current_equity_balance=220000,
            irr_gross=15.5
        )
        
        # Test data consistency between company summary and individual fund data
        company_summary = company.get_company_summary_data(session=db_session)
        
        # Verify fund1 data consistency
        fund1_enhanced = fund1.get_enhanced_fund_metrics()
        fund1_distribution = fund1.get_distribution_summary()
        
        # Company portfolio should include fund1 data
        portfolio = company_summary['portfolio_summary']
        assert portfolio['total_committed_capital'] >= fund1.commitment_amount
        assert portfolio['total_current_value'] >= fund1.current_equity_balance
        
        # Fund1 metrics should be consistent
        assert fund1_enhanced['unrealized_gains_losses'] == fund1.current_equity_balance - fund1.commitment_amount
        
        # Verify fund2 data consistency
        fund2_enhanced = fund2.get_enhanced_fund_metrics()
        
        # Completed fund should have realized gains
        assert fund2_enhanced['realized_gains_losses'] == fund2.current_equity_balance - fund2.commitment_amount
        assert fund2_enhanced['unrealized_gains_losses'] == 0  # Completed = no unrealized
    
    def test_error_handling_in_calculations(self, db_session):
        """Test error handling in portfolio calculations"""
        company = InvestmentCompanyFactory()
        
        # Create fund with problematic data
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=None,  # Missing commitment
            current_equity_balance=None  # Missing current balance
        )
        
        # Should handle missing data gracefully
        try:
            summary_data = company.get_company_summary_data(session=db_session)
            
            portfolio = summary_data['portfolio_summary']
            # Should default to 0 for missing values
            assert portfolio['total_committed_capital'] == 0
            assert portfolio['total_current_value'] == 0
            assert portfolio['total_invested_capital'] == 0
            
        except Exception as e:
            # If calculation fails, it should fail gracefully with meaningful error
            assert "calculation" in str(e).lower() or "data" in str(e).lower()
        
        # Test with zero values
        fund.commitment_amount = 0
        fund.current_equity_balance = 0
        db_session.flush()
        
        summary_data = company.get_company_summary_data(session=db_session)
        portfolio = summary_data['portfolio_summary']
        
        assert portfolio['total_committed_capital'] == 0
        assert portfolio['total_current_value'] == 0
        assert portfolio['total_invested_capital'] == 0
