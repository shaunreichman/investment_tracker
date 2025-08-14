# Enhanced Search Bar Specification

## Overview
Transform the current static search bar into an intelligent, expandable global search experience that enables users to quickly find and navigate to companies and funds.

## Design Philosophy
- **Efficiency First**: Minimize clicks and keystrokes to find entities
- **Progressive Disclosure**: Start simple, expand on interaction  
- **Keyboard Navigation**: Full keyboard support for power users
- **Visual Hierarchy**: Clear distinction between search states

## Implementation Strategy

### Phase 1: Core Expansion Foundation
**Goal**: Create expandable search modal with basic functionality
**Design Principles**:
- Use existing TopBar search bar as trigger point
- Implement modal system that centers and expands smoothly
- Maintain current search bar styling and positioning
**Tasks**:
- [ ] Create expandable search modal component
- [ ] Implement smooth expand animation from TopBar position
- [ ] Add backdrop and focus management
- [ ] Create large search input field with proper styling
- [ ] Implement basic open/close state management
**Success Criteria**:
- Search modal expands smoothly from TopBar position
- Modal centers on screen with proper backdrop
- Search input receives focus automatically
- ESC key closes modal and returns focus to TopBar

### Phase 2: Search Logic & Results
**Goal**: Implement real-time search functionality with result display
**Design Principles**:
- Use existing company and fund data APIs
- Implement debounced search to prevent excessive API calls
- Follow existing data structure patterns from useInvestmentCompanies hook
**Tasks**:
- [ ] Integrate with company search API endpoint
- [ ] Integrate with fund search API endpoint  
- [ ] Implement debounced search (300ms delay)
- [ ] Create search results list component
- [ ] Add loading states and error handling
- [ ] Implement basic result filtering and display
**Success Criteria**:
- Search results appear within 2 seconds of typing
- Results show company/fund names with relevant metadata
- Loading states provide clear feedback during search
- Error states handle API failures gracefully

### Phase 3: Enhanced User Experience
**Goal**: Add keyboard navigation and suggested content
**Design Principles**:
- Implement full keyboard navigation following accessibility standards
- Use hardcoded suggestions initially (3PG, Senior Debt Fund)
- Ensure mobile responsiveness from the start
**Tasks**:
- [ ] Add keyboard navigation (arrow keys, enter, escape)
- [ ] Implement suggested content section for empty state
- [ ] Create navigation help bar with keyboard shortcuts
- [ ] Add result selection and highlighting
- [ ] Implement enter key to open selected result
- [ ] Ensure mobile touch navigation works properly
**Success Criteria**:
- All keyboard shortcuts work as specified
- Suggested content displays when search is empty
- Navigation help bar shows proper instructions
- Mobile users can navigate results with touch

### Phase 4: Polish & Performance
**Goal**: Optimize animations, performance, and accessibility
**Design Principles**:
- Use CSS transitions for smooth animations
- Implement result caching to improve performance
- Follow WCAG accessibility guidelines for keyboard navigation
**Tasks**:
- [ ] Optimize expand/collapse animations
- [ ] Implement search result caching
- [ ] Add keyboard navigation accessibility improvements
- [ ] Optimize re-renders and component performance
- [ ] Add comprehensive keyboard navigation testing
- [ ] Ensure proper focus management and screen reader support
**Success Criteria**:
- Animations run at 60fps without jank
- Search results cache improves subsequent search speed
- All keyboard navigation passes accessibility testing
- Zero console errors during search operations

## Overall Success Metrics
- **Search Time**: < 2 seconds to find any entity
- **Navigation Efficiency**: 80% of users use keyboard shortcuts
- **User Satisfaction**: Search feature usage increases by 40%
- **Performance**: Search modal opens/closes in < 200ms
- **Accessibility**: 100% keyboard navigation coverage

## Dependencies
- Existing TopBar search bar component
- Company and fund data APIs (useInvestmentCompanies, useFunds)
- Modal/dialog component system
- Keyboard event handling utilities
- Existing theme system for consistent styling

## Directory Structure & File Organization

### New Search Component Directory
```
frontend/src/components/search/
├── EnhancedSearchModal.tsx          # Main search modal component
├── SearchInput.tsx                  # Search input field with styling
├── SearchResults.tsx                # Results list component
├── SearchResultItem.tsx             # Individual result item (company/fund)
├── SuggestedContent.tsx             # Suggested content section (3PG, Senior Debt Fund)
├── NavigationHelpBar.tsx            # Keyboard shortcuts help bar
├── index.ts                         # Export all components
└── types/
    └── search.types.ts              # Search-related type definitions
```

### Component Responsibilities
- **EnhancedSearchModal**: Main container, state management, backdrop
- **SearchInput**: Search field, input handling, clear button
- **SearchResults**: Results list, loading states, empty states
- **SearchResultItem**: Individual result display, click handling
- **SuggestedContent**: Hardcoded suggestions for empty state
- **NavigationHelpBar**: Keyboard shortcuts instructions

### Integration Points
- **TopBar**: Remains as trigger, imports search modal
- **Layout**: Search modal renders at app root level (not inside TopBar)
- **Theme**: Uses existing theme system for consistent styling
- **APIs**: Integrates with existing useInvestmentCompanies and useFunds hooks

## Notes
- Start with hardcoded suggestions (3PG, Senior Debt Fund) as specified
- Focus on core functionality before advanced features
- Ensure mobile responsiveness from the start
- Consider future integration with other searchable entities
