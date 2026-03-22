"""
Standardized API Response Codes.

This module provides a centralized enum for all response codes used across the API,
including success codes, error codes, and status indicators. This ensures consistency,
type safety, and maintainability across all endpoints.
"""

from enum import Enum


class ApiResponseCode(Enum):
    """
    Standardized response codes for API responses.
    
    Each response code maps to a specific outcome that can occur in the API,
    providing consistent response handling across all endpoints.
    """
    
    # === SUCCESS CODES (2xx) ===
    SUCCESS = "SUCCESS"
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    DELETED = "DELETED"
    NO_CONTENT = "NO_CONTENT"
    ACCEPTED = "ACCEPTED"
    PARTIAL_CONTENT = "PARTIAL_CONTENT"
    
    # === CLIENT ERRORS (4xx) ===
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"
    METHOD_NOT_ALLOWED = "METHOD_NOT_ALLOWED"
    CONFLICT_ERROR = "CONFLICT_ERROR"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    BAD_REQUEST = "BAD_REQUEST"
    PAYMENT_REQUIRED = "PAYMENT_REQUIRED"
    NOT_ACCEPTABLE = "NOT_ACCEPTABLE"
    REQUEST_TIMEOUT = "REQUEST_TIMEOUT"
    UNSUPPORTED_MEDIA_TYPE = "UNSUPPORTED_MEDIA_TYPE"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    REQUEST_ENTITY_TOO_LARGE = "REQUEST_ENTITY_TOO_LARGE"
    
    # === SERVER ERRORS (5xx) ===
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    DATABASE_ERROR = "DATABASE_ERROR"
    BAD_GATEWAY = "BAD_GATEWAY"
    GATEWAY_TIMEOUT = "GATEWAY_TIMEOUT"
    HTTP_VERSION_NOT_SUPPORTED = "HTTP_VERSION_NOT_SUPPORTED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    
    # === BUSINESS LOGIC ERRORS ===
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    BUSINESS_LOGIC_ERROR = "BUSINESS_LOGIC_ERROR"
    BUSINESS_RULE_VIOLATION = "BUSINESS_RULE_VIOLATION"
    INSUFFICIENT_FUNDS = "INSUFFICIENT_FUNDS"
    DUPLICATE_ENTRY = "DUPLICATE_ENTRY"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    MAINTENANCE_MODE = "MAINTENANCE_MODE"
    FEATURE_NOT_AVAILABLE = "FEATURE_NOT_AVAILABLE"
    
    def get_http_status_code(self) -> int:
        """
        Get the appropriate HTTP status code for this response code.
        
        Returns:
            HTTP status code
        """
        status_mapping = {
            # Success codes (2xx)
            ApiResponseCode.SUCCESS: 200,
            ApiResponseCode.CREATED: 201,
            ApiResponseCode.UPDATED: 200,
            ApiResponseCode.DELETED: 204,
            ApiResponseCode.NO_CONTENT: 204,
            ApiResponseCode.ACCEPTED: 202,
            ApiResponseCode.PARTIAL_CONTENT: 206,
            
            # Client errors (4xx)
            ApiResponseCode.VALIDATION_ERROR: 400,
            ApiResponseCode.BAD_REQUEST: 400,
            ApiResponseCode.UNAUTHORIZED: 401,
            ApiResponseCode.AUTHENTICATION_ERROR: 401,
            ApiResponseCode.PAYMENT_REQUIRED: 402,
            ApiResponseCode.FORBIDDEN: 403,
            ApiResponseCode.AUTHORIZATION_ERROR: 403,
            ApiResponseCode.RESOURCE_NOT_FOUND: 404,
            ApiResponseCode.METHOD_NOT_ALLOWED: 405,
            ApiResponseCode.NOT_ACCEPTABLE: 406,
            ApiResponseCode.CONFLICT_ERROR: 409,
            ApiResponseCode.REQUEST_TIMEOUT: 408,
            ApiResponseCode.UNSUPPORTED_MEDIA_TYPE: 415,
            ApiResponseCode.TOO_MANY_REQUESTS: 429,
            ApiResponseCode.REQUEST_ENTITY_TOO_LARGE: 413,
            
            # Server errors (5xx)
            ApiResponseCode.INTERNAL_SERVER_ERROR: 500,
            ApiResponseCode.DATABASE_ERROR: 500,
            ApiResponseCode.NOT_IMPLEMENTED: 501,
            ApiResponseCode.BAD_GATEWAY: 502,
            ApiResponseCode.SERVICE_UNAVAILABLE: 503,
            ApiResponseCode.GATEWAY_TIMEOUT: 504,
            ApiResponseCode.HTTP_VERSION_NOT_SUPPORTED: 505,
            
            # Business logic
            ApiResponseCode.BUSINESS_RULE_VIOLATION: 400,
            ApiResponseCode.BUSINESS_LOGIC_ERROR: 400,
            ApiResponseCode.INSUFFICIENT_FUNDS: 400,
            ApiResponseCode.DUPLICATE_ENTRY: 409,
            ApiResponseCode.RATE_LIMIT_EXCEEDED: 429,
            ApiResponseCode.MAINTENANCE_MODE: 503,
            ApiResponseCode.FEATURE_NOT_AVAILABLE: 501,
        }
        
        return status_mapping.get(self, 500)  # Default to 500 for unknown codes
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the response code.
        
        Returns:
            Description string
        """
        descriptions = {
            # Success codes
            ApiResponseCode.SUCCESS: "Operation completed successfully",
            ApiResponseCode.CREATED: "Resource created successfully",
            ApiResponseCode.UPDATED: "Resource updated successfully",
            ApiResponseCode.DELETED: "Resource deleted successfully",
            ApiResponseCode.NO_CONTENT: "Operation completed with no content to return",
            ApiResponseCode.ACCEPTED: "Request accepted for processing",
            ApiResponseCode.PARTIAL_CONTENT: "Partial content returned successfully",
            
            # Client errors
            ApiResponseCode.VALIDATION_ERROR: "Request validation failed",
            ApiResponseCode.RESOURCE_NOT_FOUND: "The requested resource was not found",
            ApiResponseCode.METHOD_NOT_ALLOWED: "HTTP method not allowed for this endpoint",
            ApiResponseCode.CONFLICT_ERROR: "Resource conflict occurred",
            ApiResponseCode.UNAUTHORIZED: "Authentication required",
            ApiResponseCode.FORBIDDEN: "Insufficient permissions",
            ApiResponseCode.BAD_REQUEST: "Invalid request format or parameters",
            ApiResponseCode.PAYMENT_REQUIRED: "Payment required to access this resource",
            ApiResponseCode.NOT_ACCEPTABLE: "Requested content type not acceptable",
            ApiResponseCode.REQUEST_TIMEOUT: "Request timed out",
            ApiResponseCode.UNSUPPORTED_MEDIA_TYPE: "Unsupported media type",
            ApiResponseCode.TOO_MANY_REQUESTS: "Too many requests, rate limit exceeded",
            ApiResponseCode.REQUEST_ENTITY_TOO_LARGE: "Request entity too large",
            
            # Server errors
            ApiResponseCode.INTERNAL_SERVER_ERROR: "Internal server error occurred",
            ApiResponseCode.DATABASE_ERROR: "Database operation failed",
            ApiResponseCode.SERVICE_UNAVAILABLE: "Service temporarily unavailable",
            ApiResponseCode.BAD_GATEWAY: "Bad gateway error",
            ApiResponseCode.GATEWAY_TIMEOUT: "Gateway timeout",
            ApiResponseCode.HTTP_VERSION_NOT_SUPPORTED: "HTTP version not supported",
            ApiResponseCode.NOT_IMPLEMENTED: "Feature not implemented",
            
            # Business logic
            ApiResponseCode.AUTHENTICATION_ERROR: "Authentication failed",
            ApiResponseCode.AUTHORIZATION_ERROR: "Access denied",
            ApiResponseCode.BUSINESS_LOGIC_ERROR: "Business logic error",
            ApiResponseCode.BUSINESS_RULE_VIOLATION: "Business rule violation",
            ApiResponseCode.INSUFFICIENT_FUNDS: "Insufficient funds for operation",
            ApiResponseCode.DUPLICATE_ENTRY: "Duplicate entry detected",
            ApiResponseCode.RATE_LIMIT_EXCEEDED: "Rate limit exceeded",
            ApiResponseCode.MAINTENANCE_MODE: "System is in maintenance mode",
            ApiResponseCode.FEATURE_NOT_AVAILABLE: "Feature is not available",
        }
        
        return descriptions.get(self, "Unknown response occurred")
