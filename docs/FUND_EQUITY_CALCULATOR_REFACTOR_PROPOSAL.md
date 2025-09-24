# Fund Equity Calculator Refactor Proposal

## Overview

This document outlines the proposed refactoring of the fund equity calculation system to eliminate duplication, improve performance, and create a cleaner architecture with a single source of truth for all equity calculations.

## Current Problems

### 1. Duplication of Calculation Logic
- **Multiple "Efficient" Methods**: `calculate_nav_fields_on_subsequent_capital_fund_events_after_capital_event()` and `calculate_cost_based_fields_on_subsequent_capital_fund_events_after_capital_event()`
- **Scattered Logic**: Calculation logic spread across multiple services and handlers
- **Performance Issues**: Same events processed multiple times (O(4n) complexity)

### 2. Inconsistent Architecture
- **Mixed Responsibilities**: Calculators directly modifying database objects
- **Hard to Test**: Side effects make pure calculation testing difficult
- **Maintenance Burden**: Multiple places to update calculation logic

### 3. Performance Inefficiencies
- **Repeated Processing**: Events processed multiple times for different calculations
- **Database Queries**: Multiple queries for the same data
- **Memory Overhead**: Storing intermediate state unnecessarily

## Proposed Solution

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    FundEquityCalculator                     │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ calculate_event_equity_balances() - SINGLE COMPUTATION │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ calculate_current_equity_from_balances() - DERIVED     │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ calculate_average_equity_from_balances() - DERIVED     │ │
│  └─────────────────────────────────────────────────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ calculate_total_cost_basis_from_balances() - DERIVED   │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────┐
│                    FundEquityService                        │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │ update_fund_equity_fields() - HANDLES DATABASE UPDATES │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Key Principles

1. **Single Computation**: Process events only once
2. **Pure Functions**: Calculator methods have no side effects
3. **Derived Calculations**: All other values calculated from pre-computed balances
4. **Change Detection**: Only update events that actually changed
5. **Clean Separation**: Calculator calculates, service handles database

## Implementation Details

### 1. Core Calculator Methods

#### `calculate_event_equity_balances(fund, events) -> List[Tuple[float, bool]]`
- **Purpose**: Single computation that processes all events
- **Returns**: List of (balance, has_changed) tuples for each event
- **Performance**: O(n) - processes events once
- **Side Effects**: None (pure function)

#### `calculate_current_equity_from_balances(event_balances) -> float`
- **Purpose**: Calculate current equity from pre-computed balances
- **Returns**: Final balance (last event's balance)
- **Performance**: O(1) - simple array access
- **Side Effects**: None (pure function)

#### `calculate_average_equity_from_balances(events, event_balances) -> float`
- **Purpose**: Calculate time-weighted average from pre-computed balances
- **Returns**: Time-weighted average equity balance
- **Performance**: O(n) - time weighting calculation only
- **Side Effects**: None (pure function)

#### `calculate_total_cost_basis_from_balances(event_balances) -> float`
- **Purpose**: Calculate total cost basis from pre-computed balances
- **Returns**: Total cost basis (same as current equity for both fund types)
- **Performance**: O(1) - delegates to current equity calculation
- **Side Effects**: None (pure function)

### 2. Internal Processing Methods

#### `_process_cost_based_events(events) -> List[Tuple[float, bool]]`
- **Purpose**: Process cost-based fund events (capital calls and returns)
- **Returns**: List of (balance, has_changed) tuples for each event
- **Logic**: Running balance calculation with change detection
- **Performance**: O(n) - single pass through events
- **Side Effects**: None (pure function)

#### `_process_nav_based_events(events) -> List[Tuple[float, bool]]`
- **Purpose**: Process NAV-based fund events (unit purchases and sales)
- **Returns**: List of (balance, has_changed) tuples for each event
- **Logic**: FIFO cost base calculation with change detection
- **Performance**: O(n) - single pass through events
- **Side Effects**: None (pure function)

#### `_get_relevant_events(fund, session) -> List[FundEvent]`
- **Purpose**: Get relevant events for the fund type
- **Returns**: List of events ordered by date and ID
- **Logic**: 
  - Cost-based: CAPITAL_CALL and RETURN_OF_CAPITAL events
  - NAV-based: UNIT_PURCHASE and UNIT_SALE events
- **Performance**: O(n) - database query
- **Side Effects**: None (pure function)

### 3. Backwards Compatible Methods

#### `calculate_current_equity(fund, session) -> float`
- **Purpose**: Replace existing method with same signature
- **Implementation**: Gets events, calculates balances, returns current equity
- **Compatibility**: Same signature and behavior as existing method
- **Performance**: O(n) - single computation + O(1) derivation

#### `calculate_average_equity(fund, session) -> float`
- **Purpose**: Replace existing method with same signature
- **Implementation**: Gets events, calculates balances, returns average equity
- **Compatibility**: Same signature and behavior as existing method
- **Performance**: O(n) - single computation + O(n) time weighting

#### `calculate_total_cost_basis(fund, session) -> float`
- **Purpose**: Replace existing method with same signature
- **Implementation**: Gets events, calculates balances, returns total cost basis
- **Compatibility**: Same signature and behavior as existing method
- **Performance**: O(n) - single computation + O(1) derivation

#### `recalculate_all_equity_fields(fund, session) -> dict`
- **Purpose**: Replace existing method with same signature
- **Implementation**: Gets events, calculates balances, returns all fields
- **Compatibility**: Same signature and behavior as existing method
- **Performance**: O(n) - single computation + O(n) time weighting
- **Returns**: Dictionary with all equity fields

### 4. Service Layer Methods

#### `FundEquityService.__init__(session)`
- **Purpose**: Initialize service with database session
- **Parameters**: `session: Session` - Database session
- **Side Effects**: None

#### `FundEquityService.update_fund_equity_fields(fund) -> dict`
- **Purpose**: Update all equity fields for a fund with single computation
- **Parameters**: `fund: Fund` - Fund to update
- **Returns**: Dictionary with updated values and metadata
- **Performance**: O(n) - single computation + database updates
- **Side Effects**: Updates fund and event objects in database

#### `FundEquityService._get_relevant_events(fund) -> List[FundEvent]`
- **Purpose**: Get relevant events for the fund type
- **Parameters**: `fund: Fund` - Fund to get events for
- **Returns**: List of relevant events
- **Performance**: O(n) - database query
- **Side Effects**: None

### 5. Method Relationships and Data Flow

```
FundEquityService.update_fund_equity_fields()
    │
    ├── _get_relevant_events() ──→ List[FundEvent]
    │
    └── FundEquityCalculator.calculate_event_equity_balances()
        │
        ├── _process_cost_based_events() ──→ List[Tuple[float, bool]]
        │
        └── _process_nav_based_events() ──→ List[Tuple[float, bool]]
            │
            ├── calculate_current_equity_from_balances() ──→ float
            │
            ├── calculate_average_equity_from_balances() ──→ float
            │
            └── calculate_total_cost_basis_from_balances() ──→ float
```

### 6. Data Structures

#### `List[Tuple[float, bool]]` - Event Balances
- **Structure**: List of tuples containing (balance, has_changed)
- **Purpose**: Store calculated balance and change detection for each event
- **Example**: `[(1000.0, True), (1500.0, True), (1200.0, False)]`

#### `dict` - Equity Fields Result
- **Structure**: Dictionary containing all calculated equity fields
- **Keys**: 
  - `current_equity_balance`: float
  - `average_equity_balance`: float
  - `total_cost_basis`: float
  - `updated_events`: int (count of changed events)
- **Purpose**: Return all calculated values and metadata

## Performance Analysis

### Current Implementation
```python
# Multiple computations - INEFFICIENT
current_equity = calculate_current_equity(fund, events)      # O(n)
event_balances = calculate_event_balances(fund, events)      # O(n) - DUPLICATE
average_equity = calculate_average_equity(fund, events)      # O(n) - DUPLICATE
total_cost_basis = calculate_total_cost_basis(fund, events)  # O(n) - DUPLICATE
# Total: O(4n) - 4x processing of same events
```

### Proposed Implementation
```python
# Single computation + derived calculations - EFFICIENT
event_balances = calculate_event_equity_balances(fund, events)  # O(n) - ONCE
current_equity = calculate_current_equity_from_balances(event_balances)  # O(1)
average_equity = calculate_average_equity_from_balances(events, event_balances)  # O(n) - time weighting only
total_cost_basis = calculate_total_cost_basis_from_balances(event_balances)  # O(1)
# Total: O(2n) - 50% improvement!
```

## Migration Strategy

### Phase 1: Refactor Calculator
1. **Replace existing methods** with new implementation
2. **Keep same signatures** for backwards compatibility
3. **Add helper methods** for derived calculations
4. **Test thoroughly** to ensure same behavior

### Phase 2: Create Service Layer
1. **Create FundEquityService** that uses the new methods
2. **Add event update logic** for efficient database updates
3. **Update callers** to use the new service when appropriate

### Phase 3: Remove Old Methods
1. **Remove "efficient" methods** from FundCalculationService
2. **Update all callers** to use FundEquityCalculator
3. **Clean up** unused code

## Benefits

### 1. Performance Improvements
- **50% Reduction**: From O(4n) to O(2n) complexity
- **Single Computation**: Events processed only once
- **Efficient Updates**: Only update changed events

### 2. Code Quality
- **Single Source of Truth**: All calculation logic in one place
- **No Duplication**: Eliminates scattered calculation methods
- **Pure Functions**: Easy to test and maintain
- **Clean Architecture**: Clear separation of concerns

### 3. Maintainability
- **Easy Updates**: One place to change calculation logic
- **Better Testing**: Comprehensive test coverage
- **Consistent Behavior**: Same logic everywhere
- **Future-Proof**: Easy to extend for new fund types

## Implementation Example

### Calculator Implementation
```python
class FundEquityCalculator:
    @staticmethod
    def calculate_event_equity_balances(fund: Fund, events: List[FundEvent]) -> List[Tuple[float, bool]]:
        """Calculate equity balance for each event - SINGLE COMPUTATION"""
        if fund.tracking_type == FundTrackingType.COST_BASED:
            return FundEquityCalculator._process_cost_based_events(events)
        elif fund.tracking_type == FundTrackingType.NAV_BASED:
            return FundEquityCalculator._process_nav_based_events(events)
        else:
            raise ValueError(f"Unsupported fund type: {fund.tracking_type}")
    
    @staticmethod
    def calculate_current_equity(fund: Fund, session: Session) -> float:
        """Calculate current equity balance - REPLACES existing method"""
        events = FundEquityCalculator._get_relevant_events(fund, session)
        event_balances = FundEquityCalculator.calculate_event_equity_balances(fund, events)
        return FundEquityCalculator.calculate_current_equity_from_balances(event_balances)
    
    # ... other methods
```

### Service Implementation
```python
class FundEquityService:
    def __init__(self, session: Session):
        self.session = session
        self.calculator = FundEquityCalculator()
    
    def update_fund_equity_fields(self, fund: Fund) -> dict:
        """Update all equity fields for a fund - SINGLE COMPUTATION"""
        events = self._get_relevant_events(fund)
        
        # ONE computation that gives us event balances
        event_balances = self.calculator.calculate_event_equity_balances(fund, events)
        
        # Derive all other values from the pre-calculated balances
        current_equity = self.calculator.calculate_current_equity_from_balances(event_balances)
        average_equity = self.calculator.calculate_average_equity_from_balances(events, event_balances)
        total_cost_basis = self.calculator.calculate_total_cost_basis_from_balances(event_balances)
        
        # Update fund fields
        fund.current_equity_balance = current_equity
        fund.average_equity_balance = average_equity
        fund.total_cost_basis = total_cost_basis
        
        # Update only changed events
        for event, (balance, has_changed) in zip(events, event_balances):
            if has_changed:
                event.current_equity_balance = balance
        
        return {
            'current_equity_balance': current_equity,
            'average_equity_balance': average_equity,
            'total_cost_basis': total_cost_basis,
            'updated_events': sum(1 for _, has_changed in event_balances if has_changed)
        }
```

## Testing Strategy

### 1. Unit Tests
- **Pure Function Tests**: Test calculator methods independently
- **Edge Case Tests**: Test with empty events, invalid fund types, etc.
- **Performance Tests**: Verify O(n) complexity

### 2. Integration Tests
- **Service Layer Tests**: Test database updates and transactions
- **End-to-End Tests**: Test complete workflow
- **Backwards Compatibility Tests**: Ensure existing behavior preserved

### 3. Migration Tests
- **Before/After Comparison**: Verify same results as old methods
- **Performance Benchmarks**: Measure improvement
- **Regression Tests**: Ensure no functionality lost

## Conclusion

This refactoring proposal addresses the current problems of duplication, performance issues, and architectural inconsistencies while maintaining backwards compatibility. The new architecture provides:

- **50% performance improvement** through single computation
- **Cleaner code** with single source of truth
- **Better maintainability** with pure functions
- **Easier testing** with separated concerns
- **Future-proof design** for new fund types

The migration can be done incrementally with minimal risk to existing functionality.
