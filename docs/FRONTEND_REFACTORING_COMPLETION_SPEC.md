## Frontend Refactoring Completion Specification

### Overview
Finalize the frontend refactor into a first‑class, professional system by completing remaining phases, addressing audit items, and instituting lightweight, reusable UI and form primitives. Maintain strict functional and visual parity while improving consistency, performance, and developer experience.

### Design Philosophy
- **Single source of truth**: Consolidate types, API surface, and shared primitives.
- **Consistency by default**: Shared UI components and validation patterns.
- **Pragmatism over frameworks**: Prefer small composable hooks/components over heavy abstractions.
- **Performance where it counts**: Memoization and code-splitting for heavy paths.
- **A11y baked-in**: Accessibility checks and linting as a baseline for new code.
- **Zero regression**: Preserve existing behavior and visual parity.

### Problems We’re Solving
- Duplicate type definitions that may drift.
- Redundant API methods for the same endpoint.
- Missing shared UI primitives causing stylistic drift.
- Forms lack a minimal, consistent orchestration layer.
- Missed low-effort performance wins (memoization, lazy loading).
- A11y checks not enforced in CI for new code.

### Success Criteria
- All shared domain types defined in `frontend/src/types/api.ts` (no duplicates).
- API client exposes a single canonical method per endpoint.
- Reusable UI primitives adopted across modals/sections.
- Forms share validation/state primitives; no hand-rolled one-offs.
- Heavy components/code paths are memoized or lazy loaded.
- A11y linting enabled in CI for new/changed code; `jest-axe` smoke on key surfaces.

## Implementation Strategy

### Phase 0: Immediate Cleanup & Consolidation
**Goal**: Remove drift and redundancies before further work.
**Tasks**:
- [x] Deduplicate `ExtendedFundEvent`: remove interface from `utils/helpers.ts`; import from `types/api.ts` wherever needed.
- [x] Unify API surface: alias `getFund` to same endpoint shape and keep `getFundDetail` as canonical.
- [ ] Remove unused dependency: delete `axios` from `frontend/package.json` and lockfile; ensure no references remain.
- [x] Grep and remove any stale references to edit‑event flows (edit UI is decommissioned).
- [x] Enable a11y linting dependencies (add `eslint-plugin-jsx-a11y`); integrate rule in CI (pending CI wiring).
**Design Principles**:
- One definition of each public type.
- One public client method per endpoint to prevent misuse.

### Phase 4: Shared UI Components
**Goal**: UI consistency and reuse across pages and modals.
**Tasks**:
- [ ] Create `frontend/src/components/ui/` directory.
- [ ] Add primitives with a11y defaults:
  - [ ] `StatusChip.tsx`
  - [ ] `EventTypeChip.tsx`
  - [ ] `ConfirmDialog.tsx`
  - [ ] `ErrorBoundary.tsx`
  - [ ] `LoadingSpinner.tsx`
  - [ ] `FormField.tsx` (label/help/error wiring)
  - [ ] `FormSection.tsx`
- [ ] Replace ad‑hoc usages in FundDetail and modals incrementally.
- [ ] Add focused tests (render, props, a11y labels) for each component.
**Design Principles**:
- Type‑safe props; consistent spacing/typography.
- Keyboard/focus semantics and ARIA attributes included by default.

### Phase 5: Business Logic Extraction (Targeted)
**Goal**: Extract only reusable transformations into pure utilities.
**Tasks**:
- [ ] Create `frontend/src/utils/transformers/`.
- [ ] Move/standardize reusable transformations:
  - [ ] `eventTransformers.ts` (event display mapping, tax/event labeling)
  - [ ] `chartDataTransformers.ts` (NAV chart preparation)
  - [ ] `fundTransformers.ts` (summary derivations when needed)
- [ ] Ensure pure, memo‑friendly functions with unit tests.
**Design Principles**:
- Keep hooks thin; prefer pure functions with memoization at call sites.

### Phase 6: Form System (Pragmatic)
**Goal**: Minimal, consistent building blocks for forms.
**Tasks**:
- [ ] Add `frontend/src/hooks/forms/`:
  - [ ] `useFormState.ts` (controlled state, touched, reset)
  - [ ] `useFormValidation.ts` (run validators, field errors, form validity)
  - [ ] Reuse existing `utils/validators.ts` and `useEventForm` where applicable.
- [ ] Refactor `CreateFundModal` to compose these primitives without changing UX.
- [ ] Keep validation messages and enable/disable behavior identical.
- [ ] Tests: validation behavior, enable/disable, error rendering (logic only).
**Design Principles**:
- No heavy framework; small composable hooks.
- Centralized rules in `utils/validators.ts` remain the source of truth.

### Phase 7: Layout & Navigation (Optional, Low Priority)
**Goal**: Further separation for readability, if needed.
**Tasks**:
- [ ] Extract `FundDetailHeader.tsx` (breadcrumbs, title, sidebar toggle).
- [ ] Extract `FundDetailSidebar.tsx` (composition of summary sections, sticky behavior).
- [ ] Keep `FundDetail.tsx` as orchestrator only.
**Design Principles**:
- Only proceed if it reduces noise; avoid churn for minimal gains.

### Phase 8: Performance Optimization (Targeted)
**Goal**: Reduce unnecessary renders and initial load.
**Tasks**:
- [x] Memoize heavy components with stable props:
  - [x] `EventRow.tsx`, `GroupedEventRow.tsx`
  - [x] `TableHeader.tsx`
  - [ ] `TableFilters.tsx`
- [ ] Strengthen memoization in `useEventGrouping` (stable outputs when inputs unchanged).
- [x] Code splitting (lazy load with Suspense):
  - [x] `fund/events/CreateFundEventModal`
  - [x] `companies/create-fund/CreateFundModal`
  - [ ] `fund/detail/summary/UnitPriceChartSection`
- [ ] Bundle monitoring (simple size check in CI/build output).
- [ ] Virtualization (optional): evaluate only if events > 500 consistently.
**Design Principles**:
- Prefer memoization/code‑split over premature virtualization.

### Phase 9: Testing & Documentation
**Goal**: Lock in quality gates and usage guidance.
**Tasks**:
- [ ] Add `jest-axe` smoke checks for CreateFundEventModal, CreateFundModal, FundDetail.
- [ ] Enable `eslint-plugin-jsx-a11y` in CI (treat a11y warnings as errors for new/changed code).
- [ ] Document UI kit usage patterns (MD in `docs/`); Storybook optional.
- [ ] Keep tests focused on logic and behavior (not styling).
**Design Principles**:
- Tests assert behavior, not CSS.
- Documentation illustrates composition and props expectations.

### Phase 10: Migration & Final Cleanup
**Goal**: Ensure the entire app uses the new structure; remove dead code.
**Tasks**:
- [ ] Update imports to UI kit and transformers where applicable.
- [ ] Remove unused helpers/types after migrations.
- [ ] Confirm all tests/builds pass; fix any lint errors.
- [ ] Move completed specs to `docs/specs_completed/` and update references.
**Design Principles**:
- Small PRs; green builds; reversible steps.

## Success Metrics
- **Consistency**:
  - [ ] No duplicate type interfaces (e.g., `ExtendedFundEvent`).
  - [ ] Canonical API methods only for each endpoint.
- **UI/UX**:
  - [ ] Shared UI components used in FundDetail and modals.
  - [ ] A11y lint passes for new code; `jest-axe` smoke checks pass.
- **Performance**:
  - [x] Table row components memoized; reduced re‑render counts in dev tools.
  - [x] Modals lazy‑loaded; smaller initial bundle.
  - [ ] NAV chart lazy‑loaded (pending).
  - [ ] No perceived performance regressions under typical datasets.
- **Developer Experience**:
  - [ ] Smaller diffs via UI kit.
  - [ ] Clear validators and form hooks with tests.

## Risk Mitigation
- **Type/API Drift**: Single source modules and removal of duplicates.
- **Regression Risk**: Incremental PRs, logic‑focused tests, screenshot checks where feasible.
- **Over‑engineering**: Avoid framework swaps; only add primitives with clear reuse.
- **A11y Regressions**: CI a11y lint + `jest-axe` smoke checks on key surfaces.

## Rollout Plan
- Ship Phase 0 first (fast wins). Then Phase 4 (UI kit) to unlock reuse. Proceed with Phases 5–6 (transformers + forms) in small slices, followed by targeted Phase 8 perf, then Phase 9/10 gates and cleanup. Keep each PR self‑contained, reversible, and covered by tests.


