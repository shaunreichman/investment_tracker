# Component Architecture Refactor Specification

## Overview

Refactor the frontend component architecture to create a scalable, maintainable, and consistent structure that aligns with the recently refactored hooks layer and backend domain organization. Transform monolithic page components into a clean separation of pages, domain features, and reusable UI components following enterprise patterns.

This refactor preserves 100% of existing functionality (templates, multi-step forms, tabs, conditional forms, etc.) while improving organization, testability, and developer experience.

## Design Philosophy

### Core Principles
- **Domain-Driven Organization**: Components organized by business domain (funds, companies, entities, banking), mirroring backend structure
- **Container/Presentational Pattern**: Clear separation between data/logic (Feature components) and UI rendering (View components)
- **Explicit Layering**: Pages handle routing, Features handle business logic, Shared components handle reusable UI
- **Co-location**: Related code lives together (templates with forms, charts with features that use them)
- **Alignment with Hooks**: Component structure leverages the refactored hooks architecture (`hooks/data/funds/`, `hooks/forms/`, etc.)

### Problems We're Solving
- Monolithic page components (400-500 lines) mixing routing, data, logic, and UI
- Inconsistent form patterns (manual state vs React Hook Form)
- Unclear component ownership and boundaries
- Difficult to test components in isolation
- Hard to reuse components across different contexts
- No clear pattern for where new components should live

---

## Proposed Directory Structure

```
components/
├── domains/                    # Domain-specific components (mirrors backend)
│   ├── funds/
│   │   ├── pages/                      # Route-level components
│   │   │   ├── FundListPage.tsx
│   │   │   ├── FundDetailPage.tsx
│   │   │   └── index.ts
│   │   ├── features/                   # Feature modules (Container + View pattern)
│   │   │   ├── FundList/
│   │   │   │   ├── FundListFeature.tsx        # Container (data + logic)
│   │   │   │   ├── FundListView.tsx           # Presentational (UI)
│   │   │   │   ├── components/                # Feature-specific components
│   │   │   │   │   ├── FundTable.tsx
│   │   │   │   │   ├── FundCard.tsx
│   │   │   │   │   └── FundFilters.tsx
│   │   │   │   └── index.ts
│   │   │   ├── FundDetail/
│   │   │   ├── FundSummary/
│   │   │   ├── FundEvents/
│   │   │   └── index.ts
│   │   ├── forms/                      # Domain-specific forms
│   │   │   ├── CreateFund/
│   │   │   │   ├── CreateFundForm.tsx
│   │   │   │   ├── templates/          # Templates co-located
│   │   │   │   │   ├── templates.ts
│   │   │   │   │   └── TemplateSelector.tsx
│   │   │   │   ├── sections/
│   │   │   │   │   ├── BasicInfoSection.tsx
│   │   │   │   │   └── PerformanceSection.tsx
│   │   │   │   └── index.ts
│   │   │   ├── CreateEvent/
│   │   │   │   ├── CreateEventForm.tsx
│   │   │   │   ├── EventTypeSelector.tsx
│   │   │   │   ├── event-forms/
│   │   │   │   │   ├── NavUpdateForm.tsx
│   │   │   │   │   ├── DistributionForm.tsx
│   │   │   │   │   ├── TaxStatementForm.tsx
│   │   │   │   │   └── UnitTransactionForm.tsx
│   │   │   │   └── index.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── companies/
│   │   ├── pages/
│   │   ├── features/
│   │   │   ├── CompanyList/
│   │   │   ├── CompanyOverview/
│   │   │   ├── CompanyFunds/           # Company context showing funds
│   │   │   └── CompanyTabs/
│   │   ├── forms/
│   │   └── index.ts
│   ├── entities/
│   ├── banking/
│   └── index.ts
│
├── shared/                     # Reusable UI components
│   ├── data-display/
│   │   ├── Table/
│   │   ├── Card/
│   │   ├── Chart/
│   │   ├── Chip/
│   │   └── index.ts
│   ├── feedback/
│   │   ├── LoadingSpinner/
│   │   ├── ErrorDisplay/
│   │   ├── SuccessBanner/
│   │   └── index.ts
│   ├── forms/                  # Reusable form components ✓ COMPLETE
│   │   ├── FormTextField.tsx           # Text input
│   │   ├── FormTextArea.tsx            # Multi-line text
│   │   ├── FormNumberField.tsx         # Number with formatting
│   │   ├── FormDateField.tsx           # Date picker
│   │   ├── FormSelectField.tsx         # Dropdown select
│   │   ├── FormRadioGroup.tsx          # Radio buttons
│   │   ├── FormCheckbox.tsx            # Single checkbox
│   │   ├── FormSwitch.tsx              # Toggle switch
│   │   ├── types.ts                    # Shared types
│   │   ├── README.md                   # Documentation
│   │   └── index.ts                    # Barrel export
│   ├── navigation/
│   │   ├── Tabs/
│   │   ├── Breadcrumbs/
│   │   └── index.ts
│   ├── overlays/
│   │   ├── Modal/
│   │   ├── ConfirmDialog/
│   │   └── index.ts
│   └── index.ts
│
├── layout/                     # Application layout
│   ├── AppLayout/
│   ├── PageLayout/
│   └── index.ts
│
└── index.ts
```

---

## Component Responsibility Layers

### Pages (`domains/*/pages/`)
**What**: Route-level orchestrators only
**Responsibilities**:
- Extract route parameters
- Fetch top-level data using hooks
- Handle loading/error states
- Compose feature components
- Apply page layout

**What they DON'T do**:
- Render complex UI
- Handle business logic
- Manage form state
- Contain domain calculations

### Features (`domains/*/features/`)
**What**: Self-contained feature modules with Container/View pattern
**Responsibilities**:
- Container: Data fetching, business logic, event handlers, feature state
- View: Pure UI rendering based on props received from container
- Compose smaller presentational components
- Feature-specific modals, charts, or complex components

**Pattern**:
```
FeatureName/
├── FeatureNameFeature.tsx      # Container (data + logic)
├── FeatureNameView.tsx         # Presentational (UI)
├── components/                 # Feature-specific components
└── index.ts
```

### Forms (`domains/*/forms/`)
**What**: All forms use React Hook Form + Zod validation
**Responsibilities**:
- Form orchestration with RHF
- Validation via Zod schemas
- Templates, wizards, multi-step flows
- Conditional fields and dynamic validation

**Co-location**:
- Templates live in `forms/*/templates/`
- Form sections live in `forms/*/sections/`
- Multi-step flows live in `forms/*/steps/`

### Shared (`shared/`)
**What**: Reusable presentational components with no domain logic
**Responsibilities**:
- Pure UI rendering
- Receive all data via props
- Emit events via callback props
- Generic, domain-agnostic

---

## Implementation Strategy

### Phase 1: Foundation & Structure Setup
**Goal**: Establish new directory structure and patterns with zero breaking changes to existing code

**Design Principles**:
- Create new structure alongside existing components
- Establish patterns through example migrations
- No deletions of old code until migration complete
- Document patterns for team consistency

**Tasks**:
- [x] **COMPLETE:** Create new directory structure for `shared/` 
- [x] **COMPLETE:** Move and organize form components in `shared/forms/`
  - [x] Moved all form components from `components/forms/` → `components/shared/forms/`
  - [x] FormTextField - Text input with RHF integration
  - [x] FormTextArea - Multi-line text input
  - [x] FormNumberField - Number with formatting support
  - [x] FormDateField - Native date picker
  - [x] FormSelectField - Dropdown with options
  - [x] FormRadioGroup - Radio button group
  - [x] FormCheckbox - Single checkbox for booleans
  - [x] FormSwitch - Toggle switch for booleans
  - [x] Shared types file (SelectOption, RadioOption)
  - [x] Comprehensive README with examples
  - [x] Updated barrel exports in `shared/forms/index.ts`
  - [x] Updated `shared/index.ts` to export form components
  - [x] Updated all imports (NavUpdateForm.new.tsx)
- [ ] Create new directory structure (`domains/`)
- [ ] Create README.md in each major directory explaining purpose and patterns
- [ ] Audit and organize existing shared UI components (feedback, data-display already done)
- [ ] Document Container/View pattern with code examples

**Success Criteria**:
- New directory structure exists with organized subdirectories
- Documentation exists for Container/View pattern
- All existing functionality still works (nothing broken)
- TypeScript compilation passes with zero errors
- Pattern is clear enough for team to follow

---

### Phase 2: High-Value Feature Migration
**Goal**: Migrate most complex, most-used features to establish patterns at scale

**Design Principles**:
- Migrate complete features (not partial)
- Preserve 100% of existing functionality
- Extract business logic to Feature containers
- Extract UI to View presentational components
- Test thoroughly after each feature migration

**Priority Features**:
1. **Fund Detail** → `domains/funds/pages/FundDetailPage.tsx` + `features/FundSummary/` + `features/FundEvents/`
2. **Company Overview** → `domains/companies/pages/CompanyDetailPage.tsx` + `features/CompanyOverview/` + `features/CompanyFunds/`
3. **Event Creation** → `domains/funds/forms/CreateEvent/` with conditional forms

**Tasks**:
- [ ] Migrate Fund Detail page (FundDetailPage + FundSummary feature + FundEvents feature)
- [ ] Extract FundSummary sections (Equity, Performance, Details, Transactions, Chart)
- [ ] Migrate FundEvents table with grouping logic to feature module
- [ ] Migrate Company Detail page (CompanyDetailPage + tab features)
- [ ] Migrate Company Overview tab to feature module
- [ ] Migrate Company Funds tab to feature module
- [ ] Migrate Event Creation form with event type selector and conditional forms
- [ ] Extract NavUpdateForm, DistributionForm, TaxStatementForm to `domains/funds/forms/CreateEvent/event-forms/`
- [ ] Update route definitions to use new page components
- [ ] Test all migrated features for functionality preservation

**Success Criteria**:
- Fund Detail page works identically to before (sidebar, events table, all interactions)
- Company Detail page works identically with all tabs functioning
- Event Creation works with all event types and conditional fields
- No regressions in functionality
- Loading states, error handling, and success feedback work consistently
- Container/View pattern clear in all migrated features
- TypeScript compilation passes with zero errors

---

### Phase 3: Forms Migration to React Hook Form + Zod
**Goal**: Migrate all remaining forms from manual state management to React Hook Form + Zod

**Design Principles**:
- All forms use React Hook Form for state management
- All validation defined in Zod schemas (`hooks/forms/schemas/`)
- Consistent validation display rules (red asterisk for required, errors on touched)
- Leverage existing FormTextField, FormNumberField, FormDateField components
- Templates and multi-step flows preserved and improved

**Tasks**:
- [ ] Migrate NavUpdateForm to RHF + Zod (reference existing FormTextField pattern)
- [ ] Migrate DistributionForm to RHF + Zod with conditional field logic
- [ ] Migrate TaxStatementForm to RHF + Zod with complex validation
- [ ] Migrate UnitTransactionForm to RHF + Zod
- [ ] Migrate CostBasedEventForm to RHF + Zod
- [ ] Migrate CreateFundForm to RHF + Zod preserving template functionality
- [ ] Move template definitions to `domains/funds/forms/CreateFund/templates/`
- [ ] Create TemplateSelector component using template data
- [ ] Migrate CreateCompanyForm to RHF + Zod
- [ ] Migrate CreateEntityForm to RHF + Zod
- [ ] Remove manual form state management code (formData, validationErrors, onInputChange)
- [ ] Update all form containers to use useForm hook

**Success Criteria**:
- All forms use React Hook Form + Zod validation
- Template selection works identically in CreateFundForm
- Conditional fields and validation work correctly (DistributionForm, TaxStatementForm)
- Validation display is consistent across all forms (required indicators, error messages on touch)
- Form submission integrates with mutation hooks from data layer
- No manual form state management remains
- TypeScript compilation passes with full type inference from Zod schemas
- All forms pass existing functionality tests

---

### Phase 4: Remaining Domain Migrations
**Goal**: Complete migration of all remaining components to new structure

**Design Principles**:
- Follow established patterns from Phase 2
- Maintain feature completeness
- Extract reusable components to `shared/` when appropriate
- Keep domain-specific components in domain directories

**Tasks**:
- [ ] Migrate Fund List page and feature
- [ ] Migrate Company List page and feature
- [ ] Migrate Entity List page and feature
- [ ] Migrate Entity management forms
- [ ] Migrate Banking domain components (when ready)
- [ ] Migrate remaining tabs (Activity, Analysis) for Company Detail
- [ ] Extract common table components to `shared/data-display/Table/`
- [ ] Extract common card components to `shared/data-display/Card/`
- [ ] Update all route definitions to point to new page components
- [ ] Audit for reusable components that should move to `shared/`

**Success Criteria**:
- All pages and features migrated to new structure
- All functionality preserved across all domains
- Reusable components properly extracted to `shared/`
- No duplicate components across domains
- TypeScript compilation passes with zero errors
- All routes point to new structure

---

### Phase 5: Cleanup & Optimization
**Goal**: Remove old code, optimize performance, and polish the new architecture

**Design Principles**:
- Remove old code only after confirming new code works
- Optimize component rendering with React.memo, useMemo, useCallback where needed
- Ensure accessibility standards are met
- Document component architecture for team

**Tasks**:
- [ ] Delete old component files that have been fully migrated
- [ ] Remove old directory structure (`components/companies/`, `components/fund/`, `components/entities/`)
- [ ] Update all remaining imports across codebase to use new structure
- [ ] Run TypeScript compilation to catch any broken imports
- [ ] Add React.memo to presentational components that receive stable props
- [ ] Add useMemo for expensive calculations in feature containers
- [ ] Add useCallback for event handlers passed to child components
- [ ] Run accessibility audit on all migrated components
- [ ] Verify keyboard navigation works in all features
- [ ] Run bundle size analysis to identify optimization opportunities
- [ ] Update component documentation with architecture patterns
- [ ] Create component catalog or Storybook for shared components (optional)

**Success Criteria**:
- Old component code completely removed
- Old directory structure removed
- All imports updated and TypeScript compiles with zero errors
- No performance regressions (components render efficiently)
- Bundle size not significantly increased
- Accessibility standards met (keyboard navigation, ARIA labels)
- Documentation updated with new architecture
- Team understands patterns and can add new features following structure

---

## Overall Success Metrics

### Organizational
- All components organized into clear layers: domains → pages/features/forms + shared + layout
- 100% of features follow Container/View pattern
- Zero business logic in presentational components
- Consistent directory structure across all domains

### Code Quality
- TypeScript compilation passes with zero errors and warnings
- All forms use React Hook Form + Zod validation
- Consistent validation display rules across all forms
- No prop drilling deeper than 2-3 levels
- All data fetching uses refactored hooks from `hooks/` directory

### Functional
- 100% of existing functionality preserved (templates, conditional forms, tabs, modals, filters, etc.)
- All features work identically to before migration
- Loading states, error handling, and success feedback consistent across all features

### Performance
- No performance degradation from refactor
- Proper memoization applied where beneficial
- No unnecessary re-renders in production
- Bundle size within acceptable range

### Developer Experience
- New developers can locate components within 10 seconds based on domain and feature
- Clear patterns for adding new features (follow existing domain structure)
- Easy to test components in isolation (Container/View separation)
- Reusable components well-documented in `shared/`
- Team can confidently add new features following established patterns

