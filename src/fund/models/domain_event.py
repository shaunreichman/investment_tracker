"""
Domain Event Model.

This module contains the DomainEvent model for tracking domain events
in the fund system. Models handle only data persistence and basic validation.
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from ...shared.base import Base


class DomainEvent(Base):
    """Model representing a domain event in the fund system.
    
    Responsibilities:
    - Data persistence and relationships
    - Basic validation and constraints
    - Event metadata storage
    
    Business Logic: Handled by event handlers and services
    Event Processing: Coordinated by event orchestrator
    """
    
    __tablename__ = 'domain_events'
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (SYSTEM) link to fund
    
    # Event metadata
    event_type = Column(String(100), nullable=False, index=True)  # (SYSTEM) type of domain event
    event_data = Column(JSON, nullable=True)  # (SYSTEM) event-specific data payload
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)  # (SYSTEM) when event occurred
    source = Column(String(100), nullable=False)  # (SYSTEM) source of the event (e.g., 'fund_model', 'service')
    
    # Event processing status
    processed = Column(String(50), default='PENDING')  # (SYSTEM) processing status: PENDING, PROCESSING, COMPLETED, FAILED
    error_message = Column(Text, nullable=True)  # (SYSTEM) error details if processing failed
    processed_at = Column(DateTime, nullable=True)  # (SYSTEM) when event was processed
    
    # Relationships
    fund = relationship("Fund", back_populates="domain_events")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_domain_events_fund_id_event_type', 'fund_id', 'event_type'),
        Index('idx_domain_events_timestamp', 'timestamp'),
        Index('idx_domain_events_processed', 'processed'),
        {'postgresql_using': 'btree'},
    )
    
    def __repr__(self) -> str:
        return (
            f"<DomainEvent(id={self.id}, fund_id={self.fund_id}, "
            f"type={self.event_type}, processed={self.processed})>"
        )
    
    def validate_basic_constraints(self) -> bool:
        """Basic data validation only.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.event_type:
            raise ValueError("Event type is required")
        
        if not self.source:
            raise ValueError("Event source is required")
        
        if self.processed not in ['PENDING', 'PROCESSING', 'COMPLETED', 'FAILED']:
            raise ValueError("Invalid processing status")
        
        return True
    
    def mark_as_processing(self) -> None:
        """Mark event as being processed."""
        self.processed = 'PROCESSING'
        self.processed_at = None
        self.error_message = None
    
    def mark_as_completed(self) -> None:
        """Mark event as successfully processed."""
        self.processed = 'COMPLETED'
        self.processed_at = datetime.now(timezone.utc)
        self.error_message = None
    
    def mark_as_failed(self, error_message: str) -> None:
        """Mark event as failed with error message."""
        self.processed = 'FAILED'
        self.processed_at = datetime.now(timezone.utc)
        self.error_message = error_message
