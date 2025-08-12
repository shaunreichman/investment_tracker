# Circular Dependency Analysis - Phase 1 Dependency Mapping

## Overview

This document analyzes circular dependencies in the current system architecture. Circular dependencies are a critical risk factor for the refactor and must be identified and resolved before proceeding with architectural changes.

## Identified Circular Dependencies

### 1. **Fund ↔ TaxStatement Circular Dependency**

#### **Dependency Chain**
```
Fund (src/fund/models.py)
    ↓ imports TaxStatement
TaxStatement (src/tax/models.py)
    ↓ imports Fund
Fund (src/fund/models.py)
    ↓ imports TaxStatement
... (circular)
```

#### **Evidence of Circular Dependency**

**In Fund Models (src/fund/models.py):**
```python
# Line 36: Comment acknowledging circular import issue
# Note: TaxStatement is imported as a string reference to avoid circular imports

# Line 234: Relationship definition using string reference
tax_statements = relationship("TaxStatement", back_populates="fund", cascade="all, delete-orphan", lazy='selectin')

# Lines 482, 514, 535, 1662, 2342: Direct imports when needed
from ..tax.models import TaxStatement
from src.tax.models import TaxStatement
```

**In Tax Models (src/tax/models.py):**
```python
# Line 15: Direct import of Fund
from src.fund.models import Fund

# Line 142: Relationship back to Fund
fund = relationship("Fund", back_populates="tax_statements", lazy='selectin')
```

#### **Current Workarounds**
1. **String References**: Using string references in SQLAlchemy relationships
2. **Lazy Imports**: Importing TaxStatement only when needed in methods
3. **Conditional Imports**: Different import strategies in different methods

#### **Risk Assessment**
- **Risk Level**: HIGH
- **Impact**: Could cause import errors and runtime failures
- **Refactor Impact**: Must be resolved before architectural changes

### 2. **Fund ↔ InvestmentCompany Circular Dependency**

#### **Dependency Chain**
```
Fund (src/fund/models.py)
    ↓ has investment_company_id foreign key
InvestmentCompany (src/investment_company/models.py)
    ↓ imports Fund and FundStatus
Fund (src/fund/models.py)
    ↓ imports InvestmentCompany
... (circular)
```

#### **Evidence of Circular Dependency**

**In Fund Models (src/fund/models.py):**
```python
# Line 168: Foreign key to InvestmentCompany
investment_company_id = Column(Integer, ForeignKey('investment_companies.id'), nullable=False)

# Line 240: Relationship to InvestmentCompany
investment_company = relationship("InvestmentCompany", back_populates="funds", lazy='selectin')
```

**In InvestmentCompany Models (src/investment_company/models.py):**
```python
# Lines 239, 273, 378: Direct imports of Fund and FundStatus
from ..fund.models import Fund
from ..fund.models import FundStatus
```

#### **Current Workarounds**
1. **Foreign Key Constraints**: Using string-based foreign key references
2. **Lazy Loading**: Using 'selectin' lazy loading strategy
3. **Delayed Imports**: Importing Fund models only when needed

#### **Risk Assessment**
- **Risk Level**: MEDIUM
- **Impact**: Could affect fund status updates and company record updates
- **Refactor Impact**: Must be resolved for clean event-driven architecture

## Dependency Graph Analysis

### **Current Import Structure**
```
src/
├── fund/
│   ├── models.py ← imports TaxStatement, InvestmentCompany, Entity, RiskFreeRate, BankAccount
│   └── calculations.py
├── tax/
│   ├── models.py ← imports Fund, Entity
│   └── events.py ← imports FundEvent, EventType, TaxPaymentType, DistributionType, GroupType
├── investment_company/
│   └── models.py ← imports Fund, FundStatus
├── entity/
│   └── models.py ← imports Fund
├── rates/
│   └── models.py ← no fund imports
├── banking/
│   └── models.py ← no fund imports
└── shared/
    └── calculations.py ← imports EventType, FundType
```

### **Circular Import Patterns**
1. **Fund → TaxStatement → Fund** (HIGH RISK)
2. **Fund → InvestmentCompany → Fund** (MEDIUM RISK)
3. **Fund → Entity → Fund** (LOW RISK - likely not circular)

## Impact on Refactor Architecture

### **Event-Driven Architecture Requirements**
The planned event-driven architecture requires:
1. **Clean Dependencies**: No circular imports between domains
2. **Event Publishing**: Models must be able to publish events without circular references
3. **Handler Isolation**: Event handlers must be independent of model imports

### **Current Architecture Problems**
1. **Tight Coupling**: Models directly import and update each other
2. **Circular Dependencies**: Cannot resolve imports cleanly
3. **Update Chains**: Direct method calls create complex dependency chains

## Resolution Strategies

### **Strategy 1: Domain Event Decoupling**
```
Current: Fund → TaxStatement (direct update)
Target: Fund → FundEvent → TaxStatementUpdatedEvent → TaxStatementHandler
```

**Benefits:**
- Breaks circular dependencies
- Enables event-driven architecture
- Improves testability and maintainability

**Implementation:**
1. Create domain events for all cross-model updates
2. Implement event handlers in each domain
3. Remove direct model imports between domains

### **Strategy 2: Service Layer Extraction**
```
Current: Fund model contains business logic
Target: Fund model + FundService + EventHandlers
```

**Benefits:**
- Separates concerns
- Breaks circular dependencies
- Enables clean architecture

**Implementation:**
1. Extract business logic to service classes
2. Use dependency injection for cross-domain operations
3. Implement event publishing in services

### **Strategy 3: Repository Pattern**
```
Current: Models directly query database
Target: Models + Repositories + Services
```

**Benefits:**
- Centralizes data access
- Breaks model dependencies
- Enables caching and optimization

**Implementation:**
1. Create repository interfaces
2. Implement repositories for each domain
3. Use repositories in services instead of direct model access

## Migration Plan

### **Phase 1: Analysis (Current)**
- [x] Identify all circular dependencies
- [x] Document dependency chains
- [x] Assess risk levels
- [ ] Plan resolution strategies

### **Phase 2: Dependency Resolution**
- [ ] Implement domain events for cross-model updates
- [ ] Extract business logic to services
- [ ] Remove circular imports
- [ ] Test dependency resolution

### **Phase 3: Architecture Implementation**
- [ ] Implement event handlers
- [ ] Implement repositories
- [ ] Implement services
- [ ] Test new architecture

## Risk Mitigation

### **Immediate Actions**
1. **Document All Dependencies**: Complete dependency mapping
2. **Identify Breaking Points**: Find all places where circular dependencies cause issues
3. **Plan Rollback Strategy**: Ensure system remains functional during transition

### **Long-term Actions**
1. **Implement Event System**: Break circular dependencies with events
2. **Extract Services**: Move business logic out of models
3. **Implement Repositories**: Centralize data access

## Success Criteria

### **Dependency Resolution**
- [ ] Zero circular imports between domains
- [ ] Clean dependency graph with no cycles
- [ ] All cross-model updates via events

### **Architecture Cleanliness**
- [ ] Models only contain data and relationships
- [ ] Business logic in services
- [ ] Data access in repositories
- [ ] Cross-domain communication via events

### **System Stability**
- [ ] No import errors during startup
- [ ] No runtime dependency issues
- [ ] Clean separation of concerns

## Conclusion

The current system has significant circular dependencies that must be resolved before implementing the event-driven architecture. The Fund ↔ TaxStatement circular dependency is particularly critical and requires immediate attention.

The resolution strategies outlined above provide a clear path forward:
1. **Domain Events**: Break circular dependencies
2. **Service Extraction**: Separate business logic
3. **Repository Pattern**: Centralize data access

These changes are not optional - they are required for the refactor to succeed. The circular dependencies represent a fundamental architectural flaw that prevents clean separation of concerns and must be addressed before proceeding with Phase 2.

**Next Steps:**
1. Complete dependency mapping for all domains
2. Design domain event structure
3. Plan service extraction strategy
4. Implement dependency resolution in phases
