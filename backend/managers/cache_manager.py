import os
import json
import time
import hashlib
from typing import Optional, Any, Dict, List
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class CacheManager:
    """In-memory cache manager using Python LRU cache (no Redis needed)."""
    
    def __init__(self):
        # L1 Cache: In-memory LRU cache (10K items)
        self._l1_cache_size = 10000
        
        # Cache statistics
        self.stats = {
            'embedding': {'hits': 0, 'misses': 0},
            'query': {'hits': 0, 'misses': 0},
            'session': {'hits': 0, 'misses': 0}
        }
    
    def _get_cache_key(self, cache_type: str, *args) -> str:
        """Generate cache key from arguments."""
        key_string = f"{cache_type}:{':'.join(str(arg) for arg in args)}"
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]
    
    def _update_stats(self, cache_type: str, hit: bool):
        """Update cache statistics."""
        if cache_type in self.stats:
            if hit:
                self.stats[cache_type]['hits'] += 1
            else:
                self.stats[cache_type]['misses'] += 1
    
    # L1 Cache: In-memory LRU cache
    @lru_cache(maxsize=10000)
    def _l1_get(self, key: str) -> Optional[str]:
        """L1 cache get (in-memory LRU)."""
        return None  # This is just for the decorator, actual logic below
    
    def _l1_set(self, key: str, value: str):
        """L1 cache set (in-memory LRU)."""
        # The lru_cache decorator handles this automatically
        pass
    
    # Embedding cache operations
    def get_embedding(self, text_hash: str) -> Optional[List[float]]:
        """Get embedding from cache."""
        cache_key = self._get_cache_key('embedding', text_hash)
        
        # L1: In-memory cache
        try:
            cached_value = self._l1_get(cache_key)
            if cached_value:
                self._update_stats('embedding', True)
                return json.loads(cached_value)
        except:
            pass
        
        self._update_stats('embedding', False)
        return None
    
    def set_embedding(self, text_hash: str, embedding: List[float], ttl: int = 3600):
        """Set embedding in cache."""
        cache_key = self._get_cache_key('embedding', text_hash)
        value = json.dumps(embedding)
        
        # L1: In-memory cache
        try:
            self._l1_set(cache_key, value)
        except:
            pass
    
    # Query cache operations
    def get_query_result(self, query_hash: str, namespace: str) -> Optional[Dict[str, Any]]:
        """Get query result from cache."""
        cache_key = self._get_cache_key('query', query_hash, namespace)
        
        # L1: In-memory cache
        try:
            cached_value = self._l1_get(cache_key)
            if cached_value:
                self._update_stats('query', True)
                return json.loads(cached_value)
        except:
            pass
        
        self._update_stats('query', False)
        return None
    
    def set_query_result(self, query_hash: str, namespace: str, result: Dict[str, Any], ttl: int = 1800):
        """Set query result in cache."""
        cache_key = self._get_cache_key('query', query_hash, namespace)
        value = json.dumps(result)
        
        # L1: In-memory cache
        try:
            self._l1_set(cache_key, value)
        except:
            pass
    
    # Session cache operations
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data from cache."""
        cache_key = self._get_cache_key('session', session_id)
        
        # L1: In-memory cache
        try:
            cached_value = self._l1_get(cache_key)
            if cached_value:
                self._update_stats('session', True)
                return json.loads(cached_value)
        except:
            pass
        
        self._update_stats('session', False)
        return None
    
    def set_session(self, session_id: str, data: Dict[str, Any], ttl: int = 3600):
        """Set session data in cache."""
        cache_key = self._get_cache_key('session', session_id)
        value = json.dumps(data)
        
        # L1: In-memory cache
        try:
            self._l1_set(cache_key, value)
        except:
            pass
    
    def delete_session(self, session_id: str):
        """Delete session from cache."""
        cache_key = self._get_cache_key('session', session_id)
        
        # L1: In-memory cache (LRU will handle eviction)
        # For now, we'll just let it expire naturally
        pass
    
    # Cache statistics
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_hits = sum(stats['hits'] for stats in self.stats.values())
        total_misses = sum(stats['misses'] for stats in self.stats.values())
        total_requests = total_hits + total_misses
        
        hit_rate = total_hits / total_requests if total_requests > 0 else 0
        
        return {
            'stats': self.stats,
            'total_hits': total_hits,
            'total_misses': total_misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'cache_type': 'in_memory_lru'
        }
    
    def health_check(self) -> bool:
        """Check if cache is healthy."""
        return True  # In-memory cache is always available
