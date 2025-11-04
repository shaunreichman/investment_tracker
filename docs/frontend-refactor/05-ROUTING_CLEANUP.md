# Frontend Refactor - Routing & Cleanup

## Overview

This specification details Phases 5 and 6 of the frontend refactor: centralizing all routes and cleaning up the old file structure.

**Reference**: See [00-MASTER.md](00-MASTER.md) for overall architecture and dependencies.

**Goal**: 
- **Phase 5**: Centralize all routes via `routes/index.tsx` importing domain route definitions
- **Phase 6**: Remove old file structure, verify everything works, and finalize the refactor

## Dependencies

- **Requires**: Phases 2, 3, 4 (Company, Fund, Supporting Domains) must be completed
- All domain routes must be defined before routing centralization

## Design Philosophy

- **Single Source of Truth**: All routes defined in one centralized location
- **Domain Route Integration**: Domain routes defined in each domain's `routes.tsx` file
- **Complete Cleanup**: Remove all old directories and files after verification
- **Comprehensive Testing**: Verify all routes, navigation, and functionality before cleanup
- **No Orphans**: Ensure no imports reference old paths before deletion

## Implementation Strategy

**Note**: The old source code is located in `frontend/src-old/`. All migration tasks move files FROM `frontend/src-old/` TO the new domain structure in `frontend/src/`. All paths are relative to `frontend/src/` for destinations and `frontend/src-old/` for sources.

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
- `App.tsx` uses centralized routes

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
- [ ] Remove old `services/api-client.ts` file (moved to `shared/api/apiClient.ts`)
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
- [ ] Evaluate old hooks in `hooks/formsold/`, `hooks/fundsold/`, `hooks/sharedold/` - migrate or delete
- [ ] Document any remaining considerations or future improvements

**Success Criteria**:
- All old directories and files removed
- Zero TypeScript compilation errors
- Zero runtime errors or warnings
- All functionality works identically
- Visual appearance matches exactly (theme preserved)
- All imports use new domain structure
- All barrel exports working correctly
- No orphaned imports or duplicate files

## Overall Success Metrics

- **Routing Centralization**: All routes defined in `routes/index.tsx` with domain route integration
- **Complete Cleanup**: All old directories and files removed
- **Zero Breaking Changes**: All functionality works identically after refactor
- **Import Validation**: All imports use new domain structure, no old paths referenced
- **Type Safety**: Zero TypeScript compilation errors
- **Runtime Health**: Zero runtime errors or warnings
- **Visual Consistency**: UI, theme, and styling remain 100% unchanged

