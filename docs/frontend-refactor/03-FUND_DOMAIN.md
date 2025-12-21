# Frontend Refactor - Fund Domain

## Overview

This specification details Phase 3 of the frontend refactor: reorganizing all fund-related code into the `fund/` domain structure with feature-based component nesting.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overall architecture and dependencies.

**Goal**: Reorganize fund-related code into `fund/` domain structure with API, types, hooks, components, pages, and routes.

## Dependencies

- **Requires**: [Phase 1: Shared Domain Structure](01-SHARED_DOMAIN.md) must be completed first
- **Can be parallel**: This phase can run in parallel with Company Domain (Phase 2) and Supporting Domains (Phase 4) after Phase 1 is complete

## Design Philosophy

- **Domain Consistency**: Follow the same pattern established in the shared and company domains (api, types, hooks, components, pages, routes)
- **Feature-Based Nesting**: Group components by feature (e.g., `fund-detail/`, `fund-events/`)
- **Page Extraction**: Extract `FundPage` from `FundDetail` - page handles orchestration, components handle presentation
- **Barrel Exports**: Create public API exports for clean imports from the domain
- **Preserve Functionality**: All fund-related features must work identically after migration

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Phase 3: Core Domains - Fund Domain

**Goal**: Reorganize fund-related code into `fund/` domain structure

**Design Principles**:
- Move all fund API calls to `fund/api/`
- Move fund types to `fund/types/`
- Move fund hooks to `fund/hooks/`
- Reorganize fund components with feature-based nesting
- Create domain routes in `fund/routes.tsx`
- Create domain barrel export in `fund/index.ts`
- **Type Standardization**: Eliminate legacy `EnhancedFund` type - use `Fund` type directly from `@/fund/types` throughout codebase
- **No Transformation Layer**: API responses use `Fund` type directly; components consume `Fund` type without transformation

**Tasks**:
- [x] Create `src/fund/` directory structure
- [x] Create `src/fund/api/` directory
- [x] Move `services/api/fund.api.ts` → `fund/api/fundApi.ts`
- [x] Create `fund/api/index.ts` barrel export
- [x] Create `src/fund/types/` directory
- [x] Move `types/models/fund.ts` → `fund/types/fund.ts` (split into: fund.ts, fundEvent.ts, fundEventCashFlow.ts, fundTaxStatement.ts)
- [x] Move fund-related enums from `types/enums/fund.enums.ts` → `fund/types/fundEnums.ts`
- [x] Create `fund/types/index.ts` barrel export
- [x] Create `src/fund/hooks/` directory
- [x] Move `hooks/data/funds/` → `fund/hooks/`
- [x] Rename files to remove `funds/` namespace
- [x] Update imports to use new domain structure (`@/shared/hooks/core`, `fundApi`, `../types`)
- [x] Create `fund/hooks/index.ts` barrel export
- [x] Update `fund/api/index.ts` to export singleton `fundApi` instance
- [x] Create `src/fund/hooks/schemas/` directory for fund form validation schemas
- [x] Move `hooks/forms/schemas/fundSchemas.ts` → `fund/hooks/schemas/fundSchemas.ts`
- [x] Update imports in `fundSchemas.ts` to use `@/shared/hooks/schemas` for common schemas and domain types/enums from `../types`
- [x] Create `fund/hooks/schemas/index.ts` barrel export
- [x] Create `src/fund/hooks/transformers/` directory for fund form transformers
- [x] Move `hooks/forms/transformers/fundTransformers.ts` → `fund/hooks/transformers/fundTransformers.ts`
- [x] Update imports in `fundTransformers.ts` to use `../schemas` for schema types and `../types` for API request types
- [x] Create `fund/hooks/transformers/index.ts` barrel export
- [x] Update `fund/hooks/index.ts` barrel export to include schemas and transformers
- [x] **Refactor: Eliminate EnhancedFund type and use Fund type directly**
  - [x] Identify all EnhancedFund/EnhancedFundsResponse usage:
    - [x] Search codebase for `EnhancedFund` and `EnhancedFundsResponse` imports and usages
    - [x] Document all locations using EnhancedFund (currently: `company/components/funds-tab/`)
    - [x] Review `transformToEnhancedFund()` function in `src-old/hooks/useCompaniesold.ts`
  - [x] Update company domain FundsTab to use Fund type:
    - [x] Update `company/components/funds-tab/types/funds-tab.types.ts`: Replace `EnhancedFund` with `Fund` from `@/fund/types`
    - [x] Replace `EnhancedFundsResponse` with `{ funds: Fund[]; filters?: {...} }` type or use `Fund[]` directly
    - [x] Update `FundsTabProps` to use `Fund[]` instead of `EnhancedFundsResponse`
    - [x] Update `FundsTableProps`, `FundsCardsProps`, `FundRowProps` to use `Fund` instead of `EnhancedFund`
  - [x] Fix field name mappings in components:
    - [x] Update `FundRow.tsx`: Change `fund.fund_type` → `fund.fund_investment_type`
    - [x] Update `FundsCards.tsx`: Change `fund.fund_type` → `fund.fund_investment_type`
    - [x] Verify all other field accesses use correct Fund type field names
  - [x] Update enum usage for proper type safety:
    - [x] Ensure `fund.status` is typed as `FundStatus` enum (not string)
    - [x] Ensure `fund.tracking_type` is typed as `FundTrackingType` enum (not string)
    - [x] Ensure `fund.fund_investment_type` is typed as `FundInvestmentType` enum (not string)
    - [x] Ensure `fund.currency` is typed as `Currency` enum (not string)
  - [ ] Remove EnhancedFund transformation logic:
    - [ ] Remove `transformToEnhancedFund()` function from `src-old/hooks/useCompaniesold.ts` (NOTE: Still exists in src-old, but this is expected as old code)
    - [ ] Update `useEnhancedFunds()` hook (or replace with `useFunds()`) to return `Fund[]` directly (NOTE: Still in src-old)
    - [ ] Update company domain hooks to use `useFunds()` from `@/fund/hooks` instead of `useEnhancedFunds()` (NOTE: Parent component using FundsTab not found in new src/)
  - [ ] Update company FundsTab component data fetching:
    - [ ] Replace `useEnhancedFunds()` with `useFunds()` from `@/fund/hooks` (NOTE: FundsTab receives data as prop; parent component migration status unclear)
    - [ ] Map query params correctly: `status_filter` → `fund_status` enum, `sort_by` → `SortFieldFund` enum
    - [ ] Remove transformation layer - use `Fund[]` directly from API response
  - [ ] Clean up legacy types:
    - [ ] Remove `EnhancedFund` interface from `src-old/types/api.ts` (after migration complete) (NOTE: Still in src-old, expected until full migration)
    - [ ] Remove `EnhancedFundsResponse` interface from `src-old/types/api.ts` (after migration complete) (NOTE: Still in src-old, expected until full migration)
    - [x] Remove TODO comment in `company/components/funds-tab/types/funds-tab.types.ts`
  - [x] Verify compatibility:
    - [x] All Fund type fields match what components expect (already verified: all EnhancedFund fields exist in Fund)
    - [x] All calculated fields are present: `current_equity_balance`, `completed_irr_gross`, `current_nav_total`, etc.
    - [x] All date fields are present: `start_date`, `end_date`, `current_duration`
- [x] Create `src/fund/components/` directory
- [x] Create `src/fund/components/fund-detail/` feature directory
- [x] Move `components/fund/detail/FundDetailHeader.tsx` → `fund/components/fund-detail/FundDetailHeader.tsx`
- [x] Move `components/fund/detail/summary/` → `fund/components/fund-detail/summary/`
- [x] Move `components/fund/detail/table/` → `fund/components/fund-detail/table/`
- [x] Create `fund/components/fund-detail/index.ts` barrel export
- [x] Move `components/fund/events/` → `fund/components/fund-events/` (reorganize as feature folder)
- [x] Create `fund/components/index.ts` barrel export for public API
- [x] **Follow-up: Migrate ExtendedFund usage in fund detail components** (NOTE: Moved components still reference `ExtendedFund` from `src-old/types/api.ts` - this is separate from EnhancedFund elimination and will be addressed when migrating fund detail page)
  - [x] ExtendedFund type eliminated - no references found in migrated components
  - [x] All `src-old` imports migrated in `CreateFundEventModal.tsx`: `calculateTaxPaymentDate` from `@/shared/utils/formatters`; `useEventSubmission` from `@/fund/hooks`; `useUnifiedForm`, `createValidator`, `validationRules` from `@/shared/hooks/forms`; `SuccessBanner` from `@/shared/ui/feedback` (Note: `formatNumber` and `parseNumber` are not used in this component)
- [x] Create `src/fund/pages/` directory
- [x] Extract `FundPage.tsx` from `components/fund/detail/FundDetail.tsx`: Keep orchestration logic (useParams, state, data fetching, error handling) in page; move presentation sections to component directory
- [x] Create `fund/pages/index.ts` barrel export
- [x] Create `src/fund/routes.tsx` with fund route definitions
- [x] Create `src/fund/index.ts` domain barrel export
- [x] Update all imports across codebase to use new fund domain paths
- [x] Run TypeScript compilation: `npx tsc --noEmit`
- [x] Test fund detail page and all fund-related functionality

**Success Criteria**:
- All fund code organized in `fund/` domain
- Zero TypeScript compilation errors
- All fund pages and components work identically
- Visual appearance matches exactly
- Feature-based component nesting implemented
- Domain routes defined in `fund/routes.tsx`
- `FundPage` handles orchestration; components handle presentation
- EnhancedFund type eliminated - all components use `Fund` type directly from `@/fund/types`
- No transformation layer between API responses and components - `Fund` type used end-to-end
- Proper enum types used throughout (FundStatus, FundTrackingType, FundInvestmentType) instead of strings

## Overall Success Metrics

- **Domain Organization**: All fund code organized in `fund/` domain structure
- **Zero Breaking Changes**: All fund functionality works identically after refactor
- **Import Clarity**: All imports use new fund domain paths (e.g., `import { FundDetailHeader } from '@/fund'`)
- **Type Safety**: Zero TypeScript compilation errors
- **Feature Nesting**: Components organized by feature with proper nesting
- **Page/Component Separation**: `FundPage` orchestrates data; components receive via props

