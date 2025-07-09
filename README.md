# Investment Tracker

A Python-based system for tracking multiple investments across companies and funds, with support for both NAV-based and cost-based valuation, IRR calculation, tax statement reconciliation, and robust event modeling.

---

## ⚡️ Domain-Driven Architecture (2024 Migration)

**This project has been migrated to a domain-driven architecture.**
- All models, calculations, and creation logic are now organized by domain (fund, tax, entity, rates, investment company, shared).
- The old `src/models.py`, `src/calculations.py`, and `src/utils.py` files are now **deprecated** and kept for reference only.
- All imports should use the new domain modules (see below).

---

## Project Overview

This app tracks investments, cash flows, and fund performance. It supports:

### Fund Types
- **NAV-Based Funds**: Track investments with regular NAV updates (shares, ETFs, unit trusts)
- **Cost-Based Funds**: Track investments held at cost (private equity, venture capital, real estate)

### Key Features
- IRR and after-tax IRR calculation
- Tax statement management and reconciliation
- Automated event generation (tax payments, risk-free interest charges, etc.)
- Automatic calculation of derived fields (equity balances, unit tracking, etc.)

**Data is stored in SQLite via SQLAlchemy.**  
**All business logic is tested with a comprehensive system test.**

### Recent Improvements
- **Standardized date conventions**: All calculations now use inclusive start dates and exclusive end dates for consistency
- **Automatic event listeners**: NAV-based funds automatically update current units after unit purchase/sale events
- **Enhanced FIFO tracking**: NAV-based funds use FIFO cost basis for accurate equity balance calculations
- **Improved IRR calculations**: Complete support for NAV-based fund IRR with unit sales included
- **2024: Domain-driven architecture migration**

---

## Directory Structure (Domain-Driven)

- `src/` — Main application code
  - `__init__.py` — Package exports (imports from all domain modules)
  - `database.py` — DB setup and connection
  - `shared/` — Shared utilities and base classes
    - `base.py`, `calculations.py`, `utils.py`
  - `fund/` — Fund models, calculations, creation, queries
    - `models.py`, `calculations.py`, `creation.py`, `queries.py`
  - `tax/` — Tax statement models, calculations, creation
    - `models.py`, `calculations.py`, `creation.py`
  - `entity/` — Entity models, calculations, creation
    - `models.py`, `calculations.py`, `creation.py`
  - `rates/` — Risk-free rate models, calculations, creation
    - `models.py`, `calculations.py`, `creation.py`
  - `investment_company/` — Investment company models, calculations, creation
    - `models.py`, `calculations.py`, `creation.py`
  - `dashboard/` — (Optional) Dashboard code
  - `models.py` — **DEPRECATED** (see above)
  - `calculations.py` — **DEPRECATED** (see above)
  - `utils.py` — **DEPRECATED** (see above)
- `test_full_system.py` — Comprehensive system test
- `data/` — Data files (e.g., risk-free rates)
- `DESIGN_GUIDELINES.md` — In-depth design, conventions, and rationale

---

## Domain-Driven Architecture

- **Each domain (fund, tax, entity, rates, investment company) has its own models, calculations, and creation logic.**
- **Shared logic** (utilities, base classes, pure calculations) lives in `src/shared/`.
- **All imports** should use the new domain modules, e.g.:
  ```python
  from src.fund.models import Fund, FundEvent, FundType
  from src.tax.models import TaxStatement
  from src.entity.models import Entity
  from src.rates.models import RiskFreeRate
  from src.investment_company.models import InvestmentCompany
  from src.shared.utils import with_session
  ```
- **Old files** (`src/models.py`, `src/calculations.py`, `src/utils.py`) are kept for reference only and are fully commented out.

---

## Business Logic vs Database Operations

All model methods are now designed to **separate business logic from database operations** for clarity, testability, and maintainability:

- **Pure business logic** (object creation, calculations, orchestration) is implemented in private methods (prefixed with `_`) or in domain `calculations.py` files. These methods do not perform any database operations and do not require a session.
- **Database operations** (adding, deleting, committing, querying) are handled only in public model methods decorated with `@with_session`. These methods are responsible for session management and call the pure business logic methods as needed.

**Pattern Example:**
```python
from src.fund.models import Fund
from src.tax.models import TaxStatement
from src.shared.utils import with_session

class Fund(...):
    ...
    def _create_tax_payment_event_object(self, tax_statement):
        # Pure business logic: create event object, no DB ops
        ...
        return event

    @with_session
    def create_tax_payment_events(self, session=None):
        # DB operations: add event to session, commit
        event = self._create_tax_payment_event_object(...)
        session.add(event)
        session.commit()
```

- **No business logic should be mixed with session.add, session.commit, or session.delete.**
- This pattern is followed throughout all models (Fund, TaxStatement, etc.).
- See `src/fund/models.py` and other domain modules for examples and `DESIGN_GUIDELINES.md` for more details.

---

## Session Handling

All model methods that require a database session use the `@with_session` decorator (see `src/shared/utils.py`).  
- **You do not need to manually resolve or pass a session** when calling these methods—just use the method as normal.
- Only methods that perform database queries are decorated; orchestration/helper methods are not.

---

## Quickstart

```sh
pip install -r requirements.txt
python3 test_full_system.py
```

---

## Example Usage

### NAV-Based Fund Example
```python
from src.fund.models import Fund, FundEvent, EventType, DistributionType
from datetime import date

# 1. Create NAV-based fund (minimal manual fields)
fund = Fund(
    name="ABC Ltd",
    tracking_type=FundType.NAV_BASED,
    fund_type="Equity - Consumer Discretionary",
    currency="AUD"
)

# 2. Add unit purchase (amount calculated automatically)
purchase_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.UNIT_PURCHASE,
    event_date=date(2023, 3, 28),
    units_purchased=85.0,
    unit_price=58.00,
    brokerage_fee=19.95,
    description="Initial unit purchase"
)
# amount will be calculated as: (85.0 * 58.00) + 19.95 = 4,949.95

# 3. Add NAV update (shares_owned calculated automatically)
nav_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.NAV_UPDATE,
    event_date=date(2023, 3, 31),
    nav_per_share=57.20,
    description="March 2023 NAV update"
)
```

### Cost-Based Fund Example
```python
# Create cost-based fund
fund = Fund(
    name="Private Equity Fund",
    tracking_type=FundType.COST_BASED,
    commitment_amount=1000000.0,
    expected_irr=15.0,
    expected_duration_months=120
)

# Add capital call
call_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.CAPITAL_CALL,
    event_date=date(2023, 1, 1),
    amount=500000.0
)

# Update calculated fields
fund.update_current_equity_balance()
fund.update_total_cost_basis()

# Calculate IRR
irr = fund.calculate_irr()
```

---

## Design & Contribution

- **Business logic** is separated from pure calculations (see `calculations.py`).
- **Session handling** is centralized with `@with_session` for maintainability.
- **Field classification**: Manual fields (set by user) vs calculated fields (set by system)
- **See [`DESIGN_GUIDELINES.md`](./DESIGN_GUIDELINES.md)** for:
  - Detailed field classification (manual vs. automatic)
  - Event and tax statement modeling
  - Calculation workflows
  - Coding conventions and best practices

---

## Testing

Run the comprehensive system test:
```sh
python3 test_full_system.py
```
This will clear the database, set up test data, recalculate all derived values, and verify correctness.

---

## Roadmap

- Streamlit dashboard for interactive performance and allocation visualization
- Asset class breakdowns
- Year-by-year performance reporting

---

## Maintainer

Shaun Reichman

---

*For deeper technical rationale, see [DESIGN_GUIDELINES.md](./DESIGN_GUIDELINES.md).*

## Tax Event Creation Framework

This project uses a standardized, robust framework for creating tax payment events (interest, franked/unfranked dividends, FY debt cost, etc.) for investment funds.

### Why?
- Eliminates code duplication and inconsistencies
- Ensures all tax events are deduplicated and updatable
- Makes it easy to add new tax event types and maintain business logic

### How to Use
To create all applicable tax payment events for a fund's tax statement:

```python
from src.tax.events import TaxEventManager

# Given a TaxStatement instance and a SQLAlchemy session:
created_or_updated_events = TaxEventManager.create_or_update_tax_events(tax_statement, session)
```

Or, for all tax statements of a fund:

```python
created_events = fund.create_tax_payment_events(session=session)
```

- The framework will create, update, or deduplicate events as needed.
- See DESIGN_GUIDELINES.md for advanced usage, edge cases, and technical rationale.