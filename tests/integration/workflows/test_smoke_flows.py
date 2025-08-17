from tests.factories import EntityFactory, InvestmentCompanyFactory, FundFactory
from src.fund.models import FundType


def test_basic_factory_creation(db_session):
    EntityFactory._meta.sqlalchemy_session = db_session
    InvestmentCompanyFactory._meta.sqlalchemy_session = db_session
    FundFactory._meta.sqlalchemy_session = db_session

    entity = EntityFactory()
    company = InvestmentCompanyFactory()
    fund = FundFactory(entity=entity, investment_company=company, tracking_type=FundType.COST_BASED)

    db_session.commit()

    assert entity.id is not None
    assert company.id is not None
    assert fund.id is not None
    assert fund.tracking_type == FundType.COST_BASED


