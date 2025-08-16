"""
Fund Event Model.

This module provides the FundEvent model class,
representing events that occur within funds.
"""

from typing import Optional, List
from datetime import date, datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, JSON, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums import EventType, DistributionType, FundType


class FundEvent(Base):
    """Model representing a fund event (capital call, distribution, NAV update, etc.).
    
    Responsibilities:
    - Data persistence and relationships
    - Basic validation and constraints
    - Event record keeping
    
    Business Logic: Handled by fund event services through orchestrator
    Calculations: Managed by calculation services
    Status Updates: Coordinated by status services
    """
    
    __tablename__ = 'fund_events'
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False, index=True)  # (SYSTEM) link to fund
    
    # Event details
    event_type = Column(Enum(EventType), nullable=False, index=True)  # (SYSTEM) type of fund event
    event_date = Column(Date, nullable=False, index=True)  # (MANUAL) date when event occurred
    amount = Column(Float, nullable=False)  # (MANUAL) event amount (positive for calls, negative for returns)
    description = Column(Text)  # (MANUAL) description of the event
    reference_number = Column(String(255))  # (MANUAL) external reference number
    
    # NAV-specific fields (for NAV_BASED funds)
    nav_per_unit = Column(Float, nullable=True)  # (MANUAL) NAV per unit for NAV update events
    units_change = Column(Float, nullable=True)  # (MANUAL) change in units for NAV events
    
    # Distribution-specific fields
    distribution_type = Column(Enum(DistributionType), nullable=True)  # (MANUAL) type of distribution if applicable
    tax_withholding = Column(Float, nullable=True)  # (MANUAL) tax withholding amount if applicable
    
    # Metadata
    created_at = Column(String(255), nullable=True)  # (SYSTEM) timestamp when record was created
    updated_at = Column(String(255), nullable=True)  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    fund = relationship("Fund", back_populates="fund_events")
    cash_flows = relationship("FundEventCashFlow", back_populates="fund_event", cascade="all, delete-orphan")
    
    # Performance indexes
    __table_args__ = (
        Index('idx_fund_events_fund_id', 'fund_id'),
        Index('idx_fund_events_event_type', 'event_type'),
        Index('idx_fund_events_event_date', 'event_date'),
        Index('idx_fund_events_fund_id_event_date', 'fund_id', 'event_date'),
        {'postgresql_using': 'btree'},  # Use B-tree indexes for optimal performance
    )
    
    def __repr__(self) -> str:
        return (
            f"<FundEvent(id={self.id}, fund_id={self.fund_id}, "
            f"type={self.event_type.value}, date={self.event_date}, "
            f"amount={self.amount})>"
        )
    
    def validate_basic_constraints(self) -> bool:
        """Basic data validation only.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.fund_id:
            raise ValueError("Fund ID is required")
        
        if not self.event_type:
            raise ValueError("Event type is required")
        
        if not self.event_date:
            raise ValueError("Event date is required")
        
        if self.amount is None:
            raise ValueError("Amount is required")
        
        # Validate NAV-specific fields
        if self.event_type == EventType.NAV_UPDATE:
            if self.nav_per_unit is None or self.nav_per_unit <= 0:
                raise ValueError("NAV per unit must be positive for NAV update events")
            if self.units_change is None:
                raise ValueError("Units change is required for NAV update events")
        
        # Validate distribution-specific fields
        if self.event_type == EventType.DISTRIBUTION:
            if not self.distribution_type:
                raise ValueError("Distribution type is required for distribution events")
            if self.tax_withholding is not None and self.tax_withholding < 0:
                raise ValueError("Tax withholding cannot be negative")
        
        return True
    
    def validate_fund_type_compatibility(self, fund_tracking_type: FundType) -> bool:
        """Validate that event is compatible with fund tracking type.
        
        Args:
            fund_tracking_type: The tracking type of the fund
            
        Returns:
            bool: True if compatible
            
        Raises:
            ValueError: If event is incompatible with fund type
        """
        if fund_tracking_type == FundType.NAV_BASED:
            if self.event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]:
                raise ValueError(f"{self.event_type.value} events are not applicable for NAV-based funds")
        
        elif fund_tracking_type == FundType.COST_BASED:
            if self.event_type == EventType.NAV_UPDATE:
                raise ValueError("NAV update events are not applicable for cost-based funds")
        
        return True
    
    def is_capital_inflow(self) -> bool:
        """Check if event represents capital inflow to the fund.
        
        Returns:
            bool: True if capital inflow event
        """
        return self.event_type in [EventType.CAPITAL_CALL, EventType.NAV_UPDATE]
    
    def is_capital_outflow(self) -> bool:
        """Check if event represents capital outflow from the fund.
        
        Returns:
            bool: True if capital outflow event
        """
        return self.event_type in [EventType.RETURN_OF_CAPITAL, EventType.DISTRIBUTION]
    
    def get_effective_amount(self) -> float:
        """Get the effective amount for calculations (positive for inflows, negative for outflows).
        
        Returns:
            float: Effective amount for calculations
        """
        if self.is_capital_inflow():
            return abs(self.amount)
        else:
            return -abs(self.amount)
