"""
Bank Account Service Tests

This module tests the BankAccountService business logic and operations.
Focus: Service layer business logic, validation coordination, and business rules.

Other aspects covered elsewhere:
- Model validation: test_bank_account_model.py
- Repository operations: test_bank_account_repository.py
- API operations: test_bank_account_controller.py
- Event processing: test_bank_account_event_handlers.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.banking.events.orchestrator import BankingUpdateOrchestrator
from src.banking.events.registry import BankingEventHandlerRegistry
from src.banking.models.bank_account import BankAccount
from src.banking.enums import Currency, AccountStatus


class TestBankAccountService:
    """Test suite for BankAccountService - Business logic and operations only"""
    
    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service for testing."""
        return Mock(spec=BankingValidationService)
    
    @pytest.fixture
    def mock_bank_account_repository(self):
        """Mock bank account repository for testing."""
        return Mock(spec=BankAccountRepository)
    
    @pytest.fixture
    def mock_event_orchestrator(self):
        """Mock event orchestrator for testing."""
        return Mock(spec=BankingUpdateOrchestrator)
    
    @pytest.fixture
    def mock_event_registry(self):
        """Mock event handler registry for testing."""
        return Mock(spec=BankingEventHandlerRegistry)
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_bank_account_data(self):
        """Sample bank account data for testing."""
        return {
            'entity_id': 1,
            'bank_id': 1,
            'account_name': 'Test Account',
            'account_number': '1234-5678-9012-3456',
            'currency': 'AUD',
            'status': AccountStatus.ACTIVE
        }
    
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
    
    def test_bank_account_service_initialization_defaults(self):
        """Test BankAccountService initialization with default dependencies."""
        service = BankAccountService()
        
        assert service.validation_service is not None
        assert isinstance(service.validation_service, BankingValidationService)
        assert service.bank_account_repository is not None
        assert isinstance(service.bank_account_repository, BankAccountRepository)
    
    def test_bank_account_service_initialization_with_dependencies(self, mock_validation_service, mock_bank_account_repository, mock_event_orchestrator, mock_event_registry):
        """Test BankAccountService initialization with provided dependencies."""
        service = BankAccountService(
            validation_service=mock_validation_service,
            bank_account_repository=mock_bank_account_repository,
            event_orchestrator=mock_event_orchestrator,
            event_registry=mock_event_registry
        )
        
        assert service.validation_service is mock_validation_service
        assert service.bank_account_repository is mock_bank_account_repository
        assert service.event_orchestrator is mock_event_orchestrator
        assert service.event_registry is mock_event_registry
    
    # ============================================================================
    # BANK ACCOUNT CREATION TESTS
    # ============================================================================
    
    def test_create_bank_account_success(self, mock_validation_service, mock_bank_account_repository, mock_event_orchestrator, mock_session, sample_bank_account_data, sample_bank_account):
        """Test successful bank account creation."""
        # Setup mocks
        mock_validation_service.validate_entity_exists_or_raise.return_value = None
        mock_validation_service.validate_bank_exists_or_raise.return_value = None
        mock_validation_service.validate_account_name_or_raise.return_value = None
        mock_validation_service.validate_account_number_or_raise.return_value = None
        mock_validation_service.validate_currency_code_or_raise.return_value = None
        mock_validation_service.validate_account_status_or_raise.return_value = None
        mock_validation_service.normalize_currency.return_value = Currency.AUD
        mock_validation_service.normalize_account_status.return_value = AccountStatus.ACTIVE
        mock_validation_service.validate_bank_account_uniqueness_or_raise.return_value = None
        mock_bank_account_repository.create.return_value = sample_bank_account
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.create_bank_account(
            entity_id=sample_bank_account_data['entity_id'],
            bank_id=sample_bank_account_data['bank_id'],
            account_name=sample_bank_account_data['account_name'],
            account_number=sample_bank_account_data['account_number'],
            currency=sample_bank_account_data['currency'],
            status=sample_bank_account_data['status'],
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank_account
        
        # Verify validation calls
        mock_validation_service.validate_entity_exists_or_raise.assert_called_once_with(
            sample_bank_account_data['entity_id'], mock_session
        )
        mock_validation_service.validate_bank_exists_or_raise.assert_called_once_with(
            sample_bank_account_data['bank_id'], mock_session
        )
        mock_validation_service.validate_account_name_or_raise.assert_called_once_with(
            sample_bank_account_data['account_name']
        )
        mock_validation_service.validate_account_number_or_raise.assert_called_once_with(
            sample_bank_account_data['account_number']
        )
        mock_validation_service.validate_currency_code_or_raise.assert_called_once_with(
            sample_bank_account_data['currency']
        )
        mock_validation_service.validate_account_status_or_raise.assert_called_once_with(
            sample_bank_account_data['status']
        )
        mock_validation_service.normalize_currency.assert_called_once_with(
            sample_bank_account_data['currency']
        )
        mock_validation_service.normalize_account_status.assert_called_once_with(
            sample_bank_account_data['status']
        )
        mock_validation_service.validate_bank_account_uniqueness_or_raise.assert_called_once_with(
            sample_bank_account_data['entity_id'],
            sample_bank_account_data['bank_id'],
            sample_bank_account_data['account_number'],
            mock_session
        )
        
        # Verify repository call
        mock_bank_account_repository.create.assert_called_once()
    
    def test_create_bank_account_publishes_event(self, mock_validation_service, mock_bank_account_repository, mock_event_orchestrator, mock_session, sample_bank_account_data, sample_bank_account):
        """Test that bank account creation publishes events through orchestrator."""
        # Setup mocks
        mock_validation_service.validate_entity_exists_or_raise.return_value = None
        mock_validation_service.validate_bank_exists_or_raise.return_value = None
        mock_validation_service.validate_account_name_or_raise.return_value = None
        mock_validation_service.validate_account_number_or_raise.return_value = None
        mock_validation_service.validate_currency_code_or_raise.return_value = None
        mock_validation_service.validate_account_status_or_raise.return_value = None
        mock_validation_service.normalize_currency.return_value = Currency.AUD
        mock_validation_service.normalize_account_status.return_value = AccountStatus.ACTIVE
        mock_validation_service.validate_bank_account_uniqueness_or_raise.return_value = None
        mock_bank_account_repository.create.return_value = sample_bank_account
        mock_event_orchestrator.process_banking_event.return_value = {'status': 'success'}
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository, event_orchestrator=mock_event_orchestrator)
        
        # Execute
        result = service.create_bank_account(
            entity_id=sample_bank_account_data['entity_id'],
            bank_id=sample_bank_account_data['bank_id'],
            account_name=sample_bank_account_data['account_name'],
            account_number=sample_bank_account_data['account_number'],
            currency=sample_bank_account_data['currency'],
            status=sample_bank_account_data['status'],
            session=mock_session
        )
        
        # Verify event orchestrator was called
        mock_event_orchestrator.process_banking_event.assert_called_once()
        call_args = mock_event_orchestrator.process_banking_event.call_args
        
        # Verify event data structure
        event_data = call_args[0][0]  # First positional argument
        assert event_data['event_type'] == 'bank_account_created'
        assert event_data['entity_id'] == sample_bank_account_data['entity_id']
        assert event_data['bank_id'] == sample_bank_account_data['bank_id']
        assert event_data['account_name'] == sample_bank_account_data['account_name']
        assert event_data['account_number'] == sample_bank_account_data['account_number']
        assert event_data['currency'] == Currency.AUD
        assert event_data['status'] == AccountStatus.ACTIVE
        
        # Verify session and account were passed
        assert call_args[0][1] == mock_session  # Second positional argument (session)
        assert call_args[0][2] == sample_bank_account  # Third positional argument (account)
        call_args = mock_bank_account_repository.create.call_args[0]
        created_account = call_args[0]
        assert created_account.entity_id == sample_bank_account_data['entity_id']
        assert created_account.bank_id == sample_bank_account_data['bank_id']
        assert created_account.account_name == sample_bank_account_data['account_name']
        assert created_account.account_number == sample_bank_account_data['account_number']
        assert created_account.currency == Currency.AUD
        assert created_account.status == AccountStatus.ACTIVE
    
    def test_create_bank_account_with_enum_values(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account_data, sample_bank_account):
        """Test bank account creation with enum values."""
        # Setup mocks
        mock_validation_service.validate_entity_exists_or_raise.return_value = None
        mock_validation_service.validate_bank_exists_or_raise.return_value = None
        mock_validation_service.validate_account_name_or_raise.return_value = None
        mock_validation_service.validate_account_number_or_raise.return_value = None
        mock_validation_service.validate_currency_code_or_raise.return_value = None
        mock_validation_service.validate_account_status_or_raise.return_value = None
        mock_validation_service.normalize_currency.return_value = Currency.USD
        mock_validation_service.normalize_account_status.return_value = AccountStatus.SUSPENDED
        mock_validation_service.validate_bank_account_uniqueness_or_raise.return_value = None
        mock_bank_account_repository.create.return_value = sample_bank_account
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.create_bank_account(
            entity_id=sample_bank_account_data['entity_id'],
            bank_id=sample_bank_account_data['bank_id'],
            account_name=sample_bank_account_data['account_name'],
            account_number=sample_bank_account_data['account_number'],
            currency=Currency.USD,
            status=AccountStatus.SUSPENDED,
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank_account
        mock_validation_service.normalize_currency.assert_called_once_with(Currency.USD)
        mock_validation_service.normalize_account_status.assert_called_once_with(AccountStatus.SUSPENDED)
    
    def test_create_bank_account_with_boolean_status(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account_data, sample_bank_account):
        """Test bank account creation with boolean status."""
        # Setup mocks
        mock_validation_service.validate_entity_exists_or_raise.return_value = None
        mock_validation_service.validate_bank_exists_or_raise.return_value = None
        mock_validation_service.validate_account_name_or_raise.return_value = None
        mock_validation_service.validate_account_number_or_raise.return_value = None
        mock_validation_service.validate_currency_code_or_raise.return_value = None
        mock_validation_service.validate_account_status_or_raise.return_value = None
        mock_validation_service.normalize_currency.return_value = Currency.AUD
        mock_validation_service.normalize_account_status.return_value = AccountStatus.ACTIVE
        mock_validation_service.validate_bank_account_uniqueness_or_raise.return_value = None
        mock_bank_account_repository.create.return_value = sample_bank_account
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.create_bank_account(
            entity_id=sample_bank_account_data['entity_id'],
            bank_id=sample_bank_account_data['bank_id'],
            account_name=sample_bank_account_data['account_name'],
            account_number=sample_bank_account_data['account_number'],
            currency=sample_bank_account_data['currency'],
            status=AccountStatus.SUSPENDED,  # Use SUSPENDED status
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank_account
        mock_validation_service.validate_account_status_or_raise.assert_called_once_with(AccountStatus.SUSPENDED)
        mock_validation_service.normalize_account_status.assert_called_once_with(AccountStatus.SUSPENDED)
    
    def test_create_bank_account_validation_failure(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account_data):
        """Test bank account creation with validation failure."""
        # Setup mock to raise validation error
        mock_validation_service.validate_entity_exists_or_raise.side_effect = ValueError("Entity not found")
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Entity not found"):
            service.create_bank_account(
                entity_id=sample_bank_account_data['entity_id'],
                bank_id=sample_bank_account_data['bank_id'],
                account_name=sample_bank_account_data['account_name'],
                account_number=sample_bank_account_data['account_number'],
                currency=sample_bank_account_data['currency'],
                session=mock_session
            )
        
        # Verify repository was not called
        mock_bank_account_repository.create.assert_not_called()
    
    def test_create_bank_account_uniqueness_failure(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account_data):
        """Test bank account creation with uniqueness validation failure."""
        # Setup mocks
        mock_validation_service.validate_entity_exists_or_raise.return_value = None
        mock_validation_service.validate_bank_exists_or_raise.return_value = None
        mock_validation_service.validate_account_name_or_raise.return_value = None
        mock_validation_service.validate_account_number_or_raise.return_value = None
        mock_validation_service.validate_currency_code_or_raise.return_value = None
        mock_validation_service.validate_account_status_or_raise.return_value = None
        mock_validation_service.normalize_currency.return_value = Currency.AUD
        mock_validation_service.normalize_account_status.return_value = AccountStatus.ACTIVE
        mock_validation_service.validate_bank_account_uniqueness_or_raise.side_effect = ValueError("Account already exists")
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Account already exists"):
            service.create_bank_account(
                entity_id=sample_bank_account_data['entity_id'],
                bank_id=sample_bank_account_data['bank_id'],
                account_name=sample_bank_account_data['account_name'],
                account_number=sample_bank_account_data['account_number'],
                currency=sample_bank_account_data['currency'],
                session=mock_session
            )
        
        # Verify repository was not called
        mock_bank_account_repository.create.assert_not_called()
    
    # ============================================================================
    # BANK ACCOUNT UPDATE TESTS
    # ============================================================================
    
    def test_update_bank_account_success(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test successful bank account update."""
        # Setup mocks
        update_data = {
            'account_name': 'Updated Account Name',
            'currency': 'USD',
            'status': AccountStatus.SUSPENDED
        }
        mock_validation_service.validate_bank_account_data.return_value = None
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute
            result = service.update_bank_account(
                account_id=1,
                data=update_data,
                session=mock_session
            )
        
        # Verify
        assert result is sample_bank_account
        assert result.account_name == 'Updated Account Name'
        # Note: currency and is_active updates are handled by the service, not tested here
        
        # Verify validation call
        mock_validation_service.validate_bank_account_data.assert_called_once_with(
            update_data, mock_session, exclude_id=1
        )
            
    def test_update_bank_account_partial_update(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test bank account update with partial data."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}  # Only name update
        mock_validation_service.validate_bank_account_data.return_value = None
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute
            result = service.update_bank_account(
                account_id=1,
                data=update_data,
                session=mock_session
            )
        
        # Verify
        assert result is sample_bank_account
        assert result.account_name == 'Updated Account Name'
        assert result.currency == Currency.AUD  # Unchanged
        assert result.status == AccountStatus.ACTIVE  # Unchanged
    
    def test_update_bank_account_not_found(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test bank account update with non-existent account."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return None
        with patch.object(service, 'get_bank_account_by_id', return_value=None):
            # Execute and verify exception
            with pytest.raises(RuntimeError, match="Bank account not found"):
                service.update_bank_account(
                    account_id=999,
                    data=update_data,
                    session=mock_session
                )
        
        # Verify validation was not called
        mock_validation_service.validate_bank_account_data.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    def test_update_bank_account_validation_failure(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test bank account update with validation failure."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}
        mock_validation_service.validate_bank_account_data.side_effect = ValueError("Invalid account data")
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute and verify exception
            with pytest.raises(ValueError, match="Invalid account data"):
                service.update_bank_account(
                    account_id=1,
                    data=update_data,
                    session=mock_session
                )
        
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    # ============================================================================
    # BANK ACCOUNT DELETION TESTS
    # ============================================================================
    
    def test_delete_bank_account_success(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test successful bank account deletion."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Mock _has_dependent_fund_events to return False
            with patch.object(service, '_has_dependent_fund_events', return_value=False):
                # Execute
                result = service.delete_bank_account(
                    account_id=1,
                    session=mock_session
                )
        
        # Verify
        assert result is True
        
        # Verify account was deleted through repository
        mock_bank_account_repository.delete.assert_called_once_with(sample_bank_account, mock_session)
        # Note: Services no longer manage transactions - controllers handle commits
    
    def test_delete_bank_account_not_found(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test bank account deletion with non-existent account."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return None
        with patch.object(service, 'get_bank_account_by_id', return_value=None):
            # Execute and verify exception
            with pytest.raises(RuntimeError, match="Bank account not found"):
                service.delete_bank_account(
                    account_id=999,
                    session=mock_session
                )
        
        # Verify delete was not called
        mock_session.delete.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    def test_delete_bank_account_with_dependencies(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test bank account deletion with dependent cash flows."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Mock _has_dependent_fund_events to return True
            with patch.object(service, '_has_dependent_fund_events', return_value=True):
                # Execute and verify exception
                with pytest.raises(RuntimeError, match="Cannot delete bank account with dependent fund events"):
                    service.delete_bank_account(
                        account_id=1,
                        session=mock_session
                    )
        
        # Verify delete was not called
        mock_session.delete.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    # ============================================================================
    # BANK ACCOUNT QUERY TESTS
    # ============================================================================
    
    def test_get_bank_account_by_id(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test getting bank account by ID."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock repository method
        mock_bank_account_repository.get_by_id.return_value = sample_bank_account
        
        # Execute
        result = service.get_bank_account_by_id(1, mock_session)
        
        # Verify
        assert result is sample_bank_account
        mock_bank_account_repository.get_by_id.assert_called_once_with(1, mock_session)
    
    def test_get_bank_account_by_unique(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test getting bank account by unique combination."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Setup mock
        mock_bank_account_repository.get_by_unique.return_value = sample_bank_account
        
        # Execute
        result = service.get_bank_account_by_unique(
            entity_id=1,
            bank_id=1,
            account_number='1234-5678-9012-3456',
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank_account
        mock_bank_account_repository.get_by_unique.assert_called_once_with(1, 1, '1234-5678-9012-3456', mock_session)
    
    def test_get_all_bank_accounts(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test getting all bank accounts."""
        # Setup mocks
        expected_accounts = [Mock(), Mock()]
        mock_bank_account_repository.get_all.return_value = expected_accounts
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.get_all_bank_accounts(mock_session)
        
        # Verify
        assert result is expected_accounts
        mock_bank_account_repository.get_all.assert_called_once_with(mock_session)
    
    def test_get_bank_accounts_by_entity(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test getting bank accounts by entity."""
        # Setup mocks
        expected_accounts = [Mock(), Mock()]
        mock_bank_account_repository.get_by_entity.return_value = expected_accounts
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.get_bank_accounts_by_entity(1, mock_session)
        
        # Verify
        assert result is expected_accounts
        mock_bank_account_repository.get_by_entity.assert_called_once_with(1, mock_session)
    
    def test_get_bank_accounts_by_bank(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test getting bank accounts by bank."""
        # Setup mocks
        expected_accounts = [Mock(), Mock()]
        mock_bank_account_repository.get_by_bank.return_value = expected_accounts
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.get_bank_accounts_by_bank(1, mock_session)
        
        # Verify
        assert result is expected_accounts
        mock_bank_account_repository.get_by_bank.assert_called_once_with(1, mock_session)
    
    def test_get_bank_accounts_by_currency(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test getting bank accounts by currency."""
        # Setup mocks
        expected_accounts = [Mock(), Mock()]
        mock_bank_account_repository.get_by_currency.return_value = expected_accounts
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Execute
        result = service.get_bank_accounts_by_currency('AUD', mock_session)
        
        # Verify
        assert result is expected_accounts
        mock_bank_account_repository.get_by_currency.assert_called_once_with('AUD', mock_session)
    
    # ============================================================================
    # DEPENDENCY CHECKING TESTS
    # ============================================================================
    
    def test_has_dependent_fund_events_true(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test checking for dependent fund events when they exist."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock session query chain to return actual count
        mock_session.query.return_value.filter.return_value.count.return_value = 5
        
        # Execute
        result = service._has_dependent_fund_events(1, mock_session)
        
        # Verify
        assert result is True
    
    def test_has_dependent_fund_events_false(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test checking for dependent fund events when none exist."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock session query chain to return actual count
        mock_session.query.return_value.filter.return_value.count.return_value = 0
        
        # Execute
        result = service._has_dependent_fund_events(1, mock_session)
        
        # Verify
        assert result is False
    
    def test_get_dependent_fund_events_count(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test getting count of dependent fund events."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock session query chain to return actual count
        mock_session.query.return_value.filter.return_value.count.return_value = 7
        
        # Execute
        result = service.get_dependent_fund_events_count(1, mock_session)
        
        # Verify
        assert result == 7
    
    # ============================================================================
    # BUSINESS RULE ENFORCEMENT TESTS
    # ============================================================================
    
    def test_can_delete_bank_account_true(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test can_delete_bank_account when account can be deleted."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Mock get_dependent_fund_events_count to return 0
            with patch.object(service, 'get_dependent_fund_events_count', return_value=0):
                # Execute
                can_delete, reason = service.can_delete_bank_account(1, mock_session)
        
        # Verify
        assert can_delete is True
        assert reason == "Bank account can be deleted"
    
    def test_can_delete_bank_account_not_found(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test can_delete_bank_account when account not found."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return None
        with patch.object(service, 'get_bank_account_by_id', return_value=None):
            # Execute
            can_delete, reason = service.can_delete_bank_account(999, mock_session)
        
        # Verify
        assert can_delete is False
        assert reason == "Bank account not found"
    
    def test_can_delete_bank_account_with_dependencies(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test can_delete_bank_account when account has dependent cash flows."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Mock get_dependent_fund_events_count to return 4
            with patch.object(service, 'get_dependent_fund_events_count', return_value=4):
                # Execute
                can_delete, reason = service.can_delete_bank_account(1, mock_session)
        
        # Verify
        assert can_delete is False
        assert reason == "Bank account has 4 dependent fund events"
    
    def test_validate_bank_account_for_update_success(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test validate_bank_account_for_update when validation succeeds."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}
        mock_validation_service.validate_bank_account_data.return_value = None
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute
            can_update, reason = service.validate_bank_account_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is True
        assert reason == "Bank account can be updated"
        mock_validation_service.validate_bank_account_data.assert_called_once_with(
            update_data, mock_session, exclude_id=1
        )
    
    def test_validate_bank_account_for_update_account_not_found(self, mock_validation_service, mock_bank_account_repository, mock_session):
        """Test validate_bank_account_for_update when account not found."""
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return None
        with patch.object(service, 'get_bank_account_by_id', return_value=None):
            # Execute
            can_update, reason = service.validate_bank_account_for_update(999, {'account_name': 'Updated'}, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Bank account not found"
    
    def test_validate_bank_account_for_update_validation_failure(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test validate_bank_account_for_update when validation fails."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}
        mock_validation_service.validate_bank_account_data.side_effect = ValueError("Invalid account data")
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute
            can_update, reason = service.validate_bank_account_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Invalid account data"
    
    def test_validate_bank_account_for_update_exception(self, mock_validation_service, mock_bank_account_repository, mock_session, sample_bank_account):
        """Test validate_bank_account_for_update when exception occurs."""
        # Setup mocks
        update_data = {'account_name': 'Updated Account Name'}
        mock_validation_service.validate_bank_account_data.side_effect = Exception("Unexpected error")
        
        # Create service
        service = BankAccountService(mock_validation_service, mock_bank_account_repository)
        
        # Mock get_bank_account_by_id to return our sample account
        with patch.object(service, 'get_bank_account_by_id', return_value=sample_bank_account):
            # Execute
            can_update, reason = service.validate_bank_account_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Validation error: Unexpected error"
