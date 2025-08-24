# Database Scripts

This folder contains all database-related scripts for the Investment Tracker application.

## Scripts Overview

### `init_database.py`
**Purpose**: Initialize the PostgreSQL database and create all required tables
**Usage**: `python database/init_database.py`
**What it does**:
- Creates database engine using centralized configuration
- Creates all tables defined in the SQLAlchemy models
- Optionally adds sample data
- **Run this first** when setting up a new database

### `simple_db_test.py`
**Purpose**: Test database connectivity and basic functionality
**Usage**: `python database/simple_db_test.py`
**What it does**:
- Tests PostgreSQL connection
- Verifies database exists and is accessible
- Lists all available tables
- **Use this to troubleshoot connection issues**

### `check_database_schema.py`
**Purpose**: Comprehensive database schema verification and health check
**Usage**: `python database/check_database_schema.py`
**What it does**:
- Verifies all expected tables exist
- Shows table structure (columns, constraints)
- Reports record counts for all tables
- Checks foreign key integrity
- **Use this for detailed database inspection**

## Quick Start

1. **Initialize Database** (first time only):
   ```bash
   python database/init_database.py
   ```

2. **Test Connection**:
   ```bash
   python database/simple_db_test.py
   ```

3. **Verify Schema**:
   ```bash
   python database/check_database_schema.py
   ```

**Note**: Run these commands from the project root directory (where `src/` folder is located).

## Database Configuration

The scripts use the centralized configuration from `src/config.py`:
- **Host**: `localhost` (configurable via `POSTGRES_HOST`)
- **Port**: `5432` (configurable via `POSTGRES_PORT`)
- **Database**: `investment_tracker` (configurable via `POSTGRES_DB`)
- **User**: `postgres` (configurable via `POSTGRES_USER`)
- **Password**: `development_password` (configurable via `POSTGRES_PASSWORD`)

## Troubleshooting

**Connection Issues**:
- Ensure PostgreSQL is running
- Verify database exists: `createdb investment_tracker`
- Check user permissions
- Run `simple_db_test.py` for diagnostics

**Schema Issues**:
- Run `init_database.py` to recreate tables
- Use `check_database_schema.py` for detailed inspection
- Check for missing dependencies in requirements.txt

## Notes

- All scripts automatically handle the Python path for imports
- Scripts work from the project root directory
- Virtual environment must be activated for dependencies
- Tables are created in the `investment_tracker` schema (not `public`)
