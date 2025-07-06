from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
import os
from .shared.base import Base


def create_database_engine(database_url=None):
    """
    Create a SQLAlchemy engine for the database.
    
    Args:
        database_url (str): Database URL. If None, uses SQLite in the data directory.
    
    Returns:
        sqlalchemy.engine.Engine: The database engine
    """
    if database_url is None:
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Use SQLite database in the data directory
        db_path = os.path.join(data_dir, 'investment_tracker.db')
        database_url = f"sqlite:///{db_path}"
    
    # Create engine with appropriate configuration
    engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL query logging
        poolclass=StaticPool,
        connect_args={"check_same_thread": False} if "sqlite" in database_url else {}
    )
    
    return engine


def create_session_factory(engine):
    """
    Create a session factory for database operations.
    
    Args:
        engine: SQLAlchemy engine
    
    Returns:
        sqlalchemy.orm.sessionmaker: Session factory
    """
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_scoped_session(session_factory):
    """
    Create a scoped session for thread-safe database operations.
    
    Args:
        session_factory: SQLAlchemy session factory
    
    Returns:
        sqlalchemy.orm.scoped_session: Scoped session
    """
    return scoped_session(session_factory)


def init_database(engine=None, database_url=None):
    """
    Initialize the database by creating all tables.
    
    Args:
        engine: SQLAlchemy engine (optional, will create one if not provided)
        database_url (str): Database URL (optional, used if engine is not provided)
    
    Returns:
        sqlalchemy.engine.Engine: The database engine
    """
    if engine is None:
        engine = create_database_engine(database_url)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print(f"Database initialized successfully!")
    print(f"Database URL: {engine.url}")
    
    return engine


def get_database_session(engine=None, database_url=None):
    """
    Get a database session for performing operations.
    
    Args:
        engine: SQLAlchemy engine (optional, will create one if not provided)
        database_url (str): Database URL (optional, used if engine is not provided)
    
    Returns:
        tuple: (engine, session_factory, scoped_session)
    """
    if engine is None:
        engine = create_database_engine(database_url)
    
    session_factory = create_session_factory(engine)
    scoped_session = create_scoped_session(session_factory)
    
    return engine, session_factory, scoped_session


# Global variables for easy access
_engine = None
_session_factory = None
_scoped_session = None


def get_global_session():
    """
    Get the global database session. Initialize if not already done.
    
    Returns:
        sqlalchemy.orm.scoped_session: Global scoped session
    """
    global _engine, _session_factory, _scoped_session
    
    # Lazily initialize the global session on first use
    if _scoped_session is None:
        _engine, _session_factory, _scoped_session = get_database_session()
    
    return _scoped_session


def close_global_session():
    """Close the global database session and clean up resources."""
    global _scoped_session
    
    if _scoped_session is not None:
        _scoped_session.remove()
        _scoped_session = None 