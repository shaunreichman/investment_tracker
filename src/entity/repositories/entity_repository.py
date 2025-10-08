"""
Entity Repository.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from src.entity.models import Entity
from src.entity.enums.entity_enums import SortFieldEntity
from src.shared.enums.shared_enums import SortOrder, Country
from src.entity.enums.entity_enums import EntityType


class EntityRepository:
    """
    Entity Repository.
    
    This repository handles all database operations for entities including
    CRUD operations, complex queries. It provides
    a clean interface for business logic components to interact with
    entity data without direct database access.
    """
    
    def __init__(self):
        """
        Initialize the entity repository.
        
        Args:
            None
        """
        pass


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
            entity_types: Optional entity type filter (optional)
            tax_jurisdictions: Optional tax jurisdiction filter (optional)
            names: Optional name filter (optional)
            sort_by: Optional sort field (optional)
            sort_order: Optional sort order (optional)
        Returns:
            List of entities
        """
        # Validate sort field
        if sort_by not in SortFieldEntity:
            raise ValueError(f"Invalid sort field: {sort_by}")
        
        # Validate sort order
        if sort_order not in SortOrder:
            raise ValueError(f"Invalid sort order: {sort_order}")

        # Query database
        entities = session.query(Entity)
        if entity_types:
            entities = entities.filter(Entity.entity_type.in_([et.value for et in entity_types]))
        if tax_jurisdictions:
            entities = entities.filter(Entity.tax_jurisdiction.in_([tj.value for tj in tax_jurisdictions]))
        if names:
            entities = entities.filter(Entity.name.in_(names))
        
        # Apply sorting
        if sort_by == SortFieldEntity.NAME:
            entities = entities.order_by(Entity.name.asc() if sort_order == SortOrder.ASC else Entity.name.desc())
        elif sort_by == SortFieldEntity.TYPE:
            entities = entities.order_by(Entity.entity_type.asc() if sort_order == SortOrder.ASC else Entity.entity_type.desc())
        elif sort_by == SortFieldEntity.TAX_JURISDICTION:
            entities = entities.order_by(Entity.tax_jurisdiction.asc() if sort_order == SortOrder.ASC else Entity.tax_jurisdiction.desc())
        elif sort_by == SortFieldEntity.CREATED_AT:
            entities = entities.order_by(Entity.created_at.asc() if sort_order == SortOrder.ASC else Entity.created_at.desc())
        elif sort_by == SortFieldEntity.UPDATED_AT:
            entities = entities.order_by(Entity.updated_at.asc() if sort_order == SortOrder.ASC else Entity.updated_at.desc())
        
        entities = entities.all()
        
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
        # Query database
        entity = session.query(Entity).filter(Entity.id == entity_id).first()
        
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

        return True