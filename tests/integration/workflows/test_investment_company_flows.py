from tests.factories import InvestmentCompanyFactory, FundFactory, EntityFactory
from src.investment_company.services import CompanyPortfolioService


def test_total_commitments_simple(db_session):
    # Bind factories to current session
    for factory in (InvestmentCompanyFactory, FundFactory, EntityFactory):
        factory._meta.sqlalchemy_session = db_session

    company = InvestmentCompanyFactory()
    entity = EntityFactory()
    # Create two funds with default commitment 100000 each
    FundFactory(investment_company=company, entity=entity)
    FundFactory(investment_company=company, entity=entity)
    db_session.commit()

    # Use service instead of model method
    portfolio_service = CompanyPortfolioService()
    total = portfolio_service.get_total_commitments(company, db_session)
    assert total == 200000.0


