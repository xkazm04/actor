"""
Unit tests for UX Improvement 3: Research Theme Intelligence
"""

import pytest
from src.themes.theme_detector import ThemeDetector, ResearchTheme
from src.themes.theme_manager import ThemeManager
from src.themes.academic_theme import AcademicTheme
from src.themes.news_theme import NewsTheme
from src.themes.business_theme import BusinessTheme
from src.themes.technical_theme import TechnicalTheme
from src.themes.general_theme import GeneralTheme


class TestThemeDetector:
    """Test theme detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = ThemeDetector()
        assert detector is not None
    
    def test_detect_academic_theme(self):
        """Test detecting academic theme."""
        detector = ThemeDetector()
        theme, confidence = detector.detect_theme("What are the latest research findings on quantum computing?")
        assert theme == ResearchTheme.ACADEMIC or theme == ResearchTheme.GENERAL
    
    def test_detect_news_theme(self):
        """Test detecting news theme."""
        detector = ThemeDetector()
        theme, confidence = detector.detect_theme("What happened today in the tech industry?")
        assert theme == ResearchTheme.NEWS or theme == ResearchTheme.GENERAL
    
    def test_detect_business_theme(self):
        """Test detecting business theme."""
        detector = ThemeDetector()
        theme, confidence = detector.detect_theme("What is the market size and revenue for electric vehicles?")
        assert theme == ResearchTheme.BUSINESS or theme == ResearchTheme.GENERAL
    
    def test_detect_technical_theme(self):
        """Test detecting technical theme."""
        detector = ThemeDetector()
        theme, confidence = detector.detect_theme("How to implement authentication in Python Flask?")
        assert theme == ResearchTheme.TECHNICAL or theme == ResearchTheme.GENERAL
    
    def test_detect_with_explanation(self):
        """Test detection with explanation."""
        detector = ThemeDetector()
        result = detector.detect_with_explanation("Latest research on AI")
        assert 'theme' in result
        assert 'confidence' in result
        assert 'explanation' in result


class TestThemeManager:
    """Test theme manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = ThemeManager()
        assert manager is not None
        assert len(manager.themes) > 0
    
    def test_detect_and_get_theme(self):
        """Test detect and get theme."""
        manager = ThemeManager()
        theme = manager.detect_and_get_theme("Research on quantum computing")
        assert theme is not None
        assert hasattr(theme, 'get_theme_name')
    
    def test_get_theme_by_name(self):
        """Test getting theme by name."""
        manager = ThemeManager()
        theme = manager.get_theme("academic")
        assert theme.get_theme_name() == "academic"
    
    def test_apply_theme_configuration(self):
        """Test applying theme configuration."""
        manager = ThemeManager()
        theme = manager.get_theme("academic")
        config = manager.apply_theme_configuration(theme, {})
        assert 'citation_style' in config
        assert 'tone' in config


class TestAcademicTheme:
    """Test academic theme."""
    
    def test_academic_theme_initialization(self):
        """Test academic theme initialization."""
        theme = AcademicTheme()
        assert theme.get_theme_name() == "academic"
    
    def test_get_source_priorities(self):
        """Test getting source priorities."""
        theme = AcademicTheme()
        priorities = theme.get_source_priorities()
        assert 'peer_reviewed_journals' in priorities
    
    def test_get_citation_style(self):
        """Test getting citation style."""
        theme = AcademicTheme({'citationStyle': 'MLA'})
        assert theme.get_citation_style() == 'mla'
    
    def test_score_source(self):
        """Test scoring source."""
        theme = AcademicTheme()
        source = {'url': 'https://example.edu/research', 'domain': 'example.edu'}
        score = theme.score_source(source, "test query")
        assert 0 <= score <= 1


class TestNewsTheme:
    """Test news theme."""
    
    def test_news_theme_initialization(self):
        """Test news theme initialization."""
        theme = NewsTheme()
        assert theme.get_theme_name() == "news"
    
    def test_get_output_characteristics(self):
        """Test getting output characteristics."""
        theme = NewsTheme()
        chars = theme.get_output_characteristics()
        assert chars['tone'] == 'conversational'
        assert chars['citation_style'] == 'mla'


class TestBusinessTheme:
    """Test business theme."""
    
    def test_business_theme_initialization(self):
        """Test business theme initialization."""
        theme = BusinessTheme()
        assert theme.get_theme_name() == "business"
    
    def test_get_analysis_focus(self):
        """Test getting analysis focus."""
        theme = BusinessTheme({'includeFinancials': True})
        focus = theme.get_analysis_focus()
        assert 'market_size' in focus
        assert 'revenue' in focus


class TestTechnicalTheme:
    """Test technical theme."""
    
    def test_technical_theme_initialization(self):
        """Test technical theme initialization."""
        theme = TechnicalTheme()
        assert theme.get_theme_name() == "technical"
    
    def test_get_preferred_domains(self):
        """Test getting preferred domains."""
        theme = TechnicalTheme()
        domains = theme.get_preferred_domains()
        assert 'github.com' in domains
        assert 'stackoverflow.com' in domains


class TestGeneralTheme:
    """Test general theme."""
    
    def test_general_theme_initialization(self):
        """Test general theme initialization."""
        theme = GeneralTheme()
        assert theme.get_theme_name() == "general"
    
    def test_get_source_priorities(self):
        """Test getting source priorities."""
        theme = GeneralTheme()
        priorities = theme.get_source_priorities()
        # General theme should have balanced priorities
        assert len(priorities) > 0


class TestIntegration:
    """Integration tests for UX Improvement 3."""
    
    def test_theme_detection_workflow(self):
        """Test complete theme detection workflow."""
        manager = ThemeManager()
        
        # Test academic query
        theme = manager.detect_and_get_theme("Research study on machine learning")
        assert theme.get_theme_name() in ["academic", "general"]
        
        # Test business query
        theme = manager.detect_and_get_theme("Market analysis for electric vehicles")
        assert theme.get_theme_name() in ["business", "general"]
    
    def test_theme_configuration_workflow(self):
        """Test theme configuration workflow."""
        manager = ThemeManager()
        theme = manager.get_theme("academic", {"academic": {"citationStyle": "MLA"}})
        assert theme.get_citation_style() == "mla"
        
        config = manager.apply_theme_configuration(theme, {})
        assert config['citation_style'] == 'mla'
    
    def test_source_scoring_workflow(self):
        """Test source scoring workflow."""
        manager = ThemeManager()
        theme = manager.get_theme("academic")
        
        sources = [
            {'url': 'https://example.edu/research', 'domain': 'example.edu', 'relevance_score': 0.5},
            {'url': 'https://example.com/blog', 'domain': 'example.com', 'relevance_score': 0.5}
        ]
        
        scored = manager.score_sources_with_theme(sources, "test query", theme)
        assert len(scored) == 2
        assert 'theme_score' in scored[0]



