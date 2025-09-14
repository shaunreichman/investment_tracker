"""
Fund Event Service Tests

This module tests the FundEventService event processing logic and business rules.
Focus: Event creation, validation delegation, and secondary service integration.

Other aspects covered elsewhere:
- Model validation: test_fund_event_model.py
- Status management: test_fund_status_service.py
- Calculations: test_fund_calculation_services.py
- Tax processing: test_tax_calculation_service.py
- Secondary impacts: test_fund_event_secondary_service.py
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock

from src.fund.services.fund_event_service import FundEventService
from src.fund.enums import EventType, DistributionType, FundEventOperation
from src.fund.models.fund import Fund
from src.fund.models.fund_event import FundEvent


class TestFundEventService:
    """Test suite for FundEventService - Event processing logic only"""
    
    @pytest.fixture
    def service(self):
        """Create a FundEventService instance for testing."""
        # Mock the repositories and services
        mock_capital_repo = Mock()
        mock_unit_repo = Mock()
        mock_tax_repo = Mock()
        mock_distribution_repo = Mock()
        mock_query_repo = Mock()
        mock_validation_service = Mock()
        mock_secondary_service = Mock()
        
        return FundEventService(
            capital_event_repository=mock_capital_repo,
            unit_event_repository=mock_unit_repo,
            tax_event_repository=mock_tax_repo,
            distribution_event_repository=mock_distribution_repo,
            fund_event_query_repository=mock_query_repo,
            validation_service=mock_validation_service,
            fund_event_secondary_service=mock_secondary_service
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
        assert service.capital_event_repository is not None
        assert service.unit_event_repository is not None
        assert service.distribution_event_repository is not None
        assert service.validation_service is not None
        assert service.fund_event_secondary_service is not None
    
    # ============================================================================
    # UNIT PURCHASE AND SALE EVENTS
    # ============================================================================
    
    def test_add_unit_purchase_valid_inputs(self, service, mock_fund, mock_session):
        """Test unit purchase creation with valid inputs."""
        # Setup
        units = 100.0
        unit_price = 25.50
        purchase_date = date(2024, 3, 20)
        description = "Unit Purchase"
        reference_number = "UP_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_purchase.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_PURCHASE
        mock_event.event_date = purchase_date
        mock_event.units_purchased = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_purchase.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
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
        service.validation_service.validate_unit_purchase.assert_called_once_with(
            mock_fund, units, unit_price, purchase_date, reference_number, mock_session
        )
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
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_unit_purchase_validation_error(self, service, mock_fund, mock_session):
        """Test unit purchase creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_unit_purchase.return_value = {
            'units': ["Units must be positive"]
        }
        
        with pytest.raises(ValueError, match="Units must be positive"):
            service.add_unit_purchase(
                fund=mock_fund,
                units=0,
                price=25.50,
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
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_sale.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_SALE
        mock_event.event_date = sale_date
        mock_event.units_sold = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_sale.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
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
        service.validation_service.validate_unit_sale.assert_called_once_with(
            mock_fund, units, unit_price, sale_date, reference_number, mock_session
        )
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
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_unit_sale_validation_error(self, service, mock_fund, mock_session):
        """Test unit sale creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_unit_sale.return_value = {
            'units': ["Units must be positive"]
        }
        
        with pytest.raises(ValueError, match="Units must be positive"):
            service.add_unit_sale(
                fund=mock_fund,
                units=0,
                price=30.00,
                date=date(2024, 9, 15),
                session=mock_session
            )
    
    def test_add_unit_purchase_with_brokerage_fee(self, service, mock_fund, mock_session):
        """Test unit purchase creation with brokerage fee."""
        # Setup
        units = 100.0
        unit_price = 25.50
        brokerage_fee = 15.75
        purchase_date = date(2024, 3, 20)
        description = "Unit Purchase with Fee"
        reference_number = "UP_002"
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_purchase.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_PURCHASE
        mock_event.event_date = purchase_date
        mock_event.units_purchased = units
        mock_event.unit_price = unit_price
        mock_event.brokerage_fee = brokerage_fee
        mock_event.amount = (units * unit_price) + brokerage_fee
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_purchase.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_unit_purchase(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=purchase_date,
            brokerage_fee=brokerage_fee,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_unit_purchase.assert_called_once_with(
            mock_fund, units, unit_price, purchase_date, reference_number, mock_session
        )
        service.unit_event_repository.create_unit_purchase.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.UNIT_PURCHASE,
                'event_date': purchase_date,
                'units_purchased': units,
                'unit_price': unit_price,
                'brokerage_fee': brokerage_fee,
                'amount': (units * unit_price) + brokerage_fee,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_unit_sale_with_brokerage_fee(self, service, mock_fund, mock_session):
        """Test unit sale creation with brokerage fee."""
        # Setup
        units = 50.0
        unit_price = 30.00
        brokerage_fee = 12.50
        sale_date = date(2024, 9, 15)
        description = "Unit Sale with Fee"
        reference_number = "US_002"
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_sale.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_SALE
        mock_event.event_date = sale_date
        mock_event.units_sold = units
        mock_event.unit_price = unit_price
        mock_event.brokerage_fee = brokerage_fee
        mock_event.amount = (units * unit_price) - brokerage_fee
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_sale.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_unit_sale(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=sale_date,
            brokerage_fee=brokerage_fee,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_unit_sale.assert_called_once_with(
            mock_fund, units, unit_price, sale_date, reference_number, mock_session
        )
        service.unit_event_repository.create_unit_sale.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.UNIT_SALE,
                'event_date': sale_date,
                'units_sold': units,
                'unit_price': unit_price,
                'brokerage_fee': brokerage_fee,
                'amount': (units * unit_price) - brokerage_fee,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_capital_call_with_domain_event_storage(self, service, mock_fund, mock_session):
        """Test capital call creation with domain event storage when secondary service returns changes."""
        # Setup
        amount = 50000.0
        call_date = date(2024, 3, 15)
        description = "Q1 Capital Call"
        reference_number = "CC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_capital_call.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.amount = amount
        mock_event.event_date = call_date
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Mock secondary service returns changes
        mock_change = Mock()
        mock_change.to_dict.return_value = {"field": "value", "old_value": 0, "new_value": amount}
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = [mock_change]
        
        # Mock domain event repository and its store method
        mock_domain_event_repo = Mock()
        mock_domain_event = Mock()
        mock_domain_event_repo.store_domain_fund_event.return_value = mock_domain_event
        
        # Execute with proper mocking of the DomainEventRepository instantiation
        with patch('src.fund.services.fund_event_service.DomainEventRepository') as mock_domain_repo_class:
            mock_domain_repo_class.return_value = mock_domain_event_repo
            result = service.add_capital_call(
                fund=mock_fund,
                amount=amount,
                call_date=call_date,
                description=description,
                reference_number=reference_number,
                session=mock_session
            )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_capital_call.assert_called_once_with(
            mock_fund, amount, call_date, reference_number, mock_session
        )
        service.capital_event_repository.create_capital_call.assert_called_once()
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
        
        # Verify domain event storage
        mock_domain_event_repo.store_domain_fund_event.assert_called_once_with(
            fund_id=1,
            event_type=EventType.CAPITAL_CALL,
            event_operation=FundEventOperation.CREATE,
            event_id=1,
            event_data={"changes": [{"field": "value", "old_value": 0, "new_value": amount}]},
            session=mock_session
        )
    
    def test_add_capital_call_no_domain_event_when_no_changes(self, service, mock_fund, mock_session):
        """Test capital call creation without domain event storage when secondary service returns no changes."""
        # Setup
        amount = 50000.0
        call_date = date(2024, 3, 15)
        description = "Q1 Capital Call"
        reference_number = "CC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_capital_call.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.amount = amount
        mock_event.event_date = call_date
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Mock secondary service returns no changes
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            call_date=call_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_capital_call.assert_called_once_with(
            mock_fund, amount, call_date, reference_number, mock_session
        )
        service.capital_event_repository.create_capital_call.assert_called_once()
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
        
        # Verify no domain event repository was instantiated (since no changes)
        # This is implicit - if DomainEventRepository was called, it would be patched
    
    def test_add_capital_call_default_description(self, service, mock_fund, mock_session):
        """Test capital call creation with default description when none provided."""
        # Setup
        amount = 50000.0
        call_date = date(2024, 3, 15)
        reference_number = "CC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_capital_call.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.amount = amount
        mock_event.event_date = call_date
        mock_event.description = f"Capital call: ${amount:,.2f}"
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            call_date=call_date,
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
                'amount': amount,
                'event_date': call_date,
                'description': f"Capital call: ${amount:,.2f}",
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_return_of_capital_default_description(self, service, mock_fund, mock_session):
        """Test return of capital creation with default description when none provided."""
        # Setup
        amount = 25000.0
        return_date = date(2024, 9, 30)
        reference_number = "ROC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_return_of_capital.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.RETURN_OF_CAPITAL
        mock_event.amount = amount
        mock_event.event_date = return_date
        mock_event.description = f"Return of capital: ${amount:,.2f}"
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_return_of_capital.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_return_of_capital(
            fund=mock_fund,
            amount=amount,
            return_date=return_date,
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
                'amount': amount,
                'event_date': return_date,
                'description': f"Return of capital: ${amount:,.2f}",
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_unit_purchase_default_description(self, service, mock_fund, mock_session):
        """Test unit purchase creation with default description when none provided."""
        # Setup
        units = 100.0
        unit_price = 25.50
        purchase_date = date(2024, 3, 20)
        reference_number = "UP_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_purchase.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_PURCHASE
        mock_event.event_date = purchase_date
        mock_event.units_purchased = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = f"Purchase of {units} units at {unit_price}"
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_purchase.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_unit_purchase(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=purchase_date,
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
                'description': f"Purchase of {units} units at {unit_price}",
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_unit_sale_default_description(self, service, mock_fund, mock_session):
        """Test unit sale creation with default description when none provided."""
        # Setup
        units = 50.0
        unit_price = 30.00
        sale_date = date(2024, 9, 15)
        reference_number = "US_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_unit_sale.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.UNIT_SALE
        mock_event.event_date = sale_date
        mock_event.units_sold = units
        mock_event.unit_price = unit_price
        mock_event.amount = units * unit_price
        mock_event.description = f"Unit sale of {units} units at {unit_price}"
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_unit_sale.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_unit_sale(
            fund=mock_fund,
            units=units,
            price=unit_price,
            date=sale_date,
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
                'description': f"Unit sale of {units} units at {unit_price}",
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_nav_update_default_description(self, service, mock_fund, mock_session):
        """Test NAV update creation with default description when none provided."""
        # Setup
        nav_date = date(2024, 6, 30)
        nav_per_share = 28.75
        reference_number = "NAV_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_nav_update.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.NAV_UPDATE
        mock_event.event_date = nav_date
        mock_event.nav_per_share = nav_per_share
        mock_event.description = f"NAV update to {nav_per_share}"
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_nav_update.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_nav_update(
            fund=mock_fund,
            nav_per_share=nav_per_share,
            date=nav_date,
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
                'nav_per_share': nav_per_share,
                'previous_nav_per_share': None,
                'nav_change_absolute': None,
                'nav_change_percentage': None,
                'description': f"NAV update to {nav_per_share}",
                'reference_number': reference_number
            },
            mock_session
        )
    
    def test_add_nav_update_valid_inputs(self, service, mock_fund, mock_session):
        """Test NAV update creation with valid inputs."""
        # Setup
        nav_date = date(2024, 6, 30)
        nav_per_share = 28.75
        description = "Q2 NAV Update"
        reference_number = "NAV_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_nav_update.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.NAV_UPDATE
        mock_event.event_date = nav_date
        mock_event.nav_per_share = nav_per_share
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.unit_event_repository.create_nav_update.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_nav_update(
            fund=mock_fund,
            nav_per_share=nav_per_share,
            date=nav_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_nav_update.assert_called_once_with(
            mock_fund, nav_per_share, nav_date, reference_number, mock_session
        )
        service.unit_event_repository.create_nav_update.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.NAV_UPDATE,
                'event_date': nav_date,
                'nav_per_share': nav_per_share,
                'previous_nav_per_share': None,
                'nav_change_absolute': None,
                'nav_change_percentage': None,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_nav_update_validation_error(self, service, mock_fund, mock_session):
        """Test NAV update creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_nav_update.return_value = {
            'nav_per_share': ["NAV per share must be positive"]
        }
        
        with pytest.raises(ValueError, match="NAV per share must be positive"):
            service.add_nav_update(
                fund=mock_fund,
                nav_per_share=0,
                date=date(2024, 6, 30),
                session=mock_session
            )
    
    # ============================================================================
    # CAPITAL CALL AND RETURN OF CAPITAL EVENTS
    # ============================================================================
    
    def test_add_capital_call_valid_inputs(self, service, mock_fund, mock_session):
        """Test capital call creation with valid inputs."""
        # Setup
        amount = 50000.0
        call_date = date(2024, 3, 15)
        description = "Q1 Capital Call"
        reference_number = "CC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_capital_call.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.amount = amount
        mock_event.event_date = call_date
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_capital_call.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_capital_call(
            fund=mock_fund,
            amount=amount,
            call_date=call_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_capital_call.assert_called_once_with(
            mock_fund, amount, call_date, reference_number, mock_session
        )
        service.capital_event_repository.create_capital_call.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.CAPITAL_CALL,
                'amount': amount,
                'event_date': call_date,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_capital_call_validation_error(self, service, mock_fund, mock_session):
        """Test capital call creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_capital_call.return_value = {
            'amount': ["Capital call amount must be a positive number"]
        }
        
        with pytest.raises(ValueError, match="Capital call amount must be a positive number"):
            service.add_capital_call(
                fund=mock_fund,
                amount=0,
                call_date=date(2024, 3, 15),
                session=mock_session
            )
    
    def test_add_return_of_capital_valid_inputs(self, service, mock_fund, mock_session):
        """Test return of capital creation with valid inputs."""
        # Setup
        amount = 25000.0
        return_date = date(2024, 9, 30)
        description = "Q3 Capital Return"
        reference_number = "ROC_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_return_of_capital.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.RETURN_OF_CAPITAL
        mock_event.amount = amount
        mock_event.event_date = return_date
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.capital_event_repository.create_return_of_capital.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_return_of_capital(
            fund=mock_fund,
            amount=amount,
            return_date=return_date,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_return_of_capital.assert_called_once_with(
            mock_fund, amount, return_date, reference_number, mock_session
        )
        service.capital_event_repository.create_return_of_capital.assert_called_once_with(
            1,
            {
                'fund_id': 1,
                'event_type': EventType.RETURN_OF_CAPITAL,
                'amount': amount,
                'event_date': return_date,
                'description': description,
                'reference_number': reference_number
            },
            mock_session
        )
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_return_of_capital_validation_error(self, service, mock_fund, mock_session):
        """Test return of capital creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_return_of_capital.return_value = {
            'amount': ["Return amount must be positive"]
        }
        
        with pytest.raises(ValueError, match="Return amount must be positive"):
            service.add_return_of_capital(
                fund=mock_fund,
                amount=0,
                return_date=date(2024, 9, 30),
                session=mock_session
            )
    
    # ============================================================================
    # DISTRIBUTION EVENTS
    # ============================================================================
    
    def test_add_distribution_simple(self, service, mock_fund, mock_session):
        """Test simple distribution creation."""
        # Setup
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.DIVIDEND_FRANKED
        distribution_amount = 1000.0
        description = "Q2 Dividend"
        reference_number = "DIV_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_distribution.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.DISTRIBUTION
        mock_event.event_date = event_date
        mock_event.amount = distribution_amount
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.distribution_event_repository.create_distribution.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_distribution(
            fund=mock_fund,
            event_date=event_date,
            distribution_type=distribution_type,
            distribution_amount=distribution_amount,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_distribution.assert_called_once()
        service.distribution_event_repository.create_distribution.assert_called_once()
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_distribution_with_withholding_tax(self, service, mock_fund, mock_session):
        """Test distribution creation with withholding tax."""
        # Setup
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.INTEREST
        gross_amount = 1000.0
        net_amount = 800.0
        tax_amount = 200.0
        tax_rate = 20.0
        description = "Interest with Tax"
        reference_number = "INT_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_distribution.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.DISTRIBUTION
        mock_event.event_date = event_date
        mock_event.amount = gross_amount
        mock_event.description = description
        mock_event.reference_number = reference_number
        service.distribution_event_repository.create_distribution.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute
        result = service.add_distribution(
            fund=mock_fund,
            event_date=event_date,
            distribution_type=distribution_type,
            has_withholding_tax=True,
            gross_interest_amount=gross_amount,
            net_interest_amount=net_amount,
            withholding_tax_amount=tax_amount,
            withholding_tax_rate=tax_rate,
            description=description,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_distribution.assert_called_once()
        service.distribution_event_repository.create_distribution.assert_called_once()
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_add_distribution_validation_error(self, service, mock_fund, mock_session):
        """Test distribution creation with validation error."""
        # Mock validation service returns error
        service.validation_service.validate_distribution.return_value = {
            'distribution_amount': ["Distribution amount must be positive"]
        }
        
        with pytest.raises(ValueError, match="Distribution amount must be positive"):
            service.add_distribution(
                fund=mock_fund,
                event_date=date(2024, 6, 30),
                distribution_type=DistributionType.DIVIDEND_FRANKED,
                distribution_amount=0,
                session=mock_session
            )
    
    def test_add_distribution_default_description(self, service, mock_fund, mock_session):
        """Test distribution creation with default description when none provided."""
        # Setup
        event_date = date(2024, 6, 30)
        distribution_type = DistributionType.DIVIDEND_FRANKED
        distribution_amount = 1000.0
        reference_number = "DIV_001"
        
        # Mock validation service returns no errors
        service.validation_service.validate_distribution.return_value = {}
        
        # Mock the created event
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.fund_id = 1
        mock_event.event_type = EventType.DISTRIBUTION
        mock_event.event_date = event_date
        mock_event.amount = distribution_amount
        mock_event.description = f"Distribution: {distribution_type}"
        mock_event.reference_number = reference_number
        service.distribution_event_repository.create_distribution.return_value = mock_event
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Execute - no description provided
        result = service.add_distribution(
            fund=mock_fund,
            event_date=event_date,
            distribution_type=distribution_type,
            distribution_amount=distribution_amount,
            reference_number=reference_number,
            session=mock_session
        )
        
        # Verify
        assert result == mock_event
        service.validation_service.validate_distribution.assert_called_once()
        service.distribution_event_repository.create_distribution.assert_called_once()
        service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    # ============================================================================
    # EVENT QUERYING AND MANAGEMENT
    # ============================================================================
    
    def test_get_all_fund_events(self, service, mock_fund, mock_session):
        """Test getting all fund events."""
        # Setup
        mock_events = [
            Mock(spec=FundEvent, event_type=EventType.CAPITAL_CALL, event_date=date(2024, 1, 1)),
            Mock(spec=FundEvent, event_type=EventType.UNIT_PURCHASE, event_date=date(2024, 2, 1)),
            Mock(spec=FundEvent, event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE, event_date=date(2024, 3, 1))
        ]
        service.fund_event_query_repository.get_events_by_fund.return_value = mock_events
        
        # Execute
        result = service.get_all_fund_events(mock_fund, exclude_system_events=True, session=mock_session)
        
        # Verify - should exclude system events
        assert len(result) == 2
        assert all(e.event_type != EventType.DAILY_RISK_FREE_INTEREST_CHARGE for e in result)
        service.fund_event_query_repository.get_events_by_fund.assert_called_once_with(1, mock_session)
    
    def test_get_all_fund_events_include_system_events(self, service, mock_fund, mock_session):
        """Test getting all fund events including system events."""
        # Setup
        mock_events = [
            Mock(spec=FundEvent, event_type=EventType.CAPITAL_CALL, event_date=date(2024, 1, 1)),
            Mock(spec=FundEvent, event_type=EventType.UNIT_PURCHASE, event_date=date(2024, 2, 1)),
            Mock(spec=FundEvent, event_type=EventType.DAILY_RISK_FREE_INTEREST_CHARGE, event_date=date(2024, 3, 1))
        ]
        service.fund_event_query_repository.get_events_by_fund.return_value = mock_events
        
        # Execute
        result = service.get_all_fund_events(mock_fund, exclude_system_events=False, session=mock_session)
        
        # Verify - should include all events
        assert len(result) == 3
        assert any(e.event_type == EventType.DAILY_RISK_FREE_INTEREST_CHARGE for e in result)
        service.fund_event_query_repository.get_events_by_fund.assert_called_once_with(1, mock_session)
    
    def test_delete_fund_event_success(self, service, mock_fund, mock_session):
        """Test successful fund event deletion."""
        # Setup
        fund_id = 1
        event_id = 1
        
        # Mock repositories
        mock_fund_repo = Mock()
        mock_fund_event_repo = Mock()
        
        # Mock fund and event retrieval
        mock_fund_repo.get_by_id.return_value = mock_fund
        mock_event = Mock(spec=FundEvent)
        mock_event.id = event_id
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_fund_event_repo.get_by_id.return_value = mock_event
        mock_fund_event_repo.delete.return_value = True
        
        # Mock secondary service
        service.fund_event_secondary_service.handle_event_secondary_impact.return_value = []
        
        # Patch the repositories
        with patch('src.fund.repositories.FundRepository', return_value=mock_fund_repo), \
             patch('src.fund.repositories.FundEventRepository', return_value=mock_fund_event_repo):
            
            # Execute
            result = service.delete_fund_event(fund_id, event_id, mock_session)
            
            # Verify
            assert result is True
            mock_fund_repo.get_by_id.assert_called_once_with(fund_id, mock_session)
            mock_fund_event_repo.get_by_id.assert_called_once_with(event_id, mock_session)
            mock_fund_event_repo.delete.assert_called_once_with(event_id, mock_session)
            service.fund_event_secondary_service.handle_event_secondary_impact.assert_called_once()
    
    def test_delete_fund_event_fund_not_found(self, service, mock_session):
        """Test fund event deletion when fund not found."""
        # Setup
        fund_id = 999
        event_id = 1
        
        # Mock repositories
        mock_fund_repo = Mock()
        mock_fund_repo.get_by_id.return_value = None
        
        # Patch the repository
        with patch('src.fund.repositories.FundRepository', return_value=mock_fund_repo):
            
            # Execute & Verify
            with pytest.raises(ValueError, match="Fund with id 999 not found"):
                service.delete_fund_event(fund_id, event_id, mock_session)
    
    def test_delete_fund_event_event_not_found(self, service, mock_fund, mock_session):
        """Test fund event deletion when event not found."""
        # Setup
        fund_id = 1
        event_id = 999
        
        # Mock repositories
        mock_fund_repo = Mock()
        mock_fund_event_repo = Mock()
        mock_fund_repo.get_by_id.return_value = mock_fund
        mock_fund_event_repo.get_by_id.return_value = None
        
        # Patch the repositories
        with patch('src.fund.repositories.FundRepository', return_value=mock_fund_repo), \
             patch('src.fund.repositories.FundEventRepository', return_value=mock_fund_event_repo):
            
            # Execute & Verify
            with pytest.raises(ValueError, match="Event with id 999 not found"):
                service.delete_fund_event(fund_id, event_id, mock_session)
    
