# Backend Codebase Overview

## Project Context
This is an investment tracking system built with Python, SQLAlchemy, and FastAPI. The system manages investment companies, funds, fund events, banking operations, tax calculations, and risk-free rates.

## Architecture Overview
The codebase follows a **Domain-Driven Design (DDD)** approach with:
- **Domain modules** for each business area (fund, banking, investment_company, etc.)
- **Event-driven architecture** with domain events and handlers
- **Repository pattern** for data access
- **Service layer** for business logic
- **API layer** with controllers and DTOs
- **Shared utilities** and base classes

## Directory Structure

### Root Level (`src/`)
```
src/
├── __init__.py          # Main package exports and version info
├── config.py            # Database and application configuration
├── api.py               # API entry point
├── api_legacy.py        # Legacy API implementation (89KB, 1785 lines)
├── database.py          # Database connection and session management
├── api/                 # API layer (controllers, routes, middleware)
├── banking/             # Banking domain module
├── entity/              # Entity domain module
├── fund/                # Fund domain module
├── investment_company/  # Investment company domain module
├── rates/               # Risk-free rates domain module
├── tax/                 # Tax calculations domain module
└── shared/              # Shared utilities and base classes
```

### API Layer (`src/api/`)
```
api/
├── __init__.py          # API package initialization
├── database.py          # API-specific database handling
├── performance.py       # Performance monitoring (10KB, 296 lines)
├── README_banking.md    # Banking API documentation (12KB, 510 lines)
├── controllers/         # API controllers
├── dto/                 # Data Transfer Objects
├── middleware/          # Request/response middleware
└── routes/              # API route definitions
```

### Domain Modules

#### Banking Domain (`src/banking/`)
```
banking/
├── __init__.py          # Banking module exports
├── enums.py             # Banking enums (12KB, 366 lines)
├── events/              # Domain events and handlers
│   ├── __init__.py
│   ├── base_handler.py  # Base event handler (7.2KB, 214 lines)
│   ├── orchestrator.py  # Event orchestration (16KB, 365 lines)
│   ├── registry.py      # Event registry (6.3KB, 157 lines)
│   ├── cross_module_registry.py  # Cross-module event handling (12KB, 249 lines)
│   ├── domain/          # Domain event definitions
│   └── handlers/        # Event handler implementations
├── models/              # Banking data models
├── repositories/        # Data access layer
├── services/            # Business logic services
└── scripts/             # Utility scripts
```

#### Fund Domain (`src/fund/`)
```
fund/
├── __init__.py          # Fund module exports
├── enums.py             # Fund enums (18KB, 575 lines)
├── events/              # Fund domain events
├── models/              # Fund data models
├── repositories/        # Fund data access
├── services/            # Fund business logic
└── orchestrator.py      # Fund event orchestration
```

#### Investment Company Domain (`src/investment_company/`)
```
investment_company/
├── __init__.py          # Investment company module exports
├── enums.py             # Company enums (5.9KB, 184 lines)
├── api/                 # Company-specific API endpoints
├── events/              # Company domain events
├── models/              # Company data models
├── repositories/        # Company data access
└── services/            # Company business logic
```

#### Entity Domain (`src/entity/`)
```
entity/
├── __init__.py          # Entity module exports
├── models.py            # Entity data models (5.6KB, 150 lines)
├── calculations.py      # Entity calculations (993B, 37 lines)
└── events/              # Entity domain events
```

#### Tax Domain (`src/tax/`)
```
tax/
├── __init__.py          # Tax module exports
├── models.py            # Tax models (27KB, 580 lines)
├── calculations.py      # Tax calculations (1.8KB, 59 lines)
└── events.py            # Tax domain events (15KB, 338 lines)
```

#### Rates Domain (`src/rates/`)
```
rates/
├── __init__.py          # Rates module exports
├── models.py            # Risk-free rate models (6.1KB, 158 lines)
├── calculations.py      # Rate calculations (979B, 36 lines)
└── rfr.csv              # Risk-free rate data (3.8KB, 91 lines)
```

#### Shared Utilities (`src/shared/`)
```
shared/
├── __init__.py          # Shared utilities exports
├── base.py              # Base classes (221B, 10 lines)
└── utils.py             # Utility functions (5.5KB, 178 lines)
```

## Key Design Patterns

### 1. Domain-Driven Design
- Each business domain has its own module with models, services, and repositories
- Clear separation between domain logic and infrastructure concerns
- Domain events for cross-module communication

### 2. Event-Driven Architecture
- Base event handler system (`base_handler.py`)
- Event orchestrators for coordinating complex workflows
- Cross-module event registry for domain integration
- Event handlers for business logic execution

### 3. Repository Pattern
- Data access abstracted through repository interfaces
- Domain models remain clean of database concerns
- Consistent data access patterns across domains

### 4. Service Layer
- Business logic encapsulated in service classes
- Domain calculations and validations
- Transaction management and coordination

### 5. API Layer
- Controllers for request handling
- DTOs for data transformation
- Middleware for cross-cutting concerns
- Route definitions for endpoint mapping

## Database Architecture
- **PostgreSQL** as the primary database
- **SQLAlchemy** ORM for data modeling
- **Alembic** for database migrations
- Session management through `with_session` decorator
- Centralized database configuration in `config.py`

## Key Dependencies
Based on the codebase structure, the system likely uses:
- **FastAPI** for the web framework
- **SQLAlchemy** for ORM
- **Pydantic** for data validation
- **PostgreSQL** for database
- **Alembic** for migrations

## Testing Structure
The project includes comprehensive testing:
- **Unit tests** for individual components
- **Integration tests** for workflows and data consistency
- **E2E tests** for critical user paths
- **Property-based tests** for business rules
- **Performance tests** for scalability
- **Contract tests** for API consistency

## Development Guidelines
- **Absolute imports** preferred (`from src.module import Class`)
- **Session management** handled by backend, clients remain stateless
- **Domain methods** preferred over direct constructors
- **Validation** in application code rather than database constraints
- **Event-driven** communication between modules

## Notable Files
- **`api_legacy.py`** (89KB) - Large legacy API implementation
- **`tax/models.py`** (27KB) - Complex tax modeling
- **`fund/enums.py`** (18KB) - Extensive fund type definitions
- **`banking/events/orchestrator.py`** (16KB) - Complex event orchestration
- **`tax/events.py`** (15KB) - Tax event handling

## Architecture Strengths
1. **Clear domain separation** with dedicated modules
2. **Event-driven design** for loose coupling
3. **Comprehensive testing** strategy
4. **Repository pattern** for data access abstraction
5. **Service layer** for business logic encapsulation

## Areas for Review
1. **Legacy API** (`api_legacy.py`) - Large file that may benefit from refactoring
2. **Event complexity** - Some event handlers are quite large
3. **Enum proliferation** - Some enum files are very large
4. **Cross-module dependencies** - Event registry complexity

This codebase demonstrates a mature, enterprise-level investment tracking system with solid architectural foundations and comprehensive testing coverage.
