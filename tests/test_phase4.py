"""
Unit tests for Phase 4: Report Generation & Structured Output
"""

import pytest
from src.report.citation_manager import CitationManager, Citation
from src.report.formatters import format_markdown_to_html, format_json_report, export_to_json


class TestCitation:
    """Test Citation model."""
    
    def test_citation_creation(self):
        """Test creating a citation."""
        citation = Citation(
            id=1,
            url="https://example.com",
            title="Example Article",
            author="John Doe"
        )
        assert citation.id == 1
        assert citation.url == "https://example.com"
        assert citation.title == "Example Article"
        assert citation.domain == "example.com"


class TestCitationManager:
    """Test citation manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = CitationManager()
        assert len(manager.citations) == 0
    
    def test_add_citation(self):
        """Test adding a citation."""
        manager = CitationManager()
        citation_id = manager.add_citation(
            url="https://example.com",
            title="Example",
            author="Author"
        )
        assert citation_id == 1
        assert len(manager.citations) == 1
    
    def test_add_citation_duplicate(self):
        """Test adding duplicate citation."""
        manager = CitationManager()
        id1 = manager.add_citation("https://example.com", "Title")
        id2 = manager.add_citation("https://example.com", "Title")
        assert id1 == id2
        assert len(manager.citations) == 1
    
    def test_link_claim_to_citation(self):
        """Test linking claim to citation."""
        manager = CitationManager()
        citation_id = manager.add_citation("https://example.com", "Title")
        manager.link_claim_to_citation("Test claim", citation_id)
        
        ids = manager.get_citation_ids_for_claim("Test claim")
        assert citation_id in ids
    
    def test_format_inline_citation(self):
        """Test inline citation formatting."""
        manager = CitationManager()
        formatted = manager.format_inline_citation([1, 2, 3])
        assert formatted == "[1][2][3]"
    
    def test_format_bibliography_apa(self):
        """Test APA bibliography formatting."""
        manager = CitationManager()
        manager.add_citation(
            url="https://example.com",
            title="Example Article",
            author="John Doe",
            publish_date="2024-01-01"
        )
        bib = manager.format_bibliography_apa()
        assert "References" in bib
        assert "John Doe" in bib
        assert "example.com" in bib
    
    def test_format_bibliography_mla(self):
        """Test MLA bibliography formatting."""
        manager = CitationManager()
        manager.add_citation(
            url="https://example.com",
            title="Example Article",
            author="John Doe"
        )
        bib = manager.format_bibliography_mla()
        assert "Works Cited" in bib
    
    def test_format_bibliography_chicago(self):
        """Test Chicago bibliography formatting."""
        manager = CitationManager()
        manager.add_citation(
            url="https://example.com",
            title="Example Article"
        )
        bib = manager.format_bibliography_chicago()
        assert "Bibliography" in bib


class TestFormatters:
    """Test report formatters."""
    
    def test_markdown_to_html(self):
        """Test markdown to HTML conversion."""
        markdown = "# Title\n\nParagraph text"
        html = format_markdown_to_html(markdown)
        assert "<html>" in html
        assert "<h1>Title</h1>" in html
    
    def test_format_json_report(self):
        """Test JSON report formatting."""
        data = {
            'query': 'Test query',
            'executive_summary': 'Summary text',
            'main_findings': {'Theme': 'Findings'},
            'conclusions': 'Conclusion text'
        }
        formatted = format_json_report(data)
        assert 'Test query' in formatted
        assert 'Executive Summary' in formatted
    
    def test_export_to_json(self):
        """Test JSON export."""
        data = {'key': 'value'}
        json_str = export_to_json(data, pretty=True)
        assert '"key"' in json_str
        assert '"value"' in json_str


@pytest.mark.skip(reason="Requires API keys")
class TestReportGenerator:
    """Test report generator (requires API keys)."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        from src.report.report_generator import ReportGenerator
        generator = ReportGenerator()
        assert generator.client is not None
    
    def test_generate_report(self):
        """Test report generation."""
        from src.report.report_generator import ReportGenerator
        generator = ReportGenerator()
        
        findings = {
            'key_findings': ['Finding 1'],
            'main_themes': ['Theme 1'],
            'key_facts': []
        }
        
        sources = [
            {'url': 'https://example.com', 'title': 'Example', 'snippet': 'Text'}
        ]
        
        report = generator.generate_report(
            query="Test query",
            findings=findings,
            ranked_sources=sources,
            output_format="markdown"
        )
        
        assert 'report' in report
        assert 'citations' in report
        assert report['format'] == 'markdown'


class TestIntegration:
    """Integration tests for Phase 4."""
    
    def test_citation_workflow(self):
        """Test complete citation workflow."""
        manager = CitationManager()
        
        # Add citations
        id1 = manager.add_citation("https://example1.com", "Article 1")
        id2 = manager.add_citation("https://example2.com", "Article 2")
        
        # Link claims
        manager.link_claim_to_citation("Claim 1", id1)
        manager.link_claim_to_citation("Claim 1", id2)
        
        # Format
        inline = manager.format_inline_citation([id1, id2])
        assert inline == "[1][2]"
        
        bib = manager.format_bibliography()
        assert len(manager.citations) == 2



