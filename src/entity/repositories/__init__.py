"""
Entity Repositories.

This module provides the data access layer abstraction for the entity system.
Repositories handle all database operations and provide a clean interface
for business logic components to interact with data.
"""

from src.entity.repositories.entity_repository import EntityRepository

__all__ = [
    'EntityRepository',
]
