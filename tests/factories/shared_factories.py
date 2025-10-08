"""
Shared Domain Factories.

This module contains all factory classes for shared models across the system,
following enterprise best practices for test data generation.
"""

import factory
from faker import Faker

from tests.factories.base import SessionedFactory
from src.shared.models.domain_update_event import DomainUpdateEvent
from src.fund.enums.fund_event_enums import EventType
from src.shared.enums.shared_enums import EventOperation
from src.shared.enums.domain_update_event_enums import DomainObjectType


fake = Faker()


class DomainUpdateEventFactory(SessionedFactory):
    """Factory for creating DomainUpdateEvent test data."""
    
    class Meta:
        model = DomainUpdateEvent

    # Domain object information (manual fields)
    domain_object_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        DomainObjectType.FUND,
        DomainObjectType.FUND_EVENT,
        DomainObjectType.FUND_EVENT_CASH_FLOW,
        DomainObjectType.FUND_TAX_STATEMENT,
        DomainObjectType.INVESTMENT_COMPANY,
        DomainObjectType.ENTITY,
        DomainObjectType.BANK,
        DomainObjectType.BANK_ACCOUNT,
        DomainObjectType.BANK_ACCOUNT_BALANCE,
        DomainObjectType.CONTACT,
        DomainObjectType.FX_RATE,
        DomainObjectType.RISK_FREE_RATE
    ]))
    domain_object_id = factory.LazyAttribute(lambda _: fake.random_int(min=1, max=1000))
    
    # Event operation (manual field)
    event_operation = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        EventOperation.CREATE,
        EventOperation.UPDATE,
        EventOperation.DELETE
    ]))
    
    # Fund event type (optional, only when domain object is a fund event)
    fund_event_type = factory.LazyAttribute(lambda _: fake.random_element(elements=[
        EventType.CAPITAL_CALL,
        EventType.RETURN_OF_CAPITAL,
        EventType.DISTRIBUTION,
        EventType.UNIT_PURCHASE,
        EventType.UNIT_SALE,
        EventType.NAV_UPDATE,
        EventType.DAILY_RISK_FREE_INTEREST_CHARGE,
        EventType.EOFY_DEBT_COST,
        EventType.TAX_PAYMENT
    ]))
    
    # Event data payload (manual field)
    event_data = factory.LazyAttribute(lambda _: {
        'field_name': fake.word(),
        'old_value': fake.word(),
        'new_value': fake.word(),
        'timestamp': fake.iso8601()
    })
