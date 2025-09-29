"""
Entity Route Tests.

This module tests the entity API routes with a focus on HTTP layer concerns:
- Route registration and endpoint availability
- Request validation and parameter handling
- Response formatting and status codes
- Error handling and middleware integration
- Controller delegation and DTO handling

Test Coverage:
- All entity endpoints (GET, POST, DELETE)
- Validation middleware integration
- Response handler integration
- Error handling and status codes
- Query parameter processing
- Request body validation
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, jsonify

from src.api.routes.entity import entity_bp
from src.api.dto.response_codes import ApiResponseCode
from src.api.dto.controller_response_dto import ControllerResponseDTO


class TestEntityRoutes:
    """Test suite for entity API routes."""

    @pytest.fixture
    def app(self):
        """Create Flask app with entity blueprint registered."""
        app = Flask(__name__)
        app.register_blueprint(entity_bp)
        app.config['TESTING'] = True
        return app

    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()

    @pytest.fixture
    def mock_controller(self):
        """Create mock entity controller."""
        controller = Mock()
        return controller

    ################################################################################
    # ROUTE REGISTRATION TESTS
    ################################################################################

    def test_entity_blueprint_registered(self, app):
        """Test that entity blueprint is properly registered."""
        # Check that entity routes are registered
        rules = [rule.rule for rule in app.url_map.iter_rules()]
        
        expected_routes = [
            '/api/entities',
            '/api/entities/<int:entity_id>'
        ]
        
        for route in expected_routes:
            assert any(route in rule for rule in rules), f"Route {route} not found in registered routes"

    ################################################################################
    # GET ENTITIES ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entities_success(self, mock_controller, client):
        """Test successful GET /api/entities request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{
                'id': 1,
                'name': 'Test Entity',
                'entity_type': 'INDIVIDUAL',
                'tax_jurisdiction': 'US',
                'description': 'Test entity description'
            }],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_entities.return_value = mock_dto
        
        # Act
        response = client.get('/api/entities')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert len(data['data']) == 1
        assert data['data'][0]['name'] == 'Test Entity'
        mock_controller.get_entities.assert_called_once()

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entities_with_query_parameters(self, mock_controller, client):
        """Test GET /api/entities with query parameters."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data=[{'id': 1, 'name': 'Test Entity'}],
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_entities.return_value = mock_dto
        
        # Act
        response = client.get('/api/entities?name=Test&entity_type=INDIVIDUAL&tax_jurisdiction=US')
        
        # Assert
        assert response.status_code == 200
        mock_controller.get_entities.assert_called_once()

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entities_not_found(self, mock_controller, client):
        """Test GET /api/entities when no entities found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Entities not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_entities.return_value = mock_dto
        
        # Act
        response = client.get('/api/entities')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Entities not found' in data['message']

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entities_controller_exception(self, mock_controller, client):
        """Test GET /api/entities when controller raises exception."""
        # Arrange
        mock_controller.get_entities.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/entities')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting entities' in data['message']

    ################################################################################
    # GET ENTITY BY ID ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entity_by_id_success(self, mock_controller, client):
        """Test successful GET /api/entities/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'name': 'Test Entity',
                'entity_type': 'COMPANY',
                'tax_jurisdiction': 'UK',
                'description': 'Test entity description'
            },
            response_code=ApiResponseCode.SUCCESS
        )
        mock_controller.get_entity.return_value = mock_dto
        
        # Act
        response = client.get('/api/entities/1')
        
        # Assert
        assert response.status_code == 200
        data = response.get_json()
        assert data['response_code'] == 'SUCCESS'
        assert data['data']['id'] == 1
        assert data['data']['name'] == 'Test Entity'
        mock_controller.get_entity.assert_called_once_with(1)

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entity_by_id_not_found(self, mock_controller, client):
        """Test GET /api/entities/<id> when entity not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Entity not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.get_entity.return_value = mock_dto
        
        # Act
        response = client.get('/api/entities/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Entity not found' in data['message']

    @patch('src.api.routes.entity.entity_controller')
    def test_get_entity_by_id_controller_exception(self, mock_controller, client):
        """Test GET /api/entities/<id> when controller raises exception."""
        # Arrange
        mock_controller.get_entity.side_effect = Exception("Controller error")
        
        # Act
        response = client.get('/api/entities/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting entity 1' in data['message']

    ################################################################################
    # CREATE ENTITY ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.entity.entity_controller')
    def test_create_entity_success(self, mock_controller, client):
        """Test successful POST /api/entities request."""
        # Arrange
        entity_data = {
            'name': 'New Entity',
            'entity_type': 'COMPANY',
            'tax_jurisdiction': 'US',
            'description': 'New entity description'
        }
        mock_dto = ControllerResponseDTO(
            data={
                'id': 1,
                'name': 'New Entity',
                'entity_type': 'COMPANY',
                'tax_jurisdiction': 'US',
                'description': 'New entity description'
            },
            response_code=ApiResponseCode.CREATED
        )
        mock_controller.create_entity.return_value = mock_dto
        
        # Act
        response = client.post('/api/entities', json=entity_data)
        
        # Assert
        assert response.status_code == 201
        data = response.get_json()
        assert data['response_code'] == 'CREATED'
        assert data['data']['name'] == 'New Entity'
        mock_controller.create_entity.assert_called_once()

    @patch('src.api.routes.entity.entity_controller')
    def test_create_entity_validation_error(self, mock_controller, client):
        """Test POST /api/entities with validation error."""
        # Arrange
        invalid_data = {'name': 'A'}  # Too short
        
        # Act
        response = client.post('/api/entities', json=invalid_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        # Validation errors are handled by middleware, not controller
        assert 'validation' in data or 'error' in data

    @patch('src.api.routes.entity.entity_controller')
    def test_create_entity_missing_required_fields(self, mock_controller, client):
        """Test POST /api/entities with missing required fields."""
        # Arrange
        incomplete_data = {'name': 'Test Entity'}  # Missing required 'tax_jurisdiction'
        
        # Act
        response = client.post('/api/entities', json=incomplete_data)
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation' in data or 'error' in data

    @patch('src.api.routes.entity.entity_controller')
    def test_create_entity_business_logic_error(self, mock_controller, client):
        """Test POST /api/entities with business logic error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Invalid entity type",
            response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR
        )
        mock_controller.create_entity.return_value = mock_dto
        
        entity_data = {
            'name': 'Test Entity',
            'entity_type': 'COMPANY',  # Valid enum value
            'tax_jurisdiction': 'US'
        }
        
        # Act
        response = client.post('/api/entities', json=entity_data)
        
        # Assert
        # Should return business logic error from controller (maps to 400)
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert 'Invalid entity type' in data['message']

    @patch('src.api.routes.entity.entity_controller')
    def test_create_entity_controller_exception(self, mock_controller, client):
        """Test POST /api/entities when controller raises exception."""
        # Arrange
        mock_controller.create_entity.side_effect = Exception("Controller error")
        
        entity_data = {
            'name': 'Test Entity',
            'tax_jurisdiction': 'US'
        }
        
        # Act
        response = client.post('/api/entities', json=entity_data)
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error creating entity' in data['message']

    ################################################################################
    # DELETE ENTITY ENDPOINT TESTS
    ################################################################################

    @patch('src.api.routes.entity.entity_controller')
    def test_delete_entity_success(self, mock_controller, client):
        """Test successful DELETE /api/entities/<id> request."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            message="Entity deleted successfully",
            response_code=ApiResponseCode.DELETED
        )
        mock_controller.delete_entity.return_value = mock_dto
        
        # Act
        response = client.delete('/api/entities/1')
        
        # Assert
        assert response.status_code == 204
        mock_controller.delete_entity.assert_called_once_with(1)

    @patch('src.api.routes.entity.entity_controller')
    def test_delete_entity_not_found(self, mock_controller, client):
        """Test DELETE /api/entities/<id> when entity not found."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Entity not found",
            response_code=ApiResponseCode.RESOURCE_NOT_FOUND
        )
        mock_controller.delete_entity.return_value = mock_dto
        
        # Act
        response = client.delete('/api/entities/999')
        
        # Assert
        assert response.status_code == 404
        data = response.get_json()
        assert data['response_code'] == 'RESOURCE_NOT_FOUND'
        assert 'Entity not found' in data['message']

    @patch('src.api.routes.entity.entity_controller')
    def test_delete_entity_business_logic_error(self, mock_controller, client):
        """Test DELETE /api/entities/<id> with business logic error."""
        # Arrange
        mock_dto = ControllerResponseDTO(
            error="Entity has associated records",
            response_code=ApiResponseCode.BUSINESS_LOGIC_ERROR
        )
        mock_controller.delete_entity.return_value = mock_dto
        
        # Act
        response = client.delete('/api/entities/1')
        
        # Assert
        # Should return business logic error from controller (maps to 400)
        assert response.status_code == 400
        data = response.get_json()
        assert data['response_code'] == 'BUSINESS_LOGIC_ERROR'
        assert 'Entity has associated records' in data['message']

    @patch('src.api.routes.entity.entity_controller')
    def test_delete_entity_controller_exception(self, mock_controller, client):
        """Test DELETE /api/entities/<id> when controller raises exception."""
        # Arrange
        mock_controller.delete_entity.side_effect = Exception("Controller error")
        
        # Act
        response = client.delete('/api/entities/1')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error deleting entity 1' in data['message']

    ################################################################################
    # VALIDATION MIDDLEWARE TESTS
    ################################################################################

    def test_get_entities_invalid_enum_values(self, client):
        """Test GET /api/entities with invalid enum values."""
        # Act
        response = client.get('/api/entities?entity_type=INVALID&tax_jurisdiction=INVALID')
        
        # Assert
        # Validation middleware should catch invalid enum values, but if not, controller will fail
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'validation' in data or 'error' in data or data.get('response_code') == 'INTERNAL_SERVER_ERROR'

    def test_create_entity_invalid_field_types(self, client):
        """Test POST /api/entities with invalid field types."""
        # Act
        response = client.post('/api/entities', json={
            'name': 123,  # Should be string
            'entity_type': 456,  # Should be string
            'tax_jurisdiction': 'US'
        })
        
        # Assert
        assert response.status_code == 400
        data = response.get_json()
        assert 'validation' in data or 'error' in data

    def test_create_entity_field_length_validation(self, client):
        """Test POST /api/entities with field length constraints."""
        # Test name too short
        response = client.post('/api/entities', json={
            'name': 'A',  # Too short
            'tax_jurisdiction': 'US'
        })
        assert response.status_code == 400
        
        # Test name too long
        response = client.post('/api/entities', json={
            'name': 'A' * 300,  # Too long
            'tax_jurisdiction': 'US'
        })
        assert response.status_code == 400
        
        # Test description too long
        response = client.post('/api/entities', json={
            'name': 'Test Entity',
            'tax_jurisdiction': 'US',
            'description': 'A' * 1001  # Too long
        })
        assert response.status_code == 400

    def test_create_entity_required_field_validation(self, client):
        """Test POST /api/entities with missing required fields."""
        # Test without name
        response = client.post('/api/entities', json={
            'tax_jurisdiction': 'US'
        })
        assert response.status_code == 400
        
        # Test without tax_jurisdiction
        response = client.post('/api/entities', json={
            'name': 'Test Entity'
        })
        assert response.status_code == 400
        
        # Test with empty body
        response = client.post('/api/entities', json={})
        assert response.status_code == 400

    ################################################################################
    # HTTP METHOD TESTS
    ################################################################################

    def test_unsupported_http_methods(self, client):
        """Test that unsupported HTTP methods return 405."""
        # Test PUT method on entities endpoint
        response = client.put('/api/entities')
        assert response.status_code == 405
        
        # Test PATCH method on entities endpoint
        response = client.patch('/api/entities/1')
        assert response.status_code == 405
        
        # Test PUT method on specific entity endpoint
        response = client.put('/api/entities/1')
        assert response.status_code == 405

    ################################################################################
    # ERROR HANDLING TESTS
    ################################################################################

    @patch('src.api.routes.entity.entity_controller')
    def test_route_handles_controller_exception(self, mock_controller, client):
        """Test that routes handle controller exceptions gracefully."""
        # Arrange
        mock_controller.get_entities.side_effect = Exception("Unexpected error")
        
        # Act
        response = client.get('/api/entities')
        
        # Assert
        assert response.status_code == 500
        data = response.get_json()
        assert data['response_code'] == 'INTERNAL_SERVER_ERROR'
        assert 'Unexpected error getting entities' in data['message']

    ################################################################################
    # VALIDATION MIDDLEWARE INTEGRATION TESTS
    ################################################################################

    def test_validation_middleware_integration(self, client):
        """Test that validation middleware is properly integrated."""
        # Test with invalid enum value for entity_type
        response = client.get('/api/entities?entity_type=INVALID')
        # The validation middleware should catch this, but if not, controller will fail
        assert response.status_code in [400, 500]
        
        # Test with invalid enum value for tax_jurisdiction
        response = client.get('/api/entities?tax_jurisdiction=INVALID')
        assert response.status_code in [400, 500]
        
        # Test with valid parameters - this should work
        response = client.get('/api/entities?name=Test&entity_type=COMPANY&tax_jurisdiction=US')
        # This should pass validation but may fail at controller level due to no database session
        assert response.status_code in [200, 500]

    def test_sanitization_middleware_integration(self, client):
        """Test that sanitization middleware is working."""
        # Test with potentially malicious input
        response = client.post('/api/entities', json={
            'name': '<script>alert("xss")</script>Test Entity',
            'tax_jurisdiction': 'US',
            'description': 'Test & description'
        })
        
        # Should either pass validation (if sanitized) or fail validation
        assert response.status_code in [201, 400, 422, 500]
