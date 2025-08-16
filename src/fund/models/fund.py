"""
Fund Model.

This module provides the Fund model class,
representing investment funds in the system.
"""

from typing import Optional, List
from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums import FundType, FundStatus, GroupType


class Fund(Base):
    """Model representing an investment fund.
    
    Responsibilities:
    - Data persistence and relationships
    - Basic validation and constraints
    - Orchestrator integration for business logic
    - Domain event publishing
    
    Business Logic: Delegated to services through orchestrator
    Calculations: Handled by FundCalculationService
    Status Updates: Managed by FundStatusService
    Event Processing: Coordinated by FundUpdateOrchestrator
    """
    
    __tablename__ = 'funds'
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (MANUAL) foreign key to investment company
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)  # (MANUAL) foreign key to entity
    
    # Basic fund information
    name = Column(String(255), nullable=False)  # (MANUAL) fund name
    fund_type = Column(String(100))  # (MANUAL) type of fund (e.g., 'Private Equity', 'Venture Capital')
    tracking_type = Column(Enum(FundType), nullable=False, default=FundType.NAV_BASED)  # (MANUAL) NAV_BASED or COST_BASED
    
    # Investment tracking fields (common)
    commitment_amount = Column(Float, nullable=True)  # (MANUAL) total amount committed to the fund
    current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital movements
    average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance
    expected_irr = Column(Float)  # (MANUAL) expected IRR as percentage
    expected_duration_months = Column(Integer)  # (MANUAL) expected fund duration in months
    
    # IRR storage fields (CALCULATED)
    irr_gross = Column(Float, nullable=True)  # (CALCULATED) Gross IRR when realized/completed
    irr_after_tax = Column(Float, nullable=True)  # (CALCULATED) After-tax IRR when completed
    irr_real = Column(Float, nullable=True)  # (CALCULATED) Real IRR when completed
    
    # NAV-based fund specific fields (CALCULATED)
    current_units = Column(Float, default=0.0)  # (CALCULATED) current number of units owned
    current_unit_price = Column(Float, default=0.0)  # (CALCULATED) current unit price from latest NAV update
    current_nav_total = Column(Float, default=0.0)  # (CALCULATED) current NAV total (units * unit price)
    
    # Cost-based fund specific fields (CALCULATED)
    total_cost_basis = Column(Float, default=0.0)  # (CALCULATED) total cost basis for cost-based funds
    
    # Status and metadata
    status = Column(Enum(FundStatus), default=FundStatus.ACTIVE)  # (CALCULATED) fund status (ACTIVE/REALIZED/COMPLETED)
    end_date = Column(Date, nullable=True)  # (CALCULATED) fund end date based on last equity/distribution event after equity balance reached zero
    description = Column(Text)  # (MANUAL) fund description
    currency = Column(String(10), default="AUD")  # (MANUAL) currency code for the fund
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="funds", lazy='selectin')
    entity = relationship("Entity", back_populates="funds", lazy='selectin')
    fund_events = relationship("FundEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    tax_statements = relationship("TaxStatement", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    domain_events = relationship("DomainEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    
    # Critical indexes for production performance
    __table_args__ = (
        # Foreign key indexes for JOIN performance
        Index('idx_funds_investment_company_id', 'investment_company_id'),
        Index('idx_funds_entity_id', 'entity_id'),
        # Composite indexes for common query patterns
        Index('idx_funds_status_tracking_type', 'status', 'tracking_type'),
        Index('idx_funds_equity_status', 'current_equity_balance', 'status'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Fund(id={self.id}, name='{self.name}', "
            f"tracking_type={self.tracking_type.value}, status={self.status.value})>"
        )
    
    def validate_basic_constraints(self) -> bool:
        """Basic data validation only.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if not self.name:
            raise ValueError("Fund name is required")
        
        if not self.investment_company_id:
            raise ValueError("Investment company ID is required")
        
        if not self.entity_id:
            raise ValueError("Entity ID is required")
        
        if not self.tracking_type:
            raise ValueError("Tracking type is required")
        
        if self.currency and len(self.currency) != 3:
            raise ValueError("Currency must be 3 characters (ISO-4217)")
        
        if self.expected_irr is not None and (self.expected_irr < 0 or self.expected_irr > 1000):
            raise ValueError("Expected IRR must be between 0 and 1000")
        
        if self.expected_duration_months is not None and self.expected_duration_months <= 0:
            raise ValueError("Expected duration must be positive")
        
        return True
    
    def validate_tracking_type_constraints(self) -> bool:
        """Validate tracking type specific constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.tracking_type == FundType.NAV_BASED:
            # NAV-based funds should not have cost basis
            if self.total_cost_basis and self.total_cost_basis != 0:
                raise ValueError("NAV-based funds should not have cost basis")
        
        elif self.tracking_type == FundType.COST_BASED:
            # Cost-based funds should not have NAV fields
            if self.current_units and self.current_units != 0:
                raise ValueError("Cost-based funds should not have units")
            if self.current_unit_price and self.current_unit_price != 0:
                raise ValueError("Cost-based funds should not have unit price")
            if self.current_nav_total and self.current_nav_total != 0:
                raise ValueError("Cost-based funds should not have NAV total")
        
        return True
    
    def is_nav_based(self) -> bool:
        """Check if fund is NAV-based.
        
        Returns:
            bool: True if NAV-based fund
        """
        return self.tracking_type == FundType.NAV_BASED
    
    def is_cost_based(self) -> bool:
        """Check if fund is cost-based.
        
        Returns:
            bool: True if cost-based fund
        """
        return self.tracking_type == FundType.COST_BASED
    
    def is_active(self) -> bool:
        """Check if fund is active.
        
        Returns:
            bool: True if fund is active
        """
        return self.status == FundStatus.ACTIVE
    
    def is_completed(self) -> bool:
        """Check if fund is completed.
        
        Returns:
            bool: True if fund is completed
        """
        return self.status == FundStatus.COMPLETED
    
    def is_realized(self) -> bool:
        """Check if fund is realized.
        
        Returns:
            bool: True if fund is realized
        """
        return self.status == FundStatus.REALIZED
    
    def has_equity_balance(self) -> bool:
        """Check if fund has equity balance.
        
        Returns:
            bool: True if fund has equity balance
        """
        return self.current_equity_balance > 0
    
    def get_commitment_utilization(self) -> float:
        """Get commitment utilization percentage.
        
        Returns:
            float: Commitment utilization as percentage (0-100)
        """
        if not self.commitment_amount or self.commitment_amount <= 0:
            return 0.0
        
        return (self.current_equity_balance / self.commitment_amount) * 100
    
    def get_remaining_commitment(self) -> float:
        """Get remaining commitment amount.
        
        Returns:
            float: Remaining commitment amount
        """
        if not self.commitment_amount:
            return 0.0
        
        return max(0, self.commitment_amount - self.current_equity_balance)
