"""
Relevance Scorer - Multi-factor scoring system for sources.
Scores by relevance, recency, and authority.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timezone
from urllib.parse import urlparse
from apify import Actor


class RelevanceScorer:
    """
    Scores sources based on multiple factors:
    - Relevance to query (semantic similarity)
    - Recency (newer content scores higher)
    - Authority (domain reputation)
    """
    
    def __init__(
        self,
        relevance_weight: float = 0.5,
        recency_weight: float = 0.3,
        authority_weight: float = 0.2
    ):
        """
        Initialize relevance scorer.
        
        Args:
            relevance_weight: Weight for relevance score (0-1)
            recency_weight: Weight for recency score (0-1)
            authority_weight: Weight for authority score (0-1)
        """
        total_weight = relevance_weight + recency_weight + authority_weight
        if abs(total_weight - 1.0) > 0.01:
            Actor.log.warning(f"Weights don't sum to 1.0, normalizing...")
            self.relevance_weight = relevance_weight / total_weight
            self.recency_weight = recency_weight / total_weight
            self.authority_weight = authority_weight / total_weight
        else:
            self.relevance_weight = relevance_weight
            self.recency_weight = recency_weight
            self.authority_weight = authority_weight
        
        # Known authoritative domains (can be expanded)
        self.authoritative_domains = {
            'edu': 0.9,
            'gov': 0.9,
            'org': 0.7,
            'wikipedia.org': 0.8,
            'arxiv.org': 0.9,
            'pubmed.ncbi.nlm.nih.gov': 0.9,
            'scholar.google.com': 0.9,
            'nature.com': 0.85,
            'science.org': 0.85,
            'ieee.org': 0.85,
            'acm.org': 0.85
        }
    
    def score_source(
        self,
        source: Dict,
        query: str,
        processed_content: Optional[Dict] = None
    ) -> float:
        """
        Calculate composite score for a source.
        
        Args:
            source: Source dictionary (SearchResult or similar)
            query: Original research query
            processed_content: Processed content dictionary (optional)
            
        Returns:
            Composite score (0-100)
        """
        relevance_score = self._score_relevance(source, query, processed_content)
        recency_score = self._score_recency(source, processed_content)
        authority_score = self._score_authority(source)
        
        composite = (
            relevance_score * self.relevance_weight +
            recency_score * self.recency_weight +
            authority_score * self.authority_weight
        ) * 100
        
        return round(composite, 2)
    
    def _score_relevance(
        self,
        source: Dict,
        query: str,
        processed_content: Optional[Dict] = None
    ) -> float:
        """
        Score relevance to query (0-1).
        Uses keyword matching and content analysis.
        """
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Check title
        title = source.get('title', '').lower()
        title_matches = sum(1 for word in query_words if word in title)
        title_score = min(title_matches / max(len(query_words), 1), 1.0)
        
        # Check snippet
        snippet = source.get('snippet', '').lower()
        snippet_matches = sum(1 for word in query_words if word in snippet)
        snippet_score = min(snippet_matches / max(len(query_words), 1), 1.0)
        
        # Check processed content if available
        content_score = 0.0
        if processed_content:
            markdown = processed_content.get('markdown', '').lower()
            if markdown:
                content_matches = sum(1 for word in query_words if word in markdown)
                content_score = min(content_matches / max(len(query_words) * 2, 1), 1.0)
        
        # Weighted combination
        relevance = (
            title_score * 0.4 +
            snippet_score * 0.3 +
            content_score * 0.3
        )
        
        return min(relevance, 1.0)
    
    def _score_recency(self, source: Dict, processed_content: Optional[Dict] = None) -> float:
        """
        Score recency (0-1).
        Newer content scores higher with exponential decay.
        """
        # Try to get date from processed content
        publish_date = None
        if processed_content:
            metadata = processed_content.get('metadata', {})
            date_str = metadata.get('publish_date')
            if date_str:
                try:
                    publish_date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    pass
        
        if not publish_date:
            # Default: assume content is somewhat recent (score 0.5)
            return 0.5
        
        # Calculate age in days
        now = datetime.now(timezone.utc)
        if publish_date.tzinfo is None:
            publish_date = publish_date.replace(tzinfo=timezone.utc)
        
        age_days = (now - publish_date).days
        
        # Exponential decay: score = e^(-age/365)
        # Content from 1 year ago scores ~0.37
        # Content from 6 months ago scores ~0.61
        # Content from 1 month ago scores ~0.92
        import math
        recency = math.exp(-age_days / 365.0)
        
        return min(max(recency, 0.0), 1.0)
    
    def _score_authority(self, source: Dict) -> float:
        """
        Score authority based on domain (0-1).
        """
        url = source.get('url', '')
        if not url:
            return 0.5  # Default score
        
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check exact domain matches
        for auth_domain, score in self.authoritative_domains.items():
            if auth_domain in domain:
                return score
        
        # Check TLD
        tld = domain.split('.')[-1] if '.' in domain else ''
        if tld in ['edu', 'gov']:
            return 0.8
        elif tld == 'org':
            return 0.6
        
        # Default: medium authority
        return 0.5
    
    def rank_sources(
        self,
        sources: List[Dict],
        query: str,
        processed_contents: Optional[Dict[str, Dict]] = None
    ) -> List[Dict]:
        """
        Rank sources by composite score.
        
        Args:
            sources: List of source dictionaries
            query: Original research query
            processed_contents: Dictionary mapping URLs to processed content
            
        Returns:
            List of sources with added 'score' field, sorted by score descending
        """
        processed_contents = processed_contents or {}
        
        scored_sources = []
        for source in sources:
            url = source.get('url', '')
            processed_content = processed_contents.get(url)
            
            score = self.score_source(source, query, processed_content)
            
            scored_source = source.copy()
            scored_source['score'] = score
            scored_source['relevance_score'] = self._score_relevance(source, query, processed_content)
            scored_source['recency_score'] = self._score_recency(source, processed_content)
            scored_source['authority_score'] = self._score_authority(source)
            
            scored_sources.append(scored_source)
        
        # Sort by score descending
        scored_sources.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return scored_sources


def score_and_rank_sources(
    sources: List[Dict],
    query: str,
    processed_contents: Optional[Dict[str, Dict]] = None
) -> List[Dict]:
    """
    Convenience function to score and rank sources.
    
    Args:
        sources: List of source dictionaries
        query: Original research query
        processed_contents: Dictionary mapping URLs to processed content
        
    Returns:
        Ranked list of sources with scores
    """
    scorer = RelevanceScorer()
    return scorer.rank_sources(sources, query, processed_contents)



