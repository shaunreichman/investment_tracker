"""
Shared utilities module.

This module contains shared utility functions and decorators used across domains.
"""

from functools import wraps
from sqlalchemy.orm import Session


def with_session(func):
    """
    Decorator to automatically handle database session for functions that need one.
    
    This decorator can be used in two ways:
    1. If the function already has a session parameter, it will use that session.
    2. If the function doesn't have a session parameter, it will create a new session.
    
    Usage:
        @with_session
        def my_function(session, arg1, arg2):
            # Use session here
            pass
        
        @with_session
        def my_function(arg1, arg2):
            # Session will be automatically created and passed
            pass
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Check if session is already provided
        session = None
        if args and isinstance(args[0], Session):
            session = args[0]
            # Remove session from args
            args = args[1:]
        elif 'session' in kwargs:
            session = kwargs.pop('session')
        
        if session is None:
            # Create new session
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            
            engine = create_engine('sqlite:///data/investment_tracker.db')
            SessionLocal = sessionmaker(bind=engine)
            session = SessionLocal()
            
            try:
                result = func(session, *args, **kwargs)
                session.commit()
                return result
            except Exception:
                session.rollback()
                raise
            finally:
                session.close()
        else:
            # Use provided session
            return func(session, *args, **kwargs)
    
    return wrapper 