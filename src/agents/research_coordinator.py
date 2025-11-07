"""
Research Coordinator Agent - Coordinates plan refinement and adaptive research.
Uses reasoning to adjust research strategy dynamically.
"""

import os
from typing import Dict, List, Optional
from apify import Actor

from src.planning.research_planner import ResearchPlanner, ResearchPlan
from src.planning.gap_detector import KnowledgeGapDetector
from src.reasoning.reasoning_engine import ReasoningEngine


class ResearchCoordinator:
    """
    Coordinates research planning, gap detection, and plan refinement.
    Acts as the adaptive intelligence layer for the research process.
    """
    
    def __init__(self):
        """Initialize research coordinator."""
        try:
            self.planner = ResearchPlanner()
        except Exception as e:
            Actor.log.warning(f"Research planner initialization failed: {e}")
            self.planner = None
        
        self.gap_detector = KnowledgeGapDetector()
        
        try:
            self.reasoning_engine = ReasoningEngine()
        except Exception as e:
            Actor.log.warning(f"Reasoning engine initialization failed: {e}")
            self.reasoning_engine = None
    
    def create_initial_plan(self, query: str, max_searches: int = 20) -> Optional[ResearchPlan]:
        """
        Create initial research plan.
        
        Args:
            query: Research query
            max_searches: Maximum searches
            
        Returns:
            ResearchPlan object or None if planner unavailable
        """
        if not self.planner:
            return None
        
        try:
            return self.planner.create_initial_plan(query, max_searches)
        except Exception as e:
            Actor.log.error(f"Failed to create initial plan: {e}")
            return None
    
    def assess_progress(
        self,
        query: str,
        findings: Dict,
        sources_analyzed: int,
        completed_searches: int,
        max_searches: int
    ) -> Dict:
        """
        Assess research progress and identify next steps.
        
        Args:
            query: Research query
            findings: Current findings dictionary
            sources_analyzed: Number of sources analyzed
            completed_searches: Searches completed
            max_searches: Maximum searches allowed
            
        Returns:
            Assessment dictionary with gaps and recommendations
        """
        # Detect knowledge gaps
        gap_analysis = self.gap_detector.detect_gaps(
            query,
            findings,
            sources_analyzed
        )
        
        # Determine if research should continue
        should_continue = self.gap_detector.should_continue_research(
            gap_analysis,
            completed_searches,
            max_searches
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            gap_analysis,
            findings,
            completed_searches,
            max_searches
        )
        
        return {
            'gap_analysis': gap_analysis,
            'should_continue': should_continue,
            'recommendations': recommendations,
            'progress_summary': {
                'completed_searches': completed_searches,
                'max_searches': max_searches,
                'overall_coverage': gap_analysis.get('overall_coverage', 0.0),
                'gaps_remaining': len(gap_analysis.get('gaps', []))
            }
        }
    
    def refine_plan(
        self,
        current_plan: Optional[ResearchPlan],
        findings: Dict,
        completed_searches: int
    ) -> Optional[ResearchPlan]:
        """
        Refine research plan based on findings.
        
        Args:
            current_plan: Current research plan
            findings: Current findings
            completed_searches: Searches completed
            
        Returns:
            Refined plan or None
        """
        if not self.planner or not current_plan:
            return current_plan
        
        try:
            return self.planner.refine_plan(current_plan, findings, completed_searches)
        except Exception as e:
            Actor.log.warning(f"Plan refinement failed: {e}")
            return current_plan
    
    def perform_reasoning(self, query: str, findings: Dict) -> Optional[Dict]:
        """
        Perform reasoning about findings.
        
        Args:
            query: Research query
            findings: Research findings
            
        Returns:
            Reasoning result or None
        """
        if not self.reasoning_engine:
            return None
        
        try:
            return self.reasoning_engine.reason_about_findings(query, findings)
        except Exception as e:
            Actor.log.warning(f"Reasoning failed: {e}")
            return None
    
    def _generate_recommendations(
        self,
        gap_analysis: Dict,
        findings: Dict,
        completed_searches: int,
        max_searches: int
    ) -> List[str]:
        """Generate recommendations for next steps."""
        recommendations = []
        
        gaps = gap_analysis.get('gaps', [])
        overall_coverage = gap_analysis.get('overall_coverage', 0.0)
        
        if not gaps:
            recommendations.append("Research coverage is sufficient. Consider finalizing report.")
        else:
            high_priority_gaps = [g for g in gaps if g.get('priority') == 'high']
            if high_priority_gaps:
                recommendations.append(f"Focus on {len(high_priority_gaps)} high-priority knowledge gaps.")
            
            if overall_coverage < 0.5:
                recommendations.append("Coverage is low. Consider expanding search scope.")
        
        remaining_searches = max_searches - completed_searches
        if remaining_searches < 5:
            recommendations.append(f"Only {remaining_searches} searches remaining. Prioritize critical gaps.")
        
        return recommendations



