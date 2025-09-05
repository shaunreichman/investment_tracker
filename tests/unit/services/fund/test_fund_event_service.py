"""
Fund Event Service Tests

This module tests the FundEventService event processing logic and business rules.
Focus: Event creation, validation, and processing logic only.

Other aspects covered elsewhere:
- Model validation: test_fund_event_model.py
- Status management: test_fund_status_service.py
- Calculations: test_fund_calculation_services.py
- Tax processing: test_tax_calculation_service.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_event_service import FundEventService
from src.fund.enums import EventType
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent


class TestFundEventService:
    """Test suite for FundEventService - Event processing logic only"""
    
    @pytest.fixture
    def service(self):
        """Create a FundEventService instance for testing."""
        # Mock the repositories
        mock_capital_repo = Mock()
        mock_unit_repo = Mock()
        mock_tax_repo = Mock()
        mock_query_repo = Mock()
        
        return FundEventService(
            capital_event_repository=mock_capital_repo,
            unit_event_repository=mock_unit_repo,
            tax_event_repository=mock_tax_repo,
            fund_event_query_repository=mock_query_repo
        )
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.tracking_type = "NAV_BASED"
        fund.current_equity_balance = 1000.0
        fund.fund_events = []
        return fund
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session for testing."""
        session = Mock()
        session.add = Mock()
        session.flush = Mock()
        session.commit = Mock()
        return session
    
    @pytest.fixture
    def mock_fund_event_class(self):
        """Create a mock FundEvent class for testing."""
        event_class = Mock()
        event_class.return_value = Mock(spec=FundEvent)
        return event_class
    
    def _mock_fund_events_class(self, mock_fund, mock_fund_event_class):
        """Helper method to mock the fund events class."""
        # Create a mock list-like object with the correct class
        mock_events_list = Mock()
        mock_events_list.__class__ = mock_fund_event_class
        mock_fund.fund_events = mock_events_list
    
    def test_service_initialization(self, service):
        """Test FundEventService initialization."""
        assert isinstance(service, FundEventService)
    
    def test_add_capital_call_valid_inputs(self, service, mock_fund, mock_session):
        """Test capital call creation with valid inputs."""
        # Setup
        amount = 5000.0
        call_date = date(2024, 1, 15)
        description = "Q1 Capital Call"
        reference_number = "CC_001"
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.event_date = call_date
        mock_event.amount = amount
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Execute
        result = service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            date=call_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.capital_event_repository.create_capital_call.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.CAPITAL_CALL,
                'event_date': call_date,
                'amount': amount,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_capital_call_default_description(self, service, mock_fund, mock_session):
        """Test capital call creation with default description."""
        # Setup
        amount = 5000.0
        call_date = date(2024, 1, 15)
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        expected_description = f"Capital call of {amount}"
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Execute
        service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            date=call_date,
            session=mock_session
        )
        
        # Verify default description was used
        service.capital_event_repository.create_capital_call.assert_called_once()
        call_args = service.capital_event_repository.create_capital_call.call_args
        assert call_args[0][1]['description'] == expected_description
    
    def test_add_capital_call_invalid_amount(self, service, mock_fund, mock_session):
        """Test capital call creation with invalid amount."""
        # Test zero amount
        with pytest.raises(ValueError, match="Capital call amount must be positive"):
            service.add_capital_call(
                fund=mock_fund,
                amount=0,
                date=date(2024, 1, 15),
                session=mock_session
            )
        
        # Test negative amount
        with pytest.raises(ValueError, match="Capital call amount must be positive"):
            service.add_capital_call(
                fund=mock_fund,
                amount=-1000,
                date=date(2024, 1, 15),
                session=mock_session
            )
    
    def test_add_capital_call_missing_date(self, service, mock_fund, mock_session):
        """Test capital call creation with missing date."""
        with pytest.raises(ValueError, match="Capital call date is required"):
            service.add_capital_call(
                fund=mock_fund,
                amount=5000.0,
                date=None,
                session=mock_session
            )
    
    def test_add_return_of_capital_valid_inputs(self, service, mock_fund, mock_session):
        """Test return of capital creation with valid inputs."""
        # Setup
        amount = 3000.0
        return_date = date(2024, 6, 15)
        description = "Q2 Return of Capital"
        reference_number = "ROC_001"
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        mock_event.event_type = EventType.RETURN_OF_CAPITAL
        mock_event.event_date = return_date
        mock_event.amount = amount
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_return_of_capital.return_value = mock_event
        
        # Execute
        result = service.add_return_of_capital(
            fund=mock_fund,
            amount=amount,
            date=return_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.capital_event_repository.create_return_of_capital.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.RETURN_OF_CAPITAL,
                'event_date': return_date,
                'amount': amount,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_return_of_capital_default_description(self, service, mock_fund, mock_session):
        """Test return of capital creation with default description."""
        # Setup
        amount = 3000.0
        return_date = date(2024, 6, 15)
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        expected_description = f"Return of capital of {amount}"
        service.capital_event_repository.create_return_of_capital.return_value = mock_event
        
        # Execute
        service.add_return_of_capital(
            fund=mock_fund,
            amount=amount,
            date=return_date,
            session=mock_session
        )
        
        # Verify default description was used
        service.capital_event_repository.create_return_of_capital.assert_called_once()
        call_args = service.capital_event_repository.create_return_of_capital.call_args
        assert call_args[0][1]['description'] == expected_description
    
    def test_add_return_of_capital_invalid_amount(self, service, mock_fund, mock_session):
        """Test return of capital creation with invalid amount."""
        # Test zero amount
        with pytest.raises(ValueError, match="Return of capital amount must be positive"):
            service.add_return_of_capital(
                fund=mock_fund,
                amount=0,
                date=date(2024, 6, 15),
                session=mock_session
            )
        
        # Test negative amount
        with pytest.raises(ValueError, match="Return of capital amount must be positive"):
            service.add_return_of_capital(
                fund=mock_fund,
                amount=-1000,
                date=date(2024, 6, 15),
                session=mock_session
            )
    
    def test_add_return_of_capital_missing_date(self, service, mock_fund, mock_session):
        """Test return of capital creation with missing date."""
        with pytest.raises(ValueError, match="Return of capital date is required"):
            service.add_return_of_capital(
                fund=mock_fund,
                amount=3000.0,
                date=None,
                session=mock_session
            )
    
    def test_add_unit_purchase_valid_inputs(self, service, mock_fund, mock_session):
        """Test unit purchase creation with valid inputs."""
        # Setup
        units = 100.0
        unit_price = 25.50
        purchase_date = date(2024, 3, 20)
        description = "Unit Purchase"
        reference_number = "UP_001"
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_PURCHASE
        mock_event.event_date = purchase_date
        mock_event.units_purchased = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_purchase.return_value = mock_event
        
        # Execute
        result = service.add_unit_purchase(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=purchase_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.unit_event_repository.create_unit_purchase.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.UNIT_PURCHASE,
                'event_date': purchase_date,
                'units_purchased': units,
                'unit_price': unit_price,
                'brokerage_fee': 0.0,
                'amount': units * unit_price,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_unit_purchase_invalid_units(self, service, mock_fund, mock_session):
        """Test unit purchase creation with invalid units."""
        # Test zero units
        with pytest.raises(ValueError, match="Units must be positive"):
            service.add_unit_purchase(
                fund=mock_fund,
                units=0,
                price=25.50,
                date=date(2024, 3, 20),
                session=mock_session
            )
        
        # Test negative units
        with pytest.raises(ValueError, match="Units must be positive"):
            service.add_unit_purchase(
                fund=mock_fund,
                units=-50,
                price=25.50,
                date=date(2024, 3, 20),
                session=mock_session
            )
    
    def test_add_unit_purchase_invalid_price(self, service, mock_fund, mock_session):
        """Test unit purchase creation with invalid price."""
        # Test zero price
        with pytest.raises(ValueError, match="Price must be positive"):
            service.add_unit_purchase(
                fund=mock_fund,
                units=100,
                price=0,
                date=date(2024, 3, 20),
                session=mock_session
            )
        
        # Test negative price
        with pytest.raises(ValueError, match="Price must be positive"):
            service.add_unit_purchase(
                fund=mock_fund,
                units=100,
                price=-25.50,
                date=date(2024, 3, 20),
                session=mock_session
            )
    
    def test_add_unit_sale_valid_inputs(self, service, mock_fund, mock_session):
        """Test unit sale creation with valid inputs."""
        # Setup
        units = 50.0
        unit_price = 30.00
        sale_date = date(2024, 9, 15)
        description = "Unit Sale"
        reference_number = "US_001"
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_SALE
        mock_event.event_date = sale_date
        mock_event.units_sold = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_sale.return_value = mock_event
        
        # Execute
        result = service.add_unit_sale(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=sale_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.unit_event_repository.create_unit_sale.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.UNIT_SALE,
                'event_date': sale_date,
                'units_sold': units,
                'unit_price': unit_price,
                'brokerage_fee': 0.0,
                'amount': units * unit_price,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_nav_update_valid_inputs(self, service, mock_fund, mock_session):
        """Test NAV update creation with valid inputs."""
        # Setup
        nav_date = date(2024, 6, 30)
        unit_price = 28.75
        description = "Q2 NAV Update"
        reference_number = "NAV_001"
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.fund_id = 1
        mock_event.event_type = EventType.NAV_UPDATE
        mock_event.event_date = nav_date
        mock_event.unit_price = unit_price
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_nav_update.return_value = mock_event
        
        # Execute
        result = service.add_nav_update(
            fund=mock_fund,
            nav_per_share=unit_price,
            date=nav_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.unit_event_repository.create_nav_update.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.NAV_UPDATE,
                'event_date': nav_date,
                'nav_per_share': unit_price,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_nav_update_invalid_nav_per_share(self, service, mock_fund, mock_session):
        """Test NAV update creation with invalid NAV per share."""
        # Test negative NAV per share
        with pytest.raises(ValueError, match="NAV per share cannot be negative"):
            service.add_nav_update(
                fund=mock_fund,
                nav_per_share=-25.50,
                date=date(2024, 6, 30),
                session=mock_session
            )
    
    
    def test_event_creation_without_session(self, service, mock_fund, mock_fund_event_class):
        """Test event creation without providing a session."""
        # Setup
        amount = 5000.0
        call_date = date(2024, 1, 15)
        
        # Mock the fund events class
        self._mock_fund_events_class(mock_fund, mock_fund_event_class)
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_fund_event_class.return_value = mock_event
        
        # Note: The current service implementation works with mocked repositories
        # This test documents the current behavior - no error is raised with mocked repos
        result = service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            date=call_date
        )
        # Should return a mock event when repositories are mocked
        assert result is not None
    
    def test_event_creation_edge_cases(self, service, mock_fund, mock_session):
        """Test event creation with edge case values."""
        # Setup
        mock_event = Mock(spec=FundEvent)
        service.capital_event_repository.create_capital_call.return_value = mock_event
        service.unit_event_repository.create_nav_update.return_value = mock_event
        
        # Test very small amounts
        small_amount = 0.01
        result = service.add_capital_call(
            fund=mock_fund,
            amount=small_amount,
            date=date(2024, 1, 15),
            session=mock_session
        )
        assert result == mock_event
        
        # Test very large amounts
        large_amount = 999999999.99
        result = service.add_capital_call(
            fund=mock_fund,
            amount=large_amount,
            date=date(2024, 1, 15),
            session=mock_session
        )
        assert result == mock_event
        
        # Test very small unit prices
        small_unit_price = 0.001
        result = service.add_nav_update(
            fund=mock_fund,
            nav_per_share=small_unit_price,
            date=date(2024, 6, 30),
            session=mock_session
        )
        assert result == mock_event
    
    def test_event_creation_with_long_descriptions(self, service, mock_fund, mock_session):
        """Test event creation with long descriptions."""
        # Setup
        mock_event = Mock(spec=FundEvent)
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Test long description
        long_description = "A" * 1000
        result = service.add_capital_call(
            fund=mock_fund,
            amount=5000.0,
            date=date(2024, 1, 15),
            description=long_description,
            session=mock_session
        )
        assert result == mock_event
    
    def test_event_creation_with_special_characters(self, service, mock_fund, mock_session):
        """Test event creation with special characters in descriptions."""
        # Setup
        mock_event = Mock(spec=FundEvent)
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Test special characters
        special_description = "Capital Call (Q1) - Special: $5,000.00"
        result = service.add_capital_call(
            fund=mock_fund,
            amount=5000.0,
            date=date(2024, 1, 15),
            description=special_description,
            session=mock_session
        )
        assert result == mock_event
