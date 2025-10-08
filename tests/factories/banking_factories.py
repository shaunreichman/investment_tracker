"""
Banking Domain Factories.

This module contains all factory classes for banking-related models,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.banking.models import Bank, BankAccount, BankAccountBalance


fake = Faker()


class BankFactory(SessionedFactory):
    """Factory for creating Bank test data."""
    
    class Meta:
        model = Bank

    name = factory.LazyAttribute(lambda _: fake.company())
    country = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'AU', 'US', 'UK', 'CA', 'NZ', 'SG', 'HK', 'JP', 'DE', 'FR', 'CN', 'KR'
    ]))
    bank_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'COMMERCIAL', 'INVESTMENT', 'CENTRAL', 'COOPERATIVE', 'DIGITAL'
    ]))
    swift_bic = factory.LazyAttribute(lambda _: fake.bothify(text='????AU2X', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))


class BankAccountFactory(SessionedFactory):
    """Factory for creating BankAccount test data."""
    
    class Meta:
        model = BankAccount

    # Create required relationships automatically
    entity = factory.SubFactory('tests.factories.entity_factories.EntityFactory')
    bank = factory.SubFactory(BankFactory)
    
    account_name = factory.LazyAttribute(lambda _: fake.bothify(text='Account ????', letters='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))
    account_number = factory.LazyAttribute(lambda _: fake.bothify(text='????-????-????-????', letters='0123456789'))
    currency = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF', 'CNY', 'KRW'
    ]))
    account_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'CHECKING', 'SAVINGS', 'INVESTMENT', 'BUSINESS', 'TRUST', 'JOINT'
    ]))


class BankAccountBalanceFactory(SessionedFactory):
    """Factory for creating BankAccountBalance test data."""
    
    class Meta:
        model = BankAccountBalance

    # Create required relationships automatically
    bank_account = factory.SubFactory(BankAccountFactory)
    
    currency = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'AUD', 'USD', 'EUR', 'GBP', 'CAD', 'NZD', 'SGD', 'HKD', 'JPY', 'CHF', 'CNY', 'KRW'
    ]))
    date = factory.LazyAttribute(lambda _: fake.date_between(start_date='-1y', end_date='today'))
    balance_statement = factory.LazyAttribute(lambda _: round(fake.pyfloat(min_value=0, max_value=1000000, right_digits=2), 2))
    balance_adjustment = factory.LazyAttribute(lambda _: round(fake.pyfloat(min_value=-10000, max_value=10000, right_digits=2), 2))
    balance_final = factory.LazyAttribute(lambda obj: round(obj.balance_statement + obj.balance_adjustment, 2))
