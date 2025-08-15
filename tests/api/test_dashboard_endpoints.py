"""
Dashboard API Endpoint Tests

Tests for dashboard-related endpoints:
- /api/dashboard/portfolio-summary
- /api/dashboard/funds  
- /api/dashboard/recent-events
- /api/dashboard/performance
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    InvestmentCompanyFactory, EntityFactory, FundFactory, 
    FundEventFactory, TaxStatementFactory
)


class TestDashboardPortfolioSummary:
    """Test /api/dashboard/portfolio-summary endpoint"""
    
    def test_portfolio_summary_empty_database(self, client, db_session):
        """Test portfolio summary with no data returns zero counts"""
        response = client.get('/api/dashboard/portfolio-summary')
    
        assert response.status_code == 200
        data = response.get_json()
    
        assert data['total_funds'] == 0
        assert data['active_funds'] == 0
        assert data['total_equity_balance'] == 0.0
        assert data['total_average_equity_balance'] == 0.0
        assert data['recent_events_count'] == 0
        assert data['total_tax_statements'] == 0
        assert 'last_updated' in data
    
    def test_portfolio_summary_with_funds(self, client, db_session):
        """Test portfolio summary with ACTIVE and completed funds"""
        # Create test data
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Active fund with events
        ACTIVE_fund = FundFactory(
            investment_company=company,
            entity=entity,
            status='ACTIVE'
        )
        FundEventFactory(
            fund=ACTIVE_fund,
            event_type='CAPITAL_CALL',
            amount=100000.0,
            event_date=date.today() - timedelta(days=30)
        )
        
        # Completed fund
        completed_fund = FundFactory(
            investment_company=company,
            entity=entity,
            status='REALIZED'
        )
        
        # Tax statement
        TaxStatementFactory(fund=ACTIVE_fund)
        
        response = client.get('/api/dashboard/portfolio-summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_funds'] == 2
        assert data['active_funds'] == 1
        assert data['total_tax_statements'] == 1
        assert data['recent_events_count'] >= 1
    
    def test_portfolio_summary_handles_missing_optional_fields(self, client, db_session):
        """Test portfolio summary handles funds with missing optional fields"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Fund with minimal data
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            current_equity_balance=None,
            average_equity_balance=None
        )
        
        response = client.get('/api/dashboard/portfolio-summary')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['total_funds'] == 1
        assert data['total_equity_balance'] == 0.0
        assert data['total_average_equity_balance'] == 0.0


class TestDashboardFundsList:
    """Test /api/dashboard/funds endpoint"""
    
    def test_funds_list_empty_database(self, client, db_session):
        """Test funds list with no data returns empty array"""
        response = client.get('/api/dashboard/funds')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)
        assert 'funds' in data
        assert isinstance(data['funds'], list)
        assert len(data['funds']) == 0
    
    def test_funds_list_with_funds(self, client, db_session):
        """Test funds list returns correct fund data"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            name="Test Fund",
            fund_type="SENIOR_DEBT"
        )
        
        # Add some events
        FundEventFactory(
            fund=fund,
            event_type='CAPITAL_CALL',
            amount=50000.0,
            event_date=date.today() - timedelta(days=10)
        )
        
        response = client.get('/api/dashboard/funds')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'funds' in data
        assert len(data['funds']) == 1
        fund_data = data['funds'][0]
        
        assert fund_data['id'] == fund.id
        assert fund_data['name'] == "Test Fund"
        assert fund_data['fund_type'] == "SENIOR_DEBT"
        assert fund_data['recent_events_count'] >= 1
    
    def test_funds_list_includes_required_fields(self, client, db_session):
        """Test funds list includes all required fields"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        response = client.get('/api/dashboard/funds')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'funds' in data
        fund_data = data['funds'][0]
        required_fields = ['id', 'name', 'fund_type', 'tracking_type', 'status']
        
        for field in required_fields:
            assert field in fund_data


class TestDashboardRecentEvents:
    """Test /api/dashboard/recent-events endpoint"""
    
    def test_recent_events_empty_database(self, client, db_session):
        """Test recent events with no data returns empty array"""
        response = client.get('/api/dashboard/recent-events')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert isinstance(data, dict)
        assert 'events' in data
        assert isinstance(data['events'], list)
        assert len(data['events']) == 0
    
    def test_recent_events_with_events(self, client, db_session):
        """Test recent events returns events in correct order"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(investment_company=company, entity=entity)
        
        # Create events with different dates
        old_event = FundEventFactory(
            fund=fund,
            event_type='CAPITAL_CALL',
            amount=100000.0,
            event_date=date.today() - timedelta(days=30)
        )
        
        recent_event = FundEventFactory(
            fund=fund,
            event_type='DISTRIBUTION',
            amount=5000.0,
            event_date=date.today() - timedelta(days=5)
        )
        
        response = client.get('/api/dashboard/recent-events')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'events' in data
        assert len(data['events']) >= 2
        
        # Should be ordered by date (most recent first)
        event_dates = [event['event_date'] for event in data['events']]
        assert event_dates == sorted(event_dates, reverse=True)


class TestDashboardPerformance:
    """Test /api/dashboard/performance endpoint"""
    
    def test_performance_empty_database(self, client, db_session):
        """Test performance endpoint with no data returns empty metrics"""
        response = client.get('/api/dashboard/performance')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'performance' in data
        assert isinstance(data['performance'], list)
        assert len(data['performance']) == 0
    
    def test_performance_with_funds(self, client, db_session):
        """Test performance endpoint returns fund performance data"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            current_equity_balance=120000.0
        )
        
        # Add events to calculate performance
        FundEventFactory(
            fund=fund,
            event_type='CAPITAL_CALL',
            amount=100000.0,
            event_date=date.today() - timedelta(days=365)
        )
        
        response = client.get('/api/dashboard/performance')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'performance' in data
        performance_data = data['performance']
        
        if len(performance_data) > 0:
            fund_perf = performance_data[0]
            assert 'fund_id' in fund_perf
            assert 'fund_name' in fund_perf
            assert 'current_equity' in fund_perf
