"""
Unit tests for UX Improvement 8: Multiple Export Formats & Sharing
"""

import pytest
from src.export.export_formats import ExportFormats
from src.export.export_manager import ExportManager
from src.export.sharing_manager import SharingManager


class TestExportFormats:
    """Test export formats."""
    
    def test_formats_initialization(self):
        """Test formats initialization."""
        formats = ExportFormats()
        assert formats is not None
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        formats = ExportFormats()
        supported = formats.get_supported_formats()
        assert 'pdf' in supported
        assert 'html' in supported
        assert 'json' in supported
    
    def test_export_to_html(self):
        """Test HTML export."""
        formats = ExportFormats()
        result = formats.export_to_html("<h1>Test</h1>")
        assert result['format'] == 'html'
        assert 'content' in result
    
    def test_export_to_json(self):
        """Test JSON export."""
        formats = ExportFormats()
        result = formats.export_to_json({'test': 'data'})
        assert result['format'] == 'json'
        assert 'content' in result
    
    def test_export_to_csv(self):
        """Test CSV export."""
        formats = ExportFormats()
        sources = [
            {'title': 'Test', 'url': 'https://example.com', 'domain': 'example.com'}
        ]
        result = formats.export_to_csv(sources)
        assert result['format'] == 'csv'
        assert 'content' in result
        assert result['row_count'] == 1
    
    def test_export_to_markdown(self):
        """Test Markdown export."""
        formats = ExportFormats()
        result = formats.export_to_markdown("# Test")
        assert result['format'] == 'markdown'
        assert 'content' in result


class TestExportManager:
    """Test export manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = ExportManager()
        assert manager is not None
    
    def test_export_report_html(self):
        """Test exporting report to HTML."""
        manager = ExportManager()
        result = manager.export_report(
            report_content="<h1>Test</h1>",
            report_data={'test': 'data'},
            sources=[],
            export_format='html'
        )
        assert result['format'] == 'html'
    
    def test_export_report_json(self):
        """Test exporting report to JSON."""
        manager = ExportManager()
        result = manager.export_report(
            report_content="Test",
            report_data={'test': 'data'},
            sources=[],
            export_format='json'
        )
        assert result['format'] == 'json'
    
    def test_export_multiple_formats(self):
        """Test exporting to multiple formats."""
        manager = ExportManager()
        result = manager.export_multiple_formats(
            report_content="Test",
            report_data={'test': 'data'},
            sources=[],
            formats=['html', 'json', 'markdown']
        )
        assert 'exports' in result
        assert len(result['exports']) == 3
    
    def test_get_export_info(self):
        """Test getting export format info."""
        manager = ExportManager()
        info = manager.get_export_info('html')
        assert 'name' in info
        assert 'description' in info


class TestSharingManager:
    """Test sharing manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = SharingManager()
        assert manager is not None
    
    def test_generate_shareable_link(self):
        """Test generating shareable link."""
        manager = SharingManager()
        result = manager.generate_shareable_link('test123', expiration_days=7)
        assert 'shareable_url' in result
        assert 'token' in result
        assert 'expiration_date' in result
    
    def test_create_public_link(self):
        """Test creating public link."""
        manager = SharingManager()
        result = manager.create_public_link('test123')
        assert 'public_url' in result
        assert 'token' in result
    
    def test_get_sharing_options(self):
        """Test getting sharing options."""
        manager = SharingManager()
        options = manager.get_sharing_options()
        assert 'shareable_link' in options
        assert 'public_link' in options
    
    def test_generate_embed_code(self):
        """Test generating embed code."""
        manager = SharingManager()
        result = manager.generate_embed_code('test123')
        assert 'embed_code' in result
        assert 'iframe' in result['embed_code']


class TestIntegration:
    """Integration tests for UX Improvement 8."""
    
    def test_export_workflow(self):
        """Test complete export workflow."""
        manager = ExportManager()
        result = manager.export_multiple_formats(
            report_content="Test report",
            report_data={'query': 'test'},
            sources=[],
            formats=['html', 'json']
        )
        assert result['success_count'] >= 0
        assert result['total_count'] == 2
    
    def test_sharing_workflow(self):
        """Test sharing workflow."""
        manager = SharingManager()
        shareable = manager.generate_shareable_link('test123')
        assert 'shareable_url' in shareable
        
        public = manager.create_public_link('test123')
        assert 'public_url' in public



