"""
Banking Validation Service Tests

This module tests the BankingValidationService business rule validation logic.
Focus: Validation service business rules, constraint checking, and data integrity.

Other aspects covered elsewhere:
- Model validation: test_bank_model.py, test_bank_account_model.py
- Repository operations: test_bank_repository.py, test_bank_account_repository.py
- API operations: test_bank_controller.py, test_bank_account_controller.py
- Event processing: test_bank_event_handlers.py, test_bank_account_event_handlers.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.models.bank import Bank
from src.banking.models.bank_account import BankAccount
from src.banking.enums import Country, Currency, AccountStatus


class TestBankingValidationService:
    """Test suite for BankingValidationService - Business rule validation only"""
    
    @pytest.fixture
    def mock_bank_repository(self):
        """Mock bank repository for testing."""
        return Mock(spec=BankRepository)
    
    @pytest.fixture
    def mock_bank_account_repository(self):
        """Mock bank account repository for testing."""
        return Mock(spec=BankAccountRepository)
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_bank(self):
        """Sample bank instance for testing."""
        return Bank(
            id=1,
            name='Test Bank',
            country=Country.AU,
            swift_bic='TESTAU2X'
        )
    
    @pytest.fixture
    def sample_bank_account(self):
        """Sample bank account instance for testing."""
        return BankAccount(
            id=1,
            entity_id=1,
            bank_id=1,
            account_name='Test Account',
            account_number='1234-5678-9012-3456',
            currency=Currency.AUD,
            status=AccountStatus.ACTIVE
        )
    
    # ============================================================================
    # INITIALIZATION TESTS
    # ============================================================================
    
    def test_banking_validation_service_initialization_defaults(self):
        """Test BankingValidationService initialization with default dependencies."""
        service = BankingValidationService()
        
        assert service.bank_repository is not None
        assert isinstance(service.bank_repository, BankRepository)
        assert service.bank_account_repository is not None
        assert isinstance(service.bank_account_repository, BankAccountRepository)
    
    def test_banking_validation_service_initialization_with_dependencies(self, mock_bank_repository, mock_bank_account_repository):
        """Test BankingValidationService initialization with provided dependencies."""
        service = BankingValidationService(
            bank_repository=mock_bank_repository,
            bank_account_repository=mock_bank_account_repository
        )
        
        assert service.bank_repository is mock_bank_repository
        assert service.bank_account_repository is mock_bank_account_repository
    
    # ============================================================================
    # ACCOUNT STATUS VALIDATION TESTS
    # ============================================================================
    
    def test_validate_account_status_valid(self, mock_bank_repository, mock_bank_account_repository):
        """Test account status validation with valid status."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test valid status values
        assert service.validate_account_status(AccountStatus.ACTIVE) is True
        assert service.validate_account_status(AccountStatus.SUSPENDED) is True
        assert service.validate_account_status(AccountStatus.CLOSED) is True
        assert service.validate_account_status(AccountStatus.PENDING_VERIFICATION) is True
        assert service.validate_account_status(AccountStatus.RESTRICTED) is True
    
    def test_validate_account_status_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test account status validation with invalid status."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test invalid status values
        assert service.validate_account_status(None) is False
    
    def test_validate_account_status_or_raise_valid(self, mock_bank_repository, mock_bank_account_repository):
        """Test validate_account_status_or_raise with valid status."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should not raise exception
        service.validate_account_status_or_raise(AccountStatus.ACTIVE)
        service.validate_account_status_or_raise(AccountStatus.SUSPENDED)
    
    def test_validate_account_status_or_raise_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test validate_account_status_or_raise with invalid status."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Account status must be a valid AccountStatus enum"):
            service.validate_account_status_or_raise(None)
    
    def test_normalize_account_status_valid(self, mock_bank_repository, mock_bank_account_repository):
        """Test account status normalization with valid status."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test status normalization
        assert service.normalize_account_status(AccountStatus.ACTIVE) == AccountStatus.ACTIVE
        assert service.normalize_account_status(AccountStatus.SUSPENDED) == AccountStatus.SUSPENDED
        assert service.normalize_account_status(AccountStatus.CLOSED) == AccountStatus.CLOSED
    
    def test_normalize_account_status_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test account status normalization with invalid input."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should raise ValueError for invalid input
        with pytest.raises(ValueError, match="Account status must be an AccountStatus enum"):
            service.normalize_account_status(123)
        
        with pytest.raises(ValueError, match="Account status must be an AccountStatus enum"):
            service.normalize_account_status("ACTIVE")
    
    # ============================================================================
    # CURRENCY VALIDATION TESTS
    # ============================================================================
    
    def test_validate_currency_code_valid_string(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency code validation with valid string."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test valid currency codes
        assert service.validate_currency_code('AUD') is True
        assert service.validate_currency_code('USD') is True
        assert service.validate_currency_code('EUR') is True
        assert service.validate_currency_code('GBP') is True
    
    def test_validate_currency_code_valid_enum(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency code validation with valid enum."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test valid currency enums
        assert service.validate_currency_code(Currency.AUD) is True
        assert service.validate_currency_code(Currency.USD) is True
        assert service.validate_currency_code(Currency.EUR) is True
        assert service.validate_currency_code(Currency.GBP) is True
    
    def test_validate_currency_code_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency code validation with invalid input."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test invalid currency codes
        assert service.validate_currency_code('') is False
        assert service.validate_currency_code('XX') is False
        assert service.validate_currency_code('AUDD') is False
        assert service.validate_currency_code(None) is False
        assert service.validate_currency_code(123) is False
    
    def test_validate_currency_code_or_raise_valid(self, mock_bank_repository, mock_bank_account_repository):
        """Test validate_currency_code_or_raise with valid currency code."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should not raise exception
        service.validate_currency_code_or_raise('AUD')
        service.validate_currency_code_or_raise(Currency.USD)
    
    def test_validate_currency_code_or_raise_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test validate_currency_code_or_raise with invalid currency code."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Currency must be a valid 3-letter ISO code"):
            service.validate_currency_code_or_raise('XX')
        
        with pytest.raises(ValueError, match="Currency must be a valid Currency enum or string"):
            service.validate_currency_code_or_raise(123)
    
    def test_normalize_currency_string(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency normalization with string input."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test string normalization
        assert service.normalize_currency('aud') == Currency.AUD
        assert service.normalize_currency('USD') == Currency.USD
        assert service.normalize_currency('eur') == Currency.EUR
    
    def test_normalize_currency_enum(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency normalization with enum input."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Test enum normalization (should return same enum)
        assert service.normalize_currency(Currency.AUD) == Currency.AUD
        assert service.normalize_currency(Currency.USD) == Currency.USD
        assert service.normalize_currency(Currency.EUR) == Currency.EUR
    
    def test_normalize_currency_invalid(self, mock_bank_repository, mock_bank_account_repository):
        """Test currency normalization with invalid input."""
        service = BankingValidationService(mock_bank_repository, mock_bank_account_repository)
        
        # Should raise ValueError for invalid codes
        with pytest.raises(ValueError, match="Invalid currency code: XX"):
            service.normalize_currency('XX')
        
        with pytest.raises(ValueError, match="Currency must be a string or Currency enum"):
            service.normalize_currency(123)
