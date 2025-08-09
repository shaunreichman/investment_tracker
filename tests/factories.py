import factory
from faker import Faker
from datetime import datetime

from src.entity.models import Entity
from src.investment_company.models import InvestmentCompany
from src.fund.models import Fund, FundType


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


