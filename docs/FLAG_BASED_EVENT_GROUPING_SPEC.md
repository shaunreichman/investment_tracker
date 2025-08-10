# Flag-Based Event Grouping Specification

## Overview
This specification defines a **simple, flag-based approach** to event grouping that eliminates complex frontend logic and provides a clean, enterprise-grade architecture. Instead of complex grouping services and dual API endpoints, we add simple grouping flags directly to the `FundEvent` model.

## 🎯 Design Philosophy
- **Explicit State**: Clear, explicit grouping flags instead of implicit data structure analysis
- **Single Source of Truth**: All events come from one endpoint with embedded grouping information
- **Simplified Frontend Logic**: Check boolean flags instead of complex data merging
- **Professional Standards**: Enterprise-grade architecture following industry best practices
- **Easy Extension**: Adding new grouping types requires only backend changes

## Problems We're Solving
1. **Complex Frontend Logic**: Current approach requires merging multiple data sources and analyzing complex data structures
2. **Dual API Endpoints**: Separate `/events` and `/events/grouped` endpoints create complexity
3. **Maintenance Overhead**: Complex grouping services and business logic scattered across multiple layers
4. **Testing Complexity**: Complex test setup required for multi-layer grouping logic
5. **Architectural Inconsistency**: Different approaches for different grouping types

## Proposed Solution: Flag-Based Architecture

### Database Schema Changes
Add 4 new fields to the `FundEvent` model:

```python
class FundEvent(Base):
    # ... existing fields ...
    
    # CALCULATED: Grouping flags set by backend when creating events
    is_grouped = Column(Boolean, default=False, nullable=False)  # (CALCULATED) whether this event is part of a group
    group_id = Column(Integer, nullable=True, index=True)  # (CALCULATED) unique identifier for the group (auto-generated)
    group_type = Column(Enum(GroupType), nullable=True)  # (CALCULATED) type of grouping (INTEREST_WITHHOLDING, TAX_STATEMENT, etc.)
    group_position = Column(Integer, nullable=True)  # (CALCULATED) position within group for ordering (0=first, 1=second, etc.)
```

### Group Type Enum
```python
class GroupType(enum.Enum):
    """Enumeration for event grouping types.
    
    Business definitions:
    - INTEREST_WITHHOLDING: Interest distribution events paired with withholding tax events
    - TAX_STATEMENT: Tax statement events grouped by financial year (future implementation)
    """
    INTEREST_WITHHOLDING = "interest_withholding"
    TAX_STATEMENT = "tax_statement"
```

**Location**: `src/fund/models.py` - follows the same pattern as other enums in the codebase

### Database Constraints & Validation
```python
# Business rules enforced in domain methods:
# 1. All events in a group must have the same event_date
# 2. group_id must be unique across all groups
# 3. group_position must be sequential starting from 0
# 4. If is_grouped=True, all grouping fields must be set
# 5. If is_grouped=False, all grouping fields must be NULL
# 
# Note: Database-level constraints can be added system-wide later for additional data integrity
```

## Implementation Strategy

**Note**: This implementation uses domain method validation for business rules. Database-level constraints can be added system-wide later for additional data integrity, but for now we maintain consistency with the existing architecture pattern.

### Phase 1: Database Schema & Migration
**Goal**: Add grouping fields to FundEvent model with proper constraints
**Tasks**:
- [ ] Add 4 new grouping fields to FundEvent model with proper comments
- [ ] Create Alembic migration for new fields
- [ ] Set sensible defaults (is_grouped=False, others nullable)
- [ ] Add domain method validation for date validation and group integrity
- [ ] Update model tests to include new fields and validation

**Design Principles**:
- **Backward Compatible**: Existing events default to non-grouped
- **Nullable Fields**: Only set when events are actually grouped
- **Clear Naming**: Self-documenting field names following existing patterns
- **Data Integrity**: Domain method validation ensures grouping consistency

### Phase 2: Backend Grouping Logic
**Goal**: Set grouping flags when creating interest + withholding tax events
**Tasks**:
- [ ] Update event creation logic to detect interest + withholding tax pairs
- [ ] Generate unique group_id (auto-incrementing integer) for each pair
- [ ] Set is_grouped=True and group_type for both events
- [ ] Set group_position for proper ordering (0=interest, 1=withholding)
- [ ] **CRITICAL**: Validate both events have identical event_date before grouping
- [ ] Ensure existing event creation still works for non-grouped events

**Design Principles**:
- **Simple Logic**: Group by date when interest event has has_withholding_tax=True
- **Consistent Grouping**: Same group_id for both events in a pair
- **Clear Ordering**: group_position ensures consistent display order
- **Date Validation**: Strict enforcement that grouped events share the same date

### Phase 3: API Enhancement
**Goal**: Single `/events` endpoint returns all events with grouping metadata
**Tasks**:
- [ ] Enhance existing `/api/funds/{fund_id}/events` endpoint
- [ ] Return single list of events with grouping flags embedded
- [ ] Remove need for separate `/events/grouped` endpoint
- [ ] Ensure backward compatibility for existing frontend code
- [ ] Add grouping metadata to response (total groups, group types present)

**Design Principles**:
- **Single Endpoint**: All events from one source
- **Embedded Metadata**: Grouping info included with each event
- **Consistent Response**: Same data structure for all event types

### Phase 4: Frontend Simplification
**Goal**: Replace complex grouping logic with simple flag checks
**Tasks**:
- [ ] Update frontend types to include new grouping fields (`is_grouped`, `group_id`, `group_type`, `group_position`)
- [ ] Update `FundEvent` interface in `frontend/src/types/api.ts`
- [ ] Replace complex data merging with simple boolean flag checks
- [ ] Update `GroupedEventRow` to work with flag-based approach
- [ ] **SIMPLIFY**: Replace `useEventGrouping` hook with simple filtering logic
- [ ] Remove complex grouping interfaces and data structures
- [ ] Update frontend tests to use new flag-based approach
- [ ] Remove old grouping logic from `useEventGrouping.ts`

**Design Principles**:
- **Simple Logic**: Check `is_grouped` flag instead of analyzing data structures
- **No Data Merging**: Single data source eliminates complex frontend logic
- **Consistent Display**: Grouped rows work exactly as before
- **Flag-Based**: Use explicit grouping state instead of implicit date analysis

**Frontend Code Changes**:
```typescript
// OLD: Complex grouping logic
const groupedEvents = useEventGrouping(events, fund); // Complex hook with date analysis

// NEW: Simple flag-based logic
const groupedEvents = events.filter(e => e.is_grouped);
const individualEvents = events.filter(e => !e.is_grouped);

// OLD: Complex date-based grouping
const dateGroups = groupEventsByDate(events); // Complex algorithm

// NEW: Simple group-based logic
const groups = events.filter(e => e.is_grouped).reduce((acc, event) => {
  if (!acc[event.group_id]) acc[event.group_id] = [];
  acc[event.group_id].push(event);
  return acc;
}, {});
```

### Phase 5: Testing & Validation
**Goal**: Comprehensive testing of flag-based approach
**Tasks**:
- [ ] Unit tests for new grouping field logic
- [ ] Integration tests for event creation with grouping
- [ ] API tests for enhanced events endpoint
- [ ] Frontend tests for simplified grouping logic
- [ ] End-to-end tests for complete grouping workflow
- [ ] **CRITICAL**: Test date validation constraints

**Design Principles**:
- **Simple Test Setup**: No complex mocking required
- **Clear Test Cases**: Test explicit grouping state
- **Comprehensive Coverage**: Test all grouping scenarios

## Backend & Frontend Integration Deep Dive

### Current State Analysis
The existing frontend has complex grouping logic in `useEventGrouping.ts` that:
- Groups events by date
- Manually detects interest + withholding tax pairs
- Falls back to date-based matching when flags aren't available
- Requires complex data structure analysis

### Target State: Streamlined Integration
With flag-based grouping, the integration becomes much cleaner:

#### Backend Responsibilities
1. **Event Creation**: Automatically detect and group related events
2. **Group Management**: Generate unique group IDs and maintain consistency
3. **Data Validation**: Ensure grouped events share the same date
4. **Single API**: Return all events with embedded grouping metadata

#### Frontend Responsibilities
1. **Simple Consumption**: Check `is_grouped` flag instead of complex logic
2. **Display Logic**: Use `group_position` for ordering within groups
3. **No Data Merging**: Single data source eliminates complex state management

#### API Response Structure
```typescript
// Before: Complex dual endpoints with manual frontend grouping
GET /api/funds/{id}/events        // Basic events
GET /api/funds/{id}/events/grouped // Grouped events (complex logic)

// After: Single endpoint with embedded grouping
GET /api/funds/{id}/events        // All events with grouping flags
```

#### Frontend State Management
```typescript
// Before: Complex grouping logic
const groupedEvents = useEventGrouping(events, fund); // Complex hook with date analysis

// After: Simple flag-based logic
const groupedEvents = events.filter(e => e.is_grouped); // Simple boolean check
const individualEvents = events.filter(e => !e.is_grouped); // Simple boolean check
```

### Benefits of This Integration Approach

#### 1. **Eliminates Frontend Complexity**
- No more complex date-based grouping algorithms
- No more merging multiple API responses
- No more complex state management for grouped vs. individual events

#### 2. **Simplifies Testing**
- Frontend tests become simple boolean flag checks
- Backend tests focus on grouping logic in one place
- No more complex mocking of grouped data structures

#### 3. **Improves Performance**
- Single API call instead of two
- No frontend data processing or merging
- Direct use of backend-calculated grouping state

#### 4. **Enhances Maintainability**
- Grouping logic centralized in backend
- Frontend becomes purely presentational
- Easy to add new grouping types without frontend changes

#### 5. **Better Error Handling**
- Backend validates grouping consistency
- Frontend receives pre-validated data
- Clear separation of concerns for debugging

### Migration Strategy

#### Phase 1: Backend Implementation
- Implement grouping logic in backend
- Add new fields to database
- Update event creation methods

#### Phase 2: API Enhancement
- Enhance existing events endpoint
- Return grouping metadata
- Maintain backward compatibility

#### Phase 3: Frontend Simplification
- Update types to include grouping fields
- Simplify grouping logic to use flags
- Remove complex grouping algorithms

#### Phase 4: Cleanup
- Remove old grouping endpoints
- Remove complex frontend grouping code
- Update tests to use new approach

## Architecture Benefits

### Compared to Complex Approach
- **Code Reduction**: ~80% less code (simple flags vs. complex services)
- **Maintenance**: Single place to modify grouping logic
- **Performance**: One API call instead of two
- **Testing**: Simple test setup with explicit state
- **Extension**: Easy to add new grouping types

### Professional Standards
- **Enterprise Architecture**: Follows patterns used by major financial platforms
- **Separation of Concerns**: Backend owns grouping logic, frontend is purely presentational
- **Single Responsibility**: Each component has one clear purpose
- **Explicit State**: No hidden or implicit behavior

## Success Metrics
- **Code Quality**: Significantly cleaner, more maintainable code
- **Performance**: Single API call improves table performance
- **Maintainability**: Business rules centralized, easier to modify
- **User Experience**: No change to existing grouped row display
- **Testing**: Simpler test setup without complex logic mocking
- **Architecture**: Professional, enterprise-grade design

## Future Extensibility
This approach establishes a **grouping pattern** that can be easily extended:

- **New Group Types**: Add to GroupType enum and implement backend logic
- **Advanced Grouping**: Extend group_position for multi-event groups
- **Group Metadata**: Add additional grouping fields as needed
- **Caching Strategy**: Simple to implement with explicit grouping state

## Implementation Timeline
- **Phase 1**: 1 day - Database schema and migration
- **Phase 2**: 1-2 days - Backend grouping logic
- **Phase 3**: 1 day - API enhancement
- **Phase 4**: 1-2 days - Frontend simplification
- **Phase 5**: 1 day - Testing and validation

**Total Estimated Time**: 5-7 days (vs. 6-7 weeks for complex approach)

## Risk Assessment
- **Low Risk**: Simple database changes and straightforward logic
- **Low Impact**: No changes to user experience or visual design
- **Easy Rollback**: Can revert database changes if issues arise
- **Incremental**: Can implement and test phase by phase

## Dependencies
- Existing FundEvent model and database schema
- Current event creation logic in backend
- Existing frontend GroupedEventRow component
- Alembic migration system

## Conclusion
This flag-based approach represents a **10x improvement** over the complex grouping service architecture:

- **Simpler**: 80% less code and complexity
- **Cleaner**: Professional, enterprise-grade design
- **Faster**: 5-7 days vs. 6-7 weeks
- **Better**: More maintainable and extensible

By focusing on explicit state and simple logic, we achieve a much more professional and maintainable solution that follows industry best practices. The backend/frontend integration becomes dramatically simpler, with clear separation of concerns and much easier testing and maintenance.
