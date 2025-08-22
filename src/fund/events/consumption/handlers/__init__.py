"""
Event Consumption Handlers.

This module contains all the event handlers that consume domain events
and perform business logic in response to those events.
"""

from src.fund.events.consumption.handlers.tax_statement_event_handler import TaxStatementEventHandler
from src.fund.events.consumption.handlers.company_record_event_handler import CompanyRecordEventHandler
from src.fund.events.consumption.handlers.capital_chain_event_handler import CapitalChainEventHandler
from src.fund.events.consumption.handlers.fund_status_event_handler import FundStatusEventHandler

__all__ = [
    'TaxStatementEventHandler',
    'CompanyRecordEventHandler',
    'CapitalChainEventHandler',
    'FundStatusEventHandler'
]
