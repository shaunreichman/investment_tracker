# Investment Tracker

A Python-based system for tracking multiple investments across companies and funds, with support for both NAV-based and cost-based valuation, IRR calculation, tax statement reconciliation, and robust event modeling.

---

## ⚡️ Domain-Driven Architecture (2024 Migration)

**This project uses a domain-driven architecture.**
- All models, calculations, and creation logic are organized by domain (fund, tax, entity, rates, investment company, shared).
- Old files (`src/models.py`, `src/calculations.py`, `src/utils.py`) have been removed or are fully deprecated.
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

```
investment_tracker/
├── src/                       # Core application code (domain-driven)
│   ├── fund/                  # Fund models, calculations, queries
│   ├── tax/                   # Tax models, events, calculations
│   ├── entity/                # Entity models, calculations
│   ├── investment_company/    # Investment company domain
│   ├── rates/                 # Risk-free rates and related logic
│   ├── shared/                # Shared utilities and base classes
│   └── database.py            # Database setup and session management
├── tests/                     # Test suite (unit, integration, system)
│   └── output/                # Test output artifacts
├── scripts/                   # Utility and migration scripts
├── docs/                      # Documentation
│   ├── DESIGN_GUIDELINES.md   # Core development/design patterns
│   ├── PROJECT_CONTEXT.md     # Project context and onboarding
│   └── refactor_plans/        # Refactoring and migration plans
├── alembic/                   # Database migrations (Alembic)
├── data/                      # Data files and backups
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project configuration
├── README.md                  # User-facing documentation
└── .gitignore
```

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

---

## Field Classification: (SYSTEM / MANUAL / CALCULATED / HYBRID)

- **(SYSTEM):** Set by the database/ORM (e.g., primary keys, timestamps)
- **(MANUAL):** Set by the user/developer (e.g., business data, foreign keys)
- **(CALCULATED):** Set by business logic only, never manually
- **(HYBRID):** Can be set manually or calculated, with clear precedence

See [`docs/DESIGN_GUIDELINES.md`](./docs/DESIGN_GUIDELINES.md) for a full field reference and examples.

---

## Business Logic vs Database Operations

All model methods are designed to **separate business logic from database operations** for clarity, testability, and maintainability:

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
- See `src/fund/models.py` and other domain modules for examples and [`docs/DESIGN_GUIDELINES.md`](./docs/DESIGN_GUIDELINES.md) for more details.

---

## Session Handling

All model methods that require a database session use the `@with_session` decorator (see `src/shared/utils.py`).  
- **Always pass `session` as a keyword argument.**
- Only methods that perform database queries are decorated; orchestration/helper methods are not.
- The backend (not clients) owns session lifecycle.

---

## Quickstart

```sh
pip install -r requirements.txt
PYTHONPATH=. python tests/test_main.py
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
- **Field classification**: All fields are explicitly marked as (SYSTEM), (MANUAL), (CALCULATED), or (HYBRID) in the codebase and documentation.
- **See [`docs/DESIGN_GUIDELINES.md`](./docs/DESIGN_GUIDELINES.md)** for:
  - Detailed field classification
  - Event and tax statement modeling
  - Calculation workflows
  - Coding conventions and best practices
- **See [`docs/refactor_plans/`](./docs/refactor_plans/)** for ongoing and historical refactoring plans.

---

## Testing

Run the main test suite:
```sh
PYTHONPATH=. python tests/test_main.py
```
This will clear the database, set up test data, recalculate all derived values, and verify correctness.

- All test scripts are located in the `tests/` directory for better organization.
- Source code is under `src/`.
- Database and Alembic migration files are under `alembic/`.

To run all tests with pytest (if desired):
  ```
  pytest tests/
  ```
- All new test scripts should be placed in the `tests/` directory.
- **Calculated fields** (e.g., `tax_payable`, `interest_tax_benefit`, `total_interest_expense`) must never be set directly in tests or production code. Always use the appropriate calculation method to set these fields.

---

## Cleanup Policy

- Debug and temporary output files (e.g., `CashFlowDebug.txt`, `DividendTaxDebug.txt`) should not be committed to the repository.
- Reference files (e.g., historical versions of modules) should be removed after they are no longer needed.
- Utility scripts are now organized in the `scripts/` directory.
- All documentation (including refactor plans) is in the `docs/` directory.

---

## Roadmap

- Streamlit dashboard for interactive performance and allocation visualization
- Additional financial metrics and calculations
- Data import/export features
- Real-time market data integration
- Ongoing refactoring plans tracked in [`docs/refactor_plans/`](./docs/refactor_plans/)