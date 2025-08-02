
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
- **Frontend Development:**
  - Always use TypeScript for React components.
  - Follow Material-UI patterns for consistent UI/UX.
  - Implement proper loading states and error handling in all components.
  - Use React hooks (useState, useEffect, useCallback) for state management.
- **API Integration:**
  - All frontend data fetching should go through the Flask API endpoints.
  - Use consistent error handling patterns across all API calls.
  - Implement proper loading states for all async operations.

---

## Specification Documentation Standards

### **Rule: Always Create Detailed Specs Before Major Work**
- **Never start significant development without a clear specification**
- **Specs must include**: Goals, phases, tasks, design principles, success metrics
- **Reference the Fund Detail Modernization Spec as the gold standard**

### **Specification Structure**
```markdown
# [Feature Name] Specification

## Overview
Brief description of what we're building and why

## Design Philosophy
- Core principles and design goals
- Problems we're solving
- Success criteria

## Implementation Strategy
### Phase 1: [Foundation]
**Goal**: [Clear objective]
**Tasks**:
- [ ] Specific, actionable task
- [ ] Another specific task
**Design Principles**:
- [Key design decisions and rationale]

### Phase 2: [Next Phase]
[Continue with clear phases]

## Success Metrics
- Measurable outcomes
- User experience improvements
- Technical achievements
```

### **Rule: Keep Specs Code-Free**
- **No implementation code in specification documents**
- **Focus on**: Goals, tasks, principles, design decisions
- **Include code only when**: Critical for understanding architecture or patterns
- **Reference existing code examples** from Design Guidelines when needed

### **Phase-Based Development Pattern**
1. **Foundation Phase**: Core structure, basic functionality
2. **Feature Phase**: Main functionality implementation
3. **Polish Phase**: Visual improvements, interactions
4. **Integration Phase**: Connect with other systems
5. **Optimization Phase**: Performance, accessibility

**Each phase should have**:
- Clear, measurable goals
- Specific, actionable tasks
- Design principles and constraints
- Success criteria for completion

### **Specification Review Checklist**
- [ ] Clear problem statement and goals
- [ ] Phases are logical and build upon each other
- [ ] Tasks are specific and actionable
- [ ] Design principles are stated and justified
- [ ] Success metrics are measurable
- [ ] No unnecessary code examples
- [ ] References existing patterns where appropriate

### **Example: Fund Detail Modernization Spec**
The `docs/FUND_DETAIL_MODERNIZATION_SPEC.md` demonstrates the gold standard for specifications:
- **Clear phases** with specific goals and tasks
- **Design principles** that guide implementation
- **Success metrics** that are measurable
- **Code-free** focus on what to build, not how to build it
- **Logical progression** from foundation to polish

---

## Table of Contents

1. [AI Agent Collaboration Guidelines](#ai-agent-collaboration-guidelines)
2. [Specification Documentation Standards](#specification-documentation-standards)
3. [Quick Start](#quick-start)
4. [Architecture Principles](#architecture-principles)
5. [Session Management](#session-management)
6. [Object Creation Patterns](#object-creation-patterns)
7. [Event Creation Patterns](#event-creation-patterns)
8. [Capital Event Handling](#capital-event-handling)
9. [Separation of Concerns](#separation-of-concerns)
10. [TypeScript Standards](#typescript-standards)
11. [Frontend Development Guidelines](#frontend-development-guidelines)
12. [Component Architecture Patterns](#component-architecture-patterns)
13. [Centralized API Integration](#centralized-api-integration)
14. [API Integration Patterns](#api-integration-patterns)
15. [Error Handling Standards](#error-handling-standards)
16. [Performance Standards](#performance-standards)
17. [Security Standards](#security-standards)
18. [Environment Setup](#environment-setup)
19. [Field Classification Principles](#field-classification-principles)
20. [Field Reference](#field-reference)
21. [Workflow Examples](#workflow-examples)
22. [Testing Guidelines](#testing-guidelines)
23. [Validation](#validation)
24. [Getting Started / Onboarding Checklist](#getting-started--onboarding-checklist)
25. [Quick Reference Table](#quick-reference-table)
26. [Glossary / Definitions](#glossary--definitions)
27. [Change History](#change-history)

---

## Quick Start

### **🚀 Quick Server Commands**
```bash
# Backend: http://localhost:5001
source venv/bin/activate && FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001

# Frontend: http://localhost:3000
cd frontend && npm start

# Health checks
curl http://localhost:5001/api/health  # Backend
curl http://localhost:3000              # Frontend
```

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

// ✅ CORRECT: Material-UI component patterns
const MyComponent = () => {
  const [formData, setFormData] = useState({
    name: '',
    amount: ''
  });

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <TextField
        fullWidth
        label="Fund Name"
        value={formData.name}
        onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
        required
      />
    </Box>
  );
};
```

#### **Backend Session Management**
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

#### **Object Creation Patterns**
```python
# ✅ Use class methods for root objects
company = InvestmentCompany.create(name="Test Company", session=session)
entity = Entity.create(name="Test Entity", session=session)

# ✅ Use direct object methods for related objects
fund = company.create_fund(entity, "My Fund", session=session)
```

#### **Event Creation Patterns**
```python
# ✅ Use domain methods for events
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
fund.add_distribution_with_tax_rate(gross_amount=5000, tax_rate=10.0, session=session)

# ✅ Use TaxEventManager for tax payments
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(tax_statement, session)
```

#### **Field Classification**
- **Manual fields**: Set by user (name, amount, date, etc.)
- **Calculated fields**: Never set manually (equity balances, totals, etc.)
- **Properties**: Read-only, calculated on demand (start_date, end_date, etc.)

---

## Architecture Principles

### **Core Architectural Rules**

#### **1. API Layer Must Use Domain Methods**
- **Never access database directly** from API endpoints
- **Always delegate** to domain methods for all business logic
- **API layer** is purely for HTTP request/response handling
- **Session management** belongs in domain methods, not API layer

#### **2. Backend Owns Sessions**
- **Domain methods** accept session parameters from the outermost layer
- **Domain methods** never create sessions internally
- **Test scripts/API endpoints** manage session lifecycle
- **External clients** are stateless

#### **3. All Database Operations Through Core System**
- **No direct database access** from clients or API layer
- **All data access** goes through domain methods
- **Business logic** belongs in domain layer, not API layer
- **Validation** happens at domain method boundaries

### **Web UI Architecture**

#### **Frontend-Backend Separation**
- **React Frontend**: Handles UI rendering, user interactions, and state management
- **Flask Backend**: Handles data access, business logic, and API endpoints
- **API-First Design**: All data flows through RESTful API endpoints
- **Stateless Frontend**: React components remain stateless, all data comes from API

#### **RESTful API Endpoints**
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

---

## Session Management

### **Rule: Backend Owns Sessions**
- **Domain methods** accept session parameters from the outermost layer
- **Domain methods** never create sessions internally
- **Test scripts/API endpoints** manage session lifecycle
- **External clients** are stateless

### **Pattern: Session Parameter**
```python
# ✅ CORRECT: Always use keyword argument
fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)

# ❌ INCORRECT: Positional argument
fund.add_capital_call(100000, date(2023, 1, 1), session)  # Error!
```

### **Decorator Usage**
```python
@with_session
def update_current_equity_balance(self, session=None):
    # Session automatically provided if not passed
    # Use session for database operations
```

---

## Object Creation Patterns

### **Root Objects (Class Methods)**
```python
# ✅ CORRECT: Use class methods
company = InvestmentCompany.create(name="Test Company", session=session)
entity = Entity.create(name="Test Entity", session=session)
fund = Fund.create(investment_company_id=company.id, entity_id=entity.id, name="My Fund", session=session)

# ❌ INCORRECT: Direct constructor
fund = Fund(investment_company_id=company.id, ...)  # No validation, no business logic
```

### **Related Objects (Direct Methods)**
```python
# ✅ CORRECT: Use direct object methods
fund = company.create_fund(entity, "My Fund", session=session)
event = fund.add_capital_call(amount=100000, date=date(2023, 1, 1), session=session)
```

---

## Event Creation Patterns

### **User Events (Direct Creation)**
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

### **System Events (Manager/Factory)**
```python
# ✅ CORRECT: Use managers for system-generated events
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(tax_statement, session)

# ❌ INCORRECT: Direct creation of system events
event = FundEvent(event_type=EventType.TAX_PAYMENT, ...)  # System should create this
```

---

## Capital Event Handling (Unified Flow)

### **Overview**
- All capital events (unit purchases/sales for NAV-based funds, capital calls/returns for cost-based funds) now use standardized unified methods and a unified recalculation orchestrator.
- This ensures consistency, maintainability, and efficient recalculation for edits/inserts anywhere in the event chain.
- The recalculation flow is efficient (single-pass) and robust for both NAV-based and cost-based funds.

### **Key Methods**
- For NAV-based funds:
  - `add_unit_purchase`, `update_unit_purchase`
  - `add_unit_sale`, `update_unit_sale`
- For cost-based funds:
  - `add_capital_call`, `update_capital_call`
  - `add_return_of_capital`, `update_return_of_capital`
- All methods automatically call `recalculate_capital_chain_from(event, session=session)` after insert/update.

### **Unified Recalculation Orchestrator**
- `recalculate_capital_chain_from(event, session=None)` efficiently recalculates all capital-related fields for the given event and all subsequent capital events.
- Delegates to fund-type-specific single-pass recalculators:
  - NAV-based: `_calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event`
  - Cost-based: `_calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event`
- After recalculation, fund-level summary fields are updated via `update_fund_summary_fields_after_capital_event`.

### **Architectural Rules**
- **Always use the unified methods** for adding/updating capital events. Legacy methods are removed.
- **Never set calculated fields manually** (e.g., `current_equity_balance`, `units_owned`).
- **All recalculation logic is centralized** in the orchestrator and single-pass methods for maintainability.
- **Session management**: Unified methods require a session parameter, as with all domain methods.

### **Example Usage**
```python
# NAV-based fund: add a unit purchase
fund.add_unit_purchase(units=100, price=10.0, date=date(2024, 1, 1), session=session)

# Cost-based fund: update a capital call
fund.update_capital_call(event_id=123, amount=50000.0, date=date(2024, 2, 1), session=session)
```

---

## Separation of Concerns

### **Models (`models.py`)**
- ORM logic, database queries, orchestration
- Session management and persistence
- **No business calculations**

### **Calculations (`calculations.py`)**
- Pure business logic and financial calculations
- Stateless functions (no database operations)
- Easy to test and reuse

### **Example Pattern**
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

## TypeScript Standards

### **Interface Design Principles**
- Create interfaces that extend base API types for component-specific fields
- Use proper type coercion for form data (string → enum)
- Handle optional fields with `null` vs `undefined` correctly
- Implement generic interfaces for reusable components

### **Type Safety Patterns**
```typescript
// ✅ CORRECT: Extended interfaces for component data
interface ExtendedFundEvent extends Omit<FundEvent, 'amount'> {
  amount: number | null;
  displayAmount?: string;
  formattedDate?: string;
  isEditable?: boolean;
}

// ✅ CORRECT: Type coercion for form data
const handleSubmit = async (formData: any) => {
  const apiData = {
    ...formData,
    tracking_type: formData.tracking_type === 'nav_based' 
      ? FundType.NAV_BASED 
      : FundType.COST_BASED,
    amount: formData.amount ? parseFloat(formData.amount) : null,
    event_date: formData.event_date ? new Date(formData.event_date) : undefined
  };
  await createFund.mutate(apiData);
};

// ✅ CORRECT: Generic hooks with proper typing
const useApiCall = <T>(url: string) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<ErrorInfo | null>(null);
  // ... implementation
};
```

### **Component Type Patterns**
```typescript
// ✅ CORRECT: Proper prop interfaces
interface FundDetailProps {
  fundId: number;
  onEventCreated?: (event: FundEvent) => void;
  onEventUpdated?: (event: FundEvent) => void;
  onEventDeleted?: (eventId: number) => void;
}

// ✅ CORRECT: Event handler types
const handleEventCreated = useCallback((event: FundEvent) => {
  onEventCreated?.(event);
  refetch();
}, [onEventCreated, refetch]);

// ✅ CORRECT: Form data interfaces
interface CreateFundFormData {
  name: string;
  tracking_type: 'nav_based' | 'cost_based';
  fund_type?: string;
  description?: string;
  currency?: string;
}
```

### **Type Guards and Validation**
```typescript
// ✅ CORRECT: Type guards for runtime validation
const isFundEvent = (obj: any): obj is FundEvent => {
  return obj && typeof obj.id === 'number' && typeof obj.event_type === 'string';
};

// ✅ CORRECT: Validation with TypeScript
const validateFundData = (data: any): data is CreateFundData => {
  return data && 
         typeof data.name === 'string' && 
         data.name.length > 0 &&
         ['nav_based', 'cost_based'].includes(data.tracking_type);
};
```

## Frontend Development Guidelines

### **React Component Patterns**

#### **Functional Components with Hooks**
```typescript
// ✅ CORRECT: Use functional components with hooks
const FundList = () => {
  const [funds, setFunds] = useState<Fund[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFunds()
      .then(setFunds)
      .catch(setError)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <CircularProgress />;
  if (error) return <Alert severity="error">{error}</Alert>;
  
  return (
    <Box>
      {funds.map(fund => (
        <FundCard key={fund.id} fund={fund} />
      ))}
    </Box>
  );
};
```

#### **Material-UI Integration**
```typescript
// ✅ CORRECT: Use Material-UI components consistently
import {
  Box,
  Card,
  CardContent,
  Typography,
  Button,
  TextField,
  Alert,
  CircularProgress
} from '@mui/material';

const FundForm = () => {
  const [formData, setFormData] = useState({
    name: '',
    amount: ''
  });

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Create Fund</Typography>
        <Box component="form" sx={{ mt: 2 }}>
          <TextField
            fullWidth
            label="Fund Name"
            value={formData.name}
            onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
            required
            sx={{ mb: 2 }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};
```

#### **Error Handling Patterns**
```typescript
// ✅ CORRECT: Consistent error handling
const useApiCall = <T>(url: string) => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        setError(null);
        
        const response = await fetch(url);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [url]);

  return { data, loading, error };
};
```

### **State Management**

#### **Local State with useState**
```typescript
// ✅ CORRECT: Use useState for component-local state
const [formData, setFormData] = useState({
  name: '',
  amount: '',
  description: ''
});

const handleInputChange = (field: string, value: string) => {
  setFormData(prev => ({ ...prev, [field]: value }));
};
```

#### **Complex State with useReducer**
```typescript
// ✅ CORRECT: Use useReducer for complex state
interface FormState {
  data: Record<string, string>;
  errors: Record<string, string>;
  isSubmitting: boolean;
}

const formReducer = (state: FormState, action: any) => {
  switch (action.type) {
    case 'SET_FIELD':
      return { ...state, data: { ...state.data, [action.field]: action.value } };
    case 'SET_ERROR':
      return { ...state, errors: { ...state.errors, [action.field]: action.error } };
    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.isSubmitting };
    default:
      return state;
  }
};
```

### **API Integration Patterns**

#### **Consistent API Calls**
```typescript
// ✅ CORRECT: Centralized API configuration
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001';

const apiCall = async (endpoint: string, options?: RequestInit) => {
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers
    },
    ...options
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }

  return response.json();
};

// Usage
const createFund = async (fundData: any) => {
  return apiCall('/api/funds', {
    method: 'POST',
    body: JSON.stringify(fundData)
  });
};
```

#### **Loading States**
```typescript
// ✅ CORRECT: Always show loading states
const FundList = () => {
  const { data: funds, loading, error } = useApiCall<Fund[]>('/api/funds');

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  return <FundGrid funds={funds || []} />;
};
```

---

## Component Architecture Patterns

### **Section-Based Architecture**

#### **Pattern: Break Large Components into Focused Sections**
```typescript
// ✅ CORRECT: Section-based component architecture
interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

const EquitySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => {
  // Focused on equity metrics only
  const equityMetrics = [
    { label: 'Current Balance', value: fund.current_equity_balance ?? null, icon: '💰' },
    { label: 'Average Balance', value: fund.average_equity_balance ?? null, icon: '📊' }
  ].filter(metric => metric.value !== null);

  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <AccountBalance color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Equity</Typography>
      </Box>
      {/* Section-specific content */}
    </Paper>
  );
};
```

#### **Benefits of Section-Based Architecture**
- **Focused Responsibility**: Each section handles one aspect of the data
- **Reusability**: Sections can be reused in different contexts
- **Maintainability**: Easier to modify individual sections
- **Testing**: Each section can be tested independently
- **Performance**: Only re-render sections that change

### **Chart Integration Patterns**

#### **Pattern: Conditional Chart Rendering**
```typescript
// ✅ CORRECT: Conditional chart rendering based on data availability
const UnitPriceChartSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate, events }) => {
  // Only show for NAV-based funds
  if (fund.tracking_type !== 'nav_based') {
    return null;
  }

  return (
    <Paper sx={{ p: 0.75, mb: 1, borderRadius: 2 }}>
      <Box display="flex" alignItems="center" mb={0.5}>
        <TrendingUp color="primary" sx={{ mr: 0.5, fontSize: 16 }} />
        <Typography variant="h6" sx={{ fontSize: 16 }}>Unit Price Performance</Typography>
      </Box>
      
      <Box sx={{ height: 200, position: 'relative' }}>
        {/* Chart rendering with error handling */}
      </Box>
    </Paper>
  );
};
```

#### **Chart Integration Best Practices**
- **Conditional Rendering**: Only show charts when data is available and relevant
- **Responsive Sizing**: Adapt chart size to container constraints
- **Error Handling**: Graceful fallback when chart data fails
- **Consistent Styling**: Match chart container styling with other components
- **Performance**: Optimize chart rendering for sidebar constraints

### **Responsive Layout Patterns**

#### **Pattern: Sidebar-Main Layout**
```typescript
// ✅ CORRECT: Professional dashboard layout
const FundDetail: React.FC = () => {
  const [sidebarVisible, setSidebarVisible] = useState(true);

  return (
    <Box sx={{ display: 'flex', gap: 3, height: '100%' }}>
      {/* Left Sidebar - Summary Sections */}
      <Box sx={{ 
        width: sidebarVisible ? { xs: '100%', sm: '322px', md: '368px', lg: '414px' } : 0,
        flexShrink: 0,
        position: { xs: 'static', sm: 'relative' },
        height: { xs: 'auto', sm: '100%' },
        overflowY: { xs: 'visible', sm: 'auto' }
      }}>
        <EquitySection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
        <ExpectedPerformanceSection fund={fund} formatCurrency={formatCurrency} formatDate={formatDate} />
        {/* Additional sections */}
      </Box>

      {/* Main Area - Detailed Data */}
      <Box sx={{ flex: 1, minWidth: 0 }}>
        {/* Main content area */}
      </Box>
    </Box>
  );
};
```

#### **Responsive Design Principles**
- **Mobile-First**: Stack vertically on small screens, side-by-side on larger screens
- **Flexible Widths**: Use flex properties for responsive behavior
- **Overflow Handling**: Ensure content doesn't break layout
- **Smooth Transitions**: Animate layout changes for better UX

### **Visual Consistency Patterns**

#### **Pattern: Consistent Section Styling**
```typescript
// ✅ CORRECT: Consistent styling across all sections
const sectionStyles = {
  p: 0.75,
  mb: 1,
  borderRadius: 2,
  boxShadow: '0 2px 8px rgba(0,0,0,0.08), 0 1px 3px rgba(0,0,0,0.12)',
  transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)',
  '&:hover': {
    boxShadow: '0 4px 16px rgba(0,0,0,0.12), 0 2px 6px rgba(0,0,0,0.16)',
    transform: 'translateY(-1px)'
  }
};

const headerStyles = {
  display: 'flex',
  alignItems: 'center',
  mb: 0.5
};
```

#### **Visual Hierarchy Principles**
- **Consistent Spacing**: Use Material-UI spacing system throughout
- **Icon Integration**: Use icons for visual recognition and hierarchy
- **Typography Scale**: Maintain consistent font sizes and weights
- **Color Usage**: Use colors to support hierarchy, not compete for attention

### **Data Flow Patterns**

#### **Pattern: Props Interface for Sections**
```typescript
// ✅ CORRECT: Consistent props interface for all sections
interface SectionProps {
  fund: ExtendedFund;
  formatCurrency: (amount: number | null, currency?: string) => string;
  formatDate: (dateString: string | null) => string;
  events?: ExtendedFundEvent[];
}

// All sections use the same interface
const EquitySection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => { /* ... */ };
const PerformanceSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate }) => { /* ... */ };
const ChartSection: React.FC<SectionProps> = ({ fund, formatCurrency, formatDate, events }) => { /* ... */ };
```

#### **Data Flow Benefits**
- **Consistent Interface**: All sections expect the same props
- **Reusable Functions**: Formatting functions shared across sections
- **Type Safety**: TypeScript ensures correct prop usage
- **Maintainability**: Changes to data structure affect all sections consistently

---

## API Integration Patterns

### **Backend API Structure**

#### **Consistent Endpoint Patterns**
```python
# ✅ CORRECT: RESTful API structure
@app.route('/api/funds', methods=['GET'])
def get_funds():
    """Get all funds with summary data"""
    try:
        session = get_db_session()
        try:
            funds = Fund.get_all(session=session)
            return jsonify({
                "funds": [fund.to_dict() for fund in funds],
                "total": len(funds)
            }), 200
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/funds', methods=['POST'])
def create_fund():
    """Create a new fund"""
    try:
        data = request.get_json()
        session = get_db_session()
        try:
            fund = Fund.create(**data, session=session)
            session.commit()
            return jsonify(fund.to_dict()), 201
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 400
```

#### **Error Handling**
```python
# ✅ CORRECT: Consistent error responses
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

# ✅ CORRECT: Domain-specific error handling
try:
    fund = session.query(Fund).filter_by(id=fund_id).first()
    if not fund:
        return jsonify({"error": "Fund not found"}), 404
except Exception as e:
    return jsonify({"error": "Database error"}), 500
```

### **Centralized API Integration**

#### **Core Principles**
- Use centralized `apiClient` from `services/api.ts` for all API calls
- Implement custom hooks for all data fetching and mutations
- Maintain type safety with TypeScript interfaces
- Handle loading states and error handling consistently
- Never use direct `fetch()` calls in components

#### **Custom Hooks for API Calls**
```typescript
// ✅ CORRECT: Domain-specific hooks
const { data: funds, loading, error } = useFunds();
const { data: entities } = useEntities();
const { mutate: createFund, isCreating } = useCreateFund();

// ✅ CORRECT: Error handling with centralized system
const { error, setError, clearError } = useErrorHandler();

// ✅ CORRECT: Mutation hooks with optimistic updates
const { mutate: createEvent, isCreating } = useCreateFundEvent(fundId);
const { mutate: updateEvent, isUpdating } = useUpdateFundEvent(fundId, eventId);
const { mutate: deleteEvent, isDeleting } = useDeleteFundEvent(fundId, eventId);
```

#### **Migration Patterns**
```typescript
// ❌ INCORRECT: Direct fetch calls
const [funds, setFunds] = useState([]);
useEffect(() => {
  fetch('/api/funds').then(res => res.json()).then(setFunds);
}, []);

// ✅ CORRECT: Centralized hooks
const { data: funds, loading, error } = useFunds();
```

#### **Type Safety Patterns**
```typescript
// ✅ CORRECT: Extended interfaces for component-specific data
interface ExtendedFundEvent extends Omit<FundEvent, 'amount'> {
  amount: number | null;
  displayAmount?: string;
  formattedDate?: string;
}

// ✅ CORRECT: Type coercion for form data
const handleSubmit = async (formData: any) => {
  const apiData = {
    ...formData,
    tracking_type: formData.tracking_type === 'nav_based' 
      ? FundType.NAV_BASED 
      : FundType.COST_BASED,
    amount: formData.amount ? parseFloat(formData.amount) : null
  };
  await createFund.mutate(apiData);
};
```

---

## Environment Setup

### **Development Environment**

#### **Backend Setup**
```bash
# ✅ CORRECT: Virtual environment setup
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

#### **Frontend Setup**
```bash
# ✅ CORRECT: Frontend dependencies
cd frontend
npm install
npm start  # Starts development server on port 3000
```

#### **Database Setup**
```bash
# ✅ CORRECT: Database initialization
python scripts/init_database.py
```

### **Environment Variables**

#### **Backend (.env)**
```bash
FLASK_APP=src/api.py
FLASK_ENV=development
DATABASE_URL=sqlite:///data/investment_tracker.db
```

#### **Frontend (.env)**
```bash
REACT_APP_API_BASE_URL=http://localhost:5001
REACT_APP_ENVIRONMENT=development
```

### **Running the Application**

#### **Development Mode**
```bash
# Backend: http://localhost:5001
source venv/bin/activate
FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001

# Frontend: http://localhost:3000
cd frontend
npm start
```

#### **Troubleshooting**
```bash
# Port conflicts
lsof -i :5001  # Check backend port
lsof -i :3000  # Check frontend port
pkill -f "flask run"      # Kill backend
pkill -f "react-scripts"  # Kill frontend

# Health checks
curl http://localhost:5001/api/health  # Backend
curl http://localhost:3000              # Frontend
```

#### **Production Mode**
```bash
# Build frontend
cd frontend
npm run build

# Run backend with production server
source venv/bin/activate
gunicorn -w 4 -b 0.0.0.0:5001 "src.api:app"
```

#### **Common Issues**
```bash
# Database issues
python scripts/init_database.py

# Dependency issues  
pip install -r requirements.txt  # Backend
cd frontend && npm install      # Frontend
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
# Create tax payment events using TaxEventManager
from src.tax.events import TaxEventManager
TaxEventManager.create_or_update_tax_events(statement, session)
```

---

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

#### **Component Testing Example**
```typescript
// ✅ CORRECT: Component test with React Testing Library
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CreateFundModal } from './CreateFundModal';

describe('CreateFundModal', () => {
  it('should render template selection on open', () => {
    render(
      <CreateFundModal
        open={true}
        onClose={jest.fn()}
        onFundCreated={jest.fn()}
        companyId={1}
        companyName="Test Company"
      />
    );

    expect(screen.getByText('Select a Tracking Type Template')).toBeInTheDocument();
    expect(screen.getByText('Cost-Based Fund')).toBeInTheDocument();
    expect(screen.getByText('NAV-Based Fund')).toBeInTheDocument();
  });

  it('should apply template when selected', async () => {
    render(
      <CreateFundModal
        open={true}
        onClose={jest.fn()}
        onFundCreated={jest.fn()}
        companyId={1}
        companyName="Test Company"
      />
    );

    const costBasedCard = screen.getByText('Cost-Based Fund').closest('div');
    fireEvent.click(costBasedCard!);

    await waitFor(() => {
      expect(screen.getByDisplayValue('cost_based')).toBeInTheDocument();
    });
  });
});
```

### **Integration Testing**
- Test end-to-end data flow from database to frontend.
- Validate API response formats and error handling.
- Test CORS configuration and environment setup.
- Ensure consistent data formatting between backend and frontend.

### **API Testing**
```python
# ✅ CORRECT: API endpoint testing
def test_create_fund():
    with app.test_client() as client:
        response = client.post('/api/funds', json={
            'name': 'Test Fund',
            'fund_type': 'Private Equity',
            'tracking_type': 'cost_based'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['name'] == 'Test Fund'
```

---

## Validation
- All input validation must occur at the domain method boundary (e.g., inside `