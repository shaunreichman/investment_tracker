# TanStack Table Migration Specification

## Overview

Migrate from Material-UI (MUI) table components to TanStack Table (React Table v8) across the investment tracker application. This migration will enhance table performance, add advanced features, and establish consistent table patterns while preserving existing functionality and styling.

**Note: Tests will be ignored during this migration phase. We'll address test coverage and testing infrastructure at a later date to focus on core functionality and user experience.**

## Design Philosophy

### Core Principles
1. **Preserve Existing Functionality**: All current table features must work identically after migration
2. **Performance First**: Optimize for large datasets and smooth interactions
3. **Design System Consistency**: Maintain existing MUI styling and theme integration
4. **Incremental Migration**: Migrate one table at a time to minimize risk
5. **Backward Compatibility**: Ensure existing props and interfaces remain valid

### Problems We're Solving
- **Performance Issues**: Current MUI tables don't handle large datasets efficiently
- **Feature Limitations**: Missing advanced features like column resizing, reordering, and virtual scrolling
- **Inconsistent Patterns**: Different table implementations across the application
- **Maintenance Overhead**: Custom sorting, filtering, and pagination logic duplicated across components

### Success Criteria
- All existing table functionality preserved and working identically
- Performance improved or maintained for large datasets
- New features enhance user experience without disruption
- Accessibility compliance maintained or improved
- Code maintainability and reusability significantly enhanced

## Current State Analysis

### Existing Table Implementations

#### 1. **Fund Detail Table** (`frontend/src/components/fund/detail/table/`)
- **Complexity**: High - Custom event grouping with business logic
- **Features**: Event grouping, filtering, custom row rendering
- **Lines of Code**: ~400 lines across multiple components
- **Key Components**: `TableContainer`, `TableBody`, `EventRow`, `GroupedEventRow`

#### 2. **Companies Tab Funds Table** (`frontend/src/components/companies/funds-tab/`)
- **Complexity**: High - 22 columns with complex financial data
- **Features**: 22 columns (fund details, equity, distributions, returns, performance), single-column sorting, pagination, responsive design, status chips, tracking chips, navigation to fund details
- **Lines of Code**: ~100 lines
- **Key Components**: `FundsTable`, `FundsPagination`, `FundRow`

#### 3. **Companies Table** (`frontend/src/components/CompaniesPage.tsx`)
- **Complexity**: Low - Simple data display
- **Features**: Basic table with navigation links
- **Lines of Code**: ~50 lines
- **Key Components**: Inline table implementation

#### 4. **Overall Dashboard Table** (`frontend/src/components/OverallDashboard.tsx`)
- **Complexity**: Low - Company overview display
- **Features**: Basic table with status indicators
- **Lines of Code**: ~60 lines
- **Key Components**: Inline table implementation

#### 5. **Fund Detail Table** (`frontend/src/components/fund/detail/table/`)
- **Complexity**: Very High - Complex event grouping with business logic
- **Features**: Event grouping (interest + withholding, tax statements), flag-based grouping system, event filtering, grouped row rendering, expandable functionality, event management (add/delete)
- **Lines of Code**: ~400+ lines across multiple components
- **Key Components**: `TableContainer`, `TableBody`, `EventRow`, `GroupedEventRow`, `useEventGrouping`

### Current Technology Stack
- **UI Framework**: Material-UI (MUI) v7.2.0
- **Table Components**: MUI Table, TableHead, TableBody, TableRow, TableCell
- **State Management**: React hooks + Zustand store
- **Styling**: MUI sx prop + Emotion
- **TypeScript**: v4.9.5

## Implementation Strategy

### Phase 1: Foundation & Dependencies (Week 1)
**Goal**: Establish core TanStack Table infrastructure and design system integration

**Tasks**:
- [ ] **Install Dependencies**: Add TanStack Table and TypeScript types
- [ ] **Create Core Infrastructure**: Build base table hook and utility functions
- [ ] **Design System Integration**: Create reusable table components that maintain MUI styling
- [ ] **Type Definitions**: Establish comprehensive table type system
- [ ] **Base Components**: Implement Table, TableHeader, TableBody, and TablePagination

**Design Principles**:
- Base components must be completely reusable across all table types
- Maintain existing MUI styling and responsive behavior
- Establish clear separation between table logic and presentation
- Type safety must be comprehensive and intuitive

### Phase 2: Simple Tables Migration (Week 2)
**Goal**: Migrate low-complexity tables to establish patterns and validate approach

**Table Inventory & Migration Order:**

#### 2.1 Companies Table Migration
- **File**: `frontend/src/components/CompaniesPage.tsx`
- **Current Features**: Basic table with navigation links
- **Lines of Code**: ~50 lines
- **New Features**: 
  - Sortable columns (name, description)
  - Global search across all columns
  - Pagination (25 items per page)
  - Maintain existing navigation functionality
- **Validation Criteria**: 
  - Navigation links work correctly
  - Sorting works for all sortable columns
  - Global search finds results across all columns
  - Pagination displays correct number of items
  - All existing styling preserved exactly
- **Risk Level**: Low (simplest table, lowest risk)

**Tasks**:
- [ ] Replace inline MUI table with TanStack Table component
- [ ] Implement sortable columns (name, description)
- [ ] Add global search across all columns
- [ ] Implement pagination (25 items per page)
- [ ] Preserve all existing navigation functionality
- [ ] Verify styling preservation
- [ ] Test all validation criteria

#### 2.2 Overall Dashboard Table Migration  
- **File**: `frontend/src/components/OverallDashboard.tsx`
- **Current Features**: Company overview with status indicators
- **Lines of Code**: ~60 lines
- **New Features**:
  - Sortable columns (name, status)
  - Responsive column hiding on small screens
  - Maintain status indicators and styling
- **Validation Criteria**: 
  - Status indicators display correctly
  - Responsive behavior works on different screen sizes
  - Sorting works for name and status columns
  - All existing styling preserved exactly
- **Risk Level**: Low (similar complexity to Companies table)

**Tasks**:
- [ ] Replace inline MUI table with TanStack Table component
- [ ] Implement sortable columns (name, status)
- [ ] Add responsive column hiding on small screens
- [ ] Preserve all status indicators and styling
- [ ] Test responsive behavior across screen sizes
- [ ] Verify styling preservation
- [ ] Test all validation criteria

#### 2.3 Companies Tab Funds Table Migration
- **File**: `frontend/src/components/companies/funds-tab/components/FundsTable.tsx`
- **Current Features**: 
  - 22 columns with complex financial data (fund details, equity, distributions, returns, performance)
  - Single-column sorting (click headers)
  - Hover effects and navigation to fund details
  - Status chips and tracking type chips
  - Responsive design with proper formatting
- **Lines of Code**: ~100 lines
- **New Features**:
  - Multi-column sorting (name, status, creation date, performance metrics)
  - Column resizing and reordering
  - Enhanced filtering options (status, fund type, currency)
  - Column visibility toggles (handle 22 columns efficiently)
  - Maintain existing pagination component
  - Preserve all existing chips and financial formatting
- **Validation Criteria**: 
  - All 22 columns display correctly with proper formatting
  - Multi-column sorting works correctly for all sortable columns
  - Column resizing and reordering function properly
  - Enhanced filtering works for all filterable columns
  - Existing pagination component integrates seamlessly
  - All status chips, tracking chips, and currency formatting preserved
  - Hover effects and navigation functionality maintained
  - Financial data formatting (percentages, currency) preserved exactly
- **Risk Level**: Medium-High (22 columns, complex financial data, existing chips, formatting)
- **Special Considerations**:
  - Handle 22 columns efficiently with column management
  - Preserve complex financial data formatting
  - Maintain responsive design for large column sets
  - Ensure performance with complex financial calculations

**Tasks**:
- [ ] Replace MUI table with TanStack Table component
- [ ] Implement multi-column sorting (name, status, creation date, performance metrics)
- [ ] Add column resizing and reordering functionality
- [ ] Implement enhanced filtering (status, fund type, currency)
- [ ] Add column visibility toggles for 22 columns
- [ ] Integrate with existing pagination component
- [ ] Preserve all status chips, tracking chips, and financial formatting
- [ ] Maintain hover effects and navigation functionality
- [ ] Test all 22 columns display correctly
- [ ] Verify all validation criteria

**Migration Dependencies**:
- Start with Companies Table (simplest, establishes base patterns)
- Then Dashboard Table (similar complexity, validates patterns)
- Finally Companies Tab Funds Table (22 columns, complex financial data, builds on established patterns)
- **Note**: Companies Tab Funds Table migration requires special attention due to 22 columns and complex financial formatting

**Pattern Validation**:
- Ensure migration approach works for all table types
- Verify all existing styling and responsive behavior maintained
- Confirm consistent API patterns across all migrated tables
- Test that new features enhance rather than replace existing functionality

**Note**: Fund Summary Sections (`components/fund/detail/summary/`) are NOT tables - they are summary cards, charts, and metrics displays that do not require table migration.

**Design Principles**:
- Start with simplest tables to establish migration patterns
- Preserve all existing functionality exactly as-is
- Add new features only after core functionality is verified
- Maintain identical user interactions during transition
- Establish reusable patterns for Phase 3 complex table migration

### Phase 3: Fund Detail Table Migration (Week 3-4)
**Goal**: Migrate high-complexity fund detail table (events table) while preserving business logic

**Table Details**:
- **Files**: `frontend/src/components/fund/detail/table/`
- **Current Features**: 
  - Complex event grouping (interest + withholding, tax statements)
  - Flag-based grouping system with group_position
  - Event filtering (tax events, NAV updates)
  - Grouped row rendering with expandable functionality
  - Custom scrollbar styling and responsive design
  - Event deletion functionality
  - Add event functionality
- **Lines of Code**: ~400+ lines across multiple components
- **Complexity**: High (complex business logic, critical functionality)

**Tasks**:
- [ ] **Event Grouping Preservation**: Maintain complex event grouping logic exactly
- [ ] **Custom Row Rendering**: Preserve existing EventRow and GroupedEventRow components
- [ ] **Business Logic Integration**: Integrate existing useEventGrouping hook with TanStack Table
- [ ] **Expandable Rows**: Implement expand/collapse for grouped events
- [ ] **Column-Based Filtering**: Add filters for event types, dates, and amounts
- [ ] **Event Management**: Preserve add/delete event functionality
- [ ] **Filter Toggles**: Maintain tax events and NAV updates filtering

**Critical Preservation Requirements**:
- Interest + Withholding Tax combination logic must work identically
- Tax statement grouping must function exactly as current
- Flag-based grouping with group_position must be preserved
- All existing event filtering must work identically
- Custom scrollbar styling must be maintained
- Event deletion and addition functionality must be preserved
- Complex business logic for event grouping must remain unchanged

**New Features**:
- Enhanced grouping with TanStack Table's built-in grouping
- Column management for large event datasets
- Improved performance for large event datasets
- Better accessibility and keyboard navigation

**Design Principles**:
- Business logic must remain unchanged and fully functional
- Complex event grouping must work identically to current implementation
- Performance must be equal to or better than current tables
- User experience must remain familiar and intuitive
- All existing event management functionality must be preserved

### Phase 4: Advanced Features (Week 5-6)
**Goal**: Implement advanced table features that enhance user experience

**Tasks**:
- [ ] **Column Management**: Add visibility toggles, resizing, and reordering
- [ ] **Virtual Scrolling**: Implement for large datasets to improve performance
- [ ] **Bulk Actions**: Add row selection with bulk operations
- [ ] **Global Search**: Implement search across all columns
- [ ] **Export Functionality**: Add CSV and Excel export capabilities

**Design Principles**:
- New features must enhance rather than replace existing functionality
- Performance improvements must be measurable and significant
- Advanced features should be discoverable but not overwhelming
- Accessibility must be maintained or improved with new features

### Phase 5: Testing & Documentation (Week 7)
**Goal**: Ensure quality and establish patterns for future development

**Tasks**:
- [ ] **Comprehensive Testing**: Unit, integration, and performance testing
- [ ] **Documentation Updates**: Update component architecture and team onboarding materials
- [ ] **Performance Validation**: Measure and document performance improvements
- [ ] **User Acceptance Testing**: Validate that table interactions feel natural
- [ ] **Pattern Documentation**: Create examples and best practices for future tables

**Design Principles**:
- Testing must cover all existing functionality to ensure no regression
- Documentation must be comprehensive and actionable
- Performance metrics must be measurable and documented
- User experience must be validated through actual usage

## Technical Architecture

### Core Infrastructure Components

#### 1. **Base Table Hook** (`frontend/src/hooks/useTable.ts`)
- **Purpose**: Centralized table logic with TanStack Table integration
- **Features**: Sorting, filtering, pagination, grouping, row selection
- **Configuration**: Flexible options for enabling/disabling features
- **State Management**: Comprehensive state handling for all table features

#### 2. **Base Table Component** (`frontend/src/components/ui/table/Table.tsx`)
- **Purpose**: Reusable table component that maintains MUI styling
- **Features**: Responsive design, theme integration, accessibility
- **Props**: Flexible interface for different table configurations
- **Styling**: Maintains existing MUI styling and responsive behavior

#### 3. **Table Utilities** (`frontend/src/utils/tableUtils.ts`)
- **Purpose**: Helper functions for common table operations
- **Features**: Column definition builders, export functions, performance utilities
- **Reusability**: Functions that work across all table types
- **Type Safety**: Full TypeScript support with proper type inference

### Migration Patterns

#### 1. **Column Definition Pattern**
- **Structure**: Consistent column definition format across all tables
- **Features**: Built-in sorting, filtering, and styling options
- **Customization**: Flexible cell rendering and column behavior
- **Type Safety**: Full TypeScript integration with row data types

#### 2. **State Management Pattern**
- **Centralization**: All table state managed through useTable hook
- **Persistence**: State can be persisted across component re-renders
- **Integration**: Seamless integration with existing Zustand store
- **Performance**: Optimized state updates to minimize re-renders

#### 3. **Styling Integration Pattern**
- **MUI Compatibility**: Maintains existing MUI theme and styling
- **Responsive Design**: Preserves current responsive behavior
- **Custom Styling**: Supports custom styling through sx prop
- **Accessibility**: Maintains or improves accessibility features

## Risk Mitigation

### Technical Risks
1. **Performance Degradation**
   - **Mitigation**: Comprehensive performance testing before and after migration
   - **Fallback**: Ability to revert to MUI tables if performance issues arise
   - **Monitoring**: Performance metrics tracking throughout migration

2. **Functionality Loss**
   - **Mitigation**: Feature parity testing at each migration phase
   - **Fallback**: Gradual migration with rollback capability
   - **Validation**: Automated testing to catch regressions early

3. **Styling Inconsistencies**
   - **Mitigation**: Maintain existing MUI styling and theme integration
   - **Fallback**: CSS-in-JS approach for custom styling
   - **Testing**: Visual regression testing to catch styling issues

### Business Risks
1. **User Experience Disruption**
   - **Mitigation**: Maintain identical user interactions during migration
   - **Fallback**: User testing and feedback collection
   - **Communication**: Clear communication about changes and improvements

2. **Development Timeline**
   - **Mitigation**: Phased approach with clear milestones
   - **Fallback**: Extend timeline if necessary for quality assurance
   - **Prioritization**: Focus on core functionality before advanced features

## Success Metrics

### Functional Requirements
- [ ] All existing table functionality preserved and working identically
- [ ] Performance improved or maintained for datasets of 1000+ rows
- [ ] New features enhance user experience without disruption
- [ ] Accessibility compliance maintained or improved

### Technical Requirements
- [ ] TypeScript type safety maintained and enhanced
- [ ] Component reusability significantly improved
- [ ] Code maintainability enhanced through consistent patterns
- [ ] Testing coverage maintained or improved

### User Experience Requirements
- [ ] Table interactions feel natural and responsive
- [ ] Loading states provide clear feedback
- [ ] Error handling is graceful and informative
- [ ] Mobile experience is optimized and consistent

## Migration Checklist

### **Phase 1: Foundation** ⏳
- [ ] Install TanStack Table dependencies
- [ ] Create core table infrastructure
- [ ] Implement base table components
- [ ] Create type definitions
- [ ] Set up design system integration

### **Phase 2: Simple Tables** ⏳
- [ ] Migrate Companies Table
- [ ] Migrate Overall Dashboard Table
- [ ] Migrate Funds Table
- [ ] Test basic functionality
- [ ] Verify styling preservation

### **Phase 3: Complex Tables** ⏳
- [ ] Migrate Fund Detail Table
- [ ] Preserve event grouping logic
- [ ] Implement expandable rows
- [ ] Test complex interactions
- [ ] Verify business logic preservation

### **Phase 4: Advanced Features** ⏳
- [ ] Implement column management
- [ ] Add virtual scrolling
- [ ] Implement bulk actions
- [ ] Enhance accessibility
- [ ] Performance optimization

### **Phase 5: Testing & Documentation** ⏳
- [ ] Complete testing suite
- [ ] Update documentation
- [ ] Performance validation
- [ ] User acceptance testing
- [ ] Deployment preparation

## Conclusion

This migration specification provides a comprehensive roadmap for transitioning from MUI tables to TanStack Table while maintaining the existing design system and business logic. The phased approach ensures minimal disruption and allows for thorough testing at each stage.

The migration will significantly improve table performance, add advanced features, and establish consistent patterns for future table development. By following this specification, the team can deliver a professional, enterprise-level table system that enhances the overall user experience of the investment tracker application.

## Appendix

### **A. TanStack Table Features Reference**
- [Official Documentation](https://tanstack.com/table/v8)
- [API Reference](https://tanstack.com/table/v8/docs/api/core/table)
- [Examples and Recipes](https://tanstack.com/table/v8/docs/examples/react/basic)

### **B. Migration Tools and Utilities**
- Column definition builders
- Table configuration presets
- Performance monitoring tools
- Accessibility testing utilities

### **C. Performance Benchmarks**
- Current MUI table performance metrics
- Target TanStack Table performance metrics
- Performance testing methodology
- Optimization techniques and best practices
