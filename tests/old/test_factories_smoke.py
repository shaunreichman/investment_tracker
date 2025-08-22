"""
Smoke test for all factories to ensure they work correctly.
This is a quick validation that our test data generation works.
"""

import pytest
from tests.factories import (
    BankFactory, BankAccountFactory, FundEventCashFlowFactory,
    EntityFactory, FundFactory, FundEventFactory
)
from src.fund.models import EventType


def test_bank_factory_creates_valid_bank():
    """Test that BankFactory creates valid Bank objects"""
    bank = BankFactory.build()
    
    assert bank.name is not None
    assert bank.country == "AU"
    assert bank.swift_bic is not None
    assert len(bank.swift_bic) == 8  # SWIFT BIC format


def test_bank_account_factory_creates_valid_account():
    """Test that BankAccountFactory creates valid BankAccount objects"""
    account = BankAccountFactory.build()
    
    assert account.entity is not None
    assert account.bank is not None
    assert account.account_name is not None
    assert account.account_number is not None
    assert account.currency == "AUD"
    assert account.is_active is True


def test_fund_event_cash_flow_factory_creates_valid_cash_flow():
    """Test that FundEventCashFlowFactory creates valid FundEventCashFlow objects"""
    cash_flow = FundEventCashFlowFactory.build()
    
    assert cash_flow.fund_event is not None
    assert cash_flow.bank_account is not None
    assert cash_flow.direction.value in ["INFLOW", "OUTFLOW"]
    assert cash_flow.transfer_date is not None
    assert cash_flow.currency == "AUD"
    assert cash_flow.amount > 0
    assert cash_flow.reference is not None


def test_cash_flow_direction_inference():
    """Test that cash flow direction is correctly inferred from event type"""
    # Test OUTFLOW events
    CAPITAL_CALL_event = FundEventFactory.build(event_type=EventType.CAPITAL_CALL)
    cash_flow = FundEventCashFlowFactory.build(fund_event=CAPITAL_CALL_event)
    assert cash_flow.direction.value == "OUTFLOW"
    
    # Test INFLOW events
    distribution_event = FundEventFactory.build(event_type=EventType.DISTRIBUTION)
    cash_flow = FundEventCashFlowFactory.build(fund_event=distribution_event)
    assert cash_flow.direction.value == "INFLOW"


def test_factory_relationships():
    """Test that factory relationships are properly established"""
    # Create a complete chain
    entity = EntityFactory.build()
    bank = BankFactory.build()
    account = BankAccountFactory.build(entity=entity, bank=bank)
    fund = FundFactory.build(entity=entity)
    event = FundEventFactory.build(fund=fund)
    cash_flow = FundEventCashFlowFactory.build(
        fund_event=event, 
        bank_account=account
    )
    
    # Verify relationships
    assert cash_flow.fund_event == event
    assert cash_flow.bank_account == account
    assert account.entity == entity
    assert account.bank == bank
    assert event.fund == fund
    assert fund.entity == entity
