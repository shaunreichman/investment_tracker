"""
Test Event Consumption System.

This module tests the event consumption architecture including:
- EventBus functionality
- EventConsumer base class
- Specific event handlers
- Async processing capabilities
"""

import pytest
from datetime import date
from decimal import Decimal
from unittest.mock import Mock, patch

from src.fund.events.consumption import EventBus, EventConsumer, AsyncEventProcessor
from src.fund.events.consumption.handlers import TaxStatementEventHandler, CompanyRecordEventHandler
from src.fund.events.domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    UnitsChangedEvent
)


class TestEventBus:
    """Test the EventBus functionality."""
    
    def test_event_bus_initialization(self):
        """Test that EventBus initializes correctly."""
        bus = EventBus()
        
        assert bus._subscriptions == {}
        assert bus._consumers == {}
        assert bus._stats['events_published'] == 0
        assert bus._stats['events_processed'] == 0
    
    def test_subscribe_function(self):
        """Test subscribing a function to an event type."""
        bus = EventBus()
        
        def test_handler(event):
            pass
        
        bus.subscribe(EquityBalanceChangedEvent, test_handler)
        
        assert test_handler in bus._subscriptions[EquityBalanceChangedEvent]
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 1
    
    def test_subscribe_consumer_instance(self):
        """Test subscribing a consumer instance to an event type."""
        bus = EventBus()
        
        handler = TaxStatementEventHandler()
        bus.subscribe_consumer(EquityBalanceChangedEvent, handler)
        
        assert handler in bus._consumers[EquityBalanceChangedEvent]
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 1
    
    def test_publish_event_to_function_subscriber(self):
        """Test publishing an event to function subscribers."""
        bus = EventBus()
        
        events_received = []
        
        def test_handler(event):
            events_received.append(event)
        
        bus.subscribe(EquityBalanceChangedEvent, test_handler)
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        bus.publish(event)
        
        assert len(events_received) == 1
        assert events_received[0] == event
        assert bus._stats['events_published'] == 1
        assert bus._stats['events_processed'] == 1
    
    def test_publish_event_to_consumer_instance(self):
        """Test publishing an event to consumer instances."""
        bus = EventBus()
        
        handler = TaxStatementEventHandler()
        bus.subscribe_consumer(EquityBalanceChangedEvent, handler)
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        bus.publish(event)
        
        assert bus._stats['events_published'] == 1
        assert bus._stats['events_processed'] == 1
        assert handler.processed_count == 1
    
    def test_publish_event_with_no_subscribers(self):
        """Test publishing an event when there are no subscribers."""
        bus = EventBus()
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        bus.publish(event)
        
        assert bus._stats['events_published'] == 1
        assert bus._stats['events_processed'] == 0
    
    def test_unsubscribe_function(self):
        """Test unsubscribing a function from an event type."""
        bus = EventBus()
        
        def test_handler(event):
            pass
        
        bus.subscribe(EquityBalanceChangedEvent, test_handler)
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 1
        
        bus.unsubscribe(EquityBalanceChangedEvent, test_handler)
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 0
    
    def test_unsubscribe_consumer_instance(self):
        """Test unsubscribing a consumer instance from an event type."""
        bus = EventBus()
        
        handler = TaxStatementEventHandler()
        bus.subscribe_consumer(EquityBalanceChangedEvent, handler)
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 1
        
        bus.unsubscribe_consumer(EquityBalanceChangedEvent, handler)
        assert bus.get_subscription_count(EquityBalanceChangedEvent) == 0
    
    def test_get_stats(self):
        """Test getting event bus statistics."""
        bus = EventBus()
        
        stats = bus.get_stats()
        
        assert 'events_published' in stats
        assert 'events_processed' in stats
        assert 'consumer_errors' in stats
        assert 'last_event_time' in stats
    
    def test_list_subscribers(self):
        """Test listing subscribers for event types."""
        bus = EventBus()
        
        def test_handler(event):
            pass
        
        handler = TaxStatementEventHandler()
        
        bus.subscribe(EquityBalanceChangedEvent, test_handler)
        bus.subscribe_consumer(EquityBalanceChangedEvent, handler)
        
        subscribers = bus.list_subscribers()
        
        assert 'EquityBalanceChangedEvent' in subscribers
        assert 'function:test_handler' in subscribers['EquityBalanceChangedEvent']
        assert 'instance:TaxStatementEventHandler' in subscribers['EquityBalanceChangedEvent']


class TestEventConsumer:
    """Test the EventConsumer base class."""
    
    def test_event_consumer_initialization(self):
        """Test that EventConsumer initializes correctly."""
        consumer = Mock(spec=EventConsumer)
        consumer.name = "TestConsumer"
        consumer.event_types = [EquityBalanceChangedEvent]
        consumer.enabled = True
        consumer.processed_count = 0
        
        assert consumer.name == "TestConsumer"
        assert consumer.event_types == [EquityBalanceChangedEvent]
        assert consumer.enabled is True
        assert consumer.processed_count == 0
    
    def test_can_handle_event(self):
        """Test that EventConsumer can determine if it can handle an event."""
        consumer = Mock(spec=EventConsumer)
        consumer.enabled = True
        consumer.event_types = [EquityBalanceChangedEvent]
        consumer.can_handle.return_value = True
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        assert consumer.can_handle(event) is True
    
    def test_cannot_handle_disabled_consumer(self):
        """Test that disabled consumers cannot handle events."""
        consumer = Mock(spec=EventConsumer)
        consumer.enabled = False
        consumer.event_types = [EquityBalanceChangedEvent]
        consumer.can_handle.return_value = False
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        assert consumer.can_handle(event) is False
    
    def test_can_handle_any_event_type(self):
        """Test that consumers with no event types can handle any event."""
        consumer = Mock(spec=EventConsumer)
        consumer.enabled = True
        consumer.event_types = []
        consumer.can_handle.return_value = True
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        assert consumer.can_handle(event) is True


class TestTaxStatementEventHandler:
    """Test the TaxStatementEventHandler."""
    
    def test_tax_statement_handler_initialization(self):
        """Test that TaxStatementEventHandler initializes correctly."""
        handler = TaxStatementEventHandler()
        
        assert handler.name == "TaxStatementEventHandler"
        assert EquityBalanceChangedEvent in handler.event_types
        assert DistributionRecordedEvent in handler.event_types
        assert NAVUpdatedEvent in handler.event_types
        assert handler.enabled is True
    
    def test_can_handle_equity_balance_event(self):
        """Test that TaxStatementEventHandler can handle equity balance events."""
        handler = TaxStatementEventHandler()
        
        event = EquityBalanceChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_balance=Decimal('100000.0'),
            new_balance=Decimal('150000.0'),
            change_reason="Test change"
        )
        
        assert handler.can_handle(event) is True
    
    def test_can_handle_distribution_event(self):
        """Test that TaxStatementEventHandler can handle distribution events."""
        handler = TaxStatementEventHandler()
        
        event = DistributionRecordedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            distribution_type="income",
            amount=Decimal('50000.0'),
            tax_withheld=Decimal('7500.0')
        )
        
        assert handler.can_handle(event) is True
    
    def test_cannot_handle_units_event(self):
        """Test that TaxStatementEventHandler cannot handle units events."""
        handler = TaxStatementEventHandler()
        
        event = UnitsChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_units=Decimal('1000.0'),
            new_units=Decimal('1100.0'),
            change_reason="Test change"
        )
        
        assert handler.can_handle(event) is False


class TestCompanyRecordEventHandler:
    """Test the CompanyRecordEventHandler."""
    
    def test_company_record_handler_initialization(self):
        """Test that CompanyRecordEventHandler initializes correctly."""
        handler = CompanyRecordEventHandler()
        
        assert handler.name == "CompanyRecordEventHandler"
        assert EquityBalanceChangedEvent in handler.event_types
        assert DistributionRecordedEvent in handler.event_types
        assert NAVUpdatedEvent in handler.event_types
        assert UnitsChangedEvent in handler.event_types
        assert handler.enabled is True
    
    def test_can_handle_units_event(self):
        """Test that CompanyRecordEventHandler can handle units events."""
        handler = CompanyRecordEventHandler()
        
        event = UnitsChangedEvent(
            fund_id=1,
            event_date=date(2024, 1, 15),
            old_units=Decimal('1000.0'),
            new_units=Decimal('1100.0'),
            change_reason="Test change"
        )
        
        assert handler.can_handle(event) is True


class TestAsyncEventProcessor:
    """Test the AsyncEventProcessor."""
    
    def test_async_processor_initialization(self):
        """Test that AsyncEventProcessor initializes correctly."""
        processor = AsyncEventProcessor(max_workers=2)
        
        assert processor.max_workers == 2
        assert processor.use_process_pool is False
        assert processor._running is False
        assert len(processor._workers) == 0
    
    def test_async_processor_context_manager(self):
        """Test AsyncEventProcessor as a context manager."""
        with AsyncEventProcessor(max_workers=1) as processor:
            assert processor._running is True
            assert len(processor._workers) == 1
        
        assert processor._running is False
    
    def test_async_processor_start_stop(self):
        """Test starting and stopping the AsyncEventProcessor."""
        processor = AsyncEventProcessor(max_workers=1)
        
        processor.start()
        assert processor._running is True
        assert len(processor._workers) == 1
        
        processor.stop()
        assert processor._running is False
