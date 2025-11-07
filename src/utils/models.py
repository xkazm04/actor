"""
Input validation models using Pydantic.
Defines the structure and validation rules for Actor inputs.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal, Dict, List


class QueryInput(BaseModel):
    """Validated query input model."""
    
    query: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="The research query to investigate"
    )
    
    max_searches: Optional[int] = Field(
        default=20,
        ge=5,
        le=100,
        description="Maximum number of sub-queries to execute"
    )
    
    research_depth: Literal["quick", "standard", "deep"] = Field(
        default="standard",
        description="Research depth mode"
    )
    
    output_format: Literal["markdown", "html", "json"] = Field(
        default="markdown",
        description="Output format for the final report"
    )
    
    budget_limit: Optional[float] = Field(
        default=None,
        ge=0.01,
        le=100.0,
        description="Maximum budget in USD (optional)"
    )
    
    webhook_url: Optional[str] = Field(
        default=None,
        description="Optional webhook URL for progress updates"
    )
    
    use_query_builder: Optional[bool] = Field(
        default=False,
        description="Enable interactive query builder"
    )
    
    query_template: Optional[str] = Field(
        default="custom",
        description="Query template type"
    )
    
    output_scope: Optional[Dict] = Field(
        default=None,
        description="Output scope configuration"
    )
    
    format_options: Optional[Dict] = Field(
        default=None,
        description="Format-specific options"
    )
    
    research_theme: Optional[str] = Field(
        default="auto_detect",
        description="Research theme (auto_detect, academic, news, business, technical, general)"
    )
    
    theme_options: Optional[Dict] = Field(
        default=None,
        description="Theme-specific options"
    )
    
    interactive_mode: Optional[bool] = Field(
        default=False,
        description="Enable interactive mode (preview, pause, refinement)"
    )
    
    preview_only: Optional[bool] = Field(
        default=False,
        description="Generate preview only without executing research"
    )
    
    refinement_request: Optional[str] = Field(
        default=None,
        description="Refinement instructions for existing report"
    )
    
    previous_run_id: Optional[str] = Field(
        default=None,
        description="Previous run ID for refinement or resume"
    )
    
    enable_diversity_analysis: Optional[bool] = Field(
        default=True,
        description="Enable diversity analysis and bias detection"
    )
    
    enable_perspective_balancing: Optional[bool] = Field(
        default=False,
        description="Enable automatic perspective balancing"
    )
    
    target_perspective_distribution: Optional[Dict] = Field(
        default=None,
        description="Target perspective distribution for balancing"
    )
    
    diversity_threshold: Optional[float] = Field(
        default=70.0,
        description="Minimum diversity score threshold (0-100)"
    )
    
    export_formats: Optional[List[str]] = Field(
        default=None,
        description="Additional export formats (pdf, docx, html, json, csv, markdown, xml)"
    )
    
    enable_sharing: Optional[bool] = Field(
        default=False,
        description="Enable sharing functionality"
    )
    
    sharing_options: Optional[Dict] = Field(
        default=None,
        description="Sharing options configuration"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v: str) -> str:
        """Sanitize and validate query input."""
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Basic sanitization
        if not v.strip():
            raise ValueError("Query cannot be empty or whitespace only")
        
        return v.strip()
    
    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "query": "What are the latest developments in quantum computing?",
                "max_searches": 20,
                "research_depth": "standard",
                "output_format": "markdown"
            }
        }


class SearchResult(BaseModel):
    """Model for individual search results."""
    
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Page title")
    snippet: str = Field(default="", description="Content snippet")
    source_api: str = Field(..., description="Which search API provided this result")
    relevance_score: Optional[float] = Field(default=None, ge=0, le=100, description="Relevance score")


class SubQuery(BaseModel):
    """Model for decomposed sub-queries."""
    
    query: str = Field(..., description="The sub-query text")
    priority: int = Field(default=1, ge=1, le=10, description="Priority level (1=highest)")
    category: Optional[str] = Field(default=None, description="Query category/theme")
    reasoning: Optional[str] = Field(default=None, description="Reasoning for this sub-query")


class ResearchState(BaseModel):
    """State model for resumable research execution."""
    
    main_query: str
    sub_queries: list[SubQuery] = Field(default_factory=list)
    completed_searches: int = Field(default=0)
    total_searches: int = Field(default=0)
    sources_collected: list[SearchResult] = Field(default_factory=list)
    progress_percentage: float = Field(default=0.0, ge=0, le=100)
    current_operation: Optional[str] = Field(default=None, description="Current operation being performed")
    processed_contents: dict = Field(default_factory=dict, description="Processed content by URL")
    analyzed_contents: list = Field(default_factory=list, description="Analyzed content results")

