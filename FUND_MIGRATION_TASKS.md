# Fund Model Migration Tasks

## Overview
Migrate the Fund model and all its methods from `src/models.py` to `src/fund/models.py` while preserving all business logic and ensuring identical output.

## Migration Tasks

### 1. Core Fund Model Structure
- [ ] **Task 1.1**: Migrate Fund class definition (lines 130-196 in src/models.py)
  - All fields and relationships
  - All docstrings and comments
  - All table constraints and indexes

### 2. Fund Properties
- [x] **Task 2.1**: Migrate `should_be_active` property (lines 197-209)
- [x] **Task 2.2**: Migrate `should_have_final_tax_statement` property (lines 210-245)
- [ ] **Task 2.3**: Migrate `start_date` property (lines 268-294)
- [ ] **Task 2.4**: Migrate `end_date` property (lines 295-313)
- [x] **Task 2.5**: Migrate `total_investment_duration_months` property (lines 314-331)
- [x] **Task 2.6**: Migrate `current_value` property (lines 332-346)
- [x] **Task 2.7**: Migrate `calculated_average_equity_balance` property (lines 347-351)
- [x] **Task 2.8**: Migrate `current_units` property and setter (lines 1593-1613)
- [x] **Task 2.9**: Migrate `current_unit_price` property and setter (lines 1614-1631)
- [x] **Task 2.10**: Migrate `total_cost_basis` property and setter (lines 1632-1651)

### 3. Status Update Methods
- [x] **Task 3.1**: Migrate `update_final_tax_statement_status` method (lines 246-256)
- [x] **Task 3.2**: Migrate `update_active_status` method (lines 257-267)

### 4. Core Calculation Methods
- [x] **Task 4.1**: Migrate `update_current_equity_balance` method (lines 352-378)
- [x] **Task 4.2**: Migrate `update_average_equity_balance` method (lines 379-387)
- [x] **Task 4.3**: Migrate `update_current_units_and_price` method (lines 388-422)
- [x] **Task 4.4**: Migrate `_calculate_nav_event_amounts` method (lines 423-443)
- [x] **Task 4.5**: Migrate `update_current_units_after_event` method (lines 444-466)
- [x] **Task 4.6**: Migrate `update_total_cost_basis` method (lines 467-478)
- [x] **Task 4.7**: Migrate `get_nav_based_cost_basis` method (lines 479-505)
- [x] **Task 4.8**: Migrate `update_all_calculated_fields` method (lines 506-525)

### 5. Debt Cost Methods
- [x] **Task 5.1**: Migrate `calculate_debt_cost` method (lines 526-545)
- [x] **Task 5.2**: Migrate `_calculate_daily_interest_charge_objects` method (lines 1061-1120)
- [x] **Task 5.3**: Migrate `create_daily_risk_free_interest_charges` method (lines 1121-1181)
- [x] **Task 5.4**: Migrate `calculate_financial_year_interest_expense` method (lines 1182-1229)
- [x] **Task 5.5**: Migrate `_process_financial_year_for_debt_cost` method (lines 1230-1254)
- [x] **Task 5.6**: Migrate `create_fy_debt_cost_events` method (lines 1255-1286)
- [x] **Task 5.7**: Migrate `_delete_debt_cost_events` method (lines 1287-1303)
- [x] **Task 5.8**: Migrate `recalculate_debt_costs` method (lines 1304-1321)

### 6. Distribution Methods
- [x] **Task 6.1**: Migrate `get_distributions_by_type` method (lines 546-566)
- [x] **Task 6.2**: Migrate `get_total_distributions` method (lines 567-581)
- [x] **Task 6.3**: Migrate `get_taxable_distributions` method (lines 582-600)
- [x] **Task 6.4**: Migrate `get_gross_distributions` method (lines 601-615)
- [x] **Task 6.5**: Migrate `get_net_distributions` method (lines 616-624)
- [x] **Task 6.6**: Migrate `get_total_tax_withheld` method (lines 625-638)
- [x] **Task 6.7**: Migrate `get_distributions_with_tax_details` method (lines 639-695)
- [x] **Task 6.8**: Migrate `add_distribution` method (lines 1507-1534)
- [x] **Task 6.9**: Migrate `_create_distribution_with_tax_objects` method (lines 1535-1565)
- [x] **Task 6.10**: Migrate `add_distribution_with_tax_direct` method (lines 1566-1592)
- [x] **Task 6.11**: Migrate `add_distribution_with_tax` method (lines 1021-1044)
- [x] **Task 6.12**: Migrate `add_distribution_with_tax_rate` method (lines 1045-1060)

### 7. Capital Gains Methods
- [x] **Task 7.1**: Migrate `get_capital_gains` method (lines 696-705)
- [x] **Task 7.2**: Migrate `_calculate_nav_based_capital_gains` method (lines 706-718)
- [x] **Task 7.3**: Migrate `_get_cost_based_capital_gains` method (lines 719-731)

### 8. Capital Movement Methods
- [x] **Task 8.1**: Migrate `get_capital_movements` method (lines 732-748)
- [x] **Task 8.2**: Migrate `get_capital_calls` method (lines 749-771)
- [x] **Task 8.3**: Migrate `add_capital_call` method (lines 1439-1472)
- [x] **Task 8.4**: Migrate `add_return_of_capital` method (lines 1473-1506)

### 9. Average Equity Methods
- [x] **Task 9.1**: Migrate `calculate_average_equity_balance` method (lines 772-781)
- [x] **Task 9.2**: Migrate `_calculate_nav_based_average_equity` method (lines 782-796)
- [x] **Task 9.3**: Migrate `_calculate_cost_based_average_equity` method (lines 797-812)

### 10. IRR Calculation Methods
- [x] **Task 10.1**: Migrate `_calculate_irr_base` method (lines 813-846)
- [x] **Task 10.2**: Migrate `calculate_irr` method (lines 847-852)
- [x] **Task 10.3**: Migrate `calculate_after_tax_irr` method (lines 853-858)
- [x] **Task 10.4**: Migrate `calculate_real_irr` method (lines 859-867)
- [x] **Task 10.5**: Migrate `get_irr_percentage` method (lines 868-873)
- [x] **Task 10.6**: Migrate `get_after_tax_irr_percentage` method (lines 950-954)
- [x] **Task 10.7**: Migrate `get_real_irr_percentage` method (lines 955-959)

### 11. Tax Statement Methods
- [x] **Task 11.1**: Migrate `get_tax_statements_by_financial_year` method (lines 874-891)
- [x] **Task 11.2**: Migrate `get_tax_statement_for_entity_financial_year` method (lines 892-899)
- [x] **Task 11.3**: Migrate `_create_or_update_tax_statement_object` method (lines 900-929)
- [x] **Task 11.4**: Migrate `create_or_update_tax_statement` method (lines 930-945)
- [x] **Task 11.5**: Migrate `_create_tax_payment_event_object` method (lines 960-983)
- [x] **Task 11.6**: Migrate `create_tax_payment_events` method (lines 984-1020)

### 12. NAV-Based Fund Methods
- [x] **Task 12.1**: Migrate `add_unit_purchase` method (lines 1322-1363)
- [x] **Task 12.2**: Migrate `add_unit_sale` method (lines 1364-1405)
- [x] **Task 12.3**: Migrate `add_nav_update` method (lines 1406-1438)

### 13. Event Management Methods
- [x] **Task 13.1**: Migrate `get_events` method (lines 1652-1676)
- [x] **Task 13.2**: Migrate `_get_recalculation_methods_for_event_type` method (lines 1677-1690)
- [x] **Task 13.3**: Migrate `delete_event` method (lines 1691-1723)
- [x] **Task 13.4**: Migrate `recalculate_all_fields` method (lines 1724-1741)
- [x] **Task 13.5**: Migrate `_create_bulk_event_objects` method (lines 1742-1757)
- [x] **Task 13.6**: Migrate `bulk_add_events` method (lines 1758-1781)

### 14. Utility Methods
- [x] **Task 14.1**: Migrate `__repr__` method (lines 947-950)

## Verification Tasks
- [x] **Task V1**: Verify all imports are correct in new module
- [ ] **Task V2**: Run test suite and compare output with old structure
- [ ] **Task V3**: Verify all relationships work correctly
- [ ] **Task V4**: Verify all calculations produce identical results

## Notes
- Each method must be copied exactly as-is from src/models.py
- All docstrings, comments, and logic must be preserved
- All imports must be updated to work with new module structure
- No business logic changes are allowed 