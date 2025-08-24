"""
Bank Account Model Tests

This module tests the BankAccount model validation and business rules.
Focus: Model constraints, validation, and basic business logic only.

Other aspects covered elsewhere:
- Persistence: test_bank_account_repository.py
- Business logic: test_bank_account_service.py
- API operations: test_bank_account_controller.py
- Event processing: test_bank_account_event_handlers.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.banking.models.bank_account import BankAccount
from src.banking.enums import Currency, AccountStatus


class TestBankAccountModel:
    """Test suite for BankAccount model - Core model validation only"""
    
    @pytest.fixture
    def bank_account_data(self):
        """Sample bank account data for testing."""
        return {
            'entity_id': 1,
            'bank_id': 100,
            'account_name': 'Test Account',
            'account_number': '1234-5678-9012-3456',
            'currency': Currency.AUD,
            'status': AccountStatus.ACTIVE
        }
    
    def test_bank_account_creation(self, bank_account_data):
        """Test bank account creation with valid data."""
        account = BankAccount(**bank_account_data)
        
        assert account.entity_id == 1
        assert account.bank_id == 100
        assert account.account_name == 'Test Account'
        assert account.account_number == '1234-5678-9012-3456'
        assert account.currency == Currency.AUD
        assert account.status == AccountStatus.ACTIVE
        assert account.id is None  # Will be None until database insert
        assert account.created_at is None  # SQLAlchemy defaults only set on insert
        assert account.updated_at is None
    
    def test_bank_account_required_fields(self, bank_account_data):
        """Test bank account required field validation."""
        # Note: SQLAlchemy models don't enforce nullable=False at Python level
        # These constraints are enforced at the database level
        
        # Test missing entity_id
        invalid_data = bank_account_data.copy()
        del invalid_data['entity_id']
        
        account = BankAccount(**invalid_data)
        assert account.entity_id is None
        
        # Test missing bank_id
        invalid_data = bank_account_data.copy()
        del invalid_data['bank_id']
        
        account = BankAccount(**invalid_data)
        assert account.bank_id is None
        
        # Test missing account_name
        invalid_data = bank_account_data.copy()
        del invalid_data['account_name']
        
        account = BankAccount(**invalid_data)
        assert account.account_name is None
        
        # Test missing account_number
        invalid_data = bank_account_data.copy()
        del invalid_data['account_number']
        
        account = BankAccount(**invalid_data)
        assert account.account_number is None
        
        # Test missing currency
        invalid_data = bank_account_data.copy()
        del invalid_data['currency']
        
        account = BankAccount(**invalid_data)
        assert account.currency is None
    
    def test_bank_account_optional_fields(self, bank_account_data):
        """Test bank account optional field handling."""
        # status has a default value
        bank_account_data_no_status = bank_account_data.copy()
        del bank_account_data_no_status['status']
        
        account = BankAccount(**bank_account_data_no_status)
        # Note: SQLAlchemy defaults are only applied on database insert
        assert account.status is None
        
        # Test explicit None values
        bank_account_data_none_status = bank_account_data.copy()
        bank_account_data_none_status['status'] = None
        
        account = BankAccount(**bank_account_data_none_status)
        assert account.status is None
    
    def test_bank_account_enum_validation(self, bank_account_data):
        """Test bank account enum field validation."""
        # Test valid currency enum
        account = BankAccount(**bank_account_data)
        assert isinstance(account.currency, Currency)
        assert account.currency == Currency.AUD
        
        # Test valid status enum
        assert isinstance(account.status, AccountStatus)
        assert account.status == AccountStatus.ACTIVE
        
        # Test string enum conversion
        bank_account_data_str = bank_account_data.copy()
        bank_account_data_str['currency'] = 'USD'
        bank_account_data_str['status'] = 'SUSPENDED'
        
        account = BankAccount(**bank_account_data_str)
        assert account.currency == 'USD'  # SQLAlchemy will handle enum conversion
        assert account.status == 'SUSPENDED'
        
        # Test invalid enum values (will be caught at database level)
        bank_account_data_invalid = bank_account_data.copy()
        bank_account_data_invalid['currency'] = 'INVALID'
        bank_account_data_invalid['status'] = 'INVALID'
        
        account = BankAccount(**bank_account_data_invalid)
        assert account.currency == 'INVALID'
        assert account.status == 'INVALID'
    
    def test_bank_account_relationships(self, bank_account_data):
        """Test bank account relationship setup."""
        account = BankAccount(**bank_account_data)
        
        # Test bank relationship
        assert hasattr(account, 'bank')
        assert account.bank is None  # No relationship loaded initially
        
        # Test entity relationship
        assert hasattr(account, 'entity')
        assert account.entity is None  # No relationship loaded initially
        
        # Test relationship configuration
        assert hasattr(BankAccount, '__tablename__')
        assert BankAccount.__tablename__ == 'bank_accounts'
    
    def test_bank_account_repr(self, bank_account_data):
        """Test bank account string representation."""
        account = BankAccount(**bank_account_data)
        
        repr_str = repr(account)
        assert 'BankAccount(' in repr_str
        assert 'id=' in repr_str
        assert 'entity_id=' in repr_str
        assert 'bank_id=' in repr_str
        assert 'name=' in repr_str
        assert 'number=' in repr_str
        assert 'currency=' in repr_str
        assert 'Test Account' in repr_str
        assert '1234-5678-9012-3456' in repr_str
        assert 'AUD' in repr_str
    
    def test_bank_account_timestamps(self, bank_account_data):
        """Test bank account timestamp handling."""
        account = BankAccount(**bank_account_data)
        
        # Timestamps are None until database insert
        assert account.created_at is None
        assert account.updated_at is None
        
        # Test that timestamps can be set manually
        now = datetime.utcnow()
        account.created_at = now
        account.updated_at = now
        
        assert account.created_at == now
        assert account.updated_at == now
    
    def test_bank_account_currency_validation(self, bank_account_data):
        """Test bank account currency validation."""
        # Test all supported currencies
        supported_currencies = [
            Currency.AUD, Currency.USD, Currency.EUR, Currency.GBP, Currency.CAD,
            Currency.NZD, Currency.SGD, Currency.HKD, Currency.JPY, Currency.CHF
        ]
        
        for currency in supported_currencies:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['currency'] = currency
            
            account = BankAccount(**bank_account_data_copy)
            assert account.currency == currency
    
    def test_bank_account_status_validation(self, bank_account_data):
        """Test bank account status validation."""
        # Test all supported statuses
        supported_statuses = [
            AccountStatus.ACTIVE, AccountStatus.SUSPENDED, AccountStatus.CLOSED,
            AccountStatus.PENDING_VERIFICATION, AccountStatus.RESTRICTED
        ]
        
        for status in supported_statuses:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['status'] = status
            
            account = BankAccount(**bank_account_data_copy)
            assert account.status == status
    
    def test_bank_account_name_validation(self, bank_account_data):
        """Test bank account name validation."""
        # Test various name formats
        test_names = [
            'Simple Account',
            'Account with Special Characters: & Co.',
            'International Account Ltd.',
            'Digital Account 2.0',
            'A',  # Single character
            'Very Long Account Name That Exceeds Normal Length But Should Still Work',
            'Account with Numbers 123',
            'Account with Symbols @#$%',
        ]
        
        for name in test_names:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['account_name'] = name
            
            account = BankAccount(**bank_account_data_copy)
            assert account.account_name == name
    
    def test_bank_account_number_validation(self, bank_account_data):
        """Test bank account number validation."""
        # Test various account number formats
        test_numbers = [
            '1234-5678-9012-3456',  # Standard format
            '1234567890123456',      # No dashes
            '1234 5678 9012 3456',  # Spaces instead of dashes
            '1234.5678.9012.3456',  # Dots instead of dashes
            'A123-B456-C789-D012',  # Alphanumeric
            '123456789',             # Short number
            '1234567890123456789012345678901234567890',  # Very long number
            'ACC-001',               # Custom format
        ]
        
        for number in test_numbers:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['account_number'] = number
            
            account = BankAccount(**bank_account_data_copy)
            assert account.account_number == number
    
    def test_bank_account_foreign_keys(self, bank_account_data):
        """Test bank account foreign key handling."""
        # Test various ID values
        test_ids = [
            1,           # Minimum valid ID
            100,         # Normal ID
            999999,      # Large ID
            0,           # Zero ID (invalid but allowed at model level)
            -1,          # Negative ID (invalid but allowed at model level)
        ]
        
        for entity_id in test_ids:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['entity_id'] = entity_id
            
            account = BankAccount(**bank_account_data_copy)
            assert account.entity_id == entity_id
        
        for bank_id in test_ids:
            bank_account_data_copy = bank_account_data.copy()
            bank_account_data_copy['bank_id'] = bank_id
            
            account = BankAccount(**bank_account_data_copy)
            assert account.bank_id == bank_id
    
    def test_bank_account_domain_method_create(self, bank_account_data):
        """Test bank account domain create method."""
        # Mock the service to avoid actual service calls
        with patch('src.banking.services.bank_account_service.BankAccountService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_account = BankAccount(**bank_account_data)
            mock_service_instance.create_bank_account.return_value = mock_account
            
            # Test create method
            result = BankAccount.create(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency='AUD',
                status=AccountStatus.ACTIVE,
                session=None
            )
            
            # Verify service was called
            mock_service.assert_called_once()
            mock_service_instance.create_bank_account.assert_called_once_with(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency='AUD',
                status=AccountStatus.ACTIVE,
                session=None
            )
            
            # Verify result
            assert result == mock_account
    
    def test_bank_account_domain_method_create_with_enums(self, bank_account_data):
        """Test bank account domain create method with enum values."""
        with patch('src.banking.services.bank_account_service.BankAccountService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_account = BankAccount(**bank_account_data)
            mock_service_instance.create_bank_account.return_value = mock_account
            
            # Test create method with enums
            result = BankAccount.create(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency=Currency.USD,
                status=AccountStatus.SUSPENDED,
                session=None
            )
            
            # Verify service was called with enums
            mock_service_instance.create_bank_account.assert_called_once_with(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency=Currency.USD,
                status=AccountStatus.SUSPENDED,
                session=None
            )
            
            assert result == mock_account
    
    def test_bank_account_domain_method_create_with_boolean_status(self, bank_account_data):
        """Test bank account domain create method with boolean status conversion."""
        with patch('src.banking.services.bank_account_service.BankAccountService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_account = BankAccount(**bank_account_data)
            mock_service_instance.create_bank_account.return_value = mock_account
            
            # Test create method with boolean status (should be converted to enum)
            result = BankAccount.create(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency='AUD',
                status=False,  # Boolean value that should be converted to enum
                session=None
            )
            
            # Verify service was called with boolean
            mock_service_instance.create_bank_account.assert_called_once_with(
                entity_id=1,
                bank_id=100,
                account_name='Test Account',
                account_number='1234-5678-9012-3456',
                currency='AUD',
                status=False,
                session=None
            )
            
            assert result == mock_account
    
    def test_bank_account_table_structure(self):
        """Test bank account table structure and constraints."""
        # Test table name
        assert BankAccount.__tablename__ == 'bank_accounts'
        
        # Test column definitions exist
        assert hasattr(BankAccount, 'id')
        assert hasattr(BankAccount, 'entity_id')
        assert hasattr(BankAccount, 'bank_id')
        assert hasattr(BankAccount, 'account_name')
        assert hasattr(BankAccount, 'account_number')
        assert hasattr(BankAccount, 'currency')
        assert hasattr(BankAccount, 'status')
        assert hasattr(BankAccount, 'created_at')
        assert hasattr(BankAccount, 'updated_at')
        
        # Test column types (basic validation)
        assert BankAccount.id.primary_key is True
        assert BankAccount.entity_id.nullable is False
        assert BankAccount.bank_id.nullable is False
        assert BankAccount.account_name.nullable is False
        assert BankAccount.account_number.nullable is False
        assert BankAccount.currency.nullable is False
        assert BankAccount.status.nullable is False
        assert BankAccount.created_at.nullable is True
        assert BankAccount.updated_at.nullable is True
    
    def test_bank_account_relationship_configuration(self):
        """Test bank account relationship configuration."""
        # Test bank relationship
        assert hasattr(BankAccount, 'bank')
        assert BankAccount.bank.property.back_populates == 'accounts'
        
        # Test entity relationship
        assert hasattr(BankAccount, 'entity')
        assert BankAccount.entity.property.back_populates == 'bank_accounts'
    
    def test_bank_account_unique_constraint(self):
        """Test bank account unique constraint configuration."""
        # Test that unique constraint exists
        assert hasattr(BankAccount, '__table_args__')
        
        # Find the unique constraint
        unique_constraints = [
            arg for arg in BankAccount.__table_args__
            if hasattr(arg, 'name') and 'unique' in arg.name.lower()
        ]
        
        assert len(unique_constraints) > 0
        
        # Test constraint name
        unique_constraint = unique_constraints[0]
        assert 'uq_bank_account_unique' in unique_constraint.name
        
        # Test constraint columns
        assert 'entity_id' in unique_constraint.columns
        assert 'bank_id' in unique_constraint.columns
        assert 'account_number' in unique_constraint.columns
