import pytest
from datetime import datetime
from tests.factories import BankAccountFactory, BankFactory, EntityFactory
from src.banking.models import BankAccount


class TestBankAccountEndpoints:
    """Test API endpoints for bank account CRUD operations"""

    def test_get_bank_accounts_success(self, client, db_session):
        """Test successful retrieval of all bank accounts"""
        # Create test accounts
        account1 = BankAccountFactory.create(account_name="Account 1", currency="AUD")
        account2 = BankAccountFactory.create(account_name="Account 2", currency="USD")
        
        response = client.get('/api/bank-accounts')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'bank_accounts' in data
        assert len(data['bank_accounts']) == 2
        
        # Verify account data structure
        account_data = data['bank_accounts'][0]
        assert 'id' in account_data
        assert 'entity_id' in account_data
        assert 'bank_id' in account_data
        assert 'bank_name' in account_data
        assert 'account_name' in account_data
        assert 'account_number' in account_data
        assert 'currency' in account_data
        assert 'is_active' in account_data
        
        # Verify specific data
        account_names = [a['account_name'] for a in data['bank_accounts']]
        assert "Account 1" in account_names
        assert "Account 2" in account_names

    def test_get_bank_accounts_empty(self, client, db_session):
        """Test GET bank accounts when no accounts exist"""
        response = client.get('/api/bank-accounts')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'bank_accounts' in data
        assert len(data['bank_accounts']) == 0

    def test_get_bank_accounts_with_filters(self, client, db_session):
        """Test GET bank accounts with various filters"""
        # Create test data
        entity1 = EntityFactory.create()
        entity2 = EntityFactory.create()
        bank1 = BankFactory.create()
        bank2 = BankFactory.create()
        
        account1 = BankAccountFactory.create(
            entity=entity1, bank=bank1, currency="AUD", is_active=True
        )
        account2 = BankAccountFactory.create(
            entity=entity2, bank=bank2, currency="USD", is_active=False
        )
        
        # Ensure data is committed to the session
        db_session.commit()
        
        # Test entity filter
        response = client.get(f'/api/bank-accounts?entity_id={entity1.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['bank_accounts']) == 1
        assert data['bank_accounts'][0]['entity_id'] == entity1.id
        
        # Test bank filter
        response = client.get(f'/api/bank-accounts?bank_id={bank1.id}')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['bank_accounts']) == 1
        assert data['bank_accounts'][0]['bank_id'] == bank1.id
        
        # Test currency filter
        response = client.get('/api/bank-accounts?currency=AUD')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['bank_accounts']) == 1
        assert data['bank_accounts'][0]['currency'] == "AUD"
        
        # Test ACTIVE filter
        response = client.get('/api/bank-accounts?is_active=true')
        assert response.status_code == 200
        data = response.get_json()
        assert len(data['bank_accounts']) == 1
        assert data['bank_accounts'][0]['is_active'] is True

    def test_create_bank_account_success(self, client, db_session):
        """Test successful bank account creation"""
        entity = EntityFactory.create()
        bank = BankFactory.create()
        
        # Store IDs before API call to avoid detached instance issues
        entity_id = entity.id
        bank_id = bank.id
        
        account_data = {
            "entity_id": entity_id,
            "bank_id": bank_id,
            "account_name": "Test Account",
            "account_number": "1234-5678-9012-3456",
            "currency": "AUD",
            "is_active": True
        }
        
        response = client.post('/api/bank-accounts', json=account_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['entity_id'] == entity_id
        assert data['bank_id'] == bank_id
        assert data['account_name'] == "Test Account"
        assert data['account_number'] == "1234-5678-9012-3456"
        assert data['currency'] == "AUD"
        assert data['is_active'] is True
        assert 'message' in data
        
        # Verify account was created in database
        account = db_session.query(BankAccount).filter(
            BankAccount.account_name == "Test Account"
        ).first()
        assert account is not None
        assert account.entity_id == entity_id
        assert account.bank_id == bank_id

    def test_create_bank_account_missing_required_fields(self, client, db_session):
        """Test bank account creation with missing required fields"""
        entity = EntityFactory.create()
        bank = BankFactory.create()
        
        # Missing entity_id
        account_data = {
            "bank_id": bank.id,
            "account_name": "Test Account",
            "account_number": "1234-5678",
            "currency": "AUD"
        }
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 400
        assert "Missing required field: entity_id" in response.get_json()['error']
        
        # Missing bank_id
        account_data = {
            "entity_id": entity.id,
            "account_name": "Test Account",
            "account_number": "1234-5678",
            "currency": "AUD"
        }
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 400
        assert "Missing required field: bank_id" in response.get_json()['error']

    def test_create_bank_account_empty_data(self, client, db_session):
        """Test bank account creation with empty data"""
        response = client.post('/api/bank-accounts', json={})
        assert response.status_code == 400
        assert "No data provided" in response.get_json()['error']

    def test_create_bank_account_entity_not_found(self, client, db_session):
        """Test bank account creation with non-existent entity"""
        bank = BankFactory.create()
        
        account_data = {
            "entity_id": 99999,
            "bank_id": bank.id,
            "account_name": "Test Account",
            "account_number": "1234-5678",
            "currency": "AUD"
        }
        
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 404
        assert "Entity not found" in response.get_json()['error']

    def test_create_bank_account_bank_not_found(self, client, db_session):
        """Test bank account creation with non-existent bank"""
        entity = EntityFactory.create()
        
        account_data = {
            "entity_id": entity.id,
            "bank_id": 99999,
            "account_name": "Test Account",
            "account_number": "1234-5678",
            "currency": "AUD"
        }
        
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 404
        assert "Bank not found" in response.get_json()['error']

    def test_create_bank_account_invalid_currency_format(self, client, db_session):
        """Test bank account creation with invalid currency format"""
        entity = EntityFactory.create()
        bank = BankFactory.create()
        
        account_data = {
            "entity_id": entity.id,
            "bank_id": bank.id,
            "account_name": "Test Account",
            "account_number": "1234-5678",
            "currency": "INVALID"  # Should be 3 characters
        }
        
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 400
        assert "Currency must be a 3-letter ISO code" in response.get_json()['error']

    def test_create_bank_account_duplicate_account(self, client, db_session):
        """Test bank account creation with duplicate account number"""
        entity = EntityFactory.create()
        bank = BankFactory.create()
        
        # Create first account
        existing_account = BankAccountFactory.create(
            entity=entity, bank=bank, account_number="1234-5678"
        )
        
        # Try to create second account with same number
        account_data = {
            "entity_id": entity.id,
            "bank_id": bank.id,
            "account_name": "Duplicate Account",
            "account_number": "1234-5678",
            "currency": "USD"
        }
        
        response = client.post('/api/bank-accounts', json=account_data)
        assert response.status_code == 409
        assert "Bank account with this number already exists" in response.get_json()['error']

    def test_update_bank_account_success(self, client, db_session):
        """Test successful bank account update"""
        account = BankAccountFactory.create(account_name="Original Name")
        
        update_data = {
            "account_name": "Updated Name",
            "is_active": False
        }
        
        response = client.put(f'/api/bank-accounts/{account.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['account_name'] == "Updated Name"
        assert data['is_active'] is False
        assert 'message' in data
        
        # Verify database was updated
        updated_account = db_session.query(BankAccount).filter(
            BankAccount.id == account.id
        ).first()
        assert updated_account.account_name == "Updated Name"
        assert updated_account.is_active is False

    def test_update_bank_account_not_found(self, client, db_session):
        """Test bank account update with non-existent account ID"""
        update_data = {"account_name": "Updated Name"}
        response = client.put('/api/bank-accounts/99999', json=update_data)
        
        assert response.status_code == 404
        assert "Bank account not found" in response.get_json()['error']

    def test_update_bank_account_missing_data(self, client, db_session):
        """Test bank account update with missing data"""
        account = BankAccountFactory.create()
        
        response = client.put(f'/api/bank-accounts/{account.id}', json={})
        assert response.status_code == 400
        assert "No data provided" in response.get_json()['error']

    def test_update_bank_account_invalid_currency_format(self, client, db_session):
        """Test bank account update with invalid currency format"""
        account = BankAccountFactory.create()
        
        update_data = {"currency": "INVALID"}
        response = client.put(f'/api/bank-accounts/{account.id}', json=update_data)
        
        assert response.status_code == 400
        assert "Currency must be a 3-letter ISO code" in response.get_json()['error']

    def test_delete_bank_account_success(self, client, db_session):
        """Test successful bank account deletion"""
        account = BankAccountFactory.create()
        
        response = client.delete(f'/api/bank-accounts/{account.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify account was deleted from database
        deleted_account = db_session.query(BankAccount).filter(
            BankAccount.id == account.id
        ).first()
        assert deleted_account is None

    def test_delete_bank_account_not_found(self, client, db_session):
        """Test bank account deletion with non-existent account ID"""
        response = client.delete('/api/bank-accounts/99999')
        
        assert response.status_code == 404
        assert "Bank account not found" in response.get_json()['error']
