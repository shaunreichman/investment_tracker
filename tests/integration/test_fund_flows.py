"""
Integration tests for fund flows with database persistence.

Tests the cost/NAV calculations, capital movements, and derived field updates
that require database interaction and session management.
"""

import pytest
from datetime import date
from decimal import Decimal

from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory
from src.fund.models import Fund, FundEvent, FundType, EventType


class TestCostBasedFundFlows:
    """Test cost-based fund flows (capital calls, returns, distributions)."""

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
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Verify equity balance updated
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Verify event created
        events = fund.get_all_fund_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.CAPITAL_CALL
        assert events[0].amount == 50000.0

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
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Return some capital
        fund.add_return_of_capital(20000.0, date(2023, 6, 1), "Partial capital return")
        db_session.commit()
        
        # Verify equity balance reduced
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 30000.0
        
        # Verify events created
        events = fund.get_all_fund_events()
        assert len(events) == 2
        assert events[1].event_type == EventType.RETURN_OF_CAPITAL
        assert events[1].amount == 20000.0

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
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Add distribution
        fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type="income",
            distribution_amount=5000.0,
            description="Income distribution"
        )
        db_session.commit()
        
        # Verify equity balance unchanged (distributions don't affect it)
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Verify events created
        events = fund.get_all_fund_events()
        assert len(events) == 2
        assert events[1].event_type == EventType.DISTRIBUTION
        assert events[1].amount == 5000.0

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
        fund.add_capital_call(30000.0, date(2023, 1, 1), "First capital call")
        fund.add_capital_call(20000.0, date(2023, 3, 1), "Second capital call")
        db_session.commit()
        
        # Verify cumulative equity balance
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        
        # Return capital (should recalculate from this point)
        fund.add_return_of_capital(15000.0, date(2023, 6, 1), "Partial return")
        db_session.commit()
        
        # Verify final equity balance
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 35000.0


class TestNAVBasedFundFlows:
    """Test NAV-based fund flows (unit purchases, sales, NAV updates)."""

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
            description="Initial unit purchase"
        )
        db_session.commit()
        
        # Verify units and cost updated
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_units == 1000.0
        assert fund.current_unit_price == 10.0
        
        # Verify event created
        events = fund.get_all_fund_events()
        assert len(events) == 1
        assert events[0].event_type == EventType.UNIT_PURCHASE
        assert events[0].units_purchased == 1000.0
        assert events[0].unit_price == 10.0

    def test_nav_update_calculates_nav_change_fields(self, db_session):
        """Test that NAV update correctly calculates change fields."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add initial NAV
        fund.add_nav_update(
            nav_per_share=10.0,
            date=date(2023, 1, 1),
            description="Initial NAV"
        )
        db_session.commit()
        
        # Update NAV
        fund.add_nav_update(
            nav_per_share=11.0,
            date=date(2023, 3, 1),
            description="NAV increase"
        )
        db_session.commit()
        
        # Verify NAV change fields calculated
        events = fund.get_all_fund_events()
        nav_event = events[1]  # Second event
        assert nav_event.nav_change_absolute == 1.0
        assert nav_event.nav_change_percentage == 10.0  # 10% increase
        assert nav_event.previous_nav_per_share == 10.0

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
            description="Initial unit purchase"
        )
        db_session.commit()
        
        # Sell some units
        fund.add_unit_sale(
            units=400.0,
            price=12.0,
            date=date(2023, 6, 1),
            description="Partial unit sale"
        )
        db_session.commit()
        
        # Verify units reduced
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_units == 600.0
        
        # Verify event created
        events = fund.get_all_fund_events()
        assert len(events) == 2
        assert events[1].event_type == EventType.UNIT_SALE
        assert events[1].units_sold == 400.0
        assert events[1].unit_price == 12.0


class TestFundStatusUpdates:
    """Test fund status updates based on equity balance and events."""

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
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Verify status is ACTIVE
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status.value == "active"

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
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Return all capital
        fund.add_return_of_capital(50000.0, date(2023, 6, 1), "Full capital return")
        db_session.commit()
        
        # Verify status is REALIZED
        fund = db_session.query(Fund).get(fund.id)
        assert fund.status.value == "realized"
        assert fund.current_equity_balance == 0.0
