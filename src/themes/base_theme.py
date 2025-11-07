"""
Base Theme - Abstract base class for research themes.
Defines interface for theme-specific research configurations.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from enum import Enum


class SourcePriority(Enum):
    """Source priority levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BaseTheme(ABC):
    """
    Abstract base class for research themes.
    Each theme provides specific configurations for source prioritization,
    analysis focus, and output characteristics.
    """
    
    def __init__(self, theme_options: Optional[Dict] = None):
        """
        Initialize theme.
        
        Args:
            theme_options: Theme-specific options
        """
        self.theme_options = theme_options or {}
        self.name = self.get_theme_name()
    
    @abstractmethod
    def get_theme_name(self) -> str:
        """Get theme name."""
        pass
    
    @abstractmethod
    def get_source_priorities(self) -> Dict[str, SourcePriority]:
        """
        Get source type priorities.
        
        Returns:
            Dictionary mapping source types to priority levels
        """
        pass
    
    @abstractmethod
    def get_analysis_focus(self) -> List[str]:
        """
        Get analysis focus areas.
        
        Returns:
            List of focus areas for analysis
        """
        pass
    
    @abstractmethod
    def get_output_characteristics(self) -> Dict:
        """
        Get output characteristics.
        
        Returns:
            Dictionary with tone, citation style, structure preferences
        """
        pass
    
    def get_preferred_domains(self) -> List[str]:
        """
        Get preferred source domains.
        
        Returns:
            List of preferred domain patterns
        """
        return []
    
    def get_citation_style(self) -> str:
        """
        Get preferred citation style.
        
        Returns:
            Citation style name
        """
        return self.get_output_characteristics().get('citation_style', 'apa')
    
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for theme.
        
        Args:
            query: Original query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        # Default: return empty list to use standard decomposition
        return []
    
    def score_source(self, source: Dict, query: str) -> float:
        """
        Score source relevance for this theme.
        
        Args:
            source: Source dictionary
            query: Research query
            
        Returns:
            Relevance score (0-1)
        """
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        
        # Check preferred domains
        preferred_domains = self.get_preferred_domains()
        if preferred_domains:
            for preferred in preferred_domains:
                if preferred.lower() in url or preferred.lower() in domain:
                    return 0.9  # High score for preferred domains
        
        return 0.5  # Default score



