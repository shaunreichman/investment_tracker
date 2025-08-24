"""
Test Individual Event Handlers.

This module tests each individual event handler to ensure they work
correctly and maintain the expected contracts.

Each handler is tested for:
- Event validation logic
- Event processing and state updates
- Error handling and edge cases
- Business rule enforcement
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime

from src.fund.events.handlers import (
    CapitalCallHandler,
    ReturnOfCapitalHandler,
    DistributionHandler,
    NAVUpdateHandler,
    UnitPurchaseHandler,
    UnitSaleHandler
)
from src.fund.enums import EventType, FundType, DistributionType
from src.fund.models import Fund, FundEvent


class TestCapitalCallHandler:
    """Test the capital call handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.id = 1
        self.mock_fund.current_equity_balance = 10000.0
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = CapitalCallHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
    
    def test_validate_event_cost_based_fund(self):
        """Test validation for cost-based funds."""
        event_data = {
            'amount': 1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation rejects NAV-based funds."""
        self.mock_fund.tracking_type = FundType.NAV_BASED
        
        event_data = {
            'amount': 1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires COST_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_amount(self):
        """Test validation rejects missing amount."""
        event_data = {
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'amount': 1000.0
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_amount(self):
        """Test validation rejects invalid amount."""
        event_data = {
            'amount': 'invalid',
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_amount(self):
        """Test validation rejects negative amount."""
        event_data = {
            'amount': -1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_amount(self):
        """Test validation rejects zero amount."""
        event_data = {
            'amount': 0.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    @patch.object(CapitalCallHandler, '_check_duplicate_event')
    @patch.object(CapitalCallHandler, '_create_event')
    @patch.object(CapitalCallHandler, '_update_fund_after_capital_event')
    @patch.object(CapitalCallHandler, '_publish_dependent_events')
    @patch.object(CapitalCallHandler, '_handle_status_transition')
    def test_handle_successful_capital_call(self, mock_status, mock_publish, mock_update, mock_create, mock_check):
        """Test successful capital call event handling."""
        # Mock duplicate check returns None (no duplicate)
        mock_check.return_value = None
        
        # Mock event creation
        mock_event = Mock(spec=FundEvent)
        mock_event.amount = 5000.0
        mock_create.return_value = mock_event
        
        event_data = {
            'amount': 5000.0,
            'event_date': date(2024, 1, 15),
            'description': 'Test capital call',
            'reference_number': 'CC001'
        }
        
        result = self.handler.handle(event_data)
        
        # Verify the result
        assert result == mock_event
        
        # Verify duplicate check was called
        mock_check.assert_called_once_with(
            EventType.CAPITAL_CALL,
            event_date=date(2024, 1, 15),
            amount=5000.0,
            reference_number='CC001'
        )
        
        # Verify event creation was called
        mock_create.assert_called_once_with(
            EventType.CAPITAL_CALL,
            event_date=date(2024, 1, 15),
            amount=5000.0,
            description='Test capital call',
            reference_number='CC001'
        )
        
        # Verify fund update was called
        mock_update.assert_called_once_with(mock_event)
        
        # Verify dependent events were published
        mock_publish.assert_called_once_with(mock_event)
        
        # Verify status transition was handled
        mock_status.assert_called_once_with(mock_event)
    
    @patch.object(CapitalCallHandler, '_check_duplicate_event')
    def test_handle_duplicate_capital_call(self, mock_check):
        """Test that duplicate capital calls return existing event."""
        # Mock duplicate check returns existing event
        existing_event = Mock(spec=FundEvent)
        mock_check.return_value = existing_event
        
        event_data = {
            'amount': 5000.0,
            'event_date': date(2024, 1, 15),
            'description': 'Test capital call',
            'reference_number': 'CC001'
        }
        
        result = self.handler.handle(event_data)
        
        # Should return existing event
        assert result == existing_event
        
        # Verify duplicate check was called
        mock_check.assert_called_once_with(
            EventType.CAPITAL_CALL,
            event_date=date(2024, 1, 15),
            amount=5000.0,
            reference_number='CC001'
        )
    
    def test_handle_invalid_event_data(self):
        """Test that invalid event data raises ValueError."""
        event_data = {
            'amount': -1000.0,  # Invalid negative amount
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.handle(event_data)


class TestReturnOfCapitalHandler:
    """Test the return of capital handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.id = 1
        self.mock_fund.current_equity_balance = 15000.0
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = ReturnOfCapitalHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
    
    def test_validate_event_cost_based_fund(self):
        """Test validation for cost-based funds."""
        event_data = {
            'amount': 1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation rejects NAV-based funds."""
        self.mock_fund.tracking_type = FundType.NAV_BASED
        
        event_data = {
            'amount': 1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires COST_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_amount(self):
        """Test validation rejects missing amount."""
        event_data = {
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'amount': 1000.0
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_amount(self):
        """Test validation rejects invalid amount."""
        event_data = {
            'amount': 'invalid',
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_amount(self):
        """Test validation rejects negative amount."""
        event_data = {
            'amount': -1000.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    @patch.object(ReturnOfCapitalHandler, '_check_duplicate_event')
    @patch.object(ReturnOfCapitalHandler, '_create_event')
    @patch.object(ReturnOfCapitalHandler, '_update_fund_after_capital_event')
    @patch.object(ReturnOfCapitalHandler, '_publish_dependent_events')
    @patch.object(ReturnOfCapitalHandler, '_handle_status_transition')
    def test_handle_successful_return_of_capital(self, mock_status, mock_publish, mock_update, mock_create, mock_check):
        """Test successful return of capital event handling."""
        # Mock duplicate check returns None (no duplicate)
        mock_check.return_value = None
        
        # Mock event creation
        mock_event = Mock(spec=FundEvent)
        mock_event.amount = 2000.0
        mock_create.return_value = mock_event
        
        event_data = {
            'amount': 2000.0,
            'event_date': date(2024, 1, 15),
            'description': 'Test return of capital',
            'reference_number': 'ROC001'
        }
        
        result = self.handler.handle(event_data)
        
        # Verify the result
        assert result == mock_event
        
        # Verify duplicate check was called
        mock_check.assert_called_once_with(
            EventType.RETURN_OF_CAPITAL,
            event_date=date(2024, 1, 15),
            amount=2000.0,
            reference_number='ROC001'
        )
        
        # Verify event creation was called
        mock_create.assert_called_once_with(
            EventType.RETURN_OF_CAPITAL,
            event_date=date(2024, 1, 15),
            amount=2000.0,
            description='Test return of capital',
            reference_number='ROC001'
        )
        
        # Verify fund update was called
        mock_update.assert_called_once_with(mock_event)
        
        # Verify dependent events were published
        mock_publish.assert_called_once_with(mock_event)
        
        # Verify status transition was handled
        mock_status.assert_called_once_with(mock_event)


class TestNAVUpdateHandler:
    """Test the NAV update handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.NAV_BASED
        self.mock_fund.id = 1
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = NAVUpdateHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation for NAV-based funds."""
        event_data = {
            'nav_per_share': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_cost_based_fund(self):
        """Test validation rejects cost-based funds."""
        self.mock_fund.tracking_type = FundType.COST_BASED
        
        event_data = {
            'nav_per_share': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_nav(self):
        """Test validation rejects missing NAV."""
        event_data = {
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'nav_per_share': 10.50
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_nav(self):
        """Test validation rejects invalid NAV."""
        event_data = {
            'nav_per_share': 'invalid',
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_nav(self):
        """Test validation rejects negative NAV."""
        event_data = {
            'nav_per_share': -10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_nav(self):
        """Test validation rejects zero NAV."""
        event_data = {
            'nav_per_share': 0.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="nav_per_share is required"):
            self.handler.validate_event(event_data)
    
    @patch.object(NAVUpdateHandler, '_check_duplicate_event')
    @patch.object(NAVUpdateHandler, '_create_event')
    @patch.object(NAVUpdateHandler, '_update_fund_after_nav_event')
    @patch.object(NAVUpdateHandler, '_publish_dependent_events')
    @patch.object(NAVUpdateHandler, '_calculate_nav_change_fields')
    @patch.object(NAVUpdateHandler, '_update_subsequent_nav_events')
    def test_handle_successful_nav_update(self, mock_update_subsequent, mock_calc, mock_publish, mock_update, mock_create, mock_check):
        """Test successful NAV update event handling."""
        # Mock duplicate check returns None (no duplicate)
        mock_check.return_value = None
        
        # Mock NAV change calculation
        mock_calc.return_value = (10.0, 2.75, 27.5)  # previous_nav, change_absolute, change_percentage
        
        # Mock event creation
        mock_event = Mock(spec=FundEvent)
        mock_event.nav_per_share = 12.75
        mock_create.return_value = mock_event
        
        event_data = {
            'nav_per_share': 12.75,
            'event_date': date(2024, 1, 15),
            'description': 'Test NAV update',
            'reference_number': 'NAV001'
        }
        
        result = self.handler.handle(event_data)
        
        # Verify the result
        assert result == mock_event
        
        # Verify duplicate check was called
        mock_check.assert_called_once_with(
            EventType.NAV_UPDATE,
            event_date=date(2024, 1, 15),
            reference_number='NAV001'
        )
        
        # Verify event creation was called
        mock_create.assert_called_once_with(
            EventType.NAV_UPDATE,
            event_date=date(2024, 1, 15),
            nav_per_share=12.75,
            previous_nav_per_share=10.0,
            nav_change_absolute=2.75,
            nav_change_percentage=27.5,
            description='Test NAV update',
            reference_number='NAV001'
        )
        
        # Verify fund update was called
        mock_update.assert_called_once_with(mock_event)
        
        # Verify dependent events were published
        mock_publish.assert_called_once_with(mock_event)
        
        # Verify subsequent NAV events were updated
        mock_update_subsequent.assert_called_once_with(mock_event)


class TestDistributionHandler:
    """Test the distribution handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.id = 1
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = DistributionHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
    
    def test_validate_event_simple_distribution(self):
        """Test validation for simple distributions."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'distribution_amount': 1000.0
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_withholding_tax_interest_distribution(self):
        """Test validation for interest distributions with withholding tax."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.INTEREST,
            'has_withholding_tax': True,
            'gross_interest_amount': 1000.0,
            'withholding_tax_rate': 10.0
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_withholding_tax_non_interest_distribution(self):
        """Test validation rejects non-interest distributions with withholding tax."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'has_withholding_tax': True,
            'gross_interest_amount': 1000.0,
            'withholding_tax_rate': 10.0
        }
        
        with pytest.raises(ValueError, match="Withholding tax \\(has_withholding_tax=True\\) is only valid for INTEREST distributions, not DIVIDEND_FRANKED"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_distribution_type(self):
        """Test validation rejects missing distribution type."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_amount': 1000.0
        }
        
        with pytest.raises(ValueError, match="distribution_type is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_amount_for_simple_distribution(self):
        """Test validation rejects simple distributions without amount."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.DIVIDEND_FRANKED
        }
        
        with pytest.raises(ValueError, match="distribution_amount is required for simple distributions"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'distribution_amount': 1000.0
        }
        
        with pytest.raises(ValueError, match="event_date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_amount(self):
        """Test validation rejects invalid amount."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'distribution_amount': 'invalid'
        }
        
        with pytest.raises(ValueError, match="distribution_amount must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_amount(self):
        """Test validation rejects negative amount."""
        event_data = {
            'event_date': date(2024, 1, 15),
            'distribution_type': DistributionType.DIVIDEND_FRANKED,
            'distribution_amount': -1000.0
        }
        
        with pytest.raises(ValueError, match="distribution_amount must be a valid positive number"):
            self.handler.validate_event(event_data)


class TestUnitPurchaseHandler:
    """Test the unit purchase handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.NAV_BASED
        self.mock_fund.id = 1
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = UnitPurchaseHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation for NAV-based funds."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_cost_based_fund(self):
        """Test validation rejects cost-based funds."""
        self.mock_fund.tracking_type = FundType.COST_BASED
        
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_units(self):
        """Test validation rejects missing units."""
        event_data = {
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_price(self):
        """Test validation rejects missing price."""
        event_data = {
            'units_purchased': 100.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_units(self):
        """Test validation rejects invalid units."""
        event_data = {
            'units_purchased': 'invalid',
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_price(self):
        """Test validation rejects invalid price."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 'invalid',
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_units(self):
        """Test validation rejects negative units."""
        event_data = {
            'units_purchased': -100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_price(self):
        """Test validation rejects negative price."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': -10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_units(self):
        """Test validation rejects zero units."""
        event_data = {
            'units_purchased': 0.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_price(self):
        """Test validation rejects zero price."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 0.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_with_brokerage_fee(self):
        """Test validation with valid brokerage fee."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': 25.0
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_negative_brokerage_fee(self):
        """Test validation rejects negative brokerage fee."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': -25.0
        }
        
        with pytest.raises(ValueError, match="Brokerage fee must be a valid number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_brokerage_fee(self):
        """Test validation rejects invalid brokerage fee."""
        event_data = {
            'units_purchased': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': 'invalid'
        }
        
        with pytest.raises(ValueError, match="Brokerage fee must be a valid number"):
            self.handler.validate_event(event_data)


class TestUnitSaleHandler:
    """Test the unit sale handler specifically."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.mock_session = Mock()
        self.mock_fund = Mock()
        self.mock_fund.tracking_type = FundType.NAV_BASED
        self.mock_fund.id = 1
        
        # Mock the services
        self.mock_calculation_service = Mock()
        self.mock_status_service = Mock()
        self.mock_tax_service = Mock()
        
        self.handler = UnitSaleHandler(self.mock_session, self.mock_fund)
        
        # Patch the services to use our mocks
        self.handler.calculation_service = self.mock_calculation_service
        self.handler.status_service = self.mock_status_service
        self.handler.tax_service = self.mock_tax_service
        
        # Create mock events for testing
        mock_purchase_event = Mock()
        mock_purchase_event.units_purchased = 200.0
        
        mock_sale_event = Mock()
        mock_sale_event.units_sold = 0.0
        
        # Set up the session query mock to return appropriate data
        def mock_query_side_effect(model_class):
            if model_class.__name__ == 'FundEvent':
                mock_query = Mock()
                mock_filter = Mock()
                
                # Configure the filter to return different results based on the filter criteria
                def mock_filter_side_effect(*args, **kwargs):
                    # Check if this is filtering by event type
                    for arg in args:
                        if hasattr(arg, 'right') and hasattr(arg.right, 'value'):
                            if arg.right.value == EventType.UNIT_PURCHASE:
                                mock_filter.all.return_value = [mock_purchase_event]
                                return mock_filter
                            elif arg.right.value == EventType.UNIT_SALE:
                                mock_filter.all.return_value = [mock_sale_event]
                                return mock_filter
                    
                    # Default case
                    mock_filter.all.return_value = []
                    return mock_filter
                
                mock_query.filter.side_effect = mock_filter_side_effect
                return mock_query
            return Mock()
        
        self.mock_session.query.side_effect = mock_query_side_effect
    
    def test_validate_event_NAV_BASED_fund(self):
        """Test validation for NAV-based funds."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_cost_based_fund(self):
        """Test validation rejects cost-based funds."""
        self.mock_fund.tracking_type = FundType.COST_BASED
        
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_units(self):
        """Test validation rejects missing units."""
        event_data = {
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_price(self):
        """Test validation rejects missing price."""
        event_data = {
            'units_sold': 100.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_missing_date(self):
        """Test validation rejects missing date."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50
        }
        
        with pytest.raises(ValueError, match="date is required"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_units(self):
        """Test validation rejects invalid units."""
        event_data = {
            'units_sold': 'invalid',
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_price(self):
        """Test validation rejects invalid price."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 'invalid',
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_units(self):
        """Test validation rejects negative units."""
        event_data = {
            'units_sold': -100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_negative_price(self):
        """Test validation rejects negative price."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': -10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_units(self):
        """Test validation rejects zero units."""
        event_data = {
            'units_sold': 0.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="units must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_zero_price(self):
        """Test validation rejects zero price."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 0.0,
            'event_date': date(2024, 1, 15)
        }
        
        with pytest.raises(ValueError, match="price must be a valid positive number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_with_brokerage_fee(self):
        """Test validation with valid brokerage fee."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': 25.0
        }
        
        # Should not raise
        self.handler.validate_event(event_data)
    
    def test_validate_event_negative_brokerage_fee(self):
        """Test validation rejects negative brokerage fee."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': -25.0
        }
        
        with pytest.raises(ValueError, match="Brokerage fee must be a valid number"):
            self.handler.validate_event(event_data)
    
    def test_validate_event_invalid_brokerage_fee(self):
        """Test validation rejects invalid brokerage fee."""
        event_data = {
            'units_sold': 100.0,
            'unit_price': 10.50,
            'event_date': date(2024, 1, 15),
            'brokerage_fee': 'invalid'
        }
        
        with pytest.raises(ValueError, match="Brokerage fee must be a valid number"):
            self.handler.validate_event(event_data)
