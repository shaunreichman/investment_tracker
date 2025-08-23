"""
Banking Cache Service Tests

This module tests the BankingCacheService caching functionality.
Focus: Memory cache operations and cache management (Redis is not currently integrated).

Other aspects covered elsewhere:
- Health monitoring: test_banking_health_service.py
- Repository operations: test_bank_repository.py, test_bank_account_repository.py
- API operations: test_bank_controller.py, test_bank_account_controller.py
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import json
import hashlib

from src.banking.services.banking_cache_service import BankingCacheService, cache_banking_operation


class TestBankingCacheService:
    """Test suite for BankingCacheService - Memory cache functionality only"""
    
    @pytest.fixture
    def cache_service(self):
        """Cache service with memory cache only (Redis not integrated)."""
        return BankingCacheService(redis_url="redis://localhost:6379")
    
    # ============================================================================
    # INITIALIZATION TESTS
    # ============================================================================
    
    def test_cache_service_initialization(self, cache_service):
        """Test cache service initialization with memory cache."""
        assert cache_service.default_ttl == 300
        assert cache_service.memory_cache == {}
        assert cache_service.memory_cache_ttl == {}
        # Redis client will be None since Redis is not integrated
    
    def test_cache_service_initialization_custom_ttl(self):
        """Test cache service initialization with custom TTL."""
        service = BankingCacheService(default_ttl=600)
        assert service.default_ttl == 600
    
    # ============================================================================
    # CACHE KEY GENERATION TESTS
    # ============================================================================
    
    def test_get_cache_key_consistency(self, cache_service):
        """Test cache key generation is consistent for same inputs."""
        key1 = cache_service.get_cache_key("test", "arg1", "arg2", kw1="val1", kw2="val2")
        key2 = cache_service.get_cache_key("test", "arg1", "arg2", kw1="val1", kw2="val2")
        
        assert key1 == key2
        assert key1.startswith("banking:test:")
    
    def test_get_cache_key_different_inputs(self, cache_service):
        """Test cache key generation differs for different inputs."""
        key1 = cache_service.get_cache_key("test", "arg1", "arg2")
        key2 = cache_service.get_cache_key("test", "arg1", "arg3")
        
        assert key1 != key2
    
    def test_get_cache_key_with_kwargs(self, cache_service):
        """Test cache key generation with keyword arguments."""
        key1 = cache_service.get_cache_key("banks", entity_id=123, currency="AUD")
        key2 = cache_service.get_cache_key("banks", entity_id=123, currency="AUD")
        
        assert key1.startswith("banking:banks:")
        assert key1 == key2  # Same inputs should generate same key
        assert len(key1) > len("banking:banks:")  # Should have hash suffix
    
    # ============================================================================
    # CACHE GET OPERATIONS
    # ============================================================================
    
    def test_get_from_memory_cache_success(self, cache_service):
        """Test successful get operation from memory cache."""
        test_data = {"name": "Test Bank", "country": "AU"}
        cache_service.memory_cache["test_key"] = test_data
        cache_service.memory_cache_ttl["test_key"] = datetime.now().timestamp() + 300
        
        result = cache_service.get("test_key")
        
        assert result == test_data
    
    def test_get_from_memory_cache_expired(self, cache_service):
        """Test get operation handles expired memory cache entries."""
        # Setup expired memory cache
        test_data = {"name": "Test Bank"}
        cache_service.memory_cache["test_key"] = test_data
        cache_service.memory_cache_ttl["test_key"] = datetime.now().timestamp() - 100  # Expired
        
        result = cache_service.get("test_key")
        
        assert result is None
        assert "test_key" not in cache_service.memory_cache
        assert "test_key" not in cache_service.memory_cache_ttl
    
    def test_get_cache_miss(self, cache_service):
        """Test get operation when key doesn't exist."""
        result = cache_service.get("nonexistent_key")
        
        assert result is None
    
    # ============================================================================
    # CACHE SET OPERATIONS
    # ============================================================================
    
    def test_set_in_memory_success(self, cache_service):
        """Test successful set operation in memory cache."""
        test_data = {"name": "Test Bank", "country": "AU"}
        
        result = cache_service.set("test_key", test_data, ttl=600)
        
        assert result is True
        assert "test_key" in cache_service.memory_cache
        assert "test_key" in cache_service.memory_cache_ttl
    
    def test_set_with_default_ttl(self, cache_service):
        """Test set operation uses default TTL when none specified."""
        test_data = {"name": "Test Bank"}
        
        result = cache_service.set("test_key", test_data)
        
        assert result is True
        assert "test_key" in cache_service.memory_cache
        assert "test_key" in cache_service.memory_cache_ttl
    
    def test_set_memory_failure(self, cache_service):
        """Test set operation handles memory cache failures."""
        # Force memory cache to fail by making it read-only
        cache_service.memory_cache = None
        
        result = cache_service.set("test_key", {"name": "Test Bank"})
        
        assert result is False
    
    # ============================================================================
    # CACHE DELETE OPERATIONS
    # ============================================================================
    
    def test_delete_from_memory_success(self, cache_service):
        """Test successful delete operation from memory cache."""
        # Setup memory cache
        cache_service.memory_cache["test_key"] = {"name": "Test Bank"}
        cache_service.memory_cache_ttl["test_key"] = datetime.now().timestamp() + 300
        
        result = cache_service.delete("test_key")
        
        assert result is True
        assert "test_key" not in cache_service.memory_cache
        assert "test_key" not in cache_service.memory_cache_ttl
    
    def test_delete_nonexistent_key(self, cache_service):
        """Test delete operation for nonexistent key."""
        result = cache_service.delete("nonexistent_key")
        
        assert result is True  # Still considered successful
    
    # ============================================================================
    # PATTERN INVALIDATION TESTS
    # ============================================================================
    
    def test_invalidate_pattern_memory_success(self, cache_service):
        """Test successful pattern invalidation in memory cache."""
        # Setup memory cache with matching keys
        cache_service.memory_cache["banking:banks:1"] = {"name": "Bank 1"}
        cache_service.memory_cache["banking:banks:2"] = {"name": "Bank 2"}
        cache_service.memory_cache["other:key"] = {"name": "Other"}
        cache_service.memory_cache_ttl["banking:banks:1"] = datetime.now().timestamp() + 300
        cache_service.memory_cache_ttl["banking:banks:2"] = datetime.now().timestamp() + 300
        
        invalidated_count = cache_service.invalidate_pattern("banking:banks:*")
        
        assert invalidated_count == 2
        assert "banking:banks:1" not in cache_service.memory_cache
        assert "banking:banks:2" not in cache_service.memory_cache
        assert "other:key" in cache_service.memory_cache  # Should remain
    
    def test_invalidate_pattern_no_matches(self, cache_service):
        """Test pattern invalidation when no keys match."""
        # Setup memory cache with non-matching keys
        cache_service.memory_cache["other:key"] = {"name": "Other"}
        cache_service.memory_cache_ttl["other:key"] = datetime.now().timestamp() + 300
        
        invalidated_count = cache_service.invalidate_pattern("banking:banks:*")
        
        assert invalidated_count == 0
        assert "other:key" in cache_service.memory_cache  # Should remain
    
    # ============================================================================
    # BANKING EVENT INVALIDATION TESTS
    # ============================================================================
    
    def test_invalidate_banking_events_basic(self, cache_service):
        """Test basic banking event invalidation."""
        # Setup some cache keys
        cache_service.memory_cache["banking:banks:1"] = {"name": "Bank 1"}
        cache_service.memory_cache["banking:bank_accounts:1"] = {"name": "Account 1"}
        cache_service.memory_cache["other:key"] = {"name": "Other"}
        
        cache_service.invalidate_banking_events("created")
        
        # Should invalidate banking-related keys
        assert "banking:banks:1" not in cache_service.memory_cache
        assert "banking:bank_accounts:1" not in cache_service.memory_cache
        assert "other:key" in cache_service.memory_cache  # Should remain
    
    def test_invalidate_banking_events_with_entity_id(self, cache_service):
        """Test banking event invalidation with entity ID."""
        # Setup entity-specific cache keys
        cache_service.memory_cache["banking:entity:123:accounts"] = {"accounts": []}
        cache_service.memory_cache["banking:entity:456:accounts"] = {"accounts": []}
        cache_service.memory_cache["other:key"] = {"name": "Other"}
        
        cache_service.invalidate_banking_events("updated", entity_id=123)
        
        # Should invalidate entity 123 keys
        assert "banking:entity:123:accounts" not in cache_service.memory_cache
        assert "banking:entity:456:accounts" in cache_service.memory_cache  # Should remain
        assert "other:key" in cache_service.memory_cache  # Should remain
    
    def test_invalidate_banking_events_with_bank_id(self, cache_service):
        """Test banking event invalidation with bank ID."""
        # Setup bank-specific cache keys
        cache_service.memory_cache["banking:bank:456:accounts"] = {"accounts": []}
        cache_service.memory_cache["banking:bank:789:accounts"] = {"accounts": []}
        cache_service.memory_cache["other:key"] = {"name": "Other"}
        
        cache_service.invalidate_banking_events("deleted", bank_id=456)
        
        # Should invalidate bank 456 keys
        assert "banking:bank:456:accounts" not in cache_service.memory_cache
        assert "banking:bank:789:accounts" in cache_service.memory_cache  # Should remain
        assert "other:key" in cache_service.memory_cache  # Should remain
    
    # ============================================================================
    # CACHE WARMING TESTS
    # ============================================================================
    
    def test_warm_cache_success(self, cache_service):
        """Test successful cache warming."""
        common_queries = [
            {"prefix": "banks", "args": ["AU"], "value": [{"id": 1, "name": "Bank 1"}]},
            {"prefix": "accounts", "args": [123], "value": [{"id": 1, "account": "ACC1"}]}
        ]
        
        warmed_count = cache_service.warm_cache(common_queries)
        
        assert warmed_count == 2
        assert len(cache_service.memory_cache) == 2
    
    def test_warm_cache_partial_failure(self, cache_service):
        """Test cache warming handles partial failures."""
        common_queries = [
            {"prefix": "banks", "args": ["AU"], "value": [{"id": 1, "name": "Bank 1"}]},
            {"prefix": "invalid", "args": [], "value": None}  # This will fail
        ]
        
        warmed_count = cache_service.warm_cache(common_queries)
        
        assert warmed_count == 1  # Only one query succeeded
    
    # ============================================================================
    # CACHE STATISTICS TESTS
    # ============================================================================
    
    def test_get_cache_stats_memory_only(self, cache_service):
        """Test cache statistics for memory-only cache."""
        # Add some data to cache
        cache_service.memory_cache["key1"] = "value1"
        cache_service.memory_cache["key2"] = "value2"
        
        stats = cache_service.get_cache_stats()
        
        assert 'memory_cache_size' in stats
        assert 'memory_cache_keys' in stats
        assert 'redis_available' in stats
        assert stats['memory_cache_size'] == 2
        assert stats['redis_available'] is False  # Redis not integrated
        assert 'redis_info' not in stats
    
    # ============================================================================
    # CACHE CLEAR TESTS
    # ============================================================================
    
    def test_clear_all_success(self, cache_service):
        """Test successful clear all operation."""
        # Setup memory cache
        cache_service.memory_cache["key1"] = "value1"
        cache_service.memory_cache_ttl["key1"] = datetime.now().timestamp() + 300
        
        result = cache_service.clear_all()
        
        assert result is True
        assert len(cache_service.memory_cache) == 0
        assert len(cache_service.memory_cache_ttl) == 0
    
    # ============================================================================
    # CACHE DECORATOR TESTS
    # ============================================================================
    
    def test_cache_banking_operation_decorator(self, cache_service):
        """Test the cache decorator functionality."""
        @cache_banking_operation(cache_service, "test_operation", ttl=600)
        def test_function(param1, param2):
            return f"result_{param1}_{param2}"
        
        # First call should execute function and cache result
        result1 = test_function("a", "b")
        assert result1 == "result_a_b"
        assert len(cache_service.memory_cache) == 1
        
        # Second call should return cached result
        result2 = test_function("a", "b")
        assert result2 == "result_a_b"
        assert len(cache_service.memory_cache) == 1
    
    def test_cache_banking_operation_different_params(self, cache_service):
        """Test cache decorator with different parameters."""
        @cache_banking_operation(cache_service, "test_operation")
        def test_function(param1, param2):
            return f"result_{param1}_{param2}"
        
        # Different parameters should create different cache keys
        result1 = test_function("a", "b")
        result2 = test_function("x", "y")
        
        assert result1 == "result_a_b"
        assert result2 == "result_x_y"
        assert len(cache_service.memory_cache) == 2
    
    # ============================================================================
    # GLOBAL SERVICE INSTANCE TESTS
    # ============================================================================
    
    def test_get_banking_cache_service_singleton(self):
        """Test global service instance singleton pattern."""
        from src.banking.services.banking_cache_service import get_banking_cache_service
        
        # First call should create new instance
        service1 = get_banking_cache_service()
        assert service1 is not None
        
        # Second call should return same instance
        service2 = get_banking_cache_service()
        assert service2 is service1
