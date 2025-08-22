"""
Entity API Controller.

This controller handles HTTP requests for entity operations,
providing RESTful endpoints for entity management.

Key responsibilities:
- Entity CRUD endpoints
- Business logic delegation to domain models
- Response formatting and error handling

Note: All input validation is handled by middleware validation decorators.
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
    
    All input validation is handled by middleware validation decorators.
    
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
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get pre-validated data from middleware
            data = getattr(request, 'validated_data', {})
            if not data:
                return jsonify({"error": "No validated data available"}), 400
            
            # Create entity using domain method with validated data
            entity = Entity.create(
                name=data['name'],
                entity_type=data['entity_type'],
                tax_id=data.get('tax_id'),
                is_active=data.get('is_active', True)
            )
            
            # Commit the transaction
            session.commit()
            
            # Return created entity data
            response_data = {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type.value if entity.entity_type else None,
                "tax_id": entity.tax_id,
                "is_active": entity.is_active,
                "created_date": entity.created_date.isoformat() if entity.created_date else None,
                "updated_date": entity.updated_date.isoformat() if entity.updated_date else None
            }
            
            return jsonify(response_data), 201
            
        except Exception as e:
            current_app.logger.error(f"Error creating entity: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def get_entity(self, session: Session, entity_id: int) -> tuple:
        """
        Get an entity by ID.
        
        Args:
            session: Database session
            entity_id: ID of the entity to retrieve
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get entity using domain method
            entity = Entity.get_by_id(entity_id, session=session)
            
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Format response data
            entity_data = {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type.value if entity.entity_type else None,
                "tax_id": entity.tax_id,
                "is_active": entity.is_active,
                "created_date": entity.created_date.isoformat() if entity.created_date else None,
                "updated_date": entity.updated_date.isoformat() if entity.updated_date else None
            }
            
            return jsonify(entity_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error getting entity {entity_id}: {str(e)}")
            return jsonify({"error": "Internal server error"}), 500
    
    def update_entity(self, session: Session, entity_id: int) -> tuple:
        """
        Update an existing entity.
        
        Args:
            session: Database session
            entity_id: ID of the entity to update
            
        Returns:
            Tuple of (response_data, status_code)
            
        Note: Input data is pre-validated by middleware validation decorator.
        """
        try:
            # Get entity and validate it exists
            entity = Entity.get_by_id(entity_id, session=session)
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Get pre-validated data from middleware
            data = getattr(request, 'validated_data', {})
            if not data:
                return jsonify({"error": "No validated data available"}), 400
            
            # Update entity fields
            if 'name' in data:
                entity.name = data['name']
            if 'entity_type' in data:
                entity.entity_type = data['entity_type']
            if 'tax_id' in data:
                entity.tax_id = data['tax_id']
            if 'is_active' in data:
                entity.is_active = data['is_active']
            
            # Commit the transaction
            session.commit()
            
            # Return updated entity data
            response_data = {
                "id": entity.id,
                "name": entity.name,
                "entity_type": entity.entity_type.value if entity.entity_type else None,
                "tax_id": entity.tax_id,
                "is_active": entity.is_active,
                "created_date": entity.created_date.isoformat() if entity.created_date else None,
                "updated_date": entity.updated_date.isoformat() if entity.updated_date else None
            }
            
            return jsonify(response_data), 200
            
        except Exception as e:
            current_app.logger.error(f"Error updating entity {entity_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
    
    def delete_entity(self, session: Session, entity_id: int) -> tuple:
        """
        Delete an entity.
        
        Args:
            session: Database session
            entity_id: ID of the entity to delete
            
        Returns:
            Tuple of (response_data, status_code)
        """
        try:
            # Get entity and validate it exists
            entity = Entity.get_by_id(entity_id, session=session)
            if not entity:
                return jsonify({"error": "Entity not found"}), 404
            
            # Delete entity using domain method
            Entity.delete(entity_id, session=session)
            
            # Commit the transaction
            session.commit()
            
            return jsonify({"message": "Entity deleted successfully"}), 200
            
        except Exception as e:
            current_app.logger.error(f"Error deleting entity {entity_id}: {str(e)}")
            if 'session' in locals():
                session.rollback()
            return jsonify({"error": "Internal server error"}), 500
