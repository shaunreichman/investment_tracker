import pytest
from datetime import datetime
from tests.factories import BankFactory, EntityFactory
from src.banking.models import Bank


class TestBankEndpoints:
    """Test API endpoints for bank CRUD operations"""

    def test_get_banks_success(self, client, db_session):
        """Test successful retrieval of all banks"""
        # Create test banks
        bank1 = BankFactory.create(name="Test Bank 1", country="AU")
        bank2 = BankFactory.create(name="Test Bank 2", country="US")
        
        response = client.get('/api/banks')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'banks' in data
        assert len(data['banks']) == 2
        
        # Verify bank data structure
        bank_data = data['banks'][0]
        assert 'id' in bank_data
        assert 'name' in bank_data
        assert 'country' in bank_data
        assert 'swift_bic' in bank_data
        assert 'accounts_count' in bank_data
        
        # Verify specific data
        bank_names = [b['name'] for b in data['banks']]
        assert "Test Bank 1" in bank_names
        assert "Test Bank 2" in bank_names

    def test_get_banks_empty(self, client, db_session):
        """Test GET banks when no banks exist"""
        response = client.get('/api/banks')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'banks' in data
        assert len(data['banks']) == 0

    def test_create_bank_success(self, client, db_session):
        """Test successful bank creation"""
        bank_data = {
            "name": "New Test Bank",
            "country": "CA",
            "swift_bic": "TESTCA2X"
        }
        
        response = client.post('/api/banks', json=bank_data)
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['name'] == "New Test Bank"
        assert data['country'] == "CA"
        assert data['swift_bic'] == "TESTCA2X"
        assert 'message' in data
        
        # Verify bank was created in database
        bank = db_session.query(Bank).filter(Bank.name == "New Test Bank").first()
        assert bank is not None
        assert bank.country == "CA"
        assert bank.swift_bic == "TESTCA2X"

    def test_create_bank_missing_required_fields(self, client, db_session):
        """Test bank creation with missing required fields"""
        # Missing name
        bank_data = {"country": "AU"}
        response = client.post('/api/banks', json=bank_data)
        assert response.status_code == 400
        assert "Missing required field: name" in response.get_json()['error']
        
        # Missing country
        bank_data = {"name": "Test Bank"}
        response = client.post('/api/banks', json=bank_data)
        assert response.status_code == 400
        assert "Missing required field: country" in response.get_json()['error']

    def test_create_bank_empty_data(self, client, db_session):
        """Test bank creation with empty data"""
        response = client.post('/api/banks', json={})
        assert response.status_code == 400
        assert "No data provided" in response.get_json()['error']

    def test_create_bank_invalid_country_format(self, client, db_session):
        """Test bank creation with invalid country format"""
        bank_data = {
            "name": "Test Bank",
            "country": "INVALID"  # Should be 2 characters
        }
        
        response = client.post('/api/banks', json=bank_data)
        assert response.status_code == 400
        assert "Country must be a 2-letter ISO code" in response.get_json()['error']

    def test_create_bank_duplicate_name_same_country(self, client, db_session):
        """Test bank creation with duplicate name in same country"""
        # Create first bank
        existing_bank = BankFactory.create(name="Duplicate Bank", country="AU")
        
        # Try to create second bank with same name in same country
        bank_data = {
            "name": "Duplicate Bank",
            "country": "AU"
        }
        
        response = client.post('/api/banks', json=bank_data)
        assert response.status_code == 409
        assert "Bank with this name already exists in this country" in response.get_json()['error']

    def test_create_bank_duplicate_name_different_country(self, client, db_session):
        """Test bank creation with duplicate name in different country (should succeed)"""
        # Create first bank
        existing_bank = BankFactory.create(name="Duplicate Bank", country="AU")
        
        # Try to create second bank with same name in different country
        bank_data = {
            "name": "Duplicate Bank",
            "country": "US"
        }
        
        response = client.post('/api/banks', json=bank_data)
        assert response.status_code == 201  # Should succeed for different country

    def test_update_bank_success(self, client, db_session):
        """Test successful bank update"""
        bank = BankFactory.create(name="Original Name", country="AU")
        
        update_data = {
            "name": "Updated Name",
            "country": "US",
            "swift_bic": "UPDATED"
        }
        
        response = client.put(f'/api/banks/{bank.id}', json=update_data)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['name'] == "Updated Name"
        assert data['country'] == "US"
        assert data['swift_bic'] == "UPDATED"
        assert 'message' in data
        
        # Verify database was updated
        updated_bank = db_session.query(Bank).filter(Bank.id == bank.id).first()
        assert updated_bank.name == "Updated Name"
        assert updated_bank.country == "US"
        assert updated_bank.swift_bic == "UPDATED"

    def test_update_bank_not_found(self, client, db_session):
        """Test bank update with non-existent bank ID"""
        update_data = {"name": "Updated Name"}
        response = client.put('/api/banks/99999', json=update_data)
        
        assert response.status_code == 404
        assert "Bank not found" in response.get_json()['error']

    def test_update_bank_missing_data(self, client, db_session):
        """Test bank update with missing data"""
        bank = BankFactory.create()
        
        response = client.put(f'/api/banks/{bank.id}', json={})
        assert response.status_code == 400
        assert "No data provided" in response.get_json()['error']

    def test_update_bank_invalid_country_format(self, client, db_session):
        """Test bank update with invalid country format"""
        bank = BankFactory.create()
        
        update_data = {"country": "INVALID"}
        response = client.put(f'/api/banks/{bank.id}', json=update_data)
        
        assert response.status_code == 400
        assert "Country must be a 2-letter ISO code" in response.get_json()['error']

    def test_delete_bank_success(self, client, db_session):
        """Test successful bank deletion"""
        bank = BankFactory.create()
        
        response = client.delete(f'/api/banks/{bank.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'message' in data
        
        # Verify bank was deleted from database
        deleted_bank = db_session.query(Bank).filter(Bank.id == bank.id).first()
        assert deleted_bank is None

    def test_delete_bank_not_found(self, client, db_session):
        """Test bank deletion with non-existent bank ID"""
        response = client.delete('/api/banks/99999')
        
        assert response.status_code == 404
        assert "Bank not found" in response.get_json()['error']

    def test_delete_bank_with_accounts(self, client, db_session):
        """Test bank deletion when bank has associated accounts"""
        # This test would require BankAccountFactory to be available
        # For now, we'll test the basic deletion logic
        bank = BankFactory.create()
        
        response = client.delete(f'/api/banks/{bank.id}')
        
        assert response.status_code == 200
        # Note: In a real implementation, this might fail if there are foreign key constraints
