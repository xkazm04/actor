"""
Academic Research Plugin - Optimizes research for academic topics.
Prioritizes peer-reviewed sources, academic databases, and scholarly content.
"""

from typing import Dict, List
from src.plugins.base_plugin import BasePlugin, PluginPriority


class AcademicResearchPlugin(BasePlugin):
    """
    Plugin for academic research.
    Prioritizes peer-reviewed sources and academic databases.
    """
    
    ACADEMIC_DOMAINS = [
        'arxiv.org',
        'pubmed.ncbi.nlm.nih.gov',
        'scholar.google.com',
        '.edu',
        '.ac.uk',
        '.ac.jp',
        'jstor.org',
        'ieee.org',
        'acm.org',
        'springer.com',
        'nature.com',
        'science.org',
        'plos.org',
        'researchgate.net'
    ]
    
    ACADEMIC_KEYWORDS = [
        'research', 'study', 'paper', 'publication', 'journal', 'conference',
        'methodology', 'findings', 'hypothesis', 'experiment', 'analysis',
        'peer-reviewed', 'scholarly', 'academic', 'university', 'institute'
    ]
    
    def __init__(self):
        """Initialize academic research plugin."""
        super().__init__(
            name="academic",
            description="Optimizes research for academic topics with peer-reviewed sources",
            priority=PluginPriority.HIGH
        )
    
    def get_preferred_sources(self) -> List[str]:
        """Get preferred academic sources."""
        return self.ACADEMIC_DOMAINS
    
    def get_citation_style(self) -> str:
        """Get preferred citation style (APA for academic)."""
        return "apa"
    
    def score_source_relevance(self, source: Dict, query: str) -> float:
        """
        Score source relevance for academic research.
        
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
        
        # Boost for academic domains
        for academic_domain in self.ACADEMIC_DOMAINS:
            if academic_domain in url or academic_domain in domain:
                score += 0.3
                break
        
        # Boost for academic keywords in title
        academic_keyword_count = sum(1 for keyword in self.ACADEMIC_KEYWORDS if keyword in title)
        score += min(academic_keyword_count * 0.1, 0.2)
        
        # Boost for DOI presence
        if 'doi.org' in url or 'doi:' in url.lower():
            score += 0.2
        
        # Boost for PDF (often academic papers)
        if url.endswith('.pdf') or '.pdf' in url:
            score += 0.1
        
        return min(score, 1.0)
    
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for academic research.
        Adds academic-specific sub-queries.
        
        Args:
            query: Main research query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        sub_queries = [query]  # Start with original query
        
        # Add academic-specific sub-queries
        academic_modifiers = [
            f"{query} peer-reviewed research",
            f"{query} academic study",
            f"{query} methodology",
            f"{query} findings",
            f"{query} literature review"
        ]
        
        for modifier in academic_modifiers[:max_sub_queries - 1]:
            if len(sub_queries) < max_sub_queries:
                sub_queries.append(modifier)
        
        return sub_queries[:max_sub_queries]
    
    def customize_content_extraction(self, content: Dict) -> Dict:
        """
        Customize content extraction for academic papers.
        Extracts methodology, findings, and references sections.
        
        Args:
            content: Raw content dictionary
            
        Returns:
            Processed content with academic sections
        """
        processed = content.copy()
        
        # Extract academic-specific sections
        text = content.get('content', '') or content.get('markdown', '')
        
        # Look for methodology section
        if 'methodology' in text.lower() or 'methods' in text.lower():
            processed['has_methodology'] = True
        
        # Look for findings/results section
        if 'findings' in text.lower() or 'results' in text.lower():
            processed['has_findings'] = True
        
        # Look for references
        if 'references' in text.lower() or 'bibliography' in text.lower():
            processed['has_references'] = True
        
        # Extract DOI if present
        import re
        doi_pattern = r'doi[:\s]+([0-9.]+/[^\s]+)'
        doi_match = re.search(doi_pattern, text, re.IGNORECASE)
        if doi_match:
            processed['doi'] = doi_match.group(1)
        
        return processed
    
    def get_output_sections(self) -> List[str]:
        """Get preferred output sections for academic reports."""
        return [
            "Introduction",
            "Literature Review",
            "Methodology",
            "Findings",
            "Discussion",
            "Conclusion",
            "References"
        ]
    
    def is_applicable(self, query: str) -> bool:
        """
        Check if query is academic in nature.
        
        Args:
            query: Research query
            
        Returns:
            True if query appears academic
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.ACADEMIC_KEYWORDS)



