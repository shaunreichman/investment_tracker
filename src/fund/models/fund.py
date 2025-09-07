"""
Fund Model.

This module provides the Fund model class,
representing investment funds in the system.
"""

from typing import Optional, List, Union, Dict, Any
from datetime import date, datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums import FundType, FundStatus, GroupType
from src.fund.enums import EventType, DistributionType
from src.fund.models.fund_event import FundEvent
from src.entity.models import Entity


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
    completed_irr_gross = Column(Float, nullable=True)  # (CALCULATED) Completed gross IRR when realized/completed
    completed_irr_after_tax = Column(Float, nullable=True)  # (CALCULATED) Completed after-tax IRR when completed
    completed_irr_real = Column(Float, nullable=True)  # (CALCULATED) Completed real IRR when completed
    
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
        Index('idx_funds_start_date', 'start_date'),
        Index('idx_funds_end_date', 'end_date'),
    )
    
    def __repr__(self) -> str:
        return (
            f"<Fund(id={self.id}, name='{self.name}', "
            f"tracking_type={self.tracking_type.value}, status={self.status.value})>"
        )
    
    @classmethod
    def get_all(cls, session) -> List['Fund']:
        """Get all funds from the database.
        
        Args:
            session: Database session
            
        Returns:
            List[Fund]: List of all funds
        """
        return session.query(cls).all()
    
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
    
    def validate_irr_constraints(self) -> bool:
        """Validate IRR-related constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        for irr_field in [self.completed_irr_gross, self.completed_irr_after_tax, self.completed_irr_real]:
            if irr_field is not None and (irr_field < -100 or irr_field > 1000):
                raise ValueError("IRR values must be between -100% and 1000%")
        
        return True
    
    def validate_nav_constraints(self) -> bool:
        """Validate NAV-related constraints.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If validation fails
        """
        if self.tracking_type == FundType.NAV_BASED:
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
        self.validate_irr_constraints()
        self.validate_nav_constraints()
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
    
    def has_commitment(self) -> bool:
        """Check if fund has a commitment amount.
        
        Returns:
            bool: True if fund has commitment amount
        """
        return self.commitment_amount is not None and self.commitment_amount > 0
    
    def get_commitment_utilization(self) -> float:
        """Get commitment utilization percentage.
        
        Returns:
            float: Commitment utilization as percentage (0-100)
        """
        if not self.has_commitment():
            return 0.0
        
        return (self.current_equity_balance / self.commitment_amount) * 100
    
    def get_remaining_commitment(self) -> float:
        """Get remaining commitment amount.
        
        Returns:
            float: Remaining commitment amount
        """
        if not self.has_commitment():
            return 0.0
        
        return max(0, self.commitment_amount - self.current_equity_balance)
    
    def get_fund_duration_months(self) -> Optional[int]:
        """Get the fund duration in months.
        
        Returns:
            int or None: Duration in months if start and end dates are available
        """
        if not self.start_date or not self.end_date:
            return None
        
        # Calculate months between start and end dates
        year_diff = self.end_date.year - self.start_date.year
        month_diff = self.end_date.month - self.start_date.month
        
        total_months = year_diff * 12 + month_diff
        
        # Adjust for day of month
        if self.end_date.day < self.start_date.day:
            total_months -= 1
        
        return max(0, total_months)
    
    def get_fund_age_months(self) -> Optional[int]:
        """Get the fund age in months from start date to current date.
        
        Returns:
            int or None: Age in months if start date is available
        """
        if not self.start_date:
            return None
        
        today = date.today()
        year_diff = today.year - self.start_date.year
        month_diff = today.month - self.start_date.month
        
        total_months = year_diff * 12 + month_diff
        
        # Adjust for day of month
        if today.day < self.start_date.day:
            total_months -= 1
        
        return max(0, total_months)
    
    def calculate_and_update_current_duration(self) -> Optional[int]:
        """Calculate and update the current_duration field based on fund status.
        
        For ACTIVE funds: calculates duration from start_date to today
        For REALIZED/COMPLETED funds: calculates duration from start_date to end_date
        
        Returns:
            int or None: Calculated duration in months
        """
        if not self.start_date:
            self.current_duration = None
            return None
        
        # Determine the end date based on fund status
        if self.status in [FundStatus.REALIZED, FundStatus.COMPLETED]:
            # Use the fund's end_date for completed funds
            if not self.end_date:
                self.current_duration = None
                return None
            end_date = self.end_date
        else:
            # Use today's date for active funds
            end_date = date.today()
        
        # Calculate months between start and end dates
        year_diff = end_date.year - self.start_date.year
        month_diff = end_date.month - self.start_date.month
        
        total_months = year_diff * 12 + month_diff
        
        # Adjust for day of month
        if end_date.day < self.start_date.day:
            total_months -= 1
        
        calculated_duration = max(0, total_months)
        self.current_duration = calculated_duration
        return calculated_duration
    
    def get_expected_completion_date(self) -> Optional[date]:
        """Get the expected completion date based on start date and expected duration.
        
        Returns:
            date or None: Expected completion date if start date and duration are available
        """
        if not self.start_date or not self.expected_duration_months:
            return None
        
        # Add months to start date
        year = self.start_date.year
        month = self.start_date.month + self.expected_duration_months
        
        # Adjust year if month exceeds 12
        while month > 12:
            year += 1
            month -= 12
        
        # Create new date, handling month overflow
        try:
            return date(year, month, self.start_date.day)
        except ValueError:
            # Handle month overflow (e.g., Jan 31 + 1 month = Feb 28/29)
            last_day = (date(year, month + 1, 1) - date(year, month, 1)).days
            return date(year, month, min(self.start_date.day, last_day))
    
    # ============================================================================
    # CORE BUSINESS LOGIC METHODS - Capital Movement Operations
    # ============================================================================
    
    
    
    def add_distribution(self, event_date: date, distribution_type: 'DistributionType',
                        distribution_amount: float = None, has_withholding_tax: bool = False,
                        gross_interest_amount: float = None, net_interest_amount: float = None,
                        withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                        description: str = None, reference_number: str = None,
                        session=None) -> Union['FundEvent', tuple['FundEvent', Optional['FundEvent']]]:
        """
        Add a distribution event using the service layer.
        
        Note: This method delegates to the fund service for proper orchestration.
        For direct control, use FundService.add_distribution() instead.
        
        Args:
            event_date: Distribution date
            distribution_type: Type of distribution
            distribution_amount: Simple distribution amount (when has_withholding_tax=False)
            has_withholding_tax: Whether this distribution has withholding tax
            gross_interest_amount: Gross interest amount (when has_withholding_tax=True)
            net_interest_amount: Net interest amount (when has_withholding_tax=True)
            withholding_tax_amount: Tax amount withheld (when has_withholding_tax=True)
            withholding_tax_rate: Tax rate percentage (when has_withholding_tax=True)
            description: Event description
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent or tuple: Distribution event, or (distribution_event, tax_event) for withholding tax
        """
        # Delegate to service layer for proper orchestration
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        return fund_service.add_distribution(
            self.id, event_date, distribution_type,
            distribution_amount=distribution_amount,
            has_withholding_tax=has_withholding_tax,
            gross_interest_amount=gross_interest_amount,
            net_interest_amount=net_interest_amount,
            withholding_tax_amount=withholding_tax_amount,
            withholding_tax_rate=withholding_tax_rate,
            description=description,
            reference_number=reference_number,
            session=session
        )
    
    def add_nav_update(self, nav_per_share: float, update_date: date, description: str = None,
                       reference_number: str = None, session=None) -> 'FundEvent':
        """
        Add an NAV update event using the service layer.
        
        Note: This method delegates to the fund service for proper orchestration.
        For direct control, use FundService.add_nav_update() instead.
        
        Args:
            nav_per_share: NAV per share value
            update_date: Date of the NAV update
            description: Description of the update
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created NAV update event
            
        Raises:
            ValueError: If NAV per share is invalid
        """
        if not nav_per_share or nav_per_share <= 0:
            raise ValueError("NAV per share must be a positive number")
        if not update_date:
            raise ValueError("Date is required")
        
        # Delegate to service layer for proper orchestration
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        return fund_service.add_nav_update(self.id, nav_per_share, update_date, description, reference_number, session)
    
    def add_unit_purchase(self, units: float, price: float, date: date,
                          description: str = None, reference_number: str = None,
                          session=None) -> 'FundEvent':
        """
        Add a unit purchase event using the service layer.
        
        Note: This method delegates to the fund service for proper orchestration.
        For direct control, use FundService.add_unit_purchase() instead.
        
        Args:
            units: Number of units purchased
            unit_price: Price per unit
            purchase_date: Date of the purchase
            description: Description of the purchase
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit purchase event
            
        Raises:
            ValueError: If units or price are invalid
        """
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Unit price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Delegate to service layer for proper orchestration
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        return fund_service.add_unit_purchase(self.id, units, price, date, description, reference_number, session)
    
    def add_unit_sale(self, units: float, price: float, date: date,
                      description: str = None, reference_number: str = None,
                      session=None) -> 'FundEvent':
        """
        Add a unit sale event using the service layer.
        
        Note: This method delegates to the service layer for proper orchestration.
        For direct control, use FundService.add_unit_sale() instead.
        
        Args:
            units: Number of units sold
            unit_price: Price per unit
            sale_date: Date of the sale
            description: Description of the sale
            reference_number: External reference number
            session: Database session
            
        Returns:
            FundEvent: The created unit sale event
            
        Raises:
            ValueError: If units or price are invalid
        """
        if not units or units <= 0:
            raise ValueError("Units must be a positive number")
        if not price or price <= 0:
            raise ValueError("Unit price must be a positive number")
        if not date:
            raise ValueError("Date is required")
        
        # Delegate to service layer for proper orchestration
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        return fund_service.add_unit_sale(self.id, units, price, date, description, reference_number, session)
    
    # ============================================================================
    # CORE BUSINESS PROPERTIES - Intrinsic Fund Properties
    # ============================================================================
    
    def total_capital_called(self, session=None) -> float:
        """Get total capital called amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total capital called amount
        """
        if not session:
            raise ValueError("Session required for total_capital_called")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.CAPITAL_CALL and event.amount
        )
    
    def total_capital_returned(self, session=None) -> float:
        """Get total capital returned amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total capital returned amount
        """
        if not session:
            raise ValueError("Session required for total_capital_returned")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.RETURN_OF_CAPITAL and event.amount
        )
    
    def total_distributions(self, session=None) -> float:
        """Get total distributions amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total distributions amount
        """
        if not session:
            raise ValueError("Session required for total_distributions")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.DISTRIBUTION and event.amount
        )
    
    def total_tax_withheld(self, session=None) -> float:
        """Get total tax withheld amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total tax withheld amount
        """
        if not session:
            raise ValueError("Session required for total_tax_withheld")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.TAX_PAYMENT and event.amount
        )
    
    def total_unit_purchases(self, session=None) -> float:
        """Get total unit purchases amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total unit purchases amount
        """
        if not session:
            raise ValueError("Session required for total_unit_purchases")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.UNIT_PURCHASE and event.amount
        )
    
    def total_unit_sales(self, session=None) -> float:
        """Get total unit sales amount.
        
        Args:
            session: Database session
            
        Returns:
            float: Total unit sales amount
        """
        if not session:
            raise ValueError("Session required for total_unit_sales")
        
        events = self.get_all_fund_events(session=session)
        return sum(
            event.amount for event in events 
            if event.event_type == EventType.UNIT_SALE and event.amount
        )
    
    # ============================================================================
    # EVENT QUERY METHODS - Accessing Fund's Own Data
    # ============================================================================
    
    def get_all_fund_events(self, exclude_system_events: bool = True, session=None) -> List['FundEvent']:
        """Get all fund events.
        
        Args:
            exclude_system_events: Whether to exclude system events
            session: Database session
            
        Returns:
            List[FundEvent]: List of fund events
        """
        if not session:
            raise ValueError("Session required for get_all_fund_events")
        
        query = session.query(FundEvent).filter(FundEvent.fund_id == self.id)
        if exclude_system_events:
            # Filter out system events using the enum's is_system_event method
            system_event_types = [event_type for event_type in EventType if EventType.is_system_event(event_type)]
            if system_event_types:
                query = query.filter(~FundEvent.event_type.in_(system_event_types))
        
        return query.order_by(FundEvent.event_date).all()
    
    def get_recent_events(self, limit: int = 10, exclude_system_events: bool = True, 
                         session=None) -> List['FundEvent']:
        """Get recent fund events.
        
        Args:
            limit: Maximum number of events to return
            exclude_system_events: Whether to exclude system events
            session: Database session
            
        Returns:
            List[FundEvent]: List of recent fund events
        """
        if not session:
            raise ValueError("Session required for get_recent_events")
        
        events = self.get_all_fund_events(exclude_system_events=exclude_system_events, session=session)
        return events[-limit:] if len(events) > limit else events
    
    def get_events(self, event_types: List['EventType'] = None, start_date: date = None, 
                   end_date: date = None, session=None) -> List['FundEvent']:
        """Get fund events with optional filtering.
        
        Args:
            event_types: List of event types to filter by
            start_date: Start date for filtering
            end_date: End date for filtering
            session: Database session
            
        Returns:
            List[FundEvent]: List of filtered fund events
        """
        if not session:
            raise ValueError("Session required for get_events")
        
        events = self.get_all_fund_events(session=session)
        
        if event_types:
            events = [e for e in events if e.event_type in event_types]
        
        if start_date:
            events = [e for e in events if e.event_date and e.event_date >= start_date]
        
        if end_date:
            events = [e for e in events if e.event_date and e.event_date <= end_date]
        
        return events
    
    def get_capital_calls(self, start_date: date = None, end_date: date = None, session=None) -> List['FundEvent']:
        """Get capital call events with optional date filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            session: Database session
            
        Returns:
            List[FundEvent]: List of capital call events
        """
        return self.get_events(event_types=[EventType.CAPITAL_CALL], 
                             start_date=start_date, end_date=end_date, session=session)
    
    def get_capital_returns(self, start_date: date = None, end_date: date = None, session=None) -> List['FundEvent']:
        """Get capital return events with optional date filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            session: Database session
            
        Returns:
            List[FundEvent]: List of capital return events
        """
        return self.get_events(event_types=[EventType.RETURN_OF_CAPITAL], 
                             start_date=start_date, end_date=end_date, session=session)
    
    def get_distributions(self, start_date: date = None, end_date: date = None, session=None) -> List['FundEvent']:
        """Get distribution events with optional date filtering.
        
        Args:
            start_date: Start date for filtering
            end_date: End date for filtering
            session: Database session
            
        Returns:
            List[FundEvent]: List of distribution events
        """
        return self.get_events(event_types=[EventType.DISTRIBUTION], 
                             start_date=start_date, end_date=end_date, session=session)
    
    # ============================================================================
    # ADDITIONAL BUSINESS PROPERTIES - Convenience Properties
    # ============================================================================
    
    @property
    def remaining_commitment(self) -> float:
        """Get remaining commitment amount as a property.
        
        Returns:
            float: Remaining commitment amount
        """
        return self.get_remaining_commitment()
    
    @property
    def total_called_capital(self) -> float:
        """Get total called capital as a property (requires session context).
        
        Note: This property requires a session to be available in the current context.
        For explicit control, use total_capital_called(session) method instead.
        
        Returns:
            float: Total called capital amount
            
        Raises:
            RuntimeError: If no session is available in current context
        """
        # Try to get session from current context
        try:
            from flask import current_app
            if hasattr(current_app, 'config') and current_app.config.get('TEST_DB_SESSION'):
                session = current_app.config['TEST_DB_SESSION']
                return self.total_capital_called(session=session)
        except:
            pass
        
        # Try to get session from SQLAlchemy scoped session
        try:
            from sqlalchemy.orm import scoped_session
            session = scoped_session.registry()
            if session:
                return self.total_capital_called(session=session)
        except:
            pass
        
        raise RuntimeError("No database session available. Use total_capital_called(session) method instead.")
    
    def get_start_date(self, session=None) -> Optional[date]:
        """Get fund start date (first event date).
        
        Args:
            session: Database session
            
        Returns:
            date or None: Fund start date if events exist
        """
        if not session:
            raise ValueError("Session required for get_start_date")
        
        events = self.get_all_fund_events(session=session)
        if not events:
            return None
        
        # Get the earliest event date
        event_dates = [event.event_date for event in events if event.event_date]
        return min(event_dates) if event_dates else None
    
    def get_end_date(self, session=None) -> Optional[date]:
        """Get fund end date using service layer.
        
        Note: This method delegates to the fund service for proper orchestration.
        For direct control, use FundService.get_fund_end_date() instead.
        
        Args:
            session: Database session
            
        Returns:
            date or None: Fund end date if fund is completed or realized
        """
        if not session:
            raise ValueError("Session required for get_end_date")
        
        # Calculate end date for both COMPLETED and REALIZED funds
        if self.status not in [FundStatus.COMPLETED, FundStatus.REALIZED]:
            return None
        
        # Delegate to service layer for proper orchestration
        from src.fund.services.fund_service import FundService
        fund_service = FundService()
        return fund_service.get_fund_end_date(self.id, session)
    
    def get_summary_data(self, session=None) -> Dict[str, Any]:
        """Get summary data for the fund.
        
        This method provides a clean interface for getting fund summary information
        that can be used by the frontend and other services.
        
        Args:
            session: Database session (required for some calculations)
            
        Returns:
            Dict containing fund summary data
        """
        if not session:
            raise ValueError("Session required for get_summary_data")
        # Build summary data dictionary
        summary_data = {
            'id': self.id,
            'name': self.name,
            'fund_type': self.fund_type,
            'tracking_type': self.tracking_type.value if self.tracking_type else None,
            'description': self.description,
            'currency': self.currency,
            'commitment_amount': self.commitment_amount,
            'expected_irr': self.expected_irr,
            'expected_duration_months': self.expected_duration_months,
            'investment_company_id': self.investment_company_id,
            'entity_id': self.entity_id,
            'current_equity_balance': self.current_equity_balance,
            'average_equity_balance': self.average_equity_balance,
            'status': self.status.value if self.status else None,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'current_duration': self.current_duration,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        
        # Add tracking type specific fields
        if self.tracking_type == FundType.NAV_BASED:
            summary_data.update({
                'current_units': self.current_units,
                'current_unit_price': self.current_unit_price,
                'current_nav_total': self.current_nav_total,
            })
        elif self.tracking_type == FundType.COST_BASED:
            summary_data.update({
                'total_cost_basis': self.total_cost_basis,
            })
        
        # Add IRR fields if available
        if self.completed_irr_gross is not None:
            summary_data['completed_irr_gross'] = self.completed_irr_gross
        if self.completed_irr_after_tax is not None:
            summary_data['completed_irr_after_tax'] = self.completed_irr_after_tax
        if self.completed_irr_real is not None:
            summary_data['completed_irr_real'] = self.completed_irr_real
        
        return summary_data
    
    def get_financial_years(self, session=None) -> List[str]:
        """Get all financial years from fund start date to current date.
        
        This method provides enterprise-grade financial year management by:
        - Using the fund's actual start date (from events or creation)
        - Respecting the entity's tax jurisdiction for financial year calculation
        - Providing a clean interface for frontend consumption
        
        Args:
            session: Database session (required for entity lookup and date calculations)
            
        Returns:
            List[str]: List of financial years in descending order (most recent first)
            
        Raises:
            ValueError: If session is not provided
        """
        if not session:
            raise ValueError("Session required for get_financial_years")
        
        # Get fund start date (use events if available, otherwise creation date)
        start_date = self.get_start_date(session=session)
        if not start_date:
            start_date = self.created_at.date()
        
        # Get entity for tax jurisdiction
        entity = session.query(Entity).filter(Entity.id == self.entity_id).first()
        if not entity:
            return []
        
        # Import calculation function from entity domain
        from src.entity.calculations import get_financial_years_for_fund_period
        from datetime import date
        
        # Calculate financial years from start date to current date
        end_date = date.today()
        financial_years = get_financial_years_for_fund_period(start_date, end_date, entity)
        
        # Return sorted list (most recent first)
        return sorted(list(financial_years), reverse=True)