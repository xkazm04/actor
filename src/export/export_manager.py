"""
Export Manager - Orchestrates export functionality.
Manages multiple export formats and export options.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor

from src.export.export_formats import ExportFormats, create_export_formats


class ExportManager:
    """
    Orchestrates export functionality.
    Manages multiple export formats and export options.
    """
    
    def __init__(self):
        """Initialize export manager."""
        self.export_formats = create_export_formats()
    
    def export_report(
        self,
        report_content: str,
        report_data: Dict,
        sources: List[Dict],
        export_format: str,
        metadata: Optional[Dict] = None,
        options: Optional[Dict] = None
    ) -> Dict:
        """
        Export report in specified format.
        
        Args:
            report_content: Report content (markdown/HTML)
            report_data: Full report data dictionary
            sources: List of sources
            export_format: Format to export to
            metadata: Optional metadata
            options: Optional export options
            
        Returns:
            Export result dictionary
        """
        export_format = export_format.lower()
        
        if export_format not in self.export_formats.get_supported_formats():
            Actor.log.warning(f"Unsupported export format: {export_format}")
            return {
                'error': f'Unsupported format: {export_format}',
                'supported_formats': self.export_formats.get_supported_formats()
            }
        
        # Prepare metadata
        export_metadata = {
            'exported_at': datetime.now().isoformat(),
            'format': export_format,
            **(metadata or {})
        }
        
        # Export based on format
        if export_format == 'pdf':
            return self.export_formats.export_to_pdf(report_content, export_metadata)
        elif export_format == 'docx':
            return self.export_formats.export_to_docx(report_content, export_metadata)
        elif export_format == 'html':
            return self.export_formats.export_to_html(report_content, export_metadata)
        elif export_format == 'json':
            return self.export_formats.export_to_json(report_data, export_metadata)
        elif export_format == 'csv':
            return self.export_formats.export_to_csv(sources, export_metadata)
        elif export_format == 'markdown':
            return self.export_formats.export_to_markdown(report_content, export_metadata)
        elif export_format == 'xml':
            return self.export_formats.export_to_xml(report_data, export_metadata)
        else:
            return {
                'error': f'Format {export_format} not implemented',
                'supported_formats': self.export_formats.get_supported_formats()
            }
    
    def export_multiple_formats(
        self,
        report_content: str,
        report_data: Dict,
        sources: List[Dict],
        formats: List[str],
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Export report in multiple formats.
        
        Args:
            report_content: Report content
            report_data: Full report data
            sources: List of sources
            formats: List of formats to export
            metadata: Optional metadata
            
        Returns:
            Dictionary with exports for each format
        """
        exports = {}
        
        for fmt in formats:
            try:
                export_result = self.export_report(
                    report_content=report_content,
                    report_data=report_data,
                    sources=sources,
                    export_format=fmt,
                    metadata=metadata
                )
                exports[fmt] = export_result
            except Exception as e:
                Actor.log.error(f"Failed to export to {fmt}: {e}")
                exports[fmt] = {'error': str(e)}
        
        return {
            'exports': exports,
            'formats': formats,
            'success_count': sum(1 for e in exports.values() if 'error' not in e),
            'total_count': len(formats)
        }
    
    def get_export_info(self, export_format: str) -> Dict:
        """
        Get information about an export format.
        
        Args:
            export_format: Format name
            
        Returns:
            Format information dictionary
        """
        format_info = {
            'pdf': {
                'name': 'PDF',
                'description': 'Portable Document Format - best for printing and sharing',
                'requires_library': 'reportlab or weasyprint',
                'supports_images': True,
                'supports_styling': True
            },
            'docx': {
                'name': 'DOCX',
                'description': 'Microsoft Word format - editable document',
                'requires_library': 'python-docx',
                'supports_images': True,
                'supports_styling': True
            },
            'html': {
                'name': 'HTML',
                'description': 'HyperText Markup Language - web-friendly format',
                'requires_library': None,
                'supports_images': True,
                'supports_styling': True
            },
            'json': {
                'name': 'JSON',
                'description': 'JavaScript Object Notation - structured data format',
                'requires_library': None,
                'supports_images': False,
                'supports_styling': False
            },
            'csv': {
                'name': 'CSV',
                'description': 'Comma-Separated Values - tabular data format',
                'requires_library': None,
                'supports_images': False,
                'supports_styling': False
            },
            'markdown': {
                'name': 'Markdown',
                'description': 'Markdown format - plain text with formatting',
                'requires_library': None,
                'supports_images': True,
                'supports_styling': False
            },
            'xml': {
                'name': 'XML',
                'description': 'eXtensible Markup Language - structured data format',
                'requires_library': None,
                'supports_images': False,
                'supports_styling': False
            }
        }
        
        return format_info.get(export_format.lower(), {
            'name': export_format,
            'description': 'Unknown format',
            'requires_library': None,
            'supports_images': False,
            'supports_styling': False
        })


def create_export_manager() -> ExportManager:
    """Create an export manager instance."""
    return ExportManager()

