"""
Entity Domain Factories.

This module contains all factory classes for entity-related models,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.entity.models import Entity


fake = Faker()


class EntityFactory(SessionedFactory):
    """Factory for creating Entity test data."""
    
    class Meta:
        model = Entity

    name = factory.Sequence(lambda n: f"Entity {n:04d}")
    description = factory.LazyAttribute(lambda _: fake.catch_phrase())
    entity_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'PERSON', 'COMPANY', 'TRUST', 'FUND', 'OTHER'
    ]))
    tax_jurisdiction = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        'AU', 'US', 'UK', 'CA', 'NZ', 'SG', 'HK', 'JP', 'DE', 'FR', 'CN', 'KR'
    ]))
