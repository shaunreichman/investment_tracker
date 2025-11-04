# Frontend Refactor - Shared Domain Structure

## Overview

This specification details Phase 1 of the frontend refactor: establishing the `shared/` domain structure and moving all cross-cutting concerns (types, UI components, hooks, utils) into a shared domain that will be used by all other domains.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overall architecture and dependencies.

**Goal**: Establish the `shared/` domain structure and move cross-cutting concerns from the flat structure into organized shared domain folders.

## Dependencies

- **None**: This is the foundation phase that must be completed before all other phases.

## Design Philosophy

- **Shared Domain First**: All cross-cutting concerns must be established before domain-specific migrations
- **Preserve Existing Functionality**: All shared components, types, hooks, and utils must work identically after move
- **Clear Organization**: Group shared resources by type (types, ui, hooks, utils) for discoverability
- **Barrel Exports**: Create public API exports via `index.ts` files for clean imports
- **Incremental Updates**: Update imports immediately as files move to maintain working state

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Phase 1: Foundation - Shared Domain Structure

**Goal**: Establish the `shared/` domain structure and move cross-cutting concerns

**Design Principles**:
- Move shared types (enums, errors, DTOs) to `shared/types/` from top-level `types/`
- Move base API client to `shared/api/` as it's used by all domain APIs
- Preserve all existing shared UI components in `shared/ui/` (currently `components/shared/`)
- Create barrel exports for shared domain public API
- Maintain all imports working throughout the process

**Tasks**:
- [x] Create `src/shared/types/` directory structure
- [x] Move `types/enums/shared.enums.ts` → `shared/types/enums/sharedEnums.ts` (shared enums only - domain-specific enums belong in their respective domains)
- [x] Create `shared/types/enums/index.ts` barrel export for shared enums
- [x] Update `shared/types/index.ts` barrel export (includes enums, TODOs for errors.ts and dto/)
- [x] Move `types/errors.ts` → `shared/types/errors.ts` (with fixes: deprecated substr, improved type safety)
- [x] Move `types/dto/` → `shared/types/dto/` (all DTO files)
- [x] Create `src/shared/api/` directory
- [x] Move `services/api-client.ts` → `shared/api/apiClient.ts`
- [x] Create `shared/api/index.ts` barrel export (exports `ApiClient`, `apiClient`, `ApiError`)
- [ ] Update imports in domain API files to reference `shared/api/apiClient` instead of `../api-client` (will be done when domain APIs are moved in Phases 2-4)
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
- [x] Create `src/shared/hooks/` directory (created when hooks/core was moved)
- [ ] Move `hooks/ui/` → `shared/hooks/ui/`
- [x] Move `hooks/core/` → `shared/hooks/core/` (core hooks moved with api/, error/ subdirectories)
- [x] Create `src/shared/hooks/forms/` directory for form management hooks
- [x] Move `hooks/forms/useForm.ts` → `shared/hooks/forms/useForm.ts`
- [x] Move `hooks/forms/types.ts` → `shared/hooks/forms/types.ts`
- [x] Create `src/shared/hooks/schemas/` directory for shared form validation schemas
- [x] Move `hooks/forms/schemas/commonSchemas.ts` → `shared/hooks/schemas/sharedSchemas.ts`
- [x] Create `shared/hooks/schemas/index.ts` barrel export
- [x] Create `shared/hooks/forms/index.ts` barrel export (exports `useForm`, form types)
- [x] Update `shared/hooks/index.ts` barrel export
- [ ] Create `src/shared/utils/` directory
- [ ] Move utility functions from `utils/` to `shared/utils/` (evaluate which are truly shared)
- [ ] Update all imports across codebase to use new shared paths
- [ ] Run TypeScript compilation to verify no broken imports: `npx tsc --noEmit`
- [ ] Test application to ensure all shared components work identically

**Success Criteria**:
- All shared types, API client, components, hooks, and utils organized in `shared/` domain
- Base API client moved to `shared/api/apiClient.ts` with barrel export
- Zero TypeScript compilation errors
- All imports updated and working (including domain API imports referencing new shared API client location)
- Application runs and displays identically to before refactor
- No visual or functional changes to any UI components

## Overall Success Metrics

- **Shared Domain Established**: All cross-cutting concerns organized in `shared/` domain (types, api, ui, hooks, utils)
- **Zero Breaking Changes**: All existing functionality works identically after refactor
- **Import Clarity**: All imports use new shared paths (e.g., `import { ErrorDisplay } from '@/shared/ui'`, `import { apiClient } from '@/shared/api'`)
- **Type Safety**: Zero TypeScript compilation errors
- **No Regressions**: Application runs and displays identically to before refactor

