"""
Banking API Performance Monitoring.

This module provides performance monitoring and optimization for the banking API,
ensuring sub-50ms response times and optimal performance at scale.
"""

import time
import statistics
from typing import Dict, List, Optional, Callable
from functools import wraps
from flask import current_app, request
from datetime import datetime, timedelta


class PerformanceMonitor:
    """
    Performance monitoring service for banking API operations.
    
    This service tracks response times, identifies performance bottlenecks,
    and provides optimization recommendations for the banking API.
    """
    
    def __init__(self):
        """Initialize the performance monitor."""
        self._metrics: Dict[str, List[float]] = {}
        self._operation_counts: Dict[str, int] = {}
        self._error_counts: Dict[str, int] = {}
        self._start_time = datetime.utcnow()
    
    def record_operation(self, operation: str, duration: float, success: bool = True):
        """
        Record an operation's performance metrics.
        
        Args:
            operation: Name of the operation
            duration: Duration in milliseconds
            success: Whether the operation was successful
        """
        if operation not in self._metrics:
            self._metrics[operation] = []
            self._operation_counts[operation] = 0
            self._error_counts[operation] = 0
        
        self._metrics[operation].append(duration)
        self._operation_counts[operation] += 1
        
        if not success:
            self._error_counts[operation] += 1
        
        # Keep only last 1000 measurements per operation
        if len(self._metrics[operation]) > 1000:
            self._metrics[operation] = self._metrics[operation][-1000:]
    
    def get_operation_stats(self, operation: str) -> Optional[Dict[str, float]]:
        """
        Get performance statistics for a specific operation.
        
        Args:
            operation: Name of the operation
            
        Returns:
            Dictionary with performance statistics or None if no data
        """
        if operation not in self._metrics or not self._metrics[operation]:
            return None
        
        durations = self._metrics[operation]
        
        return {
            'count': len(durations),
            'min': min(durations),
            'max': max(durations),
            'mean': statistics.mean(durations),
            'median': statistics.median(durations),
            'p95': statistics.quantiles(durations, n=20)[18],  # 95th percentile
            'p99': statistics.quantiles(durations, n=100)[98],  # 99th percentile
            'error_rate': self._error_counts[operation] / self._operation_counts[operation] if self._operation_counts[operation] > 0 else 0
        }
    
    def get_all_stats(self) -> Dict[str, Dict[str, float]]:
        """
        Get performance statistics for all operations.
        
        Returns:
            Dictionary mapping operation names to their statistics
        """
        return {
            operation: self.get_operation_stats(operation)
            for operation in self._metrics.keys()
        }
    
    def get_performance_summary(self) -> Dict[str, any]:
        """
        Get overall performance summary.
        
        Returns:
            Dictionary with overall performance metrics
        """
        all_stats = self.get_all_stats()
        
        if not all_stats:
            return {}
        
        # Calculate overall metrics
        all_durations = []
        total_operations = 0
        total_errors = 0
        
        for stats in all_stats.values():
            if stats:
                all_durations.extend(self._metrics[stats['operation']] if 'operation' in stats else [])
                total_operations += stats['count']
                total_errors += int(stats['error_rate'] * stats['count'])
        
        if not all_durations:
            return {}
        
        uptime = datetime.utcnow() - self._start_time
        
        return {
            'uptime_seconds': uptime.total_seconds(),
            'total_operations': total_operations,
            'total_errors': total_errors,
            'overall_error_rate': total_errors / total_operations if total_operations > 0 else 0,
            'overall_performance': {
                'min': min(all_durations),
                'max': max(all_durations),
                'mean': statistics.mean(all_durations),
                'median': statistics.median(all_durations),
                'p95': statistics.quantiles(all_durations, n=20)[18],
                'p99': statistics.quantiles(all_durations, n=100)[98]
            },
            'operations': all_stats
        }
    
    def identify_bottlenecks(self) -> List[Dict[str, any]]:
        """
        Identify performance bottlenecks.
        
        Returns:
            List of bottleneck descriptions with recommendations
        """
        bottlenecks = []
        all_stats = self.get_all_stats()
        
        for operation, stats in all_stats.items():
            if not stats:
                continue
            
            # Check for slow operations (>50ms average)
            if stats['mean'] > 50:
                bottlenecks.append({
                    'operation': operation,
                    'issue': 'Slow response time',
                    'current_performance': f"{stats['mean']:.2f}ms average",
                    'target': '50ms or less',
                    'recommendation': 'Consider caching, query optimization, or database indexing'
                })
            
            # Check for high error rates (>5%)
            if stats['error_rate'] > 0.05:
                bottlenecks.append({
                    'operation': operation,
                    'issue': 'High error rate',
                    'current_performance': f"{stats['error_rate']*100:.1f}% error rate",
                    'target': '5% or less',
                    'recommendation': 'Investigate error causes and improve error handling'
                })
            
            # Check for high variance (>2x mean)
            if stats['max'] > stats['mean'] * 2:
                bottlenecks.append({
                    'operation': operation,
                    'issue': 'High response time variance',
                    'current_performance': f"{stats['max']:.2f}ms max vs {stats['mean']:.2f}ms average",
                    'target': 'Consistent response times',
                    'recommendation': 'Investigate intermittent performance issues'
                })
        
        return bottlenecks


# Global performance monitor instance
performance_monitor = PerformanceMonitor()


def monitor_performance(operation: str):
    """
    Decorator to monitor performance of API operations.
    
    Args:
        operation: Name of the operation to monitor
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = (time.time() - start_time) * 1000  # Convert to milliseconds
                performance_monitor.record_operation(operation, duration, success)
        
        return wrapper
    return decorator


def get_performance_metrics() -> Dict[str, any]:
    """
    Get current performance metrics for the banking API.
    
    Returns:
        Dictionary with performance metrics and recommendations
    """
    summary = performance_monitor.get_performance_summary()
    bottlenecks = performance_monitor.identify_bottlenecks()
    
    return {
        'summary': summary,
        'bottlenecks': bottlenecks,
        'recommendations': _generate_recommendations(summary, bottlenecks)
    }


def _generate_recommendations(summary: Dict[str, any], bottlenecks: List[Dict[str, any]]) -> List[str]:
    """
    Generate performance optimization recommendations.
    
    Args:
        summary: Performance summary
        bottlenecks: Identified bottlenecks
        
    Returns:
        List of optimization recommendations
    """
    recommendations = []
    
    if not summary:
        return recommendations
    
    # Overall performance recommendations
    overall = summary.get('overall_performance', {})
    if overall.get('mean', 0) > 50:
        recommendations.append("Overall API response time exceeds 50ms target. Consider implementing caching strategies.")
    
    if summary.get('overall_error_rate', 0) > 0.05:
        recommendations.append("Overall error rate exceeds 5% target. Review error handling and system stability.")
    
    # Specific bottleneck recommendations
    for bottleneck in bottlenecks:
        recommendations.append(f"{bottleneck['operation']}: {bottleneck['recommendation']}")
    
    # General optimization recommendations
    if not recommendations:
        recommendations.append("Performance is within acceptable ranges. Continue monitoring for degradation.")
    
    return recommendations


# Performance monitoring middleware
class PerformanceMiddleware:
    """Middleware to automatically monitor API performance."""
    
    def __init__(self, app=None):
        """Initialize the middleware."""
        self.app = app
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the middleware with the Flask app."""
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Record request start time."""
        request.start_time = time.time()
    
    def after_request(self, response):
        """Record request performance metrics."""
        if hasattr(request, 'start_time'):
            duration = (time.time() - request.start_time) * 1000
            operation = f"{request.method}_{request.endpoint}"
            success = response.status_code < 400
            
            performance_monitor.record_operation(operation, duration, success)
        
        return response
