# Frontend Refactor - Master Specification

## Overview

This master specification coordinates the complete refactoring of the frontend codebase from the current flat component structure to a domain-driven architecture that matches the backend organization. The refactor will reorganize all files into domain-based directories (`company/`, `banking/`, `fund/`, `entity/`, `rates/`, `shared/`) while maintaining 100% visual consistency - the UI and theme must remain identical.

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

**See**: [00-FILE_STRUCTURE.md](00-FILE_STRUCTURE.md) for the complete detailed file structure with all nested folders, components, and organization patterns.

### Structure Overview

After the refactor, the frontend structure will match the backend domains and follow a clear domain-driven architecture:

- **Domains**: `company/`, `fund/`, `banking/`, `entity/`, `rates/`, `shared/`
- **Each Domain Contains**: `api/`, `types/`, `hooks/`, `components/`, `pages/`, `routes.tsx`, `index.ts`
- **Root Level**: `routes/`, `store/`, `theme/`, `config/`, `test-utils/`, `App.tsx`, `index.tsx`

### Key Structure Principles

1. **Domain Structure Pattern**: Each domain follows the same pattern (api, types, hooks, components, pages, routes)

2. **Page vs Component Separation**: 
   - **Pages** (`domain/pages/`): Route-mounted orchestration components that manage state and data fetching
   - **Components** (`domain/components/`): Reusable components that receive data via props

3. **Feature-Based Nesting**: Components are grouped by feature (e.g., `company-list/`, `overview-tab/`) with nested sub-components

4. **Shared Domain**: Cross-domain concerns (types, ui, hooks, utils) live in `shared/`

5. **Barrel Exports**: Clean imports via domain-level `index.ts` files

## Implementation Strategy & Dependencies

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths in specs are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

### Execution Order & Dependencies

```
Phase 1: Shared Domain (Foundation)
    ↓
Phases 2, 3, 4: Domain Migrations (Can be parallel after Phase 1)
    ├─→ Phase 2: Company Domain
    ├─→ Phase 3: Fund Domain
    └─→ Phase 4: Supporting Domains (Banking, Entity, Rates)
    ↓
Phases 5 & 6: Routing & Cleanup (After all domains complete)
    ├─→ Phase 5: Routing Centralization
    └─→ Phase 6: Cleanup and Verification
```

### Phase Specifications

1. **[Shared Domain Structure](01-SHARED_DOMAIN.md)** (Phase 1)
   - **Dependencies**: None (foundation)
   - **Goal**: Establish the `shared/` domain structure and move cross-cutting concerns
   - Establishes shared types, UI components, hooks, and utils
   - **Must complete before**: All other phases

2. **[Company Domain](02-COMPANY_DOMAIN.md)** (Phase 2)
   - **Dependencies**: Requires Phase 1 (Shared Domain)
   - **Goal**: Reorganize company-related code into `company/` domain structure
   - Can be done in parallel with Phases 3 & 4 after Phase 1 is complete

3. **[Fund Domain](03-FUND_DOMAIN.md)** (Phase 3)
   - **Dependencies**: Requires Phase 1 (Shared Domain)
   - **Goal**: Reorganize fund-related code into `fund/` domain structure
   - Can be done in parallel with Phases 2 & 4 after Phase 1 is complete

4. **[Supporting Domains](04-SUPPORTING_DOMAINS.md)** (Phase 4)
   - **Dependencies**: Requires Phase 1 (Shared Domain)
   - **Goal**: Reorganize banking, entity, and rates code into their respective domain structures
   - Can be done in parallel with Phases 2 & 3 after Phase 1 is complete

5. **[Routing & Cleanup](05-ROUTING_CLEANUP.md)** (Phases 5 & 6)
   - **Dependencies**: Requires Phases 2, 3, 4 (Company, Fund, Supporting Domains)
   - **Goal**: Centralize routing and remove old file structure
   - Phase 5: Routing Centralization
   - Phase 6: Cleanup and Verification

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

2. **Layout Components**: Components in `components/layout/` (RouteLayout, MainSidebar, TopBar) should be moved to `shared/ui/layout/` as cross-cutting reusable UI components.

3. **Store and Configuration**: Files in `store/`, `config/`, `test-utils/` should remain at root level as they are cross-cutting concerns.

4. **Data Fetching Edge Cases**: 
   - **General Rule**: Components should receive data via props. Pages orchestrate data fetching.
   - **Modals**: Modals that fetch independent data (e.g., `CreateFundModal` fetching entities for dropdown) may fetch their own data if the data is specific to the modal and not shared elsewhere. However, prefer passing props when the data is available from parent.
   - **Self-Contained Components**: If a component is truly self-contained and reusable across different contexts where parent data isn't available, it may fetch its own data. Evaluate case-by-case - prefer props when possible.

5. **Incremental Migration**: Each phase should be completed and verified before moving to the next. Do not move to Phase 2 until Phase 1 is fully complete and tested.

6. **Import Updates**: As files are moved, imports must be updated immediately to maintain a working state. Use IDE refactoring tools where possible.

7. **Barrel Exports**: Domain-level `index.ts` files should export public API only. Internal feature imports should use direct paths.

8. **Old Hooks**: There are old hooks in `hooks/formsold/`, `hooks/fundsold/`, `hooks/sharedold/` - evaluate if these should be migrated or deleted during cleanup phase.

## Status Tracking

Track overall progress by checking completion status in each phase specification:
- [ ] Phase 1: Shared Domain Structure
- [ ] Phase 2: Company Domain
- [ ] Phase 3: Fund Domain
- [ ] Phase 4: Supporting Domains
- [ ] Phase 5: Routing Centralization
- [ ] Phase 6: Cleanup and Verification

