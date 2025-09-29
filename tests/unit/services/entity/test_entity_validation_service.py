"""
Entity Validation Service Unit Tests.

This module tests the EntityValidationService class, focusing on business rule validation
and dependency checking. Tests are precise and focused on validation functionality.

Test Coverage:
- Entity deletion validation with dependency checking
- Bank account dependency validation
- Tax statement dependency validation
- Fund dependency validation
- Error message formatting
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session

from src.entity.services.entity_validation_service import EntityValidationService
from tests.factories.entity_factories import EntityFactory
from tests.factories.banking_factories import BankAccountFactory
from tests.factories.fund_factories import FundFactory, FundTaxStatementFactory


class TestEntityValidationService:
    """Test suite for EntityValidationService."""

    @pytest.fixture
    def service(self):
        """Create an EntityValidationService instance for testing."""
        return EntityValidationService()

    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock(spec=Session)

    @pytest.fixture
    def mock_entity(self):
        """Mock entity instance."""
        return EntityFactory.build(id=1, name='Test Entity')

    ################################################################################
    # Test validate_entity_deletion method
    ################################################################################

    def test_validate_entity_deletion_returns_empty_when_no_dependencies(self, service, mock_session):
        """Test that validate_entity_deletion returns empty dict when no dependencies exist."""
        # Arrange
        entity_id = 1
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_funds:
            
            # Act
            result = service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            assert result == {}
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    def test_validate_entity_deletion_returns_bank_account_error_when_dependent_accounts_exist(self, service, mock_session):
        """Test that validate_entity_deletion returns bank account error when dependent accounts exist."""
        # Arrange
        entity_id = 1
        dependent_accounts = [BankAccountFactory.build() for _ in range(2)]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=dependent_accounts) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_funds:
            
            # Act
            result = service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            expected_errors = {'bank_accounts': ['Cannot delete entity with dependent bank accounts']}
            assert result == expected_errors
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    def test_validate_entity_deletion_returns_tax_statement_error_when_dependent_statements_exist(self, service, mock_session):
        """Test that validate_entity_deletion returns tax statement error when dependent statements exist."""
        # Arrange
        entity_id = 1
        dependent_statements = [FundTaxStatementFactory.build() for _ in range(2)]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=dependent_statements) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_funds:
            
            # Act
            result = service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            expected_errors = {'tax_statements': ['Cannot delete entity with dependent tax statements']}
            assert result == expected_errors
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    def test_validate_entity_deletion_returns_fund_error_when_dependent_funds_exist(self, service, mock_session):
        """Test that validate_entity_deletion returns fund error when dependent funds exist."""
        # Arrange
        entity_id = 1
        dependent_funds = [FundFactory.build() for _ in range(2)]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=dependent_funds) as mock_funds:
            
            # Act
            result = service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            expected_errors = {'funds': ['Cannot delete entity with dependent funds']}
            assert result == expected_errors
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    def test_validate_entity_deletion_returns_multiple_errors_when_multiple_dependencies_exist(self, service, mock_session):
        """Test that validate_entity_deletion returns multiple errors when multiple dependencies exist."""
        # Arrange
        entity_id = 1
        dependent_accounts = [BankAccountFactory.build()]
        dependent_statements = [FundTaxStatementFactory.build()]
        dependent_funds = [FundFactory.build()]
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=dependent_accounts) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=dependent_statements) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=dependent_funds) as mock_funds:
            
            # Act
            result = service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            expected_errors = {
                'bank_accounts': ['Cannot delete entity with dependent bank accounts'],
                'tax_statements': ['Cannot delete entity with dependent tax statements'],
                'funds': ['Cannot delete entity with dependent funds']
            }
            assert result == expected_errors
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    def test_validate_entity_deletion_calls_repositories_with_correct_entity_id(self, service, mock_session):
        """Test that validate_entity_deletion calls repositories with correct entity ID."""
        # Arrange
        entity_id = 42
        
        with patch.object(service.bank_account_repository, 'get_bank_accounts', return_value=[]) as mock_bank_accounts, \
             patch.object(service.fund_tax_statement_repository, 'get_fund_tax_statements', return_value=[]) as mock_tax_statements, \
             patch.object(service.fund_repository, 'get_funds', return_value=[]) as mock_funds:
            
            # Act
            service.validate_entity_deletion(entity_id, mock_session)

            # Assert
            mock_bank_accounts.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_tax_statements.assert_called_once_with(mock_session, entity_id=entity_id)
            mock_funds.assert_called_once_with(mock_session, entity_id=entity_id)

    ################################################################################
    # Test service initialization
    ################################################################################

    def test_service_initializes_dependencies(self, service):
        """Test that service initializes with correct dependencies."""
        # Assert
        assert service.bank_account_repository is not None
        assert service.fund_tax_statement_repository is not None
        assert service.fund_repository is not None
        assert hasattr(service, 'bank_account_repository')
        assert hasattr(service, 'fund_tax_statement_repository')
        assert hasattr(service, 'fund_repository')
