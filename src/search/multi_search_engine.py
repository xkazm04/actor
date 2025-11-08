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
    SERP = "serp"  # Primary: Serp API
    GOOGLE = "google"  # Fallback
    BRAVE = "brave"  # Fallback
    BING = "bing"  # Fallback


class MultiSearchEngine:
    """
    Multi-provider search engine with intelligent API selection and retry logic.
    """
    
    def __init__(self):
        """Initialize search engine with API credentials."""
        # Primary: Serp API
        self.serp_api_key = os.getenv("SERP_API_KEY")
        
        # Fallbacks
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
            SearchAPI.SERP: {"calls": 0, "reset_time": time.time()},
            SearchAPI.GOOGLE: {"calls": 0, "reset_time": time.time()},
            SearchAPI.BRAVE: {"calls": 0, "reset_time": time.time()},
            SearchAPI.BING: {"calls": 0, "reset_time": time.time()}
        }
    
    def _get_available_apis(self) -> List[SearchAPI]:
        """Get list of available APIs based on configured keys."""
        available = []
        # Primary: Serp API
        if self.serp_api_key:
            available.append(SearchAPI.SERP)
        # Fallbacks
        if self.google_api_key and self.google_engine_id:
            available.append(SearchAPI.GOOGLE)
        if self.brave_api_key:
            available.append(SearchAPI.BRAVE)
        if self.bing_api_key:
            available.append(SearchAPI.BING)
        return available
    
    def _select_api(self, prefer_primary: bool = True) -> Optional[SearchAPI]:
        """
        Select next API with priority to Serp API.
        
        Args:
            prefer_primary: If True, always prefer Serp API first, then fallback to others
        """
        available = self._get_available_apis()
        if not available:
            return None
        
        # Always prefer Serp API if available
        if prefer_primary and SearchAPI.SERP in available:
            return SearchAPI.SERP
        
        # Round-robin selection for fallbacks
        fallback_apis = [api for api in available if api != SearchAPI.SERP]
        if fallback_apis:
            api = fallback_apis[self.current_api_index % len(fallback_apis)]
            self.current_api_index += 1
            return api
        
        # If only Serp is available
        return SearchAPI.SERP if SearchAPI.SERP in available else None
    
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
    
    async def _search_serp(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """Search using Serp API (primary search method)."""
        url = "https://serpapi.com/search"
        params = {
            "api_key": self.serp_api_key,
            "q": query,
            "num": min(num_results, 100),  # Serp API allows up to 100 results
            "engine": "google"  # Use Google search engine via Serp API
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise Exception(f"Serp API error: {response.status} - {error_text}")
                
                data = await response.json()
                results = []
                
                # Serp API returns results in 'organic_results' field
                for item in data.get("organic_results", []):
                    results.append(SearchResult(
                        url=item.get("link", ""),
                        title=item.get("title", ""),
                        snippet=item.get("snippet", ""),
                        source_api="serp"
                    ))
                
                # If we need more results, check 'related_questions' or 'answer_box'
                if len(results) < num_results:
                    # Add answer box if available
                    answer_box = data.get("answer_box")
                    if answer_box and answer_box.get("link"):
                        results.append(SearchResult(
                            url=answer_box.get("link", ""),
                            title=answer_box.get("title", answer_box.get("answer", "")),
                            snippet=answer_box.get("answer", answer_box.get("snippet", "")),
                            source_api="serp"
                        ))
                
                return results[:num_results]
    
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
        
        # Phase 6: Check cache first (try Serp API cache first)
        primary_api = self._select_api(prefer_primary=True)
        if primary_api:
            cached_results = await self.cache_manager.get_search_results(query, primary_api.value)
            if cached_results:
                Actor.log.info(f"Cache hit for query '{query[:50]}...' using {primary_api.value}")
                await self.cache_stats.record_hit('search')
                # Convert cached dicts back to SearchResult objects
                return [SearchResult(**r) if isinstance(r, dict) else r for r in cached_results]
        
        await self.cache_stats.record_miss('search')
        
        last_error = None
        tried_apis = set()
        
        # Try Serp API first (primary)
        for attempt in range(max_retries):
            # On first attempt, prefer Serp API
            # On subsequent attempts, try fallbacks
            prefer_primary = (attempt == 0)
            api = self._select_api(prefer_primary=prefer_primary)
            
            if not api:
                break
            
            # Skip if we've already tried this API
            if api in tried_apis and prefer_primary:
                # Move to fallbacks
                prefer_primary = False
                api = self._select_api(prefer_primary=False)
                if not api or api in tried_apis:
                    break
            
            tried_apis.add(api)
            
            # Check rate limits
            if not await self._check_rate_limit(api):
                Actor.log.warning(f"Rate limit reached for {api.value}. Trying next API...")
                continue
            
            try:
                await self._increment_rate_limit(api)
                
                Actor.log.info(f"Searching '{query}' using {api.value} API (attempt {attempt + 1})")
                
                if api == SearchAPI.SERP:
                    results = await self._search_serp(query, num_results)
                elif api == SearchAPI.GOOGLE:
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
                
                # If Serp API failed, try fallbacks immediately
                if api == SearchAPI.SERP and attempt == 0:
                    Actor.log.info("Serp API failed, trying fallback APIs...")
                    continue
                
                # Exponential backoff for retries
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

