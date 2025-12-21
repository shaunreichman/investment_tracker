# Frontend Refactor - Supporting Domains

## Overview

This specification details Phase 4 of the frontend refactor: reorganizing banking, entity, and rates code into their respective domain structures.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overall architecture and dependencies.

**Goal**: Reorganize banking, entity, and rates code into their respective domain structures following the same pattern as company and fund domains.

## Dependencies

- **Requires**: [Phase 1: Shared Domain Structure](01-SHARED_DOMAIN.md) must be completed first
- **Can be parallel**: This phase can run in parallel with Company Domain (Phase 2) and Fund Domain (Phase 3) after Phase 1 is complete

## Design Philosophy

- **Consistent Pattern**: Follow the same domain structure pattern established in company and fund domains
- **Domain Independence**: Each domain (banking, entity, rates) is independent and can be migrated separately
- **Entity Special Case**: Entity domain will extract `AllEntitiesPage` from the old `OverallDashboard`
- **Barrel Exports**: Create public API exports for clean imports from each domain
- **Preserve Functionality**: All functionality must work identically after migration

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Phase 4: Supporting Domains - Banking, Entity, Rates

**Goal**: Reorganize banking, entity, and rates code into their respective domain structures

**Design Principles**:
- Follow the same pattern established in company and fund domains
- Move API, types, hooks, components to respective domains
- Create domain routes and barrel exports
- Maintain all existing functionality

**Tasks**:

#### Banking Domain
- [x] Create `src/bank/` directory structure
- [x] Move `services/api/banking.api.ts` → `bank/api/bankApi.ts`
- [x] Move `types/models/banking.ts` → `bank/types/` (split into bank.ts, bankAccount.ts, bankAccountBalance.ts)
- [x] Move banking enums → `bank/types/bankEnums.ts`
- [x] Move `hooks/data/banking/` → `bank/hooks/` ✅ **Verified**: All three hook files migrated (`useBanks.ts`, `useBankAccounts.ts`, `useBankAccountBalances.ts`). Logic identical, only import paths updated (core hooks: `@/hooks/core/api` → `@/shared/hooks/core`, API: `api.banking` → `bankingApi`, types: `@/types/models/banking` → `../types`)
- [x] Create `src/bank/hooks/schemas/` directory for banking form validation schemas
- [x] Move `hooks/forms/schemas/bankingSchemas.ts` → `bank/hooks/schemas/bankingSchemas.ts`
- [x] Update imports in `bankingSchemas.ts` to use `@/shared/hooks/schemas` for common schemas and domain types/enums from `../types`
- [x] Create `bank/hooks/schemas/index.ts` barrel export
- [x] Create `src/bank/hooks/transformers/` directory for banking form transformers
- [x] Move `hooks/forms/transformers/bankingTransformers.ts` → `bank/hooks/transformers/bankingTransformers.ts`
- [x] Update imports in `bankingTransformers.ts` to use `../schemas` for schema types and `../types` for API request types
- [x] Create `bank/hooks/transformers/index.ts` barrel export
- [x] Update `bank/hooks/index.ts` barrel export to include schemas and transformers
- [x] Move banking components (if any) → `bank/components/` ✅ **Verified**: No banking components exist in old location - banking functionality is API/hooks only (no UI components to migrate)
- [x] Create `bank/api/index.ts` barrel export
- [x] Create `bank/types/index.ts` barrel export
- [x] Create `bank/hooks/index.ts` barrel export ✅ **Verified**: Barrel export created with all banking hooks exported
- [x] Create `bank/routes.tsx` and `bank/index.ts` ✅ **Verified**: Both files created. `bank/routes.tsx` exports empty `bankRoutes` array (appropriate since banking has no UI pages). `bank/index.ts` exports all domain resources (types, API, hooks, routes) as barrel export following the established pattern.

#### Entity Domain
- [x] Create `src/entity/` directory structure
- [x] Move `services/api/entity.api.ts` → `entity/api/entityApi.ts`
- [x] Move `types/models/entity.ts` → `entity/types/entity.ts` ✅ **Verified**: File moved, content identical (100% match), imports updated to use `./entityEnums` and `@/shared/types`
- [x] Move entity enums → `entity/types/entityEnums.ts` ✅ **Verified**: File moved, renamed to camelCase (`entityEnums.ts`), content identical
- [x] Move `hooks/data/entities/` → `entity/hooks/` ✅ **Verified**: `useEntities.ts` migrated with all hooks (useEntities, useEntity, useCreateEntity, useDeleteEntity). Logic identical, only import paths updated (core hooks: `@/hooks/core/api` → `@/shared/hooks/core`, API: `api.entities` → `entityApi`, types: `@/types/models/entity` → `../types`)
- [x] Create `src/entity/hooks/schemas/` directory for entity form validation schemas
- [x] Move `hooks/forms/schemas/entitySchemas.ts` → `entity/hooks/schemas/entitySchemas.ts`
- [x] Update imports in `entitySchemas.ts` to use `@/shared/hooks/schemas` for common schemas and domain types/enums from `../types`
- [x] Create `entity/hooks/schemas/index.ts` barrel export
- [x] Create `src/entity/hooks/transformers/` directory for entity form transformers
- [x] Move `hooks/forms/transformers/entityTransformers.ts` → `entity/hooks/transformers/entityTransformers.ts`
- [x] Update imports in `entityTransformers.ts` to use `../schemas` for schema types and `../types` for API request types
- [x] Create `entity/hooks/transformers/index.ts` barrel export
- [x] Update `entity/hooks/index.ts` barrel export to include schemas and transformers ✅ **Verified**: All files migrated. Content identical to old files (100% match). Imports correctly updated: `entitySchemas.ts` uses `@/shared/hooks/schemas` for common schemas and `../../types` for domain types (correct relative path); `entityTransformers.ts` uses `../schemas` for schema types and `../../types` for API request types. Both barrel exports created and main `entity/hooks/index.ts` exports schemas and transformers.
- [x] Move `components/entities/` → `entity/components/` (maintain feature structure) ✅ **Verified**: All 6 files moved from `src-old/components/entities/` to `src/entity/components/entity-list/` (EntityCards.tsx, EntityTable.tsx, EntityList.tsx, EntityFilters.tsx, DependencyBlockedDialog.tsx, index.ts). Feature structure maintained with `entity-list/` subdirectory following the same pattern as company domain's `company-list/`.
- [x] Create `entity/components/index.ts` barrel export for public API ✅ **Verified**: Barrel export created at `src/entity/components/index.ts` with `export * from './entity-list';`. The `entity-list/index.ts` properly exports all components and their types (EntityList, EntityFilters, EntityTable, EntityCards, DependencyBlockedDialog) following the established pattern.
- [x] Create `src/entity/pages/` directory ✅ **Verified**: Directory exists at `frontend/src/entity/pages/`
- [x] Create `entity/pages/AllEntitiesPage.tsx`: Extract entity management section from old `OverallDashboard` (EntityList and CreateEntityModal integration) ✅ **Verified**: File exists at `frontend/src/entity/pages/AllEntitiesPage.tsx`. Extracts entity management section with proper page structure, integrates EntityList component, and integrates CreateEntityModal (note: CreateEntityModal still needs migration from src-old, but integration is complete)
- [x] Refactor `EntityList` to receive data via props: Remove `useEntities()` hook, accept `data`, `loading`, `error`, `onRefresh` as props (parent page will fetch data) ✅ **Verified**: `EntityList` component accepts `data`, `loading`, `error`, `onRefresh` as props via `EntityListProps` interface. No `useEntities()` hook call found in component - data fetching moved to parent page.
- [x] Update `AllEntitiesPage` to fetch entity data using `useEntities()` hook and pass to `EntityList` component ✅ **Verified**: `AllEntitiesPage` calls `useEntities()` hook (line 37) and passes `data={entities}`, `loading={loading}`, `error={error}`, `onRefresh={refetch}` to `EntityList` component (lines 133-138). Data flow properly separated with parent fetching and child receiving via props.
- [x] Create `entity/pages/index.ts` barrel export ✅ **Verified**: Barrel export created at `frontend/src/entity/pages/index.ts` with proper export of AllEntitiesPage
- [x] Create `entity/api/index.ts` barrel export
- [x] Create `entity/types/index.ts` barrel export ✅ **Verified**: Barrel export created with proper exports for enums and types
- [x] Create `entity/hooks/index.ts` barrel export ✅ **Verified**: Barrel export created with all entity hooks exported (useEntities, useEntity, useCreateEntity, useDeleteEntity)
- [x] Create `entity/routes.tsx` and `entity/index.ts` ✅ **Verified**: Both files created. `entity/routes.tsx` exports `entityRoutes` array with `/entities` route using RouteLayout and DomainErrorBoundary, integrating AllEntitiesPage. `entity/index.ts` exports all domain resources (types, API, hooks, components, pages, routes) as barrel export following the established pattern.

#### Rates Domain
- [x] Create `src/rates/` directory structure
- [x] Move `services/api/rates.api.ts` → `rates/api/ratesApi.ts`
- [x] Move `types/models/rates.ts` → `rates/types/` (split into `riskFreeRate.ts` and `fxRate.ts`) ✅ **Verified**: Types migrated and split into separate files - `riskFreeRate.ts` contains RiskFreeRate types, `fxRate.ts` contains FxRate types. Content identical to old file, imports updated to use absolute paths (`@/shared/types`). Improved organization with domain-specific file separation.
- [x] Move rates enums → `rates/types/ratesEnums.ts` ✅ **Verified**: Enums migrated, content identical
- [x] Move `hooks/data/rates/` → `rates/hooks/` ✅ **Verified**: All hooks migrated (`useFxRates.ts`, `useRiskFreeRates.ts`). Logic identical to old files, only import paths updated (core hooks: `@/hooks/core/api` → `@/shared/hooks/core`, API: `api.rates` → `ratesApi`, types: `@/types/models/rates` → `../types`). Comment example corrected from `country: Country.AU` to `currency: Currency.AUD` to match actual type structure.
- [x] Create `src/rates/hooks/schemas/` directory for rates form validation schemas
- [x] Move `hooks/forms/schemas/rateSchemas.ts` → `rates/hooks/schemas/rateSchemas.ts`
- [x] Update imports in `rateSchemas.ts` to use `@/shared/hooks/schemas` for common schemas and domain types/enums from `../types`
- [x] Create `rates/hooks/schemas/index.ts` barrel export
- [x] Create `src/rates/hooks/transformers/` directory for rates form transformers
- [x] Move `hooks/forms/transformers/rateTransformers.ts` → `rates/hooks/transformers/rateTransformers.ts`
- [x] Update imports in `rateTransformers.ts` to use `../schemas` for schema types and `../types` for API request types
- [x] Create `rates/hooks/transformers/index.ts` barrel export
- [x] Update `rates/hooks/index.ts` barrel export to include schemas and transformers ✅ **Verified**: All files migrated correctly. Content identical to old files (100% match). Imports updated correctly: `rateSchemas.ts` uses `@/shared/hooks/schemas` for common schemas and `../../types` for domain types; `rateTransformers.ts` uses `../schemas` for schema types and `../../types` for API request types. Both barrel exports created and main `rates/hooks/index.ts` exports schemas and transformers.
- [x] Move rates components (if any) → `rates/components/` ✅ **Verified**: No rates components exist in old location - rates functionality is API/hooks only (no UI components to migrate)
- [x] Create `rates/api/index.ts` barrel export
- [x] Create `rates/types/index.ts` barrel export ✅ **Verified**: Barrel export created with proper re-exports for both RiskFreeRate and FxRate types, plus enums
- [x] Create `rates/hooks/index.ts` barrel export ✅ **Verified**: Barrel export created with all rate hooks exported (useFxRates, useFxRate, useCreateFxRate, useDeleteFxRate, useRiskFreeRates, useRiskFreeRate, useCreateRiskFreeRate, useDeleteRiskFreeRate)
- [x] Create `rates/routes.tsx` and `rates/index.ts` ✅ **Verified**: Both files created. `rates/routes.tsx` exports empty `ratesRoutes` array (appropriate since rates has no UI pages - rates functionality is API/hooks/types only). `rates/index.ts` exports all domain resources (types, API, hooks, routes) as barrel export following the established pattern.

#### Cross-Domain Updates
- [x] Update all imports across codebase to use new domain paths
- [x] Run TypeScript compilation: `npx tsc --noEmit`
- [x] Test all banking, entity, and rates functionality

**Success Criteria**:
- All banking, entity, and rates code organized in respective domains
- Zero TypeScript compilation errors
- All functionality works identically
- Visual appearance matches exactly
- `AllEntitiesPage` created and `EntityList` receives data via props
- Domain routes and barrel exports created for all three domains

## Overall Success Metrics

- **Domain Organization**: All banking, entity, and rates code organized in respective domain structures
- **Zero Breaking Changes**: All functionality works identically after refactor
- **Import Clarity**: All imports use new domain paths (e.g., `import { EntityList } from '@/entity'`)
- **Type Safety**: Zero TypeScript compilation errors
- **Entity Page Extraction**: `AllEntitiesPage` extracted from `OverallDashboard` with proper data flow

