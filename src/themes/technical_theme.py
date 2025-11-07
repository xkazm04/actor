"""
Technical Theme - Optimizes research for technical and developer contexts.
Prioritizes official documentation, code repositories, and technical specifications.
"""

from typing import Dict, List, Optional
from src.themes.base_theme import BaseTheme, SourcePriority


class TechnicalTheme(BaseTheme):
    """Technical and developer research theme."""
    
    def get_theme_name(self) -> str:
        """Get theme name."""
        return "technical"
    
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """Get source priorities for technical research."""
        return {
            'official_documentation': SourcePriority.HIGH,
            'github_repositories': SourcePriority.HIGH,
            'technical_specifications': SourcePriority.HIGH,
            'api_documentation': SourcePriority.HIGH,
            'stack_overflow': SourcePriority.MEDIUM,
            'developer_forums': SourcePriority.MEDIUM,
            'technical_blogs': SourcePriority.MEDIUM,
            'tutorials': SourcePriority.MEDIUM,
            'news': SourcePriority.LOW
        }
    
    def get_analysis_focus(self) -> List[str]:
        """Get analysis focus areas."""
        focus = [
            'implementation_details',
            'code_examples',
            'performance_benchmarks',
            'best_practices',
            'common_pitfalls',
            'version_compatibility'
        ]
        
        if self.theme_options.get('includeCodeExamples', True):
            focus.extend(['code_snippets', 'examples', 'patterns'])
        
        if self.theme_options.get('documentationPriority', True):
            focus.insert(0, 'official_documentation')
        
        return focus
    
    def get_output_characteristics(self) -> Dict:
        """Get output characteristics."""
        return {
            'tone': 'technical',
            'citation_style': 'ieee',
            'structure': 'technical',
            'perspective': 'third_person',
            'include_code': True,
            'version_info': True,
            'command_examples': True,
            'architecture_diagrams': True,
            'sections': [
                'overview',
                'installation_setup',
                'core_concepts',
                'implementation_guide',
                'code_examples',
                'performance_considerations',
                'troubleshooting',
                'api_reference',
                'community_resources'
            ]
        }
    
    def get_preferred_domains(self) -> List[str]:
        """Get preferred domains."""
        return [
            'github.com',
            'stackoverflow.com',
            'docs.python.org',
            'developer.mozilla.org',
            'nodejs.org',
            'reactjs.org',
            'vuejs.org',
            'angular.io',
            'docker.com',
            'kubernetes.io',
            'aws.amazon.com',
            'cloud.google.com',
            'microsoft.com/developer'
        ]
    
    def score_source(self, source: Dict, query: str) -> float:
        """Score source for technical research."""
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        title = source.get('title', '').lower()
        
        score = 0.5  # Base score
        
        # Technical indicators
        technical_indicators = [
            'github', 'documentation', 'api', 'docs', 'tutorial',
            'guide', 'example', 'code', 'implementation', 'technical',
            'developer', 'programming', 'stackoverflow', 'npm', 'pypi'
        ]
        
        for indicator in technical_indicators:
            if indicator in url or indicator in domain or indicator in title:
                score += 0.1
        
        return min(score, 1.0)



