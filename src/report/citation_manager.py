"""
Citation Manager - Tracks citations and formats them in multiple styles.
Manages inline citations and bibliography generation.
"""

from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse


class Citation:
    """Model for a citation."""
    
    def __init__(
        self,
        id: int,
        url: str,
        title: str,
        author: Optional[str] = None,
        publish_date: Optional[str] = None,
        domain: Optional[str] = None,
        access_date: Optional[str] = None
    ):
        self.id = id
        self.url = url
        self.title = title
        self.author = author
        self.publish_date = publish_date
        self.domain = domain or self._extract_domain(url)
        self.access_date = access_date or datetime.now().isoformat()
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'author': self.author,
            'publish_date': self.publish_date,
            'domain': self.domain,
            'access_date': self.access_date
        }


class CitationManager:
    """
    Manages citations throughout the report generation process.
    Tracks which sources support which claims.
    """
    
    def __init__(self):
        """Initialize citation manager."""
        self.citations: List[Citation] = []
        self.citation_map: Dict[str, int] = {}  # URL -> citation ID
        self.claim_citations: Dict[str, List[int]] = {}  # claim -> citation IDs
    
    def add_citation(
        self,
        url: str,
        title: str,
        author: Optional[str] = None,
        publish_date: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> int:
        """
        Add a citation and return its ID.
        
        Args:
            url: Source URL
            title: Source title
            author: Author name (optional)
            publish_date: Publish date (optional)
            metadata: Additional metadata (optional)
            
        Returns:
            Citation ID
        """
        # Check if citation already exists
        if url in self.citation_map:
            return self.citation_map[url]
        
        # Extract metadata if provided
        if metadata:
            author = author or metadata.get('author')
            publish_date = publish_date or metadata.get('publish_date')
        
        # Create new citation
        citation_id = len(self.citations) + 1
        citation = Citation(
            id=citation_id,
            url=url,
            title=title,
            author=author,
            publish_date=publish_date
        )
        
        self.citations.append(citation)
        self.citation_map[url] = citation_id
        
        return citation_id
    
    def add_citation_from_source(self, source: Dict) -> int:
        """
        Add citation from a source dictionary.
        
        Args:
            source: Source dictionary with url, title, etc.
            
        Returns:
            Citation ID
        """
        return self.add_citation(
            url=source.get('url', ''),
            title=source.get('title', 'Unknown'),
            author=source.get('author'),
            publish_date=source.get('publish_date'),
            metadata=source.get('metadata', {})
        )
    
    def link_claim_to_citation(self, claim: str, citation_id: int):
        """
        Link a claim to a citation.
        
        Args:
            claim: The claim text
            citation_id: Citation ID
        """
        if claim not in self.claim_citations:
            self.claim_citations[claim] = []
        
        if citation_id not in self.claim_citations[claim]:
            self.claim_citations[claim].append(citation_id)
    
    def get_citation_ids_for_claim(self, claim: str) -> List[int]:
        """Get citation IDs for a claim."""
        return self.claim_citations.get(claim, [])
    
    def format_inline_citation(self, citation_ids: List[int]) -> str:
        """
        Format inline citation (e.g., [1][2]).
        
        Args:
            citation_ids: List of citation IDs
            
        Returns:
            Formatted citation string
        """
        if not citation_ids:
            return ""
        
        formatted = ''.join(f'[{cid}]' for cid in citation_ids)
        return formatted
    
    def format_bibliography_apa(self) -> str:
        """Format bibliography in APA style."""
        lines = []
        lines.append("## References\n")
        
        for citation in self.citations:
            # APA format: Author (Year). Title. Domain. URL
            parts = []
            
            if citation.author:
                parts.append(citation.author)
            
            if citation.publish_date:
                year = citation.publish_date[:4] if len(citation.publish_date) >= 4 else ""
                if year:
                    parts.append(f"({year})")
            
            parts.append(f"{citation.title}.")
            
            if citation.domain:
                parts.append(citation.domain)
            
            parts.append(f"Retrieved from {citation.url}")
            
            lines.append(f"[{citation.id}] {' '.join(parts)}\n")
        
        return '\n'.join(lines)
    
    def format_bibliography_mla(self) -> str:
        """Format bibliography in MLA style."""
        lines = []
        lines.append("## Works Cited\n")
        
        for citation in self.citations:
            # MLA format: Author. "Title." Domain, Date, URL.
            parts = []
            
            if citation.author:
                parts.append(f"{citation.author}.")
            
            parts.append(f'"{citation.title}."')
            
            if citation.domain:
                parts.append(citation.domain + ",")
            
            if citation.publish_date:
                date_str = citation.publish_date[:10] if len(citation.publish_date) >= 10 else citation.publish_date
                parts.append(date_str + ",")
            
            parts.append(citation.url + ".")
            
            lines.append(f"[{citation.id}] {' '.join(parts)}\n")
        
        return '\n'.join(lines)
    
    def format_bibliography_chicago(self) -> str:
        """Format bibliography in Chicago style."""
        lines = []
        lines.append("## Bibliography\n")
        
        for citation in self.citations:
            # Chicago format: Author. "Title." Domain. Date. URL.
            parts = []
            
            if citation.author:
                parts.append(f"{citation.author}.")
            
            parts.append(f'"{citation.title}."')
            
            if citation.domain:
                parts.append(citation.domain + ".")
            
            if citation.publish_date:
                date_str = citation.publish_date[:10] if len(citation.publish_date) >= 10 else citation.publish_date
                parts.append(date_str + ".")
            
            parts.append(citation.url)
            
            lines.append(f"[{citation.id}] {' '.join(parts)}\n")
        
        return '\n'.join(lines)
    
    def format_bibliography(self, style: str = "apa") -> str:
        """
        Format bibliography in specified style.
        
        Args:
            style: Citation style (apa, mla, chicago)
            
        Returns:
            Formatted bibliography
        """
        style = style.lower()
        if style == "mla":
            return self.format_bibliography_mla()
        elif style == "chicago":
            return self.format_bibliography_chicago()
        else:  # Default to APA
            return self.format_bibliography_apa()
    
    def get_all_citations(self) -> List[Dict]:
        """Get all citations as dictionaries."""
        return [c.to_dict() for c in self.citations]



