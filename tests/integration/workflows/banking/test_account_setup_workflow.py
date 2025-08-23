"""
Banking Account Setup Workflow Tests.

This module tests the complete account setup workflow for banking operations,
including bank creation, bank account creation, and validation workflows.

Test Coverage:
- Bank creation workflow with validation
- Bank account creation workflow with validation
- Business rule enforcement during setup
- Error handling for invalid setups
- Cross-entity banking relationships
"""

import pytest
from sqlalchemy.orm import Session

from tests.factories import BankFactory, BankAccountFactory, EntityFactory
from src.banking.models import Bank, BankAccount
from src.banking.services.bank_service import BankService
from src.banking.services.bank_account_service import BankAccountService
from src.banking.services.banking_validation_service import BankingValidationService
from src.banking.enums import Country, Currency, AccountStatus
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository


class TestAccountSetupWorkflow:
    """Test suite for banking account setup workflows."""

    # ============================================================================
    # BANK CREATION WORKFLOW TESTS
    # ============================================================================

    def test_bank_creation_workflow_success(self, db_session: Session):
        """Test successful bank creation workflow with all validations."""
        # Arrange
        bank_service = BankService()
        bank_name = "Test Bank Australia"
        country = "AU"
        swift_bic = "TESTAU2X"

        # Act
        bank = bank_service.create_bank(
            name=bank_name,
            country=country,
            swift_bic=swift_bic,
            session=db_session
        )

        # Assert
        assert bank.id is not None
        assert bank.name == bank_name
        assert bank.country == Country.AU
        assert bank.swift_bic == swift_bic
        assert bank.created_at is not None
        assert bank.updated_at is not None

    def test_bank_creation_workflow_without_swift(self, db_session: Session):
        """Test bank creation workflow without SWIFT/BIC identifier."""
        # Arrange
        bank_service = BankService()
        bank_name = "Local Bank Australia"
        country = "AU"

        # Act
        bank = bank_service.create_bank(
            name=bank_name,
            country=country,
            session=db_session
        )

        # Assert
        assert bank.id is not None
        assert bank.name == bank_name
        assert bank.country == Country.AU
        assert bank.swift_bic is None

    def test_bank_creation_workflow_different_country(self, db_session: Session):
        """Test bank creation workflow with different country."""
        # Arrange
        bank_service = BankService()
        bank_name = "US Investment Bank"
        country = "US"
        swift_bic = "USIBUS3X"

        # Act
        bank = bank_service.create_bank(
            name=bank_name,
            country=country,
            swift_bic=swift_bic,
            session=db_session
        )

        # Assert
        assert bank.id is not None
        assert bank.name == bank_name
        assert bank.country == Country.US
        assert bank.swift_bic == swift_bic

    def test_bank_creation_workflow_duplicate_name_country(self, db_session: Session):
        """Test bank creation workflow prevents duplicate name/country combinations."""
        # Arrange
        bank_service = BankService()
        bank_name = "Duplicate Bank"
        country = "AU"

        # Create first bank
        first_bank = bank_service.create_bank(
            name=bank_name,
            country=country,
            session=db_session
        )
        assert first_bank.id is not None

        # Act & Assert - Attempt to create duplicate
        with pytest.raises(ValueError, match="Bank with this name already exists in this country"):
            bank_service.create_bank(
                name=bank_name,
                country=country,
                session=db_session
            )

    def test_bank_creation_workflow_same_name_different_country(self, db_session: Session):
        """Test bank creation workflow allows same name in different countries."""
        # Arrange
        bank_service = BankService()
        bank_name = "Global Bank"

        # Create bank in Australia
        au_bank = bank_service.create_bank(
            name=bank_name,
            country="AU",
            session=db_session
        )

        # Act - Create bank with same name in US
        us_bank = bank_service.create_bank(
            name=bank_name,
            country="US",
            session=db_session
        )

        # Assert
        assert au_bank.id != us_bank.id
        assert au_bank.name == us_bank.name
        assert au_bank.country == Country.AU
        assert us_bank.country == Country.US

    # ============================================================================
    # BANK ACCOUNT CREATION WORKFLOW TESTS
    # ============================================================================

    def test_bank_account_creation_workflow_success(self, db_session: Session):
        """Test successful bank account creation workflow."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        # Create bank first
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            session=db_session
        )
        
        # Create entity
        entity = EntityFactory()
        db_session.flush()

        # Act
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        # Assert
        assert account.id is not None
        assert account.entity_id == entity.id
        assert account.bank_id == bank.id
        assert account.account_name == "Test Account"
        assert account.account_number == "1234-5678-9012-3456"
        assert account.currency == Currency.AUD
        assert account.status == AccountStatus.ACTIVE
        assert account.created_at is not None
        assert account.updated_at is not None

    def test_bank_account_creation_workflow_different_currency(self, db_session: Session):
        """Test bank account creation workflow with different currency."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="US Bank",
            country="US",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()

        # Act
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="USD Account",
            account_number="9876-5432-1098-7654",
            currency="USD",
            session=db_session
        )

        # Assert
        assert account.currency == Currency.USD
        assert account.status == AccountStatus.ACTIVE  # Default status

    def test_bank_account_creation_workflow_inactive_status(self, db_session: Session):
        """Test bank account creation workflow with inactive status."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()

        # Act
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Inactive Account",
            account_number="1111-2222-3333-4444",
            currency="AUD",
            status=AccountStatus.SUSPENDED,
            session=db_session
        )

        # Assert
        assert account.status == AccountStatus.SUSPENDED

    def test_bank_account_creation_workflow_duplicate_account(self, db_session: Session):
        """Test bank account creation workflow prevents duplicate accounts."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()

        account_number = "5555-6666-7777-8888"

        # Create first account
        first_account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="First Account",
            account_number=account_number,
            currency="AUD",
            session=db_session
        )
        assert first_account.id is not None

        # Act & Assert - Attempt to create duplicate
        with pytest.raises(ValueError, match="Bank account already exists for this entity/bank/account_number"):
            account_service.create_bank_account(
                entity_id=entity.id,
                bank_id=bank.id,
                account_name="Second Account",
                account_number=account_number,
                currency="AUD",
                session=db_session
            )

    def test_bank_account_creation_workflow_prevents_same_number_different_entity(self, db_session: Session):
        """Test bank account creation workflow prevents same account number for different entities at same bank."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            session=db_session
        )
        
        entity1 = EntityFactory()
        entity2 = EntityFactory()
        db_session.flush()

        account_number = "9999-8888-7777-6666"

        # Create account for first entity
        account1 = account_service.create_bank_account(
            entity_id=entity1.id,
            bank_id=bank.id,
            account_name="Entity 1 Account",
            account_number=account_number,
            currency="AUD",
            session=db_session
        )

        # Act & Assert - Attempt to create account with same number for second entity should fail
        with pytest.raises(ValueError, match="Bank account already exists for this entity/bank/account_number or account number already exists at this bank"):
            account_service.create_bank_account(
                entity_id=entity2.id,
                bank_id=bank.id,
                account_name="Entity 2 Account",
                account_number=account_number,
                currency="AUD",
                session=db_session
            )

        # Assert - Only the first account should exist
        assert account1.id is not None
        assert account1.account_number == account_number
        assert account1.entity_id == entity1.id

    # ============================================================================
    # INTEGRATED ACCOUNT SETUP WORKFLOW TESTS
    # ============================================================================

    def test_complete_account_setup_workflow(self, db_session: Session):
        """Test complete account setup workflow from scratch."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        # Create multiple banks
        au_bank = bank_service.create_bank(
            name="Australia Bank",
            country="AU",
            swift_bic="AUSBAU2X",
            session=db_session
        )
        
        us_bank = bank_service.create_bank(
            name="US Bank",
            country="US",
            swift_bic="USBKUS3X",
            session=db_session
        )

        # Create entity
        entity = EntityFactory()
        db_session.flush()

        # Act - Create multiple accounts across banks
        aud_account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=au_bank.id,
            account_name="AUD Operating Account",
            account_number="AUD-001-002-003",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        usd_account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=us_bank.id,
            account_name="USD Investment Account",
            account_number="USD-001-002-003",
            currency="USD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        # Assert
        assert aud_account.bank_id == au_bank.id
        assert aud_account.currency == Currency.AUD
        assert usd_account.bank_id == us_bank.id
        assert usd_account.currency == Currency.USD
        
        # Verify relationships
        assert aud_account.bank == au_bank
        assert usd_account.bank == us_bank
        assert aud_account.entity == entity
        assert usd_account.entity == entity

    def test_account_setup_workflow_with_factory_pattern(self, db_session: Session):
        """Test account setup workflow using factory pattern for test data."""
        # Arrange - Set up factories
        BankFactory._meta.sqlalchemy_session = db_session
        BankAccountFactory._meta.sqlalchemy_session = db_session
        EntityFactory._meta.sqlalchemy_session = db_session

        # Act - Create using factories
        bank = BankFactory()
        entity = EntityFactory()
        account = BankAccountFactory(bank=bank, entity=entity)
        
        db_session.flush()

        # Assert
        assert bank.id is not None
        assert entity.id is not None
        assert account.id is not None
        assert account.bank_id == bank.id
        assert account.entity_id == entity.id
        assert account.bank == bank
        assert account.entity == entity

    def test_account_setup_workflow_validation_errors(self, db_session: Session):
        """Test account setup workflow handles validation errors properly."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()

        # Act & Assert - Invalid bank name
        with pytest.raises(ValueError, match="Bank name is required and cannot be empty"):
            bank_service.create_bank(
                name="",
                country="AU",
                session=db_session
            )

        # Act & Assert - Invalid country
        with pytest.raises(ValueError, match="Country must be a valid 2-letter ISO code"):
            bank_service.create_bank(
                name="Test Bank",
                country="INVALID",
                session=db_session
            )

        # Act & Assert - Invalid SWIFT/BIC
        with pytest.raises(ValueError, match="SWIFT/BIC must be 8 or 11 alphanumeric characters"):
            bank_service.create_bank(
                name="Test Bank",
                country="AU",
                swift_bic="INVALID",
                session=db_session
            )

    def test_account_setup_workflow_transaction_rollback(self, db_session: Session):
        """Test account setup workflow properly handles transaction rollback on errors."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        # Create valid bank
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()

        # Act - Attempt to create account with invalid entity ID
        with pytest.raises(ValueError, match="Entity not found"):
            account_service.create_bank_account(
                entity_id=99999,  # Non-existent entity
                bank_id=bank.id,
                account_name="Test Account",
                account_number="1234-5678-9012-3456",
                currency="AUD",
                session=db_session
            )

        # Assert - Bank should still exist (transaction rolled back)
        assert bank.id is not None
        # Verify no account was created
        accounts = db_session.query(BankAccount).filter_by(bank_id=bank.id).all()
        assert len(accounts) == 0
