"""
Base Plugin - Abstract base class for domain-specific research plugins.
Defines the interface that all plugins must implement.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from enum import Enum


class PluginPriority(Enum):
    """Plugin priority levels."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class BasePlugin(ABC):
    """
    Abstract base class for domain-specific research plugins.
    All plugins must inherit from this class and implement required methods.
    """
    
    def __init__(self, name: str, description: str, priority: PluginPriority = PluginPriority.MEDIUM):
        """
        Initialize plugin.
        
        Args:
            name: Plugin name
            description: Plugin description
            priority: Plugin priority level
        """
        self.name = name
        self.description = description
        self.priority = priority
        self.enabled = True
    
    @abstractmethod
    def get_preferred_sources(self) -> List[str]:
        """
        Get list of preferred source domains/types for this plugin.
        
        Returns:
            List of preferred source identifiers
        """
        pass
    
    @abstractmethod
    def get_citation_style(self) -> str:
        """
        Get preferred citation style for this plugin.
        
        Returns:
            Citation style name (apa, mla, chicago, ieee)
        """
        pass
    
    @abstractmethod
    def score_source_relevance(self, source: Dict, query: str) -> float:
        """
        Score source relevance for this domain.
        
        Args:
            source: Source dictionary
            query: Research query
            
        Returns:
            Relevance score (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def customize_query_decomposition(self, query: str, max_sub_queries: int) -> List[str]:
        """
        Customize query decomposition for this domain.
        
        Args:
            query: Main research query
            max_sub_queries: Maximum number of sub-queries
            
        Returns:
            List of customized sub-queries
        """
        pass
    
    def customize_content_extraction(self, content: Dict) -> Dict:
        """
        Customize content extraction for this domain.
        Override in subclasses for domain-specific extraction.
        
        Args:
            content: Raw content dictionary
            
        Returns:
            Processed content dictionary
        """
        return content
    
    def customize_report_formatting(self, report: str, findings: Dict) -> str:
        """
        Customize report formatting for this domain.
        Override in subclasses for domain-specific formatting.
        
        Args:
            report: Generated report
            findings: Research findings
            
        Returns:
            Formatted report
        """
        return report
    
    def get_search_modifiers(self) -> Dict[str, Any]:
        """
        Get search API modifiers for this plugin.
        Override to customize search behavior.
        
        Returns:
            Dictionary of search modifiers
        """
        return {}
    
    def get_output_sections(self) -> List[str]:
        """
        Get preferred output sections for this domain.
        
        Returns:
            List of section names
        """
        return ["Introduction", "Findings", "Conclusion"]
    
    def is_applicable(self, query: str) -> bool:
        """
        Check if this plugin is applicable to a query.
        Override to implement domain detection logic.
        
        Args:
            query: Research query
            
        Returns:
            True if plugin is applicable
        """
        return True
    
    def get_metadata(self) -> Dict:
        """
        Get plugin metadata.
        
        Returns:
            Metadata dictionary
        """
        return {
            'name': self.name,
            'description': self.description,
            'priority': self.priority.value,
            'enabled': self.enabled
        }



