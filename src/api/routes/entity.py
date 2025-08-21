"""
Entity API Routes.

This module contains all entity-related API endpoints including
entity management and CRUD operations.
"""

from flask import Blueprint, jsonify, request
from src.api.controllers import EntityController
from src.api.database import get_db_session

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
