"""
Query Templates - Pre-built query templates for common research types.
Provides structured templates to help users formulate effective queries.
"""

from typing import Dict, List, Optional
from enum import Enum


class QueryTemplateType(Enum):
    """Query template types."""
    CUSTOM = "custom"
    COMPARISON = "comparison"
    PROS_CONS = "pros_cons"
    MARKET_ANALYSIS = "market_analysis"
    EVOLUTION = "evolution"
    EXPERT_OPINIONS = "expert_opinions"


class QueryTemplate:
    """Represents a query template."""
    
    def __init__(
        self,
        template_type: QueryTemplateType,
        name: str,
        description: str,
        template: str,
        placeholders: List[str],
        example: Optional[str] = None
    ):
        """
        Initialize query template.
        
        Args:
            template_type: Template type enum
            name: Template name
            description: Template description
            template: Template string with placeholders
            placeholders: List of placeholder names
            example: Example filled template
        """
        self.template_type = template_type
        self.name = name
        self.description = description
        self.template = template
        self.placeholders = placeholders
        self.example = example
    
    def fill(self, **kwargs) -> str:
        """
        Fill template with provided values.
        
        Args:
            **kwargs: Values for placeholders
            
        Returns:
            Filled query string
        """
        filled = self.template
        for placeholder in self.placeholders:
            value = kwargs.get(placeholder, f"[{placeholder}]")
            filled = filled.replace(f"{{{placeholder}}}", value)
        return filled
    
    def to_dict(self) -> Dict:
        """Convert template to dictionary."""
        return {
            'type': self.template_type.value,
            'name': self.name,
            'description': self.description,
            'template': self.template,
            'placeholders': self.placeholders,
            'example': self.example
        }


class QueryTemplateLibrary:
    """Library of query templates."""
    
    def __init__(self):
        """Initialize template library."""
        self.templates: Dict[QueryTemplateType, QueryTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default templates."""
        # Comparison template
        self.templates[QueryTemplateType.COMPARISON] = QueryTemplate(
            template_type=QueryTemplateType.COMPARISON,
            name="Comparison",
            description="Compare two or more items on specific criteria",
            template="Compare {item_a} vs {item_b} in terms of {criteria}",
            placeholders=["item_a", "item_b", "criteria"],
            example="Compare Python vs JavaScript in terms of performance, ease of use, and ecosystem"
        )
        
        # Pros and Cons template
        self.templates[QueryTemplateType.PROS_CONS] = QueryTemplate(
            template_type=QueryTemplateType.PROS_CONS,
            name="Pros & Cons",
            description="Analyze advantages and disadvantages of a topic",
            template="What are the pros and cons of {topic}?",
            placeholders=["topic"],
            example="What are the pros and cons of remote work?"
        )
        
        # Market Analysis template
        self.templates[QueryTemplateType.MARKET_ANALYSIS] = QueryTemplate(
            template_type=QueryTemplateType.MARKET_ANALYSIS,
            name="Market Analysis",
            description="Analyze market for a product or service in a region",
            template="Analyze the market for {product_service} in {region}",
            placeholders=["product_service", "region"],
            example="Analyze the market for electric vehicles in Europe"
        )
        
        # Evolution template
        self.templates[QueryTemplateType.EVOLUTION] = QueryTemplate(
            template_type=QueryTemplateType.EVOLUTION,
            name="Evolution Over Time",
            description="Track how a topic has changed over time",
            template="How has {topic} evolved from {start_year} to {end_year}?",
            placeholders=["topic", "start_year", "end_year"],
            example="How has artificial intelligence evolved from 2010 to 2025?"
        )
        
        # Expert Opinions template
        self.templates[QueryTemplateType.EXPERT_OPINIONS] = QueryTemplate(
            template_type=QueryTemplateType.EXPERT_OPINIONS,
            name="Expert Opinions",
            description="Gather expert opinions on a topic",
            template="What are expert opinions on {topic}?",
            placeholders=["topic"],
            example="What are expert opinions on climate change mitigation strategies?"
        )
    
    def get_template(self, template_type: QueryTemplateType) -> Optional[QueryTemplate]:
        """
        Get template by type.
        
        Args:
            template_type: Template type
            
        Returns:
            Template instance or None
        """
        return self.templates.get(template_type)
    
    def get_all_templates(self) -> List[QueryTemplate]:
        """Get all templates."""
        return list(self.templates.values())
    
    def suggest_template(self, query: str) -> Optional[QueryTemplate]:
        """
        Suggest template based on query.
        
        Args:
            query: User query
            
        Returns:
            Suggested template or None
        """
        query_lower = query.lower()
        
        # Check for comparison keywords
        if any(keyword in query_lower for keyword in ['compare', 'vs', 'versus', 'difference between']):
            return self.templates.get(QueryTemplateType.COMPARISON)
        
        # Check for pros/cons keywords
        if any(keyword in query_lower for keyword in ['pros', 'cons', 'advantages', 'disadvantages', 'benefits', 'drawbacks']):
            return self.templates.get(QueryTemplateType.PROS_CONS)
        
        # Check for market analysis keywords
        if any(keyword in query_lower for keyword in ['market', 'industry', 'sector', 'market size']):
            return self.templates.get(QueryTemplateType.MARKET_ANALYSIS)
        
        # Check for evolution keywords
        if any(keyword in query_lower for keyword in ['evolved', 'changed', 'development', 'history', 'timeline']):
            return self.templates.get(QueryTemplateType.EVOLUTION)
        
        # Check for expert opinions keywords
        if any(keyword in query_lower for keyword in ['expert', 'opinion', 'view', 'perspective', 'think']):
            return self.templates.get(QueryTemplateType.EXPERT_OPINIONS)
        
        return None


# Global template library instance
_template_library: Optional[QueryTemplateLibrary] = None


def get_template_library() -> QueryTemplateLibrary:
    """Get global template library instance."""
    global _template_library
    if _template_library is None:
        _template_library = QueryTemplateLibrary()
    return _template_library



