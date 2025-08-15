"""
Event Consumption Integration Test.

This module tests the integration between the event consumption system
and the existing domain events to ensure they work together correctly.
"""

import pytest
from datetime import date
from decimal import Decimal

from src.fund.events.consumption import EventBus, AsyncEventProcessor
from src.fund.events.consumption.handlers import TaxStatementEventHandler, CompanyRecordEventHandler
from src.fund.events.domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    UnitsChangedEvent
)


class TestEventConsumptionIntegration:
    """Test the integration between event consumption and domain events."""
    
    def test_event_bus_with_real_handlers(self):
        """Test that the event bus works with real event handlers."""
        # Create event bus
        bus = EventBus()
        
        # Create handlers
        tax_handler = TaxStatementEventHandler()
        company_handler = CompanyRecordEventHandler()
        
        # Subscribe handlers to events
        bus.subscribe_consumer(EquityBalanceChangedEvent, tax_handler)
        bus.subscribe_consumer(EquityBalanceChangedEvent, company_handler)
        bus.subscribe_consumer(DistributionRecordedEvent, tax_handler)
        bus.subscribe_consumer(DistributionRecordedEvent, company_handler)
        bus.subscribe_consumer(NAVUpdatedEvent, tax_handler)
        bus.subscribe_consumer(NAVUpdatedEvent, company_handler)
        bus.subscribe_consumer(UnitsChangedEvent, company_handler)
        
        # Verify subscriptions
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 2
        assert bus.get_subscription_count(DistributionRecordedEvent) == 2
        assert bus.get_subscription_count(NAVUpdatedEvent) == 2
        assert bus.get_subscription_count(UnitsChangedEvent) == 1
        
        # Create and publish events
        equity_event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test equity change"
        )
        
        distribution_event = DistributionRecordedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            distribution_type="income",
            amount=Decimal('50000.0'),
            tax_withheld=Decimal('7500.0')
        )
        
        nav_event = NAVUpdatedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_nav=Decimal('10.0'),
            new_nav=Decimal('10.50'),
            change_reason="Test NAV update"
        )
        
        units_event = UnitsChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_units=Decimal('1000.0'),
            new_units=Decimal('1100.0'),
            change_reason="Test units change"
        )
        
        # Publish events
        bus.publish(equity_event)
        bus.publish(distribution_event)
        bus.publish(nav_event)
        bus.publish(units_event)
        
        # Verify event processing
        stats = bus.get_stats()
        assert stats['events_published'] == 4
        assert stats['events_processed'] == 7  # 2+2+2+1 = 7 handlers total
        
        # Verify handler statistics
        assert tax_handler.processed_count == 3  # equity, distribution, nav
        assert company_handler.processed_count == 4  # equity, distribution, nav, units
        
        # Verify no errors
        assert stats['consumer_errors'] == 0
    
    def test_event_bus_subscriber_listing(self):
        """Test that the event bus can list all subscribers correctly."""
        bus = EventBus()
        
        # Create handlers
        tax_handler = TaxStatementEventHandler()
        company_handler = CompanyRecordEventHandler()
        
        # Subscribe handlers
        bus.subscribe_consumer(EquityBalanceChangedEvent, tax_handler)
        bus.subscribe_consumer(DistributionRecordedEvent, company_handler)
        
        # List subscribers
        subscribers = bus.list_subscribers()
        
        assert 'EquityBalanceChangedEvent' in subscribers
        assert 'DistributionRecordedEvent' in subscribers
        assert 'instance:TaxStatementEventHandler' in subscribers['EquityBalanceChangedEvent']
        assert 'instance:CompanyRecordEventHandler' in subscribers['DistributionRecordedEvent']
    
    def test_event_bus_error_handling(self):
        """Test that the event bus handles consumer errors gracefully."""
        bus = EventBus()
        
        # Create a handler that will raise an error
        class ErrorHandler(TaxStatementEventHandler):
            def handle_event(self, event):
                raise ValueError("Test error")
        
        error_handler = ErrorHandler()
        bus.subscribe_consumer(EquityBalanceChangedEvent, error_handler)
        
        # Create and publish an event
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test error handling"
        )
        
        # Publish event - should not raise exception
        bus.publish(event)
        
        # Verify error was recorded
        stats = bus.get_stats()
        assert stats['events_published'] == 1
        assert stats['events_processed'] == 0  # Error handler failed
        assert stats['consumer_errors'] == 1
    
    def test_async_event_processor_basic_functionality(self):
        """Test basic AsyncEventProcessor functionality."""
        processor = AsyncEventProcessor(max_workers=1)
        
        # Test context manager
        with processor:
            assert processor._running is True
            assert len(processor._workers) == 1
            
            # Test stats
            stats = processor.get_stats()
            assert stats['running'] is True
            assert stats['worker_count'] == 1
        
        # Verify cleanup
        assert processor._running is False
    
    def test_event_consumption_workflow(self):
        """Test complete event consumption workflow."""
        # Create event bus
        bus = EventBus()
        
        # Create handlers
        tax_handler = TaxStatementEventHandler()
        company_handler = CompanyRecordEventHandler()
        
        # Subscribe handlers
        bus.subscribe_consumer(EquityBalanceChangedEvent, tax_handler)
        bus.subscribe_consumer(EquityBalanceChangedEvent, company_handler)
        
        # Create event
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Integration test"
        )
        
        # Publish event
        bus.publish(event)
        
        # Verify complete workflow
        assert bus._stats['events_published'] == 1
        assert bus._stats['events_processed'] == 2
        assert tax_handler.processed_count == 1
        assert company_handler.processed_count == 1
        assert tax_handler.last_processed is not None
        assert company_handler.last_processed is not None
        
        # Verify handler states
        assert tax_handler.enabled is True
        assert company_handler.enabled is True
        
        # Test handler statistics
        tax_stats = tax_handler.get_stats()
        company_stats = company_handler.get_stats()
        
        assert tax_stats['name'] == "TaxStatementEventHandler"
        assert company_stats['name'] == "CompanyRecordEventHandler"
        assert tax_stats['processed_count'] == 1
        assert company_stats['processed_count'] == 1
