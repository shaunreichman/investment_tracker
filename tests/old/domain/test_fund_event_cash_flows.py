"""
Domain logic tests for FundEventCashFlow functionality.

Tests the core business logic for:
- Cash flow reconciliation
- Withholding tax matching
- Completion flag management
- Currency validation
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


class TestCashFlowReconciliation:
    """Test cash flow reconciliation logic"""
    
    def test_same_currency_reconciliation_success(self, db_session):
        """Test successful reconciliation when amounts match within tolerance"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund, 
            event_type=EventType.CAPITAL_CALL, 
            amount=10000.0
        )
        
        # Add cash flow that matches exactly
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=10000.0,
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is set
        assert event.is_cash_flow_complete is True
    
    def test_same_currency_reconciliation_within_tolerance(self, db_session):
        """Test reconciliation succeeds when difference is within 0.01 tolerance"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund, 
            event_type=EventType.CAPITAL_CALL, 
            amount=10000.0
        )
        
        # Add cash flow with small difference (within tolerance)
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=9999.995,  # 0.005 difference (well within 0.01 tolerance)
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is set
        assert event.is_cash_flow_complete is True
    
    def test_same_currency_reconciliation_failure(self, db_session):
        """Test reconciliation fails when difference exceeds tolerance"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund, 
            event_type=EventType.CAPITAL_CALL, 
            amount=10000.0
        )
        
        # Add cash flow with difference exceeding tolerance
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=account,
            amount=9999.98,  # 0.02 difference (exceeds 0.01 tolerance)
            currency="AUD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is not set
        assert event.is_cash_flow_complete is False
    
    def test_cross_currency_cash_flows_skip_reconciliation(self, db_session):
        """Test that cross-currency cash flows don't affect completion flag"""
        # Create test data with different currencies
        entity = EntityFactory.create()
        bank = BankFactory.create()
        aud_account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        usd_account = BankAccountFactory.create(entity=entity, bank=bank, currency="USD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund, 
            event_type=EventType.CAPITAL_CALL, 
            amount=10000.0
        )
        
        # Add cash flows in different currencies
        aud_cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=aud_account,
            amount=5000.0,
            currency="AUD"
        )
        usd_cash_flow = FundEventCashFlowFactory.create(
            fund_event=event,
            bank_account=usd_account,
            amount=5000.0,
            currency="USD"
        )
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is not set due to cross-currency flows
        assert event.is_cash_flow_complete is False
    
    def test_no_cash_flows_completion_false(self, db_session):
        """Test that events without cash flows have completion flag set to False"""
        # Create test data
        entity = EntityFactory.create()
        fund = FundFactory.create(entity=entity)
        event = FundEventFactory.create(
            fund=fund, 
            event_type=EventType.CAPITAL_CALL, 
            amount=10000.0
        )
        
        # Ensure no cash flows exist
        assert len(event.cash_flows) == 0
        
        # Trigger reconciliation
        event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is False
        assert event.is_cash_flow_complete is False


class TestWithholdingTaxMatching:
    """Test withholding tax matching logic for interest distributions"""
    
    def test_interest_withholding_reconciliation(self, db_session):
        """Test net amount calculation when interest withholding exists"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create interest distribution event
        event_date = date(2024, 6, 30)
        distribution_event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            event_date=event_date,
            amount=10000.0,  # Gross interest amount
            distribution_type=DistributionType.INTEREST
        )
        
        # Create corresponding withholding tax payment
        tax_payment_event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.TAX_PAYMENT,
            event_date=event_date,
            amount=1500.0,  # 15% withholding
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        
        # Add cash flow for net amount received (gross - withholding)
        net_amount = 10000.0 - 1500.0  # 8500.0
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=distribution_event,
            bank_account=account,
            amount=net_amount,
            currency="AUD"
        )
        
        # Trigger reconciliation
        distribution_event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is set (net amount reconciles)
        assert distribution_event.is_cash_flow_complete is True
    
    def test_interest_withholding_different_dates_no_matching(self, db_session):
        """Test that withholding tax on different dates doesn't affect reconciliation"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        
        # Create interest distribution event
        distribution_event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            event_date=date(2024, 6, 30),
            amount=10000.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Create withholding tax payment on different date
        tax_payment_event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.TAX_PAYMENT,
            event_date=date(2024, 7, 15),  # Different date
            amount=1500.0,
            tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING
        )
        
        # Add cash flow for full gross amount (no withholding matching)
        cash_flow = FundEventCashFlowFactory.create(
            fund_event=distribution_event,
            bank_account=account,
            amount=10000.0,  # Full gross amount
            currency="AUD"
        )
        
        # Trigger reconciliation
        distribution_event._recompute_cash_flow_completion(session=db_session)
        
        # Verify completion flag is set (full amount reconciles)
        assert distribution_event.is_cash_flow_complete is True


class TestCashFlowDirectionInference:
    """Test automatic direction inference based on event type"""
    
    def test_capital_call_OUTFLOW_direction(self, db_session):
        """Test that CAPITAL_CALL events infer OUTFLOW direction"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank)
        fund = FundFactory.create(entity=entity)
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=10000.0
        )
        
        # Add cash flow without specifying direction
        cash_flow = event.add_cash_flow(
            bank_account_id=account.id,
            transfer_date=date.today(),
            currency="AUD",
            amount=10000.0,
            session=db_session
        )
        
        # Verify direction is inferred as OUTFLOW
        assert cash_flow.direction == CashFlowDirection.OUTFLOW
    
    def test_distribution_INFLOW_direction(self, db_session):
        """Test that DISTRIBUTION events infer INFLOW direction"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank)
        fund = FundFactory.create(entity=entity)
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.DISTRIBUTION,
            amount=5000.0,
            distribution_type=DistributionType.INTEREST
        )
        
        # Add cash flow without specifying direction
        cash_flow = event.add_cash_flow(
            bank_account_id=account.id,
            transfer_date=date.today(),
            currency="AUD",
            amount=5000.0,
            session=db_session
        )
        
        # Verify direction is inferred as INFLOW
        assert cash_flow.direction == CashFlowDirection.INFLOW


class TestCurrencyValidation:
    """Test currency validation rules"""
    
    def test_currency_must_match_bank_account(self, db_session):
        """Test that cash flow currency must match bank account currency"""
        # Create test data with mismatched currencies
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=10000.0
        )
        
        # Attempt to add cash flow with mismatched currency
        with pytest.raises(ValueError, match="Cash flow currency must equal BankAccount.currency"):
            event.add_cash_flow(
                bank_account_id=account.id,
                transfer_date=date.today(),
                currency="USD",  # Different from account currency (AUD)
                amount=10000.0,
                session=db_session
            )
    
    def test_valid_currency_creates_cash_flow(self, db_session):
        """Test that matching currency successfully creates cash flow"""
        # Create test data
        entity = EntityFactory.create()
        bank = BankFactory.create()
        account = BankAccountFactory.create(entity=entity, bank=bank, currency="AUD")
        fund = FundFactory.create(entity=entity, currency="AUD")
        event = FundEventFactory.create(
            fund=fund,
            event_type=EventType.CAPITAL_CALL,
            amount=10000.0
        )
        
        # Add cash flow with matching currency
        cash_flow = event.add_cash_flow(
            bank_account_id=account.id,
            transfer_date=date.today(),
            currency="AUD",  # Matches account currency
            amount=10000.0,
            session=db_session
        )
        
        # Verify cash flow was created
        assert cash_flow.id is not None
        assert cash_flow.currency == "AUD"
        assert cash_flow.amount == 10000.0
