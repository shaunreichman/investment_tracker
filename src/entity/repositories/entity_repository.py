"""
Entity Repository.

This repository provides data access operations for Entity entities,
implementing the repository pattern for clean separation of concerns.

Key responsibilities:
- Entity CRUD operations
- Entity querying and filtering
- Entity relationship management
- Data persistence operations
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.entity.models import Entity
from src.entity.enums.entity_enums import SortFieldEntity
from src.shared.enums.shared_enums import SortOrder, EntityType


class EntityRepository:
    """
    Repository for entity data access operations.
    
    This repository handles all database operations for entities including
    CRUD operations, complex queries, and caching strategies. It provides
    a clean interface for business logic components to interact with
    entity data without direct database access.
    
    Attributes:
        _cache (Dict): Internal cache for frequently accessed data
        _cache_ttl (int): Time-to-live for cached data in seconds
    """
    
    def __init__(self, cache_ttl: int = 300):
        """
        Initialize the entity repository.
        
        Args:
            cache_ttl: Time-to-live for cached data in seconds (default: 5 minutes)
        """
        self._cache: Dict[str, Any] = {}
        self._cache_ttl = cache_ttl


    ################################################################################
    # Get Entity
    ################################################################################

    def get_entities(self, session: Session, 
                    entity_type: Optional[EntityType] = None,
                    tax_jurisdiction: Optional[str] = None,
                    name: Optional[str] = None,
                    sort_by: SortFieldEntity = SortFieldEntity.NAME,
                    sort_order: SortOrder = SortOrder.ASC
    ) -> List[Entity]:
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
        cache_key = f"entities:entity_type:{entity_type}:tax_jurisdiction:{tax_jurisdiction}:name:{name}:sort_by:{sort_by.value}:sort_order:{sort_order.value}"

        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Validate sort field
        if sort_by not in SortFieldEntity:
            raise ValueError(f"Invalid sort field: {sort_by}")
        
        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")
        
        # Query database
        entities = session.query(Entity)
        if entity_type:
            entities = entities.filter(Entity.entity_type == entity_type.value)
        if tax_jurisdiction:
            entities = entities.filter(Entity.tax_jurisdiction == tax_jurisdiction)
        if name:
            entities = entities.filter(Entity.name == name)
        
        # Apply sorting
        if sort_by == SortFieldEntity.NAME:
            entities = entities.order_by(Entity.name.asc() if sort_order == SortOrder.ASC else Entity.name.desc())
        elif sort_by == SortFieldEntity.TYPE:
            entities = entities.order_by(Entity.type.asc() if sort_order == SortOrder.ASC else Entity.type.desc())
        elif sort_by == SortFieldEntity.CREATED_AT:
            entities = entities.order_by(Entity.created_at.asc() if sort_order == SortOrder.ASC else Entity.created_at.desc())
        elif sort_by == SortFieldEntity.UPDATED_AT:
            entities = entities.order_by(Entity.updated_at.asc() if sort_order == SortOrder.ASC else Entity.updated_at.desc())
        
        entities = entities.all()
        
        # Cache the result
        self._cache[cache_key] = entities
        return entities

    def get_entity_by_id(self, entity_id: int, session: Session) -> Optional[Entity]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            session: Database session
            
        Returns:
            Entity object if found, None otherwise
        """
        cache_key = f"entity:id:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        entity = session.query(Entity).filter(Entity.id == entity_id).first()
        
        # Cache the result
        if entity:
            self._cache[cache_key] = entity
        
        return entity


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
            Created entity instance
        """
        entity = Entity(**entity_data)
        session.add(entity)
        session.flush()
        
        # Clear relevant caches
        self._clear_entity_caches()
        
        return entity


    ################################################################################
    # Delete Entity
    ################################################################################
    
    def delete_entity(self, entity_id: int, session: Session) -> None:
        """
        Delete an entity.
        
        Args:
            entity_id: ID of the entity to delete
            session: Database session
        """
        entity = self.get_entity_by_id(entity_id, session)
        if not entity:
            return False
        
        session.delete(entity)
        session.flush()
        
        # Clear relevant caches
        self._clear_entity_caches()

        return True
        
    
    def _clear_entity_caches(self) -> None:
        """Clear all entity-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('entity')]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
