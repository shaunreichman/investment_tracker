"""
Comprehensive tests for fund validation service.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.fund.enums import FundStatus


class TestFundValidationService:
    """Test fund validation service enterprise patterns."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validation_service = FundValidationService()
        self.mock_session = Mock()
    
    def test_validate_fund_deletion_success_no_events(self):
        """Test successful validation when fund has no events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = []
        fund.tax_statements = []
        fund.domain_events = []
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert errors == {}
    
    def test_validate_fund_deletion_fails_with_events(self):
        """Test validation fails when fund has events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = [Mock(), Mock()]  # 2 events
        fund.tax_statements = []
        fund.domain_events = []
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'fund_events' in errors
        assert 'Cannot delete fund with 2 fund events' in errors['fund_events'][0]
    
    def test_validate_fund_deletion_fails_with_tax_statements(self):
        """Test validation fails when fund has tax statements."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = []
        fund.tax_statements = [Mock()]  # 1 tax statement
        fund.domain_events = []
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'tax_statements' in errors
        assert 'Cannot delete fund with 1 tax statements' in errors['tax_statements'][0]
    
    def test_validate_fund_deletion_fails_with_domain_events(self):
        """Test validation fails when fund has domain events."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = []
        fund.tax_statements = []
        fund.domain_events = [Mock(), Mock(), Mock()]  # 3 domain events
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert 'domain_events' in errors
        assert 'Cannot delete fund with 3 domain events' in errors['domain_events'][0]
    
    def test_validate_fund_deletion_fails_with_multiple_constraints(self):
        """Test validation fails with multiple constraint violations."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = [Mock(), Mock()]  # 2 events
        fund.tax_statements = [Mock()]  # 1 tax statement
        fund.domain_events = [Mock()]  # 1 domain event
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert len(errors) == 3
        assert 'fund_events' in errors
        assert 'tax_statements' in errors
        assert 'domain_events' in errors
        assert 'Cannot delete fund with 2 fund events' in errors['fund_events'][0]
        assert 'Cannot delete fund with 1 tax statements' in errors['tax_statements'][0]
        assert 'Cannot delete fund with 1 domain events' in errors['domain_events'][0]
    
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
        fund.fund_events = None
        fund.tax_statements = None
        fund.domain_events = None
        
        # Act & Assert
        with pytest.raises(TypeError):
            self.validation_service.validate_fund_deletion(fund, self.mock_session)
    
    def test_validate_fund_deletion_with_empty_lists(self):
        """Test validation succeeds with empty lists."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.fund_events = []
        fund.tax_statements = []
        fund.domain_events = []
        
        # Act
        errors = self.validation_service.validate_fund_deletion(fund, self.mock_session)
        
        # Assert
        assert errors == {}
