"""
Health and Error Handling Tests

Tests for:
- Health check endpoint
- Error handling scenarios
- Invalid request handling
- Edge cases
"""

import pytest
import json


class TestHealthEndpoint:
    """Test /api/health endpoint"""
    
    def test_health_check_success(self, client):
        """Test health check returns success status"""
        response = client.get('/api/health')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == "ok"
        assert data['message'] == "API is running"
    
    def test_health_check_methods(self, client):
        """Test health check only accepts GET method"""
        # Test POST (should fail)
        response = client.post('/api/health')
        assert response.status_code == 405  # Method Not Allowed
        
        # Test PUT (should fail)
        response = client.put('/api/health')
        assert response.status_code == 405
        
        # Test DELETE (should fail)
        response = client.delete('/api/health')
        assert response.status_code == 405


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_404_not_found(self, client):
        """Test non-existent endpoints return 404"""
        response = client.get('/api/non-existent-endpoint')
        
        assert response.status_code == 404
        
        # Try to get JSON, but handle case where 404 might not return JSON
        try:
            data = response.get_json()
            if data is not None:
                assert 'error' in data
        except Exception:
            # 404 might return HTML or plain text, which is acceptable
            pass
    
    def test_invalid_json_handling(self, client):
        """Test endpoints handle invalid JSON gracefully"""
        # Test with investment companies endpoint
        response = client.post(
            '/api/investment-companies',
            data="invalid json content",
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_missing_content_type(self, client):
        """Test endpoints handle missing content-type gracefully"""
        response = client.post(
            '/api/investment-companies',
            data='{"name": "Test"}'
            # Missing content-type header
        )
        
        # Should either accept or return a clear error
        assert response.status_code in [200, 201, 400, 415]
    
    def test_empty_request_body(self, client):
        """Test endpoints handle empty request bodies"""
        response = client.post(
            '/api/investment-companies',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestInputValidation:
    """Test input validation scenarios"""
    
    def test_missing_required_fields(self, client):
        """Test endpoints validate required fields"""
        # Test investment company creation without name
        company_data = {
            "abn": "12345678901"
            # Missing name field
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
    
    def test_invalid_field_types(self, client):
        """Test endpoints validate field types"""
        # Test with invalid amount type
        company_data = {
            "name": "Test Company",
            "abn": "12345678901",
            "address": 123  # Should be string
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        # Should either accept or return validation error
        assert response.status_code in [200, 201, 400, 422]
    
    def test_invalid_enum_values(self, client, db_session):
        """Test endpoints validate enum values"""
        from tests.factories import InvestmentCompanyFactory, EntityFactory
        
        company = InvestmentCompanyFactory()
        entity = EntityFactory()
        
        # Test with invalid fund type
        fund_data = {
            "name": "Test Fund",
            "fund_type": "INVALID_TYPE",  # Invalid enum value
            "tracking_type": "COST_BASED",
            "investment_company_id": company.id,
            "entity_id": entity.id
        }
        
        response = client.post(
            '/api/funds',
            data=json.dumps(fund_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data


class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_very_long_strings(self, client):
        """Test endpoints handle very long input strings"""
        very_long_name = "A" * 1000  # Very long name
        
        company_data = {
            "name": very_long_name,
            "abn": "12345678901"
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        # Should either accept or return validation error
        assert response.status_code in [200, 201, 400, 422]
    
    def test_special_characters(self, client):
        """Test endpoints handle special characters in input"""
        special_name = "Company & Co. (Pty) Ltd. - 100%"
        
        company_data = {
            "name": special_name,
            "abn": "12345678901"
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        # Should accept valid special characters
        assert response.status_code in [200, 201]
    
    def test_unicode_characters(self, client):
        """Test endpoints handle unicode characters"""
        unicode_name = "Café & Résumé Company"
        
        company_data = {
            "name": unicode_name,
            "abn": "12345678901"
        }
        
        response = client.post(
            '/api/investment-companies',
            data=json.dumps(company_data),
            content_type='application/json'
        )
        
        # Should accept unicode characters
        assert response.status_code in [200, 201]
    
    def test_zero_and_negative_values(self, client, db_session):
        """Test endpoints handle zero and negative numeric values"""
        from tests.factories import InvestmentCompanyFactory, EntityFactory, FundFactory
        from src.fund.models import Fund
        from src.investment_company.models import InvestmentCompany
        from src.entity.models import Entity

        company = InvestmentCompanyFactory()
        entity = EntityFactory()

        # Create a fund first
        fund = FundFactory(
            investment_company=company,
            entity=entity
        )
        
        # Ensure data is committed to the database
        db_session.commit()
        
        print(f"DEBUG: Created fund with ID: {fund.id}")

        # Test with zero amount - should return 400 (validation error)
        event_data = {
            "event_type": "CAPITAL_CALL",
            "amount": 0.0,
            "event_date": "2024-01-01"
        }

        response = client.post(
            f'/api/funds/{fund.id}/events',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        print(f"DEBUG: First request status: {response.status_code}")

        # Should return validation error for zero amount
        assert response.status_code == 400
        assert "positive number" in response.get_json()["error"].lower()

        # Test with negative amount - should return 400 (validation error)
        event_data["amount"] = -100.0
        
        response = client.post(
            f'/api/funds/{fund.id}/events',
            data=json.dumps(event_data),
            content_type='application/json'
        )
        
        print(f"DEBUG: Second request status: {response.status_code}")

        # Should return validation error for negative amount
        assert response.status_code == 400
        assert "positive number" in response.get_json()["error"].lower()
