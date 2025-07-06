"""
DEPRECATED - This file has been migrated to domain-driven architecture.

All models and functionality have been moved to their respective domain modules:
- Fund, FundEvent, enums → src/fund/models.py
- Entity → src/entity/models.py  
- TaxStatement → src/tax/models.py
- RiskFreeRate → src/rates/models.py
- InvestmentCompany → src/investment_company/models.py

This file is kept for reference only and should not be used in new code.
All imports should use the new domain modules instead.

Migration completed: [Date]
"""

# DEPRECATED - All content below has been migrated to domain modules
# This file is kept for reference only

"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Date, Boolean, Enum, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import enum
from sqlalchemy import func
import numpy as np
import numpy_financial as npf
from sqlalchemy import event
from src.utils import with_session
from src.calculations import (
    calculate_irr,
    calculate_average_equity_balance_nav,
    calculate_average_equity_balance_cost,
    calculate_debt_cost,
    get_equity_change_for_event,
    calculate_nav_based_capital_gains,
    calculate_cost_based_capital_gains,
    orchestrate_nav_based_average_equity,
    orchestrate_cost_based_average_equity,
    orchestrate_irr_base,
    net_income,
    tax_payable,
    interest_tax_benefit,
    get_risk_free_rate_for_date,
    get_reconciliation_explanation,
    get_financial_years_for_fund_period
)
from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.elements import ColumnElement

Base = declarative_base()


class EventType(enum.Enum):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class FundType(enum.Enum):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class DistributionType(enum.Enum):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class InvestmentCompany(Base):
    # DEPRECATED - Moved to src/investment_company/models.py
    pass


class Entity(Base):
    # DEPRECATED - Moved to src/entity/models.py
    pass


class Fund(Base):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class TaxPaymentType(enum.Enum):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class FundEvent(Base):
    # DEPRECATED - Moved to src/fund/models.py
    pass


class RiskFreeRate(Base):
    # DEPRECATED - Moved to src/rates/models.py
    pass


class TaxStatement(Base):
    # DEPRECATED - Moved to src/tax/models.py
    pass
"""