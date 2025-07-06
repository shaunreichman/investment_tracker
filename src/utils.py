"""
DEPRECATED - This file has been migrated to domain-driven architecture.

All utility functions have been moved to the shared module:
- with_session decorator → src/shared/utils.py

This file is kept for reference only and should not be used in new code.
All imports should use the new domain modules instead.

Migration completed: [Date]
"""

# DEPRECATED - All content below has been migrated to domain modules
# This file is kept for reference only

"""
# All utility functions have been migrated to src/shared/utils.py
# See deprecation header above for details
"""

from functools import wraps
from sqlalchemy.orm import object_session

"""
Utility functions for investment tracker.

This module provides general-purpose utilities, including decorators for session management.
"""

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