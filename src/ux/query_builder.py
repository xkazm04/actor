"""
Query Builder - Interactive query builder with AI-assisted refinement.
Provides guided query creation, templates, and validation.
"""

from typing import Dict, List, Optional
from apify import Actor

from src.ux.query_templates import QueryTemplateLibrary, QueryTemplateType, get_template_library
from src.ux.query_validator import QueryValidator, create_query_validator
from src.agents.query_assistant import QueryAssistant, create_query_assistant


class QueryBuilder:
    """
    Interactive query builder with AI-assisted refinement.
    Provides templates, validation, and guided query creation.
    """
    
    def __init__(self):
        """Initialize query builder."""
        self.template_library = get_template_library()
        self.validator = create_query_validator()
        self.assistant = create_query_assistant()
    
    def build_query(
        self,
        initial_query: Optional[str] = None,
        template_type: Optional[str] = None,
        template_values: Optional[Dict] = None,
        use_ai_refinement: bool = True
    ) -> Dict:
        """
        Build query using templates or AI assistance.
        
        Args:
            initial_query: Initial query text (optional)
            template_type: Template type to use (optional)
            template_values: Values for template placeholders (optional)
            use_ai_refinement: Whether to use AI for refinement
            
        Returns:
            Built query dictionary
        """
        result = {
            'query': '',
            'template_used': None,
            'validation': {},
            'suggestions': [],
            'refined_query': None
        }
        
        # Use template if specified
        if template_type and template_type != 'custom':
            try:
                template_enum = QueryTemplateType(template_type)
                template = self.template_library.get_template(template_enum)
                
                if template:
                    if template_values:
                        query = template.fill(**template_values)
                    else:
                        query = template.template  # Return template with placeholders
                    
                    result['query'] = query
                    result['template_used'] = template.to_dict()
            except ValueError:
                Actor.log.warning(f"Unknown template type: {template_type}")
        
        # Use initial query if provided
        if initial_query:
            result['query'] = initial_query
        
        if not result['query']:
            return {
                **result,
                'error': 'No query provided'
            }
        
        # Validate query
        validation = self.validator.validate_query(result['query'])
        result['validation'] = validation
        
        # Get suggestions
        suggestions = self.validator.suggest_improvements(result['query'])
        result['suggestions'] = suggestions
        
        # AI refinement if enabled and query has issues
        if use_ai_refinement and (validation.get('issues') or validation.get('severity') == 'warning'):
            refinement = self.assistant.refine_query(result['query'])
            result['refined_query'] = refinement.get('refined_query')
            result['refinement_improvements'] = refinement.get('improvements', [])
        
        return result
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query and provide comprehensive feedback.
        
        Args:
            query: Query to analyze
            
        Returns:
            Analysis dictionary
        """
        # Validation
        validation = self.validator.validate_query(query)
        
        # AI analysis
        ai_analysis = self.assistant.analyze_query(query)
        
        # Template suggestion
        suggested_template = self.template_library.suggest_template(query)
        
        # Related subtopics
        related_subtopics = self.validator.suggest_related_subtopics(query)
        
        return {
            'query': query,
            'validation': validation,
            'ai_analysis': ai_analysis,
            'suggested_template': suggested_template.to_dict() if suggested_template else None,
            'related_subtopics': related_subtopics,
            'query_variations': self.assistant.generate_query_variations(query, count=3)
        }
    
    def get_clarifying_questions(self, query: str) -> List[str]:
        """
        Get clarifying questions for ambiguous queries.
        
        Args:
            query: Query to analyze
            
        Returns:
            List of clarifying questions
        """
        # Get questions from validator
        validation = self.validator.validate_query(query)
        questions = validation.get('suggestions', [])
        
        # Get questions from AI assistant
        ai_questions = self.assistant.suggest_clarifying_questions(query)
        
        # Combine and deduplicate
        all_questions = list(set(questions + ai_questions))
        
        return all_questions[:5]  # Limit to top 5
    
    def guided_refinement(
        self,
        query: str,
        answers: Optional[Dict] = None
    ) -> Dict:
        """
        Guided query refinement using multi-step wizard.
        
        Args:
            query: Initial query
            answers: Answers to clarifying questions
            
        Returns:
            Refined query dictionary
        """
        # Step 1: Analyze initial query
        analysis = self.analyze_query(query)
        
        # Step 2: Get clarifying questions
        questions = self.get_clarifying_questions(query)
        
        # Step 3: If answers provided, refine query
        if answers:
            # Use answers to refine query
            context = {
                'user_answers': answers,
                'original_query': query
            }
            refinement = self.assistant.refine_query(query, context)
            
            return {
                'original_query': query,
                'refined_query': refinement.get('refined_query', query),
                'improvements': refinement.get('improvements', []),
                'questions_answered': answers
            }
        else:
            # Return questions for user to answer
            return {
                'original_query': query,
                'clarifying_questions': questions,
                'next_step': 'answer_questions'
            }
    
    def preview_research_plan(self, query: str) -> Dict:
        """
        Generate preview of research plan before execution.
        
        Args:
            query: Research query
            
        Returns:
            Research plan preview
        """
        analysis = self.analyze_query(query)
        
        # Estimate sub-queries (simplified)
        word_count = len(query.split())
        estimated_sub_queries = max(5, min(20, word_count * 2))
        
        # Get query variations for sub-queries
        variations = self.assistant.generate_query_variations(query, count=min(5, estimated_sub_queries))
        
        return {
            'query': query,
            'estimated_sub_queries': estimated_sub_queries,
            'sample_sub_queries': variations,
            'suggested_template': analysis.get('suggested_template'),
            'validation_issues': analysis.get('validation', {}).get('issues', []),
            'recommendations': analysis.get('validation', {}).get('suggestions', [])
        }


def create_query_builder() -> QueryBuilder:
    """Create a query builder instance."""
    return QueryBuilder()



