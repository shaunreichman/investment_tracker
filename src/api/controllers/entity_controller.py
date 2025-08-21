"""
Entity API Controller.

This controller handles HTTP requests for entity operations,
providing RESTful endpoints for entity management.

Key responsibilities:
- Entity CRUD endpoints
- Entity validation and error handling
- Input sanitization and type validation
"""

from typing import List, Optional, Dict, Any
from flask import request, jsonify, current_app
from sqlalchemy.orm import Session

from src.entity.models import Entity


class EntityController:
    """
    Controller for entity operations.
    
    This controller handles HTTP requests and provides REST API endpoints
    for entity operations. It delegates business logic to the domain
    models and handles request/response formatting.
    
    Attributes:
        None - Direct domain model usage for simplicity
    """
    
    def __init__(self):
        """Initialize the entity controller."""
        pass
    
    def get_entities(self, session: Session) -> tuple:
        """
        Get all entities with summary data.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get all entities using domain methods
            entities = Entity.get_all(session=session)
            
            # Format response data
            entities_data = []
            for entity in entities:
                entity_data = {
                    "id": entity.id,
                    "name": entity.name,
                    "entity_type": entity.entity_type.value if entity.entity_type else None,
                    "tax_id": entity.tax_id,
                    "is_active": entity.is_active,
                    "created_date": entity.created_date.isoformat() if entity.created_date else None,
                    "updated_date": entity.updated_date.isoformat() if entity.updated_date else None
                }
                entities_data.append(entity_data)
            
            return jsonify(entities_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting entities: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def create_entity(self, session: Session) -> tuple:
        """
        Create a new entity.
        
        Args:
            session: Database session
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get request data
            data = request.get_json()
            if not data:
                return jsonify({"error": "No data provided"}), 400
            
            # Validate required fields
            required_fields = ['name', 'entity_type']
            for field in required_fields:
                if field not in data or not data[field]:
                    return jsonify({"error": f"Missing required field: {field}"}), 400
            
            # Validate entity type
            valid_entity_types = ['INDIVIDUAL', 'TRUST', 'LLC', 'CORPORATION', 'PARTNERSHIP']
            if data['entity_type'] not in valid_entity_types:
                return jsonify({"error": f"Invalid entity type. Must be one of: {', '.join(valid_entity_types)}"}), 400
            
            # Create entity using domain method
            entity = Entity.create(
                name=data['name'].strip(),
                entity_type=data['entity_type'],
                tax_id=data.get('tax_id'),
                is_active=data.get('is_active', True),
                session=session
            )
            
            # Commit the transaction
            session.commit()
            
            # Format response data
            response_data = {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type.value if entity.entity_type else None,
                "tax_id": entity.tax_id,
                "is_active": entity.is_active,
                "created_date": entity.created_date.isoformat() if entity.created_date else None,
                "updated_date": entity.updated_date.isoformat() if entity.updated_date else None,
                "message": "Entity created successfully"
            }
            
            return jsonify(response_data), 201
            
        except ValueError as e:
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            current_app.logger.error(f"Error creating entity: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
