"""
Entity domain creation and management.

This module contains entity creation and management functions.
"""

from sqlalchemy.orm import Session
from .models import Entity


def create_entity(name, description=None, tax_jurisdiction="AU", session=None):
    """
    Create a new entity.
    
    Args:
        name (str): Entity name (must be unique)
        description (str, optional): Entity description
        tax_jurisdiction (str): Tax jurisdiction code (default: "AU")
        session (Session, optional): Database session
    
    Returns:
        Entity: The created entity
    """
    entity = Entity(
        name=name,
        description=description,
        tax_jurisdiction=tax_jurisdiction
    )
    
    if session:
        session.add(entity)
        session.commit()
    
    return entity


def get_entity_by_name(name, session):
    """
    Get an entity by name.
    
    Args:
        name (str): Entity name
        session (Session): Database session
    
    Returns:
        Entity or None: The entity if found, None otherwise
    """
    return session.query(Entity).filter(Entity.name == name).first()


def get_all_entities(session):
    """
    Get all entities.
    
    Args:
        session (Session): Database session
    
    Returns:
        list: List of all entities
    """
    return session.query(Entity).all()


__all__ = [
    'create_entity',
    'get_entity_by_name', 
    'get_all_entities',
] 