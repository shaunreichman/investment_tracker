# Comprehensive Migration Tasks

## Overview
This document outlines the complete migration plan for reorganizing the investment tracker codebase from a monolithic structure to a domain-driven architecture. **CRITICAL REQUIREMENT: Every piece of code must be copied with EXACT same logic, docstrings, and output as the original.**

## Migration Principles
1. **EXACT PRESERVATION**: Copy every method/function with identical logic, docstrings, and behavior
2. **NO LOGIC CHANGES**: Maintain exact same output and calculations
3. **COMPLETE INVENTORY**: Every single method/function must be accounted for
4. **VERIFICATION**: Test each migration to ensure identical results

## Detailed Method/Function Mapping

### EXACT TARGET LOCATIONS FOR EACH METHOD/FUNCTION

#### From src/calculations.py → Target Locations:

**→ src/shared/calculations.py:**
- `get_equity_change_for_event(event, fund_type)` - Used by multiple modules
- `get_reconciliation_explanation(gross_diff, tax_diff, net_diff)` - Used by tax module

**→ src/fund/calculations.py:**
- `calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200)`
- `calculate_average_equity_balance_nav(unit_events, start_date, end_date)`
- `calculate_average_equity_balance_cost(capital_events)`
- `calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)`
- `calculate_nav_based_capital_gains(events)`
- `calculate_cost_based_capital_gains(events)`
- `orchestrate_nav_based_average_equity(unit_events)`
- `orchestrate_cost_based_average_equity(capital_events)`
- `orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False)`
- `calculate_nav_event_amounts(unit_events)`
- `calculate_cumulative_units_and_cost_basis(unit_events, as_of_date=None)`
- `calculate_nav_based_cost_basis_for_irr(unit_events, as_of_date=None)`

**→ src/tax/calculations.py:**
- `net_income(total_income, non_resident_withholding_tax_from_statement)`
- `tax_payable(total_interest_income, interest_taxable_rate, non_resident_withholding_tax_from_statement)`
- `interest_tax_benefit(total_interest_expense, interest_deduction_rate)`

**→ src/entity/calculations.py:**
- `get_financial_years_for_fund_period(start_date, end_date, entity)`
- `get_financial_year_dates(financial_year, tax_jurisdiction="AU")`

**→ src/rates/calculations.py:**
- `get_risk_free_rate_for_date(target_date, risk_free_rates)`

#### From src/models.py → Target Locations:

**→ src/investment_company/models.py:**
- `InvestmentCompany(Base)` class with `__repr__(self)` method

**→ src/entity/models.py:**
- `Entity(Base)` class (already exists)
- Add `__repr__(self)` method from old models.py
- Add `get_financial_year(self, date)` method from old models.py

**→ src/tax/models.py:**
- `TaxStatement(Base)` class (already exists)
- Add these methods from old models.py:
  - `net_interest_income(self)` - Property
  - `get_net_income(self)` - Method
  - `calculate_tax_payable(self)` - Method
  - `calculate_interest_tax_benefit(self)` - Method
  - `get_financial_year_dates(self)` - Method
  - `__repr__(self)` - Method
  - `calculate_total_income(self)` - Method
  - `get_tax_payment_date(self)` - Method
  - `reconcile_with_actual_distributions(self, session=None)` - Method
  - `_create_fy_debt_cost_event_object(self)` - Method
  - `create_fy_debt_cost_event(self, session=None)` - Method
  - `non_resident_withholding_tax_difference(self)` - Property
  - `calculate_interest_income_fields(self, session=None)` - Method
  - `sum_tax_payments_for_fy(self, session=None)` - Method

**→ src/tax/creation.py:**
- `_create_or_update_tax_statement_object(self, entity_id, financial_year, **kwargs)` - From Fund class
- `create_or_update_tax_statement(self, entity_id, financial_year, session=None, **kwargs)` - From Fund class
- `_create_tax_payment_event_object(self, tax_statement)` - From Fund class
- `create_tax_payment_events(self, session=None)` - From Fund class

#### From src/utils.py → Target Locations:

**→ src/shared/utils.py:**
- `with_session(method)` decorator

## Current Structure Analysis

### src/calculations.py (730 lines) - COMPLETE INVENTORY
**Functions to migrate (18 total):**
1. `calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200)` - IRR calculation
2. `calculate_average_equity_balance_nav(unit_events, start_date, end_date)` - NAV-based average equity
3. `calculate_average_equity_balance_cost(capital_events)` - Cost-based average equity
4. `calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)` - Debt cost calculation
5. `calculate_nav_based_capital_gains(events)` - NAV-based capital gains
6. `calculate_cost_based_capital_gains(events)` - Cost-based capital gains
7. `orchestrate_nav_based_average_equity(unit_events)` - NAV average equity orchestration
8. `orchestrate_cost_based_average_equity(capital_events)` - Cost average equity orchestration
9. `orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False)` - IRR orchestration
10. `net_income(total_income, non_resident_withholding_tax_from_statement)` - Net income calculation
11. `tax_payable(total_interest_income, interest_taxable_rate, non_resident_withholding_tax_from_statement)` - Tax payable calculation
12. `interest_tax_benefit(total_interest_expense, interest_deduction_rate)` - Interest tax benefit
13. `get_financial_year_dates(financial_year, tax_jurisdiction="AU")` - Financial year dates
14. `calculate_nav_event_amounts(unit_events)` - NAV event amounts
15. `calculate_cumulative_units_and_cost_basis(unit_events, as_of_date=None)` - Cumulative units calculation
16. `calculate_nav_based_cost_basis_for_irr(unit_events, as_of_date=None)` - NAV cost basis for IRR
17. `get_risk_free_rate_for_date(target_date, risk_free_rates)` - Risk-free rate lookup
18. `get_reconciliation_explanation(gross_diff, tax_diff, net_diff)` - Reconciliation explanation
19. `get_financial_years_for_fund_period(start_date, end_date, entity)` - Financial years for period
20. `get_equity_change_for_event(event, fund_type)` - Equity change for event

### src/models.py (2253 lines) - COMPLETE INVENTORY

#### Classes to migrate:
1. `InvestmentCompany(Base)` - Investment company model
2. `Entity(Base)` - Entity model (already exists in entity module)
3. `Fund(Base)` - Fund model (✅ COMPLETED)
4. `FundEvent(Base)` - Fund event model (✅ COMPLETED)
5. `RiskFreeRate(Base)` - Risk-free rate model (already exists in rates module)
6. `TaxStatement(Base)` - Tax statement model (already exists in tax module)

#### Enums to migrate:
1. `EventType(enum.Enum)` - Event types (✅ COMPLETED)
2. `FundType(enum.Enum)` - Fund types (✅ COMPLETED)
3. `DistributionType(enum.Enum)` - Distribution types (✅ COMPLETED)
4. `TaxPaymentType(enum.Enum)` - Tax payment types (✅ COMPLETED)

#### InvestmentCompany methods to migrate:
1. `__repr__(self)` - String representation

#### Entity methods to migrate:
1. `__repr__(self)` - String representation
2. `get_financial_year(self, date)` - Financial year calculation

#### TaxStatement methods to migrate (from old models.py):
1. `net_interest_income(self)` - Property for net interest income
2. `get_net_income(self)` - Get net income
3. `calculate_tax_payable(self)` - Calculate tax payable
4. `calculate_interest_tax_benefit(self)` - Calculate interest tax benefit
5. `get_financial_year_dates(self)` - Get financial year dates
6. `__repr__(self)` - String representation
7. `calculate_total_income(self)` - Calculate total income
8. `get_net_income(self)` - Get net income (duplicate)
9. `get_tax_payment_date(self)` - Get tax payment date
10. `reconcile_with_actual_distributions(self, session=None)` - Reconcile distributions
11. `_create_fy_debt_cost_event_object(self)` - Create FY debt cost event
12. `create_fy_debt_cost_event(self, session=None)` - Create FY debt cost event
13. `non_resident_withholding_tax_difference(self)` - Property for tax difference
14. `calculate_interest_income_fields(self, session=None)` - Calculate interest income fields
15. `sum_tax_payments_for_fy(self, session=None)` - Sum tax payments for FY

### src/utils.py (36 lines) - COMPLETE INVENTORY
**Functions to migrate (1 total):**
1. `with_session(method)` - Session decorator

## Target Structure
```
src/
├── __init__.py - Package exports (updated)
├── database.py - Database setup (stays)
├── shared/
│   ├── __init__.py
│   ├── base.py - SQLAlchemy Base
│   ├── calculations.py - Shared calculation utilities
│   └── utils.py - Shared utilities (moved from src/utils.py)
├── fund/
│   ├── __init__.py
│   ├── models.py - Fund, FundEvent, enums (✅ COMPLETED)
│   ├── calculations.py - Fund-specific calculations
│   ├── creation.py - Fund creation and event management (✅ EXISTS)
│   └── queries.py - Fund-specific queries (✅ EXISTS)
├── entity/
│   ├── __init__.py
│   ├── models.py - Entity model (✅ EXISTS)
│   ├── calculations.py - Entity-specific calculations
│   └── creation.py - Entity creation and management
├── tax/
│   ├── __init__.py
│   ├── models.py - TaxStatement model (✅ EXISTS)
│   ├── calculations.py - Tax-specific calculations
│   └── creation.py - Tax statement creation and management
├── rates/
│   ├── __init__.py
│   ├── models.py - RiskFreeRate model (✅ EXISTS)
│   ├── calculations.py - Rate-specific calculations
│   └── creation.py - Rate data creation and management
├── investment_company/
│   ├── __init__.py
│   ├── models.py - InvestmentCompany model
│   ├── calculations.py - Investment company calculations
│   └── creation.py - Investment company creation and management
└── dashboard/
    ├── __init__.py
    └── [dashboard-specific files]
```

## Detailed Migration Tasks

### 1. Shared Module Migration

#### 1.1 Shared Utilities
- [ ] **Task 1.1.1**: Move `with_session` decorator from `src/utils.py` to `src/shared/utils.py` (EXACT COPY)
- [ ] **Task 1.1.2**: Update all imports to use `from ..shared.utils import with_session`
- [ ] **Task 1.1.3**: Comment out all lines in `src/utils.py` after migration (keep for reference)

#### 1.2 Shared Calculations
- [ ] **Task 1.2.1**: Create `src/shared/calculations.py`
- [ ] **Task 1.2.2**: Move shared calculation functions from `src/calculations.py` (EXACT COPIES):
  - [ ] `get_equity_change_for_event(event, fund_type)` - Used by multiple modules
  - [ ] `get_reconciliation_explanation(gross_diff, tax_diff, net_diff)` - Used by tax module
- [ ] **Task 1.2.3**: Update imports in all modules

### 2. Fund Module Migration

#### 2.1 Fund Models (✅ COMPLETED)
- [x] **Task 2.1.1**: Migrate Fund class from `src/models.py` to `src/fund/models.py`
- [x] **Task 2.1.2**: Migrate FundEvent class from `src/models.py` to `src/fund/models.py`
- [x] **Task 2.1.3**: Migrate enums (EventType, FundType, DistributionType, TaxPaymentType) to `src/fund/models.py`
- [x] **Task 2.1.4**: Update all imports and relationships
- [x] **Task 2.1.5**: Verify all imports work correctly

#### 2.2 Fund Calculations
- [ ] **Task 2.2.1**: Create `src/fund/calculations.py`
- [ ] **Task 2.2.2**: Move fund-specific calculation functions from `src/calculations.py` (EXACT COPIES):
  - [ ] `calculate_irr(cash_flows, days_from_start, tolerance=1e-10, max_iterations=200)`
  - [ ] `calculate_average_equity_balance_nav(unit_events, start_date, end_date)`
  - [ ] `calculate_average_equity_balance_cost(capital_events)`
  - [ ] `calculate_debt_cost(events, risk_free_rates, start_date, end_date, currency)`
  - [ ] `calculate_nav_based_capital_gains(events)`
  - [ ] `calculate_cost_based_capital_gains(events)`
  - [ ] `orchestrate_nav_based_average_equity(unit_events)`
  - [ ] `orchestrate_cost_based_average_equity(capital_events)`
  - [ ] `orchestrate_irr_base(cash_flow_events, start_date, include_tax_payments=False, include_risk_free_charges=False, include_fy_debt_cost=False, return_cashflows=False)`
  - [ ] `calculate_nav_event_amounts(unit_events)`
  - [ ] `calculate_cumulative_units_and_cost_basis(unit_events, as_of_date=None)`
  - [ ] `calculate_nav_based_cost_basis_for_irr(unit_events, as_of_date=None)`
- [ ] **Task 2.2.3**: Update imports in `src/fund/models.py`

#### 2.3 Fund Creation (✅ EXISTS)
- [x] **Task 2.3.1**: Fund creation.py already exists in `src/fund/creation.py`
- [ ] **Task 2.3.2**: Update imports in `src/fund/creation.py` to use new module structure
- [ ] **Task 2.3.3**: Ensure creation methods work with migrated models and calculations

### 3. Tax Module Migration

#### 3.1 Tax Models (✅ EXISTS)
- [x] **Task 3.1.1**: TaxStatement model already exists in `src/tax/models.py`

#### 3.2 Tax Calculations
- [ ] **Task 3.2.1**: Create `src/tax/calculations.py`
- [ ] **Task 3.2.2**: Move tax-specific calculation functions from `src/calculations.py` (EXACT COPIES):
  - [ ] `net_income(total_income, non_resident_withholding_tax_from_statement)`
  - [ ] `tax_payable(total_interest_income, interest_taxable_rate, non_resident_withholding_tax_from_statement)`
  - [ ] `interest_tax_benefit(total_interest_expense, interest_deduction_rate)`
- [ ] **Task 3.2.3**: Update imports in `src/tax/models.py`

#### 3.3 Tax Creation
- [ ] **Task 3.3.1**: Create `src/tax/creation.py`
- [ ] **Task 3.3.2**: Move tax statement creation methods from `src/models.py` (EXACT COPIES):
  - [ ] `_create_or_update_tax_statement_object(self, entity_id, financial_year, **kwargs)`
  - [ ] `create_or_update_tax_statement(self, entity_id, financial_year, session=None, **kwargs)`
  - [ ] `_create_tax_payment_event_object(self, tax_statement)`
  - [ ] `create_tax_payment_events(self, session=None)`
- [ ] **Task 3.3.3**: Update imports in `src/tax/models.py`

### 4. Entity Module Migration

#### 4.1 Entity Models (✅ EXISTS)
- [x] **Task 4.1.1**: Entity model already exists in `src/entity/models.py`

#### 4.2 Entity Calculations
- [ ] **Task 4.2.1**: Create `src/entity/calculations.py`
- [ ] **Task 4.2.2**: Move entity-specific calculation functions from `src/calculations.py` (EXACT COPIES):
  - [ ] `get_financial_years_for_fund_period(start_date, end_date, entity)`
  - [ ] `get_financial_year_dates(financial_year, tax_jurisdiction="AU")`
- [ ] **Task 4.2.3**: Update imports in `src/entity/models.py`

#### 4.3 Entity Creation
- [ ] **Task 4.3.1**: Create `src/entity/creation.py`
- [ ] **Task 4.3.2**: Create entity management methods
- [ ] **Task 4.3.3**: Update imports in `src/entity/models.py`

### 5. Rates Module Migration

#### 5.1 Rates Models (✅ EXISTS)
- [x] **Task 5.1.1**: RiskFreeRate model already exists in `src/rates/models.py`

#### 5.2 Rates Calculations
- [ ] **Task 5.2.1**: Create `src/rates/calculations.py`
- [ ] **Task 5.2.2**: Move rate-specific calculation functions from `src/calculations.py` (EXACT COPIES):
  - [ ] `get_risk_free_rate_for_date(target_date, risk_free_rates)`
- [ ] **Task 5.2.3**: Update imports in `src/rates/models.py`

#### 5.3 Rates Creation
- [ ] **Task 5.3.1**: Create `src/rates/creation.py`
- [ ] **Task 5.3.2**: Create rate data management methods
- [ ] **Task 5.3.3**: Update imports in `src/rates/models.py`

### 6. Investment Company Module Migration

#### 6.1 Investment Company Models
- [ ] **Task 6.1.1**: Create `src/investment_company/models.py`
- [ ] **Task 6.1.2**: Move InvestmentCompany class from `src/models.py` to `src/investment_company/models.py` (EXACT COPY)
- [ ] **Task 6.1.3**: Update all imports and relationships

#### 6.2 Investment Company Calculations
- [ ] **Task 6.2.1**: Create `src/investment_company/calculations.py`
- [ ] **Task 6.2.2**: Move investment company-specific calculation functions (if any)
- [ ] **Task 6.2.3**: Update imports in `src/investment_company/models.py`

#### 6.3 Investment Company Creation
- [ ] **Task 6.3.1**: Create `src/investment_company/creation.py`
- [ ] **Task 6.3.2**: Create investment company management methods
- [ ] **Task 6.3.3**: Update imports in `src/investment_company/models.py`

### 7. Package Exports Migration

#### 7.1 Update Package __init__.py
- [ ] **Task 7.1.1**: Update `src/__init__.py` to import from new module locations
- [ ] **Task 7.1.2**: Update `__all__` list to reflect new structure
- [ ] **Task 7.1.3**: Ensure backward compatibility for existing imports

### 8. Database Module

#### 8.1 Database Setup
- [ ] **Task 8.1.1**: Review `src/database.py` for any needed updates
- [ ] **Task 8.1.2**: Update imports if necessary
- [ ] **Task 8.1.3**: Ensure database setup works with new module structure

### 9. Cleanup Tasks

#### 9.1 Comment Out Old Files (Instead of Deleting)
- [ ] **Task 9.1.1**: Comment out all lines in `src/models.py` after all migrations complete (keep for reference)
- [ ] **Task 9.1.2**: Comment out all lines in `src/calculations.py` after all migrations complete (keep for reference)
- [ ] **Task 9.1.3**: Comment out all lines in `src/utils.py` after migration to shared (keep for reference)
- [ ] **Task 9.1.4**: Add header comments to each file explaining they are deprecated but kept for reference

#### 9.2 Update Documentation
- [ ] **Task 9.2.1**: Update README.md to reflect new structure
- [ ] **Task 9.2.2**: Update any other documentation files
- [ ] **Task 9.2.3**: Create module-specific documentation

## Verification Tasks

### 10. Comprehensive Testing
- [ ] **Task 10.1**: Run all existing tests with new structure
- [ ] **Task 10.2**: Verify all imports work correctly
- [ ] **Task 10.3**: Verify all relationships work correctly
- [ ] **Task 10.4**: Verify all calculations produce identical results
- [ ] **Task 10.5**: Test database operations with new structure
- [ ] **Task 10.6**: Verify backward compatibility for existing code

## Progress Tracking

### Completed Tasks
- ✅ Fund models migration (67/67 tasks completed)
- ✅ Import verification for fund models

### Current Status
- **Total Tasks**: ~80+ tasks identified
- **Completed**: ~15 tasks (19%)
- **Remaining**: ~65 tasks (81%)

## Notes
- **CRITICAL**: Every method/function must be copied with EXACT same logic, docstrings, and behavior
- **NO LOGIC CHANGES**: Maintain exact same output and calculations
- **COMPLETE INVENTORY**: Every single method/function must be accounted for
- **VERIFICATION**: Test each migration to ensure identical results
- **SAFETY FIRST**: Old files are commented out instead of deleted for easy rollback and reference
- Each domain module should be self-contained with its own models and calculations
- Shared utilities and calculations go in the shared module
- Maintain backward compatibility during migration
- Test thoroughly after each module migration
- Update imports incrementally to avoid breaking changes
- Keep commented old files for reference and potential rollback 