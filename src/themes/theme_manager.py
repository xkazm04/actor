"""
Theme Manager - Manages research themes and applies theme-specific configurations.
Orchestrates theme detection, selection, and application.
"""

from typing import Dict, Optional, List
from apify import Actor

from src.themes.theme_detector import ThemeDetector, ResearchTheme, create_theme_detector
from src.themes.academic_theme import AcademicTheme
from src.themes.news_theme import NewsTheme
from src.themes.business_theme import BusinessTheme
from src.themes.technical_theme import TechnicalTheme
from src.themes.general_theme import GeneralTheme
from src.themes.base_theme import BaseTheme


class ThemeManager:
    """
    Manages research themes and applies theme-specific configurations.
    Handles theme detection, selection, and application.
    """
    
    def __init__(self):
        """Initialize theme manager."""
        self.detector = create_theme_detector()
        self.themes: Dict[str, BaseTheme] = {}
        self._initialize_themes()
    
    def _initialize_themes(self):
        """Initialize all available themes."""
        self.themes = {
            ResearchTheme.ACADEMIC.value: AcademicTheme(),
            ResearchTheme.NEWS.value: NewsTheme(),
            ResearchTheme.BUSINESS.value: BusinessTheme(),
            ResearchTheme.TECHNICAL.value: TechnicalTheme(),
            ResearchTheme.GENERAL.value: GeneralTheme()
        }
    
    def detect_and_get_theme(
        self,
        query: str,
        user_theme: Optional[str] = None,
        theme_options: Optional[Dict] = None
    ) -> BaseTheme:
        """
        Detect theme from query or use user-specified theme.
        
        Args:
            query: Research query
            user_theme: User-specified theme (optional)
            theme_options: Theme-specific options (optional)
            
        Returns:
            Theme instance
        """
        if user_theme and user_theme != 'auto_detect':
            # Use user-specified theme
            theme_name = user_theme.lower()
            if theme_name in self.themes:
                # Apply theme options if provided
                if theme_options and theme_name in theme_options:
                    theme_class = type(self.themes[theme_name])
                    return theme_class(theme_options[theme_name])
                return self.themes[theme_name]
            else:
                Actor.log.warning(f"Unknown theme: {user_theme}, using general")
                return self.themes[ResearchTheme.GENERAL.value]
        
        # Auto-detect theme
        detection_result = self.detector.detect_with_explanation(query)
        detected_theme = detection_result['theme']
        confidence = detection_result['confidence']
        
        Actor.log.info(f"Auto-detected theme: {detected_theme} (confidence: {confidence:.2f})")
        
        # Apply theme options if provided
        if theme_options and detected_theme in theme_options:
            theme_class = type(self.themes[detected_theme])
            return theme_class(theme_options[detected_theme])
        
        return self.themes[detected_theme]
    
    def get_theme(self, theme_name: str, theme_options: Optional[Dict] = None) -> BaseTheme:
        """
        Get theme by name.
        
        Args:
            theme_name: Theme name
            theme_options: Theme-specific options (optional)
            
        Returns:
            Theme instance
        """
        theme_name = theme_name.lower()
        if theme_name in self.themes:
            if theme_options and theme_name in theme_options:
                theme_class = type(self.themes[theme_name])
                return theme_class(theme_options[theme_name])
            return self.themes[theme_name]
        
        return self.themes[ResearchTheme.GENERAL.value]
    
    def apply_theme_configuration(
        self,
        theme: BaseTheme,
        research_config: Dict
    ) -> Dict:
        """
        Apply theme configuration to research config.
        
        Args:
            theme: Theme instance
            research_config: Research configuration dictionary
            
        Returns:
            Updated research configuration
        """
        # Get theme characteristics
        output_chars = theme.get_output_characteristics()
        source_priorities = theme.get_source_priorities()
        analysis_focus = theme.get_analysis_focus()
        
        # Update research config with theme settings
        updated_config = research_config.copy()
        
        # Update citation style
        updated_config['citation_style'] = theme.get_citation_style()
        
        # Update output tone
        updated_config['tone'] = output_chars.get('tone', 'professional')
        
        # Update source priorities
        updated_config['source_priorities'] = {
            k: v.value for k, v in source_priorities.items()
        }
        
        # Update analysis focus
        updated_config['analysis_focus'] = analysis_focus
        
        # Update preferred domains
        updated_config['preferred_domains'] = theme.get_preferred_domains()
        
        return updated_config
    
    def score_sources_with_theme(
        self,
        sources: List[Dict],
        query: str,
        theme: BaseTheme
    ) -> List[Dict]:
        """
        Score sources using theme-specific scoring.
        
        Args:
            sources: List of source dictionaries
            query: Research query
            theme: Theme instance
            
        Returns:
            List of sources with updated scores
        """
        scored_sources = []
        for source in sources:
            theme_score = theme.score_source(source, query)
            # Combine with existing relevance score
            existing_score = source.get('relevance_score', 0.5)
            combined_score = (existing_score + theme_score) / 2
            source['relevance_score'] = combined_score
            source['theme_score'] = theme_score
            scored_sources.append(source)
        
        return scored_sources


# Global theme manager instance
_theme_manager: Optional[ThemeManager] = None


def get_theme_manager() -> ThemeManager:
    """Get global theme manager instance."""
    global _theme_manager
    if _theme_manager is None:
        _theme_manager = ThemeManager()
    return _theme_manager



