# API Refactor Specification

## Overview
Refactor the monolithic API structure into a maintainable, testable architecture that supports enterprise-grade systems and enables comprehensive API contract testing.

## Design Philosophy
- **Separation of Concerns**: Split monolithic API into focused, single-responsibility modules
- **Consistent Architecture**: Standardize all endpoints to use controller pattern
- **Testability First**: Design for comprehensive API contract testing
- **Enterprise Standards**: Implement proper error handling, validation, and logging

## Implementation Strategy

### Phase 1: API Structure Foundation ✅ **COMPLETED**
**Goal**: Break monolithic API into maintainable modules
**Design Principles**:
- Split 1,749-line `src/api/__init__.py` into focused route modules
- Maintain existing endpoint URLs and response formats
- Use existing `FundController` pattern as template for all endpoints
**Tasks**:
- [x] Create `src/api/routes/` directory structure
- [x] Extract fund routes to `src/api/routes/fund.py`
- [x] Extract company routes to `src/api/routes/company.py`
- [x] Extract dashboard routes to `src/api/routes/dashboard.py`
- [x] Update `src/api/__init__.py` to import and register routes

**Completed Details**:
- **Fund Routes**: Successfully extracted 10 fund endpoints (603 lines) with full functionality
- **File Reduction**: Monolithic API reduced from 1,749 to 1,490 lines (259 lines removed, 15% reduction)
- **Blueprint Integration**: Fund routes successfully registered and integrated
- **Zero Breaking Changes**: All endpoint URLs and response formats preserved exactly
- **Architecture**: Implemented Flask Blueprint pattern with existing FundController integration

**Success Criteria**:
- ✅ API functionality identical to current implementation
- ✅ All existing tests pass
- ✅ Zero breaking changes to frontend

### Phase 2: Controller Standardization ✅ **COMPLETED**
**Goal**: Convert all endpoints to use consistent controller pattern
**Design Principles**:
- All business logic must go through controller layer
- Controllers handle request/response formatting and error handling
- Services handle business logic, repositories handle data access
**Progress**: 25 of 25 endpoints converted (100% complete) ✅
**Tasks**:
- [x] Create `CompanyController` following `FundController` pattern
- [x] Create `DashboardController` for dashboard endpoints
- [x] **Phase 2A: Entity & Banking Controllers** ✅ **COMPLETED**
  - [x] Create `EntityController` for entity management
  - [x] Create `BankingController` for bank and bank account management
  - [x] Create route files: `src/api/routes/entity.py` and `src/api/routes/banking.py`
  - [x] Convert all entity and banking endpoints to use controllers
  - [x] Remove old direct Flask routes from main API file
  - [x] Fix circular import issues by creating `src/api/database.py`
- [x] **Phase 2B: Tax & Fund Cleanup** ✅ **COMPLETED**
  - [x] Create `TaxController` for tax statement endpoints
  - [x] Create `src/api/routes/tax.py`
  - [x] Convert tax statement endpoints
  - [x] Remove duplicate fund endpoint from main API file
- [x] **Phase 2C: Integration & Testing** ✅ **COMPLETED**
  - [x] Register all new blueprints in `src/api/__init__.py`
  - [x] Remove all direct Flask routes from main API file
  - [x] Implement consistent error response format across all controllers
  - [x] Ensure all endpoints return proper HTTP status codes
**Success Criteria**:
- ✅ 100% of endpoints use controller pattern
- ✅ Consistent error response format (JSON with error message and status)
- ✅ All endpoints return proper HTTP status codes

### Phase 3: Middleware Implementation ✅ **IN PROGRESS**
**Goal**: Add enterprise-grade middleware for validation, error handling, and logging
**Design Principles**:
- Request validation happens before reaching controllers
- Centralized error handling with proper logging
- Input sanitization and type validation
- **Clean Break Approach**: Remove legacy methods, standardize on middleware-only architecture
**Progress**: Phase 3A, 3B, 3C, 3D, 3E, 3F, 3G, and DashboardController updates completed (100% complete) ✅
**Tasks**:
- [x] **Phase 3A: Request Validation Middleware** ✅ **COMPLETED**
  - [x] Create `src/api/middleware/validation.py` for request validation
  - [x] Implement JSON schema validation for request bodies
  - [x] Add type checking and sanitization
  - [x] Create custom validation decorators for routes
  - [x] Integrate validation middleware into banking routes
  - [x] Update BankingController to use middleware-only approach
- [ ] **Phase 3B: Centralized Error Handling** 🔄 **IN PROGRESS**
  - [x] Create `src/api/middleware/error_handling.py` for centralized error handling
  - [x] Implement global exception handlers for common errors
  - [x] Create custom exception classes for business logic
  - [x] Integrate error handlers into Flask app
  - [ ] Test error handling with various error scenarios
- [ ] **Phase 3C: Request/Response Logging** 🔄 **IN PROGRESS**
  - [x] Create `src/api/middleware/logging.py` for request/response logging
  - [x] Implement request/response logging with correlation IDs
  - [x] Add performance timing for endpoints
  - [x] Integrate logging middleware into Flask app
  - [ ] Test logging functionality and performance impact
- [ ] **Phase 3D: Middleware Integration** 🔄 **IN PROGRESS**
  - [x] Update `src/api/__init__.py` to register all middleware
  - [x] Implement before_request and after_request hooks
  - [x] Add error handlers to the Flask app
  - [ ] Ensure middleware doesn't break existing functionality
  - [ ] Test complete middleware stack
- [x] **Phase 3E: Controller Middleware Integration** ✅ **COMPLETED - CLEAN BREAK APPROACH**
  - [x] **TaxController Updates** (HIGH PRIORITY) ✅ **COMPLETED**
    - [x] Remove manual validation logic, replace with validation middleware
    - [x] Add `@validate_tax_statement_data` decorator to tax routes
    - [x] Update controller methods to accept pre-validated data only
    - [x] Remove legacy validation methods
  - [x] **EntityController Updates** (HIGH PRIORITY) ✅ **COMPLETED**
    - [x] Remove manual entity type validation, replace with middleware
    - [x] Add `@validate_entity_data` decorator to entity routes
    - [x] Update controller methods to accept pre-validated data only
    - [x] Remove legacy validation methods
  - [x] **FundController Updates** (MEDIUM PRIORITY) ✅ **COMPLETED**
    - [x] Remove manual fund validation, replace with middleware
    - [x] Add `@validate_fund_data` decorator to fund routes
    - [x] Update controller methods to accept pre-validated data only
    - [x] Remove legacy validation methods
  - [x] **DashboardController Updates** ✅ **COMPLETED**
    - [x] Controller methods already use clean architecture pattern
    - [x] No manual validation logic present (all GET endpoints)
    - [x] Proper error handling and domain delegation implemented
  - [x] **Phase 3F: Route Middleware Integration** ✅ **COMPLETED - CLEAN BREAK APPROACH**
    - [x] **Fund Routes** (MEDIUM PRIORITY) ✅ **COMPLETED**
      - [x] Added validation decorators to all POST endpoints
      - [x] Updated routes to use pre-validated data from controllers
      - [x] Removed fallback logic for legacy methods
    - [x] **Company Routes** (MEDIUM PRIORITY) ✅ **COMPLETED**
      - [x] Added validation decorators to all POST endpoints
      - [x] Updated routes to use pre-validated data from controllers
      - [x] Removed fallback logic for legacy methods
    - [x] **Entity Routes** (MEDIUM PRIORITY) ✅ **COMPLETED**
      - [x] Already using validation decorators
      - [x] Routes already use pre-validated data from controllers
      - [x] No fallback logic present
    - [x] **Tax Routes** (HIGH PRIORITY) ✅ **COMPLETED**
      - [x] Already using validation decorators
      - [x] Routes already use pre-validated data from controllers
      - [x] No fallback logic present
- [x] **Phase 3G: Legacy Code Cleanup** ✅ **COMPLETED - CLEAN BREAK APPROACH**
  - [x] Remove all legacy controller methods (e.g., `create_bank()`, `create_entity()`) ✅ **COMPLETED**
  - [x] Remove fallback logic in routes (`getattr(request, 'validated_data', request.get_json() or {})`) ✅ **COMPLETED**
  - [x] Standardize all endpoints to use middleware validation only ✅ **COMPLETED**
  - [x] Update all tests to use new validation patterns ✅ **COMPLETED**
  - [x] Remove duplicate validation logic from controllers ✅ **COMPLETED**

**Success Criteria**:
- All endpoints validate input before processing
- Consistent error logging with request context
- Zero unhandled exceptions reaching frontend
- **Clean Codebase**: No duplicate validation logic, no legacy methods
- **Standardized Architecture**: All endpoints use same middleware patterns

### Phase 4: API Contract Testing Implementation
**Goal**: Implement comprehensive API contract tests following the new streamlined test structure
**Design Principles**:
- Test all endpoint contracts, not business logic
- Validate request/response schemas and status codes
- Test error conditions and edge cases
- Focus on fund domain first, then expand to other domains
- Use new streamlined test structure for maintainability

#### **Phase 4A: Fund Domain Testing Foundation** 🔄 **IN PROGRESS**
**Goal**: Implement comprehensive fund domain API testing
**Priority**: HIGH - Fund domain is core business logic
**Tasks**:

**4A.1: Test Infrastructure Setup** (Week 1)
- [ ] Create `tests/api/` directory structure
- [ ] Create `tests/api/__init__.py`
- [ ] Create `tests/api/utils/` directory with test utilities
- [ ] Create `tests/api/utils/api_test_client.py` - Custom API test client
- [ ] Create `tests/api/utils/test_data_factories.py` - Fund test data generation
- [ ] Create `tests/api/utils/mock_services.py` - Service mocking utilities
- [ ] Create `tests/api/utils/assertions.py` - Custom assertions for API responses

**4A.2: Fund API Contracts Testing** (Week 1-2)
- [ ] Create `tests/api/contracts/` directory
- [ ] Create `tests/api/contracts/__init__.py`
- [ ] Create `tests/api/contracts/test_fund_contracts.py`
  - [ ] Test fund creation request/response schemas
  - [ ] Test fund update request/response schemas
  - [ ] Test fund event request/response schemas
  - [ ] Test fund calculation request/response schemas
  - [ ] Validate JSON schema compliance for all fund endpoints
  - [ ] Test required vs optional field validation

**4A.3: Fund Endpoints Testing** (Week 2-3)
- [ ] Create `tests/api/endpoints/` directory
- [ ] Create `tests/api/endpoints/__init__.py`
- [ ] Create `tests/api/endpoints/fund/` directory
- [ ] Create `tests/api/endpoints/fund/__init__.py`
- [ ] Create `tests/api/endpoints/fund/test_fund_operations.py`
  - [ ] Test GET `/api/funds` - List all funds
  - [ ] Test GET `/api/funds/<id>` - Get specific fund
  - [ ] Test POST `/api/funds` - Create new fund
  - [ ] Test PUT `/api/funds/<id>` - Update fund
  - [ ] Test DELETE `/api/funds/<id>` - Delete fund
  - [ ] Validate HTTP status codes for all operations
  - [ ] Test response format consistency
- [ ] Create `tests/api/endpoints/fund/test_fund_calculations.py`
  - [ ] Test POST `/api/funds/<id>/calculate` - Fund calculations
  - [ ] Test POST `/api/funds/<id>/calculate-equity` - Equity calculations
  - [ ] Test POST `/api/funds/<id>/calculate-nav` - NAV calculations
  - [ ] Test POST `/api/funds/<id>/calculate-irr` - IRR calculations
  - [ ] Validate calculation response schemas
  - [ ] Test calculation error handling
- [ ] Create `tests/api/endpoints/fund/test_fund_events.py`
  - [ ] Test POST `/api/funds/<id>/events` - Create fund events
  - [ ] Test GET `/api/funds/<id>/events` - List fund events
  - [ ] Test POST `/api/funds/<id>/events/capital-call` - Capital call events
  - [ ] Test POST `/api/funds/<id>/events/distribution` - Distribution events
  - [ ] Test POST `/api/funds/<id>/events/return-of-capital` - Return of capital
  - [ ] Validate event creation response schemas
  - [ ] Test event validation rules

**4A.4: Fund Integration Testing** (Week 3-4)
- [ ] Create `tests/api/integration/` directory
- [ ] Create `tests/api/integration/__init__.py`
- [ ] Create `tests/api/integration/test_fund_banking_integration.py`
  - [ ] Test fund creation with bank account integration
  - [ ] Test capital call workflow with banking operations
  - [ ] Test distribution workflow with banking operations
  - [ ] Validate cross-domain data consistency
- [ ] Create `tests/api/integration/test_fund_company_integration.py`
  - [ ] Test fund creation with investment company integration
  - [ ] Test fund-company relationship management
  - [ ] Validate company-fund data consistency
- [ ] Create `tests/api/integration/test_fund_tax_integration.py`
  - [ ] Test fund events with tax implications
  - [ ] Test tax calculation integration with fund operations
  - [ ] Validate tax-fund data consistency

**4A.5: Fund Middleware Testing** (Week 4)
- [ ] Create `tests/api/middleware/` directory
- [ ] Create `tests/api/middleware/__init__.py`
- [ ] Create `tests/api/middleware/test_validation.py`
  - [ ] Test fund data validation middleware
  - [ ] Test fund event validation middleware
  - [ ] Test fund calculation validation middleware
  - [ ] Validate middleware error responses
- [ ] Create `tests/api/middleware/test_error_handling.py`
  - [ ] Test fund endpoint error handling
  - [ ] Test validation error responses
  - [ ] Test business rule violation handling
- [ ] Create `tests/api/middleware/test_logging.py`
  - [ ] Test fund endpoint request/response logging
  - [ ] Test performance timing for fund operations
  - [ ] Test correlation ID tracking

**4A.6: Fund Performance Testing** (Week 4-5)
- [ ] Create `tests/api/performance/` directory
- [ ] Create `tests/api/performance/__init__.py`
- [ ] Create `tests/api/performance/test_response_times.py`
  - [ ] Test fund endpoint response times
  - [ ] Test fund calculation performance
  - [ ] Test fund event processing performance
  - [ ] Establish performance baselines
- [ ] Create `tests/api/performance/test_concurrent_requests.py`
  - [ ] Test concurrent fund operations
  - [ ] Test concurrent fund calculations
  - [ ] Test concurrent fund event processing

**4A.7: Fund Security Testing** (Week 5)
- [ ] Create `tests/api/security/` directory
- [ ] Create `tests/api/security/__init__.py`
- [ ] Create `tests/api/security/test_authentication.py`
  - [ ] Test fund endpoint authentication
  - [ ] Test unauthenticated access rejection
  - [ ] Test authentication token validation
- [ ] Create `tests/api/security/test_authorization.py`
  - [ ] Test fund endpoint authorization
  - [ ] Test role-based access control
  - [ ] Test permission validation
- [ ] Create `tests/api/security/test_input_validation.py`
  - [ ] Test fund data input sanitization
  - [ ] Test SQL injection prevention
  - [ ] Test XSS prevention

#### **Phase 4B: Fund Test Implementation Details**
**Implementation Strategy**:
- **Test Data Management**: Use factories to generate realistic fund test data
- **Mocking Strategy**: Mock external services to isolate API testing
- **Database Isolation**: Each test runs in isolated transaction
- **Response Validation**: Comprehensive response schema validation
- **Error Testing**: Test all error conditions and edge cases

**Test Coverage Requirements**:
- **100% Fund Endpoint Coverage**: All fund endpoints must have tests
- **Schema Validation**: All request/response schemas must be validated
- **Error Handling**: All error conditions must be tested
- **Integration Testing**: Cross-domain workflows must be validated
- **Performance Baseline**: Establish performance benchmarks

**Success Criteria for Phase 4A**:
- ✅ All fund API endpoints have comprehensive contract tests
- ✅ All fund request/response schemas are validated
- ✅ All fund error conditions are tested
- ✅ Fund integration tests cover cross-domain workflows
- ✅ Fund middleware tests validate validation and error handling
- ✅ Fund performance tests establish baselines
- ✅ Fund security tests validate authentication and authorization
- ✅ All fund tests pass consistently
- ✅ Test execution time under 30 seconds for fund test suite

#### **Phase 4C: Expansion to Other Domains** (Future)
**Next Domains to Implement**:
1. **Banking Domain**: Bank accounts, transactions, reconciliation
2. **Company Domain**: Investment companies, relationships, management
3. **Tax Domain**: Tax calculations, statements, reporting
4. **Entity Domain**: Entity management, investments, relationships

**Expansion Strategy**:
- Follow same testing patterns established in fund domain
- Reuse test utilities and infrastructure
- Maintain consistent test structure across all domains
- Prioritize based on business criticality

**Success Criteria**:
- 100% API endpoint coverage across all domains
- Consistent testing patterns across all domains
- All tests pass consistently
- API contracts documented through comprehensive test examples

## Overall Success Metrics
- **Maintainability**: API code split into focused modules under 200 lines each
- **Testability**: 100% API endpoint coverage with contract tests
- **Consistency**: All endpoints use same architectural pattern
- **Performance**: Zero regression in API response times
- **Quality**: Zero linting errors, 100% test pass rate

## Risk Mitigation
- **Breaking Changes**: Maintain exact endpoint URLs and response formats
- **Test Coverage**: Run existing tests after each phase to catch regressions
- **Frontend Impact**: Coordinate with frontend team to validate no breaking changes
- **Performance**: Monitor API response times during refactoring
