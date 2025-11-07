"""
Content Fetcher - Extracts full content from URLs.
Supports concurrent fetching, multiple content types, and Apify Web Scraper integration.
"""

import asyncio
import aiohttp
from typing import List, Optional, Dict
from urllib.parse import urlparse
from apify import Actor
from src.utils.models import SearchResult
from src.cache.cache_manager import get_cache_manager
from src.cache.cache_stats import get_cache_stats


class ContentFetcher:
    """
    Fetches full content from URLs with concurrent processing.
    Supports HTML, PDF, and plain text content types.
    """
    
    def __init__(self, max_concurrent: int = 8):
        """
        Initialize content fetcher.
        
        Args:
            max_concurrent: Maximum number of concurrent requests (5-10 recommended)
        """
        self.max_concurrent = max(5, min(max_concurrent, 10))
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Phase 6: Initialize caching
        self.cache_manager = get_cache_manager()
        self.cache_stats = get_cache_stats()
    
    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()
    
    async def fetch_content(self, url: str) -> Optional[Dict]:
        """
        Fetch content from a single URL.
        
        Args:
            url: URL to fetch
            
        Returns:
            Dictionary with content, metadata, and status, or None if failed
        """
        # Phase 6: Check cache first
        cached_content = await self.cache_manager.get_content(url)
        if cached_content:
            Actor.log.debug(f"Cache hit for content: {url[:50]}...")
            await self.cache_stats.record_hit('content')
            return cached_content
        
        await self.cache_stats.record_miss('content')
        
        try:
            async with self.session.get(url, allow_redirects=True) as response:
                if response.status != 200:
                    Actor.log.warning(f"Failed to fetch {url}: HTTP {response.status}")
                    return None
                
                content_type = response.headers.get('Content-Type', '').lower()
                
                # Determine content type
                if 'pdf' in content_type:
                    result = await self._handle_pdf(url, response)
                elif 'html' in content_type or 'text/html' in content_type:
                    result = await self._handle_html(url, response)
                else:
                    # Try to read as text
                    text = await response.text()
                    result = {
                        'url': url,
                        'content': text[:100000],  # Limit to 100KB
                        'content_type': 'text',
                        'status': 'success',
                        'metadata': self._extract_basic_metadata(url, text)
                    }
                
                # Phase 6: Cache the content
                if result:
                    await self.cache_manager.set_content(url, result)
                
                return result
        
        except asyncio.TimeoutError:
            Actor.log.warning(f"Timeout fetching {url}")
            return None
        except Exception as e:
            Actor.log.warning(f"Error fetching {url}: {e}")
            return None
    
    async def _handle_html(self, url: str, response: aiohttp.ClientResponse) -> Dict:
        """Handle HTML content."""
        html = await response.text()
        
        return {
            'url': url,
            'raw_html': html,
            'content_type': 'html',
            'status': 'success',
            'metadata': self._extract_basic_metadata(url, html)
        }
    
    async def _handle_pdf(self, url: str, response: aiohttp.ClientResponse) -> Dict:
        """Handle PDF content (basic implementation)."""
        # For now, return metadata only
        # Full PDF parsing would require pdfplumber or similar
        Actor.log.info(f"PDF detected at {url} - basic metadata extraction only")
        
        return {
            'url': url,
            'content_type': 'pdf',
            'status': 'success',
            'metadata': self._extract_basic_metadata(url, ''),
            'note': 'PDF content extraction requires additional processing'
        }
    
    def _extract_basic_metadata(self, url: str, content: str) -> Dict:
        """Extract basic metadata from URL and content."""
        parsed = urlparse(url)
        
        metadata = {
            'domain': parsed.netloc,
            'path': parsed.path,
            'scheme': parsed.scheme
        }
        
        # Try to extract title from HTML if present
        if content:
            import re
            title_match = re.search(r'<title>(.*?)</title>', content, re.IGNORECASE | re.DOTALL)
            if title_match:
                metadata['title'] = title_match.group(1).strip()[:200]
        
        return metadata
    
    async def fetch_multiple(
        self,
        urls: List[str],
        use_apify_scraper: bool = False
    ) -> List[Dict]:
        """
        Fetch content from multiple URLs concurrently.
        
        Args:
            urls: List of URLs to fetch
            use_apify_scraper: Whether to use Apify Web Scraper Actor for better extraction
            
        Returns:
            List of content dictionaries
        """
        if use_apify_scraper:
            return await self._fetch_with_apify_scraper(urls)
        
        # Use semaphore to limit concurrent requests
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def fetch_with_semaphore(url: str):
            async with semaphore:
                return await self.fetch_content(url)
        
        tasks = [fetch_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None results and exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                Actor.log.warning(f"Fetch exception: {result}")
            elif result is not None:
                valid_results.append(result)
        
        Actor.log.info(f"Fetched content from {len(valid_results)}/{len(urls)} URLs")
        return valid_results
    
    async def _fetch_with_apify_scraper(self, urls: List[str]) -> List[Dict]:
        """
        Use Apify Web Scraper Actor for better content extraction.
        This handles JavaScript-heavy sites and provides cleaner content.
        """
        try:
            # Call Apify Web Scraper Actor
            Actor.log.info(f"Using Apify Web Scraper for {len(urls)} URLs")
            
            # Note: This requires the Apify Web Scraper Actor to be available
            # For now, fallback to direct fetching
            Actor.log.warning("Apify Web Scraper integration not fully implemented, using direct fetch")
            return await self.fetch_multiple(urls, use_apify_scraper=False)
            
        except Exception as e:
            Actor.log.error(f"Apify scraper failed: {e}, falling back to direct fetch")
            return await self.fetch_multiple(urls, use_apify_scraper=False)


async def fetch_urls(urls: List[str], max_concurrent: int = 8) -> List[Dict]:
    """
    Convenience function to fetch multiple URLs.
    
    Args:
        urls: List of URLs
        max_concurrent: Maximum concurrent requests
        
    Returns:
        List of content dictionaries
    """
    async with ContentFetcher(max_concurrent) as fetcher:
        return await fetcher.fetch_multiple(urls)

