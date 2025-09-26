"""
Fund Model.

This module provides the Fund model class, representing investment funds in the system.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_enums import FundTrackingType, FundStatus, FundTaxStatementFinancialYearType, FundInvestmentType
from src.shared.enums.shared_enums import Currency, Country


class Fund(Base):
    """
    Model representing an investment fund.
    """
    
    __tablename__ = 'funds'
    
    # Primary key and relationships
    id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
    investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (MANUAL) foreign key to investment company
    entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)  # (MANUAL) foreign key to entity
    
    # Basic fund information
    name = Column(String(255), nullable=False)  # (MANUAL) fund name
    fund_investment_type = Column(Enum(FundInvestmentType), nullable=False, default=FundInvestmentType.PRIVATE_EQUITY)  # (MANUAL) type of fund (e.g., 'Private Equity', 'Venture Capital')
    tracking_type = Column(Enum(FundTrackingType), nullable=False, default=FundTrackingType.NAV_BASED)  # (MANUAL) NAV_BASED or COST_BASED
    description = Column(Text, nullable=True)  # (MANUAL) fund description
    currency = Column(Enum(Currency), nullable=False, default=Currency.AUD)  # (MANUAL) currency code for the fund
    tax_jurisdiction = Column(Enum(Country), nullable=False, default=Country.AU)  # (MANUAL) tax jurisdiction for the fund
    tax_statement_financial_year_type = Column(Enum(FundTaxStatementFinancialYearType), nullable=False)  # (CALCULATED) financial year type (eg. CALENDAR_YEAR or HALF_YEAR)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated

    # Expected information
    expected_irr = Column(Float, nullable=True)  # (MANUAL) expected IRR as percentage
    expected_duration_months = Column(Integer, nullable=True)  # (MANUAL) expected fund duration in months
    
    # Investment tracking fields (common)
    commitment_amount = Column(Float, nullable=True)  # (MANUAL) total amount committed to the fund
    current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital movements
    average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance
    
    # IRR storage fields (CALCULATED)
    completed_irr_gross = Column(Float, nullable=True)  # (CALCULATED) Completed gross IRR when realized/completed
    completed_irr_after_tax = Column(Float, nullable=True)  # (CALCULATED) Completed after-tax IRR when completed
    completed_irr_real = Column(Float, nullable=True)  # (CALCULATED) Completed real IRR when completed

    # Profitability storage fields (CALCULATED)
    pnl = Column(Float, default=0.0)  # (CALCULATED) PNL
    realized_pnl = Column(Float, default=0.0)  # (CALCULATED) Realized PNL
    unrealized_pnl = Column(Float, default=0.0)  # (CALCULATED) Unrealized PNL
    realized_pnl_capital_gain = Column(Float, default=0.0)  # (CALCULATED) Realized Capital Gain PNL
    unrealized_pnl_capital_gain = Column(Float, default=0.0)  # (CALCULATED) Unrealized Capital Gain PNL
    realized_pnl_dividend = Column(Float, default=0.0)  # (CALCULATED) Realized Dividend PNL
    realized_pnl_interest = Column(Float, default=0.0)  # (CALCULATED) Realized Interest PNL
    realized_pnl_distribution = Column(Float, default=0.0)  # (CALCULATED) Realized Distribution PNL

    # NAV-based fund specific fields (CALCULATED)
    current_units = Column(Float, default=0.0)  # (CALCULATED) current number of units owned
    current_unit_price = Column(Float, default=0.0)  # (CALCULATED) current unit price from latest NAV update
    current_nav_total = Column(Float, default=0.0)  # (CALCULATED) current NAV total (units * unit price)
    
    # Cost-based fund specific fields (CALCULATED)
    total_cost_basis = Column(Float, default=0.0)  # (CALCULATED) total cost basis for cost-based funds
    
    # Status and metadata
    status = Column(Enum(FundStatus), default=FundStatus.ACTIVE)  # (CALCULATED) fund status (ACTIVE/REALIZED/COMPLETED)
    start_date = Column(Date, nullable=True)  # (CALCULATED) fund start date based on first capital call or unit purchase
    end_date = Column(Date, nullable=True)  # (CALCULATED) fund end date based on last equity/distribution event after equity balance reached zero
    current_duration = Column(Integer, nullable=True)  # (CALCULATED) current fund duration in months based on status
   
    # Relationships
    investment_company = relationship("InvestmentCompany", back_populates="funds", lazy='selectin')
    entity = relationship("Entity", back_populates="funds", lazy='selectin')
    fund_events = relationship("FundEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    tax_statements = relationship("FundTaxStatement", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    domain_events = relationship("DomainEvent", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')
    
    # Critical indexes for production performance
    __table_args__ = (
        # Foreign key indexes for JOIN performance
        Index('idx_funds_investment_company_id', 'investment_company_id'),
        Index('idx_funds_entity_id', 'entity_id'),
        # Composite indexes for common query patterns
        Index('idx_funds_status_tracking_type', 'status', 'tracking_type'),
        Index('idx_funds_equity_status', 'current_equity_balance', 'status'),
        Index('idx_funds_start_date', 'start_date'),
        Index('idx_funds_end_date', 'end_date'),
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
        if self.tracking_type == FundTrackingType.NAV_BASED:
            # NAV-based funds should not have cost basis
            if self.total_cost_basis and self.total_cost_basis != 0:
                raise ValueError("NAV-based funds should not have cost basis")
        
        elif self.tracking_type == FundTrackingType.COST_BASED:
            # Cost-based funds should not have NAV fields
            if self.current_units and self.current_units != 0:
                raise ValueError("Cost-based funds should not have units")
            if self.current_unit_price and self.current_unit_price != 0:
                raise ValueError("Cost-based funds should not have unit price")
            if self.current_nav_total and self.current_nav_total != 0:
                raise ValueError("Cost-based funds should not have NAV total")
        
        return True
    
    def validate_date_constraints(self) -> bool:
        """Validate date-related constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValueError("Start date cannot be after end date")
        
        if self.start_date and self.start_date > date.today():
            raise ValueError("Start date cannot be in the future")
        
        if self.end_date and self.end_date > date.today():
            raise ValueError("End date cannot be in the future")
        
        return True
    
    def validate_commitment_constraints(self) -> bool:
        """Validate commitment-related constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.commitment_amount is not None and self.commitment_amount < 0:
            raise ValueError("Commitment amount cannot be negative")
        
        if self.current_equity_balance < 0:
            raise ValueError("Current equity balance cannot be negative")
        
        if self.average_equity_balance < 0:
            raise ValueError("Average equity balance cannot be negative")
        
        return True
    
    def validate_nav_constraints(self) -> bool:
        """Validate NAV-related constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.tracking_type == FundTrackingType.NAV_BASED:
            if self.current_units < 0:
                raise ValueError("Current units cannot be negative")
            if self.current_unit_price < 0:
                raise ValueError("Current unit price cannot be negative")
            if self.current_nav_total < 0:
                raise ValueError("Current NAV total cannot be negative")
        
        return True
    
    def validate_all_constraints(self) -> bool:
        """Validate all constraints for the fund.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        self.validate_basic_constraints()
        self.validate_tracking_type_constraints()
        self.validate_date_constraints()
        self.validate_commitment_constraints()
        self.validate_nav_constraints()
        return True