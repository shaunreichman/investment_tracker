"""
Entity API Routes.

This module contains all entity-related API endpoints including
entity management and CRUD operations.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint, jsonify
from src.api.controllers.entity_controller import EntityController
from src.api.middleware.validation import validate_entity_data
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response


# Create blueprint for entity routes
entity_bp = Blueprint('entity', __name__)

# Initialize controller
entity_controller = EntityController()

###############################################################
# ENTITY ENDPOINTS
###############################################################

###############################################
# Get entities
###############################################

@entity_bp.route('/api/entities', methods=['GET'])
def get_entities():
    """
    Get list of all entities with summary data
    
    Returns:
        Standardized response with list of entities
    """
    try:
        dto = entity_controller.get_entities()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting entities: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


@entity_bp.route('/api/entities/<int:entity_id>', methods=['GET'])
def get_entity(entity_id):
    """
    Get a specific entity by ID
    
    Path Parameters:
        entity_id (int): ID of the entity to retrieve
        
    Returns:
        Standardized response with entity data
    """
    try:
        dto = entity_controller.get_entity(entity_id)
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error getting entity {entity_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Create entity
###############################################

@entity_bp.route('/api/entities', methods=['POST'])
@validate_entity_data
def create_entity():
    """
    Create a new entity using domain methods

    Request Body:
        name (str): Entity name (required)
        description (str): Entity description (optional)
        tax_jurisdiction (str): Entity tax jurisdiction (optional)
    
    Returns:
        Standardized response with created entity data
    """
    try:
        dto = entity_controller.create_entity()
        return handle_controller_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error creating entity: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()


###############################################
# Delete entity
###############################################

@entity_bp.route('/api/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id):
    """
    Delete an entity
    
    Path Parameters:
        entity_id (int): ID of the entity to delete
        
    Returns:
        Standardized response confirming deletion (204 No Content on success)
    """
    try:
        dto = entity_controller.delete_entity(entity_id)
        return handle_delete_response(dto)
    except Exception as e:
        response = ApiResponse(
            response_code=ApiResponseCode.INTERNAL_SERVER_ERROR,
            message=f"Unexpected error deleting entity {entity_id}: {str(e)}"
        )
        return jsonify(response.to_dict()), response.response_code.get_http_status_code()
