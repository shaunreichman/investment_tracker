"""
Fund Event Model.

This module provides the FundEvent model class, representing events that occur within funds.
The model handles only data persistence and basic validation, with business logic
delegated to services for clean separation of concerns.
"""

from typing import List
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, Date, Boolean, Enum, ForeignKey, Text, Index
from sqlalchemy.orm import relationship

from src.shared.base import Base
from src.fund.enums.fund_event_enums import EventType, DistributionType, TaxPaymentType, GroupType
from src.fund.enums.fund_enums import FundTrackingType


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
    amount = Column(Float, nullable=True)  # (MANUAL) event amount (positive for calls, negative for returns, null for NAV updates)
    description = Column(Text)  # (MANUAL) description of the event
    reference_number = Column(String(255))  # (MANUAL) external reference number
    
    # NAV-specific fields (for NAV_BASED funds)
    nav_per_share = Column(Float, nullable=True)  # (MANUAL) NAV per share for NAV_UPDATE events
    previous_nav_per_share = Column(Float, nullable=True)  # (CALCULATED) previous NAV per share for NAV_UPDATE events
    nav_change_absolute = Column(Float, nullable=True)  # (CALCULATED) absolute change in NAV for NAV_UPDATE events
    nav_change_percentage = Column(Float, nullable=True)  # (CALCULATED) percentage change in NAV for NAV_UPDATE events

    units_owned = Column(Float, nullable=True)  # (CALCULATED) cumulative units owned after this event
    
    # Distribution-specific fields
    distribution_type = Column(Enum(DistributionType), nullable=True)  # (MANUAL) type of distribution if applicable
    tax_withholding = Column(Float, nullable=True)  # (MANUAL) tax withholding amount if applicable
    has_withholding_tax = Column(Boolean, default=False)  # (MANUAL) flag for distributions with associated withholding tax
    
    # Tax-specific fields
    tax_payment_type = Column(Enum(TaxPaymentType), nullable=True)  # (MANUAL) type of tax payment (INTEREST, CAPITAL_GAINS, etc.)
    tax_statement_id = Column(Integer, ForeignKey('tax_statements.id'), nullable=True, index=True)  # (MANUAL) foreign key to tax statement for TAX_PAYMENT events
    
    # Unit transaction fields
    units_purchased = Column(Float, nullable=True)  # (MANUAL) units purchased in this event
    units_sold = Column(Float, nullable=True)  # (MANUAL) units sold in this event
    unit_price = Column(Float, nullable=True)  # (MANUAL) unit price for this transaction
    brokerage_fee = Column(Float, default=0.0, nullable=True)  # (MANUAL) brokerage fee for unit transactions (must be non-negative)
    
    # Calculated fields
    current_equity_balance = Column(Float, nullable=True)  # (CALCULATED) For NAV-based funds: FIFO cost base after this event. For cost-based funds: net capital after this event
    
    # Debt cost fields
    dc_current_equity_balance = Column(Float, nullable=True)  # (CALCULATED) current equity balance used for this daily debt cost event
    dc_risk_free_rate = Column(Float, nullable=True)  # (CALCULATED) risk free rate used for this daily debt cost event

    # System flags
    is_cash_flow_complete = Column(Boolean, default=False)  # (SYSTEM) auto-managed flag set by reconciliation logic
    
    # Grouping fields (CALCULATED: Grouping flags set by backend when creating events)
    is_grouped = Column(Boolean, default=False, nullable=False)  # (CALCULATED) whether this event is part of a group
    group_id = Column(Integer, nullable=True, index=True)  # (CALCULATED) unique identifier for the group (auto-generated)
    group_type = Column(Enum(GroupType), nullable=True)  # (CALCULATED) type of grouping (INTEREST_WITHHOLDING, TAX_STATEMENT, etc.)
    group_position = Column(Integer, nullable=True)  # (CALCULATED) position within group for ordering (0=first, 1=second, etc.)
    
    # Metadata
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was created
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))  # (SYSTEM) timestamp when record was last updated
    
    # Relationships
    fund = relationship("Fund", back_populates="fund_events")
    cash_flows = relationship("FundEventCashFlow", back_populates="fund_event", cascade="all, delete-orphan")
    tax_statement = relationship("FundTaxStatement", lazy='selectin')  # Eager load for tax statement data
    
    # Performance indexes
    __table_args__ = (
        # Core indexes
        Index('idx_fund_events_fund_id', 'fund_id'),
        Index('idx_fund_events_event_type', 'event_type'),
        Index('idx_fund_events_event_date', 'event_date'),
        Index('idx_fund_events_fund_id_event_date', 'fund_id', 'event_date'),
        
        # Advanced indexes for common query patterns
        Index('idx_fund_events_fund_date', 'fund_id', 'event_date'),
        Index('idx_fund_events_type_date', 'event_type', 'event_date'),
        Index('idx_fund_events_fund_type', 'fund_id', 'event_type'),
        Index('idx_fund_events_group_id', 'group_id'),
        Index('idx_fund_events_tax_statement_id', 'tax_statement_id'),
    )
    
    def __init__(self, **kwargs):
        """Initialize FundEvent with default values for grouping fields."""
        # Set default values for grouping fields
        self.is_grouped = False
        self.group_id = None
        self.group_type = None
        self.group_position = None
        
        # Set default values for system flags
        self.is_cash_flow_complete = False
        self.has_withholding_tax = False
        
        # Call parent constructor with remaining kwargs
        super().__init__(**kwargs)
    
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
        
        # Amount is required for most events, but not for NAV updates
        if self.amount is None and self.event_type != EventType.NAV_UPDATE:
            raise ValueError("Amount is required")
        
        # Validate NAV-specific fields
        if self.event_type == EventType.NAV_UPDATE:
            if self.nav_per_share is None or self.nav_per_share <= 0:
                raise ValueError("NAV per share must be positive for NAV update events")
        
        # Validate distribution-specific fields
        if self.event_type == EventType.DISTRIBUTION:
            if not self.distribution_type:
                raise ValueError("Distribution type is required for distribution events")
            if self.tax_withholding is not None and self.tax_withholding < 0:
                raise ValueError("Tax withholding cannot be negative")
        
        # Validate unit transaction fields
        if self.event_type in [EventType.UNIT_PURCHASE, EventType.UNIT_SALE]:
            if self.unit_price is None or self.unit_price <= 0:
                raise ValueError("Unit price must be positive for unit transactions")
            if self.brokerage_fee is not None and self.brokerage_fee < 0:
                raise ValueError("Brokerage fee cannot be negative")
        
        # Validate tax payment fields
        if self.event_type == EventType.TAX_PAYMENT:
            if not self.tax_payment_type:
                raise ValueError("Tax payment type is required for tax payment events")
            if self.tax_statement_id is None:
                raise ValueError("Tax statement ID is required for tax payment events")
        
        return True
    
    def validate_fund_type_compatibility(self, fund_tracking_type: FundTrackingType) -> bool:
        """Validate that event is compatible with fund tracking type.
        
        Args:
            fund_tracking_type: The tracking type of the fund
            
        Returns:
            bool: True if compatible
            
        Raises:
            ValueError: If event is incompatible with fund type
        """
        if fund_tracking_type == FundTrackingType.NAV_BASED:
            if self.event_type in [EventType.CAPITAL_CALL, EventType.RETURN_OF_CAPITAL]:
                raise ValueError(f"{self.event_type.value} events are not applicable for NAV-based funds")
        
        elif fund_tracking_type == FundTrackingType.COST_BASED:
            if self.event_type == EventType.NAV_UPDATE:
                raise ValueError("NAV update events are not applicable for cost-based funds")
        
        return True
    
    def validate_field_combinations(self) -> bool:
        """Validate field combinations based on event type.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If field combinations are invalid
        """
        # NAV update events must have NAV-related fields
        if self.event_type == EventType.NAV_UPDATE:
            if self.nav_per_share is None:
                raise ValueError("NAV per share is required for NAV update events")
        
        # Unit transactions must have unit-related fields
        if self.event_type == EventType.UNIT_PURCHASE:
            if self.units_purchased is None or self.units_purchased <= 0:
                raise ValueError("Units purchased must be positive for unit purchase events")
            if self.units_sold is not None and self.units_sold != 0:
                raise ValueError("Units sold should not be set for unit purchase events")
        
        elif self.event_type == EventType.UNIT_SALE:
            if self.units_sold is None or self.units_sold <= 0:
                raise ValueError("Units sold must be positive for unit sale events")
            if self.units_purchased is not None and self.units_purchased != 0:
                raise ValueError("Units purchased should not be set for unit sale events")
        
        # Distribution events must have distribution-related fields
        if self.event_type == EventType.DISTRIBUTION:
            if not self.distribution_type:
                raise ValueError("Distribution type is required for distribution events")
            if self.tax_withholding is not None and self.tax_withholding < 0:
                raise ValueError("Tax withholding cannot be negative")
        
        # Tax payment events must have tax-related fields
        if self.event_type == EventType.TAX_PAYMENT:
            if not self.tax_payment_type:
                raise ValueError("Tax payment type is required for tax payment events")
            if self.tax_statement_id is None:
                raise ValueError("Tax statement ID is required for tax payment events")
        
        return True
    
    def validate_grouping_consistency(self) -> bool:
        """Validate grouping field consistency.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If grouping fields are inconsistent
        """
        # If event is grouped, all grouping fields must be set
        if self.is_grouped:
            if self.group_id is None:
                raise ValueError("Group ID is required when event is grouped")
            if self.group_type is None:
                raise ValueError("Group type is required when event is grouped")
            if self.group_position is None:
                raise ValueError("Group position is required when event is grouped")
            if self.group_position < 0:
                raise ValueError("Group position cannot be negative")
        
        # If event is not grouped, grouping fields should not be set
        else:
            if self.group_id is not None:
                raise ValueError("Group ID should not be set when event is not grouped")
            if self.group_type is not None:
                raise ValueError("Group type should not be set when event is not grouped")
            if self.group_position is not None:
                raise ValueError("Group position should not be set when event is not grouped")
        
        return True
    
    def validate_grouping_business_rules(self) -> bool:
        """Validate that grouping makes business sense according to business rules.
        
        This method enforces business logic about which event types and combinations
        can be grouped together, ensuring data integrity and business rule compliance.
        
        Returns:
            bool: True if validation passes
            
        Raises:
            ValueError: If grouping violates business rules
        """
        # If not grouped, no business rules to validate
        if not self.is_grouped:
            return True
        
        # Validate INTEREST_WITHHOLDING grouping rules
        if self.group_type == GroupType.INTEREST_WITHHOLDING:
            if self.event_type == EventType.DISTRIBUTION:
                # Distribution events in interest withholding groups must be INTEREST type
                if self.distribution_type != DistributionType.INTEREST:
                    raise ValueError(
                        f"Distribution events in {GroupType.INTEREST_WITHHOLDING.value} groups "
                        f"must have distribution_type={DistributionType.INTEREST.value}, "
                        f"got {self.distribution_type.value if self.distribution_type else 'None'}"
                    )
                
                # Interest distributions must have withholding tax flag set
                if not self.has_withholding_tax:
                    raise ValueError(
                        f"Interest distributions in {GroupType.INTEREST_WITHHOLDING.value} groups "
                        f"must have has_withholding_tax=True"
                    )
                
            elif self.event_type == EventType.TAX_PAYMENT:
                # Tax payment events in interest withholding groups must be withholding tax types
                if not self.tax_payment_type or not TaxPaymentType.is_withholding_tax(self.tax_payment_type):
                    raise ValueError(
                        f"Tax payment events in {GroupType.INTEREST_WITHHOLDING.value} groups "
                        f"must have withholding tax payment types, got {self.tax_payment_type.value if self.tax_payment_type else 'None'}"
                    )
                
            else:
                # Only DISTRIBUTION and TAX_PAYMENT events can be in interest withholding groups
                raise ValueError(
                    f"Only {EventType.DISTRIBUTION.value} and {EventType.TAX_PAYMENT.value} events "
                    f"can be in {GroupType.INTEREST_WITHHOLDING.value} groups, "
                    f"got {self.event_type.value}"
                )
        
        # Validate TAX_STATEMENT grouping rules
        elif self.group_type == GroupType.TAX_STATEMENT:
            if self.event_type == EventType.TAX_PAYMENT:
                # Tax payment events in tax statement groups must have valid tax payment types
                if not self.tax_payment_type:
                    raise ValueError(
                        f"Tax payment events in {GroupType.TAX_STATEMENT.value} groups "
                        f"must have a valid tax_payment_type"
                    )
                
                # Must have tax statement ID for tax statement grouping
                if not self.tax_statement_id:
                    raise ValueError(
                        f"Tax payment events in {GroupType.TAX_STATEMENT.value} groups "
                        f"must have a valid tax_statement_id"
                    )
                
            elif self.event_type == EventType.DISTRIBUTION:
                # Distribution events in tax statement groups must be taxable types
                if not self.distribution_type or not DistributionType.is_taxable(self.distribution_type):
                    raise ValueError(
                        f"Distribution events in {GroupType.TAX_STATEMENT.value} groups "
                        f"must be taxable distribution types, got {self.distribution_type.value if self.distribution_type else 'None'}"
                    )
                
            else:
                # Only TAX_PAYMENT and DISTRIBUTION events can be in tax statement groups
                raise ValueError(
                    f"Only {EventType.TAX_PAYMENT.value} and {EventType.DISTRIBUTION.value} events "
                    f"can be in {GroupType.TAX_STATEMENT.value} groups, "
                    f"got {self.event_type.value}"
                )
        
        # Validate group position constraints
        if self.group_position is not None:
            if self.group_position < 0:
                raise ValueError("Group position cannot be negative")
            
            # Position 0 should typically be the primary event (distribution, not tax payment)
            if self.group_type == GroupType.INTEREST_WITHHOLDING:
                if self.event_type == EventType.TAX_PAYMENT and self.group_position == 0:
                    raise ValueError(
                        f"Tax payment events in {GroupType.INTEREST_WITHHOLDING.value} groups "
                        f"should not be at position 0 (should be after the distribution event)"
                    )
            
            elif self.group_type == GroupType.TAX_STATEMENT:
                if self.event_type == EventType.TAX_PAYMENT and self.group_position == 0:
                    # Tax payments can be first in tax statement groups
                    pass
                elif self.event_type == EventType.DISTRIBUTION and self.group_position == 0:
                    # Distributions can be first in tax statement groups
                    pass
        
        return True
    
    def validate_all_grouping(self) -> bool:
        """Validate all grouping rules (consistency + business rules).
        
        This method combines both field consistency validation and business rule validation
        to provide comprehensive grouping validation.
        
        Returns:
            bool: True if all validation passes
            
        Raises:
            ValueError: If any validation fails
        """
        self.validate_grouping_consistency()
        self.validate_grouping_business_rules()
        return True
    
    @classmethod
    def validate_group_business_rules(cls, grouped_events: List['FundEvent']) -> bool:
        """Validate business rules for a complete group of events.
        
        This method validates that all events in a group follow business rules together,
        including cross-event validation like date consistency and logical relationships.
        
        Args:
            grouped_events: List of FundEvent instances that should form a valid group
            
        Returns:
            bool: True if all validation passes
            
        Raises:
            ValueError: If the group violates business rules
        """
        if not grouped_events:
            raise ValueError("Group must contain at least one event")
        
        if len(grouped_events) == 1:
            # Single event groups are valid
            return grouped_events[0].validate_all_grouping()
        
        # Get group metadata from first event
        first_event = grouped_events[0]
        group_id = first_event.group_id
        group_type = first_event.group_type
        event_date = first_event.event_date
        
        # Validate all events have consistent group metadata
        for event in grouped_events:
            if event.group_id != group_id:
                raise ValueError(
                    f"All events in a group must have the same group_id. "
                    f"Expected {group_id}, got {event.group_id}"
                )
            
            if event.group_type != group_type:
                raise ValueError(
                    f"All events in a group must have the same group_type. "
                    f"Expected {group_type.value}, got {event.group_type.value}"
                )
            
            if event.event_date != event_date:
                raise ValueError(
                    f"All events in a group must have the same event_date. "
                    f"Expected {event_date}, got {event.event_date}"
                )
            
            # Validate individual event business rules
            event.validate_all_grouping()
        
        # Validate group-specific business rules
        if group_type == GroupType.INTEREST_WITHHOLDING:
            cls._validate_interest_withholding_group(grouped_events)
        elif group_type == GroupType.TAX_STATEMENT:
            cls._validate_tax_statement_group(grouped_events)
        
        # Validate group position consistency
        cls._validate_group_position_consistency(grouped_events)
        
        return True
    
    @classmethod
    def _validate_interest_withholding_group(cls, grouped_events: List['FundEvent']) -> None:
        """Validate business rules for interest withholding groups.
        
        Args:
            grouped_events: List of events in an interest withholding group
            
        Raises:
            ValueError: If group violates interest withholding business rules
        """
        # Must have exactly one distribution event and one tax payment event
        distribution_events = [e for e in grouped_events if e.event_type == EventType.DISTRIBUTION]
        tax_events = [e for e in grouped_events if e.event_type == EventType.TAX_PAYMENT]
        
        if len(distribution_events) != 1:
            raise ValueError(
                f"Interest withholding groups must contain exactly one distribution event, "
                f"got {len(distribution_events)}"
            )
        
        if len(tax_events) != 1:
            raise ValueError(
                f"Interest withholding groups must contain exactly one tax payment event, "
                f"got {len(tax_events)}"
            )
        
        # Distribution must be at position 0, tax payment at position 1
        distribution_event = distribution_events[0]
        tax_event = tax_events[0]
        
        if distribution_event.group_position != 0:
            raise ValueError(
                f"Distribution events in interest withholding groups must be at position 0, "
                f"got position {distribution_event.group_position}"
            )
        
        if tax_event.group_position != 1:
            raise ValueError(
                f"Tax payment events in interest withholding groups must be at position 1, "
                f"got position {tax_event.group_position}"
            )
        
        # Validate that the tax payment amount relates to the distribution
        if distribution_event.amount <= 0 or tax_event.amount <= 0:
            raise ValueError(
                f"Both distribution and tax payment amounts must be positive in interest withholding groups"
            )
    
    @classmethod
    def _validate_tax_statement_group(cls, grouped_events: List['FundEvent']) -> None:
        """Validate business rules for tax statement groups.
        
        Args:
            grouped_events: List of events in a tax statement group
            
        Raises:
            ValueError: If group violates tax statement business rules
        """
        # Must have at least one tax payment event
        tax_events = [e for e in grouped_events if e.event_type == EventType.TAX_PAYMENT]
        
        if not tax_events:
            raise ValueError(
                f"Tax statement groups must contain at least one tax payment event"
            )
        
        # Tax payment events must have valid tax statement IDs
        for event in tax_events:
            if event.tax_statement_id is None:
                raise ValueError(
                    f"Tax payment events in tax statement groups must have a valid tax_statement_id"
                )
        
        # Validate group positions are sequential starting from 0
        positions = sorted([e.group_position for e in grouped_events])
        expected_positions = list(range(len(grouped_events)))
        
        if positions != expected_positions:
            raise ValueError(
                f"Group positions must be sequential starting from 0. "
                f"Expected {expected_positions}, got {positions}"
            )
    
    @classmethod
    def _validate_group_position_consistency(cls, grouped_events: List['FundEvent']) -> None:
        """Validate that group positions are consistent and sequential.
        
        Args:
            grouped_events: List of events in a group
            
        Raises:
            ValueError: If group positions are inconsistent
        """
        # All events must have group positions
        for event in grouped_events:
            if event.group_position is None:
                raise ValueError(
                    f"All events in a group must have a group_position"
                )
        
        # Positions must be unique
        positions = [e.group_position for e in grouped_events]
        if len(positions) != len(set(positions)):
            raise ValueError(
                f"Group positions must be unique within a group. "
                f"Got duplicate positions: {positions}"
            )
        
        # Positions must be sequential starting from 0
        sorted_positions = sorted(positions)
        expected_positions = list(range(len(grouped_events)))
        
        if sorted_positions != expected_positions:
            raise ValueError(
                f"Group positions must be sequential starting from 0. "
                f"Expected {expected_positions}, got {sorted_positions}"
            )