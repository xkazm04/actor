"""
Content Analyzer - LLM-based analysis of content.
Extracts insights, themes, facts, and builds knowledge graphs.
"""

import os
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from apify import Actor


class ContentAnalyzer:
    """
    Analyzes content using Claude Sonnet to extract insights, themes, and facts.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize content analyzer.
        
        Args:
            api_key: Anthropic API key. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable required")
        
        self.client = Anthropic(api_key=self.api_key)
        self.model = "claude-sonnet-4-20250514"
    
    def analyze_content(
        self,
        content: Dict,
        query: str,
        max_insights: int = 10
    ) -> Dict:
        """
        Analyze processed content and extract insights.
        
        Args:
            content: Processed content dictionary
            query: Original research query
            max_insights: Maximum number of insights to extract
            
        Returns:
            Analysis dictionary with insights, themes, facts, etc.
        """
        markdown = content.get('markdown', '')
        url = content.get('url', '')
        
        if not markdown or len(markdown) < 100:
            return {
                'url': url,
                'insights': [],
                'themes': [],
                'facts': [],
                'status': 'insufficient_content'
            }
        
        # Use chunks if content is too long
        chunks = content.get('chunks', [])
        if chunks:
            # Analyze first few chunks (most important content usually at top)
            text_to_analyze = '\n\n'.join([chunk.get('text', '') for chunk in chunks[:3]])
        else:
            # Limit to first 8000 characters
            text_to_analyze = markdown[:8000]
        
        prompt = f"""Analyze the following content in relation to this research query: "{query}"

Content:
{text_to_analyze}

Extract and return a JSON object with:
1. "insights": Array of {max_insights} key insights (strings)
2. "themes": Array of main themes/topics covered (strings)
3. "facts": Array of specific facts, statistics, or claims (objects with "fact" and "context" fields)
4. "contradictions": Array of any contradictions or conflicting information found (strings)
5. "quotes": Array of notable quotes (objects with "quote" and "context" fields)

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = response.content[0].text if response.content else ""
            
            # Clean JSON response
            content_text = content_text.strip()
            if content_text.startswith("```json"):
                content_text = content_text[7:]
            if content_text.startswith("```"):
                content_text = content_text[3:]
            if content_text.endswith("```"):
                content_text = content_text[:-3]
            content_text = content_text.strip()
            
            analysis = json.loads(content_text)
            
            return {
                'url': url,
                'insights': analysis.get('insights', [])[:max_insights],
                'themes': analysis.get('themes', []),
                'facts': analysis.get('facts', []),
                'contradictions': analysis.get('contradictions', []),
                'quotes': analysis.get('quotes', []),
                'status': 'success'
            }
        
        except json.JSONDecodeError as e:
            Actor.log.error(f"Failed to parse analysis JSON for {url}: {e}")
            return {
                'url': url,
                'insights': [],
                'themes': [],
                'facts': [],
                'status': 'parse_error',
                'error': str(e)
            }
        except Exception as e:
            Actor.log.error(f"Content analysis failed for {url}: {e}")
            return {
                'url': url,
                'insights': [],
                'themes': [],
                'facts': [],
                'status': 'error',
                'error': str(e)
            }
    
    def analyze_multiple(
        self,
        contents: List[Dict],
        query: str,
        max_per_source: int = 10
    ) -> List[Dict]:
        """
        Analyze multiple content sources.
        
        Args:
            contents: List of processed content dictionaries
            query: Original research query
            max_per_source: Maximum insights per source
            
        Returns:
            List of analysis dictionaries
        """
        analyses = []
        
        for i, content in enumerate(contents):
            Actor.log.info(f"Analyzing content {i+1}/{len(contents)}: {content.get('url', 'unknown')}")
            
            analysis = self.analyze_content(content, query, max_per_source)
            analyses.append(analysis)
        
        return analyses
    
    def synthesize_analyses(
        self,
        analyses: List[Dict],
        query: str
    ) -> Dict:
        """
        Synthesize multiple analyses into a unified knowledge structure.
        
        Args:
            analyses: List of analysis dictionaries
            query: Original research query
            
        Returns:
            Synthesized knowledge dictionary
        """
        # Collect all insights, themes, facts
        all_insights = []
        all_themes = []
        all_facts = []
        all_contradictions = []
        
        for analysis in analyses:
            all_insights.extend(analysis.get('insights', []))
            all_themes.extend(analysis.get('themes', []))
            all_facts.extend(analysis.get('facts', []))
            all_contradictions.extend(analysis.get('contradictions', []))
        
        # Use LLM to synthesize
        prompt = f"""Synthesize information from multiple sources about: "{query}"

Insights from sources:
{json.dumps(all_insights[:50], indent=2)}

Themes identified:
{json.dumps(list(set(all_themes)), indent=2)}

Facts collected:
{json.dumps(all_facts[:30], indent=2)}

Contradictions found:
{json.dumps(all_contradictions, indent=2)}

Return a JSON object with:
1. "key_findings": Array of top 10 most important findings (strings)
2. "main_themes": Array of main themes (strings, deduplicated)
3. "key_facts": Array of most important facts (objects)
4. "contradictions": Array of contradictions that need reconciliation (strings)
5. "knowledge_gaps": Array of areas where more information is needed (strings)

Return ONLY valid JSON, no markdown formatting."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content_text = response.content[0].text if response.content else ""
            
            # Clean JSON response
            content_text = content_text.strip()
            if content_text.startswith("```json"):
                content_text = content_text[7:]
            if content_text.startswith("```"):
                content_text = content_text[3:]
            if content_text.endswith("```"):
                content_text = content_text[:-3]
            content_text = content_text.strip()
            
            synthesis = json.loads(content_text)
            
            return {
                'key_findings': synthesis.get('key_findings', []),
                'main_themes': synthesis.get('main_themes', []),
                'key_facts': synthesis.get('key_facts', []),
                'contradictions': synthesis.get('contradictions', []),
                'knowledge_gaps': synthesis.get('knowledge_gaps', []),
                'sources_analyzed': len(analyses),
                'status': 'success'
            }
        
        except Exception as e:
            Actor.log.error(f"Synthesis failed: {e}")
            return {
                'key_findings': all_insights[:10],
                'main_themes': list(set(all_themes)),
                'key_facts': all_facts[:20],
                'contradictions': all_contradictions,
                'knowledge_gaps': [],
                'sources_analyzed': len(analyses),
                'status': 'error',
                'error': str(e)
            }


def analyze_content(content: Dict, query: str) -> Dict:
    """
    Convenience function to analyze content.
    
    Args:
        content: Processed content dictionary
        query: Original research query
        
    Returns:
        Analysis dictionary
    """
    analyzer = ContentAnalyzer()
    return analyzer.analyze_content(content, query)



