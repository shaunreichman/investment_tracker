import os
import sys
from pathlib import Path
import tempfile
import shutil
import random
from typing import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Ensure project root is on sys.path so `import src.*` works
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.shared.base import Base
from src.api import create_app


@pytest.fixture(scope="session")
def _temp_db_dir() -> Generator[str, None, None]:
    tmpdir = tempfile.mkdtemp(prefix="it_db_")
    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@pytest.fixture(scope="session")
def engine(_temp_db_dir):
    db_path = os.path.join(_temp_db_dir, "test.db")
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    # Import all model modules so their tables are registered with Base
    import src.fund.models  # noqa: F401
    import src.banking.models  # noqa: F401
    import src.entity.models  # noqa: F401
    import src.tax.models  # noqa: F401
    import src.rates.models  # noqa: F401
    import src.investment_company.models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    return engine


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
    """Clean the database before each test by truncating all tables"""
    # Create a separate session for cleaning
    Session = scoped_session(SessionFactory)
    session = Session()
    
    try:
        # Get all table names
        from sqlalchemy import inspect, text
        inspector = inspect(session.bind)
        table_names = inspector.get_table_names()
        
        # Disable foreign key constraints temporarily
        session.execute(text("PRAGMA foreign_keys=OFF"))
        
        # Truncate all tables
        for table_name in table_names:
            session.execute(text(f"DELETE FROM {table_name}"))
        
        # Re-enable foreign key constraints
        session.execute(text("PRAGMA foreign_keys=ON"))
        
        # Commit the cleanup
        session.commit()
    finally:
        session.close()
        Session.remove()


@pytest.fixture(scope="session")
def app(engine):
    # Create test database URL for the API
    db_url = f"sqlite:///{engine.url.database}"
    
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


class BaseTestCase:
    """Base test class that provides database session access"""
    
    @pytest.fixture(autouse=True)
    def setup_session(self, db_session):
        """Automatically inject database session into test methods"""
        self.db_session = db_session
        yield


