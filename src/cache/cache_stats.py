"""
Cache Statistics - Tracks cache performance and hit rates.
Provides cache statistics and reporting.
"""

from typing import Dict, Optional
from datetime import datetime
from apify import Actor


class CacheStats:
    """
    Tracks cache statistics including hit rates and performance metrics.
    """
    
    def __init__(self):
        """Initialize cache statistics tracker."""
        self.stats_key = "cache_stats"
        self.stats: Optional[Dict] = None
    
    async def load_stats(self) -> Dict:
        """
        Load cache statistics from storage.
        
        Returns:
            Statistics dictionary
        """
        if self.stats is None:
            try:
                self.stats = await Actor.get_value(self.stats_key) or {}
            except Exception:
                self.stats = {}
            
            # Initialize if empty
            if not self.stats:
                self.stats = {
                    'total_requests': 0,
                    'cache_hits': 0,
                    'cache_misses': 0,
                    'search_cache_hits': 0,
                    'search_cache_misses': 0,
                    'content_cache_hits': 0,
                    'content_cache_misses': 0,
                    'total_cache_size': 0,
                    'last_updated': datetime.now().isoformat()
                }
        
        return self.stats
    
    async def record_hit(self, category: str):
        """
        Record a cache hit.
        
        Args:
            category: Cache category (search, content, etc.)
        """
        await self.load_stats()
        
        self.stats['cache_hits'] = self.stats.get('cache_hits', 0) + 1
        self.stats['total_requests'] = self.stats.get('total_requests', 0) + 1
        
        if category == 'search':
            self.stats['search_cache_hits'] = self.stats.get('search_cache_hits', 0) + 1
        elif category == 'content':
            self.stats['content_cache_hits'] = self.stats.get('content_cache_hits', 0) + 1
        
        self.stats['last_updated'] = datetime.now().isoformat()
        await self._save_stats()
    
    async def record_miss(self, category: str):
        """
        Record a cache miss.
        
        Args:
            category: Cache category
        """
        await self.load_stats()
        
        self.stats['cache_misses'] = self.stats.get('cache_misses', 0) + 1
        self.stats['total_requests'] = self.stats.get('total_requests', 0) + 1
        
        if category == 'search':
            self.stats['search_cache_misses'] = self.stats.get('search_cache_misses', 0) + 1
        elif category == 'content':
            self.stats['content_cache_misses'] = self.stats.get('content_cache_misses', 0) + 1
        
        self.stats['last_updated'] = datetime.now().isoformat()
        await self._save_stats()
    
    async def get_hit_rate(self) -> float:
        """
        Get overall cache hit rate.
        
        Returns:
            Hit rate (0-1)
        """
        await self.load_stats()
        
        total = self.stats.get('total_requests', 0)
        if total == 0:
            return 0.0
        
        hits = self.stats.get('cache_hits', 0)
        return hits / total
    
    async def get_category_hit_rate(self, category: str) -> float:
        """
        Get hit rate for specific category.
        
        Args:
            category: Cache category
            
        Returns:
            Hit rate (0-1)
        """
        await self.load_stats()
        
        if category == 'search':
            hits = self.stats.get('search_cache_hits', 0)
            misses = self.stats.get('search_cache_misses', 0)
        elif category == 'content':
            hits = self.stats.get('content_cache_hits', 0)
            misses = self.stats.get('content_cache_misses', 0)
        else:
            return 0.0
        
        total = hits + misses
        if total == 0:
            return 0.0
        
        return hits / total
    
    async def get_summary(self) -> Dict:
        """
        Get cache statistics summary.
        
        Returns:
            Summary dictionary
        """
        await self.load_stats()
        
        total_requests = self.stats.get('total_requests', 0)
        hits = self.stats.get('cache_hits', 0)
        misses = self.stats.get('cache_misses', 0)
        
        return {
            'total_requests': total_requests,
            'cache_hits': hits,
            'cache_misses': misses,
            'overall_hit_rate': self.stats.get('overall_hit_rate', await self.get_hit_rate()),
            'search_hit_rate': await self.get_category_hit_rate('search'),
            'content_hit_rate': await self.get_category_hit_rate('content'),
            'search_hits': self.stats.get('search_cache_hits', 0),
            'search_misses': self.stats.get('search_cache_misses', 0),
            'content_hits': self.stats.get('content_cache_hits', 0),
            'content_misses': self.stats.get('content_cache_misses', 0),
            'last_updated': self.stats.get('last_updated', datetime.now().isoformat())
        }
    
    async def reset(self):
        """Reset cache statistics."""
        self.stats = {
            'total_requests': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'search_cache_hits': 0,
            'search_cache_misses': 0,
            'content_cache_hits': 0,
            'content_cache_misses': 0,
            'total_cache_size': 0,
            'last_updated': datetime.now().isoformat()
        }
        await self._save_stats()
    
    async def _save_stats(self):
        """Save statistics to storage."""
        try:
            await Actor.set_value(self.stats_key, self.stats)
        except Exception as e:
            Actor.log.warning(f"Failed to save cache stats: {e}")


# Global cache stats instance
_cache_stats: Optional[CacheStats] = None


def get_cache_stats() -> CacheStats:
    """Get global cache statistics instance."""
    global _cache_stats
    if _cache_stats is None:
        _cache_stats = CacheStats()
    return _cache_stats



