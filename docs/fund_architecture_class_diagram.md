# Fund Architecture Refactor - Class Relationship Diagram

## Overview

This document provides a detailed view of all proposed classes and their relationships for the fund architecture refactor. This diagram serves as a reference for developers implementing the new architecture.

## Class Hierarchy & Relationships

### 1. Core Event Handling Classes

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Abstract Base Classes                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────┐                                       │
│  │        BaseFundEventHandler         │                                       │
│  │                                     │                                       │
│  │  + session: Session                 │                                       │
│  │  + fund: Fund                       │                                       │
  │  │                                     │                                       │
│  │  + handle(event: FundEvent)         │                                       │
│  │  + validate_event(event: FundEvent) │                                       │
│  │  + publish_dependent_events()       │                                       │
│  │  + _get_fund(fund_id: int)         │                                       │
│  └─────────────────────────────────────┘                                       │
│                              ↑                                                 │
│                              │                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                              Concrete Handlers                              ││
│  │                                                                             ││
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ ││
│  │  │   CapitalCallHandler│  │ReturnOfCapitalHandler│  │  DistributionHandler│ ││
│  │  │                     │  │                     │  │                     │ ││
│  │  │  + _validate_capital│  │  + _validate_return │  │  + _validate_dist   │ ││
│  │  │  + _update_equity   │  │  + _update_equity   │  │  + _record_dist     │ ││
│  │  │  + _publish_equity  │  │  + _publish_equity  │  │  + _handle_tax      │ ││
│  │  │  + _trigger_status  │  │  + _publish_equity  │  │  + _publish_dist    │ ││
│  │  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ ││
│  │                                                                             ││
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ ││
│  │  │    NAVUpdateHandler │  │  UnitPurchaseHandler│  │     UnitSaleHandler │ ││
│  │  │                     │  │                     │  │                     │ ││
│  │  │  + _validate_nav    │  │  + _validate_purchase│  │  + _validate_sale   │ ││
│  │  │  + _update_nav      │  │  + _update_units    │  │  + _update_units    │ ││
│  │  │  + _update_subsequent│  │  + _update_equity  │  │  + _update_equity   │ ││
│  │  │  + _publish_nav     │  │  + _publish_units  │  │  + _publish_units   │ ││
│  │  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 2. Event Management & Orchestration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Event Management Layer                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    FundEventHandlerRegistry                                 │ │
│  │                                                                             │ │
│  │  + handlers: Dict[EventType, Type[BaseFundEventHandler]]                   │ │
│  │                                                                             │ │
│  │  + register_handler(event_type, handler_class)                             │ │
│  │  + get_handler(event_type, session)                                        │ │
│  │  + handle_event(event, session)                                            │ │
│  │  + _register_default_handlers()                                            │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                    FundUpdateOrchestrator                                  │ │
│  │                                                                             │ │
│  │  + registry: FundEventHandlerRegistry                                       │ │
│  │                                                                             │ │
│  │  + process_fund_event(event, session)                                      │ │
│  │  + _handle_dependent_updates(event, session)                               │ │
│  │  + _commit_changes(session)                                                 │ │
│  │  + _rollback_on_error(session, error)                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3. Domain Event System

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Domain Event System                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                           FundDomainEvent                                  │ │
│  │                                                                             │ │
│  │  + fund_id: int                                                            │ │
│  │  + event_date: date                                                        │ │
│  │  + timestamp: datetime                                                     │ │
│  │  + event_id: str                                                           │ │
│  │                                                                             │ │
│  │  + __repr__()                                                              │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                              ↑                                                 │
│                              │                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              Specific Events                                │ │
│  │                                                                             │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐ │ │
│  │  │EquityBalanceChanged │  │DistributionRecorded │  │     NAVUpdated     │ │ │
│  │  │       Event         │  │       Event         │  │       Event        │ │ │
│  │  │                     │  │                     │  │                     │ │ │
│  │  │  + old_balance      │  │  + distribution_type│  │  + old_nav          │ │ │
│  │  │  + new_balance      │  │  + amount           │  │  + new_nav          │ │ │
│  │  │  + change_reason    │  │  + tax_withheld     │  │  + change_reason    │ │ │
│  │  └─────────────────────┘  └─────────────────────┘  └─────────────────────┘ │ │
│  │                                                                             │ │
│  │  ┌─────────────────────┐  ┌─────────────────────┐                          │ │
│  │  │   UnitsChangedEvent │  │TaxStatementUpdated │                          │ │
│  │  │                     │  │       Event        │                          │ │
│  │  │  + old_units        │  │                     │                          │ │
│  │  │  + new_units        │  │  + tax_statement_id│                          │ │
│  │  │  + change_reason    │  │  + update_type      │                          │ │
│  │  └─────────────────────┘  └─────────────────────┘                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 4. Business Logic Services

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Business Logic Services                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        FundCalculationService                              │ │
│  │                                                                             │ │
│  │  + calculate_fifo_cost_basis(events, fund_type)                            │ │
│  │  + calculate_equity_balance(events, fund_type)                             │ │
│  │  + calculate_average_equity_balance(events, fund_type)                     │ │
│  │  + calculate_irr(cash_flows, start_date, end_date)                         │ │
│  │  + calculate_nav_change(previous_nav, current_nav)                         │ │
│  │  + calculate_tax_withholding(gross_amount, rate)                           │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                          FundStatusService                                 │ │
│  │                                                                             │ │
│  │  + determine_status(equity_balance, end_date, tax_statements)              │ │
│  │  + can_transition_to(from_status, to_status, fund_state)                  │ │
│  │  + trigger_status_update(fund, new_status, reason)                         │ │
│  │  + should_calculate_irr(status, fund_state)                                │ │
│  │  + validate_status_transition(from_status, to_status)                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                        TaxCalculationService                               │ │
│  │                                                                             │ │
│  │  + calculate_withholding_tax(gross_amount, rate)                           │ │
│  │  + calculate_net_amount(gross_amount, tax_withheld)                        │ │
│  │  + calculate_gross_amount(net_amount, rate)                                │ │
│  │  + validate_tax_calculation(gross, net, tax)                              │ │
│  │  + apply_tax_rates(amount, rates, jurisdiction)                            │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 5. Data Access Layer

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Data Access Layer                                 │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            FundRepository                                  │ │
│  │                                                                             │ │
│  │  + get_by_id(fund_id: int)                                                 │ │
│  │  + get_by_investment_company(company_id: int)                              │ │
│  │  + get_by_entity(entity_id: int)                                           │ │
│  │  + get_all()                                                               │ │
│  │  + create(fund_data: dict)                                                 │ │
│  │  + update(fund_id: int, fund_data: dict)                                  │ │
│  │  + delete(fund_id: int)                                                    │ │
│  │  + get_funds_by_status(status: FundStatus)                                │ │
│  │  + get_funds_by_type(fund_type: str)                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                         FundEventRepository                                │ │
│  │                                                                             │ │
│  │  + get_by_fund(fund_id: int, event_types: List[EventType])                │ │
│  │  + get_by_date_range(start_date: date, end_date: date)                     │ │
│  │  + get_by_type(event_type: EventType)                                      │ │
│  │  + create(event_data: dict)                                                │ │
│  │  + update(event_id: int, event_data: dict)                                │ │
│  │  + delete(event_id: int)                                                   │ │
│  │  + bulk_create(events: List[dict])                                         │ │
│  │  + get_events_for_recalculation(fund_id: int, from_event_id: int)          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                      TaxStatementRepository                                │ │
│  │                                                                             │ │
│  │  + get_by_fund_and_year(fund_id: int, financial_year: str)                │ │
│  │  + get_by_entity_and_year(entity_id: int, financial_year: str)             │ │
│  │  + create(statement_data: dict)                                            │ │
│  │  + update(statement_id: int, statement_data: dict)                         │ │
│  │  + delete(statement_id: int)                                               │ │
│  │  + get_final_statements(fund_id: int)                                      │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6. API & Service Layer

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API & Service Layer                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                            FundController                                  │ │
│  │                                                                             │ │
│  │  + GET /api/funds/{id}                                                     │ │
│  │  + POST /api/funds                                                         │ │
│  │  + PUT /api/funds/{id}                                                     │ │
│  │  + DELETE /api/funds/{id}                                                  │ │
│  │  + POST /api/funds/{id}/events                                             │ │
│  │  + GET /api/funds/{id}/events                                              │ │
│  │  + PUT /api/funds/{id}/events/{event_id}                                   │ │
│  │  + DELETE /api/funds/{id}/events/{event_id}                                │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
│                              ↓                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐ │
│  │                              FundService                                   │ │
│  │                                                                             │ │
│  │  + create_fund(fund_data: dict)                                            │ │
│  │  + update_fund(fund_id: int, fund_data: dict)                             │ │
│  │  + delete_fund(fund_id: int)                                               │ │
│  │  + add_fund_event(fund_id: int, event_data: dict)                         │ │
│  │  + update_fund_event(fund_id: int, event_id: int, event_data: dict)       │ │
│  │  + delete_fund_event(fund_id: int, event_id: int)                         │ │
│  │  + get_fund_summary(fund_id: int)                                          │ │
│  │  + get_fund_metrics(fund_id: int)                                          │ │
│  └─────────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 7. Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              Complete System Flow                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  API Request                                                                   │
│       ↓                                                                        │
│  FundController                                                                │
│       ↓                                                                        │
│  FundService                                                                   │
│       ↓                                                                        │
│  FundUpdateOrchestrator                                                        │
│       ↓                                                                        │
│  FundEventHandlerRegistry                                                      │
│       ↓                                                                        │
│  Specific Handler (e.g., CapitalCallHandler)                                   │
│       ↓                                                                        │
│  Business Logic Services (FundCalculationService, FundStatusService)           │
│       ↓                                                                        │
│  Domain Events Published                                                        │
│       ↓                                                                        │
│  Event Handlers for Dependent Updates                                          │
│       ↓                                                                        │
│  Data Access Layer (Repositories)                                              │
│       ↓                                                                        │
│  Database (Fund, FundEvent, TaxStatement, etc.)                               │
│       ↓                                                                        │
│  Response Returned                                                             │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Key Design Patterns

### 1. **Registry Pattern**
- `FundEventHandlerRegistry` manages handler registration and routing
- Allows dynamic handler registration and easy testing

### 2. **Strategy Pattern**
- Each event type has its own handler strategy
- Handlers can be swapped or extended without changing core logic

### 3. **Observer Pattern**
- Domain events notify dependent components of state changes
- Loose coupling between components

### 4. **Repository Pattern**
- Data access abstracted through repository interfaces
- Easier testing and potential for caching strategies

### 5. **Service Layer Pattern**
- Business logic separated into dedicated services
- Models become simple data containers

## Implementation Notes

### 1. **Handler Registration**
```python
# Handlers are registered by event type
registry.register_handler(EventType.CAPITAL_CALL, CapitalCallHandler)
registry.register_handler(EventType.DISTRIBUTION, DistributionHandler)
```

### 2. **Event Flow**
```python
# Events flow through the system
orchestrator.process_fund_event(event, session)
  → registry.handle_event(event, session)
    → handler.handle(event)
      → business_services.calculate()
      → domain_events.publish()
        → dependent_handlers.handle()
```

### 3. **Transaction Management**
```python
# Orchestrator manages transaction boundaries
try:
    registry.handle_event(event, session)
    _handle_dependent_updates(event, session)
    session.commit()
except Exception as e:
    session.rollback()
    raise e
```

### 4. **Error Handling**
```python
# Each layer has appropriate error handling
class FundEventHandlerError(Exception):
    """Base exception for fund event handling errors"""
    pass

class ValidationError(FundEventHandlerError):
    """Validation failed"""
    pass
```

## Testing Strategy

### 1. **Unit Tests**
- Test each handler in isolation
- Mock dependencies for clean testing
- Test all business logic paths

### 2. **Integration Tests**
- Test complete event flow
- Test database operations
- Test transaction rollback scenarios

### 3. **Performance Tests**
- Test with realistic data volumes
- Measure response times
- Validate O(1) complexity claims

### 4. **Contract Tests**
- Ensure API contracts remain unchanged
- Test backward compatibility
- Validate error responses

This class diagram provides a comprehensive view of the new architecture and serves as a reference for developers implementing the refactor. Each class has clear responsibilities and the relationships between them support the goal of creating a maintainable, scalable, and performant system.
