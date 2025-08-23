"""
Banking Transaction Workflow Tests.

This module tests the complete transaction processing workflow for banking operations,
including banking updates, deletions, status changes, and business logic workflows.

Test Coverage:
- Banking update workflows with validation
- Banking deletion workflows with dependency checking
- Account status change workflows
- Currency change workflows
- Business rule enforcement during transactions
- Error handling for invalid transactions
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


class TestTransactionWorkflow:
    """Test suite for banking transaction workflows."""

    # ============================================================================
    # BANK UPDATE WORKFLOW TESTS
    # ============================================================================

    def test_bank_update_workflow_success(self, db_session: Session):
        """Test successful bank update workflow."""
        # Arrange
        bank_service = BankService()
        bank = bank_service.create_bank(
            name="Original Bank Name",
            country="AU",
            swift_bic="ORIGAU2X",
            session=db_session
        )
        
        original_name = bank.name
        original_swift = bank.swift_bic

        # Act
        updated_bank = bank_service.update_bank(
            bank_id=bank.id,
            data={
                "name": "Updated Bank Name",
                "swift_bic": "UPDTAU2X"
            },
            session=db_session
        )

        # Assert
        assert updated_bank.id == bank.id
        assert updated_bank.name == "Updated Bank Name"
        assert updated_bank.name != original_name
        assert updated_bank.swift_bic == "UPDTAU2X"
        assert updated_bank.swift_bic != original_swift
        assert updated_bank.country == Country.AU  # Unchanged
        assert updated_bank.updated_at > bank.created_at

    def test_bank_update_workflow_partial_update(self, db_session: Session):
        """Test bank update workflow with partial updates."""
        # Arrange
        bank_service = BankService()
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            swift_bic="TESTAU2X",
            session=db_session
        )
        
        original_name = bank.name
        original_swift = bank.swift_bic

        # Act - Update only name
        updated_bank = bank_service.update_bank(
            bank_id=bank.id,
            data={"name": "New Bank Name"},
            session=db_session
        )

        # Assert
        assert updated_bank.name == "New Bank Name"
        assert updated_bank.name != original_name
        assert updated_bank.swift_bic == original_swift  # Unchanged
        assert updated_bank.country == Country.AU  # Unchanged

    def test_bank_update_workflow_remove_swift(self, db_session: Session):
        """Test bank update workflow removing SWIFT/BIC."""
        # Arrange
        bank_service = BankService()
        bank = bank_service.create_bank(
            name="Test Bank",
            country="AU",
            swift_bic="TESTAU2X",
            session=db_session
        )
        
        assert bank.swift_bic == "TESTAU2X"

        # Act - Remove SWIFT/BIC
        updated_bank = bank_service.update_bank(
            bank_id=bank.id,
            data={"swift_bic": None},
            session=db_session
        )

        # Assert
        assert updated_bank.swift_bic is None

    def test_bank_update_workflow_duplicate_name_country(self, db_session: Session):
        """Test bank update workflow prevents duplicate name/country combinations."""
        # Arrange
        bank_service = BankService()
        
        # Create two banks
        bank1 = bank_service.create_bank(
            name="First Bank",
            country="AU",
            session=db_session
        )
        
        bank2 = bank_service.create_bank(
            name="Second Bank",
            country="AU",
            session=db_session
        )

        # Act & Assert - Attempt to update bank2 to have same name as bank1
        with pytest.raises(ValueError, match="Bank with this name already exists in this country"):
            bank_service.update_bank(
                bank_id=bank2.id,
                data={"name": "First Bank", "country": "AU"},  # Same name and country as bank1
                session=db_session
            )

    def test_bank_update_workflow_same_name_different_country(self, db_session: Session):
        """Test bank update workflow allows same name in different countries."""
        # Arrange
        bank_service = BankService()
        
        # Create banks in different countries
        au_bank = bank_service.create_bank(
            name="Global Bank",
            country="AU",
            session=db_session
        )
        
        us_bank = bank_service.create_bank(
            name="Different Bank",
            country="US",
            session=db_session
        )

        # Act - Update US bank to have same name as AU bank
        updated_us_bank = bank_service.update_bank(
            bank_id=us_bank.id,
            data={"name": "Global Bank"},  # Same name as AU bank
            session=db_session
        )

        # Assert
        assert updated_us_bank.name == "Global Bank"
        assert au_bank.name == "Global Bank"
        assert au_bank.country == Country.AU
        assert updated_us_bank.country == Country.US

    # ============================================================================
    # BANK ACCOUNT UPDATE WORKFLOW TESTS
    # ============================================================================

    def test_bank_account_update_workflow_success(self, db_session: Session):
        """Test successful bank account update workflow."""
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
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Original Account Name",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        # Act
        updated_account = account_service.update_bank_account(
            account_id=account.id,
            data={
                "account_name": "Updated Account Name",
                "currency": "USD",
                "status": AccountStatus.SUSPENDED
            },
            session=db_session
        )

        # Assert
        assert updated_account.id == account.id
        assert updated_account.account_name == "Updated Account Name"
        assert updated_account.currency == Currency.USD
        assert updated_account.status == AccountStatus.SUSPENDED
        assert updated_account.account_number == "1234-5678-9012-3456"  # Unchanged
        assert updated_account.updated_at > account.created_at

    def test_bank_account_update_workflow_partial_update(self, db_session: Session):
        """Test bank account update workflow with partial updates."""
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
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        original_name = account.account_name
        original_currency = account.currency

        # Act - Update only status
        updated_account = account_service.update_bank_account(
            account_id=account.id,
            data={"status": AccountStatus.SUSPENDED},
            session=db_session
        )

        # Assert
        assert updated_account.status == AccountStatus.SUSPENDED
        assert updated_account.account_name == original_name  # Unchanged
        assert updated_account.currency == original_currency  # Unchanged

    def test_bank_account_update_workflow_currency_change(self, db_session: Session):
        """Test bank account update workflow with currency changes."""
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
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            session=db_session
        )

        # Act - Change currency
        updated_account = account_service.update_bank_account(
            account_id=account.id,
            data={"currency": "USD"},
            session=db_session
        )

        # Assert
        assert updated_account.currency == Currency.USD
        assert updated_account.currency != Currency.AUD

    def test_bank_account_update_workflow_status_transitions(self, db_session: Session):
        """Test bank account update workflow with status transitions."""
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
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )

        # Act & Assert - Test various status transitions
        # ACTIVE -> SUSPENDED
        suspended_account = account_service.update_bank_account(
            account_id=account.id,
            data={"status": AccountStatus.SUSPENDED},
            session=db_session
        )
        assert suspended_account.status == AccountStatus.SUSPENDED

        # SUSPENDED -> ACTIVE
        reactivated_account = account_service.update_bank_account(
            account_id=account.id,
            data={"status": AccountStatus.ACTIVE},
            session=db_session
        )
        assert reactivated_account.status == AccountStatus.ACTIVE

    def test_bank_account_update_workflow_duplicate_account_number(self, db_session: Session):
        """Test bank account update workflow prevents duplicate account numbers."""
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
        
        # Create two accounts with different numbers
        account1 = account_service.create_bank_account(
            entity_id=entity1.id,
            bank_id=bank.id,
            account_name="Account 1",
            account_number="1111-1111-1111-1111",
            currency="AUD",
            session=db_session
        )
        
        account2 = account_service.create_bank_account(
            entity_id=entity2.id,
            bank_id=bank.id,
            account_name="Account 2",
            account_number="2222-2222-2222-2222",
            currency="AUD",
            session=db_session
        )

        # Act & Assert - Attempt to create a NEW account with same number as account1
        with pytest.raises(ValueError, match="Bank account already exists for this entity/bank/account_number"):
            account_service.create_bank_account(
                entity_id=entity2.id,
                bank_id=bank.id,
                account_name="Duplicate Account",
                account_number="1111-1111-1111-1111",  # Same as account1
                currency="AUD",
                session=db_session
            )

    # ============================================================================
    # BANKING DELETION WORKFLOW TESTS
    # ============================================================================

    def test_bank_deletion_workflow_success(self, db_session: Session):
        """Test successful bank deletion workflow."""
        # Arrange
        bank_service = BankService()
        bank = bank_service.create_bank(
            name="Bank to Delete",
            country="AU",
            session=db_session
        )
        
        bank_id = bank.id
        assert bank_id is not None

        # Act
        bank_service.delete_bank(bank_id, session=db_session)

        # Assert - Bank should be deleted
        deleted_bank = db_session.query(Bank).filter_by(id=bank_id).first()
        assert deleted_bank is None

    def test_bank_deletion_workflow_with_accounts(self, db_session: Session):
        """Test bank deletion workflow with existing accounts (should fail)."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="Bank with Accounts",
            country="AU",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()
        
        # Create account for this bank
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Test Account",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            session=db_session
        )
        
        assert account.id is not None

        # Act & Assert - Attempt to delete bank with accounts should fail
        with pytest.raises(RuntimeError, match="Cannot delete bank with dependent accounts"):
            bank_service.delete_bank(bank.id, session=db_session)

        # Assert - Bank and account should still exist
        assert db_session.query(Bank).filter_by(id=bank.id).first() is not None
        assert db_session.query(BankAccount).filter_by(id=account.id).first() is not None

    def test_bank_account_deletion_workflow_success(self, db_session: Session):
        """Test successful bank account deletion workflow."""
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
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Account to Delete",
            account_number="1234-5678-9012-3456",
            currency="AUD",
            session=db_session
        )
        
        account_id = account.id
        assert account_id is not None

        # Act
        account_service.delete_bank_account(account_id, session=db_session)

        # Assert - Account should be deleted
        deleted_account = db_session.query(BankAccount).filter_by(id=account_id).first()
        assert deleted_account is None
        
        # Bank should still exist
        assert db_session.query(Bank).filter_by(id=bank.id).first() is not None

    # ============================================================================
    # INTEGRATED TRANSACTION WORKFLOW TESTS
    # ============================================================================

    def test_complete_banking_transaction_workflow(self, db_session: Session):
        """Test complete banking transaction workflow from creation to deletion."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        # Create bank
        bank = bank_service.create_bank(
            name="Transaction Test Bank",
            country="AU",
            swift_bic="TRXTAU2X",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()

        # Act - Complete workflow
        # 1. Create account
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Transaction Account",
            account_number="TRX-001-002-003",
            currency="AUD",
            status=AccountStatus.ACTIVE,
            session=db_session
        )
        
        # 2. Update account
        updated_account = account_service.update_bank_account(
            account_id=account.id,
            data={
                "account_name": "Updated Transaction Account",
                "currency": "USD"
            },
            session=db_session
        )
        
        # 3. Change status
        inactive_account = account_service.update_bank_account(
            account_id=account.id,
            data={"status": AccountStatus.SUSPENDED},
            session=db_session
        )
        
        # 4. Reactivate account
        reactivated_account = account_service.update_bank_account(
            account_id=account.id,
            data={"status": AccountStatus.ACTIVE},
            session=db_session
        )
        
        # 5. Delete account
        account_service.delete_bank_account(account.id, session=db_session)
        
        # 6. Delete bank
        bank_service.delete_bank(bank.id, session=db_session)

        # Assert - Everything should be cleaned up
        assert db_session.query(BankAccount).filter_by(id=account.id).first() is None
        assert db_session.query(Bank).filter_by(id=bank.id).first() is None

    def test_transaction_workflow_validation_errors(self, db_session: Session):
        """Test transaction workflow handles validation errors properly."""
        # Arrange
        bank_service = BankService()
        account_service = BankAccountService()
        
        bank = bank_service.create_bank(
            name="Validation Test Bank",
            country="AU",
            session=db_session
        )
        
        entity = EntityFactory()
        db_session.flush()
        
        account = account_service.create_bank_account(
            entity_id=entity.id,
            bank_id=bank.id,
            account_name="Validation Account",
            account_number="VAL-001-002-003",
            currency="AUD",
            session=db_session
        )

        # Act & Assert - Invalid updates
        with pytest.raises(ValueError, match="Account name is required and cannot be empty"):
            account_service.update_bank_account(
                account_id=account.id,
                data={"account_name": ""},
                session=db_session
            )

        with pytest.raises(ValueError, match="Currency must be a valid 3-letter ISO code"):
            account_service.update_bank_account(
                account_id=account.id,
                data={"currency": "INVALID"},
                session=db_session
            )

        with pytest.raises(ValueError, match="Account status must be a valid AccountStatus enum"):
            account_service.update_bank_account(
                account_id=account.id,
                data={"status": "INVALID"},
                session=db_session
            )

    def test_transaction_workflow_with_factory_pattern(self, db_session: Session):
        """Test transaction workflow using factory pattern for test data."""
        # Arrange - Set up factories
        BankFactory._meta.sqlalchemy_session = db_session
        BankAccountFactory._meta.sqlalchemy_session = db_session
        EntityFactory._meta.sqlalchemy_session = db_session

        # Act - Create and manipulate using factories
        bank = BankFactory()
        entity = EntityFactory()
        account = BankAccountFactory(bank=bank, entity=entity)
        
        db_session.flush()
        
        # Update account
        account_service = BankAccountService()
        updated_account = account_service.update_bank_account(
            account_id=account.id,
            data={
                "account_name": "Factory Updated Account",
                "currency": "USD"
            },
            session=db_session
        )
        
        # Assert
        assert updated_account.account_name == "Factory Updated Account"
        assert updated_account.currency == Currency.USD
        assert updated_account.bank == bank
        assert updated_account.entity == entity
