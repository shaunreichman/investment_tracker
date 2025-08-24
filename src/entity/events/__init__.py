"""
Entity Events Module.

This module contains event handling for the entity system,
including banking integration and other cross-module events.
"""

from .banking_integration_handler import EntityBankingIntegrationHandler

__all__ = [
    'EntityBankingIntegrationHandler',
]
