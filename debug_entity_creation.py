#!/usr/bin/env python3
"""
Debug script for entity creation issue
"""

import sys
import os
sys.path.append('src')

from src.entity.models.entity import Entity
from src.entity.enums.entity_enums import EntityType
from src.shared.enums.shared_enums import Country

def test_entity_creation():
    """Test entity creation with different data formats"""
    
    print("Testing Entity creation...")
    
    # Test 1: With enum objects
    print("\n1. Testing with enum objects:")
    try:
        entity_data_enum = {
            'name': 'Test Entity',
            'entity_type': EntityType.PERSON,
            'tax_jurisdiction': Country.AU,
            'description': 'Test entity'
        }
        print(f"Entity data: {entity_data_enum}")
        entity = Entity(**entity_data_enum)
        print(f"✅ Success: {entity}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 2: With string values
    print("\n2. Testing with string values:")
    try:
        entity_data_string = {
            'name': 'Test Entity 2',
            'entity_type': 'PERSON',
            'tax_jurisdiction': 'AU',
            'description': 'Test entity 2'
        }
        print(f"Entity data: {entity_data_string}")
        entity = Entity(**entity_data_string)
        print(f"✅ Success: {entity}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print(f"Error type: {type(e)}")
    
    # Test 3: Check enum values
    print("\n3. Checking enum values:")
    print(f"EntityType.PERSON = {EntityType.PERSON}")
    print(f"EntityType.PERSON.value = {EntityType.PERSON.value}")
    print(f"Country.AU = {Country.AU}")
    print(f"Country.AU.value = {Country.AU.value}")

if __name__ == "__main__":
    test_entity_creation()
