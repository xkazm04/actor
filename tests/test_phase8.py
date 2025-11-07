"""
Unit tests for Phase 8: Multi-Source Citation System
"""

import pytest
from src.citations.citation_manager import CitationManager, Citation
from src.citations.source_verifier import SourceVerifier
from src.citations.citation_scorer import CitationScorer
from src.citations.styles import get_formatter, APAStyleFormatter, MLAStyleFormatter, ChicagoStyleFormatter, IEEEStyleFormatter


class TestCitationManager:
    """Test citation manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = CitationManager()
        assert len(manager.citations) == 0
        assert len(manager.citation_map) == 0
    
    def test_add_citation(self):
        """Test adding citation."""
        manager = CitationManager()
        citation_id = manager.add_citation(
            url="https://example.com",
            title="Test Article",
            author="John Doe",
            publish_date="2025-01-01"
        )
        
        assert citation_id == 1
        assert len(manager.citations) == 1
    
    def test_add_citation_duplicate(self):
        """Test adding duplicate citation."""
        manager = CitationManager()
        id1 = manager.add_citation("https://example.com", "Test")
        id2 = manager.add_citation("https://example.com", "Test")
        
        assert id1 == id2
        assert len(manager.citations) == 1
    
    def test_link_claim_to_citation(self):
        """Test linking claim to citation."""
        manager = CitationManager()
        citation_id = manager.add_citation("https://example.com", "Test")
        manager.link_claim_to_citation("Test claim", citation_id)
        
        assert citation_id in manager.claim_citations["Test claim"]
    
    def test_format_inline_citation(self):
        """Test inline citation formatting."""
        manager = CitationManager()
        formatted = manager.format_inline_citation([1, 2, 3])
        assert formatted == "[1][2][3]"
    
    def test_format_bibliography_apa(self):
        """Test APA bibliography formatting."""
        manager = CitationManager()
        manager.add_citation("https://example.com", "Test", "Author", "2025-01-01")
        bib = manager.format_bibliography("apa")
        
        assert "References" in bib
        assert "[1]" in bib
    
    def test_format_bibliography_mla(self):
        """Test MLA bibliography formatting."""
        manager = CitationManager()
        manager.add_citation("https://example.com", "Test", "Author", "2025-01-01")
        bib = manager.format_bibliography("mla")
        
        assert "Works Cited" in bib
        assert "[1]" in bib
    
    def test_format_bibliography_chicago(self):
        """Test Chicago bibliography formatting."""
        manager = CitationManager()
        manager.add_citation("https://example.com", "Test", "Author", "2025-01-01")
        bib = manager.format_bibliography("chicago")
        
        assert "Bibliography" in bib
        assert "[1]" in bib
    
    def test_format_bibliography_ieee(self):
        """Test IEEE bibliography formatting."""
        manager = CitationManager()
        manager.add_citation("https://example.com", "Test", "Author", "2025-01-01")
        bib = manager.format_bibliography("ieee")
        
        assert "References" in bib
        assert "[1]" in bib


class TestSourceVerifier:
    """Test source verifier."""
    
    def test_verifier_initialization(self):
        """Test verifier initialization."""
        verifier = SourceVerifier()
        assert verifier is not None
    
    def test_verify_source_academic(self):
        """Test verifying academic source."""
        verifier = SourceVerifier()
        source = {
            'url': 'https://example.edu/article',
            'domain': 'example.edu',
            'title': 'Academic Article'
        }
        
        result = verifier.verify_source(source)
        assert result['is_academic'] is True
        assert result['quality_score'] > 0.8
    
    def test_verify_source_fact_check(self):
        """Test verifying fact-check source."""
        verifier = SourceVerifier()
        source = {
            'url': 'https://snopes.com/article',
            'domain': 'snopes.com',
            'title': 'Fact Check'
        }
        
        result = verifier.verify_source(source)
        assert result['is_fact_check'] is True
        assert result['quality_score'] > 0.8
    
    def test_calculate_claim_confidence(self):
        """Test calculating claim confidence."""
        verifier = SourceVerifier()
        sources = [
            {'url': 'https://example.edu/article', 'domain': 'example.edu', 'title': 'Test'}
        ]
        
        result = verifier.calculate_claim_confidence("Test claim", sources)
        assert 'confidence' in result
        assert 'score' in result
        assert result['source_count'] == 1


class TestCitationScorer:
    """Test citation scorer."""
    
    def test_scorer_initialization(self):
        """Test scorer initialization."""
        scorer = CitationScorer()
        assert scorer is not None
    
    def test_score_citation_quality(self):
        """Test scoring citation quality."""
        scorer = CitationScorer()
        citation = {
            'id': 1,
            'url': 'https://example.com',
            'title': 'Test',
            'author': 'Author'
        }
        
        result = scorer.score_citation_quality(citation)
        assert 'quality_score' in result
        assert result['quality_score'] >= 0
    
    def test_calculate_source_diversity(self):
        """Test calculating source diversity."""
        scorer = CitationScorer()
        citations = [{'id': 1}]
        sources = [
            {'url': 'https://example1.com', 'domain': 'example1.com'},
            {'url': 'https://example2.com', 'domain': 'example2.com'}
        ]
        
        result = scorer.calculate_source_diversity(citations, sources)
        assert 'diversity_score' in result
        assert result['domain_count'] == 2
    
    def test_identify_unsupported_claims(self):
        """Test identifying unsupported claims."""
        scorer = CitationScorer()
        claims = ["Claim 1", "Claim 2"]
        claim_citations = {"Claim 1": [1]}
        
        result = scorer.identify_unsupported_claims(claims, claim_citations)
        assert len(result) > 0
        assert any(c['claim'] == "Claim 2" for c in result)
    
    def test_calculate_citation_coverage(self):
        """Test calculating citation coverage."""
        scorer = CitationScorer()
        claims = ["Claim 1", "Claim 2"]
        claim_citations = {"Claim 1": [1], "Claim 2": [2]}
        
        result = scorer.calculate_citation_coverage(claims, claim_citations)
        assert result['coverage_percentage'] == 100.0
        assert result['supported_claims'] == 2


class TestCitationStyles:
    """Test citation style formatters."""
    
    def test_apa_formatter(self):
        """Test APA formatter."""
        formatter = APAStyleFormatter()
        citation = {
            'author': 'Doe, J.',
            'publish_date': '2025-01-01',
            'title': 'Test Article',
            'domain': 'example.com',
            'url': 'https://example.com'
        }
        
        formatted = formatter.format_citation(citation)
        assert 'Doe, J.' in formatted
        assert '(2025)' in formatted
    
    def test_mla_formatter(self):
        """Test MLA formatter."""
        formatter = MLAStyleFormatter()
        citation = {
            'author': 'Doe, John',
            'title': 'Test Article',
            'domain': 'example.com',
            'publish_date': '2025-01-01',
            'url': 'https://example.com'
        }
        
        formatted = formatter.format_citation(citation)
        assert 'Doe, John' in formatted
        assert '"Test Article."' in formatted
    
    def test_chicago_formatter(self):
        """Test Chicago formatter."""
        formatter = ChicagoStyleFormatter()
        citation = {
            'author': 'Doe, John',
            'title': 'Test Article',
            'domain': 'example.com',
            'publish_date': '2025-01-01',
            'url': 'https://example.com'
        }
        
        formatted = formatter.format_citation(citation)
        assert 'Doe, John' in formatted
        assert '"Test Article."' in formatted
    
    def test_ieee_formatter(self):
        """Test IEEE formatter."""
        formatter = IEEEStyleFormatter()
        citation = {
            'author': 'J. Doe',
            'title': 'Test Article',
            'domain': 'example.com',
            'publish_date': '2025-01-01',
            'url': 'https://example.com'
        }
        
        formatted = formatter.format_citation(citation)
        assert 'J. Doe' in formatted
        assert '[Online]' in formatted
    
    def test_get_formatter(self):
        """Test getting formatter by style name."""
        apa = get_formatter("apa")
        assert isinstance(apa, APAStyleFormatter)
        
        mla = get_formatter("mla")
        assert isinstance(mla, MLAStyleFormatter)
        
        chicago = get_formatter("chicago")
        assert isinstance(chicago, ChicagoStyleFormatter)
        
        ieee = get_formatter("ieee")
        assert isinstance(ieee, IEEEStyleFormatter)


class TestIntegration:
    """Integration tests for Phase 8."""
    
    def test_citation_workflow(self):
        """Test complete citation workflow."""
        manager = CitationManager()
        
        # Add citations
        source1 = {
            'url': 'https://example.edu/article',
            'title': 'Academic Article',
            'domain': 'example.edu'
        }
        citation_id1 = manager.add_citation_from_source(source1)
        
        source2 = {
            'url': 'https://example.com/article',
            'title': 'Regular Article',
            'domain': 'example.com'
        }
        citation_id2 = manager.add_citation_from_source(source2)
        
        # Link claims
        manager.link_claim_to_citation("Claim 1", citation_id1)
        manager.link_claim_to_citation("Claim 1", citation_id2)
        
        # Verify sources
        verification = manager.verify_all_sources()
        assert verification['total_sources'] == 2
        
        # Calculate statistics
        claims = ["Claim 1"]
        stats = manager.get_citation_statistics(claims)
        assert stats['total_citations'] == 2
        assert stats['coverage']['coverage_percentage'] == 100.0
    
    def test_citation_quality_scoring(self):
        """Test citation quality scoring."""
        manager = CitationManager()
        citation_id = manager.add_citation(
            "https://example.edu/article",
            "Academic Article",
            "Author",
            "2025-01-01"
        )
        
        source = {
            'url': 'https://example.edu/article',
            'domain': 'example.edu',
            'title': 'Academic Article'
        }
        manager.sources[citation_id] = source
        
        quality = manager.score_citation_quality(citation_id)
        assert 'quality_score' in quality
        assert quality['quality_score'] > 0



