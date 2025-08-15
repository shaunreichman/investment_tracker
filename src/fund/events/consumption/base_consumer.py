"""
Base Event Consumer.

This module provides the base class for all event consumers in the system.
Event consumers handle domain events and perform dependent updates.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import logging
from datetime import datetime

from ..domain.base_event import FundDomainEvent

logger = logging.getLogger(__name__)


class EventConsumer(ABC):
    """
    Base class for all event consumers.
    
    Event consumers handle domain events and perform dependent updates
    to maintain system consistency. Each consumer should handle one
    specific type of event and perform the necessary updates.
    
    Attributes:
        name (str): Human-readable name for this consumer
        event_types (list): List of event types this consumer handles
        enabled (bool): Whether this consumer is currently enabled
        last_processed (datetime): When this consumer last processed an event
        processed_count (int): Total number of events processed by this consumer
    """
    
    def __init__(self, name: str, event_types: list = None):
        """
        Initialize the event consumer.
        
        Args:
            name: Human-readable name for this consumer
            event_types: List of event types this consumer handles
        """
        self.name = name
        self.event_types = event_types or []
        self.enabled = True
        self.last_processed: Optional[datetime] = None
        self.processed_count = 0
        
        logger.info(f"Initialized event consumer: {name}")
    
    @abstractmethod
    def handle_event(self, event: FundDomainEvent) -> None:
        """
        Handle a domain event.
        
        This method must be implemented by subclasses to define
        how they process specific types of events.
        
        Args:
            event: The domain event to handle
        """
        pass
    
    def can_handle(self, event: FundDomainEvent) -> bool:
        """
        Check if this consumer can handle a specific event.
        
        Args:
            event: The domain event to check
            
        Returns:
            True if this consumer can handle the event, False otherwise
        """
        if not self.enabled:
            return False
        
        if not self.event_types:
            return True  # Can handle any event type if none specified
        
        return type(event) in self.event_types
    
    def process_event(self, event: FundDomainEvent) -> bool:
        """
        Process an event if this consumer can handle it.
        
        Args:
            event: The domain event to process
            
        Returns:
            True if the event was processed, False otherwise
        """
        if not self.can_handle(event):
            return False
        
        try:
            logger.debug(f"Consumer {self.name} processing event: {type(event).__name__}")
            
            # Process the event
            self.handle_event(event)
            
            # Update statistics
            self.last_processed = datetime.now()
            self.processed_count += 1
            
            logger.debug(f"Consumer {self.name} successfully processed event: {type(event).__name__}")
            return True
            
        except Exception as e:
            logger.error(f"Error in consumer {self.name} processing event {type(event).__name__}: {e}")
            raise
    
    def enable(self) -> None:
        """Enable this consumer."""
        self.enabled = True
        logger.info(f"Enabled event consumer: {self.name}")
    
    def disable(self) -> None:
        """Disable this consumer."""
        self.enabled = False
        logger.info(f"Disabled event consumer: {self.name}")
    
    def get_stats(self) -> dict:
        """
        Get consumer statistics.
        
        Returns:
            Dictionary with consumer statistics
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'event_types': [et.__name__ for et in self.event_types],
            'last_processed': self.last_processed.isoformat() if self.last_processed else None,
            'processed_count': self.processed_count
        }
    
    def reset_stats(self) -> None:
        """Reset consumer statistics."""
        self.last_processed = None
        self.processed_count = 0
        logger.info(f"Reset statistics for consumer: {self.name}")
    
    def __repr__(self) -> str:
        """String representation of the consumer."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"enabled={self.enabled}, "
            f"processed_count={self.processed_count})"
        )
