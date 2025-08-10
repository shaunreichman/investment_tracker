import factory
from faker import Faker
from datetime import datetime

from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund, FundType
from src.tax.models import TaxStatement


fake = Faker()


class SessionedFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        abstract = True
        sqlalchemy_session_persistence = "flush"


class EntityFactory(SessionedFactory):
    class Meta:
        model = Entity

    name = factory.LazyAttribute(lambda _: f"Entity {fake.unique.company()}")
    description = factory.LazyAttribute(lambda _: fake.catch_phrase())
    tax_jurisdiction = "AU"


class InvestmentCompanyFactory(SessionedFactory):
    class Meta:
        model = InvestmentCompany

    name = factory.LazyAttribute(lambda _: f"Company {fake.unique.company()}")
    description = factory.LazyAttribute(lambda _: fake.bs())
    website = factory.LazyAttribute(lambda _: fake.url())
    contact_email = factory.LazyAttribute(lambda _: fake.company_email())
    contact_phone = factory.LazyAttribute(lambda _: fake.phone_number())


class FundFactory(SessionedFactory):
    class Meta:
        model = Fund

    # Create required relationships automatically
    investment_company = factory.SubFactory(InvestmentCompanyFactory)
    entity = factory.SubFactory(EntityFactory)

    name = factory.LazyAttribute(lambda _: f"Fund {fake.unique.color_name()} {fake.random_int(1, 9999)}")
    fund_type = "Private Debt"
    tracking_type = FundType.COST_BASED
    currency = "AUD"
    description = factory.LazyAttribute(lambda _: fake.sentence())
    commitment_amount = 100000.0
    expected_irr = 10.0
    expected_duration_months = 48


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


