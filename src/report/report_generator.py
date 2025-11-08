"""
Report Generator - Generates comprehensive research reports using Claude Sonnet.
Creates well-structured reports with citations and multiple output formats.
"""

import os
import json
from typing import Dict, List, Optional
from datetime import datetime
from anthropic import Anthropic
from apify import Actor

from src.citations.citation_manager import CitationManager
from src.report.scope_configurator import ScopeConfigurator, OutputScopeConfig, create_scope_configurator
from src.report.section_builder import SectionBuilder, create_section_builder
from src.report.style_adapter import StyleAdapter


class ReportGenerator:
    """
    Generates comprehensive research reports from findings.
    Uses Claude Sonnet for high-quality synthesis.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize report generator.
        
        Args:
            api_key: Anthropic API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
        self.citation_manager = CitationManager()
        self.plugin_config: Optional[Dict] = None  # Phase 9: Plugin configuration
    
    def generate_report(
        self,
        query: str,
        findings: Optional[Dict],
        ranked_sources: List[Dict],
        reasoning: Optional[Dict] = None,
        research_plan: Optional[Dict] = None,
        output_format: str = "markdown",
        plugin_config: Optional[Dict] = None,  # Phase 9: Plugin configuration
        output_scope: Optional[Dict] = None,  # UX Improvement 2: Output scope
        format_options: Optional[Dict] = None,  # UX Improvement 2: Format options
        theme_config: Optional[Dict] = None  # UX Improvement 3: Theme configuration
    ) -> Dict:
        """
        Generate comprehensive research report.
        
        Args:
            query: Original research query
            findings: Research findings dictionary
            ranked_sources: Ranked sources list
            reasoning: Reasoning results (optional)
            research_plan: Research plan (optional)
            output_format: Output format (markdown, html, json)
            plugin_config: Plugin configuration (optional)
            
        Returns:
            Dictionary with report in requested format
        """
        # Ensure findings is not None - handle case where synthesis failed
        if findings is None:
            findings = {}
        
        # Ensure ranked_sources is not None
        if ranked_sources is None:
            ranked_sources = []
        
        # UX Improvement 2: Create scope configuration
        scope_configurator = create_scope_configurator()
        if output_scope:
            scope_config = scope_configurator.create_config(
                report_length=output_scope.get('reportLength', 'standard'),
                sections=self._normalize_sections(output_scope.get('sections')),
                writing_style=output_scope.get('writingStyle')
            )
        else:
            scope_config = scope_configurator.create_config()
        
        # UX Improvement 2: Create style adapter
        style_adapter = StyleAdapter(scope_config)
        
        # Phase 9: Use plugin citation style if available
        # UX Improvement 3: Use theme citation style if available, otherwise plugin, otherwise default
        citation_style = "apa"  # Default
        if theme_config and 'citation_style' in theme_config:
            citation_style = theme_config['citation_style']
        elif plugin_config and 'citation_style' in plugin_config:
            citation_style = plugin_config['citation_style']
        
        # Limit sources based on report length
        min_sources, max_sources = scope_config.get_source_count_range()
        limited_sources = ranked_sources[:max_sources]
        
        # Add sources to citation manager
        for source in limited_sources:
            self.citation_manager.add_citation_from_source(source)
        
        # UX Improvement 2: Use section builder if sections are configured
        if output_scope and output_scope.get('sections'):
            section_builder = create_section_builder(scope_config)
            sections = section_builder.build_all_sections(
                query=query,
                findings=findings,
                sources=limited_sources,
                reasoning=reasoning
            )
            # Generate LLM sections for enabled sections
            report_sections = self._generate_sections_with_style(
                query,
                findings,
                reasoning,
                research_plan,
                style_adapter,
                scope_config
            )
            # Merge section builder sections with LLM sections
            report_sections = {**sections, **report_sections}
        else:
            # Generate report sections using LLM
            report_sections = self._generate_sections_with_style(
                query,
                findings,
                reasoning,
                research_plan,
                style_adapter,
                scope_config
            )
        
        # Build full report
        report_markdown = self._build_report_markdown(
            query,
            report_sections,
            limited_sources,
            citation_style,  # Phase 9: Use plugin citation style
            scope_config  # UX Improvement 2: Apply scope config
        )
        
        # UX Improvement 2: Apply style adaptation
        report_markdown = style_adapter.adapt_text(report_markdown)
        
        # Convert to requested format
        if output_format == "html":
            report_content = self._markdown_to_html(report_markdown, format_options)
        elif output_format == "json":
            report_content = self._markdown_to_json(report_sections, limited_sources)
        else:  # markdown
            report_content = report_markdown
        
        return {
            'query': query,
            'report': report_content,
            'format': output_format,
            'citations': self.citation_manager.get_all_citations(),
            'sections': report_sections,
            'word_count': len(report_markdown.split()),
            'scope_config': scope_config.to_dict()  # UX Improvement 2: Include scope config
        }
    
    def _generate_sections_with_style(
        self,
        query: str,
        findings: Optional[Dict],
        reasoning: Optional[Dict],
        research_plan: Optional[Dict],
        style_adapter: StyleAdapter,
        scope_config: OutputScopeConfig
    ) -> Dict:
        """Generate report sections using LLM with style configuration."""
        # Handle None findings gracefully
        if findings is None:
            findings = {}
        
        key_findings = findings.get('key_findings', [])
        main_themes = findings.get('main_themes', [])
        key_facts = findings.get('key_facts', [])
        contradictions = findings.get('contradictions', [])
        
        reasoning_steps = reasoning.get('reasoning_steps', []) if reasoning else []
        final_conclusions = reasoning.get('final_conclusions', []) if reasoning else []
        
        # Get style instructions
        style_instructions = style_adapter.get_style_instructions()
        
        # Get word range
        min_words, max_words = scope_config.get_word_range()
        
        # Get enabled sections
        enabled_sections = scope_config.get_enabled_sections()
        
        prompt = f"""Generate a research report for this query: "{query}"

Style Requirements:
{style_instructions}

Target Length: {min_words}-{max_words} words

Key Findings:
{json.dumps(key_findings[:15], indent=2)}

Main Themes:
{json.dumps(main_themes, indent=2)}

Key Facts:
{json.dumps(key_facts[:20], indent=2)}

Contradictions Found:
{json.dumps(contradictions, indent=2)}

Reasoning Steps:
{json.dumps(reasoning_steps[:5], indent=2) if reasoning_steps else 'None'}

Final Conclusions:
{json.dumps(final_conclusions, indent=2) if final_conclusions else 'None'}

Generate sections only for: {', '.join(enabled_sections)}

Return JSON with section names as keys and content as values."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Parse JSON response
            import re
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                sections = json.loads(json_match.group())
                return sections
        except Exception as e:
            Actor.log.warning(f"Failed to generate styled sections: {e}")
        
        # Fallback to original method
        return self._generate_sections(query, findings, reasoning, research_plan)
    
    def _normalize_sections(self, sections: Optional[Dict]) -> Optional[Dict]:
        """Normalize section names from camelCase to snake_case."""
        if not sections:
            return None
        
        normalized = {}
        mapping = {
            'executiveSummary': 'executive_summary',
            'keyFindings': 'key_findings',
            'detailedAnalysis': 'detailed_analysis',
            'expertOpinions': 'expert_opinions',
            'caseStudies': 'case_studies',
            'futureTrends': 'future_trends'
        }
        
        for key, value in sections.items():
            normalized_key = mapping.get(key, key)
            normalized[normalized_key] = value
        
        return normalized
    
    def _generate_sections(
        self,
        query: str,
        findings: Dict,
        reasoning: Optional[Dict],
        research_plan: Optional[Dict]
    ) -> Dict:
        """Generate report sections using LLM."""
        key_findings = findings.get('key_findings', [])
        main_themes = findings.get('main_themes', [])
        key_facts = findings.get('key_facts', [])
        contradictions = findings.get('contradictions', [])
        
        reasoning_steps = reasoning.get('reasoning_steps', []) if reasoning else []
        final_conclusions = reasoning.get('final_conclusions', []) if reasoning else []
        
        prompt = f"""Generate a comprehensive research report for this query: "{query}"

Key Findings:
{json.dumps(key_findings[:15], indent=2)}

Main Themes:
{json.dumps(main_themes, indent=2)}

Key Facts:
{json.dumps(key_facts[:20], indent=2)}

Contradictions Found:
{json.dumps(contradictions, indent=2)}

Reasoning Steps:
{json.dumps(reasoning_steps[:5], indent=2) if reasoning_steps else 'None'}

Final Conclusions:
{json.dumps(final_conclusions, indent=2) if final_conclusions else 'None'}

Generate a well-structured report with these sections:

1. Executive Summary (2-3 paragraphs with key takeaways)
2. Introduction (context and research objectives)
3. Main Findings (organized by themes, with specific facts and statistics)
4. Detailed Analysis (synthesis of findings, reasoning chains)
5. Contradictions and Limitations (if any)
6. Conclusions (final conclusions and implications)

For each factual claim, include citation placeholders like [CITATION_1], [CITATION_2] etc.
Use clear, professional language suitable for non-experts.
Include specific examples, statistics, and concrete details.

Return a JSON object with:
{{
  "executive_summary": "2-3 paragraphs",
  "introduction": "introduction text",
  "main_findings": {{
    "theme1": "detailed findings for theme1",
    "theme2": "detailed findings for theme2"
  }},
  "detailed_analysis": "detailed analysis text",
  "contradictions": "contradictions section if any",
  "conclusions": "conclusions section"
}}

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Clean JSON response
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            sections = json.loads(content)
            return sections
            
        except Exception as e:
            Actor.log.error(f"Report generation failed: {e}")
            # Fallback to simple structure
            return {
                'executive_summary': f"This report synthesizes research on: {query}",
                'introduction': f"Research was conducted to answer: {query}",
                'main_findings': {'Overview': ' '.join(key_findings[:5])},
                'detailed_analysis': ' '.join(key_findings),
                'contradictions': ' '.join(contradictions) if contradictions else 'None identified',
                'conclusions': ' '.join(final_conclusions) if final_conclusions else 'Research completed'
            }
    
    def _build_report_markdown(
        self,
        query: str,
        sections: Dict,
        ranked_sources: List[Dict],
        citation_style: str = "apa",
        scope_config: Optional[OutputScopeConfig] = None
    ) -> str:
        """Build full markdown report."""
        lines = []
        
        # Title
        lines.append(f"# Deep Research Report: {query}\n")
        lines.append(f"*Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")
        lines.append("---\n\n")
        
        # Executive Summary
        lines.append("## Executive Summary\n\n")
        lines.append(sections.get('executive_summary', '') + "\n\n")
        
        # Introduction
        lines.append("## Introduction\n\n")
        lines.append(sections.get('introduction', '') + "\n\n")
        
        # Main Findings
        lines.append("## Main Findings\n\n")
        main_findings = sections.get('main_findings', {})
        if isinstance(main_findings, dict):
            for theme, content in main_findings.items():
                lines.append(f"### {theme}\n\n")
                lines.append(content + "\n\n")
        else:
            lines.append(str(main_findings) + "\n\n")
        
        # Detailed Analysis
        lines.append("## Detailed Analysis\n\n")
        lines.append(sections.get('detailed_analysis', '') + "\n\n")
        
        # Contradictions
        contradictions = sections.get('contradictions', '')
        if contradictions and contradictions.lower() not in ['none', 'none identified', '']:
            lines.append("## Contradictions and Limitations\n\n")
            lines.append(contradictions + "\n\n")
        
        # Conclusions
        lines.append("## Conclusions\n\n")
        lines.append(sections.get('conclusions', '') + "\n\n")
        
        # Methodology
        lines.append("## Methodology\n\n")
        lines.append("This report was generated through comprehensive research involving:\n")
        lines.append(f"- Multiple search queries across various sources\n")
        lines.append(f"- Analysis of {len(ranked_sources)} sources\n")
        lines.append("- Content extraction and relevance scoring\n")
        lines.append("- LLM-based synthesis and reasoning\n\n")
        
        # Sources
        lines.append("## Sources\n\n")
        for i, source in enumerate(ranked_sources[:20], 1):
            url = source.get('url', '')
            title = source.get('title', 'Unknown')
            lines.append(f"{i}. [{title}]({url})\n")
        
        # Bibliography
        lines.append("\n")
        lines.append(self.citation_manager.format_bibliography(style=citation_style))  # Phase 9: Use plugin style
        
        return ''.join(lines)
    
    def _markdown_to_html(self, markdown: str, format_options: Optional[Dict] = None) -> str:
        """Convert markdown to HTML with optional formatting."""
        import markdown
        
        html_content = markdown.markdown(markdown, extensions=['extra', 'codehilite'])
        
        # UX Improvement 2: Apply HTML format options
        html_options = format_options.get('html', {}) if format_options else {}
        theme = html_options.get('theme', 'professional')
        responsive = html_options.get('responsive', True)
        print_optimized = html_options.get('printOptimized', True)
        
        # Generate HTML with theme
        css = self._get_theme_css(theme)
        responsive_meta = '<meta name="viewport" content="width=device-width, initial-scale=1.0">' if responsive else ''
        print_css = '<style media="print">@page { margin: 2cm; }</style>' if print_optimized else ''
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    {responsive_meta}
    <title>Research Report</title>
    <style>
        {css}
    </style>
    {print_css}
</head>
<body>
    <div class="report-container">
        {html_content}
    </div>
</body>
</html>"""
        
        return html
    
    def _get_theme_css(self, theme: str) -> str:
        """Get CSS for theme."""
        themes = {
            'minimal': """
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1, h2, h3 { color: #333; }
            """,
            'professional': """
                body { font-family: 'Georgia', serif; max-width: 900px; margin: 0 auto; padding: 40px; line-height: 1.6; }
                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; }
            """,
            'academic': """
                body { font-family: 'Times New Roman', serif; max-width: 800px; margin: 0 auto; padding: 40px; line-height: 1.8; }
                h1, h2, h3 { color: #000; font-weight: bold; }
                p { text-align: justify; }
            """,
            'dark': """
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #1e1e1e; color: #d4d4d4; max-width: 900px; margin: 0 auto; padding: 40px; }
                h1, h2, h3 { color: #4ec9b0; }
                code { background: #252526; color: #ce9178; }
            """
        }
        return themes.get(theme, themes['professional'])
    
    def _markdown_to_json(self, sections: Dict, sources: List[Dict]) -> Dict:
        """Convert report to JSON format."""
        return {
            'query': sections.get('query', ''),
            'executive_summary': sections.get('executive_summary', ''),
            'introduction': sections.get('introduction', ''),
            'main_findings': sections.get('main_findings', {}),
            'detailed_analysis': sections.get('detailed_analysis', ''),
            'contradictions': sections.get('contradictions', ''),
            'conclusions': sections.get('conclusions', ''),
            'sources': sources[:20],
            'citations': self.citation_manager.get_all_citations()
        }


def generate_report(
    query: str,
    findings: Dict,
    ranked_sources: List[Dict],
    output_format: str = "markdown"
) -> Dict:
    """
    Convenience function to generate a report.
    
    Args:
        query: Research query
        findings: Research findings
        ranked_sources: Ranked sources
        output_format: Output format
        
    Returns:
        Report dictionary
    """
    generator = ReportGenerator()
    return generator.generate_report(query, findings, ranked_sources, output_format=output_format)

