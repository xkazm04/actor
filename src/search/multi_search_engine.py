"""
Multi-search engine with support for multiple search APIs.
Implements round-robin API selection, retry logic, and rate limit handling.
"""

import os
import asyncio
import time
from typing import List, Optional, Dict
from enum import Enum
import aiohttp
from apify import Actor

from src.utils.models import SearchResult
from src.cache.cache_manager import get_cache_manager
from src.cache.cache_stats import get_cache_stats


class SearchAPI(Enum):
    """Supported search APIs."""
    GOOGLE = "google"
    BRAVE = "brave"
    BING = "bing"


class MultiSearchEngine:
    """
    Multi-provider search engine with intelligent API selection and retry logic.
    """
    
    def __init__(self):
        """Initialize search engine with API credentials."""
        self.google_api_key = os.getenv("GOOGLE_SEARCH_API_KEY")
        self.google_engine_id = os.getenv("GOOGLE_SEARCH_ENGINE_ID")
        self.brave_api_key = os.getenv("BRAVE_SEARCH_API_KEY")
        self.bing_api_key = os.getenv("BING_SEARCH_API_KEY")
        
        # Phase 6: Initialize caching
        self.cache_manager = get_cache_manager()
        self.cache_stats = get_cache_stats()
        
        # Track API usage for round-robin
        self.api_usage_count = {api: 0 for api in SearchAPI}
        self.current_api_index = 0
        
        # Rate limit tracking
        self.rate_limits = {
            SearchAPI.GOOGLE: {"calls": 0, "reset_time": time.time()},
            SearchAPI.BRAVE: {"calls": 0, "reset_time": time.time()},
            SearchAPI.BING: {"calls": 0, "reset_time": time.time()}
        }
    
    def _get_available_apis(self) -> List[SearchAPI]:
        """Get list of available APIs based on configured keys."""
        available = []
        if self.google_api_key and self.google_engine_id:
            available.append(SearchAPI.GOOGLE)
        if self.brave_api_key:
            available.append(SearchAPI.BRAVE)
        if self.bing_api_key:
            available.append(SearchAPI.BING)
        return available
    
    def _select_api(self) -> Optional[SearchAPI]:
        """Select next API using round-robin strategy."""
        available = self._get_available_apis()
        if not available:
            return None
        
        # Round-robin selection
        api = available[self.current_api_index % len(available)]
        self.current_api_index += 1
        return api
    
    async def _check_rate_limit(self, api: SearchAPI) -> bool:
        """Check if API is within rate limits."""
        # Simple rate limiting: 100 calls per minute per API
        limit_info = self.rate_limits[api]
        current_time = time.time()
        
        # Reset if a minute has passed
        if current_time - limit_info["reset_time"] > 60:
            limit_info["calls"] = 0
            limit_info["reset_time"] = current_time
        
        return limit_info["calls"] < 100
    
    async def _increment_rate_limit(self, api: SearchAPI):
        """Increment rate limit counter."""
        self.rate_limits[api]["calls"] += 1
    
    async def _search_google(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Google Custom Search API."""
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.google_api_key,
            "cx": self.google_engine_id,
            "q": query,
            "num": min(num_results, 10)  # Google limits to 10 per request
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Google API error: {response.status}")
                
                data = await response.json()
                results = []
                
                for item in data.get("items", []):
                    results.append(SearchResult(
                        url=item.get("link", ""),
                        title=item.get("title", ""),
                        snippet=item.get("snippet", ""),
                        source_api="google"
                    ))
                
                return results
    
    async def _search_brave(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Brave Search API."""
        url = "https://api.search.brave.com/res/v1/web/search"
        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": self.brave_api_key
        }
        params = {
            "q": query,
            "count": min(num_results, 20)  # Brave allows up to 20
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Brave API error: {response.status}")
                
                data = await response.json()
                results = []
                
                for item in data.get("web", {}).get("results", []):
                    results.append(SearchResult(
                        url=item.get("url", ""),
                        title=item.get("title", ""),
                        snippet=item.get("description", ""),
                        source_api="brave"
                    ))
                
                return results
    
    async def _search_bing(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Bing Search API."""
        url = "https://api.bing.microsoft.com/v7.0/search"
        headers = {
            "Ocp-Apim-Subscription-Key": self.bing_api_key
        }
        params = {
            "q": query,
            "count": min(num_results, 50)  # Bing allows up to 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params=params) as response:
                if response.status != 200:
                    raise Exception(f"Bing API error: {response.status}")
                
                data = await response.json()
                results = []
                
                for item in data.get("webPages", {}).get("value", []):
                    results.append(SearchResult(
                        url=item.get("url", ""),
                        title=item.get("name", ""),
                        snippet=item.get("snippet", ""),
                        source_api="bing"
                    ))
                
                return results
    
    async def search(
        self,
        query: str,
        num_results: int = 10,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ) -> List[SearchResult]:
        """
        Perform search with automatic retry and API fallback.
        
        Args:
            query: Search query
            num_results: Number of results to return
            max_retries: Maximum retry attempts
            retry_delay: Initial delay between retries (exponential backoff)
            
        Returns:
            List of SearchResult objects
        """
        available_apis = self._get_available_apis()
        if not available_apis:
            Actor.log.warning("No search APIs configured. Using mock results.")
            return self._get_mock_results(query, num_results)
        
        # Phase 6: Check cache first
        api = self._select_api()
        cached_results = await self.cache_manager.get_search_results(query, api.value)
        
        if cached_results:
            Actor.log.info(f"Cache hit for query '{query[:50]}...' using {api.value}")
            await self.cache_stats.record_hit('search')
            # Convert cached dicts back to SearchResult objects
            return [SearchResult(**r) if isinstance(r, dict) else r for r in cached_results]
        
        await self.cache_stats.record_miss('search')
        
        last_error = None
        
        for attempt in range(max_retries):
            api = self._select_api()
            
            # Check rate limits
            if not await self._check_rate_limit(api):
                Actor.log.warning(f"Rate limit reached for {api.value}. Waiting...")
                await asyncio.sleep(60)
                continue
            
            try:
                await self._increment_rate_limit(api)
                
                Actor.log.info(f"Searching '{query}' using {api.value} API (attempt {attempt + 1})")
                
                if api == SearchAPI.GOOGLE:
                    results = await self._search_google(query, num_results)
                elif api == SearchAPI.BRAVE:
                    results = await self._search_brave(query, num_results)
                elif api == SearchAPI.BING:
                    results = await self._search_bing(query, num_results)
                else:
                    continue
                
                Actor.log.info(f"Found {len(results)} results from {api.value}")
                
                # Phase 6: Cache the results
                await self.cache_manager.set_search_results(query, api.value, [r.model_dump() for r in results])
                
                return results
                
            except Exception as e:
                last_error = e
                Actor.log.warning(f"Search failed with {api.value}: {e}")
                
                # Exponential backoff
                if attempt < max_retries - 1:
                    delay = retry_delay * (2 ** attempt)
                    Actor.log.info(f"Retrying in {delay} seconds...")
                    await asyncio.sleep(delay)
        
        # All retries failed, return mock results as fallback
        Actor.log.error(f"All search APIs failed. Last error: {last_error}")
        return self._get_mock_results(query, num_results)
    
    def _get_mock_results(self, query: str, num_results: int) -> List[SearchResult]:
        """Generate mock results when APIs are unavailable (for testing)."""
        return [
            SearchResult(
                url=f"https://example.com/article-{i}",
                title=f"Article {i} about {query}",
                snippet=f"This article discusses {query} in detail...",
                source_api="mock"
            )
            for i in range(min(num_results, 5))
        ]

