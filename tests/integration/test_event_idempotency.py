"""
Integration tests for system event idempotency.

Tests that events can be safely re-run without side effects,
and that duplicate event prevention works correctly.
"""

import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from tests.factories import FundFactory, EntityFactory, InvestmentCompanyFactory
from src.fund.models import Fund, FundEvent, FundType, EventType


class TestEventIdempotency:
    """Test that events can be safely re-run without side effects."""

    def test_capital_call_idempotency(self, db_session):
        """Test that capital call can be safely re-run with same parameters."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial state
        initial_balance = fund.current_equity_balance
        initial_event_count = len(fund.get_all_fund_events())
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Record state after first call
        after_first_call_balance = fund.current_equity_balance
        after_first_call_events = len(fund.get_all_fund_events())
        
        # Try to add the same capital call again (should be idempotent)
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Verify no change in state
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == after_first_call_balance
        assert len(fund.get_all_fund_events()) == after_first_call_events
        
        # Verify only one event was created
        events = fund.get_all_fund_events()
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 1

    def test_nav_update_idempotency(self, db_session):
        """Test that NAV update can be safely re-run with same parameters."""
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
        
        # Record state after first NAV update
        after_first_nav_events = len(fund.get_all_fund_events())
        
        # Try to add the same NAV update again (should be idempotent)
        fund.add_nav_update(
            nav_per_share=10.0,
            date=date(2023, 1, 1),
            description="Initial NAV"
        )
        db_session.commit()
        
        # Verify no change in event count
        fund = db_session.query(Fund).get(fund.id)
        assert len(fund.get_all_fund_events()) == after_first_nav_events
        
        # Verify only one NAV event was created
        events = fund.get_all_fund_events()
        nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
        assert len(nav_events) == 1

    def test_distribution_idempotency(self, db_session):
        """Test that distribution can be safely re-run with same parameters."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add distribution
        fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type="income",
            distribution_amount=5000.0,
            description="Income distribution"
        )
        db_session.commit()
        
        # Record state after first distribution
        after_first_dist_events = len(fund.get_all_fund_events())
        
        # Try to add the same distribution again (should be idempotent)
        fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type="income",
            distribution_amount=5000.0,
            description="Income distribution"
        )
        db_session.commit()
        
        # Verify no change in event count
        fund = db_session.query(Fund).get(fund.id)
        assert len(fund.get_all_fund_events()) == after_first_dist_events
        
        # Verify only one distribution event was created
        events = fund.get_all_fund_events()
        dist_events = [e for e in events if e.event_type == EventType.DISTRIBUTION]
        assert len(dist_events) == 1


class TestDuplicateEventPrevention:
    """Test that duplicate events are prevented based on business rules."""

    def test_duplicate_capital_call_same_date_amount(self, db_session):
        """Test that duplicate capital calls on same date with same amount are prevented."""
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
        
        # Try to add duplicate capital call
        with pytest.raises(ValueError, match="Duplicate event"):
            fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        
        # Verify no duplicate event was created
        events = fund.get_all_fund_events()
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 1

    def test_duplicate_nav_update_same_date(self, db_session):
        """Test that duplicate NAV updates on same date are prevented."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add NAV update
        fund.add_nav_update(
            nav_per_share=10.0,
            date=date(2023, 1, 1),
            description="Initial NAV"
        )
        db_session.commit()
        
        # Try to add duplicate NAV update
        with pytest.raises(ValueError, match="Duplicate NAV update"):
            fund.add_nav_update(
                nav_per_share=11.0,  # Different NAV value
                date=date(2023, 1, 1),  # Same date
                description="Updated NAV"
            )
        
        # Verify no duplicate event was created
        events = fund.get_all_fund_events()
        nav_events = [e for e in events if e.event_type == EventType.NAV_UPDATE]
        assert len(nav_events) == 1

    def test_duplicate_distribution_same_date_type_amount(self, db_session):
        """Test that duplicate distributions on same date with same type and amount are prevented."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add distribution
        fund.add_distribution(
            event_date=date(2023, 6, 1),
            distribution_type="income",
            distribution_amount=5000.0,
            description="Income distribution"
        )
        db_session.commit()
        
        # Try to add duplicate distribution
        with pytest.raises(ValueError, match="Duplicate distribution"):
            fund.add_distribution(
                event_date=date(2023, 6, 1),
                distribution_type="income",
                distribution_amount=5000.0,
                description="Income distribution"
            )
        
        # Verify no duplicate event was created
        events = fund.get_all_fund_events()
        dist_events = [e for e in events if e.event_type == EventType.DISTRIBUTION]
        assert len(dist_events) == 1


class TestEventReplayRecovery:
    """Test that events can be replayed for recovery scenarios."""

    def test_capital_call_replay_after_rollback(self, db_session):
        """Test that capital call can be replayed after a rollback scenario."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Simulate a failed transaction (rollback)
        try:
            fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
            # Simulate some error that causes rollback
            raise Exception("Simulated error")
        except Exception:
            db_session.rollback()
        
        # Verify no event was persisted
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 0.0
        assert len(fund.get_all_fund_events()) == 0
        
        # Replay the capital call (should work)
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call")
        db_session.commit()
        
        # Verify event was created successfully
        fund = db_session.query(Fund).get(fund.id)
        assert fund.current_equity_balance == 50000.0
        assert len(fund.get_all_fund_events()) == 1

    def test_nav_update_replay_after_rollback(self, db_session):
        """Test that NAV update can be replayed after a rollback scenario."""
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Simulate a failed transaction (rollback)
        try:
            fund.add_nav_update(
                nav_per_share=10.0,
                date=date(2023, 1, 1),
                description="Initial NAV"
            )
            # Simulate some error that causes rollback
            raise Exception("Simulated error")
        except Exception:
            db_session.rollback()
        
        # Verify no event was persisted
        fund = db_session.query(Fund).get(fund.id)
        assert len(fund.get_all_fund_events()) == 0
        
        # Replay the NAV update (should work)
        fund.add_nav_update(
            nav_per_share=10.0,
            date=date(2023, 1, 1),
            description="Initial NAV"
        )
        db_session.commit()
        
        # Verify event was created successfully
        fund = db_session.query(Fund).get(fund.id)
        assert len(fund.get_all_fund_events()) == 1
        assert fund.current_unit_price == 10.0
