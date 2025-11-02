# Frontend Structure Design

## Proposed Structure

```
src/
  routes/
    index.tsx                  # Centralized routes (imports domain routes)
  
  company/
    api/                      # HTTP API calls to backend
      companyApi.ts
      index.ts
    types/                    # Domain-specific TypeScript types/interfaces
      company.ts
      contact.ts
      index.ts
    hooks/                    # Custom hooks
      useCompanies.ts
      useContacts.ts
      index.ts
    components/               # Domain components (feature-based nesting)
      company-list/           # Feature: list view
        CompanyList.tsx
        CompanyTable.tsx
        CompanyCards.tsx
        CompanyFilters.tsx
        index.ts
      company-form/           # Feature: create/edit
        CompanyForm.tsx
        CompanyFormFields.tsx
        index.ts
      overview-tab/           # Feature: overview tab
        OverviewTab.tsx
        components/
        types/
        index.ts
      funds-tab/              # Feature: funds tab
        FundsTab.tsx
        components/
        types/
        index.ts
    routes.tsx                # Domain route definitions
    pages/                    # Page components
      CompanyPage.tsx
    index.ts                  # Domain barrel export (public API)

  banking/
    api/
    types/
    hooks/
    components/               # Feature-based nesting
    routes.tsx
    pages/

  fund/
    api/
    types/
    hooks/
    components/
    routes.tsx
    pages/

  shared/
    types/                    # Cross-domain types (enums, errors, DTOs)
      enums.ts                # Country, Currency, SortOrder
      errors.ts               # ErrorInfo, ErrorType
      dto.ts                  # ApiResponse, common DTOs
      index.ts
    ui/                       # Reusable UI components
    hooks/                    # Cross-domain hooks
    utils/                    # Pure utility functions
```

## Strengths

- ✅ Domain-driven organization (matches backend)
- ✅ Clear separation of concerns
- ✅ Scales well with new domains
- ✅ Shared utilities isolated

## Open Questions

1. **API folder**: `api/` vs `services/`?
   - **What it contains**: Functions that make HTTP calls to backend (e.g., `getCompany(id)`, `createCompany(data)`)
   - **`api/`**: More conventional in frontend React/TypeScript; clearly indicates HTTP API communication
   - **`services/`**: Matches backend terminology; broader term (could imply business logic)
   - **Recommendation**: `api/` - clearer separation (frontend handles HTTP, backend handles business logic)
2. **Models folder**: `models/` vs `types/`?
   - **What it contains**: TypeScript interfaces/types for domain entities (e.g., `Company`, `Fund`, `Bank`)
   - **`models/`**: Mirrors backend structure; currently used in codebase
   - **`types/`**: TypeScript convention; clearly indicates type definitions only (no behavior)
   - **Recommendation**: `types/` - standard TypeScript practice, avoids confusion with backend behavioral models
3. **State folder**: Do we need `state/` at domain level?
   - **Current setup**: Zustand global store (`src/store/`) for app-wide state (preferences, UI state)
   - **Server state**: Handled by custom hooks (`hooks/data/`) - data fetching and caching
   - **When you need `state/`**: Complex shared client state within a domain (beyond server data)
   - **Examples**: Optimistic updates, complex form state, multi-step workflows
   - **Recommendation**: **Skip `state/` folder** - use global store for app-wide, hooks for server data, component state for local. Only add domain stores if clear need.
4. **Routing**: Where should route definitions live?
   - **What it means**: React Router `<Route>` components that map URLs to page components (e.g., `/companies/:companyId` → `CompanyPage`)
   - **Industry standard**: **Centralized routing** is the best practice for enterprise apps
   - **Benefits**: Single source of truth, easier maintenance, consistent handling, better overview
   - **Option 1**: Keep in `App.tsx` (simple, works well for small-to-medium apps)
   - **Option 2**: Top-level `routes/` folder (`src/routes/index.tsx` - imports from domain routes, combines all)
   - **Option 3**: Hybrid - domain routes in `company/routes.tsx`, imported by `routes/index.tsx` or `App.tsx`
   - **Recommendation**: **Option 2 or 3** - centralized config (`routes/index.tsx`) that imports domain route definitions. Keeps routes centralized but organized by domain.
5. ✅ **File organization**: Use nested folders (feature-based)
   - **Decision**: Nested structure - group by feature/functionality
   - **Pattern**: `company-list/`, `company-form/`, `overview-tab/` - each feature has its own folder
   - **Structure**: Feature folder contains related components, types, and index file
   - **Benefits**: Clear feature boundaries, easier to find related files, scales well
6. **Index files**: Barrel exports vs direct imports?
   - **What it means**: Whether to use `index.ts` files that re-export everything from a folder
   - **Barrel exports**: `company/index.ts` exports all from domain, allowing clean imports
   - **Direct imports**: Import directly from file paths (e.g., `from './company/api/companyApi'`)
   - **Example - Barrel**: `import { CompanyList, CompanyCard } from '@/company'` (cleaner)
   - **Example - Direct**: `import { CompanyList } from '@/company/components/company-list/CompanyList'` (explicit paths)
   - **Enterprise best practice**: **Hybrid approach** - use barrel exports for public domain API, direct imports within features
   - **Public API barrels**: Domain-level `index.ts` (e.g., `company/index.ts`) - clean public interface
   - **Internal direct**: Within features/components, use direct imports to avoid circular dependencies
   - **Benefits**: Clean public API, explicit internal imports, better tree-shaking, avoids circular deps
   - **Pattern**: `import { CompanyList } from '@/company'` (public), `import { useFilter } from './hooks/useFilter'` (internal)
   - **Recommendation**: **Hybrid** - barrel exports for domain boundaries, direct imports within features
7. **Shared types**: Should `shared/types/` exist for cross-domain types?
   - **What it means**: Types that are used by multiple domains (e.g., `Country`, `Currency`, error types, common DTOs)
   - **Current pattern**: Top-level `types/` folder with `enums/shared.enums.ts`, `errors.ts`, `dto/`
   - **Option 1**: Keep at top-level `types/` folder (current approach - centralized)
   - **Option 2**: Move to `shared/types/` (aligns with domain structure - explicit shared location)
   - **Examples of shared types**: `Country`, `Currency`, `SortOrder`, `ErrorInfo`, `ApiResponse<T>`, common utility types
   - **Enterprise best practice**: **Use `shared/types/`** - aligns with domain-driven structure, explicit that these are cross-cutting concerns
   - **Benefits**: Clear separation, matches backend `shared/` pattern, explicit shared location, consistent with domain structure
   - **Recommendation**: **Move to `shared/types/`** - maintains domain-driven organization while clearly marking cross-domain types

## Recommendations

1. ✅ Use `api/` (frontend handles HTTP communication, backend handles business logic)
2. ✅ Use `types/` (TypeScript convention, clearly indicates type definitions only)
3. ✅ Skip `state/` folder (server state via hooks, global store for app-wide, component state for local)
4. ✅ **Centralized routing** - Use `routes/index.tsx` that imports domain route definitions. Industry standard for enterprise apps.
5. ✅ **Nested folders (feature-based)** - Group by feature/functionality (e.g., `company-list/`, `company-form/`). Clear boundaries, scales well.
6. ✅ **Hybrid imports** - Barrel exports for domain public API (`company/index.ts`), direct imports within features. Best practice for enterprise apps.
7. ✅ **Shared types in `shared/types/`** - Move cross-domain types (enums, errors, DTOs) to `shared/types/`. Aligns with domain-driven structure, matches backend pattern.

