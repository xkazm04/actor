"""
News Theme - Optimizes research for news and journalism contexts.
Prioritizes recent articles, fact-checking, and multiple perspectives.
"""

from typing import Dict, List, Optional
from src.themes.base_theme import BaseTheme, SourcePriority


class NewsTheme(BaseTheme):
    """News and journalism research theme."""
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return "news"
    
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """Get source priorities for news research."""
        return {
            'major_news_outlets': SourcePriority.HIGH,
            'fact_checking_sites': SourcePriority.HIGH,
            'official_statements': SourcePriority.HIGH,
            'press_releases': SourcePriority.MEDIUM,
            'news_aggregators': SourcePriority.MEDIUM,
            'social_media': SourcePriority.LOW,
            'blogs': SourcePriority.LOW
        }
    
    def get_analysis_focus(self) -> List[str]:
        """Get analysis focus areas."""
        return [
            'timeline_of_events',
            'multiple_perspectives',
            'fact_vs_opinion',
            'primary_vs_secondary_sources',
            'media_bias_detection',
            'recent_updates',
            'expert_opinions'
        ]
    
    def get_output_characteristics(self) -> Dict:
        """Get output characteristics."""
        recency_bias = self.theme_options.get('recencyBias', 'recent')
        perspective_diversity = self.theme_options.get('perspectiveDiversity', True)
        fact_check_required = self.theme_options.get('factCheckRequired', True)
        
        return {
            'tone': 'conversational',
            'citation_style': 'mla',
            'structure': 'chronological',
            'perspective': 'first_second_person',
            'recency_bias': recency_bias,
            'perspective_diversity': perspective_diversity,
            'fact_check': fact_check_required,
            'sections': [
                'what_happened',
                'key_facts',
                'different_perspectives',
                'expert_opinions',
                'latest_updates',
                'fact_check_results'
            ]
        }
    
    def get_preferred_domains(self) -> List[str]:
        """Get preferred domains."""
        return [
            'reuters.com',
            'ap.org',
            'bbc.com',
            'cnn.com',
            'nytimes.com',
            'washingtonpost.com',
            'theguardian.com',
            'factcheck.org',
            'snopes.com',
            'allsides.com',
            'politifact.com'
        ]
    
    def score_source(self, source: Dict, query: str) -> float:
        """Score source for news research."""
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        title = source.get('title', '').lower()
        snippet = source.get('snippet', '').lower()
        
        score = 0.5  # Base score
        
        # News indicators
        news_indicators = [
            'news', 'report', 'article', 'breaking', 'update',
            'reuters', 'ap', 'bbc', 'cnn', 'fact-check'
        ]
        
        for indicator in news_indicators:
            if indicator in url or indicator in domain or indicator in title or indicator in snippet:
                score += 0.1
        
        # Recency bonus (if date available)
        # This would require date parsing, simplified here
        if '2024' in url or '2024' in title or '2024' in snippet:
            score += 0.2
        
        return min(score, 1.0)



