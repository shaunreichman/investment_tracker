"""
Base Fund Event Handler.

This module provides the base class for all fund event handlers,
defining the common interface and shared functionality.

Key responsibilities:
- Common event processing logic
- Event validation and error handling
- Event relationship management
- Event publishing and side effects
"""

from typing import Dict, Any, Optional, List
from datetime import date, datetime
from sqlalchemy.orm import Session
from abc import ABC, abstractmethod

from src.fund.models import Fund, FundEvent
from src.fund.enums import EventType, FundType, FundStatus
from src.fund.services.fund_calculation_service import FundCalculationService
from src.fund.services.fund_status_service import FundStatusService
from src.fund.services.tax_calculation_service import TaxCalculationService
