"""
Fund Event Secondary Service Tests

This module tests the FundEventSecondaryService which handles secondary impacts
of fund events by orchestrating various specialized services.

Key focus areas:
- Event type routing to appropriate services
- Service orchestration and coordination
- Change collection and aggregation
- Proper delegation to specialized services
"""

import pytest
from datetime import date
from unittest.mock import Mock, patch, MagicMock
from typing import List

from src.fund.services.fund_event_secondary_service import FundEventSecondaryService
from src.fund.models import Fund, FundFieldChange
from src.fund.enums import EventType
from src.shared.enums.shared_enums import EventOperation


class TestFundEventSecondaryService:
    """Test suite for FundEventSecondaryService - Secondary impact orchestration"""
    
    @pytest.fixture
    def service(self):
        """Create a FundEventSecondaryService instance for testing."""
        return FundEventSecondaryService()
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.current_equity_balance = 1000.0
        fund.end_date = None
        return fund
    
    @pytest.fixture
    def mock_field_change(self):
        """Create a mock FundFieldChange object."""
        change = Mock(spec=FundFieldChange)
        change.field_name = "current_equity_balance"
        change.old_value = 1000.0
        change.new_value = 1500.0
        return change

    # ============================================================================
    # SERVICE INITIALIZATION TESTS
    # ============================================================================
    
    def test_service_initialization(self, service):
        """Test service initialization."""
        assert isinstance(service, FundEventSecondaryService)
        assert hasattr(service, 'logger')

    # ============================================================================
    # MAIN METHOD TESTS - handle_event_secondary_impact
    # ============================================================================
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_capital_call_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                       mock_status_service, mock_equity_service, mock_date_service,
                                       service, mock_fund, mock_session, mock_field_change):
        """Test handling of capital call event with all secondary impacts."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.CREATE
        
        # Mock service instances and their return values
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_start_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Capital call: start_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify all services were instantiated with session
        mock_date_service.assert_called_once_with(mock_session)
        mock_equity_service.assert_called_once_with(mock_session)
        mock_status_service.assert_called_once_with(mock_session)
        mock_irr_service.assert_called_once_with(mock_session)
        mock_pnl_service.assert_called_once_with(mock_session)
        mock_nav_service.assert_called_once_with(mock_session)
        
        # Verify specific service methods were called
        mock_date_service_instance.update_fund_start_date.assert_called_once_with(
            fund_id=mock_fund.id, event_id=event_id, fund_event_operation=operation, session=mock_session
        )
        # Equity service is called twice for equity events
        assert mock_equity_service_instance.update_fund_equity_fields.call_count == 2
        mock_equity_service_instance.update_fund_equity_fields.assert_any_call(
            mock_fund, mock_session, current_equity_flag=True
        )
        mock_equity_service_instance.update_fund_equity_fields.assert_any_call(
            mock_fund, mock_session, current_equity_flag=False
        )
        mock_status_service_instance.update_status_after_equity_event.assert_called_once_with(
            mock_fund, mock_session
        )
        mock_date_service_instance.update_fund_duration.assert_called_once_with(
            mock_fund, mock_session
        )
        mock_irr_service_instance.update_irrs.assert_called_once_with(
            mock_fund, mock_session
        )
        mock_pnl_service_instance.update_fund_pnl.assert_called_once_with(
            mock_fund, mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_return_of_capital_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                           mock_status_service, mock_equity_service, mock_date_service,
                                           service, mock_fund, mock_session, mock_field_change):
        """Test handling of return of capital event."""
        # Arrange
        event_id = 2
        event_type = EventType.RETURN_OF_CAPITAL
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_end_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Return of capital: end_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify end date update was called
        mock_date_service_instance.update_fund_end_date.assert_called_once_with(
            mock_fund.id, mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_nav_update_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                    mock_status_service, mock_equity_service, mock_date_service,
                                    service, mock_fund, mock_session, mock_field_change):
        """Test handling of NAV update event."""
        # Arrange
        event_id = 3
        event_type = EventType.NAV_UPDATE
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_nav_service_instance.update_nav_fund_fields.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3  # NAV update: irr, nav, pnl
        
        # Verify NAV service was called
        mock_nav_service_instance.update_nav_fund_fields.assert_called_once_with(
            mock_fund, mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_tax_statement_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                       mock_status_service, mock_equity_service, mock_date_service,
                                       service, mock_fund, mock_session, mock_field_change):
        """Test handling of tax statement event."""
        # Arrange
        event_id = 4
        event_type = EventType.TAX_PAYMENT
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_status_service_instance.update_status_after_tax_statement.return_value = [mock_field_change]
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 3  # Only status, IRR, and PnL for tax events
        
        # Verify tax statement status update was called
        mock_status_service_instance.update_status_after_tax_statement.assert_called_once_with(
            mock_fund, mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_delete_operation(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                    mock_status_service, mock_equity_service, mock_date_service,
                                    service, mock_fund, mock_session, mock_field_change):
        """Test handling of delete operation for capital call event."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.DELETE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_start_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Delete capital call: start_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify start date update was called without event_id for delete operation
        mock_date_service_instance.update_fund_start_date.assert_called_once_with(
            fund_id=mock_fund.id, fund_event_operation=operation, session=mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_update_operation(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                    mock_status_service, mock_equity_service, mock_date_service,
                                    service, mock_fund, mock_session, mock_field_change):
        """Test handling of update operation for capital call event."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.UPDATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_start_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Update capital call: start_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify start date update was called without event_id for UPDATE operation
        mock_date_service_instance.update_fund_start_date.assert_called_once_with(
            fund_id=mock_fund.id, fund_event_operation=operation, session=mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_unit_purchase_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                       mock_status_service, mock_equity_service, mock_date_service,
                                       service, mock_fund, mock_session, mock_field_change):
        """Test handling of unit purchase event (equity call event)."""
        # Arrange
        event_id = 5
        event_type = EventType.UNIT_PURCHASE
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_start_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Unit purchase: start_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify start date update was called with event_id for CREATE operation
        mock_date_service_instance.update_fund_start_date.assert_called_once_with(
            fund_id=mock_fund.id, event_id=event_id, fund_event_operation=operation, session=mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_unit_sale_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                   mock_status_service, mock_equity_service, mock_date_service,
                                   service, mock_fund, mock_session, mock_field_change):
        """Test handling of unit sale event (equity return event)."""
        # Arrange
        event_id = 6
        event_type = EventType.UNIT_SALE
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_date_service_instance.update_fund_end_date.return_value = mock_field_change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [mock_field_change]
        mock_status_service_instance.update_status_after_equity_event.return_value = [mock_field_change]
        mock_date_service_instance.update_fund_duration.return_value = mock_field_change
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Unit sale: end_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Verify end date update was called
        mock_date_service_instance.update_fund_end_date.assert_called_once_with(
            mock_fund.id, mock_session
        )
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_system_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                mock_status_service, mock_equity_service, mock_date_service,
                                service, mock_fund, mock_session, mock_field_change):
        """Test handling of system event (e.g., daily interest charge)."""
        # Arrange
        event_id = 7
        event_type = EventType.DAILY_RISK_FREE_INTEREST_CHARGE
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2  # Only IRR and PnL for system events
        
        # Verify equity services were not called
        mock_equity_service_instance.update_fund_equity_fields.assert_not_called()
        mock_status_service_instance.update_status_after_equity_event.assert_not_called()
        mock_date_service_instance.update_fund_duration.assert_not_called()
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_handle_non_equity_event(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                   mock_status_service, mock_equity_service, mock_date_service,
                                   service, mock_fund, mock_session, mock_field_change):
        """Test handling of non-equity event (e.g., distribution)."""
        # Arrange
        event_id = 8
        event_type = EventType.DISTRIBUTION
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values
        mock_irr_service_instance.update_irrs.return_value = [mock_field_change]
        mock_pnl_service_instance.update_fund_pnl.return_value = [mock_field_change]
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 2  # Only IRR and PnL for non-equity events
        
        # Verify equity services were not called
        mock_equity_service_instance.update_fund_equity_fields.assert_not_called()
        mock_status_service_instance.update_status_after_equity_event.assert_not_called()
        mock_date_service_instance.update_fund_duration.assert_not_called()
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_service_error_handling(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                   mock_status_service, mock_equity_service, mock_date_service,
                                   service, mock_fund, mock_session):
        """Test error handling when a service fails."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock one service to raise an exception
        mock_date_service_instance.update_fund_start_date.side_effect = Exception("Service error")
        
        # Act & Assert
        with pytest.raises(Exception, match="Service error"):
            service.handle_event_secondary_impact(
                fund=mock_fund,
                fund_event_type=event_type,
                fund_event_operation=operation,
                session=mock_session,
                event_id=event_id
            )
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_change_aggregation(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                               mock_status_service, mock_equity_service, mock_date_service,
                               service, mock_fund, mock_session):
        """Test that changes from all services are properly aggregated."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.CREATE
        
        # Create multiple mock changes
        change1 = Mock(spec=FundFieldChange)
        change1.field_name = "current_equity_balance"
        change2 = Mock(spec=FundFieldChange)
        change2.field_name = "status"
        change3 = Mock(spec=FundFieldChange)
        change3.field_name = "duration"
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values with multiple changes
        mock_date_service_instance.update_fund_start_date.return_value = change1
        mock_equity_service_instance.update_fund_equity_fields.return_value = [change2]
        mock_status_service_instance.update_status_after_equity_event.return_value = [change3]
        mock_date_service_instance.update_fund_duration.return_value = None  # No change
        mock_irr_service_instance.update_irrs.return_value = []
        mock_pnl_service_instance.update_fund_pnl.return_value = []
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # Capital call: start_date, equity_current, equity_other, status, duration, irr, pnl
        
        # Check that our specific changes are in the result
        # change1 is returned directly from start_date update
        assert change1 in result
        # change2 is returned as a list from equity service calls
        assert [change2] in result
        # change3 is returned as a list from status service
        assert [change3] in result
    
    # ============================================================================
    # EDGE CASE TESTS
    # ============================================================================
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_services_return_none_changes(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                                         mock_status_service, mock_equity_service, mock_date_service,
                                         service, mock_fund, mock_session):
        """Test handling when services return None instead of changes."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.CREATE
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values - all return None
        mock_date_service_instance.update_fund_start_date.return_value = None
        mock_equity_service_instance.update_fund_equity_fields.return_value = None
        mock_status_service_instance.update_status_after_equity_event.return_value = None
        mock_date_service_instance.update_fund_duration.return_value = None
        mock_irr_service_instance.update_irrs.return_value = None
        mock_pnl_service_instance.update_fund_pnl.return_value = None
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # All services called, but returning None
        assert all(change is None for change in result)
    
    @patch('src.fund.services.fund_event_secondary_service.FundDateService')
    @patch('src.fund.services.fund_event_secondary_service.FundEquityService')
    @patch('src.fund.services.fund_event_secondary_service.FundStatusService')
    @patch('src.fund.services.fund_event_secondary_service.FundIrRService')
    @patch('src.fund.services.fund_event_secondary_service.FundPnlService')
    @patch('src.fund.services.fund_event_secondary_service.FundNavService')
    def test_mixed_return_types(self, mock_nav_service, mock_pnl_service, mock_irr_service,
                               mock_status_service, mock_equity_service, mock_date_service,
                               service, mock_fund, mock_session, mock_field_change):
        """Test handling of mixed return types (single change vs list of changes)."""
        # Arrange
        event_id = 1
        event_type = EventType.CAPITAL_CALL
        operation = EventOperation.CREATE
        
        # Create multiple mock changes
        change1 = Mock(spec=FundFieldChange)
        change1.field_name = "start_date"
        change2 = Mock(spec=FundFieldChange)
        change2.field_name = "equity_balance"
        change3 = Mock(spec=FundFieldChange)
        change3.field_name = "status"
        
        # Mock service instances
        mock_date_service_instance = Mock()
        mock_equity_service_instance = Mock()
        mock_status_service_instance = Mock()
        mock_irr_service_instance = Mock()
        mock_pnl_service_instance = Mock()
        mock_nav_service_instance = Mock()
        
        mock_date_service.return_value = mock_date_service_instance
        mock_equity_service.return_value = mock_equity_service_instance
        mock_status_service.return_value = mock_status_service_instance
        mock_irr_service.return_value = mock_irr_service_instance
        mock_pnl_service.return_value = mock_pnl_service_instance
        mock_nav_service.return_value = mock_nav_service_instance
        
        # Mock return values with mixed types
        mock_date_service_instance.update_fund_start_date.return_value = change1  # Single change
        mock_equity_service_instance.update_fund_equity_fields.return_value = [change2, change3]  # List of changes
        mock_status_service_instance.update_status_after_equity_event.return_value = None  # No change
        mock_date_service_instance.update_fund_duration.return_value = change1  # Single change
        mock_irr_service_instance.update_irrs.return_value = []  # Empty list
        mock_pnl_service_instance.update_fund_pnl.return_value = [change2]  # Single item list
        
        # Act
        result = service.handle_event_secondary_impact(
            fund=mock_fund,
            fund_event_type=event_type,
            fund_event_operation=operation,
            session=mock_session,
            event_id=event_id
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) == 7  # All services called
        
        # Verify the mixed return types are handled correctly
        assert change1 in result  # Single change from start_date
        assert [change2, change3] in result  # List of changes from equity service
        assert None in result  # None from status service
        assert change1 in result  # Single change from duration
        assert [] in result  # Empty list from IRR service
        assert [change2] in result  # Single item list from PnL service
