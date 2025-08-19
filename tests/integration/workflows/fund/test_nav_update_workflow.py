"""
Integration tests for complete NAV update workflows.

This file focuses ONLY on NAV update workflow testing, consolidating
all NAV update related integration tests into a single, focused location.

Tests end-to-end NAV update processes including:
- NAV update creation and validation
- NAV change calculations and tracking
- Unit price and NAV total updates
- Event system coordination
- Business rule enforcement
- NAV-based fund restrictions
- Subsequent NAV event updates
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    FundFactory, EntityFactory, InvestmentCompanyFactory,
    BankFactory, BankAccountFactory, FundEventCashFlowFactory
)
from src.fund.models import (
    Fund, FundType, EventType, CashFlowDirection,
    FundEvent, FundEventCashFlow
)
from src.fund.enums import FundType


class TestNAVUpdateWorkflow:
    """Test complete NAV update workflows from creation to completion"""

    def test_basic_nav_update_workflow(self, db_session):
        """Test basic NAV update workflow with unit price and NAV total updates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            current_units=1000.0  # Start with some units
        )
        db_session.commit()
        
        # Initial state validation
        assert fund.current_unit_price == 0.0
        assert fund.current_nav_total == 0.0
        assert fund.tracking_type == FundType.NAV_BASED
        
        # Execute NAV update
        event = fund.add_nav_update(25.50, date(2023, 6, 1), "Initial NAV update", session=db_session)
        db_session.commit()
        
        # Verify fund state updates
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 25.50
        assert fund.current_nav_total == 25500.0  # 1000 units * $25.50
        
        # Verify event creation
        assert event is not None
        assert event.event_type == EventType.NAV_UPDATE
        assert event.nav_per_share == 25.50
        assert event.event_date == date(2023, 6, 1)
        assert event.description == "Initial NAV update"
        assert event.nav_change_absolute is None  # First NAV update
        assert event.nav_change_percentage is None  # First NAV update
        assert event.previous_nav_per_share is None  # First NAV update

    def test_nav_update_with_change_calculations(self, db_session):
        """Test NAV update workflow with NAV change calculations"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund with initial NAV
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            current_units=1000.0
        )
        db_session.commit()
        
        # First NAV update
        first_event = fund.add_nav_update(25.50, date(2023, 6, 1), "Initial NAV", session=db_session)
        db_session.commit()
        
        # Second NAV update with changes
        second_event = fund.add_nav_update(26.75, date(2023, 7, 1), "July NAV update", session=db_session)
        db_session.commit()
        
        # Verify second event has change calculations
        assert second_event.nav_change_absolute == 1.25  # 26.75 - 25.50
        assert abs(second_event.nav_change_percentage - 4.90) < 0.1  # (1.25/25.50)*100
        assert second_event.previous_nav_per_share == 25.50
        
        # Verify fund state updated to latest NAV
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 26.75
        assert fund.current_nav_total == 26750.0  # 1000 units * $26.75

    def test_nav_update_business_rules_validation(self, db_session):
        """Test NAV update business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test: Cannot update with negative NAV
        with pytest.raises(ValueError, match="NAV per share must be a positive number"):
            fund.add_nav_update(-10.0, date(2023, 6, 1), "Negative NAV", session=db_session)
        
        # Test: Cannot update with zero NAV
        with pytest.raises(ValueError, match="NAV per share must be a positive number"):
            fund.add_nav_update(0.0, date(2023, 6, 1), "Zero NAV", session=db_session)
        
        # Test: Cannot update with None date
        with pytest.raises(ValueError, match="Date is required"):
            fund.add_nav_update(25.50, None, "No date", session=db_session)
        
        # Test: Valid NAV update should work
        fund.add_nav_update(25.50, date(2023, 6, 1), "Valid NAV", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 25.50

    def test_cost_based_fund_restricts_nav_updates(self, db_session):
        """Test that cost-based funds correctly restrict NAV updates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create cost-based fund
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Cost-based funds should not allow NAV updates
        with pytest.raises(ValueError, match="Event requires NAV_BASED fund, but fund is COST_BASED"):
            fund.add_nav_update(25.50, date(2023, 6, 1), "Cost-based NAV update", session=db_session)
        
        # Verify no events were created
        events = fund.get_all_fund_events(session=db_session)
        assert len(events) == 0

    def test_nav_update_subsequent_event_updates(self, db_session):
        """Test that NAV updates properly update subsequent NAV events"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            current_units=1000.0
        )
        db_session.commit()
        
        # Create NAV updates in chronological order
        first_event = fund.add_nav_update(25.00, date(2023, 6, 1), "June NAV", session=db_session)
        second_event = fund.add_nav_update(26.00, date(2023, 7, 1), "July NAV", session=db_session)
        third_event = fund.add_nav_update(27.00, date(2023, 8, 1), "August NAV", session=db_session)
        db_session.commit()
        
        # Now insert a NAV update between June and July
        middle_event = fund.add_nav_update(25.50, date(2023, 6, 15), "Mid-June NAV", session=db_session)
        db_session.commit()
        
        # Verify the middle event has correct change calculations
        assert middle_event.previous_nav_per_share == 25.00
        assert middle_event.nav_change_absolute == 0.50
        assert abs(middle_event.nav_change_percentage - 2.0) < 0.1  # (0.50/25.00)*100
        
        # Verify subsequent events were updated
        second_event = db_session.get(FundEvent, second_event.id)
        third_event = db_session.get(FundEvent, third_event.id)
        
        # Second event should now reference the middle event
        assert second_event.previous_nav_per_share == 25.50
        assert second_event.nav_change_absolute == 0.50
        assert abs(second_event.nav_change_percentage - 1.96) < 0.1  # (0.50/25.50)*100
        
        # Third event should still reference the second event
        assert third_event.previous_nav_per_share == 26.00
        assert third_event.nav_change_absolute == 1.00
        assert abs(third_event.nav_change_percentage - 3.85) < 0.1  # (1.00/26.00)*100

    def test_nav_update_with_units_workflow(self, db_session):
        """Test NAV update workflow with unit purchases and NAV total calculations"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial NAV update
        fund.add_nav_update(25.00, date(2023, 6, 1), "Initial NAV", session=db_session)
        db_session.commit()
        
        # Purchase units
        fund.add_unit_purchase(1000.0, 25.00, date(2023, 6, 15), "Initial unit purchase", session=db_session)
        db_session.commit()
        
        # NAV update after unit purchase
        fund.add_nav_update(26.00, date(2023, 7, 1), "July NAV update", session=db_session)
        db_session.commit()
        
        # Verify fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1000.0
        assert fund.current_unit_price == 26.00
        assert fund.current_nav_total == 26000.0  # 1000 units * $26.00
        
        # Purchase more units
        fund.add_unit_purchase(500.0, 26.00, date(2023, 7, 15), "Additional units", session=db_session)
        db_session.commit()
        
        # NAV update after additional units
        fund.add_nav_update(27.00, date(2023, 8, 1), "August NAV update", session=db_session)
        db_session.commit()
        
        # Verify updated fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_units == 1500.0
        assert fund.current_unit_price == 27.00
        assert fund.current_nav_total == 40500.0  # 1500 units * $27.00

    def test_nav_update_idempotent_behavior(self, db_session):
        """Test that NAV updates are idempotent and don't create duplicates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # First NAV update
        first_event = fund.add_nav_update(25.50, date(2023, 6, 1), "June NAV", session=db_session)
        db_session.commit()
        
        # Try to create the same NAV update again
        second_event = fund.add_nav_update(25.50, date(2023, 6, 1), "June NAV", session=db_session)
        db_session.commit()
        
        # Should return the same event (idempotent behavior)
        assert second_event.id == first_event.id
        
        # Verify only one event exists
        events = fund.get_all_fund_events(session=db_session)
        nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
        assert len(nav_events) == 1
        
        # Verify fund state unchanged
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 25.50

    def test_nav_update_event_metadata_validation(self, db_session):
        """Test NAV update event metadata and validation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Create NAV update with specific metadata
        update_date = date(2023, 6, 15)
        description = "Test NAV update with metadata"
        nav_value = 30.00
        reference = "NAV001"
        
        event = fund.add_nav_update(
            nav_value, 
            update_date, 
            description, 
            reference, 
            session=db_session
        )
        db_session.commit()
        
        # Verify event metadata
        assert event.event_type == EventType.NAV_UPDATE
        assert event.nav_per_share == nav_value
        assert event.event_date == update_date
        assert event.description == description
        assert event.reference_number == reference
        assert event.fund_id == fund.id
        
        # Verify event is properly linked to fund
        assert event.fund == fund
        assert event in fund.fund_events

    def test_nav_update_workflow_transaction_integrity(self, db_session):
        """Test NAV update workflow maintains transaction integrity"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            current_units=1000.0
        )
        db_session.commit()
        
        # Record initial state
        initial_unit_price = fund.current_unit_price
        initial_nav_total = fund.current_nav_total
        
        # Execute NAV update
        fund.add_nav_update(30.00, date(2023, 6, 1), "Transaction test NAV", session=db_session)
        db_session.commit()
        
        # Verify all related state changes are consistent
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 30.00
        assert fund.current_nav_total == 30000.0  # 1000 units * $30.00
        
        # Verify the NAV total calculation is correct
        assert fund.current_nav_total == fund.current_units * fund.current_unit_price
        
        # Verify event count increased by exactly one
        events = fund.get_all_fund_events(session=db_session)
        nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
        assert len(nav_events) == 1

    def test_nav_update_with_cash_flow_integration(self, db_session):
        """Test NAV update workflow with cash flow creation and reconciliation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory, 
                       BankFactory, BankAccountFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund and bank account
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(
            entity=entity,
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            currency="AUD",
            current_units=1000.0
        )
        db_session.commit()
        
        # Create NAV update event
        event = fund.add_nav_update(25.50, date(2023, 6, 1), "NAV update with cash flow", session=db_session)
        db_session.commit()
        
        # Add cash flow for the NAV update (e.g., management fee)
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=500.0,
            currency="AUD",
            transfer_date=date(2023, 6, 2),
            direction=CashFlowDirection.OUTFLOW
        )
        db_session.commit()
        
        # Verify cash flow was created and linked
        assert len(event.cash_flows) == 1
        assert event.cash_flows[0].amount == 500.0
        assert event.cash_flows[0].direction == CashFlowDirection.OUTFLOW
        assert event.cash_flows[0].transfer_date == date(2023, 6, 2)
        assert event.cash_flows[0].fund_event_id == event.id

    def test_nav_update_performance_metrics_calculation(self, db_session):
        """Test NAV update workflow calculates performance metrics correctly"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create NAV-based fund
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0,
            current_units=1000.0
        )
        db_session.commit()
        
        # Create NAV updates over time
        fund.add_nav_update(20.00, date(2023, 1, 1), "January NAV", session=db_session)
        fund.add_nav_update(22.00, date(2023, 2, 1), "February NAV", session=db_session)
        fund.add_nav_update(21.00, date(2023, 3, 1), "March NAV", session=db_session)
        fund.add_nav_update(24.00, date(2023, 4, 1), "April NAV", session=db_session)
        db_session.commit()
        
        # Get all NAV events
        events = fund.get_all_fund_events(session=db_session)
        nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
        nav_events.sort(key=lambda x: x.event_date)
        
        # Verify NAV change calculations
        assert len(nav_events) == 4
        
        # First event (no previous NAV)
        assert nav_events[0].nav_change_absolute is None
        assert nav_events[0].nav_change_percentage is None
        
        # Second event (20 -> 22)
        assert nav_events[1].nav_change_absolute == 2.00
        assert nav_events[1].nav_change_percentage == 10.0  # (2.00/20.00)*100
        
        # Third event (22 -> 21)
        assert nav_events[2].nav_change_absolute == -1.00
        assert abs(nav_events[2].nav_change_percentage - (-4.55)) < 0.1  # (-1.00/22.00)*100
        
        # Fourth event (21 -> 24)
        assert nav_events[3].nav_change_absolute == 3.00
        assert abs(nav_events[3].nav_change_percentage - 14.29) < 0.1  # (3.00/21.00)*100
        
        # Verify final fund state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_unit_price == 24.00
        assert fund.current_nav_total == 24000.0  # 1000 units * $24.00
