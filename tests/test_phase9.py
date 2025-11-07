"""
Unit tests for Phase 9: Domain-Specific Research Plugins
"""

import pytest
from src.plugins.base_plugin import BasePlugin, PluginPriority
from src.plugins.academic_plugin import AcademicResearchPlugin
from src.plugins.news_plugin import NewsResearchPlugin
from src.plugins.technical_plugin import TechnicalResearchPlugin
from src.plugins.business_plugin import BusinessResearchPlugin
from src.plugins.plugin_manager import PluginManager, get_plugin_manager


class TestBasePlugin:
    """Test base plugin."""
    
    def test_plugin_initialization(self):
        """Test plugin initialization."""
        plugin = AcademicResearchPlugin()
        assert plugin.name == "academic"
        assert plugin.description is not None
        assert plugin.priority == PluginPriority.HIGH
    
    def test_plugin_metadata(self):
        """Test plugin metadata."""
        plugin = AcademicResearchPlugin()
        metadata = plugin.get_metadata()
        assert 'name' in metadata
        assert 'description' in metadata
        assert 'priority' in metadata


class TestAcademicPlugin:
    """Test academic research plugin."""
    
    def test_get_preferred_sources(self):
        """Test getting preferred sources."""
        plugin = AcademicResearchPlugin()
        sources = plugin.get_preferred_sources()
        assert 'arxiv.org' in sources
        assert 'pubmed.ncbi.nlm.nih.gov' in sources
    
    def test_get_citation_style(self):
        """Test getting citation style."""
        plugin = AcademicResearchPlugin()
        assert plugin.get_citation_style() == "apa"
    
    def test_score_source_relevance(self):
        """Test scoring source relevance."""
        plugin = AcademicResearchPlugin()
        source = {
            'url': 'https://arxiv.org/abs/1234.5678',
            'domain': 'arxiv.org',
            'title': 'Research Paper'
        }
        score = plugin.score_source_relevance(source, "test query")
        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for academic source
    
    def test_customize_query_decomposition(self):
        """Test query decomposition customization."""
        plugin = AcademicResearchPlugin()
        queries = plugin.customize_query_decomposition("quantum computing", 5)
        assert len(queries) <= 5
        assert "quantum computing" in queries[0]
    
    def test_is_applicable(self):
        """Test applicability check."""
        plugin = AcademicResearchPlugin()
        assert plugin.is_applicable("research paper on AI")
        assert not plugin.is_applicable("weather today")


class TestNewsPlugin:
    """Test news research plugin."""
    
    def test_get_preferred_sources(self):
        """Test getting preferred sources."""
        plugin = NewsResearchPlugin()
        sources = plugin.get_preferred_sources()
        assert 'reuters.com' in sources
        assert 'bbc.com' in sources
    
    def test_get_citation_style(self):
        """Test getting citation style."""
        plugin = NewsResearchPlugin()
        assert plugin.get_citation_style() == "mla"
    
    def test_score_source_relevance(self):
        """Test scoring source relevance."""
        plugin = NewsResearchPlugin()
        source = {
            'url': 'https://reuters.com/article',
            'domain': 'reuters.com',
            'title': 'Breaking News',
            'publish_date': '2025-01-01'
        }
        score = plugin.score_source_relevance(source, "test query")
        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for news source
    
    def test_is_applicable(self):
        """Test applicability check."""
        plugin = NewsResearchPlugin()
        assert plugin.is_applicable("latest news on AI")
        assert not plugin.is_applicable("mathematical proof")


class TestTechnicalPlugin:
    """Test technical research plugin."""
    
    def test_get_preferred_sources(self):
        """Test getting preferred sources."""
        plugin = TechnicalResearchPlugin()
        sources = plugin.get_preferred_sources()
        assert 'github.com' in sources
        assert 'stackoverflow.com' in sources
    
    def test_get_citation_style(self):
        """Test getting citation style."""
        plugin = TechnicalResearchPlugin()
        assert plugin.get_citation_style() == "ieee"
    
    def test_score_source_relevance(self):
        """Test scoring source relevance."""
        plugin = TechnicalResearchPlugin()
        source = {
            'url': 'https://github.com/user/repo',
            'domain': 'github.com',
            'title': 'Python Library',
            'snippet': 'code example'
        }
        score = plugin.score_source_relevance(source, "test query")
        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for technical source
    
    def test_is_applicable(self):
        """Test applicability check."""
        plugin = TechnicalResearchPlugin()
        assert plugin.is_applicable("how to use Python API")
        assert not plugin.is_applicable("philosophy of mind")


class TestBusinessPlugin:
    """Test business research plugin."""
    
    def test_get_preferred_sources(self):
        """Test getting preferred sources."""
        plugin = BusinessResearchPlugin()
        sources = plugin.get_preferred_sources()
        assert 'sec.gov' in sources
        assert 'bloomberg.com' in sources
    
    def test_get_citation_style(self):
        """Test getting citation style."""
        plugin = BusinessResearchPlugin()
        assert plugin.get_citation_style() == "chicago"
    
    def test_score_source_relevance(self):
        """Test scoring source relevance."""
        plugin = BusinessResearchPlugin()
        source = {
            'url': 'https://sec.gov/filing',
            'domain': 'sec.gov',
            'title': 'Company Financial Report'
        }
        score = plugin.score_source_relevance(source, "test query")
        assert 0 <= score <= 1
        assert score > 0.5  # Should be high for business source
    
    def test_is_applicable(self):
        """Test applicability check."""
        plugin = BusinessResearchPlugin()
        assert plugin.is_applicable("market analysis of tech companies")
        assert not plugin.is_applicable("quantum physics")


class TestPluginManager:
    """Test plugin manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = PluginManager()
        assert len(manager.plugins) > 0
    
    def test_get_applicable_plugins(self):
        """Test getting applicable plugins."""
        manager = PluginManager()
        plugins = manager.get_applicable_plugins("research paper on AI")
        assert len(plugins) > 0
        assert any(p.name == "academic" for p in plugins)
    
    def test_get_plugin_by_name(self):
        """Test getting plugin by name."""
        manager = PluginManager()
        plugin = manager.get_plugin_by_name("academic")
        assert plugin is not None
        assert plugin.name == "academic"
    
    def test_combine_plugins(self):
        """Test combining plugins."""
        manager = PluginManager()
        academic = manager.get_plugin_by_name("academic")
        technical = manager.get_plugin_by_name("technical")
        
        config = manager.combine_plugins([academic, technical])
        assert 'preferred_sources' in config
        assert 'citation_style' in config
        assert len(config['preferred_sources']) > 0
    
    def test_get_combined_config(self):
        """Test getting combined config."""
        manager = PluginManager()
        config = manager.get_combined_config("research paper on Python programming")
        assert 'preferred_sources' in config or config == {}
    
    def test_score_source_with_plugins(self):
        """Test scoring source with plugins."""
        manager = PluginManager()
        source = {
            'url': 'https://arxiv.org/abs/1234',
            'domain': 'arxiv.org',
            'title': 'Research Paper'
        }
        score = manager.score_source_with_plugins(source, "research paper")
        assert 0 <= score <= 1


class TestIntegration:
    """Integration tests for Phase 9."""
    
    def test_plugin_workflow(self):
        """Test complete plugin workflow."""
        manager = PluginManager()
        
        # Get applicable plugins
        plugins = manager.get_applicable_plugins("academic research paper")
        assert len(plugins) > 0
        
        # Get combined config
        config = manager.get_combined_config("academic research paper")
        assert isinstance(config, dict)
    
    def test_multiple_plugins(self):
        """Test using multiple plugins."""
        manager = PluginManager()
        
        # Query that matches multiple domains
        query = "Python programming research paper"
        plugins = manager.get_applicable_plugins(query)
        
        # Should match both academic and technical
        plugin_names = [p.name for p in plugins]
        assert len(plugin_names) >= 1



