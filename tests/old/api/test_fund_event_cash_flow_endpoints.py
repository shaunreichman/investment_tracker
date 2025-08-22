import pytest
from datetime import datetime, date
from tests.factories import (
    FundEventCashFlowFactory, FundEventFactory, FundFactory, 
    BankAccountFactory, EntityFactory, BankFactory
)
from src.fund.models import FundEventCashFlow, EventType, CashFlowDirection


class TestFundEventCashFlowEndpoints:
    """Test API endpoints for fund event cash flow CRUD operations"""

    def test_get_fund_event_cash_flows_success(self, client, db_session):
        """Test successful retrieval of cash flows for a specific fund event"""
        # Create test data
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund, event_type=EventType.DISTRIBUTION)
        account = BankAccountFactory.create()
        
        cash_flow1 = FundEventCashFlowFactory.create(
            fund_event=event, bank_account=account, amount=1000.0
        )
        cash_flow2 = FundEventCashFlowFactory.create(
            fund_event=event, bank_account=account, amount=500.0
        )
        
        response = client.get(f'/api/funds/{fund.id}/events/{event.id}/cash-flows')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'fund_id' in data
        assert 'event_id' in data
        assert 'event_type' in data
        assert 'event_date' in data
        assert 'event_amount' in data
        assert 'is_cash_flow_complete' in data
        assert 'cash_flows' in data
        assert len(data['cash_flows']) == 2
        
        # Verify cash flow data structure
        cf_data = data['cash_flows'][0]
        assert 'id' in cf_data
        assert 'bank_account_id' in cf_data
        assert 'bank_name' in cf_data
        assert 'account_name' in cf_data
        assert 'direction' in cf_data
        assert 'transfer_date' in cf_data
        assert 'currency' in cf_data
        assert 'amount' in cf_data
        assert 'reference' in cf_data
        assert 'notes' in cf_data

    def test_get_fund_event_cash_flows_empty(self, client, db_session):
        """Test GET cash flows when no cash flows exist for the event"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        
        response = client.get(f'/api/funds/{fund.id}/events/{event.id}/cash-flows')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'cash_flows' in data
        assert len(data['cash_flows']) == 0

    def test_get_fund_event_cash_flows_fund_not_found(self, client, db_session):
        """Test GET cash flows with non-existent fund ID"""
        response = client.get('/api/funds/99999/events/1/cash-flows')
        
        assert response.status_code == 404
        assert "Fund not found" in response.get_json()['error']

    def test_get_fund_event_cash_flows_event_not_found(self, client, db_session):
        """Test GET cash flows with non-existent event ID"""
        fund = FundFactory.create()
        
        response = client.get(f'/api/funds/{fund.id}/events/99999/cash-flows')
        
        assert response.status_code == 404
        assert "Fund event not found" in response.get_json()['error']

    def test_get_fund_event_cash_flows_event_wrong_fund(self, client, db_session):
        """Test GET cash flows when event belongs to different fund"""
        fund1 = FundFactory.create()
        fund2 = FundFactory.create()
        event = FundEventFactory.create(fund=fund2)
        
        response = client.get(f'/api/funds/{fund1.id}/events/{event.id}/cash-flows')
        
        assert response.status_code == 404
        assert "Fund event not found" in response.get_json()['error']

    def test_add_fund_event_cash_flow_success(self, client, db_session):
        """Test successful cash flow addition to a fund event"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund, event_type=EventType.DISTRIBUTION)
        account = BankAccountFactory.create(currency="AUD")
        
        cash_flow_data = {
            "bank_account_id": account.id,
            "transfer_date": "2024-01-15",
            "currency": "AUD",
            "amount": 1000.0,
            "reference": "REF-123",
            "notes": "Test cash flow"
        }
        
        # Store IDs before API call to avoid detached instance issues
        fund_id = fund.id
        event_id = event.id
        account_id = account.id
        
        response = client.post(f'/api/funds/{fund_id}/events/{event_id}/cash-flows', 
                             json=cash_flow_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['fund_event_id'] == event_id
        assert data['bank_account_id'] == account_id
        assert data['amount'] == 1000.0
        assert data['currency'] == "AUD"
        assert data['reference'] == "REF-123"
        assert data['notes'] == "Test cash flow"
        assert 'message' in data
        
        # Verify cash flow was created in database
        cash_flow = db_session.query(FundEventCashFlow).filter(
            FundEventCashFlow.fund_event_id == event_id
        ).first()
        assert cash_flow is not None
        assert cash_flow.amount == 1000.0
        assert cash_flow.currency == "AUD"

    def test_add_fund_event_cash_flow_missing_required_fields(self, client, db_session):
        """Test cash flow addition with missing required fields"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        account = BankAccountFactory.create()
        
        # Missing bank_account_id
        cash_flow_data = {
            "transfer_date": "2024-01-15",
            "currency": "AUD",
            "amount": 1000.0
        }
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', 
                             json=cash_flow_data)
        assert response.status_code == 400
        assert "Missing required field: bank_account_id" in response.get_json()['error']
        
        # Missing transfer_date
        cash_flow_data = {
            "bank_account_id": account.id,
            "currency": "AUD",
            "amount": 1000.0
        }
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', 
                             json=cash_flow_data)
        assert response.status_code == 400
        assert "Missing required field: transfer_date" in response.get_json()['error']

    def test_add_fund_event_cash_flow_empty_data(self, client, db_session):
        """Test cash flow addition with empty data"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', json={})
        assert response.status_code == 400
        assert "No data provided" in response.get_json()['error']

    def test_add_fund_event_cash_flow_fund_not_found(self, client, db_session):
        """Test cash flow addition with non-existent fund ID"""
        account = BankAccountFactory.create()
        
        cash_flow_data = {
            "bank_account_id": account.id,
            "transfer_date": "2024-01-15",
            "currency": "AUD",
            "amount": 1000.0
        }
        
        response = client.post('/api/funds/99999/events/1/cash-flows', json=cash_flow_data)
        assert response.status_code == 404
        assert "Fund not found" in response.get_json()['error']

    def test_add_fund_event_cash_flow_event_not_found(self, client, db_session):
        """Test cash flow addition with non-existent event ID"""
        fund = FundFactory.create()
        account = BankAccountFactory.create()
        
        cash_flow_data = {
            "bank_account_id": account.id,
            "transfer_date": "2024-01-15",
            "currency": "AUD",
            "amount": 1000.0
        }
        
        response = client.post(f'/api/funds/{fund.id}/events/99999/cash-flows', json=cash_flow_data)
        assert response.status_code == 404
        assert "Fund event not found" in response.get_json()['error']

    def test_add_fund_event_cash_flow_bank_account_not_found(self, client, db_session):
        """Test cash flow addition with non-existent bank account ID"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        
        cash_flow_data = {
            "bank_account_id": 99999,
            "transfer_date": "2024-01-15",
            "currency": "AUD",
            "amount": 1000.0
        }
        
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', 
                             json=cash_flow_data)
        assert response.status_code == 404
        assert "Bank account not found" in response.get_json()['error']

    def test_add_fund_event_cash_flow_currency_mismatch(self, client, db_session):
        """Test cash flow addition with currency mismatch"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        account = BankAccountFactory.create(currency="AUD")
        
        cash_flow_data = {
            "bank_account_id": account.id,
            "transfer_date": "2024-01-15",
            "currency": "USD",  # Different from account currency
            "amount": 1000.0
        }
        
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', 
                             json=cash_flow_data)
        assert response.status_code == 400
        assert "Cash flow currency must match bank account currency" in response.get_json()['error']

    def test_add_fund_event_cash_flow_invalid_date_format(self, client, db_session):
        """Test cash flow addition with invalid date format"""
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        account = BankAccountFactory.create()
        
        cash_flow_data = {
            "bank_account_id": account.id,
            "transfer_date": "invalid-date",
            "currency": "AUD",
            "amount": 1000.0
        }
        
        response = client.post(f'/api/funds/{fund.id}/events/{event.id}/cash-flows', 
                             json=cash_flow_data)
        assert response.status_code == 400
        assert "Invalid transfer_date format" in response.get_json()['error']

    def test_get_cash_flows_success(self, client, db_session):
        """Test successful retrieval of all cash flows with filtering"""
        # Create test data
        fund = FundFactory.create()
        event = FundEventFactory.create(fund=fund)
        account = BankAccountFactory.create(currency="AUD")
        
        cash_flow1 = FundEventCashFlowFactory.create(
            fund_event=event, bank_account=account, amount=1000.0,
            transfer_date=date(2024, 1, 15)
        )
        cash_flow2 = FundEventCashFlowFactory.create(
            fund_event=event, bank_account=account, amount=500.0,
            transfer_date=date(2024, 1, 20)
        )
        
        response = client.get('/api/cash-flows')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'cash_flows' in data
        assert len(data['cash_flows']) == 2
        
        # Verify cash flow data structure
        cf_data = data['cash_flows'][0]
        assert 'id' in cf_data
        assert 'fund_event_id' in cf_data
        assert 'fund_id' in cf_data
        assert 'fund_name' in cf_data
        assert 'event_type' in cf_data
        assert 'event_date' in cf_data
        assert 'bank_account_id' in cf_data
        assert 'bank_name' in cf_data
        assert 'account_name' in cf_data
        assert 'direction' in cf_data
        assert 'transfer_date' in cf_data
        assert 'currency' in cf_data
        assert 'amount' in cf_data
        assert 'reference' in cf_data
        assert 'notes' in cf_data

    def test_get_cash_flows_with_filters(self, client, db_session):
        """Test GET cash flows with various filters"""
        # Create test data
        fund1 = FundFactory.create()
        fund2 = FundFactory.create()
        event1 = FundEventFactory.create(fund=fund1)
        event2 = FundEventFactory.create(fund=fund2)
        account1 = BankAccountFactory.create(currency="AUD")
        account2 = BankAccountFactory.create(currency="USD")
        
        # Store IDs before API calls to avoid detached instance issues
        fund1_id = fund1.id
        fund2_id = fund2.id
        event1_id = event1.id
        event2_id = event2.id
        account1_id = account1.id
        account2_id = account2.id
        
        cash_flow1 = FundEventCashFlowFactory.create(
            fund_event=event1, bank_account=account1, currency="AUD",
            transfer_date=date(2024, 1, 15)
        )
        cash_flow2 = FundEventCashFlowFactory.create(
            fund_event=event2, bank_account=account2, currency="USD",
            transfer_date=date(2024, 1, 20)
        )
        
        # Ensure data is committed to the session
        db_session.commit()
        
        # Test fund filter
        response = client.get(f'/api/cash-flows?fund_id={fund1_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cash_flows']) == 1
        assert data['cash_flows'][0]['fund_id'] == fund1_id
        
        # Test bank account filter
        response = client.get(f'/api/cash-flows?bank_account_id={account1_id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cash_flows']) == 1
        assert data['cash_flows'][0]['bank_account_id'] == account1_id
        
        # Test currency filter
        response = client.get('/api/cash-flows?currency=AUD')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cash_flows']) == 1
        assert data['cash_flows'][0]['currency'] == "AUD"
        
        # Test date range filters
        response = client.get('/api/cash-flows?start_date=2024-01-16&end_date=2024-01-25')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['cash_flows']) == 1
        assert data['cash_flows'][0]['transfer_date'] == "2024-01-20"

    def test_get_cash_flows_invalid_date_format(self, client, db_session):
        """Test GET cash flows with invalid date format"""
        response = client.get('/api/cash-flows?start_date=invalid-date')
        assert response.status_code == 400
        assert "Invalid start_date format" in response.get_json()['error']
        
        response = client.get('/api/cash-flows?end_date=invalid-date')
        assert response.status_code == 400
        assert "Invalid end_date format" in response.get_json()['error']

    def test_get_cash_flows_empty(self, client, db_session):
        """Test GET cash flows when no cash flows exist"""
        response = client.get('/api/cash-flows')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'cash_flows' in data
        assert len(data['cash_flows']) == 0
