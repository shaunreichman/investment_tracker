# Project Context – Investment Tracker

## Overview

This document provides **project-specific context** for developers working on the Investment Tracker. It focuses on the "why" behind decisions, project evolution, and developer-specific workflows.

**For setup and usage:** See [README.md](../README.md)  
**For development patterns:** See [DESIGN_GUIDELINES.md](DESIGN_GUIDELINES.md)

---

## Project Evolution & Key Decisions

### Domain-Driven Architecture Migration (2024)
**Why:** The original monolithic structure (`src/models.py`, `src/calculations.py`) became difficult to maintain as the project grew.

**What changed:**
- Organized code by business domain (fund, tax, entity, rates, investment_company)
- Each domain has its own `models.py`, `calculations.py`, and `queries.py`
- Shared utilities moved to `src/shared/`
- Clear separation between domain logic and infrastructure

**Impact:** Better maintainability, clearer ownership, easier testing

### Field Classification System
**Why:** Financial calculations require precise understanding of which fields are user-input vs. system-calculated.

**Implementation:**
- Every field explicitly marked as (SYSTEM/MANUAL/CALCULATED/HYBRID)
- Prevents bugs from manually setting calculated fields
- Makes business logic more transparent
- See [DESIGN_GUIDELINES.md](DESIGN_GUIDELINES.md) for full reference

### Session Management Pattern
**Why:** SQLAlchemy sessions need careful lifecycle management to prevent memory leaks and ensure data consistency.

**Pattern:**
- Backend owns all session lifecycle
- Domain methods accept `session` parameter
- `@with_session` decorator for database operations
- Clients remain stateless

---

## Developer Workflows

### Setting Up Development Environment

1. **Clone and setup:**
   ```bash
   git clone <repository-url>
   cd investment_tracker
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Initialize database:**
   ```bash
   python scripts/init_database.py
   ```

3. **Run tests to verify setup:**
   ```bash
   python tests/test_main.py
   ```

### Common Development Tasks

#### Adding a New Domain
1. Create domain directory: `src/new_domain/`
2. Add `models.py`, `calculations.py`, `queries.py`
3. Follow naming conventions from existing domains
4. Add tests in `tests/test_new_domain.py`
5. Update imports throughout codebase

#### Adding a New Field
1. Determine classification: (SYSTEM/MANUAL/CALCULATED/HYBRID)
2. Add field to model with classification comment
3. Update any calculation methods that depend on it
4. Add migration if needed: `alembic revision --autogenerate -m "add new field"`
5. Update tests to verify classification

#### Debugging Database Issues
```bash
# Reset database completely
python scripts/init_database.py

# Check migration status
alembic current
alembic history

# Run specific test
python tests/test_main.py
```

#### Debugging Frontend Issues
```bash
# Check for unused imports (ESLint warnings)
cd frontend
npm run lint

# Fix common issues
npm run lint -- --fix

# Check API connectivity
curl http://localhost:5001/api/health
```

### Code Review Checklist

- [ ] **Domain organization:** Code in correct domain directory?
- [ ] **Field classification:** All fields properly marked?
- [ ] **Session management:** Using `@with_session` decorator?
- [ ] **Tests:** New functionality has test coverage?
- [ ] **Documentation:** Updated relevant docs?
- [ ] **Imports:** Using domain-specific imports?

---

## Technical Debt & Known Issues

### Current Technical Debt
- **ESLint warnings:** Unused imports in React components (see terminal output)
- **Missing dependencies:** Some useEffect hooks missing dependencies
- **Legacy code:** Some old patterns may still exist in edge cases

### Planned Improvements
- **Frontend cleanup:** Remove unused imports and fix dependency warnings
- **Test coverage:** Expand unit tests for edge cases
- **Performance:** Optimize database queries for large datasets
- **Documentation:** Keep docs in sync with code changes

---

## Project-Specific Patterns

### Financial Calculation Patterns
- **IRR calculations:** Use domain-specific calculation methods
- **Tax calculations:** Follow tax statement reconciliation patterns
- **Unit tracking:** NAV-based funds use FIFO cost basis
- **Date handling:** Inclusive start dates, exclusive end dates

### Database Patterns
- **Migrations:** Use Alembic for all schema changes
- **Session management:** Always use `@with_session` decorator
- **Field updates:** Never manually set calculated fields
- **Query optimization:** Use domain-specific query methods

### Testing Patterns
- **System tests:** `tests/test_main.py` validates entire system
- **Output comparison:** Test outputs saved to `tests/output/`
- **Database state:** Tests reset database to known state
- **Calculation validation:** IRR and cash flow are primary metrics

---

## Troubleshooting for Developers

### Common Issues & Solutions

**Import errors after domain migration:**
```bash
# Check you're using domain imports
from src.fund.models import Fund  # ✅ Correct
from src.models import Fund       # ❌ Old pattern
```

**Database session issues:**
```python
# Always use keyword arguments
fund.create_capital_call(amount=100000, session=session)  # ✅ Correct
fund.create_capital_call(100000, session)                 # ❌ Wrong
```

**Test failures:**
```bash
# Reset database and reinitialize
python scripts/init_database.py
python tests/test_main.py
```

**Frontend build issues:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm start
```

### Debugging Workflows

**Database debugging:**
```python
# Add to your test/debug script
from src.database import get_database_session
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()

try:
    # Your debugging code here
    funds = session.query(Fund).all()
    print(f"Found {len(funds)} funds")
finally:
    session.close()
```

**Frontend debugging:**
```typescript
// Add to React components for debugging
console.log('API Response:', data);
console.log('Component State:', state);
```

---

## Onboarding Checklist for New Developers

1. **Environment setup:**
   - [ ] Python 3.8+ installed
   - [ ] Node.js 18+ installed
   - [ ] Virtual environment created
   - [ ] Dependencies installed
   - [ ] Database initialized
   - [ ] Tests passing

2. **Documentation review:**
   - [ ] README.md (setup and usage)
   - [ ] DESIGN_GUIDELINES.md (development patterns)
   - [ ] PROJECT_CONTEXT.md (this file - project context)

3. **Codebase exploration:**
   - [ ] Understand domain structure in `src/`
   - [ ] Review field classification system
   - [ ] Examine session management patterns
   - [ ] Look at test structure

4. **First contribution:**
   - [ ] Follow domain-driven organization
   - [ ] Use proper field classification
   - [ ] Implement session management correctly
   - [ ] Add appropriate tests
   - [ ] Update documentation

---

## Future Considerations

### Planned Features
- **Streamlit dashboard:** Interactive visualization
- **Real-time data:** Market data integration
- **Import/export:** Data migration tools
- **Performance optimization:** Large dataset handling

### Architectural Evolution
- **Microservices:** Potential future migration
- **Real-time updates:** WebSocket integration
- **Advanced analytics:** Machine learning integration
- **Mobile app:** React Native consideration

---

*This document should be updated as the project evolves to maintain clear context for developers joining the project.* 