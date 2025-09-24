import factory
from faker import Faker
from datetime import datetime

from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus
from src.fund.models import Fund, FundEvent, FundEventCashFlow
from src.fund.enums import FundTrackingType, EventType, DistributionType, TaxPaymentType, CashFlowDirection, FundStatus
from src.tax.models import TaxStatement
from src.rates.models import RiskFreeRate
from src.banking.models import Bank, BankAccount


fake = Faker()

# Global session for factories
_current_session = None

def set_session(session):
    """Set the database session for all factories"""
    global _current_session
    _current_session = session
    
    # Update all factory Meta classes to use this session
    SessionedFactory._meta.sqlalchemy_session = session
    FundFactory._meta.sqlalchemy_session = session
    EntityFactory._meta.sqlalchemy_session = session
    InvestmentCompanyFactory._meta.sqlalchemy_session = session
    ContactFactory._meta.sqlalchemy_session = session
    FundEventFactory._meta.sqlalchemy_session = session
    TaxStatementFactory._meta.sqlalchemy_session = session
    RiskFreeRateFactory._meta.sqlalchemy_session = session
    BankFactory._meta.sqlalchemy_session = session
    BankAccountFactory._meta.sqlalchemy_session = session
    FundEventCashFlowFactory._meta.sqlalchemy_session = session


class SessionedFactory(factory.alchemy.SQLAlchemyModelFactory):
    """Base factory that uses the current session"""
    
    class Meta:
        sqlalchemy_session = None  # Will be set dynamically
    
    @classmethod
    def create(cls, **kwargs):
        """Override create to ensure session is set before creating"""
        if cls._meta.sqlalchemy_session is None:
            # Try to get session from current app context
            try:
                from flask import current_app
                if current_app.config.get('TEST_DB_SESSION'):
                    cls._meta.sqlalchemy_session = current_app.config['TEST_DB_SESSION']
            except:
                pass
        
        # Create the object
        obj = cls.build(**kwargs)
        
        # Add to session but don't commit - let the test session handle it
        if cls._meta.sqlalchemy_session:
            cls._meta.sqlalchemy_session.add(obj)
            cls._meta.sqlalchemy_session.flush()  # Flush to get ID but don't commit
            cls._meta.sqlalchemy_session.refresh(obj)
        
        return obj


class EntityFactory(SessionedFactory):
    class Meta:
        model = Entity

    name = factory.Sequence(lambda n: f"Entity {n:04d}")
    description = factory.LazyAttribute(lambda _: fake.catch_phrase())
    tax_jurisdiction = "AU"


class InvestmentCompanyFactory(SessionedFactory):
    class Meta:
        model = InvestmentCompany

    name = factory.Sequence(lambda n: f"Company {n:04d}")
    description = factory.LazyAttribute(lambda _: fake.bs())
    website = factory.LazyAttribute(lambda _: fake.url())
    company_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        CompanyType.PRIVATE_EQUITY,
        CompanyType.VENTURE_CAPITAL,
        CompanyType.REAL_ESTATE,
        CompanyType.INFRASTRUCTURE,
        CompanyType.CREDIT,
        CompanyType.HEDGE_FUND,
        CompanyType.FAMILY_OFFICE,
        CompanyType.INVESTMENT_BANK,
        CompanyType.ASSET_MANAGEMENT,
        CompanyType.OTHER
    ]))
    status = CompanyStatus.ACTIVE  # Default to active status
    business_address = factory.LazyAttribute(lambda _: fake.address())


class ContactFactory(SessionedFactory):
    class Meta:
        model = Contact

    # Create required relationships automatically
    investment_company = factory.SubFactory(InvestmentCompanyFactory)
    
    name = factory.LazyAttribute(lambda _: fake.name())
    title = factory.LazyAttribute(lambda _: fake.job())
    direct_number = factory.LazyAttribute(lambda _: fake.phone_number())
    direct_email = factory.LazyAttribute(lambda _: fake.email())
    notes = factory.LazyAttribute(lambda _: fake.sentence())


class FundFactory(SessionedFactory):
    class Meta:
        model = Fund

    # Create required relationships automatically
    investment_company = factory.SubFactory(InvestmentCompanyFactory)
    entity = factory.SubFactory(EntityFactory)

    # Use a more robust naming strategy that won't hit uniqueness limits
    name = factory.Sequence(lambda n: f"Fund {n:04d}")
    fund_type = "Private Debt"
    tracking_type = FundTrackingType.COST_BASED
    status = FundStatus.ACTIVE  # Set default status
    currency = "AUD"
    description = factory.LazyAttribute(lambda _: fake.sentence())
    commitment_amount = 100000.0
    expected_irr = 10.0
    expected_duration_months = 48


class FundEventFactory(SessionedFactory):
    class Meta:
        model = FundEvent

    # Create required relationships automatically
    fund = factory.SubFactory(FundFactory)
    
    event_type = EventType.CAPITAL_CALL
    event_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=1000, max_value=50000, right_digits=2))
    description = factory.LazyAttribute(lambda _: fake.sentence())
    reference_number = factory.Sequence(lambda n: f"REF-{n:06d}")


class RiskFreeRateFactory(SessionedFactory):
    class Meta:
        model = RiskFreeRate

    currency = "AUD"
    rate_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0.1, max_value=10.0, right_digits=2))
    rate_type = "government_bond"
    source = factory.LazyAttribute(lambda _: fake.company())


class TaxStatementFactory(SessionedFactory):
    class Meta:
        model = TaxStatement

    # Create required relationships automatically
    fund = factory.SubFactory(FundFactory)
    entity = factory.SubFactory(EntityFactory)
    
    statement_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    financial_year = factory.LazyAttribute(lambda obj: f"{obj.statement_date.year}-{obj.statement_date.year + 1}")
    
    # Income fields - use correct field names from the model
    dividend_franked_income_amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    dividend_unfranked_income_amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    interest_income_amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    capital_gain_income_amount = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=10000, right_digits=2))
    
    # Tax rate fields
    dividend_franked_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    dividend_unfranked_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    interest_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    capital_gain_income_tax_rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0, max_value=50, right_digits=1))
    
    # Other fields
    accountant = factory.LazyAttribute(lambda _: fake.name())
    notes = factory.LazyAttribute(lambda _: fake.sentence())


class BankFactory(SessionedFactory):
    class Meta:
        model = Bank

    name = factory.LazyAttribute(lambda _: fake.company())
    country = "AU"  # Default to Australia
    swift_bic = factory.LazyAttribute(lambda _: fake.bothify(text='????AU2X', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


class BankAccountFactory(SessionedFactory):
    class Meta:
        model = BankAccount

    # Create required relationships automatically
    entity = factory.SubFactory(EntityFactory)
    bank = factory.SubFactory(BankFactory)
    
    account_name = factory.LazyAttribute(lambda _: fake.bothify(text='Account ????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    account_number = factory.LazyAttribute(lambda _: fake.bothify(text='????-????-????-????', letters='0123456789'))
    currency = "AUD"  # Default to AUD
    status = "ACTIVE"


class FundEventCashFlowFactory(SessionedFactory):
    class Meta:
        model = FundEventCashFlow

    # Create required relationships automatically
    fund_event = factory.SubFactory(FundEventFactory)
    bank_account = factory.SubFactory(BankAccountFactory)
    
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


