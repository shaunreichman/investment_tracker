"""
Comprehensive tests for fund validation service.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.fund.enums import FundStatus


class TestFundValidationService:
    """Test fund validation service enterprise patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock the repositories
        with patch('src.fund.services.fund_validation_service.FundEventRepository') as mock_fund_event_repo, \
             patch('src.fund.services.fund_validation_service.TaxStatementRepository') as mock_tax_statement_repo, \
             patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo:
            
            self.mock_fund_event_repo = mock_fund_event_repo.return_value
            self.mock_tax_statement_repo = mock_tax_statement_repo.return_value
            self.mock_domain_event_repo = mock_domain_event_repo.return_value
            
            self.validation_service = FundValidationService()
            self.mock_session = Mock()
    
    def test_validate_fund_deletion_success_no_events(self):
        """Test successful validation when fund has no events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 0
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 0
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 0
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert errors == {}
        
        # Verify repository calls
        self.mock_fund_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_tax_statement_repo.get_statement_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_domain_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
    
    def test_validate_fund_deletion_fails_with_events(self):
        """Test validation fails when fund has events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 2
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 0
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 0
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'fund_events' in errors
        assert 'Cannot delete fund with 2 fund events' in errors['fund_events'][0]
        
        # Verify repository calls
        self.mock_fund_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
    
    def test_validate_fund_deletion_fails_with_tax_statements(self):
        """Test validation fails when fund has tax statements."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 0
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 1
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 0
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'tax_statements' in errors
        assert 'Cannot delete fund with 1 tax statements' in errors['tax_statements'][0]
        
        # Verify repository calls
        self.mock_tax_statement_repo.get_statement_count_by_fund.assert_called_once_with(1, self.mock_session)
    
    def test_validate_fund_deletion_fails_with_domain_events(self):
        """Test validation fails when fund has domain events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 0
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 0
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 3
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'domain_events' in errors
        assert 'Cannot delete fund with 3 domain events' in errors['domain_events'][0]
        
        # Verify repository calls
        self.mock_domain_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
    
    def test_validate_fund_deletion_fails_with_multiple_constraints(self):
        """Test validation fails with multiple constraint violations."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 2
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 1
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 1
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert len(errors) == 3
        assert 'fund_events' in errors
        assert 'tax_statements' in errors
        assert 'domain_events' in errors
        assert 'Cannot delete fund with 2 fund events' in errors['fund_events'][0]
        assert 'Cannot delete fund with 1 tax statements' in errors['tax_statements'][0]
        assert 'Cannot delete fund with 1 domain events' in errors['domain_events'][0]
        
        # Verify all repository calls
        self.mock_fund_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_tax_statement_repo.get_statement_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_domain_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
    
    def test_get_deletion_rules(self):
        """Test deletion rules are properly defined."""
        # Act
        rules = self.validation_service.get_deletion_rules()
        
        # Assert
        assert len(rules) == 3
        assert "Fund must have 0 fund events to be deleted" in rules
        assert "Fund must have 0 tax statements to be deleted" in rules
        assert "Fund must have 0 domain events to be deleted" in rules
    
    def test_validate_fund_deletion_with_none_values(self):
        """Test validation handles None values gracefully."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = None  # Invalid fund ID
        
        # Act & Assert
        with pytest.raises((TypeError, AttributeError)):
            self.validation_service.validate_fund_deletion(fund, self.mock_session)
    
    def test_validate_fund_deletion_with_empty_lists(self):
        """Test validation succeeds with empty lists."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.id = 1
        
        # Mock repository responses for empty counts
        self.mock_fund_event_repo.get_event_count_by_fund.return_value = 0
        self.mock_tax_statement_repo.get_statement_count_by_fund.return_value = 0
        self.mock_domain_event_repo.get_event_count_by_fund.return_value = 0
        
        # Act
        with patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo_class:
            mock_domain_event_repo_class.return_value = self.mock_domain_event_repo
            errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert errors == {}
        
        # Verify repository calls
        self.mock_fund_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_tax_statement_repo.get_statement_count_by_fund.assert_called_once_with(1, self.mock_session)
        self.mock_domain_event_repo.get_event_count_by_fund.assert_called_once_with(1, self.mock_session)
