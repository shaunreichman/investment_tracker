#!/usr/bin/env python3
"""
Debug script for direct entity creation without validation middleware
"""

import sys
import os
sys.path.append('src')

from src.api import create_app
from src.entity.enums.entity_enums import EntityType
from src.shared.enums.shared_enums import Country
from flask import request, jsonify

def test_direct_entity_creation():
    """Test entity creation without validation middleware"""
    
    print("Testing direct entity creation...")
    
    # Create Flask app
    app = create_app()
    
    @app.route('/test-direct-entity', methods=['POST'])
    def test_direct_entity():
        """Test endpoint that creates entity directly without validation"""
        try:
            from src.api.controllers.entity_controller import EntityController
            from src.api.middleware.database_session import get_current_session
            
            # Get request data
            entity_data = request.get_json()
            print(f"Request data: {entity_data}")
            
            # Convert string values to enum objects manually
            if 'entity_type' in entity_data:
                entity_data['entity_type'] = EntityType(entity_data['entity_type'])
            if 'tax_jurisdiction' in entity_data:
                entity_data['tax_jurisdiction'] = Country(entity_data['tax_jurisdiction'])
            
            print(f"Converted data: {entity_data}")
            
            # Create entity controller
            controller = EntityController()
            session = get_current_session()
            
            # Create entity using service directly
            from src.entity.services.entity_service import EntityService
            entity_service = EntityService()
            entity = entity_service.create_entity(entity_data, session)
            session.commit()
            
            print(f"Entity created: {entity}")
            
            # Format entity for response
            from src.api.controllers.formatters.entity_formatter import format_entity
            formatted_entity = format_entity(entity)
            print(f"Formatted entity: {formatted_entity}")
            
            return jsonify({
                'success': True,
                'data': formatted_entity
            })
            
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    with app.test_client() as client:
        with app.app_context():
            # Test data
            entity_data = {
                'name': 'Test Entity Direct',
                'entity_type': 'PERSON',
                'tax_jurisdiction': 'AU',
                'description': 'Test entity for direct creation'
            }
            
            print(f"Entity data: {entity_data}")
            
            # Make POST request
            print("\nMaking POST request to /test-direct-entity...")
            response = client.post('/test-direct-entity', 
                                 json=entity_data,
                                 content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")

if __name__ == "__main__":
    test_direct_entity_creation()
