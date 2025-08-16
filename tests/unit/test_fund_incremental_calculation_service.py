"""
Unit tests for FundIncrementalCalculationService.

Tests the O(1) incremental calculation system that replaces
the O(n) full chain recalculation approach.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session

from src.fund.services.fund_incremental_calculation_service import FundIncrementalCalculationService
from src.fund.models import Fund, FundEvent, EventType, FundType
from src.fund.enums import FundStatus
from tests.factories import FundFactory, InvestmentCompanyFactory, EntityFactory


class TestFundIncrementalCalculationService:
    """Test suite for FundIncrementalCalculationService."""
    
    @pytest.fixture
    def service(self):
        """Create a fresh service instance for each test."""
        return FundIncrementalCalculationService()
    
    @pytest.fixture
    def nav_fund(self, db_session):
        """Create a NAV-based fund for testing."""
        from tests.factories import set_session
        set_session(db_session)
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.NAV_BASED
        )
        return fund
    
    @pytest.fixture
    def cost_fund(self, db_session):
        """Create a cost-based fund for testing."""
        from tests.factories import set_session
        set_session(db_session)
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.COST_BASED
        )
        return fund
    
    def test_service_initialization(self, service):
        """Test that the service initializes correctly."""
        assert service is not None
        assert hasattr(service, '_calculation_cache')
        assert service._calculation_cache == {}
    
    def test_get_affected_events_nav_based(self, service, nav_fund, db_session):
        """Test that NAV-based events correctly identify affected events."""
        # Create a unit purchase event
        event1 = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date(2024, 1, 1),
            units_purchased=100,
            unit_price=10.0,
            brokerage_fee=5.0
        )
        db_session.add(event1)
        db_session.flush()
        
        # Create a unit sale event
        event2 = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.UNIT_SALE,
            event_date=date(2024, 2, 1),
            units_sold=50,
            unit_price=12.0,
            brokerage_fee=5.0
        )
        db_session.add(event2)
        db_session.flush()
        
        # Test that only the sale event is affected by the purchase
        affected_events = service._get_affected_events(nav_fund, event1, db_session)
        assert len(affected_events) == 2  # Purchase and sale
        assert affected_events[0].id == event1.id
        assert affected_events[1].id == event2.id
        
        # Test that only the sale event is affected by the sale
        affected_events = service._get_affected_events(nav_fund, event2, db_session)
        assert len(affected_events) == 1  # Only sale
        assert affected_events[0].id == event2.id
    
    def test_get_affected_events_cost_based(self, service, cost_fund, db_session):
        """Test that cost-based events correctly identify affected events."""
        # Create a capital call event
        event1 = FundEvent(
            fund_id=cost_fund.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2024, 1, 1),
            amount=100000.0
        )
        db_session.add(event1)
        db_session.flush()
        
        # Create a return of capital event
        event2 = FundEvent(
            fund_id=cost_fund.id,
            event_type=EventType.RETURN_OF_CAPITAL,
            event_date=date(2024, 2, 1),
            amount=50000.0
        )
        db_session.add(event2)
        db_session.flush()
        
        # Test that both events are affected by the capital call
        affected_events = service._get_affected_events(cost_fund, event1, db_session)
        assert len(affected_events) == 2  # Call and return
        assert affected_events[0].id == event1.id
        assert affected_events[1].id == event2.id
        
        # Test that only return is affected by the return
        affected_events = service._get_affected_events(cost_fund, event2, db_session)
        assert len(affected_events) == 1  # Only return
        assert affected_events[0].id == event2.id
    
    def test_get_affected_events_non_capital_event(self, service, nav_fund, db_session):
        """Test that non-capital events return no affected events."""
        # Create a distribution event (non-capital)
        event = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=1000.0
        )
        db_session.add(event)
        db_session.flush()
        
        # Non-capital events should not affect capital chain
        affected_events = service._get_affected_events(nav_fund, event, db_session)
        assert len(affected_events) == 0
    
    def test_build_fifo_state(self, service):
        """Test FIFO state building for NAV-based calculations."""
        # Create test events
        events = [
            FundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2024, 1, 1),
                units_purchased=100,
                unit_price=10.0,
                brokerage_fee=5.0
            ),
            FundEvent(
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2024, 2, 1),
                units_purchased=50,
                unit_price=12.0,
                brokerage_fee=3.0
            ),
            FundEvent(
                event_type=EventType.UNIT_SALE,
                event_date=date(2024, 3, 1),
                units_sold=75,
                unit_price=15.0,
                brokerage_fee=5.0
            )
        ]
        
        fifo, cumulative_units = service._build_fifo_state(events)
        
        # Check FIFO state
        assert len(fifo) == 2  # 100 units @ 10.0, 25 units @ 12.0
        assert fifo[0][0] == 25  # Remaining units from first purchase (100 - 75)
        assert abs(fifo[0][1] - 10.0) < 0.01  # First purchase price
        assert fifo[1][0] == 50  # All units from second purchase
        assert abs(fifo[1][1] - 12.0) < 0.01  # Second purchase price
        
        # Check cumulative units
        assert cumulative_units == 75  # 100 + 50 - 75
    
    def test_build_running_balance(self, service):
        """Test running balance building for cost-based calculations."""
        # Create test events
        events = [
            FundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2024, 2, 1),
                amount=100000.0
            ),
            FundEvent(
                event_type=EventType.CAPITAL_CALL,
                event_date=date(2024, 2, 1),
                amount=50000.0
            ),
            FundEvent(
                event_type=EventType.RETURN_OF_CAPITAL,
                event_date=date(2024, 3, 1),
                amount=75000.0
            )
        ]
        
        balance = service._build_running_balance(events)
        assert balance == 75000.0  # 100000 + 50000 - 75000
    
    def test_process_unit_purchase_incrementally(self, service):
        """Test incremental unit purchase processing."""
        event = FundEvent(
            event_type=EventType.UNIT_PURCHASE,
            units_purchased=100,
            unit_price=10.0,
            brokerage_fee=5.0
        )
        
        fifo = []
        cumulative_units = 0.0
        
        fifo, cumulative_units = service._process_unit_purchase_incrementally(
            event, fifo, cumulative_units
        )
        
        # Check event fields updated
        assert event.amount == 1005.0  # (100 * 10) + 5
        assert event.units_owned == 100
        assert event.current_equity_balance == 1000.0  # 100 * 10 (excludes brokerage)
        
        # Check FIFO state updated
        assert len(fifo) == 1
        assert fifo[0][0] == 100  # units
        assert fifo[0][1] == 10.0  # unit_price
        assert cumulative_units == 100
    
    def test_process_unit_sale_incrementally(self, service):
        """Test incremental unit sale processing."""
        # Setup FIFO with existing units
        fifo = [(100, 10.0, 10.05, date(2024, 1, 1), 5.0)]
        cumulative_units = 100.0
        
        event = FundEvent(
            event_type=EventType.UNIT_SALE,
            units_sold=60,
            unit_price=12.0,
            brokerage_fee=3.0
        )
        
        fifo, cumulative_units = service._process_unit_sale_incrementally(
            event, fifo, cumulative_units
        )
        
        # Check event fields updated
        assert event.amount == 717.0  # (60 * 12) - 3
        assert event.units_owned == 40  # 100 - 60
        assert event.current_equity_balance == 400.0  # 40 * 10
        
        # Check FIFO state updated
        assert len(fifo) == 1
        assert fifo[0][0] == 40  # remaining units
        assert cumulative_units == 40
    
    def test_process_capital_call_incrementally(self, service):
        """Test incremental capital call processing."""
        event = FundEvent(
            event_type=EventType.CAPITAL_CALL,
            amount=100000.0
        )
        
        running_balance = 50000.0
        
        new_balance = service._process_capital_call_incrementally(event, running_balance)
        
        # Check event fields updated
        assert event.current_equity_balance == 150000.0  # 50000 + 100000
        
        # Check balance updated
        assert new_balance == 150000.0
    
    def test_process_return_of_capital_incrementally(self, service):
        """Test incremental return of capital processing."""
        event = FundEvent(
            event_type=EventType.RETURN_OF_CAPITAL,
            amount=50000.0
        )
        
        running_balance = 150000.0
        
        new_balance = service._process_return_of_capital_incrementally(event, running_balance)
        
        # Check event fields updated
        assert event.current_equity_balance == 100000.0  # 150000 - 50000
        
        # Check balance updated
        assert new_balance == 100000.0
    
    def test_update_capital_chain_incrementally_nav_based(self, service, nav_fund, db_session):
        """Test complete incremental update for NAV-based fund."""
        # Create initial unit purchase
        event1 = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date(2024, 1, 1),
            units_purchased=100,
            unit_price=10.0,
            brokerage_fee=5.0
        )
        db_session.add(event1)
        db_session.flush()
        
        # Create unit sale that should be affected
        event2 = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.UNIT_SALE,
            event_date=date(2024, 2, 1),
            units_sold=50,
            unit_price=12.0,
            brokerage_fee=3.0
        )
        db_session.add(event2)
        db_session.flush()
        
        # Perform incremental update
        service.update_capital_chain_incrementally(nav_fund, event1, db_session)
        
        # Check that both events were processed
        assert event1.units_owned == 100
        assert event1.current_equity_balance == 1000.0
        assert event2.units_owned == 50
        assert event2.current_equity_balance == 500.0
        
        # Check fund summary updated
        assert nav_fund.current_units == 50
        assert nav_fund.current_equity_balance == 500.0
    
    def test_update_capital_chain_incrementally_cost_based(self, service, cost_fund, db_session):
        """Test complete incremental update for cost-based fund."""
        # Create initial capital call
        event1 = FundEvent(
            fund_id=cost_fund.id,
            event_type=EventType.CAPITAL_CALL,
            event_date=date(2024, 1, 1),
            amount=100000.0
        )
        db_session.add(event1)
        db_session.flush()
        
        # Create return of capital that should be affected
        event2 = FundEvent(
            fund_id=cost_fund.id,
            event_type=EventType.RETURN_OF_CAPITAL,
            event_date=date(2024, 2, 1),
            amount=50000.0
        )
        db_session.add(event2)
        db_session.flush()
        
        # Perform incremental update
        service.update_capital_chain_incrementally(cost_fund, event1, db_session)
        
        # Check that both events were processed
        assert event1.current_equity_balance == 100000.0
        assert event2.current_equity_balance == 50000.0
        
        # Check fund summary updated
        assert cost_fund.current_equity_balance == 50000.0
    
    def test_update_capital_chain_incrementally_no_affected_events(self, service, nav_fund, db_session):
        """Test incremental update when no events are affected."""
        # Create a distribution event (non-capital)
        event = FundEvent(
            fund_id=nav_fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=1000.0
        )
        db_session.add(event)
        db_session.flush()
        
        # This should not trigger any capital chain updates
        service.update_capital_chain_incrementally(nav_fund, event, db_session)
        
        # No changes should occur
        assert nav_fund.current_equity_balance == 0.0
    
    def test_clear_cache(self, service):
        """Test that cache clearing works correctly."""
        # Add some test data to cache
        service._calculation_cache[1] = {'test': 'data'}
        service._calculation_cache[2] = {'another': 'test'}
        
        assert len(service._calculation_cache) == 2
        
        # Clear cache
        service.clear_cache()
        
        assert len(service._calculation_cache) == 0
        assert service._calculation_cache == {}


class TestIncrementalCalculationPerformance:
    """Performance tests for incremental calculation system."""
    
    @pytest.fixture
    def service(self):
        return FundIncrementalCalculationService()
    
    @pytest.fixture
    def large_nav_fund(self, db_session):
        """Create a fund with many events for performance testing."""
        from tests.factories import set_session
        set_session(db_session)
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        fund = FundFactory(
            investment_company=company,
            entity=entity,
            tracking_type=FundType.NAV_BASED
        )
        
        # Create 100 unit purchase events
        for i in range(100):
            event = FundEvent(
                fund_id=fund.id,
                event_type=EventType.UNIT_PURCHASE,
                event_date=date(2024, 1, 1) + timedelta(days=i),
                units_purchased=10,
                unit_price=10.0 + (i * 0.1),
                brokerage_fee=5.0
            )
            db_session.add(event)
        
        # Create 50 unit sale events
        for i in range(50):
            event = FundEvent(
                fund_id=fund.id,
                event_type=EventType.UNIT_SALE,
                event_date=date(2024, 6, 1) + timedelta(days=i),
                units_sold=5,
                unit_price=15.0 + (i * 0.1),
                brokerage_fee=3.0
            )
            db_session.add(event)
        
        db_session.commit()
        return fund
    
    def test_incremental_update_performance(self, service, large_nav_fund, db_session):
        """Test that incremental updates maintain O(1) performance."""
        import time
        
        # Create a new event at the end of the timeline
        new_event = FundEvent(
            fund_id=large_nav_fund.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date(2024, 8, 1),  # After all existing events
            units_purchased=20,
            unit_price=12.0,
            brokerage_fee=5.0
        )
        db_session.add(new_event)
        db_session.flush()
        
        # Measure incremental update time
        start_time = time.time()
        service.update_capital_chain_incrementally(large_nav_fund, new_event, db_session)
        incremental_time = time.time() - start_time
        
        # The incremental update should be fast (O(1)) even with 150 events
        assert incremental_time < 0.1  # Should complete in under 100ms
        
        # Verify the update worked correctly
        assert new_event.units_owned > 0  # Should have some units
        assert new_event.current_equity_balance > 0
    
    def test_cache_effectiveness(self, service, large_nav_fund, db_session):
        """Test that caching improves performance for repeated operations."""
        import time
        
        # Create a test event
        event = FundEvent(
            fund_id=large_nav_fund.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=date(2024, 7, 1),
            units_purchased=10,
            unit_price=20.0,
            brokerage_fee=5.0
        )
        db_session.add(event)
        db_session.flush()
        
        # First update (cache miss)
        start_time = time.time()
        service.update_capital_chain_incrementally(large_nav_fund, event, db_session)
        first_update_time = time.time() - start_time
        
        # Second update (cache hit)
        start_time = time.time()
        service.update_capital_chain_incrementally(large_nav_fund, event, db_session)
        second_update_time = time.time() - start_time
        
        # Second update should be faster due to caching
        assert second_update_time < first_update_time
