"""
Output Scope Configurator - Configures report length, sections, and structure.
Manages report scope based on user preferences.
"""

from typing import Dict, List, Optional, Literal
from enum import Enum


class ReportLength(Enum):
    """Report length presets."""
    BRIEF = "brief"  # 200-500 words
    STANDARD = "standard"  # 1000-2000 words
    COMPREHENSIVE = "comprehensive"  # 3000-5000 words
    DEEP_DIVE = "deep_dive"  # 5000-10000+ words


class WritingTone(Enum):
    """Writing tone options."""
    ACADEMIC = "academic"
    PROFESSIONAL = "professional"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"


class ReadingLevel(Enum):
    """Reading level options."""
    EXPERT = "expert"
    INTERMEDIATE = "intermediate"
    GENERAL = "general"


class Perspective(Enum):
    """Perspective options."""
    OBJECTIVE = "objective"
    CRITICAL = "critical"
    OPTIMISTIC = "optimistic"


class OutputScopeConfig:
    """Configuration for output scope."""
    
    def __init__(
        self,
        report_length: str = "standard",
        sections: Optional[Dict[str, bool]] = None,
        writing_style: Optional[Dict[str, str]] = None
    ):
        """
        Initialize output scope configuration.
        
        Args:
            report_length: Report length preset
            sections: Section inclusion flags
            writing_style: Writing style configuration
        """
        self.report_length = ReportLength(report_length) if isinstance(report_length, str) else report_length
        
        # Default sections
        default_sections = {
            "executive_summary": True,
            "key_findings": True,
            "detailed_analysis": True,
            "methodology": False,
            "expert_opinions": True,
            "statistics": True,
            "case_studies": False,
            "future_trends": True,
            "recommendations": False,
            "bibliography": True
        }
        self.sections = {**default_sections, **(sections or {})}
        
        # Default writing style
        default_style = {
            "tone": "professional",
            "reading_level": "intermediate",
            "perspective": "objective"
        }
        self.writing_style = {**default_style, **(writing_style or {})}
    
    def get_word_range(self) -> tuple:
        """
        Get word count range for report length.
        
        Returns:
            Tuple of (min_words, max_words)
        """
        ranges = {
            ReportLength.BRIEF: (200, 500),
            ReportLength.STANDARD: (1000, 2000),
            ReportLength.COMPREHENSIVE: (3000, 5000),
            ReportLength.DEEP_DIVE: (5000, 10000)
        }
        return ranges.get(self.report_length, (1000, 2000))
    
    def get_source_count_range(self) -> tuple:
        """
        Get source count range for report length.
        
        Returns:
            Tuple of (min_sources, max_sources)
        """
        ranges = {
            ReportLength.BRIEF: (3, 5),
            ReportLength.STANDARD: (10, 20),
            ReportLength.COMPREHENSIVE: (30, 50),
            ReportLength.DEEP_DIVE: (50, 100)
        }
        return ranges.get(self.report_length, (10, 20))
    
    def get_enabled_sections(self) -> List[str]:
        """
        Get list of enabled sections.
        
        Returns:
            List of enabled section names
        """
        return [section for section, enabled in self.sections.items() if enabled]
    
    def to_dict(self) -> Dict:
        """Convert configuration to dictionary."""
        return {
            'report_length': self.report_length.value if isinstance(self.report_length, ReportLength) else self.report_length,
            'sections': self.sections,
            'writing_style': self.writing_style,
            'word_range': self.get_word_range(),
            'source_count_range': self.get_source_count_range(),
            'enabled_sections': self.get_enabled_sections()
        }


class ScopeConfigurator:
    """Configures output scope based on user preferences."""
    
    def __init__(self):
        """Initialize scope configurator."""
        pass
    
    def create_config(
        self,
        report_length: str = "standard",
        sections: Optional[Dict[str, bool]] = None,
        writing_style: Optional[Dict[str, str]] = None
    ) -> OutputScopeConfig:
        """
        Create output scope configuration.
        
        Args:
            report_length: Report length preset
            sections: Section inclusion flags
            writing_style: Writing style configuration
            
        Returns:
            Output scope configuration
        """
        return OutputScopeConfig(
            report_length=report_length,
            sections=sections,
            writing_style=writing_style
        )
    
    def get_length_description(self, report_length: str) -> Dict:
        """
        Get description for report length preset.
        
        Args:
            report_length: Report length preset
            
        Returns:
            Description dictionary
        """
        descriptions = {
            "brief": {
                "name": "Executive Brief",
                "word_range": "200-500 words",
                "source_count": "Top 3 sources",
                "use_case": "Quick overview, decision-makers",
                "format": "Bullet points"
            },
            "standard": {
                "name": "Standard Report",
                "word_range": "1000-2000 words",
                "source_count": "10-20 sources",
                "use_case": "General research, presentations",
                "format": "Mixed format (paragraphs + bullets)"
            },
            "comprehensive": {
                "name": "Comprehensive Analysis",
                "word_range": "3000-5000 words",
                "source_count": "30-50 sources",
                "use_case": "Academic papers, strategic planning",
                "format": "Detailed paragraphs"
            },
            "deep_dive": {
                "name": "Deep Dive",
                "word_range": "5000-10000+ words",
                "source_count": "50-100+ sources",
                "use_case": "Thesis research, market reports",
                "format": "Multiple sections and subsections"
            }
        }
        return descriptions.get(report_length, descriptions["standard"])


def create_scope_configurator() -> ScopeConfigurator:
    """Create a scope configurator instance."""
    return ScopeConfigurator()



