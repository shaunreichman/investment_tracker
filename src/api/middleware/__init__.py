"""
API Middleware Package.

This package contains middleware components for the API including:
- Request validation
- Error handling
- Logging and monitoring
- Database session management
- Response handling
"""

from src.api.middleware.validation import validate_request, ValidationError
from src.api.middleware.error_handling import setup_error_handlers
from src.api.middleware.logging import setup_logging_middleware
from src.api.middleware.database_session import setup_database_session_middleware
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response

__all__ = [
    'validate_request',
    'ValidationError', 
    'setup_error_handlers',
    'setup_logging_middleware',
    'setup_database_session_middleware',
    'handle_controller_response',
    'handle_delete_response',
]