"""
General Theme - Balanced theme for general-purpose research.
Uses balanced mix of all source types and standard analysis.
"""

from typing import Dict, List, Optional
from src.themes.base_theme import BaseTheme, SourcePriority


class GeneralTheme(BaseTheme):
    """General-purpose research theme."""
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return "general"
    
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """Get source priorities for general research."""
        return {
            'news': SourcePriority.MEDIUM,
            'academic': SourcePriority.MEDIUM,
            'business': SourcePriority.MEDIUM,
            'technical': SourcePriority.MEDIUM,
            'blogs': SourcePriority.MEDIUM,
            'official': SourcePriority.MEDIUM
        }
    
    def get_analysis_focus(self) -> List[str]:
        """Get analysis focus areas."""
        return [
            'comprehensive_coverage',
            'balanced_perspectives',
            'key_findings',
            'main_themes',
            'synthesis'
        ]
    
    def get_output_characteristics(self) -> Dict:
        """Get output characteristics."""
        return {
            'tone': 'professional',
            'citation_style': 'apa',
            'structure': 'standard',
            'perspective': 'third_person',
            'sections': [
                'executive_summary',
                'introduction',
                'main_findings',
                'detailed_analysis',
                'conclusions',
                'references'
            ]
        }
    
    def get_preferred_domains(self) -> List[str]:
        """Get preferred domains."""
        return []  # No specific preference
    
    def score_source(self, source: Dict, query: str) -> float:
        """Score source for general research."""
        # Balanced scoring
        return 0.5



