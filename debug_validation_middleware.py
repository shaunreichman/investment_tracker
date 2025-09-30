#!/usr/bin/env python3
"""
Debug script for validation middleware
"""

import sys
import os
sys.path.append('src')

from src.api import create_app
from src.api.middleware.validation.base_validation import validate_request
from src.entity.enums.entity_enums import EntityType
from src.shared.enums.shared_enums import Country
from flask import request, jsonify

def test_validation_middleware():
    """Test the validation middleware directly"""
    
    print("Testing validation middleware...")
    
    # Create Flask app
    app = create_app()
    
    @app.route('/test-validation', methods=['POST'])
    @validate_request(
        required_fields=['name', 'entity_type', 'tax_jurisdiction'],
        field_types={
            'name': 'string',
            'entity_type': 'string',
            'description': 'string',
            'tax_jurisdiction': 'string'
        },
        field_lengths={
            'name': {'min': 2, 'max': 255},
            'entity_type': {'max': 255},
            'description': {'max': 1000},
            'tax_jurisdiction': {'min': 2, 'max': 255}
        },
        enum_fields={
            'entity_type': EntityType,
            'tax_jurisdiction': Country
        },
        sanitize=True
    )
    def test_validation():
        """Test endpoint to see what validation middleware produces"""
        entity_data = getattr(request, 'validated_data', {})
        
        print(f"Raw request data: {request.get_json()}")
        print(f"Validated data: {entity_data}")
        print(f"Entity type: {type(entity_data.get('entity_type'))}")
        print(f"Tax jurisdiction: {type(entity_data.get('tax_jurisdiction'))}")
        
        return jsonify({
            'raw_data': request.get_json(),
            'validated_data': entity_data,
            'entity_type_type': str(type(entity_data.get('entity_type'))),
            'tax_jurisdiction_type': str(type(entity_data.get('tax_jurisdiction')))
        })
    
    with app.test_client() as client:
        with app.app_context():
            # Test data
            entity_data = {
                'name': 'Test Entity Validation',
                'entity_type': 'PERSON',
                'tax_jurisdiction': 'AU',
                'description': 'Test entity for validation'
            }
            
            print(f"Entity data: {entity_data}")
            
            # Make POST request
            print("\nMaking POST request to /test-validation...")
            response = client.post('/test-validation', 
                                 json=entity_data,
                                 content_type='application/json')
            
            print(f"Response status: {response.status_code}")
            print(f"Response data: {response.get_json()}")

if __name__ == "__main__":
    test_validation_middleware()
