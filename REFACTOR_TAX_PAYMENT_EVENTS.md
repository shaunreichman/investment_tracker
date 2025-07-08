# Tax Payment Events Refactoring Plan

## Current Issues

After analyzing the tax models, I've identified several areas where tax payment event creation logic is duplicated and could be standardized:

### 1. **Duplicate Event Creation Patterns**

**Current Methods:**
- `TaxStatement._create_tax_payment_event_object()` - Creates interest tax payment events
- `TaxStatement._create_dividend_tax_payment_event_objects()` - Creates dividend tax payment events  
- `TaxStatement._create_fy_debt_cost_event_object()` - Creates FY debt cost events
- `Fund._create_tax_payment_event_object()` - Duplicates interest tax payment logic
- `Fund.create_tax_payment_events()` - Orchestrates multiple event types
- `TaxStatement.create_tax_payment_events()` - Similar orchestration logic

**Problems:**
- Duplicate business logic for creating similar event types
- Inconsistent event creation patterns
- Mixed responsibilities between Fund and TaxStatement classes
- No standardized approach to event validation and deduplication

### 2. **Inconsistent Event Validation**

**Current Issues:**
- Different methods check for existing events in different ways
- Some methods use exact matching, others use partial matching
- Inconsistent handling of event updates vs. creation
- No standardized event deduplication strategy

### 3. **Mixed Responsibilities**

**Current Issues:**
- Fund class handles tax payment events but delegates to TaxStatement
- TaxStatement has both business logic and database operations mixed
- No clear separation between event object creation and database persistence

## Proposed Refactoring

### Phase 1: Create Standardized Event Creation Framework

#### 1.1 Create `TaxEventFactory` Class
```python
class TaxEventFactory:
    """Factory for creating standardized tax payment events."""
    
    @staticmethod
    def create_interest_tax_payment(tax_statement, session=None):
        """Create interest tax payment event object."""
        
    @staticmethod  
    def create_dividend_tax_payment(tax_statement, dividend_type, session=None):
        """Create dividend tax payment event object."""
        
    @staticmethod
    def create_fy_debt_cost_event(tax_statement, session=None):
        """Create FY debt cost event object."""
        
    @staticmethod
    def create_all_tax_events(tax_statement, session=None):
        """Create all applicable tax events for a tax statement."""
```

#### 1.2 Create `TaxEventManager` Class
```python
class TaxEventManager:
    """Manages tax event creation, validation, and database operations."""
    
    @staticmethod
    def create_or_update_tax_events(tax_statement, session=None):
        """Create or update all tax events for a tax statement."""
        
    @staticmethod
    def find_existing_event(event_criteria, session=None):
        """Find existing event based on standardized criteria."""
        
    @staticmethod
    def validate_event_creation(tax_statement, event_type, session=None):
        """Validate that event creation is appropriate."""
```

### Phase 2: Standardize Event Creation Methods

#### 2.1 Refactor TaxStatement Methods
- Replace `_create_tax_payment_event_object()` with `TaxEventFactory.create_interest_tax_payment()`
- Replace `_create_dividend_tax_payment_event_objects()` with `TaxEventFactory.create_dividend_tax_payment()`
- Replace `_create_fy_debt_cost_event_object()` with `TaxEventFactory.create_fy_debt_cost_event()`
- Update `create_tax_payment_events()` to use `TaxEventManager`

#### 2.2 Refactor Fund Methods
- Remove duplicate `_create_tax_payment_event_object()` method
- Update `create_tax_payment_events()` to use `TaxEventManager`
- Ensure Fund class delegates all tax event creation to TaxStatement

### Phase 3: Standardize Event Validation

#### 3.1 Create Standardized Event Criteria
```python
class TaxEventCriteria:
    """Standardized criteria for identifying tax events."""
    
    def __init__(self, fund_id, event_type, event_date, amount, tax_payment_type=None):
        self.fund_id = fund_id
        self.event_type = event_type
        self.event_date = event_date
        self.amount = amount
        self.tax_payment_type = tax_payment_type
```

#### 3.2 Implement Consistent Event Deduplication
- Use standardized criteria for finding existing events
- Implement consistent update vs. create logic
- Add proper error handling for duplicate events

### Phase 4: Improve Code Organization

#### 4.1 Create `src/tax/events.py` Module
- Move `TaxEventFactory` and `TaxEventManager` to dedicated module
- Create standardized event creation interfaces
- Add comprehensive documentation and type hints

#### 4.2 Update Imports and Dependencies
- Update all tax-related modules to use new event creation framework
- Ensure proper separation of concerns
- Add unit tests for new event creation framework

## Implementation Tasks

### Task 1: Create TaxEventFactory Class
- [x] Create `src/tax/events.py` module
- [x] Implement `TaxEventFactory` with static methods for each event type
- [x] Add comprehensive validation and error handling for `create_interest_tax_payment`
- [x] Implement `create_dividend_tax_payment` for both franked and unfranked dividends
- [x] Add unit tests for factory methods

### Task 2: Create TaxEventManager Class  
- [x] Implement `TaxEventManager` with event management methods
- [x] Create standardized event criteria and validation
- [x] Implement consistent event deduplication logic
- [x] Add unit tests for manager methods

### Task 3: Refactor TaxStatement Methods
- [x] Replace existing event creation methods with factory calls
- [x] Update `create_tax_payment_events()` to use manager
- [x] Ensure backward compatibility during transition
- [x] Update unit tests for refactored methods

### Task 4: Refactor Fund Methods
- [x] Remove duplicate event creation logic from Fund class
- [x] Update Fund's `create_tax_payment_events()` to delegate to TaxStatement/TaxEventManager
- [x] Ensure proper separation of concerns
- [x] Update unit tests for refactored methods

### Task 5: Add Comprehensive Testing
- [x] Create integration tests for new event creation framework
- [x] Test event deduplication and update scenarios
- [x] Test error handling and edge cases
- [x] Ensure all existing functionality is preserved

### Task 6: Documentation and Cleanup
- [ ] Update docstrings and comments
- [ ] Add usage examples and best practices
- [ ] Remove deprecated methods and code
- [ ] Update project documentation

## Benefits of Refactoring

### 1. **Reduced Code Duplication**
- Single source of truth for event creation logic
- Consistent patterns across all tax event types
- Easier maintenance and bug fixes

### 2. **Improved Maintainability**
- Clear separation of concerns
- Standardized interfaces and patterns
- Better testability with isolated components

### 3. **Enhanced Reliability**
- Consistent validation and error handling
- Standardized event deduplication
- Better handling of edge cases

### 4. **Future Extensibility**
- Easy to add new tax event types
- Consistent patterns for new features
- Better support for complex tax scenarios

## Migration Strategy

### Phase 1: Add New Framework (Non-breaking)
- Create new classes alongside existing methods
- Add comprehensive tests for new framework
- Ensure new framework works correctly

### Phase 2: Gradual Migration (Non-breaking)
- Update one method at a time to use new framework
- Maintain backward compatibility
- Test each migration step thoroughly

### Phase 3: Cleanup (Breaking)
- Remove deprecated methods
- Update all imports and references
- Final testing and validation

## Questions for Discussion

1. **Event Creation Location**: Should event creation be centralized in TaxStatement or distributed across domain objects?

2. **Validation Strategy**: What level of validation should be performed at the factory vs. manager level?

3. **Error Handling**: How should we handle cases where event creation fails or produces invalid events?

4. **Performance**: Are there any performance considerations for the new event creation framework?

5. **Testing Strategy**: What's the best approach for testing the new framework while maintaining existing functionality? 