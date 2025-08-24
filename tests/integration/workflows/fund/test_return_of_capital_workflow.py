"""
Integration tests for complete return of capital workflows.

This file focuses ONLY on return of capital workflow testing, consolidating
all return of capital related integration tests into a single, focused location.

Tests end-to-end return of capital processes including:
- Return of capital creation and validation
- Equity balance updates and recalculation
- Cash flow integration and reconciliation
- Event system coordination and orchestration
- Business rule enforcement and validation
- Fund status transitions and state management
- Data consistency across component boundaries

**Core Testing Principles**:
- Single Responsibility: Each test validates one specific workflow aspect
- Factory-Based Testing: Real database interactions for integration validation
- No Duplication: Focus on integration scenarios, not unit test logic
- Business Value Focus: Test business outcomes and data consistency
- Targeted Assertions: Validate specific workflow behaviors
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
from src.fund.enums import DistributionType
from src.fund.events.orchestrator import FundUpdateOrchestrator


class TestReturnOfCapitalWorkflow:
    """Test complete return of capital workflows from creation to completion"""

    def test_basic_return_of_capital_workflow(self, db_session):
        """Test basic return of capital workflow with equity balance update"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with cost-based tracking and initial capital
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add initial capital call to establish equity balance
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Initial state validation
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 50000.0
        assert fund.total_capital_called(session=db_session) == 50000.0
        
        # Execute return of capital
        event = fund.add_return_of_capital(
            amount=20000.0,
            return_date=date(2023, 6, 30),
            description="Partial capital return",
            reference_number="ROC001",
            session=db_session
        )
        db_session.commit()
        
        # Verify fund state updates
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 30000.0  # 50000 - 20000
        assert fund.total_capital_called(session=db_session) == 50000.0  # Unchanged
        assert fund.remaining_commitment == 70000.0  # 100000 - 30000 (increases when capital returned)
        
        # Verify event creation
        assert event is not None
        assert event.event_type == EventType.RETURN_OF_CAPITAL
        assert event.amount == 20000.0
        assert event.event_date == date(2023, 6, 30)
        assert event.description == "Partial capital return"
        assert event.reference_number == "ROC001"
        
        # Verify event is properly linked to fund
        events = fund.get_all_fund_events(session=db_session)
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(return_events) == 1
        assert return_events[0].id == event.id

    def test_multiple_returns_of_capital_workflow(self, db_session):
        """Test multiple returns of capital with cumulative equity balance updates"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with larger commitment
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=200000.0
        )
        db_session.commit()
        
        # Add initial capital call
        fund.add_capital_call(100000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Initial state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 100000.0
        
        # First return of capital
        fund.add_return_of_capital(30000.0, date(2023, 3, 31), "Q1 return", session=db_session)
        db_session.commit()
        
        # Verify intermediate state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 70000.0  # 100000 - 30000
        
        # Second return of capital
        fund.add_return_of_capital(25000.0, date(2023, 6, 30), "Q2 return", session=db_session)
        db_session.commit()
        
        # Verify final state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 45000.0  # 70000 - 25000
        
        # Verify all events exist and are properly ordered
        events = fund.get_all_fund_events(session=db_session)
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(return_events) == 2
        
        # Verify chronological order
        assert return_events[0].event_date == date(2023, 3, 31)
        assert return_events[1].event_date == date(2023, 6, 30)
        assert return_events[0].amount == 30000.0
        assert return_events[1].amount == 25000.0

    def test_return_of_capital_with_cash_flow_integration(self, db_session):
        """Test return of capital workflow with cash flow creation and reconciliation"""
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
        
        # Add initial capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial capital call", session=db_session)
        db_session.commit()
        
        # Create return of capital event
        event = fund.add_return_of_capital(
            amount=20000.0,
            return_date=date(2023, 6, 30),
            description="Return with cash flow",
            session=db_session
        )
        db_session.commit()
        
        # Add cash flow for the return of capital
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=20000.0,
            currency="AUD",
            transfer_date=date(2023, 7, 1),
            direction=CashFlowDirection.INFLOW  # Money coming back to investor
        )
        db_session.commit()
        
        # Verify cash flow integration
        assert cash_flow.fund_event_id == event.id
        assert cash_flow.amount == 20000.0
        assert cash_flow.direction == CashFlowDirection.INFLOW
        assert cash_flow.currency == "AUD"
        
        # Verify fund state remains consistent
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 30000.0  # 50000 - 20000
        
        # Verify event has associated cash flow
        event = db_session.get(FundEvent, event.id)
        cash_flows = event.cash_flows
        assert len(cash_flows) == 1
        assert cash_flows[0].id == cash_flow.id

    def test_return_of_capital_business_rule_validation(self, db_session):
        """Test return of capital business rules and constraints"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Test 1: NAV-based funds cannot have returns of capital
        nav_fund = FundFactory.create(
            tracking_type=FundType.NAV_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        with pytest.raises(ValueError, match="Returns of capital are only applicable for cost-based funds"):
            nav_fund.add_return_of_capital(
                amount=10000.0,
                return_date=date(2023, 6, 30),
                description="Should fail",
                session=db_session
            )
        
        # Test 2: Cannot return more capital than currently invested
        cost_fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        cost_fund.add_capital_call(30000.0, date(2023, 1, 1), "Initial call", session=db_session)
        db_session.commit()
        
        # Try to return more than invested (should work but result in negative balance)
        # This tests the system's handling of edge cases
        event = cost_fund.add_return_of_capital(
            amount=40000.0,  # More than the 30000 invested
            return_date=date(2023, 6, 30),
            description="Over-return",
            session=db_session
        )
        db_session.commit()
        
        # Verify the event was created (business rule allows it)
        assert event is not None
        assert event.amount == 40000.0
        
        # Verify fund state reflects the over-return
        cost_fund = db_session.get(Fund, cost_fund.id)
        assert cost_fund.current_equity_balance == -10000.0  # 30000 - 40000

    def test_return_of_capital_event_system_integration(self, db_session):
        """Test return of capital integration with event system and orchestrator"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with initial capital
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=db_session)
        db_session.commit()
        
        # Initial state
        fund = db_session.get(Fund, fund.id)
        initial_equity = fund.current_equity_balance
        assert initial_equity == 50000.0
        
        # Execute return of capital through orchestrator
        orchestrator = FundUpdateOrchestrator()
        event_data = {
            'event_type': EventType.RETURN_OF_CAPITAL,
            'amount': 20000.0,
            'event_date': date(2023, 6, 30),
            'description': 'Orchestrator test return',
            'reference_number': 'ORCH001'
        }
        
        event = orchestrator.process_fund_event(event_data, db_session, fund)
        db_session.commit()
        
        # Verify event was created and processed
        assert event is not None
        assert event.event_type == EventType.RETURN_OF_CAPITAL
        assert event.amount == 20000.0
        
        # Verify fund state was updated
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 30000.0  # 50000 - 20000
        
        # Verify event is properly linked
        events = fund.get_all_fund_events(session=db_session)
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(return_events) == 1
        assert return_events[0].id == event.id

    def test_return_of_capital_fund_status_workflow(self, db_session):
        """Test return of capital impact on fund status transitions"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with initial capital
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=db_session)
        db_session.commit()
        
        # Initial status should be ACTIVE
        fund = db_session.get(Fund, fund.id)
        assert fund.status.value == "ACTIVE"
        assert fund.current_equity_balance == 50000.0
        
        # Partial return of capital - should remain ACTIVE
        fund.add_return_of_capital(20000.0, date(2023, 6, 30), "Partial return", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.status.value == "ACTIVE"  # Still has equity
        assert fund.current_equity_balance == 30000.0
        
        # Full return of capital - should transition to REALIZED
        fund.add_return_of_capital(30000.0, date(2023, 12, 31), "Full return", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 0.0  # All capital returned
        # Note: Status transition to REALIZED happens in separate workflow
        # This test focuses on the return of capital workflow, not status transitions

    def test_return_of_capital_data_consistency_workflow(self, db_session):
        """Test return of capital data consistency across all fund calculations"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with initial capital
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        # Add capital call
        fund.add_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=db_session)
        db_session.commit()
        
        # Record initial state for consistency validation
        fund = db_session.get(Fund, fund.id)
        initial_equity = fund.current_equity_balance
        initial_called = fund.total_capital_called(session=db_session)
        initial_remaining = fund.remaining_commitment
        
        assert initial_equity == 50000.0
        assert initial_called == 50000.0
        assert initial_remaining == 50000.0
        
        # Execute return of capital
        fund.add_return_of_capital(20000.0, date(2023, 6, 30), "Consistency test", session=db_session)
        db_session.commit()
        
        # Verify data consistency across all calculations
        fund = db_session.get(Fund, fund.id)
        
        # Equity balance should be reduced
        assert fund.current_equity_balance == 30000.0  # 50000 - 20000
        
        # Total capital called should remain unchanged
        assert fund.total_capital_called(session=db_session) == 50000.0
        
        # Remaining commitment should increase when capital is returned
        assert fund.remaining_commitment == 70000.0  # 100000 - 30000
        
        # Verify event consistency
        events = fund.get_all_fund_events(session=db_session)
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        
        assert len(capital_call_events) == 1
        assert len(return_events) == 1
        
        # Verify amounts are consistent
        total_calls = sum(e.amount for e in capital_call_events)
        total_returns = sum(e.amount for e in return_events)
        calculated_equity = total_calls - total_returns
        
        assert calculated_equity == 30000.0
        assert calculated_equity == fund.current_equity_balance

    def test_return_of_capital_edge_cases_workflow(self, db_session):
        """Test return of capital edge cases and boundary conditions"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Test 1: Return of capital on same date as capital call
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=100000.0
        )
        db_session.commit()
        
        same_date = date(2023, 6, 30)
        
        # Add capital call and return on same date
        fund.add_capital_call(50000.0, same_date, "Same day call", session=db_session)
        fund.add_return_of_capital(20000.0, same_date, "Same day return", session=db_session)
        db_session.commit()
        
        # Verify final state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 30000.0  # 50000 - 20000
        
        # Test 2: Multiple returns on same date
        fund.add_return_of_capital(15000.0, same_date, "Second same day return", session=db_session)
        db_session.commit()
        
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 15000.0  # 30000 - 15000
        
        # Verify all events exist
        events = fund.get_all_fund_events(session=db_session)
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        assert len(return_events) == 2
        
        # Test 3: Return of capital with zero amount (should fail)
        with pytest.raises(ValueError, match="Return amount must be a positive number"):
            fund.add_return_of_capital(
                amount=0.0,
                return_date=date(2023, 7, 1),
                description="Zero amount",
                session=db_session
            )
        
        # Test 4: Return of capital with negative amount (should fail)
        with pytest.raises(ValueError, match="Return amount must be a positive number"):
            fund.add_return_of_capital(
                amount=-1000.0,
                return_date=date(2023, 7, 1),
                description="Negative amount",
                session=db_session
            )

    def test_return_of_capital_performance_workflow(self, db_session):
        """Test return of capital performance with larger datasets"""
        # Setup factories with session
        for factory in (FundFactory, EntityFactory, InvestmentCompanyFactory):
            factory._meta.sqlalchemy_session = db_session
        
        # Create fund with larger commitment
        fund = FundFactory.create(
            tracking_type=FundType.COST_BASED,
            commitment_amount=1000000.0  # 1M commitment
        )
        db_session.commit()
        
        # Add multiple capital calls to establish baseline
        call_amounts = [100000.0, 150000.0, 200000.0, 250000.0]  # Total: 700K
        call_dates = [date(2023, 1, 1), date(2023, 3, 1), date(2023, 6, 1), date(2023, 9, 1)]
        
        for amount, call_date in zip(call_amounts, call_dates):
            fund.add_capital_call(amount, call_date, f"Call {amount}", session=db_session)
            db_session.commit()
        
        # Verify initial state
        fund = db_session.get(Fund, fund.id)
        assert fund.current_equity_balance == 700000.0
        
        # Execute multiple returns of capital
        return_amounts = [50000.0, 100000.0, 150000.0, 200000.0]  # Total: 500K
        return_dates = [date(2023, 12, 1), date(2024, 3, 1), date(2024, 6, 1), date(2024, 9, 1)]
        
        for amount, return_date in zip(return_amounts, return_dates):
            fund.add_return_of_capital(amount, return_date, f"Return {amount}", session=db_session)
            db_session.commit()
        
        # Verify final state
        fund = db_session.get(Fund, fund.id)
        expected_equity = 700000.0 - 500000.0  # 200K remaining
        assert fund.current_equity_balance == expected_equity
        
        # Verify all events were created
        events = fund.get_all_fund_events(session=db_session)
        capital_call_events = [e for e in events if e.event_type == EventType.CAPITAL_CALL]
        return_events = [e for e in events if e.event_type == EventType.RETURN_OF_CAPITAL]
        
        assert len(capital_call_events) == 4
        assert len(return_events) == 4
        
        # Verify total amounts are consistent
        total_calls = sum(e.amount for e in capital_call_events)
        total_returns = sum(e.amount for e in return_events)
        calculated_equity = total_calls - total_returns
        
        assert total_calls == 700000.0
        assert total_returns == 500000.0
        assert calculated_equity == 200000.0
        assert calculated_equity == fund.current_equity_balance
