"""
Banking Cache Service for Phase 6.

This service implements sophisticated caching strategies for banking data,
providing significant performance improvements for production workloads.
"""

import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import logging
from functools import wraps

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    redis = None

logger = logging.getLogger(__name__)


class BankingCacheService:
    """
    Advanced caching service for banking operations.
    
    This service provides multiple caching strategies:
    - Redis-based caching for high-performance data access
    - In-memory caching for frequently accessed data
    - Intelligent cache invalidation based on banking events
    - Cache warming for common query patterns
    """
    
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 300):
        """
        Initialize the banking cache service.
        
        Args:
            redis_url: Redis connection URL
            default_ttl: Default cache TTL in seconds (5 minutes)
        """
        self.default_ttl = default_ttl
        self.redis_client = None
        self.memory_cache = {}
        self.memory_cache_ttl = {}
        
        if REDIS_AVAILABLE:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                logger.info("✅ Redis cache initialized successfully")
            except Exception as e:
                logger.warning(f"⚠️ Redis cache unavailable, falling back to memory: {e}")
                self.redis_client = None
        else:
            logger.warning("⚠️ Redis not available, using memory cache only")
    
    def get_cache_key(self, prefix: str, *args, **kwargs) -> str:
        """
        Generate a consistent cache key for given parameters.
        
        Args:
            prefix: Cache key prefix
            *args: Positional arguments to include in key
            **kwargs: Keyword arguments to include in key
            
        Returns:
            Consistent cache key string
        """
        # Create a hash of the arguments for consistent key generation
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        key_hash = hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
        return f"banking:{prefix}:{key_hash}"
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache (Redis first, then memory).
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        # Try Redis first
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    logger.debug(f"✅ Cache hit (Redis): {key}")
                    return json.loads(value)
            except Exception as e:
                logger.warning(f"⚠️ Redis get error: {e}")
        
        # Fall back to memory cache
        if key in self.memory_cache:
            ttl = self.memory_cache_ttl.get(key, 0)
            if datetime.now().timestamp() < ttl:
                logger.debug(f"✅ Cache hit (Memory): {key}")
                return self.memory_cache[key]
            else:
                # Expired, remove from memory cache
                del self.memory_cache[key]
                del self.memory_cache_ttl[key]
        
        logger.debug(f"❌ Cache miss: {key}")
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Set value in cache (both Redis and memory).
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (uses default if None)
            
        Returns:
            True if successful, False otherwise
        """
        ttl = ttl or self.default_ttl
        success = True
        
        # Set in Redis
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json.dumps(value))
                logger.debug(f"✅ Cached in Redis: {key} (TTL: {ttl}s)")
            except Exception as e:
                logger.warning(f"⚠️ Redis set error: {e}")
                success = False
        
        # Set in memory cache
        try:
            self.memory_cache[key] = value
            self.memory_cache_ttl[key] = datetime.now().timestamp() + ttl
            logger.debug(f"✅ Cached in Memory: {key} (TTL: {ttl}s)")
        except Exception as e:
            logger.warning(f"⚠️ Memory cache set error: {e}")
            success = False
        
        return success
    
    def delete(self, key: str) -> bool:
        """
        Delete value from cache (both Redis and memory).
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Delete from Redis
        if self.redis_client:
            try:
                self.redis_client.delete(key)
                logger.debug(f"✅ Deleted from Redis: {key}")
            except Exception as e:
                logger.warning(f"⚠️ Redis delete error: {e}")
                success = False
        
        # Delete from memory cache
        try:
            if key in self.memory_cache:
                del self.memory_cache[key]
            if key in self.memory_cache_ttl:
                del self.memory_cache_ttl[key]
            logger.debug(f"✅ Deleted from Memory: {key}")
        except Exception as e:
            logger.warning(f"⚠️ Memory cache delete error: {e}")
            success = False
        
        return success
    
    def invalidate_pattern(self, pattern: str) -> int:
        """
        Invalidate all cache keys matching a pattern.
        
        Args:
            pattern: Redis pattern to match (e.g., "banking:banks:*")
            
        Returns:
            Number of keys invalidated
        """
        invalidated_count = 0
        
        # Invalidate Redis keys
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                if keys:
                    self.redis_client.delete(*keys)
                    invalidated_count += len(keys)
                    logger.info(f"✅ Invalidated {len(keys)} Redis keys matching: {pattern}")
            except Exception as e:
                logger.warning(f"⚠️ Redis pattern invalidation error: {e}")
        
        # Invalidate memory cache keys
        try:
            memory_keys = [k for k in self.memory_cache.keys() if pattern.replace('*', '') in k]
            for key in memory_keys:
                del self.memory_cache[key]
                if key in self.memory_cache_ttl:
                    del self.memory_cache_ttl[key]
            invalidated_count += len(memory_keys)
            logger.info(f"✅ Invalidated {len(memory_keys)} memory keys matching: {pattern}")
        except Exception as e:
            logger.warning(f"⚠️ Memory cache pattern invalidation error: {e}")
        
        return invalidated_count
    
    def invalidate_banking_events(self, event_type: str, entity_id: Optional[int] = None, bank_id: Optional[int] = None):
        """
        Invalidate cache based on banking events.
        
        Args:
            event_type: Type of banking event (created, updated, deleted, etc.)
            entity_id: Entity ID affected by the event
            bank_id: Bank ID affected by the event
        """
        patterns_to_invalidate = []
        
        # Common banking patterns
        patterns_to_invalidate.extend([
            "banking:banks:*",
            "banking:bank_accounts:*",
            "banking:summary:*",
        ])
        
        # Entity-specific patterns
        if entity_id:
            patterns_to_invalidate.extend([
                f"banking:entity:{entity_id}:*",
                f"banking:accounts:entity:{entity_id}:*",
            ])
        
        # Bank-specific patterns
        if bank_id:
            patterns_to_invalidate.extend([
                f"banking:bank:{bank_id}:*",
                f"banking:accounts:bank:{bank_id}:*",
            ])
        
        # Event-specific patterns
        if event_type in ['created', 'updated', 'deleted']:
            patterns_to_invalidate.extend([
                f"banking:recent_{event_type}:*",
                f"banking:activity:*",
            ])
        
        # Invalidate all matching patterns
        total_invalidated = 0
        for pattern in patterns_to_invalidate:
            total_invalidated += self.invalidate_pattern(pattern)
        
        logger.info(f"✅ Invalidated {total_invalidated} cache keys for {event_type} event")
    
    def warm_cache(self, common_queries: List[Dict[str, Any]]) -> int:
        """
        Warm cache with common query patterns.
        
        Args:
            common_queries: List of common queries to pre-cache
            
        Returns:
            Number of queries successfully cached
        """
        warmed_count = 0
        
        for query in common_queries:
            try:
                key = self.get_cache_key(query['prefix'], *query.get('args', []), **query.get('kwargs', {}))
                if query.get('value') is not None:
                    self.set(key, query['value'], query.get('ttl', self.default_ttl))
                    warmed_count += 1
                    logger.debug(f"✅ Cache warmed: {key}")
            except Exception as e:
                logger.warning(f"⚠️ Cache warming failed for query {query}: {e}")
        
        logger.info(f"✅ Cache warmed with {warmed_count} queries")
        return warmed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.
        
        Returns:
            Dictionary with cache statistics
        """
        stats = {
            'memory_cache_size': len(self.memory_cache),
            'memory_cache_keys': list(self.memory_cache.keys()),
            'redis_available': self.redis_client is not None,
        }
        
        if self.redis_client:
            try:
                info = self.redis_client.info()
                stats['redis_info'] = {
                    'used_memory': info.get('used_memory_human', 'N/A'),
                    'connected_clients': info.get('connected_clients', 'N/A'),
                    'total_commands_processed': info.get('total_commands_processed', 'N/A'),
                }
            except Exception as e:
                stats['redis_info'] = {'error': str(e)}
        
        return stats
    
    def clear_all(self) -> bool:
        """
        Clear all cache data (both Redis and memory).
        
        Returns:
            True if successful, False otherwise
        """
        success = True
        
        # Clear Redis cache
        if self.redis_client:
            try:
                self.redis_client.flushdb()
                logger.info("✅ Redis cache cleared")
            except Exception as e:
                logger.warning(f"⚠️ Redis clear error: {e}")
                success = False
        
        # Clear memory cache
        try:
            self.memory_cache.clear()
            self.memory_cache_ttl.clear()
            logger.info("✅ Memory cache cleared")
        except Exception as e:
            logger.warning(f"⚠️ Memory cache clear error: {e}")
            success = False
        
        return success


def cache_banking_operation(cache_service: BankingCacheService, prefix: str, ttl: int = 300):
    """
    Decorator for caching banking operations.
    
    Args:
        cache_service: BankingCacheService instance
        prefix: Cache key prefix
        ttl: Cache TTL in seconds
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = cache_service.get_cache_key(prefix, *args, **kwargs)
            
            # Try to get from cache
            cached_result = cache_service.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache_service.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator


# Global cache service instance
_banking_cache_service = None


def get_banking_cache_service() -> BankingCacheService:
    """Get the global banking cache service instance."""
    global _banking_cache_service
    if _banking_cache_service is None:
        _banking_cache_service = BankingCacheService()
    return _banking_cache_service
