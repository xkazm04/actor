"""
Knowledge Gap Detector - Identifies what aspects of research are well-covered
and what needs more investigation.
"""

from typing import List, Dict, Optional
from apify import Actor


class KnowledgeGapDetector:
    """
    Detects knowledge gaps in research by analyzing coverage of query aspects.
    """
    
    def __init__(self):
        """Initialize gap detector."""
        pass
    
    def detect_gaps(
        self,
        query: str,
        findings: Dict,
        sources_analyzed: int,
        query_aspects: Optional[List[str]] = None
    ) -> Dict:
        """
        Detect knowledge gaps in current research.
        
        Args:
            query: Original research query
            findings: Dictionary with key findings, themes, facts
            sources_analyzed: Number of sources analyzed
            query_aspects: List of aspects to check (if None, extracts from query)
            
        Returns:
            Dictionary with gap analysis
        """
        if query_aspects is None:
            query_aspects = self._extract_aspects(query)
        
        key_findings = findings.get('key_findings', [])
        themes = findings.get('main_themes', [])
        facts = findings.get('key_facts', [])
        
        # Analyze coverage for each aspect
        aspect_coverage = {}
        for aspect in query_aspects:
            coverage = self._assess_coverage(aspect, key_findings, themes, facts)
            aspect_coverage[aspect] = coverage
        
        # Identify gaps (low coverage aspects)
        gaps = []
        for aspect, coverage in aspect_coverage.items():
            if coverage['score'] < 0.5:  # Less than 50% coverage
                gaps.append({
                    'aspect': aspect,
                    'coverage_score': coverage['score'],
                    'evidence_count': coverage['evidence_count'],
                    'priority': 'high' if coverage['score'] < 0.3 else 'medium'
                })
        
        # Sort gaps by priority
        gaps.sort(key=lambda x: (x['priority'] == 'high', -x['coverage_score']))
        
        return {
            'query_aspects': query_aspects,
            'aspect_coverage': aspect_coverage,
            'gaps': gaps,
            'overall_coverage': self._calculate_overall_coverage(aspect_coverage),
            'sources_analyzed': sources_analyzed,
            'sufficient_coverage': len(gaps) == 0 or self._calculate_overall_coverage(aspect_coverage) > 0.7
        }
    
    def _extract_aspects(self, query: str) -> List[str]:
        """
        Extract key aspects from query.
        Simple keyword-based extraction.
        """
        # Common question words that indicate aspects
        question_words = ['what', 'why', 'how', 'when', 'where', 'who']
        
        aspects = []
        query_lower = query.lower()
        
        # Check for question patterns
        if 'what' in query_lower:
            aspects.append('definition_and_scope')
        if 'why' in query_lower or 'reason' in query_lower:
            aspects.append('causes_and_reasons')
        if 'how' in query_lower:
            aspects.append('methods_and_processes')
        if 'when' in query_lower or 'recent' in query_lower or 'latest' in query_lower:
            aspects.append('timeline_and_recency')
        if 'where' in query_lower:
            aspects.append('location_and_context')
        if 'who' in query_lower:
            aspects.append('stakeholders_and_actors')
        
        # If no specific aspects found, use general ones
        if not aspects:
            aspects = ['overview', 'current_state', 'key_findings']
        
        return aspects
    
    def _assess_coverage(
        self,
        aspect: str,
        findings: List[str],
        themes: List[str],
        facts: List[Dict]
    ) -> Dict:
        """
        Assess how well an aspect is covered.
        
        Returns:
            Dictionary with coverage score and evidence count
        """
        aspect_keywords = aspect.lower().replace('_', ' ')
        
        # Count evidence related to this aspect
        evidence_count = 0
        
        # Check findings
        for finding in findings:
            if any(keyword in finding.lower() for keyword in aspect_keywords.split()):
                evidence_count += 1
        
        # Check themes
        for theme in themes:
            if any(keyword in theme.lower() for keyword in aspect_keywords.split()):
                evidence_count += 1
        
        # Check facts
        for fact in facts:
            fact_text = str(fact.get('fact', '')).lower()
            if any(keyword in fact_text for keyword in aspect_keywords.split()):
                evidence_count += 1
        
        # Calculate coverage score (0-1)
        # More evidence = higher score, but cap at 1.0
        score = min(evidence_count / 5.0, 1.0) if evidence_count > 0 else 0.0
        
        return {
            'score': score,
            'evidence_count': evidence_count,
            'status': 'well_covered' if score > 0.7 else 'partially_covered' if score > 0.3 else 'under_covered'
        }
    
    def _calculate_overall_coverage(self, aspect_coverage: Dict) -> float:
        """Calculate overall coverage score."""
        if not aspect_coverage:
            return 0.0
        
        scores = [coverage['score'] for coverage in aspect_coverage.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    def should_continue_research(
        self,
        gap_analysis: Dict,
        completed_searches: int,
        max_searches: int,
        min_coverage_threshold: float = 0.7
    ) -> bool:
        """
        Determine if research should continue.
        
        Args:
            gap_analysis: Result from detect_gaps()
            completed_searches: Number of searches completed
            max_searches: Maximum allowed searches
            min_coverage_threshold: Minimum coverage to stop (0-1)
            
        Returns:
            True if research should continue, False otherwise
        """
        # Stop if max searches reached
        if completed_searches >= max_searches:
            return False
        
        # Stop if sufficient coverage achieved
        overall_coverage = gap_analysis.get('overall_coverage', 0.0)
        if overall_coverage >= min_coverage_threshold:
            return True  # Actually return False - we have enough
        
        # Continue if there are high-priority gaps
        gaps = gap_analysis.get('gaps', [])
        high_priority_gaps = [g for g in gaps if g.get('priority') == 'high']
        
        if high_priority_gaps:
            return True
        
        # Continue if coverage is low
        if overall_coverage < min_coverage_threshold:
            return True
        
        return False


def detect_knowledge_gaps(query: str, findings: Dict, sources_analyzed: int) -> Dict:
    """
    Convenience function to detect knowledge gaps.
    
    Args:
        query: Research query
        findings: Research findings dictionary
        sources_analyzed: Number of sources analyzed
        
    Returns:
        Gap analysis dictionary
    """
    detector = KnowledgeGapDetector()
    return detector.detect_gaps(query, findings, sources_analyzed)



