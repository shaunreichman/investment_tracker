# Frontend Refactoring Specification

> **Next Steps:** Phase 2 - Extract FundDetail Component into focused sections

## Overview
Transform the frontend codebase from a monolithic structure with massive files and code duplication into a maintainable, scalable, and professional-grade React application that follows industry best practices.

## Design Philosophy
- **Single Responsibility**: Each file has one clear purpose and responsibility
- **Code Reusability**: Shared utilities and components eliminate duplication
- **Maintainability**: Small, focused components that are easy to understand and modify
- **Performance**: Optimized rendering and reduced bundle size
- **Team Collaboration**: Multiple developers can work simultaneously without conflicts
- **Professional Standards**: Follow React and TypeScript industry conventions
- **Functional Parity**: **ZERO changes to existing functionality or user experience**
- **Visual Parity**: **ZERO changes to UI appearance, styling, or behavior**

## Problems We're Solving
1. **Massive File Sizes**: FundDetail.tsx (2,221 lines) violates professional standards
2. **Code Duplication**: formatCurrency, formatDate, validateField repeated across components
3. **Mixed Responsibilities**: Components handle UI, business logic, validation, and API calls
4. **Maintenance Nightmare**: Finding and modifying functionality is difficult
5. **Testing Complexity**: Large components are unwieldy to test
6. **Inconsistent Patterns**: Mixed approaches to error handling and validation

## Success Criteria
- All files under 500 lines (industry standard)
- Zero code duplication for common utilities
- 90%+ test coverage for new components
- Faster development cycles and easier debugging
- Reduced bundle size and improved performance
- Professional-grade architecture that supports team growth
- **Complex components are broken into focused, testable pieces**
- **Business logic is extracted into reusable hooks and utilities**
- **100% functional parity** - no regression in any feature or behavior
- **100% visual parity** - no changes to UI appearance or user experience

## Implementation Strategy

### Phase 1: Foundation & Shared Utilities
**Goal**: Create centralized utilities and establish foundation for refactoring
**Tasks**:
- [x] Create `frontend/src/utils/formatters.ts` with centralized currency, date, and number formatting
  - [x] Extract `formatCurrency` from FundDetail.tsx (line 853) and other components
  - [x] Extract `formatDate` from FundDetail.tsx (line 878) and OverallDashboard.tsx
  - [x] Extract `formatBrokerageFee` from FundDetail.tsx (line 864)
  - [x] Add support for null/undefined values with graceful fallbacks
  - [x] Add currency parameter support (default 'AUD')
  - [x] Add Excel-style accounting format (parentheses for negatives)
- [x] Create `frontend/src/utils/validators.ts` with reusable validation patterns
  - [x] Extract `validateField` from CreateFundEventModal.tsx (line 297), EditFundEventModal.tsx (line 183), CreateFundModal.tsx (line 205)
  - [x] Create `createValidator` function for composable validation rules
  - [x] Define validation rules for: amounts, dates, required fields, email, URLs
  - [x] Add custom validation for fund-specific business rules
  - [x] Ensure validation messages are user-friendly and consistent
- [x] Create `frontend/src/utils/constants.ts` with shared constants and enums
  - [x] Extract event types from CreateFundEventModal.tsx (line 30)
  - [x] Extract distribution types from CreateFundEventModal.tsx (line 40)
  - [x] Extract fund types and tracking types
  - [x] Add status enums and color mappings
  - [x] Add tax payment types and rates
- [x] Create `frontend/src/utils/helpers.ts` with common utility functions
  - [x] Extract `getEventTypeColor` from FundDetail.tsx (line 890)
  - [x] Extract `getEventTypeLabel` from FundDetail.tsx (line 900)
  - [x] Extract `getStatusInfo` from FundDetail.tsx (line 320)
  - [x] Add helper for combining interest + withholding tax events
  - [x] Add helper for chart data preparation
- [x] Update all components to use centralized utilities
  - [x] Update FundDetail.tsx to import from utils
  - [x] Update CreateFundEventModal.tsx to use shared validators
  - [x] Update EditFundEventModal.tsx to use shared validators
  - [x] Update CreateFundModal.tsx to use shared validators
  - [x] Update CompaniesPage.tsx to use shared formatters
  - [x] Update OverallDashboard.tsx to use shared formatters
- [x] Add comprehensive tests for all utility functions
  - [x] Test formatters with null/undefined values
  - [x] Test validators with edge cases
  - [x] Test helpers with various input combinations
  - [x] Test currency formatting with different currencies
**Design Principles**:
- All formatting functions support null/undefined values gracefully
- Validation functions are composable and reusable
- Constants are type-safe and well-documented
- Utilities are pure functions with no side effects
**Critical Context**:
- The current `formatCurrency` in FundDetail.tsx uses Excel accounting format (parentheses for negatives)
- Event type colors and labels are used throughout the application
- Validation patterns are repeated across all modal components
- Chart data preparation logic is complex and should be centralized

### Phase 2: Extract FundDetail Component (PARTIALLY COMPLETE)
**Goal**: Break down the massive FundDetail.tsx into focused, maintainable components
**Tasks**:
- [x] Create `frontend/src/components/fund-detail/` directory structure
- [x] Extract `EquitySection.tsx` (~149 lines) with equity and NAV metrics
  - [x] Extract from FundDetail.tsx lines 51-181 (EquitySection component)
  - [x] Include `isActiveNavFund` logic for NAV-based fund display
  - [x] Include conditional rendering for NAV metrics (current NAV, units owned, NAV market value)
  - [x] Include priority-based metric ordering and styling
  - [x] Add proper TypeScript interfaces for metric data structure
- [x] Extract `ExpectedPerformanceSection.tsx` (~110 lines) with expected performance
  - [x] Extract `ExpectedPerformanceSection` from FundDetail.tsx lines 182-275
  - [x] Include IRR formatting with percentage display
  - [x] Include duration formatting with month display
- [x] Extract `CompletedPerformanceSection.tsx` (~132 lines) with completed performance
  - [x] Extract `CompletedPerformanceSection` from FundDetail.tsx lines 275-390
  - [x] Include conditional rendering based on fund status
  - [x] Include IRR formatting with percentage display
  - [x] Include duration formatting with month display
- [x] Extract `FundDetailsSection.tsx` (~110 lines) with basic fund information
  - [x] Extract from FundDetail.tsx lines 390-515 (FundDetailsSection component)
  - [x] Include status display with color coding and tooltips
  - [x] Include currency and duration information
  - [x] Include status transition logic (ACTIVE → REALIZED → COMPLETED)
- [x] Extract `TransactionSummarySection.tsx` (~96 lines) with transaction totals
  - [x] Extract from FundDetail.tsx lines 515-595 (TransactionSummarySection component)
  - [x] Include conditional display for cost-based vs NAV-based funds
  - [x] Include transaction type filtering and grouping
  - [x] Include color coding for different transaction types
- [x] Extract `UnitPriceChartSection.tsx` (~246 lines) with NAV performance chart
  - [x] Extract from FundDetail.tsx lines 595-853 (UnitPriceChartSection component)
  - [x] Include chart data preparation logic (NAV data, purchase/sale data)
  - [x] Include error handling for chart rendering
  - [x] Include responsive chart sizing and tooltips
  - [x] Include date range calculation and tick generation
- [ ] Extract `FundDetailTable/` directory with **INCREMENTAL, STEP-BY-STEP** approach (~400 lines total)
  
  **Phase 2B.1: Foundation & Debug Infrastructure** (Safe, no UI changes) - ✅ COMPLETED
  - [x] Create `FundDetailTable/` directory structure
  - [x] Create `FundDetailTable/debug.ts` (~50 lines) - Debug utilities for table rendering
    - [x] Create `debugTableRendering` function to log table state and events
    - [x] Create `compareTableRendering` function to compare before/after rendering
    - [x] Create `logEventGrouping` function to debug event grouping logic
    - [x] Create `validateTableStructure` function to ensure table integrity
    - [x] **TEST**: Verify debug utilities work with existing table without breaking functionality
  - [x] Create `FundDetailTable/index.ts` (~10 lines) - Basic exports
    - [x] Export debug utilities only
    - [x] **TEST**: Verify imports work without breaking existing code
  
  **Phase 2B.2: Extract Event Grouping Logic** (Safe, isolated logic) - ✅ COMPLETED
  - [x] Create `FundDetailTable/useEventGrouping.ts` (~80 lines) - Event grouping logic hook
    - [x] Extract event grouping logic from FundDetail.tsx lines 650-680
    - [x] Include date-based event grouping algorithm
    - [x] Include interest + withholding tax combination logic
    - [x] Include grouped event calculations and formatting
    - [x] Include memoization for performance optimization
    - [x] Add comprehensive logging for debugging
    - [x] **TEST**: Verify hook returns identical grouping results to original logic
    - [x] **TEST**: Test with various event combinations and fund types
  
  **Phase 2B.3: Extract Row Rendering Components** (Safe, isolated components) - ✅ COMPLETED
  - [x] Create `FundDetailTable/EventRow.tsx` (~150 lines) - Individual event row rendering
    - [x] Extract individual row logic from FundDetail.tsx lines 808-1043
    - [x] Include event type-specific cell rendering (tax payments, NAV updates, etc.)
    - [x] Include conditional column display for different event types
    - [x] Include complex tax payment type handling (EOFY_INTEREST_TAX, DIVIDENDS_FRANKED_TAX, etc.)
    - [x] Include EOFY debt cost event handling with deduction calculations
    - [x] Include row hover effects and styling
    - [x] Add comprehensive prop validation
    - [x] **TEST**: Verify component renders correctly in isolation
    - [x] **TEST**: Test with all event types and edge cases
  - [x] Create `FundDetailTable/GroupedEventRow.tsx` (~120 lines) - Grouped events row rendering
    - [x] Extract grouped row logic from FundDetail.tsx lines 684-773
    - [x] Include interest + withholding tax combination logic
    - [x] Include grouped event amount calculations
    - [x] Include conditional equity/tax column display
    - [x] Include grouped row styling and hover effects
    - [x] Add comprehensive prop validation
    - [x] **TEST**: Verify component renders correctly in isolation
    - [x] **TEST**: Test with various interest + withholding combinations
  
  **Phase 2B.4: Granular Table Extraction with Step-by-Step Verification** (REALISTIC APPROACH)
  
  **Goal**: Extract the 850-line table logic into focused, manageable components with immediate verification at each step
  **Strategy**: Break down complex table logic into small, testable pieces that can be verified immediately
  
  **Step 1: Extract TableFilters Component** (SAFE, IMMEDIATE VERIFICATION) - ✅ COMPLETED
  - [x] Create `FundDetailTable/TableFilters.tsx` (~80 lines) - Filter toggles and add button
    - [x] Extract filter toggle logic from FundDetail.tsx lines 450-500
    - [x] Include "Show Tax Events" and "Show NAV Updates" switches
    - [x] Include "Add Event" button with modal trigger
    - [x] Include responsive styling and hover effects
    - [x] Add proper TypeScript interfaces for filter props
    - [x] **VERIFICATION**: Toggle filters work identically to original
    - [x] **VERIFICATION**: Add Event button opens modal correctly
    - [x] **VERIFICATION**: Filters work on all fund types (NAV-based and cost-based)
    - [x] **VERIFICATION**: No visual changes to filter section
  
  **Step 2: Extract TableHeader Component** (SAFE, IMMEDIATE VERIFICATION) - ✅ COMPLETED
  - [x] Create `FundDetailTable/TableHeader.tsx` (~120 lines) - Table header row
    - [x] Extract header row logic from FundDetail.tsx lines 536-660
    - [x] Include conditional column display based on fund type
    - [x] Include responsive column styling and typography
    - [x] Include event count display in header
    - [x] Add proper TypeScript interfaces for header props
    - [x] **VERIFICATION**: All columns display correctly
    - [x] **VERIFICATION**: NAV column shows/hides based on fund type
    - [x] **VERIFICATION**: Tax column shows/hides based on filter state
    - [x] **VERIFICATION**: Column alignment and styling identical to original
  
  **Step 3: Extract ActionButtons Component** (SAFE, IMMEDIATE VERIFICATION) - ✅ COMPLETED
  - [x] Create `FundDetailTable/ActionButtons.tsx` (~80 lines) - Edit/delete buttons
    - [x] Extract action button logic from FundDetail.tsx lines 1040-1084
    - [x] Include edit/delete button rendering with event type filtering
    - [x] Include button styling and hover effects
    - [x] Include proper event type validation for editable events
    - [x] Add comprehensive TypeScript interfaces
    - [x] **VERIFICATION**: Edit button opens edit modal for editable events
    - [x] **VERIFICATION**: Delete button opens delete dialog for editable events
    - [x] **VERIFICATION**: Buttons don't show for system events (TAX_PAYMENT, etc.)
    - [x] **VERIFICATION**: Button styling and hover effects identical to original
  
  **Step 4: Extract Event Grouping Logic** (SAFE, IMMEDIATE VERIFICATION) - ✅ COMPLETED
  - [x] Create `FundDetailTable/useEventGrouping.ts` (~100 lines) - Event grouping logic
    - [x] Extract grouping logic from FundDetail.tsx lines 695-710
    - [x] Include date-based event grouping algorithm
    - [x] Include interest + withholding tax combination logic
    - [x] Include event filtering based on showTaxEvents and showNavUpdates
    - [x] Add comprehensive logging for debugging
    - [x] **VERIFICATION**: Events grouped by date correctly
    - [x] **VERIFICATION**: Interest + withholding tax events identified correctly
    - [x] **VERIFICATION**: Grouping works for all event types
    - [x] **VERIFICATION**: Performance maintained or improved
  
  **Step 5: Extract IndividualEventRow Component** (RISKY, CAREFUL TESTING REQUIRED) - ✅ COMPLETED
  - [x] Create `FundDetailTable/EventRow.tsx` (~200 lines) - Individual event row
    - [x] Extract individual row rendering logic from FundDetail.tsx lines 850-1084
    - [x] Include NAV-based vs cost-based fund logic
    - [x] Include event type-specific cell rendering
    - [x] Include conditional column display
    - [x] Add comprehensive TypeScript interfaces
    - [x] **VERIFICATION**: Test with every event type:
      - [x] CAPITAL_CALL, RETURN_OF_CAPITAL (cost-based funds)
      - [x] UNIT_PURCHASE, UNIT_SALE (NAV-based funds)
      - [x] DISTRIBUTION (INTEREST, DIVIDEND, OTHER)
      - [x] TAX_PAYMENT (all types: EOFY_INTEREST_TAX, DIVIDENDS_FRANKED_TAX, etc.)
      - [x] NAV_UPDATE (NAV-based funds only)
      - [x] EOFY_DEBT_COST, MANAGEMENT_FEE, CARRIED_INTEREST
    - [x] **VERIFICATION**: Row styling identical to original
    - [x] **VERIFICATION**: Cell content displays correctly for all event types
  
  **Step 6: Extract CombinedEventRow Component** (RISKY, CAREFUL TESTING REQUIRED) - ✅ COMPLETED
  - [x] Create `FundDetailTable/GroupedEventRow.tsx` (~150 lines) - Combined interest + withholding
    - [x] Extract combined row logic from FundDetail.tsx lines 723-815
    - [x] Include interest + withholding tax combination logic
    - [x] Include conditional column display for combined events
    - [x] Include complex tax payment type handling
    - [x] Add comprehensive TypeScript interfaces
    - [x] **VERIFICATION**: Test with funds that have interest + withholding tax events
    - [x] **VERIFICATION**: Test with funds that don't have combined events
    - [x] **VERIFICATION**: Combined row displays correctly
    - [x] **VERIFICATION**: Other events on same date still display correctly
  
  **Step 7: Create TableBody Component** (SAFE INTEGRATION, IMMEDIATE VERIFICATION) - ✅ COMPLETED
  - [x] Create `FundDetailTable/TableBody.tsx` (~100 lines) - Table body with extracted components
    - [x] Integrate useEventGrouping hook with extracted row components
    - [x] Use GroupedEventRow for combined events (interest + withholding)
    - [x] Use EventRow for individual events
    - [x] Include all existing table body styling and responsive behavior
    - [x] Add comprehensive TypeScript interfaces
    - [x] **VERIFICATION**: All event types render correctly
    - [x] **VERIFICATION**: Event grouping works identically to original
    - [x] **VERIFICATION**: Row styling and hover effects identical to original
    - [x] **VERIFICATION**: Performance maintained or improved
  
  **Step 8: Create TableContainer Component** (INTEGRATION, COMPREHENSIVE TESTING)
  - [ ] Create `FundDetailTable/TableContainer.tsx` (~150 lines) - Complete table container
    - [ ] Combine TableFilters, TableHeader, and TableBody components
    - [ ] Include table wrapper and responsive layout from FundDetail.tsx
    - [ ] Include loading states and error boundaries
    - [ ] Include comprehensive TypeScript interfaces
    - [ ] **VERIFICATION**: Complete table renders identically to original
    - [ ] **VERIFICATION**: All interactions work correctly
    - [ ] **VERIFICATION**: Performance maintained or improved
    - [ ] **VERIFICATION**: No console errors or warnings
  
  **Step 9: Integration and Final Testing** (COMPREHENSIVE VERIFICATION)
  - [ ] Replace original table section in FundDetail.tsx with TableContainer
    - [ ] Remove original table JSX (~850 lines)
    - [ ] Add TableContainer component import
    - [ ] Replace table section with TableContainer component
    - [ ] Add debug logging to compare before/after rendering
    - [ ] **VERIFICATION**: Complete visual regression testing
    - [ ] **VERIFICATION**: All functionality preserved
    - [ ] **VERIFICATION**: Performance testing with large datasets
    - [ ] **VERIFICATION**: Cross-browser compatibility testing

**GRANULAR APPROACH PRINCIPLES**:
- **Step-by-Step Verification**: Each step must be verified immediately before proceeding
- **Small, Manageable Pieces**: No component larger than 200 lines (industry standard)
- **Clear Responsibilities**: Each component has one focused purpose
- **Immediate Testing**: Each step tested in isolation before integration
- **Rollback Safety**: Each step easily reversible if issues arise
- **Debug Infrastructure**: Comprehensive logging and debugging utilities
- **Preservation First**: Every step maintains 100% functional and visual parity
- **Performance Monitoring**: Track render performance throughout

**VERIFICATION STRATEGY**:
- **Safe Steps (1-6)**: ✅ COMPLETED - All foundational components extracted and tested
- **Integration Steps (7)**: ✅ COMPLETED - TableBody component integrated and tested
- **Integration Steps (8)**: Safe integration using extracted components
- **Final Step (9)**: End-to-end testing with performance validation

**SAFETY MEASURES**:
- **Debug Infrastructure**: Use existing debug utilities from FundDetailTable/debug.ts
- **Visual Regression**: Screenshot comparison before/after each step
- **Functional Testing**: Test all event types, filter combinations, and interactions
- **Performance Testing**: Ensure no performance regression
- **User Interaction Testing**: Test all buttons, filters, and interactions
- **Rollback Scripts**: Keep original code commented out during transition
- **Comprehensive Logging**: Detailed logging for troubleshooting

**CRITICAL PRESERVATION REQUIREMENTS**:
- **Event Grouping Logic**: Must group events by date exactly as before, combining interest + withholding tax events identically
- **Tax Payment Display**: Must show tax payment types (EOFY_INTEREST_TAX, DIVIDENDS_FRANKED_TAX, etc.) with exact same formatting and calculations
- **Conditional Columns**: Must show/hide columns based on fund type and event types exactly as before
- **Row Styling**: Must preserve exact hover effects, colors, spacing, and typography
- **Action Buttons**: Must show edit/delete buttons for same event types with identical behavior
- **Filtering Logic**: Must preserve showTaxEvents and showNavUpdates functionality exactly
- **Responsive Behavior**: Must maintain identical responsive behavior on all screen sizes
- **Performance**: Must maintain or improve render performance

**REALISTIC TIMELINE**:
- **Week 1**: Steps 7-8 (Safe integration using extracted components)
- **Week 2**: Step 9 (Integration and final testing)
- [ ] Extract `FundDetailHeader.tsx` (~100 lines) with breadcrumbs and title
  - [ ] Extract header from FundDetail.tsx lines 1100-1200
  - [ ] Include breadcrumb navigation with proper routing
  - [ ] Include fund title and subtitle display
  - [ ] Include sidebar toggle functionality
- [ ] Extract `FundDetailSidebar.tsx` (~200 lines) with summary sections
  - [ ] Extract sidebar container from FundDetail.tsx lines 1150-1200
  - [ ] Include responsive sidebar behavior
  - [ ] Include section composition and layout
  - [ ] Include sidebar visibility state management
- [ ] Create main `FundDetail.tsx` orchestrator (~200 lines)
  - [x] Extract main component logic from FundDetail.tsx lines 850-1100
  - [x] Include API data fetching and error handling
  - [x] Include state management for modals and dialogs
  - [x] Include event handlers for CRUD operations
  - [x] Include responsive layout orchestration
  - [ ] **STILL NEEDS**: Extract remaining table, header, and sidebar logic
- [ ] Add comprehensive tests for each section component
  - [ ] Test conditional rendering based on fund type
  - [ ] Test data formatting and display
  - [ ] Test user interactions and callbacks
  - [ ] Test error states and loading states

**PROFESSIONAL SOLUTION BENEFITS**:

This incremental approach will result in a **very professional solution** because it addresses the core challenges of enterprise-grade React development:

### **1. Risk Mitigation & Safety**
- **Zero Downtime**: Each step is tested and validated before proceeding
- **Rollback Capability**: Any phase can be safely reverted if issues arise
- **Debug Infrastructure**: Comprehensive logging and debugging tools for troubleshooting
- **Visual Regression**: Automated screenshot comparison ensures UI consistency

### **2. Maintainability & Scalability**
- **Single Responsibility**: Each component has one clear purpose
- **Reusable Logic**: Event grouping logic extracted into reusable hooks
- **Type Safety**: Comprehensive TypeScript interfaces and prop validation
- **Performance Optimization**: Memoization and performance monitoring throughout

### **3. Professional Development Standards**
- **Incremental Testing**: Each component tested in isolation before integration
- **Comprehensive Error Handling**: Error boundaries and loading states
- **Accessibility**: Keyboard navigation and screen reader support
- **Performance Monitoring**: Track render performance and memory usage

### **4. Team Collaboration Benefits**
- **Parallel Development**: Multiple developers can work on different components simultaneously
- **Clear Interfaces**: Well-defined props and interfaces for all components
- **Documentation**: Comprehensive logging and debugging utilities
- **Code Review**: Smaller, focused components are easier to review

### **5. Enterprise-Grade Architecture**
- **Separation of Concerns**: Business logic separated from UI components
- **Reusable Patterns**: Consistent patterns across all components
- **Error Recovery**: Graceful error handling and user feedback
- **Performance**: Optimized rendering and reduced bundle size

### **6. Future-Proof Design**
- **Extensible**: Easy to add new event types or fund types
- **Testable**: Each component can be tested independently
- **Debuggable**: Comprehensive logging and debugging infrastructure
- **Maintainable**: Clear structure and documentation

**This approach transforms a monolithic, hard-to-maintain component into a professional, enterprise-grade React application that follows industry best practices and supports long-term team growth.**

### Phase 3: Refactor Modal Components
**Goal**: Break down large modal components into manageable, reusable pieces
**Tasks**:
- [ ] Create `frontend/src/components/modals/` directory structure
- [ ] Refactor `CreateFundEventModal/`:
  - [ ] Extract `EventTypeSelector.tsx` (~150 lines) for event type selection
    - [ ] Extract from CreateFundEventModal.tsx lines 30-100 (EVENT_TEMPLATES)
    - [ ] Include template selection with icons and descriptions
    - [ ] Include tracking type filtering (nav_based vs cost_based)
    - [ ] Include template application logic
  - [ ] Extract `DistributionForm.tsx` (~200 lines) for distribution events
    - [ ] Extract from CreateFundEventModal.tsx lines 500-800 (distribution form logic)
    - [ ] Include distribution type selection (INTEREST, DIVIDEND, OTHER)
    - [ ] Include sub-distribution types (FRANKED, UNFRANKED, WITHHOLDING_TAX)
    - [ ] Include withholding tax calculation logic
    - [ ] Include gross/net amount handling
  - [ ] Extract `UnitTransactionForm.tsx` (~200 lines) for unit purchases/sales
    - [ ] Extract from CreateFundEventModal.tsx lines 800-1000 (unit transaction logic)
    - [ ] Include units and unit price validation
    - [ ] Include brokerage fee handling
    - [ ] Include amount calculation (units × price + brokerage)
  - [ ] Extract `NavUpdateForm.tsx` (~150 lines) for NAV updates
    - [ ] Extract from CreateFundEventModal.tsx lines 1000-1150 (NAV update logic)
    - [ ] Include NAV per share validation
    - [ ] Include NAV change calculation
    - [ ] Include percentage change display
  - [ ] Extract `TaxStatementForm.tsx` (~300 lines) for tax statements
    - [ ] Extract from CreateFundEventModal.tsx lines 1150-1276 (tax statement logic)
    - [ ] Include financial year validation
    - [ ] Include interest income breakdown fields
    - [ ] Include tax rate calculations
    - [ ] Include debt interest deduction logic
  - [ ] Create main orchestrator (~100 lines)
    - [ ] Extract from CreateFundEventModal.tsx lines 100-500 (main component logic)
    - [ ] Include form state management
    - [ ] Include validation orchestration
    - [ ] Include API submission logic
- [ ] Refactor `EditFundEventModal/`:
  - [ ] Extract `EventForm.tsx` (~200 lines) for general event editing
    - [ ] Extract from EditFundEventModal.tsx lines 200-400 (general form logic)
    - [ ] Include event type-specific field rendering
    - [ ] Include form validation and error display
    - [ ] Include form submission handling
  - [ ] Extract `WithholdingTaxForm.tsx` (~150 lines) for tax withholding
    - [ ] Extract from EditFundEventModal.tsx lines 400-600 (withholding tax logic)
    - [ ] Include gross/net interest handling
    - [ ] Include withholding amount/rate calculations
    - [ ] Include tax payment type handling
  - [ ] Create main orchestrator (~100 lines)
    - [ ] Extract from EditFundEventModal.tsx lines 50-200 (main component logic)
    - [ ] Include event data initialization
    - [ ] Include form state management
    - [ ] Include API update logic
- [ ] Refactor `CreateFundModal/`:
  - [ ] Extract `TemplateSelector.tsx` (~150 lines) for fund templates
    - [ ] Extract from CreateFundModal.tsx lines 50-150 (FUND_TEMPLATES)
    - [ ] Include template selection with icons and descriptions
    - [ ] Include template application logic
    - [ ] Include stepper navigation
  - [ ] Extract `FundForm.tsx` (~200 lines) for fund creation form
    - [ ] Extract from CreateFundModal.tsx lines 150-400 (fund form logic)
    - [ ] Include entity selection with CreateEntityModal integration
    - [ ] Include fund type and tracking type selection
    - [ ] Include commitment amount and expected performance fields
    - [ ] Include form validation and error display
  - [ ] Create main orchestrator (~100 lines)
    - [ ] Extract from CreateFundModal.tsx lines 400-850 (main component logic)
    - [ ] Include stepper state management
    - [ ] Include form submission logic
    - [ ] Include success/error handling
- [ ] Add comprehensive tests for each modal component
  - [ ] Test form validation and error states
  - [ ] Test template selection and application
  - [ ] Test API submission and response handling
  - [ ] Test conditional field rendering
**Design Principles**:
- Form components are reusable across different contexts
- Validation logic is centralized and consistent
- Error handling follows established patterns
- Modal state management is clean and predictable
**Critical Context**:
- CreateFundEventModal has complex conditional form rendering based on event type
- EditFundEventModal handles withholding tax calculations and gross/net amounts
- CreateFundModal uses a stepper pattern with template selection
- All modals share similar validation patterns that should be centralized
- Tax statement forms have complex field dependencies and calculations

### Phase 4: Create Shared UI Components
**Goal**: Establish a consistent, reusable UI component library
**Tasks**:
- [ ] Create `frontend/src/components/ui/` directory structure
- [ ] Create `CurrencyDisplay.tsx` with consistent currency formatting
- [ ] Create `DateDisplay.tsx` with consistent date formatting
- [ ] Create `StatusChip.tsx` with fund and event status indicators
- [ ] Create `EventTypeChip.tsx` with event type indicators
- [ ] Create `LoadingSpinner.tsx` with consistent loading states
- [ ] Create `ErrorBoundary.tsx` with error boundary functionality
- [ ] Create `ConfirmDialog.tsx` with reusable confirmation dialogs
- [ ] Create `FormField.tsx` with consistent form field styling
- [ ] Create `FormSection.tsx` with form section organization
- [ ] Add comprehensive tests for all UI components
**Design Principles**:
- All components are fully typed with TypeScript
- Consistent Material-UI integration
- Accessible design patterns
- Responsive design principles

### Phase 5: Extract Business Logic
**Goal**: Separate business logic from UI components for better maintainability
**Tasks**:
- [ ] Create `frontend/src/hooks/business/` directory structure
- [ ] Create `useFundCalculations.ts` for fund-specific calculations
- [ ] Create `useEventProcessing.ts` for event data processing
- [ ] Create `useTaxCalculations.ts` for tax-related calculations
- [ ] Create `useChartData.ts` for chart data transformation
- [ ] Create `frontend/src/utils/transformers/` directory structure
- [ ] Create `fundTransformers.ts` for fund data transformation
- [ ] Create `eventTransformers.ts` for event data transformation
- [ ] Create `chartDataTransformers.ts` for chart data preparation
- [ ] Create `taxTransformers.ts` for tax data transformation
- [ ] Add comprehensive tests for all business logic
**Design Principles**:
- Business logic is pure and testable
- Transformers handle data conversion consistently
- Hooks provide clean interfaces for components
- Calculations are optimized and memoized

### Phase 6: Create Form System
**Goal**: Establish a consistent, reusable form system
**Tasks**:
- [ ] Create `frontend/src/components/forms/` directory structure
- [ ] Create `FormField.tsx` with consistent field rendering
- [ ] Create `FormSection.tsx` with form section organization
- [ ] Create `FormActions.tsx` with form action buttons
- [ ] Create `EventTypeSelector.tsx` with event type selection
- [ ] Create `DistributionTypeSelector.tsx` with distribution type selection
- [ ] Create `TaxStatementForm.tsx` with tax statement form
- [ ] Create `frontend/src/hooks/forms/` directory structure
- [ ] Create `useFormValidation.ts` for form validation logic
- [ ] Create `useFormState.ts` for form state management
- [ ] Create `useEventForm.ts` for event form logic
- [ ] Create `useTaxStatementForm.ts` for tax statement form logic
- [ ] Add comprehensive tests for form system
**Design Principles**:
- Form validation is consistent across all forms
- Form state management is predictable and testable
- Form components are reusable and composable
- Error handling is user-friendly and informative

### Phase 7: Layout and Navigation
**Goal**: Create consistent layout and navigation patterns
**Tasks**:
- [ ] Create `frontend/src/components/layout/` directory structure
- [ ] Create `PageHeader.tsx` with consistent page headers
- [ ] Create `Breadcrumbs.tsx` with navigation breadcrumbs
- [ ] Create `Sidebar.tsx` with responsive sidebar layout
- [ ] Create `MainContent.tsx` with main content area
- [ ] Create `ResponsiveLayout.tsx` with responsive layout wrapper
- [ ] Create `Navigation.tsx` with consistent navigation patterns
- [ ] Update all pages to use new layout components
- [ ] Add comprehensive tests for layout components
**Design Principles**:
- Responsive design works on all screen sizes
- Navigation is intuitive and accessible
- Layout components are flexible and reusable
- Consistent spacing and typography

### Phase 8: Performance Optimization
**Goal**: Optimize performance and reduce bundle size
**Tasks**:
- [ ] Implement React.memo for expensive components
  - [ ] Memoize FundDetail sections (EquitySection, PerformanceSection, etc.)
  - [ ] Memoize chart components (UnitPriceChartSection)
  - [ ] Memoize table components (FundDetailTable)
  - [ ] Memoize form components with stable props
- [ ] Add useMemo and useCallback for expensive calculations
  - [ ] Memoize chart data preparation in UnitPriceChartSection
  - [ ] Memoize event grouping logic in FundDetailTable
  - [ ] Memoize validation calculations in form components
  - [ ] Memoize formatting functions with stable dependencies
- [ ] Implement code splitting for large components
  - [ ] Lazy load modal components (CreateFundEventModal, EditFundEventModal)
  - [ ] Lazy load chart components (UnitPriceChartSection)
  - [ ] Lazy load form components (TaxStatementForm)
  - [ ] Use React.lazy with Suspense boundaries
- [ ] Optimize bundle size with tree shaking
  - [ ] Remove unused Material-UI imports
  - [ ] Remove unused utility functions
  - [ ] Remove unused TypeScript types
  - [ ] Configure webpack for tree shaking
- [ ] Implement lazy loading for modals and forms
  - [ ] Lazy load CreateFundEventModal on demand
  - [ ] Lazy load EditFundEventModal on demand
  - [ ] Lazy load CreateFundModal on demand
  - [ ] Add loading states for lazy components
- [ ] Add performance monitoring and metrics
  - [ ] Add React DevTools Profiler integration
  - [ ] Add bundle size monitoring
  - [ ] Add render time monitoring
  - [ ] Add memory usage monitoring
- [ ] Optimize chart rendering and data processing
  - [ ] Optimize chart data transformation in UnitPriceChartSection
  - [ ] Implement chart data caching
  - [ ] Optimize chart re-rendering logic
  - [ ] Add chart performance monitoring
- [ ] Implement virtual scrolling for large tables
  - [ ] Implement virtual scrolling for FundDetailTable
  - [ ] Optimize table row rendering
  - [ ] Add scroll performance monitoring
  - [ ] Test with large datasets (1000+ events)
- [ ] Add comprehensive performance tests
  - [ ] Test component render times
  - [ ] Test memory usage patterns
  - [ ] Test bundle size impact
  - [ ] Test user interaction responsiveness
**Design Principles**:
- Components only re-render when necessary
- Bundle size is optimized for production
- Performance is measured and monitored
- User experience is smooth and responsive
**Critical Context**:
- Chart data preparation in UnitPriceChartSection is computationally expensive
- Event grouping logic in FundDetailTable processes large datasets
- Modal components are large and should be lazy loaded
- Form validation calculations can be expensive with complex rules

### Phase 9: Testing and Documentation
**Goal**: Ensure comprehensive testing and documentation
**Tasks**:
- [ ] Add unit tests for all new components
- [ ] Add integration tests for critical user flows
- [ ] Add visual regression tests for UI components
- [ ] Create component documentation with Storybook
- [ ] Document architecture decisions and patterns
- [ ] Create developer onboarding documentation
- [ ] Add API documentation for new hooks and utilities
- [ ] Create troubleshooting and debugging guides
- [ ] Achieve 90%+ test coverage for new code
**Design Principles**:
- Tests are comprehensive and maintainable
- Documentation is clear and up-to-date
- New developers can onboard quickly
- Architecture decisions are well-documented

### Phase 10: Migration and Cleanup
**Goal**: Complete migration and cleanup of old code
**Tasks**:
- [ ] Migrate all components to use new utilities
  - [ ] Update FundDetail.tsx to use centralized formatters and validators
  - [ ] Update CreateFundEventModal.tsx to use shared validation patterns
  - [ ] Update EditFundEventModal.tsx to use shared validation patterns
  - [ ] Update CreateFundModal.tsx to use shared validation patterns
  - [ ] Update CompaniesPage.tsx to use shared formatters
  - [ ] Update OverallDashboard.tsx to use shared formatters
- [ ] Remove old utility functions from components
  - [ ] Remove formatCurrency from FundDetail.tsx (line 853)
  - [ ] Remove formatDate from FundDetail.tsx (line 878) and OverallDashboard.tsx
  - [ ] Remove validateField from all modal components
  - [ ] Remove getEventTypeColor and getEventTypeLabel from FundDetail.tsx
  - [ ] Remove duplicate constants and enums
- [ ] Update all imports to use new structure
  - [ ] Update import paths for new component structure
  - [ ] Update import paths for new utility structure
  - [ ] Update import paths for new hook structure
  - [ ] Ensure all imports are properly typed
- [ ] Remove unused code and dependencies
  - [ ] Remove unused Material-UI imports
  - [ ] Remove unused utility functions
  - [ ] Remove unused TypeScript types
  - [ ] Remove unused CSS and styling
- [ ] Update TypeScript types and interfaces
  - [ ] Update component prop interfaces
  - [ ] Update utility function signatures
  - [ ] Update hook return types
  - [ ] Ensure strict TypeScript compliance
- [ ] Ensure all tests pass with new structure
  - [ ] Run existing tests and fix any failures
  - [ ] Update test imports to use new structure
  - [ ] Add tests for new utility functions
  - [ ] Ensure test coverage is maintained
- [ ] Update deployment and build configurations
  - [ ] Update webpack configuration for new structure
  - [ ] Update build scripts and deployment scripts
  - [ ] Update environment configurations
  - [ ] Update CI/CD pipeline configurations
- [ ] Create migration guide for team
  - [ ] Document new component structure
  - [ ] Document new utility functions
  - [ ] Document new patterns and conventions
  - [ ] Create troubleshooting guide
- [ ] Monitor for any regressions or issues
  - [ ] Monitor application performance
  - [ ] Monitor error rates and user feedback
  - [ ] Monitor bundle size and load times
  - [ ] Have rollback plan ready if needed
**Design Principles**:
- Migration is gradual and safe
- No functionality is lost during migration
- Team is informed and prepared for changes
- Rollback plan is available if needed
**Critical Context**:
- The current formatCurrency function uses Excel accounting format (parentheses for negatives)
- Event type colors and labels are used throughout the application
- Validation patterns are repeated across all modal components
- Chart data preparation logic is complex and should be centralized
- All components must maintain their current functionality during migration

## Success Metrics

### Code Quality Metrics
- [ ] All files under 500 lines (industry standard)
- [ ] Zero code duplication for common utilities
- [ ] 90%+ test coverage for new components
- [ ] TypeScript strict mode enabled
- [ ] No ESLint warnings or errors

### Performance Metrics
- [ ] Bundle size reduced by 20%+
- [ ] Component render time improved by 30%+
- [ ] Memory usage optimized
- [ ] Lighthouse performance score > 90

### Developer Experience Metrics
- [ ] Development cycle time reduced by 40%+
- [ ] Code review time reduced by 50%+
- [ ] New feature development time reduced by 30%+
- [ ] Bug fix time reduced by 50%+

### Team Collaboration Metrics
- [ ] Multiple developers can work simultaneously
- [ ] Code conflicts reduced by 70%+
- [ ] Onboarding time for new developers reduced by 60%+
- [ ] Architecture decisions are clear and documented

## Risk Mitigation

### Technical Risks
- **Risk**: Breaking existing functionality during refactoring
- **Mitigation**: Comprehensive testing and gradual migration
- **Risk**: Performance regression from new architecture
- **Mitigation**: Performance monitoring and optimization

### Team Risks
- **Risk**: Team productivity impact during transition
- **Mitigation**: Parallel development and clear communication
- **Risk**: Knowledge transfer and onboarding
- **Mitigation**: Comprehensive documentation and training

### Timeline Risks
- **Risk**: Refactoring taking longer than expected
- **Mitigation**: Phased approach with clear milestones
- **Risk**: Scope creep during implementation
- **Mitigation**: Strict adherence to specification and priorities

## Architecture Decisions

### Component Structure
- **Decision**: Section-based architecture for FundDetail
- **Rationale**: Each section has clear responsibility and can be tested independently
- **Impact**: Improved maintainability and reusability

### Utility Organization
- **Decision**: Centralized utilities with clear separation of concerns
- **Rationale**: Eliminates duplication and ensures consistency
- **Impact**: Reduced bundle size and improved developer experience

### Form System
- **Decision**: Reusable form components with centralized validation
- **Rationale**: Consistent user experience and reduced development time
- **Impact**: Faster feature development and better maintainability

### Business Logic Separation
- **Decision**: Extract business logic into custom hooks and transformers
- **Rationale**: Improves testability and reusability
- **Impact**: Better code organization and easier testing

## Conclusion

This refactoring specification provides a comprehensive roadmap for transforming the frontend codebase into a professional-grade React application. The phased approach ensures minimal disruption while achieving significant improvements in maintainability, performance, and developer experience.

The specification follows industry best practices and sets the project up for long-term success with a scalable, maintainable architecture that supports team growth and feature development. 