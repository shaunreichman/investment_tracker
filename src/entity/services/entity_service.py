"""
Entity Service
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from src.entity.repositories.entity_repository import EntityRepository
from src.entity.services.entity_validation_service import EntityValidationService
from src.entity.models import Entity
from src.entity.enums.entity_enums import SortFieldEntity, EntityType
from src.shared.enums.shared_enums import SortOrder, Country
from src.shared.exceptions import ValidationException

class EntityService:
    """
    Service layer for entity operations.

    This module provides the EntityService class, which handles entity operations and business logic.
    The service provides clean separation of concerns for:
    - Entity retrieval
    - Entity creation
    - Entity deletion with dependency checking

    The service uses the EntityRepository to perform CRUD operations and the EntityValidationService to validate entities.
    The service is used by the EntityController to handle entity operations.
    """
    
    def __init__(self):
        """
        Initialize the entity service with all required components.

        Args:
            entity_repository: Entity repository to use. If None, creates a new one.
            entity_validation_service: Entity validation service to use. If None, creates a new one.
        """
        self.entity_repository = EntityRepository()
        self.entity_validation_service = EntityValidationService()


    ################################################################################
    # Get Entity
    ################################################################################

    def get_entities(self, session: Session, 
                    entity_types: Optional[List[EntityType]] = None,
                    tax_jurisdictions: Optional[List[Country]] = None,
                    names: Optional[List[str]] = None,
                    sort_by: SortFieldEntity = SortFieldEntity.NAME,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List[Entity]:
        """
        Get entities with filtering.
        
        Args:
            session: Database session
            entity_types: Optional entity type filter
            tax_jurisdictions: Optional tax jurisdiction filter
            names: Optional name filter
            sort_by: Optional sort field
            sort_order: Optional sort order
        Returns:
            List of Entity objects
        """
        return self.entity_repository.get_entities(session, entity_types, tax_jurisdictions, names, sort_by, sort_order)
        
    def get_entity_by_id(self, entity_id: int, session: Session) -> Optional[Entity]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            session: Database session
            
        Returns:
            Entity: The entity object, or None if not found
        """
        return self.entity_repository.get_entity_by_id(entity_id, session)
    

    ################################################################################
    # Create Entity
    ################################################################################

    def create_entity(self, entity_data: Dict[str, Any], session: Session) -> Entity:
        """
        Create a new entity.
        
        Args:
            entity_data: Dictionary containing entity data
            session: Database session
            
        Returns:
            Entity: The created entity object
            
        Raises:
            ValueError: If required fields are missing or invalid
        """
        entity = self.entity_repository.create_entity(entity_data, session)
        if not entity:
            raise ValueError(f"Failed to create entity with name '{entity_data.get('name', 'unknown')}'")
        
        return entity


    ################################################################################
    # Delete Entity
    ################################################################################
    
    def delete_entity(self, entity_id: int, session: Session) -> bool:
        """
        Delete an entity with enterprise-grade validation.
        
        Args:
            entity_id: ID of the entity to delete
            session: Database session
            
        Returns:
            True if entity was deleted, False if not found
            
        Raises:
            ValidationException: If deletion validation fails with structured details
            ValueError: If entity not found or deletion fails
        """
        # Get existing entity
        entity = self.entity_repository.get_entity_by_id(entity_id, session)
        if not entity:
            raise ValueError(f"Entity with ID {entity_id} not found")
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.entity_validation_service.validate_entity_deletion(entity_id, session)
        if validation_errors:
            raise ValidationException(
                message=f"Deletion validation failed for entity with ID {entity_id}",
                details=validation_errors
            )
        
        # Delete the entity
        success = self.entity_repository.delete_entity(entity_id, session)
        if not success:
            raise ValueError(f"Failed to delete entity with ID {entity_id}")
        
        return success