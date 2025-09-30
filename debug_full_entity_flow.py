#!/usr/bin/env python3
"""
Debug script for full entity creation flow
"""

import sys
import os
sys.path.append('src')

from src.entity.services.entity_service import EntityService
from src.entity.enums.entity_enums import EntityType
from src.shared.enums.shared_enums import Country
from src.database import get_global_session

def test_full_entity_flow():
    """Test the full entity creation flow"""
    
    print("Testing full entity creation flow...")
    
    # Test data
    entity_data = {
        'name': 'Test Entity Full Flow',
        'entity_type': EntityType.PERSON,
        'tax_jurisdiction': Country.AU,
        'description': 'Test entity for full flow'
    }
    
    print(f"Entity data: {entity_data}")
    
    try:
        # Get database session
        print("\n1. Getting database session...")
        session = get_global_session()
        print("✅ Database session created")
        
        # Create entity service
        print("\n2. Creating entity service...")
        entity_service = EntityService()
        print("✅ Entity service created")
        
        # Create entity
        print("\n3. Creating entity...")
        entity = entity_service.create_entity(entity_data, session)
        print(f"✅ Entity created: {entity}")
        
        # Commit transaction
        print("\n4. Committing transaction...")
        session.commit()
        print("✅ Transaction committed")
        
        # Get entity by ID
        print("\n5. Retrieving entity by ID...")
        retrieved_entity = entity_service.get_entity_by_id(entity.id, session)
        print(f"✅ Entity retrieved: {retrieved_entity}")
        
        # Clean up
        print("\n6. Cleaning up...")
        session.delete(entity)
        session.commit()
        print("✅ Entity deleted")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    test_full_entity_flow()
