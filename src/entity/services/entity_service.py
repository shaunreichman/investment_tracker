"""
Entity API Service.

This service provides the business logic layer for entity operations,
coordinating between the API controllers and the domain models.

Key responsibilities:
- Entity CRUD operations
- Entity business rule enforcement
- Entity validation and coordination
- Business logic orchestration
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from src.entity.repositories import EntityRepository
from src.entity.services import EntityValidationService
from src.entity.models import Entity
from src.entity.enums.entity_enums import SortFieldEntity, EntityType
from src.shared.enums.shared_enums import SortOrder, Country

class EntityService:
    """
    Service layer for entity operations.
    
    This service coordinates between the API layer, business logic services,
    and data access layer. It provides a clean interface for handling
    entity-related business operations.
    
    Attributes:
        entity_repository (EntityRepository): Repository for entity data access
        logger (Logger): Logger for logging operations
    """
    
    def __init__(self):
        """Initialize the entity service with all required components."""
        self.entity_repository = EntityRepository()
        self.entity_validation_service = EntityValidationService()
        self.logger = logging.getLogger(__name__)


    ################################################################################
    # Get Entity
    ################################################################################

    def get_entities(self, session: Session, 
                    entity_type: Optional[EntityType] = None,
                    tax_jurisdiction: Optional[str] = None,
                    name: Optional[str] = None,
                    sort_by: SortFieldEntity = SortFieldEntity.NAME,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List['Entity']:
        """
        Get entities with filtering.
        
        Args:
            session: Database session
            entity_type: Optional entity type filter
            tax_jurisdiction: Optional tax jurisdiction filter
            name: Optional name filter
            sort_by: Optional sort field
            sort_order: Optional sort order
        Returns:
            List of Entity objects
        """
        return self.entity_repository.get_entities(session, entity_type, tax_jurisdiction, name, sort_by, sort_order)
        
    def get_entity_by_id(self, entity_id: int, session: Session) -> Optional['Entity']:
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

    def create_entity(self, entity_data: Dict[str, Any], session: Session) -> 'Entity':
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
        # Validate required fields
        required_fields = ['name', 'tax_jurisdiction']
        for field in required_fields:
            if field not in entity_data:
                raise ValueError(f"Required field '{field}' is missing")

        processed_data = entity_data.copy()
        if 'tax_jurisdiction' in processed_data and isinstance(processed_data['tax_jurisdiction'], str):
            try:
                processed_data['tax_jurisdiction'] = Country(processed_data['tax_jurisdiction'])
            except ValueError:
                raise ValueError(f"Invalid tax jurisdiction: {processed_data['tax_jurisdiction']}. Must be one of: {[c.value for c in Country]}")
        
        entity = self.entity_repository.create_entity(processed_data, session)
        if not entity:
            raise ValueError(f"Failed to create entity")
        
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
            ValueError: If deletion validation fails
        """
        # Get existing entity
        entity = self.entity_repository.get_entity_by_id(entity_id, session)
        if not entity:
            return False
        
        # ENTERPRISE VALIDATION: Validate deletion
        validation_errors = self.entity_validation_service.validate_entity_deletion(entity_id, session)
        if validation_errors:
            raise ValueError(f"Deletion validation failed: {validation_errors}")
        
        # Delete the entity
        success = self.entity_repository.delete_entity(entity_id, session)
        if not success:
            raise ValueError(f"Failed to delete entity")
        
        return True