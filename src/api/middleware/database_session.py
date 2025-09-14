"""
Database Session Middleware.

This module provides automatic database session management for Flask requests.
Sessions are automatically created at request start and cleaned up at request end.

Key features:
- Automatic session creation and cleanup
- Proper commit/rollback handling
- Exception-safe session management
- Integration with Flask's g context
- Thread-safe session handling
"""

from flask import g, current_app
from sqlalchemy.orm import Session
from src.database import create_database_engine, create_session_factory


def setup_database_session_middleware(app):
    """
    Set up database session middleware for the Flask app.
    
    This middleware:
    1. Creates a database session at the start of each request
    2. Attaches it to Flask's g context for access throughout the request
    3. Automatically commits or rolls back the session at request end
    4. Ensures proper cleanup even on exceptions
    
    Args:
        app: Flask application instance
    """
    
    # Create session factory once at startup for efficiency
    engine = create_database_engine()
    session_factory = create_session_factory(engine)
    
    @app.before_request
    def open_session():
        """
        Create a database session for this request.
        
        The session is attached to Flask's g context so it can be accessed
        throughout the request lifecycle by controllers, services, and repositories.
        """
        try:
            g.db = session_factory()
            current_app.logger.debug("Database session created for request")
        except Exception as e:
            current_app.logger.error(f"Failed to create database session: {e}")
            raise
    
    @app.teardown_request
    def close_session(exception=None):
        """
        Clean up database session after request completion.
        
        Args:
            exception: Exception that occurred during request processing, if any
        """
        db: Session = g.pop("db", None)
        if db is None:
            return
        
        try:
            if exception is None:
                # No exception occurred, commit the transaction
                db.commit()
                current_app.logger.debug("Database session committed successfully")
            else:
                # Exception occurred, rollback the transaction
                db.rollback()
                current_app.logger.warning(f"Database session rolled back due to exception: {exception}")
        except Exception as e:
            # Log any errors during commit/rollback but don't raise
            current_app.logger.error(f"Error during session cleanup: {e}")
        finally:
            # Always close the session
            try:
                db.close()
                current_app.logger.debug("Database session closed")
            except Exception as e:
                current_app.logger.error(f"Error closing database session: {e}")


def get_current_session() -> Session:
    """
    Get the current database session from Flask's g context.
    
    This is a convenience function for accessing the session that was
    created by the middleware. Use this instead of creating sessions manually.
    
    Returns:
        Session: The current database session
        
    Raises:
        RuntimeError: If no session is available in the current context
    """
    if not hasattr(g, 'db') or g.db is None:
        raise RuntimeError(
            "No database session available. Make sure database session middleware is enabled."
        )
    return g.db
