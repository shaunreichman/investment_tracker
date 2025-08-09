### Title
Backend Testing Suite — Professional, Layered, and Fast

### Goals and Non-Goals
- **goals**:
  - Establish a first-class, layered test suite for the backend with clear taxonomy, fixtures, and conventions
  - Achieve initial coverage of 70–80% and a stable runtime under 90 seconds for a full local run
  - Ensure deterministic, isolated tests with clean data setup and teardown
  - Validate key financial calculations (IRR, cash-flow generation, tax events) with crisp assertions and invariants
  - Provide an ergonomic developer experience and CI-ready structure (coverage gates, fast vs. full runs)
- **non-goals**:
  - Rewriting domain logic
  - Frontend test strategy (covered elsewhere)
  - Heavy end-to-end/browser tests

### Key Principles
- **Layered**: unit (pure calcs) → domain-integration (models + session) → API (Flask routes) → optional regression
- **Isolation**: each test independent; DB state reset per test
- **Determinism**: stable seeds and data builders; numeric assertions with tolerances
- **Clarity-first**: tests assert key logic; avoid snapshot text-diffing except in isolated regression checks
- **Backend owns sessions**: outer layer manages sessions; fixtures reflect project-wide architecture
- **Minimal flakiness**: time, randomness, and ordering handled explicitly

### Test Taxonomy and Structure
- `tests/unit/`
  - Pure functions in `src/*/calculations.py` (e.g., IRR helpers, transformers that don’t hit DB)
- `tests/domain/`
  - Model class methods and domain methods: `Fund.add_distribution`, `create_daily_risk_free_interest_charges`, `update_status`, tax event creation
- `tests/api/`
  - Flask `test_client` tests for endpoints: contract, validation, happy-paths, critical error paths
- `tests/property/` (introduced gradually)
  - Target high-value invariants of core finance math using Hypothesis
- `tests/regression/` (optional, off by default locally)
  - Legacy baseline/long scenarios; not part of required CI gates

### Tooling
- pytest
- pytest-cov (coverage)
- factory_boy + Faker (data builders)
- hypothesis (property-based tests for critical calculations)
- optional: pytest-xdist (parallel), freezegun (time control)

### Database Strategy
- **Engine**: temporary SQLite file per test session; `Base.metadata.create_all` for schema setup
- **Session**: scoped session factory created once per session; per-test transaction/rollback or truncate strategy
- **Reference data**: seeding utilities for risk-free rates when tests require them
- **Migrations**: small “migration smoke” job that runs alembic upgrades against a temp DB (not per-test)

### Fixtures (conftest.py)
- `engine` (session scope): creates temp SQLite DB file and initializes schema
- `SessionFactory` (session scope): SQLAlchemy sessionmaker bound to `engine`
- `db_session` (function scope): fresh session per test; rolls back and expunges at end
- `app` (session scope): Flask app via `create_app()` with test config
- `client` (function scope): Flask test_client bound to fresh `db_session`
- `seed_rfrates` (function/helper): load minimal risk-free rates
- `faker` (function scope): Faker seeded per test

### Factories (tests/factories.py)
- `EntityFactory`, `InvestmentCompanyFactory`, `FundFactory` (supports `tracking_type` variants), `FundEventFactory`, `TaxStatementFactory`
- Provide sensible defaults; allow overrides via kwargs
- Align with MANUAL / CALCULATED / SYSTEM labeling in test data where helpful (short comments or variable names)

### Assertions and Conventions
- Monetary/IRR assertions use tolerances (e.g., abs diff <= 1e-6 for IRR, <= 0.01 for currency)
- Explicit invariants:
  - System-generated events (tax payments, daily interest, EOFY debt costs) are idempotent
  - Adding events updates derived values consistently
  - NAV-based and cost-based paths update the correct derived fields
- Naming: test names describe behavior, not implementation; arrange-act-assert structure
- Seeded randomness: stable seeds for Faker and Hypothesis profiles

### Property-Based Testing Plan
- **Why**: catches edge cases and invariant violations in finance math that example-based tests miss
- **Scope (initial)**:
  - IRR cash-flow properties: adding zero-cash-flow periods doesn’t change IRR; proportional scaling of all cash flows leaves IRR unchanged
  - NAV update properties: monotonic NAV changes produce expected sign of returns
  - Tax statement aggregations: non-negative rate inputs produce non-negative tax amounts
- **Execution**:
  - Keep example count modest by default (e.g., 50) for speed; define a “thorough” profile for nightly
  - Focus on pure/unit level first; domain-level properties added sparingly

### Runtime Targets
- **fast default**: < 45–60 seconds locally for unit + domain + API
- **full suite**: < 90 seconds locally including heavier scenarios
- Mark slow tests with `@pytest.mark.slow`; exclude by default, include in nightly profile

### Coverage Targets
- Initial: 70–80%
- Gate in CI at 70% initially; raise to 80–85% after phase 2
- Coverage focus on domain calculations and API input validation/error handling

### CI Strategy (deferred implementation)
- PR: fast subset + coverage gate; no regression tests
- Nightly: full + `-m slow` + extended Hypothesis profile + migration smoke
- Artifacts: coverage XML + HTML report

### Migration Smoke Test (lightweight)
- Create temp DB → run alembic upgrade head → verify key tables exist
- Optionally instantiate minimal records via factories to ensure ORM compatibility

### Phases and Tasks
- **Phase 0 — Project Setup**
  - [ ] Add test dependencies to `requirements.txt`: pytest, pytest-cov, factory_boy, Faker, hypothesis, freezegun (optional), pytest-xdist (optional)
  - [ ] Create `tests/conftest.py` with engine/session/app/client fixtures
  - [ ] Add `tests/factories.py` for core models
  - [ ] Establish pytest.ini or pyproject config for markers, hypothesis settings, and coverage

- **Phase 1 — Unit Tests (Pure Calculations)**
  - [ ] Cover functions in `src/*/calculations.py` (entity, fund, tax, rates)
  - [ ] Add tolerance-aware assertions for IRR and monetary calculations
  - [ ] Introduce initial property tests for IRR invariants (modest example count)

- **Phase 2 — Domain Integration Tests**
  - [ ] CRUD and business flows for `Fund` (cost-based and NAV-based)
  - [ ] Tax event generation (`create_tax_payment_events`, EOFY debt cost, daily charges)
  - [ ] Idempotency checks for system events
  - [ ] Derived fields consistency (`current_equity_balance`, `average_equity_balance`, stored IRRs)
  - [ ] Extend property tests selectively to domain invariants where practical

- **Phase 3 — API Contract Tests**
  - [ ] `GET /api/dashboard/*` endpoints: shape, types, and basic aggregates
  - [ ] `POST /api/investment-companies`, `/api/entities`, `/api/funds`, `/api/funds/:id/events`, `/api/funds/:id/tax-statements`
  - [ ] Validation and key error cases (missing fields, invalid enums, ranges)
  - [ ] Ensure serialization matches frontend expectations (fields and enums)

- **Phase 4 — Migration Smoke + Profiles**
  - [ ] Add migration smoke test outside the per-test DB cycle
  - [ ] Define pytest markers and profiles: default (fast), full (includes `slow`), nightly (thorough Hypothesis)

- **Phase 5 — Cleanup and Quality Gates**
  - [ ] Archive outdated legacy tests under `tests/_archive/` and exclude from test discovery
  - [ ] Enforce coverage gate at 70% in CI, plan to raise to 80–85%
  - [ ] Documentation: README section for running tests; dev ergonomics (fast vs. full commands)

### Commands (developer ergonomics)
- Run fast default:
  - `pytest`
- Run with coverage:
  - `pytest`
  - `pytest --cov=src --cov-report=term-missing`
- Run full including slow:
  - `pytest -m "not slow"`
  - `pytest -m slow`
- Nightly thorough Hypothesis profile (later):
  - `pytest -m "not slow" --hypothesis-profile=thorough`

### Risks and Mitigations
- **Floating-point sensitivity**: use decimal/tolerances where appropriate; assert within sensible epsilons
- **Test data brittleness**: prefer factories/builders; avoid strict snapshots; assert on semantic fields
- **Flaky time-based logic**: freeze time in tests; avoid now() without control
- **Parallelization with SQLite**: default to session-scoped temp file; avoid shared in-memory engines

### Acceptance Criteria
- CI-ready pytest suite with: fixtures, factories, unit + domain + API layers
- Coverage ≥ 70% and documented commands to run fast vs. full
- Deterministic, isolated tests with reproducible seeds
- Documented conventions aligned with project architecture and session management


