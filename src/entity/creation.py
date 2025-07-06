"""
Entity domain creation and management.

This module contains entity utility functions and management operations.
"""

from sqlalchemy.orm import Session
from .models import Entity
from ..shared.utils import with_database_session


@with_database_session
def get_entity_by_name(name, session=None):
    """
    Get an entity by name.
    
    Args:
        name (str): Entity name
        session (Session, optional): Database session (handled by @with_database_session)
    
    Returns:
        Entity or None: The entity if found, None otherwise
    """
    return session.query(Entity).filter(Entity.name == name).first()


@with_database_session
def get_all_entities(session=None):
    """
    Get all entities.
    
    Args:
        session (Session, optional): Database session (handled by @with_database_session)
    
    Returns:
        list: List of all entities
    """
    return session.query(Entity).all()


__all__ = [
    'get_entity_by_name', 
    'get_all_entities',
] 