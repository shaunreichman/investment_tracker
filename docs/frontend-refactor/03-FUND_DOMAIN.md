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
- `FundPage` handles orchestration; components handle presentation

## Overall Success Metrics

- **Domain Organization**: All fund code organized in `fund/` domain structure
- **Zero Breaking Changes**: All fund functionality works identically after refactor
- **Import Clarity**: All imports use new fund domain paths (e.g., `import { FundDetailHeader } from '@/fund'`)
- **Type Safety**: Zero TypeScript compilation errors
- **Feature Nesting**: Components organized by feature with proper nesting
- **Page/Component Separation**: `FundPage` orchestrates data; components receive via props

