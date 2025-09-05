"""
Fund Incremental Calculation Service Tests.

This module tests the FundIncrementalCalculationService which provides O(1) incremental updates
for fund capital chain calculations.

Key responsibilities tested:
- Incremental capital chain updates
- Smart event dependency tracking
- NAV-based and cost-based incremental calculations
- Fund summary updates

Test focus: Incremental calculation logic only - no model validation, no performance testing, no integration concerns.
"""

import pytest
from datetime import date, datetime
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from src.fund.services.fund_incremental_calculation_service import FundIncrementalCalculationService
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.enums import EventType, FundType, FundStatus
from src.fund.models import Fund, FundEvent


class TestFundIncrementalCalculationService:
    """Test suite for FundIncrementalCalculationService - Incremental calculation logic only"""
    
    @pytest.fixture
    def service(self):
        """Create a FundIncrementalCalculationService instance for testing."""
        return FundIncrementalCalculationService()
    
    @pytest.fixture
    def mock_fund(self):
        """Create a mock Fund object for testing."""
        fund = Mock(spec=Fund)
        fund.id = 1
        fund.name = "Test Fund"
        fund.tracking_type = FundType.NAV_BASED
        fund.status = FundStatus.ACTIVE
        fund.start_date = date(2020, 1, 1)
        fund.end_date = None
        fund.current_units = 0.0
        fund.current_equity_balance = 0.0
        fund.current_unit_price = 0.0
        fund.current_nav_total = 0.0
        fund.fund_events = []
        return fund
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session for testing."""
        session = Mock(spec=Session)
        return session

    # ============================================================================
    # SERVICE INITIALIZATION AND ARCHITECTURE
    # ============================================================================
    
    def test_service_initialization(self, service):
        """Test that the service initializes correctly."""
        assert service is not None
        assert hasattr(service, '_calculation_cache')
        assert service._calculation_cache == {}
        assert hasattr(service, 'calculation_service')
        assert isinstance(service.calculation_service, FundCalculationService)
    
    def test_clear_cache(self, service):
        """Test that the calculation cache can be cleared."""
        # Add some test data to cache
        service._calculation_cache[1] = {'test': 'data'}
        service._calculation_cache[2] = {'another': 'test'}
        
        assert len(service._calculation_cache) == 2
        
        service.clear_cache()
        
        assert len(service._calculation_cache) == 0

    # ============================================================================
    # INCREMENTAL CAPITAL CHAIN UPDATES
    # ============================================================================
    
    def test_update_capital_chain_incrementally_no_affected_events(self, service, mock_fund, mock_session):
        """Test incremental update when no events are affected."""
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        
        with patch.object(service, '_get_affected_events') as mock_get:
            mock_get.return_value = []
            
            service.update_capital_chain_incrementally(mock_fund, mock_event, mock_session)
            
            # Should not call any recalculation methods
            mock_get.assert_called_once_with(mock_fund, mock_event, mock_session)
    
    def test_update_capital_chain_incrementally_with_affected_events(self, service, mock_fund, mock_session):
        """Test incremental update when events are affected."""
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.CAPITAL_CALL
        
        affected_events = [mock_event]
        
        with patch.object(service, '_get_affected_events') as mock_get:
            with patch.object(service, '_recalculate_affected_events_incrementally') as mock_recalc:
                with patch.object(service, '_update_fund_summary_incrementally') as mock_update:
                    with patch.object(service, '_update_fund_status_incrementally') as mock_status:
                        mock_get.return_value = affected_events
                        
                        service.update_capital_chain_incrementally(mock_fund, mock_event, mock_session)
                        
                        mock_get.assert_called_once_with(mock_fund, mock_event, mock_session)
                        mock_recalc.assert_called_once_with(mock_fund, affected_events, mock_session)
                        mock_update.assert_called_once_with(mock_fund, mock_event, mock_session)
                        mock_status.assert_called_once_with(mock_fund, mock_session)

    # ============================================================================
    # SMART EVENT DEPENDENCY TRACKING
    # ============================================================================
    
    def test_get_affected_events_non_capital_event(self, service, mock_fund, mock_session):
        """Test that non-capital events don't affect capital chain."""
        mock_event = Mock(spec=FundEvent)
        mock_event.id = 1
        mock_event.event_type = EventType.DISTRIBUTION  # Non-capital event
        
        result = service._get_affected_events(mock_fund, mock_event, mock_session)
        
        assert result == []
    
    def test_get_affected_events_capital_event(self, service, mock_fund, mock_session):
        """Test that capital events correctly identify affected events."""
        # Create mock events
        mock_event1 = Mock(spec=FundEvent)
        mock_event1.id = 1
        mock_event1.event_type = EventType.CAPITAL_CALL
        
        mock_event2 = Mock(spec=FundEvent)
        mock_event2.id = 2
        mock_event2.event_type = EventType.UNIT_PURCHASE
        
        mock_event3 = Mock(spec=FundEvent)
        mock_event3.id = 3
        mock_event3.event_type = EventType.UNIT_SALE
        
        # Mock the query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [mock_event1, mock_event2, mock_event3]
        
        result = service._get_affected_events(mock_fund, mock_event1, mock_session)
        
        # Should return the triggering event and all subsequent events
        assert len(result) == 3
        assert result[0].id == 1  # Triggering event
        assert result[1].id == 2  # Subsequent event
        assert result[2].id == 3  # Subsequent event
    
    def test_get_affected_events_middle_event(self, service, mock_fund, mock_session):
        """Test that triggering from middle event returns correct subset."""
        # Create mock events
        mock_event1 = Mock(spec=FundEvent)
        mock_event1.id = 1
        mock_event1.event_type = EventType.CAPITAL_CALL
        
        mock_event2 = Mock(spec=FundEvent)
        mock_event2.id = 2
        mock_event2.event_type = EventType.UNIT_PURCHASE
        
        mock_event3 = Mock(spec=FundEvent)
        mock_event3.id = 3
        mock_event3.event_type = EventType.UNIT_SALE
        
        # Mock the query chain
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = [mock_event1, mock_event2, mock_event3]
        
        # Trigger from middle event
        result = service._get_affected_events(mock_fund, mock_event2, mock_session)
        
        # Should return the triggering event and subsequent events only
        assert len(result) == 2
        assert result[0].id == 2  # Triggering event
        assert result[1].id == 3  # Subsequent event
        assert mock_event1 not in result  # Previous event not included

    # ============================================================================
    # INCREMENTAL RECALCULATION
    # ============================================================================
    
    def test_recalculate_affected_events_incrementally_nav_based(self, service, mock_fund, mock_session):
        """Test incremental recalculation for NAV-based funds."""
        mock_fund.tracking_type = FundType.NAV_BASED
        
        affected_events = [Mock(spec=FundEvent)]
        
        with patch.object(service, '_calculate_nav_fields_incrementally') as mock_nav:
            service._recalculate_affected_events_incrementally(mock_fund, affected_events, mock_session)
            
            mock_nav.assert_called_once_with(mock_fund, affected_events, mock_session)
    
    def test_recalculate_affected_events_incrementally_cost_based(self, service, mock_fund, mock_session):
        """Test incremental recalculation for cost-based funds."""
        mock_fund.tracking_type = FundType.COST_BASED
        
        affected_events = [Mock(spec=FundEvent)]
        
        with patch.object(service, '_calculate_cost_based_fields_incrementally') as mock_cost:
            service._recalculate_affected_events_incrementally(mock_fund, affected_events, mock_session)
            
            mock_cost.assert_called_once_with(mock_fund, affected_events, mock_session)
    
    def test_recalculate_affected_events_incrementally_no_events(self, service, mock_fund, mock_session):
        """Test incremental recalculation with no affected events."""
        affected_events = []
        
        with patch.object(service, '_calculate_nav_fields_incrementally') as mock_nav:
            with patch.object(service, '_calculate_cost_based_fields_incrementally') as mock_cost:
                service._recalculate_affected_events_incrementally(mock_fund, affected_events, mock_session)
                
                mock_nav.assert_not_called()
                mock_cost.assert_not_called()

    # ============================================================================
    # NAV-BASED INCREMENTAL CALCULATIONS
    # ============================================================================
    
    def test_calculate_nav_fields_incrementally(self, service, mock_fund, mock_session):
        """Test incremental NAV field calculation."""
        # Create mock events
        mock_event1 = Mock(spec=FundEvent)
        mock_event1.id = 1
        mock_event1.event_type = EventType.UNIT_PURCHASE
        mock_event1.event_date = date(2023, 1, 1)
        
        mock_event2 = Mock(spec=FundEvent)
        mock_event2.id = 2
        mock_event2.event_type = EventType.UNIT_SALE
        mock_event2.event_date = date(2023, 1, 2)
        
        affected_events = [mock_event1, mock_event2]
        
        # Mock previous events query
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = []
        
        with patch.object(service, '_build_fifo_state') as mock_build_fifo:
            with patch.object(service, '_process_unit_purchase_incrementally') as mock_purchase:
                with patch.object(service, '_process_unit_sale_incrementally') as mock_sale:
                    mock_build_fifo.return_value = ([], 0.0)
                    mock_purchase.return_value = ([], 0.0)
                    mock_sale.return_value = ([], 0.0)
                    
                    service._calculate_nav_fields_incrementally(mock_fund, affected_events, mock_session)
                    
                    mock_build_fifo.assert_called_once()
                    mock_purchase.assert_called_once()
                    mock_sale.assert_called_once()
    
    def test_build_fifo_state(self, service):
        """Test FIFO state building from events."""
        # Create mock events
        mock_purchase1 = Mock(spec=FundEvent)
        mock_purchase1.event_type = EventType.UNIT_PURCHASE
        mock_purchase1.units_purchased = 100.0
        mock_purchase1.unit_price = 10.0
        mock_purchase1.brokerage_fee = 50.0
        mock_purchase1.event_date = date(2023, 1, 1)
        
        mock_sale = Mock(spec=FundEvent)
        mock_sale.event_type = EventType.UNIT_SALE
        mock_sale.units_sold = 30.0
        
        mock_purchase2 = Mock(spec=FundEvent)
        mock_purchase2.event_type = EventType.UNIT_PURCHASE
        mock_purchase2.units_purchased = 50.0
        mock_purchase2.unit_price = 12.0
        mock_purchase2.brokerage_fee = 25.0
        mock_purchase2.event_date = date(2023, 1, 2)
        
        events = [mock_purchase1, mock_sale, mock_purchase2]
        
        fifo, cumulative_units = service._build_fifo_state(events)
        
        # build_fifo_state only processes purchase events, not sales
        # After purchase1: 100 units at 10.50 effective price
        # After purchase2: 50 units at 12.50 effective price
        # Sale events don't modify the FIFO queue in this method
        assert len(fifo) == 2
        assert cumulative_units == 120.0  # 100 + 50 - 30 = 120
        
        # Check first FIFO entry (first purchase)
        first_entry = fifo[0]
        assert first_entry.units == 100.0  # units
        assert first_entry.unit_price == 10.0  # unit_price
        assert first_entry.effective_price == 10.5  # effective_price (10 + 50/100)
        
        # Check second FIFO entry (second purchase)
        second_entry = fifo[1]
        assert second_entry.units == 50.0  # units
        assert second_entry.unit_price == 12.0  # unit_price
        assert second_entry.effective_price == 12.5  # effective_price (12 + 25/50)
    
    def test_process_unit_purchase_incrementally(self, service):
        """Test incremental unit purchase processing."""
        mock_event = Mock(spec=FundEvent)
        mock_event.units_purchased = 100.0
        mock_event.unit_price = 10.0
        mock_event.brokerage_fee = 50.0
        mock_event.event_date = date(2023, 1, 1)
        
        fifo = []
        cumulative_units = 0.0
        
        new_fifo, new_cumulative_units = service._process_unit_purchase_incrementally(
            mock_event, fifo, cumulative_units
        )
        
        # Check event was updated
        assert mock_event.amount == 1050.0  # (100 * 10) + 50
        assert mock_event.units_owned == 100.0
        # SYSTEM: Equity balance is calculated from FIFO state (units * unit_price), not including brokerage fees
        assert mock_event.current_equity_balance == 1000.0  # 100 * 10
        
        # Check FIFO state
        assert len(new_fifo) == 1
        assert new_cumulative_units == 100.0
        
        fifo_entry = new_fifo[0]
        assert fifo_entry.units == 100.0  # units
        assert fifo_entry.unit_price == 10.0   # unit_price
        assert fifo_entry.effective_price == 10.5   # effective_price
    
    def test_process_unit_sale_incrementally(self, service):
        """Test incremental unit sale processing."""
        mock_event = Mock(spec=FundEvent)
        mock_event.units_sold = 30.0
        mock_event.unit_price = 15.0
        mock_event.brokerage_fee = 25.0
        mock_event.event_date = date(2023, 1, 2)
        
        # Pre-existing FIFO state
        from src.fund.calculators.fifo_capital_gains_calculator import FifoUnit
        fifo = [FifoUnit(units=100.0, unit_price=10.0, effective_price=10.5, purchase_date=date(2023, 1, 1), brokerage_fee=50.0)]
        cumulative_units = 100.0
        
        new_fifo, new_cumulative_units = service._process_unit_sale_incrementally(
            mock_event, fifo, cumulative_units
        )
        
        # Check event was updated
        assert mock_event.amount == 425.0  # (30 * 15) - 25
        assert mock_event.units_owned == 70.0
        
        # Check FIFO state
        assert len(new_fifo) == 1
        assert new_fifo[0].units == 70.0  # remaining units
        assert new_cumulative_units == 70.0

    # ============================================================================
    # COST-BASED INCREMENTAL CALCULATIONS
    # ============================================================================
    
    def test_calculate_cost_based_fields_incrementally(self, service, mock_fund, mock_session):
        """Test incremental cost-based field calculation."""
        # Create mock events
        mock_event1 = Mock(spec=FundEvent)
        mock_event1.id = 1
        mock_event1.event_type = EventType.CAPITAL_CALL
        mock_event1.event_date = date(2023, 1, 1)
        
        mock_event2 = Mock(spec=FundEvent)
        mock_event2.id = 2
        mock_event2.event_type = EventType.RETURN_OF_CAPITAL
        mock_event2.event_date = date(2023, 1, 2)
        
        affected_events = [mock_event1, mock_event2]
        
        # Mock previous events query
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.all.return_value = []
        
        with patch.object(service, '_build_running_balance') as mock_build_balance:
            with patch.object(service, '_process_capital_call_incrementally') as mock_call:
                with patch.object(service, '_process_return_of_capital_incrementally') as mock_return:
                    mock_build_balance.return_value = 0.0
                    mock_call.return_value = 0.0
                    mock_return.return_value = 0.0
                    
                    service._calculate_cost_based_fields_incrementally(mock_fund, affected_events, mock_session)
                    
                    mock_build_balance.assert_called_once()
                    mock_call.assert_called_once()
                    mock_return.assert_called_once()
    
    def test_build_running_balance(self, service):
        """Test running balance building from events."""
        # Create mock events
        mock_call1 = Mock(spec=FundEvent)
        mock_call1.event_type = EventType.CAPITAL_CALL
        mock_call1.amount = 1000.0
        
        mock_return = Mock(spec=FundEvent)
        mock_return.event_type = EventType.RETURN_OF_CAPITAL
        mock_return.amount = 300.0
        
        mock_call2 = Mock(spec=FundEvent)
        mock_call2.event_type = EventType.CAPITAL_CALL
        mock_call2.amount = 500.0
        
        events = [mock_call1, mock_return, mock_call2]
        
        balance = service._build_running_balance(events)
        
        # 1000 - 300 + 500 = 1200
        assert balance == 1200.0
    
    def test_process_capital_call_incrementally(self, service):
        """Test incremental capital call processing."""
        mock_event = Mock(spec=FundEvent)
        mock_event.amount = 1000.0
        
        running_balance = 500.0
        
        new_balance = service._process_capital_call_incrementally(mock_event, running_balance)
        
        # Check event was updated
        assert mock_event.current_equity_balance == 1500.0
        
        # Check new balance
        assert new_balance == 1500.0
    
    def test_process_return_of_capital_incrementally(self, service):
        """Test incremental return of capital processing."""
        mock_event = Mock(spec=FundEvent)
        mock_event.amount = 300.0
        
        running_balance = 1500.0
        
        new_balance = service._process_return_of_capital_incrementally(mock_event, running_balance)
        
        # Check event was updated
        assert mock_event.current_equity_balance == 1200.0
        
        # Check new balance
        assert new_balance == 1200.0

    # ============================================================================
    # FUND SUMMARY UPDATES
    # ============================================================================
    
    def test_update_fund_summary_incrementally_nav_based(self, service, mock_fund, mock_session):
        """Test incremental NAV fund summary updates."""
        mock_fund.tracking_type = FundType.NAV_BASED
        
        mock_event = Mock(spec=FundEvent)
        
        with patch.object(service, '_update_nav_fund_summary_incrementally') as mock_nav:
            service._update_fund_summary_incrementally(mock_fund, mock_event, mock_session)
            
            mock_nav.assert_called_once_with(mock_fund, mock_event, mock_session)
    
    def test_update_fund_summary_incrementally_cost_based(self, service, mock_fund, mock_session):
        """Test incremental cost-based fund summary updates."""
        mock_fund.tracking_type = FundType.COST_BASED
        
        mock_event = Mock(spec=FundEvent)
        
        with patch.object(service, '_update_cost_based_fund_summary_incrementally') as mock_cost:
            service._update_fund_summary_incrementally(mock_fund, mock_event, mock_session)
            
            mock_cost.assert_called_once_with(mock_fund, mock_event, mock_session)
    
    def test_update_nav_fund_summary_incrementally(self, service, mock_fund, mock_session):
        """Test incremental NAV fund summary updates."""
        mock_event = Mock(spec=FundEvent)
        mock_event.units_owned = 100.0
        mock_event.current_equity_balance = 1500.0
        mock_event.unit_price = 15.0
        
        # Mock latest unit event query
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.first.return_value = mock_event
        
        service._update_nav_fund_summary_incrementally(mock_fund, mock_event, mock_session)
        
        # Check fund was updated
        assert mock_fund.current_units == 100.0
        assert mock_fund.current_equity_balance == 1500.0
        assert mock_fund.current_unit_price == 15.0
        assert mock_fund.current_nav_total == 1500.0
    
    def test_update_cost_based_fund_summary_incrementally(self, service, mock_fund, mock_session):
        """Test incremental cost-based fund summary updates."""
        mock_event = Mock(spec=FundEvent)
        mock_event.current_equity_balance = 2000.0
        
        # Mock latest capital event query
        mock_query = Mock()
        mock_filter = Mock()
        mock_order_by = Mock()
        
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_filter
        mock_filter.order_by.return_value = mock_order_by
        mock_order_by.first.return_value = mock_event
        
        service._update_cost_based_fund_summary_incrementally(mock_fund, mock_event, mock_session)
        
        # Check fund was updated
        assert mock_fund.current_equity_balance == 2000.0

    # ============================================================================
    # FUND STATUS UPDATES
    # ============================================================================
    
    def test_update_fund_status_incrementally_to_realized(self, service, mock_fund, mock_session):
        """Test fund status update to realized when equity balance is zero."""
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 0.0
        
        service._update_fund_status_incrementally(mock_fund, mock_session)
        
        assert mock_fund.status == FundStatus.REALIZED
    
    def test_update_fund_status_incrementally_to_active(self, service, mock_fund, mock_session):
        """Test fund status update to active when equity balance is positive."""
        mock_fund.status = FundStatus.REALIZED
        mock_fund.current_equity_balance = 1000.0
        
        service._update_fund_status_incrementally(mock_fund, mock_session)
        
        assert mock_fund.status == FundStatus.ACTIVE
    
    def test_update_fund_status_incrementally_no_change(self, service, mock_fund, mock_session):
        """Test fund status update when no change is needed."""
        mock_fund.status = FundStatus.ACTIVE
        mock_fund.current_equity_balance = 1000.0
        
        service._update_fund_status_incrementally(mock_fund, mock_session)
        
        # Status should remain unchanged
        assert mock_fund.status == FundStatus.ACTIVE

    # ============================================================================
    # EDGE CASES AND ERROR HANDLING
    # ============================================================================
    
    def test_process_unit_purchase_incrementally_zero_units(self, service):
        """Test unit purchase processing with zero units."""
        mock_event = Mock(spec=FundEvent)
        mock_event.units_purchased = 0.0
        mock_event.unit_price = 10.0
        mock_event.brokerage_fee = 50.0
        
        fifo = []
        cumulative_units = 100.0
        
        new_fifo, new_cumulative_units = service._process_unit_purchase_incrementally(
            mock_event, fifo, cumulative_units
        )
        
        # Should handle zero units gracefully
        assert mock_event.amount == 50.0  # Just brokerage fee
        assert new_cumulative_units == 100.0  # No change
        assert len(new_fifo) == 0  # No FIFO entry for zero units
    
    def test_process_unit_sale_incrementally_insufficient_units(self, service):
        """Test unit sale processing when insufficient units in FIFO."""
        mock_event = Mock(spec=FundEvent)
        mock_event.units_sold = 150.0  # More than available in FIFO
        mock_event.unit_price = 15.0
        mock_event.brokerage_fee = 25.0
        
        # Pre-existing FIFO state with only 100 units
        from src.fund.calculators.fifo_capital_gains_calculator import FifoUnit
        fifo = [FifoUnit(units=100.0, unit_price=10.0, effective_price=10.5, purchase_date=date(2023, 1, 1), brokerage_fee=50.0)]
        cumulative_units = 100.0
        
        new_fifo, new_cumulative_units = service._process_unit_sale_incrementally(
            mock_event, fifo, cumulative_units
        )
        
        # Should handle insufficient units gracefully
        # SYSTEM: Amount is calculated as (units * unit_price) - brokerage_fee = (150 * 15) - 25 = 2225.0
        assert mock_event.amount == 2225.0  # (150 * 15) - 25
        assert new_cumulative_units == -50.0  # Negative units (edge case)
        assert len(new_fifo) == 0  # FIFO should be empty
    
    def test_build_fifo_state_with_none_values(self, service):
        """Test FIFO state building with None values in events."""
        # Create mock events with None values
        mock_purchase = Mock(spec=FundEvent)
        mock_purchase.event_type = EventType.UNIT_PURCHASE
        mock_purchase.units_purchased = None  # None value
        mock_purchase.unit_price = 10.0
        mock_purchase.brokerage_fee = 50.0
        
        events = [mock_purchase]
        
        fifo, cumulative_units = service._build_fifo_state(events)
        
        # Should handle None values gracefully
        assert len(fifo) == 0  # No FIFO entry for None units
        assert cumulative_units == 0.0  # No cumulative units
