"""
Integration tests for complete capital call workflows.

This file focuses ONLY on capital call workflow testing, consolidating
all capital call related integration tests into a single, focused location.

Tests end-to-end capital call processes including:
- Capital call creation and validation
- Equity balance updates
- Cash flow integration
- Event system coordination
- Business rule enforcement
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
from src.fund.services.fund_service import FundService


class TestCapitalCallWorkflow:
    """Test complete capital call workflows from creation to completion"""

    def test_basic_capital_call_workflow(self, db_session):
        """Test basic capital call workflow with equity balance update"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with cost-based tracking
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Initial state validation
        assert fund.current_equity_balance == 0.0
        assert fund.total_capital_called(session=db_session) == 0.0
        assert fund.remaining_commitment == 100000.0
        
        # Execute capital call
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_capital_call(fund, 50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Verify fund state updates
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 50000.0
        assert fund.total_capital_called(session=db_session) == 50000.0
        assert fund.remaining_commitment == 50000.0
        
        # Verify event creation
        events = fund.get_all_fund_events(session=db_session)
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 1
        assert capital_call_events[0].amount == 50000.0
        assert capital_call_events[0].event_date == date(2023, 1, 1)
        assert capital_call_events[0].description == "Initial capital call"

    def test_capital_call_with_cash_flow_integration(self, db_session):
        """Test capital call workflow with cash flow creation and reconciliation"""
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
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0,
            currency="AUD"
        )
        db_session.commit()
        
        # Create capital call event
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_capital_call(fund, 50000.0, date(2023, 1, 15), "Capital call with cash flow", session=db_session)
        db_session.commit()
        
        # Add cash flow for the capital call
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=50000.0,
            currency="AUD",
            transfer_date=date(2023, 1, 16),
            direction=CashFlowDirection.OUTFLOW
        )
        db_session.commit()
        
        # Verify cash flow was created and linked
        assert len(event.cash_flows) == 1
        assert event.cash_flows[0].amount == 50000.0
        assert event.cash_flows[0].direction == CashFlowDirection.OUTFLOW
        assert event.cash_flows[0].transfer_date == date(2023, 1, 16)
        assert event.cash_flows[0].fund_event_id == event.id

    def test_multiple_capital_calls_workflow(self, db_session):
        """Test multiple capital calls workflow with cumulative tracking"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Initial state
        assert fund.current_equity_balance == 0.0
        assert fund.total_capital_called(session=db_session) == 0.0
        assert fund.remaining_commitment == 200000.0
        
        # First capital call
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_capital_call(fund, 75000.0, date(2023, 1, 1), "First capital call", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 75000.0
        assert fund.total_capital_called(session=db_session) == 75000.0
        assert fund.remaining_commitment == 125000.0
        
        # Second capital call
        fund_event_service.add_capital_call(fund, 50000.0, date(2023, 3, 1), "Second capital call", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 125000.0
        assert fund.total_capital_called(session=db_session) == 125000.0
        assert fund.remaining_commitment == 75000.0
        
        # Verify all events exist
        events = fund.get_all_fund_events(session=db_session)
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 2
        
        # Verify event amounts and dates
        event_amounts = [e.amount for e in capital_call_events]
        event_dates = [e.event_date for e in capital_call_events]
        assert 75000.0 in event_amounts
        assert 50000.0 in event_amounts
        assert date(2023, 1, 1) in event_dates
        assert date(2023, 3, 1) in event_dates

    def test_capital_call_business_rules_validation(self, db_session):
        """Test capital call business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Test: Cannot call more than remaining commitment
        with pytest.raises(ValueError, match="Cannot call more capital than remaining commitment"):
            from src.fund.services.fund_event_service import FundEventService
            fund_event_service = FundEventService()
            fund_event_service.add_capital_call(fund, 150000.0, date(2023, 1, 1), "Excessive capital call", session=db_session)
        
        # Test: Cannot call negative amount
        with pytest.raises(ValueError, match="Capital call amount must be a positive number"):
            fund_event_service.add_capital_call(fund, -10000.0, date(2023, 1, 1), "Negative capital call", session=db_session)
        
        # Test: Cannot call zero amount
        with pytest.raises(ValueError, match="Capital call amount must be a positive number"):
            fund_event_service.add_capital_call(fund, 0.0, date(2023, 1, 1), "Zero capital call", session=db_session)
        
        # Test: Valid capital call should work
        fund_event_service.add_capital_call(fund, 50000.0, date(2023, 1, 1), "Valid capital call", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 50000.0
        assert fund.remaining_commitment == 50000.0

    def test_nav_based_fund_restricts_capital_calls(self, db_session):
        """Test that NAV-based funds correctly restrict capital calls"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # NAV-based funds should not allow capital calls
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        with pytest.raises(ValueError, match="Capital calls are only applicable for cost-based funds"):
            fund_event_service.add_capital_call(fund, 40000.0, date(2023, 1, 1), "NAV-based capital call", session=db_session)
        
        # Verify no events were created
        events = fund.get_all_fund_events(session=db_session)
        assert len(events) == 0

    def test_capital_call_event_metadata_validation(self, db_session):
        """Test capital call event metadata and validation"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Create capital call with specific metadata
        call_date = date(2023, 1, 15)
        description = "Test capital call with metadata"
        amount = 30000.0
        
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        event = fund_event_service.add_capital_call(fund, amount, call_date, description, session=db_session)
        db_session.commit()
        
        # Verify event metadata
        assert event.event_type == EventType.CAPITAL_CALL
        assert event.amount == amount
        assert event.event_date == call_date
        assert event.description == description
        assert event.fund_id == fund.id
        
        # Verify event is properly linked to fund
        assert event.fund == fund
        assert event in fund.fund_events

    def test_capital_call_workflow_transaction_integrity(self, db_session):
        """Test capital call workflow maintains transaction integrity"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Record initial state
        initial_equity = fund.current_equity_balance
        initial_called = fund.total_capital_called(session=db_session)
        initial_remaining = fund.remaining_commitment
        
        # Execute capital call
        from src.fund.services.fund_event_service import FundEventService
        fund_event_service = FundEventService()
        fund_event_service.add_capital_call(fund, 25000.0, date(2023, 1, 1), "Transaction test call", session=db_session)
        db_session.commit()
        
        # Verify all related state changes are consistent
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == initial_equity + 25000.0
        assert fund.total_capital_called(session=db_session) == initial_called + 25000.0
        assert fund.remaining_commitment == initial_remaining - 25000.0
        
        # Verify the sum of called and remaining equals total commitment
        assert fund.total_capital_called(session=db_session) + fund.remaining_commitment == fund.commitment_amount
        
        # Verify event count increased by exactly one
        events = fund.get_all_fund_events(session=db_session)
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        assert len(capital_call_events) == 1
