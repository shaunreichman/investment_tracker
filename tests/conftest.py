import os
import sys
from pathlib import Path
import tempfile
import shutil
import random
import uuid
from typing import Generator

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session

# Ensure project root is on sys.path so `import src.*` works
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.base import Base
from src.api import create_app


def create_test_database_name() -> str:
    """Create a unique test database name to avoid conflicts."""
    return f"test_{uuid.uuid4().hex[:8]}"


def create_postgresql_test_engine(database_name: str):
    """Create a PostgreSQL engine for testing with the specified database."""
    # Use the same connection parameters as the main database but with test database name
    from database_config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD
    
    # Connect to default postgres database first to create test database
    default_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
    default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
    
    try:
        # Create test database
        with default_engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE {database_name}"))
            print(f"Created test database: {database_name}")
    except Exception as e:
        print(f"Database {database_name} might already exist: {e}")
    finally:
        default_engine.dispose()
    
    # Create engine for the test database
    test_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{database_name}"
    return create_engine(test_url, echo=False)


def drop_test_database(database_name: str):
    """Drop the test database."""
    from database_config import POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER, POSTGRES_PASSWORD
    
    # Connect to default postgres database to drop test database
    default_url = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
    default_engine = create_engine(default_url, isolation_level="AUTOCOMMIT")
    
    try:
        with default_engine.connect() as conn:
            # Terminate all connections to the test database
            conn.execute(text(f"""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = '{database_name}' AND pid <> pg_backend_pid()
            """))
            
            # Drop the test database
            conn.execute(text(f"DROP DATABASE IF EXISTS {database_name}"))
            print(f"Dropped test database: {database_name}")
    except Exception as e:
        print(f"Error dropping test database {database_name}: {e}")
    finally:
        default_engine.dispose()


@pytest.fixture(scope="session")
def test_database_name() -> str:
    """Generate a unique test database name for this test session."""
    return create_test_database_name()


@pytest.fixture(scope="session")
def engine(test_database_name):
    """Create PostgreSQL test database engine."""
    engine = create_postgresql_test_engine(test_database_name)
    
    # Import all model modules so their tables are registered with Base
    # Import order matters - import dependencies first
    import src.banking.models  # noqa: F401
    import src.entity.models  # noqa: F401
    import src.tax.models  # noqa: F401
    import src.rates.models  # noqa: F401
    import src.investment_company.models  # noqa: F401
    import src.fund.models  # noqa: F401

    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Cleanup: drop the test database
    engine.dispose()
    drop_test_database(test_database_name)


@pytest.fixture(scope="session")
def SessionFactory(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def _seed_random():
    random.seed(1337)
    try:
        import numpy as np  # type: ignore
        np.random.seed(1337)
    except Exception:
        pass


@pytest.fixture()
def db_session(SessionFactory):
    Session = scoped_session(SessionFactory)
    session = Session()
    
    try:
        yield session
    finally:
        # Rollback all changes
        try:
            session.rollback()
        except Exception:
            pass  # Session might be in invalid state
        
        # Close the session
        session.close()
        Session.remove()


@pytest.fixture(autouse=True)
def clean_database(SessionFactory):
    """Clean the database before each test using PostgreSQL transaction rollback"""
    # Create a separate session for cleaning
    Session = scoped_session(SessionFactory)
    session = Session()
    
    try:
        # Get all table names
        from sqlalchemy import inspect
        inspector = inspect(session.bind)
        table_names = inspector.get_table_names()
        
        # Clear all tables except risk_free_rates (reference data)
        # Include ALL tables that might contain test data
        tables_to_clear = [
            'tax_statements', 
            'fund_events', 
            'funds', 
            'entities', 
            'investment_companies',
            'bank_accounts',  # Add banking tables
            'banks',
            'fund_event_cash_flows'  # Add cash flow tables
        ]
        
        for table_name in tables_to_clear:
            if table_name in table_names:
                try:
                    session.execute(text(f"TRUNCATE TABLE {table_name} RESTART IDENTITY CASCADE"))
                    print(f"Cleared table: {table_name}")
                except Exception as e:
                    print(f"Warning: Could not clear table {table_name}: {e}")
        
        # Commit the cleanup
        session.commit()
    finally:
        session.close()
        Session.remove()


@pytest.fixture(scope="session")
def app(engine):
    # Create test database URL for the API
    db_url = str(engine.url)
    
    app = create_app(db_config={'database_url': db_url})
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture()
def client(app, db_session):
    """Test client with database session injected into app context"""
    with app.test_client() as test_client:
        # Inject the test session into the app context
        app.config['TEST_DB_SESSION'] = db_session
        yield test_client


@pytest.fixture(autouse=True)
def setup_factories(db_session):
    """Automatically set the database session for all factories before each test"""
    from tests.factories import set_session
    set_session(db_session)
    yield
    # No need to manually rollback - nested transaction handles it automatically


@pytest.fixture(autouse=True)
def cleanup_event_bus():
    """
    Clean up event bus between tests to prevent hanging.
    
    This fixture ensures that event handler subscriptions don't accumulate
    across tests, which can cause memory leaks and resource conflicts.
    """
    yield
    try:
        from src.fund.events.consumption.event_bus import event_bus
        event_bus.clear_subscriptions()
        print("✅ Event bus subscriptions cleared")
    except Exception as e:
        print(f"⚠️ Warning: Could not clear event bus subscriptions: {e}")


class BaseTestCase:
    """Base test class that provides database session access"""
    
    @pytest.fixture(autouse=True)
    def setup_session(self, db_session):
        """Automatically inject database session into test methods"""
        self.db_session = db_session
        yield


