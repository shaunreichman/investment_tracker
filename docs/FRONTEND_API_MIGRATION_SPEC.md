# Frontend API Migration Specification

## Overview
Migrate frontend code to work with the refactored backend API architecture. The backend has moved from a monolithic API structure to a modular blueprint-based system with controllers, DTOs, and standardized response formats.

## Design Philosophy
- **Complete Migration**: Move entirely to new API structure, no backward compatibility
- **Clean Break**: Update all frontend code to use new endpoints and response formats
- **Modern API Patterns**: Leverage new DTOs, controllers, and enhanced features
- **Performance First**: Use new pagination, filtering, and optimization capabilities

## Implementation Strategy

### Phase 1: API Response Format Migration
**Goal**: Update frontend to handle new DTO response format and error handling
**Design Principles**:
- All API calls must use new `{success: boolean, data: any}` response format
- Error handling must use new structured error format
- No fallback to old formats - complete migration only
**Tasks**:
- [x] Update API client base request method for new response format
- [x] Implement DTO response extraction across all API methods
- [x] Update error handling for new structured error format
- [x] Remove any old response format handling code
**Success Criteria**:
- All API calls properly extract data from DTO wrappers
- Error handling uses new structured format consistently
- No references to old response formats remain

### Phase 2: Endpoint Compatibility Verification
**Goal**: Verify all existing endpoints work with new backend structure
**Design Principles**:
- Test each endpoint category systematically
- Identify any URL or parameter changes
- Maintain existing frontend behavior
**Tasks**:
- [ ] Test fund API endpoints (`/api/funds/*`)
- [ ] Test company API endpoints (`/api/companies/*`, `/api/investment-companies`)
- [ ] Test entity API endpoints (`/api/entities`)
- [ ] Test dashboard API endpoints (`/api/dashboard/*`)
- [ ] Test tax statement endpoints (`/api/funds/*/tax-statements`)
**Success Criteria**:
- 100% of existing endpoints return expected data
- No 404 or routing errors
- Response data structure matches frontend expectations

### Phase 3: Enhanced API Features
**Goal**: Leverage new backend capabilities for improved user experience
**Design Principles**:
- Add new features incrementally
- Maintain backward compatibility
- Use new pagination and filtering where beneficial
**Tasks**:
- [ ] Implement pagination for list endpoints (companies, funds)
- [ ] Add enhanced filtering options for fund lists
- [ ] Update company overview to use enhanced endpoints
- [ ] Add banking API integration (if needed by frontend)
**Success Criteria**:
- List endpoints support pagination with configurable page sizes
- Enhanced filtering improves user experience
- New features don't break existing functionality

### Phase 4: Performance & Testing
**Goal**: Optimize performance and ensure comprehensive test coverage
**Design Principles**:
- All new API features must have test coverage
- Performance improvements must be measurable
- Error scenarios must be properly tested
**Tasks**:
- [ ] Update API service tests for new response formats
- [ ] Add integration tests for enhanced endpoints
- [ ] Performance test pagination and filtering
- [ ] Test error handling for all new scenarios
**Success Criteria**:
- 100% test coverage for API service methods
- Pagination responses under 200ms
- All error scenarios properly handled and tested

## Overall Success Metrics
- **Zero Breaking Changes**: All existing frontend functionality preserved
- **100% Endpoint Compatibility**: Every old endpoint works with new backend
- **Enhanced User Experience**: New features improve usability without regression
- **Comprehensive Testing**: Full test coverage for all API interactions
- **Performance Maintained**: No degradation in API response times

## Risk Mitigation
- **Legacy API Reference**: `src/api_legacy.py` preserved for comparison
- **Incremental Deployment**: Each phase can be deployed independently
- **Rollback Plan**: Frontend can revert to old API format if needed
- **Comprehensive Testing**: Each phase thoroughly tested before proceeding
