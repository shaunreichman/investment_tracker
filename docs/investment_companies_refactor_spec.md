# Investment Companies Refactor Specification

## 🚀 **PROJECT STATUS: Architecture Foundation Phase** 🎯

**Current Phase**: Phase 1 - Foundation & Service Layer (0% COMPLETED) 🚀 **READY TO BEGIN**  
**Overall Progress**: 0% Complete - Foundation phase ready to begin  
**Risk Level**: MEDIUM (Current System) → **VERY LOW** (Complete enterprise architecture)

## Overview

This specification outlines the refactoring of the investment_company module from a monolithic, tightly-coupled model to a clean, event-driven architecture that mirrors the successful fund refactor. The goal is to create a first-class professional enterprise system with clear separation of concerns, maintainable business logic, and scalable performance.

## Design Philosophy

- **Architectural Consistency**: Mirror the exact patterns established in the fund refactor
- **Domain-Driven Design**: Clear boundaries between fund and company domains
- **Separation of Concerns**: Move complex business logic from models into dedicated services
- **Event-Driven Architecture**: Use domain events for loose coupling between components
- **Single Responsibility**: Each class has one clear purpose and reason to change
- **Enterprise Standards**: Achieve professional-grade maintainability and testability
- **Performance at Scale**: Support 1000+ companies, 5000+ funds, 100+ contacts with O(1) operations

## Current State Analysis

### Problems Identified
- **Monolithic Model**: 403 lines of business logic mixed with model definitions
- **Tight Coupling**: Direct database queries embedded in model methods
- **No Service Layer**: Business logic scattered throughout the model
- **Missing API Layer**: No REST endpoints for investment company operations
- **Poor Separation of Concerns**: Calculations, validation, and data access all mixed together
- **No Event System**: Changes don't trigger dependent updates
- **Limited Testability**: Business logic embedded in models makes unit testing difficult

### Current Architecture
```
InvestmentCompany → Fund → TaxStatement → Entity
    ↓                ↓         ↓           ↓
Complex          Multiple   Complex      Multiple
Business         Update     Tax          Update
Logic            Paths      Logic        Paths
```

## Target Architecture

### Enterprise-Grade Domain-Driven Design
```
Company Domain (Portfolio Management) ←→ Fund Domain (Fund Creation)
    ↓                                        ↓
CompanyPortfolioService              FundCreationService
    ↓                                        ↓
Portfolio Operations                  Fund Business Logic
    ↓                                        ↓
Company Events                        Fund Domain Events
```

### Event-Driven Handler Pattern
```
CompanyEvent → EventHandlerRegistry → SpecificHandler → DomainEvents → OtherHandlers
    ↓              ↓                      ↓              ↓              ↓
Event         Routes to              Handles         Publishes      Handle
Creation      Appropriate            Specific        Domain         Dependent
              Handler               Logic           Events         Updates
```

## Class Structure & Relationships

### Core Architecture Classes

#### 1. Event Handling Layer
```
BaseCompanyEventHandler (Abstract)
├── CompanyCreatedHandler
├── ContactAddedHandler
├── ContactUpdatedHandler
├── CompanyUpdatedHandler
├── PortfolioUpdatedHandler
└── CompanyDeletedHandler
```

#### 2. Event Management Layer
```
CompanyEventHandlerRegistry
├── Registers handlers for each event type
├── Routes events to appropriate handlers
└── Manages handler lifecycle

CompanyUpdateOrchestrator
├── Coordinates complete update pipeline
├── Manages transaction boundaries
└── Handles dependent updates
```

#### 3. Domain Event System
```
CompanyDomainEvent (Base)
├── CompanyCreatedEvent
├── ContactAddedEvent
├── ContactUpdatedEvent
├── CompanyUpdatedEvent
├── PortfolioUpdatedEvent
└── CompanyDeletedEvent
```

#### 4. Business Logic Services
```
CompanyPortfolioService
├── Manages portfolio operations and fund coordination
├── Delegates fund creation to fund domain
├── Handles company portfolio updates
└── Ensures data consistency across domains

CompanySummaryService
├── Handles portfolio calculations (total commitments, fund counts)
├── Separated from models for testability
└── Supports both active and completed fund scenarios

ContactManagementService
├── Manages contact operations and validation
├── Handles business rules for contact management
└── Triggers company updates when contacts change

CompanyValidationService
├── Handles business rule validation and constraint checking
├── Ensures data integrity at company level
└── Provides validation for company operations
```

#### 5. Data Access Layer
```
InvestmentCompanyRepository
├── Handles all database operations for companies
├── Implements caching strategies
└── Provides optimized queries for common operations

ContactRepository
├── Manages contact persistence
├── Handles bulk operations efficiently
└── Provides contact querying capabilities

CompanySummaryRepository
├── Manages summary data and calculations
├── Implements materialized views for performance
└── Provides aggregated data access
```

### Class Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API Layer                                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│  CompanyController  →  CompanyService  →  CompanyUpdateOrchestrator            │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Business Logic Layer                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  CompanyPortfolioService  ←→  CompanySummaryService  ←→  ContactManagementService │
│           ↓                           ↓                           ↓              │
│  FundCreationService      ←→  CompanyValidationService  ←→  ContactOperations   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Event Handling Layer                                    │
├─────────────────────────────────────────────────────────────────────────────────┤
│  CompanyEventHandlerRegistry                                                   │
│  ├── CompanyCreatedHandler                                                     │
│  ├── ContactAddedHandler                                                       │
│  ├── ContactUpdatedHandler                                                     │
│  ├── CompanyUpdatedHandler                                                     │
│  ├── PortfolioUpdatedHandler                                                   │
│  └── CompanyDeletedHandler                                                     │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Domain Event System                                     │
├─────────────────────────────────────────────────────────────────────────────────┤
│  CompanyDomainEvent  →  EventBus  →  EventHandlers  →  Dependent Updates      │
│  ├── CompanyCreatedEvent                                                       │
│  ├── ContactAddedEvent                                                         │
│  ├── ContactUpdatedEvent                                                       │
│  ├── CompanyUpdatedEvent                                                       │
│  ├── PortfolioUpdatedEvent                                                     │
│  └── CompanyDeletedEvent                                                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Data Access Layer                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│  InvestmentCompanyRepository  ←→  ContactRepository  ←→  CompanySummaryRepository │
└─────────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────────┐
│                        Database Layer                                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│  InvestmentCompany  ←→  Contact  ←→  Fund  ←→  Entity                         │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## Implementation Strategy

### Phase 1: Foundation & Service Layer (2 weeks) 🏗️ **FOUNDATION PHASE**
**Goal**: Extract business logic from models into dedicated services while maintaining all existing functionality

**Design Principles**:
- **Mirror fund refactor patterns exactly** - Use identical service layer structure
- **Zero breaking changes** - All existing functionality must continue to work unchanged
- **Incremental extraction** - Extract one service at a time to maintain stability
- **Comprehensive testing** - Each extracted service must have 100% test coverage
- **Domain-driven design** - Clear boundaries between company and fund domains

**Tasks**:
- [ ] **Create CompanyPortfolioService**: Extract portfolio operations and fund coordination logic
- [ ] **Create CompanySummaryService**: Extract portfolio calculations, fund counting, and performance metrics
- [ ] **Create ContactManagementService**: Extract contact operations, validation, and business rules
- [ ] **Create CompanyValidationService**: Extract business rule validation and constraint checking
- [ ] **Update InvestmentCompany Model**: Integrate with new services while maintaining existing interface
- [ ] **Comprehensive Testing**: Test all extracted services in isolation with 100% coverage
- [ ] **Performance Validation**: Ensure no performance regression from extraction

**Success Criteria**:
- [ ] InvestmentCompany model reduced from 403 lines to under 150 lines (250+ lines extracted)
- [ ] 100% test coverage for all extracted services
- [ ] Zero performance regression on all operations
- [ ] All existing tests continue to pass
- [ ] All existing functionality preserved through new service layer
- [ ] Clear domain boundaries established between company and fund systems

### Phase 2: Repository Layer & Data Access (1 week) 🗄️ **DATA ACCESS PHASE**
**Goal**: Implement repository pattern for clean data access abstraction

**Design Principles**:
- **Mirror fund repository patterns exactly** - Use identical repository structure and methods
- **Clean separation of concerns** - Models become simple data containers
- **Optimized queries** - Implement efficient data access patterns
- **Caching strategy** - Add caching for frequently accessed data

**Tasks**:
- [ ] **Create InvestmentCompanyRepository**: Handle all company CRUD operations and queries
- [ ] **Create ContactRepository**: Manage contact persistence and relationship queries
- [ ] **Create CompanySummaryRepository**: Handle summary data and aggregated calculations
- [ ] **Implement Caching Strategy**: Add Redis-based caching for company summaries
- [ ] **Optimize Database Queries**: Add proper indexes and query optimization
- [ ] **Integration Testing**: Test repository layer with real database operations

**Success Criteria**:
- [ ] All database operations abstracted through repository layer
- [ ] Zero direct database queries in models or services
- [ ] Caching implemented for company summary data
- [ ] Database query performance improved by 50%+
- [ ] 100% test coverage for repository layer

### Phase 3: Event Handler Architecture (2 weeks) 🔄 **EVENT SYSTEM PHASE**
**Goal**: Implement event-driven architecture for company updates

**Design Principles**:
- **Mirror fund event handler patterns exactly** - Use identical handler structure and registry
- **Handler isolation** - Each handler handles one event type with clear boundaries
- **Event publishing** - Handlers publish domain events for dependent updates
- **Registry pattern** - Centralized routing of events to appropriate handlers
- **Domain boundaries** - Company events don't duplicate fund business logic

**Tasks**:
- [ ] **Implement BaseCompanyEventHandler**: Abstract base class with common functionality
- [ ] **Create Event Handler Registry**: Centralized routing system for company events
- [ ] **Implement Specific Handlers**: CompanyCreated, ContactAdded, ContactUpdated, CompanyUpdated, PortfolioUpdated, CompanyDeleted
- [ ] **Create CompanyUpdateOrchestrator**: Coordinates complete update pipeline
- [ ] **Add Domain Events**: Implement event classes and publishing mechanism
- [ ] **Integration Testing**: Test complete event flow from API to database

**Success Criteria**:
- [ ] All event types have dedicated handlers with clear responsibilities
- [ ] Event registry properly routes events to appropriate handlers
- [ ] Domain events are published for all significant state changes
- [ ] Complete update pipeline works end-to-end
- [ ] All existing functionality preserved through new architecture
- [ ] Company events coordinate with fund domain without duplicating logic

### Phase 4: API Layer Implementation (1 week) 🌐 **API PHASE**
**Goal**: Create comprehensive REST API for investment company operations

**Design Principles**:
- **Mirror fund API patterns exactly** - Use identical controller and service structure
- **Consistent response formats** - Standardized error handling and response structures
- **Comprehensive endpoints** - Full CRUD operations for companies and contacts
- **Performance optimization** - Sub-500ms response times for all operations (realistic enterprise targets)

**Tasks**:
- [ ] **Create CompanyController**: Implement REST endpoints for company operations
- [ ] **Create CompanyService**: API service layer with business logic coordination
- [ ] **Implement DTOs**: Data transfer objects for request/response handling
- [ ] **Add Error Handling**: Consistent error responses and validation
- [ ] **Performance Testing**: Ensure all endpoints meet performance requirements
- [ ] **API Documentation**: Complete endpoint documentation and examples

**Success Criteria**:
- [ ] All CRUD operations available through REST API
- [ ] Consistent error handling across all endpoints
- [ ] Sub-500ms response times for all operations (realistic enterprise targets)
- [ ] 100% API test coverage
- [ ] Complete API documentation with examples

### Phase 5: Integration & Event System (1 week) 🔗 **INTEGRATION PHASE**
**Goal**: Connect new architecture to existing system and implement cross-module events

**Design Principles**:
- **Seamless integration** - New architecture works alongside existing system
- **Cross-module events** - Company changes trigger fund and entity updates
- **Backward compatibility** - All existing functionality continues to work
- **Performance validation** - No regression in system performance
- **Domain coordination** - Company and fund domains work together seamlessly

**Tasks**:
- [ ] **Connect to Fund System**: Implement cross-module event handling through CompanyPortfolioService
- [ ] **Connect to Entity System**: Handle entity-related updates
- [ ] **End-to-End Testing**: Validate complete workflows across all modules
- [ ] **Performance Validation**: Ensure no performance regression from integration
- [ ] **Rollback Strategy**: Implement ability to fall back to old system if issues arise

**Success Criteria**:
- [ ] New architecture fully integrated with existing system
- [ ] Cross-module events working correctly through domain coordination
- [ ] All integration tests passing
- [ ] Zero performance regression from integration
- [ ] Rollback capability implemented and tested
- [ ] Company and fund domains coordinate without duplication

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
- [ ] **Scalability Testing**: Test with realistic enterprise volumes (100+ companies, 500+ funds)
- [ ] **Monitoring Setup**: Implement performance metrics and health checks
- [ ] **Documentation Completion**: Complete all technical documentation

**Success Criteria**:
- [ ] All performance benchmarks met
- [ ] System scales to realistic enterprise volumes
- [ ] Comprehensive monitoring and logging implemented
- [ ] All technical documentation completed
- [ ] Production deployment ready

## Detailed Architecture Patterns

### 1. Service Layer Pattern (Enterprise-Grade Domain Coordination)

```python
# CompanyPortfolioService - Coordinates between company and fund domains
class CompanyPortfolioService:
    def add_fund_to_portfolio(self, fund_data: Dict[str, Any], session: Session) -> Fund:
        """
        Add a fund to company portfolio with domain coordination.
        
        This service coordinates between company and fund domains without
        duplicating fund business logic.
        """
        # Delegate fund creation to fund domain (single source of truth)
        fund_service = FundCreationService()
        fund = fund_service.create_fund(fund_data, session)
        
        # Update company portfolio (company domain responsibility)
        self._update_company_portfolio(fund, session)
        
        # Publish company domain event
        self._publish_domain_event(CompanyPortfolioUpdatedEvent(fund))
        
        return fund
    
    def _update_company_portfolio(self, fund: Fund, session: Session) -> None:
        """Update company portfolio data after fund addition."""
        # Update fund count
        # Update total commitments
        # Trigger summary recalculations
        pass
```

### 2. Repository Pattern (Mirrors Fund Refactor)

```python
# InvestmentCompanyRepository - Clean data access
class InvestmentCompanyRepository:
    def get_by_id(self, company_id: int) -> Optional[InvestmentCompany]:
        """Get company by ID with optimized query."""
        pass
    
    def get_by_name(self, name: str) -> Optional[InvestmentCompany]:
        """Get company by name with caching."""
        pass
    
    def get_companies_with_fund_counts(self) -> List[Dict[str, Any]]:
        """Get companies with optimized fund count queries."""
        pass
```

### 3. Event Handler Pattern (Domain-Focused)

```python
# BaseCompanyEventHandler - Common functionality
class BaseCompanyEventHandler(ABC):
    def __init__(self, session: Session, company: InvestmentCompany):
        self.session = session
        self.company = company
        self.portfolio_service = CompanyPortfolioService()
        self.summary_service = CompanySummaryService()
        self.contact_service = ContactManagementService()
    
    @abstractmethod
    def handle(self, event_data: Dict[str, Any]) -> Any:
        """Handle the event and return result."""
        pass
    
    def _publish_dependent_events(self, result: Any) -> None:
        """Publish domain events for dependent updates."""
        pass
```

### 4. Domain Event Pattern (Company-Focused)

```python
# CompanyDomainEvent - Event base class
class CompanyDomainEvent:
    def __init__(self, company_id: int, event_date: date, timestamp: datetime, event_id: str):
        self.company_id = company_id
        self.event_date = event_date
        self.timestamp = timestamp
        self.event_id = event_id

# PortfolioUpdatedEvent - Company portfolio changes
class PortfolioUpdatedEvent(CompanyDomainEvent):
    def __init__(self, company_id: int, event_date: date, fund_id: int, operation: str):
        super().__init__(company_id, event_date, datetime.now(timezone.utc), str(uuid.uuid4()))
        self.fund_id = fund_id
        self.operation = operation  # 'added', 'removed', 'updated'
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

4. **Domain boundary confusion**
   - **Mitigation**: Clear documentation of domain responsibilities
   - **Mitigation**: CompanyPortfolioService as clear coordination point

### Business Risks
1. **Development time**
   - **Mitigation**: Phased approach allows early benefits and risk identification
   - **Mitigation**: Parallel development of new features where possible

2. **Learning curve**
   - **Mitigation**: Use identical patterns to fund refactor for consistency
   - **Mitigation**: Comprehensive documentation and examples

## Success Metrics

### Phase 1 Metrics (Foundation & Service Layer)
- [ ] InvestmentCompany model reduced from 403 lines to under 150 lines (250+ lines extracted)
- [ ] 100% test coverage for all extracted services
- [ ] Zero performance regression on all operations
- [ ] All existing tests continue to pass
- [ ] Clear domain boundaries established

### Phase 2 Metrics (Repository Layer)
- [ ] All database operations abstracted through repository layer
- [ ] Zero direct database queries in models or services
- [ ] Caching implemented for company summary data
- [ ] Database query performance improved by 50%+
- [ ] 100% test coverage for repository layer

### Phase 3 Metrics (Event Handler Architecture)
- [ ] All event types have dedicated handlers with clear responsibilities
- [ ] Event registry properly routes events to appropriate handlers
- [ ] Complete update pipeline working end-to-end
- [ ] All existing functionality preserved through new architecture
- [ ] Company and fund domains coordinate without duplication

### Phase 4 Metrics (API Layer)
- [ ] All CRUD operations available through REST API
- [ ] Consistent error handling across all endpoints
- [ ] Sub-500ms response times for all operations (realistic enterprise targets)
- [ ] 100% API test coverage

### Phase 5 Metrics (Integration)
- [ ] New architecture fully integrated with existing system
- [ ] Cross-module events working correctly through domain coordination
- [ ] All integration tests passing
- [ ] Zero performance regression from integration

### Phase 6 Metrics (Optimization)
- [ ] All performance benchmarks met
- [ ] System scales to realistic enterprise volumes
- [ ] Comprehensive monitoring and logging implemented
- [ ] Production deployment ready

## Overall Success Metrics
- [ ] **Maintainability**: InvestmentCompany model complexity reduced by 70% (from 403 to under 150 lines)
- [ ] **Performance**: All operations achieve sub-500ms response times (realistic enterprise targets)
- [ ] **Scalability**: System supports realistic enterprise volumes (100+ companies, 500+ funds)
- [ ] **Reliability**: Zero breaking changes to existing functionality
- [ ] **Test Coverage**: 100% test coverage for all new components
- [ ] **Architecture Consistency**: 100% alignment with fund refactor patterns
- [ ] **Domain Boundaries**: Clear separation between company and fund domains
- [ ] **Enterprise Standards**: Professional-grade maintainability and testability achieved

## File Structure Reference

### Current Structure (Monolithic)
```
src/investment_company/
├── models.py (403 lines - everything in one file)
├── calculations.py (43 lines - minimal calculations)
└── __init__.py
```

### Refactored Structure (Enterprise-Grade Modular) - **TARGET ARCHITECTURE**

#### 1. Event Handling Layer
```
src/investment_company/events/
├── __init__.py
├── base_handler.py (BaseCompanyEventHandler abstract class)
├── handlers/
│   ├── __init__.py
│   ├── company_created_handler.py
│   ├── contact_added_handler.py
│   ├── contact_updated_handler.py
│   ├── company_updated_handler.py
│   ├── portfolio_updated_handler.py
│   └── company_deleted_handler.py
├── registry.py (CompanyEventHandlerRegistry)
└── orchestrator.py (CompanyUpdateOrchestrator)
```

#### 2. Domain Events System
```
src/investment_company/events/domain/
├── __init__.py
├── base_event.py (CompanyDomainEvent)
├── company_created_event.py
├── contact_added_event.py
├── contact_updated_event.py
├── company_updated_event.py
├── portfolio_updated_event.py
└── company_deleted_event.py
```

#### 3. Business Logic Services
```
src/investment_company/services/
├── __init__.py
├── company_portfolio_service.py (portfolio operations, fund coordination)
├── company_summary_service.py (portfolio calculations, fund counting)
├── contact_management_service.py (contact operations, validation)
└── company_validation_service.py (business rules, constraints)
```

#### 4. Data Access Layer
```
src/investment_company/repositories/
├── __init__.py
├── investment_company_repository.py (company CRUD operations, caching)
├── contact_repository.py (contact persistence, bulk operations)
└── company_summary_repository.py (summary data, materialized views)
```

#### 5. API Layer
```
src/investment_company/api/
├── __init__.py
├── company_controller.py (REST endpoints)
├── company_service.py (API service layer)
└── dto/
    ├── company_dto.py (company data transfer objects)
    └── contact_dto.py (contact data transfer objects)
```

#### 6. Core Models (Simplified)
```
src/investment_company/
├── __init__.py
├── models.py (simplified - under 150 lines)
└── calculations.py (minimal - basic calculations only)
```

## Key Architectural Decisions

### 1. Domain Boundaries
- **Company Domain**: Owns company portfolio management, contact management, and company operations
- **Fund Domain**: Owns fund creation logic, fund business rules, and fund lifecycle
- **Coordination**: CompanyPortfolioService coordinates between domains without duplicating logic

### 2. Event System Design
- **Company Events**: Handle company-specific state changes and portfolio updates
- **Fund Events**: Handle fund-specific business logic and lifecycle
- **Cross-Domain**: Company events can trigger fund updates, but don't implement fund logic

### 3. Service Layer Responsibilities
- **CompanyPortfolioService**: Portfolio operations and fund coordination
- **CompanySummaryService**: Company-level calculations and summaries
- **ContactManagementService**: Contact operations and validation
- **CompanyValidationService**: Company business rules and constraints

### 4. Performance Targets
- **Response Times**: Sub-500ms for all operations (realistic enterprise targets)
- **Scalability**: Support realistic enterprise volumes (100+ companies, 500+ funds)
- **Caching**: Redis-based caching for frequently accessed data

## Conclusion

This refactor represents a critical foundation for the investment company system's future scalability and maintainability. By mirroring the successful fund refactor architecture while maintaining clear domain boundaries, we establish:

✅ **Architectural Consistency** across the entire system  
✅ **Professional Quality** with clear separation of concerns  
✅ **Enterprise Standards** for maintainability and testability  
✅ **Scalability Foundation** for future growth and features  
✅ **Domain-Driven Design** with clear boundaries and responsibilities  

**Current Progress**: We are ready to begin Phase 1 with a clear architectural vision, proven patterns from the fund refactor, and enterprise-grade domain coordination.

**Next Steps**: 
1. **IMMEDIATE**: Begin Phase 1 - Foundation & Service Layer with CompanyPortfolioService
2. **READY FOR IMPLEMENTATION**: All architectural decisions aligned with fund refactor and enterprise standards
3. **FINAL GOAL**: First-class professional enterprise system with clear domain boundaries and scalable architecture

The investment company refactor will create a cohesive, maintainable, and scalable enterprise system that integrates seamlessly with the existing fund architecture while maintaining clear domain responsibilities and enterprise-grade standards.
