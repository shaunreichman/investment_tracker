# Fund Event Cash Flows Specification

## Overview
Add the ability to record actual bank transfers for fund cash-flow events. Each `FundEvent` can have zero or more `FundEventCashFlow` records that capture real transfers (date, bank account, currency, amount). Event dates remain canonical for IRR and calculations; transfer dates are informational for now. Only investor-owned bank accounts are modeled.

## Design Principles
- Minimal, accurate, auditable data model (no attachments/workflows yet)
- Preserve existing IRR/date logic (transfer dates do not affect IRR)
- Strict reconciliation only when currencies match; otherwise defer
- Optional per-event cash flows; auto-computed completion status
- Keep scope to investor accounts only (no fund manager accounts)

## Scope
- Introduce `Bank` and `BankAccount` (owned by `Entity`)
- Introduce `FundEventCashFlow` (required links to `FundEvent` and `BankAccount`)
- Add `is_cash_flow_complete` to `FundEvent` (auto-set)
- Validation and reconciliation rules (including interest withholding)
- Remove `MANAGEMENT_FEE`, `CARRIED_INTEREST`, and `OTHER` from `EventType`

## Out of Scope (for now)
- API/Frontend integration
- Bank feed imports, matching, or settlement lifecycle
- Attachments/doc links
- Manager (counterparty) bank accounts
- Reports/aggregates

## Data Model

### Bank
- id (PK)
- name (string, required)
- country (string, required)
- swift_bic (string, optional)
- routing_number (string, optional)

### BankAccount
- id (PK)
- entity_id (FK -> `Entity.id`, required)
- bank_id (FK -> `Bank.id`, required)
- account_name (string, required)
- account_number (string, required)
- currency (string, required, ISO-4217 code)
- is_active (bool, default true)

Constraints/Rules:
- A `BankAccount` belongs to an `Entity`
- All cash flows from a `BankAccount` must use the same `currency`
- Uniqueness: (`entity_id`, `bank_id`, `account_number`) must be unique

### FundEvent (additions/changes)
- is_cash_flow_complete (bool, default false) — auto-managed
- Remove `MANAGEMENT_FEE`, `CARRIED_INTEREST`, and `OTHER` from `EventType`

### FundEventCashFlow
- id (PK)
- fund_event_id (FK -> `FundEvent.id`, required)
- bank_account_id (FK -> `BankAccount.id`, required)
- direction (enum: inflow | outflow, required; investor perspective)
- transfer_date (date, required; bank transaction date)
- currency (string, required; must equal `BankAccount.currency`)
- amount (float, required)
- reference (string, optional)
- notes (text, optional)

Constraints/Rules:
- A `FundEventCashFlow` is valid only when both `fund_event_id` and `bank_account_id` are set
- `currency` must equal the linked `BankAccount.currency`
- Multiple cash flows per event allowed (multi-day, multi-account)

## Event Applicability and Direction
Events that may have cash flows (investor perspective):
- Outflow: `CAPITAL_CALL`, `UNIT_PURCHASE`
- Inflow: `RETURN_OF_CAPITAL`, `DISTRIBUTION`, `UNIT_SALE`
- No cash flows: `TAX_PAYMENT`, `NAV_UPDATE`, `DAILY_RISK_FREE_INTEREST_CHARGE`, `EOFY_DEBT_COST`

Notes:
- Interest withholding: record only the net cash actually received on the `DISTRIBUTION` event; no separate cash flows for the associated `TAX_PAYMENT` event.
- `MANAGEMENT_FEE` removed from `EventType` (not used).

## Validation and Reconciliation

### Currency rules
1) If every `FundEventCashFlow.currency` equals the fund’s currency:
   - Enforce hard reconciliation within 0.01 (fund currency)
2) If any cash flow currency differs from the fund’s currency:
   - Skip reconciliation (no validation error)

Additionally:
- For each `FundEventCashFlow`, `currency` must equal `BankAccount.currency` (hard error otherwise)

### Reconciliation target (same-currency only)
Let `target_amount` be what cash flows must sum to within 0.01 tolerance.
- Default: `target_amount = FundEvent.amount`
- Special case (interest distribution with withholding):
  - If `FundEvent.event_type == DISTRIBUTION` and `FundEvent.distribution_type == INTEREST`, and a corresponding `TAX_PAYMENT` of type `NON_RESIDENT_INTEREST_WITHHOLDING` exists for the same fund and date (see matching below), then:
    - `target_amount = FundEvent.amount - sum(withholding_tax_payments.amount)`

Matching strategy for withholding tax payments:
- Same-date match only: same `event_date`, same fund, type `NON_RESIDENT_INTEREST_WITHHOLDING`

### Completion flag
- `FundEvent.is_cash_flow_complete` is auto-managed:
  - False if no cash flows exist for the event
  - True when same-currency reconciliation passes within tolerance
  - False when same-currency reconciliation fails
  - False when any cross-currency cash flows exist (validation skipped)

## Lifecycle
- `transfer_date` is the bank transaction date (informational for now)
- No settlement statuses
- Cash flows can be added/edited until reconciliation passes; completion is computed automatically (no manual override)

## Migration / Backfill
- Create `banks`, `bank_accounts`, `fund_event_cash_flows` tables
- Add `is_cash_flow_complete` to `fund_events`
- Drop `MANAGEMENT_FEE`, `CARRIED_INTEREST`, and `OTHER` from `eventtype` enum (confirm no live data relies on these)
- Do not modify historical events; cash flows are optional and may be added over time

## Phases and Tasks

### Phase 0: Spec Finalization
- [ ] Confirm open questions below

### Phase 1: Schema (Alembic + Models)
- [x] Add `Bank` and `BankAccount` models and tables
- [x] Add `FundEventCashFlow` model and table
- [x] Add `is_cash_flow_complete` to `FundEvent`
- [x] Remove `MANAGEMENT_FEE`, `CARRIED_INTEREST`, and `OTHER` from `EventType` (code-level; DB enum storage varies by dialect)
- [x] Constraints: `FundEventCashFlow.currency == BankAccount.currency` (note: enforced in domain logic due to cross-table limitation)
- [x] Uniqueness: (`entity_id`, `bank_id`, `account_number`) on `BankAccount`
- [x] Indexes: `fund_event_id`, `bank_account_id`, `transfer_date` on `FundEventCashFlow`

### Phase 2: Domain Logic & Validation
- [x] Add creation/update methods for bank, bank account (class methods)
- [x] Add methods to add/update/delete `FundEventCashFlow` records
- [x] Implement reconciliation logic and auto-manage `is_cash_flow_complete`
- [x] Implement withholding matching via a centralized helper: same-date interest-withholding pairing only
- [x] Unit tests for reconciliation and withholding scenarios (completed in Phase 2A)

Notes:
- Cash flow direction is automatically inferred from `FundEvent.event_type` (outflow: CAPITAL_CALL, UNIT_PURCHASE; inflow: RETURN_OF_CAPITAL, DISTRIBUTION, UNIT_SALE). No manual direction input.
- `distribution_type` is required for distribution creation and validated.

### Phase 2A: Testing Suite Implementation
- [x] Add `BankFactory` and `BankAccountFactory` to test factories
- [x] Add `FundEventCashFlowFactory` to test factories
- [x] Create domain logic tests for cash flow reconciliation
- [x] Create domain logic tests for withholding tax matching
- [x] Create domain logic tests for completion flag management
- [x] Create API endpoint tests for bank CRUD operations
- [x] Create API endpoint tests for bank account CRUD operations
- [x] Create API endpoint tests for fund event cash flows CRUD operations
- [x] Create integration tests for complete cash flow workflows
- [x] Create property-based tests for reconciliation invariants

### Phase 3: API Implementation ✅
- [x] Design API endpoints/DTOs for CRUD (cash flows, banks, accounts)
- [x] Implement endpoints and validations
- [x] Add minimal queries (by event, by account, by date)

### Phase 4: Frontend (Deferred)
- [ ] UI to view/add/edit cash flows on events
- [ ] Display completion status and reconciliation messages

### Phase 5: Reporting (Deferred)
- [ ] Aggregations by account/date range/status

## Current Progress Summary

### Phase 2A Status: 100% Complete ✅
- **Domain Logic**: 100% Complete (11/11 tests passing)
- **API Endpoints**: 100% Complete (48/48 tests passing)
- **Integration Tests**: 100% Complete (5/5 tests passing)
- **Property-Based Tests**: 100% Complete (7/7 tests passing)

### Phase 3 Status: 100% Complete ✅
- **API Design**: 100% Complete
- **API Implementation**: 100% Complete
- **API Testing**: 100% Complete (48/48 tests passing)

### Completed Components
- ✅ All database models and migrations
- ✅ Complete domain logic implementation
- ✅ Full API endpoint implementation
- ✅ Comprehensive unit and API testing
- ✅ Test factories and fixtures
- ✅ API endpoints for cash flows, banks, and bank accounts
- ✅ Complete CRUD operations with validation
- ✅ Query capabilities by event, account, and date

### Next Phase: Frontend Implementation
- Ready to begin Phase 4: Frontend UI development
- Backend foundation is complete and fully tested

## Success Criteria
- ✅ Accurate recording of actual transfers per event
- ✅ Strict reconciliation for same-currency flows with 0.01 tolerance
- ✅ Interest withholding handled: net receipt reconciles using matched TAX_PAYMENT(s)
- ✅ `is_cash_flow_complete` reliably reflects reconciliation status
- ✅ No regressions to IRR or event calculations
- ✅ Comprehensive test coverage for all cash flow functionality
- ✅ API endpoints properly validated with edge case testing
- ✅ Domain logic thoroughly tested with property-based validation
- ✅ Complete API implementation with CRUD operations
- ✅ Full validation and error handling
- ✅ Query capabilities for all use cases

## Open Questions
None for now.


