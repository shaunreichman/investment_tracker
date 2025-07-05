# Investment Tracker

A Python-based system for tracking multiple investments across companies and funds, with support for both NAV-based and cost-based valuation, IRR calculation, tax statement reconciliation, and robust event modeling.

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

---

## Fund Types Explained

### NAV-Based Funds
**Use for**: Listed shares, ETFs, unit trusts, managed funds with regular NAV reporting

**Key Characteristics**:
- No fixed commitment amount (buy units as needed)
- No expected IRR (performance determined by market)
- No fixed duration (hold as long as desired)
- Track units owned and unit prices
- NAV updates provide current market value

**Manual Fields Only**:
```python
fund = Fund(
    name="ABC Ltd",
    fund_type="Equity - Consumer Discretionary",
    tracking_type=FundType.NAV_BASED,
    currency="AUD",
    description="ABC Ltd on the ASX"
)
```

**Automatic Calculations**:
- `current_units`: Total units owned (from purchase/sale events)
- `current_unit_price`: Latest unit price (from NAV updates)
- `current_equity_balance`: FIFO cost basis of remaining units
- `amount` in unit events: (units × unit price) ± brokerage fees
- `cost_of_units`: FIFO cost basis after each unit event
- `shares_owned` in NAV events: Cumulative units at that date

**Note**: NAV-based funds use FIFO (First In, First Out) cost basis tracking for accurate equity balance calculations.

### Cost-Based Funds
**Use for**: Private equity, venture capital, real estate, infrastructure funds

**Key Characteristics**:
- Fixed commitment amount
- Expected IRR and duration
- Track capital calls and returns
- Value based on cost basis

**Manual Fields**:
```python
fund = Fund(
    name="Blackstone Real Estate Partners X",
    fund_type="Real Estate",
    tracking_type=FundType.COST_BASED,
    commitment_amount=1000000.0,
    expected_irr=15.0,
    expected_duration_months=120,
    currency="USD",
    description="Real estate private equity fund"
)
```

**Automatic Calculations**:
- `total_cost_basis`: Capital calls - capital returns
- `current_equity_balance`: Same as total_cost_basis
- `is_active`: True if equity balance > 0

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

### NAV-Based Fund Example
```python
from src.models import Fund, FundEvent, EventType, DistributionType
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
# shares_owned will be calculated as: 85.0

# 4. Update calculated fields
fund.update_current_units_and_price()
fund.update_current_equity_balance()

# 5. Calculate IRR
irr = fund.calculate_irr()
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