"""
Fund Equity Service Tests

This module tests the FundEquityService which handles database operations
for fund equity calculations using the pure FundEquityCalculator.

Key focus areas:
- Single computation approach for efficiency
- Database updates with change detection
- Proper delegation to calculator layer
- Field change tracking
"""

import pytest
from decimal import Decimal
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.fund.services.fund_equity_service import FundEquityService
from src.fund.models import Fund, FundFieldChange, FundEvent
from src.fund.enums import EventType, SortOrder, FundTrackingType, FundStatus


class TestFundEquityService:
    """Test suite for FundEquityService - Database operations for equity calculations"""
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def service(self, mock_session):
        """Create a FundEquityService instance for testing."""
        return FundEquityService(mock_session)
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.tracking_type = FundTrackingType.NAV_BASED
        fund.status = FundStatus.ACTIVE
        fund.current_equity_balance = Decimal('10000.00')
        fund.average_equity_balance = Decimal('9500.00')
        fund.total_cost_basis = Decimal('8000.00')
        return fund
    
    @pytest.fixture
    def mock_events(self):
        """Create mock fund events for testing."""
        from datetime import date
        
        events = []
        
        # Event 1: Capital call
        event1 = Mock(spec=FundEvent)
        event1.id = 1
        event1.event_type = EventType.CAPITAL_CALL
        event1.event_date = date(2024, 1, 1)
        event1.amount = Decimal('10000.00')
        event1.current_equity_balance = Decimal('10000.00')
        event1.fund = Mock()  # Add fund reference for calculator
        event1.units_purchased = None
        event1.unit_price = None
        event1.units_sold = None
        events.append(event1)
        
        # Event 2: Return of capital
        event2 = Mock(spec=FundEvent)
        event2.id = 2
        event2.event_type = EventType.RETURN_OF_CAPITAL
        event2.event_date = date(2024, 6, 1)
        event2.amount = Decimal('2000.00')
        event2.current_equity_balance = Decimal('8000.00')
        event2.fund = Mock()  # Add fund reference for calculator
        event2.units_purchased = None
        event2.unit_price = None
        event2.units_sold = None
        events.append(event2)
        
        return events
    
    @pytest.fixture
    def mock_event_balances(self):
        """Create mock event balances for testing."""
        return [
            (Decimal('10000.00'), True),   # Event 1: balance changed
            (Decimal('8000.00'), False),   # Event 2: balance unchanged
        ]

    # ============================================================================
    # SERVICE INITIALIZATION TESTS
    # ============================================================================
    
    def test_service_initialization(self, mock_session):
        """Test service initialization with database session."""
        service = FundEquityService(mock_session)
        
        assert service.session == mock_session
        assert hasattr(service, 'calculator')
    
    # ============================================================================
    # MAIN METHOD TESTS - update_fund_equity_fields
    # ============================================================================
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_all_flags_true(self, mock_repo_class, 
                                                      service, mock_fund, mock_session, mock_events, mock_event_balances):
        """Test updating all equity fields with all flags enabled."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = mock_event_balances
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('8000.00')
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9000.00')
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('7500.00')
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act
        result = service.update_fund_equity_fields(mock_fund, mock_session)
        
        # Assert
        # Verify repository was called correctly
        mock_repo_class.get_by_fund.assert_called_once_with(
            mock_fund.id, mock_session,
            event_types=[EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL, EventType.UNIT_PURCHASE, EventType.UNIT_SALE],
            sort_order=SortOrder.ASC
        )
        
        # Verify calculator methods were called
        mock_calculator.calculate_event_equity_balances.assert_called_once_with(mock_fund, mock_events)
        mock_calculator.calculate_current_equity_from_balances.assert_called_once_with(mock_event_balances)
        mock_calculator.calculate_average_equity_from_balances.assert_called_once_with(mock_events, mock_event_balances)
        mock_calculator.calculate_total_cost_basis_from_balances.assert_called_once_with(mock_event_balances, mock_fund, mock_events)
        
        # Verify fund fields were updated
        assert mock_fund.current_equity_balance == Decimal('8000.00')
        assert mock_fund.average_equity_balance == Decimal('9000.00')
        assert mock_fund.total_cost_basis == Decimal('7500.00')
        
        # Verify event updates for changed events only
        assert mock_events[0].current_equity_balance == Decimal('10000.00')  # Changed
        # Event 2 should not be updated since has_changed=False
        
        # Verify field changes tracking
        assert len(result) == 3
        assert any(change.field_name == 'current_equity_balance' for change in result)
        assert any(change.field_name == 'average_equity_balance' for change in result)
        assert any(change.field_name == 'total_cost_basis' for change in result)
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_selective_flags(self, mock_repo_class,
                                                       service, mock_fund, mock_session, mock_events, mock_event_balances):
        """Test updating only specific equity fields with selective flags."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = mock_event_balances
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('8000.00')
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9000.00')
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('7500.00')
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act - Only update current equity and total cost basis
        result = service.update_fund_equity_fields(
            mock_fund, mock_session,
            current_equity_flag=True,
            average_equity_flag=False,
            total_cost_basis_flag=True
        )
        
        # Assert
        # Verify only current equity and total cost basis were calculated
        mock_calculator.calculate_current_equity_from_balances.assert_called_once()
        mock_calculator.calculate_average_equity_from_balances.assert_not_called()
        mock_calculator.calculate_total_cost_basis_from_balances.assert_called_once()
        
        # Verify only specific fields were updated
        assert mock_fund.current_equity_balance == Decimal('8000.00')
        assert mock_fund.average_equity_balance == Decimal('9500.00')  # Unchanged
        assert mock_fund.total_cost_basis == Decimal('7500.00')
        
        # Verify only relevant field changes are tracked
        assert len(result) == 2
        assert any(change.field_name == 'current_equity_balance' for change in result)
        assert any(change.field_name == 'total_cost_basis' for change in result)
        assert not any(change.field_name == 'average_equity_balance' for change in result)
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_no_changes(self, mock_repo_class,
                                                  service, mock_fund, mock_session, mock_events):
        """Test when no fields actually change values."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = [
            (Decimal('10000.00'), False),   # No change
            (Decimal('8000.00'), False),    # No change
        ]
        # Return same values as current fund values
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('10000.00')
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9500.00')
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('8000.00')
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act
        result = service.update_fund_equity_fields(mock_fund, mock_session)
        
        # Assert
        # Verify fund fields were updated to same values
        assert mock_fund.current_equity_balance == Decimal('10000.00')
        assert mock_fund.average_equity_balance == Decimal('9500.00')
        assert mock_fund.total_cost_basis == Decimal('8000.00')
        
        # Verify no field changes were detected
        assert result is None
        
        # Verify no events were updated since none changed
        for event in mock_events:
            # Events should not have their current_equity_balance updated
            pass
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_event_updates(self, mock_repo_class,
                                                     service, mock_fund, mock_session, mock_events):
        """Test that only changed events get their balance updated."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = [
            (Decimal('10500.00'), True),    # Changed
            (Decimal('8000.00'), False),    # Unchanged
            (Decimal('3000.00'), True),     # Changed
        ]
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('8000.00')
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9000.00')
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('7500.00')
        
        # Add third event
        event3 = Mock(spec=FundEvent)
        event3.id = 3
        event3.event_type = EventType.UNIT_PURCHASE
        mock_events.append(event3)
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act
        service.update_fund_equity_fields(mock_fund, mock_session)
        
        # Assert
        # Verify only changed events were updated
        assert mock_events[0].current_equity_balance == Decimal('10500.00')  # Changed
        # mock_events[1] should not be updated (has_changed=False)
        assert mock_events[2].current_equity_balance == Decimal('3000.00')   # Changed
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_field_change_tracking(self, mock_repo_class,
                                                             service, mock_fund, mock_session, mock_events):
        """Test proper tracking of field changes with old and new values."""
        # Arrange
        old_current_equity = mock_fund.current_equity_balance
        old_average_equity = mock_fund.average_equity_balance
        old_total_cost = mock_fund.total_cost_basis
        
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = [(Decimal('10000.00'), False)]
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('12000.00')  # Changed
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9500.00')   # Same
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('9000.00') # Changed
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act
        result = service.update_fund_equity_fields(mock_fund, mock_session)
        
        # Assert
        assert len(result) == 2  # Only current_equity_balance and total_cost_basis changed
        
        # Verify current equity change
        current_equity_change = next(change for change in result if change.field_name == 'current_equity_balance')
        assert current_equity_change.old_value == old_current_equity
        assert current_equity_change.new_value == Decimal('12000.00')
        
        # Verify total cost basis change
        cost_basis_change = next(change for change in result if change.field_name == 'total_cost_basis')
        assert cost_basis_change.old_value == old_total_cost
        assert cost_basis_change.new_value == Decimal('9000.00')
        
        # Verify no average equity change
        assert not any(change.field_name == 'average_equity_balance' for change in result)
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_repository_error(self, mock_repo_class, service, mock_fund, mock_session):
        """Test handling of repository errors."""
        # Arrange
        mock_repo_class.get_by_fund.side_effect = Exception("Database error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Database error"):
            service.update_fund_equity_fields(mock_fund, mock_session)
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_update_fund_equity_fields_calculator_error(self, mock_repo_class,
                                                        service, mock_fund, mock_session, mock_events):
        """Test handling of calculator errors."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.side_effect = Exception("Calculation error")
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act & Assert
        with pytest.raises(Exception, match="Calculation error"):
            service.update_fund_equity_fields(mock_fund, mock_session)
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    @patch('src.fund.services.fund_equity_service.FundEventRepository')
    def test_service_calculator_integration(self, mock_repo_class,
                                           service, mock_fund, mock_session, mock_events):
        """Test proper integration between service and calculator layers."""
        # Arrange
        mock_calculator = Mock()
        service.calculator = mock_calculator  # Replace the real calculator with mock
        mock_calculator.calculate_event_equity_balances.return_value = [(Decimal('10000.00'), True)]
        mock_calculator.calculate_current_equity_from_balances.return_value = Decimal('8000.00')
        mock_calculator.calculate_average_equity_from_balances.return_value = Decimal('9000.00')
        mock_calculator.calculate_total_cost_basis_from_balances.return_value = Decimal('7500.00')
        
        mock_repo_class.get_by_fund.return_value = mock_events
        
        # Act
        service.update_fund_equity_fields(mock_fund, mock_session)
        
        # Assert
        # Verify calculator was properly instantiated and used
        assert service.calculator == mock_calculator
        
        # Verify all calculator methods were called with correct parameters
        mock_calculator.calculate_event_equity_balances.assert_called_once_with(mock_fund, mock_events)
        mock_calculator.calculate_current_equity_from_balances.assert_called_once()
        mock_calculator.calculate_average_equity_from_balances.assert_called_once()
        mock_calculator.calculate_total_cost_basis_from_balances.assert_called_once()
