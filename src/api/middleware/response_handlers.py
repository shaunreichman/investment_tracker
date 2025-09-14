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
from src.api.dto.controller_response_dto import ControllerResponseStatus


def handle_controller_response(dto, success_status_code=200):
    """
    Standardized handler for controller DTO responses.
    
    This function handles the conversion from ControllerResponseDTO to
    Flask HTTP responses with proper status codes and error handling.
    
    Args:
        dto: ControllerResponseDTO from controller
        success_status_code: HTTP status code for success (default 200)
        
    Returns:
        Tuple of (json_response, status_code)
        
    Examples:
        # Success case
        dto = ControllerResponseDTO(data={"id": 1}, status=ControllerResponseStatus.SUCCESS.value)
        return handle_controller_response(dto, 201)  # Returns 201 Created
        
        # Error case
        dto = ControllerResponseDTO(error="Not found", status=ControllerResponseStatus.NOT_FOUND.value)
        return handle_controller_response(dto)  # Returns 404 Not Found
    """
    if dto.error:
        # Use standardized status code mapping from enum
        status_code = ControllerResponseStatus.get_status_code(dto.status)
        response = ApiResponse(success=False, message=dto.error)
        return jsonify(response.to_dict()), status_code
    else:
        # Success case - data already formatted by controller
        response = ApiResponse(data=dto.data)
        return jsonify(response.to_dict()), success_status_code


def handle_delete_response(dto):
    """
    Specialized handler for DELETE operations that return 204 No Content on success.
    
    DELETE operations follow REST conventions where successful deletion
    returns 204 No Content with an empty response body.
    
    Args:
        dto: ControllerResponseDTO from controller
        
    Returns:
        Tuple of (response, status_code) or ('', 204) for success
        
    Examples:
        # Success case
        dto = ControllerResponseDTO(status=ControllerResponseStatus.SUCCESS.value)
        return handle_delete_response(dto)  # Returns ('', 204)
        
        # Error case
        dto = ControllerResponseDTO(error="Not found", status=ControllerResponseStatus.NOT_FOUND.value)
        return handle_delete_response(dto)  # Returns error response with 404
    """
    if dto.error:
        # Use standardized status code mapping from enum
        status_code = ControllerResponseStatus.get_status_code(dto.status)
        response = ApiResponse(success=False, message=dto.error)
        return jsonify(response.to_dict()), status_code
    else:
        # Success case - DELETE operations return 204 No Content
        return '', 204
