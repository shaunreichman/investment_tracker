"""
Base Event Consumer.

This module provides the base class for all event consumers in the system.
Event consumers handle domain events and perform dependent updates.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
import logging
from datetime import datetime
from sqlalchemy.orm import Session

from src.fund.events.domain.base_event import FundDomainEvent

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
        session (Session): Database session for database operations
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
        self.session: Optional[Session] = None
        
        logger.info(f"Initialized event consumer: {name}")
    
    def set_session(self, session: Session) -> None:
        """
        Set the database session for this consumer.
        
        Args:
            session: Database session to use for operations
        """
        self.session = session
        logger.debug(f"Set session for consumer {self.name}")
    
    def get_session(self) -> Optional[Session]:
        """
        Get the current database session.
        
        Returns:
            Database session if set, None otherwise
        """
        return self.session
    
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
            self.processed_count += 1
            self.last_processed = datetime.now()
            
            logger.debug(f"Consumer {self.name} successfully processed event: {type(event).__name__}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing event in consumer {self.name}: {e}")
            raise
    
    def enable(self) -> None:
        """Enable this consumer."""
        self.enabled = True
        logger.info(f"Enabled consumer: {self.name}")
    
    def disable(self) -> None:
        """Disable this consumer."""
        self.enabled = False
        logger.info(f"Disabled consumer: {self.name}")
    
    def reset_stats(self) -> None:
        """Reset processing statistics."""
        self.processed_count = 0
        self.last_processed = None
        logger.debug(f"Reset statistics for consumer: {self.name}")
    
    def get_stats(self) -> dict:
        """
        Get consumer statistics.
        
        Returns:
            Dictionary with consumer statistics
        """
        return {
            'name': self.name,
            'enabled': self.enabled,
            'processed_count': self.processed_count,
            'last_processed': self.last_processed.isoformat() if self.last_processed else None,
            'event_types': [et.__name__ for et in self.event_types]
        }
    
    def __repr__(self) -> str:
        """String representation of the consumer."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"enabled={self.enabled}, "
            f"processed_count={self.processed_count})"
        )
