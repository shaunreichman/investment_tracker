# Persistent TopBar Navigation Specification

## Overview
Implement persistent TopBar navigation that remains visible during page transitions, eliminating the current issue where the TopBar disappears when navigating between companies and funds.

## Design Philosophy
- **Persistent Navigation**: Top-level navigation should remain accessible during all user interactions
- **Professional UX**: Follow modern SPA patterns used by enterprise applications
- **Consistent Layout**: Maintain visual stability during route transitions

## Implementation Strategy

### Phase 1: Layout Restructuring
**Goal**: Move TopBar from individual pages to persistent layout structure
**Design Principles**:
- TopBar becomes part of RouteLayout, not individual page components
- Use React Router hooks for dynamic page context and breadcrumbs
- Maintain existing TopBar styling and functionality
**Tasks**:
- [ ] Refactor RouteLayout.tsx to include persistent TopBar
- [ ] Update TopBar.tsx to be route-aware using useLocation and useParams
- [ ] Remove TopBar imports and instances from OverallDashboard, EnhancedCompaniesPage, and FundDetail
- [ ] Update TopBar positioning to account for new layout structure
**Success Criteria**:
- TopBar remains visible during all page transitions
- Zero console errors after refactoring
- All existing TopBar functionality preserved

### Phase 2: Dynamic Context Integration
**Goal**: Make TopBar dynamically display correct page title and breadcrumbs
**Design Principles**:
- TopBar automatically detects current route and updates content
- Breadcrumbs remain functional for navigation
- Page titles update without manual prop passing
**Tasks**:
- [ ] Implement route-based page title detection in TopBar
- [ ] Add dynamic breadcrumb generation based on current route
- [ ] Ensure breadcrumb navigation works correctly
- [ ] Test navigation between all routes (/, /companies/:id, /funds/:id)
**Success Criteria**:
- TopBar displays correct page title for each route
- Breadcrumbs update automatically and remain clickable
- Navigation between all routes works seamlessly

### Phase 3: Loading State Integration
**Goal**: Add loading indicators while preserving TopBar visibility
**Design Principles**:
- Loading states appear in content area, not in TopBar
- TopBar remains fully functional during data loading
- Use existing LoadingSpinner component for consistency
**Tasks**:
- [ ] Add loading states to content areas of each page
- [ ] Ensure TopBar remains interactive during loading
- [ ] Test loading states across all major user flows
**Success Criteria**:
- TopBar remains visible and functional during all loading states
- Loading indicators appear in appropriate content areas
- User can navigate to other pages while current page loads

## Overall Success Metrics
- TopBar remains visible during 100% of page transitions
- Zero TopBar flickering or disappearance during navigation
- All existing TopBar functionality preserved and enhanced
- Navigation performance remains under 200ms for route changes
