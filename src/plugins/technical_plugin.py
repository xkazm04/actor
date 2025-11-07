"""
Technical Research Plugin - Optimizes research for technical topics.
Prioritizes documentation, GitHub repos, Stack Overflow, and technical specs.
"""

from typing import Dict, List
from src.plugins.base_plugin import BasePlugin, PluginPriority


class TechnicalResearchPlugin(BasePlugin):
    """
    Plugin for technical research.
    Prioritizes documentation, code repositories, and technical resources.
    """
    
    TECHNICAL_DOMAINS = [
        'github.com',
        'stackoverflow.com',
        'stackexchange.com',
        'docs.python.org',
        'developer.mozilla.org',
        'docs.microsoft.com',
        'developer.android.com',
        'kubernetes.io',
        'docker.com',
        'npmjs.com',
        'pypi.org',
        'rubygems.org',
        'npmjs.com',
        'readthedocs.io',
        'medium.com',
        'dev.to',
        'reddit.com/r/programming',
        'hackernews.com'
    ]
    
    TECHNICAL_KEYWORDS = [
        'code', 'programming', 'development', 'api', 'documentation',
        'tutorial', 'guide', 'implementation', 'technical', 'software',
        'framework', 'library', 'package', 'repository', 'github',
        'stack overflow', 'how to', 'example', 'syntax', 'function'
    ]
    
    def __init__(self):
        """Initialize technical research plugin."""
        super().__init__(
            name="technical",
            description="Optimizes research for technical topics and programming",
            priority=PluginPriority.HIGH
        )
    
    def get_preferred_sources(self) -> List[str]:
        """Get preferred technical sources."""
        return self.TECHNICAL_DOMAINS
    
    def get_citation_style(self) -> str:
        """Get preferred citation style (IEEE for technical)."""
        return "ieee"
    
    def score_source_relevance(self, source: Dict, query: str) -> float:
        """
        Score source relevance for technical research.
        
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
        snippet = source.get('snippet', '').lower()
        
        # Boost for technical domains
        for tech_domain in self.TECHNICAL_DOMAINS:
            if tech_domain in url or tech_domain in domain:
                score += 0.3
                break
        
        # Boost for GitHub
        if 'github.com' in url:
            score += 0.2
        
        # Boost for documentation sites
        if 'docs.' in domain or '/docs/' in url:
            score += 0.2
        
        # Boost for technical keywords
        all_text = f"{title} {snippet}".lower()
        tech_keyword_count = sum(1 for keyword in self.TECHNICAL_KEYWORDS if keyword in all_text)
        score += min(tech_keyword_count * 0.1, 0.2)
        
        # Boost for code examples
        if '```' in snippet or 'code' in snippet or 'example' in snippet:
            score += 0.1
        
        return min(score, 1.0)
    
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for technical research.
        Adds technical-specific sub-queries.
        
        Args:
            query: Main research query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        sub_queries = [query]  # Start with original query
        
        # Add technical-specific sub-queries
        technical_modifiers = [
            f"{query} documentation",
            f"{query} tutorial",
            f"{query} example code",
            f"{query} implementation guide",
            f"{query} best practices",
            f"{query} github"
        ]
        
        for modifier in technical_modifiers[:max_sub_queries - 1]:
            if len(sub_queries) < max_sub_queries:
                sub_queries.append(modifier)
        
        return sub_queries[:max_sub_queries]
    
    def customize_content_extraction(self, content: Dict) -> Dict:
        """
        Customize content extraction for technical content.
        Extracts code examples, API documentation, and usage patterns.
        
        Args:
            content: Raw content dictionary
            
        Returns:
            Processed content with technical sections
        """
        processed = content.copy()
        
        # Extract code examples
        text = content.get('content', '') or content.get('markdown', '')
        
        # Look for code blocks
        import re
        code_blocks = re.findall(r'```[\s\S]*?```', text)
        if code_blocks:
            processed['code_examples'] = code_blocks
            processed['has_code'] = True
        
        # Look for API documentation
        if 'api' in text.lower() or 'endpoint' in text.lower():
            processed['has_api_docs'] = True
        
        # Look for installation instructions
        if 'install' in text.lower() or 'setup' in text.lower():
            processed['has_installation'] = True
        
        return processed
    
    def get_output_sections(self) -> List[str]:
        """Get preferred output sections for technical reports."""
        return [
            "Overview",
            "Technical Details",
            "Implementation",
            "Code Examples",
            "API Reference",
            "Resources"
        ]
    
    def is_applicable(self, query: str) -> bool:
        """
        Check if query is technical in nature.
        
        Args:
            query: Research query
            
        Returns:
            True if query appears technical
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.TECHNICAL_KEYWORDS)



