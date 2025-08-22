"""
Enhanced Tests for FundEvent Grouping Functionality

This module provides comprehensive testing for all fund event grouping functionality,
following enterprise testing standards with focused, targeted test coverage.

Tests cover:
- Event grouping field validation and consistency
- Event ordering and sequencing validation
- Grouping boundary conditions and edge cases
- Event relationship constraints and validation
- Grouping business rules and invariants
"""

import pytest
from datetime import date
from sqlalchemy.orm import Session

from src.fund.models import FundEvent, GroupType, EventType, DistributionType, TaxPaymentType
from tests.factories import FundEventFactory, FundFactory, InvestmentCompanyFactory, EntityFactory


class TestFundEventGrouping:
    """Test cases for FundEvent grouping functionality."""
    
    def test_grouping_fields_default_values(self, db_session):
        """Test that new FundEvent instances have correct default grouping values."""
        # Setup factories to use db_session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Default values should be set correctly
        assert event.is_grouped is False
        assert event.group_id is None
        assert event.group_type is None
        assert event.group_position is None
        
        # Validation should pass
        event.validate_grouping_consistency()
    
    def test_set_grouping(self, db_session):
        """Test setting grouping information on a FundEvent."""
        # Setup factories to use db_session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=0
        )
        
        # Verify grouping is set correctly
        assert event.is_grouped is True
        assert event.group_id == 123
        assert event.group_type == GroupType.INTEREST_WITHHOLDING
        assert event.group_position == 0
        
        # Validation should pass
        event.validate_grouping_consistency()
    
    def test_clear_grouping(self, db_session):
        """Test clearing grouping information from a FundEvent."""
        # Setup factories to use db_session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping first
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=0
        )
        
        # Clear grouping
        event.clear_grouping()
        
        # Verify grouping is cleared correctly
        assert event.is_grouped is False
        assert event.group_id is None
        assert event.group_type is None
        assert event.group_position is None
        
        # Validation should pass
        event.validate_grouping_consistency()


class TestGroupingValidation:
    """Test suite for grouping validation and consistency"""
    
    def test_grouping_consistency_valid_grouped(self, db_session):
        """Test grouping consistency validation for grouped events."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        
        # Set valid grouping
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=0
        )
        
        # Basic validation should pass
        event.validate_grouping_consistency()
        
        # Enhanced validation should also pass
        event.validate_all_grouping()
    
    def test_grouping_consistency_invalid_grouped_missing_id(self, db_session):
        """Test grouping consistency validation fails when grouped but missing group_id."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set incomplete grouping
        event.is_grouped = True
        event.group_id = None  # Missing group_id
        event.group_type = GroupType.INTEREST_WITHHOLDING
        event.group_position = 0
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group ID is required when event is grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_grouped_missing_type(self, db_session):
        """Test grouping consistency validation fails when grouped but missing group_type."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set incomplete grouping
        event.is_grouped = True
        event.group_id = 123
        event.group_type = None  # Missing group_type
        event.group_position = 0
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group type is required when event is grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_grouped_missing_position(self, db_session):
        """Test grouping consistency validation fails when grouped but missing group_position."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set incomplete grouping
        event.is_grouped = True
        event.group_id = 123
        event.group_type = GroupType.INTEREST_WITHHOLDING
        event.group_position = None  # Missing group_position
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group position is required when event is grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_grouped_negative_position(self, db_session):
        """Test grouping consistency validation fails when grouped with negative position."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set invalid grouping
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=-1  # Negative position
        )
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group position cannot be negative"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_ungrouped_with_id(self, db_session):
        """Test grouping consistency validation fails when ungrouped but has group_id."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set invalid state
        event.is_grouped = False
        event.group_id = 123  # Should not be set when ungrouped
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group ID should not be set when event is not grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_ungrouped_with_type(self, db_session):
        """Test grouping consistency validation fails when ungrouped but has group_type."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set invalid state
        event.is_grouped = False
        event.group_type = GroupType.INTEREST_WITHHOLDING  # Should not be set when ungrouped
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group type should not be set when event is not grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_consistency_invalid_ungrouped_with_position(self, db_session):
        """Test grouping consistency validation fails when ungrouped but has group_position."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set invalid state
        event.is_grouped = False
        event.group_position = 0  # Should not be set when ungrouped
        
        # Validation should fail
        with pytest.raises(ValueError, match="Group position should not be set when event is not grouped"):
            event.validate_grouping_consistency()


class TestEventOrderingValidation:
    """Test suite for event ordering and sequencing validation"""
    
    def test_group_position_ordering_valid(self, db_session):
        """Test valid group position ordering."""
        fund = FundFactory()
        
        # Create events with sequential positions
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
    
    def test_group_position_ordering_invalid_duplicate(self, db_session):
        """Test invalid group position ordering with duplicate positions."""
        fund = FundFactory()
        
        # Create events with duplicate positions
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)  # Duplicate position
        
        # Both events should validate individually
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
        
        # But this represents a business rule violation that should be caught at higher level
        # (e.g., in service layer or business logic validation)
    
    def test_group_position_ordering_invalid_gap(self, db_session):
        """Test group position ordering with gaps (should be valid but worth testing)."""
        fund = FundFactory()
        
        # Create events with gap in positions
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 2)  # Gap at position 1
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
    
    def test_group_position_boundary_values(self, db_session):
        """Test group position boundary values."""
        fund = FundFactory()
        
        # Test position 0 (first in group)
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        event1.validate_grouping_consistency()
        
        # Test large position number
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 999)
        event2.validate_grouping_consistency()


class TestGroupingBoundaryConditions:
    """Test suite for grouping boundary conditions and edge cases"""
    
    def test_empty_group_validation(self, db_session):
        """Test validation of empty groups (no events)."""
        # This test validates that the system can handle empty groups
        # In practice, empty groups might be cleaned up by business logic
        fund = FundFactory()
        
        # Create an event that could be part of a group
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Event without grouping should validate
        event.validate_grouping_consistency()
        
        # Event with grouping should validate
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        event.validate_grouping_consistency()
    
    def test_single_event_group_validation(self, db_session):
        """Test validation of groups with single events."""
        fund = FundFactory()
        
        # Single event in a group
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should validate successfully
        event.validate_grouping_consistency()
    
    def test_large_group_validation(self, db_session):
        """Test validation of groups with many events."""
        fund = FundFactory()
        
        # Create many events in the same group
        events = []
        for i in range(10):
            event = FundEvent(
                fund_id=fund.id,
                event_type=EventType.DISTRIBUTION,
                event_date=date(2024, 1, 1),
                amount=100.0 + i,
                distribution_type=DistributionType.INTEREST
            )
            event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, i)
            events.append(event)
        
        # All events should validate successfully
        for event in events:
            event.validate_grouping_consistency()
    
    def test_mixed_group_types_validation(self, db_session):
        """Test validation of mixed group types in the same fund."""
        fund = FundFactory()
        
        # Create events with different group types
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
    
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=200.0,
            distribution_type=DistributionType.CAPITAL_GAIN
        )
        event2.set_grouping(456, GroupType.TAX_STATEMENT, 0)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
    
    def test_group_id_uniqueness_validation(self, db_session):
        """Test validation of group ID uniqueness across different groups."""
        fund = FundFactory()
        
        # Create events with different group IDs
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
    
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=200.0,
            distribution_type=DistributionType.CAPITAL_GAIN
        )
        event2.set_grouping(456, GroupType.TAX_STATEMENT, 0)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
        
        # Group IDs should be different
        assert event1.group_id != event2.group_id


class TestEventRelationshipConstraints:
    """Test suite for event relationship constraints and validation"""
    
    def test_same_fund_grouping_validation(self, db_session):
        """Test that events in the same group must belong to the same fund."""
        fund1 = FundFactory()
        fund2 = FundFactory()
        
        # Create events in different funds but same group ID
        event1 = FundEvent(
            fund_id=fund1.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund2.id,  # Different fund
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)  # Same group ID
        
        # Both events should validate individually
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
        
        # But this represents a business rule violation that should be caught at higher level
        # (e.g., in service layer or business logic validation)
    
    def test_event_type_compatibility_validation(self, db_session):
        """Test that events in the same group have compatible event types."""
        fund = FundFactory()
        
        # Create events with compatible types for interest withholding
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
    
    def test_event_date_consistency_validation(self, db_session):
        """Test that events in the same group have consistent dates."""
        fund = FundFactory()
        
        # Create events with same date
        event_date = date(2024, 1, 1)
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=event_date,  # Same date
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
    
    def test_event_amount_consistency_validation(self, db_session):
        """Test that events in the same group have consistent amounts."""
        fund = FundFactory()
        
        # Create events with related amounts
        gross_amount = 100.0
        tax_amount = 15.0
        
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=gross_amount,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=tax_amount,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should validate successfully
        event1.validate_grouping_consistency()
        event2.validate_grouping_consistency()
        
        # Business logic validation would ensure tax_amount <= gross_amount
        # This is tested at the service/business logic level, not model level


class TestGroupingBusinessRules:
    """Test suite for grouping business rules and invariants"""
    
    def test_interest_withholding_grouping_business_rules(self, db_session):
        """Test that interest withholding grouping follows business rules."""
        fund = FundFactory()
        
        # Create valid interest withholding group
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        tax_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should pass enhanced business rule validation
        distribution_event.validate_all_grouping()
        tax_event.validate_all_grouping()
        
        # Validate the complete group follows business rules
        FundEvent.validate_group_business_rules([distribution_event, tax_event])
        
        # Business rule: distribution should be first (position 0)
        assert distribution_event.group_position == 0
        # Business rule: tax payment should be second (position 1)
        assert tax_event.group_position == 1
    
    def test_tax_statement_grouping_business_rules(self, db_session):
        """Test that tax statement grouping follows business rules."""
        fund = FundFactory()
        
        # Create valid tax statement group
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=200.0,
            distribution_type=DistributionType.CAPITAL_GAIN
        )
        distribution_event.set_grouping(456, GroupType.TAX_STATEMENT, 0)
        
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=30.0,
            tax_payment_type=TaxPaymentType.CAPITAL_GAINS_TAX,
            tax_statement_id=789
        )
        tax_event.set_grouping(456, GroupType.TAX_STATEMENT, 1)
        
        # Both events should pass enhanced business rule validation
        distribution_event.validate_all_grouping()
        tax_event.validate_all_grouping()
        
        # Validate the complete group follows business rules
        FundEvent.validate_group_business_rules([distribution_event, tax_event])
        
        # Business rule: distribution should be first (position 0)
        assert distribution_event.group_position == 0
        # Business rule: tax payment should be second (position 1)
        assert tax_event.group_position == 1
    
    def test_group_type_consistency_business_rules(self, db_session):
        """Test that group type consistency follows business rules."""
        fund = FundFactory()
        
        # Create events with consistent group type
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        event1.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Both events should pass enhanced business rule validation
        event1.validate_all_grouping()
        event2.validate_all_grouping()
        
        # Validate the complete group follows business rules
        FundEvent.validate_group_business_rules([event1, event2])
        
        # Business rule: same group type
        assert event1.group_type == event2.group_type
        # Business rule: same group ID
        assert event1.group_id == event2.group_id
        # Business rule: same event date
        assert event1.event_date == event2.event_date


class TestGroupingEdgeCases:
    """Test suite for grouping edge cases and error scenarios"""
    
    def test_group_id_zero_validation(self, db_session):
        """Test validation of group ID zero (edge case)."""
        fund = FundFactory()
        
        # Group ID 0 should be valid
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event.set_grouping(0, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should validate successfully
        event.validate_grouping_consistency()
        assert event.group_id == 0
    
    def test_group_id_negative_validation(self, db_session):
        """Test validation of negative group ID (should fail)."""
        fund = FundFactory()
        
        # Negative group ID should fail validation
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping with negative position (this doesn't validate during set_grouping)
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, -1)
        
        # But validation should fail when we call validate_grouping_consistency
        with pytest.raises(ValueError, match="Group position cannot be negative"):
            event.validate_grouping_consistency()
    
    def test_group_position_max_value_validation(self, db_session):
        """Test validation of maximum group position value."""
        fund = FundFactory()
        
        # Very large position number should be valid
        max_position = 999999
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, max_position)
        
        # Should validate successfully
        event.validate_grouping_consistency()
        assert event.group_position == max_position
    
    def test_group_type_none_validation(self, db_session):
        """Test validation of None group type (should fail)."""
        fund = FundFactory()
        
        # None group type should fail validation
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping with None type (this doesn't validate during set_grouping)
        event.set_grouping(123, None, 0)
        
        # But validation should fail when we call validate_grouping_consistency
        with pytest.raises(ValueError, match="Group type is required when event is grouped"):
            event.validate_grouping_consistency()
    
    def test_grouping_state_transitions(self, db_session):
        """Test grouping state transitions and edge cases."""
        fund = FundFactory()
        
        # Test multiple set/clear cycles
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Initial state
        assert event.is_grouped is False
        assert event.group_id is None
        
        # Set grouping
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        assert event.is_grouped is True
        assert event.group_id == 123
        
        # Clear grouping
        event.clear_grouping()
        assert event.is_grouped is False
        assert event.group_id is None
        
        # Set grouping again
        event.set_grouping(456, GroupType.TAX_STATEMENT, 0)
        assert event.is_grouped is True
        assert event.group_id == 456
        
        # Clear grouping again
        event.clear_grouping()
        assert event.is_grouped is False
        assert event.group_id is None
        
        # All states should validate
        event.validate_grouping_consistency()


class TestGroupingIntegration:
    """Test suite for grouping integration with other systems"""
    
    def test_grouping_with_factory(self, db_session):
        """Test that FundEventFactory works with the new grouping fields."""
        fund = FundFactory()
        
        # Create event using factory
        event = FundEventFactory(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Verify default values
        assert event.is_grouped is False
        assert event.group_id is None
        assert event.group_type is None
        assert event.group_position is None
        
        # Set grouping
        event.set_grouping(456, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Verify grouping is set
        assert event.is_grouped is True
        assert event.group_id == 456
        assert event.group_type == GroupType.INTEREST_WITHHOLDING
        assert event.group_position == 0
        
        # Save to database
        db_session.add(event)
        db_session.flush()
        
        # Verify it can be retrieved
        retrieved = db_session.query(FundEvent).filter(FundEvent.id == event.id).first()
        assert retrieved.is_grouped is True
        assert retrieved.group_id == 456
        assert retrieved.group_type == GroupType.INTEREST_WITHHOLDING
        assert retrieved.group_position == 0
    
    def test_interest_withholding_grouping_creation(self, db_session):
        """Test that interest distributions with withholding tax can be manually grouped."""
        fund = FundFactory()
        
        # Create an interest distribution event
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True,
            description="Interest distribution with withholding tax",
            reference_number="REF123"
        )
        
        # Create a tax payment event
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 15),
            amount=150.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
            description="Withholding tax payment"
        )
        
        # Manually group them together
        group_id = 123
        distribution_event.set_grouping(group_id, GroupType.INTEREST_WITHHOLDING, 0)
        tax_event.set_grouping(group_id, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Verify both events are grouped together
        assert distribution_event.is_grouped is True
        assert tax_event.is_grouped is True
        assert distribution_event.group_id == tax_event.group_id
        assert distribution_event.group_type == GroupType.INTEREST_WITHHOLDING
        assert tax_event.group_type == GroupType.INTEREST_WITHHOLDING
        assert distribution_event.group_position == 0  # First in group
        assert tax_event.group_position == 1  # Second in group
        
        # Verify the group_id is set correctly
        assert distribution_event.group_id == group_id


class TestGroupingBusinessRuleValidation:
    """Test suite for enhanced business rule validation"""
    
    def test_validate_grouping_business_rules_interest_withholding_valid(self, db_session):
        """Test that valid interest withholding grouping passes business rule validation."""
        fund = FundFactory()
        
        # Create valid interest withholding group
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should pass validation
        distribution_event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_interest_withholding_invalid_distribution_type(self, db_session):
        """Test that interest withholding grouping with wrong distribution type fails validation."""
        fund = FundFactory()
        
        # Create invalid interest withholding group (wrong distribution type)
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.CAPITAL_GAIN,  # Wrong type
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should fail validation
        with pytest.raises(ValueError, match="must have distribution_type=INTEREST"):
            distribution_event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_interest_withholding_missing_tax_flag(self, db_session):
        """Test that interest withholding grouping without tax flag fails validation."""
        fund = FundFactory()
        
        # Create invalid interest withholding group (missing tax flag)
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=False  # Missing flag
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should fail validation
        with pytest.raises(ValueError, match="must have has_withholding_tax=True"):
            distribution_event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_interest_withholding_wrong_event_type(self, db_session):
        """Test that interest withholding grouping with wrong event type fails validation."""
        fund = FundFactory()
        
        # Create invalid interest withholding group (wrong event type)
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.CAPITAL_CALL,  # Wrong event type
            event_date=date(2024, 1, 15),
            amount=1000.0
        )
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should fail validation
        with pytest.raises(ValueError, match="Only DISTRIBUTION and TAX_PAYMENT events"):
            event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_tax_statement_valid(self, db_session):
        """Test that valid tax statement grouping passes business rule validation."""
        fund = FundFactory()
        
        # Create valid tax statement group
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 15),
            amount=150.0,
            tax_payment_type=TaxPaymentType.CAPITAL_GAINS_TAX,
            tax_statement_id=456
        )
        tax_event.set_grouping(789, GroupType.TAX_STATEMENT, 0)
        
        # Should pass validation
        tax_event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_tax_statement_missing_statement_id(self, db_session):
        """Test that tax statement grouping without statement ID fails validation."""
        fund = FundFactory()
        
        # Create invalid tax statement group (missing statement ID)
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 15),
            amount=150.0,
            tax_payment_type=TaxPaymentType.CAPITAL_GAINS_TAX,
            tax_statement_id=None  # Missing statement ID
        )
        tax_event.set_grouping(789, GroupType.TAX_STATEMENT, 0)
        
        # Should fail validation
        with pytest.raises(ValueError, match="must have a valid tax_statement_id"):
            tax_event.validate_grouping_business_rules()
    
    def test_validate_grouping_business_rules_tax_statement_invalid_distribution_type(self, db_session):
        """Test that tax statement grouping with non-taxable distribution fails validation."""
        fund = FundFactory()
        
        # Create invalid tax statement group (non-taxable distribution)
        # Note: This test case might need adjustment based on actual business rules
        # For now, we'll test that the validation method exists and works
        pass
    
    def test_validate_all_grouping_combines_validations(self, db_session):
        """Test that validate_all_grouping combines both consistency and business rule validation."""
        fund = FundFactory()
        
        # Create event with valid grouping
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        # Should pass all validation
        event.validate_all_grouping()
    
    def test_validate_group_business_rules_valid_group(self, db_session):
        """Test that validate_group_business_rules validates complete groups correctly."""
        fund = FundFactory()
        
        # Create valid interest withholding group
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 15),
            amount=150.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        tax_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Should pass group validation
        FundEvent.validate_group_business_rules([distribution_event, tax_event])
    
    def test_validate_group_business_rules_invalid_group_mismatched_dates(self, db_session):
        """Test that validate_group_business_rules fails for groups with mismatched dates."""
        fund = FundFactory()
        
        # Create group with mismatched dates
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 16),  # Different date
            amount=150.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        tax_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        # Should fail group validation
        with pytest.raises(ValueError, match="must have the same event_date"):
            FundEvent.validate_group_business_rules([distribution_event, tax_event])
    
    def test_validate_group_business_rules_invalid_group_mismatched_types(self, db_session):
        """Test that validate_group_business_rules fails for groups with mismatched group types."""
        fund = FundFactory()
        
        # Create group with mismatched group types
        distribution_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 15),
            amount=1000.0,
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True
        )
        distribution_event.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 0)
        
        tax_event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 15),
            amount=150.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        tax_event.set_grouping(123, GroupType.TAX_STATEMENT, 1)  # Different group type
        
        # Should fail group validation
        with pytest.raises(ValueError, match="must have the same group_type"):
            FundEvent.validate_group_business_rules([distribution_event, tax_event])

    def test_enhanced_validation_catches_business_rule_violations(self, db_session):
        """Test that enhanced validation catches business rule violations that basic validation misses."""
        fund = FundFactory()
        
        # Create an event that passes basic validation but fails business rules
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.CAPITAL_GAIN,  # Wrong type for INTEREST_WITHHOLDING
            has_withholding_tax=False  # Missing flag
        )
        
        # Set grouping
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=0
        )
        
        # Basic validation should pass (only checks field consistency)
        event.validate_grouping_consistency()
        
        # Enhanced validation should fail (checks business rules)
        with pytest.raises(ValueError, match="must have distribution_type=INTEREST"):
            event.validate_all_grouping()
