"""
Plugin Manager - Manages domain-specific research plugins.
Handles plugin registration, selection, and combination.
"""

from typing import List, Dict, Optional, Type
from src.plugins.base_plugin import BasePlugin
from src.plugins.academic_plugin import AcademicResearchPlugin
from src.plugins.news_plugin import NewsResearchPlugin
from src.plugins.technical_plugin import TechnicalResearchPlugin
from src.plugins.business_plugin import BusinessResearchPlugin


class PluginManager:
    """
    Manages domain-specific research plugins.
    Handles plugin registration, selection, and combination.
    """
    
    def __init__(self):
        """Initialize plugin manager."""
        self.plugins: List[BasePlugin] = []
        self._register_default_plugins()
    
    def _register_default_plugins(self):
        """Register default plugins."""
        self.register_plugin(AcademicResearchPlugin())
        self.register_plugin(NewsResearchPlugin())
        self.register_plugin(TechnicalResearchPlugin())
        self.register_plugin(BusinessResearchPlugin())
    
    def register_plugin(self, plugin: BasePlugin):
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance to register
        """
        if plugin not in self.plugins:
            self.plugins.append(plugin)
    
    def unregister_plugin(self, plugin_name: str):
        """
        Unregister a plugin by name.
        
        Args:
            plugin_name: Name of plugin to unregister
        """
        self.plugins = [p for p in self.plugins if p.name != plugin_name]
    
    def get_applicable_plugins(self, query: str) -> List[BasePlugin]:
        """
        Get plugins applicable to a query.
        
        Args:
            query: Research query
            
        Returns:
            List of applicable plugins, sorted by priority
        """
        applicable = [p for p in self.plugins if p.enabled and p.is_applicable(query)]
        # Sort by priority (highest first)
        applicable.sort(key=lambda p: p.priority.value, reverse=True)
        return applicable
    
    def get_plugin_by_name(self, name: str) -> Optional[BasePlugin]:
        """
        Get plugin by name.
        
        Args:
            name: Plugin name
            
        Returns:
            Plugin instance or None
        """
        for plugin in self.plugins:
            if plugin.name == name:
                return plugin
        return None
    
    def combine_plugins(self, plugins: List[BasePlugin]) -> Dict:
        """
        Combine multiple plugins to create a unified configuration.
        
        Args:
            plugins: List of plugins to combine
            
        Returns:
            Combined configuration dictionary
        """
        if not plugins:
            return {}
        
        # Combine preferred sources (union)
        all_sources = set()
        for plugin in plugins:
            all_sources.update(plugin.get_preferred_sources())
        
        # Use citation style from highest priority plugin
        citation_style = plugins[0].get_citation_style()
        
        # Combine output sections
        all_sections = []
        for plugin in plugins:
            all_sections.extend(plugin.get_output_sections())
        # Remove duplicates while preserving order
        unique_sections = []
        seen = set()
        for section in all_sections:
            if section not in seen:
                unique_sections.append(section)
                seen.add(section)
        
        # Combine search modifiers
        combined_modifiers = {}
        for plugin in plugins:
            modifiers = plugin.get_search_modifiers()
            combined_modifiers.update(modifiers)
        
        return {
            'preferred_sources': list(all_sources),
            'citation_style': citation_style,
            'output_sections': unique_sections,
            'search_modifiers': combined_modifiers,
            'plugins': [p.name for p in plugins]
        }
    
    def get_combined_config(self, query: str, max_plugins: int = 2) -> Dict:
        """
        Get combined configuration from applicable plugins.
        
        Args:
            query: Research query
            max_plugins: Maximum number of plugins to combine
            
        Returns:
            Combined configuration dictionary
        """
        applicable = self.get_applicable_plugins(query)
        selected = applicable[:max_plugins]
        
        if not selected:
            return {}
        
        return self.combine_plugins(selected)
    
    def score_source_with_plugins(self, source: Dict, query: str) -> float:
        """
        Score source using all applicable plugins.
        
        Args:
            source: Source dictionary
            query: Research query
            
        Returns:
            Combined relevance score (0.0-1.0)
        """
        applicable = self.get_applicable_plugins(query)
        
        if not applicable:
            return 0.5  # Default score
        
        # Average scores from all applicable plugins
        scores = [plugin.score_source_relevance(source, query) for plugin in applicable]
        return sum(scores) / len(scores) if scores else 0.5
    
    def get_all_plugins(self) -> List[BasePlugin]:
        """Get all registered plugins."""
        return self.plugins.copy()
    
    def get_plugin_metadata(self) -> List[Dict]:
        """Get metadata for all plugins."""
        return [p.get_metadata() for p in self.plugins]


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager instance."""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager



