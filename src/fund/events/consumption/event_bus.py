"""
Event Bus System.

This module provides the centralized event routing and subscription system
that enables loose coupling between components through domain events.
"""

from typing import Dict, List, Callable, Any, Optional, Type
from collections import defaultdict
import logging
from datetime import datetime

from ..domain.base_event import FundDomainEvent
from ..domain import (
    EquityBalanceChangedEvent,
    DistributionRecordedEvent,
    NAVUpdatedEvent,
    UnitsChangedEvent,
    TaxStatementUpdatedEvent
)

logger = logging.getLogger(__name__)


class EventBus:
    """
    Centralized event routing and subscription system.
    
    This class manages:
    1. Event subscriptions - components can subscribe to specific event types
    2. Event routing - events are routed to all registered subscribers
    3. Event processing - synchronous and asynchronous event handling
    4. Error handling - graceful handling of consumer failures
    """
    
    def __init__(self):
        """Initialize the event bus."""
        # Map event types to lists of consumer functions
        self._subscriptions: Dict[Type[FundDomainEvent], List[Callable]] = defaultdict(list)
        
        # Map event types to consumer instances (for stateful consumers)
        self._consumers: Dict[Type[FundDomainEvent], List[Any]] = defaultdict(list)
        
        # Event processing statistics
        self._stats = {
            'events_published': 0,
            'events_processed': 0,
            'consumer_errors': 0,
            'last_event_time': None
        }
    
    def subscribe(self, event_type: Type[FundDomainEvent], consumer: Callable) -> None:
        """
        Subscribe a consumer function to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            consumer: Function to call when events of this type are published
        """
        if consumer not in self._subscriptions[event_type]:
            self._subscriptions[event_type].append(consumer)
            logger.info(f"Subscribed consumer {consumer.__name__} to {event_type.__name__}")
    
    def subscribe_consumer(self, event_type: Type[FundDomainEvent], consumer_instance: Any) -> None:
        """
        Subscribe a consumer instance to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            consumer_instance: Consumer instance with handle_event method
        """
        if hasattr(consumer_instance, 'handle_event'):
            if consumer_instance not in self._consumers[event_type]:
                self._consumers[event_type].append(consumer_instance)
                logger.info(f"Subscribed consumer instance {type(consumer_instance).__name__} to {event_type.__name__}")
        else:
            raise ValueError(f"Consumer instance must have 'handle_event' method")
    
    def unsubscribe(self, event_type: Type[FundDomainEvent], consumer: Callable) -> None:
        """
        Unsubscribe a consumer function from a specific event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            consumer: Function to unsubscribe
        """
        if consumer in self._subscriptions[event_type]:
            self._subscriptions[event_type].remove(consumer)
            logger.info(f"Unsubscribed consumer {consumer.__name__} from {event_type.__name__}")
    
    def unsubscribe_consumer(self, event_type: Type[FundDomainEvent], consumer_instance: Any) -> None:
        """
        Unsubscribe a consumer instance from a specific event type.
        
        Args:
            event_type: The type of event to unsubscribe from
            consumer_instance: Consumer instance to unsubscribe
        """
        if consumer_instance in self._consumers[event_type]:
            self._consumers[event_type].remove(consumer_instance)
            logger.info(f"Unsubscribed consumer instance {type(consumer_instance).__name__} from {event_type.__name__}")
    
    def publish(self, event: FundDomainEvent) -> None:
        """
        Publish an event to all subscribed consumers.
        
        Args:
            event: The domain event to publish
        """
        event_type = type(event)
        self._stats['events_published'] += 1
        self._stats['last_event_time'] = datetime.now()
        
        logger.debug(f"Publishing {event_type.__name__} event: {event.event_id}")
        
        # Process function-based consumers
        for consumer_func in self._subscriptions[event_type]:
            try:
                consumer_func(event)
                self._stats['events_processed'] += 1
            except Exception as e:
                self._stats['consumer_errors'] += 1
                logger.error(f"Error in consumer function {consumer_func.__name__}: {e}")
        
        # Process instance-based consumers
        for consumer_instance in self._consumers[event_type]:
            try:
                consumer_instance.process_event(event)
                self._stats['events_processed'] += 1
            except Exception as e:
                self._stats['consumer_errors'] += 1
                logger.error(f"Error in consumer instance {type(consumer_instance).__name__}: {e}")
        
        logger.debug(f"Published {event_type.__name__} event to {len(self._subscriptions[event_type]) + len(self._consumers[event_type])} consumers")
    
    def publish_batch(self, events: List[FundDomainEvent]) -> None:
        """
        Publish multiple events in batch.
        
        Args:
            events: List of domain events to publish
        """
        for event in events:
            self.publish(event)
    
    def get_subscription_count(self, event_type: Type[FundDomainEvent]) -> int:
        """
        Get the number of subscribers for a specific event type.
        
        Args:
            event_type: The event type to check
            
        Returns:
            Number of subscribers
        """
        return len(self._subscriptions[event_type]) + len(self._consumers[event_type])
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get event bus statistics.
        
        Returns:
            Dictionary with event processing statistics
        """
        return self._stats.copy()
    
    def clear_subscriptions(self) -> None:
        """Clear all event subscriptions."""
        self._subscriptions.clear()
        self._consumers.clear()
        logger.info("Cleared all event subscriptions")
    
    def list_subscribers(self, event_type: Optional[Type[FundDomainEvent]] = None) -> Dict[str, List[str]]:
        """
        List all subscribers for specified event type or all event types.
        
        Args:
            event_type: Specific event type to list, or None for all
            
        Returns:
            Dictionary mapping event types to lists of subscriber names
        """
        result = {}
        
        if event_type:
            event_types = [event_type]
        else:
            event_types = list(self._subscriptions.keys()) + list(self._consumers.keys())
        
        for et in event_types:
            subscribers = []
            
            # Function-based subscribers
            for func in self._subscriptions[et]:
                subscribers.append(f"function:{func.__name__}")
            
            # Instance-based subscribers
            for instance in self._consumers[et]:
                subscribers.append(f"instance:{type(instance).__name__}")
            
            result[et.__name__] = subscribers
        
        return result


# Global event bus instance
event_bus = EventBus()
