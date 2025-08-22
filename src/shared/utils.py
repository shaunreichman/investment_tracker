"""
Shared Utilities.

This module provides utility functions and decorators used across the system,
including session management and common database operations.
"""

from typing import Callable, Any, Optional, TypeVar, ParamSpec
from functools import wraps
from sqlalchemy.orm import Session, scoped_session, sessionmaker, object_session
from contextlib import contextmanager

from src.shared.base import Base

def get_database_session():
    """Import and return get_database_session to avoid circular imports"""
    from database import get_database_session as _get_database_session
    return _get_database_session()

def with_session(method):
    """
    Decorator for model methods that require a SQLAlchemy session.
    Ensures the session argument is set, using object_session(self) if not provided.
    
    Usage:
        - Apply to instance methods that accept a 'session' keyword argument.
        - If 'session' is not provided, attempts to resolve it from the SQLAlchemy object session.
        - Raises RuntimeError if no session is available.
    
    Best practices:
        - Use for methods that may be called both inside and outside explicit session contexts.
        - Avoid using for static or class methods.
    
    Args:
        method (callable): The instance method to wrap.
    
    Returns:
        callable: The wrapped method with session resolution logic.
    """
    @wraps(method)
    def wrapper(self, *args, session=None, **kwargs):
        resolved_session = session or object_session(self)
        if resolved_session is None:
            raise RuntimeError(f"No SQLAlchemy session found for {self.__class__.__name__}.{method.__name__}")
        return method(self, *args, session=resolved_session, **kwargs)
    return wrapper


def with_class_session(method):
    """
    Decorator for class methods that require a SQLAlchemy session.
    Creates a new database session if one is not provided.
    
    Usage:
        - Apply to class methods that accept a 'session' keyword argument.
        - If 'session' is not provided, creates a new session from the database.
        - Automatically commits changes and closes the session.
    
    Args:
        method (callable): The class method to wrap.
    
    Returns:
        callable: The wrapped method with session management.
    """
    @wraps(method)
    def wrapper(cls, *args, session=None, **kwargs):
        # If no session provided, create one
        if session is None:
            engine, session_factory, scoped_session = get_database_session()
            session = scoped_session()
            auto_commit = True
        else:
            auto_commit = False
        
        try:
            # Call the original method
            result = method(cls, *args, session=session, **kwargs)
            
            # Auto-commit if we created the session
            if auto_commit:
                session.commit()
            
            return result
        except Exception:
            # Rollback on error if we created the session
            if auto_commit:
                session.rollback()
            raise
        finally:
            # Close the session if we created it
            if auto_commit:
                session.close()
    
    return wrapper


def with_database_session(func):
    """
    Decorator for standalone functions that require a database session.
    Creates a new database session if one is not provided.
    
    Usage:
        - Apply to standalone functions that accept a 'session' keyword argument.
        - If 'session' is not provided, creates a new session from the database.
        - Automatically commits changes and closes the session.
    
    Args:
        func (callable): The standalone function to wrap.
    
    Returns:
        callable: The wrapped function with session management.
    """
    @wraps(func)
    def wrapper(*args, session=None, **kwargs):
        # If no session provided, create one
        if session is None:
            engine, session_factory, scoped_session = get_database_session()
            session = scoped_session()
            auto_commit = True
        else:
            auto_commit = False
        
        try:
            # Call the original function
            result = func(*args, session=session, **kwargs)
            
            # Auto-commit if we created the session
            if auto_commit:
                session.commit()
            
            return result
        except Exception:
            # Rollback on error if we created the session
            if auto_commit:
                session.rollback()
            raise
        finally:
            # Close the session if we created it
            if auto_commit:
                session.close()
    
    return wrapper


def reset_database_for_testing(session):
    """
    Domain-level utility to reset the database for testing.
    Drops all tables and recreates them with the current schema.
    
    This function follows the principle that all database operations
    are handled by the core system, not by clients.
    
    Args:
        session (Session): Database session (required - managed by outermost backend layer)
    
    Returns:
        bool: True if reset was successful
    """
    from sqlalchemy import text
    
    # Get the engine from the session
    engine = session.bind
    
    # Drop all tables
    Base.metadata.drop_all(engine)
    
    # Recreate all tables
    Base.metadata.create_all(engine)
    
    return True


__all__ = [
    'with_session',
    'with_class_session',
    'with_database_session',
    'reset_database_for_testing',
] 