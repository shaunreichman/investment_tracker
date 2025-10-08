"""
Shared Models Package.

This package contains the new, clean shared models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.
"""

from src.shared.models.domain_update_event import DomainUpdateEvent, DomainFieldChange

__all__ = [
    'DomainUpdateEvent',
    'DomainFieldChange',
]