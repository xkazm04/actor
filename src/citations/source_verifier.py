"""
Source Verifier - Verifies source quality and reliability.
Flags potentially unreliable sources and identifies contradictions.
"""

from typing import Dict, List, Optional, Tuple
from urllib.parse import urlparse
from datetime import datetime
from apify import Actor


class SourceVerifier:
    """
    Verifies source quality and reliability.
    Flags potentially unreliable sources and identifies contradictions.
    """
    
    # Known unreliable domains (can be expanded)
    UNRELIABLE_DOMAINS = {
        'example.com',  # Placeholder
        # Add more as needed
    }
    
    # Known fact-checking domains
    FACT_CHECK_DOMAINS = {
        'snopes.com',
        'factcheck.org',
        'politifact.com',
        'reuters.com',
        'ap.org',
        'bbc.com'
    }
    
    # Academic domains
    ACADEMIC_DOMAINS = {
        '.edu',
        '.ac.uk',
        '.ac.jp',
        'scholar.google.com',
        'arxiv.org',
        'pubmed.ncbi.nlm.nih.gov'
    }
    
    def __init__(self):
        """Initialize source verifier."""
        pass
    
    def verify_source(self, source: Dict) -> Dict:
        """
        Verify a source and return quality metrics.
        
        Args:
            source: Source dictionary with url, title, domain, etc.
            
        Returns:
            Verification result with quality score and flags
        """
        url = source.get('url', '')
        domain = source.get('domain', '')
        title = source.get('title', '')
        
        if not domain:
            domain = self._extract_domain(url)
        
        verification = {
            'url': url,
            'domain': domain,
            'quality_score': 0.5,  # Default neutral score
            'flags': [],
            'warnings': [],
            'is_reliable': True,
            'is_academic': False,
            'is_fact_check': False,
            'confidence': 'medium'
        }
        
        # Check domain reputation
        if domain in self.UNRELIABLE_DOMAINS:
            verification['is_reliable'] = False
            verification['quality_score'] = 0.1
            verification['flags'].append('unreliable_domain')
            verification['warnings'].append(f"Domain {domain} is flagged as potentially unreliable")
            verification['confidence'] = 'low'
        elif self._is_academic_domain(domain):
            verification['is_academic'] = True
            verification['quality_score'] = 0.9
            verification['flags'].append('academic_source')
            verification['confidence'] = 'high'
        elif self._is_fact_check_domain(domain):
            verification['is_fact_check'] = True
            verification['quality_score'] = 0.85
            verification['flags'].append('fact_check_source')
            verification['confidence'] = 'high'
        elif self._is_government_domain(domain):
            verification['quality_score'] = 0.8
            verification['flags'].append('government_source')
            verification['confidence'] = 'high'
        elif self._is_news_domain(domain):
            verification['quality_score'] = 0.7
            verification['flags'].append('news_source')
            verification['confidence'] = 'medium'
        else:
            verification['quality_score'] = 0.5
            verification['confidence'] = 'medium'
        
        # Check for missing metadata
        if not source.get('author'):
            verification['warnings'].append("Missing author information")
            verification['quality_score'] *= 0.9
        
        if not source.get('publish_date'):
            verification['warnings'].append("Missing publication date")
            verification['quality_score'] *= 0.9
        
        # Check URL structure
        if not url.startswith(('http://', 'https://')):
            verification['warnings'].append("Invalid URL format")
            verification['quality_score'] *= 0.8
        
        return verification
    
    def detect_contradictions(
        self,
        claims: List[str],
        claim_sources: Dict[str, List[Dict]]
    ) -> List[Dict]:
        """
        Detect contradictions between sources for the same claim.
        
        Args:
            claims: List of claim texts
            claim_sources: Mapping of claim -> list of sources
            
        Returns:
            List of detected contradictions
        """
        contradictions = []
        
        for claim in claims:
            sources = claim_sources.get(claim, [])
            if len(sources) < 2:
                continue
            
            # Compare source content/claims (simplified - would need actual content comparison)
            # For now, flag if sources have very different quality scores
            quality_scores = []
            for source in sources:
                verification = self.verify_source(source)
                quality_scores.append(verification['quality_score'])
            
            if len(set(quality_scores)) > 1:
                max_diff = max(quality_scores) - min(quality_scores)
                if max_diff > 0.4:  # Significant difference
                    contradictions.append({
                        'claim': claim,
                        'sources': sources,
                        'quality_difference': max_diff,
                        'severity': 'medium' if max_diff < 0.6 else 'high'
                    })
        
        return contradictions
    
    def calculate_claim_confidence(
        self,
        claim: str,
        sources: List[Dict]
    ) -> Dict:
        """
        Calculate confidence score for a claim based on sources.
        
        Args:
            claim: Claim text
            sources: List of sources supporting the claim
            
        Returns:
            Confidence metrics
        """
        if not sources:
            return {
                'claim': claim,
                'confidence': 'none',
                'score': 0.0,
                'source_count': 0,
                'warning': 'No sources found for this claim'
            }
        
        verifications = [self.verify_source(s) for s in sources]
        avg_quality = sum(v['quality_score'] for v in verifications) / len(verifications)
        
        # Higher confidence with more sources
        source_count_factor = min(len(sources) / 3.0, 1.0)  # Cap at 3 sources
        
        # Higher confidence with higher quality sources
        confidence_score = avg_quality * (0.5 + 0.5 * source_count_factor)
        
        # Determine confidence level
        if confidence_score >= 0.8:
            confidence_level = 'high'
        elif confidence_score >= 0.6:
            confidence_level = 'medium'
        elif confidence_score >= 0.4:
            confidence_level = 'low'
        else:
            confidence_level = 'very_low'
        
        return {
            'claim': claim,
            'confidence': confidence_level,
            'score': confidence_score,
            'source_count': len(sources),
            'avg_source_quality': avg_quality,
            'has_academic_sources': any(v['is_academic'] for v in verifications),
            'has_fact_check_sources': any(v['is_fact_check'] for v in verifications)
        }
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ""
    
    def _is_academic_domain(self, domain: str) -> bool:
        """Check if domain is academic."""
        domain_lower = domain.lower()
        return any(academic in domain_lower for academic in self.ACADEMIC_DOMAINS)
    
    def _is_fact_check_domain(self, domain: str) -> bool:
        """Check if domain is a fact-checking site."""
        return domain.lower() in self.FACT_CHECK_DOMAINS
    
    def _is_government_domain(self, domain: str) -> bool:
        """Check if domain is government."""
        return domain.lower().endswith('.gov') or domain.lower().endswith('.gov.uk')
    
    def _is_news_domain(self, domain: str) -> bool:
        """Check if domain is a news site."""
        news_indicators = ['news', 'times', 'post', 'tribune', 'herald', 'journal', 'gazette']
        domain_lower = domain.lower()
        return any(indicator in domain_lower for indicator in news_indicators)


def create_source_verifier() -> SourceVerifier:
    """Create a source verifier instance."""
    return SourceVerifier()



