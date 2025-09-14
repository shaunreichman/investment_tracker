"""
Targeted tests for fund validation service.
Tests focus on the current validation logic in the service.
"""

import pytest
from unittest.mock import Mock, patch
from datetime import date
from src.fund.services.fund_validation_service import FundValidationService
from src.fund.models import Fund
from src.fund.enums import FundStatus, FundType, DistributionType


class TestFundValidationService:
    """Test fund validation service validation logic."""
    
    def setup_method(self):
        """Set up test fixtures."""
        # Mock repositories with minimal setup
        with patch('src.fund.services.fund_validation_service.FundEventRepository') as mock_fund_event_repo, \
             patch('src.fund.services.fund_validation_service.TaxStatementRepository') as mock_tax_statement_repo, \
             patch('src.fund.services.fund_validation_service.CapitalEventRepository') as mock_capital_event_repo, \
             patch('src.fund.services.fund_validation_service.DomainEventRepository') as mock_domain_event_repo:
            
            self.mock_fund_event_repo = mock_fund_event_repo.return_value
            self.mock_tax_statement_repo = mock_tax_statement_repo.return_value
            self.mock_capital_event_repo = mock_capital_event_repo.return_value
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
    
    def test_validate_capital_call_exceeds_commitment(self):
        """Test capital call validation when amount exceeds remaining commitment."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=25000.0)  # Only 25k remaining
        amount = 50000.0  # Trying to call 50k
        call_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_capital_call(
            fund, amount, call_date, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Cannot call more capital than remaining commitment" in errors['amount'][0]
    
    # ==================== RETURN OF CAPITAL VALIDATION TESTS ====================
    
    def test_validate_return_of_capital_success(self):
        """Test successful return of capital validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
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
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
        amount = 25000.0
        return_date = date(2024, 9, 30)
        
        # Act
        errors = self.validation_service.validate_return_of_capital(
            fund, amount, return_date, None, None
        )
        
        # Assert
        assert errors == {}
    
    # ==================== UNIT PURCHASE VALIDATION TESTS ====================
    
    def test_validate_unit_purchase_success(self):
        """Test successful unit purchase validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        units = 100.0
        price = 25.50
        purchase_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_unit_purchase(
            fund, units, price, purchase_date, None, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_unit_purchase_invalid_units(self):
        """Test unit purchase validation with invalid units."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        units = 0.0  # Invalid units
        price = 25.50
        purchase_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_unit_purchase(
            fund, units, price, purchase_date, None, self.mock_session
        )
        
        # Assert
        assert 'units' in errors
        assert "Units must be a positive number" in errors['units'][0]
    
    def test_validate_unit_purchase_invalid_price(self):
        """Test unit purchase validation with invalid price."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        units = 100.0
        price = -25.50  # Invalid price
        purchase_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_unit_purchase(
            fund, units, price, purchase_date, None, self.mock_session
        )
        
        # Assert
        assert 'price' in errors
        assert "Unit price must be a positive number" in errors['price'][0]
    
    def test_validate_unit_purchase_missing_date(self):
        """Test unit purchase validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        units = 100.0
        price = 25.50
        purchase_date = None
        
        # Act
        errors = self.validation_service.validate_unit_purchase(
            fund, units, price, purchase_date, None, self.mock_session
        )
        
        # Assert
        assert 'purchase_date' in errors
        assert "Purchase date is required" in errors['purchase_date'][0]
    
    def test_validate_unit_purchase_wrong_fund_type(self):
        """Test unit purchase validation with cost-based fund."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
        units = 100.0
        price = 25.50
        purchase_date = date(2024, 3, 15)
        
        # Act
        errors = self.validation_service.validate_unit_purchase(
            fund, units, price, purchase_date, None, self.mock_session
        )
        
        # Assert
        assert 'fund_type' in errors
        assert "Unit purchases are only applicable for NAV-based funds" in errors['fund_type'][0]
    
    # ==================== UNIT SALE VALIDATION TESTS ====================
    
    def test_validate_unit_sale_success(self):
        """Test successful unit sale validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = 100.0
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_unit_sale_insufficient_units(self):
        """Test unit sale validation with insufficient units."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 50.0  # Less than sale amount
        units = 100.0
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'units' in errors
        assert "Insufficient units: trying to sell 100.0 but only 50.0 available" in errors['units'][0]
    
    def test_validate_unit_sale_wrong_fund_type(self):
        """Test unit sale validation with cost-based fund."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
        fund.current_units = 1000.0
        units = 100.0
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'fund_type' in errors
        assert "Unit sales are only applicable for NAV-based funds" in errors['fund_type'][0]
    
    def test_validate_unit_sale_zero_available_units(self):
        """Test unit sale when fund has 0 available units."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 0.0  # No units available
        units = 100.0
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'units' in errors
        assert "Insufficient units: trying to sell 100.0 but only 0.0 available" in errors['units'][0]
    
    def test_validate_unit_sale_invalid_price(self):
        """Test unit sale validation with negative price."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = 100.0
        price = -25.50  # Negative price
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'price' in errors
        assert "Unit price must be a positive number" in errors['price'][0]
    
    def test_validate_unit_sale_zero_price(self):
        """Test unit sale validation with zero price."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = 100.0
        price = 0.0  # Zero price
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'price' in errors
        assert "Unit price must be a positive number" in errors['price'][0]
    
    def test_validate_unit_sale_zero_units(self):
        """Test unit sale validation with zero units."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = 0.0  # Zero units
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'units' in errors
        assert "Units must be a positive number" in errors['units'][0]
    
    def test_validate_unit_sale_negative_units(self):
        """Test unit sale validation with negative units."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = -100.0  # Negative units
        price = 25.50
        sale_date = date(2024, 6, 15)
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'units' in errors
        assert "Units must be a positive number" in errors['units'][0]
    
    def test_validate_unit_sale_missing_date(self):
        """Test unit sale validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.current_units = 1000.0
        units = 100.0
        price = 25.50
        sale_date = None  # Missing date
        
        # Act
        errors = self.validation_service.validate_unit_sale(
            fund, units, price, sale_date, None, self.mock_session
        )
        
        # Assert
        assert 'sale_date' in errors
        assert "Sale date is required" in errors['sale_date'][0]
    
    # ==================== NAV UPDATE VALIDATION TESTS ====================
    
    def test_validate_nav_update_success(self):
        """Test successful NAV update validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.id = 1
        nav_per_share = 25.50
        update_date = date(2024, 3, 15)
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert errors == {}
    
    def test_validate_nav_update_invalid_nav(self):
        """Test NAV update validation with invalid NAV."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        nav_per_share = 0.0  # Invalid NAV
        update_date = date(2024, 3, 15)
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'nav_per_share' in errors
        assert "NAV per share must be a positive number" in errors['nav_per_share'][0]
    
    def test_validate_nav_update_missing_date(self):
        """Test NAV update validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        nav_per_share = 25.50
        update_date = None
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'update_date' in errors
        assert "Update date is required" in errors['update_date'][0]
    
    def test_validate_nav_update_wrong_fund_type(self):
        """Test NAV update validation with cost-based fund."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.COST_BASED
        fund.commitment_amount = 100000.0
        fund.get_remaining_commitment = Mock(return_value=75000.0)
        nav_per_share = 25.50
        update_date = date(2024, 3, 15)
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'fund_type' in errors
        assert "NAV updates are only applicable for NAV-based funds" in errors['fund_type'][0]
    
    def test_validate_nav_update_duplicate_date(self):
        """Test NAV update validation with duplicate date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.id = 1
        nav_per_share = 25.50
        update_date = date(2024, 3, 15)
        
        # Mock duplicate event
        duplicate_event = Mock()
        duplicate_event.event_date = update_date
        
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=duplicate_event):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'duplicate' in errors
        assert "NAV update already exists for 2024-03-15" in errors['duplicate'][0]
    
    def test_validate_nav_update_negative_nav(self):
        """Test NAV update validation with negative NAV value."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.id = 1
        nav_per_share = -25.50  # Negative NAV
        update_date = date(2024, 3, 15)
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'nav_per_share' in errors
        assert "NAV per share must be a positive number" in errors['nav_per_share'][0]
    
    def test_validate_nav_update_zero_nav(self):
        """Test NAV update validation with zero NAV value."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.id = 1
        nav_per_share = 0.0  # Zero NAV
        update_date = date(2024, 3, 15)
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'nav_per_share' in errors
        assert "NAV per share must be a positive number" in errors['nav_per_share'][0]
    
    def test_validate_nav_update_missing_date(self):
        """Test NAV update validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        fund.id = 1
        nav_per_share = 25.50
        update_date = None  # Missing date
        
        # Mock no duplicate events
        with patch.object(self.validation_service, '_check_duplicate_nav_event', return_value=None):
            # Act
            errors = self.validation_service.validate_nav_update(
                fund, nav_per_share, update_date, None, self.mock_session
            )
        
        # Assert
        assert 'update_date' in errors
        assert "Update date is required" in errors['update_date'][0]
    
    # ==================== DISTRIBUTION VALIDATION TESTS ====================
    
    def test_validate_distribution_simple_success(self):
        """Test successful simple distribution validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME
        distribution_amount = 1000.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_distribution_withholding_tax_success(self):
        """Test successful withholding tax distribution validation."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        withholding_tax_amount = 150.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, withholding_tax_amount, None, None, self.mock_session
        )
        
        # Assert
        assert errors == {}
    
    def test_validate_distribution_missing_date(self):
        """Test distribution validation with missing date."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = None
        distribution_type = DistributionType.INCOME
        distribution_amount = 1000.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'event_date' in errors
        assert "Event date is required" in errors['event_date'][0]
    
    def test_validate_distribution_missing_type(self):
        """Test distribution validation with missing type."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = None
        distribution_amount = 1000.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_type' in errors
        assert "Distribution type is required" in errors['distribution_type'][0]
    
    def test_validate_distribution_withholding_tax_wrong_type(self):
        """Test withholding tax distribution with wrong distribution type."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME  # Wrong type for withholding tax
        gross_interest_amount = 1000.0
        withholding_tax_amount = 150.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, withholding_tax_amount, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_type' in errors
        assert "Withholding tax is only valid for INTEREST distributions" in errors['distribution_type'][0]
    
    def test_validate_distribution_withholding_tax_no_amounts(self):
        """Test withholding tax distribution with no amount fields."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "For withholding tax distributions, exactly one of gross_interest_amount OR net_interest_amount must be provided" in errors['amount'][0]
    
    def test_validate_distribution_withholding_tax_both_amounts(self):
        """Test withholding tax distribution with both amount fields."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        net_interest_amount = 850.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, net_interest_amount, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "For withholding tax distributions, only one of gross_interest_amount OR net_interest_amount can be provided (not both)" in errors['amount'][0]
    
    def test_validate_distribution_simple_with_withholding_fields(self):
        """Test simple distribution with withholding tax fields provided."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME
        distribution_amount = 1000.0
        gross_interest_amount = 1000.0  # Should not be provided for simple distribution
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            gross_interest_amount, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'withholding_tax' in errors
        assert "Withholding tax fields should not be provided for simple distributions" in errors['withholding_tax'][0]
    
    def test_validate_distribution_simple_invalid_amount(self):
        """Test simple distribution with invalid amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME
        distribution_amount = -1000.0  # Negative amount
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_amount' in errors
        assert "Distribution amount must be positive" in errors['distribution_amount'][0]
    
    def test_validate_distribution_simple_zero_amount(self):
        """Test simple distribution with zero amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME
        distribution_amount = 0.0  # Zero amount (falsy value)
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_amount' in errors
        assert "Distribution amount is required for simple distributions" in errors['distribution_amount'][0]
    
    def test_validate_distribution_simple_missing_amount(self):
        """Test simple distribution with missing amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INCOME
        distribution_amount = None  # Missing amount
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_amount' in errors
        assert "Distribution amount is required for simple distributions" in errors['distribution_amount'][0]
    
    def test_validate_distribution_withholding_tax_invalid_rate(self):
        """Test withholding tax distribution with invalid tax rate."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        withholding_tax_rate = 150.0  # Invalid rate > 100%
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, None, withholding_tax_rate, None, self.mock_session
        )
        
        # Assert
        assert 'withholding_tax_rate' in errors
        assert "withholding_tax_rate must be between 0% and 100%" in errors['withholding_tax_rate'][0]
    
    def test_validate_distribution_withholding_tax_negative_rate(self):
        """Test withholding tax distribution with negative tax rate."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        withholding_tax_rate = -10.0  # Negative rate
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, None, withholding_tax_rate, None, self.mock_session
        )
        
        # Assert
        assert 'withholding_tax_rate' in errors
        assert "withholding_tax_rate must be between 0% and 100%" in errors['withholding_tax_rate'][0]
    
    def test_validate_distribution_withholding_tax_invalid_amount(self):
        """Test withholding tax distribution with invalid tax amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        withholding_tax_amount = -150.0  # Negative tax amount
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, withholding_tax_amount, None, None, self.mock_session
        )
        
        # Assert
        assert 'withholding_tax_amount' in errors
        assert "withholding_tax_amount must be positive" in errors['withholding_tax_amount'][0]
    
    def test_validate_distribution_withholding_tax_zero_amount(self):
        """Test withholding tax distribution with zero tax amount."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        withholding_tax_amount = 0.0  # Zero tax amount
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, withholding_tax_amount, None, None, self.mock_session
        )
        
        # Assert
        assert 'withholding_tax_amount' in errors
        assert "withholding_tax_amount must be positive" in errors['withholding_tax_amount'][0]
    
    def test_validate_distribution_withholding_tax_invalid_numeric_fields(self):
        """Test withholding tax distribution with invalid numeric field values."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = "invalid"  # Invalid string value
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'gross_interest_amount' in errors
        assert "gross_interest_amount must be a valid number" in errors['gross_interest_amount'][0]
    
    def test_validate_distribution_withholding_tax_logical_consistency(self):
        """Test withholding tax distribution logical consistency check."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_interest_amount = 1000.0
        net_interest_amount = 1000.0  # Same as gross (should be less)
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, None, True,
            gross_interest_amount, net_interest_amount, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'amount' in errors
        assert "Gross amount must be greater than net amount for withholding tax distributions" in errors['amount'][0]
    
    def test_validate_distribution_invalid_type_string(self):
        """Test distribution with invalid type string."""
        # Arrange
        fund = Mock(spec=Fund)
        fund.tracking_type = FundType.NAV_BASED
        event_date = date(2024, 6, 30)
        distribution_type = "INVALID_TYPE"  # Invalid string
        distribution_amount = 1000.0
        
        # Act
        errors = self.validation_service.validate_distribution(
            fund, event_date, distribution_type, distribution_amount, False,
            None, None, None, None, None, self.mock_session
        )
        
        # Assert
        assert 'distribution_type' in errors
        assert "Invalid distribution_type" in errors['distribution_type'][0]
