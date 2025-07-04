# Project Context - Investment Tracker

## Current State (December 2024)

This is a Python investment tracker using SQLAlchemy ORM for managing funds, events, tax statements, and financial calculations. The project is in a stable, well-tested state with comprehensive documentation.

## Recent Major Work: Session Handling Refactor

### What Was Done
- **Centralized session resolution** using a `@with_session` decorator from `src/utils.py`
- **Removed repetitive session resolution code** from model methods
- **Improved code maintainability** without performance cost
- **Decorated only methods that perform database queries** (following best practices)

### Key Issues Encountered & Resolved
1. **Keyword Argument Problems**: Methods decorated with `@with_session` must be called with `session=session` keyword argument, not positional. This caused "multiple values for argument 'session'" errors.

2. **Missing Methods**: Several methods needed restoration after the refactor:
   - `add_distribution_with_tax`
   - `create_tax_payment_events`
   - `create_daily_risk_free_interest_charges`
   - `create_fy_debt_cost_events`

3. **Syntax Errors**: Fixed issues with keyword arguments in method calls.

### Testing & Validation
- **Comprehensive system test** (`test_full_system.py`) passes with correct IRR and cash flow results
- **All business logic preserved** during the refactor
- **Performance maintained** - no degradation observed

## Recent Major Work: NAV-Based Fund Implementation

### What Was Done
- **Added comprehensive NAV-based fund support** alongside existing cost-based funds
- **Implemented automatic field calculations** for NAV-based funds:
  - `amount` in unit purchase/sale events: `(units * unit_price) ± brokerage_fee`
  - `shares_owned` in NAV update events: Cumulative units from all unit events
  - `current_units` and `current_unit_price`: Calculated from NAV events
- **Added `brokerage_fee` field** to FundEvent model for transaction costs
- **Updated database schema** to make commitment_amount nullable (not applicable for NAV-based funds)
- **Moved calculation logic** from models.py to calculations.py for better code organization
- **Updated comprehensive documentation** in DESIGN_GUIDELINES.md and README.md

### Key Design Decisions

#### Manual vs Calculated Fields
**NAV-Based Funds**:
- **Manual Fields Only**: `name`, `fund_type`, `tracking_type`, `description`, `currency`
- **No Manual Fields**: `commitment_amount`, `expected_irr`, `expected_duration_months` (not applicable)
- **Automatic Calculations**: `current_units`, `current_unit_price`, `current_equity_balance`, `amount` in events, `shares_owned` in NAV events

**Cost-Based Funds**:
- **Manual Fields**: `name`, `fund_type`, `tracking_type`, `commitment_amount`, `expected_irr`, `expected_duration_months`, `description`, `currency`
- **Automatic Calculations**: `total_cost_basis`, `current_equity_balance`, `is_active`

#### Event Types for NAV-Based Funds
- **UNIT_PURCHASE**: Manual fields: `units_purchased`, `unit_price`, `brokerage_fee`; Calculated: `amount`
- **UNIT_SALE**: Manual fields: `units_sold`, `unit_price`, `brokerage_fee`; Calculated: `amount` (negative)
- **NAV_UPDATE**: Manual fields: `nav_per_share`; Calculated: `shares_owned`
- **DISTRIBUTION**: Manual fields: `amount`, `distribution_type`; No calculated fields

### Key Issues Encountered & Resolved
1. **Database Schema Changes**: SQLite doesn't support ALTER COLUMN for nullability changes, requiring database recreation
2. **Import Issues**: Fixed relative imports in models.py to work with the project structure
3. **Code Organization**: Moved calculation logic from models.py to calculations.py for better separation of concerns
4. **Documentation**: Comprehensive updates to explain the new NAV-based fund patterns

### Testing & Validation
- **Database migration** completed successfully with backup/restore process
- **Calculation logic** moved to calculations.py and tested
- **Documentation updated** with clear examples and field classifications
- **Ready for system testing** with NAV-based fund examples

### Architectural Impact
- **Enhanced fund type support**: Now supports both NAV-based and cost-based funds with appropriate field handling
- **Improved code organization**: Calculation logic properly separated from model definitions
- **Better user experience**: Clear distinction between manual and calculated fields
- **Comprehensive documentation**: Detailed examples and field classifications for both fund types

## Architectural Decisions

### Session Handling Pattern
```python
@with_session
def some_method(self, session=None, **kwargs):
    # Method logic here
    # session is automatically resolved by decorator
```

**Why this pattern**: Eliminates repetitive session resolution code while maintaining clear method signatures.

### Database Models
- **Fund**: Core investment entity
- **Event**: Financial transactions and calculations
- **TaxStatement**: Tax-related data
- **RiskFreeRate**: Market data for calculations

### Testing Strategy
- **System-level tests** that validate end-to-end calculations
- **IRR and cash flow validation** as primary success metrics
- **Comprehensive test coverage** for all major features

## Development Workflow

### Git Strategy
- **Feature branches** for significant changes
- **Pull requests** for code review
- **Test before merge** - all tests must pass
- **Documentation updates** with code changes

### Recent Workflow Example
1. Created `session-refactor-v2` branch
2. Incremental refactoring with testing at each step
3. Fixed issues as they arose
4. Comprehensive testing before merge
5. Updated documentation (README.md, DESIGN_GUIDELINES.md)
6. Merged to main and cleaned up branches

## Key Lessons Learned

### Session Management
- **Always use keyword arguments** when calling decorated methods
- **Test thoroughly** after session-related changes
- **Preserve business logic** during refactoring

### Code Organization
- **Centralize common patterns** (like session handling)
- **Document architectural decisions** for future reference
- **Keep documentation in sync** with code changes

### Testing
- **System tests are critical** for financial calculations
- **IRR and cash flow validation** catch most issues
- **Test before merging** to avoid breaking changes

## Current Project Structure
```
investment_tracker/
├── data/                    # Data files
├── src/
│   ├── __init__.py
│   ├── calculations.py      # Financial calculations
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   └── utils.py             # Utilities (including @with_session)
├── pyproject.toml           # Project configuration
├── requirements.txt         # Dependencies
├── README.md               # User documentation
├── DESIGN_GUIDELINES.md    # Development patterns
├── PROJECT_CONTEXT.md      # This file
└── test_full_system.py     # Comprehensive system tests
```

## Future Considerations

### Potential Enhancements
- **Streamlit dashboard** for visualization (mentioned in DESIGN_GUIDELINES.md)
- **Additional financial metrics** and calculations
- **Data import/export** capabilities
- **Real-time market data** integration

### Technical Debt
- **None currently identified** - recent refactor cleaned up main issues
- **Monitor session handling patterns** as project grows
- **Consider performance optimization** if data volume increases significantly

## Getting Started for New Developers

1. **Read README.md** for installation and basic usage
2. **Review DESIGN_GUIDELINES.md** for development patterns
3. **Run test_full_system.py** to verify everything works
4. **Follow session handling patterns** established in the refactor
5. **Test thoroughly** before making changes to financial calculations

## Critical Areas

### Financial Calculations & Cash Flows
- **Three IRR Types**: 
  - `calculate_irr()`: Basic IRR from capital flows
  - `calculate_after_tax_irr()`: Includes tax payments
  - `calculate_real_irr()`: Includes opportunity cost (risk-free rates)
- **Cash Flow Events**: Capital calls, returns, distributions, tax payments, risk-free charges, debt cost benefits
- **Event-Driven Calculations**: All financial metrics are calculated from `FundEvent` records
- **Test any changes** to these areas thoroughly - use `test_full_system.py`

### Database Operations
- **Use @with_session decorator** for database queries
- **Follow established patterns** in models.py
- **Maintain data integrity** in all operations

---

*This context file should be updated as the project evolves to maintain a clear record of decisions, work history, and architectural patterns.* 