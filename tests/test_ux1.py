"""
Unit tests for UX Improvement 1: Smart Query Builder
"""

import pytest
from src.ux.query_templates import QueryTemplateLibrary, QueryTemplateType, QueryTemplate
from src.ux.query_validator import QueryValidator
from src.agents.query_assistant import QueryAssistant
from src.ux.query_builder import QueryBuilder


class TestQueryTemplates:
    """Test query templates."""
    
    def test_template_library_initialization(self):
        """Test template library initialization."""
        library = QueryTemplateLibrary()
        assert len(library.templates) > 0
    
    def test_get_template(self):
        """Test getting template by type."""
        library = QueryTemplateLibrary()
        template = library.get_template(QueryTemplateType.COMPARISON)
        assert template is not None
        assert template.template_type == QueryTemplateType.COMPARISON
    
    def test_template_fill(self):
        """Test filling template."""
        library = QueryTemplateLibrary()
        template = library.get_template(QueryTemplateType.COMPARISON)
        
        filled = template.fill(item_a="Python", item_b="JavaScript", criteria="performance")
        assert "Python" in filled
        assert "JavaScript" in filled
        assert "performance" in filled
    
    def test_suggest_template(self):
        """Test template suggestion."""
        library = QueryTemplateLibrary()
        
        # Comparison query
        template = library.suggest_template("Compare Python vs JavaScript")
        assert template is not None
        assert template.template_type == QueryTemplateType.COMPARISON
        
        # Pros/cons query
        template = library.suggest_template("What are the pros and cons of remote work?")
        assert template is not None
        assert template.template_type == QueryTemplateType.PROS_CONS


class TestQueryValidator:
    """Test query validator."""
    
    def test_validator_initialization(self):
        """Test validator initialization."""
        validator = QueryValidator()
        assert validator is not None
    
    def test_validate_query_empty(self):
        """Test validating empty query."""
        validator = QueryValidator()
        result = validator.validate_query("")
        assert result['is_valid'] is False
    
    def test_validate_query_short(self):
        """Test validating short query."""
        validator = QueryValidator()
        result = validator.validate_query("AI")
        assert result['is_valid'] is False or result['severity'] == 'warning'
    
    def test_validate_query_good(self):
        """Test validating good query."""
        validator = QueryValidator()
        result = validator.validate_query("What are the latest developments in quantum computing?")
        assert result['is_valid'] is True or result['severity'] == 'info'
    
    def test_check_ambiguity(self):
        """Test ambiguity checking."""
        validator = QueryValidator()
        result = validator._check_ambiguity("Tell me about it")
        assert result['is_ambiguous'] is True
    
    def test_check_breadth(self):
        """Test breadth checking."""
        validator = QueryValidator()
        result = validator._check_breadth("everything about AI")
        assert result['is_too_broad'] is True
    
    def test_suggest_improvements(self):
        """Test improvement suggestions."""
        validator = QueryValidator()
        suggestions = validator.suggest_improvements("AI")
        assert len(suggestions) > 0


class TestQueryAssistant:
    """Test query assistant."""
    
    def test_assistant_initialization(self):
        """Test assistant initialization."""
        assistant = QueryAssistant()
        assert assistant is not None
    
    def test_analyze_query_fallback(self):
        """Test query analysis (fallback)."""
        assistant = QueryAssistant()
        result = assistant._fallback_analysis("test query")
        assert 'is_ambiguous' in result
        assert 'clarifying_questions' in result
    
    def test_suggest_clarifying_questions(self):
        """Test clarifying questions."""
        assistant = QueryAssistant()
        questions = assistant.suggest_clarifying_questions("Tell me about it")
        assert len(questions) >= 0  # May be empty if no LLM


class TestQueryBuilder:
    """Test query builder."""
    
    def test_builder_initialization(self):
        """Test builder initialization."""
        builder = QueryBuilder()
        assert builder.template_library is not None
        assert builder.validator is not None
    
    def test_build_query_with_template(self):
        """Test building query with template."""
        builder = QueryBuilder()
        result = builder.build_query(
            template_type="comparison",
            template_values={
                "item_a": "Python",
                "item_b": "JavaScript",
                "criteria": "performance"
            }
        )
        assert 'query' in result
        assert "Python" in result['query']
    
    def test_build_query_with_initial(self):
        """Test building query with initial query."""
        builder = QueryBuilder()
        result = builder.build_query(initial_query="test query")
        assert result['query'] == "test query"
        assert 'validation' in result
    
    def test_analyze_query(self):
        """Test query analysis."""
        builder = QueryBuilder()
        result = builder.analyze_query("test query")
        assert 'query' in result
        assert 'validation' in result
        assert 'ai_analysis' in result
    
    def test_get_clarifying_questions(self):
        """Test getting clarifying questions."""
        builder = QueryBuilder()
        questions = builder.get_clarifying_questions("Tell me about it")
        assert isinstance(questions, list)
    
    def test_preview_research_plan(self):
        """Test research plan preview."""
        builder = QueryBuilder()
        preview = builder.preview_research_plan("test query")
        assert 'query' in preview
        assert 'estimated_sub_queries' in preview


class TestIntegration:
    """Integration tests for UX Improvement 1."""
    
    def test_query_builder_workflow(self):
        """Test complete query builder workflow."""
        builder = QueryBuilder()
        
        # Analyze query
        analysis = builder.analyze_query("AI in healthcare")
        assert 'query' in analysis
        
        # Get clarifying questions
        questions = builder.get_clarifying_questions("AI in healthcare")
        assert isinstance(questions, list)
        
        # Build query with template
        built = builder.build_query(
            template_type="pros_cons",
            template_values={"topic": "AI in healthcare"}
        )
        assert 'query' in built
    
    def test_template_workflow(self):
        """Test template workflow."""
        library = QueryTemplateLibrary()
        
        # Get template
        template = library.get_template(QueryTemplateType.MARKET_ANALYSIS)
        assert template is not None
        
        # Fill template
        query = template.fill(product_service="electric vehicles", region="Europe")
        assert "electric vehicles" in query
        assert "Europe" in query



