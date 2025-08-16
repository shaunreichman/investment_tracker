"""
Tests for FundEvent grouping functionality.

This module tests the new grouping fields and validation methods added to FundEvent.
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
    
    def test_validate_grouping_consistency_valid_grouped(self, db_session):
        """Test validation passes for correctly grouped events."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=0
        )
        
        # Should not raise any exceptions
        event.validate_grouping_consistency()
    
    def test_validate_grouping_consistency_invalid_grouped_missing_fields(self, db_session):
        """Test validation fails for grouped events with missing fields."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set is_grouped but leave other fields None
        event.is_grouped = True
        event.group_id = None
        event.group_type = None
        event.group_position = None
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Grouped events must have a group_id"):
            event.validate_grouping_consistency()
    
    def test_validate_grouping_consistency_invalid_non_grouped_with_fields(self, db_session):
        """Test validation fails for non-grouped events with grouping fields set."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping fields but leave is_grouped False
        event.is_grouped = False
        event.group_id = 123
        event.group_type = GroupType.INTEREST_WITHHOLDING
        event.group_position = 0
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="Non-grouped events must not have a group_id"):
            event.validate_grouping_consistency()
    
    def test_validate_grouping_consistency_invalid_position_negative(self, db_session):
        """Test validation fails for grouped events with negative position."""
        fund = FundFactory()
        event = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Set grouping with negative position
        event.set_grouping(
            group_id=123,
            group_type=GroupType.INTEREST_WITHHOLDING,
            group_position=-1
        )
        
        # Should raise ValueError
        with pytest.raises(ValueError, match="group_position must be >= 0"):
            event.validate_grouping_consistency()
    
    def test_get_next_group_id(self, db_session):
        """Test getting the next available group ID."""
        # Initially no groups exist
        next_id = FundEvent.get_next_group_id(db_session)
        assert next_id == 1
        
        # Create some events with group IDs
        fund = FundFactory()
        event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 1, 1),
            amount=100.0,
            distribution_type=DistributionType.INTEREST
        )
        event1.set_grouping(100, GroupType.INTEREST_WITHHOLDING, 0)
        
        event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 1, 1),
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(200, GroupType.INTEREST_WITHHOLDING, 1)
        
        db_session.add_all([event1, event2])
        db_session.flush()
        
        # Next group ID should be max + 1
        next_id = FundEvent.get_next_group_id(db_session)
        assert next_id == 201
    
    def test_validate_group_date_consistency_valid(self, db_session):
        """Test date consistency validation passes for valid groups."""
        fund = FundFactory()
        event_date = date(2024, 1, 1)
        
        # Create events in the same group with same date
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
            event_date=event_date,
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        db_session.add_all([event1, event2])
        db_session.flush()
        
        # Validation should pass
        FundEvent.validate_group_date_consistency(db_session, 123, event_date)
    
    def test_validate_group_date_consistency_invalid(self, db_session):
        """Test date consistency validation fails for invalid groups."""
        fund = FundFactory()
        event_date = date(2024, 1, 1)
        
        # Create events in the same group with different dates
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
            event_date=date(2024, 1, 2),  # Different date
            amount=15.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        event2.set_grouping(123, GroupType.INTEREST_WITHHOLDING, 1)
        
        db_session.add_all([event1, event2])
        db_session.flush()
        
        # Validation should fail
        with pytest.raises(ValueError, match="All events in group 123 must have the same event_date"):
            FundEvent.validate_group_date_consistency(db_session, 123, event_date)
    
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
        """Test that interest distributions with withholding tax are automatically grouped."""
        fund = FundFactory()
        
        # Create an interest distribution with withholding tax
        distribution_event, tax_event = fund.add_distribution(
            event_date=date(2024, 1, 15),
            distribution_type=DistributionType.INTEREST,
            has_withholding_tax=True,
            gross_interest_amount=1000.0,
            withholding_tax_amount=150.0,
            description="Interest distribution with withholding tax",
            reference_number="REF123"
        )
        
        # Verify both events are grouped together
        assert distribution_event.is_grouped is True
        assert tax_event.is_grouped is True
        assert distribution_event.group_id == tax_event.group_id
        assert distribution_event.group_type == GroupType.INTEREST_WITHHOLDING
        assert tax_event.group_type == GroupType.INTEREST_WITHHOLDING
        assert distribution_event.group_position == 0  # First in group
        assert tax_event.group_position == 1  # Second in group
        
        # Verify the group_id is unique and sequential
        assert distribution_event.group_id > 0
