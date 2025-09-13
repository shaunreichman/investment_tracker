"""
Fund Event Handlers Module.

This module contains the banking integration handler for cross-module events.
Other fund event handlers have been replaced by the service layer architecture.
"""

from src.fund.events.handlers.banking_integration_handler import BankingIntegrationHandler

__all__ = [
    'BankingIntegrationHandler',
]
