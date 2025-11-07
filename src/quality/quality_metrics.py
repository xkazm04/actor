"""
Quality Metrics - Tracks and evaluates research quality.
Measures accuracy, completeness, coherence, and citation quality.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor


class QualityMetrics:
    """
    Tracks and evaluates research quality metrics.
    Measures accuracy, completeness, coherence, and citation quality.
    """
    
    def __init__(self):
        """Initialize quality metrics tracker."""
        self.metrics: Dict = {}
    
    def calculate_accuracy_score(
        self,
        claims: List[str],
        sources: List[Dict],
        fact_check_results: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Calculate accuracy score based on fact verification.
        
        Args:
            claims: List of factual claims
            sources: List of sources supporting claims
            fact_check_results: Optional fact-check results
            
        Returns:
            Accuracy metrics dictionary
        """
        if not claims:
            return {
                'score': 0.0,
                'total_claims': 0,
                'verified_claims': 0,
                'unverified_claims': 0
            }
        
        # Simple accuracy calculation based on source quality
        verified_count = 0
        for claim in claims:
            # Check if claim has high-quality sources
            claim_sources = [s for s in sources if claim.lower() in str(s.get('title', '')).lower() or claim.lower() in str(s.get('snippet', '')).lower()]
            if claim_sources:
                # Check source quality
                high_quality = any(
                    self._is_high_quality_source(s) for s in claim_sources
                )
                if high_quality:
                    verified_count += 1
        
        accuracy_score = verified_count / len(claims) if claims else 0.0
        
        return {
            'score': accuracy_score,
            'total_claims': len(claims),
            'verified_claims': verified_count,
            'unverified_claims': len(claims) - verified_count,
            'percentage': accuracy_score * 100
        }
    
    def calculate_completeness_score(
        self,
        query: str,
        findings: Dict,
        expected_aspects: Optional[List[str]] = None
    ) -> Dict:
        """
        Calculate completeness score based on query coverage.
        
        Args:
            query: Original research query
            findings: Research findings dictionary
            expected_aspects: Optional list of expected aspects to cover
            
        Returns:
            Completeness metrics dictionary
        """
        key_findings = findings.get('key_findings', [])
        main_themes = findings.get('main_themes', [])
        
        # Extract query keywords
        query_keywords = set(query.lower().split())
        
        # Check coverage of query keywords in findings
        findings_text = ' '.join(key_findings + main_themes).lower()
        covered_keywords = sum(1 for keyword in query_keywords if keyword in findings_text)
        
        completeness_score = covered_keywords / len(query_keywords) if query_keywords else 0.0
        
        return {
            'score': completeness_score,
            'query_keywords': len(query_keywords),
            'covered_keywords': covered_keywords,
            'key_findings_count': len(key_findings),
            'main_themes_count': len(main_themes),
            'percentage': completeness_score * 100
        }
    
    def calculate_coherence_score(
        self,
        report: str,
        sections: Dict
    ) -> Dict:
        """
        Calculate coherence score based on logical flow and readability.
        
        Args:
            report: Generated report text
            sections: Report sections dictionary
            
        Returns:
            Coherence metrics dictionary
        """
        # Simple coherence metrics
        word_count = len(report.split())
        sentence_count = report.count('.') + report.count('!') + report.count('?')
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Check for section transitions
        section_count = len(sections)
        
        # Simple coherence score (can be enhanced with NLP)
        coherence_score = 0.7  # Base score
        
        # Adjust based on structure
        if section_count >= 3:
            coherence_score += 0.1
        
        # Adjust based on sentence length (optimal: 15-20 words)
        if 15 <= avg_sentence_length <= 20:
            coherence_score += 0.1
        elif avg_sentence_length > 30:
            coherence_score -= 0.1
        
        coherence_score = max(0.0, min(1.0, coherence_score))
        
        return {
            'score': coherence_score,
            'word_count': word_count,
            'sentence_count': sentence_count,
            'avg_sentence_length': avg_sentence_length,
            'section_count': section_count,
            'percentage': coherence_score * 100
        }
    
    def calculate_citation_quality_score(
        self,
        citations: List[Dict],
        citation_stats: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate citation quality score.
        
        Args:
            citations: List of citations
            citation_stats: Optional citation statistics
            
        Returns:
            Citation quality metrics dictionary
        """
        if not citations:
            return {
                'score': 0.0,
                'total_citations': 0,
                'reliable_sources': 0,
                'academic_sources': 0
            }
        
        # Count reliable sources
        reliable_count = 0
        academic_count = 0
        
        for citation in citations:
            url = citation.get('url', '').lower()
            domain = citation.get('domain', '').lower()
            
            if self._is_high_quality_source(citation):
                reliable_count += 1
            
            if '.edu' in domain or 'arxiv' in url or 'pubmed' in url:
                academic_count += 1
        
        quality_score = reliable_count / len(citations) if citations else 0.0
        
        return {
            'score': quality_score,
            'total_citations': len(citations),
            'reliable_sources': reliable_count,
            'academic_sources': academic_count,
            'percentage': quality_score * 100
        }
    
    def calculate_overall_quality(
        self,
        accuracy: Dict,
        completeness: Dict,
        coherence: Dict,
        citation_quality: Dict,
        weights: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate overall quality score.
        
        Args:
            accuracy: Accuracy metrics
            completeness: Completeness metrics
            coherence: Coherence metrics
            citation_quality: Citation quality metrics
            weights: Optional weights for each metric
            
        Returns:
            Overall quality metrics dictionary
        """
        if weights is None:
            weights = {
                'accuracy': 0.3,
                'completeness': 0.25,
                'coherence': 0.2,
                'citation_quality': 0.25
            }
        
        overall_score = (
            accuracy.get('score', 0.0) * weights['accuracy'] +
            completeness.get('score', 0.0) * weights['completeness'] +
            coherence.get('score', 0.0) * weights['coherence'] +
            citation_quality.get('score', 0.0) * weights['citation_quality']
        )
        
        return {
            'overall_score': overall_score,
            'percentage': overall_score * 100,
            'accuracy': accuracy.get('score', 0.0),
            'completeness': completeness.get('score', 0.0),
            'coherence': coherence.get('score', 0.0),
            'citation_quality': citation_quality.get('score', 0.0),
            'weights': weights
        }
    
    def _is_high_quality_source(self, source: Dict) -> bool:
        """Check if source is high quality."""
        url = source.get('url', '').lower()
        domain = source.get('domain', '').lower()
        
        # Check for high-quality indicators
        high_quality_domains = [
            '.edu', '.gov', '.ac.uk', '.ac.jp',
            'arxiv.org', 'pubmed.ncbi.nlm.nih.gov',
            'reuters.com', 'ap.org', 'bbc.com',
            'nature.com', 'science.org'
        ]
        
        return any(domain_indicator in url or domain_indicator in domain for domain_indicator in high_quality_domains)
    
    def get_quality_report(
        self,
        query: str,
        findings: Dict,
        report: str,
        citations: List[Dict],
        citation_stats: Optional[Dict] = None
    ) -> Dict:
        """
        Generate comprehensive quality report.
        
        Args:
            query: Research query
            findings: Research findings
            report: Generated report
            citations: List of citations
            citation_stats: Optional citation statistics
            
        Returns:
            Comprehensive quality report
        """
        # Extract claims from findings
        claims = findings.get('key_findings', []) + findings.get('key_facts', [])
        sources = [c for c in citations if isinstance(c, dict)]
        
        # Calculate all metrics
        accuracy = self.calculate_accuracy_score(claims, sources)
        completeness = self.calculate_completeness_score(query, findings)
        coherence = self.calculate_coherence_score(report, findings)
        citation_quality = self.calculate_citation_quality_score(citations, citation_stats)
        
        # Calculate overall quality
        overall = self.calculate_overall_quality(
            accuracy,
            completeness,
            coherence,
            citation_quality
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'overall_quality': overall,
            'accuracy': accuracy,
            'completeness': completeness,
            'coherence': coherence,
            'citation_quality': citation_quality,
            'recommendations': self._generate_recommendations(overall, accuracy, completeness, coherence, citation_quality)
        }
    
    def _generate_recommendations(
        self,
        overall: Dict,
        accuracy: Dict,
        completeness: Dict,
        coherence: Dict,
        citation_quality: Dict
    ) -> List[str]:
        """Generate quality improvement recommendations."""
        recommendations = []
        
        if accuracy.get('score', 0.0) < 0.7:
            recommendations.append("Improve fact verification and source quality")
        
        if completeness.get('score', 0.0) < 0.7:
            recommendations.append("Expand coverage of query aspects")
        
        if coherence.get('score', 0.0) < 0.7:
            recommendations.append("Improve report structure and logical flow")
        
        if citation_quality.get('score', 0.0) < 0.7:
            recommendations.append("Use more reliable and academic sources")
        
        if overall.get('overall_score', 0.0) < 0.7:
            recommendations.append("Overall quality needs improvement across multiple dimensions")
        
        return recommendations if recommendations else ["Quality metrics are within acceptable range"]


def create_quality_metrics() -> QualityMetrics:
    """Create a quality metrics instance."""
    return QualityMetrics()



