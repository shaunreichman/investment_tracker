"""
Company Models Package.

This package contains the company models with professional architecture.
Models handle only data persistence and basic validation, with business logic
delegated to services through the orchestrator.

Architecture mirrors the successful fund refactor pattern.
"""

# Import models
from src.company.models.contact import Contact
from src.company.models.company import Company

__all__ = [
    'Contact',
    'Company',
]