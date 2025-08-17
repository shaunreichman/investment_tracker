"""
Test Base Fund Event Handler.

This module tests the BaseFundEventHandler base class functionality,
focusing on common methods and shared logic that all handlers inherit.

Key testing areas:
- Common validation methods
- Event creation and management
- Domain event publishing
- Fund summary field updates
- Error handling and rollback
- Date parsing and validation

Testing Approach: Mock-Based Testing (Unit Tests)
Reasoning: Base handler should be tested in isolation for fast execution and focused validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import date, datetime
from decimal import Decimal

from src.fund.events.base_handler import BaseFundEventHandler
from src.fund.enums import EventType, FundType, FundStatus
from src.fund.models import Fund, FundEvent


class ConcreteTestHandler(BaseFundEventHandler):
    """Concrete implementation of BaseFundEventHandler for testing."""
    
    def handle(self, event_data):
        """Implement abstract method for testing."""
        self.validate_event(event_data)
        return self._create_event(EventType.CAPITAL_CALL, **event_data)
    
    def validate_event(self, event_data):
        """Implement abstract method for testing."""
        if 'amount' not in event_data:
            raise ValueError("Amount is required")
    
    def _parse_date(self, date_value):
        """Override to add debug output."""
        print(f"DEBUG: _parse_date called with {date_value} of type {type(date_value)}")
        result = super()._parse_date(date_value)
        print(f"DEBUG: _parse_date returned {result} of type {type(result)}")
        return result


class TestBaseFundEventHandler:
    """Test the BaseFundEventHandler base class functionality."""
    
    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.mock_session = Mock()
        self.mock_fund = Mock(spec=Fund)
        self.mock_fund.id = 1
        self.mock_fund.tracking_type = FundType.COST_BASED
        self.mock_fund.status = FundStatus.ACTIVE
        self.mock_fund.name = "Test Fund"
        
        # Create concrete handler instance for testing
        self.handler = ConcreteTestHandler(self.mock_session, self.mock_fund)
    
    def test_handler_initialization(self):
        """Test that handler initializes with correct dependencies."""
        assert self.handler.session == self.mock_session
        assert self.handler.fund == self.mock_fund
        assert self.handler.calculation_service is not None
        assert self.handler.status_service is not None
        assert self.handler.tax_service is not None
        assert self.handler.logger is not None
    
    def test_get_fund_success(self):
        """Test successful fund retrieval by ID."""
        mock_fund = Mock(spec=Fund)
        self.mock_session.query.return_value.filter.return_value.first.return_value = mock_fund
        
        result = self.handler._get_fund(1)
        
        assert result == mock_fund
        self.mock_session.query.assert_called_once()
    
    def test_get_fund_not_found(self):
        """Test fund retrieval when fund doesn't exist."""
        self.mock_session.query.return_value.filter.return_value.first.return_value = None
        
        with pytest.raises(ValueError, match="Fund with ID 1 not found"):
            self.handler._get_fund(1)
    
    def test_validate_fund_type_success(self):
        """Test successful fund type validation."""
        # Should not raise an exception
        self.handler._validate_fund_type(FundType.COST_BASED)
    
    def test_validate_fund_type_mismatch(self):
        """Test fund type validation failure."""
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund"):
            self.handler._validate_fund_type(FundType.NAV_BASED)
    
    def test_validate_positive_amount_success(self):
        """Test successful positive amount validation."""
        # Test various valid positive amounts
        valid_amounts = [100.0, 0.01, Decimal('50.50'), "75.25"]
        
        for amount in valid_amounts:
            # Should not raise an exception
            self.handler._validate_positive_amount(amount, "test_amount")
    
    def test_validate_positive_amount_zero(self):
        """Test amount validation failure for zero."""
        with pytest.raises(ValueError, match="test_amount must be a valid positive number"):
            self.handler._validate_positive_amount(0, "test_amount")
    
    def test_validate_positive_amount_negative(self):
        """Test amount validation failure for negative values."""
        with pytest.raises(ValueError, match="test_amount must be a valid positive number"):
            self.handler._validate_positive_amount(-100, "test_amount")
    
    def test_validate_positive_amount_invalid_type(self):
        """Test amount validation failure for invalid types."""
        with pytest.raises(ValueError, match="test_amount must be a valid positive number"):
            self.handler._validate_positive_amount("invalid", "test_amount")
    
    def test_validate_required_date_success(self):
        """Test successful required date validation."""
        valid_dates = [date(2024, 1, 1), datetime(2024, 1, 1), "2024-01-01"]
        
        for date_val in valid_dates:
            # Should not raise an exception
            self.handler._validate_required_date(date_val, "test_date")
    
    def test_validate_required_date_missing(self):
        """Test required date validation failure for missing dates."""
        with pytest.raises(ValueError, match="test_date is required"):
            self.handler._validate_required_date(None, "test_date")
        
        with pytest.raises(ValueError, match="test_date is required"):
            self.handler._validate_required_date("", "test_date")
    
    def test_check_duplicate_event_no_duplicate(self):
        """Test duplicate event check when no duplicate exists."""
        # Setup mock chain properly
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.filter.return_value = mock_filter
        mock_filter.first.return_value = None
        
        result = self.handler._check_duplicate_event(EventType.CAPITAL_CALL, amount=1000)
        
        assert result is None
    
    def test_check_duplicate_event_with_duplicate(self):
        """Test duplicate event check when duplicate exists."""
        mock_event = Mock(spec=FundEvent)
        
        # Setup mock chain properly
        mock_query = Mock()
        mock_filter = Mock()
        mock_first = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.filter.return_value = mock_filter
        mock_filter.first.return_value = mock_event
        
        result = self.handler._check_duplicate_event(EventType.CAPITAL_CALL, amount=1000)
        
        assert result == mock_event
    
    def test_create_event_success(self):
        """Test successful event creation."""
        event_data = {
            'event_date': date(2024, 1, 1),
            'amount': 1000.0,
            'description': 'Test event'
        }
        
        result = self.handler._create_event(EventType.CAPITAL_CALL, **event_data)
        
        assert isinstance(result, FundEvent)
        assert result.fund_id == self.mock_fund.id
        assert result.event_type == EventType.CAPITAL_CALL
        assert result.event_date == date(2024, 1, 1)
        assert result.amount == 1000.0
        assert result.description == 'Test event'
        
        # Verify event was added to session
        self.mock_session.add.assert_called_once_with(result)
        self.mock_session.flush.assert_called_once()
    
    @patch('src.fund.repositories.domain_event_repository.DomainEventRepository')
    def test_publish_dependent_events_success(self, mock_domain_repo_class):
        """Test successful publishing of dependent events."""
        mock_domain_repo = Mock()
        mock_domain_repo_class.return_value = mock_domain_repo
        
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.DISTRIBUTION
        mock_event.event_date = date(2024, 1, 1)
        mock_event.amount = 1000.0
        mock_event.withholding_tax_amount = 100.0
        
        # Mock the domain event creation method
        with patch.object(self.handler, '_create_domain_events_for_fund_event') as mock_create:
            mock_create.return_value = [Mock(), Mock()]  # Two domain events
            
            self.handler._publish_dependent_events(mock_event)
            
            # Verify domain events were stored
            mock_domain_repo.store_domain_events.assert_called_once()
    
    @patch('src.fund.repositories.domain_event_repository.DomainEventRepository')
    def test_publish_dependent_events_no_events(self, mock_domain_repo_class):
        """Test publishing when no dependent events are created."""
        mock_domain_repo = Mock()
        mock_domain_repo_class.return_value = mock_domain_repo
        
        mock_event = Mock(spec=FundEvent)
        
        # Mock the domain event creation method to return no events
        with patch.object(self.handler, '_create_domain_events_for_fund_event') as mock_create:
            mock_create.return_value = []
            
            self.handler._publish_dependent_events(mock_event)
            
            # Verify no domain events were stored
            mock_domain_repo.store_domain_events.assert_not_called()
    
    def test_publish_events_to_bus_success(self):
        """Test successful publishing to event bus."""
        mock_domain_events = [Mock(), Mock()]
        
        # Mock the event bus by patching the import path that's used inside the method
        with patch('src.fund.events.consumption.event_bus.event_bus') as mock_event_bus:
            self.handler._publish_events_to_bus(mock_domain_events)
            
            # Verify events were published to bus
            assert mock_event_bus.publish.call_count == 2
    
    def test_publish_events_to_bus_import_error(self):
        """Test event bus publishing when import fails."""
        mock_domain_events = [Mock()]
        
        # Mock the import to fail by patching the specific import path
        with patch('src.fund.events.consumption.event_bus.event_bus', side_effect=ImportError("Event bus not available")):
            # Should not raise an exception, just log warning
            self.handler._publish_events_to_bus(mock_domain_events)
    
    def test_create_domain_events_for_fund_event_equity_change(self):
        """Test domain event creation for equity balance changes."""
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        mock_event.event_date = date(2024, 1, 1)
        mock_event.previous_equity_balance = 0.0
        mock_event.current_equity_balance = 1000.0
        
        with patch('src.fund.events.domain.equity_balance_changed_event.EquityBalanceChangedEvent') as mock_equity_event:
            mock_equity_event.return_value = Mock()
            
            result = self.handler._create_domain_events_for_fund_event(mock_event)
            
            assert len(result) == 1
            mock_equity_event.assert_called_once()
    
    def test_create_domain_events_for_fund_event_distribution(self):
        """Test domain event creation for distribution events."""
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.DISTRIBUTION
        mock_event.event_date = date(2024, 1, 1)
        mock_event.amount = 1000.0
        mock_event.withholding_tax_amount = 100.0
        mock_event.distribution_type = 'CASH'
        
        # Mock the getattr calls to return proper values
        mock_event.previous_equity_balance = 0.0
        mock_event.current_equity_balance = 0.0
        
        with patch('src.fund.events.domain.distribution_recorded_event.DistributionRecordedEvent') as mock_dist_event, \
             patch('src.fund.events.domain.tax_statement_updated_event.TaxStatementUpdatedEvent') as mock_tax_event:
            
            mock_dist_event.return_value = Mock()
            mock_tax_event.return_value = Mock()
            
            result = self.handler._create_domain_events_for_fund_event(mock_event)
            
            assert len(result) == 2  # Distribution + Tax events
            mock_dist_event.assert_called_once()
            mock_tax_event.assert_called_once()
    
    def test_update_fund_summary_fields_cost_based(self):
        """Test fund summary field updates for cost-based funds."""
        # Mock fund events query
        mock_capital_event = Mock()
        mock_capital_event.event_type = EventType.CAPITAL_CALL
        mock_capital_event.amount = 1000.0
        
        # Setup mock chain properly
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        mock_all = Mock()
        
        self.mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [mock_capital_event]
        
        self.handler._update_fund_summary_fields()
        
        # Verify fund fields were updated
        assert self.mock_fund.total_cost_basis == 1000.0
        assert self.mock_fund.current_equity_balance == 1000.0
        assert self.mock_fund.average_equity_balance == 1000.0
    
    def test_update_fund_summary_fields_nav_based(self):
        """Test fund summary field updates for NAV-based funds."""
        self.mock_fund.tracking_type = FundType.NAV_BASED
        self.mock_fund.current_units = 100.0
        self.mock_fund.current_unit_price = 10.0
        
        self.handler._update_nav_based_fund_summary()
        
        # Verify NAV total was calculated
        assert self.mock_fund.current_nav_total == 1000.0
    
    def test_handle_status_transition_no_transition(self):
        """Test status transition handling when no transition is needed."""
        # Mock status service to indicate no transition needed
        mock_status_service = Mock()
        mock_status_service.should_calculate_irr.return_value = False
        self.handler.status_service = mock_status_service
        
        self.handler._handle_status_transition(Mock())
        
        # Verify no status update was attempted
        assert self.mock_fund.status == FundStatus.ACTIVE
    
    def test_commit_changes_success(self):
        """Test successful commit of changes."""
        self.handler._commit_changes()
        
        # Verify session was committed
        self.mock_session.commit.assert_called_once()
    
    def test_commit_changes_failure(self):
        """Test commit failure handling."""
        self.mock_session.commit.side_effect = Exception("Database error")
        
        with pytest.raises(RuntimeError, match="Failed to commit changes"):
            self.handler._commit_changes()
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
    
    def test_parse_date_date_object(self):
        """Test date parsing with date object."""
        test_date = date(2024, 1, 1)
        result = self.handler._parse_date(test_date)
        
        assert result == test_date
    
    def test_parse_date_datetime_object(self):
        """Test date parsing with datetime object."""
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        result = self.handler._parse_date(test_datetime)
        
        # The method should return a date object, not datetime
        assert isinstance(result, date)
        assert result == date(2024, 1, 1)
    
    def test_parse_date_debug(self):
        """Debug test to understand datetime parsing issue."""
        test_datetime = datetime(2024, 1, 1, 12, 0, 0)
        print(f"Input type: {type(test_datetime)}")
        print(f"Input value: {test_datetime}")
        
        # Check if the method exists and what it is
        print(f"Handler type: {type(self.handler)}")
        print(f"Handler class: {self.handler.__class__}")
        print(f"Method exists: {hasattr(self.handler, '_parse_date')}")
        print(f"Method: {getattr(self.handler, '_parse_date')}")
        
        result = self.handler._parse_date(test_datetime)
        print(f"Result type: {type(result)}")
        print(f"Result value: {result}")
        
        # Check if the method is working correctly
        assert isinstance(result, date)
        assert result == date(2024, 1, 1)
    
    def test_parse_date_string_iso_format(self):
        """Test date parsing with ISO format string."""
        result = self.handler._parse_date("2024-01-01")
        
        assert result == date(2024, 1, 1)
    
    def test_parse_date_string_slash_format(self):
        """Test date parsing with slash format string."""
        result = self.handler._parse_date("2024/01/01")
        
        assert result == date(2024, 1, 1)
    
    def test_parse_date_invalid_format(self):
        """Test date parsing with invalid format."""
        with pytest.raises(ValueError, match="Invalid date format"):
            self.handler._parse_date("01-01-2024")
    
    def test_parse_date_invalid_type(self):
        """Test date parsing with invalid type."""
        with pytest.raises(ValueError, match="Invalid date type"):
            self.handler._parse_date(123)
    
    def test_rollback_on_error(self):
        """Test error rollback handling."""
        test_error = ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            self.handler._rollback_on_error(test_error)
        
        # Verify rollback was called
        self.mock_session.rollback.assert_called_once()
    
    def test_concrete_handler_implementation(self):
        """Test that concrete handler can be instantiated and used."""
        event_data = {'amount': 1000.0, 'event_date': '2024-01-01'}
        
        result = self.handler.handle(event_data)
        
        assert isinstance(result, FundEvent)
        assert result.event_type == EventType.CAPITAL_CALL
    
    def test_concrete_handler_validation_failure(self):
        """Test that concrete handler validation works correctly."""
        event_data = {'event_date': '2024-01-01'}  # Missing amount
        
        with pytest.raises(ValueError, match="Amount is required"):
            self.handler.handle(event_data)
