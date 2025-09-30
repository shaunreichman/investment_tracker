"""
Formatters for Entity objects.

- Provide consistent response structure
"""

from typing import Dict, Any
from src.entity.models import Entity

def format_entity(entity: Entity) -> Dict[str, Any]:
    """
    Format an Entity object for HTTP response.
    """
    return {
        'id': entity.id,
        'name': entity.name,
        'description': entity.description,
        'tax_jurisdiction': entity.tax_jurisdiction.value,
        'entity_type': entity.entity_type.value,
        'created_at': entity.created_at.isoformat() if entity.created_at else None,
        'updated_at': entity.updated_at.isoformat() if entity.updated_at else None
    }