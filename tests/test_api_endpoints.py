import unittest
import json
import os
import sys
from datetime import datetime, date, timedelta

# Add the src directory to the path so we can import the API
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from database import get_database_session

class TestAPIEndpoints(unittest.TestCase):
    """Test cases for Flask API endpoints"""
    
    def setUp(self):
        """Set up test client and database session"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Get database session for test data setup
        self.engine, self.session_factory, self.scoped_session = get_database_session()
        self.session = self.scoped_session()
    
    def tearDown(self):
        """Clean up after tests"""
        self.session.close()
    
    def test_health_check_endpoint(self):
        """Test the health check endpoint"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('status', data)
        self.assertIn('message', data)
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['message'], 'API is running')
    
    def test_portfolio_summary_endpoint(self):
        """Test the portfolio summary endpoint"""
        response = self.client.get('/api/dashboard/portfolio-summary')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        required_fields = [
            'total_funds', 'active_funds', 'total_equity_balance',
            'total_average_equity_balance', 'recent_events_count',
            'total_tax_statements', 'last_updated'
        ]
        
        for field in required_fields:
            self.assertIn(field, data)
        
        # Check data types
        self.assertIsInstance(data['total_funds'], int)
        self.assertIsInstance(data['active_funds'], int)
        self.assertIsInstance(data['total_equity_balance'], (int, float))
        self.assertIsInstance(data['total_average_equity_balance'], (int, float))
        self.assertIsInstance(data['recent_events_count'], int)
        self.assertIsInstance(data['total_tax_statements'], int)
        self.assertIsInstance(data['last_updated'], str)
    
    def test_funds_list_endpoint(self):
        """Test the funds list endpoint"""
        response = self.client.get('/api/dashboard/funds')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('funds', data)
        self.assertIsInstance(data['funds'], list)
        
        if data['funds']:  # If there are funds in the database
            fund = data['funds'][0]
            required_fields = [
                'id', 'name', 'fund_type', 'tracking_type', 'currency',
                'current_equity_balance', 'average_equity_balance', 'is_active',
                'investment_company', 'entity', 'recent_events_count'
            ]
            
            for field in required_fields:
                self.assertIn(field, fund)
            
            # Check data types
            self.assertIsInstance(fund['id'], int)
            self.assertIsInstance(fund['name'], str)
            self.assertIsInstance(fund['fund_type'], str)
            self.assertIsInstance(fund['tracking_type'], str)
            self.assertIsInstance(fund['currency'], str)
            self.assertIsInstance(fund['current_equity_balance'], (int, float))
            self.assertIsInstance(fund['average_equity_balance'], (int, float))
            self.assertIsInstance(fund['is_active'], (bool, int))
            self.assertIsInstance(fund['investment_company'], str)
            self.assertIsInstance(fund['entity'], str)
            self.assertIsInstance(fund['recent_events_count'], int)
    
    def test_recent_events_endpoint(self):
        """Test the recent events endpoint"""
        response = self.client.get('/api/dashboard/recent-events')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('events', data)
        self.assertIsInstance(data['events'], list)
        
        if data['events']:  # If there are events in the database
            event = data['events'][0]
            required_fields = [
                'id', 'fund_name', 'event_type', 'event_date', 'amount',
                'description', 'reference_number'
            ]
            
            for field in required_fields:
                self.assertIn(field, event)
            
            # Check data types
            self.assertIsInstance(event['id'], int)
            self.assertIsInstance(event['fund_name'], str)
            self.assertIsInstance(event['event_type'], str)
            self.assertIsInstance(event['event_date'], str)
            self.assertIsInstance(event['description'], str)
            self.assertIsInstance(event['reference_number'], (str, type(None)))
    
    def test_dashboard_performance_endpoint(self):
        """Test the dashboard performance endpoint"""
        response = self.client.get('/api/dashboard/performance')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertIn('performance', data)
        self.assertIsInstance(data['performance'], list)
        
        if data['performance']:  # If there are performance records
            performance = data['performance'][0]
            required_fields = [
                'fund_id', 'fund_name', 'current_equity', 'average_equity',
                'total_events', 'last_event_date'
            ]
            
            for field in required_fields:
                self.assertIn(field, performance)
            
            # Check data types
            self.assertIsInstance(performance['fund_id'], int)
            self.assertIsInstance(performance['fund_name'], str)
            self.assertIsInstance(performance['current_equity'], (int, float))
            self.assertIsInstance(performance['average_equity'], (int, float))
            self.assertIsInstance(performance['total_events'], int)
    
    def test_fund_detail_endpoint_valid_id(self):
        """Test the fund detail endpoint with a valid fund ID"""
        # First get a list of funds to find a valid ID
        funds_response = self.client.get('/api/dashboard/funds')
        self.assertEqual(funds_response.status_code, 200)
        
        funds_data = json.loads(funds_response.data)
        if funds_data['funds']:
            fund_id = funds_data['funds'][0]['id']
            
            response = self.client.get(f'/api/funds/{fund_id}')
            self.assertEqual(response.status_code, 200)
            
            data = json.loads(response.data)
            required_sections = ['fund', 'events', 'statistics']
            
            for section in required_sections:
                self.assertIn(section, data)
            
            # Check fund data
            fund = data['fund']
            fund_fields = [
                'id', 'name', 'fund_type', 'tracking_type', 'currency',
                'current_equity_balance', 'average_equity_balance', 'is_active',
                'investment_company', 'entity', 'created_at'
            ]
            
            for field in fund_fields:
                self.assertIn(field, fund)
            
            # Check statistics data
            stats = data['statistics']
            stats_fields = [
                'total_events', 'capital_calls', 'distributions', 'nav_updates',
                'unit_purchases', 'unit_sales', 'total_capital_called',
                'total_capital_returned', 'total_distributions'
            ]
            
            for field in stats_fields:
                self.assertIn(field, stats)
    
    def test_fund_detail_endpoint_invalid_id(self):
        """Test the fund detail endpoint with an invalid fund ID"""
        response = self.client.get('/api/funds/99999')  # Non-existent fund ID
        self.assertEqual(response.status_code, 404)
        
        data = json.loads(response.data)
        self.assertIn('error', data)
        self.assertIn('Fund not found', data['error'])
    
    def test_api_endpoints_content_type(self):
        """Test that all API endpoints return JSON content type"""
        endpoints = [
            '/api/health',
            '/api/dashboard/portfolio-summary',
            '/api/dashboard/funds',
            '/api/dashboard/recent-events',
            '/api/dashboard/performance'
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.content_type, 'application/json')
    
    def test_api_error_handling(self):
        """Test API error handling for invalid endpoints"""
        response = self.client.get('/api/nonexistent-endpoint')
        self.assertEqual(response.status_code, 404)
    
    def test_cors_headers(self):
        """Test that CORS headers are properly set"""
        response = self.client.get('/api/health')
        self.assertEqual(response.status_code, 200)
        
        # Check for CORS headers (Flask-CORS sets these)
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        # Note: Flask-CORS may not set all headers in test environment

if __name__ == '__main__':
    unittest.main() 