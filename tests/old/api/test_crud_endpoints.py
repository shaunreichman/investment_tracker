"""
CRUD API Endpoint Tests

Tests for create, read, update, delete operations:
- Investment companies
- Entities  
- Funds
- Fund events
- Tax statements
"""

import pytest
import json
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    InvestmentCompanyFactory, EntityFactory, FundFactory, 
    FundEventFactory, TaxStatementFactory
)
from src.investment_company.models import InvestmentCompany


class TestInvestmentCompanyCRUD:
    """Test investment company CRUD operations"""
    
    def test_get_investment_companies_empty(self, client):
        """Test GET /api/investment-companies with no data"""
        response = client.get('/api/investment-companies')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'companies' in data
        assert isinstance(data['companies'], list)
        assert len(data['companies']) == 0
    
    def test_get_investment_companies_with_data(self, client, db_session):
        """Test GET /api/investment-companies returns companies"""
        company1 = InvestmentCompanyFactory.create(name="Company A")
        company2 = InvestmentCompanyFactory.create(name="Company B")
        
        response = client.get('/api/investment-companies')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'companies' in data
        assert len(data['companies']) == 2
        
        company_names = [c['name'] for c in data['companies']]
        assert "Company A" in company_names
        assert "Company B" in company_names
    
    def test_create_investment_company_success(self, client):
        """Test POST /api/investment-companies creates company"""
        company_data = {
            "name": "New Company",
            "description": "Test company description",
            "website": "https://testcompany.com"
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['name'] == "New Company"
        assert data['description'] == "Test company description"
        assert data['website'] == "https://testcompany.com"
        assert 'id' in data
    
    def test_create_investment_company_missing_required_fields(self, client):
        """Test POST /api/investment-companies validates required fields"""
        company_data = {
            "abn": "12345678901"
            # Missing name
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_investment_company_invalid_json(self, client):
        """Test POST /api/investment-companies handles invalid JSON"""
        response = client.post(
            '/api/investment-companies',
            data="invalid json",
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestEntityCRUD:
    """Test entity CRUD operations"""
    
    def test_get_entities_empty(self, client):
        """Test GET /api/entities with no data"""
        response = client.get('/api/entities')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'entities' in data
        assert isinstance(data['entities'], list)
        assert len(data['entities']) == 0
    
    def test_get_entities_with_data(self, client, db_session):
        """Test GET /api/entities returns entities"""
        entity1 = EntityFactory(name="Entity A")
        entity2 = EntityFactory(name="Entity B")
        
        response = client.get('/api/entities')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'entities' in data
        assert len(data['entities']) == 2
        
        entity_names = [e['name'] for e in data['entities']]
        assert "Entity A" in entity_names
        assert "Entity B" in entity_names
    
    def test_create_entity_success(self, client):
        """Test POST /api/entities creates entity"""
        entity_data = {
            "name": "New Entity",
            "description": "Test entity description",
            "tax_jurisdiction": "AU"
        }
        
        response = client.post(
            '/api/entities',
            data=json.dumps(entity_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['name'] == "New Entity"
        assert data['description'] == "Test entity description"
        assert data['tax_jurisdiction'] == "AU"
        assert 'id' in data
    
    def test_create_entity_missing_required_fields(self, client):
        """Test POST /api/entities validates required fields"""
        entity_data = {
            "abn": "98765432109"
            # Missing name
        }
        
        response = client.post(
            '/api/entities',
            data=json.dumps(entity_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestFundCRUD:
    """Test fund CRUD operations"""
    
    def test_get_company_funds_empty(self, client, db_session):
        """Test GET /api/companies/{id}/funds with no funds"""
        company = InvestmentCompanyFactory()
        
        response = client.get(f'/api/companies/{company.id}/funds')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'funds' in data
        assert isinstance(data['funds'], list)
        assert len(data['funds']) == 0
    
    def test_get_company_funds_with_data(self, client, db_session):
        """Test GET /api/companies/{id}/funds returns funds"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund1 = FundFactory(
            investment_company=company,
            entity=entity,
            name="Fund A"
        )
        fund2 = FundFactory(
            investment_company=company,
            entity=entity,
            name="Fund B"
        )
        
        response = client.get(f'/api/companies/{company.id}/funds')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'funds' in data
        assert len(data['funds']) == 2
        
        fund_names = [f['name'] for f in data['funds']]
        assert "Fund A" in fund_names
        assert "Fund B" in fund_names
    
    def test_get_fund_detail(self, client, db_session):
        """Test GET /api/funds/{id} returns fund details"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            name="Test Fund"
        )
        
        response = client.get(f'/api/funds/{fund.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        
        # Check the nested structure matches the API response
        assert 'fund' in data
        assert 'events' in data
        assert 'tax_statements' in data
        assert 'statistics' in data
        
        # Check fund details are in the fund object
        fund_data = data['fund']
        assert fund_data['id'] == fund.id
        assert fund_data['name'] == "Test Fund"
        assert 'investment_company' in fund_data
        assert 'entity' in fund_data
    
    def test_get_fund_detail_not_found(self, client):
        """Test GET /api/funds/{id} returns 404 for non-existent fund"""
        response = client.get('/api/funds/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_create_fund_success(self, client, db_session):
        """Test POST /api/funds creates fund"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        fund_data = {
            "name": "New Fund",
            "fund_type": "SENIOR_DEBT",
            "tracking_type": "COST_BASED",
            "investment_company_id": company.id,
            "entity_id": entity.id,
            "commitment_amount": 1000000.0
        }
        
        response = client.post(
            '/api/funds',
            data=json.dumps(fund_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['name'] == "New Fund"
        assert data['fund_type'] == "SENIOR_DEBT"
        assert data['tracking_type'] == "COST_BASED"
        assert 'id' in data
    
    def test_create_fund_missing_required_fields(self, client):
        """Test POST /api/funds validates required fields"""
        fund_data = {
            "name": "New Fund"
            # Missing required fields
        }
        
        response = client.post(
            '/api/funds',
            data=json.dumps(fund_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestFundEventCRUD:
    """Test fund event CRUD operations"""
    
    def test_create_fund_event_success(self, client, db_session):
        """Test POST /api/funds/{id}/events creates event"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        event_data = {
            "event_type": "CAPITAL_CALL",
            "amount": 100000.0,
            "event_date": date.today().isoformat(),
            "description": "Initial capital call"
        }
        
        response = client.post(
            f'/api/funds/{fund.id}/events',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['event_type'] == "CAPITAL_CALL"
        assert data['amount'] == 100000.0
        assert data['description'] == "Initial capital call"
        assert 'id' in data
    
    def test_create_fund_event_invalid_event_type(self, client, db_session):
        """Test POST /api/funds/{id}/events validates event type"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        event_data = {
            "event_type": "INVALID_TYPE",
            "amount": 100000.0,
            "event_date": date.today().isoformat()
        }
        
        response = client.post(
            f'/api/funds/{fund.id}/events',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_create_fund_event_fund_not_found(self, client):
        """Test POST /api/funds/{id}/events returns 404 for non-existent fund"""
        event_data = {
            "event_type": "CAPITAL_CALL",
            "amount": 100000.0,
            "event_date": date.today().isoformat()
        }
        
        response = client.post(
            '/api/funds/99999/events',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
    
    def test_delete_fund_event_success(self, client, db_session):
        """Test DELETE /api/funds/{id}/events/{event_id} deletes event"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        event = FundEventFactory(
            fund=fund,
            event_type='CAPITAL_CALL',
            amount=100000.0
        )
        
        response = client.delete(f'/api/funds/{fund.id}/events/{event.id}')
    
        assert response.status_code == 204  # DELETE operations return 204 No Content
        # 204 No Content means no response body, so we don't check response data
    
    def test_delete_fund_event_not_found(self, client, db_session):
        """Test DELETE /api/funds/{id}/events/{event_id} returns 404 for non-existent event"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        response = client.delete(f'/api/funds/{fund.id}/events/99999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data


class TestTaxStatementCRUD:
    """Test tax statement CRUD operations"""
    
    def test_create_tax_statement_success(self, client, db_session):
        """Test POST /api/funds/{id}/tax-statements creates tax statement"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        tax_data = {
            "entity_id": entity.id,
            "financial_year": "2024",
            "eofy_debt_interest_deduction_rate": 30.0,
            "statement_date": date.today().isoformat()
        }
        
        response = client.post(
            f'/api/funds/{fund.id}/tax-statements',
            data=json.dumps(tax_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert data['financial_year'] == "2024"
        assert data['entity_id'] == entity.id
        assert data['eofy_debt_interest_deduction_rate'] == 30.0
        assert 'id' in data
    
    def test_get_fund_tax_statements(self, client, db_session):
        """Test GET /api/funds/{id}/tax-statements returns tax statements"""
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        TaxStatementFactory(
            fund=fund,
            financial_year="2023"
        )
        TaxStatementFactory(
            fund=fund,
            financial_year="2024"
        )
        
        response = client.get(f'/api/funds/{fund.id}/tax-statements')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'tax_statements' in data
        assert len(data['tax_statements']) == 2
        
        years = [ts['financial_year'] for ts in data['tax_statements']]
        assert "2023" in years
        assert "2024" in years
