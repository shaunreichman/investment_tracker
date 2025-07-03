# Investment Tracker

A Python-based system for tracking multiple investments across companies and funds, with support for both NAV-based and cost-based valuation, IRR calculation, tax statement reconciliation, and robust event modeling.

---

## Project Overview

This app tracks investments, cash flows, and fund performance. It supports:
- NAV-based and cost-based fund tracking
- IRR and after-tax IRR calculation
- Tax statement management and reconciliation
- Automated event generation (tax payments, risk-free interest charges, etc.)

**Data is stored in SQLite via SQLAlchemy.**  
**All business logic is tested with a comprehensive system test.**

---

## Tech Stack

- Python 3.x
- SQLAlchemy (ORM)
- SQLite
- pandas, numpy
- (Optional: Streamlit for future dashboards)
- pytest

---

## Directory Structure

- `src/` — Main application code
  - `models.py` — ORM models and business logic
  - `calculations.py` — Pure calculation utilities (IRR, equity, tax, etc.)
  - `utils.py` — Session handling and helpers
  - `database.py` — DB setup and connection
- `test_full_system.py` — Comprehensive system test
- `data/` — Data files (e.g., risk-free rates)
- `DESIGN_GUIDELINES.md` — In-depth design, conventions, and rationale

---

## Session Handling

All model methods that require a database session use the `@with_session` decorator (see `src/utils.py`).  
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

```python
from src.models import Fund

# Create or load a fund (see DESIGN_GUIDELINES.md for field details)
fund = Fund(...)

# Update calculated fields
fund.update_current_equity_balance()
fund.update_average_equity_balance()

# Calculate IRR
irr = fund.calculate_irr()
after_tax_irr = fund.calculate_after_tax_irr()
```

---

## Design & Contribution

- **Business logic** is separated from pure calculations (see `calculations.py`).
- **Session handling** is centralized with `@with_session` for maintainability.
- **See [`DESIGN_GUIDELINES.md`](./DESIGN_GUIDELINES.md)** for:
  - Field classification (manual vs. automatic)
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