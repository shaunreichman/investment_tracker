"""
Logging Middleware.

This module provides comprehensive logging including:
- Request/response logging with correlation IDs
- Performance timing for endpoints
- Structured logging for debugging and monitoring
- Log level configuration
"""

import time
import uuid
import json
from typing import Dict, Any, Optional, Callable
from functools import wraps
from flask import Flask, request, current_app, g
from datetime import datetime


class RequestLogger:
    """
    Request logging engine.
    
    Provides methods for logging request/response information
    and performance metrics.
    """
    
    def __init__(self):
        """Initialize the logger."""
        pass
    
    def generate_request_id(self) -> str:
        """
        Generate a unique request ID.
        
        Returns:
            Unique request identifier
        """
        return str(uuid.uuid4())
    
    def log_request_start(self, request_id: str) -> None:
        """
        Log the start of a request.
        
        Args:
            request_id: Unique request identifier
        """
        if not current_app:
            return
        
        log_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": request.url,
            "endpoint": request.endpoint,
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr,
            "content_type": request.content_type,
            "content_length": request.content_length,
            "event": "request_start"
        }
        
        current_app.logger.info("Request started", extra=log_data)
    
    def log_request_end(self, request_id: str, status_code: int, response_time: float, 
                       response_size: Optional[int] = None) -> None:
        """
        Log the end of a request.
        
        Args:
            request_id: Unique request identifier
            status_code: HTTP response status code
            response_time: Response time in seconds
            response_size: Optional response size in bytes
        """
        if not current_app:
            return
        
        log_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": request.url,
            "endpoint": request.endpoint,
            "status_code": status_code,
            "response_time": response_time,
            "response_time_ms": round(response_time * 1000, 2),
            "event": "request_end"
        }
        
        if response_size:
            log_data["response_size"] = response_size
        
        # Log level based on status code
        if status_code >= 500:
            current_app.logger.error("Request completed with server error", extra=log_data)
        elif status_code >= 400:
            current_app.logger.warning("Request completed with client error", extra=log_data)
        else:
            current_app.logger.info("Request completed successfully", extra=log_data)
    
    def log_request_error(self, request_id: str, error: Exception, response_time: float) -> None:
        """
        Log request errors.
        
        Args:
            request_id: Unique request identifier
            error: The exception that occurred
            response_time: Response time in seconds
        """
        if not current_app:
            return
        
        log_data = {
            "request_id": request_id,
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "url": request.url,
            "endpoint": request.endpoint,
            "error_type": type(error).__name__,
            "error_message": str(error),
            "response_time": response_time,
            "response_time_ms": round(response_time * 1000, 2),
            "event": "request_error"
        }
        
        current_app.logger.error("Request failed", extra=log_data)
    
    def get_request_context(self) -> Dict[str, Any]:
        """
        Get current request context for logging.
        
        Returns:
            Dictionary containing request context information
        """
        if not request:
            return {}
        
        return {
            "request_id": getattr(g, 'request_id', None),
            "method": request.method,
            "url": request.url,
            "endpoint": request.endpoint,
            "user_agent": request.headers.get('User-Agent'),
            "ip": request.remote_addr,
            "content_type": request.content_type,
            "content_length": request.content_length
        }


def setup_logging_middleware(app: Flask) -> None:
    """
    Set up logging middleware for the Flask application.
    
    Args:
        app: Flask application instance
    """
    
    @app.before_request
    def before_request():
        """Log request start and generate request ID."""
        # Generate unique request ID
        g.request_id = RequestLogger().generate_request_id()
        
        # Store start time
        g.start_time = time.time()
        
        # Log request start
        logger = RequestLogger()
        logger.log_request_start(g.request_id)
    
    @app.after_request
    def after_request(response_obj):
        """Log request completion and performance metrics."""
        # Calculate response time
        start_time = getattr(g, 'start_time', time.time())
        response_time = time.time() - start_time
        
        # Get request ID
        request_id = getattr(g, 'request_id', 'unknown')
        
        # Log request completion
        logger = RequestLogger()
        logger.log_request_end(
            request_id=request_id,
            status_code=response_obj.status_code,
            response_time=response_time,
            response_size=len(response_obj.get_data()) if response_obj.get_data() else None
        )
        
        # Add request ID to response headers for client tracking
        response_obj.headers['X-Request-ID'] = request_id
        response_obj.headers['X-Response-Time'] = f"{response_time:.3f}s"
        
        return response_obj
    
    @app.teardown_request
    def teardown_request(exception):
        """Log request errors if they occur."""
        if exception:
            start_time = getattr(g, 'start_time', time.time())
            response_time = time.time() - start_time
            request_id = getattr(g, 'request_id', 'unknown')
            
            logger = RequestLogger()
            logger.log_request_error(request_id, exception, response_time)


def log_performance(func: Callable) -> Callable:
    """
    Decorator for logging function performance.
    
    Args:
        func: Function to wrap with performance logging
        
    Returns:
        Decorated function with performance logging
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            response_time = time.time() - start_time
            
            if current_app:
                current_app.logger.debug(
                    f"Function {func.__name__} completed in {response_time:.3f}s",
                    extra={
                        "function": func.__name__,
                        "response_time": response_time,
                        "response_time_ms": round(response_time * 1000, 2),
                        "event": "function_performance"
                    }
                )
            
            return result
            
        except Exception as e:
            response_time = time.time() - start_time
            
            if current_app:
                current_app.logger.error(
                    f"Function {func.__name__} failed after {response_time:.3f}s: {str(e)}",
                    extra={
                        "function": func.__name__,
                        "response_time": response_time,
                        "response_time_ms": round(response_time * 1000, 2),
                        "error": str(e),
                        "event": "function_error"
                    }
                )
            
            raise
    
    return wrapper


def log_business_operation(operation: str, details: Dict[str, Any] = None) -> Callable:
    """
    Decorator for logging business operations.
    
    Args:
        operation: Name of the business operation
        details: Additional details to log
        
    Returns:
        Decorated function with business operation logging
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log operation start
            if current_app:
                current_app.logger.info(
                    f"Business operation started: {operation}",
                    extra={
                        "operation": operation,
                        "function": func.__name__,
                        "timestamp": datetime.utcnow().isoformat(),
                        "details": details or {},
                        "event": "business_operation_start"
                    }
                )
            
            try:
                result = func(*args, **kwargs)
                response_time = time.time() - start_time
                
                # Log operation success
                if current_app:
                    current_app.logger.info(
                        f"Business operation completed: {operation}",
                        extra={
                            "operation": operation,
                            "function": func.__name__,
                            "response_time": response_time,
                            "response_time_ms": round(response_time * 1000, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "details": details or {},
                            "event": "business_operation_success"
                        }
                    )
                
                return result
                
            except Exception as e:
                response_time = time.time() - start_time
                
                # Log operation failure
                if current_app:
                    current_app.logger.error(
                        f"Business operation failed: {operation}",
                        extra={
                            "operation": operation,
                            "function": func.__name__,
                            "response_time": response_time,
                            "response_time_ms": round(response_time * 1000, 2),
                            "timestamp": datetime.utcnow().isoformat(),
                            "details": details or {},
                            "error": str(e),
                            "event": "business_operation_failure"
                        }
                    )
                
                raise
        
        return wrapper
    return decorator


def get_request_logger() -> RequestLogger:
    """
    Get the current request logger instance.
    
    Returns:
        RequestLogger instance
    """
    return RequestLogger()
