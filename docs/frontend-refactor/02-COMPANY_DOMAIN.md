# Frontend Refactor - Company Domain

## Overview

This specification details Phase 2 of the frontend refactor: reorganizing all company-related code into the `company/` domain structure with feature-based component nesting.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overall architecture and dependencies.

**Goal**: Reorganize company-related code into `company/` domain structure with API, types, hooks, components, pages, and routes.

## Dependencies

- **Requires**: [Phase 1: Shared Domain Structure](01-SHARED_DOMAIN.md) must be completed first
- **Can be parallel**: This phase can run in parallel with Fund Domain (Phase 3) and Supporting Domains (Phase 4) after Phase 1 is complete

## Design Philosophy

- **Domain Consistency**: Follow the same pattern established in the shared domain (api, types, hooks, components, pages, routes)
- **Feature-Based Nesting**: Group components by feature (e.g., `company-list/`, `overview-tab/`, `funds-tab/`)
- **Page vs Component**: Pages orchestrate data fetching and state; components receive data via props
- **Barrel Exports**: Create public API exports for clean imports from the domain
- **Preserve Functionality**: All company-related features must work identically after migration

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Phase 2: Core Domains - Company Domain

**Goal**: Reorganize company-related code into `company/` domain structure

**Design Principles**:
- Move all company API calls to `company/api/`
- Move company types to `company/types/`
- Move company hooks to `company/hooks/`
- Reorganize company components with feature-based nesting
- **Design System Adoption**: Refactor components to use shared design system components where appropriate (e.g., `PortfolioSummaryCards` → `StatCard`)
- Create domain routes in `company/routes.tsx`
- Create domain barrel export in `company/index.ts`

**Tasks**:
- [x] Create `src/company/` directory structure
- [x] Create `src/company/api/` directory
- [x] Move `services/api/company.api.ts` → `company/api/companyApi.ts`
- [x] Create `company/api/index.ts` barrel export
- [x] Create `src/company/types/` directory
- [x] Move `types/models/company.ts` → `company/types/company.ts`
- [x] Separate Contact model into `company/types/contact.ts` (aligned with spec pattern, matches backend structure)
- [x] Move company-related enums from `types/enums/company.enums.ts` → `company/types/companyEnums.ts`
- [x] Create `company/types/index.ts` barrel export (exports both Company and Contact types)
- [x] Create `src/company/hooks/` directory
- [x] Move `hooks/data/companies/` → `company/hooks/`
- [x] Rename files to remove `companies/` namespace (e.g., `useCompanies.ts` not `companies/useCompanies.ts`)
- [x] Create `company/hooks/index.ts` barrel export
- [x] Create `src/company/hooks/schemas/` directory for company form validation schemas
- [x] Move `hooks/forms/schemas/companySchemas.ts` → `company/hooks/schemas/companySchemas.ts`
- [x] Update imports in `companySchemas.ts` to use `@/shared/hooks/schemas` for common schemas
- [x] Create `company/hooks/schemas/index.ts` barrel export
- [x] Create `src/company/hooks/transformers/` directory for company form transformers
- [x] Move `hooks/forms/transformers/companyTransformers.ts` → `company/hooks/transformers/companyTransformers.ts`
- [x] Update imports in `companyTransformers.ts` to use `../schemas` for schema types
- [x] Create `company/hooks/transformers/index.ts` barrel export
- [x] Update `company/hooks/index.ts` barrel export to include schemas and transformers
- [x] Create `src/company/components/` directory
- [x] Move `components/companies/company-list/` → `company/components/company-list/`
- [x] Refactor `CompanyList` to receive data via props: Remove `useCompanies()` hook, accept `data`, `loading`, `error`, `onRefresh` as props (parent page will fetch data)
- [x] Create `src/company/pages/` directory
- [x] Rename `components/OverallDashboard.tsx` → `company/pages/AllCompaniesPage.tsx`
- [x] Remove entity management section from `AllCompaniesPage` (EntityList and CreateEntityModal - will move to separate entity page)
- [x] Update `AllCompaniesPage` to fetch company data using `useCompanies()` hook and pass to `CompanyList` component
- [x] Move `components/companies/company-details-tab/` → `company/components/company-details-tab/` (evaluate if this should be `details-tab/`)
- [x] Move `components/companies/overview-tab/` → `company/components/overview-tab/`
- [x] **Refactor `PortfolioSummaryCards` to use shared `StatCard` component** (design system adoption)
  - [x] Replace manual MUI Card implementation in `PortfolioSummaryCards` with `StatCard` from `@/shared/ui/data-display/Card`
  - [x] Transform 3 manual cards to use `StatCard` props (title, value, subtitle, icon, color)
  - [x] Verify visual appearance matches exactly (same styling, spacing, colors)
  - [x] **Note**: This demonstrates design system adoption - reduces ~75 lines to ~15 lines per card while maintaining consistency
- [x] **Migrate shared UI hooks** (required for FundsTab component)
  - [x] Create `src/shared/hooks/ui/` directory
  - [x] Move `hooks/sharedold/useDebouncedSearchold.ts` → `shared/hooks/ui/useDebouncedSearch.ts`
  - [x] Move `hooks/sharedold/useResponsiveViewold.ts` → `shared/hooks/ui/useResponsiveView.ts`
  - [x] Move `hooks/sharedold/useTableSortingold.ts` → `shared/hooks/ui/useTableSorting.ts`
  - [x] Update hook implementations to remove "old" suffix and clean up exports
  - [x] Create `shared/hooks/ui/index.ts` barrel export
  - [x] Update `shared/hooks/index.ts` to export UI hooks
- [x] **Migrate fund filters hook** (required for FundsTab component)
  - [x] Move `hooks/fundsold/useFundsFiltersold.ts` → `fund/hooks/useFundsFilters.ts` (or evaluate if it should be in `shared/hooks/ui/` if generic)
  - [x] Update hook implementation to remove "old" suffix
  - [x] Update `fund/hooks/index.ts` to export `useFundsFilters`
- [x] **Refactor CreateFundModal to use new form hook** (required before component migration)
  - [x] Convert `CreateFundModal` from `useUnifiedForm` to `useForm` (React Hook Form + Zod)
  - [x] Use existing `fund/hooks/schemas/fundSchemas.ts` for validation
  - [x] Update form state management to React Hook Form patterns
  - [x] Verify form functionality matches existing behavior
- [x] Move `components/companies/funds-tab/` → `company/components/funds-tab/`
  - [x] Update imports to use new hook paths: `@/shared/hooks/ui` and `@/fund/hooks`
- [x] Move `components/companies/analysis-tab/` → `company/components/analysis-tab/`
- [x] Move `components/companies/activity-tab/` → `company/components/activity-tab/`
- [x] Move `components/companies/create-fund/` → `company/components/create-fund/`
  - [x] Update imports to use new hook paths: `@/entity/hooks`, `@/fund/hooks`, `@/shared/hooks/forms`
- [x] Move `components/CreateCompanyModal.tsx` → `company/components/create-company-modal/` (reorganize as feature folder)
- [x] Update all component imports within company domain
- [x] Create `company/components/index.ts` barrel export for public API
- [x] Move `components/companies/CompaniesPage.tsx` → `company/pages/CompanyPage.tsx`
  - [x] Replace `useEnhancedFunds()` with `useFunds()` from `@/fund/hooks`
  - [x] Update data structure: Replace `EnhancedFundsResponse` with `FundsTabData` type from `@/company/components/funds-tab/types`
  - [x] Map query params correctly: `status_filter` → `fund_status` enum, `sort_by` → `SortFieldFund` enum
  - [x] Update FundsTab props to use `FundsTabData` instead of `EnhancedFundsResponse`
  - [x] Remove transformation layer - use `Fund[]` directly from API response
- [x] Create `company/pages/index.ts` barrel export
- [x] Create `src/company/routes.tsx` with company route definitions
- [x] Create `src/company/index.ts` domain barrel export
- [x] Update all imports across codebase to use new company domain paths
- [x] Run TypeScript compilation: `npx tsc --noEmit`
- [x] Test company page, company list, and all company-related functionality

**Success Criteria**:
- All company code organized in `company/` domain
- Zero TypeScript compilation errors
- All company pages and components work identically
- Visual appearance matches exactly
- Feature-based component nesting implemented
- Domain routes defined in `company/routes.tsx`
- `CompanyList` receives data via props (data fetching handled by page)
- `PortfolioSummaryCards` uses shared `StatCard` component (design system adoption)
- Shared UI hooks migrated to `shared/hooks/ui/` (useDebouncedSearch, useResponsiveView, useTableSorting)
- Fund filters hook migrated to appropriate location
- `CreateFundModal` uses new `useForm` hook with Zod schemas (replacing `useUnifiedForm`)
- `CompanyPage` uses `Fund` type directly from `@/fund/types` (no EnhancedFund transformation layer)

## Overall Success Metrics

- **Domain Organization**: All company code organized in `company/` domain structure
- **Zero Breaking Changes**: All company functionality works identically after refactor
- **Import Clarity**: All imports use new company domain paths (e.g., `import { CompanyList } from '@/company'`)
- **Type Safety**: Zero TypeScript compilation errors
- **Feature Nesting**: Components organized by feature with proper nesting
- **Page/Component Separation**: Pages orchestrate data; components receive via props

