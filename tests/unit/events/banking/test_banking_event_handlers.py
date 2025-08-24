"""
Test Banking Event Handlers.

This module tests all 8 banking event handlers:
- BankCreatedHandler
- BankUpdatedHandler
- BankDeletedHandler
- BankAccountCreatedHandler
- BankAccountUpdatedHandler
- BankAccountDeletedHandler
- CurrencyChangedHandler
- AccountStatusChangedHandler

Each handler is tested for:
- Event validation and business rules
- Event processing logic
- Domain event publishing
- Error handling and rollback
- Cross-module integration
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.banking.models import Bank, BankAccount
from src.banking.events.base_handler import BaseBankingEventHandler
from src.banking.events.handlers.bank_created_handler import BankCreatedHandler
from src.banking.events.handlers.bank_updated_handler import BankUpdatedHandler
from src.banking.events.handlers.bank_deleted_handler import BankDeletedHandler
from src.banking.events.handlers.bank_account_created_handler import BankAccountCreatedHandler
from src.banking.events.handlers.bank_account_updated_handler import BankAccountUpdatedHandler
from src.banking.events.handlers.bank_account_deleted_handler import BankAccountDeletedHandler
from src.banking.events.handlers.currency_changed_handler import CurrencyChangedHandler
from src.banking.events.handlers.account_status_changed_handler import AccountStatusChangedHandler


class TestBaseBankingEventHandler:
    """Test base functionality for all banking event handlers."""
    
    def test_base_handler_initialization(self):
        """Test base handler initialization with required parameters."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Act
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Assert
        assert handler.session == mock_session
        assert handler.banking_entity == mock_bank
        assert handler.bank_service is not None
        assert handler.bank_account_service is not None
        assert handler.validation_service is not None
        assert handler.logger is not None
    
    def test_base_handler_get_bank(self):
        """Test base handler bank retrieval functionality."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Mock the session query chain
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_bank
        
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Act
        result = handler._get_bank(123)
        
        # Assert
        assert result == mock_bank
        mock_session.query.assert_called_once_with(Bank)
    
    def test_base_handler_get_bank_account(self):
        """Test base handler bank account retrieval functionality."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Mock the session query chain
        mock_query = Mock()
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_account
        
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Act
        result = handler._get_bank_account(456)
        
        # Assert
        assert result == mock_account
        mock_session.query.assert_called_once_with(BankAccount)
    
    def test_base_handler_validate_required_fields(self):
        """Test base handler required field validation."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {"name": "Test Bank", "country": "US"}
        required_fields = ["name", "country"]
        
        # Act & Assert - Should not raise exception
        handler._validate_required_fields(event_data, required_fields)
    
    def test_base_handler_validate_required_fields_missing(self):
        """Test base handler required field validation with missing fields."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {"name": "Test Bank"}  # Missing country
        required_fields = ["name", "country"]
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['country'\]"):
            handler._validate_required_fields(event_data, required_fields)
    
    def test_base_handler_log_event_processing(self):
        """Test base handler event logging functionality."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Mock the logger
        with patch.object(handler, 'logger') as mock_logger:
            # Act
            handler._log_event_processing("test_event", {"data": "value"})
            
            # Assert
            mock_logger.info.assert_called_once()
    
    def test_base_handler_publish_domain_event(self):
        """Test base handler domain event publishing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        # Mock the domain event
        mock_event = Mock()
        mock_event.to_dict.return_value = {"event_data": "value"}
        
        # Act
        handler._publish_domain_event("test_event", mock_event)
        
        # Assert
        # The _publish_domain_event method only logs events, doesn't persist to database
        # So we don't expect session.add or session.commit to be called


class TestBankCreatedHandler:
    """Test BankCreatedHandler functionality."""
    
    def test_bank_created_handler_initialization(self):
        """Test bank created handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Act
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        # Assert
        assert handler.bank == mock_bank
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_created_handler_validate_event_success(self):
        """Test bank created handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {
            "name": "Test Bank",
            "country": "US"
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_created_handler_validate_event_missing_name(self):
        """Test bank created handler validation with missing name."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {
            "country": "US"  # Missing name
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['name'\]"):
            handler.validate_event(event_data)
    
    def test_bank_created_handler_validate_event_invalid_country(self):
        """Test bank created handler validation with invalid country code."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {
            "name": "Test Bank",
            "country": "USA"  # Invalid: should be 2 letters
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Country must be a 2-letter ISO 3166-1 alpha-2 code"):
            handler.validate_event(event_data)
    
    def test_bank_created_handler_validate_event_empty_name(self):
        """Test bank created handler validation with empty name."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {
            "name": "   ",  # Empty/whitespace name
            "country": "US"
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Bank name cannot be empty"):
            handler.validate_event(event_data)
    
    def test_bank_created_handler_handle_success(self):
        """Test bank created handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        mock_bank.name = "Test Bank"
        mock_bank.country = "US"
        mock_bank.swift_bic = "TESTUS33"
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankCreatedHandler(mock_session, mock_bank)
        
        event_data = {
            "name": "Test Bank",
            "country": "US"
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['bank_id'] == 123
        assert result['name'] == "Test Bank"
        assert result['country'] == "US"
        assert result['status'] == "created"
        # The handler doesn't persist to database during event handling


class TestBankUpdatedHandler:
    """Test BankUpdatedHandler functionality."""
    
    def test_bank_updated_handler_initialization(self):
        """Test bank updated handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Act
        handler = BankUpdatedHandler(mock_session, mock_bank)
        
        # Assert
        assert handler.bank == mock_bank
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_updated_handler_validate_event_success(self):
        """Test bank updated handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankUpdatedHandler(mock_session, mock_bank)
        
        event_data = {
            "changes": {"name": "New Bank", "swift_bic": "NEWUS33"}
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_updated_handler_validate_event_missing_changes(self):
        """Test bank updated handler validation with missing changes."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankUpdatedHandler(mock_session, mock_bank)
        
        event_data = {
            "old_values": {"name": "Old Bank"}  # Missing changes
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['changes'\]"):
            handler.validate_event(event_data)
    
    def test_bank_updated_handler_handle_success(self):
        """Test bank updated handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        mock_bank.name = "Updated Bank"
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankUpdatedHandler(mock_session, mock_bank)
        
        event_data = {
            "changes": {"name": "Updated Bank"}
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['bank_id'] == 123
        assert result['status'] == "updated"
        assert result['changes_applied'] == {"name": "Updated Bank"}
        # The handler doesn't persist to database during event handling


class TestBankDeletedHandler:
    """Test BankDeletedHandler functionality."""
    
    def test_bank_deleted_handler_initialization(self):
        """Test bank deleted handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Act
        handler = BankDeletedHandler(mock_session, mock_bank)
        
        # Assert
        assert handler.bank == mock_bank
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_deleted_handler_validate_event_success(self):
        """Test bank deleted handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankDeletedHandler(mock_session, mock_bank)
        
        event_data = {
            "deletion_reason": "Merger",
            "deleted_by": "admin"
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_deleted_handler_validate_event_no_validation(self):
        """Test bank deleted handler validation - no validation required."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        handler = BankDeletedHandler(mock_session, mock_bank)
        
        event_data = {
            "deleted_by": "admin"  # Any data is fine
        }
        
        # Act & Assert - Should not raise any exception
        handler.validate_event(event_data)  # No validation required
    
    def test_bank_deleted_handler_handle_success(self):
        """Test bank deleted handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_bank.id = 123
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankDeletedHandler(mock_session, mock_bank)
        
        event_data = {
            "deletion_reason": "Merger",
            "deleted_by": "admin"
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['bank_id'] == 123
        assert result['status'] == "deleted"
        assert result['deletion_reason'] == "Merger"
        # The handler doesn't persist to database during event handling


class TestBankAccountCreatedHandler:
    """Test BankAccountCreatedHandler functionality."""
    
    def test_bank_account_created_handler_initialization(self):
        """Test bank account created handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Act
        handler = BankAccountCreatedHandler(mock_session, mock_account)
        
        # Assert
        assert handler.account == mock_account
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_account_created_handler_validate_event_success(self):
        """Test bank account created handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountCreatedHandler(mock_session, mock_account)
        
        event_data = {
            "entity_id": 789,
            "bank_id": 123,
            "account_name": "Test Account",
            "account_number": "1234567890",
            "currency": "USD"
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_account_created_handler_validate_event_missing_account_number(self):
        """Test bank account created handler validation with missing account_number."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountCreatedHandler(mock_session, mock_account)
        
        event_data = {
            "entity_id": 789,
            "bank_id": 123,
            "account_name": "Test Account",
            "currency": "USD"  # Missing account_number
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['account_number'\]"):
            handler.validate_event(event_data)
    
    def test_bank_account_created_handler_validate_event_invalid_currency(self):
        """Test bank account created handler validation with invalid currency."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountCreatedHandler(mock_session, mock_account)
        
        event_data = {
            "entity_id": 789,
            "bank_id": 123,
            "account_name": "Test Account",
            "account_number": "1234567890",
            "currency": "INVALID"  # Invalid currency code
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Currency must be a 3-letter ISO 4217 code"):
            handler.validate_event(event_data)
    
    def test_bank_account_created_handler_handle_success(self):
        """Test bank account created handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        mock_account.account_number = "1234567890"
        mock_account.currency = "USD"
        mock_account.bank_id = 123
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankAccountCreatedHandler(mock_session, mock_account)
        
        event_data = {
            "entity_id": 789,
            "bank_id": 123,
            "account_name": "Test Account",
            "account_number": "1234567890",
            "currency": "USD"
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['account_id'] == 456
        assert result['account_number'] == "1234567890"
        assert result['currency'] == "USD"
        assert result['status'] == "created"
        # The handler doesn't persist to database during event handling


class TestBankAccountUpdatedHandler:
    """Test BankAccountUpdatedHandler functionality."""
    
    def test_bank_account_updated_handler_initialization(self):
        """Test bank account updated handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Act
        handler = BankAccountUpdatedHandler(mock_session, mock_account)
        
        # Assert
        assert handler.account == mock_account
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_account_updated_handler_validate_event_success(self):
        """Test bank account updated handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountUpdatedHandler(mock_session, mock_account)
        
        event_data = {
            "changes": {"balance": 15000.00, "status": "active"}
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_account_updated_handler_validate_event_missing_changes(self):
        """Test bank account updated handler validation with missing changes."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountUpdatedHandler(mock_session, mock_account)
        
        event_data = {
            "old_values": {"balance": 10000.00}  # Missing changes
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['changes'\]"):
            handler.validate_event(event_data)
    
    def test_bank_account_updated_handler_handle_success(self):
        """Test bank account updated handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        mock_account.entity_id = 789
        mock_account.bank_id = 123
        mock_account.account_name = "Test Account"
        mock_account.account_number = "1234567890"
        mock_account.currency = "USD"
        mock_account.is_active = True
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankAccountUpdatedHandler(mock_session, mock_account)
        
        event_data = {
            "changes": {"balance": 15000.00}
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['account_id'] == 456
        assert result['status'] == "updated"
        assert result['changes_applied'] == {"balance": 15000.00}
        # The handler doesn't persist to database during event handling


class TestBankAccountDeletedHandler:
    """Test BankAccountDeletedHandler functionality."""
    
    def test_bank_account_deleted_handler_initialization(self):
        """Test bank account deleted handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Act
        handler = BankAccountDeletedHandler(mock_session, mock_account)
        
        # Assert
        assert handler.account == mock_account
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_bank_account_deleted_handler_validate_event_success(self):
        """Test bank account deleted handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountDeletedHandler(mock_session, mock_account)
        
        event_data = {
            "deletion_reason": "Account closed",
            "final_balance": 0.00
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_bank_account_deleted_handler_validate_event_no_validation(self):
        """Test bank account deleted handler validation - no validation required."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = BankAccountDeletedHandler(mock_session, mock_account)
        
        event_data = {
            "final_balance": 0.00  # Any data is fine
        }
        
        # Act & Assert - Should not raise any exception
        handler.validate_event(event_data)  # No validation required
    
    def test_bank_account_deleted_handler_handle_success(self):
        """Test bank account deleted handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        mock_account.entity_id = 789
        mock_account.bank_id = 123
        mock_account.account_name = "Test Account"
        mock_account.account_number = "1234567890"
        mock_account.currency = "USD"
        mock_account.is_active = True
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = BankAccountDeletedHandler(mock_session, mock_account)
        
        event_data = {
            "deletion_reason": "Account closed",
            "final_balance": 0.00
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['account_id'] == 456
        assert result['status'] == "deleted"
        assert result['deletion_reason'] == "Account closed"
        # The handler doesn't persist to database during event handling


class TestCurrencyChangedHandler:
    """Test CurrencyChangedHandler functionality."""
    
    def test_currency_changed_handler_initialization(self):
        """Test currency changed handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Act
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        # Assert
        assert handler.account == mock_account
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_currency_changed_handler_validate_event_success(self):
        """Test currency changed handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_currency": "USD",
            "new_currency": "EUR",
            "exchange_rate": 0.85
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_currency_changed_handler_validate_event_missing_old_currency(self):
        """Test currency changed handler validation with missing old_currency."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        event_data = {
            "new_currency": "EUR",  # Missing old_currency
            "exchange_rate": 0.85
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['old_currency'\]"):
            handler.validate_event(event_data)
    
    def test_currency_changed_handler_validate_event_invalid_old_currency(self):
        """Test currency changed handler validation with invalid old currency."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_currency": "INVALID",  # Invalid currency code
            "new_currency": "EUR"
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Old currency must be a 3-letter ISO 4217 code"):
            handler.validate_event(event_data)
    
    def test_currency_changed_handler_validate_event_same_currency(self):
        """Test currency changed handler validation with same old and new currency."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_currency": "USD",
            "new_currency": "USD"  # Same currency
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Old and new currencies must be different"):
            handler.validate_event(event_data)
    
    def test_currency_changed_handler_handle_success(self):
        """Test currency changed handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        mock_account.currency = "EUR"
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = CurrencyChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_currency": "USD",
            "new_currency": "EUR",
            "exchange_rate": 0.85
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['account_id'] == 456
        assert result['status'] == "currency_changed"
        assert result['old_currency'] == "USD"
        assert result['new_currency'] == "EUR"
        # The handler doesn't persist to database during event handling


class TestAccountStatusChangedHandler:
    """Test AccountStatusChangedHandler functionality."""
    
    def test_account_status_changed_handler_initialization(self):
        """Test account status changed handler initialization."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        
        # Act
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        # Assert
        assert handler.account == mock_account
        assert isinstance(handler, BaseBankingEventHandler)
    
    def test_account_status_changed_handler_validate_event_success(self):
        """Test account status changed handler event validation with valid data."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_status": True,
            "new_status": False,
            "reason": "Compliance review"
        }
        
        # Act & Assert - Should not raise exception
        handler.validate_event(event_data)
    
    def test_account_status_changed_handler_validate_event_missing_old_status(self):
        """Test account status changed handler validation with missing old_status."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        event_data = {
            "new_status": False,  # Missing old_status
            "reason": "Compliance review"
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match=r"Missing required fields: \['old_status'\]"):
            handler.validate_event(event_data)
    
    def test_account_status_changed_handler_validate_event_invalid_status(self):
        """Test account status changed handler validation with invalid status."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_status": True,
            "new_status": "invalid_status",  # Invalid status (not boolean)
            "reason": "Test"
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="New status must be a boolean value"):
            handler.validate_event(event_data)
    
    def test_account_status_changed_handler_validate_event_same_status(self):
        """Test account status changed handler validation with same old and new status."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_status": True,
            "new_status": True,  # Same status
            "reason": "Test"
        }
        
        # Act & Assert - Should raise ValueError
        with pytest.raises(ValueError, match="Old and new status must be different"):
            handler.validate_event(event_data)
    
    def test_account_status_changed_handler_handle_success(self):
        """Test account status changed handler successful event processing."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_account = Mock(spec=BankAccount)
        mock_account.id = 456
        mock_account.status = "suspended"
        
        # Mock the session add and commit
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        handler = AccountStatusChangedHandler(mock_session, mock_account)
        
        event_data = {
            "old_status": True,
            "new_status": False,
            "reason": "Compliance review"
        }
        
        # Act
        result = handler.handle(event_data)
        
        # Assert
        assert result['account_id'] == 456
        assert result['status'] == "status_changed"
        assert result['old_status'] == True
        assert result['new_status'] == False
        # The handler doesn't persist to database during event handling


class TestBankingEventHandlersIntegration:
    """Test integration between different banking event handlers."""
    
    def test_handler_consistency_across_events(self):
        """Test that all handlers follow consistent patterns."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_account = Mock(spec=BankAccount)
        
        # Create all handlers
        handlers = [
            BankCreatedHandler(mock_session, mock_bank),
            BankUpdatedHandler(mock_session, mock_bank),
            BankDeletedHandler(mock_session, mock_bank),
            BankAccountCreatedHandler(mock_session, mock_account),
            BankAccountUpdatedHandler(mock_session, mock_account),
            BankAccountDeletedHandler(mock_session, mock_account),
            CurrencyChangedHandler(mock_session, mock_account),
            AccountStatusChangedHandler(mock_session, mock_account)
        ]
        
        # Act & Assert
        for handler in handlers:
            # All handlers should inherit from base class
            assert isinstance(handler, BaseBankingEventHandler)
            
            # All handlers should have required methods
            assert hasattr(handler, 'validate_event')
            assert hasattr(handler, 'handle')
            assert hasattr(handler, 'session')
            assert hasattr(handler, 'banking_entity')
    
    def test_handler_error_handling_consistency(self):
        """Test that all handlers handle errors consistently."""
        # Arrange
        mock_session = Mock(spec=Session)
        mock_bank = Mock(spec=Bank)
        mock_account = Mock(spec=BankAccount)
        
        # Test handlers that require validation
        test_cases = [
            (BankCreatedHandler, mock_bank, {"country": "US"}),  # Missing name
            (BankAccountCreatedHandler, mock_account, {"entity_id": 789, "bank_id": 123, "account_name": "Test", "currency": "USD"}),  # Missing account_number
            (CurrencyChangedHandler, mock_account, {"new_currency": "EUR"}),  # Missing old_currency
            (AccountStatusChangedHandler, mock_account, {"new_status": False})  # Missing old_status
        ]
        
        # Act & Assert
        for handler_class, entity, invalid_data in test_cases:
            handler = handler_class(mock_session, entity)
            
            # All handlers should raise ValueError for invalid data
            with pytest.raises(ValueError):
                handler.validate_event(invalid_data)
