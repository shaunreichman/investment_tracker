# AI Agent Collaboration Guidelines

- **Testing:**
  - Run tests frequently, especially after any non-trivial change.
  - For `test_main.py`, always:
    - Save its output to `tests/output/test_main_output_new.txt`.
    - Compare this output to `tests/output/test_main_output1.txt`.
    - If outputs differ, inform the user immediately, as this likely indicates a problem.

- **Iteration:**
  - Prefer small, reviewable steps over large, sweeping changes.
  - Summarize each change clearly before and after making it.
  - When in doubt, ask for confirmation before making structural or potentially controversial changes.

- **Communication:**
  - Be explicit about what is being changed and why.
  - Default to autonomy for routine or obvious improvements, but pause for user input on ambiguous or high-impact decisions.
  - Use dedicated debug scripts for deep dives or complex logic issues.

- **Code & Architecture:**
  - Follow domain-driven design and project conventions.
  - All database operations must be handled by the core system, not by clients.
  - Use class methods and domain methods for object creation and manipulation (never direct constructors).

- **Documentation:**
  - Update documentation and code comments to reflect any significant changes or new patterns.

- **Proactive Debugging:**
  - When encountering unexpected behavior or logic issues, create a dedicated debug script to inspect the state and isolate the problem, rather than making speculative fixes.

- **Refactoring Philosophy:**
  - Only propose refactors that clearly improve code clarity, maintainability, or future extensibility—not for the sake of refactoring alone.

- **Session & State Management:**
  - Always treat the backend as the owner of session and state; clients should remain stateless and never perform direct database operations.

- **Commit Discipline:**
  - Only suggest committing changes after all tests have passed and the user has reviewed the changes, unless otherwise directed.

- **Documentation Consistency:**
  - When introducing new patterns or conventions, update both code comments and relevant documentation to keep everything in sync.

- **User Preferences First:**
  - When in doubt, defer to explicit user preferences or ask for clarification before proceeding with ambiguous tasks.

# Investment Tracker Design Guidelines v2

> **2024 Migration Note:** This project uses a domain-driven architecture. All models, calculations, and creation logic are organized by domain (fund, tax, entity, rates, investment company, shared). Old files (`src/models.py`, `src/calculations.py`, `src/utils.py`) are deprecated.

---

## Table of Contents

1. [Quick Start (5 min read)](#quick-start)
2. [Architecture Principles](#architecture-principles)
3. [Field Reference](#field-reference)
4. [Workflow Examples](#workflow-examples)
5. [Testing Guidelines](#testing-guidelines)

---

## Quick Start

### **Core Patterns (Everyone Needs to Know)**

#### 1. **Session Management**
```python
# ✅ CORRECT: Outermost layer manages sessions
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()

try:
    # Domain methods accept session parameter
    company = InvestmentCompany.create(name="Test Company", session=session)
    fund = company.create_fund(entity, "My Fund", session=session)
    fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
    session.commit()
finally:
    session.close()
```

#### 2. **Object Creation**
```python
# ✅ Use class methods for root objects
company = InvestmentCompany.create(name="Test Company", session=session)
entity = Entity.create(name="Test Entity", session=session)

# ✅ Use direct object methods for related objects
fund = company.create_fund(entity, "My Fund", session=session)
```

#### 3. **Event Creation**
```python
# ✅ Use domain methods for events
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
fund.add_distribution_with_tax_rate(gross_amount=5000, tax_rate=10.0, session=session)

# ✅ Use TaxEventManager for tax payments
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(tax_statement, session)
```

#### 4. **Field Classification**
- **Manual fields**: Set by user (name, amount, date, etc.)
- **Calculated fields**: Never set manually (equity balances, totals, etc.)
- **Properties**: Read-only, calculated on demand (start_date, end_date, etc.)

---

## Architecture Principles

### **Session Management**

#### **Rule: Backend Owns Sessions**
- **Domain methods** accept session parameters from the outermost layer
- **Domain methods** never create sessions internally
- **Test scripts/API endpoints** manage session lifecycle
- **External clients** are stateless

#### **Pattern: Session Parameter**
```python
# ✅ CORRECT: Always use keyword argument
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)

# ❌ INCORRECT: Positional argument
fund.add_capital_call(100000, date(2023, 1, 1), session)  # Error!
```

#### **Decorator Usage**
```python
@with_session
def update_current_equity_balance(self, session=None):
    # Session automatically provided if not passed
    # Use session for database operations
```

### **Object Creation Patterns**

#### **Root Objects (Class Methods)**
```python
# ✅ CORRECT: Use class methods
company = InvestmentCompany.create(name="Test Company", session=session)
entity = Entity.create(name="Test Entity", session=session)
fund = Fund.create(investment_company_id=company.id, entity_id=entity.id, name="My Fund", session=session)

# ❌ INCORRECT: Direct constructor
fund = Fund(investment_company_id=company.id, ...)  # No validation, no business logic
```

#### **Related Objects (Direct Methods)**
```python
# ✅ CORRECT: Use direct object methods
fund = company.create_fund(entity, "My Fund", session=session)
event = fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
```

### **Event Creation Patterns**

#### **User Events (Direct Creation)**
```python
# ✅ CORRECT: Direct FundEvent creation for user-entered events
event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.CAPITAL_CALL,
    event_date=date(2023, 1, 1),
    amount=100000.0,
    description="Initial capital call"
)
session.add(event)
```

#### **System Events (Manager/Factory)**
```python
# ✅ CORRECT: Use managers for system-generated events
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(tax_statement, session)

# ❌ INCORRECT: Direct creation of system events
event = FundEvent(event_type=EventType.TAX_PAYMENT, ...)  # System should create this
```

### **Separation of Concerns**

#### **Models (`models.py`)**
- ORM logic, database queries, orchestration
- Session management and persistence
- **No business calculations**

#### **Calculations (`calculations.py`)**
- Pure business logic and financial calculations
- Stateless functions (no database operations)
- Easy to test and reuse

#### **Example Pattern**
```python
# In models.py
def calculate_irr(self, session=None):
    events = session.query(FundEvent).filter(...).all()
    return calculate_irr(events, ...)  # Delegate to calculations.py

# In calculations.py
def calculate_irr(events, ...):
    # Pure calculation logic
    return irr_value
```

---

## Field Classification Principles

### **Rule: Every Field Must Be Explicitly Classified**
- **MANUAL**: Set by user/developer, required for object creation
- **CALCULATED**: Set by system only, never manually
- **HYBRID**: Can be set manually OR calculated (with clear precedence)

### **Implementation: Comments on Field Initialization**
```python
class Fund(Base):
    # MANUAL FIELDS
    name = Column(String(255), nullable=False)  # (MANUAL) fund name
    fund_type = Column(String(100))  # (MANUAL) type of fund (e.g., 'Private Equity', 'Venture Capital')
    tracking_type = Column(Enum(FundType), nullable=False)  # (MANUAL) NAV_BASED or COST_BASED
    
    # CALCULATED FIELDS
    current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital movements
    average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance
    is_active = Column(Boolean, default=True)  # (CALCULATED) whether fund has positive equity balance
    
    # HYBRID FIELDS
    description = Column(Text)  # (HYBRID) fund description, manual preferred, auto-generated fallback
```

---

## Field Reference

**Note:** All field definitions use the format `# (SYSTEM/MANUAL/CALCULATED/HYBRID) description` to make their classification explicit and self-documenting.
- (SYSTEM): set by the database/ORM/system (e.g., primary keys, timestamps)
- (MANUAL): set by the user/developer (e.g., foreign keys, business data)
- (CALCULATED): set by business logic
- (HYBRID): can be set manually or calculated

### **Fund Model Fields**

#### **Manual Fields (Set by User)**
```python
id = Column(Integer, primary_key=True)  # (SYSTEM) auto-generated primary key
investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)  # (MANUAL) foreign key to investment company, must be set at creation
entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)  # (MANUAL) foreign key to entity, must be set at creation
name = Column(String(255), nullable=False)  # (MANUAL) fund name
fund_type = Column(String(100))  # (MANUAL) type of fund (e.g., 'Private Equity', 'Venture Capital')
tracking_type = Column(Enum(FundType), nullable=False)  # (MANUAL) NAV_BASED or COST_BASED
description = Column(Text)  # (MANUAL) fund description
currency = Column(String(10), default="AUD")  # (MANUAL) currency code for the fund
commitment_amount = Column(Float, nullable=True)  # (MANUAL) total amount committed to the fund
expected_irr = Column(Float)  # (MANUAL) expected IRR as percentage
expected_duration_months = Column(Integer)  # (MANUAL) expected fund duration in months
```

#### **Calculated Fields (Never Set Manually)**
```python
current_equity_balance = Column(Float, default=0.0)  # (CALCULATED) current equity balance from capital calls - returns
average_equity_balance = Column(Float, default=0.0)  # (CALCULATED) time-weighted average equity balance
is_active = Column(Boolean, default=True)  # (CALCULATED) whether fund has positive equity balance
final_tax_statement_received = Column(Boolean, default=False)  # (CALCULATED) whether all expected tax statements received
_current_units = Column('current_units', Float)  # (CALCULATED) current number of units owned
_current_unit_price = Column('current_unit_price', Float)  # (CALCULATED) current unit price from latest NAV update
_total_cost_basis = Column('total_cost_basis', Float)  # (CALCULATED) total cost basis from capital calls - capital returns
created_at = Column(DateTime, default=datetime.utcnow)  # (SYSTEM) timestamp when record was created
updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)  # (SYSTEM) timestamp when record was last updated
```

### **TaxStatement Model Fields**

#### **Manual Fields (Set by User)**
```python
# Statement identification
fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
entity_id = Column(Integer, ForeignKey('entities.id'), nullable=False)
financial_year = Column(String(10), nullable=False)

# Interest income breakdown (manual)
interest_received_in_cash = Column(Float, default=0.0)  # (MANUAL) Actual cash flow received this FY
interest_receivable_this_fy = Column(Float, default=0.0)  # (MANUAL) Accounting income for this FY, not yet received
interest_receivable_prev_fy = Column(Float, default=0.0)  # (MANUAL) Accounting income from prev FY, received this FY
interest_non_resident_withholding_tax_from_statement = Column(Float, default=0.0)  # (MANUAL) Withholding tax as reported

# Tax rates (manual)
interest_income_tax_rate = Column(Float, default=0.0)  # (MANUAL) Manually defined interest tax rate (%)
fy_debt_interest_deduction_rate = Column(Float, default=0.0)  # (MANUAL) Manually defined interest deduction rate (%)

# Other manual fields
foreign_income = Column(Float, default=0.0)
capital_gains = Column(Float, default=0.0)
other_income = Column(Float, default=0.0)
foreign_tax_credits = Column(Float, default=0.0)
non_resident = Column(Boolean, default=False)
accountant = Column(String(255))
notes = Column(Text)
statement_date = Column(Date)
```

#### **Calculated Fields (Never Set Manually)**
```python
# Calculated interest income fields
interest_income_amount = Column(Float, default=0.0)  # (CALCULATED) = interest_received_in_cash + interest_receivable_this_fy - interest_receivable_prev_fy
interest_tax_amount = Column(Float, default=0.0)  # (CALCULATED) = interest_income_amount * interest_income_tax_rate / 100 - interest_non_resident_withholding_tax_from_statement
interest_non_resident_withholding_tax_already_withheld = Column(Float, default=0.0)  # (CALCULATED) = sum of TAX_PAYMENT events

# Debt cost tracking
fy_debt_interest_deduction_sum_of_daily_interest = Column(Float, default=0.0)  # (CALCULATED) Total interest expense for the FY
fy_debt_interest_deduction_total_deduction = Column(Float, default=0.0)  # (CALCULATED) Calculated tax benefit from interest deduction
```

### **FundEvent Model Fields**

#### **Manual Fields (Set by User)**
```python
# Event identification
fund_id = Column(Integer, ForeignKey('funds.id'), nullable=False)
event_type = Column(Enum(EventType), nullable=False)
event_date = Column(Date, nullable=False)
amount = Column(Float)  # (MANUAL) The cash flow amount

# Event-specific data (depending on event type)
distribution_type = Column(Enum(DistributionType))  # (MANUAL) For distributions
units_purchased = Column(Float)  # (MANUAL) For unit purchases
units_sold = Column(Float)  # (MANUAL) For unit sales
unit_price = Column(Float)  # (MANUAL) For unit transactions
nav_per_share = Column(Float)  # (MANUAL) For NAV updates
brokerage_fee = Column(Float, default=0.0)  # (MANUAL) For unit transactions

# Tax payment type (for TAX_PAYMENT events)
tax_payment_type = Column(Enum(TaxPaymentType))  # (MANUAL) Type of tax payment

# Metadata
description = Column(Text)
reference_number = Column(String(100))
```

#### **Calculated Fields (Never Set Manually)**
```python
# NAV tracking (calculated from NAV events)
units_owned = Column(Float)  # (CALCULATED) Calculated from cumulative unit events
cost_of_units = Column(Float)  # (CALCULATED) FIFO cost basis of remaining units after this event
```

---

## Workflow Examples

### **Creating a New Fund**

#### **Step 1: Create Root Objects**
```python
# Get database session
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()

try:
    # Create root objects using class methods
    company = InvestmentCompany.create(name="Test Company", session=session)
    entity = Entity.create(name="Test Entity", session=session)
    
    # Create fund using direct object method
    fund = company.create_fund(
        entity=entity,
        name="My Fund",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        currency="AUD",
        description="Fund description",
        session=session
    )
```

#### **Step 2: Add Initial Events**
```python
    # Add capital call to establish equity
    fund.add_capital_call(
        amount=100000.0,
        date=date(2023, 1, 1),
        description="Initial capital call",
        session=session
    )
    
    # Add distribution with tax
    fund.add_distribution_with_tax_rate(
        event_date=date(2023, 6, 30),
        gross_amount=5000.0,
        tax_rate=10.0,
        distribution_type=DistributionType.INTEREST,
        description="Interest distribution",
        session=session
    )
    
    session.commit()
finally:
    session.close()
```

### **Creating Tax Statements**

#### **Step 1: Create Tax Statement**
```python
# Create tax statement with manual fields
statement = TaxStatement.create(
    fund_id=fund.id,
    entity_id=entity.id,
    financial_year="2023-24",
    interest_received_in_cash=8000.0,
    interest_receivable_this_fy=1000.0,
    interest_receivable_prev_fy=500.0,
    interest_non_resident_withholding_tax_from_statement=1200.0,
    interest_income_tax_rate=10.0,
    fy_debt_interest_deduction_rate=32.5,
    accountant="Findex",
    statement_date=date(2024, 8, 24),
    session=session
)
```

#### **Step 2: Calculate Derived Fields**
```python
# Calculate interest income amount
statement.calculate_interest_income_amount()

# Calculate tax amounts
statement.calculate_interest_tax_amount()
statement.calculate_fy_debt_interest_deduction_total_deduction()
```

#### **Step 3: Create Tax Payment Events**
```python
# Create tax payment events using manager
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(statement, session)
```

### **NAV-Based Fund Setup**

#### **Step 1: Create NAV-Based Fund**
```python
fund = company.create_fund(
    entity=entity,
    name="ABC Ltd",
    fund_type="Equity - Consumer Discretionary",
    tracking_type=FundType.NAV_BASED,
    currency="AUD",
    description="ABC Ltd on the ASX",
    session=session
)
```

#### **Step 2: Add Unit Purchase**
```python
# Add unit purchase event
purchase_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.UNIT_PURCHASE,
    event_date=date(2023, 3, 28),
    units_purchased=85.0,
    unit_price=58.00,
    brokerage_fee=19.95,
    description="Initial unit purchase"
)
session.add(purchase_event)
```

#### **Step 3: Add NAV Update**
```python
# Add NAV update event
nav_event = FundEvent(
    fund_id=fund.id,
    event_type=EventType.NAV_UPDATE,
    event_date=date(2023, 3, 31),
    nav_per_share=57.20,
    description="March 2023 NAV update"
)
session.add(nav_event)
```

#### **Step 4: Update Calculated Fields**
```python
# Update calculated fields
fund.update_current_units_and_price(session=session)
fund.update_current_equity_balance(session=session)
fund.update_average_equity_balance(session=session)
```

---

## Testing Guidelines

### **Session Management in Tests**

#### **✅ CORRECT: Use Domain Methods with Shared Session**
```python
def setup_test_data(session):
    """Set up test data using domain methods."""
    # Create entities using class methods
    company = InvestmentCompany.create(name="Test Company", session=session)
    entity = Entity.create(name="Test Entity", session=session)
    
    # Create funds using class methods
    fund = Fund.create(
        investment_company_id=company.id,
        entity_id=entity.id,
        name="Test Fund",
        fund_type="Private Debt",
        tracking_type=FundType.COST_BASED,
        session=session
    )
    
    # Add events using domain methods
    fund.add_capital_call(
        amount=100000.0,
        date=date(2023, 1, 1),
        description="Initial capital call",
        session=session
    )
    
    # Create tax statements using class methods
    TaxStatement.create(
        fund_id=fund.id,
        entity_id=entity.id,
        financial_year="2023-24",
        interest_received_in_cash=5000.0,
        interest_income_tax_rate=10.0,
        session=session
    )

def main():
    """Main test function."""
    # Get database session
    engine, session_factory, scoped_session = get_database_session()
    session = scoped_session()
    
    try:
        # Set up test data with shared session
        setup_test_data(session)
        
        # Run tests with shared session
        recalculate_everything(session)
        verify_results(session)
        
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
```

### **Field Setting Rules**

#### **✅ DO: Set Manual Fields**
```python
# ✅ CORRECT: Set manual fields
fund = Fund.create(
    name="My Fund",
    fund_type="Private Debt",
    tracking_type=FundType.COST_BASED,
    commitment_amount=100000.0,
    session=session
)

statement = TaxStatement.create(
    fund_id=fund.id,
    entity_id=entity.id,
    financial_year="2023-24",
    interest_received_in_cash=5000.0,
    interest_income_tax_rate=10.0,
    session=session
)
```

#### **❌ DON'T: Set Calculated Fields**
```python
# ❌ INCORRECT: Setting calculated fields
fund.current_equity_balance = 100000.0  # Should be calculated from events
fund.is_active = True  # Should be calculated from equity balance
statement.interest_income_amount = 5000.0  # Should be calculated from manual fields
statement.interest_tax_amount = 500.0  # Should be calculated from rate
```

#### **✅ DO: Call Calculation Methods**
```python
# ✅ CORRECT: Call calculation methods
statement.calculate_interest_income_amount()
statement.calculate_interest_tax_amount()
fund.update_current_equity_balance(session=session)
fund.update_average_equity_balance(session=session)
```

### **Test Structure**

#### **All tests must reside in the `tests/` directory**
- Unit tests for pure functions in `calculations.py`
- Integration tests for model methods
- System tests for end-to-end workflows

#### **Test Data Setup**
- Use domain methods for object creation
- Set only manual fields
- Call calculation methods to verify they work
- Use shared session for all operations

#### **Verification**
- Verify calculated fields are correct
- Verify system-generated events are created
- Verify business logic is applied correctly

---

## Common Mistakes to Avoid

### **1. Session Management**
```python
# ❌ INCORRECT: Creating sessions in domain methods
def add_capital_call(self, amount, date, description):
    session = Session()  # Don't do this!
    # ... rest of method

# ✅ CORRECT: Accept session from caller
def add_capital_call(self, amount, date, description, session=None):
    # Use provided session
```

### **2. Direct Constructor Usage**
```python
# ❌ INCORRECT: Direct constructor
fund = Fund(investment_company_id=company.id, ...)
session.add(fund)

# ✅ CORRECT: Use class method
fund = Fund.create(investment_company_id=company.id, ..., session=session)
```

### **3. Setting Calculated Fields**
```python
# ❌ INCORRECT: Setting calculated fields
fund.current_equity_balance = 100000.0
statement.interest_income_amount = 5000.0

# ✅ CORRECT: Let system calculate
fund.update_current_equity_balance(session=session)
statement.calculate_interest_income_amount()
```

### **4. Direct System Event Creation**
```python
# ❌ INCORRECT: Creating system events directly
event = FundEvent(event_type=EventType.TAX_PAYMENT, ...)

# ✅ CORRECT: Use managers for system events
TaxEventManager.create_or_update_tax_events(tax_statement, session)
```

### **5. Positional Session Arguments**
```python
# ❌ INCORRECT: Positional session argument
fund.add_capital_call(100000, date(2023, 1, 1), session)

# ✅ CORRECT: Keyword session argument
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
```

---

## Migration Notes

### **Deprecated Files**
- `src/models.py` - Moved to domain modules
- `src/calculations.py` - Moved to domain modules  
- `src/utils.py` - Moved to `src/shared/utils.py`

### **Deprecated Fields**
- `vintage_year` - Removed, can be derived from `start_date`
- `gross_interest_income` - Removed, use interest income breakdown fields
- `tax_withheld` - Removed, use event-based tax payments

### **Deprecated Methods**
- `_create_tax_payment_event_object()` - Use `TaxEventManager`
- `create_tax_payment_events()` - Use `TaxEventManager.create_or_update_tax_events()`

### **Updated Field Names**
- `interest_taxable_rate` → `interest_income_tax_rate`
- `interest_deduction_rate` → `fy_debt_interest_deduction_rate`

---

## Quick Reference

### **Import Patterns**
```python
from src.fund.models import Fund, FundEvent, FundType
from src.tax.models import TaxStatement
from src.entity.models import Entity
from src.rates.models import RiskFreeRate
from src.investment_company.models import InvestmentCompany
from src.shared.utils import with_session
from src.tax.events import TaxEventManager
```

### **Common Workflows**
```python
# Create fund with events
company = InvestmentCompany.create(name="Company", session=session)
entity = Entity.create(name="Entity", session=session)
fund = company.create_fund(entity, "Fund", session=session)
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)

# Create tax statement with payments
statement = TaxStatement.create(fund_id=fund.id, entity_id=entity.id, financial_year="2023-24", session=session)
statement.calculate_interest_income_amount()
TaxEventManager.create_or_update_tax_events(statement, session)
```

### **Session Management**
```python
# Always use keyword arguments
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)

# Outermost layer manages sessions
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()
try:
    # ... operations ...
    session.commit()
finally:
    session.close()
``` 