"""
Citation Manager - Tracks citations and formats them in multiple styles.
Manages inline citations and bibliography generation.
Phase 8: Enhanced with source verification and quality scoring.
"""

from typing import List, Dict, Optional
from datetime import datetime
from urllib.parse import urlparse

from src.citations.source_verifier import SourceVerifier
from src.citations.citation_scorer import CitationScorer


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
        
        # Phase 8: Initialize verification and scoring
        self.source_verifier = SourceVerifier()
        self.citation_scorer = CitationScorer(self.source_verifier)
        self.sources: Dict[int, Dict] = {}  # citation_id -> source dict
    
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
        
        # Phase 8: Store source for verification
        if metadata:
            self.sources[citation_id] = {
                'url': url,
                'title': title,
                'author': author,
                'publish_date': publish_date,
                **metadata
            }
        
        return citation_id
    
    def add_citation_from_source(self, source: Dict) -> int:
        """
        Add citation from a source dictionary.
        
        Args:
            source: Source dictionary with url, title, etc.
            
        Returns:
            Citation ID
        """
        citation_id = self.add_citation(
            url=source.get('url', ''),
            title=source.get('title', 'Unknown'),
            author=source.get('author'),
            publish_date=source.get('publish_date'),
            metadata=source.get('metadata', {})
        )
        
        # Phase 8: Store source for verification
        self.sources[citation_id] = source
        
        return citation_id
    
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
            style: Citation style (apa, mla, chicago, ieee)
            
        Returns:
            Formatted bibliography
        """
        formatter = get_formatter(style)
        lines = [formatter.format_bibliography_header()]
        
        for citation in self.citations:
            formatted = formatter.format_citation(citation.to_dict())
            lines.append(f"[{citation.id}] {formatted}\n")
        
        return '\n'.join(lines)
    
    def get_all_citations(self) -> List[Dict]:
        """Get all citations as dictionaries."""
        return [c.to_dict() for c in self.citations]
    
    # Phase 8: Enhanced methods
    
    def verify_all_sources(self) -> Dict:
        """
        Verify all sources and return verification results.
        
        Returns:
            Verification summary
        """
        verifications = []
        for citation_id, source in self.sources.items():
            verification = self.source_verifier.verify_source(source)
            verification['citation_id'] = citation_id
            verifications.append(verification)
        
        return {
            'total_sources': len(verifications),
            'reliable_sources': sum(1 for v in verifications if v['is_reliable']),
            'academic_sources': sum(1 for v in verifications if v['is_academic']),
            'fact_check_sources': sum(1 for v in verifications if v['is_fact_check']),
            'avg_quality_score': sum(v['quality_score'] for v in verifications) / len(verifications) if verifications else 0.0,
            'verifications': verifications
        }
    
    def score_citation_quality(self, citation_id: int) -> Dict:
        """
        Score the quality of a specific citation.
        
        Args:
            citation_id: Citation ID
            
        Returns:
            Quality score dictionary
        """
        citation = next((c for c in self.citations if c.id == citation_id), None)
        if not citation:
            return {'error': 'Citation not found'}
        
        source = self.sources.get(citation_id)
        return self.citation_scorer.score_citation_quality(citation.to_dict(), source)
    
    def calculate_source_diversity(self) -> Dict:
        """
        Calculate source diversity metrics.
        
        Returns:
            Diversity metrics
        """
        sources_list = list(self.sources.values())
        return self.citation_scorer.calculate_source_diversity(
            [c.to_dict() for c in self.citations],
            sources_list
        )
    
    def identify_unsupported_claims(self, claims: List[str]) -> List[Dict]:
        """
        Identify claims without citations.
        
        Args:
            claims: List of claim texts
            
        Returns:
            List of unsupported claims
        """
        return self.citation_scorer.identify_unsupported_claims(claims, self.claim_citations)
    
    def calculate_citation_coverage(self, claims: List[str]) -> Dict:
        """
        Calculate citation coverage metrics.
        
        Args:
            claims: List of claims
            
        Returns:
            Coverage metrics
        """
        return self.citation_scorer.calculate_citation_coverage(claims, self.claim_citations)
    
    def detect_contradictions(self, claims: List[str]) -> List[Dict]:
        """
        Detect contradictions between sources.
        
        Args:
            claims: List of claim texts
            
        Returns:
            List of detected contradictions
        """
        claim_sources = {}
        for claim in claims:
            citation_ids = self.claim_citations.get(claim, [])
            sources = [self.sources.get(cid, {}) for cid in citation_ids if cid in self.sources]
            claim_sources[claim] = sources
        
        return self.source_verifier.detect_contradictions(claims, claim_sources)
    
    def calculate_claim_confidence(self, claim: str) -> Dict:
        """
        Calculate confidence score for a claim.
        
        Args:
            claim: Claim text
            
        Returns:
            Confidence metrics
        """
        citation_ids = self.claim_citations.get(claim, [])
        sources = [self.sources.get(cid, {}) for cid in citation_ids if cid in self.sources]
        return self.source_verifier.calculate_claim_confidence(claim, sources)
    
    def get_citation_statistics(self, claims: List[str]) -> Dict:
        """
        Get comprehensive citation statistics.
        
        Args:
            claims: List of claims
            
        Returns:
            Statistics dictionary
        """
        verification_summary = self.verify_all_sources()
        coverage = self.calculate_citation_coverage(claims)
        diversity = self.calculate_source_diversity()
        unsupported = self.identify_unsupported_claims(claims)
        contradictions = self.detect_contradictions(claims)
        
        return {
            'total_citations': len(self.citations),
            'total_claims': len(claims),
            'verification': verification_summary,
            'coverage': coverage,
            'diversity': diversity,
            'unsupported_claims': unsupported,
            'contradictions': contradictions,
            'citation_quality': {
                'avg_score': verification_summary.get('avg_quality_score', 0.0),
                'reliable_percentage': (verification_summary.get('reliable_sources', 0) / 
                                      max(verification_summary.get('total_sources', 1), 1)) * 100
            }
        }

