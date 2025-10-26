"""
Multi-Level Cache Manager for RAGFlow Enhanced Backend
Implements L1 (In-memory LRU), L2 (Redis), L3 (Supabase Storage) caching
"""

import os
import json
import time
import hashlib
import logging
from typing import Any, Optional, Dict, Tuple
from datetime import datetime, timedelta
from collections import OrderedDict
import asyncio

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

logger = logging.getLogger(__name__)

class LRUCache:
    """L1 Cache: In-memory LRU cache with configurable size"""
    
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.cache = OrderedDict()
        self.hits = 0
        self.misses = 0
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L1 cache"""
        if key in self.cache:
            # Move to end (most recently used)
            value = self.cache.pop(key)
            self.cache[key] = value
            self.hits += 1
            self.access_times[key] = time.time()
            return value
        else:
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> None:
        """Set value in L1 cache"""
        if key in self.cache:
            # Update existing
            self.cache.pop(key)
        elif len(self.cache) >= self.max_size:
            # Remove least recently used
            self.cache.popitem(last=False)
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def delete(self, key: str) -> bool:
        """Delete key from L1 cache"""
        if key in self.cache:
            del self.cache[key]
            if key in self.access_times:
                del self.access_times[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all L1 cache"""
        self.cache.clear()
        self.access_times.clear()
        self.hits = 0
        self.misses = 0
    
    def stats(self) -> Dict:
        """Get L1 cache statistics"""
        total_requests = self.hits + self.misses
        hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(hit_rate, 2),
            "total_requests": total_requests
        }

class RedisCache:
    """L2 Cache: Redis cache with connection pooling"""
    
    def __init__(self, redis_url: str = None):
        self.redis_client = None
        self.connected = False
        self.hits = 0
        self.misses = 0
        
        if REDIS_AVAILABLE and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url, decode_responses=True)
                # Test connection
                self.redis_client.ping()
                self.connected = True
                logger.info("✅ Redis L2 cache connected")
            except Exception as e:
                logger.warning(f"Redis L2 cache connection failed: {e}")
                self.connected = False
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L2 cache"""
        if not self.connected:
            return None
        
        try:
            value = self.redis_client.get(key)
            if value is not None:
                self.hits += 1
                return json.loads(value)
            else:
                self.misses += 1
                return None
        except Exception as e:
            logger.error(f"Redis L2 cache get error: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in L2 cache"""
        if not self.connected:
            return False
        
        try:
            serialized_value = json.dumps(value)
            self.redis_client.setex(key, ttl, serialized_value)
            return True
        except Exception as e:
            logger.error(f"Redis L2 cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from L2 cache"""
        if not self.connected:
            return False
        
        try:
            result = self.redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Redis L2 cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all L2 cache"""
        if not self.connected:
            return False
        
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            logger.error(f"Redis L2 cache clear error: {e}")
            return False
    
    def stats(self) -> Dict:
        """Get L2 cache statistics"""
        if not self.connected:
            return {"connected": False}
        
        try:
            info = self.redis_client.info()
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "connected": True,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "memory_used": info.get("used_memory_human", "N/A"),
                "keys": info.get("db0", {}).get("keys", 0)
            }
        except Exception as e:
            logger.error(f"Redis L2 cache stats error: {e}")
            return {"connected": False, "error": str(e)}

class SupabaseCache:
    """L3 Cache: Supabase Storage for persistent caching"""
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        self.supabase_client = None
        self.connected = False
        self.hits = 0
        self.misses = 0
        
        if SUPABASE_AVAILABLE and supabase_url and supabase_key:
            try:
                self.supabase_client = create_client(supabase_url, supabase_key)
                self.connected = True
                logger.info("✅ Supabase L3 cache connected")
            except Exception as e:
                logger.warning(f"Supabase L3 cache connection failed: {e}")
                self.connected = False
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key for Supabase storage"""
        return f"cache/{hashlib.md5(key.encode()).hexdigest()}.json"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from L3 cache"""
        if not self.connected:
            return None
        
        try:
            cache_key = self._get_cache_key(key)
            result = self.supabase_client.storage.from_("ragflow-cache").download(cache_key)
            
            if result:
                self.hits += 1
                return json.loads(result)
            else:
                self.misses += 1
                return None
        except Exception as e:
            logger.error(f"Supabase L3 cache get error: {e}")
            self.misses += 1
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in L3 cache"""
        if not self.connected:
            return False
        
        try:
            cache_key = self._get_cache_key(key)
            cache_data = {
                "value": value,
                "expires_at": (datetime.utcnow() + timedelta(seconds=ttl)).isoformat(),
                "created_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = json.dumps(cache_data)
            result = self.supabase_client.storage.from_("ragflow-cache").upload(
                cache_key, 
                serialized_data.encode(),
                file_options={"content-type": "application/json"}
            )
            return result is not None
        except Exception as e:
            logger.error(f"Supabase L3 cache set error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from L3 cache"""
        if not self.connected:
            return False
        
        try:
            cache_key = self._get_cache_key(key)
            result = self.supabase_client.storage.from_("ragflow-cache").remove([cache_key])
            return result is not None
        except Exception as e:
            logger.error(f"Supabase L3 cache delete error: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all L3 cache"""
        if not self.connected:
            return False
        
        try:
            # List all cache files and delete them
            files = self.supabase_client.storage.from_("ragflow-cache").list()
            cache_files = [f["name"] for f in files if f["name"].startswith("cache/")]
            
            if cache_files:
                result = self.supabase_client.storage.from_("ragflow-cache").remove(cache_files)
                return result is not None
            return True
        except Exception as e:
            logger.error(f"Supabase L3 cache clear error: {e}")
            return False
    
    def stats(self) -> Dict:
        """Get L3 cache statistics"""
        if not self.connected:
            return {"connected": False}
        
        try:
            files = self.supabase_client.storage.from_("ragflow-cache").list()
            cache_files = [f for f in files if f["name"].startswith("cache/")]
            
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                "connected": True,
                "hits": self.hits,
                "misses": self.misses,
                "hit_rate": round(hit_rate, 2),
                "total_requests": total_requests,
                "files_count": len(cache_files),
                "total_size": sum(f.get("metadata", {}).get("size", 0) for f in cache_files)
            }
        except Exception as e:
            logger.error(f"Supabase L3 cache stats error: {e}")
            return {"connected": False, "error": str(e)}

class MultiLevelCache:
    """Multi-level cache manager with L1, L2, L3 caching"""
    
    def __init__(self, l1_size: int = 10000, redis_url: str = None, 
                 supabase_url: str = None, supabase_key: str = None):
        self.l1_cache = LRUCache(max_size=l1_size)
        self.l2_cache = RedisCache(redis_url)
        self.l3_cache = SupabaseCache(supabase_url, supabase_key)
        
        self.total_requests = 0
        self.cache_hits = 0
        self.cache_misses = 0
        
        logger.info("🚀 Multi-level cache system initialized")
    
    async def get(self, key: str) -> Tuple[Optional[Any], str]:
        """Get value from multi-level cache with cache level info"""
        start_time = time.time()
        self.total_requests += 1
        
        # L1 Cache (In-memory LRU) - <1ms
        value = self.l1_cache.get(key)
        if value is not None:
            self.cache_hits += 1
            response_time = (time.time() - start_time) * 1000
            logger.debug(f"L1 cache hit for {key} ({response_time:.2f}ms)")
            return value, "L1"
        
        # L2 Cache (Redis) - <10ms
        value = self.l2_cache.get(key)
        if value is not None:
            # Store in L1 for faster future access
            self.l1_cache.set(key, value)
            self.cache_hits += 1
            response_time = (time.time() - start_time) * 1000
            logger.debug(f"L2 cache hit for {key} ({response_time:.2f}ms)")
            return value, "L2"
        
        # L3 Cache (Supabase Storage) - <100ms
        value = self.l3_cache.get(key)
        if value is not None:
            # Store in L1 and L2 for faster future access
            self.l1_cache.set(key, value)
            self.l2_cache.set(key, value)
            self.cache_hits += 1
            response_time = (time.time() - start_time) * 1000
            logger.debug(f"L3 cache hit for {key} ({response_time:.2f}ms)")
            return value, "L3"
        
        # Cache miss
        self.cache_misses += 1
        response_time = (time.time() - start_time) * 1000
        logger.debug(f"Cache miss for {key} ({response_time:.2f}ms)")
        return None, "MISS"
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in all cache levels"""
        try:
            # Set in all levels
            self.l1_cache.set(key, value, ttl)
            self.l2_cache.set(key, value, ttl)
            self.l3_cache.set(key, value, ttl)
            
            logger.debug(f"Value set in all cache levels for {key}")
            return True
        except Exception as e:
            logger.error(f"Error setting cache value for {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from all cache levels"""
        try:
            l1_result = self.l1_cache.delete(key)
            l2_result = self.l2_cache.delete(key)
            l3_result = self.l3_cache.delete(key)
            
            logger.debug(f"Value deleted from all cache levels for {key}")
            return l1_result or l2_result or l3_result
        except Exception as e:
            logger.error(f"Error deleting cache value for {key}: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache levels"""
        try:
            self.l1_cache.clear()
            self.l2_cache.clear()
            self.l3_cache.clear()
            
            logger.info("All cache levels cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing caches: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get comprehensive cache statistics"""
        l1_stats = self.l1_cache.stats()
        l2_stats = self.l2_cache.stats()
        l3_stats = self.l3_cache.stats()
        
        total_requests = self.total_requests
        overall_hit_rate = (self.cache_hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "overall": {
                "total_requests": total_requests,
                "cache_hits": self.cache_hits,
                "cache_misses": self.cache_misses,
                "hit_rate": round(overall_hit_rate, 2)
            },
            "l1_cache": l1_stats,
            "l2_cache": l2_stats,
            "l3_cache": l3_stats
        }
    
    def health_check(self) -> Dict:
        """Check health of all cache levels"""
        return {
            "l1_cache": {"status": "healthy", "size": len(self.l1_cache.cache)},
            "l2_cache": {"status": "healthy" if self.l2_cache.connected else "disconnected"},
            "l3_cache": {"status": "healthy" if self.l3_cache.connected else "disconnected"}
        }

# Global cache instance
cache_manager = None

def initialize_cache_manager():
    """Initialize the global cache manager"""
    global cache_manager
    
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    cache_manager = MultiLevelCache(
        l1_size=10000,
        redis_url=redis_url,
        supabase_url=supabase_url,
        supabase_key=supabase_key
    )
    
    logger.info("✅ Multi-level cache manager initialized")
    return cache_manager

def get_cache_manager() -> MultiLevelCache:
    """Get the global cache manager instance"""
    global cache_manager
    if cache_manager is None:
        cache_manager = initialize_cache_manager()
    return cache_manager
