# Calculation/Model Split Audit – Investment Tracker (2024)

## Purpose
Review each domain (fund, tax, entity, investment_company, rates, shared) for:
- Proper separation of business logic (calculations.py) and persistence/orchestration (models.py)
- Opportunities for improved clarity or maintainability

---

## Fund Domain

**models.py:**
- Handles ORM definitions, relationships, and orchestration.
- Imports all calculation functions from calculations.py and shared/calculations.py.
- Most calculation logic (IRR, average equity, debt cost, capital gains, etc.) is delegated to functions in calculations.py.
- Some methods in models.py (e.g., update_current_equity_balance, calculate_average_equity_balance) are thin wrappers that call calculation functions and update model fields.
- Business logic for creating and updating related objects (e.g., tax statements, events) is present, but actual calculations are delegated.

**calculations.py:**
- Contains all the core calculation logic for IRR, average equity, debt cost, capital gains, NAV event amounts, etc.
- Functions are pure and stateless, operating on data passed in as arguments.
- No database or session logic.

**Assessment:**
- The split is clean: models.py handles persistence and orchestration, while calculations.py contains pure business logic.
- Thin wrappers in models.py are appropriate, as they update model fields and call calculation functions.
- No major calculation logic is embedded in models.py.

**Recommendation:**
- No refactoring needed for the fund domain. The separation of concerns is clear and maintainable.

---

## Tax Domain

**models.py:**
- Handles ORM definitions, relationships, and orchestration for TaxStatement.
- Imports calculation functions from calculations.py.
- Calculation methods (e.g., calculate_interest_tax_amount, calculate_fy_debt_interest_deduction_total_deduction) are thin wrappers that call calculation functions and update model fields.
- Some aggregation and update logic (e.g., calculate_dividend_totals) is present, but actual calculations are delegated to calculations.py or are simple field updates.

**calculations.py:**
- Contains pure functions for tax calculations (e.g., tax_payable, calculate_fy_debt_interest_deduction_total_deduction).
- Functions are stateless and operate on arguments only.
- No database or session logic.

**Assessment:**
- The split is clean: models.py handles persistence and orchestration, while calculations.py contains pure business logic.
- Thin wrappers in models.py are appropriate for updating fields and calling calculation functions.
- No major calculation logic is embedded in models.py.

**Recommendation:**
- No refactoring needed for the tax domain. The separation of concerns is clear and maintainable.

---

## Entity Domain

**models.py:**
- Handles ORM definitions, relationships, and orchestration for Entity.
- Business logic is limited to validation and object creation.
- Calculation logic (e.g., get_financial_years_for_period) delegates to calculations.py.

**calculations.py:**
- Contains pure functions for entity-specific calculations (e.g., get_financial_years_for_fund_period).
- Stateless and operates on arguments only.

**Assessment:**
- The split is clean: models.py handles persistence and orchestration, calculations.py contains pure business logic.
- No major calculation logic is embedded in models.py.

**Recommendation:**
- No refactoring needed for the entity domain. The separation of concerns is clear and maintainable.

---

## Investment Company Domain

**models.py:**
- Handles ORM definitions, relationships, and orchestration for InvestmentCompany.
- Business logic is limited to validation and object creation.
- Calculation logic (e.g., get_total_funds_under_management, get_total_commitments) delegates to calculations.py.

**calculations.py:**
- Contains pure functions for investment company-specific calculations.
- Stateless and operates on arguments only.

**Assessment:**
- The split is clean: models.py handles persistence and orchestration, calculations.py contains pure business logic.
- No major calculation logic is embedded in models.py.

**Recommendation:**
- No refactoring needed for the investment company domain. The separation of concerns is clear and maintainable.

---

## Rates Domain

**models.py:**
- Handles ORM definitions and relationships for RiskFreeRate.
- Calculation logic (e.g., get_rate_for_date) delegates to calculations.py.

**calculations.py:**
- Contains pure functions for rates-specific calculations (e.g., get_risk_free_rate_for_date).
- Stateless and operates on arguments only.

**Assessment:**
- The split is clean: models.py handles persistence and orchestration, calculations.py contains pure business logic.
- No major calculation logic is embedded in models.py.

**Recommendation:**
- No refactoring needed for the rates domain. The separation of concerns is clear and maintainable.

---

## Shared Domain

**calculations.py:**
- Contains pure, stateless calculation functions used across domains (e.g., IRR, equity change, financial year calculations).
- No persistence or business orchestration logic.

**Assessment:**
- Fulfills its role as a shared utility layer.
- No domain-specific business logic present.

**Recommendation:**
- No refactoring needed for the shared domain. The separation of concerns is clear and maintainable.

--- 