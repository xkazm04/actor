"""
Section Builder - Dynamically builds report sections based on configuration.
Generates sections only when enabled in configuration.
"""

from typing import Dict, List, Optional
from apify import Actor
from src.report.scope_configurator import OutputScopeConfig, ReportLength


class SectionBuilder:
    """
    Builds report sections dynamically based on configuration.
    Only generates sections that are enabled.
    """
    
    def __init__(self, scope_config):
        """
        Initialize section builder.
        
        Args:
            scope_config: OutputScopeConfig instance
        """
        self.scope_config = scope_config
    
    def build_section(
        self,
        section_name: str,
        content: Dict,
        findings: Dict
    ) -> Optional[str]:
        """
        Build a specific section.
        
        Args:
            section_name: Name of section to build
            content: Content data for section
            findings: Research findings
            
        Returns:
            Section markdown or None if disabled
        """
        if not self.scope_config.sections.get(section_name, False):
            return None
        
        builders = {
            "executive_summary": self._build_executive_summary,
            "key_findings": self._build_key_findings,
            "detailed_analysis": self._build_detailed_analysis,
            "methodology": self._build_methodology,
            "expert_opinions": self._build_expert_opinions,
            "statistics": self._build_statistics,
            "case_studies": self._build_case_studies,
            "future_trends": self._build_future_trends,
            "recommendations": self._build_recommendations,
            "bibliography": self._build_bibliography
        }
        
        builder = builders.get(section_name)
        if builder:
            return builder(content, findings)
        
        return None
    
    def build_all_sections(
        self,
        query: str,
        findings: Dict,
        sources: List[Dict],
        reasoning: Optional[Dict] = None
    ) -> Dict[str, str]:
        """
        Build all enabled sections.
        
        Args:
            query: Research query
            findings: Research findings
            sources: List of sources
            reasoning: Optional reasoning results
            
        Returns:
            Dictionary of section_name -> section_content
        """
        sections = {}
        
        # Prepare content dictionary
        content = {
            'query': query,
            'findings': findings,
            'sources': sources,
            'reasoning': reasoning
        }
        
        # Build each enabled section
        for section_name in self.scope_config.get_enabled_sections():
            section_content = self.build_section(section_name, content, findings)
            if section_content:
                sections[section_name] = section_content
        
        return sections
    
    def _build_executive_summary(self, content: Dict, findings: Dict) -> str:
        """Build executive summary section."""
        key_findings = findings.get('key_findings', [])[:3]  # Top 3 for brief
        if self.scope_config.report_length == ReportLength.BRIEF:
            # Bullet points format
            bullets = "\n".join([f"- {finding}" for finding in key_findings])
            return f"## Executive Summary\n\n{bullets}\n"
        else:
            # Paragraph format
            summary_text = " ".join(key_findings[:2])
            return f"## Executive Summary\n\n{summary_text}\n"
    
    def _build_key_findings(self, content: Dict, findings: Dict) -> str:
        """Build key findings section."""
        key_findings = findings.get('key_findings', [])
        main_themes = findings.get('main_themes', [])
        
        findings_text = "\n".join([f"- {finding}" for finding in key_findings])
        themes_text = "\n".join([f"- {theme}" for theme in main_themes])
        
        return f"## Key Findings\n\n### Main Themes\n{themes_text}\n\n### Key Points\n{findings_text}\n"
    
    def _build_detailed_analysis(self, content: Dict, findings: Dict) -> str:
        """Build detailed analysis section."""
        synthesis = findings.get('synthesis', {})
        analysis_text = synthesis.get('analysis', 'No detailed analysis available.')
        
        return f"## Detailed Analysis\n\n{analysis_text}\n"
    
    def _build_methodology(self, content: Dict, findings: Dict) -> str:
        """Build methodology section."""
        sources = content.get('sources', [])
        source_count = len(sources)
        
        return f"## Methodology\n\nThis research analyzed {source_count} sources using a comprehensive search and analysis approach.\n"
    
    def _build_expert_opinions(self, content: Dict, findings: Dict) -> str:
        """Build expert opinions section."""
        expert_opinions = findings.get('expert_opinions', [])
        if not expert_opinions:
            return "## Expert Opinions\n\nNo expert opinions identified in sources.\n"
        
        opinions_text = "\n".join([f"- {opinion}" for opinion in expert_opinions])
        return f"## Expert Opinions\n\n{opinions_text}\n"
    
    def _build_statistics(self, content: Dict, findings: Dict) -> str:
        """Build statistics section."""
        statistics = findings.get('statistics', [])
        if not statistics:
            return "## Statistics & Data\n\nNo statistics identified in sources.\n"
        
        stats_text = "\n".join([f"- {stat}" for stat in statistics])
        return f"## Statistics & Data\n\n{stats_text}\n"
    
    def _build_case_studies(self, content: Dict, findings: Dict) -> str:
        """Build case studies section."""
        case_studies = findings.get('case_studies', [])
        if not case_studies:
            return "## Case Studies\n\nNo case studies identified in sources.\n"
        
        cases_text = "\n\n".join([f"### {case.get('title', 'Case Study')}\n\n{case.get('description', '')}" for case in case_studies])
        return f"## Case Studies\n\n{cases_text}\n"
    
    def _build_future_trends(self, content: Dict, findings: Dict) -> str:
        """Build future trends section."""
        future_trends = findings.get('future_trends', [])
        if not future_trends:
            return "## Future Trends\n\nNo future trends identified in sources.\n"
        
        trends_text = "\n".join([f"- {trend}" for trend in future_trends])
        return f"## Future Trends\n\n{trends_text}\n"
    
    def _build_recommendations(self, content: Dict, findings: Dict) -> str:
        """Build recommendations section."""
        recommendations = findings.get('recommendations', [])
        if not recommendations:
            return "## Recommendations\n\nNo recommendations provided.\n"
        
        recs_text = "\n".join([f"- {rec}" for rec in recommendations])
        return f"## Recommendations\n\n{recs_text}\n"
    
    def _build_bibliography(self, content: Dict, findings: Dict) -> str:
        """Build bibliography section."""
        sources = content.get('sources', [])
        if not sources:
            return "## Bibliography\n\nNo sources available.\n"
        
        # Format sources
        sources_text = "\n".join([
            f"{i+1}. {source.get('title', 'Untitled')} - {source.get('url', 'No URL')}"
            for i, source in enumerate(sources[:20])  # Limit to top 20
        ])
        
        return f"## Bibliography\n\n{sources_text}\n"


def create_section_builder(scope_config) -> SectionBuilder:
    """Create a section builder instance."""
    return SectionBuilder(scope_config)

