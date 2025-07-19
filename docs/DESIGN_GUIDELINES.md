
## AI Agent Collaboration Guidelines

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

---

## Table of Contents

1. AI Agent Collaboration Guidelines
2. Getting Started / Onboarding Checklist
3. Quick Reference Table
4. Overview
5. Web UI Architecture
6. Session Management
7. Object/Event Creation
8. Field Classification
9. Architectural Rules
10. API Design Patterns
11. React Component Patterns
12. Testing Strategy
13. Validation
14. Error Handling Policy
15. Glossary / Definitions
16. Examples
17. FAQ
18. Change History

---

## Quick Start

### **Core Patterns (Everyone Needs to Know)**

#### **React Component Patterns**
```typescript
// ✅ CORRECT: Functional components with hooks
const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchData()
      .then(setData)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  return <DashboardContent data={data} />;
};

// ✅ CORRECT: API integration with error handling
const fetchData = async () => {
  const response = await fetch('/api/dashboard/funds');
  if (!response.ok) {
    throw new Error('Failed to fetch data');
  }
  return response.json();
};
```

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

### **Web UI Architecture**

#### **Frontend-Backend Separation**
- **React Frontend**: Handles UI rendering, user interactions, and state management
- **Flask Backend**: Handles data access, business logic, and API endpoints
- **API-First Design**: All data flows through RESTful API endpoints
- **Stateless Frontend**: React components remain stateless, all data comes from API

#### **API Design Patterns**
```python
# ✅ CORRECT: RESTful API endpoints with consistent naming
GET /api/health                    # Health check
GET /api/dashboard/portfolio-summary  # Portfolio overview
GET /api/dashboard/funds           # List all funds
GET /api/dashboard/recent-events   # Recent events
GET /api/dashboard/performance     # Performance data
GET /api/funds/<fund_id>          # Fund details

# ✅ CORRECT: Consistent response format
{
  "funds": [...],           # Array of objects
  "events": [...],          # Array of objects  
  "performance": [...],      # Array of objects
  "error": "message"        # Error messages
}
```

#### **CORS and Environment Configuration**
```python
# ✅ CORRECT: CORS setup for development
from flask_cors import CORS
app = Flask(__name__)
CORS(app)  # Allow cross-origin requests from React

# ✅ CORRECT: Environment variables in React
REACT_APP_API_BASE_URL=http://localhost:5001
```

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

### Capital Event Handling (Unified Flow)

#### Overview
- All capital events (unit purchases/sales for NAV-based funds, capital calls/returns for cost-based funds) now use standardized unified methods and a unified recalculation orchestrator.
- This ensures consistency, maintainability, and efficient recalculation for edits/inserts anywhere in the event chain.
- The recalculation flow is efficient (single-pass) and robust for both NAV-based and cost-based funds.

#### Key Methods
- For NAV-based funds:
  - `add_unit_purchase`, `update_unit_purchase`
  - `add_unit_sale`, `update_unit_sale`
- For cost-based funds:
  - `add_capital_call`, `update_capital_call`
  - `add_return_of_capital`, `update_return_of_capital`
- All methods automatically call `recalculate_capital_chain_from(event, session=session)` after insert/update.

#### Unified Recalculation Orchestrator
- `recalculate_capital_chain_from(event, session=None)` efficiently recalculates all capital-related fields for the given event and all subsequent capital events.
- Delegates to fund-type-specific single-pass recalculators:
  - NAV-based: `_calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event`
  - Cost-based: `_calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event`
- After recalculation, fund-level summary fields are updated via `update_fund_summary_fields_after_capital_event`.

#### Architectural Rules
- **Always use the unified methods** for adding/updating capital events. Legacy methods are removed.
- **Never set calculated fields manually** (e.g., `current_equity_balance`, `units_owned`).
- **All recalculation logic is centralized** in the orchestrator and single-pass methods for maintainability.
- **Session management**: Unified methods require a session parameter, as with all domain methods.

#### Example Usage
```python
# NAV-based fund: add a unit purchase
fund.add_unit_purchase(units=100, price=10.0, date=date(2024, 1, 1), session=session)

# Cost-based fund: update a capital call
fund.update_capital_call(event_id=123, amount=50000.0, date=date(2024, 2, 1), session=session)
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
``` 
```

## Testing Guidelines

### **Backend Testing**
- Run the main test script (`tests/test_main.py`) after all major changes.
- Output test results to a new file using the convention `system_test_output_new##.txt` for traceability.
- Run API endpoint tests (`tests/test_api_endpoints.py`) to validate API functionality.
- Run tests frequently during development to catch regressions early.
- All new features and refactors must be accompanied by a successful test run before commit.

### **Frontend Testing**
- Write component tests for all React components (`*.test.tsx`).
- Test component rendering, user interactions, and API integration.
- Mock external dependencies (fetch API, React Router hooks).
- Test loading states, error handling, and data formatting.
- Use React Testing Library for component testing.

### **Integration Testing**
- Test end-to-end data flow from database to frontend.
- Validate API response formats and error handling.
- Test CORS configuration and environment setup.
- Ensure consistent data formatting between backend and frontend.

# Getting Started / Onboarding Checklist
- Read the "Overview" and "Architectural Rules" sections first.
- Review the "Quick Reference" table below for common methods and usage.
- Always use the `@with_session` decorator for DB methods.
- Run `tests/test_main.py` after any major change.
- Output test results to a new file (see Testing Guidelines).
- See the Glossary for definitions of key terms.

## Quick Reference Table
| Method                | Purpose                                 | Usage Example                  |
|-----------------------|-----------------------------------------|--------------------------------|
| add_unit_purchase     | Add a unit purchase event (NAV fund)    | fund.add_unit_purchase(...)    |
| update_unit_sale      | Update a unit sale event                | fund.update_unit_sale(...)     |
| add_capital_call      | Add a capital call (cost-based fund)    | fund.add_capital_call(...)     |
| add_return_of_capital | Add a return of capital                 | fund.add_return_of_capital(...)|

## Validation
- All input validation must occur at the domain method boundary (e.g., inside `add_unit_purchase`, not in the API layer).
- Raise clear, domain-specific exceptions for invalid input (e.g., `InvalidEventError`).
- Never silently ignore or coerce invalid data.

## Error Handling Policy

### **Backend Error Handling**
- Always raise explicit exceptions for error conditions; never return None or ambiguous values.
- Use domain-specific exception classes where possible.
- Log unexpected exceptions with enough context for debugging.
- Do not leak raw DB or system errors to the API layer—wrap in domain errors.

### **API Error Handling**
```python
# ✅ CORRECT: Consistent API error responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ✅ CORRECT: Domain-specific error handling
try:
    fund = session.query(Fund).filter_by(id=fund_id).first()
    if not fund:
        return jsonify({'error': 'Fund not found'}), 404
except Exception as e:
    return jsonify({'error': 'Database error'}), 500
```

### **Frontend Error Handling**
```typescript
// ✅ CORRECT: Graceful error handling in components
const [error, setError] = useState<string | null>(null);

const handleError = (error: Error) => {
  setError(error.message);
  console.error('API Error:', error);
};

// ✅ CORRECT: User-friendly error messages
if (error) {
  return (
    <Alert severity="error">
      {error.includes('not found') ? 'Fund not found' : 'An error occurred'}
    </Alert>
  );
}
```

## Glossary / Definitions
- **NAV-based fund:** A fund where value is tracked by Net Asset Value per unit.
- **Cost-based fund:** A fund where value is tracked by contributed/returned capital.
- **FIFO:** First-In, First-Out; used for cost base and capital gains calculations.
- **Capital event:** Any event that changes the equity/capital of a fund (purchase, sale, call, return).
- **@with_session:** Decorator to ensure DB session management is handled by the backend.
- **Domain method:** A method on a domain model (e.g., Fund) that encapsulates business logic.
- **API-First Design:** Architecture where all data flows through RESTful API endpoints.
- **Stateless Frontend:** React components that don't maintain application state, relying on API data.
- **CORS:** Cross-Origin Resource Sharing; allows frontend to make requests to backend API.
- **Component Testing:** Testing React components in isolation with mocked dependencies.

[See also: Session Management](#session-management)
[See also: Architectural Rules](#architectural-rules)

## Change History
- 2024-07-13: Major update—removed v2 method references, clarified legacy file removal, added explicit testing guidelines, onboarding checklist, error handling, validation, glossary, and quick reference table.

