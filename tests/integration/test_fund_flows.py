"""
Integration tests for fund cash flows and equity balance calculations.

Tests that fund events correctly update equity balances,
and that capital chain recalculations work properly.
"""

import pytest
from datetime import date

from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory
from src.fund.models import Fund, FundType, EventType, DistributionType


class TestCostBasedFundFlows:
    """Test cash flows for cost-based funds."""

    def test_capital_call_updates_equity_balance(self, db_session):
        """Test that capital call correctly updates equity balance."""
        # Setup
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial state
        assert fund.current_equity_balance == 0.0
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Verify equity balance updated
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Verify event was created
        events = fund.get_all_fund_events()
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 1
        assert capital_call_events[0].amount == 50000.0

    def test_capital_return_reduces_equity_balance(self, db_session):
        """Test that capital return correctly reduces equity balance."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call first
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Verify initial state
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Add capital return
        fund.add_return_of_capital(30000.0, date(2023, 6, 1), "Partial capital return", session=db_session)
        db_session.commit()
        
        # Verify equity balance reduced
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 20000.0
        
        # Verify both events exist
        events = fund.get_all_fund_events()
        assert len(events) == 2
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        capital_return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(capital_call_events) == 1
        assert len(capital_return_events) == 1

    def test_distribution_does_not_affect_equity_balance(self, db_session):
        """Test that distributions don't affect equity balance (only capital movements do)."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Record equity balance before distribution
        fund = db_session.query(Fund).get(fund.id)
        equity_before_distribution = fund.current_equity_balance
        
        # Add distribution
        fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type=DistributionType.INCOME,
            distribution_amount=5000.0,
            description="Income distribution",
            session=db_session
        )
        db_session.commit()
        
        # Verify equity balance unchanged
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == equity_before_distribution
        
        # Verify distribution event was created
        events = fund.get_all_fund_events()
        distribution_events = [e for e in events if e.event_type == EventType.DISTRIBUTION]
        assert len(distribution_events) == 1

    def test_capital_chain_recalculation_after_capital_event(self, db_session):
        """Test that capital chain recalculates correctly after capital events."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add multiple capital calls
        fund.add_capital_call(30000.0, date(2023, 1, 1), "First capital call", session=db_session)
        fund.add_capital_call(20000.0, date(2023, 3, 1), "Second capital call", session=db_session)
        db_session.commit()
        
        # Verify total equity balance
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Add capital return
        fund.add_return_of_capital(25000.0, date(2023, 6, 1), "Partial capital return", session=db_session)
        db_session.commit()
        
        # Verify final equity balance
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 25000.0
        
        # Verify all events exist
        events = fund.get_all_fund_events()
        assert len(events) == 3
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        capital_return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(capital_call_events) == 2
        assert len(capital_return_events) == 1


class TestNAVBasedFundFlows:
    """Test cash flows for NAV-based funds."""

    def test_unit_purchase_updates_units_and_cost(self, db_session):
        """Test that unit purchase correctly updates units and cost basis."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial state
        assert fund.current_units == 0.0
        assert fund.current_unit_price == 0.0
        
        # Add unit purchase
        fund.add_unit_purchase(
            units=1000.0,
            price=10.0,
            date=date(2023, 1, 1),
            description="Initial unit purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify units and cost updated
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_units == 1000.0
        assert fund.current_unit_price == 10.0
        
        # Verify event was created
        events = fund.get_all_fund_events()
        unit_purchase_events = [e for e in events if e.event_type == EventType.UNIT_PURCHASE]
        assert len(unit_purchase_events) == 1
        assert unit_purchase_events[0].units_purchased == 1000.0
        assert unit_purchase_events[0].unit_price == 10.0

    def test_unit_sale_reduces_units_and_updates_cost_basis(self, db_session):
        """Test that unit sale correctly reduces units and updates cost basis."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add unit purchase first
        fund.add_unit_purchase(
            units=1000.0,
            price=10.0,
            date=date(2023, 1, 1),
            description="Initial unit purchase",
            session=db_session
        )
        db_session.commit()
        
        # Verify initial state
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_units == 1000.0
        
        # Add unit sale
        fund.add_unit_sale(
            units=400.0,
            price=12.0,
            date=date(2023, 6, 1),
            description="Partial unit sale",
            session=db_session
        )
        db_session.commit()
        
        # Verify units reduced
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_units == 600.0
        
        # Verify both events exist
        events = fund.get_all_fund_events()
        assert len(events) == 2
        unit_purchase_events = [e for e in events if e.event_type == EventType.UNIT_PURCHASE]
        unit_sale_events = [e for e in events if e.event_type == EventType.UNIT_SALE]
        assert len(unit_purchase_events) == 1
        assert len(unit_sale_events) == 1


class TestFundStatusUpdates:
    """Test that fund status updates correctly based on equity balance."""

    def test_fund_status_active_when_equity_positive(self, db_session):
        """Test that fund status remains ACTIVE when equity balance > 0."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Verify status is ACTIVE
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status.value == "active"
        assert fund.current_equity_balance > 0

    def test_fund_status_realized_when_equity_zero(self, db_session):
        """Test that fund status changes to REALIZED when equity balance = 0."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Verify initial state
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Return all capital
        fund.add_return_of_capital(50000.0, date(2023, 6, 1), "Full capital return", session=db_session)
        db_session.commit()
        
        # Verify status is REALIZED
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status.value == "realized"
        assert fund.current_equity_balance == 0.0
