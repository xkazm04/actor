"""
Export Formats - Handles multiple export formats for research reports.
Supports PDF, DOCX, HTML, JSON, CSV, and more.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor


class ExportFormats:
    """
    Handles multiple export formats for research reports.
    Supports various formats for different use cases.
    """
    
    def __init__(self):
        """Initialize export formats handler."""
        pass
    
    def export_to_pdf(self, report_content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to PDF format.
        
        Args:
            report_content: Report content (markdown or HTML)
            metadata: Optional metadata (title, author, etc.)
            
        Returns:
            Dictionary with PDF export information
        """
        # Note: Actual PDF generation would require libraries like reportlab or weasyprint
        # For now, return metadata about PDF export
        Actor.log.info("PDF export requested (requires PDF library)")
        
        return {
            'format': 'pdf',
            'content': report_content,
            'metadata': metadata or {},
            'note': 'PDF generation requires additional libraries (reportlab/weasyprint)',
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_docx(self, report_content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to DOCX format.
        
        Args:
            report_content: Report content (markdown or HTML)
            metadata: Optional metadata
            
        Returns:
            Dictionary with DOCX export information
        """
        # Note: Actual DOCX generation would require python-docx library
        Actor.log.info("DOCX export requested (requires docx library)")
        
        return {
            'format': 'docx',
            'content': report_content,
            'metadata': metadata or {},
            'note': 'DOCX generation requires python-docx library',
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_html(self, report_content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to HTML format.
        
        Args:
            report_content: Report content (markdown or HTML)
            metadata: Optional metadata
            
        Returns:
            Dictionary with HTML export
        """
        # HTML is already supported, just wrap it
        return {
            'format': 'html',
            'content': report_content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_json(self, report_data: Dict, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to JSON format.
        
        Args:
            report_data: Report data dictionary
            metadata: Optional metadata
            
        Returns:
            Dictionary with JSON export
        """
        import json
        
        export_data = {
            'report': report_data,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
        
        return {
            'format': 'json',
            'content': json.dumps(export_data, indent=2),
            'data': export_data,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_csv(self, sources: List[Dict], metadata: Optional[Dict] = None) -> Dict:
        """
        Export sources to CSV format.
        
        Args:
            sources: List of source dictionaries
            metadata: Optional metadata
            
        Returns:
            Dictionary with CSV export
        """
        import csv
        import io
        
        if not sources:
            return {
                'format': 'csv',
                'content': '',
                'note': 'No sources to export',
                'timestamp': datetime.now().isoformat()
            }
        
        # Create CSV content
        output = io.StringIO()
        fieldnames = ['title', 'url', 'domain', 'snippet', 'relevance_score']
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for source in sources:
            row = {
                'title': source.get('title', ''),
                'url': source.get('url', ''),
                'domain': source.get('domain', ''),
                'snippet': source.get('snippet', ''),
                'relevance_score': source.get('relevance_score', 0)
            }
            writer.writerow(row)
        
        csv_content = output.getvalue()
        output.close()
        
        return {
            'format': 'csv',
            'content': csv_content,
            'metadata': metadata or {},
            'row_count': len(sources),
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_markdown(self, report_content: str, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to Markdown format.
        
        Args:
            report_content: Report content (markdown)
            metadata: Optional metadata
            
        Returns:
            Dictionary with Markdown export
        """
        return {
            'format': 'markdown',
            'content': report_content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def export_to_xml(self, report_data: Dict, metadata: Optional[Dict] = None) -> Dict:
        """
        Export report to XML format.
        
        Args:
            report_data: Report data dictionary
            metadata: Optional metadata
            
        Returns:
            Dictionary with XML export
        """
        import xml.etree.ElementTree as ET
        
        root = ET.Element('research_report')
        
        # Add metadata
        meta_elem = ET.SubElement(root, 'metadata')
        for key, value in (metadata or {}).items():
            meta_elem.set(key, str(value))
        
        # Add report data
        report_elem = ET.SubElement(root, 'report')
        self._dict_to_xml(report_data, report_elem)
        
        # Convert to string
        xml_content = ET.tostring(root, encoding='unicode', method='xml')
        
        return {
            'format': 'xml',
            'content': xml_content,
            'metadata': metadata or {},
            'timestamp': datetime.now().isoformat()
        }
    
    def _dict_to_xml(self, data: Dict, parent):
        """Helper to convert dict to XML elements."""
        import xml.etree.ElementTree as ET
        
        for key, value in data.items():
            if isinstance(value, dict):
                elem = ET.SubElement(parent, key)
                self._dict_to_xml(value, elem)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        elem = ET.SubElement(parent, key)
                        self._dict_to_xml(item, elem)
                    else:
                        elem = ET.SubElement(parent, key)
                        elem.text = str(item)
            else:
                elem = ET.SubElement(parent, key)
                elem.text = str(value)
    
    def get_supported_formats(self) -> List[str]:
        """
        Get list of supported export formats.
        
        Returns:
            List of format names
        """
        return ['pdf', 'docx', 'html', 'json', 'csv', 'markdown', 'xml']


def create_export_formats() -> ExportFormats:
    """Create an export formats instance."""
    return ExportFormats()

