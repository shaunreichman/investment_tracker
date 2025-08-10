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

    investment_company = factory.SubFactory(InvestmentCompanyFactory)
    entity = factory.SubFactory(EntityFactory)
    investment_company_id = factory.SelfAttribute("investment_company.id")
    entity_id = factory.SelfAttribute("entity.id")

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

    fund = factory.SubFactory(FundFactory)
    fund_id = factory.SelfAttribute("fund.id")
    
    statement_date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    financial_year = factory.LazyAttribute(lambda obj: f"{obj.statement_date.year}-{obj.statement_date.year + 1}")
    
    # Income fields
    dividend_income = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=10000, precision=2))
    interest_income = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=10000, precision=2))
    capital_gains = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=10000, precision=2))
    
    # Tax fields
    dividend_tax_amount = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=5000, precision=2))
    interest_tax_amount = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=5000, precision=2))
    capital_gains_tax_amount = factory.LazyAttribute(lambda _: fake.random_float(min=0, max=5000, precision=2))
    
    # Other fields
    accountant = factory.LazyAttribute(lambda _: fake.name())
    notes = factory.LazyAttribute(lambda _: fake.sentence())


