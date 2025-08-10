# Interest + Withholding Tax Grouping Specification

## Overview
Currently, interest distribution events with withholding tax are grouped on the frontend using complex date-based matching algorithms in the `useEventGrouping` hook. This specification defines a **backend-first approach** to move this grouping logic to the backend, simplifying frontend code and improving performance while maintaining the existing user experience.

## Design Philosophy
- **Backend-first architecture**: Business logic and grouping rules owned by the backend, not presentation layer
- **Professional enterprise standards**: Follow separation of concerns with backend handling business logic, frontend handling presentation
- **Quick win approach**: Simple, low-risk implementation that improves code quality
- **Preserve existing UX**: Maintain current grouped row display and expandable functionality
- **Consistent with tax statement grouping**: Follow same architectural patterns for future consistency

## Problems We're Solving
1. **Complex frontend logic**: Current `useEventGrouping` hook uses intricate date-based matching algorithms (lines 60-120)
2. **Maintenance complexity**: Frontend grouping logic mixed with presentation concerns
3. **Performance overhead**: Frontend processes and groups events that could be grouped at database level
4. **Inconsistent architecture**: Some grouping in frontend, some in backend
5. **Testing complexity**: Frontend grouping logic requires complex test setup and mocking

## Implementation Strategy

### Phase 1: Backend Grouping Logic Foundation
**Goal**: Implement interest + withholding tax grouping at the backend level
**Tasks**:
- [ ] Create `InterestWithholdingGroupingService` in backend to handle grouping business logic
- [ ] Use existing `has_withholding_tax` flag to identify interest events that need grouping
- [ ] Group interest distribution events with their corresponding withholding tax events by date
- [ ] Create `InterestWithholdingGroup` data structure in backend
- [ ] Update API endpoints to return grouped interest + withholding tax events
- [ ] Ensure individual events without grouping remain as individual events
**Design Principles**:
- **Backend owns business logic**: Grouping rules centralized in backend services
- **Simple grouping logic**: Group by date when interest event has `has_withholding_tax = true`
- **Performance optimization**: Database-level grouping for efficiency
- **Business entity representation**: API returns meaningful grouped data

### Phase 2: Frontend Data Structure & Interface Updates
**Goal**: Update frontend to consume backend-grouped interest + withholding tax events
**Tasks**:
- [ ] Create `InterestWithholdingGroup` interface that matches backend response structure
- [ ] Update `useEventGrouping` hook to handle backend-grouped events
- [ ] Remove complex frontend grouping logic for interest + withholding tax
- [ ] Ensure proper TypeScript typing for grouped responses
**Design Principles**:
- Frontend interfaces match backend data structures exactly
- No business logic in frontend - only presentation and user interaction
- Consistent with existing API consumption patterns
- Clean, maintainable frontend code

### Phase 3: Frontend Row Component Updates
**Goal**: Update existing `GroupedEventRow` to work with backend-grouped data
**Tasks**:
- [ ] Ensure `GroupedEventRow` component works with new backend data structure
- [ ] Verify expandable functionality works correctly
- [ ] Test styling consistency with existing grouped rows
- [ ] Update any hardcoded logic that assumes frontend grouping
**Design Principles**:
- Maintain existing visual design and user experience
- No changes to expandable row behavior
- Consistent with current `GroupedEventRow` patterns

### Phase 4: Integration and Testing
**Goal**: Seamlessly integrate backend grouping with existing table functionality
**Tasks**:
- [ ] Update `TableBody` component to handle backend-grouped interest + withholding tax events
- [ ] Ensure proper event counting and filtering with grouped rows
- [ ] Test grouping behavior with various interest + withholding tax configurations
- [ ] Verify mobile responsiveness of grouped rows
- [ ] Update tests to reflect new backend grouping approach
**Design Principles**:
- Maintain existing table performance and responsiveness
- Ensure grouped rows work properly with all existing filters
- Preserve accessibility standards for screen readers
- Backend grouping handles all business logic complexity

## Success Metrics
- **Code Quality**: Frontend becomes cleaner and more maintainable
- **Performance**: Backend grouping improves table performance
- **Consistency**: Interest grouping follows enterprise architecture patterns
- **Maintainability**: Business rules in one place, easier to modify
- **User Experience**: No change to existing grouped row display
- **Testing**: Simpler test setup without complex frontend logic mocking

## Technical Considerations
- **Backend Architecture**: Grouping service follows existing service layer patterns
- **Data Structure**: Backend returns grouped business entities, frontend consumes as-is
- **Performance**: Database-level grouping for efficiency
- **Filtering**: Grouped rows must work correctly with existing filters
- **Mobile**: Expandable rows must work well on mobile devices
- **Accessibility**: Maintain existing ARIA attributes and screen reader support
- **API Design**: Clean, semantic responses representing business concepts

## Dependencies
- Existing backend service layer architecture
- Current `GroupedEventRow` component as reference implementation
- Existing `has_withholding_tax` flag in `FundEvent` model
- Existing table styling and Material-UI patterns
- Backend grouping service implementation

## Future Enhancements (Post-Implementation)
- **Consistent Architecture**: Use same patterns for tax statement grouping
- **Advanced Grouping**: Additional grouping rules for other event types
- **Caching Strategy**: Implement backend caching for grouped data
- **Real-time Updates**: WebSocket integration for live grouping updates

## Architecture Benefits of Backend-First Approach
- **Separation of Concerns**: Business logic centralized in backend, presentation in frontend
- **Single Source of Truth**: All clients receive consistent grouped data
- **Performance**: Database-level grouping more efficient than frontend processing
- **Maintainability**: Business rules in one place, easier to modify and extend
- **Professional Standards**: Follows enterprise-level architecture patterns
- **Code Quality**: Frontend becomes purely presentational, no complex business logic
- **Consistency**: Follows same architectural pattern as future tax statement grouping

## Implementation Timeline
- **Phase 1**: 1-2 sprints (backend service and API updates)
- **Phase 2**: 1 sprint (frontend interface updates)
- **Phase 3**: 1 sprint (row component updates)
- **Phase 4**: 1 sprint (integration and testing)

**Total Estimated Time**: 4-5 sprints

## Risk Assessment
- **Low Risk**: Simple grouping logic, existing flag already available
- **Low Impact**: No changes to user experience or visual design
- **Easy Rollback**: Can revert to frontend grouping if issues arise
- **Incremental**: Can be implemented and tested independently
