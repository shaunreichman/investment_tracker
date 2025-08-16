"""
Event Consumer Handlers.

This module contains specific event handlers for different types of
dependent updates in the system.
"""

from .tax_statement_event_handler import TaxStatementEventHandler
from .company_record_event_handler import CompanyRecordEventHandler
from .capital_chain_event_handler import CapitalChainEventHandler
from .fund_status_event_handler import FundStatusEventHandler

__all__ = [
    'TaxStatementEventHandler',
    'CompanyRecordEventHandler',
    'CapitalChainEventHandler',
    'FundStatusEventHandler'
]
