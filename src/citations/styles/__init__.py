"""
Citation Style Templates - Templates for different citation styles.
Supports APA, MLA, Chicago, and IEEE styles.
"""

from typing import Dict, Optional
from datetime import datetime


class CitationStyleFormatter:
    """Base class for citation style formatters."""
    
    def format_citation(self, citation: Dict) -> str:
        """Format a single citation."""
        raise NotImplementedError
    
    def format_bibliography_header(self) -> str:
        """Format bibliography header."""
        raise NotImplementedError


class APAStyleFormatter(CitationStyleFormatter):
    """APA citation style formatter."""
    
    def format_citation(self, citation: Dict) -> str:
        """Format citation in APA style."""
        parts = []
        
        if citation.get('author'):
            parts.append(citation['author'])
        
        if citation.get('publish_date'):
            year = citation['publish_date'][:4] if len(citation['publish_date']) >= 4 else ""
            if year:
                parts.append(f"({year})")
        
        if citation.get('title'):
            parts.append(f"{citation['title']}.")
        
        if citation.get('domain'):
            parts.append(citation['domain'])
        
        if citation.get('url'):
            parts.append(f"Retrieved from {citation['url']}")
        
        return ' '.join(parts)
    
    def format_bibliography_header(self) -> str:
        """Format bibliography header."""
        return "## References\n"


class MLAStyleFormatter(CitationStyleFormatter):
    """MLA citation style formatter."""
    
    def format_citation(self, citation: Dict) -> str:
        """Format citation in MLA style."""
        parts = []
        
        if citation.get('author'):
            parts.append(f"{citation['author']}.")
        
        if citation.get('title'):
            title = citation['title']
            parts.append(f'"{title}."')
        
        if citation.get('domain'):
            parts.append(citation['domain'] + ",")
        
        if citation.get('publish_date'):
            date_str = citation['publish_date'][:10] if len(citation['publish_date']) >= 10 else citation['publish_date']
            parts.append(date_str + ",")
        
        if citation.get('url'):
            parts.append(citation['url'] + ".")
        
        return ' '.join(parts)
    
    def format_bibliography_header(self) -> str:
        """Format bibliography header."""
        return "## Works Cited\n"


class ChicagoStyleFormatter(CitationStyleFormatter):
    """Chicago citation style formatter."""
    
    def format_citation(self, citation: Dict) -> str:
        """Format citation in Chicago style."""
        parts = []
        
        if citation.get('author'):
            parts.append(f"{citation['author']}.")
        
        if citation.get('title'):
            title = citation['title']
            parts.append(f'"{title}."')
        
        if citation.get('domain'):
            parts.append(citation['domain'] + ".")
        
        if citation.get('publish_date'):
            date_str = citation['publish_date'][:10] if len(citation['publish_date']) >= 10 else citation['publish_date']
            parts.append(date_str + ".")
        
        if citation.get('url'):
            parts.append(citation['url'])
        
        return ' '.join(parts)
    
    def format_bibliography_header(self) -> str:
        """Format bibliography header."""
        return "## Bibliography\n"


class IEEEStyleFormatter(CitationStyleFormatter):
    """IEEE citation style formatter."""
    
    def format_citation(self, citation: Dict) -> str:
        """Format citation in IEEE style."""
        parts = []
        
        if citation.get('author'):
            # IEEE uses "Author, Title, Publisher, Year"
            parts.append(citation['author'] + ",")
        
        if citation.get('title'):
            title = citation['title']
            parts.append(f'"{title},"')
        
        if citation.get('domain'):
            parts.append(citation['domain'] + ",")
        
        if citation.get('publish_date'):
            year = citation['publish_date'][:4] if len(citation['publish_date']) >= 4 else ""
            if year:
                parts.append(year + ".")
        
        if citation.get('url'):
            parts.append(f"[Online]. Available: {citation['url']}")
        
        return ' '.join(parts)
    
    def format_bibliography_header(self) -> str:
        """Format bibliography header."""
        return "## References\n"


def get_formatter(style: str) -> CitationStyleFormatter:
    """
    Get citation style formatter.
    
    Args:
        style: Citation style (apa, mla, chicago, ieee)
        
    Returns:
        Citation style formatter instance
    """
    style = style.lower()
    if style == "mla":
        return MLAStyleFormatter()
    elif style == "chicago":
        return ChicagoStyleFormatter()
    elif style == "ieee":
        return IEEEStyleFormatter()
    else:  # Default to APA
        return APAStyleFormatter()



