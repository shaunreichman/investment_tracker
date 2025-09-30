"""
Entity API Routes.

This module contains all entity-related API endpoints including
entity management and CRUD operations.

All endpoints use middleware validation for input data.
All endpoints use the entity controller with DTO responses.
"""

from flask import Blueprint, jsonify
from src.api.controllers.entity_controller import EntityController
from src.api.dto.api_response import ApiResponse
from src.api.dto.response_codes import ApiResponseCode
from src.api.middleware.response_handlers import handle_controller_response, handle_delete_response
from src.api.middleware.validation.base_validation import validate_request
from src.shared.enums.shared_enums import Country
from src.entity.enums.entity_enums import EntityType


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
@validate_request(
    field_types={
        'name': 'string',
        'entity_type': 'string',
        'tax_jurisdiction': 'string'
    },
    field_lengths={'name': {'max': 255}},
    enum_fields={
        'entity_type': EntityType,
        'tax_jurisdiction': Country
    },
    sanitize=True
)
def get_entities():
    """
    Get list of all entities with summary data
    
    Query Parameters (all optional):
        name (str): Filter by entity name
        entity_type (str): Filter by entity type (INDIVIDUAL, COMPANY, etc.)
        tax_jurisdiction (str): Filter by tax jurisdiction (US, UK, etc.)
    
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
@validate_request(
    required_fields=['name', 'entity_type', 'tax_jurisdiction'],
    field_types={
        'name': 'string',
        'entity_type': 'string',
        'description': 'string',
        'tax_jurisdiction': 'string'
    },
    field_lengths={
        'name': {'min': 2, 'max': 255},
        'entity_type': {'max': 255},
        'description': {'max': 1000},
        'tax_jurisdiction': {'min': 2, 'max': 255}
    },
    enum_fields={
        'entity_type': EntityType,
        'tax_jurisdiction': Country
    },
    sanitize=True
)
def create_entity():
    """
    Create a new entity using domain methods

    Request Body:
        name (str): Entity name (required)
        entity_type (str): Entity type (optional)
        description (str): Entity description (optional)
        tax_jurisdiction (str): Entity tax jurisdiction (required)
    
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
