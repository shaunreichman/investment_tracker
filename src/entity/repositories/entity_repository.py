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
from sqlalchemy import and_, or_, func

from src.entity.models import Entity


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
    
    def get_by_id(self, entity_id: int, session: Session) -> Optional[Entity]:
        """
        Get an entity by its ID.
        
        Args:
            entity_id: ID of the entity to retrieve
            session: Database session
            
        Returns:
            Entity object if found, None otherwise
        """
        cache_key = f"entity:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        entity = session.query(Entity).filter(Entity.id == entity_id).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = entity
        
        return entity
    
    def get_by_name(self, name: str, session: Session) -> Optional[Entity]:
        """
        Get an entity by its name.
        
        Args:
            name: Entity name
            session: Database session
            
        Returns:
            Entity object if found, None otherwise
        """
        cache_key = f"entity:name:{name}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        entity = session.query(Entity).filter(Entity.name == name.strip()).first()
        
        # Cache the result (including None to prevent race conditions)
        self._cache[cache_key] = entity
        
        return entity
    
    def get_all(self, session: Session) -> List[Entity]:
        """
        Get all entities.
        
        Args:
            session: Database session
            
        Returns:
            List of all entities
        """
        cache_key = "entities:all"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        entities = session.query(Entity).order_by(Entity.name).all()
        
        # Cache the result
        self._cache[cache_key] = entities
        
        return entities
    
    def get_by_tax_jurisdiction(self, tax_jurisdiction: str, session: Session) -> List[Entity]:
        """
        Get all entities for a specific tax jurisdiction.
        
        Args:
            tax_jurisdiction: Tax jurisdiction code
            session: Database session
            
        Returns:
            List of entities in the specified tax jurisdiction
        """
        cache_key = f"entities:tax_jurisdiction:{tax_jurisdiction}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        entities = session.query(Entity).filter(Entity.tax_jurisdiction == tax_jurisdiction).all()
        
        # Cache the result
        self._cache[cache_key] = entities
        
        return entities
    
    def create(self, entity: Entity, session: Session) -> Entity:
        """
        Create a new entity.
        
        Args:
            entity: Entity instance to create
            session: Database session
            
        Returns:
            Created entity instance
        """
        session.add(entity)
        session.flush()
        
        # Clear relevant caches
        self._clear_entity_caches()
        
        return entity
    
    def update(self, entity: Entity, session: Session) -> Entity:
        """
        Update an existing entity.
        
        Args:
            entity: Entity instance to update
            session: Database session
            
        Returns:
            Updated entity instance
        """
        session.flush()
        
        # Clear relevant caches
        self._clear_entity_caches()
        
        return entity
    
    def delete(self, entity: Entity, session: Session) -> None:
        """
        Delete an entity.
        
        Args:
            entity: Entity instance to delete
            session: Database session
        """
        session.delete(entity)
        session.flush()
        
        # Clear relevant caches
        self._clear_entity_caches()
    
    def exists(self, entity_id: int, session: Session) -> bool:
        """
        Check if an entity exists.
        
        Args:
            entity_id: ID of the entity to check
            session: Database session
            
        Returns:
            True if entity exists, False otherwise
        """
        cache_key = f"entity:exists:{entity_id}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        exists = session.query(Entity).filter(Entity.id == entity_id).first() is not None
        
        # Cache the result
        self._cache[cache_key] = exists
        
        return exists
    
    def count_by_tax_jurisdiction(self, tax_jurisdiction: str, session: Session) -> int:
        """
        Count entities in a specific tax jurisdiction.
        
        Args:
            tax_jurisdiction: Tax jurisdiction code
            session: Database session
            
        Returns:
            Number of entities in the tax jurisdiction
        """
        cache_key = f"entities:count:tax_jurisdiction:{tax_jurisdiction}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(Entity).filter(Entity.tax_jurisdiction == tax_jurisdiction).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def get_total_count(self, session: Session) -> int:
        """
        Get total count of all entities.
        
        Args:
            session: Database session
            
        Returns:
            Total number of entities
        """
        cache_key = "entities:total_count"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database
        count = session.query(Entity).count()
        
        # Cache the result
        self._cache[cache_key] = count
        
        return count
    
    def search(self, search_term: str, session: Session) -> List[Entity]:
        """
        Search entities by name or description.
        
        Args:
            search_term: Search term
            session: Database session
            
        Returns:
            List of matching entities
        """
        if not search_term:
            return []
        
        cache_key = f"entities:search:{search_term}"
        
        # Check cache first
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Query database with search
        entities = session.query(Entity).filter(
            or_(
                Entity.name.ilike(f"%{search_term}%"),
                Entity.description.ilike(f"%{search_term}%")
            )
        ).all()
        
        # Cache the result
        self._cache[cache_key] = entities
        
        return entities
    
    def _clear_entity_caches(self) -> None:
        """Clear all entity-related caches."""
        keys_to_remove = [key for key in self._cache.keys() if key.startswith('entity')]
        for key in keys_to_remove:
            del self._cache[key]
    
    def clear_cache(self) -> None:
        """Clear all caches."""
        self._cache.clear()
