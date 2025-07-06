"""
Tax domain module.

This module contains all tax-related models and business logic.
Tax statements, calculations, and reconciliation logic are handled here.
"""

from .models import TaxStatement

__all__ = [
    'TaxStatement'
] 