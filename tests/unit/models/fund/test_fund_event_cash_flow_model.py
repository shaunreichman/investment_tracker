"""
Fund Event Cash Flow Model Tests

This module tests the FundEventCashFlow model validation and business rules.
Focus: Model constraints, validation, and basic business logic only.

Other aspects covered elsewhere:
- Persistence: test_fund_event_cash_flow_repository.py
- Business logic: test_fund_event_service.py
- Calculations: test_fund_calculation_services.py
- Event processing: test_event_handlers.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal

# NEW ARCHITECTURE IMPORTS - NOT legacy monolithic models
from src.fund.models.fund_event_cash_flow import FundEventCashFlow
from src.fund.enums import CashFlowDirection


class TestFundEventCashFlowModel:
    """Test suite for FundEventCashFlow model - Core model validation only"""
    
    @pytest.fixture
    def cash_flow_data(self):
        """Sample cash flow data for testing."""
        return {
            'fund_event_id': 1,
            'bank_account_id': 100,
            'direction': CashFlowDirection.OUTFLOW,
            'transfer_date': date(2024, 1, 15),
            'currency': 'AUD',
            'amount': 10000.00,
            'reference': 'CAPITAL_CALL_001',
            'description': 'Capital call for Q1 2024'
        }
    
    def test_cash_flow_creation(self, cash_flow_data):
        """Test cash flow creation with valid data."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        assert cash_flow.fund_event_id == 1
        assert cash_flow.bank_account_id == 100
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        assert cash_flow.transfer_date == date(2024, 1, 15)
        assert cash_flow.currency == 'AUD'
        assert cash_flow.amount == 10000.00
        assert cash_flow.reference == 'CAPITAL_CALL_001'
        assert cash_flow.description == 'Capital call for Q1 2024'
        
        # Note: SQLAlchemy defaults are only set on database insert, not object creation
        assert cash_flow.id is None  # Will be None until database insert
    
    def test_cash_flow_required_fields(self, cash_flow_data):
        """Test cash flow required field validation."""
        # Note: SQLAlchemy models don't enforce nullable=False at Python level
        # These constraints are enforced at the database level
        
        # Test missing fund_event_id
        invalid_data = cash_flow_data.copy()
        del invalid_data['fund_event_id']
        
        # SQLAlchemy allows creation, but database insert would fail
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.fund_event_id is None
        
        # Test missing bank_account_id
        invalid_data = cash_flow_data.copy()
        del invalid_data['bank_account_id']
        
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.bank_account_id is None
        
        # Test missing direction
        invalid_data = cash_flow_data.copy()
        del invalid_data['direction']
        
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.direction is None
        
        # Test missing transfer_date
        invalid_data = cash_flow_data.copy()
        del invalid_data['transfer_date']
        
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.transfer_date is None
        
        # Test missing currency
        invalid_data = cash_flow_data.copy()
        del invalid_data['currency']
        
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.currency is None
        
        # Test missing amount
        invalid_data = cash_flow_data.copy()
        del invalid_data['amount']
        
        cash_flow = FundEventCashFlow(**invalid_data)
        assert cash_flow.amount is None
    
    def test_cash_flow_optional_fields(self, cash_flow_data):
        """Test cash flow optional field handling."""
        # Test without optional fields
        minimal_data = {
            'fund_event_id': cash_flow_data['fund_event_id'],
            'bank_account_id': cash_flow_data['bank_account_id'],
            'direction': cash_flow_data['direction'],
            'transfer_date': cash_flow_data['transfer_date'],
            'currency': cash_flow_data['currency'],
            'amount': cash_flow_data['amount']
        }
        
        cash_flow = FundEventCashFlow(**minimal_data)
        assert cash_flow.reference is None
        assert cash_flow.description is None
    
    def test_cash_flow_direction_enum_validation(self, cash_flow_data):
        """Test cash flow direction enum validation."""
        # Test valid INFLOW direction
        inflow_data = cash_flow_data.copy()
        inflow_data['direction'] = CashFlowDirection.INFLOW
        cash_flow = FundEventCashFlow(**inflow_data)
        assert cash_flow.direction == CashFlowDirection.INFLOW
        
        # Test valid OUTFLOW direction
        outflow_data = cash_flow_data.copy()
        outflow_data['direction'] = CashFlowDirection.OUTFLOW
        cash_flow = FundEventCashFlow(**outflow_data)
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
        
        # Test that we can set direction manually
        cash_flow.direction = CashFlowDirection.INFLOW
        assert cash_flow.direction == CashFlowDirection.INFLOW
    
    def test_cash_flow_currency_validation(self, cash_flow_data):
        """Test cash flow currency validation."""
        # Test valid 3-character currency codes
        valid_currencies = ['AUD', 'USD', 'EUR', 'GBP', 'JPY']
        
        for currency in valid_currencies:
            currency_data = cash_flow_data.copy()
            currency_data['currency'] = currency
            cash_flow = FundEventCashFlow(**currency_data)
            assert cash_flow.currency == currency
        
        # Test that we can set currency manually
        cash_flow = FundEventCashFlow(**cash_flow_data)
        cash_flow.currency = 'USD'
        assert cash_flow.currency == 'USD'
    
    def test_cash_flow_amount_validation(self, cash_flow_data):
        """Test cash flow amount validation."""
        # Test valid positive amounts
        valid_amounts = [0.01, 1.0, 100.50, 10000.00, 999999.99]
        
        for amount in valid_amounts:
            amount_data = cash_flow_data.copy()
            amount_data['amount'] = amount
            cash_flow = FundEventCashFlow(**amount_data)
            assert cash_flow.amount == amount
        
        # Test that we can set amount manually
        cash_flow = FundEventCashFlow(**cash_flow_data)
        cash_flow.amount = 5000.00
        assert cash_flow.amount == 5000.00
    
    def test_cash_flow_transfer_date_validation(self, cash_flow_data):
        """Test cash flow transfer date validation."""
        # Test valid dates
        valid_dates = [
            date(2020, 1, 1),
            date(2024, 6, 15),
            date(2030, 12, 31)
        ]
        
        for transfer_date in valid_dates:
            date_data = cash_flow_data.copy()
            date_data['transfer_date'] = transfer_date
            cash_flow = FundEventCashFlow(**date_data)
            assert cash_flow.transfer_date == transfer_date
        
        # Test that we can set date manually
        cash_flow = FundEventCashFlow(**cash_flow_data)
        new_date = date(2024, 3, 20)
        cash_flow.transfer_date = new_date
        assert cash_flow.transfer_date == new_date
    
    def test_cash_flow_reference_validation(self, cash_flow_data):
        """Test cash flow reference field validation."""
        # Test valid reference strings
        valid_references = [
            'CAPITAL_CALL_001',
            'DIST_2024_Q1',
            'UNIT_PURCHASE_123',
            'RETURN_CAPITAL_456',
            None  # Reference is optional
        ]
        
        for reference in valid_references:
            ref_data = cash_flow_data.copy()
            ref_data['reference'] = reference
            cash_flow = FundEventCashFlow(**ref_data)
            assert cash_flow.reference == reference
        
        # Test that we can set reference manually
        cash_flow = FundEventCashFlow(**cash_flow_data)
        cash_flow.reference = 'NEW_REFERENCE'
        assert cash_flow.reference == 'NEW_REFERENCE'
    
    def test_cash_flow_description_validation(self, cash_flow_data):
        """Test cash flow description field validation."""
        # Test valid descriptions
        valid_descriptions = [
            'Capital call for Q1 2024',
            'Distribution payment',
            'Unit purchase transaction',
            'Return of capital',
            None  # Description is optional
        ]
        
        for description in valid_descriptions:
            desc_data = cash_flow_data.copy()
            desc_data['description'] = description
            cash_flow = FundEventCashFlow(**desc_data)
            assert cash_flow.description == description
        
        # Test that we can set description manually
        cash_flow = FundEventCashFlow(**cash_flow_data)
        cash_flow.description = 'Updated description'
        assert cash_flow.description == 'Updated description'
    
    def test_cash_flow_relationships(self, cash_flow_data):
        """Test cash flow relationship fields."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        # Test that relationships are accessible (will be None until database insert)
        assert cash_flow.fund_event is None
        assert cash_flow.bank_account is None
        
        # Test that we can set relationships manually
        # Note: In real usage, these would be SQLAlchemy relationship objects
        cash_flow.fund_event_id = 999
        assert cash_flow.fund_event_id == 999
        
        cash_flow.bank_account_id = 888
        assert cash_flow.bank_account_id == 888
    
    def test_cash_flow_repr_method(self, cash_flow_data):
        """Test cash flow string representation."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        # Test that repr includes key information
        repr_str = repr(cash_flow)
        assert 'FundEventCashFlow' in repr_str
        assert 'event_id=1' in repr_str
        assert 'acct_id=100' in repr_str
        assert 'dir=OUTFLOW' in repr_str
        assert 'date=2024-01-15' in repr_str
        assert 'AUD 10000.0' in repr_str
    
    def test_cash_flow_validate_basic_constraints(self, cash_flow_data):
        """Test cash flow basic constraints validation method."""
        cash_flow = FundEventCashFlow(**cash_flow_data)
        
        # Test valid cash flow passes validation
        assert cash_flow.validate_basic_constraints() is True
        
        # Test validation with missing required fields
        invalid_cash_flow = FundEventCashFlow()
        
        # Test missing fund_event_id
        with pytest.raises(ValueError, match="Fund event ID is required"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test missing bank_account_id
        invalid_cash_flow.fund_event_id = 1
        with pytest.raises(ValueError, match="Bank account ID is required"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test missing direction
        invalid_cash_flow.bank_account_id = 100
        with pytest.raises(ValueError, match="Cash flow direction is required"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test missing transfer_date
        invalid_cash_flow.direction = CashFlowDirection.OUTFLOW
        with pytest.raises(ValueError, match="Transfer date is required"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test missing currency
        invalid_cash_flow.transfer_date = date(2024, 1, 15)
        with pytest.raises(ValueError, match="Currency is required"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test missing amount
        invalid_cash_flow.currency = 'AUD'
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test zero amount
        invalid_cash_flow.amount = 0
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test negative amount
        invalid_cash_flow.amount = -100
        with pytest.raises(ValueError, match="Amount must be a positive number"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test invalid currency length
        invalid_cash_flow.amount = 1000
        invalid_cash_flow.currency = 'AU'  # 2 characters
        with pytest.raises(ValueError, match="Currency must be 3 characters"):
            invalid_cash_flow.validate_basic_constraints()
        
        # Test valid cash flow passes validation
        invalid_cash_flow.currency = 'AUD'
        assert invalid_cash_flow.validate_basic_constraints() is True
    
    def test_cash_flow_validate_currency_match_static_method(self):
        """Test cash flow currency match validation static method."""
        # Test matching currencies (case insensitive)
        assert FundEventCashFlow.validate_currency_match('AUD', 'AUD') is True
        assert FundEventCashFlow.validate_currency_match('USD', 'USD') is True
        assert FundEventCashFlow.validate_currency_match('aud', 'AUD') is True
        assert FundEventCashFlow.validate_currency_match('AUD', 'aud') is True
        
        # Test non-matching currencies
        with pytest.raises(ValueError, match="Currency mismatch: bank account uses AUD, cash flow uses USD"):
            FundEventCashFlow.validate_currency_match('AUD', 'USD')
        
        with pytest.raises(ValueError, match="Currency mismatch: bank account uses USD, cash flow uses EUR"):
            FundEventCashFlow.validate_currency_match('USD', 'EUR')
        
        with pytest.raises(ValueError, match="Currency mismatch: bank account uses EUR, cash flow uses GBP"):
            FundEventCashFlow.validate_currency_match('EUR', 'GBP')
    
    def test_cash_flow_edge_cases(self, cash_flow_data):
        """Test cash flow edge cases and boundary conditions."""
        # Test very large amounts
        large_amount_data = cash_flow_data.copy()
        large_amount_data['amount'] = 999999999.99
        cash_flow = FundEventCashFlow(**large_amount_data)
        assert cash_flow.amount == 999999999.99
        
        # Test very small amounts
        small_amount_data = cash_flow_data.copy()
        small_amount_data['amount'] = 0.01
        cash_flow = FundEventCashFlow(**small_amount_data)
        assert cash_flow.amount == 0.01
        
        # Test long reference string
        long_ref_data = cash_flow_data.copy()
        long_ref_data['reference'] = 'A' * 255  # Max length
        cash_flow = FundEventCashFlow(**long_ref_data)
        assert cash_flow.reference == 'A' * 255
        
        # Test long description
        long_desc_data = cash_flow_data.copy()
        long_desc_data['description'] = 'A' * 1000  # Long description
        cash_flow = FundEventCashFlow(**long_desc_data)
        assert cash_flow.description == 'A' * 1000
        
        # Test future dates
        future_date_data = cash_flow_data.copy()
        future_date_data['transfer_date'] = date(2030, 12, 31)
        cash_flow = FundEventCashFlow(**future_date_data)
        assert cash_flow.transfer_date == date(2030, 12, 31)
        
        # Test past dates
        past_date_data = cash_flow_data.copy()
        past_date_data['transfer_date'] = date(2020, 1, 1)
        cash_flow = FundEventCashFlow(**past_date_data)
        assert cash_flow.transfer_date == date(2020, 1, 1)
