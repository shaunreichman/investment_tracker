#!/usr/bin/env python3
"""
Debug script for API entity creation
"""

import sys
import os
sys.path.append('src')

from src.api import create_app
from src.entity.enums.entity_enums import EntityType
from src.shared.enums.shared_enums import Country

def test_api_entity_creation():
    """Test entity creation through the API"""
    
    print("Testing API entity creation...")
    
    # Create Flask app
    app = create_app()
    
    with app.test_client() as client:
        with app.app_context():
            # Test data
            entity_data = {
                'name': 'Test Entity API',
                'entity_type': 'PERSON',
                'tax_jurisdiction': 'AU',
                'description': 'Test entity for API'
            }
            
            print(f"Entity data: {entity_data}")
            
            # Make POST request
            print("\nMaking POST request to /api/entities...")
            response = client.post('/api/entities', 
                                 json=entity_data,
                                 content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")
            
            if response.status_code == 201:
                print("✅ Entity created successfully!")
            else:
                print("❌ Entity creation failed!")

if __name__ == "__main__":
    test_api_entity_creation()
