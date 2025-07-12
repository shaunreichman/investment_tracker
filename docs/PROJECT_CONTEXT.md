# Project Context – Investment Tracker

## Overview (2024)

Investment Tracker is a Python-based system for managing investment funds, events, tax statements, and financial calculations. The project uses SQLAlchemy ORM, a domain-driven architecture, and explicit field classification for clarity and maintainability.

---

## Project Structure

```
investment_tracker/
├── src/                       # Core application code (domain-driven)
│   ├── fund/                  # Fund models, calculations, queries
│   ├── tax/                   # Tax models, events, calculations
│   ├── entity/                # Entity models, calculations
│   ├── investment_company/    # Investment company domain
│   ├── rates/                 # Risk-free rates and related logic
│   ├── shared/                # Shared utilities and base classes
│   └── database.py            # Database setup and session management
├── tests/                     # Test suite (unit, integration, system)
│   └── output/                # Test output artifacts
├── scripts/                   # Utility and migration scripts
├── docs/                      # Documentation
│   ├── DESIGN_GUIDELINES.md   # Core development/design patterns
│   ├── PROJECT_CONTEXT.md     # This file
│   └── refactor_plans/        # Refactoring and migration plans
├── alembic/                   # Database migrations (Alembic)
├── data/                      # Data files and backups
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project configuration
├── README.md                  # User-facing documentation
└── .gitignore
```

---

## Domain-Driven Architecture

- **Each domain (fund, tax, entity, etc.) has its own models, calculations, and logic.**
- **No business logic in models.py:** All calculations are in calculations.py within each domain.
- **Session management is handled at the outermost layer** (API, CLI, or test scripts), never inside domain methods.
- **All database operations are performed via domain methods** that accept a session parameter.

---

## Field Classification (SYSTEM / MANUAL / CALCULATED / HYBRID)

Every model field is explicitly classified:
- **(SYSTEM):** Set by the database/ORM (e.g., primary keys, timestamps)
- **(MANUAL):** Set by the user/developer (e.g., business data, foreign keys)
- **(CALCULATED):** Set by business logic only, never manually
- **(HYBRID):** Can be set manually or calculated, with clear precedence

See `docs/DESIGN_GUIDELINES.md` for full field reference and examples.

---

## Core Patterns & Best Practices

### Session Management
- Use the `@with_session` decorator for methods that require a database session.
- Always pass `session` as a keyword argument.
- The backend (not clients) owns session lifecycle.

### Object & Event Creation
- Use class methods (e.g., `Fund.create()`, `Entity.create()`) for root objects.
- Use domain methods for related objects and events (e.g., `fund.add_capital_call()`).
- Use managers (e.g., `TaxEventManager`) for system-generated events.

### Separation of Concerns
- **Models:** ORM logic, session management, orchestration (no business calculations)
- **Calculations:** Pure business logic, stateless, easy to test

---

## Testing & Validation
- Comprehensive system and unit tests in `tests/`
- Test outputs stored in `tests/output/`
- IRR and cash flow validation are primary success metrics
- All major features have test coverage

---

## Documentation
- **DESIGN_GUIDELINES.md:** Core development patterns, field reference, workflow examples, and testing guidelines
- **refactor_plans/:** Architectural and migration plans, technical debt tracking
- **README.md:** User-facing setup and usage instructions

---

## Onboarding for New Developers
1. Read `README.md` for setup and usage
2. Review `docs/DESIGN_GUIDELINES.md` for development patterns and field classifications
3. Explore the domain structure in `src/`
4. Run tests in `tests/` to verify setup
5. Follow session and object creation patterns in all new code

---

## Future Considerations
- Streamlit dashboard for visualization
- Additional financial metrics and calculations
- Data import/export features
- Real-time market data integration
- Ongoing refactoring plans tracked in `docs/refactor_plans/`

---

*This file should be updated as the project evolves to maintain a clear record of decisions, structure, and best practices.* 