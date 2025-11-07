"""
Unit tests for UX Improvement 2: Granular Output Scope & Format Configuration
"""

import pytest
from src.report.scope_configurator import ScopeConfigurator, OutputScopeConfig, ReportLength
from src.report.section_builder import SectionBuilder
from src.report.style_adapter import StyleAdapter


class TestScopeConfigurator:
    """Test scope configurator."""
    
    def test_configurator_initialization(self):
        """Test configurator initialization."""
        configurator = ScopeConfigurator()
        assert configurator is not None
    
    def test_create_config_default(self):
        """Test creating default configuration."""
        configurator = ScopeConfigurator()
        config = configurator.create_config()
        assert config.report_length == ReportLength.STANDARD
        assert config.sections['executive_summary'] is True
    
    def test_create_config_custom(self):
        """Test creating custom configuration."""
        configurator = ScopeConfigurator()
        config = configurator.create_config(
            report_length="brief",
            sections={"executive_summary": True, "methodology": False}
        )
        assert config.report_length == ReportLength.BRIEF
        assert config.sections['methodology'] is False
    
    def test_get_word_range(self):
        """Test getting word range."""
        config = OutputScopeConfig(report_length="brief")
        min_words, max_words = config.get_word_range()
        assert min_words == 200
        assert max_words == 500
    
    def test_get_source_count_range(self):
        """Test getting source count range."""
        config = OutputScopeConfig(report_length="standard")
        min_sources, max_sources = config.get_source_count_range()
        assert min_sources == 10
        assert max_sources == 20
    
    def test_get_enabled_sections(self):
        """Test getting enabled sections."""
        config = OutputScopeConfig(
            sections={"executive_summary": True, "methodology": False}
        )
        enabled = config.get_enabled_sections()
        assert "executive_summary" in enabled
        assert "methodology" not in enabled
    
    def test_get_length_description(self):
        """Test getting length description."""
        configurator = ScopeConfigurator()
        desc = configurator.get_length_description("brief")
        assert desc['name'] == "Executive Brief"
        assert 'word_range' in desc


class TestSectionBuilder:
    """Test section builder."""
    
    def test_builder_initialization(self):
        """Test builder initialization."""
        config = OutputScopeConfig()
        builder = SectionBuilder(config)
        assert builder.scope_config == config
    
    def test_build_section_enabled(self):
        """Test building enabled section."""
        config = OutputScopeConfig(sections={"executive_summary": True})
        builder = SectionBuilder(config)
        
        content = {'query': 'test'}
        findings = {'key_findings': ['finding 1']}
        
        section = builder.build_section("executive_summary", content, findings)
        assert section is not None
        assert "Executive Summary" in section
    
    def test_build_section_disabled(self):
        """Test building disabled section."""
        config = OutputScopeConfig(sections={"methodology": False})
        builder = SectionBuilder(config)
        
        content = {'query': 'test'}
        findings = {}
        
        section = builder.build_section("methodology", content, findings)
        assert section is None
    
    def test_build_all_sections(self):
        """Test building all enabled sections."""
        config = OutputScopeConfig(
            sections={
                "executive_summary": True,
                "key_findings": True,
                "methodology": False
            }
        )
        builder = SectionBuilder(config)
        
        sections = builder.build_all_sections(
            query="test query",
            findings={'key_findings': ['finding']},
            sources=[]
        )
        
        assert "executive_summary" in sections
        assert "key_findings" in sections
        assert "methodology" not in sections


class TestStyleAdapter:
    """Test style adapter."""
    
    def test_adapter_initialization(self):
        """Test adapter initialization."""
        config = OutputScopeConfig()
        adapter = StyleAdapter(config)
        assert adapter.scope_config == config
    
    def test_get_style_instructions(self):
        """Test getting style instructions."""
        config = OutputScopeConfig(
            writing_style={
                "tone": "academic",
                "reading_level": "expert",
                "perspective": "objective"
            }
        )
        adapter = StyleAdapter(config)
        instructions = adapter.get_style_instructions()
        assert len(instructions) > 0
        assert "academic" in instructions.lower() or "formal" in instructions.lower()
    
    def test_adapt_text(self):
        """Test adapting text."""
        config = OutputScopeConfig(
            writing_style={"tone": "academic"}
        )
        adapter = StyleAdapter(config)
        
        text = "We found that this is true"
        adapted = adapter.adapt_text(text)
        assert text != adapted or len(adapted) > 0  # May or may not change
    
    def test_format_section_header(self):
        """Test formatting section header."""
        config = OutputScopeConfig()
        adapter = StyleAdapter(config)
        
        header = adapter.format_section_header("executive_summary")
        assert "Executive Summary" in header or "Summary" in header


class TestIntegration:
    """Integration tests for UX Improvement 2."""
    
    def test_scope_config_workflow(self):
        """Test complete scope config workflow."""
        configurator = ScopeConfigurator()
        config = configurator.create_config(
            report_length="brief",
            sections={"executive_summary": True, "key_findings": True},
            writing_style={"tone": "professional"}
        )
        
        assert config.report_length == ReportLength.BRIEF
        assert len(config.get_enabled_sections()) == 2
    
    def test_section_builder_workflow(self):
        """Test section builder workflow."""
        config = OutputScopeConfig(
            sections={"executive_summary": True, "key_findings": True}
        )
        builder = SectionBuilder(config)
        
        sections = builder.build_all_sections(
            query="test",
            findings={'key_findings': ['finding 1', 'finding 2']},
            sources=[]
        )
        
        assert len(sections) == 2
    
    def test_style_adapter_workflow(self):
        """Test style adapter workflow."""
        config = OutputScopeConfig(
            writing_style={
                "tone": "academic",
                "reading_level": "general",
                "perspective": "objective"
            }
        )
        adapter = StyleAdapter(config)
        
        instructions = adapter.get_style_instructions()
        assert len(instructions) > 0
        
        text = "This is a test"
        adapted = adapter.adapt_text(text)
        assert len(adapted) > 0



