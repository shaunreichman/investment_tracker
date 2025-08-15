"""
Event Consumer Handlers.

This module contains specific event handlers for different types of
dependent updates in the system.
"""

from .tax_statement_event_handler import TaxStatementEventHandler
from .company_record_event_handler import CompanyRecordEventHandler

__all__ = [
    'TaxStatementEventHandler',
    'CompanyRecordEventHandler'
]
