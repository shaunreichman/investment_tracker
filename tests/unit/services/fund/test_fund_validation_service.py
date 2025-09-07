"""
Comprehensive tests for fund validation service.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import date
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType


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
    # ==================== CAPITAL CALL VALIDATION TESTS ====================
    
    def test_validate_capital_call_success(self):
        """Test successful capital call validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 50000.0
        call_date = date(2024, 3, 15)
        reference_number = "CC_001"
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, reference_number, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_capital_call_invalid_amount_zero(self):
        """Test capital call validation with zero amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 0.0
        call_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Capital call amount must be a positive number" in errors['amount'][0]
    
    def test_validate_capital_call_invalid_amount_negative(self):
        """Test capital call validation with negative amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = -1000.0
        call_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Capital call amount must be a positive number" in errors['amount'][0]
    
    def test_validate_capital_call_missing_date(self):
        """Test capital call validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 50000.0
        call_date = None
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert 'call_date' in errors
        assert "Capital call date is required" in errors['call_date'][0]
    
    def test_validate_capital_call_wrong_fund_type(self):
        """Test capital call validation with NAV-based fund."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        amount = 50000.0
        call_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert 'fund_type' in errors
        assert "Capital calls are only applicable for cost-based funds" in errors['fund_type'][0]
    
    def test_validate_capital_call_multiple_errors(self):
        """Test capital call validation with multiple errors."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED  # Wrong fund type
        amount = -1000.0  # Negative amount
        call_date = None  # Missing date
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert len(errors) == 3
        assert 'amount' in errors
        assert 'call_date' in errors
        assert 'fund_type' in errors
        assert "Capital call amount must be a positive number" in errors['amount'][0]
        assert "Capital call date is required" in errors['call_date'][0]
        assert "Capital calls are only applicable for cost-based funds" in errors['fund_type'][0]
    
    # ==================== RETURN OF CAPITAL VALIDATION TESTS ====================
    
    def test_validate_return_of_capital_success(self):
        """Test successful return of capital validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 25000.0
        return_date = date(2024, 9, 30)
        reference_number = "ROC_001"
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, reference_number, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_return_of_capital_invalid_amount_zero(self):
        """Test return of capital validation with zero amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 0.0
        return_date = date(2024, 9, 30)
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Return amount must be a positive number" in errors['amount'][0]
    
    def test_validate_return_of_capital_invalid_amount_negative(self):
        """Test return of capital validation with negative amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = -5000.0
        return_date = date(2024, 9, 30)
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Return amount must be a positive number" in errors['amount'][0]
    
    def test_validate_return_of_capital_missing_date(self):
        """Test return of capital validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 25000.0
        return_date = None
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, self.mock_session
        )
        
        # Assert
        assert 'return_date' in errors
        assert "Return date is required" in errors['return_date'][0]
    
    def test_validate_return_of_capital_wrong_fund_type(self):
        """Test return of capital validation with NAV-based fund."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        amount = 25000.0
        return_date = date(2024, 9, 30)
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, self.mock_session
        )
        
        # Assert
        assert 'fund_type' in errors
        assert "Returns of capital are only applicable for cost-based funds" in errors['fund_type'][0]
    
    def test_validate_return_of_capital_multiple_errors(self):
        """Test return of capital validation with multiple errors."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED  # Wrong fund type
        amount = -5000.0  # Negative amount
        return_date = None  # Missing date
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, self.mock_session
        )
        
        # Assert
        assert len(errors) == 3
        assert 'amount' in errors
        assert 'return_date' in errors
        assert 'fund_type' in errors
        assert "Return amount must be a positive number" in errors['amount'][0]
        assert "Return date is required" in errors['return_date'][0]
        assert "Returns of capital are only applicable for cost-based funds" in errors['fund_type'][0]
    
    def test_validate_capital_call_with_none_session(self):
        """Test capital call validation handles None session gracefully."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 50000.0
        call_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, None
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_return_of_capital_with_none_session(self):
        """Test return of capital validation handles None session gracefully."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        amount = 25000.0
        return_date = date(2024, 9, 30)
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, None
        )
        
        # Assert
        assert errors == {}
