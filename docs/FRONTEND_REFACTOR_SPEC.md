# Frontend Refactor Specification

## Overview

This specification details the complete refactoring of the frontend codebase from the current flat component structure to a domain-driven architecture that matches the backend organization. The refactor will reorganize all files into domain-based directories (`company/`, `banking/`, `fund/`, `entity/`, `rates/`, `shared/`) while maintaining 100% visual consistency - the UI and theme must remain identical.

**Goal**: Transform the frontend structure to match backend domains, improve maintainability and scalability, without any changes to the user experience, appearance, or functionality.

## Design Philosophy

- **Domain-Driven Alignment**: Frontend structure mirrors backend domains for consistency across the stack
- **Feature-Based Component Organization**: Group components by feature/functionality within domains (e.g., `company-list/`, `company-form/`)
- **Zero Visual Changes**: All UI components, styling, theme, and user interactions must remain identical
- **Preserve Functionality**: All existing features must work exactly as before the refactor
- **Incremental Migration**: Structure changes happen file-by-file, maintaining working state throughout
- **Barrel Export Strategy**: Public domain API via `index.ts`, direct imports within features to avoid circular dependencies
- **Centralized Routing**: Single source of truth for routes via `routes/index.tsx` that imports domain route definitions
- **Page vs Component Separation**: Page-level components (route-mounted, stateful, orchestrate multiple features) live in `pages/`, while reusable feature components live in `components/`

## Proposed Final File Structure

After the refactor, the frontend structure will match the backend domains and follow a clear domain-driven architecture:

```
frontend/src/
├── routes/
│   └── index.tsx                    # Centralized routes (imports domain routes)
│
├── company/                          # Company domain
│   ├── api/                          # HTTP API calls to backend
│   │   ├── companyApi.ts
│   │   └── index.ts
│   ├── types/                        # Domain-specific TypeScript types/interfaces
│   │   ├── company.ts
│   │   ├── contact.ts
│   │   ├── enums.ts                  # Company-specific enums (or reference shared)
│   │   └── index.ts
│   ├── hooks/                        # Custom hooks for company logic
│   │   ├── useCompanies.ts
│   │   ├── useContacts.ts
│   │   └── index.ts
│   ├── components/                   # Feature-based nested components
│   │   ├── company-list/             # Feature: list view
│   │   │   ├── CompanyList.tsx
│   │   │   ├── CompanyTable.tsx
│   │   │   ├── CompanyFilters.tsx
│   │   │   └── index.ts
│   │   ├── company-details-tab/      # Feature: details tab
│   │   │   ├── CompanyDetailsTab.tsx
│   │   │   ├── components/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── overview-tab/              # Feature: overview tab
│   │   │   ├── OverviewTab.tsx
│   │   │   ├── components/
│   │   │   ├── types/
│   │   │   └── index.ts
│   │   ├── funds-tab/                 # Feature: funds tab
│   │   │   ├── FundsTab.tsx
│   │   │   ├── components/
│   │   │   └── index.ts
│   │   ├── analysis-tab/              # Feature: analysis tab
│   │   │   ├── AnalysisTab.tsx
│   │   │   ├── components/
│   │   │   └── index.ts
│   │   ├── activity-tab/              # Feature: activity tab
│   │   │   ├── ActivityTab.tsx
│   │   │   ├── components/
│   │   │   └── index.ts
│   │   ├── create-fund/               # Feature: create fund
│   │   │   ├── CreateFundModal.tsx
│   │   │   └── index.ts
│   │   ├── create-company-modal/      # Feature: create company
│   │   │   ├── CreateCompanyModal.tsx
│   │   │   └── index.ts
│   │   └── index.ts                   # Public API barrel export
│   ├── pages/                         # Page components
│   │   ├── AllCompaniesPage.tsx       # Landing page at `/` - shows all companies list
│   │   ├── CompanyPage.tsx            # Individual company detail at `/companies/:companyId`
│   │   └── index.ts
│   ├── routes.tsx                     # Domain route definitions
│   └── index.ts                       # Domain barrel export (public API)
│
├── fund/                              # Fund domain
│   ├── api/
│   │   ├── fundApi.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── fund.ts
│   │   ├── fundEvent.ts
│   │   ├── fundTaxStatement.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useFunds.ts
│   │   ├── useFundDetail.ts
│   │   ├── useFundEvents.ts
│   │   └── index.ts
│   ├── components/
│   │   ├── fund-detail/               # Feature: fund detail sections and sub-components
│   │   │   ├── FundDetailHeader.tsx
│   │   │   ├── summary/               # Summary section components
│   │   │   │   ├── EquitySection.tsx
│   │   │   │   ├── ExpectedPerformanceSection.tsx
│   │   │   │   ├── CompletedPerformanceSection.tsx
│   │   │   │   ├── FundDetailsSection.tsx
│   │   │   │   ├── TransactionSummarySection.tsx
│   │   │   │   └── UnitPriceChartSection.tsx
│   │   │   ├── table/                 # Events table components
│   │   │   │   ├── TableContainer.tsx
│   │   │   │   ├── TableHeader.tsx
│   │   │   │   ├── TableBody.tsx
│   │   │   │   ├── EventRow.tsx
│   │   │   │   └── ...
│   │   │   └── index.ts
│   │   ├── fund-events/                # Feature: fund events modal
│   │   │   ├── CreateFundEventModal.tsx
│   │   │   ├── components/
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── pages/                         # Page-level route-mounted components
│   │   ├── FundPage.tsx               # Main fund page (manages state, data fetching, orchestrates)
│   │   └── index.ts
│   ├── routes.tsx
│   └── index.ts
│
├── banking/                           # Banking domain
│   ├── api/
│   │   ├── bankingApi.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── bank.ts
│   │   ├── bankAccount.ts
│   │   ├── bankAccountBalance.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useBanks.ts
│   │   ├── useBankAccounts.ts
│   │   └── index.ts
│   ├── components/                    # Feature-based nesting (if any)
│   ├── pages/                         # Banking pages (if any)
│   ├── routes.tsx                     # Banking routes (if any)
│   └── index.ts
│
├── entity/                            # Entity domain
│   ├── api/
│   │   ├── entityApi.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── entity.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useEntities.ts
│   │   └── index.ts
│   ├── components/
│   │   ├── entity-list/                # Feature: entity list
│   │   │   ├── EntityList.tsx
│   │   │   ├── EntityTable.tsx
│   │   │   ├── EntityCards.tsx
│   │   │   ├── EntityFilters.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── pages/
│   │   ├── AllEntitiesPage.tsx        # Landing page for entities (if separate route needed)
│   │   └── index.ts
│   ├── routes.tsx
│   └── index.ts
│
├── rates/                             # Rates domain
│   ├── api/
│   │   ├── ratesApi.ts
│   │   └── index.ts
│   ├── types/
│   │   ├── riskFreeRate.ts
│   │   ├── fxRate.ts
│   │   ├── enums.ts
│   │   └── index.ts
│   ├── hooks/
│   │   ├── useRiskFreeRates.ts
│   │   ├── useFxRates.ts
│   │   └── index.ts
│   ├── components/                    # Rates components (if any)
│   ├── pages/
│   ├── routes.tsx
│   └── index.ts
│
├── shared/                            # Shared cross-domain resources
│   ├── types/                         # Cross-domain types
│   │   ├── enums/
│   │   │   ├── shared.enums.ts        # Country, Currency, SortOrder
│   │   │   └── index.ts
│   │   ├── errors.ts                  # ErrorInfo, ErrorType
│   │   ├── dto/
│   │   │   ├── api-response.ts
│   │   │   ├── response-codes.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── ui/                            # Reusable UI components
│   │   ├── data-display/
│   │   │   ├── StatCard.tsx
│   │   │   ├── DataCard.tsx
│   │   │   ├── SummaryCard.tsx
│   │   │   ├── StatusChip.tsx
│   │   │   └── index.ts
│   │   ├── feedback/
│   │   │   ├── ErrorDisplay.tsx
│   │   │   ├── ErrorToast.tsx
│   │   │   ├── DomainErrorBoundary.tsx
│   │   │   ├── LoadingSpinner.tsx
│   │   │   └── index.ts
│   │   ├── forms/
│   │   │   ├── FormTextField.tsx
│   │   │   ├── FormNumberField.tsx
│   │   │   ├── FormSelectField.tsx
│   │   │   └── index.ts
│   │   ├── navigation/
│   │   │   ├── TabNavigation.tsx
│   │   │   ├── Breadcrumbs.tsx
│   │   │   └── index.ts
│   │   ├── overlays/
│   │   │   ├── ConfirmDialog.tsx
│   │   │   ├── FormModal.tsx
│   │   │   └── index.ts
│   │   ├── layout/                     # App-level layout components
│   │   │   ├── RouteLayout.tsx
│   │   │   ├── MainSidebar.tsx
│   │   │   ├── TopBar.tsx
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── hooks/                         # Cross-domain hooks
│   │   ├── core/                      # Core API hooks
│   │   │   ├── api/
│   │   │   ├── error/
│   │   │   └── index.ts
│   │   ├── ui/                        # UI hooks
│   │   │   ├── useErrorAutoDismiss.ts
│   │   │   ├── useErrorDetailsToggle.ts
│   │   │   └── index.ts
│   │   └── index.ts
│   ├── utils/                         # Pure utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── helpers.ts
│   │   └── index.ts
│   └── index.ts                       # Shared domain barrel export
│
├── store/                             # Global app state (Zustand)
│   ├── useAppStore.ts
│   ├── AppStoreProvider.tsx
│   └── index.ts
│
├── theme/                             # Theme configuration (unchanged)
│   ├── dockerTheme.ts
│   ├── DockerThemeProvider.tsx
│   └── index.ts
│
├── config/                            # Configuration (unchanged)
│   └── environment.ts
│
├── test-utils/                        # Test utilities (unchanged)
│   ├── mock-api.ts
│   ├── mock-data.ts
│   └── render-utils.tsx
│
├── App.tsx                            # Main app component (uses routes/index.tsx)
├── index.tsx                          # Entry point
└── index.css                         # Global styles
```

### Key Structure Notes:

1. **Domain Structure**: Each domain (`company/`, `fund/`, `banking/`, `entity/`, `rates/`) follows the same pattern:
   - `api/` - HTTP API calls
   - `types/` - Domain-specific types
   - `hooks/` - Domain-specific hooks
   - `components/` - Feature-based nested components
   - `pages/` - Page components
   - `routes.tsx` - Domain route definitions
   - `index.ts` - Domain barrel export

2. **Page vs Component Separation**: Understanding when to use `pages/` vs `components/`:
   - **Pages** (`domain/pages/`): Route-mounted, top-level orchestration components that manage state, data fetching, error handling, and coordinate multiple features/components. These are the main entry points for routes. Examples: `AllCompaniesPage.tsx` (mounts at `/`, shows all companies list), `CompanyPage.tsx` (mounts at `/companies/:companyId`, orchestrates tabs), `FundPage.tsx` (mounts at `/funds/:fundId`, orchestrates fund detail view), `AllEntitiesPage.tsx` (mounts at `/entities`, shows all entities list)
   - **Components** (`domain/components/`): Reusable, composable feature components that **receive data via props** and handle presentation logic. Components should NOT fetch their own data - data fetching is the responsibility of pages or parent components. Organized by feature with nested sub-components. Examples: `OverviewTab.tsx`, `FundDetailHeader.tsx`, `CompanyList.tsx`, `EquitySection.tsx`, `TableContainer.tsx`
   - **Data Flow Rule**: Components receive data via props (`data`, `loading`, `error`, callbacks). Pages fetch data using hooks and pass it down. This creates clear separation: pages orchestrate data, components present UI.
   - **Decision Criteria**: 
     - If it's mounted to a route → `pages/`
     - If it uses `useParams()` or routing hooks → `pages/`
     - If it fetches data (uses API hooks) → Should be `pages/` OR parent should fetch and pass down
     - If it orchestrates multiple features/components → `pages/`
     - If it receives data via props → `components/`
     - If it's reusable across different contexts → `components/`
   - **Key Insight**: The page is the **orchestrator** (manages state and data flow), while components are the **sections** (receive props, handle presentation). The page imports and composes components, components don't import pages.
   - **Note**: Some components like `CompanyList` and `EntityList` currently fetch their own data. During refactor, these should be updated to receive data via props, with their parent pages (`AllCompaniesPage` and `AllEntitiesPage`) handling data fetching for consistency with the architecture pattern.

3. **Feature-Based Component Nesting**: Components are grouped by feature (e.g., `company-list/`, `company-form/`) rather than being flat, with each feature folder containing related components, types, and an `index.ts` file.

4. **Shared Domain**: Cross-domain concerns live in `shared/`:
   - `shared/types/` - Enums, errors, DTOs used by multiple domains
   - `shared/ui/` - Reusable UI components
   - `shared/hooks/` - Cross-domain hooks
   - `shared/utils/` - Pure utility functions

5. **Layout Components**: App-level layout components (RouteLayout, MainSidebar, TopBar) are in `shared/ui/layout/` as they are cross-cutting reusable UI components, consistent with the domain-driven structure.

6. **Barrel Exports**: Each domain has an `index.ts` file that exports the public API, allowing clean imports like `import { CompanyList } from '@/company'`.

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths in this spec are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Phase 1: Foundation - Shared Domain Structure
**Goal**: Establish the `shared/` domain structure and move cross-cutting concerns

**Design Principles**:
- Move shared types (enums, errors, DTOs) to `shared/types/` from top-level `types/`
- Preserve all existing shared UI components in `shared/ui/` (currently `components/shared/`)
- Create barrel exports for shared domain public API
- Maintain all imports working throughout the process

**Tasks**:
- [ ] Create `src/shared/types/` directory structure
- [ ] Move `types/enums/` → `shared/types/enums/` (all enum files)
- [ ] Move `types/errors.ts` → `shared/types/errors.ts`
- [ ] Move `types/dto/` → `shared/types/dto/` (all DTO files)
- [ ] Update `shared/types/index.ts` barrel export
- [ ] Create `src/shared/ui/` directory
- [ ] Move `components/shared/data-display/` → `shared/ui/data-display/`
- [ ] Move `components/shared/feedback/` → `shared/ui/feedback/`
- [ ] Move `components/shared/forms/` → `shared/ui/forms/`
- [ ] Move `components/shared/navigation/` → `shared/ui/navigation/`
- [ ] Move `components/shared/overlays/` → `shared/ui/overlays/`
- [ ] Create `src/shared/ui/layout/` directory
- [ ] Move `components/layout/RouteLayout.tsx` → `shared/ui/layout/RouteLayout.tsx`
- [ ] Move `components/layout/MainSidebar.tsx` → `shared/ui/layout/MainSidebar.tsx`
- [ ] Move `components/layout/TopBar.tsx` → `shared/ui/layout/TopBar.tsx`
- [ ] Create `shared/ui/layout/index.ts` barrel export
- [ ] Update `shared/ui/index.ts` barrel export to include layout components
- [ ] Create `src/shared/hooks/` directory
- [ ] Move `hooks/ui/` → `shared/hooks/ui/`
- [ ] Move `hooks/core/` → `shared/hooks/core/` (or keep at root - evaluate)
- [ ] Update `shared/hooks/index.ts` barrel export
- [ ] Create `src/shared/utils/` directory
- [ ] Move utility functions from `utils/` to `shared/utils/` (evaluate which are truly shared)
- [ ] Update all imports across codebase to use new shared paths
- [ ] Run TypeScript compilation to verify no broken imports: `npx tsc --noEmit`
- [ ] Test application to ensure all shared components work identically

**Success Criteria**:
- All shared types, components, hooks, and utils organized in `shared/` domain
- Zero TypeScript compilation errors
- All imports updated and working
- Application runs and displays identically to before refactor
- No visual or functional changes to any UI components

### Phase 2: Core Domains - Company Domain
**Goal**: Reorganize company-related code into `company/` domain structure

**Design Principles**:
- Move all company API calls to `company/api/`
- Move company types to `company/types/`
- Move company hooks to `company/hooks/`
- Reorganize company components with feature-based nesting
- Create domain routes in `company/routes.tsx`
- Create domain barrel export in `company/index.ts`

**Tasks**:
- [ ] Create `src/company/` directory structure
- [ ] Create `src/company/api/` directory
- [ ] Move `services/api/company.api.ts` → `company/api/companyApi.ts`
- [ ] Create `company/api/index.ts` barrel export
- [ ] Create `src/company/types/` directory
- [ ] Move `types/models/company.ts` → `company/types/company.ts`
- [ ] Move company-related enums from `types/enums/company.enums.ts` → `company/types/enums.ts` (or reference from shared)
- [ ] Create `company/types/index.ts` barrel export
- [ ] Create `src/company/hooks/` directory
- [ ] Move `hooks/data/companies/` → `company/hooks/`
- [ ] Rename files to remove `companies/` namespace (e.g., `useCompanies.ts` not `companies/useCompanies.ts`)
- [ ] Create `company/hooks/index.ts` barrel export
- [ ] Create `src/company/components/` directory
- [ ] Move `components/companies/company-list/` → `company/components/company-list/`
- [ ] Refactor `CompanyList` to receive data via props: Remove `useCompanies()` hook, accept `data`, `loading`, `error`, `onRefresh` as props (parent page will fetch data)
- [ ] Create `src/company/pages/` directory
- [ ] Rename `components/OverallDashboard.tsx` → `company/pages/AllCompaniesPage.tsx`
- [ ] Remove entity management section from `AllCompaniesPage` (EntityList and CreateEntityModal - will move to separate entity page)
- [ ] Update `AllCompaniesPage` to fetch company data using `useCompanies()` hook and pass to `CompanyList` component
- [ ] Move `components/companies/company-details-tab/` → `company/components/company-details-tab/` (evaluate if this should be `details-tab/`)
- [ ] Move `components/companies/overview-tab/` → `company/components/overview-tab/`
- [ ] Move `components/companies/funds-tab/` → `company/components/funds-tab/`
- [ ] Move `components/companies/analysis-tab/` → `company/components/analysis-tab/`
- [ ] Move `components/companies/activity-tab/` → `company/components/activity-tab/`
- [ ] Move `components/companies/create-fund/` → `company/components/create-fund/`
- [ ] Move `components/CreateCompanyModal.tsx` → `company/components/create-company-modal/` (reorganize as feature folder)
- [ ] Update all component imports within company domain
- [ ] Create `company/components/index.ts` barrel export for public API
- [ ] Move `components/companies/CompaniesPage.tsx` → `company/pages/CompanyPage.tsx`
- [ ] Create `company/pages/index.ts` barrel export
- [ ] Create `src/company/routes.tsx` with company route definitions
- [ ] Create `src/company/index.ts` domain barrel export
- [ ] Update all imports across codebase to use new company domain paths
- [ ] Run TypeScript compilation: `npx tsc --noEmit`
- [ ] Test company page, company list, and all company-related functionality

**Success Criteria**:
- All company code organized in `company/` domain
- Zero TypeScript compilation errors
- All company pages and components work identically
- Visual appearance matches exactly
- Feature-based component nesting implemented
- Domain routes defined in `company/routes.tsx`

### Phase 3: Core Domains - Fund Domain
**Goal**: Reorganize fund-related code into `fund/` domain structure

**Design Principles**:
- Move all fund API calls to `fund/api/`
- Move fund types to `fund/types/`
- Move fund hooks to `fund/hooks/`
- Reorganize fund components with feature-based nesting
- Create domain routes in `fund/routes.tsx`
- Create domain barrel export in `fund/index.ts`

**Tasks**:
- [ ] Create `src/fund/` directory structure
- [ ] Create `src/fund/api/` directory
- [ ] Move `services/api/fund.api.ts` → `fund/api/fundApi.ts`
- [ ] Create `fund/api/index.ts` barrel export
- [ ] Create `src/fund/types/` directory
- [ ] Move `types/models/fund.ts` → `fund/types/fund.ts`
- [ ] Move fund-related enums from `types/enums/fund.enums.ts` → `fund/types/enums.ts` (or reference from shared)
- [ ] Create `fund/types/index.ts` barrel export
- [ ] Create `src/fund/hooks/` directory
- [ ] Move `hooks/data/funds/` → `fund/hooks/`
- [ ] Rename files to remove `funds/` namespace
- [ ] Create `fund/hooks/index.ts` barrel export
- [ ] Create `src/fund/components/` directory
- [ ] Create `src/fund/components/fund-detail/` feature directory
- [ ] Move `components/fund/detail/FundDetailHeader.tsx` → `fund/components/fund-detail/FundDetailHeader.tsx`
- [ ] Move `components/fund/detail/summary/` → `fund/components/fund-detail/summary/`
- [ ] Move `components/fund/detail/table/` → `fund/components/fund-detail/table/`
- [ ] Create `fund/components/fund-detail/index.ts` barrel export
- [ ] Move `components/fund/events/` → `fund/components/fund-events/` (reorganize as feature folder)
- [ ] Create `fund/components/index.ts` barrel export for public API
- [ ] Create `src/fund/pages/` directory
- [ ] Extract `FundPage.tsx` from `components/fund/detail/FundDetail.tsx`: Keep orchestration logic (useParams, state, data fetching, error handling) in page; move presentation sections to component directory
- [ ] Create `fund/pages/index.ts` barrel export
- [ ] Create `src/fund/routes.tsx` with fund route definitions
- [ ] Create `src/fund/index.ts` domain barrel export
- [ ] Update all imports across codebase to use new fund domain paths
- [ ] Run TypeScript compilation: `npx tsc --noEmit`
- [ ] Test fund detail page and all fund-related functionality

**Success Criteria**:
- All fund code organized in `fund/` domain
- Zero TypeScript compilation errors
- All fund pages and components work identically
- Visual appearance matches exactly
- Feature-based component nesting implemented
- Domain routes defined in `fund/routes.tsx`

### Phase 4: Supporting Domains - Banking, Entity, Rates
**Goal**: Reorganize banking, entity, and rates code into their respective domain structures

**Design Principles**:
- Follow the same pattern established in company and fund domains
- Move API, types, hooks, components to respective domains
- Create domain routes and barrel exports
- Maintain all existing functionality

**Tasks**:
- [ ] Create `src/banking/` directory structure
- [ ] Move `services/api/banking.api.ts` → `banking/api/bankingApi.ts`
- [ ] Move `types/models/banking.ts` → `banking/types/banking.ts`
- [ ] Move banking enums → `banking/types/enums.ts`
- [ ] Move `hooks/data/banking/` → `banking/hooks/`
- [ ] Move banking components (if any) → `banking/components/`
- [ ] Create `banking/api/index.ts`, `banking/types/index.ts`, `banking/hooks/index.ts` barrel exports
- [ ] Create `banking/routes.tsx` and `banking/index.ts`
- [ ] Create `src/entity/` directory structure
- [ ] Move `services/api/entity.api.ts` → `entity/api/entityApi.ts`
- [ ] Move `types/models/entity.ts` → `entity/types/entity.ts`
- [ ] Move entity enums → `entity/types/enums.ts`
- [ ] Move `hooks/data/entities/` → `entity/hooks/`
- [ ] Move `components/entities/` → `entity/components/` (maintain feature structure)
- [ ] Create `entity/components/index.ts` barrel export for public API
- [ ] Create `src/entity/pages/` directory
- [ ] Create `entity/pages/AllEntitiesPage.tsx`: Extract entity management section from old `OverallDashboard` (EntityList and CreateEntityModal integration)
- [ ] Refactor `EntityList` to receive data via props: Remove `useEntities()` hook, accept `data`, `loading`, `error`, `onRefresh` as props (parent page will fetch data)
- [ ] Update `AllEntitiesPage` to fetch entity data using `useEntities()` hook and pass to `EntityList` component
- [ ] Create `entity/pages/index.ts` barrel export
- [ ] Create `entity/api/index.ts`, `entity/types/index.ts`, `entity/hooks/index.ts` barrel exports
- [ ] Create `entity/routes.tsx` and `entity/index.ts`
- [ ] Create `src/rates/` directory structure
- [ ] Move `services/api/rates.api.ts` → `rates/api/ratesApi.ts`
- [ ] Move `types/models/rates.ts` → `rates/types/rates.ts`
- [ ] Move rates enums → `rates/types/enums.ts`
- [ ] Move `hooks/data/rates/` → `rates/hooks/`
- [ ] Move rates components (if any) → `rates/components/`
- [ ] Create `rates/api/index.ts`, `rates/types/index.ts`, `rates/hooks/index.ts` barrel exports
- [ ] Create `rates/routes.tsx` and `rates/index.ts`
- [ ] Update all imports across codebase
- [ ] Run TypeScript compilation: `npx tsc --noEmit`
- [ ] Test all banking, entity, and rates functionality

**Success Criteria**:
- All banking, entity, and rates code organized in respective domains
- Zero TypeScript compilation errors
- All functionality works identically
- Visual appearance matches exactly

### Phase 5: Routing Centralization
**Goal**: Centralize all routes via `routes/index.tsx` importing domain route definitions

**Design Principles**:
- Single source of truth for all routes in `routes/index.tsx`
- Domain routes defined in each domain's `routes.tsx` file
- Maintain all existing route paths and behavior
- Update `App.tsx` to import from centralized routes

**Tasks**:
- [ ] Create `src/routes/` directory
- [ ] Create `src/routes/index.tsx` as centralized route configuration
- [ ] Import route definitions from `company/routes.tsx`
- [ ] Import route definitions from `fund/routes.tsx`
- [ ] Import route definitions from `banking/routes.tsx` (if any)
- [ ] Import route definitions from `entity/routes.tsx` (includes `AllEntitiesPage` at `/entities` if needed)
- [ ] Import route definitions from `rates/routes.tsx` (if any)
- [ ] Define `/` route to use `AllCompaniesPage` from `company/pages/AllCompaniesPage.tsx`
- [ ] Define `/companies/:companyId` route to use `CompanyPage` from `company/pages/CompanyPage.tsx`
- [ ] Define `/entities` route to use `AllEntitiesPage` from `entity/pages/AllEntitiesPage.tsx` (if separate route needed)
- [ ] Update `App.tsx` to use routes from `routes/index.tsx`
- [ ] Remove route definitions from `App.tsx`
- [ ] Ensure all route wrappers (like `FundDetailWrapper`, `CompaniesPageWrapper`) are handled appropriately
- [ ] Test all routes work correctly
- [ ] Verify navigation and routing behavior matches exactly

**Success Criteria**:
- All routes centralized in `routes/index.tsx`
- Zero TypeScript compilation errors
- All routes work identically to before refactor
- Navigation behavior unchanged
- Domain routes defined in their respective `routes.tsx` files

### Phase 6: Cleanup and Verification
**Goal**: Remove old file structure, verify everything works, and finalize the refactor

**Design Principles**:
- Remove empty old directories
- Verify no duplicate files or orphaned imports
- Ensure all barrel exports work correctly
- Validate import paths use domain structure
- Confirm theme and styling remain unchanged

**Tasks**:
- [ ] Remove old `components/OverallDashboard.tsx` file (renamed to `company/pages/AllCompaniesPage.tsx`)
- [ ] Remove old `components/companies/` directory (if empty)
- [ ] Remove old `components/fund/` directory (if empty)
- [ ] Remove old `components/entities/` directory (if empty)
- [ ] Remove old `services/api/` files (already moved)
- [ ] Remove old `hooks/data/` files (already moved)
- [ ] Remove old `types/models/` files (already moved)
- [ ] Remove old `types/enums/` files (already moved)
- [ ] Remove old `types/dto/` files (already moved)
- [ ] Verify no imports reference old paths (search codebase)
- [ ] Update any remaining old imports to use new domain structure
- [ ] Run full TypeScript compilation: `npx tsc --noEmit`
- [ ] Run application and test all major user flows:
  - [ ] AllCompaniesPage (landing page at `/`) loads and displays correctly
  - [ ] AllEntitiesPage loads and displays correctly (if separate route)
  - [ ] Company list and details work
  - [ ] Fund details and events work
  - [ ] All forms and modals work
  - [ ] Navigation and routing work
  - [ ] Theme and styling match exactly
- [ ] Verify no console errors or warnings
- [ ] Check that all barrel exports work (`index.ts` files)
- [ ] Document any remaining considerations or future improvements

**Success Criteria**:
- All old directories and files removed
- Zero TypeScript compilation errors
- Zero runtime errors or warnings
- All functionality works identically
- Visual appearance matches exactly (theme preserved)
- All imports use new domain structure
- All barrel exports working correctly

## Overall Success Metrics

- **Structure Alignment**: Frontend domains match backend domains exactly (`company/`, `banking/`, `fund/`, `entity/`, `rates/`, `shared/`)
- **Zero Breaking Changes**: All existing functionality works identically after refactor
- **Visual Consistency**: UI, theme, and styling remain 100% unchanged
- **Code Organization**: Feature-based component nesting implemented across all domains
- **Import Clarity**: All imports use clean domain paths (e.g., `import { CompanyList } from '@/company'`)
- **Routing Centralization**: Single source of truth for routes in `routes/index.tsx`
- **Type Safety**: Zero TypeScript compilation errors
- **No Regressions**: All tests pass (if applicable) and manual testing confirms no functionality lost

## Key Considerations

1. **Theme Preservation**: The Docker theme in `theme/dockerTheme.ts` must remain completely unchanged. No theme-related files should be moved or modified.

2. **Layout Components**: Components in `components/layout/` (RouteLayout, MainSidebar, TopBar) should remain at root level or be evaluated for shared domain placement.

3. **Store and Configuration**: Files in `store/`, `config/`, `test-utils/` should remain at root level as they are cross-cutting concerns.

4. **Data Fetching Edge Cases**: 
   - **General Rule**: Components should receive data via props. Pages orchestrate data fetching.
   - **Modals**: Modals that fetch independent data (e.g., `CreateFundModal` fetching entities for dropdown) may fetch their own data if the data is specific to the modal and not shared elsewhere. However, prefer passing props when the data is available from parent.
   - **Self-Contained Components**: If a component is truly self-contained and reusable across different contexts where parent data isn't available, it may fetch its own data. Evaluate case-by-case - prefer props when possible.

5. **Incremental Migration**: Each phase should be completed and verified before moving to the next. Do not move to Phase 2 until Phase 1 is fully complete and tested.

6. **Import Updates**: As files are moved, imports must be updated immediately to maintain a working state. Use IDE refactoring tools where possible.

7. **Barrel Exports**: Domain-level `index.ts` files should export public API only. Internal feature imports should use direct paths.

8. **Old Hooks**: There are old hooks in `hooks/formsold/`, `hooks/fundsold/`, `hooks/sharedold/` - evaluate if these should be migrated or deleted during cleanup phase.

