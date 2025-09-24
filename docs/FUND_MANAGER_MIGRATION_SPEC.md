# FundManager Migration Specification

## Overview
Migrate from the FundManager anti-pattern to rich domain models where the Fund class owns its business logic, eliminating unnecessary abstraction layers and improving architectural clarity.

## Current Problem
- **FundManager creates unnecessary indirection** - adds complexity without value
- **Fund model is anemic** - just data containers with no behavior
- **Tests are broken** - calling methods that don't exist on Fund objects
- **Architecture violates DDD principles** - business logic separated from domain entities

## Target Architecture
```
Fund Model → Business Logic Methods → Direct Operations
FundEventService → Orchestration & Cross-Cutting Concerns
FundCalculationService → Complex Calculations
FundStatusService → Status Management & Transitions
```

## Method Migration Plan

### ✅ MOVE TO FUND MODEL (Core Business Logic)

#### **Capital Movement Operations**
```python
def create_capital_call(self, amount: float, call_date: date, description: str, 
                    reference_number: str = None, session: Session = None) -> FundEvent

def create_return_of_capital(self, amount: float, return_date: date, description: str,
                         reference_number: str = None, session: Session = None) -> FundEvent

def create_distribution(self, event_date: date, distribution_type: DistributionType,
                    distribution_amount: float = None, has_withholding_tax: bool = False,
                    gross_interest_amount: float = None, net_interest_amount: float = None,
                    withholding_tax_amount: float = None, withholding_tax_rate: float = None,
                    description: str = None, reference_number: str = None,
                    session: Session = None) -> Union[FundEvent, tuple[FundEvent, Optional[FundEvent]]]

def create_nav_update(self, nav_per_share: float, update_date: date, description: str = None,
                  reference_number: str = None, session: Session = None) -> FundEvent

def create_unit_purchase(self, units: float, unit_price: float, purchase_date: date,
                     description: str = None, reference_number: str = None,
                     session: Session = None) -> FundEvent

def create_unit_sale(self, units: float, unit_price: float, sale_date: date,
                  description: str = None, reference_number: str = None,
                  session: Session = None) -> FundEvent
```

#### **Core Business Properties**
```python
def total_capital_called(self, session: Session = None) -> float
def total_capital_returned(self, session: Session = None) -> float
def total_distributions(self, session: Session = None) -> float
def total_tax_withheld(self, session: Session = None) -> float
def total_unit_purchases(self, session: Session = None) -> float
def total_unit_sales(self, session: Session = None) -> float
def start_date(self, session: Session = None) -> Optional[date]
def end_date(self, session: Session = None) -> Optional[date]
```

#### **Event Query Methods**
```python
def get_all_fund_events(self, exclude_system_events: bool = True, session: Session = None) -> List[FundEvent]
def get_recent_events(self, limit: int = 10, exclude_system_events: bool = True, session: Session = None) -> List[FundEvent]
def get_events(self, event_types: List[EventType] = None, start_date: date = None, end_date: date = None, session: Session = None) -> List[FundEvent]
def get_capital_calls(self, start_date: date = None, end_date: date = None, session: Session = None) -> List[FundEvent]
def get_capital_returns(self, start_date: date = None, end_date: date = None, session: Session = None) -> List[FundEvent]
def get_distributions(self, start_date: date = None, end_date: date = None, session: Session = None) -> List[FundEvent]
```

### ❌ KEEP AS SERVICES (Cross-Cutting Concerns)

#### **Complex Calculations**
```python
def calculate_gross_irr(self, session: Session = None) -> float
def calculate_net_irr(self, session: Session = None) -> float  
def calculate_real_irr(self, session: Session = None) -> float
def calculate_average_equity_balance(self, session: Session = None) -> float
def update_average_equity_balance(self, session: Session = None) -> None
```

#### **Status Management**
```python
def update_status(self, session: Session = None) -> None
def update_status_after_equity_event(self, session: Session = None) -> None
def update_status_after_tax_statement(self, session: Session = None) -> None
def calculate_end_date(self, session: Session = None) -> Optional[date]
```

#### **Analytics & Reporting**
```python
def get_enhanced_fund_metrics(self, session: Session = None) -> Dict[str, Any]
def get_distribution_summary(self, session: Session = None) -> Dict[str, Any]
def get_summary_data(self, session: Session = None) -> Dict[str, Any]
```

## Implementation Phases

### **Phase 1: Add Core Methods to Fund Model**
- [ ] Add capital movement methods to Fund class
- [ ] Add business property methods to Fund class
- [ ] Add event query methods to Fund class
- [ ] Maintain existing orchestrator integration

### **Phase 2: Update Existing Tests**
- [ ] Fix broken integration tests to use Fund methods directly
- [ ] Update test imports and method calls
- [ ] Ensure all tests pass with new architecture

### **Phase 3: Remove FundManager**
- [ ] Update all imports across codebase
- [ ] Remove FundManager class entirely
- [ ] Clean up any remaining references

### **Phase 4: Validation & Cleanup**
- [ ] Run complete test suite
- [ ] Validate API endpoints work correctly
- [ ] Update documentation and examples

## Code Examples

### **Before (FundManager Pattern)**
```python
# ❌ BAD: Unnecessary indirection
fund_manager = FundManager(fund)
event = fund_manager.create_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=db_session)
total_called = fund_manager.total_capital_called()
```

### **After (Rich Domain Model)**
```python
# ✅ GOOD: Direct domain operations
event = fund.create_capital_call(50000.0, date(2023, 1, 1), "Initial call", session=db_session)
total_called = fund.total_capital_called()
```

## Benefits

### **Architectural Improvements**
- **Cleaner domain models** - business logic co-located with data
- **Better encapsulation** - Fund owns its behavior
- **Eliminates anti-pattern** - no more "manager" classes

### **Developer Experience**
- **Simpler testing** - test Fund methods directly
- **Better IntelliSense** - all methods on Fund object
- **Consistent patterns** - all domain models follow same approach

### **Maintainability**
- **Fewer classes** - less code to maintain
- **Clearer responsibilities** - each class has single, clear purpose
- **Easier debugging** - business logic in expected location

## Success Criteria
- [ ] All existing tests pass with new architecture
- [ ] FundManager class completely removed
- [ ] Fund model contains all core business logic methods
- [ ] Services handle only cross-cutting concerns
- [ ] API endpoints work identically to before
- [ ] No performance regression in fund operations

## Risk Mitigation
- **Maintain existing orchestrator integration** - no changes to event system
- **Gradual migration** - phase-by-phase implementation
- **Comprehensive testing** - validate each phase before proceeding
- **Rollback plan** - can revert to FundManager if issues arise

## Timeline
- **Phase 1**: 1-2 days (add methods to Fund model)
- **Phase 2**: 1-2 days (fix existing tests)
- **Phase 3**: 1 day (remove FundManager)
- **Phase 4**: 1 day (validation & cleanup)
- **Total**: 4-6 days for complete migration

## Conclusion
This migration transforms the codebase from an anti-pattern to a clean, enterprise-grade architecture that follows domain-driven design principles. The result is a more maintainable, testable, and professional system.
