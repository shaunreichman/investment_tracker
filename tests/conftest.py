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
        session.rollback()
    finally:
        session.close()
        Session.remove()


@pytest.fixture(scope="session")
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
    })
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


