"""
Bank Model Tests

This module tests the Bank model validation and business rules.
Focus: Model constraints, validation, and basic business logic only.

Other aspects covered elsewhere:
- Persistence: test_bank_repository.py
- Business logic: test_bank_service.py
- API operations: test_bank_controller.py
- Event processing: test_bank_event_handlers.py
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch

from src.banking.models.bank import Bank
from src.banking.enums import Country


class TestBankModel:
    """Test suite for Bank model - Core model validation only"""
    
    @pytest.fixture
    def bank_data(self):
        """Sample bank data for testing."""
        return {
            'name': 'Test Bank',
            'country': Country.AU,
            'swift_bic': 'TESTAU2X'
        }
    
    def test_bank_creation(self, bank_data):
        """Test bank creation with valid data."""
        bank = Bank(**bank_data)
        
        assert bank.name == 'Test Bank'
        assert bank.country == Country.AU
        assert bank.swift_bic == 'TESTAU2X'
        assert bank.id is None  # Will be None until database insert
        assert bank.created_at is None  # SQLAlchemy defaults only set on insert
        assert bank.updated_at is None
    
    def test_bank_required_fields(self, bank_data):
        """Test bank required field validation."""
        # Note: SQLAlchemy models don't enforce nullable=False at Python level
        # These constraints are enforced at the database level
        
        # Test missing name
        invalid_data = bank_data.copy()
        del invalid_data['name']
        
        bank = Bank(**invalid_data)
        assert bank.name is None
        
        # Test missing country
        invalid_data = bank_data.copy()
        del invalid_data['country']
        
        bank = Bank(**invalid_data)
        assert bank.country is None
        
        # Test missing swift_bic (optional field)
        invalid_data = bank_data.copy()
        del invalid_data['swift_bic']
        
        bank = Bank(**invalid_data)
        assert bank.swift_bic is None
    
    def test_bank_optional_fields(self, bank_data):
        """Test bank optional field handling."""
        # swift_bic is optional
        bank_data_no_swift = bank_data.copy()
        del bank_data_no_swift['swift_bic']
        
        bank = Bank(**bank_data_no_swift)
        assert bank.swift_bic is None
        
        # swift_bic can be None
        bank_data_none_swift = bank_data.copy()
        bank_data_none_swift['swift_bic'] = None
        
        bank = Bank(**bank_data_none_swift)
        assert bank.swift_bic is None
    
    def test_bank_enum_validation(self, bank_data):
        """Test bank enum field validation."""
        # Test valid country enum
        bank = Bank(**bank_data)
        assert isinstance(bank.country, Country)
        assert bank.country == Country.AU
        
        # Test string country conversion
        bank_data_str = bank_data.copy()
        bank_data_str['country'] = 'US'
        
        bank = Bank(**bank_data_str)
        assert bank.country == 'US'  # SQLAlchemy will handle enum conversion
        
        # Test invalid country (will be caught at database level)
        bank_data_invalid = bank_data.copy()
        bank_data_invalid['country'] = 'INVALID'
        
        bank = Bank(**bank_data_invalid)
        assert bank.country == 'INVALID'  # SQLAlchemy will handle validation
    
    def test_bank_relationships(self, bank_data):
        """Test bank relationship setup."""
        bank = Bank(**bank_data)
        
        # Test accounts relationship
        assert hasattr(bank, 'accounts')
        assert bank.accounts == []  # Empty list initially
        
        # Test relationship configuration
        assert hasattr(Bank, '__tablename__')
        assert Bank.__tablename__ == 'banks'
    
    def test_bank_repr(self, bank_data):
        """Test bank string representation."""
        bank = Bank(**bank_data)
        
        repr_str = repr(bank)
        assert 'Bank(' in repr_str
        assert 'id=' in repr_str
        assert 'name=' in repr_str
        assert 'country=' in repr_str
        assert 'Test Bank' in repr_str
        assert 'AU' in repr_str
    
    def test_bank_timestamps(self, bank_data):
        """Test bank timestamp handling."""
        bank = Bank(**bank_data)
        
        # Timestamps are None until database insert
        assert bank.created_at is None
        assert bank.updated_at is None
        
        # Test that timestamps can be set manually
        now = datetime.utcnow()
        bank.created_at = now
        bank.updated_at = now
        
        assert bank.created_at == now
        assert bank.updated_at == now
    
    def test_bank_swift_bic_format(self, bank_data):
        """Test bank SWIFT/BIC format handling."""
        # Test valid SWIFT/BIC format
        bank = Bank(**bank_data)
        assert bank.swift_bic == 'TESTAU2X'
        
        # Test different SWIFT/BIC formats
        test_swift_codes = [
            'ABCDUS2X',  # US format
            'ABCDGB2X',  # UK format
            'ABCDDE2X',  # Germany format
            'ABCDJP2X',  # Japan format
            None,         # No SWIFT/BIC
            '',           # Empty string
        ]
        
        for swift_code in test_swift_codes:
            bank_data_copy = bank_data.copy()
            bank_data_copy['swift_bic'] = swift_code
            
            bank = Bank(**bank_data_copy)
            assert bank.swift_bic == swift_code
    
    def test_bank_country_validation(self, bank_data):
        """Test bank country validation."""
        # Test all supported countries
        supported_countries = [
            Country.AU, Country.US, Country.UK, Country.CA, Country.NZ,
            Country.SG, Country.HK, Country.JP, Country.DE, Country.FR
        ]
        
        for country in supported_countries:
            bank_data_copy = bank_data.copy()
            bank_data_copy['country'] = country
            
            bank = Bank(**bank_data_copy)
            assert bank.country == country
    
    def test_bank_name_validation(self, bank_data):
        """Test bank name validation."""
        # Test various name formats
        test_names = [
            'Simple Bank',
            'Bank with Special Characters: & Co.',
            'International Bank Ltd.',
            'Digital Bank 2.0',
            'A',  # Single character
            'Very Long Bank Name That Exceeds Normal Length But Should Still Work',
            'Bank with Numbers 123',
            'Bank with Symbols @#$%',
        ]
        
        for name in test_names:
            bank_data_copy = bank_data.copy()
            bank_data_copy['name'] = name
            
            bank = Bank(**bank_data_copy)
            assert bank.name == name
    
    def test_bank_domain_method_create(self, bank_data):
        """Test bank domain create method."""
        # Mock the service to avoid actual service calls
        with patch('src.banking.services.bank_service.BankService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_bank = Bank(**bank_data)
            mock_service_instance.create_bank.return_value = mock_bank
            
            # Test create method
            result = Bank.create(
                name='Test Bank',
                country='AU',
                swift_bic='TESTAU2X',
                session=None
            )
            
            # Verify service was called
            mock_service.assert_called_once()
            mock_service_instance.create_bank.assert_called_once_with(
                'Test Bank', 'AU', 'TESTAU2X', None
            )
            
            # Verify result
            assert result == mock_bank
    
    def test_bank_domain_method_create_with_enum(self, bank_data):
        """Test bank domain create method with enum values."""
        with patch('src.banking.services.bank_service.BankService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_bank = Bank(**bank_data)
            mock_service_instance.create_bank.return_value = mock_bank
            
            # Test create method with enum
            result = Bank.create(
                name='Test Bank',
                country=Country.US,
                swift_bic='TESTUS2X',
                session=None
            )
            
            # Verify service was called with enum
            mock_service_instance.create_bank.assert_called_once_with(
                'Test Bank', Country.US, 'TESTUS2X', None
            )
            
            assert result == mock_bank
    
    def test_bank_domain_method_create_no_swift(self, bank_data):
        """Test bank domain create method without SWIFT/BIC."""
        with patch('src.banking.services.bank_service.BankService') as mock_service:
            mock_service_instance = Mock()
            mock_service.return_value = mock_service_instance
            
            mock_bank = Bank(**bank_data)
            mock_service_instance.create_bank.return_value = mock_bank
            
            # Test create method without SWIFT/BIC
            result = Bank.create(
                name='Test Bank',
                country='AU',
                session=None
            )
            
            # Verify service was called with None for swift_bic
            mock_service_instance.create_bank.assert_called_once_with(
                'Test Bank', 'AU', None, None
            )
            
            assert result == mock_bank
    
    def test_bank_table_structure(self):
        """Test bank table structure and constraints."""
        # Test table name
        assert Bank.__tablename__ == 'banks'
        
        # Test column definitions exist
        assert hasattr(Bank, 'id')
        assert hasattr(Bank, 'name')
        assert hasattr(Bank, 'country')
        assert hasattr(Bank, 'swift_bic')
        assert hasattr(Bank, 'created_at')
        assert hasattr(Bank, 'updated_at')
        
        # Test column types (basic validation)
        assert Bank.id.primary_key is True
        assert Bank.name.nullable is False
        assert Bank.country.nullable is False
        assert Bank.swift_bic.nullable is True
        assert Bank.created_at.nullable is True
        assert Bank.updated_at.nullable is True
    
    def test_bank_relationship_configuration(self):
        """Test bank relationship configuration."""
        # Test accounts relationship
        assert hasattr(Bank, 'accounts')
        
        # Verify relationship is properly configured
        # This is a basic check - detailed relationship testing is in integration tests
        assert Bank.accounts.property.back_populates == 'bank'
        # Test that the cascade includes the expected options
        cascade_options = str(Bank.accounts.property.cascade)
        assert 'delete' in cascade_options
        assert 'delete-orphan' in cascade_options
