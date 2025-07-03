# Investment Tracker Design Guidelines

> See [README.md](./README.md) for a high-level project overview, quickstart, and usage examples.

---

**Note:**
- Streamlit dashboarding is a planned roadmap feature and is **not yet implemented**. All logic and testing should be completed first.
- **Always run `test_full_system.py` before merging major changes** to ensure the system remains correct and stable.
- If you make significant changes to the codebase or API, **please update this DESIGN_GUIDELINES.md to keep it in sync**.

---

## Session Handling Convention

- All model methods that require a SQLAlchemy session are decorated with `@with_session` (see `src/utils.py`).
- This decorator ensures a session is always available, removing the need for manual session resolution in each method.
- **Only methods that directly perform database queries or ORM operations should be decorated.**
- Orchestration/helper methods that only call other decorated methods do **not** need the decorator.
- Always call decorated methods with `session=session` as a keyword argument if passing a session explicitly.

**Example:**
```python
@with_session
def update_current_equity_balance(self, session=None):
    # ... use session ...
```

---

## Where to Put New Logic

| Type of Logic                | Where to Put It                |
|------------------------------|-------------------------------|
| Database queries/ORM ops     | Decorated model methods       |
| Pure calculations/stateless  | `calculations.py`             |
| Session helpers/decorators   | `utils.py`                    |
| Orchestration (no queries)   | Undecorated model methods     |

---

## Common Pitfalls

- **Do not pass `session` as a positional argument to decorated methods.**  
  Always use `session=session` as a keyword argument.
- **Do not decorate pure calculation or property methods.**
- **If you see 'got multiple values for argument session',** check for positional session arguments or double-injection.

---

## Changelog / Major Refactors

- **2024-05:** Centralized session handling using the `@with_session` decorator.  
  - Removed repetitive session resolution code from model methods.
  - Improved maintainability and reduced boilerplate.

---

## Field Classification: Manual vs Automatic

This document clarifies which fields should be manually set by users and which should be automatically calculated by the system.

## Fund Model Fields

### MANUAL FIELDS (Set by User)
These fields represent the fundamental characteristics of a fund and should be set when creating the fund:

```python
# Basic fund information
name = Column(String(255), nullable=False)
fund_type = Column(String(100))  # e.g., 'Private Equity', 'Venture Capital'
tracking_type = Column(Enum(FundType), nullable=False)  # NAV_BASED or COST_BASED
commitment_amount = Column(Float, nullable=False)  # Total amount committed
expected_irr = Column(Float)  # Expected IRR as percentage
expected_duration_months = Column(Integer)  # Expected fund duration
description = Column(Text)
currency = Column(String(10), default="AUD")
```

### AUTOMATIC FIELDS (Calculated by System)
These fields should NEVER be manually set - they are calculated from events and other data:

```python
# Equity tracking (calculated from capital movements)
current_equity_balance = Column(Float, default=0.0)  # Calculated from capital calls - returns
average_equity_balance = Column(Float, default=0.0)  # Calculated from time-weighted average

# Fund status (calculated from equity balance)
is_active = Column(Boolean, default=True)  # Calculated from current_equity_balance > 0
final_tax_statement_received = Column(Boolean, default=False)  # Calculated from tax statements vs fund end date

# NAV-based fund specific (calculated from NAV events)
current_units = Column(Float)  # Calculated from cumulative NAV update events
current_unit_price = Column(Float)  # Calculated from most recent NAV update

# Cost-based fund specific (calculated from capital movements)
total_cost_basis = Column(Float)  # Calculated from capital calls - capital returns

# Derived properties (calculated on-demand)
@property
def start_date(self):  # Calculated from first capital call
@property  
def end_date(self):  # Calculated when equity balance goes to 0
@property
def current_value(self):  # Calculated based on fund type
@property
def total_investment_duration_months(self):  # Calculated from start/end dates
```

## FundEvent Model Fields

### MANUAL FIELDS (Set by User)
```python
# Event identification
fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
event_type = Column(Enum(EventType), nullable=False)
event_date = Column(Date, nullable=False)
amount = Column(Float)  # The cash flow amount

# Event-specific data (depending on event type)
distribution_type = Column(Enum(DistributionType))  # For distributions
units_purchased = Column(Float)  # For unit purchases
units_sold = Column(Float)  # For unit sales
unit_price = Column(Float)  # For unit transactions
nav_per_share = Column(Float)  # For NAV updates

# Metadata
description = Column(Text)
reference_number = Column(String(100))
```

### AUTOMATIC FIELDS (Calculated by System)
```python
# NAV tracking (calculated from NAV events)
shares_owned = Column(Float)  # Calculated from cumulative NAV update events
```

**Note**: Tax withholding is handled via separate `TAX_PAYMENT` events, not as fields on distribution events.

## TaxStatement Model Fields

### MANUAL FIELDS (Set by User)
```python
# Statement identification
fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
financial_year = Column(String(10), nullable=False)

# Interest income breakdown (manual)
distribution_receivable_this_fy = Column(Float, default=0.0)  # Accounting income for this FY, not yet received
distribution_received_prev_fy = Column(Float, default=0.0)    # Accounting income from prev FY, received this FY
interest_received_in_cash = Column(Float, default=0.0)        # Actual cash flow received this FY
non_resident_withholding_tax_from_statement = Column(Float, default=0.0)  # Withholding tax as reported on the statement

# Other manual fields (unchanged)
foreign_income = Column(Float, default=0.0)
capital_gains = Column(Float, default=0.0)
other_income = Column(Float, default=0.0)
tax_withheld = Column(Float, default=0.0)
foreign_tax_credits = Column(Float, default=0.0)
interest_taxable_rate = Column(Float, default=0.0)  # Manually defined interest tax rate (%)
interest_deduction_rate = Column(Float, default=0.0)  # Manually defined interest deduction rate (%) for interest expense tax benefit
non_resident = Column(Boolean, default=False)
accountant = Column(String(255))
notes = Column(Text)
statement_date = Column(Date)
```

### AUTOMATIC FIELDS (Calculated by System)
```python
# Calculated interest income fields
total_interest_income = Column(Float, default=0.0)  # = interest_received_in_cash + distribution_receivable_this_fy - distribution_received_prev_fy
non_resident_withholding_tax_already_withheld = Column(Float, default=0.0)  # = sum of all FundEvent TAX_PAYMENTs with tax_payment_type=NON_RESIDENT_INTEREST_WITHHOLDING for this FY

# Other calculated fields (unchanged)
total_income = Column(Float, default=0.0)
tax_payable = Column(Float, default=0.0)
interest_tax_benefit = Column(Float, default=0.0)
tax_already_paid = Column(Float, default=0.0)
total_interest_expense = Column(Float, default=0.0)

# New tax payment calculation
tax_payable = Column(Float, default=0.0)
tax_payable = Column(Float, default=0.0)
```

### Calculation Workflow
1. Set all manual fields when creating or updating a TaxStatement.
2. Call `calculate_interest_income_fields(session)` to update the calculated fields.
3. Use the calculated fields for reporting, reconciliation, and IRR calculations.

### Calculation Formulas
- `total_interest_income = interest_received_in_cash + distribution_receivable_this_fy - distribution_received_prev_fy`
- `non_resident_withholding_tax_difference = non_resident_withholding_tax_already_withheld - non_resident_withholding_tax_from_statement`

## System-Generated Events

The following event types are created automatically by the system and should NEVER be manually created:

### Tax Payment Events
- **Event Type**: `TAX_PAYMENT`
- **Created by**: `fund.create_tax_payment_events()`
- **Trigger**: When `tax_payable > 0` in tax statements
- **Amount**: `tax_payable` from tax statement

### Daily Risk-Free Interest Charges
- **Event Type**: `DAILY_RISK_FREE_INTEREST_CHARGE`
- **Created by**: `fund.create_daily_risk_free_interest_charges()`
- **Trigger**: For real IRR calculations
- **Amount**: Daily interest charge based on risk-free rates

### FY Debt Cost Events
- **Event Type**: `FY_DEBT_COST`
- **Created by**: `fund.create_fy_debt_cost_events()`
- **Trigger**: For real IRR calculations
- **Amount**: Tax benefit from interest deductions

## Final Tax Statement Tracking

### Purpose
The `final_tax_statement_received` field automatically tracks whether all expected tax statements have been received for a fund, ensuring IRR calculations include all relevant cash flows.

### Logic
- **Active funds**: Always `False` (still waiting for future tax statements)
- **Completed funds**: `True` if tax statement exists for the financial year when the fund ended
- **Automatically calculated**: Never manually set

### Example Scenarios

#### ✅ Fund with Complete Tax Statements
```python
# Fund ended on 2024-08-02 (FY 2024-2025)
# Tax statement exists for FY 2024-2025
fund.final_tax_statement_received  # True
```

#### ❌ Fund Missing Final Tax Statement
```python
# Fund ended on 2024-08-02 (FY 2024-2025)
# No tax statement for FY 2024-2025
fund.final_tax_statement_received  # False
```

#### 🔄 Active Fund
```python
# Fund still has equity balance > 0
fund.final_tax_statement_received  # False (regardless of existing statements)
```

### Usage in IRR Calculations
- **Basic IRR**: Not affected (no tax payments)
- **After-tax IRR**: May be incomplete if `final_tax_statement_received = False`
- **Real IRR**: May be incomplete if `final_tax_statement_received = False`

### Best Practice
Always check `final_tax_statement_received` before reporting final IRR figures for completed funds.

## Removed Fields

### vintage_year
- **Status**: REMOVED
- **Reason**: Not essential, can be derived from `start_date` if needed
- **Impact**: Simplifies fund creation, reduces manual data entry

### gross_interest_income
- **Status**: REMOVED
- **Reason**: Not essential, can be derived from interest income breakdown fields
- **Impact**: Simplifies tax statement creation, reduces manual data entry

### tax_withheld
- **Status**: REMOVED
- **Reason**: Not essential, can be derived from interest income breakdown fields and event-based withholding
- **Impact**: Simplifies tax statement creation, reduces manual data entry

## Best Practices

### Creating a New Fund
1. **Set manual fields only**:
   ```python
   fund = Fund(
       name="My Fund",
       tracking_type=FundType.COST_BASED,
       commitment_amount=100000.0,
       # DO NOT set current_equity_balance, average_equity_balance, is_active, etc.
   )
   ```

2. **Add events to establish equity**:
   ```python
   # Add capital call event
   event = FundEvent(
       fund_id=fund.id,
       event_type=EventType.CAPITAL_CALL,
       event_date=date(2023, 1, 1),
       amount=50000.0
   )
   ```

3. **Let system calculate derived values**:
   ```python
   fund.update_current_equity_balance()  # Calculates from events
   fund.update_average_equity_balance()  # Calculates time-weighted average
   fund.update_active_status()  # Updates is_active based on equity
   ```

### Creating Distributions with Tax Withholding

**IMPORTANT**: Each cash flow should be a separate event. Distribution events should NEVER contain tax withholding information.

#### ✅ CORRECT WAY - Use the provided methods:

1. **Add distribution with tax rate** (recommended):
   ```python
   # This automatically creates both distribution and tax payment events
   dist_event, tax_event = fund.add_distribution_with_tax_rate(
       event_date=date(2024, 12, 15),
       gross_amount=10000.0,
       tax_rate=10.0,  # 10% tax rate
       distribution_type=DistributionType.INTEREST,
       description="Interest distribution"
   )
   # Creates:
   # - DISTRIBUTION event: $10,000 (gross amount)
   # - TAX_PAYMENT event: $1,000 (automatically calculated)
   ```

2. **Add distribution with specific tax amount**:
   ```python
   dist_event, tax_event = fund.add_distribution_with_tax(
       event_date=date(2024, 12, 15),
       gross_amount=10000.0,
       tax_withheld=1000.0,  # Specific tax amount
       distribution_type=DistributionType.INTEREST,
       description="Interest distribution"
   )
   ```

#### ✅ CORRECT WAY - Manual event creation (if needed):

```python
# Create distribution event (gross amount only)
dist_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.DISTRIBUTION,
    event_date=date(2024, 12, 15),
    amount=10000.0,  # Gross amount only
    distribution_type=DistributionType.INTEREST,
    description="Interest distribution"
)

# Create separate tax payment event
tax_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.TAX_PAYMENT,
    event_date=date(2024, 12, 15),
    amount=1000.0,  # Tax amount as separate cash flow
    description="Tax withheld on interest distribution"
)
```

#### Benefits of Separate Events:

1. **Clear cash flow tracking**: Each event represents a distinct cash movement
2. **Accurate IRR calculations**: Tax payments are properly included in after-tax IRR
3. **Flexible tax handling**: Tax rates can vary by distribution type or date
4. **Audit trail**: Clear separation of gross distributions and tax withholdings
5. **Consistent design**: All cash flows follow the same pattern

### Creating Tax Statements
1. **Set income components and rates**:
   ```python
   statement = TaxStatement(
       fund_id=fund.id,
       entity_id=entity.id,
       financial_year="2023-2024",
       distribution_receivable_this_fy=1000.0,
       distribution_received_prev_fy=500.0,
       interest_received_in_cash=8000.0,
       non_resident_withholding_tax_from_statement=1200.0,
       # ... other manual fields ...
   )
   ```

2. **Calculate derived values**:
   ```python
   statement.calculate_tax_payable()  # Calculates from rate
   # total_interest_expense will be calculated from daily interest charges
   ```

3. **Create tax payment events**:
   ```python
   fund.create_tax_payment_events()  # Creates TAX_PAYMENT events
   ```

### Testing Guidelines
When writing tests:
- **DO** set manual fields (fund details, event amounts, tax rates)
- **DON'T** set automatic fields (equity balances, calculated totals, is_active)
- **DO** call calculation methods to verify they work
- **DO** verify that system-generated events are created correctly

## Common Mistakes to Avoid

1. **Setting equity balances manually** - These should always be calculated from events
2. **Setting is_active manually** - Should be calculated from equity balance
3. **Setting current_units/current_unit_price manually** - Should be calculated from NAV events
4. **Setting total_cost_basis manually** - Should be calculated from capital movements
5. **Setting shares_owned manually** - Should be calculated from NAV events
6. **Setting total_interest_expense manually** - Should be calculated from daily interest charges
7. **Creating system-generated events manually** - Let the system create TAX_PAYMENT, DAILY_RISK_FREE_INTEREST_CHARGE, and FY_DEBT_COST events
8. **Setting calculated totals manually** - Let the system calculate total_income, tax_payable, etc.
9. **Not calling calculation methods** - Always call update methods after adding events

## Validation Rules

The system should enforce these rules:
- `current_equity_balance`, `average_equity_balance`, `is_active` should be read-only (calculated only)
- `current_units`, `current_unit_price`, `total_cost_basis` should be read-only (calculated only)
- `shares_owned` should be read-only (calculated only)
- `total_interest_expense` should be read-only (calculated only)
- System-generated event types should not be manually created
- Tax statements should have `interest_taxable_rate` set before calculating `tax_payable`
- Tax payment is calculated as: `total_interest_income * interest_taxable_rate - non_resident_withholding_tax_from_statement`.
- Fund type should determine which fields are valid (NAV vs cost-based)

## Tax Payment Type

### Purpose
The `tax_payment_type` field is used to categorize tax payment events for future-proofing and filtering.

### Recommended Values
- **INTEREST**: For interest-related tax payments
- **CAPITAL_GAINS**: For capital gains tax payments
- **FOREIGN_INCOME**: For tax payments related to foreign income
- **OTHER**: For tax payments related to other types of income

### Usage
- **Filtering**: Use `tax_payment_type` to filter tax payment events based on their type.
- **Reconciliation**: Use `tax_payment_type` to reconcile tax payment events with tax statements.

### Example
```python
# Create a tax payment event with a specific tax_payment_type
tax_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.TAX_PAYMENT,
    event_date=date(2024, 12, 15),
    amount=1000.0,
    tax_payment_type=TaxPaymentType.INTEREST,
    description="Tax withheld on interest distribution"
)
```

### How to Use
1. **Filtering**: Use `tax_payment_type` in queries to filter events based on their type.
2. **Reconciliation**: Use `tax_payment_type` to verify that tax payments are correctly recorded in tax statements.

## Add a Section on Tax Payment Type

### Purpose
The `tax_payment_type` field is used to categorize tax payment events for future-proofing and filtering.

### Recommended Values
- **INTEREST**: For interest-related tax payments
- **CAPITAL_GAINS**: For capital gains tax payments
- **FOREIGN_INCOME**: For tax payments related to foreign income
- **OTHER**: For tax payments related to other types of income

### Usage
- **Filtering**: Use `tax_payment_type` to filter tax payment events based on their type.
- **Reconciliation**: Use `tax_payment_type` to reconcile tax payment events with tax statements.

### Example
```python
# Create a tax payment event with a specific tax_payment_type
tax_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.TAX_PAYMENT,
    event_date=date(2024, 12, 15),
    amount=1000.0,
    tax_payment_type=TaxPaymentType.INTEREST,
    description="Tax withheld on interest distribution"
)
```

### How to Use
1. **Filtering**: Use `tax_payment_type` in queries to filter events based on their type.
2. **Reconciliation**: Use `tax_payment_type` to verify that tax payments are correctly recorded in tax statements.

## FundEvent Model Fields

### TAX_PAYMENT Event Type
- Add `tax_payment_type` (Enum) to distinguish the purpose of each tax payment.
- **Enum values:**
  - `NON_RESIDENT_INTEREST_WITHHOLDING`
  - `CAPITAL_GAINS_TAX`
  - `OTHER`
- **Usage:**
  - When creating a TAX_PAYMENT event for non-resident interest withholding, set `tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING`.
  - Use this field to filter and sum only the relevant tax payments for reconciliation and reporting.

### Example Usage
```python
# Creating a TaxStatement with new fields
statement = TaxStatement(
    fund_id=fund.id,
    entity_id=entity.id,
    financial_year="2023-2024",
    distribution_receivable_this_fy=1000.0,
    distribution_received_prev_fy=500.0,
    interest_received_in_cash=8000.0,
    non_resident_withholding_tax_from_statement=1200.0,
    # ... other manual fields ...
)
statement.calculate_interest_income_fields(session)

# Creating a FundEvent TAX_PAYMENT for non-resident interest withholding
tax_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.TAX_PAYMENT,
    event_date=date(2024, 6, 30),
    amount=1200.0,
    tax_payment_type=TaxPaymentType.NON_RESIDENT_INTEREST_WITHHOLDING,
    description="Non-resident interest withholding tax"
)
```

---

## Best Practices
- Always use the new manual fields for interest income breakdown in TaxStatement.
- Never set the calculated fields directly; always use the calculation method.
- Always set `tax_payment_type` for TAX_PAYMENT events for clarity and future-proofing.
- Use the calculated fields for all reporting, reconciliation, and IRR calculations.

## Equity Balance for Opportunity Cost (Risk-Free Interest Charge)

- The equity balance used for daily risk-free interest charge (opportunity cost) calculations is affected **only by capital events**:
    - CAPITAL_CALL
    - RETURN_OF_CAPITAL
    - UNIT_PURCHASE
    - UNIT_SALE
- Distributions, tax payments, management fees, and carried interest **do not** affect the equity balance for this purpose.
- **Rationale:** This matches industry standard practice, where opportunity cost is calculated on invested capital, not after distributions or other outflows. Distributions and other outflows are considered returns, not reductions in capital at risk. 

**Note:**
- `interest_taxable_rate` and `interest_deduction_rate` must always be set manually for each tax statement. The system will not auto-calculate these rates, except to use a default fallback (e.g., 32.5%) only if not provided. Always confirm the correct rate for each fund/entity/financial year based on the actual tax statement or jurisdictional rules. 

---

## Separation of Concerns: Models vs. Calculations

### Models (`models.py`)
- Only handle ORM logic, database queries, and orchestration.
- Should not contain business or calculation logic except for data access and aggregation.
- Model methods that fetch or aggregate data should use `get_` or `update_` prefixes.

### Calculations (`calculations.py`)
- All pure business logic and financial/statistical calculations live here.
- Functions should be stateless and accept plain data (numbers, lists, dicts, etc.).
- Easy to test and reuse.
- Use `calculate_`, `get_`, or `orchestrate_` prefixes for pure functions as appropriate.

### How to Add New Business Logic
- If it's a calculation or business rule that doesn't require ORM/session, add it to `calculations.py`.
- If it's a data fetch, aggregation, or ORM operation, keep it in the model.

### Testing
- All functions in `calculations.py` should have unit tests.
- Model methods should be tested via integration or system tests.

### Example Pattern
```python
# In models.py
def calculate_irr(self, session=None):
    """Calculate IRR for this fund."""
    # ORM logic to fetch events
    events = session.query(FundEvent)...
    # Delegate to calculations.py
    return calculate_irr(events, ...)
```
```python
# In calculations.py
def calculate_irr(events, ...):
    """Pure function: calculate IRR from event data."""
    ...
```

### Reporting/Formatting Logic
- If you have complex reporting or formatting, consider a `reporting.py` or `formatting.py` utility.

--- 