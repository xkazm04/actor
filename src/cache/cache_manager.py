"""
Cache Manager - Manages caching of search results and content.
Uses Apify Key-Value Store for persistent caching with TTL.
"""

import hashlib
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from apify import Actor


class CacheManager:
    """
    Manages caching of search results and content.
    Uses Apify Key-Value Store for persistence.
    """
    
    def __init__(self, default_ttl_hours: int = 24):
        """
        Initialize cache manager.
        
        Args:
            default_ttl_hours: Default TTL in hours (24-48 recommended)
        """
        self.default_ttl_hours = default_ttl_hours
        self.cache_prefix = "cache_"
    
    def _generate_cache_key(self, category: str, identifier: str) -> str:
        """
        Generate cache key from category and identifier.
        
        Args:
            category: Cache category (e.g., 'search', 'content')
            identifier: Unique identifier (query, URL, etc.)
            
        Returns:
            Cache key string
        """
        # Create hash for long identifiers
        if len(identifier) > 100:
            identifier_hash = hashlib.md5(identifier.encode()).hexdigest()
            key = f"{self.cache_prefix}{category}_{identifier_hash}"
        else:
            # Sanitize identifier for key
            safe_id = identifier.replace(' ', '_').replace('/', '_')[:100]
            key = f"{self.cache_prefix}{category}_{safe_id}"
        
        return key
    
    async def get(
        self,
        category: str,
        identifier: str,
        ttl_hours: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Get cached value.
        
        Args:
            category: Cache category
            identifier: Cache identifier
            ttl_hours: TTL override (optional)
            
        Returns:
            Cached data or None if not found/expired
        """
        cache_key = self._generate_cache_key(category, identifier)
        ttl = ttl_hours or self.default_ttl_hours
        
        try:
            cached_data = await Actor.get_value(cache_key)
            
            if cached_data is None:
                return None
            
            # Check expiration
            if 'expires_at' in cached_data:
                expires_at = datetime.fromisoformat(cached_data['expires_at'])
                if datetime.now() > expires_at:
                    # Cache expired, remove it
                    await Actor.set_value(cache_key, None)
                    return None
            
            # Return cached value
            return cached_data.get('value')
            
        except Exception as e:
            Actor.log.warning(f"Cache get failed for {cache_key}: {e}")
            return None
    
    async def set(
        self,
        category: str,
        identifier: str,
        value: Any,
        ttl_hours: Optional[int] = None
    ):
        """
        Set cached value.
        
        Args:
            category: Cache category
            identifier: Cache identifier
            value: Value to cache
            ttl_hours: TTL override (optional)
        """
        cache_key = self._generate_cache_key(category, identifier)
        ttl = ttl_hours or self.default_ttl_hours
        
        try:
            expires_at = datetime.now() + timedelta(hours=ttl)
            
            cache_entry = {
                'value': value,
                'cached_at': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat(),
                'category': category,
                'identifier': identifier[:200]  # Store truncated identifier
            }
            
            await Actor.set_value(cache_key, cache_entry)
            Actor.log.debug(f"Cached {category}:{identifier[:50]} (expires: {expires_at.isoformat()})")
            
        except Exception as e:
            Actor.log.warning(f"Cache set failed for {cache_key}: {e}")
    
    async def invalidate(self, category: str, identifier: Optional[str] = None):
        """
        Invalidate cache entry or all entries in category.
        
        Args:
            category: Cache category
            identifier: Specific identifier (None = invalidate all in category)
        """
        if identifier:
            cache_key = self._generate_cache_key(category, identifier)
            try:
                await Actor.set_value(cache_key, None)
                Actor.log.info(f"Invalidated cache: {category}:{identifier[:50]}")
            except Exception as e:
                Actor.log.warning(f"Cache invalidation failed: {e}")
        else:
            # Invalidate all entries in category (would need to iterate through keys)
            Actor.log.warning(f"Bulk invalidation for category {category} not fully implemented")
    
    async def get_search_results(
        self,
        query: str,
        api: str,
        ttl_hours: int = 24
    ) -> Optional[list]:
        """
        Get cached search results.
        
        Args:
            query: Search query
            api: Search API name
            ttl_hours: TTL in hours (default 24)
            
        Returns:
            Cached search results or None
        """
        identifier = f"{api}:{query}"
        return await self.get("search", identifier, ttl_hours)
    
    async def set_search_results(
        self,
        query: str,
        api: str,
        results: list,
        ttl_hours: int = 24
    ):
        """
        Cache search results.
        
        Args:
            query: Search query
            api: Search API name
            results: Search results to cache
            ttl_hours: TTL in hours (default 24)
        """
        identifier = f"{api}:{query}"
        await self.set("search", identifier, results, ttl_hours)
    
    async def get_content(self, url: str, ttl_hours: int = 48) -> Optional[Dict]:
        """
        Get cached content.
        
        Args:
            url: Content URL
            ttl_hours: TTL in hours (default 48)
            
        Returns:
            Cached content or None
        """
        return await self.get("content", url, ttl_hours)
    
    async def set_content(self, url: str, content: Dict, ttl_hours: int = 48):
        """
        Cache content.
        
        Args:
            url: Content URL
            content: Content data to cache
            ttl_hours: TTL in hours (default 48)
        """
        await self.set("content", url, content, ttl_hours)
    
    async def get_processed_content(self, url: str, ttl_hours: int = 48) -> Optional[Dict]:
        """
        Get cached processed content.
        
        Args:
            url: Content URL
            ttl_hours: TTL in hours (default 48)
            
        Returns:
            Cached processed content or None
        """
        return await self.get("processed_content", url, ttl_hours)
    
    async def set_processed_content(self, url: str, content: Dict, ttl_hours: int = 48):
        """
        Cache processed content.
        
        Args:
            url: Content URL
            content: Processed content data to cache
            ttl_hours: TTL in hours (default 48)
        """
        await self.set("processed_content", url, content, ttl_hours)


# Global cache manager instance
_cache_manager: Optional[CacheManager] = None


def get_cache_manager() -> CacheManager:
    """Get global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = CacheManager()
    return _cache_manager



