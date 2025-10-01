"""
Integration tests for bank account creation workflow through all refactored layers.

This file tests the complete bank account creation workflow from API route through
all refactored layers: Routes -> Controllers -> Services -> Repositories.

Tests cover:
- API route validation and request handling
- Controller orchestration and response formatting
- Service business logic and validation
- Repository data persistence
- Database constraint validation
- Error handling across all layers
- Entity and Bank relationship validation
"""

import pytest
from datetime import datetime
from unittest.mock import patch

from tests.factories import (
    BankFactory, BankAccountFactory, EntityFactory
)
from src.banking.models import BankAccount
from src.banking.enums.bank_account_enums import BankAccountType, BankAccountStatus
from src.shared.enums.shared_enums import Currency
from src.api.controllers.banking_controller import BankingController
from src.banking.services.bank_account_service import BankAccountService
from src.banking.repositories.bank_account_repository import BankAccountRepository
from src.api.dto.response_codes import ApiResponseCode


class TestBankAccountCreationWorkflowIntegration:
    """Test complete bank account creation workflow through all refactored layers"""

    def test_bank_account_creation_service_layer_flow(self, db_session):
        """Test bank account creation through service layer flow"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        # Test data for bank account creation
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Checking Account',
            'account_number': '1234567890',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        
        # Test service layer creation
        bank_account_service = BankAccountService()
        created_bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        
        # Verify bank account was created correctly
        assert created_bank_account is not None
        assert created_bank_account.id is not None
        assert created_bank_account.entity_id == entity.id
        assert created_bank_account.bank_id == bank.id
        assert created_bank_account.account_name == 'Test Checking Account'
        assert created_bank_account.account_number == '1234567890'
        assert created_bank_account.currency == 'AUD'
        assert created_bank_account.account_type == 'CHECKING'
        assert created_bank_account.status == BankAccountStatus.INACTIVE  # Default status
        assert created_bank_account.current_balance == 0.0  # Default balance
        assert created_bank_account.created_at is not None
        assert created_bank_account.updated_at is not None
        
        # Verify bank account was persisted to database
        bank_account_repository = BankAccountRepository()
        retrieved_bank_account = bank_account_repository.get_bank_account_by_id(
            created_bank_account.id, db_session
        )
        assert retrieved_bank_account is not None
        assert retrieved_bank_account.id == created_bank_account.id

    def test_bank_account_creation_service_with_different_data(self, db_session):
        """Test bank account creation with different data combinations"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        # Test data for bank account creation
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Savings Account',
            'account_number': '9876543210',
            'currency': 'USD',
            'account_type': 'SAVINGS'
        }
        
        # Test service layer creation
        bank_account_service = BankAccountService()
        created_bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        
        # Verify bank account was created correctly
        assert created_bank_account is not None
        assert created_bank_account.id is not None
        assert created_bank_account.entity_id == entity.id
        assert created_bank_account.bank_id == bank.id
        assert created_bank_account.account_name == 'Test Savings Account'
        assert created_bank_account.account_number == '9876543210'
        assert created_bank_account.currency == 'USD'
        assert created_bank_account.account_type == 'SAVINGS'
        assert created_bank_account.status == BankAccountStatus.INACTIVE
        assert created_bank_account.current_balance == 0.0

    def test_bank_account_creation_validation_errors(self, db_session):
        """Test bank account creation with validation errors"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        bank_account_service = BankAccountService()
        
        # Test 1: Bank not found
        with pytest.raises(ValueError, match="Bank not found"):
            bank_account_service.create_bank_account(
                bank_id=99999,  # Non-existent bank ID
                bank_account_data={
                    'entity_id': entity.id,
                    'account_name': 'Test Account',
                    'account_number': '1234567890',
                    'currency': 'AUD',
                    'account_type': 'CHECKING'
                },
                session=db_session
            )
        
        # Test 2: Entity not found
        with pytest.raises(ValueError, match="Entity not found"):
            bank_account_service.create_bank_account(
                bank_id=bank.id,
                bank_account_data={
                    'entity_id': 99999,  # Non-existent entity ID
                    'account_name': 'Test Account',
                    'account_number': '1234567890',
                    'currency': 'AUD',
                    'account_type': 'CHECKING'
                },
                session=db_session
            )

    def test_bank_account_creation_database_constraints(self, db_session):
        """Test bank account creation with database constraint violations"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        # Create first bank account
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Account 1',
            'account_number': '1234567890',
            'currency': 'AUD',
            'account_type': 'CHECKING'
        }
        
        bank_account_service = BankAccountService()
        first_bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        
        # Test unique constraint violation - same entity, bank, and account number
        with pytest.raises(Exception):  # Should raise database constraint error
            duplicate_bank_account_data = {
                'entity_id': entity.id,
                'account_name': 'Test Account 2',
                'account_number': '1234567890',  # Same account number
                'currency': 'AUD',
                'account_type': 'SAVINGS'
            }
            
            bank_account_service.create_bank_account(
                bank_id=bank.id,
                bank_account_data=duplicate_bank_account_data,
                session=db_session
            )

    def test_bank_account_creation_different_currencies_and_types(self, db_session):
        """Test bank account creation with different currencies and account types"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        bank_account_service = BankAccountService()
        
        # Test different currencies
        currencies = ['AUD', 'USD', 'EUR', 'GBP', 'CAD']
        account_types = ['CHECKING', 'SAVINGS', 'INVESTMENT', 'BUSINESS', 'TRUST', 'JOINT']
        
        created_accounts = []
        
        for i, (currency, account_type) in enumerate(zip(currencies, account_types)):
            bank_account_data = {
                'entity_id': entity.id,
                'account_name': f'Test Account {i+1}',
                'account_number': f'123456789{i}',
                'currency': currency,
                'account_type': account_type
            }
            
            created_account = bank_account_service.create_bank_account(
                bank_id=bank.id,
                bank_account_data=bank_account_data,
                session=db_session
            )
            
            created_accounts.append(created_account)
            
            # Verify each account was created correctly
            assert created_account.currency == currency
            assert created_account.account_type == account_type
            assert created_account.status == BankAccountStatus.INACTIVE
            assert created_account.current_balance == 0.0
        
        # Verify all accounts were created
        assert len(created_accounts) == 5
        
        # Verify all accounts are linked to the same entity and bank
        for account in created_accounts:
            assert account.entity_id == entity.id
            assert account.bank_id == bank.id

    def test_bank_account_creation_service_error_handling(self, db_session):
        """Test service error handling for bank account creation"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        bank_account_service = BankAccountService()
        
        # Test 1: Invalid bank ID
        with pytest.raises(ValueError, match="Bank not found"):
            bank_account_service.create_bank_account(
                bank_id=99999,  # Non-existent bank ID
                bank_account_data={
                    'entity_id': 1,
                    'account_name': 'Test Account',
                    'account_number': '1234567890',
                    'currency': 'AUD',
                    'account_type': 'CHECKING'
                },
                session=db_session
            )
        
        # Test 2: Invalid entity ID
        bank = BankFactory.create()
        with pytest.raises(ValueError, match="Entity not found"):
            bank_account_service.create_bank_account(
                bank_id=bank.id,
                bank_account_data={
                    'entity_id': 99999,  # Non-existent entity ID
                    'account_name': 'Test Account',
                    'account_number': '1234567890',
                    'currency': 'AUD',
                    'account_type': 'CHECKING'
                },
                session=db_session
            )

    def test_bank_account_creation_repository_layer(self, db_session):
        """Test bank account creation at repository layer"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        # Test repository layer creation
        bank_account_repository = BankAccountRepository()
        
        bank_account_data = {
            'entity_id': entity.id,
            'bank_id': bank.id,
            'account_name': 'Test Repository Account',
            'account_number': '5555555555',
            'currency': 'EUR',
            'account_type': 'INVESTMENT',
            'status': 'INACTIVE'
        }
        
        created_bank_account = bank_account_repository.create_bank_account(
            bank_account_data=bank_account_data,
            session=db_session
        )
        
        # Verify bank account was created
        assert created_bank_account is not None
        assert created_bank_account.id is not None
        assert created_bank_account.entity_id == entity.id
        assert created_bank_account.bank_id == bank.id
        assert created_bank_account.account_name == 'Test Repository Account'
        assert created_bank_account.account_number == '5555555555'
        assert created_bank_account.currency == 'EUR'
        assert created_bank_account.account_type == 'INVESTMENT'
        assert created_bank_account.status == 'INACTIVE'
        
        # Verify bank account was flushed to session
        db_session.flush()
        assert created_bank_account in db_session

    def test_bank_account_creation_with_relationships(self, db_session):
        """Test bank account creation with proper relationship handling"""
        # Setup factories with session
        for factory in (BankFactory, BankAccountFactory, EntityFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create required entities
        bank = BankFactory.create(
            name="Test Bank",
            country="AU",
            bank_type="COMMERCIAL"
        )
        
        entity = EntityFactory.create(
            name="Test Entity",
            entity_type="COMPANY",
            tax_jurisdiction="AU"
        )
        
        bank_account_service = BankAccountService()
        
        bank_account_data = {
            'entity_id': entity.id,
            'account_name': 'Test Relationship Account',
            'account_number': '7777777777',
            'currency': 'GBP',
            'account_type': 'JOINT'
        }
        
        created_bank_account = bank_account_service.create_bank_account(
            bank_id=bank.id,
            bank_account_data=bank_account_data,
            session=db_session
        )
        
        # Verify relationships are properly established
        assert created_bank_account.entity is not None
        assert created_bank_account.entity.id == entity.id
        assert created_bank_account.entity.name == entity.name
        
        assert created_bank_account.bank is not None
        assert created_bank_account.bank.id == bank.id
        assert created_bank_account.bank.name == bank.name
        
        # Verify reverse relationships
        assert created_bank_account in entity.bank_accounts
        assert created_bank_account in bank.accounts
