"""
Standardized Response Handlers for API Routes.

This module provides shared response handling functions that can be used
across all API route modules to ensure consistent response formatting.

Key Functions:
- handle_controller_response(): Standard handler for most operations
- handle_delete_response(): Specialized handler for DELETE operations
"""

from flask import jsonify
from src.api.dto.api_response import ApiResponse


def handle_controller_response(dto):
    """
    Standardized handler for controller DTO responses.
    
    This function handles the conversion from ControllerResponseDTO to
    Flask HTTP responses with proper status codes and error handling.
    
    Args:
        dto: ControllerResponseDTO from controller
        
    Returns:
        Tuple of (json_response, status_code)
        
    Examples:
        # Success case
        dto = ControllerResponseDTO(data={"id": 1}, response_code=ApiResponseCode.SUCCESS)
        return handle_controller_response(dto)  # Returns 200 OK
        
        # Error case
        dto = ControllerResponseDTO(error="Not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
        return handle_controller_response(dto)  # Returns 404 Not Found
    """
    # Handle HTTP status code mapping at the API layer
    status_code = dto.response_code.get_http_status_code()
    
    if dto.error:
        # Create error response
        response = ApiResponse(
            response_code=dto.response_code,
            message=dto.error,
            data=dto.data,
            details=dto.details
        )
    else:
        # Success case - data already formatted by controller
        response = ApiResponse(
            response_code=dto.response_code,
            data=dto.data,
            message=dto.message,
            details=dto.details
        )
    
    return jsonify(response.to_dict()), status_code


def handle_delete_response(dto):
    """
    Specialized handler for DELETE operations.
    
    DELETE operations return 204 No Content on success, but still use
    ApiResponse for consistency with the rest of the API.
    
    Args:
        dto: ControllerResponseDTO from controller
        
    Returns:
        Tuple of (json_response, status_code)
        
    Examples:
        # Success case
        dto = ControllerResponseDTO(response_code=ApiResponseCode.DELETED, message="Fund deleted successfully")
        return handle_delete_response(dto)  # Returns ApiResponse with 204
        
        # Error case
        dto = ControllerResponseDTO(error="Not found", response_code=ApiResponseCode.RESOURCE_NOT_FOUND)
        return handle_delete_response(dto)  # Returns error response with 404
    """
    if dto.error:
        # Use the response code's HTTP status mapping
        status_code = dto.response_code.get_http_status_code()
        response = ApiResponse(
            response_code=dto.response_code,
            message=dto.error,
            details=dto.details
        )
        return jsonify(response.to_dict()), status_code
    else:
        # Success case - Use ApiResponse for consistency, even with 204
        status_code = dto.response_code.get_http_status_code()
        response = ApiResponse(
            response_code=dto.response_code,
            data=dto.data,
            message=dto.message or "Resource deleted successfully",
            details=dto.details
        )
        return jsonify(response.to_dict()), status_code
