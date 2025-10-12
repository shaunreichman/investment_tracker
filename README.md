# Investment Tracker

A Python-based system for tracking multiple investments across companies and funds, with support for both NAV-based and cost-based valuation, IRR calculation, tax statement reconciliation, and robust event modeling.

## Features

- **Multi-Company Support:** Track investments across different companies
- **Fund Management:** Support for both NAV-based and cost-based fund tracking
- **Event Modeling:** Comprehensive event system for capital calls, distributions, NAV updates, and more
- **IRR Calculations:** Multiple IRR calculation methods including after-tax and real IRR
- **Tax Integration:** Tax statement reconciliation and tax payment event generation
- **Risk-Free Rate Tracking:** Market data integration for opportunity cost calculations
- **Web UI:** Modern React-based web interface for viewing and managing investments

## Architecture

The system follows a domain-driven design with clear separation of concerns:

- **Entity Domain:** Investment entities (persons/companies)
- **Company Domain:** Companies and fund management
- **Fund Domain:** Fund tracking, events, and calculations
- **Tax Domain:** Tax statements and tax payment events
- **Rates Domain:** Market data and risk-free rates
- **Web UI:** React frontend with Flask API backend
- **Database:** PostgreSQL with centralized configuration and connection pooling

### Database System

The application now uses a **PostgreSQL-based database system** with:
- **Centralized Configuration**: Single configuration file (`database_config.py`) with environment variable support
- **Connection Pooling**: Optimized connection management with health checks
- **Direct Schema Management**: No migration files, direct table creation and verification
- **Enhanced Session Management**: Improved database session handling with global session support

### Domain-Driven Design

The project uses a domain-driven architecture where:

- **Each domain** (fund, tax, entity, rates, company) has its own models, calculations, and creation logic
- **Shared logic** (utilities, base classes, pure calculations) lives in `src/shared/`
- **All imports** should use the new domain modules:

```python
from src.fund.models import Fund, FundEvent, FundTrackingType
from src.tax.models import TaxStatement
from src.entity.models import Entity
from src.rates.models import RiskFreeRate
from src.company.models import Company
from src.shared.utils import with_session
```

### Field Classification

All fields are explicitly classified as:
- **(SYSTEM):** Set by the database/ORM (e.g., primary keys, timestamps)
- **(MANUAL):** Set by the user/developer (e.g., business data, foreign keys)
- **(CALCULATED):** Set by business logic only, never manually
- **(HYBRID):** Can be set manually or calculated, with clear precedence

See [`docs/DESIGN_GUIDELINES.md`](./docs/DESIGN_GUIDELINES.md) for a full field reference and examples.

### Session Management

All model methods that require a database session use the `@with_session` decorator:
- **Always pass `session` as a keyword argument**
- Only methods that perform database queries are decorated
- The backend (not clients) owns session lifecycle
- See [`docs/DESIGN_GUIDELINES.md`](./docs/DESIGN_GUIDELINES.md) for detailed patterns

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+ (for web UI)
- PostgreSQL 12+ (required)

### Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd investment_tracker
   ```

2. **Set up Python environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL database:**
   ```bash
   # macOS
   brew install postgresql
   brew services start postgresql
   
   # Ubuntu
   sudo apt-get install postgresql postgresql-contrib
   sudo systemctl start postgresql
   
   # Create database and user
   createdb investment_tracker
   psql -d investment_tracker -c "CREATE USER postgres WITH PASSWORD 'development_password';"
   ```

4. **Verify database setup:**
   ```bash
   python check_database_schema.py  # Check schema integrity
   python simple_db_test.py         # Test database connection
   ```

5. **Set up web UI:**
   ```bash
   cd frontend
   npm install
   cd ..
   ```

### Running the Application

#### Backend Only (Python)

Run the Flask API server:
```bash
source venv/bin/activate
FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001
```

The API will be available at http://localhost:5001

#### Frontend Only (React)

```bash
cd frontend
npm start
```

The React app will be available at http://localhost:3000

#### Running Both Servers

You'll need to run both servers in separate terminals:

**Terminal 1 (Backend):**
```bash
source venv/bin/activate
FLASK_APP=src/api.py python -m flask run --host=0.0.0.0 --port=5001
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm start
```

### Environment Configuration

The React frontend uses environment variables for configuration:

- `REACT_APP_API_BASE_URL`: Base URL for the Flask API (default: http://localhost:5001)

Create a `.env` file in the `frontend/` directory:
```
REACT_APP_API_BASE_URL=http://localhost:5001
```

## Web UI Features

> **🎉 FRONTEND REFACTORING COMPLETED: The web UI has been upgraded to a first-class, professional-grade system with enterprise standards, comprehensive testing (307 tests), and modern React patterns.**

The web interface provides:

- **Dashboard**: Overview of all funds with portfolio summary, fund table, and recent events
- **Fund Details**: Detailed view of individual funds with events, statistics, and transaction history
- **Real-time Data**: All data comes from the live database via Flask API
- **Responsive Design**: Works on desktop and mobile devices
- **Professional UI**: Material UI components with modern styling
- **Enterprise Standards**: Comprehensive testing, accessibility compliance, and performance optimization

## API Endpoints

The Flask API provides the following endpoints:

- `GET /api/health` - Health check endpoint
- `GET /api/dashboard/portfolio-summary` - Portfolio overview statistics
- `GET /api/dashboard/funds` - List of all funds with key metrics
- `GET /api/dashboard/recent-events` - Recent fund events
- `GET /api/dashboard/performance` - Performance data for all funds
- `GET /api/funds/<fund_id>` - Detailed fund information and events

## Project Structure

```
investment_tracker/
├── src/                       # Core application code (domain-driven)
│   ├── fund/                  # Fund models, calculations, queries
│   ├── tax/                   # Tax models, events, calculations
│   ├── entity/                # Entity models, calculations
│   ├── company/               # Company domain
│   ├── rates/                 # Risk-free rates and related logic
│   ├── shared/                # Shared utilities and base classes
│   ├── config.py              # Enhanced configuration management
│   └── database.py            # Database setup and session management
├── frontend/                  # React frontend
│   ├── src/                   # React source code
│   └── public/                # Static assets
├── tests/                     # Test suite (unit, integration, system)
│   └── output/                # Test output artifacts
├── scripts/                   # Utility and database scripts
├── docs/                      # Documentation
│   ├── DESIGN_GUIDELINES.md   # Core development/design patterns
│   ├── PROJECT_CONTEXT.md     # Project context and onboarding
│   ├── TANSTACK_TABLE_MIGRATION_SPEC.md  # Frontend table migration plan
│   └── refactor_plans/        # Refactoring and migration plans
├── database_config.py         # Centralized PostgreSQL configuration
├── check_database_schema.py   # Database schema verification
├── simple_db_test.py          # Database connection testing
├── requirements.txt           # Python dependencies
├── pyproject.toml             # Project configuration
├── README.md                  # User-facing documentation
└── .gitignore
```

## Testing

### Backend Tests

Run the main test suite:
```bash
python tests/test_main.py
```

Run API endpoint tests:
```bash
python tests/test_api_endpoints.py
```

### Frontend Tests

Run React component tests:
```bash
cd frontend
npm test
```

### System Tests

The system includes comprehensive tests for:
- Backend API endpoints and data validation
- React component rendering and user interactions
- End-to-end data flow from database to frontend
- Error handling and loading states

## Example Usage

### Database Setup
The system now uses PostgreSQL with a centralized configuration. Before running examples, ensure:
1. PostgreSQL is installed and running
2. Database `investment_tracker` exists
3. User `postgres` with password `development_password` is configured
4. Run `python check_database_schema.py` to verify schema

### NAV-Based Fund Example
```python
from src.fund.models import Fund, FundEvent, EventType, DistributionType
from src.database import get_database_session
from datetime import date

# Get database session
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()

try:
    # 1. Create NAV-based fund (minimal manual fields)
    fund = Fund(
        name="ABC Ltd",
        tracking_type=FundTrackingType.NAV_BASED,
        fund_type="Equity - Consumer Discretionary",
        currency="AUD"
    )
    session.add(fund)
    session.flush()  # Get fund ID

    # 2. Add unit purchase (amount calculated automatically)
    purchase_event = FundEvent(
        fund_id=fund.id,
        event_type=EventType.UNIT_PURCHASE,
        event_date=date(2023, 3, 28),
        units_purchased=85.0,
        unit_price=58.00,
        brokerage_fee=19.95,
        description="Initial unit purchase"
    )
    # amount will be calculated as: (85.0 * 58.00) + 19.95 = 4,949.95
    session.add(purchase_event)
    
    # 3. Add NAV update (shares_owned calculated automatically)
    nav_event = FundEvent(
        fund_id=fund.id,
        event_type=EventType.NAV_UPDATE,
        event_date=date(2023, 3, 31),
        nav_per_share=57.20,
        description="March 2023 NAV update"
    )
    session.add(nav_event)
    
    session.commit()
finally:
    session.close()
```

### Cost-Based Fund Example
```python
from src.fund.models import Fund, FundEvent, EventType
from src.database import get_database_session
from datetime import date

# Get database session
engine, session_factory, scoped_session = get_database_session()
session = scoped_session()

try:
    # Create cost-based fund
    fund = Fund(
        name="Private Equity Fund",
        tracking_type=FundTrackingType.COST_BASED,
        commitment_amount=1000000.0,
        expected_irr=15.0,
        expected_duration_months=120
    )
    session.add(fund)
    session.flush()

    # Add capital call
    call_event = FundEvent(
        fund_id=fund.id,
        event_type=EventType.CAPITAL_CALL,
        event_date=date(2023, 1, 1),
        amount=500000.0
    )
    session.add(call_event)
    
    # Update calculated fields
    fund.update_current_equity_balance()
    fund.update_total_cost_basis()
    
    # Calculate IRR
    irr = fund.calculate_irr()
    
    session.commit()
finally:
    session.close()
```

## Troubleshooting

### Common Issues

**Frontend won't connect to backend:**
- Ensure the Flask API is running on port 5001
- Check that `REACT_APP_API_BASE_URL` is set correctly in frontend/.env
- Verify CORS is enabled in the Flask app

**Database connection errors:**
- Verify PostgreSQL is running: `brew services list` (macOS) or `sudo systemctl status postgresql` (Ubuntu)
- Test database connection: `python simple_db_test.py`
- Check database schema: `python check_database_schema.py`
- Verify connection settings in `database_config.py`
- Ensure database and user exist: `psql -l` to list databases

**Import errors:**
- Ensure you're using the domain-driven imports (e.g., `from src.fund.models import Fund`)
- Check that the virtual environment is activated
- Verify all dependencies are installed with `pip install -r requirements.txt`

**Test failures:**
- Verify database connection: `python simple_db_test.py`
- Check database schema integrity: `python check_database_schema.py`
- Ensure PostgreSQL service is running and accessible
- Verify the test database is not corrupted

## Contributing

### Before Contributing

1. **Read the documentation:**
   - [Design Guidelines](docs/DESIGN_GUIDELINES.md) - Architecture and development guidelines
   - [Project Context](docs/PROJECT_CONTEXT.md) - Project overview and context

2. **Understand the architecture:**
   - Domain-driven design principles
   - Session management patterns
   - Field classification system

3. **Set up development environment:**
   - Follow the installation instructions above
   - Run tests to ensure everything works
   - Familiarize yourself with the codebase structure

### Development Guidelines

- **Follow domain-driven design** - organize code by domain (fund, tax, entity, etc.)
- **Use the `@with_session` decorator** for database operations
- **Never set calculated fields manually** - use appropriate calculation methods
- **Write tests** for new features and changes
- **Update documentation** when adding new patterns or conventions
- **Follow the field classification system** - mark all fields as (SYSTEM), (MANUAL), (CALCULATED), or (HYBRID)

### Code Style

- Use Python 3.8+ features
- Follow PEP 8 for Python code
- Use TypeScript for React components
- Implement proper error handling and loading states
- Write clear, descriptive commit messages

## Documentation

- [Design Guidelines](docs/DESIGN_GUIDELINES.md) - Architecture and development guidelines
- [Project Context](docs/PROJECT_CONTEXT.md) - Project overview and context
- [Web UI Tasks](docs/web_app_summary_dashboard_tasks.md) - Web UI development roadmap and current status

## Roadmap

- Streamlit dashboard for interactive performance and allocation visualization
- Additional financial metrics and calculations
- Data import/export features
- Real-time market data integration
- Ongoing refactoring plans tracked in [`docs/refactor_plans/`](./docs/refactor_plans/)

## License

[Add your license information here]

---

## Recent Improvements

- **2024: Database Centralization Complete** - Migrated from SQLite to PostgreSQL with centralized configuration and connection pooling
- **2024: TanStack Table Migration Foundation** - Comprehensive specification for migrating from Material-UI tables to TanStack Table for enhanced performance
- **2024: Enhanced Database Management** - Direct schema management without migration files, improved connection health checks
- **Standardized date conventions**: All calculations now use inclusive start dates and exclusive end dates for consistency
- **Automatic event listeners**: NAV-based funds automatically update current units after unit purchase/sale events
- **Enhanced FIFO tracking**: NAV-based funds use FIFO cost basis for accurate equity balance calculations
- **Improved IRR calculations**: Complete support for NAV-based fund IRR with unit sales included
- **2024: Domain-driven architecture migration** - Complete reorganization into domain modules