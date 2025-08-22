"""
Error Handling Middleware.

This module provides centralized error handling including:
- Global exception handlers for common errors
- Structured error logging with request context
- Consistent error response format
- Custom exception classes for business logic
"""

import traceback
from typing import Dict, Any, Optional, Union
from flask import Flask, jsonify, request, current_app
from werkzeug.exceptions import HTTPException


class BusinessLogicError(Exception):
    """Custom exception for business logic errors."""
    
    def __init__(self, message: str, error_code: str = None, status_code: int = 400, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ResourceNotFoundError(BusinessLogicError):
    """Exception for when a requested resource is not found."""
    
    def __init__(self, resource_type: str, resource_id: str, message: str = None):
        self.resource_type = resource_type
        self.resource_id = resource_id
        super().__init__(
            message or f"{resource_type} with id {resource_id} not found",
            error_code="RESOURCE_NOT_FOUND",
            status_code=404,
            details={"resource_type": resource_type, "resource_id": resource_id}
        )


class ValidationError(BusinessLogicError):
    """Exception for validation errors."""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message,
            error_code="VALIDATION_ERROR",
            status_code=400,
            details={"field": field, **details} if details else {"field": field}
        )


class ConflictError(BusinessLogicError):
    """Exception for resource conflicts."""
    
    def __init__(self, message: str, resource_type: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message,
            error_code="CONFLICT_ERROR",
            status_code=409,
            details={"resource_type": resource_type, **details} if details else {"resource_type": resource_type}
        )


class AuthenticationError(BusinessLogicError):
    """Exception for authentication errors."""
    
    def __init__(self, message: str = "Authentication required", details: Dict[str, Any] = None):
        super().__init__(
            message,
            error_code="AUTHENTICATION_ERROR",
            status_code=401,
            details=details
        )


class AuthorizationError(BusinessLogicError):
    """Exception for authorization errors."""
    
    def __init__(self, message: str = "Insufficient permissions", details: Dict[str, Any] = None):
        super().__init__(
            message,
            error_code="AUTHORIZATION_ERROR",
            status_code=403,
            details=details
        )


def create_error_response(
    message: str,
    error_code: str = None,
    status_code: int = 500,
    details: Dict[str, Any] = None,
    request_id: str = None
) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message: Error message
        error_code: Optional error code for client handling
        status_code: HTTP status code
        details: Additional error details
        request_id: Optional request ID for tracking
        
    Returns:
        Tuple of (response_data, status_code)
    """
    error_response = {
        "error": message,
        "type": "error",
        "status_code": status_code
    }
    
    if error_code:
        error_response["error_code"] = error_code
    
    if details:
        error_response["details"] = details
    
    if request_id:
        error_response["request_id"] = request_id
    
    return jsonify(error_response), status_code


def log_error(error: Exception, request_context: Dict[str, Any] = None) -> None:
    """
    Log error with structured context information.
    
    Args:
        error: The exception that occurred
        request_context: Additional request context information
    """
    if not current_app:
        return
    
    error_info = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    if request_context:
        error_info.update(request_context)
    
    if isinstance(error, BusinessLogicError):
        current_app.logger.warning(f"Business logic error: {error.message}", extra=error_info)
    else:
        current_app.logger.error(f"Unexpected error: {str(error)}", extra=error_info)


def setup_error_handlers(app: Flask) -> None:
    """
    Set up global error handlers for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(BusinessLogicError)
    def handle_business_logic_error(error: BusinessLogicError):
        """Handle business logic errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr
        })
        
        return create_error_response(
            message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details
        )
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        """Handle validation errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "field": error.details.get('field') if error.details else None
        })
        
        return create_error_response(
            message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details
        )
    
    @app.errorhandler(ResourceNotFoundError)
    def handle_resource_not_found_error(error: ResourceNotFoundError):
        """Handle resource not found errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "resource_type": error.resource_type,
            "resource_id": error.resource_id
        })
        
        return create_error_response(
            message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details
        )
    
    @app.errorhandler(ConflictError)
    def handle_conflict_error(error: ConflictError):
        """Handle conflict errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "resource_type": error.details.get('resource_type') if error.details else None
        })
        
        return create_error_response(
            message=error.message,
            error_code=error.error_code,
            status_code=error.status_code,
            details=error.details
        )
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error: HTTPException):
        """Handle HTTP exceptions."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "status_code": error.code
        })
        
        return create_error_response(
            message=error.description or "HTTP error occurred",
            status_code=error.code
        )
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        """Handle all other exceptions."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url,
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr
        })
        
        # Don't expose internal error details in production
        if app.debug:
            return create_error_response(
                message=str(error),
                status_code=500,
                details={"traceback": traceback.format_exc()}
            )
        else:
            return create_error_response(
                message="Internal server error",
                status_code=500
            )
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """Handle 404 errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url
        })
        
        return create_error_response(
            message="Resource not found",
            error_code="NOT_FOUND",
            status_code=404
        )
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Handle 405 errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url
        })
        
        return create_error_response(
            message="Method not allowed",
            error_code="METHOD_NOT_ALLOWED",
            status_code=405
        )
    
    @app.errorhandler(500)
    def handle_internal_server_error(error):
        """Handle 500 errors."""
        log_error(error, {
            "endpoint": request.endpoint,
            "method": request.method,
            "url": request.url
        })
        
        return create_error_response(
            message="Internal server error",
            error_code="INTERNAL_SERVER_ERROR",
            status_code=500
        )


def get_request_context() -> Dict[str, Any]:
    """
    Get current request context for logging.
    
    Returns:
        Dictionary containing request context information
    """
    if not request:
        return {}
    
    return {
        "endpoint": request.endpoint,
        "method": request.method,
        "url": request.url,
        "user_agent": request.headers.get('User-Agent'),
        "ip": request.remote_addr,
        "content_type": request.content_type,
        "content_length": request.content_length
    }
