"""
Shared domain module.

This module contains shared utilities, base classes, and common functionality used across domains.
"""

from src.shared.enums import SortOrder, EventOperation, Country, Currency
from src.shared.base import Base
from src.shared.utils import *

__all__ = [
    'SortOrder',
    'EventOperation',
    'Country',
    'Currency',
    'Base',
    'utils',
]