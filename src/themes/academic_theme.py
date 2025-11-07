"""
Academic Theme - Optimizes research for academic contexts.
Prioritizes peer-reviewed sources, academic databases, and formal analysis.
"""

from typing import Dict, List, Optional
from src.themes.base_theme import BaseTheme, SourcePriority


class AcademicTheme(BaseTheme):
    """Academic research theme."""
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return "academic"
    
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """Get source priorities for academic research."""
        return {
            'peer_reviewed_journals': SourcePriority.HIGH,
            'academic_databases': SourcePriority.HIGH,
            'university_research': SourcePriority.HIGH,
            'conference_papers': SourcePriority.HIGH,
            'textbooks': SourcePriority.MEDIUM,
            'academic_publishers': SourcePriority.MEDIUM,
            'news': SourcePriority.LOW,
            'blogs': SourcePriority.LOW
        }
    
    def get_analysis_focus(self) -> List[str]:
        """Get analysis focus areas."""
        return [
            'research_methodology',
            'study_design',
            'sample_size',
            'statistical_significance',
            'literature_review',
            'research_gaps',
            'methodological_approaches'
        ]
    
    def get_output_characteristics(self) -> Dict:
        """Get output characteristics."""
        citation_style = self.theme_options.get('citationStyle', 'APA')
        include_doi = self.theme_options.get('includeDOI', True)
        
        return {
            'tone': 'academic',
            'citation_style': citation_style.lower(),
            'include_doi': include_doi,
            'structure': 'formal',
            'perspective': 'third_person',
            'sections': [
                'abstract',
                'literature_review',
                'methodology',
                'findings',
                'discussion',
                'references'
            ]
        }
    
    def get_preferred_domains(self) -> List[str]:
        """Get preferred domains."""
        return [
            '.edu',
            '.ac.uk',
            '.ac.jp',
            'arxiv.org',
            'pubmed.ncbi.nlm.nih.gov',
            'scholar.google.com',
            'jstor.org',
            'springer.com',
            'ieee.org',
            'acm.org',
            'nature.com',
            'science.org'
        ]
    
    def score_source(self, source: Dict, query: str) -> float:
        """Score source for academic research."""
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        title = source.get('title', '').lower()
        
        # High score for academic domains
        academic_indicators = [
            '.edu', '.ac.', 'arxiv', 'pubmed', 'jstor', 'scholar',
            'journal', 'paper', 'research', 'study', 'university'
        ]
        
        score = 0.5  # Base score
        
        for indicator in academic_indicators:
            if indicator in url or indicator in domain or indicator in title:
                score += 0.1
        
        return min(score, 1.0)



