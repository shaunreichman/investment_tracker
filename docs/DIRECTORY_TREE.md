# Directory tree for investment_tracker

```
investment_tracker
├── alembic
│   ├── versions
│   │   ├── 0a4750fa04b2_add_nav_change_fields_to_fundevent_model.py
│   │   ├── 0e0cbd0e843f_add_irr_storage_columns_to_funds_table.py
│   │   ├── 1267d9948898_add_fund_status_field.py
│   │   ├── 4e212ad5fd5d_rename_fy_debt_interest_deduction_.py
│   │   ├── 762e1a853f03_add_end_date_to_funds.py
│   │   ├── a67a839417fb_add_tax_statement_id_to_fund_events.py
│   │   ├── abb88ad11ad3_add_dividend_franked_and_dividend_.py
│   │   ├── dec654353eed_remove_final_tax_statement_received_.py
│   │   └── f223dde71466_base_schema_no_total_cost_basis.py
│   ├── versions_backup
│   │   ├── 1a9fb49d4218_merge_heads_after_dropping_cost_of_.py
│   │   ├── 23f450329111_add_dividend_fields_to_tax_statement.py
│   │   ├── 27f064a83d4d_remove_tax_already_paid_field.py
│   │   ├── 39973e45f047_add_dividend_tax_amount_fields.py
│   │   ├── 4a2d8b3da2a7_remove_unused_income_fields_from_tax_.py
│   │   ├── 72b17b2c3309_rename_interest_income_fields_to_.py
│   │   ├── 7761261ccf39_rename_dividend_income_fields_to_be_.py
│   │   ├── 932568d88bfa_add_current_nav_total_to_fund.py
│   │   ├── aa30bbb41a7e_rename_interest_income_tax_amount_to_.py
│   │   ├── add_capital_gain_fields_to_tax_statement.py
│   │   ├── add_current_equity_balance_to_fundevent.py
│   │   ├── bf379fa293fb_add_dividend_amount_from_tax_statement_.py
│   │   ├── drop_cost_of_units_from_fund_events.py
│   │   └── e6b544621144_rename_debt_cost_tracking_fields_to_be_.py
│   ├── env.py
│   ├── README
│   └── script.py.mako
├── data
│   ├── investment_tracker.db
│   ├── investment_tracker.db.backup
│   └── investment_tracker.db.broken.1752418889
├── docs
│   ├── guidlines
│   │   ├── COMPONENT_ARCHITECTURE.md
│   │   ├── PROJECT_CONTEXT.md
│   │   ├── TEAM_ONBOARDING.md
│   │   └── TESTING_STANDARDS.md
│   ├── refactor_plans
│   │   ├── audit 12-jul-25
│   │   │   ├── api_consistency_audit.md
│   │   │   ├── calculation_model_split_audit.md
│   │   │   ├── domain_module_audit.md
│   │   │   ├── performance_review.md
│   │   │   ├── test_suite_audit.md
│   │   │   └── validation_error_handling_audit.md
│   │   ├── COMPREHENSIVE_MIGRATION_TASKS.md
│   │   └── REFACTOR_TAX_PAYMENT_EVENTS.md
│   ├── specs_completed
│   │   ├── CENTRALIZED_API_IMPLEMENTATION_GUIDE.md
│   │   ├── CREATE_ONLY_CLEANUP_SPEC.md
│   │   ├── CREATE_ONLY_EVENT_FORM_SPEC.md
│   │   ├── DISTRIBUTION_METHOD_CONSOLIDATION_SPEC.md
│   │   ├── DOCUMENTATION_AUDIT_SUMMARY.md
│   │   ├── ERROR_HANDLING_STANDARDIZATION_GUIDE.md
│   │   ├── EVENT_RELATIONSHIP_GROUPING_SPEC.md
│   │   ├── FUND_DETAIL_INTEGRATION_SPEC.md
│   │   ├── FUND_STATUS_ENHANCEMENT_SPEC.md
│   │   ├── IRR_CALCULATION_AND_STORAGE_SPEC.md
│   │   ├── NAV_INFORMATION_DISPLAY_SPEC.md
│   │   └── UNIFIED_EVENT_FORM_SPEC.md
│   ├── DESIGN_GUIDELINES.md
│   ├── FRONTEND_REFACTORING_SPEC.md
│   ├── FUND_CREATION_FEATURE.md
│   ├── FUND_DETAIL_MODERNIZATION_SPEC.md
│   ├── FUND_DETAIL_REDESIGN_SPEC.md
│   ├── FUND_EVENTS_FEATURE_PLAN.md
│   └── TAX_STATEMENT_IMPLEMENTATION_GUIDE.md
├── frontend
│   ├── coverage
│   │   ├── lcov-report
│   │   │   ├── src
│   │   │   │   ├── components
│   │   │   │   │   ├── fund-detail
│   │   │   │   │   │   ├── FundDetailTable
│   │   │   │   │   │   │   ├── ActionButtons.tsx.html
│   │   │   │   │   │   │   ├── debug.ts.html
│   │   │   │   │   │   │   ├── EventRow.tsx.html
│   │   │   │   │   │   │   ├── GroupedEventRow.tsx.html
│   │   │   │   │   │   │   ├── index.html
│   │   │   │   │   │   │   ├── index.ts.html
│   │   │   │   │   │   │   ├── TableBody.tsx.html
│   │   │   │   │   │   │   ├── TableContainer.tsx.html
│   │   │   │   │   │   │   ├── TableFilters.tsx.html
│   │   │   │   │   │   │   ├── TableHeader.tsx.html
│   │   │   │   │   │   │   └── useEventGrouping.ts.html
│   │   │   │   │   │   ├── CompletedPerformanceSection.tsx.html
│   │   │   │   │   │   ├── EquitySection.tsx.html
│   │   │   │   │   │   ├── ExpectedPerformanceSection.tsx.html
│   │   │   │   │   │   ├── FundDetailsSection.tsx.html
│   │   │   │   │   │   ├── index.html
│   │   │   │   │   │   ├── index.ts.html
│   │   │   │   │   │   ├── TransactionSummarySection.tsx.html
│   │   │   │   │   │   └── UnitPriceChartSection.tsx.html
│   │   │   │   │   ├── CompaniesPage.tsx.html
│   │   │   │   │   ├── CreateEntityModal.tsx.html
│   │   │   │   │   ├── CreateFundEventModal.tsx.html
│   │   │   │   │   ├── CreateFundModal.tsx.html
│   │   │   │   │   ├── CreateInvestmentCompanyModal.tsx.html
│   │   │   │   │   ├── EditFundEventModal.tsx.html
│   │   │   │   │   ├── ErrorDisplay.tsx.html
│   │   │   │   │   ├── ErrorToast.tsx.html
│   │   │   │   │   ├── FundDetail.tsx.html
│   │   │   │   │   ├── index.html
│   │   │   │   │   └── OverallDashboard.tsx.html
│   │   │   │   ├── config
│   │   │   │   │   ├── environment.ts.html
│   │   │   │   │   └── index.html
│   │   │   │   ├── hooks
│   │   │   │   │   ├── index.html
│   │   │   │   │   ├── useApiCall.ts.html
│   │   │   │   │   ├── useDashboard.ts.html
│   │   │   │   │   ├── useEntities.ts.html
│   │   │   │   │   ├── useErrorHandler.ts.html
│   │   │   │   │   ├── useFunds.ts.html
│   │   │   │   │   └── useInvestmentCompanies.ts.html
│   │   │   │   ├── services
│   │   │   │   │   ├── api.ts.html
│   │   │   │   │   └── index.html
│   │   │   │   ├── types
│   │   │   │   │   ├── api.ts.html
│   │   │   │   │   ├── errors.ts.html
│   │   │   │   │   └── index.html
│   │   │   │   ├── utils
│   │   │   │   │   ├── constants.ts.html
│   │   │   │   │   ├── formatters.ts.html
│   │   │   │   │   ├── helpers.ts.html
│   │   │   │   │   ├── index.html
│   │   │   │   │   └── validators.ts.html
│   │   │   │   ├── App.tsx.html
│   │   │   │   ├── index.html
│   │   │   │   ├── index.tsx.html
│   │   │   │   └── reportWebVitals.ts.html
│   │   │   ├── base.css
│   │   │   ├── block-navigation.js
│   │   │   ├── favicon.png
│   │   │   ├── index.html
│   │   │   ├── prettify.css
│   │   │   ├── prettify.js
│   │   │   ├── sort-arrow-sprite.png
│   │   │   └── sorter.js
│   │   ├── clover.xml
│   │   ├── coverage-final.json
│   │   └── lcov.info
│   ├── public
│   │   ├── favicon.ico
│   │   ├── index.html
│   │   ├── logo192.png
│   │   ├── logo512.png
│   │   ├── manifest.json
│   │   └── robots.txt
│   ├── src
│   │   ├── components
│   │   │   ├── fund
│   │   │   │   ├── detail
│   │   │   │   │   ├── summary
│   │   │   │   │   │   ├── CompletedPerformanceSection.tsx
│   │   │   │   │   │   ├── EquitySection.tsx
│   │   │   │   │   │   ├── ExpectedPerformanceSection.tsx
│   │   │   │   │   │   ├── FundDetailsSection.tsx
│   │   │   │   │   │   ├── TransactionSummarySection.tsx
│   │   │   │   │   │   └── UnitPriceChartSection.tsx
│   │   │   │   │   ├── table
│   │   │   │   │   │   ├── ActionButtons.test.tsx
│   │   │   │   │   │   ├── ActionButtons.tsx
│   │   │   │   │   │   ├── debug.ts
│   │   │   │   │   │   ├── EventRow.tsx
│   │   │   │   │   │   ├── GroupedEventRow.tsx
│   │   │   │   │   │   ├── index.ts
│   │   │   │   │   │   ├── TableBody.test.tsx
│   │   │   │   │   │   ├── TableBody.tsx
│   │   │   │   │   │   ├── TableContainer.test.tsx
│   │   │   │   │   │   ├── TableContainer.tsx
│   │   │   │   │   │   ├── TableFilters.integration.test.tsx
│   │   │   │   │   │   ├── TableFilters.test.tsx
│   │   │   │   │   │   ├── TableFilters.tsx
│   │   │   │   │   │   ├── TableHeader.test.tsx
│   │   │   │   │   │   ├── TableHeader.tsx
│   │   │   │   │   │   └── useEventGrouping.ts
│   │   │   │   │   ├── FundDetail.test.tsx
│   │   │   │   │   ├── FundDetail.tsx
│   │   │   │   │   └── index.ts
│   │   │   │   └── events
│   │   │   │       ├── create
│   │   │   │       │   ├── DistributionForm.test.tsx
│   │   │   │       │   ├── DistributionForm.tsx
│   │   │   │       │   ├── EventTypeSelector.test.tsx
│   │   │   │       │   ├── EventTypeSelector.tsx
│   │   │   │       │   ├── NavUpdateForm.test.tsx
│   │   │   │       │   ├── NavUpdateForm.tsx
│   │   │   │       │   ├── TaxStatementForm.test.tsx
│   │   │   │       │   ├── TaxStatementForm.tsx
│   │   │   │       │   ├── UnitTransactionForm.test.tsx
│   │   │   │       │   └── UnitTransactionForm.tsx
│   │   │   │       ├── CreateFundEventModal.test.tsx
│   │   │   │       └── CreateFundEventModal.tsx
│   │   │   ├── CompaniesPage.tsx
│   │   │   ├── CreateEntityModal.tsx
│   │   │   ├── CreateFundModal.tsx
│   │   │   ├── CreateInvestmentCompanyModal.tsx
│   │   │   ├── ErrorDisplay.tsx
│   │   │   ├── ErrorToast.tsx
│   │   │   └── OverallDashboard.tsx
│   │   ├── config
│   │   │   └── environment.ts
│   │   ├── hooks
│   │   │   ├── useApiCall.ts
│   │   │   ├── useCreateEventForm.ts
│   │   │   ├── useCreateEventValidation.test.ts
│   │   │   ├── useCreateEventValidation.ts
│   │   │   ├── useDashboard.ts
│   │   │   ├── useEntities.ts
│   │   │   ├── useErrorHandler.ts
│   │   │   ├── useEventForm.test.ts
│   │   │   ├── useEventForm.ts
│   │   │   ├── useEventSubmission.ts
│   │   │   ├── useFunds.ts
│   │   │   └── useInvestmentCompanies.ts
│   │   ├── services
│   │   │   └── api.ts
│   │   ├── types
│   │   │   ├── api.ts
│   │   │   └── errors.ts
│   │   ├── utils
│   │   │   ├── __tests__
│   │   │   │   ├── formatters.test.ts
│   │   │   │   ├── helpers.test.ts
│   │   │   │   └── validators.test.ts
│   │   │   ├── constants.ts
│   │   │   ├── formatters.ts
│   │   │   ├── helpers.ts
│   │   │   └── validators.ts
│   │   ├── App.css
│   │   ├── App.test.tsx
│   │   ├── App.tsx
│   │   ├── index.css
│   │   ├── index.tsx
│   │   ├── logo.svg
│   │   ├── react-app-env.d.ts
│   │   ├── reportWebVitals.ts
│   │   └── setupTests.ts
│   ├── .env
│   ├── .gitignore
│   ├── package-lock.json
│   ├── package.json
│   ├── README.md
│   └── tsconfig.json
├── scripts
│   ├── add_missing_columns.sql
│   ├── compare_test_outputs.py
│   ├── import_risk_free_rates.py
│   ├── init_database.py
│   └── update_distribution_type_enum.sql
├── src
│   ├── api
│   │   └── __init__.py
│   ├── entity
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   └── models.py
│   ├── fund
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   ├── models.py
│   │   └── queries.py
│   ├── investment_company
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   └── models.py
│   ├── investment_tracker.egg-info
│   │   ├── dependency_links.txt
│   │   ├── PKG-INFO
│   │   ├── SOURCES.txt
│   │   └── top_level.txt
│   ├── rates
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   └── models.py
│   ├── shared
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── calculations.py
│   │   └── utils.py
│   ├── tax
│   │   ├── __init__.py
│   │   ├── calculations.py
│   │   ├── events.py
│   │   └── models.py
│   ├── __init__.py
│   ├── api.py
│   └── database.py
├── tests
│   ├── output
│   │   ├── test_main_output_baseline.txt
│   │   └── test_main_output_new.txt
│   ├── run_test_with_baseline.py
│   ├── test_main.py
│   └── test_utils.py
├── .gitignore
├── alembic.ini
├── package-lock.json
├── package.json
├── pyproject.toml
├── README.md
├── requirements.txt
└── rfr.csv
```
