"""
Integration tests for complete cash flow workflows.

Tests end-to-end cash flow processes including:
- Creating cash flows for different event types
- Reconciliation across multiple cash flows
- Withholding tax integration
- Completion flag management
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal

from tests.factories import (
    BankFactory, BankAccountFactory, FundEventCashFlowFactory,
    EntityFactory, FundFactory, FundEventFactory, TaxStatementFactory
)
from src.fund.models import (
    EventType, DistributionType, TaxPaymentType, CashFlowDirection,
    FundEventCashFlow
)
from src.tax.models import TaxStatement


class TestCompleteCashFlowWorkflows:
    """Test complete cash flow workflows from creation to reconciliation"""

    def test_capital_call_workflow_with_single_cash_flow(self, db_session):
        """Test complete workflow for capital call with single cash flow"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create capital call event
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=50000.0,
            event_date=date(2024, 1, 15)
        )
        
        # Initially no cash flows, completion should be False
        assert event.is_cash_flow_complete is False
        
        # Add cash flow
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=50000.0,
            currency="AUD",
            transfer_date=date(2024, 1, 16),
            direction=CashFlowDirection.OUTFLOW
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion
        assert event.is_cash_flow_complete is True
        
        # Verify cash flow was created correctly
        assert len(event.cash_flows) == 1
        assert event.cash_flows[0].amount == 50000.0
        assert event.cash_flows[0].direction == CashFlowDirection.OUTFLOW

    def test_distribution_workflow_with_withholding_tax(self, db_session):
        """Test complete workflow for interest distribution with withholding tax"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create distribution event with GROSS amount (before withholding)
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            amount=11500.0,  # Gross amount before withholding (10000 + 1500)
            event_date=date(2024, 6, 30),
            distribution_type=DistributionType.INTEREST
        )
        
        # Create corresponding withholding tax payment
        tax_statement = TaxStatementFactory.create(
            fund=fund,
            entity=entity,
            financial_year=2024
        )
        
        withholding_event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.TAX_PAYMENT,
            amount=1500.0,  # 15% withholding
            event_date=date(2024, 6, 30),
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
            tax_statement_id=tax_statement.id
        )
        
        # Add cash flow for net distribution (what investor actually received)
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=10000.0,  # Net amount received (gross - withholding)
            currency="AUD",
            transfer_date=date(2024, 7, 2),
            direction=CashFlowDirection.INFLOW
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion - should reconcile against net amount (10000) after withholding adjustment
        assert event.is_cash_flow_complete is True
        
        # Verify cash flow details
        assert len(event.cash_flows) == 1
        assert event.cash_flows[0].amount == 10000.0
        assert event.cash_flows[0].direction == CashFlowDirection.INFLOW

    def test_multi_cash_flow_workflow(self, db_session):
        """Test workflow with multiple cash flows for same event"""
        # Setup
        entity = EntityFactory.create()
        bank1 = BankFactory.create(name="Bank 1")
        bank2 = BankFactory.create(name="Bank 2")
        account1 = BankAccountFactory.create(entity=entity, bank=bank1, currency="AUD")
        account2 = BankAccountFactory.create(entity=entity, bank=bank2, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create large capital call event
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=200000.0,
            event_date=date(2024, 3, 1)
        )
        
        # Add first cash flow (partial)
        cash_flow1 = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account1,
            amount=120000.0,
            currency="AUD",
            transfer_date=date(2024, 3, 2),
            direction=CashFlowDirection.OUTFLOW
        )
        
        # Initially incomplete
        event._recompute_cash_flow_completion(session=db_session)
        assert event.is_cash_flow_complete is False
        
        # Add second cash flow (remaining amount)
        cash_flow2 = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account2,
            amount=80000.0,
            currency="AUD",
            transfer_date=date(2024, 3, 5),
            direction=CashFlowDirection.OUTFLOW
        )
        
        # Now should be complete
        event._recompute_cash_flow_completion(session=db_session)
        assert event.is_cash_flow_complete is True
        
        # Verify both cash flows
        assert len(event.cash_flows) == 2
        total_cash_flows = sum(cf.amount for cf in event.cash_flows)
        assert total_cash_flows == 200000.0

    def test_cross_currency_workflow(self, db_session):
        """Test workflow with cross-currency cash flows (should skip reconciliation)"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        aud_account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        usd_account = BankAccountFactory.create(entity=entity, bank=bank, currency="USD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create distribution event
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            amount=10000.0,
            event_date=date(2024, 8, 15),
            distribution_type=DistributionType.DIVIDEND_FRANKED
        )
        
        # Add AUD cash flow
        aud_cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=aud_account,
            amount=8000.0,
            currency="AUD",
            transfer_date=date(2024, 8, 16),
            direction=CashFlowDirection.INFLOW
        )
        
        # Add USD cash flow
        usd_cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=usd_account,
            amount=1500.0,  # USD equivalent
            currency="USD",
            transfer_date=date(2024, 8, 16),
            direction=CashFlowDirection.INFLOW
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Cross-currency should skip reconciliation, completion remains False
        assert event.is_cash_flow_complete is False
        
        # Verify both cash flows exist
        assert len(event.cash_flows) == 2
        aud_flows = [cf for cf in event.cash_flows if cf.currency == "AUD"]
        usd_flows = [cf for cf in event.cash_flows if cf.currency == "USD"]
        assert len(aud_flows) == 1
        assert len(usd_flows) == 1

    def test_cash_flow_removal_workflow(self, db_session):
        """Test workflow for removing cash flows and updating completion"""
        # Setup
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create event with cash flow
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=25000.0,
            event_date=date(2024, 4, 10)
        )
        
        # Add cash flow
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=25000.0,
            currency="AUD",
            transfer_date=date(2024, 4, 11),
            direction=CashFlowDirection.OUTFLOW
        )
        
        # Verify completion
        event._recompute_cash_flow_completion(session=db_session)
        assert event.is_cash_flow_complete is True
        
        # Remove cash flow
        event.remove_cash_flow(cash_flow.id, session=db_session)
        
        # Refresh the event from database to ensure we have latest state
        db_session.refresh(event)
        
        # Verify completion is now False
        event._recompute_cash_flow_completion(session=db_session)
        assert event.is_cash_flow_complete is False
        assert len(event.cash_flows) == 0
