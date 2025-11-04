# Frontend Refactor - Proposed Final File Structure

This document details the complete proposed file structure after the frontend refactor. This structure matches the backend domains and follows a clear domain-driven architecture.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overview, design philosophy, and implementation strategy.

## Complete File Structure

```
frontend/src/
├── routes/
│   └── index.tsx                    # Centralized routes (imports domain routes)
│
├── company/                          # Company domain
│   ├── ✅ api/                          # HTTP API calls to backend
│   │   ├── ✅ companyApi.ts
│   │   └── ✅ index.ts
│   ├── ✅ types/                        # Domain-specific TypeScript types/interfaces
│   │   ├── ✅ company.ts
│   │   ├── ✅ contact.ts
│   │   ├── ✅ companyEnums.ts        # Company-specific enums
│   │   └── ✅ index.ts
│   ├── ✅ hooks/                        # Custom hooks for company logic
│   │   ├── ✅ useCompanies.ts
│   │   ├── ✅ useContacts.ts
│   │   ├── ✅ schemas/                   # Form validation schemas
│   │   │   ├── ✅ companySchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ transformers/              # Form transformers
│   │   │   ├── ✅ companyTransformers.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts
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
│   ├── ✅ api/
│   │   ├── ✅ fundApi.ts
│   │   └── ✅ index.ts
│   ├── ✅ types/
│   │   ├── ✅ fund.ts
│   │   ├── ✅ fundEvent.ts
│   │   ├── ✅ fundTaxStatement.ts
│   │   ├── ✅ fundEventCashFlow.ts
│   │   ├── ✅ fundEnums.ts
│   │   └── ✅ index.ts
│   ├── ✅ hooks/
│   │   ├── ✅ useFunds.ts
│   │   ├── ✅ useFundEvents.ts
│   │   ├── ✅ useFundEventCashFlows.ts
│   │   ├── ✅ useFundTaxStatements.ts
│   │   ├── ✅ useFundFinancialYears.ts
│   │   ├── ✅ schemas/                   # Form validation schemas
│   │   │   ├── ✅ fundSchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ transformers/               # Form transformers
│   │   │   ├── ✅ fundTransformers.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts
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
├── bank/                              # Bank domain
│   ├── ✅ api/
│   │   ├── ✅ bankingApi.ts
│   │   └── ✅ index.ts
│   ├── ✅ types/
│   │   ├── ✅ bank.ts
│   │   ├── ✅ bankAccount.ts
│   │   ├── ✅ bankAccountBalance.ts
│   │   ├── ✅ bankEnums.ts
│   │   └── ✅ index.ts
│   ├── ✅ hooks/
│   │   ├── ✅ useBanks.ts
│   │   ├── ✅ useBankAccounts.ts
│   │   ├── ✅ useBankAccountBalances.ts
│   │   ├── ✅ schemas/                   # Form validation schemas
│   │   │   ├── ✅ bankingSchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ transformers/              # Form transformers
│   │   │   ├── ✅ bankingTransformers.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts
│   ├── components/                    # Feature-based nesting (if any)
│   ├── pages/                         # Banking pages (if any)
│   ├── routes.tsx                     # Banking routes (if any)
│   └── index.ts
│
├── entity/                            # Entity domain
│   ├── ✅ api/
│   │   ├── ✅ entityApi.ts
│   │   └── ✅ index.ts
│   ├── ✅ types/
│   │   ├── ✅ entity.ts
│   │   ├── ✅ entityEnums.ts
│   │   └── ✅ index.ts
│   ├── ✅ hooks/
│   │   ├── ✅ useEntities.ts
│   │   ├── ✅ schemas/                   # Form validation schemas
│   │   │   ├── ✅ entitySchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ transformers/              # Form transformers
│   │   │   ├── ✅ entityTransformers.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts
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
│   ├── ✅ api/
│   │   ├── ✅ ratesApi.ts
│   │   └── ✅ index.ts
│   ├── ✅ types/
│   │   ├── ✅ riskFreeRate.ts             # RiskFreeRate types (migrated from src-old/types/models/rates.ts)
│   │   ├── ✅ fxRate.ts                   # FxRate types (migrated from src-old/types/models/rates.ts)
│   │   ├── ✅ ratesEnums.ts               # Rate domain enums
│   │   └── ✅ index.ts                    # Barrel export for all rate types
│   ├── ✅ hooks/
│   │   ├── ✅ useRiskFreeRates.ts         # Risk-free rate hooks (migrated from src-old/hooks/data/rates/)
│   │   ├── ✅ useFxRates.ts               # FX rate hooks (migrated from src-old/hooks/data/rates/)
│   │   ├── ✅ schemas/                    # Form validation schemas
│   │   │   ├── ✅ rateSchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ transformers/               # Form transformers
│   │   │   ├── ✅ rateTransformers.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts                    # Barrel export for all rate hooks
│   ├── components/                     # Rates components (if any)
│   ├── pages/
│   ├── routes.tsx
│   └── index.ts
│
├── shared/                            # Shared cross-domain resources
│   ├── types/                         # Cross-domain types
│   │   ├── ✅ enums/
│   │   │   ├── ✅ sharedEnums.ts          # Shared enums
│   │   │   └── ✅ index.ts                # Barrel export for shared enums
│   │   ├── ✅ errors.ts                   # ErrorInfo, ErrorType, ErrorSeverity, error utilities
│   │   ├── ✅ dto/                        # DTO types (TODO: not yet migrated)
│   │   │   ├── ✅ api-response.ts
│   │   │   ├── ✅ response-codes.ts
│   │   │   ├── ✅ type-guards.ts
│   │   │   └── ✅ index.ts
│   │   └── ✅ index.ts                    # Main barrel export (exports enums, TODOs for errors.ts and dto/)
│   ├── ✅ api/                            # Base API client (used by all domain APIs)
│   │   ├── ✅ apiClient.ts                # ApiClient class, apiClient instance, ApiError
│   │   └── ✅ index.ts
│   ├── ui/                              # Reusable UI components
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
│   │   ├── ✅ core/                      # Core API hooks
│   │   │   ├── ✅ api/
│   │   │   │   ├── ✅ useQuery.ts
│   │   │   │   ├── ✅ useMutation.ts
│   │   │   │   └── ✅ index.ts
│   │   │   ├── ✅ error/
│   │   │   │   ├── ✅ useErrorHandler.ts
│   │   │   │   └── ✅ index.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ forms/                     # Form management hooks
│   │   │   ├── ✅ useForm.ts
│   │   │   ├── ✅ types.ts
│   │   │   └── ✅ index.ts
│   │   ├── ✅ schemas/                   # Shared form validation schemas
│   │   │   ├── ✅ sharedSchemas.ts
│   │   │   └── ✅ index.ts
│   │   ├── ui/                        # UI hooks
│   │   │   ├── useErrorAutoDismiss.ts
│   │   │   ├── useErrorDetailsToggle.ts
│   │   │   └── index.ts
│   │   └── index.ts                   # Main barrel export
│   ├── utils/                         # Pure utility functions
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── helpers.ts
│   │   └── index.ts
│   └── index.ts                       # Shared domain barrel export
│
├── ✅ store/                             # Global app state (Zustand)
│   ├── ✅ useAppStore.ts
│   ├── ✅ AppStoreProvider.tsx
│   ├── ✅ migration.ts
│   └── ✅ index.ts
│
├── ✅ theme/                             # Theme configuration (unchanged - verified migrated)
│   ├── ✅ dockerTheme.ts
│   ├── ✅ DockerThemeProvider.tsx
│   └── ✅ index.ts
│
├── ✅ config/                            # Configuration (unchanged)
│   └── ✅ environment.ts
│
├── test-utils/                        # Test utilities (unchanged)
│   ├── mock-api.ts
│   ├── mock-data.ts
│   └── render-utils.tsx
│
├── App.tsx                            # Main app component (uses routes/index.tsx)
├── index.tsx                          # Entry point
└── index.css                          # Global styles
```

## Key Structure Principles

### 1. Domain Structure Pattern

Each domain (`company/`, `fund/`, `banking/`, `entity/`, `rates/`) follows the same pattern:
- `api/` - HTTP API calls to backend
- `types/` - Domain-specific TypeScript types/interfaces
- `hooks/` - Domain-specific hooks
- `components/` - Feature-based nested components
- `pages/` - Page components (route-mounted orchestration components)
- `routes.tsx` - Domain route definitions
- `index.ts` - Domain barrel export (public API)

### 2. Feature-Based Component Nesting

Components are grouped by feature (e.g., `company-list/`, `overview-tab/`, `fund-detail/`) rather than being flat. Each feature folder contains:
- Feature component(s)
- Sub-components (in nested `components/` folder if needed)
- Types (in nested `types/` folder if needed)
- `index.ts` barrel export

### 3. Page vs Component Separation

**Pages** (`domain/pages/`):
- Route-mounted, top-level orchestration components
- Manage state, data fetching, error handling
- Coordinate multiple features/components
- Examples: `AllCompaniesPage.tsx`, `CompanyPage.tsx`, `FundPage.tsx`, `AllEntitiesPage.tsx`

**Components** (`domain/components/`):
- Reusable, composable feature components
- **Receive data via props** (do NOT fetch their own data)
- Handle presentation logic
- Examples: `OverviewTab.tsx`, `FundDetailHeader.tsx`, `CompanyList.tsx`, `EquitySection.tsx`

**Data Flow Rule**: Components receive data via props (`data`, `loading`, `error`, callbacks). Pages fetch data using hooks and pass it down.

### 4. Shared Domain Organization

Cross-domain concerns live in `shared/`:
- `shared/types/` - Enums, errors, DTOs used by multiple domains
- `shared/api/` - Base API client (`ApiClient`, `apiClient`, `ApiError`) used by all domain APIs
- `shared/ui/` - Reusable UI components (data-display, feedback, forms, navigation, overlays, layout)
- `shared/hooks/` - Cross-domain hooks (core, ui)
- `shared/utils/` - Pure utility functions

### 5. Barrel Exports

Each domain and major subdirectory has an `index.ts` file that exports the public API, allowing clean imports:
- `import { CompanyList } from '@/company'`
- `import { ErrorDisplay } from '@/shared/ui'`
- `import { FundDetailHeader } from '@/fund'`

### 6. Root-Level Directories

These remain at root level as cross-cutting concerns:
- `store/` - Global app state (Zustand)
- `theme/` - Theme configuration (unchanged - verified migrated)
- `config/` - Configuration (unchanged)
- `test-utils/` - Test utilities (unchanged)
- `routes/` - Centralized route configuration

## Migration Notes

**Source Location**: Old source code is located in `frontend/src-old/`

**Migration Path**: All files move FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`

**Path References**: 
- Destination paths: Relative to `frontend/src/`
- Source paths: Relative to `frontend/src-old/`

