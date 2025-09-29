"""
Fund Domain Factories.

This module contains all factory classes for fund-related models,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.fund.models import Fund, FundEvent, FundEventCashFlow, FundTaxStatement, DomainFundEvent
from src.fund.enums import FundTrackingType, EventType, DistributionType, TaxPaymentType, CashFlowDirection, FundInvestmentType
from src.shared.enums.shared_enums import Currency, Country, EventOperation


fake = Faker()


class FundFactory(SessionedFactory):
    """Factory for creating Fund test data."""
    
    class Meta:
        model = Fund

    # Create required relationships automatically
    investment_company = factory.SubFactory('tests.factories.investment_company_factories.InvestmentCompanyFactory')
    entity = factory.SubFactory('tests.factories.entity_factories.EntityFactory')

    # Basic fund information (manual fields)
    name = factory.Sequence(lambda n: f"Fund {n:04d}")
    fund_investment_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        FundInvestmentType.PRIVATE_EQUITY,
        FundInvestmentType.VENTURE_CAPITAL,
        FundInvestmentType.PRIVATE_DEBT,
        FundInvestmentType.REAL_ESTATE,
        FundInvestmentType.INFRASTRUCTURE,
        FundInvestmentType.OTHER
    ]))
    tracking_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        FundTrackingType.COST_BASED, FundTrackingType.NAV_BASED
    ]))
    description = factory.LazyAttribute(lambda _: fake.sentence())
    currency = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        Currency.AUD, Currency.USD, Currency.EUR, Currency.GBP
    ]))
    tax_jurisdiction = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        Country.AU, Country.US, Country.UK, Country.SG
    ]))
    
    # Expected information (manual fields)
    expected_irr = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=5.0, max_value=25.0, right_digits=1))
    expected_duration_months = factory.LazyAttribute(lambda _: fake.random_int(min=12, max=120))
    commitment_amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=10000, max_value=1000000, right_digits=2))


class FundEventFactory(SessionedFactory):
    """Factory for creating FundEvent test data."""
    
    class Meta:
        model = FundEvent

    # Create required relationships automatically
    fund = factory.SubFactory(FundFactory)
    
    # Basic event fields (manual)
    event_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        EventType.CAPITAL_CALL, EventType.DISTRIBUTION, EventType.NAV_UPDATE,
        EventType.UNIT_PURCHASE, EventType.UNIT_SALE, EventType.TAX_PAYMENT,
        EventType.RETURN_OF_CAPITAL, EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
        EventType.EOFY_DEBT_COST
    ]))
    event_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=1000, max_value=50000, right_digits=2))
    description = factory.LazyAttribute(lambda _: fake.sentence())
    reference_number = factory.Sequence(lambda n: f"REF-{n:06d}")
    
    # NAV-specific fields (manual)
    nav_per_share = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=1.0, max_value=1000.0, right_digits=4))
    
    # Distribution-specific fields (manual)
    distribution_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        DistributionType.INCOME, DistributionType.DIVIDEND_FRANKED, DistributionType.DIVIDEND_UNFRANKED,
        DistributionType.INTEREST, DistributionType.RENT, DistributionType.CAPITAL_GAIN
    ]))
    tax_withholding = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=1000, right_digits=2))
    has_withholding_tax = factory.LazyAttribute(lambda _: fake.boolean())
    
    # Tax-specific fields (manual)
    tax_payment_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING, TaxPaymentType.CAPITAL_GAINS_TAX,
        TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING_DIFFERENCE, TaxPaymentType.DIVIDENDS_FRANKED_TAX,
        TaxPaymentType.DIVIDENDS_UNFRANKED_TAX
    ]))
    
    # Unit transaction fields (manual)
    units_purchased = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=1000, right_digits=4))
    units_sold = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=1000, right_digits=4))
    unit_price = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=1.0, max_value=1000.0, right_digits=4))
    brokerage_fee = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=100, right_digits=2))


class FundEventCashFlowFactory(SessionedFactory):
    """Factory for creating FundEventCashFlow test data."""
    
    class Meta:
        model = FundEventCashFlow

    # Create required relationships automatically
    fund_event = factory.SubFactory(FundEventFactory)
    bank_account = factory.SubFactory('tests.factories.banking_factories.BankAccountFactory')
    
    # Direction will be inferred from event type, but we can override
    direction = factory.LazyAttribute(lambda obj: 
        CashFlowDirection.OUTFLOW if obj.fund_event.event_type in [EventType.CAPITAL_CALL, EventType.UNIT_PURCHASE]
        else CashFlowDirection.INFLOW
    )
    transfer_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-1y', end_date='today'))
    currency = factory.LazyAttribute(lambda obj: obj.bank_account.currency)
    amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=100, max_value=50000, right_digits=2))
    reference = factory.LazyAttribute(lambda _: fake.bothify(text='REF-????-????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'))
    description = factory.LazyAttribute(lambda _: fake.sentence())


class FundTaxStatementFactory(SessionedFactory):
    """Factory for creating FundTaxStatement test data."""
    
    class Meta:
        model = FundTaxStatement

    # Create required relationships automatically
    fund = factory.SubFactory(FundFactory)
    entity = factory.SubFactory('tests.factories.entity_factories.EntityFactory')
    
    statement_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    financial_year = factory.LazyAttribute(lambda obj: f"{obj.statement_date.year}-{obj.statement_date.year + 1}")
    
    
    # Tax rate fields
    dividend_franked_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    dividend_unfranked_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    interest_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    capital_gain_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    
    # Interest income fields (manual)
    interest_received_in_cash = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    interest_receivable_this_fy = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    interest_receivable_prev_fy = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    interest_non_resident_withholding_tax_from_statement = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=1000, right_digits=2))
    
    # Debt cost fields (manual)
    eofy_debt_interest_deduction_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    
    # Other fields
    accountant = factory.LazyAttribute(lambda _: fake.name())
    notes = factory.LazyAttribute(lambda _: fake.sentence())


class DomainFundEventFactory(SessionedFactory):
    """Factory for creating DomainFundEvent test data."""
    
    class Meta:
        model = DomainFundEvent

    # Create required relationships automatically
    fund = factory.SubFactory('tests.factories.fund_factories.FundFactory')
    
    # Basic domain fund event information (manual fields)
    event_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        EventType.CAPITAL_CALL,
        EventType.RETURN_OF_CAPITAL,
        EventType.DISTRIBUTION,
        EventType.UNIT_PURCHASE,
        EventType.UNIT_SALE,
        EventType.NAV_UPDATE,
        EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
        EventType.EOFY_DEBT_COST,
        EventType.TAX_PAYMENT
    ]))
    event_operation = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        EventOperation.CREATE,
        EventOperation.UPDATE,
        EventOperation.DELETE
    ]))
    fund_event_id = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=1000))
    event_data = factory.LazyAttribute(lambda _: {
        'field_name': fake.word(),
        'old_value': fake.word(),
        'new_value': fake.word(),
        'timestamp': fake.iso8601()
    })
