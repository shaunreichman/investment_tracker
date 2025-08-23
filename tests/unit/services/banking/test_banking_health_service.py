"""
Banking Health Service Tests

This module tests the BankingHealthService health monitoring functionality.
Focus: Health checks, system monitoring, and business logic validation.

Other aspects covered elsewhere:
- Cache operations: test_banking_cache_service.py
- Repository operations: test_bank_repository.py, test_bank_account_repository.py
- API operations: test_bank_controller.py, test_bank_account_controller.py
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.banking.services.banking_health_service import BankingHealthService
from src.banking.services.banking_cache_service import BankingCacheService


class TestBankingHealthService:
    """Test suite for BankingHealthService - Health monitoring only"""
    
    @pytest.fixture
    def mock_cache_service(self):
        """Mock cache service for testing."""
        mock = Mock(spec=BankingCacheService)
        mock.get_cache_stats.return_value = {
            'memory_cache_size': 50,
            'redis_available': True
        }
        return mock
    
    @pytest.fixture
    def mock_session(self):
        """Mock database session for testing."""
        mock = Mock(spec=Session)
        mock.execute.return_value.scalar.return_value = 0
        return mock
    
    @pytest.fixture
    def health_service(self, mock_cache_service):
        """Health service with mocked dependencies."""
        with patch('src.banking.services.banking_health_service.get_banking_cache_service', return_value=mock_cache_service):
            return BankingHealthService()
    
    # ============================================================================
    # INITIALIZATION TESTS
    # ============================================================================
    
    def test_health_service_initialization(self, mock_cache_service):
        """Test health service initialization with dependencies."""
        with patch('src.banking.services.banking_health_service.get_banking_cache_service', return_value=mock_cache_service):
            service = BankingHealthService()
            
            assert service.cache_service is mock_cache_service
            assert service.bank_repo is not None
            assert service.bank_account_repo is not None
            assert service.start_time is not None
            assert service.health_history == []
    
    # ============================================================================
    # SYSTEM HEALTH TESTS
    # ============================================================================
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_get_system_health_success(self, mock_disk, mock_memory, mock_cpu, health_service, mock_session):
        """Test successful system health check."""
        # Setup mocks
        mock_cpu.return_value = 25.0
        mock_memory.return_value.percent = 60.0
        mock_disk.return_value.percent = 45.0
        
        # Execute health check
        health_status = health_service.get_system_health(mock_session)
        
        # Verify structure
        assert 'timestamp' in health_status
        assert 'uptime' in health_status
        assert 'overall_status' in health_status
        assert 'checks' in health_status
        assert 'warnings' in health_status
        assert 'errors' in health_status
        
        # Verify status
        assert health_status['overall_status'] in ['healthy', 'degraded', 'unhealthy']
        assert 'system' in health_status['checks']
        assert 'database' in health_status['checks']
        assert 'cache' in health_status['checks']
        assert 'business_logic' in health_status['checks']
        assert 'performance' in health_status['checks']
    
    def test_get_system_health_with_error(self, health_service, mock_session):
        """Test system health check handles errors gracefully."""
        # Force an error by making session.execute raise an exception
        mock_session.execute.side_effect = Exception("Database connection failed")
        
        health_status = health_service.get_system_health(mock_session)
        
        # The health service catches errors in individual checks and sets status to 'error'
        # but doesn't add them to the main errors list - it sets overall status based on check results
        assert health_status['overall_status'] in ['degraded', 'unhealthy']
        # Check that individual checks have error status
        assert any(check.get('status') == 'error' for check in health_status['checks'].values())
    
    # ============================================================================
    # SYSTEM RESOURCE CHECKS
    # ============================================================================
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_resources_healthy(self, mock_disk, mock_memory, mock_cpu, health_service):
        """Test system resources when all are healthy."""
        mock_cpu.return_value = 25.0
        mock_memory.return_value.percent = 60.0
        mock_disk.return_value.percent = 45.0
        
        result = health_service._check_system_resources()
        
        assert result['status'] == 'healthy'
        assert result['cpu_percent'] == 25.0
        assert result['memory_percent'] == 60.0
        assert result['disk_percent'] == 45.0
        assert len(result['warnings']) == 0
    
    @patch('psutil.cpu_percent')
    @patch('psutil.virtual_memory')
    @patch('psutil.disk_usage')
    def test_system_resources_warnings(self, mock_disk, mock_memory, mock_cpu, health_service):
        """Test system resources when warnings are triggered."""
        mock_cpu.return_value = 85.0  # High CPU
        mock_memory.return_value.percent = 90.0  # High memory
        mock_disk.return_value.percent = 95.0  # High disk
        
        result = health_service._check_system_resources()
        
        assert result['status'] == 'warning'
        assert len(result['warnings']) == 3
        assert any('High CPU usage' in w for w in result['warnings'])
        assert any('High memory usage' in w for w in result['warnings'])
        assert any('High disk usage' in w for w in result['warnings'])
    
    # ============================================================================
    # DATABASE HEALTH CHECKS
    # ============================================================================
    
    def test_database_health_success(self, health_service, mock_session):
        """Test database health check success."""
        # Setup mock to return reasonable values
        mock_session.execute.return_value.scalar.return_value = 5
        
        result = health_service._check_database_health(mock_session)
        
        assert result['status'] == 'healthy'
        assert 'response_time' in result
        assert 'bank_count' in result
        assert 'account_count' in result
        assert len(result['warnings']) == 0
    
    def test_database_health_slow_response(self, health_service, mock_session):
        """Test database health check with slow response."""
        # Mock time to simulate slow response
        with patch('time.time') as mock_time:
            mock_time.side_effect = [0.0, 0.15]  # 150ms response time
            mock_session.execute.return_value.scalar.return_value = 5
            
            result = health_service._check_database_health(mock_session)
            
            assert result['status'] == 'warning'
            assert result['response_time'] > 0.1
            assert any('Slow database response' in w for w in result['warnings'])
    
    # ============================================================================
    # CACHE HEALTH CHECKS
    # ============================================================================
    
    def test_cache_health_success(self, health_service, mock_cache_service):
        """Test cache health check success."""
        mock_cache_service.get_cache_stats.return_value = {
            'memory_cache_size': 50,
            'redis_available': True
        }
        
        result = health_service._check_cache_health()
        
        assert result['status'] == 'healthy'
        assert result['redis_available'] is True
        assert result['memory_cache_size'] == 50
        assert len(result['warnings']) == 0
    
    def test_cache_health_redis_unavailable(self, health_service, mock_cache_service):
        """Test cache health check when Redis is unavailable."""
        mock_cache_service.get_cache_stats.return_value = {
            'memory_cache_size': 50,
            'redis_available': False
        }
        
        result = health_service._check_cache_health()
        
        assert result['status'] == 'warning'
        assert result['redis_available'] is False
        assert any('Redis cache unavailable' in w for w in result['warnings'])
    
    # ============================================================================
    # BUSINESS LOGIC CHECKS
    # ============================================================================
    
    def test_business_logic_healthy(self, health_service, mock_session):
        """Test business logic check when all is healthy."""
        # Setup mock to return no issues
        mock_session.execute.return_value.scalar.return_value = 0
        
        result = health_service._check_business_logic(mock_session)
        
        assert result['status'] == 'healthy'
        assert result['checks']['orphaned_accounts'] == 0
        assert result['checks']['duplicate_accounts'] == 0
        assert len(result['warnings']) == 0
    
    def test_business_logic_orphaned_accounts(self, health_service, mock_session):
        """Test business logic check with orphaned accounts."""
        # Setup mock to return orphaned accounts
        mock_session.execute.return_value.scalar.side_effect = [3, 0, 0]  # 3 orphaned accounts
        
        result = health_service._check_business_logic(mock_session)
        
        assert result['status'] == 'warning'
        assert result['checks']['orphaned_accounts'] == 3
        assert any('Found 3 orphaned bank accounts' in w for w in result['warnings'])
    
    def test_business_logic_duplicate_accounts(self, health_service, mock_session):
        """Test business logic check with duplicate accounts."""
        # Setup mock to return duplicate accounts
        mock_session.execute.return_value.scalar.side_effect = [0, 2, 0]  # 2 duplicate accounts
        
        result = health_service._check_business_logic(mock_session)
        
        assert result['status'] == 'error'
        assert result['checks']['duplicate_accounts'] == 2
        assert any('Found 2 duplicate account numbers' in w for w in result['warnings'])
    
    # ============================================================================
    # HEALTH SUMMARY AND TRENDS
    # ============================================================================
    
    def test_health_summary_no_history(self, health_service):
        """Test health summary when no history exists."""
        summary = health_service.get_health_summary()
        
        assert summary['status'] == 'unknown'
        assert 'No health checks performed yet' in summary['message']
    
    def test_health_summary_with_history(self, health_service, mock_session):
        """Test health summary with existing history."""
        # Perform a health check to create history
        with patch('psutil.cpu_percent', return_value=25.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 60.0
            mock_disk.return_value.percent = 45.0
            
            health_service.get_system_health(mock_session)
            
            summary = health_service.get_health_summary()
            
            assert summary['status'] in ['healthy', 'degraded', 'unhealthy']
            assert 'timestamp' in summary
            assert 'uptime' in summary
    
    def test_health_trends_no_history(self, health_service):
        """Test health trends when no history exists."""
        trends = health_service.get_health_trends(hours=24)
        
        assert 'No health history available' in trends['message']
    
    def test_health_trends_with_history(self, health_service, mock_session):
        """Test health trends with existing history."""
        # Perform multiple health checks to create history
        with patch('psutil.cpu_percent', return_value=25.0), \
             patch('psutil.virtual_memory') as mock_memory, \
             patch('psutil.disk_usage') as mock_disk:
            
            mock_memory.return_value.percent = 60.0
            mock_disk.return_value.percent = 45.0
            
            # Create some history
            for _ in range(3):
                health_service.get_system_health(mock_session)
            
            trends = health_service.get_health_trends(hours=24)
            
            assert 'period_hours' in trends
            assert 'total_checks' in trends
            assert 'status_distribution' in trends
            assert 'latest_status' in trends
            assert trends['total_checks'] >= 3
    
    # ============================================================================
    # OVERALL STATUS DETERMINATION
    # ============================================================================
    
    def test_overall_status_healthy(self, health_service):
        """Test overall status determination when all checks are healthy."""
        checks = {
            'system': {'status': 'healthy'},
            'database': {'status': 'healthy'},
            'cache': {'status': 'healthy'}
        }
        
        status = health_service._determine_overall_status(checks)
        assert status == 'healthy'
    
    def test_overall_status_degraded(self, health_service):
        """Test overall status determination when some checks have warnings."""
        checks = {
            'system': {'status': 'warning'},
            'database': {'status': 'healthy'},
            'cache': {'status': 'healthy'}
        }
        
        status = health_service._determine_overall_status(checks)
        assert status == 'degraded'
    
    def test_overall_status_unhealthy(self, health_service):
        """Test overall status determination when any check has errors."""
        checks = {
            'system': {'status': 'healthy'},
            'database': {'status': 'error'},
            'cache': {'status': 'healthy'}
        }
        
        status = health_service._determine_overall_status(checks)
        assert status == 'unhealthy'
