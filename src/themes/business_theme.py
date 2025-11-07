"""
Business Theme - Optimizes research for business and market contexts.
Prioritizes financial reports, market research, and business analysis.
"""

from typing import Dict, List, Optional
from src.themes.base_theme import BaseTheme, SourcePriority


class BusinessTheme(BaseTheme):
    """Business and market research theme."""
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return "business"
    
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """Get source priorities for business research."""
        return {
            'financial_reports': SourcePriority.HIGH,
            'sec_filings': SourcePriority.HIGH,
            'market_research_firms': SourcePriority.HIGH,
            'business_news': SourcePriority.HIGH,
            'company_websites': SourcePriority.MEDIUM,
            'industry_analysts': SourcePriority.MEDIUM,
            'consultants': SourcePriority.MEDIUM,
            'blogs': SourcePriority.LOW
        }
    
    def get_analysis_focus(self) -> List[str]:
        """Get analysis focus areas."""
        focus = [
            'market_size',
            'market_growth',
            'competitive_landscape',
            'financial_metrics',
            'kpis',
            'swot_analysis',
            'trends',
            'forecasts'
        ]
        
        if self.theme_options.get('includeFinancials', True):
            focus.extend(['revenue', 'profit', 'roi', 'valuation'])
        
        if self.theme_options.get('competitorAnalysis', True):
            focus.extend(['competitors', 'market_share', 'competitive_advantages'])
        
        if self.theme_options.get('marketSizeEstimates', True):
            focus.extend(['market_size', 'growth_rate', 'projections'])
        
        return focus
    
    def get_output_characteristics(self) -> Dict:
        """Get output characteristics."""
        return {
            'tone': 'professional',
            'citation_style': 'chicago',
            'structure': 'executive_friendly',
            'perspective': 'third_person',
            'data_visualization': True,
            'financial_metrics': True,
            'strategic_implications': True,
            'sections': [
                'executive_summary',
                'market_overview',
                'competitive_analysis',
                'financial_performance',
                'key_trends',
                'strategic_recommendations'
            ]
        }
    
    def get_preferred_domains(self) -> List[str]:
        """Get preferred domains."""
        return [
            'sec.gov',
            'bloomberg.com',
            'wsj.com',
            'ft.com',
            'forbes.com',
            'gartner.com',
            'forrester.com',
            'idc.com',
            'mckinsey.com',
            'bain.com',
            'pwc.com',
            'deloitte.com'
        ]
    
    def score_source(self, source: Dict, query: str) -> float:
        """Score source for business research."""
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        title = source.get('title', '').lower()
        
        score = 0.5  # Base score
        
        # Business indicators
        business_indicators = [
            'market', 'business', 'financial', 'revenue', 'profit',
            'company', 'industry', 'investment', 'strategy', 'roi',
            'sec', 'filing', 'earnings', 'quarterly', 'annual'
        ]
        
        for indicator in business_indicators:
            if indicator in url or indicator in domain or indicator in title:
                score += 0.1
        
        return min(score, 1.0)



