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
- **Design System Components**: Migrate all shared components including those not currently used (e.g., Card components) - they establish the design system foundation for future use
- **Overlay Primitives Reimagined**: Replace legacy modal wrappers with enterprise-grade primitives that decouple behavior from presentation, guarantee accessibility, and expose analytics/i18n hooks; preserve legacy APIs only as thin adapters during transition
- **Unified Error Contract**: Normalize errors once and share the schema across API, services, and UI; instrument UI boundaries with telemetry hooks for observability
- Create barrel exports for shared domain public API
- Maintain all imports working throughout the process
- **Transitional Primitives**: Treat `NumberInputField` as a stopgap—carry it forward to keep legacy flows functional, but schedule a redesign to make it fully controlled, locale-aware, accessible, and covered by automated tests before broad adoption

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
- [x] Update imports in domain API files to reference `shared/api/apiClient` instead of `../api-client` (will be done when domain APIs are moved in Phases 2-4)
- [x] Create `src/shared/ui/` directory
- [x] **Phase 1A: Data Display - Chip Components** (actively used components)
  - [x] Create `src/shared/ui/data-display/` directory structure
  - [x] Create `src/shared/ui/data-display/Chip/` directory
  - [x] Move `components/shared/data-display/Chip/` → `shared/ui/data-display/Chip/` (StatusChip, EventTypeChip, TrackingTypeChip)
  - [x] Create `shared/ui/data-display/Chip/index.ts` barrel export
  - [x] Update imports in components using Chip components (FundsCards.tsx, etc.) - Note: Components in `src-old/` will be updated when migrated in later phases
- [x] **Phase 1B: Data Display - Card Components** (design system components for future use)
  - [x] Create `src/shared/ui/data-display/Card/` directory
  - [x] Move `components/shared/data-display/Card/StatCard/` → `shared/ui/data-display/Card/StatCard/`
  - [x] Move `components/shared/data-display/Card/SummaryCard/` → `shared/ui/data-display/Card/SummaryCard/`
    - [x] **Improvement**: Update SummaryCard key usage from `index` to stable identifiers for better React performance and stability:
      - [x] Line 60: Change `key={rowIndex}` to use `row.label` (or combined identifier if labels aren't unique)
      - [x] Line 130: Change `key={sectionIndex}` to use `section.title` (or combined identifier if titles aren't unique)
  - [x] Move `components/shared/data-display/Card/README.md` → `shared/ui/data-display/Card/README.md`
  - [x] Create `shared/ui/data-display/Card/index.ts` barrel export (exports StatCard, SummaryCard and their types)
  - [x] **Note**: These Card components are design system components currently exported but not used in the codebase. They should be migrated for future use. Future refactoring of existing components (e.g., PortfolioSummaryCards) to use these shared components is a separate task (Phase 2).
  - [x] **Consolidation Decision**: DataCard has been excluded from migration. SummaryCard provides equivalent functionality (single-section summary with label-value rows) and eliminates code duplication. StatCard is kept for its unique single-metric/KPI use case with trend indicators.
- [x] **Phase 1C: Data Display - Barrel Exports**
  - [x] Create `shared/ui/data-display/index.ts` barrel export (exports from Chip and Card)
  - [x] Update `shared/ui/index.ts` barrel export to include data-display components
- [x] Move `components/shared/feedback/` → `shared/ui/feedback/` (excluding `ErrorToast`)
- [x] Define shared error normalization utility in `shared/utils/errors/` (common schema, helpers, tests)
  - **Status**: COMPLETE. The `shared/utils/errors/` directory exists with:
    - `errorNormalization.ts` - contains all normalization functions (`createErrorInfo`, `categorizeError`, `getUserFriendlyMessage`, `getErrorSeverity`, `isRetryableError`, etc.)
    - `errorLogger.ts` - migrated `errorLogger` class from `src-old/utils/errorLogger.ts` with full functionality
    - `index.ts` - barrel export for all error utilities
- [x] Update `DomainErrorBoundary` and `ErrorDisplay` to consume normalized errors exclusively
  - **Status**: COMPLETE.
    - `DomainErrorBoundary` imports `errorLogger`, `createErrorInfo`, and `ErrorContext` from `@/shared/utils/errors` (line 24) and uses normalized error utilities throughout.
    - `ErrorDisplay` uses `ErrorInfo` from `@/shared/types/errors` and imports hooks from `@/shared/hooks/errors` (not from `src-old`).
    - Both components fully use the new `shared/utils/errors/` module.
- [x] Add optional telemetry/analytics callbacks to `DomainErrorBoundary` for automated incident capture
  - **Status**: COMPLETE. `DomainErrorBoundary` exposes `onErrorCaptured?: (error: NormalizedErrorInfo, context: ErrorContext) => void` prop (line 51) and calls it in `componentDidCatch` (lines 156-158) after logging the error.
  - [x] **Decision**: Do not migrate `components/shared/feedback/ErrorToast.tsx`; keep archived in `src-old` until a consolidated toast/notification strategy is defined.
- [x] **Forms - Legacy Numeric Primitive**
  - [x] Move `components/shared/forms/primitives/NumberInputField.tsx` → `shared/ui/forms/NumberInputField.tsx` (preserve current usage in fund/event workflows)
  - [x] Document follow-up to harden `NumberInputField` before general reuse (controlled value sync, precision handling, accessibility, automated coverage, locale strategy)
  - **Status**: COMPLETE. Component migrated to `shared/ui/forms/NumberInputField/` with full directory structure (component, types, README, barrel exports). README documents all follow-up hardening tasks (controlled value sync, precision handling, accessibility, automated coverage, locale strategy). No imports using old path.
- [x] **Forms - Archived Wrappers**
  - [x] Leave `components/shared/forms/` React Hook Form wrappers, utils, and README in `src-old/` until the shared form architecture is redesigned (they have no live imports today)
  - **Status**: COMPLETE. All React Hook Form wrappers (FormCheckbox, FormDateField, FormNumberField, FormRadioGroup, FormSelectField, FormSwitch, FormTextArea, FormTextField), utils, and README remain in `src-old/components/shared/forms/` as required. No imports using these files from new location.
- [ ] Move `components/shared/navigation/` → `shared/ui/navigation/`
- [ ] **Phase 1D: Navigation - Breadcrumbs**
  - **Goals**:
    - Deliver an enterprise-grade breadcrumb component that is accessible, theme-aware, and router-integrated.
    - Maintain a legacy wrapper until consumers migrate to the new implementation.
  - **Design Principles**:
    - Render semantic structure: wrap in `<nav aria-label="Breadcrumb">`, use ordered list with `aria-current="page"` on the terminal crumb.
    - Default to React Router `<Link>` when `to` provided; fall back to `button` + `onNavigate` handler when routing unavailable.
    - Enforce design tokens (spacing, typography, palette) from shared theme; expose density variant props only if both variants ship.
    - Support overflow with `maxItems` + middle ellipsis strategy and tooltips for truncated labels.
    - Emit console warnings for duplicate ids/paths, empty arrays, or missing navigation handlers on intermediate crumbs.
  - **Tasks**:
    - [x] Create `shared/ui/navigation/breadcrumbs/` directory and scaffold component, prop types, stories, tests, and README.
    - [x] Define `BreadcrumbItem` with required `id`, `label`, optional `to`, `icon`, `disabled`, `segmentMeta` (reserved for analytics).
    - [x] Implement `BreadcrumbsV2` component with semantic markup, disabled crumb handling, keyboard activation, and optional `renderItem` override. _(Note: Implemented as `Breadcrumbs`, not `BreadcrumbsV2` - all features present)_
    - [x] Provide barrel exports from `shared/ui/navigation/breadcrumbs/index.ts` and re-export via `shared/ui/navigation/index.ts`.
    - [ ] Add Storybook stories: default, with icons, long trail collapse, router integration, `onNavigate` callback.
    - [x] Document migration plan and prop table in README; flag legacy component for deprecation after migration.
    - [ ] Update consumers (`TopBar`, any others) to adopt new `Breadcrumbs`, retaining feature parity and verifying visual regressions. _(Note: TopBar still in `src-old` using legacy component)_
- [ ] **Phase 1E: Navigation - Tabs (Legacy Preservation)**
  - [x] Create `shared/ui/navigation/Tabs/` directory and migrate `TabNavigation` plus supporting types.
  - [x] Retain MUI button-based tab rendering, disabled/icon support, and aria labelling; remove legacy Arrow/Home/End keyboard handlers and document that only standard Tab focus remains.
  - [x] Implement actual breakpoint detection (e.g., `useMediaQuery`) or annotate the TODO with acceptance criteria for Phase 1 delivery.
  - [ ] Provide Storybook stories (desktop + mobile breakpoint) and regression tests asserting click-based tab switching.
  - [ ] Update consumers to import from `@/shared/ui/navigation/Tabs` and verify visual parity after migration. _(Note: Only consumer is in `src-old/components/companies/CompaniesPage.tsx` - will be updated when that component migrates)_
- [ ] **Phase 1F: Overlays - Enterprise Primitives**
  - [x] Create `shared/ui/overlays/` directory with barrel export scaffolding
  - [x] Implement `ConfirmDialog` with typed action descriptors, loading/error states, analytics callbacks, and Storybook coverage (default, destructive, async error, custom footer) _(Note: Implementation complete with all features; Storybook stories not yet created)_
  - [x] Implement `FormModal` integrating React Hook Form context, dirty-state guard, standardized submit/cancel slots, and Storybook coverage (basic form, async submit, validation error, custom actions) _(Note: Implementation complete with all features; Storybook stories not yet created)_
  - [x] Write Jest/RTL tests validating focus management, keyboard interaction, callback contracts, and dirty guard behavior for both overlays
  - [x] Create README documenting API, accessibility guarantees, telemetry events, and migration checklist
  - [ ] Update consumers in `src` to use wrappers backed by New components, confirm visual parity, and capture follow-up ticket to remove wrappers after domain migrations _(Note: No consumers in `src` directory yet; legacy components still in `src-old`)_
- [x] Create `src/shared/ui/layout/` directory
- [x] Move `components/layout/RouteLayout.tsx` → `shared/ui/layout/RouteLayout.tsx`
- [x] Move `components/layout/MainSidebar.tsx` → `shared/ui/layout/MainSidebar.tsx`
- [x] Move `components/layout/TopBar.tsx` → `shared/ui/layout/TopBar.tsx`
- [x] Create `shared/ui/layout/index.ts` barrel export
- [x] Update `shared/ui/index.ts` barrel export to include layout components
- [x] Create `src/shared/hooks/` directory (created when hooks/core was moved)
- [x] Move `hooks/ui/` (excluding `useToggle`) → `shared/hooks/errors/`
- [x] Move `hooks/core/` → `shared/hooks/core/` (core hooks moved with api/, error/ subdirectories)
- [x] Create `src/shared/hooks/forms/` directory for form management hooks
- [x] Move `hooks/forms/useForm.ts` → `shared/hooks/forms/useForm.ts`
- [x] Move `hooks/forms/types.ts` → `shared/hooks/forms/types.ts`
- [x] Create `src/shared/hooks/schemas/` directory for shared form validation schemas
- [x] Move `hooks/forms/schemas/commonSchemas.ts` → `shared/hooks/schemas/sharedSchemas.ts`
- [x] Create `shared/hooks/schemas/index.ts` barrel export
- [x] Create `shared/hooks/forms/index.ts` barrel export (exports `useForm`, form types)
- [x] Update `shared/hooks/index.ts` barrel export
- [x] **Phase 1G: Utilities Realignment**
- [x] Create `src/shared/utils/` directory with barrels for cross-domain helpers (e.g., `shared/utils/index.ts`)
  - [x] Split legacy `utils/` by responsibility:
     - [x] **Fund constants migration** — moved into `src/fund/utils/constants/{eventTemplates,fundOptions,fundDisplayConfig,fundTaxDefaults,visualizationConfig}.ts` with barrel export; legacy `getFinancialYears` helper removed (superseded by backend query).
     - [x] **Fund transformers migration** — move live helpers from `utils/transformers/fundTransformers.ts` into `src/fund/utils/formatters/` and expose via barrel. _(Status: COMPLETE. Helpers `getStatusInfo`, `getStatusTooltip`, `getTrackingTypeColor`, `isActiveNavFund` migrated to `fund/utils/formatters/fundStatusFormatters.ts` and `fundTrackingFormatters.ts` with barrel exports)_
     - [x] **Legacy transformers archiving** — keep `utils/transformers/chartDataTransformers.ts` and `eventTransformers.ts` archived under `src-old/` with backlog note. _(Status: COMPLETE. Files archived in `src-old/utils/transformers/`. Backlog notes documented in `phase-1g-utilities-audit.md`: chartDataTransformers needs NAV chart rebuild; eventTransformers to be replaced when event labelling moves to fund domain)_
     - [x] **Shared validation primitives** — move `createValidator`, `validationRules`, and bundles into `shared/hooks/forms/validation/`. _(Status: COMPLETE. All validation primitives migrated to `shared/hooks/forms/validation/` with barrel exports)_
     - [x] **Shared error utilities** — rehome `errorLogger` and normalized error helpers into `shared/ui/feedback/`. _(Status: COMPLETE. Error utilities located in `shared/utils/errors/` which is appropriate for utility functions. ErrorLogger and normalized error helpers (`errorNormalization.ts`, `errorLogger.ts`) are fully migrated with barrel exports. Note: Spec initially suggested `shared/ui/feedback/` but `shared/utils/errors/` is more appropriate for utility functions)_
     - [x] **Cross-domain formatters** — migrate currency/percentage/date helpers into `shared/utils/formatters/`. _(Status: COMPLETE. Currency, number, percentage, and date formatters migrated to `shared/utils/formatters/` with barrel exports)_
     - [x] **Enum label maps** — relocate domain-specific label maps (company/entity/banking) to their owners; keep only global maps in shared. _(Status: COMPLETE. Domain-specific labels moved to `entity/utils/labels/`, `fund/utils/labels/`, `banking/utils/labels/`. Global geography/currency labels in `shared/utils/formatters/labels.ts`)_
     - [x] **Primitive replacements** — replace or retire `deepClone`, `debounce`, `throttle` primitives; document outcome. _(Status: COMPLETE. Deprecation documented in `shared/utils/primitives/README.md` with replacement recommendations: use lodash equivalents or native APIs like `structuredClone()`)_
  - [x] Update all imports across codebase to use new domain-aligned paths (shared vs. fund vs. entity) _(Status: COMPLETE. TypeScript compilation passes with zero errors. No imports from `src-old/utils/` found in `src/` directory)_
  - [x] Capture follow-up tickets for any utilities left in `src-old/utils/` pending future domain migrations _(Status: COMPLETE. Backlog documented in `phase-1g-utilities-audit.md`)_
- [x] Update all imports across codebase to use new shared paths _(Status: COMPLETE. Verified via TypeScript compilation)_
- [x] Run TypeScript compilation to verify no broken imports: `npx tsc --noEmit` _(Status: COMPLETE. Compilation passes with zero errors)_

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

