"""
Query Validator - Validates queries and provides suggestions.
Detects overly broad/narrow queries and suggests improvements.
"""

from typing import Dict, List, Optional, Tuple
from apify import Actor


class QueryValidator:
    """
    Validates queries and provides improvement suggestions.
    Detects issues and suggests fixes.
    """
    
    def __init__(self):
        """Initialize query validator."""
        pass
    
    def validate_query(self, query: str) -> Dict:
        """
        Validate query and return analysis.
        
        Args:
            query: Query to validate
            
        Returns:
            Validation result dictionary
        """
        if not query or not query.strip():
            return {
                'is_valid': False,
                'issues': ['Query is empty'],
                'suggestions': ['Please provide a research query'],
                'severity': 'error'
            }
        
        query = query.strip()
        issues = []
        suggestions = []
        severity = 'info'
        
        # Check query length
        if len(query) < 10:
            issues.append('Query is too short')
            suggestions.append('Provide more context or details in your query')
            severity = 'warning'
        elif len(query) > 2000:
            issues.append('Query is too long')
            suggestions.append('Consider breaking into multiple focused queries')
            severity = 'warning'
        
        # Check for ambiguity
        ambiguity_result = self._check_ambiguity(query)
        if ambiguity_result['is_ambiguous']:
            issues.append('Query may be ambiguous')
            suggestions.extend(ambiguity_result['clarifying_questions'])
            severity = 'warning'
        
        # Check for breadth
        breadth_result = self._check_breadth(query)
        if breadth_result['is_too_broad']:
            issues.append('Query may be too broad')
            suggestions.extend(breadth_result['narrowing_suggestions'])
            severity = 'warning'
        elif breadth_result['is_too_narrow']:
            issues.append('Query may be too narrow')
            suggestions.extend(breadth_result['broadening_suggestions'])
            severity = 'info'
        
        # Check for missing context
        context_result = self._check_context(query)
        if context_result['missing_context']:
            issues.append('Query may be missing context')
            suggestions.extend(context_result['context_suggestions'])
            severity = 'info'
        
        return {
            'is_valid': len(issues) == 0 or severity == 'info',
            'issues': issues,
            'suggestions': suggestions,
            'severity': severity,
            'query_length': len(query),
            'word_count': len(query.split())
        }
    
    def _check_ambiguity(self, query: str) -> Dict:
        """
        Check if query is ambiguous.
        
        Args:
            query: Query to check
            
        Returns:
            Ambiguity analysis
        """
        ambiguous_keywords = [
            'it', 'this', 'that', 'they', 'them', 'these', 'those',
            'thing', 'stuff', 'something', 'anything'
        ]
        
        query_lower = query.lower()
        ambiguous_words = [word for word in ambiguous_keywords if word in query_lower]
        
        # Check for vague terms
        vague_terms = ['good', 'bad', 'better', 'best', 'nice', 'interesting']
        vague_found = [term for term in vague_terms if term in query_lower]
        
        clarifying_questions = []
        
        if ambiguous_words:
            clarifying_questions.append("Please specify what you're referring to")
        
        if vague_found:
            clarifying_questions.append("Be more specific about what you want to know")
        
        # Check for common ambiguous patterns
        if 'how' in query_lower and len(query.split()) < 5:
            clarifying_questions.append("Specify what aspect of 'how' you're interested in")
        
        return {
            'is_ambiguous': len(ambiguous_words) > 0 or len(vague_found) > 0 or len(clarifying_questions) > 0,
            'ambiguous_words': ambiguous_words,
            'vague_terms': vague_found,
            'clarifying_questions': clarifying_questions
        }
    
    def _check_breadth(self, query: str) -> Dict:
        """
        Check if query is too broad or too narrow.
        
        Args:
            query: Query to check
            
        Returns:
            Breadth analysis
        """
        word_count = len(query.split())
        query_lower = query.lower()
        
        # Too broad indicators
        too_broad_keywords = ['everything', 'all', 'complete', 'comprehensive', 'full']
        too_broad = any(keyword in query_lower for keyword in too_broad_keywords)
        
        # Too narrow indicators (very specific, single aspect)
        too_narrow = word_count < 5 and not any(keyword in query_lower for keyword in ['what', 'how', 'why', 'when', 'where'])
        
        narrowing_suggestions = []
        broadening_suggestions = []
        
        if too_broad:
            narrowing_suggestions.append("Focus on specific aspects or timeframes")
            narrowing_suggestions.append("Break into multiple focused queries")
        
        if too_narrow:
            broadening_suggestions.append("Consider adding context or related aspects")
            broadening_suggestions.append("Specify what you want to learn about the topic")
        
        # Check for single-word queries (likely too broad)
        if word_count == 1:
            narrowing_suggestions.append("Add more context: what specifically about this topic?")
        
        return {
            'is_too_broad': too_broad or word_count == 1,
            'is_too_narrow': too_narrow,
            'word_count': word_count,
            'narrowing_suggestions': narrowing_suggestions,
            'broadening_suggestions': broadening_suggestions
        }
    
    def _check_context(self, query: str) -> Dict:
        """
        Check if query is missing context.
        
        Args:
            query: Query to check
            
        Returns:
            Context analysis
        """
        query_lower = query.lower()
        missing_context = []
        context_suggestions = []
        
        # Check for time context
        time_keywords = ['recent', 'latest', 'current', 'now', 'today', 'recently']
        has_time_context = any(keyword in query_lower for keyword in time_keywords)
        
        if not has_time_context and any(keyword in query_lower for keyword in ['what', 'how', 'why']):
            missing_context.append('timeframe')
            context_suggestions.append("Consider specifying timeframe: recent, historical, or all-time")
        
        # Check for perspective context
        perspective_keywords = ['technical', 'business', 'academic', 'practical', 'theoretical']
        has_perspective = any(keyword in query_lower for keyword in perspective_keywords)
        
        if not has_perspective:
            context_suggestions.append("Consider specifying perspective: technical, business, academic, or general")
        
        # Check for scope context
        scope_keywords = ['global', 'local', 'national', 'international', 'region']
        has_scope = any(keyword in query_lower for keyword in scope_keywords)
        
        return {
            'missing_context': missing_context,
            'has_time_context': has_time_context,
            'has_perspective': has_perspective,
            'has_scope': has_scope,
            'context_suggestions': context_suggestions
        }
    
    def suggest_improvements(self, query: str) -> List[str]:
        """
        Suggest query improvements.
        
        Args:
            query: Query to improve
            
        Returns:
            List of improvement suggestions
        """
        validation = self.validate_query(query)
        suggestions = validation.get('suggestions', [])
        
        # Add general suggestions
        word_count = len(query.split())
        if word_count < 8:
            suggestions.append("Add more specific details to your query")
        
        if word_count > 50:
            suggestions.append("Consider breaking into multiple focused queries")
        
        return suggestions
    
    def suggest_related_subtopics(self, query: str) -> List[str]:
        """
        Suggest related subtopics to explore.
        
        Args:
            query: Original query
            
        Returns:
            List of related subtopic suggestions
        """
        query_lower = query.lower()
        subtopics = []
        
        # Generic subtopic suggestions based on common patterns
        if 'how' in query_lower:
            subtopics.append(f"Best practices for {query}")
            subtopics.append(f"Common challenges with {query}")
        
        if 'what' in query_lower:
            subtopics.append(f"History of {query}")
            subtopics.append(f"Future trends in {query}")
        
        if 'why' in query_lower:
            subtopics.append(f"Alternatives to {query}")
            subtopics.append(f"Impact of {query}")
        
        # Add domain-specific suggestions
        if any(keyword in query_lower for keyword in ['technology', 'software', 'system']):
            subtopics.append("Implementation considerations")
            subtopics.append("Performance and scalability")
        
        if any(keyword in query_lower for keyword in ['business', 'market', 'company']):
            subtopics.append("Market size and growth")
            subtopics.append("Competitive landscape")
        
        return subtopics[:5]  # Limit to top 5


def create_query_validator() -> QueryValidator:
    """Create a query validator instance."""
    return QueryValidator()



