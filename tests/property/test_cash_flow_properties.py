"""
Property-based tests for cash flow reconciliation invariants.

Tests mathematical properties and edge cases of the reconciliation logic:
- Reconciliation mathematical invariants
- Edge case validation
- Boundary condition testing
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from hypothesis.extra.numpy import arrays
import numpy as np
from datetime import date, timedelta

from tests.factories import (
    BankFactory, BankAccountFactory, FundEventCashFlowFactory,
    EntityFactory, FundFactory, FundEventFactory
)
from src.fund.models import (
    EventType, DistributionType, CashFlowDirection
)


class TestCashFlowReconciliationProperties:
    """Test mathematical properties of cash flow reconciliation"""

    @given(
        target_amount=st.floats(min_value=0.01, max_value=1000000.0),
        tolerance=st.floats(min_value=0.001, max_value=0.005)  # Keep within 0.01 fund tolerance
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_reconciliation_tolerance_property(self, db_session, target_amount, tolerance):
        """Test that reconciliation succeeds when difference is within tolerance"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event with target amount
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=target_amount
        )
        
        # Add cash flow within tolerance
        cash_flow_amount = target_amount + (tolerance * 0.5)  # Within tolerance
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=cash_flow_amount,
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Should be complete when within tolerance
        assert event.is_cash_flow_complete is True

    @given(
        base_amount=st.floats(min_value=100.0, max_value=10000.0),
        cash_flow_count=st.integers(min_value=1, max_value=5)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_multi_cash_flow_sum_property(self, db_session, base_amount, cash_flow_count):
        """Test that multiple cash flows sum correctly for reconciliation"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event with target amount
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=base_amount
        )
        
        # Create multiple cash flows that sum to target
        cash_flow_amounts = []
        remaining = base_amount
        
        for i in range(cash_flow_count - 1):
            if remaining <= 0:
                break
            # Random amount up to remaining
            amount = min(remaining, np.random.uniform(1.0, remaining * 0.8))
            cash_flow_amounts.append(amount)
            remaining -= amount
        
        # Add final cash flow for remaining amount
        if remaining > 0:
            cash_flow_amounts.append(remaining)
        
        # Create cash flows
        for cf_amount in cash_flow_amounts:
            FundEventCashFlowFactory.create(
                fund_event=event,
                bank_account=account,
                amount=cf_amount,
                currency="AUD"
            )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Should be complete when sum equals target
        total_cash_flows = sum(cf.amount for cf in event.cash_flows)
        assert abs(total_cash_flows - base_amount) < 0.01
        assert event.is_cash_flow_complete is True

    @given(
        target_amount=st.floats(min_value=100.0, max_value=10000.0),
        excess_amount=st.floats(min_value=0.02, max_value=100.0)  # Must exceed 0.01 tolerance
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_reconciliation_excess_amount_property(self, db_session, target_amount, excess_amount):
        """Test that reconciliation fails when cash flows exceed target amount beyond tolerance"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event with target amount
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=target_amount
        )
        
        # Add cash flow that exceeds target beyond tolerance
        cash_flow_amount = target_amount + excess_amount
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=cash_flow_amount,
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Should not be complete when amount exceeds target beyond tolerance
        assert event.is_cash_flow_complete is False

    @given(
        target_amount=st.floats(min_value=100.0, max_value=10000.0),
        shortfall_amount=st.floats(min_value=0.02, max_value=100.0)  # Must exceed 0.01 tolerance
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_reconciliation_shortfall_property(self, db_session, target_amount, shortfall_amount):
        """Test that reconciliation fails when cash flows are less than target amount beyond tolerance"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event with target amount
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=target_amount
        )
        
        # Add cash flow that is less than target beyond tolerance
        cash_flow_amount = max(0.01, target_amount - shortfall_amount)
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=cash_flow_amount,
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Should not be complete when amount is less than target beyond tolerance
        assert event.is_cash_flow_complete is False

    @given(
        amounts=st.lists(
            st.floats(min_value=0.01, max_value=1000.0),
            min_size=1, max_size=10
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_cash_flow_direction_consistency_property(self, db_session, amounts):
        """Test that cash flow directions are consistent with event types"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Test different event types
        event_types = [
            (EventType.CAPITAL_CALL, CashFlowDirection.OUTFLOW),
            (EventType.DISTRIBUTION, CashFlowDirection.INFLOW),
            (EventType.RETURN_OF_CAPITAL, CashFlowDirection.INFLOW),
            (EventType.UNIT_PURCHASE, CashFlowDirection.OUTFLOW),
            (EventType.UNIT_SALE, CashFlowDirection.INFLOW)
        ]
        
        for event_type, expected_direction in event_types:
            event = FundEventFactory.create(
                fund=fund,
                event_type=event_type,
                amount=sum(amounts)
            )
            
            # Add cash flows
            for amount in amounts:
                cash_flow = FundEventCashFlowFactory.create(
                    fund_event=event,
                    bank_account=account,
                    amount=amount,
                    currency="AUD"
                )
                
                # Direction should be automatically inferred correctly
                assert cash_flow.direction == expected_direction

    @given(
        target_amount=st.floats(min_value=100.0, max_value=10000.0),
        currency_mismatch=st.booleans()
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_currency_validation_property(self, db_session, target_amount, currency_mismatch):
        """Test currency validation properties"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        if currency_mismatch:
            # Create account with different currency
            account = BankAccountFactory.create(entity=entity, bank=bank, currency="USD")
        else:
            # Create account with matching currency
            account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        
        # Create event
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=target_amount
        )
        
        if currency_mismatch:
            # Should raise error for currency mismatch when using domain method
            with pytest.raises(ValueError, match="Cash flow currency must equal BankAccount.currency"):
                event.add_cash_flow(
                    bank_account_id=account.id,
                    transfer_date=date.today(),
                    currency="AUD",  # Different from account currency (USD)
                    amount=target_amount,
                    session=db_session
                )
        else:
            # Should work for matching currency using domain method
            cash_flow = event.add_cash_flow(
                bank_account_id=account.id,
                transfer_date=date.today(),
                currency="AUD",
                amount=target_amount,
                session=db_session
            )
            assert cash_flow.currency == "AUD"
            assert cash_flow.currency == account.currency

    @given(
        target_amount=st.floats(min_value=100.0, max_value=10000.0),
        cash_flow_count=st.integers(min_value=0, max_value=3)
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_completion_flag_consistency_property(self, db_session, target_amount, cash_flow_count):
        """Test that completion flag is consistent with cash flow state"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=target_amount
        )
        
        # Initially no cash flows
        assert event.is_cash_flow_complete is False
        assert len(event.cash_flows) == 0
        
        # Add cash flows
        for i in range(cash_flow_count):
            amount = target_amount / cash_flow_count if cash_flow_count > 0 else 0
            if amount > 0:
                FundEventCashFlowFactory.create(
                    fund_event=event,
                    bank_account=account,
                    amount=amount,
                    currency="AUD"
                )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify consistency
        if cash_flow_count == 0:
            # No cash flows = not complete
            assert event.is_cash_flow_complete is False
        elif cash_flow_count == 1:
            # Single cash flow = complete if amount matches
            total_cash_flows = sum(cf.amount for cf in event.cash_flows)
            expected_complete = abs(total_cash_flows - target_amount) < 0.01
            assert event.is_cash_flow_complete == expected_complete
        else:
            # Multiple cash flows = complete if sum matches
            total_cash_flows = sum(cf.amount for cf in event.cash_flows)
            expected_complete = abs(total_cash_flows - target_amount) < 0.01
            assert event.is_cash_flow_complete == expected_complete
