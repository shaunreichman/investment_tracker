# Entity Refactor Specification

## 🚀 **PROJECT STATUS: Architecture Alignment Phase** 🎯

**Current Phase**: Phase 1 - Foundation & Service Layer (0% COMPLETED) 🚀 **READY TO BEGIN**  
**Overall Progress**: 0% Complete - Foundation phase ready to begin  
**Risk Level**: LOW (Current System) → **VERY LOW** (Complete enterprise architecture)

## Overview

This specification outlines the refactoring of the entity module from a clean, focused model to a fully enterprise-grade architecture that mirrors the successful fund refactor. The goal is to achieve architectural consistency across the entire system while maintaining the entity module's current simplicity and adding enterprise patterns for scalability and maintainability.

## Design Philosophy

- **Architectural Consistency**: Mirror the exact patterns established in the fund refactor
- **Light Refactor Approach**: Maintain current simplicity while adding enterprise patterns
- **Separation of Concerns**: Move business logic from models into dedicated services
- **Event-Driven Integration**: Connect to existing domain event system
- **Single Responsibility**: Each class has one clear purpose and reason to change
- **Enterprise Standards**: Achieve professional-grade maintainability and testability
- **Performance at Scale**: Support 1000+ entities, 5000+ funds, 100+ tax jurisdictions with O(1) operations

## Current State Analysis

### Strengths Identified
- **Clean Model Structure**: Only 149 lines with focused responsibility
- **Proper Domain Methods**: Uses `@classmethod` for creation with validation
- **Basic API Layer**: Has GET and POST endpoints for entities
- **Minimal Business Logic**: Most logic is simple and contained
- **Good Separation**: Calculations are properly separated into `calculations.py`
- **Maintainable Code**: Current implementation is clean and focused

### Areas for Improvement
- **No Service Layer**: Business logic embedded in model methods
- **Direct Database Queries**: Some queries still in model methods
- **Missing Repository Pattern**: No data access abstraction
- **Limited Event System**: No domain events for entity changes
- **Basic API Implementation**: Minimal endpoints, no comprehensive CRUD
- **Missing Validation Layer**: Basic validation embedded in API layer

### Current Architecture
```
Entity → Fund → TaxStatement → InvestmentCompany
  ↓        ↓         ↓              ↓
Simple   Multiple   Complex      Multiple
Model    Update     Tax          Update
Logic    Paths      Logic        Paths
```

## Target Architecture

### Event-Driven Handler Pattern
```
EntityEvent → EventHandlerRegistry → SpecificHandler → DomainEvents → OtherHandlers
    ↓              ↓                      ↓              ↓              ↓
Event         Routes to              Handles         Publishes      Handle
Creation      Appropriate            Specific        Domain         Dependent
              Handler               Logic           Events         Updates
```

## Class Structure & Relationships

### Core Architecture Classes

#### 1. Event Handling Layer
```
BaseEntityEventHandler (Abstract)
├── EntityCreatedHandler
├── EntityUpdatedHandler
├── EntityDeletedHandler
├── TaxJurisdictionChangedHandler
└── EntityFundsUpdatedHandler
```

#### 2. Event Management Layer
```
EntityEventHandlerRegistry
├── Registers handlers for each event type
├── Routes events to appropriate handlers
└── Manages handler lifecycle

EntityUpdateOrchestrator
├── Coordinates complete update pipeline
├── Manages transaction boundaries
└── Handles dependent updates
```

#### 3. Domain Event System
```
EntityDomainEvent (Base)
├── EntityCreatedEvent
├── EntityUpdatedEvent
├── EntityDeletedEvent
├── TaxJurisdictionChangedEvent
└── EntityFundsUpdatedEvent
```

#### 4. Business Logic Services
```
EntityService
├── Handles entity operations and validation
├── Separated from models for testability
└── Supports tax jurisdiction calculations

EntityCalculationService
├── Handles financial year calculations
├── Manages jurisdiction-specific logic
└── Provides entity-specific calculations

EntityValidationService
├── Manages business rule validation
├── Handles constraint checking
└── Ensures data integrity
```

#### 5. Data Access Layer
```
EntityRepository
├── Handles all database operations for entities
├── Implements caching strategies
└── Provides optimized queries for common operations

EntitySummaryRepository
├── Manages summary data and calculations
├── Implements materialized views for performance
└── Provides aggregated data access
```

### Class Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API Layer                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  EntityController  →  EntityService  →  EntityUpdateOrchestrator              │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Business Logic Layer                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  EntityService  ←→  EntityCalculationService  ←→  EntityValidationService     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Event Handling Layer                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  EntityEventHandlerRegistry                                                   │
│  ├── EntityCreatedHandler                                                     │
│  ├── EntityUpdatedHandler                                                     │
│  ├── EntityDeletedHandler                                                     │
│  ├── TaxJurisdictionChangedHandler                                           │
│  └── EntityFundsUpdatedHandler                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Domain Event System                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  EntityDomainEvent  →  EventBus  →  EventHandlers  →  Dependent Updates      │
│  ├── EntityCreatedEvent                                                       │
│  ├── EntityUpdatedEvent                                                       │
│  ├── EntityDeletedEvent                                                       │
│  ├── TaxJurisdictionChangedEvent                                             │
│  └── EntityFundsUpdatedEvent                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  EntityRepository  ←→  EntitySummaryRepository                                │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Database Layer                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  Entity  ←→  Fund  ←→  TaxStatement  ←→  InvestmentCompany                   │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: Foundation & Service Layer (1 week) 🏗️ **FOUNDATION PHASE**
**Goal**: Extract business logic from models into dedicated services while maintaining all existing functionality

**Design Principles**:
- **Mirror fund refactor patterns exactly** - Use identical service layer structure
- **Light refactor approach** - Maintain current simplicity while adding enterprise patterns
- **Zero breaking changes** - All existing functionality must continue to work unchanged
- **Incremental extraction** - Extract one service at a time to maintain stability
- **Comprehensive testing** - Each extracted service must have 100% test coverage

**Tasks**:
- [ ] **Create EntityService**: Extract entity operations, validation, and business rules
- [ ] **Create EntityCalculationService**: Extract financial year calculations and jurisdiction logic
- [ ] **Create EntityValidationService**: Extract business rule validation and constraint checking
- [ ] **Update Entity Model**: Integrate with new services while maintaining existing interface
- [ ] **Comprehensive Testing**: Test all extracted services in isolation with 100% coverage
- [ ] **Performance Validation**: Ensure no performance regression from extraction

**Success Criteria**:
- [ ] Entity model maintained under 100 lines (business logic extracted)
- [ ] 100% test coverage for all extracted services
- [ ] Zero performance regression on all operations
- [ ] All existing tests continue to pass
- [ ] All existing functionality preserved through new service layer

### Phase 2: Repository Layer & Data Access (1 week) 🗄️ **DATA ACCESS PHASE**
**Goal**: Implement repository pattern for clean data access abstraction

**Design Principles**:
- **Mirror fund repository patterns exactly** - Use identical repository structure and methods
- **Clean separation of concerns** - Models become simple data containers
- **Optimized queries** - Implement efficient data access patterns
- **Caching strategy** - Add caching for frequently accessed data

**Tasks**:
- [ ] **Create EntityRepository**: Handle all entity CRUD operations and queries
- [ ] **Create EntitySummaryRepository**: Handle summary data and aggregated calculations
- [ ] **Implement Caching Strategy**: Add Redis-based caching for entity data
- [ ] **Optimize Database Queries**: Add proper indexes and query optimization
- [ ] **Integration Testing**: Test repository layer with real database operations

**Success Criteria**:
- [ ] All database operations abstracted through repository layer
- [ ] Zero direct database queries in models or services
- [ ] Caching implemented for entity data
- [ ] Database query performance improved by 30%+
- [ ] 100% test coverage for repository layer

### Phase 3: Event Handler Architecture (1 week) 🔄 **EVENT SYSTEM PHASE**
**Goal**: Implement event-driven architecture for entity updates

**Design Principles**:
- **Mirror fund event handler patterns exactly** - Use identical handler structure and registry
- **Handler isolation** - Each handler handles one event type with clear boundaries
- **Event publishing** - Handlers publish domain events for dependent updates
- **Registry pattern** - Centralized routing of events to appropriate handlers
- **Light implementation** - Focus on essential events, not complex workflows

**Tasks**:
- [ ] **Implement BaseEntityEventHandler**: Abstract base class with common functionality
- [ ] **Create Event Handler Registry**: Centralized routing system for entity events
- [ ] **Implement Specific Handlers**: EntityCreated, EntityUpdated, EntityDeleted, TaxJurisdictionChanged
- [ ] **Create EntityUpdateOrchestrator**: Coordinates complete update pipeline
- [ ] **Add Domain Events**: Implement event classes and publishing mechanism
- [ ] **Integration Testing**: Test complete event flow from API to database

**Success Criteria**:
- [ ] All event types have dedicated handlers with clear responsibilities
- [ ] Event registry properly routes events to appropriate handlers
- [ ] Domain events are published for all significant state changes
- [ ] Complete update pipeline works end-to-end
- [ ] All existing functionality preserved through new architecture

### Phase 4: API Layer Enhancement (1 week) 🌐 **API PHASE**
**Goal**: Enhance existing API with comprehensive CRUD operations and enterprise patterns

**Design Principles**:
- **Mirror fund API patterns exactly** - Use identical controller and service structure
- **Enhance existing endpoints** - Build upon current GET and POST functionality
- **Consistent response formats** - Standardized error handling and response structures
- **Performance optimization** - Sub-50ms response times for all operations

**Tasks**:
- [ ] **Create EntityController**: Implement REST endpoints for entity operations
- [ ] **Create EntityService**: API service layer with business logic coordination
- [ ] **Implement DTOs**: Data transfer objects for request/response handling
- [ ] **Add Missing Endpoints**: PUT and DELETE operations for complete CRUD
- [ ] **Enhance Error Handling**: Consistent error responses and validation
- [ ] **Performance Testing**: Ensure all endpoints meet performance requirements

**Success Criteria**:
- [ ] All CRUD operations available through REST API
- [ ] Consistent error handling across all endpoints
- [ ] Sub-50ms response times for all operations
- [ ] 100% API test coverage
- [ ] Complete API documentation with examples

### Phase 5: Integration & Event System (1 week) 🔗 **INTEGRATION PHASE**
**Goal**: Connect new architecture to existing system and implement cross-module events

**Design Principles**:
- **Seamless integration** - New architecture works alongside existing system
- **Cross-module events** - Entity changes trigger fund and tax statement updates
- **Backward compatibility** - All existing functionality continues to work
- **Performance validation** - No regression in system performance

**Tasks**:
- [ ] **Connect to Fund System**: Implement cross-module event handling
- [ ] **Connect to Tax Statement System**: Handle tax statement updates
- [ ] **End-to-End Testing**: Validate complete workflows across all modules
- [ ] **Performance Validation**: Ensure no performance regression from integration
- [ ] **Rollback Strategy**: Implement ability to fall back to old system if issues arise

**Success Criteria**:
- [ ] New architecture fully integrated with existing system
- [ ] Cross-module events working correctly
- [ ] All integration tests passing
- [ ] Zero performance regression from integration
- [ ] Rollback capability implemented and tested

### Phase 6: Optimization & Production Readiness (1 week) 🚀 **OPTIMIZATION PHASE**
**Goal**: Optimize performance and prepare for production deployment

**Design Principles**:
- **Performance optimization** - Achieve target performance benchmarks
- **Production hardening** - Error handling, logging, and monitoring
- **Scalability validation** - Test with realistic data volumes
- **Documentation completion** - Complete all technical documentation

**Tasks**:
- [ ] **Performance Optimization**: Implement caching and query optimization
- [ ] **Production Hardening**: Add comprehensive error handling and logging
- [ ] **Scalability Testing**: Test with 1000+ entities and 5000+ funds
- [ ] **Monitoring Setup**: Implement performance metrics and health checks
- [ ] **Documentation Completion**: Complete all technical documentation

**Success Criteria**:
- [ ] All performance benchmarks met
- [ ] System scales to target production volumes
- [ ] Comprehensive monitoring and logging implemented
- [ ] All technical documentation completed
- [ ] Production deployment ready

## Detailed Architecture Patterns

### 1. Service Layer Pattern (Mirrors Fund Refactor)

```python
# EntityService - Extracted business logic
class EntityService:
    def create_entity(self, name: str, description: str = None, tax_jurisdiction: str = "AU") -> Entity:
        """Create a new entity with validation and business logic."""
        pass
    
    def update_entity(self, entity: Entity, **kwargs) -> Entity:
        """Update entity with validation and business rules."""
        pass
    
    def delete_entity(self, entity: Entity) -> bool:
        """Delete entity with proper cleanup and validation."""
        pass
```

### 2. Repository Pattern (Mirrors Fund Refactor)

```python
# EntityRepository - Clean data access
class EntityRepository:
    def __init__(self, session: Session):
        self.session = session
    
    def get_by_id(self, entity_id: int) -> Optional[Entity]:
        """Get entity by ID with optimized query."""
        pass
    
    def get_by_name(self, name: str) -> Optional[Entity]:
        """Get entity by name with caching."""
        pass
    
    def get_entities_with_fund_counts(self) -> List[Dict[str, Any]]:
        """Get entities with optimized fund count queries."""
        pass
```

### 3. Event Handler Pattern (Mirrors Fund Refactor)

```python
# BaseEntityEventHandler - Common functionality
class BaseEntityEventHandler(ABC):
    def __init__(self, session: Session, entity: Entity):
        self.session = session
        self.entity = entity
        self.entity_service = EntityService()
        self.calculation_service = EntityCalculationService()
    
    @abstractmethod
    def handle(self, event_data: Dict[str, Any]) -> Any:
        """Handle the event and return result."""
        pass
    
    def _publish_dependent_events(self, result: Any) -> None:
        """Publish domain events for dependent updates."""
        pass
```

### 4. Domain Event Pattern (Mirrors Fund Refactor)

```python
# EntityDomainEvent - Event base class
class EntityDomainEvent:
    def __init__(self, entity_id: int, event_date: date, timestamp: datetime, event_id: str):
        self.entity_id = entity_id
        self.event_date = event_date
        self.timestamp = timestamp
        self.event_id = event_id

# EntityCreatedEvent - Specific event type
class EntityCreatedEvent(EntityDomainEvent):
    def __init__(self, entity_id: int, event_date: date, entity_name: str, tax_jurisdiction: str):
        super().__init__(entity_id, event_date, datetime.now(timezone.utc), str(uuid.uuid4()))
        self.entity_name = entity_name
        self.tax_jurisdiction = tax_jurisdiction
```

## Risk Mitigation

### Technical Risks
1. **Breaking existing functionality**
   - **Mitigation**: Comprehensive testing at each phase with existing test suite
   - **Mitigation**: Zero breaking changes policy - all existing APIs must work unchanged

2. **Performance regression**
   - **Mitigation**: Performance benchmarking before and after each phase
   - **Mitigation**: Performance gates in CI/CD pipeline

3. **Integration complexity**
   - **Mitigation**: Mirror proven patterns from fund refactor
   - **Mitigation**: Incremental integration with rollback capability

### Business Risks
1. **Development time**
   - **Mitigation**: Light refactor approach reduces implementation time
   - **Mitigation**: Phased approach allows early benefits and risk identification

2. **Learning curve**
   - **Mitigation**: Use identical patterns to fund refactor for consistency
   - **Mitigation**: Comprehensive documentation and examples

## Success Metrics

### Phase 1 Metrics (Foundation & Service Layer)
- [ ] Entity model maintained under 100 lines (business logic extracted)
- [ ] 100% test coverage for all extracted services
- [ ] Zero performance regression on all operations
- [ ] All existing tests continue to pass

### Phase 2 Metrics (Repository Layer)
- [ ] All database operations abstracted through repository layer
- [ ] Zero direct database queries in models or services
- [ ] Database query performance improved by 30%+
- [ ] 100% test coverage for repository layer

### Phase 3 Metrics (Event Handler Architecture)
- [ ] All event types have dedicated handlers with clear responsibilities
- [ ] Event registry properly routes events to appropriate handlers
- [ ] Complete update pipeline working end-to-end
- [ ] All existing functionality preserved through new architecture

### Phase 4 Metrics (API Layer)
- [ ] All CRUD operations available through REST API
- [ ] Consistent error handling across all endpoints
- [ ] Sub-50ms response times for all operations
- [ ] 100% API test coverage

### Phase 5 Metrics (Integration)
- [ ] New architecture fully integrated with existing system
- [ ] Cross-module events working correctly
- [ ] All integration tests passing
- [ ] Zero performance regression from integration

### Phase 6 Metrics (Optimization)
- [ ] All performance benchmarks met
- [ ] System scales to target production volumes
- [ ] Comprehensive monitoring and logging implemented
- [ ] Production deployment ready

## Overall Success Metrics
- [ ] **Maintainability**: Entity model complexity maintained under 100 lines with business logic extracted
- [ ] **Performance**: All operations achieve sub-50ms response times
- [ ] **Scalability**: System supports 1000+ entities, 5000+ funds, 100+ tax jurisdictions
- [ ] **Reliability**: Zero breaking changes to existing functionality
- [ ] **Test Coverage**: 100% test coverage for all new components
- [ ] **Architecture Consistency**: 100% alignment with fund refactor patterns
- [ ] **Enterprise Standards**: Professional-grade maintainability and testability achieved

## File Structure Reference

### Current Structure (Clean & Focused)
```
src/entity/
├── models.py (149 lines - clean, focused model)
├── calculations.py (37 lines - minimal calculations)
└── __init__.py
```

### Refactored Structure (Modular) - **TARGET ARCHITECTURE**

#### 1. Event Handling Layer
```
src/entity/events/
├── __init__.py
├── base_handler.py (BaseEntityEventHandler abstract class)
├── handlers/
│   ├── __init__.py
│   ├── entity_created_handler.py
│   ├── entity_updated_handler.py
│   ├── entity_deleted_handler.py
│   ├── tax_jurisdiction_changed_handler.py
│   └── entity_funds_updated_handler.py
├── registry.py (EntityEventHandlerRegistry)
└── orchestrator.py (EntityUpdateOrchestrator)
```

#### 2. Domain Events System
```
src/entity/events/domain/
├── __init__.py
├── base_event.py (EntityDomainEvent)
├── entity_created_event.py
├── entity_updated_event.py
├── entity_deleted_event.py
├── tax_jurisdiction_changed_event.py
└── entity_funds_updated_event.py
```

#### 3. Business Logic Services
```
src/entity/services/
├── __init__.py
├── entity_service.py (entity operations, validation)
├── entity_calculation_service.py (financial year calculations)
└── entity_validation_service.py (business rules, constraints)
```

#### 4. Data Access Layer
```
src/entity/repositories/
├── __init__.py
├── entity_repository.py (entity CRUD operations, caching)
└── entity_summary_repository.py (summary data, materialized views)
```

#### 5. API Layer
```
src/entity/api/
├── __init__.py
├── entity_controller.py (REST endpoints)
├── entity_service.py (API service layer)
└── dto/
    └── entity_dto.py (entity data transfer objects)
```

#### 6. Core Models (Maintained Simplicity)
```
src/entity/
├── __init__.py
├── models.py (simplified - under 100 lines)
└── calculations.py (minimal - basic calculations only)
```

## Implementation Timeline

### **Total Duration: 6 weeks**
- **Phase 1**: Foundation & Service Layer (1 week)
- **Phase 2**: Repository Layer & Data Access (1 week)
- **Phase 3**: Event Handler Architecture (1 week)
- **Phase 4**: API Layer Enhancement (1 week)
- **Phase 5**: Integration & Event System (1 week)
- **Phase 6**: Optimization & Production Readiness (1 week)

### **Dependencies**
- **Prerequisite**: Investment company refactor should be completed first
- **Parallel Development**: Can run alongside other system improvements
- **Integration Points**: Will integrate with fund and investment company event systems

## Conclusion

This refactor represents a **light architectural alignment** that will achieve enterprise-grade standards while maintaining the entity module's current simplicity. By mirroring the successful fund refactor architecture, we establish:

✅ **Architectural Consistency** across the entire system  
✅ **Professional Quality** with clear separation of concerns  
✅ **Enterprise Standards** for maintainability and testability  
✅ **Scalability Foundation** for future growth and features  
✅ **Maintained Simplicity** - no over-engineering of simple operations  

**Current Progress**: We are ready to begin Phase 1 with a clear architectural vision and proven patterns from the fund refactor.

**Next Steps**: 
1. **IMMEDIATE**: Begin Phase 1 - Foundation & Service Layer (after investment_company refactor)
2. **READY FOR IMPLEMENTATION**: All architectural decisions aligned with fund refactor
3. **FINAL GOAL**: First-class professional enterprise system matching fund architecture standards

The entity refactor will create a cohesive, maintainable, and scalable enterprise system that integrates seamlessly with the existing fund and investment company architecture while preserving its focused, simple nature.
