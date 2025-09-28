"""
Rates Domain Factories.

This module contains all factory classes for rates-related models,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.rates.models import RiskFreeRate


fake = Faker()


class RiskFreeRateFactory(SessionedFactory):
    """Factory for creating RiskFreeRate test data."""
    
    class Meta:
        model = RiskFreeRate

    currency = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF', 'CNY', 'KRW'
    ]))
    date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-2y', end_date='today'))
    rate = factory.LazyAttribute(lambda _: fake.pyfloat(min_value=0.1, max_value=10.0, right_digits=2))
    rate_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'GOVERNMENT_BOND', 'LIBOR', 'SOFR'
    ]))
    source = factory.LazyAttribute(lambda _: fake.company())
