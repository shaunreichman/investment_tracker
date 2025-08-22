"""
Entity API Routes.

This module contains all entity-related API endpoints including
entity management and CRUD operations.

All endpoints use middleware validation for input data.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers.entity_controller import EntityController
from src.api.database import get_db_session
from src.api.middleware.validation import validate_entity_data

# Create blueprint for entity routes
entity_bp = Blueprint('entity', __name__)

# Initialize controller
entity_controller = EntityController()


@entity_bp.route('/api/entities', methods=['GET'])
def get_entities():
    """Get list of all entities with summary data"""
    try:
        session = get_db_session()
        try:
            return entity_controller.get_entities(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@entity_bp.route('/api/entities', methods=['POST'])
@validate_entity_data
def create_entity():
    """Create a new entity using domain methods"""
    try:
        session = get_db_session()
        try:
            return entity_controller.create_entity(session)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@entity_bp.route('/api/entities/<int:entity_id>', methods=['GET'])
def get_entity(entity_id):
    """Get a specific entity by ID"""
    try:
        session = get_db_session()
        try:
            return entity_controller.get_entity(session, entity_id)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@entity_bp.route('/api/entities/<int:entity_id>', methods=['PUT'])
@validate_entity_data
def update_entity(entity_id):
    """Update an existing entity"""
    try:
        session = get_db_session()
        try:
            return entity_controller.update_entity(session, entity_id)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@entity_bp.route('/api/entities/<int:entity_id>', methods=['DELETE'])
def delete_entity(entity_id):
    """Delete an entity"""
    try:
        session = get_db_session()
        try:
            return entity_controller.delete_entity(session, entity_id)
        finally:
            session.close()
    except Exception as e:
        return jsonify({"error": str(e)}), 500
