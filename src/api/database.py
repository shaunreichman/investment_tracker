"""
Database session management for API operations.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from src.database import create_database_engine


def get_db_session(db_config=None):
    """
    Get a database session.
    
    Args:
        db_config: Optional database configuration
        
    Returns:
        Database session
    """
    if db_config and 'database_url' in db_config:
        # Use test database if configured
        engine = create_engine(db_config['database_url'])
    else:
        # Use centralized PostgreSQL database by default
        engine = create_database_engine()
    
    Session = sessionmaker(bind=engine)
    return scoped_session(Session)
