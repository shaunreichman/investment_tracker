# End State File Directory Structure

This document outlines the complete target directory structure for the enterprise testing package.
## This document ONLY contains the file directory structure

This document only marks off the folders as complete once ALL sub files are complete

```
tests/
├── conftest.py                          # Global test configuration and fixtures
├── factories.py                         # Test data factories for all models
├── test_utils.py                        # Common testing utilities and helpers
├── run_test_with_baseline.py            # Baseline comparison test runner
│
├── unit/                                # Unit tests - fastest execution
│   ├── __init__.py
│   ├── models/                          # Domain model validation and business rules
│   │   ├── __init__.py
│   │   ├── ✅ fund/                        # Fund domain models
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_fund_models.py      # Fund model validation and business rules
│   │   │   ├── ✅ test_fund_event_grouping.py # FundEvent grouping with enhanced business rules
│   │   │   ├── ✅ test_domain_event_model.py # DomainEvent model tests
│   │   │   └── ✅ test_fund_event_cash_flow_model.py # Cash flow model tests
│   │   ├── ✅ investment_company/          # Investment company models
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_investment_company_model.py        # InvestmentCompany validation
│   │   │   └── ✅ test_contact_model.py                   # Contact model validation
│   │   ├── entity/                      # Entity models
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_model.py     # Entity model validation
│   │   │   └── test_entity_relationship_model.py # Entity relationships
│   │   ├── ✅ banking/                     # Banking models
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_bank_model.py      # Bank model validation and business rules
│   │   │   └── ✅ test_bank_account_model.py # Bank account validation and business rules
│   │   ├── tax/                         # Tax models
│   │   │   ├── __init__.py
│   │   │   ├── test_tax_statement_model.py # Tax statement validation
│   │   │   ├── test_tax_event_model.py  # Tax event validation
│   │   │   └── test_tax_calculation_model.py # Tax calculation models
│   │   └── rates/                       # Rate models
│   │       ├── __init__.py
│   │       ├── test_risk_free_rate_model.py # Risk-free rate validation
│   │       └── test_rate_calculation_model.py # Rate calculation models
│   ├── services/                        # Business logic and service layer
│   │   ├── __init__.py
│   │   ├── ✅ fund/                        # Fund services
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_fund_calculation_services.py     # Financial + equity balance calculation logic
│   │   │   ├── ✅ test_fund_status_service.py           # Status transition logic
│   │   │   ├── ✅ test_fund_event_service.py            # Event processing logic
│   │   │   ├── ✅ test_tax_calculation_service.py       # Tax calculation logic
│   │   │   └── ✅ test_fund_incremental_calculation_service.py # Incremental calculations
│   │   ├── ✅ investment_company/          # Investment company services
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_company_portfolio_service.py        # Portfolio operations & fund coordination
│   │   │   ├── ✅ test_company_summary_service.py          # Summary calculations & metrics
│   │   │   ├── ✅ test_contact_management_service.py       # Contact operations & validation
│   │   │   ├── ✅ test_company_validation_service.py       # Business rule validation
│   │   │   ├── ✅ test_company_calculation_service.py      # Portfolio calculations & metrics
│   │   │   ├── ✅ test_fund_coordination_service.py        # Fund creation coordination
│   │   │   └── ✅ test_company_service.py                  # Core company operations
│   │   ├── entity/                      # Entity services
│   │   │   ├── __init__.py
│   │   │   └── test_entity_service.py                # Entity management logic
│   │   ├── ✅ banking/                     # Banking services
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_bank_service.py                  # Bank business logic and operations
│   │   │   ├── ✅ test_bank_account_service.py          # Account business logic and operations
│   │   │   ├── ✅ test_banking_validation_service.py    # Validation logic and business rules
│   │   │   ├── ✅ test_banking_health_service.py        # Health monitoring and system status
│   │   │   └── ✅ test_banking_cache_service.py         # Caching logic and performance
│   │   └── tax/                         # Tax services
│   │       ├── __init__.py
│   │       └── test_tax_service.py                      # Tax processing logic
│   ├── calculations/                    # Financial and business calculations
│   │   ├── __init__.py
│   │   ├── ✅  fund/                        # Fund-specific calculations
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_irr_calculations.py              # IRR calculation algorithms
│   │   │   ├── ✅ test_debt_cost_calculations.py        # Debt cost calculations
│   │   │   ├── ✅ test_fifo_calculations.py             # FIFO unit calculations
│   │   │   └── ✅ test_nav_calculations.py              # NAV-based calculations
│   │   ├── entity/                      # Entity calculations
│   │   │   ├── __init__.py
│   │   │   └── test_entity_calculations.py           # Entity financial metrics
│   │   ├── tax/                         # Tax calculations
│   │   │   ├── __init__.py
│   │   │   └── test_tax_calculations.py              # Tax computation logic
│   │   ├── rates/                       # Rate calculations
│   │   │   ├── __init__.py
│   │   │   └── test_rate_calculations.py             # Rate computation logic
│   │   └── shared/                      # Shared calculation utilities
│   │       ├── __init__.py
│   │       └── test_shared_calculations.py           # Common calculation utilities
│   ├── events/                          # Event system and handlers
│   │   ├── __init__.py
│   │   ├── ✅ fund/                        # Fund event handling
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_orchestrator.py                  # Event orchestration logic
│   │   │   ├── ✅ test_event_handlers.py                # Individual event handlers
│   │   │   ├── ✅ test_event_registry.py                # Event routing and registration
│   │   │   ├── ✅ test_base_handler.py                  # Base handler functionality
│   │   │   └── ✅ test_async_processor.py               # Async event processing
│   │   ├── ✅ investment_company/          # Investment company event handling
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_base_handler.py                  # Base handler functionality
│   │   │   ├── ✅ test_registry.py                      # Event registry & routing
│   │   │   ├── ✅ test_orchestrator.py                  # Update pipeline coordination
│   │   │   ├── ✅ test_event_handlers.py                # Individual event handlers
│   │   │   └── ✅ test_domain_events.py                 # Domain event functionality
│   │   ├── ✅ banking/                     # Banking event handling
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_banking_event_handlers.py        # 8 specific event handlers
│   │   │   ├── ✅ test_banking_event_registry.py        # Event routing and registration
│   │   │   ├── ✅ test_banking_orchestrator.py          # Pipeline coordination
│   │   │   ├── ✅ test_banking_cross_module_registry.py # Cross-module integration
│   │   │   └── ✅ test_banking_domain_events.py         # 8 domain events
│   │   ├── tax/                         # Tax event handling
│   │   │   ├── __init__.py
│   │   │   └── test_tax_event_handlers.py            # Tax event processing
│   │   └── shared/                      # Shared event utilities
│   │       ├── __init__.py
│   │       └── test_event_utilities.py               # Common event utilities
│   ├── repositories/                    # Data access layer
│   │   ├── __init__.py
│   │   ├── ✅ fund/                        # Fund data access
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_fund_repository.py               # Data access logic
│   │   │   ├── ✅ test_fund_event_repository.py         # Event query logic
│   │   │   ├── ✅ test_domain_event_repository.py       # Domain event persistence
│   │   │   └── ✅ test_tax_statement_repository.py      # Tax statement persistence
│   │   ├── ✅ investment_company/          # Company data access
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_company_repository.py            # Company data access
│   │   │   └── ✅ test_contact_repository.py            # Contact data access
│   │   ├── entity/                      # Entity data access
│   │   │   ├── __init__.py
│   │   │   └── test_entity_repository.py             # Entity data access
│   │   ├── ✅ banking/                     # Banking data access
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_bank_repository.py               # Bank data access and caching
│   │   │   ├── ✅ test_bank_account_repository.py       # Account data access and caching
│   │   │   └── ✅ test_banking_summary_repository.py    # Summary data access and aggregation
│   │   └── tax/                         # Tax data access
│   │       ├── __init__.py
│   │       └── test_tax_repository.py                # Tax data access
│   ├── enums/                           # Enum validation and business rules
│   │   ├── __init__.py
│   │   ├── ✅ fund/                        # Fund enums
│   │   │   ├── ✅ __init__.py
│   │   │   └── ✅ test_fund_enums.py                    # Fund enum validation
│   │   ├── ✅ investment_company/          # Company enums
│   │   │   ├── ✅ __init__.py
│   │   │   └── ✅ test_company_enums.py                   # Company enum validation
│   │   ├── entity/                      # Entity enums
│   │   │   ├── __init__.py
│   │   │   └── test_entity_enums.py                  # Entity enum validation
│   │   ├── ✅ banking/                     # Banking enums
│   │   │   ├── ✅ __init__.py
│   │   │   └── ✅ test_banking_enums.py                 # Banking enum validation
│   │   ├── tax/                         # Tax enums
│   │   │   ├── __init__.py
│   │   │   └── test_tax_enums.py                     # Tax enum validation
│   │   └── rates/                       # Rate enums
│   │       ├── __init__.py
│   │       └── test_rate_enums.py                    # Rate enum validation
│   └── shared/                          # Shared utilities and base classes
│       ├── __init__.py
│       ├── test_base_classes.py                      # Base class functionality
│       ├── test_utilities.py                         # Utility function tests
│       └── test_database.py                          # Database utility tests
│
├── integration/                          # Integration tests - medium execution speed
│   ├── __init__.py
│   ├── workflows/                        # Complete business workflow testing
│   │   ├── __init__.py
│   │   ├── ✅ fund/                         # Fund-specific workflows
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_capital_call_workflow.py         # Complete capital call flow
│   │   │   ├── ✅ test_return_of_capital_workflow.py    # Complete capital return flow
│   │   │   ├── ✅ test_distribution_workflow.py         # Complete distribution flow
│   │   │   ├── ✅ test_nav_update_workflow.py         # NAV update and recalculation
│   │   │   ├── ✅ test_fund_realization_workflow.py     # Fund completion workflow
│   │   │   └── ✅ test_unit_workflows.py                # Unit purchase and sale workflows
│   │   ├── ✅ investment_company/             # Company management workflows
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_company_creation_workflow.py     # Company setup workflow
│   │   │   ├── ✅ test_company_portfolio_workflow.py    # Portfolio management workflow
│   │   │   ├── ✅ test_company_contact_workflow.py      # Contact management workflow
│   │   │   ├── ✅ test_cross_domain_coordination.py     # Fund-company-entity coordination
│   │   │   └── ✅ test_event_driven_workflows.py        # Event-driven operation flows
│   │   ├── entity/                        # Entity management workflows
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_creation_workflow.py      # Entity setup workflow
│   │   │   └── test_entity_investment_workflow.py    # Investment workflow
│   │   ├── ✅ banking/                       # Banking workflows
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_account_setup_workflow.py        # Account creation workflow
│   │   │   ├── ✅ test_transaction_workflow.py          # Transaction processing
│   │   │   ├── ✅ test_banking_event_workflow.py        # Event processing workflow
│   │   │   └── ✅ test_banking_cross_module_workflow.py # Cross-module integration workflow
│   │   └── tax/                           # Tax workflows
│   │       ├── __init__.py
│   │       ├── test_tax_calculation_workflow.py      # Tax computation workflow
│   │       └── test_tax_reporting_workflow.py        # Tax reporting workflow
│   ├── services/                          # Service interaction testing
│   │   ├── __init__.py
│   │   ├── fund/                          # Fund service integration
│   │   │   ├── __init__.py
│   │   │   ├── ❌ test_fund_calculation_integration.py  # Service interaction tests **NOT IMPLEMENTING**
│   │   │   └── ❌ test_fund_event_integration.py        # Event service integration **NOT IMPLEMENTING**
│   │   ├── cross_domain/                   # Cross-domain service integration
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_company_integration.py      # Fund-company integration
│   │   │   ├── test_fund_entity_integration.py       # Fund-entity integration
│   │   │   └── test_fund_banking_integration.py     # Fund-banking integration
│   │   └── event_system/                   # Event system integration
│   │       ├── __init__.py
│   │       ├── test_event_system_integration.py      # Event system end-to-end
│   │       └── test_event_handling.py                # Event handling integration
│   ├── data_consistency/                   # Data consistency validation
│   │   ├── __init__.py
│   │   ├── ✅ fund/                           # Fund data consistency
│   │   │   ├── ✅ __init__.py
│   │   │   ├── ✅ test_fund_equity_balance.py           # Equity balance consistency
│   │   │   ├── ✅ test_event_ordering.py                # Event sequence validation
│   │   │   └── ✅ test_calculation_consistency.py       # Cross-calculation validation
│   │   ├── cross_domain/                    # Cross-domain consistency
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_fund_consistency.py       # Entity-fund consistency
│   │   │   ├── test_company_fund_consistency.py      # Company-fund consistency
│   │   │   └── test_banking_fund_consistency.py      # Banking-fund consistency
│   │   └── system/                         # System-wide consistency
│   │       ├── __init__.py
│   │       ├── test_transaction_boundaries.py        # ACID compliance testing
│   │       └── test_audit_trail_consistency.py      # Audit trail validation
│   └── repositories/                       # Data access integration
│       ├── __init__.py
│       ├── test_fund_repository_integration.py       # Fund data access
│       ├── test_company_repository_integration.py    # Company data access
│       ├── test_entity_repository_integration.py     # Entity data access
│       ├── test_banking_repository_integration.py    # Banking data access
│       └── test_tax_repository_integration.py        # Tax data access
│
├── api/                                  # API tests - HTTP endpoint validation
│   ├── __init__.py
│   ├── contracts/                        # API contract validation
│   │   ├── __init__.py
│   │   ├── banking/                      # Banking API contracts
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_api_schema.py             # API schema validation
│   │   │   ├── test_banking_dto_contracts.py          # DTO contract validation
│   │   │   └── test_banking_error_contracts.py        # Error response contracts
│   │   ├── test_banking_contracts.py                  # Banking API schema validation (legacy)
│   │   ├── test_fund_contracts.py                     # Fund API schema validation
│   │   ├── test_company_contracts.py                  # Company API schema validation
│   │   └── test_tax_contracts.py                      # Tax API schema validation
│   ├── endpoints/                         # API endpoint testing
│   │   ├── __init__.py
│   │   ├── banking/                      # Banking domain endpoints
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_controller.py             # Enhanced controller endpoints
│   │   │   ├── test_banking_dto_validation.py         # DTO validation and contracts
│   │   │   ├── test_banking_middleware.py             # Validation middleware
│   │   │   ├── test_banking_performance.py            # Performance endpoints
│   │   │   ├── test_bank_accounts.py                  # Account management endpoints
│   │   │   └── test_bank_transactions.py              # Transaction management endpoints
│   │   ├── fund/                         # Fund domain endpoints
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_operations.py   # Fund CRUD operations
│   │   │   ├── test_fund_calculations.py # Calculation endpoints
│   │   │   └── test_fund_events.py       # Event management endpoints
│   │   ├── investment_company/           # Company domain endpoints
│   │   │   ├── __init__.py
│   │   │   ├── test_company_operations.py    # Company CRUD operations
│   │   │   ├── test_company_calculations.py  # Company calculation endpoints
│   │   │   ├── test_company_validation.py    # Input validation testing
│   │   │   ├── test_company_error_handling.py # Error handling testing
│   │   │   └── test_company_integration.py   # API integration testing
│   │   └── tax/                          # Tax domain endpoints
│   │       ├── __init__.py
│   │       ├── test_tax_calculations.py   # Tax calculation endpoints
│   │       └── test_tax_integration.py    # Tax integration endpoints
│   ├── integration/                      # Cross-domain integration testing
│   │   ├── __init__.py
│   │   ├── test_banking_fund_integration.py      # Banking-fund integration
│   │   ├── test_company_fund_integration.py      # Company-fund integration
│   │   └── test_tax_fund_integration.py          # Tax-fund integration
│   ├── middleware/                       # Middleware functionality testing
│   │   ├── __init__.py
│   │   ├── test_error_handling.py        # Error handling middleware
│   │   ├── test_logging.py               # Logging middleware
│   │   ├── test_authentication.py        # Authentication middleware
│   │   └── test_validation.py            # Validation middleware
│   ├── performance/                      # API performance testing
│   │   ├── __init__.py
│   │   ├── test_response_times.py        # Response time validation
│   │   ├── test_concurrent_requests.py   # Concurrent request handling
│   │   └── test_memory_usage.py         # Memory usage validation
│   └── security/                         # Security testing
│       ├── __init__.py
│       ├── test_authentication.py        # Authentication mechanisms
│       ├── test_authorization.py         # Access control validation
│       ├── test_input_validation.py     # Input validation security
│       └── test_rate_limiting.py        # Rate limiting security
│
├── e2e/                                  # End-to-end tests - complete user journeys
│   ├── __init__.py
│   ├── critical_paths/                    # Critical business path testing
│   │   ├── __init__.py
│   │   ├── fund/                           # Fund lifecycle testing
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_lifecycle.py                # Complete fund lifecycle
│   │   │   ├── test_capital_management.py            # Capital call to distribution
│   │   │   ├── test_nav_management.py                # NAV-based fund management
│   │   │   └── test_cost_based_management.py         # Cost-based fund management
│   │   ├── investment_company/              # Company management testing
│   │   │   ├── __init__.py
│   │   │   ├── test_company_lifecycle.py             # Company creation to closure
│   │   │   └── test_company_relationship_management.py # Relationship management
│   │   ├── entity/                          # Entity management testing
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_lifecycle.py              # Entity creation to closure
│   │   │   └── test_entity_investment_management.py  # Investment management
│   │   ├── banking/                         # Banking operations testing
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_lifecycle.py             # Account setup to closure
│   │   │   ├── test_transaction_management.py        # Transaction processing
│   │   │   ├── test_banking_cross_module_workflow.py # Cross-module integration workflow
│   │   │   └── test_banking_performance_workflow.py  # Performance under load workflow
│   │   ├── tax/                             # Tax operations testing
│   │   │   ├── __init__.py
│   │   │   ├── test_tax_calculation_workflows.py     # Tax computation workflows
│   │   │   └── test_tax_reporting_workflows.py       # Tax reporting workflows
│   │   └── cross_domain/                     # Cross-domain workflows
│   │       ├── __init__.py
│   │       ├── test_fund_company_integration.py      # Fund-company integration
│   │       ├── test_fund_entity_integration.py       # Fund-entity integration
│   │       ├── test_fund_banking_integration.py      # Fund-banking integration
│   │       └── test_fund_tax_integration.py          # Fund-tax integration
│   ├── user_scenarios/                      # User perspective testing
│   │   ├── __init__.py
│   │   ├── investor/                         # Investor workflows
│   │   │   ├── __init__.py
│   │   │   ├── test_investor_portfolio_view.py       # Portfolio overview
│   │   │   ├── test_investor_reporting.py            # Investment reporting
│   │   │   └── test_investor_tax_reporting.py        # Tax reporting
│   │   ├── fund_manager/                     # Fund manager workflows
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_management.py               # Fund administration
│   │   │   ├── test_capital_management.py            # Capital management
│   │   │   └── test_performance_reporting.py         # Performance analysis
│   │   ├── administrator/                    # Administrator workflows
│   │   │   ├── __init__.py
│   │   │   ├── test_system_administration.py         # System administration
│   │   │   ├── test_user_management.py               # User management
│   │   │   └── test_system_monitoring.py             # System monitoring
│   │   └── compliance/                       # Compliance workflows
│   │       ├── __init__.py
│   │       ├── test_regulatory_reporting.py           # Regulatory compliance
│   │       └── test_audit_trail_validation.py        # Audit trail validation
│   └── regression/                           # Regression testing
│       ├── __init__.py
│       ├── test_known_issues.py                      # Previously fixed bugs
│       ├── test_performance_regressions.py            # Performance regression detection
│       └── test_business_rule_regressions.py          # Business rule regression detection
│
├── performance/                          # Performance tests - load and stress testing
│   ├── __init__.py
│   ├── load_tests/                       # Load testing under expected conditions
│   │   ├── __init__.py
│   │   ├── fund/                          # Fund performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_calculation_load.py         # Calculation service load
│   │   │   ├── test_fund_event_processing_load.py    # Event processing load
│   │   │   └── test_fund_query_load.py               # Fund query performance
│   │   ├── investment_company/             # Company performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_company_query_load.py            # Company query performance
│   │   │   └── test_company_relationship_load.py     # Relationship query performance
│   │   ├── entity/                        # Entity performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_query_load.py             # Entity query performance
│   │   │   └── test_entity_investment_load.py        # Investment query performance
│   │   ├── banking/                       # Banking performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_transaction_load.py      # Transaction processing load
│   │   │   ├── test_banking_query_load.py            # Banking query performance
│   │   │   ├── test_banking_event_load.py             # Event processing load
│   │   │   └── test_banking_cache_load.py             # Cache performance load
│   │   ├── tax/                           # Tax performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_tax_calculation_load.py          # Tax calculation load
│   │   │   └── test_tax_query_load.py                # Tax query performance
│   │   ├── api/                            # API performance testing
│   │   │   ├── __init__.py
│   │   │   ├── test_api_endpoint_load.py             # API endpoint load
│   │   │   └── test_api_contract_validation_load.py  # Contract validation load
│   │   └── system/                         # System-wide performance testing
│   │       ├── __init__.py
│   │       ├── test_database_query_load.py           # Database query performance
│   │       ├── test_event_system_load.py             # Event system load
│   │       └── test_calculation_engine_load.py       # Calculation engine load
│   ├── stress_tests/                       # Stress testing under extreme conditions
│   │   ├── __init__.py
│   │   ├── database/                        # Database stress testing
│   │   │   ├── __init__.py
│   │   │   ├── test_database_connection_stress.py    # Connection pool stress
│   │   │   ├── test_database_query_stress.py         # Query performance stress
│   │   │   └── test_database_transaction_stress.py   # Transaction stress
│   │   ├── memory/                          # Memory stress testing
│   │   │   ├── __init__.py
│   │   │   ├── test_memory_usage_stress.py           # Memory usage under load
│   │   │   └── test_memory_leak_stress.py            # Memory leak detection
│   │   ├── concurrency/                     # Concurrency stress testing
│   │   │   ├── __init__.py
│   │   │   ├── test_concurrent_operations.py         # Concurrent operation handling
│   │   │   ├── test_race_condition_stress.py         # Race condition stress
│   │   │   ├── test_deadlock_stress.py               # Deadlock detection
│   │   │   └── test_banking_concurrency_stress.py    # Banking concurrent operations stress
│   │   └── volume/                          # Volume stress testing
│   │       ├── __init__.py
│   │       ├── test_event_volume_stress.py           # High event volume handling
│   │       ├── test_data_volume_stress.py            # Large dataset stress
│   │       ├── test_user_volume_stress.py            # High user volume stress
│   │       └── test_banking_volume_stress.py         # Banking high volume operations stress
│   ├── scalability/                         # Scalability testing
│   │   ├── __init__.py
│   │   ├── data_scaling/                     # Data volume scaling
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_data_scaling.py              # Fund data scaling
│   │   │   ├── test_company_data_scaling.py           # Company data scaling
│   │   │   ├── test_entity_data_scaling.py            # Entity data scaling
│   │   │   ├── test_banking_data_scaling.py           # Banking data scaling (1000+ banks, 5000+ accounts)
│   │   │   └── test_transaction_data_scaling.py       # Transaction data scaling
│   │   ├── user_scaling/                     # User concurrency scaling
│   │   │   ├── __init__.py
│   │   │   ├── test_investor_concurrency_scaling.py  # Investor concurrency
│   │   │   └── test_administrator_scaling.py         # Administrator scaling
│   │   └── system_scaling/                   # System resource scaling
│   │       ├── __init__.py
│   │       ├── test_calculation_engine_scaling.py     # Calculation engine scaling
│   │       ├── test_event_processor_scaling.py        # Event processor scaling
│   │       ├── test_banking_event_processor_scaling.py # Banking event processor scaling
│   │       └── test_api_gateway_scaling.py            # API gateway scaling
│   └── baseline/                             # Performance baseline management
│       ├── __init__.py
│       ├── test_performance_baseline.py               # Performance baseline establishment
│       ├── test_performance_regression.py              # Performance regression detection
│       └── test_performance_monitoring.py              # Performance monitoring validation
│
├── property/                             # Property tests - business rule validation
│   ├── __init__.py
│   ├── business_rules/                    # Business rule property validation
│   │   ├── __init__.py
│   │   ├── fund/                          # Fund business rules
│   │   │   ├── __init__.py
│   │   │   ├── test_fund_invariants.py               # Fund state invariants
│   │   │   ├── test_equity_balance_properties.py     # Equity balance properties
│   │   │   ├── test_event_ordering_properties.py     # Event sequence properties
│   │   │   ├── test_status_transition_properties.py  # Status transition properties
│   │   │   └── test_fund_type_properties.py          # Fund type-specific properties
│   │   ├── investment_company/             # Company business rules
│   │   │   ├── __init__.py
│   │   │   ├── test_company_invariants.py            # Company state invariants
│   │   │   ├── test_company_relationship_properties.py # Relationship properties
│   │   │   └── test_company_status_properties.py     # Company status properties
│   │   ├── entity/                        # Entity business rules
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_invariants.py             # Entity state invariants
│   │   │   ├── test_entity_investment_properties.py  # Investment properties
│   │   │   └── test_entity_tax_properties.py         # Tax-related properties
│   │   ├── banking/                       # Banking business rules
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_invariants.py            # Banking state invariants
│   │   │   ├── test_transaction_properties.py        # Transaction properties
│   │   │   └── test_account_properties.py            # Account properties
│   │   ├── tax/                           # Tax business rules
│   │   │   ├── __init__.py
│   │   │   ├── test_tax_invariants.py                # Tax state invariants
│   │   │   ├── test_tax_calculation_properties.py    # Tax calculation properties
│   │   │   └── test_tax_reporting_properties.py      # Tax reporting properties
│   │   └── rates/                         # Rate business rules
│   │       ├── __init__.py
│   │       ├── test_rate_invariants.py               # Rate state invariants
│   │       └── test_rate_calculation_properties.py   # Rate calculation properties
│   ├── financial_properties/               # Financial calculation properties
│   │   ├── __init__.py
│   │   ├── fund/                           # Fund financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_irr_properties.py                # IRR calculation properties
│   │   │   ├── test_fifo_properties.py               # FIFO calculation properties
│   │   │   ├── test_nav_properties.py                # NAV calculation properties
│   │   │   ├── test_debt_cost_properties.py          # Debt cost calculation properties
│   │   │   └── test_equity_balance_properties.py     # Equity balance properties
│   │   ├── investment_company/              # Company financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_company_performance_properties.py # Performance calculation properties
│   │   │   └── test_company_valuation_properties.py  # Valuation calculation properties
│   │   ├── entity/                         # Entity financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_entity_performance_properties.py # Entity performance properties
│   │   │   └── test_entity_valuation_properties.py  # Entity valuation properties
│   │   ├── banking/                        # Banking financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_banking_performance_properties.py # Banking performance properties
│   │   │   ├── test_banking_transaction_properties.py # Transaction calculation properties
│   │   │   └── test_banking_cache_properties.py      # Cache performance properties
│   │   ├── tax/                            # Tax financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_tax_calculation_properties.py    # Tax calculation properties
│   │   │   └── test_tax_liability_properties.py      # Tax liability properties
│   │   ├── rates/                          # Rate financial properties
│   │   │   ├── __init__.py
│   │   │   ├── test_rate_calculation_properties.py   # Rate calculation properties
│   │   │   └── test_rate_interpolation_properties.py # Rate interpolation properties
│   │   └── shared/                         # Shared financial properties
│   │       ├── __init__.py
│   │       ├── test_calculation_properties.py        # General calculation properties
│   │       └── test_math_properties.py               # Mathematical properties
│   └── data_integrity/                     # Data integrity properties
│       ├── __init__.py
│       ├── transaction_properties/           # Transaction integrity
│       │   ├── __init__.py
│       │   ├── test_transaction_acid_properties.py   # ACID compliance properties
│       │   ├── test_transaction_isolation_properties.py # Isolation level properties
│       │   └── test_transaction_consistency_properties.py # Consistency properties
│       ├── audit_properties/                 # Audit trail properties
│       │   ├── __init__.py
│       │   ├── test_audit_trail_properties.py        # Audit trail validation
│       │   ├── test_audit_logging_properties.py      # Audit logging properties
│       │   └── test_audit_recovery_properties.py     # Audit recovery properties
│       ├── consistency_properties/            # Data consistency properties
│       │   ├── __init__.py
│       │   ├── test_cross_model_consistency.py       # Cross-model consistency
│       │   ├── test_referential_integrity.py         # Referential integrity
│       │   └── test_business_rule_consistency.py     # Business rule consistency
│       └── validation_properties/             # Data validation properties
│           ├── __init__.py
│           ├── test_input_validation_properties.py    # Input validation properties
│           ├── test_business_rule_validation.py       # Business rule validation
│           └── test_error_handling_properties.py      # Error handling properties
│
├── domain/                               # Domain-specific test utilities
│   ├── __init__.py
│   ├── test_companies_ui_domain.py              # Companies UI domain tests
│   └── test_fund_event_cash_flows.py            # Cash flow domain tests
│
├── output/                               # Test output and baseline files
│   ├── test_main_output_baseline.txt             # Baseline test output
│   └── test_main_output_new.txt                  # Current test output
│
└── scripts/                              # Test execution and utility scripts
    ├── ci-runner.py                              # CI/CD test runner
    ├── performance/                               # Performance testing scripts
    │   ├── __init__.py
    │   ├── baseline_results_*.txt                 # Performance baseline results
    │   ├── database_analysis_*.txt                # Database performance analysis
    │   └── load_testing_script.py                 # Load testing automation
    └── test_categories.py                        # Test categorization utilities
