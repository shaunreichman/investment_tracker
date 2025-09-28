"""
Investment Company Domain Factories.

This module contains all factory classes for investment company-related models,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.investment_company.models import InvestmentCompany, Contact
from src.investment_company.enums import CompanyType, CompanyStatus


fake = Faker()


class InvestmentCompanyFactory(SessionedFactory):
    """Factory for creating InvestmentCompany test data."""
    
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
    """Factory for creating Contact test data."""
    
    class Meta:
        model = Contact

    # Create required relationships automatically
    investment_company = factory.SubFactory(InvestmentCompanyFactory)
    
    name = factory.LazyAttribute(lambda _: fake.name())
    title = factory.LazyAttribute(lambda _: fake.job())
    direct_number = factory.LazyAttribute(lambda _: fake.phone_number())
    direct_email = factory.LazyAttribute(lambda _: fake.email())
    notes = factory.LazyAttribute(lambda _: fake.sentence())
