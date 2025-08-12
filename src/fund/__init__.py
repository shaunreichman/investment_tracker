"""
Fund domain module.

This module contains all fund-related models, calculations, and business logic.
Funds can be either NAV-based (tracking units and NAV) or cost-based (tracking capital calls/returns).
"""

from .enums import FundType, EventType, DistributionType
from .models import Fund, FundEvent
from .calculations import *
from .queries import *

__all__ = [
    'Fund',
    'FundEvent', 
    'FundType',
    'EventType',
    'DistributionType',
] 