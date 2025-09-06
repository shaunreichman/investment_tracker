"""
Bank Service Tests

This module tests the BankService business logic and operations.
Focus: Service layer business logic, validation coordination, and business rules.

Other aspects covered elsewhere:
- Model validation: test_bank_model.py
- Repository operations: test_bank_repository.py
- API operations: test_bank_controller.py
- Event processing: test_bank_event_handlers.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.banking.services.bank_service import BankService
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.repositories.bank_repository import BankRepository
from src.banking.events.orchestrator import BankingUpdateOrchestrator
from src.banking.events.registry import BankingEventHandlerRegistry
from src.banking.models.bank import Bank
from src.banking.enums import Country


class TestBankService:
    """Test suite for BankService - Business logic and operations only"""
    
    @pytest.fixture
    def mock_validation_service(self):
        """Mock validation service for testing."""
        return Mock(spec=BankingValidationService)
    
    @pytest.fixture
    def mock_bank_repository(self):
        """Mock bank repository for testing."""
        return Mock(spec=BankRepository)
    
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
    def sample_bank_data(self):
        """Sample bank data for testing."""
        return {
            'name': 'Test Bank',
            'country': 'AU',
            'swift_bic': 'TESTAU2X'
        }
    
    @pytest.fixture
    def sample_bank(self):
        """Sample bank instance for testing."""
        return Bank(
            id=1,
            name='Test Bank',
            country=Country.AU,
            swift_bic='TESTAU2X'
        )
    
    # ============================================================================
    # INITIALIZATION TESTS
    # ============================================================================
    
    def test_bank_service_initialization_defaults(self):
        """Test BankService initialization with default dependencies."""
        service = BankService()
        
        assert service.validation_service is not None
        assert isinstance(service.validation_service, BankingValidationService)
        assert service.bank_repository is not None
        assert isinstance(service.bank_repository, BankRepository)
    
    def test_bank_service_initialization_with_dependencies(self, mock_validation_service, mock_bank_repository):
        """Test BankService initialization with provided dependencies."""
        service = BankService(
            validation_service=mock_validation_service,
            bank_repository=mock_bank_repository
        )
        
        assert service.validation_service is mock_validation_service
        assert service.bank_repository is mock_bank_repository
    
    # ============================================================================
    # BANK CREATION TESTS
    # ============================================================================
    
    def test_create_bank_success(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank_data, sample_bank):
        """Test successful bank creation."""
        # Setup mocks
        mock_validation_service.validate_bank_name_or_raise.return_value = None
        mock_validation_service.validate_country_code_or_raise.return_value = None
        mock_validation_service.validate_swift_bic_or_raise.return_value = None
        mock_validation_service.normalize_country.return_value = Country.AU
        mock_validation_service.validate_bank_uniqueness_or_raise.return_value = None
        mock_bank_repository.create.return_value = sample_bank
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute
        result = service.create_bank(
            name=sample_bank_data['name'],
            country=sample_bank_data['country'],
            swift_bic=sample_bank_data['swift_bic'],
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank
        
        # Verify validation calls
        mock_validation_service.validate_bank_name_or_raise.assert_called_once_with(sample_bank_data['name'])
        mock_validation_service.validate_country_code_or_raise.assert_called_once_with(sample_bank_data['country'])
        mock_validation_service.validate_swift_bic_or_raise.assert_called_once_with(sample_bank_data['swift_bic'])
        mock_validation_service.normalize_country.assert_called_once_with(sample_bank_data['country'])
        mock_validation_service.validate_bank_uniqueness_or_raise.assert_called_once_with(
            sample_bank_data['name'], Country.AU, mock_session
        )
        
        # Verify repository call
        mock_bank_repository.create.assert_called_once()
        call_args = mock_bank_repository.create.call_args[0]
        created_bank = call_args[0]
        assert created_bank.name == sample_bank_data['name'].strip()
        assert created_bank.country == Country.AU
        assert created_bank.swift_bic == sample_bank_data['swift_bic']
    
    def test_create_bank_publishes_event(self, mock_validation_service, mock_bank_repository, mock_event_orchestrator, mock_session, sample_bank_data, sample_bank):
        """Test that bank creation publishes events through orchestrator."""
        # Setup mocks
        mock_validation_service.validate_bank_name_or_raise.return_value = None
        mock_validation_service.validate_country_code_or_raise.return_value = None
        mock_validation_service.validate_swift_bic_or_raise.return_value = None
        mock_validation_service.normalize_country.return_value = Country.AU
        mock_validation_service.validate_bank_uniqueness_or_raise.return_value = None
        mock_bank_repository.create.return_value = sample_bank
        mock_event_orchestrator.process_banking_event.return_value = {'status': 'success'}
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository, event_orchestrator=mock_event_orchestrator)
        
        # Execute
        result = service.create_bank(
            name=sample_bank_data['name'],
            country=sample_bank_data['country'],
            swift_bic=sample_bank_data['swift_bic'],
            session=mock_session
        )
        
        # Verify event orchestrator was called
        mock_event_orchestrator.process_banking_event.assert_called_once()
        call_args = mock_event_orchestrator.process_banking_event.call_args
        
        # Verify event data structure
        event_data = call_args[0][0]  # First positional argument
        assert event_data['event_type'] == 'bank_created'
        assert event_data['bank_id'] == sample_bank.id
        assert event_data['name'] == sample_bank.name
        assert event_data['country'] == sample_bank.country
        assert event_data['swift_bic'] == sample_bank.swift_bic
        
        # Verify session and bank were passed
        assert call_args[0][1] == mock_session  # Second positional argument (session)
        assert call_args[0][2] == sample_bank  # Third positional argument (bank)
    
    def test_create_bank_with_enum_country(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank_data, sample_bank):
        """Test bank creation with Country enum."""
        # Setup mocks
        mock_validation_service.validate_bank_name_or_raise.return_value = None
        mock_validation_service.validate_country_code_or_raise.return_value = None
        mock_validation_service.validate_swift_bic_or_raise.return_value = None
        mock_validation_service.normalize_country.return_value = Country.US
        mock_validation_service.validate_bank_uniqueness_or_raise.return_value = None
        mock_bank_repository.create.return_value = sample_bank
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute
        result = service.create_bank(
            name=sample_bank_data['name'],
            country=Country.US,
            swift_bic=sample_bank_data['swift_bic'],
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank
        mock_validation_service.normalize_country.assert_called_once_with(Country.US)
    
    def test_create_bank_without_swift_bic(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank_data, sample_bank):
        """Test bank creation without SWIFT/BIC."""
        # Setup mocks
        mock_validation_service.validate_bank_name_or_raise.return_value = None
        mock_validation_service.validate_country_code_or_raise.return_value = None
        mock_validation_service.validate_swift_bic_or_raise.return_value = None
        mock_validation_service.normalize_country.return_value = Country.AU
        mock_validation_service.validate_bank_uniqueness_or_raise.return_value = None
        mock_bank_repository.create.return_value = sample_bank
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute
        result = service.create_bank(
            name=sample_bank_data['name'],
            country=sample_bank_data['country'],
            session=mock_session
        )
        
        # Verify
        assert result is sample_bank
        mock_validation_service.validate_swift_bic_or_raise.assert_called_once_with(None)
    
    def test_create_bank_validation_failure(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank_data):
        """Test bank creation with validation failure."""
        # Setup mock to raise validation error
        mock_validation_service.validate_bank_name_or_raise.side_effect = ValueError("Invalid bank name")
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Invalid bank name"):
            service.create_bank(
                name=sample_bank_data['name'],
                country=sample_bank_data['country'],
                session=mock_session
            )
        
        # Verify repository was not called
        mock_bank_repository.create.assert_not_called()
    
    def test_create_bank_uniqueness_failure(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank_data):
        """Test bank creation with uniqueness validation failure."""
        # Setup mocks
        mock_validation_service.validate_bank_name_or_raise.return_value = None
        mock_validation_service.validate_country_code_or_raise.return_value = None
        mock_validation_service.validate_swift_bic_or_raise.return_value = None
        mock_validation_service.normalize_country.return_value = Country.AU
        mock_validation_service.validate_bank_uniqueness_or_raise.side_effect = ValueError("Bank already exists")
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute and verify exception
        with pytest.raises(ValueError, match="Bank already exists"):
            service.create_bank(
                name=sample_bank_data['name'],
                country=sample_bank_data['country'],
                session=mock_session
            )
        
        # Verify repository was not called
        mock_bank_repository.create.assert_not_called()
    
    # ============================================================================
    # BANK UPDATE TESTS
    # ============================================================================
    
    def test_update_bank_success(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test successful bank update."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name', 'country': 'US'}
        mock_validation_service.validate_bank_data.return_value = None
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute
            result = service.update_bank(
                bank_id=1,
                data=update_data,
                session=mock_session
            )
        
        # Verify
        assert result is sample_bank
        assert result.name == 'Updated Bank Name'
        assert result.country == 'US'
        
        # Verify validation call
        mock_validation_service.validate_bank_data.assert_called_once_with(
            update_data, mock_session, exclude_id=1
        )
            
    def test_update_bank_partial_update(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test bank update with partial data."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}  # Only name update
        mock_validation_service.validate_bank_data.return_value = None
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute
            result = service.update_bank(
                bank_id=1,
                data=update_data,
                session=mock_session
            )
        
        # Verify
        assert result is sample_bank
        assert result.name == 'Updated Bank Name'
        assert result.country == Country.AU  # Unchanged
        assert result.swift_bic == 'TESTAU2X'  # Unchanged
    
    def test_update_bank_not_found(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test bank update with non-existent bank."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return None
        with patch.object(service, 'get_bank_by_id', return_value=None):
            # Execute and verify exception
            with pytest.raises(RuntimeError, match="Bank not found"):
                service.update_bank(
                    bank_id=999,
                    data=update_data,
                    session=mock_session
                )
        
        # Verify validation was not called
        mock_validation_service.validate_bank_data.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    def test_update_bank_validation_failure(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test bank update with validation failure."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}
        mock_validation_service.validate_bank_data.side_effect = ValueError("Invalid bank data")
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute and verify exception
            with pytest.raises(ValueError, match="Invalid bank data"):
                service.update_bank(
                    bank_id=1,
                    data=update_data,
                    session=mock_session
                )
        
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    # ============================================================================
    # BANK DELETION TESTS
    # ============================================================================
    
    def test_delete_bank_success(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test successful bank deletion."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Mock _has_dependent_accounts to return False
            with patch.object(service, '_has_dependent_accounts', return_value=False):
                # Execute
                result = service.delete_bank(
                    bank_id=1,
                    session=mock_session
                )
        
        # Verify
        assert result is True
        
        # Verify bank was deleted through repository
        mock_bank_repository.delete.assert_called_once_with(sample_bank, mock_session)
        # Note: Services no longer manage transactions - controllers handle commits
    
    def test_delete_bank_not_found(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test bank deletion with non-existent bank."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return None
        with patch.object(service, 'get_bank_by_id', return_value=None):
            # Execute and verify exception
            with pytest.raises(RuntimeError, match="Bank not found"):
                service.delete_bank(
                    bank_id=999,
                    session=mock_session
                )
        
        # Verify delete was not called
        mock_session.delete.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    def test_delete_bank_with_dependencies(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test bank deletion with dependent accounts."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Mock _has_dependent_accounts to return True
            with patch.object(service, '_has_dependent_accounts', return_value=True):
                # Execute and verify exception
                with pytest.raises(RuntimeError, match="Cannot delete bank with dependent accounts"):
                    service.delete_bank(
                        bank_id=1,
                        session=mock_session
                    )
        
        # Verify delete was not called
        mock_session.delete.assert_not_called()
        # Verify session commit was not called
        mock_session.commit.assert_not_called()
    
    # ============================================================================
    # BANK QUERY TESTS
    # ============================================================================
    
    def test_get_bank_by_id(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test getting bank by ID."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock repository method
        mock_bank_repository.get_by_id.return_value = sample_bank
        
        # Execute
        result = service.get_bank_by_id(1, mock_session)
        
        # Verify
        assert result is sample_bank
        mock_bank_repository.get_by_id.assert_called_once_with(1, mock_session)
    
    def test_get_bank_by_name_and_country(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test getting bank by name and country."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock repository method
        mock_bank_repository.get_by_name_and_country.return_value = sample_bank
        
        # Execute
        result = service.get_bank_by_name_and_country('Test Bank', 'AU', mock_session)
        
        # Verify
        assert result is sample_bank
        mock_bank_repository.get_by_name_and_country.assert_called_once_with('Test Bank', 'AU', mock_session)
    
    def test_get_all_banks(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test getting all banks."""
        # Setup mocks
        expected_banks = [Mock(), Mock()]
        mock_bank_repository.get_all.return_value = expected_banks
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute
        result = service.get_all_banks(mock_session)
        
        # Verify
        assert result is expected_banks
        mock_bank_repository.get_all.assert_called_once_with(mock_session)
    
    def test_get_banks_by_country(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test getting banks by country."""
        # Setup mocks
        expected_banks = [Mock(), Mock()]
        mock_bank_repository.get_by_country.return_value = expected_banks
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Execute
        result = service.get_banks_by_country('AU', mock_session)
        
        # Verify
        assert result is expected_banks
        mock_bank_repository.get_by_country.assert_called_once_with('AU', mock_session)
    
    # ============================================================================
    # DEPENDENCY CHECKING TESTS
    # ============================================================================
    
    def test_has_dependent_accounts_true(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test checking for dependent accounts when they exist."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock BankAccountRepository
        mock_account_repo = Mock()
        mock_account_repo.count_by_bank.return_value = 3
        
        with patch('src.banking.repositories.bank_account_repository.BankAccountRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_account_repo
            # Execute
            result = service._has_dependent_accounts(1, mock_session)
        
        # Verify
        assert result is True
        mock_account_repo.count_by_bank.assert_called_once_with(1, mock_session)
    
    def test_has_dependent_accounts_false(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test checking for dependent accounts when none exist."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock BankAccountRepository
        mock_account_repo = Mock()
        mock_account_repo.count_by_bank.return_value = 0
        
        with patch('src.banking.repositories.bank_account_repository.BankAccountRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_account_repo
            # Execute
            result = service._has_dependent_accounts(1, mock_session)
        
        # Verify
        assert result is False
        mock_account_repo.count_by_bank.assert_called_once_with(1, mock_session)
    
    def test_get_dependent_accounts_count(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test getting count of dependent accounts."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock BankAccountRepository
        mock_account_repo = Mock()
        mock_account_repo.count_by_bank.return_value = 5
        
        with patch('src.banking.repositories.bank_account_repository.BankAccountRepository') as mock_repo_class:
            mock_repo_class.return_value = mock_account_repo
            # Execute
            result = service.get_dependent_accounts_count(1, mock_session)
        
        # Verify
        assert result == 5
        mock_account_repo.count_by_bank.assert_called_once_with(1, mock_session)
    
    # ============================================================================
    # BUSINESS RULE ENFORCEMENT TESTS
    # ============================================================================
    
    def test_can_delete_bank_true(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test can_delete_bank when bank can be deleted."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Mock get_dependent_accounts_count to return 0
            with patch.object(service, 'get_dependent_accounts_count', return_value=0):
                # Execute
                can_delete, reason = service.can_delete_bank(1, mock_session)
        
        # Verify
        assert can_delete is True
        assert reason == "Bank can be deleted"
    
    def test_can_delete_bank_not_found(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test can_delete_bank when bank not found."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return None
        with patch.object(service, 'get_bank_by_id', return_value=None):
            # Execute
            can_delete, reason = service.can_delete_bank(999, mock_session)
        
        # Verify
        assert can_delete is False
        assert reason == "Bank not found"
    
    def test_can_delete_bank_with_dependencies(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test can_delete_bank when bank has dependent accounts."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Mock get_dependent_accounts_count to return 3
            with patch.object(service, 'get_dependent_accounts_count', return_value=3):
                # Execute
                can_delete, reason = service.can_delete_bank(1, mock_session)
        
        # Verify
        assert can_delete is False
        assert reason == "Bank has 3 dependent accounts"
    
    def test_validate_bank_for_update_success(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test validate_bank_for_update when validation succeeds."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}
        mock_validation_service.validate_bank_data.return_value = None
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute
            can_update, reason = service.validate_bank_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is True
        assert reason == "Bank can be updated"
        mock_validation_service.validate_bank_data.assert_called_once_with(
            update_data, mock_session, exclude_id=1
        )
    
    def test_validate_bank_for_update_bank_not_found(self, mock_validation_service, mock_bank_repository, mock_session):
        """Test validate_bank_for_update when bank not found."""
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return None
        with patch.object(service, 'get_bank_by_id', return_value=None):
            # Execute
            can_update, reason = service.validate_bank_for_update(999, {'name': 'Updated'}, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Bank not found"
    
    def test_validate_bank_for_update_validation_failure(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test validate_bank_for_update when validation fails."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}
        mock_validation_service.validate_bank_data.side_effect = ValueError("Invalid bank data")
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute
            can_update, reason = service.validate_bank_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Invalid bank data"
    
    def test_validate_bank_for_update_exception(self, mock_validation_service, mock_bank_repository, mock_session, sample_bank):
        """Test validate_bank_for_update when exception occurs."""
        # Setup mocks
        update_data = {'name': 'Updated Bank Name'}
        mock_validation_service.validate_bank_data.side_effect = Exception("Unexpected error")
        
        # Create service
        service = BankService(mock_validation_service, mock_bank_repository)
        
        # Mock get_bank_by_id to return our sample bank
        with patch.object(service, 'get_bank_by_id', return_value=sample_bank):
            # Execute
            can_update, reason = service.validate_bank_for_update(1, update_data, mock_session)
        
        # Verify
        assert can_update is False
        assert reason == "Validation error: Unexpected error"
