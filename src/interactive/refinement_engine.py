"""
Refinement Engine - Handles report refinement based on user feedback.
Allows iterative improvement of reports.
"""

from typing import Dict, List, Optional
from apify import Actor

from src.report.report_generator import ReportGenerator


class RefinementEngine:
    """
    Handles report refinement based on user feedback.
    Allows iterative improvement of reports.
    """
    
    def __init__(self):
        """Initialize refinement engine."""
        self.report_generator = ReportGenerator()
    
    async def refine_report(
        self,
        original_report: Dict,
        refinement_request: str,
        query: str,
        findings: Dict,
        ranked_sources: List[Dict],
        reasoning: Optional[Dict] = None
    ) -> Dict:
        """
        Refine report based on user feedback.
        
        Args:
            original_report: Original report dictionary
            refinement_request: User's refinement request
            query: Research query
            findings: Research findings
            ranked_sources: Ranked sources
            reasoning: Reasoning results (optional)
            
        Returns:
            Refined report dictionary
        """
        Actor.log.info(f"Refining report based on: {refinement_request}")
        
        # Parse refinement request
        refinement_instructions = self._parse_refinement_request(refinement_request)
        
        # Generate refined report
        refined_report = await self._apply_refinements(
            original_report=original_report,
            refinement_instructions=refinement_instructions,
            query=query,
            findings=findings,
            ranked_sources=ranked_sources,
            reasoning=reasoning
        )
        
        return {
            'original_report': original_report,
            'refined_report': refined_report,
            'refinement_instructions': refinement_instructions,
            'changes_made': self._identify_changes(original_report, refined_report)
        }
    
    def _parse_refinement_request(self, request: str) -> Dict:
        """
        Parse refinement request into structured instructions.
        
        Args:
            request: User's refinement request text
            
        Returns:
            Structured refinement instructions
        """
        request_lower = request.lower()
        instructions = {
            'add_more_about': [],
            'remove_sections': [],
            'expand_sections': [],
            'add_perspectives': [],
            'add_recent_sources': False,
            'change_tone': None,
            'change_length': None
        }
        
        # Detect "add more about X"
        if 'add more' in request_lower or 'expand' in request_lower:
            # Extract topics (simplified)
            if 'about' in request_lower:
                parts = request_lower.split('about')
                if len(parts) > 1:
                    topics = parts[1].split('and')
                    instructions['add_more_about'] = [t.strip() for t in topics]
        
        # Detect "remove X section"
        if 'remove' in request_lower or 'delete' in request_lower:
            # Extract section names (simplified)
            if 'section' in request_lower:
                instructions['remove_sections'] = ['section']  # Simplified
        
        # Detect "too long" or "too short"
        if 'too long' in request_lower:
            instructions['change_length'] = 'shorter'
        elif 'too short' in request_lower or 'more detail' in request_lower:
            instructions['change_length'] = 'longer'
        
        # Detect "add Y perspective"
        if 'perspective' in request_lower:
            instructions['add_perspectives'] = ['additional']  # Simplified
        
        # Detect "more recent sources"
        if 'recent' in request_lower or 'latest' in request_lower:
            instructions['add_recent_sources'] = True
        
        return instructions
    
    async def _apply_refinements(
        self,
        original_report: Dict,
        refinement_instructions: Dict,
        query: str,
        findings: Dict,
        ranked_sources: List[Dict],
        reasoning: Optional[Dict]
    ) -> Dict:
        """
        Apply refinement instructions to report.
        
        Args:
            original_report: Original report
            refinement_instructions: Structured refinement instructions
            query: Research query
            findings: Research findings
            ranked_sources: Ranked sources
            reasoning: Reasoning results
            
        Returns:
            Refined report dictionary
        """
        # For now, regenerate report with refinement context
        # In production, would use LLM to apply specific refinements
        
        # Add refinement context to findings
        refined_findings = findings.copy()
        if refinement_instructions.get('add_more_about'):
            refined_findings['refinement_focus'] = refinement_instructions['add_more_about']
        
        # Regenerate report
        refined_report = self.report_generator.generate_report(
            query=query,
            findings=refined_findings,
            ranked_sources=ranked_sources,
            reasoning=reasoning,
            output_format=original_report.get('format', 'markdown')
        )
        
        return refined_report
    
    def _identify_changes(self, original: Dict, refined: Dict) -> List[str]:
        """
        Identify changes between original and refined report.
        
        Args:
            original: Original report
            refined: Refined report
            
        Returns:
            List of changes made
        """
        changes = []
        
        original_word_count = original.get('word_count', 0)
        refined_word_count = refined.get('word_count', 0)
        
        if refined_word_count > original_word_count:
            changes.append(f"Increased word count from {original_word_count} to {refined_word_count}")
        elif refined_word_count < original_word_count:
            changes.append(f"Decreased word count from {original_word_count} to {refined_word_count}")
        
        original_sections = original.get('sections', {})
        refined_sections = refined.get('sections', {})
        
        if len(refined_sections) > len(original_sections):
            changes.append(f"Added {len(refined_sections) - len(original_sections)} new sections")
        
        return changes if changes else ["Report refined based on feedback"]


def create_refinement_engine() -> RefinementEngine:
    """Create a refinement engine instance."""
    return RefinementEngine()



