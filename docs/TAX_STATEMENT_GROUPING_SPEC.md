# Tax Statement Grouping Specification

## Overview
Currently, tax statements create multiple separate `TAX_PAYMENT` events that appear as individual rows in the fund events table. This specification defines a **backend-first grouping approach** to consolidate all tax events from the same tax statement into meaningful business entities, making it easier to see the complete tax picture for each financial year while maintaining the existing excellent cash flow visibility.

## Design Philosophy
- **Backend-first architecture**: Business logic and grouping rules owned by the backend, not presentation layer
- **Professional enterprise standards**: Follow separation of concerns with backend handling business logic, frontend handling presentation
- **Preserve cash flow clarity**: Maintain the current red/black color coding and positive/negative formatting
- **Show complete tax picture**: Display all tax components (interest, dividends, capital gains) plus the EOFY debt interest deduction benefit
- **Reduce table clutter**: Consolidate scattered tax events into meaningful groups
- **Maintain data integrity**: Grouping represents business logic, not just presentation

## Problems We're Solving
1. **Scattered tax events**: Multiple tax payment rows for the same financial year make it hard to see the complete tax situation
2. **Missing context**: Individual tax events don't show the relationship to the underlying tax statement
3. **EOFY debt benefit visibility**: The debt interest deduction benefit is hard to see in isolation
4. **Table clutter**: Too many tax-related rows reduce readability of the overall cash flow story
5. **Inconsistent grouping**: Frontend-only grouping could lead to different experiences across clients

## Implementation Strategy

### Phase 1: Backend Grouping Logic Foundation ✅ **UPDATED APPROACH**
**Goal**: Implement tax statement grouping at the backend level following enterprise architecture best practices
**Tasks**:
- [ ] Create `TaxStatementGroupingService` in backend to handle grouping business logic
- [ ] Extend existing event grouping system to identify tax events with the same `tax_statement_id`
- [ ] Create new `TaxStatementGroup` data structure in backend (not just frontend interface)
- [ ] Update API endpoints to return grouped tax events as structured business entities
- [ ] Ensure tax events without tax statements remain as individual events
**Design Principles**:
- **Backend owns business logic**: Grouping rules and business logic centralized in backend services
- **Single source of truth**: All clients receive consistent, pre-processed grouped data
- **Performance optimization**: Database-level grouping for efficiency and scalability
- **Business entity representation**: API returns meaningful business concepts, not raw data

### Phase 2: Frontend Data Structure & Interface Updates
**Goal**: Update frontend to consume backend-grouped tax events
**Tasks**:
- [ ] Update `ExtendedFundEvent` interface to include grouped tax statement data
- [ ] Create `TaxStatementGroup` interface that matches backend response structure
- [ ] Update `useEventGrouping` hook to handle backend-grouped tax events
- [ ] Ensure proper TypeScript typing for grouped tax statement responses
**Design Principles**:
- Frontend interfaces match backend data structures exactly
- No business logic in frontend - only presentation and user interaction
- Consistent with existing API consumption patterns

### Phase 3: Frontend Grouped Row Component
**Goal**: Create a new `TaxStatementRow` component to display backend-grouped tax events
**Tasks**:
- [ ] Create `TaxStatementRow` component following the pattern of existing `GroupedEventRow`
- [ ] Design the grouped row layout to show:
  - Main row with tax statement summary (financial year, total tax impact)
  - Expandable details showing individual tax components
  - Clear display of the EOFY debt interest deduction benefit
- [ ] Ensure proper styling consistency with existing grouped rows
- [ ] Implement expand/collapse functionality for tax details
**Design Principles**:
- Follow Material-UI design patterns for expandable rows
- Use consistent color coding (red for tax outflows, black for debt benefits)
- Show net tax impact prominently in the main row
- Display data exactly as received from backend (no frontend manipulation)

### Phase 4: Enhanced Tax Statement Display
**Goal**: Improve the information displayed in grouped tax statement rows
**Tasks**:
- [ ] Show comprehensive tax breakdown in the main row:
  - Financial year and statement date
  - Total tax payable (negative amount)
  - Net tax after debt benefits (if applicable)
- [ ] Display individual tax components in expandable details:
  - Interest tax with income amount and rate
  - Dividend tax (franked/unfranked) with amounts and rates
  - Capital gains tax with gain amounts and rates
  - EOFY debt interest deduction benefit (positive amount)
- [ ] Add visual indicators for tax statement completeness and status
**Design Principles**:
- Prioritize net tax impact visibility
- Show tax rates and income amounts for context
- Highlight the debt benefit as a positive cash flow
- All data sourced directly from backend grouping service

### Phase 5: Integration and Polish
**Goal**: Seamlessly integrate backend tax statement grouping with existing table functionality
**Tasks**:
- [ ] Update `TableBody` component to render `TaxStatementRow` for backend-grouped tax events
- [ ] Ensure proper event counting and filtering with grouped rows
- [ ] Test grouping behavior with various tax statement configurations
- [ ] Verify mobile responsiveness of grouped tax statement rows
- [ ] Add proper accessibility attributes for expandable rows
**Design Principles**:
- Maintain existing table performance and responsiveness
- Ensure grouped rows work properly with all existing filters
- Preserve accessibility standards for screen readers
- Backend grouping handles all business logic complexity

## Success Metrics
- **User Experience**: Users can see complete tax picture for each financial year in one place
- **Table Clarity**: Reduced number of tax-related rows improves overall table readability
- **Cash Flow Visibility**: Net tax impact and debt benefits are clearly visible
- **Performance**: Backend grouping maintains and improves table performance
- **Consistency**: Tax statement grouping follows enterprise architecture patterns
- **Scalability**: Backend grouping handles large datasets efficiently

## Technical Considerations
- **Backend Architecture**: Grouping service follows existing service layer patterns
- **Data Structure**: Backend returns grouped business entities, frontend consumes as-is
- **Performance**: Database-level grouping for efficiency and scalability
- **Filtering**: Grouped rows must work correctly with existing tax event filters
- **Mobile**: Expandable rows must work well on mobile devices
- **Accessibility**: Proper ARIA attributes for expandable functionality
- **API Design**: Clean, semantic responses representing business concepts

## Dependencies
- Existing backend service layer architecture
- Current `GroupedEventRow` component as reference implementation
- Tax statement data already available in database
- Existing table styling and Material-UI patterns
- Backend grouping service implementation

## Future Enhancements (Post-Implementation)
- **Tax Statement Summary**: Add summary row showing total tax impact across all funds
- **Cross-Fund Grouping**: Group tax events across multiple funds for the same entity/financial year
- **Tax Statement Status**: Visual indicators for draft, final, or amended tax statements
- **Export Integration**: Include grouped tax information in table exports
- **Caching Strategy**: Implement backend caching for grouped tax statement data
- **Real-time Updates**: WebSocket integration for live tax statement grouping updates

## Architecture Benefits of Backend-First Approach
- **Separation of Concerns**: Business logic centralized in backend, presentation in frontend
- **Single Source of Truth**: All clients receive consistent grouped data
- **Performance**: Database-level grouping more efficient than frontend processing
- **Maintainability**: Business rules in one place, easier to modify and extend
- **Scalability**: Backend grouping handles large datasets and multiple concurrent users
- **Professional Standards**: Follows enterprise-level architecture patterns
- **API Design**: Clean, semantic API responses representing business concepts
