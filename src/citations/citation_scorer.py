"""
Citation Scorer - Scores citation quality and tracks citation coverage.
Identifies unsupported claims and calculates source diversity.
"""

from typing import Dict, List, Optional
from collections import Counter
from src.citations.source_verifier import SourceVerifier


class CitationScorer:
    """
    Scores citation quality and tracks citation coverage.
    Identifies unsupported claims and calculates source diversity.
    """
    
    def __init__(self, source_verifier: Optional[SourceVerifier] = None):
        """
        Initialize citation scorer.
        
        Args:
            source_verifier: Source verifier instance (optional)
        """
        self.source_verifier = source_verifier or SourceVerifier()
    
    def score_citation_quality(
        self,
        citation: Dict,
        source: Optional[Dict] = None
    ) -> Dict:
        """
        Score the quality of a citation.
        
        Args:
            citation: Citation dictionary
            source: Source dictionary (optional)
            
        Returns:
            Quality score dictionary
        """
        score = 0.5  # Base score
        factors = []
        
        # Check if source is verified
        if source:
            verification = self.source_verifier.verify_source(source)
            score = verification['quality_score']
            factors.append(f"Source quality: {verification['confidence']}")
        
        # Check citation completeness
        completeness_score = 0.0
        if citation.get('url'):
            completeness_score += 0.3
        if citation.get('title'):
            completeness_score += 0.3
        if citation.get('author'):
            completeness_score += 0.2
        if citation.get('publish_date'):
            completeness_score += 0.2
        
        factors.append(f"Citation completeness: {completeness_score:.2f}")
        
        # Combine scores
        final_score = (score * 0.7) + (completeness_score * 0.3)
        
        return {
            'citation_id': citation.get('id'),
            'quality_score': final_score,
            'source_quality': score,
            'completeness_score': completeness_score,
            'factors': factors,
            'is_primary_source': self._is_primary_source(citation, source),
            'is_secondary_source': self._is_secondary_source(citation, source)
        }
    
    def calculate_source_diversity(
        self,
        citations: List[Dict],
        sources: List[Dict]
    ) -> Dict:
        """
        Calculate source diversity score.
        
        Args:
            citations: List of citations
            sources: List of sources
            
        Returns:
            Diversity metrics
        """
        if not sources:
            return {
                'diversity_score': 0.0,
                'domain_count': 0,
                'unique_domains': [],
                'domain_distribution': {}
            }
        
        # Count domains
        domains = []
        for source in sources:
            domain = source.get('domain', '')
            if not domain:
                domain = self.source_verifier._extract_domain(source.get('url', ''))
            domains.append(domain)
        
        domain_counter = Counter(domains)
        unique_domains = list(domain_counter.keys())
        
        # Calculate diversity (Shannon diversity index)
        total = len(domains)
        if total == 0:
            diversity_score = 0.0
        else:
            diversity_score = 0.0
            for count in domain_counter.values():
                proportion = count / total
                if proportion > 0:
                    diversity_score -= proportion * (proportion.bit_length() - 1)  # Simplified
        
        # Normalize to 0-1 scale
        max_diversity = len(unique_domains) if len(unique_domains) > 1 else 1
        normalized_diversity = min(len(unique_domains) / max(10, total), 1.0)  # Cap at 10 domains
        
        return {
            'diversity_score': normalized_diversity,
            'domain_count': len(unique_domains),
            'total_sources': total,
            'unique_domains': unique_domains,
            'domain_distribution': dict(domain_counter),
            'is_diverse': normalized_diversity >= 0.5
        }
    
    def identify_unsupported_claims(
        self,
        claims: List[str],
        claim_citations: Dict[str, List[int]]
    ) -> List[Dict]:
        """
        Identify claims without citations.
        
        Args:
            claims: List of claim texts
            claim_citations: Mapping of claim -> citation IDs
            
        Returns:
            List of unsupported claims
        """
        unsupported = []
        
        for claim in claims:
            citation_ids = claim_citations.get(claim, [])
            if not citation_ids:
                unsupported.append({
                    'claim': claim,
                    'citation_count': 0,
                    'severity': 'high'
                })
            elif len(citation_ids) == 1:
                unsupported.append({
                    'claim': claim,
                    'citation_count': 1,
                    'severity': 'low',
                    'warning': 'Only one source supports this claim'
                })
        
        return unsupported
    
    def calculate_citation_coverage(
        self,
        claims: List[str],
        claim_citations: Dict[str, List[int]]
    ) -> Dict:
        """
        Calculate citation coverage metrics.
        
        Args:
            claims: List of claims
            claim_citations: Mapping of claim -> citation IDs
            
        Returns:
            Coverage metrics
        """
        total_claims = len(claims)
        if total_claims == 0:
            return {
                'coverage_percentage': 0.0,
                'total_claims': 0,
                'supported_claims': 0,
                'unsupported_claims': 0,
                'avg_citations_per_claim': 0.0
            }
        
        supported_claims = sum(1 for claim in claims if claim_citations.get(claim))
        unsupported_claims = total_claims - supported_claims
        
        total_citations = sum(len(ids) for ids in claim_citations.values())
        avg_citations = total_citations / total_claims if total_claims > 0 else 0.0
        
        coverage_percentage = (supported_claims / total_claims) * 100
        
        return {
            'coverage_percentage': coverage_percentage,
            'total_claims': total_claims,
            'supported_claims': supported_claims,
            'unsupported_claims': unsupported_claims,
            'avg_citations_per_claim': avg_citations,
            'is_fully_covered': coverage_percentage == 100.0
        }
    
    def _is_primary_source(self, citation: Dict, source: Optional[Dict]) -> bool:
        """Check if citation is a primary source."""
        if not source:
            return False
        
        verification = self.source_verifier.verify_source(source)
        return verification.get('is_academic', False) or verification.get('is_fact_check', False)
    
    def _is_secondary_source(self, citation: Dict, source: Optional[Dict]) -> bool:
        """Check if citation is a secondary source."""
        if not source:
            return True  # Default to secondary if unknown
        
        verification = self.source_verifier.verify_source(source)
        return not (verification.get('is_academic', False) or verification.get('is_fact_check', False))


def create_citation_scorer(source_verifier: Optional[SourceVerifier] = None) -> CitationScorer:
    """Create a citation scorer instance."""
    return CitationScorer(source_verifier)



