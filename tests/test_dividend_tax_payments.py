#!/usr/bin/env python3
"""
Test script for franked/unfranked dividend tax payment logic.
"""
import sys
import os
from datetime import date
from sqlalchemy.orm import sessionmaker
import pytest
from sqlalchemy import create_engine
from src.shared.base import Base
from src.tax.events import TaxEventManager, TaxEventCriteria
from src.fund.models import FundEvent, EventType, TaxPaymentType

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import get_database_session
from src.fund.models import Fund, FundEvent, DistributionType, EventType, TaxPaymentType
from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.tax.models import TaxStatement
from test_utils import clear_database_except_rates
from src.tax.events import TaxEventFactory

print('Python executable:', sys.executable)
print('sys.path:', sys.path)

import pytest

def test_dividend_tax_payments():
    print("Testing franked/unfranked dividend tax payment logic...")
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    try:
        clear_database_except_rates(session)
        # Create company/entity/fund
        company = InvestmentCompany.create("DivCo", session=session)
        entity = Entity.create("DivEntity", "individual", session=session)
        fund = Fund.create(
            investment_company_id=company.id,
            entity_id=entity.id,
            name="Dividend Fund",
            fund_type="Equity",
            tracking_type="nav_based",
            session=session
        )
        # Add franked and unfranked dividends
        fund.add_distribution(
            amount=1000.0,
            date=date(2024, 1, 30),
            distribution_type=DistributionType.DIVIDEND_FRANKED,
            description="Fully franked dividend",
            session=session
        )
        fund.add_distribution(
            amount=500.0,
            date=date(2024, 2, 28),
            distribution_type=DistributionType.DIVIDEND_UNFRANKED,
            description="Unfranked dividend",
            session=session
        )
        fund.add_distribution(
            amount=2000.0,
            date=date(2024, 5, 20),
            distribution_type=DistributionType.DIVIDEND_FRANKED,
            description="Fully franked dividend",
            session=session
        )
        fund.add_distribution(
            amount=750.0,
            date=date(2024, 5, 25),
            distribution_type=DistributionType.DIVIDEND_UNFRANKED,
            description="Unfranked dividend",
            session=session
        )
        # Create tax statement for FY 2023-24
        tax_statement = TaxStatement(
            fund_id=fund.id,
            entity_id=entity.id,
            financial_year="2023-24",
            dividend_franked_income_tax_rate=30.0,   # 30% tax rate
            dividend_unfranked_income_tax_rate=10.0  # 10% tax rate
        )
        session.add(tax_statement)
        session.commit()
        # Call create_tax_payment_events
        fund.create_tax_payment_events(session=session)
        # Query tax payment events
        events = session.query(FundEvent).filter(
            FundEvent.fund_id == fund.id,
            FundEvent.event_type == EventType.TAX_PAYMENT
        ).all()
        print("\n=== TAX PAYMENT EVENTS CREATED ===")
        for e in events:
            print(f"Type: {e.tax_payment_type.value}, Amount: {e.amount}, Desc: {e.description}")
        # Check for correct events
        franked = [e for e in events if e.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX]
        unfranked = [e for e in events if e.tax_payment_type == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX]
        assert len(franked) == 1, "Should be one franked dividend tax event"
        assert len(unfranked) == 1, "Should be one unfranked dividend tax event"
        assert abs(franked[0].amount - 900.0) < 0.01, f"Franked tax should be 900.0, got {franked[0].amount}"
        assert abs(unfranked[0].amount - 125.0) < 0.01, f"Unfranked tax should be 125.0, got {unfranked[0].amount}"
        print("\n✅ Dividend tax payment logic works as expected!")
    finally:
        session.close()

# --- TaxEventFactory Unit Tests ---
class DummyTaxStatement:
    def __init__(self, fund_id=1, entity_id=1, financial_year="2023-24", 
                 dividend_franked_income_amount=0.0, dividend_franked_income_tax_rate=0.0,
                 dividend_unfranked_income_amount=0.0, dividend_unfranked_income_tax_rate=0.0,
                 interest_income_amount=0.0, interest_income_tax_rate=0.0,
                 fy_debt_interest_deduction_sum_of_daily_interest=0.0, fy_debt_interest_deduction_rate=0.0,
                 interest_non_resident_withholding_tax_from_statement=0.0,
                 capital_gain_income_amount=0.0, capital_gain_income_tax_rate=0.0):
        self.fund_id = fund_id
        self.entity_id = entity_id
        self.financial_year = financial_year
        self.dividend_franked_income_amount = dividend_franked_income_amount
        self.dividend_franked_income_tax_rate = dividend_franked_income_tax_rate
        self.dividend_unfranked_income_amount = dividend_unfranked_income_amount
        self.dividend_unfranked_income_tax_rate = dividend_unfranked_income_tax_rate
        self.dividend_franked_income_amount_from_tax_statement_flag = dividend_franked_income_amount > 0
        self.dividend_unfranked_income_amount_from_tax_statement_flag = dividend_unfranked_income_amount > 0
        self.dividend_franked_tax_amount = 0.0
        self.dividend_unfranked_tax_amount = 0.0
        self.interest_income_amount = interest_income_amount
        self.interest_income_tax_rate = interest_income_tax_rate
        self.fy_debt_interest_deduction_sum_of_daily_interest = fy_debt_interest_deduction_sum_of_daily_interest
        self.fy_debt_interest_deduction_rate = fy_debt_interest_deduction_rate
        self.fy_debt_interest_deduction_total_deduction = 0.0
        self.interest_non_resident_withholding_tax_from_statement = interest_non_resident_withholding_tax_from_statement
        self.tax_payment_date = date(2024, 6, 30)
        self._fy_dates = (date(2023, 7, 1), date(2024, 6, 30))
        self.interest_tax_amount = 0.0
        self.interest_tax_benefit = 0.0
        # Capital gain fields
        self.capital_gain_income_amount = capital_gain_income_amount
        self.capital_gain_income_tax_rate = capital_gain_income_tax_rate
        self.capital_gain_tax_amount = 0.0
        self.capital_gain_discount_amount = 0.0
        self.capital_gain_income_amount_from_tax_statement_flag = capital_gain_income_amount > 0
    def calculate_interest_tax_amount(self):
        if self.interest_income_tax_rate and self.interest_income_amount and self.interest_income_tax_rate != 0 and self.interest_income_amount > 0:
            total_tax_liability = self.interest_income_amount * (self.interest_income_tax_rate / 100)
            self.interest_tax_amount = max(0, total_tax_liability - (self.interest_non_resident_withholding_tax_from_statement or 0.0))
        else:
            self.interest_tax_amount = 0.0
        return self.interest_tax_amount
    def calculate_fy_debt_interest_deduction_total_deduction(self):
        """Calculate interest tax benefit for testing."""
        if self.fy_debt_interest_deduction_sum_of_daily_interest and self.fy_debt_interest_deduction_rate:
            self.interest_benefit = (self.fy_debt_interest_deduction_sum_of_daily_interest * self.fy_debt_interest_deduction_rate) / 100
        else:
            self.interest_benefit = 0.0
        self.fy_debt_interest_deduction_total_deduction = self.interest_benefit
        return self.fy_debt_interest_deduction_total_deduction
    def calculate_dividend_totals(self, session=None):
        """Calculate dividend totals for testing."""
        return self.dividend_franked_income_amount, self.dividend_unfranked_income_amount
    def get_tax_payment_date(self):
        return self.tax_payment_date
    def get_financial_year_dates(self):
        return self._fy_dates

    def calculate_dividend_franked_tax_amount(self):
        """Calculate franked dividend tax amount for testing."""
        if self.dividend_franked_income_amount and self.dividend_franked_income_tax_rate:
            self.dividend_franked_tax_amount = (self.dividend_franked_income_amount * self.dividend_franked_income_tax_rate) / 100.0
        else:
            self.dividend_franked_tax_amount = 0.0
        return self.dividend_franked_tax_amount

    def calculate_dividend_unfranked_tax_amount(self):
        """Calculate unfranked dividend tax amount for testing."""
        if self.dividend_unfranked_income_amount and self.dividend_unfranked_income_tax_rate:
            self.dividend_unfranked_tax_amount = (self.dividend_unfranked_income_amount * self.dividend_unfranked_income_tax_rate) / 100.0
        else:
            self.dividend_unfranked_tax_amount = 0.0
        return self.dividend_unfranked_tax_amount

    def calculate_capital_gain_totals(self, session=None):
        # Dummy: just return the set value
        return self.capital_gain_income_amount
    def calculate_capital_gain_discount(self, session=None):
        # Dummy: 50% discount if gain exists
        if self.capital_gain_income_amount > 0:
            self.capital_gain_discount_amount = 0.5 * self.capital_gain_income_amount
        else:
            self.capital_gain_discount_amount = 0.0
        return self.capital_gain_discount_amount
    def calculate_capital_gain_tax_amount(self):
        # Dummy: tax on full gain (not discounted)
        if self.capital_gain_income_amount and self.capital_gain_income_tax_rate:
            self.capital_gain_tax_amount = (self.capital_gain_income_amount * self.capital_gain_income_tax_rate) / 100.0
        else:
            self.capital_gain_tax_amount = 0.0
        return self.capital_gain_tax_amount

def test_create_interest_tax_payment():
    ts = DummyTaxStatement(
        fund_id=1,
        financial_year='2023-24',
        interest_income_amount=1000.0,
        interest_income_tax_rate=30.0,
        interest_non_resident_withholding_tax_from_statement=50.0
    )
    ts.calculate_interest_tax_amount()
    event = TaxEventFactory.create_interest_tax_payment(ts)
    assert event is not None
    assert event.amount == ts.interest_tax_amount
    assert event.fund_id == ts.fund_id
    assert event.event_type.name == 'TAX_PAYMENT'

def test_create_interest_tax_payment_none():
    ts = DummyTaxStatement(
        interest_income_amount=0.0,  # This will result in interest_tax_amount = 0
        interest_income_tax_rate=30.0
    )
    ts.calculate_interest_tax_amount()
    event = TaxEventFactory.create_interest_tax_payment(ts)
    assert event is None

def test_create_dividend_tax_payment_franked():
    ts = DummyTaxStatement(dividend_franked_income_amount=200.0, dividend_franked_income_tax_rate=30.0)
    ts.calculate_dividend_totals() # Ensure totals are calculated
    event = TaxEventFactory.create_dividend_tax_payment(ts, DistributionType.DIVIDEND_FRANKED)
    assert event is not None
    assert event.amount == 60.0
    assert event.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    assert "Franked" in event.description

def test_create_dividend_tax_payment_unfranked():
    ts = DummyTaxStatement(dividend_unfranked_income_amount=150.0, dividend_unfranked_income_tax_rate=20.0)
    ts.calculate_dividend_totals() # Ensure totals are calculated
    event = TaxEventFactory.create_dividend_tax_payment(ts, DistributionType.DIVIDEND_UNFRANKED)
    assert event is not None
    assert event.amount == 30.0
    assert event.tax_payment_type == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
    assert "Unfranked" in event.description

def test_create_dividend_tax_payment_none():
    ts = DummyTaxStatement(dividend_franked_income_amount=0.0, dividend_franked_income_tax_rate=30.0)
    event = TaxEventFactory.create_dividend_tax_payment(ts, DistributionType.DIVIDEND_FRANKED)
    assert event is None

def test_create_fy_debt_cost_event():
    ts = DummyTaxStatement(
        fy_debt_interest_deduction_sum_of_daily_interest=200.0,
        fy_debt_interest_deduction_rate=25.0
    )
    ts.calculate_fy_debt_interest_deduction_total_deduction()
    event = TaxEventFactory.create_fy_debt_cost_event(ts)
    assert event is not None
    assert event.amount == ts.fy_debt_interest_deduction_total_deduction
    assert event.event_type.name == 'FY_DEBT_COST'

def test_create_fy_debt_cost_event_none():
    ts = DummyTaxStatement(
        fy_debt_interest_deduction_sum_of_daily_interest=0.0,  # This will result in interest_tax_benefit = 0
        fy_debt_interest_deduction_rate=25.0
    )
    ts.calculate_fy_debt_interest_deduction_total_deduction()
    event = TaxEventFactory.create_fy_debt_cost_event(ts)
    assert event is None

def test_create_all_tax_events():
    ts = DummyTaxStatement(
        interest_income_amount=1000.0,
        interest_income_tax_rate=30.0,
        interest_non_resident_withholding_tax_from_statement=50.0,
        dividend_franked_income_amount=200.0,
        dividend_franked_income_tax_rate=30.0,
        dividend_unfranked_income_amount=150.0,
        dividend_unfranked_income_tax_rate=20.0,
        fy_debt_interest_deduction_sum_of_daily_interest=200.0,
        fy_debt_interest_deduction_rate=25.0
    )
    ts.calculate_interest_tax_amount()
    ts.calculate_fy_debt_interest_deduction_total_deduction()
    events = TaxEventFactory.create_all_tax_events(ts)
    # Should create 4 events: interest tax, franked, unfranked, fy debt cost
    assert len(events) == 4
    event_types = {e.event_type.name for e in events}
    assert 'TAX_PAYMENT' in event_types
    assert 'FY_DEBT_COST' in event_types

# --- TaxEventManager Unit Tests ---
@pytest.fixture(scope="function")
def in_memory_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_find_existing_event(in_memory_session):
    session = in_memory_session
    # Add a FundEvent
    event = FundEvent(
        fund_id=1,
        event_type=EventType.TAX_PAYMENT,
        event_date=date(2024, 6, 30),
        amount=100.0,
        tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
    )
    session.add(event)
    session.commit()
    criteria = TaxEventCriteria(
        fund_id=1,
        event_type=EventType.TAX_PAYMENT,
        event_date=date(2024, 6, 30),
        amount=100.0,
        tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
    )
    found = TaxEventManager.find_existing_event(criteria, session)
    assert found is not None
    assert found.amount == 100.0
    # Negative case
    criteria2 = TaxEventCriteria(
        fund_id=1,
        event_type=EventType.TAX_PAYMENT,
        event_date=date(2024, 6, 30),
        amount=200.0,
        tax_payment_type=TaxPaymentType.EOFY_INTEREST_TAX
    )
    not_found = TaxEventManager.find_existing_event(criteria2, session)
    assert not_found is None


def test_create_or_update_tax_events(in_memory_session):
    session = in_memory_session
    ts = DummyTaxStatement(
        interest_income_amount=1000.0,
        interest_income_tax_rate=30.0,
        interest_non_resident_withholding_tax_from_statement=50.0,
        dividend_franked_income_amount=200.0,
        dividend_franked_income_tax_rate=30.0,
        dividend_unfranked_income_amount=150.0,
        dividend_unfranked_income_tax_rate=20.0,
        fy_debt_interest_deduction_sum_of_daily_interest=200.0,
        fy_debt_interest_deduction_rate=25.0
    )
    ts.calculate_interest_tax_amount()
    ts.calculate_fy_debt_interest_deduction_total_deduction()
    created = TaxEventManager.create_or_update_tax_events(ts, session)
    assert len(created) == 4
    event_types = {e.event_type.name for e in created}
    assert 'TAX_PAYMENT' in event_types
    assert 'FY_DEBT_COST' in event_types


def test_validate_event_creation():
    ts = DummyTaxStatement(
        interest_income_amount=1000.0,
        interest_income_tax_rate=30.0,
        interest_non_resident_withholding_tax_from_statement=50.0,
        dividend_franked_income_amount=200.0,
        dividend_franked_income_tax_rate=30.0,
        dividend_unfranked_income_amount=150.0,
        dividend_unfranked_income_tax_rate=20.0,
        fy_debt_interest_deduction_sum_of_daily_interest=200.0,
        fy_debt_interest_deduction_rate=25.0
    )
    ts.calculate_interest_tax_amount()
    ts.calculate_fy_debt_interest_deduction_total_deduction()
    assert TaxEventManager.validate_event_creation(ts, EventType.TAX_PAYMENT, None)
    assert TaxEventManager.validate_event_creation(ts, TaxPaymentType.DIVIDENDS_FRANKED_TAX, None)
    assert TaxEventManager.validate_event_creation(ts, TaxPaymentType.DIVIDENDS_UNFRANKED_TAX, None)
    assert TaxEventManager.validate_event_creation(ts, EventType.FY_DEBT_COST, None)
    # Negative cases
    ts2 = DummyTaxStatement(
        interest_income_amount=0.0,
        interest_income_tax_rate=0.0,
        interest_non_resident_withholding_tax_from_statement=0.0,
        dividend_franked_income_amount=0.0,
        dividend_franked_income_tax_rate=0.0,
        dividend_unfranked_income_amount=0.0,
        dividend_unfranked_income_tax_rate=0.0,
        fy_debt_interest_deduction_sum_of_daily_interest=0.0,
        fy_debt_interest_deduction_rate=0.0
    )
    ts2.calculate_interest_tax_amount()
    ts2.calculate_fy_debt_interest_deduction_total_deduction()
    assert not TaxEventManager.validate_event_creation(ts2, EventType.TAX_PAYMENT, None)
    assert not TaxEventManager.validate_event_creation(ts2, TaxPaymentType.DIVIDENDS_FRANKED_TAX, None)
    assert not TaxEventManager.validate_event_creation(ts2, TaxPaymentType.DIVIDENDS_UNFRANKED_TAX, None)
    assert not TaxEventManager.validate_event_creation(ts2, EventType.FY_DEBT_COST, None)

# --- Edge Case Tests for Tax Event Framework ---
def test_manual_vs_calculated_dividend_totals(in_memory_session):
    session = in_memory_session
    # Add fund, entity, and events
    company = InvestmentCompany.create("ManualCalcCo", session=session)
    entity = Entity.create("ManualCalcEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="ManualCalcFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    # Add franked dividend event
    fund.add_distribution(
        amount=1000.0,
        date=date(2024, 1, 30),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        session=session
    )
    # Tax statement with manual total_dividends_franked
    tax_statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        dividend_franked_income_amount=500.0,  # Manual value (should override event)
        dividend_franked_income_tax_rate=20.0
    )
    session.add(tax_statement)
    session.commit()
    fund.create_tax_payment_events(session=session)
    event = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    assert event is not None
    assert event.amount == 100.0  # 500 * 20%

def test_only_one_rate_set(in_memory_session):
    session = in_memory_session
    company = InvestmentCompany.create("OneRateCo", session=session)
    entity = Entity.create("OneRateEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="OneRateFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    fund.add_distribution(
        amount=1000.0,
        date=date(2024, 1, 30),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        session=session
    )
    fund.add_distribution(
        amount=500.0,
        date=date(2024, 2, 28),
        distribution_type=DistributionType.DIVIDEND_UNFRANKED,
        session=session
    )
    tax_statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        dividend_franked_income_tax_rate=25.0  # Only franked rate set
    )
    session.add(tax_statement)
    session.commit()
    fund.create_tax_payment_events(session=session)
    franked = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    unfranked = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
    ).first()
    assert franked is not None
    assert unfranked is None

def test_duplicate_tax_statement_unique_constraint(in_memory_session):
    session = in_memory_session
    company = InvestmentCompany.create("DupCo", session=session)
    entity = Entity.create("DupEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="DupFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    tax_statement1 = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24"
    )
    session.add(tax_statement1)
    session.commit()
    # Attempt to add duplicate
    tax_statement2 = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24"
    )
    session.add(tax_statement2)
    with pytest.raises(Exception):
        session.commit()
    session.rollback()

def test_event_update_scenario(in_memory_session):
    session = in_memory_session
    company = InvestmentCompany.create("UpdateCo", session=session)
    entity = Entity.create("UpdateEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="UpdateFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    fund.add_distribution(
        amount=1000.0,
        date=date(2024, 1, 30),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        session=session
    )
    tax_statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        dividend_franked_income_tax_rate=10.0
    )
    session.add(tax_statement)
    session.commit()
    fund.create_tax_payment_events(session=session)
    event = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    assert event.amount == 100.0
    # Update rate and re-create events
    tax_statement.dividend_franked_income_tax_rate = 20.0
    session.commit()
    fund.create_tax_payment_events(session=session)
    # Should not create duplicate, but amount should reflect new rate
    event2 = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    assert event2.amount == 200.0

def test_tax_payment_event_with_zero_rate(in_memory_session):
    session = in_memory_session
    company = InvestmentCompany.create("ZeroRateCo", session=session)
    entity = Entity.create("ZeroRateEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="ZeroRateFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    fund.add_distribution(
        amount=1000.0,
        date=date(2024, 1, 30),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        session=session
    )
    tax_statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        dividend_franked_income_tax_rate=0.0
    )
    session.add(tax_statement)
    session.commit()
    fund.create_tax_payment_events(session=session)
    event = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    assert event is None

def test_negative_dividend_amount(in_memory_session):
    session = in_memory_session
    company = InvestmentCompany.create("NegDivCo", session=session)
    entity = Entity.create("NegDivEntity", "individual", session=session)
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="NegDivFund",
        fund_type="Equity",
        tracking_type="nav_based",
        session=session
    )
    fund.add_distribution(
        amount=-1000.0,
        date=date(2024, 1, 30),
        distribution_type=DistributionType.DIVIDEND_FRANKED,
        session=session
    )
    tax_statement = TaxStatement(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        dividend_franked_income_tax_rate=20.0
    )
    session.add(tax_statement)
    session.commit()
    fund.create_tax_payment_events(session=session)
    event = session.query(FundEvent).filter(
        FundEvent.fund_id == fund.id,
        FundEvent.tax_payment_type == TaxPaymentType.DIVIDENDS_FRANKED_TAX
    ).first()
    assert event is None

def test_capital_gain_tax_payment_event():
    """
    Test capital gain tax payment event creation for NAV-based fund with FIFO and AU discount logic.
    """
    from src.fund.models import Fund, FundType, EventType, FundEvent, DistributionType, TaxPaymentType
    from src.tax.models import TaxStatement
    from src.tax.events import TaxEventFactory
    from datetime import date, timedelta
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker, scoped_session
    from src.entity.models import Entity

    # Setup in-memory SQLite DB
    engine = create_engine('sqlite:///:memory:')
    Fund.metadata.create_all(engine)
    Entity.metadata.create_all(engine)
    FundEvent.metadata.create_all(engine)
    TaxStatement.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    session = Session()

    try:
        # Create AU entity
        entity = Entity.create(name="Test AU Entity", tax_jurisdiction="AU", session=session)
        # Create NAV-based fund
        fund = Fund.create(
            investment_company_id=1,
            entity_id=entity.id,
            name="Test NAV Fund",
            fund_type="Equity",
            tracking_type=FundType.NAV_BASED,
            session=session
        )
        # Unit purchase: 100 units @ $10 on 2022-01-01
        purchase_date = date(2022, 1, 1)
        fund_event1 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.UNIT_PURCHASE,
            event_date=purchase_date,
            units_purchased=100,
            unit_price=10.0
        )
        session.add(fund_event1)
        # Unit sale: 100 units @ $20 on 2023-07-01 (holding > 12 months)
        sale_date = date(2023, 7, 1)
        fund_event2 = FundEvent(
            fund_id=fund.id,
            event_type=EventType.UNIT_SALE,
            event_date=sale_date,
            units_sold=100,
            unit_price=20.0
        )
        session.add(fund_event2)
        session.commit()
        # Create tax statement for FY 2023-24
        tax_statement = TaxStatement(
            fund_id=fund.id,
            entity_id=entity.id,
            financial_year="2023-24",
            capital_gain_income_tax_rate=30.0
        )
        session.add(tax_statement)
        session.commit()
        # Calculate capital gain totals and discount
        tax_statement.calculate_capital_gain_totals(session=session)
        tax_statement.calculate_capital_gain_discount(session=session)
        # Should be 100 * (20-10) = $1000 gain, all eligible for 50% discount
        assert abs(tax_statement.capital_gain_income_amount - 1000.0) < 0.01
        assert abs(tax_statement.capital_gain_discount_amount - 500.0) < 0.01
        # Calculate tax amount (should be on full gain, not discounted)
        tax_statement.calculate_capital_gain_tax_amount()
        assert abs(tax_statement.capital_gain_tax_amount - 300.0) < 0.01
        # Create capital gain tax payment event
        event = TaxEventFactory.create_capital_gain_tax_payment(tax_statement, session=session)
        assert event is not None
        assert event.tax_payment_type == TaxPaymentType.CAPITAL_GAINS_TAX
        assert abs(event.amount - 300.0) < 0.01
        print("\n✅ Capital gain tax payment event logic works as expected!")
    finally:
        session.close()

if __name__ == "__main__":
    test_dividend_tax_payments() 