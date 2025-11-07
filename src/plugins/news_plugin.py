"""
News Research Plugin - Optimizes research for news and current events.
Focuses on recent articles, fact-checking, and primary sources.
"""

from typing import Dict, List
from datetime import datetime, timedelta
from src.plugins.base_plugin import BasePlugin, PluginPriority


class NewsResearchPlugin(BasePlugin):
    """
    Plugin for news and current events research.
    Prioritizes recent articles and fact-checking sources.
    """
    
    NEWS_DOMAINS = [
        'reuters.com',
        'ap.org',
        'bbc.com',
        'cnn.com',
        'theguardian.com',
        'nytimes.com',
        'washingtonpost.com',
        'wsj.com',
        'ft.com',
        'bloomberg.com'
    ]
    
    FACT_CHECK_DOMAINS = [
        'snopes.com',
        'factcheck.org',
        'politifact.com',
        'reuters.com',
        'ap.org'
    ]
    
    NEWS_KEYWORDS = [
        'news', 'breaking', 'latest', 'recent', 'today', 'yesterday',
        'report', 'article', 'story', 'update', 'developing', 'current',
        'event', 'happening', 'announcement', 'statement', 'press'
    ]
    
    def __init__(self):
        """Initialize news research plugin."""
        super().__init__(
            name="news",
            description="Optimizes research for news and current events",
            priority=PluginPriority.HIGH
        )
    
    def get_preferred_sources(self) -> List[str]:
        """Get preferred news sources."""
        return self.NEWS_DOMAINS + self.FACT_CHECK_DOMAINS
    
    def get_citation_style(self) -> str:
        """Get preferred citation style (MLA for news)."""
        return "mla"
    
    def score_source_relevance(self, source: Dict, query: str) -> float:
        """
        Score source relevance for news research.
        
        Args:
            source: Source dictionary
            query: Research query
            
        Returns:
            Relevance score (0.0-1.0)
        """
        score = 0.5  # Base score
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        title = source.get('title', '').lower()
        publish_date = source.get('publish_date', '')
        
        # Boost for news domains
        for news_domain in self.NEWS_DOMAINS:
            if news_domain in url or news_domain in domain:
                score += 0.3
                break
        
        # Boost for fact-check domains
        for fact_check in self.FACT_CHECK_DOMAINS:
            if fact_check in url or fact_check in domain:
                score += 0.4
                break
        
        # Boost for recent articles (last 30 days)
        if publish_date:
            try:
                pub_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                days_ago = (datetime.now() - pub_date.replace(tzinfo=None)).days
                if days_ago <= 30:
                    score += 0.2
                elif days_ago <= 90:
                    score += 0.1
            except:
                pass
        
        # Boost for news keywords in title
        news_keyword_count = sum(1 for keyword in self.NEWS_KEYWORDS if keyword in title)
        score += min(news_keyword_count * 0.1, 0.2)
        
        return min(score, 1.0)
    
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for news research.
        Adds time-sensitive and fact-checking sub-queries.
        
        Args:
            query: Main research query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        sub_queries = [query]  # Start with original query
        
        # Add news-specific sub-queries
        news_modifiers = [
            f"{query} latest news",
            f"{query} recent developments",
            f"{query} breaking news",
            f"{query} fact check",
            f"{query} verified information"
        ]
        
        for modifier in news_modifiers[:max_sub_queries - 1]:
            if len(sub_queries) < max_sub_queries:
                sub_queries.append(modifier)
        
        return sub_queries[:max_sub_queries]
    
    def get_search_modifiers(self) -> Dict:
        """
        Get search modifiers for news research.
        Prefer recent results.
        
        Returns:
            Dictionary of search modifiers
        """
        return {
            'date_restrict': 'd30',  # Last 30 days
            'sort_by_date': True
        }
    
    def get_output_sections(self) -> List[str]:
        """Get preferred output sections for news reports."""
        return [
            "Summary",
            "Key Developments",
            "Timeline",
            "Sources",
            "Fact-Check Status"
        ]
    
    def is_applicable(self, query: str) -> bool:
        """
        Check if query is news-related.
        
        Args:
            query: Research query
            
        Returns:
            True if query appears news-related
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.NEWS_KEYWORDS)



