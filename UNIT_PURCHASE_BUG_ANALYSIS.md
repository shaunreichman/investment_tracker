# Unit Purchase Integration Test Failures - Root Cause Analysis

## Problem Summary

All 7 failing integration tests for unit purchases are failing with the same error:
```
ValueError: Remaining units do not match current units
```

**Location**: `src/fund/calculators/fund_pnl_calculator.py:51`

---

## Root Cause

The `fund.current_units` field is **never being updated** when unit purchase/sale events occur.

### The Flow:

1. **Unit Purchase Event Created** → Creates a new `FundEvent` with `units_purchased`
2. **Secondary Service Triggered** → `fund_event_secondary_service.handle_event_secondary_impact()`
3. **Equity Service Updates** → `fund_equity_service.update_fund_equity_fields()`:
   - ✅ Updates `event.units_owned` for each event (lines 86-101)
   - ❌ **NEVER updates `fund.current_units`**
4. **PNL Calculator Runs** → `fund_pnl_calculator.calculate_pnl()`:
   - Calculates total units from events using FIFO calculator
   - Compares `capital_gains_dict.remaining_units` vs `fund.current_units`
   - **FAILS because `fund.current_units` is still 0.0** (never updated!)

---

## Evidence

### 1. Fund Model Has the Field
```python
# src/fund/models/fund.py:69
current_units = Column(Float, default=0.0)  # (CALCULATED) current number of units owned
```

### 2. Equity Service Updates Events, NOT Fund
```python
# src/fund/services/fund_equity_service.py:86-101
for event, (balance, has_changed) in zip(events, event_balances):
    # ... updates event.current_equity_balance
    
    # Update units owned for NAV-based funds
    if fund.tracking_type == FundTrackingType.NAV_BASED:
        units_owned += event.units_purchased or 0.0
        units_owned -= event.units_sold or 0.0
        # ✅ Updates the EVENT's units_owned
        event.units_owned = units_owned
        # ❌ MISSING: fund.current_units = units_owned
```

### 3. No Code Updates fund.current_units
```bash
$ grep -r "fund\.current_units\s*=" src/fund/
# No matches found!
```

### 4. PNL Calculator Expects fund.current_units to Be Accurate
```python
# src/fund/calculators/fund_pnl_calculator.py:47-51
if fund.tracking_type == FundTrackingType.NAV_BASED:
    fifo_capital_gains_calculator = FifoCapitalGainsCalculator()
    capital_gains_dict = fifo_capital_gains_calculator.calculate_capital_gains(fund_events)
    # Validates that the calculator's result matches the fund's stored value
    if capital_gains_dict.remaining_units != fund.current_units:
        raise ValueError("Remaining units do not match current units")
```

---

## Impact

**All Unit Purchase/Sale Operations Fail** for NAV-based funds because:
- Unit purchase/sale events are created successfully
- Events have correct `units_owned` values
- BUT `fund.current_units` remains at 0.0
- PNL calculation detects the mismatch and raises error

---

## Failed Tests (7 total)

All in `test_unit_purchase_workflow_integration.py`:
1. `test_unit_purchase_service_layer_flow`
2. `test_unit_purchase_service_layer_validation`
3. `test_unit_purchase_equity_calculations`
4. `test_multiple_unit_purchases_fifo_tracking`
5. `test_unit_purchase_with_cash_flow_integration`
6. `test_unit_purchase_transaction_integrity`
7. `test_unit_purchase_performance_with_large_dataset`

---

## Fix Required

**Add `fund.current_units` update to `FundEquityService.update_fund_equity_fields()`**

### Location to Fix:
`src/fund/services/fund_equity_service.py` around line 102

### Suggested Fix:
```python
# After line 101, add:
if fund.tracking_type == FundTrackingType.NAV_BASED:
    old_current_units = fund.current_units
    fund.current_units = units_owned
    if old_current_units != fund.current_units:
        equity_changes.append(FundFieldChange(
            object='FUND', 
            object_id=fund.id, 
            field_name='current_units', 
            old_value=old_current_units, 
            new_value=fund.current_units
        ))
```

This would:
1. Update `fund.current_units` to match the final `units_owned` from the loop
2. Track the change in the `equity_changes` list
3. Ensure PNL calculator's validation passes

---

## Why This Wasn't Caught Earlier

- Unit tests use mocks, so the PNL calculator validation wasn't triggered
- Integration tests for capital calls/returns work because they don't use units
- Only NAV-based funds with unit tracking trigger this validation
- The validation is actually a **good check** - it caught a missing implementation!

---

## Related Code Locations

- **Bug Location**: `src/fund/services/fund_equity_service.py:86-110`
- **Validation Check**: `src/fund/calculators/fund_pnl_calculator.py:47-51`
- **Model Definition**: `src/fund/models/fund.py:69`
- **Failing Tests**: `tests/integration/workflows/fund/test_unit_purchase_workflow_integration.py`
