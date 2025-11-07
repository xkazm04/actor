"""
Unit tests for UX Improvement 6: Smart Source Diversity & Bias Detection
"""

import pytest
from src.diversity.diversity_scorer import DiversityScorer
from src.diversity.bias_detector import BiasDetector
from src.diversity.perspective_balancer import PerspectiveBalancer
from src.diversity.diversity_manager import DiversityManager


class TestDiversityScorer:
    """Test diversity scorer."""
    
    def test_scorer_initialization(self):
        """Test scorer initialization."""
        scorer = DiversityScorer()
        assert scorer is not None
    
    def test_calculate_diversity_score_empty(self):
        """Test diversity score with empty sources."""
        scorer = DiversityScorer()
        result = scorer.calculate_diversity_score([])
        assert result['overall_score'] == 0
    
    def test_calculate_diversity_score(self):
        """Test diversity score calculation."""
        scorer = DiversityScorer()
        sources = [
            {'url': 'https://example.com/article1', 'domain': 'example.com'},
            {'url': 'https://test.co.uk/article2', 'domain': 'test.co.uk'},
            {'url': 'https://sample.de/article3', 'domain': 'sample.de'}
        ]
        result = scorer.calculate_diversity_score(sources)
        assert 'overall_score' in result
        assert 'geographic_diversity' in result
        assert 'domain_diversity' in result
    
    def test_calculate_geographic_diversity(self):
        """Test geographic diversity calculation."""
        scorer = DiversityScorer()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com'},
            {'url': 'https://test.co.uk', 'domain': 'test.co.uk'}
        ]
        score = scorer._calculate_geographic_diversity(sources)
        assert 0 <= score <= 100
    
    def test_calculate_domain_diversity(self):
        """Test domain diversity calculation."""
        scorer = DiversityScorer()
        sources = [
            {'domain': 'example.com'},
            {'domain': 'test.com'},
            {'domain': 'sample.com'}
        ]
        score = scorer._calculate_domain_diversity(sources)
        assert 0 <= score <= 100


class TestBiasDetector:
    """Test bias detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = BiasDetector()
        assert detector is not None
    
    def test_detect_bias(self):
        """Test bias detection."""
        detector = BiasDetector()
        source = {
            'url': 'https://reuters.com/article',
            'title': 'News Article',
            'snippet': 'Factual report',
            'domain': 'reuters.com'
        }
        result = detector.detect_bias(source)
        assert 'political_leaning' in result
        assert 'is_sponsored' in result
        assert 'is_sensationalist' in result
    
    def test_detect_political_leaning(self):
        """Test political leaning detection."""
        detector = BiasDetector()
        text = "reuters news article"
        domain = "reuters.com"
        leaning = detector._detect_political_leaning(text, domain)
        assert leaning in ['left', 'right', 'center', 'unknown']
    
    def test_get_bias_summary(self):
        """Test bias summary generation."""
        detector = BiasDetector()
        sources = [
            {'url': 'https://reuters.com/article', 'domain': 'reuters.com'},
            {'url': 'https://bbc.com/article', 'domain': 'bbc.com'}
        ]
        summary = detector.get_bias_summary(sources)
        assert 'total_sources' in summary
        assert 'political_distribution' in summary


class TestPerspectiveBalancer:
    """Test perspective balancer."""
    
    def test_balancer_initialization(self):
        """Test balancer initialization."""
        balancer = PerspectiveBalancer()
        assert balancer is not None
    
    def test_balance_sources(self):
        """Test source balancing."""
        balancer = PerspectiveBalancer()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com', 'relevance_score': 0.8},
            {'url': 'https://test.com', 'domain': 'test.com', 'relevance_score': 0.7}
        ]
        balanced = balancer.balance_sources(sources)
        assert len(balanced) <= len(sources)
    
    def test_get_balance_report(self):
        """Test balance report generation."""
        balancer = PerspectiveBalancer()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com'}
        ]
        report = balancer.get_balance_report(sources)
        assert 'balance_score' in report
        assert 'distribution' in report


class TestDiversityManager:
    """Test diversity manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = DiversityManager()
        assert manager is not None
    
    def test_analyze_diversity(self):
        """Test diversity analysis."""
        manager = DiversityManager()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com'},
            {'url': 'https://test.co.uk', 'domain': 'test.co.uk'}
        ]
        analysis = manager.analyze_diversity(sources)
        assert 'diversity_score' in analysis
        assert 'bias_summary' in analysis
    
    def test_score_source_diversity(self):
        """Test source diversity scoring."""
        manager = DiversityManager()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com'}
        ]
        score = manager.score_source_diversity(sources)
        assert 'overall_score' in score


class TestIntegration:
    """Integration tests for UX Improvement 6."""
    
    def test_diversity_analysis_workflow(self):
        """Test complete diversity analysis workflow."""
        manager = DiversityManager()
        sources = [
            {'url': 'https://reuters.com/article1', 'domain': 'reuters.com', 'relevance_score': 0.8},
            {'url': 'https://bbc.com/article2', 'domain': 'bbc.com', 'relevance_score': 0.7},
            {'url': 'https://example.com/article3', 'domain': 'example.com', 'relevance_score': 0.6}
        ]
        
        analysis = manager.analyze_diversity(sources, enable_balancing=False)
        assert 'diversity_score' in analysis
        assert 'bias_summary' in analysis
    
    def test_perspective_balancing_workflow(self):
        """Test perspective balancing workflow."""
        manager = DiversityManager()
        sources = [
            {'url': 'https://example.com', 'domain': 'example.com', 'relevance_score': 0.8},
            {'url': 'https://test.com', 'domain': 'test.com', 'relevance_score': 0.7}
        ]
        
        balanced = manager.balance_perspectives(sources)
        assert len(balanced) <= len(sources)



