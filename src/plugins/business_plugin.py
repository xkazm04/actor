"""
Business Research Plugin - Optimizes research for business topics.
Focuses on market reports, company filings, financial data, and competitor analysis.
"""

from typing import Dict, List
from src.plugins.base_plugin import BasePlugin, PluginPriority


class BusinessResearchPlugin(BasePlugin):
    """
    Plugin for business research.
    Prioritizes market reports, SEC filings, and financial data.
    """
    
    BUSINESS_DOMAINS = [
        'sec.gov',
        'bloomberg.com',
        'reuters.com',
        'wsj.com',
        'ft.com',
        'forbes.com',
        'mckinsey.com',
        'bain.com',
        'bcg.com',
        'gartner.com',
        'idc.com',
        'statista.com',
        'crunchbase.com',
        'linkedin.com'
    ]
    
    BUSINESS_KEYWORDS = [
        'business', 'market', 'company', 'financial', 'revenue', 'profit',
        'competitor', 'industry', 'strategy', 'analysis', 'report',
        'earnings', 'quarterly', 'annual', 'sec filing', 'ipo',
        'merger', 'acquisition', 'investment', 'valuation'
    ]
    
    def __init__(self):
        """Initialize business research plugin."""
        super().__init__(
            name="business",
            description="Optimizes research for business and market topics",
            priority=PluginPriority.MEDIUM
        )
    
    def get_preferred_sources(self) -> List[str]:
        """Get preferred business sources."""
        return self.BUSINESS_DOMAINS
    
    def get_citation_style(self) -> str:
        """Get preferred citation style (Chicago for business)."""
        return "chicago"
    
    def score_source_relevance(self, source: Dict, query: str) -> float:
        """
        Score source relevance for business research.
        
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
        
        # Boost for business domains
        for business_domain in self.BUSINESS_DOMAINS:
            if business_domain in url or business_domain in domain:
                score += 0.3
                break
        
        # Boost for SEC filings
        if 'sec.gov' in url:
            score += 0.3
        
        # Boost for financial keywords
        business_keyword_count = sum(1 for keyword in self.BUSINESS_KEYWORDS if keyword in title)
        score += min(business_keyword_count * 0.1, 0.2)
        
        # Boost for market reports
        if 'report' in title or 'analysis' in title:
            score += 0.1
        
        return min(score, 1.0)
    
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for business research.
        Adds business-specific sub-queries.
        
        Args:
            query: Main research query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        sub_queries = [query]  # Start with original query
        
        # Add business-specific sub-queries
        business_modifiers = [
            f"{query} market analysis",
            f"{query} financial data",
            f"{query} company information",
            f"{query} industry report",
            f"{query} competitor analysis"
        ]
        
        for modifier in business_modifiers[:max_sub_queries - 1]:
            if len(sub_queries) < max_sub_queries:
                sub_queries.append(modifier)
        
        return sub_queries[:max_sub_queries]
    
    def customize_report_formatting(self, report: str, findings: Dict) -> str:
        """
        Customize report formatting for business reports.
        Adds executive summary and financial highlights.
        
        Args:
            report: Generated report
            findings: Research findings
            
        Returns:
            Formatted report with business sections
        """
        # Add executive summary section if not present
        if "Executive Summary" not in report:
            report = f"## Executive Summary\n\n{report}\n"
        
        return report
    
    def get_output_sections(self) -> List[str]:
        """Get preferred output sections for business reports."""
        return [
            "Executive Summary",
            "Market Overview",
            "Financial Analysis",
            "Competitive Landscape",
            "Key Insights",
            "Recommendations"
        ]
    
    def is_applicable(self, query: str) -> bool:
        """
        Check if query is business-related.
        
        Args:
            query: Research query
            
        Returns:
            True if query appears business-related
        """
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in self.BUSINESS_KEYWORDS)



