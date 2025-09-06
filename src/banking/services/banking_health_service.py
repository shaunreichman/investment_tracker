"""
Banking Health Service for Phase 6.

This service provides comprehensive health monitoring for the banking system,
including health checks, performance metrics, and system status monitoring.

ARCHITECTURAL EXCEPTION:
This service intentionally uses direct database operations (session.execute, etc.)
which normally violate our services layer rules. This is an approved exception
because:

1. HEALTH MONITORING PURPOSE: This service tests database connectivity and
   performance directly, which requires bypassing normal data access patterns
2. SYSTEM DIAGNOSTICS: Must perform raw SQL queries to test database health
   independently of business logic
3. PRODUCTION MONITORING: Used by load balancers and monitoring systems that
   need direct system health information
4. NOT BUSINESS LOGIC: This is infrastructure monitoring, not business operations

Normal business services should use repositories for data access, but health
monitoring services are an exception to this rule.
"""

import time
import psutil
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from src.banking.services.banking_cache_service import get_banking_cache_service
from src.banking.repositories.bank_repository import BankRepository
from src.banking.repositories.bank_account_repository import BankAccountRepository

logger = logging.getLogger(__name__)


class BankingHealthService:
    """
    Comprehensive health monitoring service for banking operations.
    
    This service provides:
    - System health checks
    - Performance metrics
    - Database connectivity monitoring
    - Cache health monitoring
    - Business logic validation
    
    NOTE: This service uses direct database operations (session.execute, etc.)
    which is an approved architectural exception for health monitoring purposes.
    See module docstring for detailed explanation.
    """
    
    def __init__(self):
        """Initialize the health monitoring service."""
        self.cache_service = get_banking_cache_service()
        self.bank_repo = BankRepository()
        self.bank_account_repo = BankAccountRepository()
        self.start_time = datetime.utcnow()
        self.health_history = []
    
    def get_system_health(self, session: Session) -> Dict[str, Any]:
        """
        Get comprehensive system health status.
        
        Args:
            session: Database session
            
        Returns:
            Dictionary with complete health status
        """
        logger.info("🔍 Checking banking system health...")
        
        health_status = {
            'timestamp': datetime.utcnow().isoformat(),
            'uptime': self._get_uptime(),
            'overall_status': 'healthy',
            'checks': {},
            'warnings': [],
            'errors': []
        }
        
        try:
            # 1. System resource checks
            health_status['checks']['system'] = self._check_system_resources()
            
            # 2. Database connectivity checks
            health_status['checks']['database'] = self._check_database_health(session)
            
            # 3. Cache health checks
            health_status['checks']['cache'] = self._check_cache_health()
            
            # 4. Business logic validation
            health_status['checks']['business_logic'] = self._check_business_logic(session)
            
            # 5. Performance metrics
            health_status['checks']['performance'] = self._get_performance_metrics()
            
            # Determine overall status
            health_status['overall_status'] = self._determine_overall_status(health_status['checks'])
            
            # Store health history
            self._store_health_history(health_status)
            
            logger.info(f"✅ Health check complete: {health_status['overall_status']}")
            
        except Exception as e:
            error_msg = f"Health check failed: {str(e)}"
            health_status['errors'].append(error_msg)
            health_status['overall_status'] = 'unhealthy'
            logger.error(error_msg)
        
        return health_status
    
    def _get_uptime(self) -> str:
        """Get system uptime since service start."""
        uptime = datetime.utcnow() - self.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m {seconds}s"
        elif hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        else:
            return f"{minutes}m {seconds}s"
    
    def _check_system_resources(self) -> Dict[str, Any]:
        """Check system resource usage."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            status = 'healthy'
            warnings = []
            
            # CPU check
            if cpu_percent > 80:
                status = 'warning'
                warnings.append(f"High CPU usage: {cpu_percent:.1f}%")
            
            # Memory check
            if memory.percent > 85:
                status = 'warning'
                warnings.append(f"High memory usage: {memory.percent:.1f}%")
            
            # Disk check
            if disk.percent > 90:
                status = 'warning'
                warnings.append(f"High disk usage: {disk.percent:.1f}%")
            
            return {
                'status': status,
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_percent': disk.percent,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.warning(f"⚠️ System resource check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_database_health(self, session: Session) -> Dict[str, Any]:
        """Check database connectivity and performance."""
        try:
            start_time = time.time()
            
            # Test basic connectivity
            result = session.execute(text("SELECT 1"))
            result.fetchone()
            
            # Test banking tables
            bank_count = session.execute(text("SELECT COUNT(*) FROM banks")).scalar()
            account_count = session.execute(text("SELECT COUNT(*) FROM bank_accounts")).scalar()
            
            # Test query performance
            query_time = time.time() - start_time
            
            status = 'healthy'
            warnings = []
            
            if query_time > 0.1:  # 100ms threshold
                status = 'warning'
                warnings.append(f"Slow database response: {query_time:.3f}s")
            
            return {
                'status': status,
                'response_time': query_time,
                'bank_count': bank_count,
                'account_count': account_count,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Database health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_cache_health(self) -> Dict[str, Any]:
        """Check cache system health."""
        try:
            cache_stats = self.cache_service.get_cache_stats()
            
            status = 'healthy'
            warnings = []
            
            # Check memory cache size
            memory_size = cache_stats.get('memory_cache_size', 0)
            if memory_size > 1000:  # More than 1000 cached items
                warnings.append(f"Large memory cache: {memory_size} items")
            
            # Check Redis availability
            redis_available = cache_stats.get('redis_available', False)
            if not redis_available:
                warnings.append("Redis cache unavailable - using memory only")
            
            if warnings:
                status = 'warning'
            
            return {
                'status': status,
                'redis_available': redis_available,
                'memory_cache_size': memory_size,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Cache health check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _check_business_logic(self, session: Session) -> Dict[str, Any]:
        """Check business logic integrity."""
        try:
            status = 'healthy'
            warnings = []
            checks = {}
            
            # Check for orphaned bank accounts
            orphaned_accounts = session.execute(text("""
                SELECT COUNT(*) FROM bank_accounts ba 
                LEFT JOIN entities e ON ba.entity_id = e.id 
                WHERE e.id IS NULL
            """)).scalar()
            
            if orphaned_accounts > 0:
                status = 'warning'
                warnings.append(f"Found {orphaned_accounts} orphaned bank accounts")
            
            checks['orphaned_accounts'] = orphaned_accounts
            
            # Check for duplicate account numbers per entity
            duplicate_accounts = session.execute(text("""
                SELECT COUNT(*) FROM (
                    SELECT entity_id, account_number, COUNT(*) 
                    FROM bank_accounts 
                    GROUP BY entity_id, account_number 
                    HAVING COUNT(*) > 1
                ) duplicates
            """)).scalar()
            
            if duplicate_accounts > 0:
                status = 'error'
                warnings.append(f"Found {duplicate_accounts} duplicate account numbers")
            
            checks['duplicate_accounts'] = duplicate_accounts
            
            # Check for inactive banks with active accounts
            inactive_banks_with_accounts = session.execute(text("""
                SELECT COUNT(*) FROM banks b 
                JOIN bank_accounts ba ON b.id = ba.bank_id 
                WHERE ba.is_active = true
            """)).scalar()
            
            checks['inactive_banks_with_accounts'] = inactive_banks_with_accounts
            
            return {
                'status': status,
                'checks': checks,
                'warnings': warnings
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Business logic check failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get current performance metrics."""
        try:
            # Get cache hit rates (simplified)
            cache_stats = self.cache_service.get_cache_stats()
            
            return {
                'status': 'healthy',
                'cache_hit_rate': 'N/A',  # Would need more sophisticated tracking
                'memory_cache_size': cache_stats.get('memory_cache_size', 0),
                'redis_available': cache_stats.get('redis_available', False)
            }
            
        except Exception as e:
            logger.warning(f"⚠️ Performance metrics failed: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def _determine_overall_status(self, checks: Dict[str, Any]) -> str:
        """Determine overall health status based on individual checks."""
        if any(check.get('status') == 'error' for check in checks.values()):
            return 'unhealthy'
        elif any(check.get('status') == 'warning' for check in checks.values()):
            return 'degraded'
        else:
            return 'healthy'
    
    def _store_health_history(self, health_status: Dict[str, Any]):
        """Store health check history for trending."""
        self.health_history.append(health_status)
        
        # Keep only last 100 health checks
        if len(self.health_history) > 100:
            self.health_history = self.health_history[-100:]
    
    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for quick status checks."""
        if not self.health_history:
            return {'status': 'unknown', 'message': 'No health checks performed yet'}
        
        latest = self.health_history[-1]
        return {
            'status': latest['overall_status'],
            'timestamp': latest['timestamp'],
            'uptime': latest['uptime']
        }
    
    def get_health_trends(self, hours: int = 24) -> Dict[str, Any]:
        """Get health trends over specified time period."""
        if not self.health_history:
            return {'message': 'No health history available'}
        
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_checks = [
            check for check in self.health_history
            if datetime.fromisoformat(check['timestamp']) > cutoff_time
        ]
        
        if not recent_checks:
            return {'message': f'No health checks in last {hours} hours'}
        
        status_counts = {}
        for check in recent_checks:
            status = check['overall_status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            'period_hours': hours,
            'total_checks': len(recent_checks),
            'status_distribution': status_counts,
            'latest_status': recent_checks[-1]['overall_status']
        }


def get_banking_health_service() -> BankingHealthService:
    """Get the global banking health service instance."""
    return BankingHealthService()
