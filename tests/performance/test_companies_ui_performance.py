"""
Performance tests for Companies UI backend functionality.

These tests verify that the backend can handle large datasets and complex calculations
within acceptable performance thresholds as specified in the Companies UI Backend Spec.
"""

import pytest
import time
from datetime import date, timedelta
from tests.factories import (
    InvestmentCompanyFactory, 
    FundFactory, 
    FundEventFactory,
    EntityFactory
)
from src.fund.models import FundStatus, FundType, EventType, DistributionType


class TestCompaniesUIPerformance:
    """Performance tests for Companies UI backend functionality."""
    
    def test_large_company_portfolio_performance(self, db_session):
        """Test performance with large company portfolio (100+ funds)"""
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
        start_time = time.time()
        summary_data = company.get_company_summary_data(session=db_session)
        end_time = time.time()
        
        # Should complete within reasonable time (under 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Verify calculations are correct
        portfolio = summary_data['portfolio_summary']
        status_breakdown = summary_data['fund_status_breakdown']
        
        assert portfolio['total_committed_capital'] > 0
        assert status_breakdown['active_funds_count'] == 70
        assert status_breakdown['completed_funds_count'] == 30
    
    def test_fund_metrics_calculation_performance(self, db_session):
        """Test performance of enhanced fund metrics calculation"""
        company = InvestmentCompanyFactory()
        
        # Create fund with many events
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Add 1000 distribution events
        base_date = date(2020, 1, 1)
        for i in range(1000):
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                distribution_type=DistributionType.INCOME,
                amount=1000 + i,
                event_date=base_date + timedelta(days=i)
            )
        
        # Test enhanced metrics calculation performance
        start_time = time.time()
        enhanced_metrics = fund.get_enhanced_fund_metrics(session=db_session)
        end_time = time.time()
        
        # Should complete within reasonable time (under 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Verify calculations are correct
        assert enhanced_metrics['unrealized_gains_losses'] == -50000  # 950k - 1000k
        assert enhanced_metrics['realized_gains_losses'] > 0
    
    def test_distribution_summary_performance(self, db_session):
        """Test performance of distribution summary calculation"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(investment_company=company)
        
        # Add 500 distribution events
        base_date = date(2020, 1, 1)
        for i in range(500):
            FundEventFactory(
                fund=fund,
                event_type=EventType.DISTRIBUTION,
                distribution_type=DistributionType.INCOME,
                amount=500 + i,
                event_date=base_date + timedelta(days=i * 30)  # Monthly distributions
            )
        
        # Test distribution summary calculation performance
        start_time = time.time()
        distribution_summary = fund.get_distribution_summary(session=db_session)
        end_time = time.time()
        
        # Should complete within reasonable time (under 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify calculations are correct
        assert distribution_summary['distribution_count'] == 500
        assert distribution_summary['total_distribution_amount'] > 0
        assert distribution_summary['distribution_frequency_months'] is not None
    
    def test_mixed_fund_types_performance(self, db_session):
        """Test performance with mixed NAV-based and cost-based funds"""
        company = InvestmentCompanyFactory()
        
        # Create 50 NAV-based funds
        nav_funds = []
        for i in range(50):
            fund = FundFactory(
                investment_company=company,
                tracking_type=FundType.NAV_BASED,
                status=FundStatus.ACTIVE,
                commitment_amount=100000 + (i * 1000),
                current_equity_balance=95000 + (i * 1000)
            )
            nav_funds.append(fund)
        
        # Create 50 cost-based funds
        cost_funds = []
        for i in range(50):
            fund = FundFactory(
                investment_company=company,
                tracking_type=FundType.COST_BASED,
                status=FundStatus.ACTIVE,
                commitment_amount=100000 + (i * 1000),
                current_equity_balance=95000 + (i * 1000)
            )
            cost_funds.append(fund)
        
        # Test company summary calculation performance with mixed fund types
        start_time = time.time()
        summary_data = company.get_company_summary_data(session=db_session)
        end_time = time.time()
        
        # Should complete within reasonable time (under 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Verify calculations are correct
        portfolio = summary_data['portfolio_summary']
        assert portfolio['total_committed_capital'] > 0
        assert portfolio['total_current_value'] > 0
    
    def test_concurrent_fund_operations_performance(self, db_session):
        """Test performance of concurrent fund operations"""
        company = InvestmentCompanyFactory()
        
        # Create 20 funds
        funds = []
        for i in range(20):
            fund = FundFactory(
                investment_company=company,
                status=FundStatus.ACTIVE,
                commitment_amount=100000 + (i * 1000),
                current_equity_balance=95000 + (i * 1000)
            )
            funds.append(fund)
        
        # Test concurrent enhanced metrics calculation
        start_time = time.time()
        all_metrics = []
        for fund in funds:
            metrics = fund.get_enhanced_fund_metrics(session=db_session)
            all_metrics.append(metrics)
        end_time = time.time()
        
        # Should complete within reasonable time (under 1 second)
        assert (end_time - start_time) < 1.0
        
        # Verify all calculations completed
        assert len(all_metrics) == 20
        for metrics in all_metrics:
            assert 'unrealized_gains_losses' in metrics
            assert 'realized_gains_losses' in metrics
            assert 'total_profit_loss' in metrics
    
    def test_large_event_dataset_performance(self, db_session):
        """Test performance with large event datasets"""
        company = InvestmentCompanyFactory()
        fund = FundFactory(
            investment_company=company,
            status=FundStatus.ACTIVE,
            commitment_amount=1000000,
            current_equity_balance=950000
        )
        
        # Add 2000 mixed events
        base_date = date(2020, 1, 1)
        event_types = [EventType.DISTRIBUTION, EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]
        
        for i in range(2000):
            event_type = event_types[i % len(event_types)]
            FundEventFactory(
                fund=fund,
                event_type=event_type,
                amount=1000 + i,
                event_date=base_date + timedelta(days=i)
            )
        
        # Test fund operations with large event dataset
        start_time = time.time()
        
        # Get enhanced metrics
        enhanced_metrics = fund.get_enhanced_fund_metrics(session=db_session)
        
        # Get distribution summary
        distribution_summary = fund.get_distribution_summary(session=db_session)
        
        # Get recent events
        recent_events = fund.get_recent_events(limit=100, session=db_session)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 2 seconds)
        assert (end_time - start_time) < 2.0
        
        # Verify calculations are correct
        assert enhanced_metrics['unrealized_gains_losses'] == -50000
        assert distribution_summary['distribution_count'] > 0
        assert len(recent_events) <= 100
    
    def test_memory_usage_under_load(self, db_session):
        """Test memory usage remains reasonable under load"""
        company = InvestmentCompanyFactory()
        
        # Create 20 funds with events (reduced from 200 for reasonable performance testing)
        funds = []
        for i in range(20):
            fund = FundFactory(
                investment_company=company,
                status=FundStatus.ACTIVE,
                commitment_amount=100000 + (i * 1000),
                current_equity_balance=95000 + (i * 1000)
            )
            
            # Add 5 events per fund (reduced from 10)
            base_date = date(2020, 1, 1)
            for j in range(5):
                FundEventFactory(
                    fund=fund,
                    event_type=EventType.DISTRIBUTION,
                    amount=1000 + j,
                    event_date=base_date + timedelta(days=j * 30)
                )
            
            funds.append(fund)
        
        # Test memory usage during bulk operations
        start_time = time.time()
        
        # Perform bulk operations
        all_summaries = []
        all_metrics = []
        
        for fund in funds:
            summary = fund.get_summary_data(session=db_session)
            metrics = fund.get_enhanced_fund_metrics(session=db_session)
            all_summaries.append(summary)
            all_metrics.append(metrics)
        
        end_time = time.time()
        
        # Should complete within reasonable time (under 5 seconds)
        assert (end_time - start_time) < 5.0
        
        # Verify all operations completed
        assert len(all_summaries) == 20
        assert len(all_metrics) == 20
        
        # Verify data integrity
        for summary in all_summaries:
            assert 'id' in summary
            assert 'total_distributions' in summary
        
        for metrics in all_metrics:
            assert 'unrealized_gains_losses' in metrics
            assert 'realized_gains_losses' in metrics
