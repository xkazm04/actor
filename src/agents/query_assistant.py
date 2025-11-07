"""
Query Assistant - AI-powered query refinement using Claude Sonnet.
Analyzes queries, detects ambiguity, and suggests improvements.
"""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from apify import Actor


class QueryAssistant:
    """
    AI-powered query assistant for query refinement.
    Uses Claude Sonnet to analyze and improve queries.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize query assistant.
        
        Args:
            api_key: Anthropic API key (optional)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        if self.api_key:
            try:
                self.client = Anthropic(api_key=self.api_key)
                self.model = "claude-sonnet-4-20250514"
            except Exception as e:
                Actor.log.warning(f"Query assistant initialization failed: {e}")
                self.client = None
        else:
            self.client = None
            Actor.log.warning("ANTHROPIC_API_KEY not set, query assistant will use fallback methods")
    
    def analyze_query(self, query: str) -> Dict:
        """
        Analyze query for ambiguity and vagueness.
        
        Args:
            query: Query to analyze
            
        Returns:
            Analysis result dictionary
        """
        if not self.client:
            return self._fallback_analysis(query)
        
        prompt = f"""Analyze this research query for ambiguity, vagueness, and clarity:

Query: "{query}"

Provide analysis in JSON format:
{{
  "is_ambiguous": true/false,
  "ambiguity_level": "low/medium/high",
  "ambiguous_aspects": ["aspect1", "aspect2"],
  "clarifying_questions": ["question1", "question2"],
  "suggested_refinements": ["refinement1", "refinement2"],
  "query_quality_score": 0-100
}}

Return ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Parse JSON response
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                analysis = json.loads(json_match.group())
                return analysis
            else:
                return self._fallback_analysis(query)
                
        except Exception as e:
            Actor.log.warning(f"Query analysis failed: {e}")
            return self._fallback_analysis(query)
    
    def suggest_clarifying_questions(self, query: str) -> List[str]:
        """
        Suggest clarifying questions for ambiguous queries.
        
        Args:
            query: Query to analyze
            
        Returns:
            List of clarifying questions
        """
        analysis = self.analyze_query(query)
        return analysis.get('clarifying_questions', [])
    
    def refine_query(self, query: str, context: Optional[Dict] = None) -> Dict:
        """
        Refine query based on analysis.
        
        Args:
            query: Original query
            context: Optional context (user preferences, domain, etc.)
            
        Returns:
            Refined query dictionary
        """
        if not self.client:
            return {
                'original_query': query,
                'refined_query': query,
                'improvements': [],
                'confidence': 0.5
            }
        
        context_str = ""
        if context:
            context_str = f"\nContext: {context}"
        
        prompt = f"""Refine this research query to be more specific and effective:

Original Query: "{query}"{context_str}

Provide a refined version and explain improvements in JSON format:
{{
  "refined_query": "improved query text",
  "improvements": ["improvement1", "improvement2"],
  "confidence": 0.0-1.0,
  "reasoning": "explanation of changes"
}}

Return ONLY valid JSON, no markdown formatting."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Parse JSON response
            import json
            import re
            
            json_match = re.search(r'\{[\s\S]*\}', content)
            if json_match:
                refinement = json.loads(json_match.group())
                refinement['original_query'] = query
                return refinement
            else:
                return {
                    'original_query': query,
                    'refined_query': query,
                    'improvements': [],
                    'confidence': 0.5
                }
                
        except Exception as e:
            Actor.log.warning(f"Query refinement failed: {e}")
            return {
                'original_query': query,
                'refined_query': query,
                'improvements': [],
                'confidence': 0.5
            }
    
    def generate_query_variations(self, query: str, count: int = 3) -> List[str]:
        """
        Generate alternative query formulations.
        
        Args:
            query: Original query
            count: Number of variations to generate
            
        Returns:
            List of query variations
        """
        if not self.client:
            return [query]  # Return original if no LLM
        
        prompt = f"""Generate {count} alternative formulations of this research query:

Original: "{query}"

Provide variations that:
- Use different phrasings
- Emphasize different aspects
- May yield different search results

Return as JSON array:
["variation1", "variation2", "variation3"]

Return ONLY valid JSON array, no markdown formatting."""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            content = response.content[0].text if response.content else ""
            
            # Parse JSON array
            import json
            import re
            
            json_match = re.search(r'\[[\s\S]*\]', content)
            if json_match:
                variations = json.loads(json_match.group())
                return variations[:count]
            else:
                return [query]
                
        except Exception as e:
            Actor.log.warning(f"Query variation generation failed: {e}")
            return [query]
    
    def _fallback_analysis(self, query: str) -> Dict:
        """Fallback analysis when LLM is not available."""
        # Simple heuristic-based analysis
        word_count = len(query.split())
        
        is_ambiguous = word_count < 5 or any(word in query.lower() for word in ['it', 'this', 'that', 'thing'])
        
        clarifying_questions = []
        if is_ambiguous:
            clarifying_questions.append("What specific aspect are you interested in?")
            clarifying_questions.append("What do you want to learn about this topic?")
        
        return {
            'is_ambiguous': is_ambiguous,
            'ambiguity_level': 'medium' if is_ambiguous else 'low',
            'ambiguous_aspects': [],
            'clarifying_questions': clarifying_questions,
            'suggested_refinements': [],
            'query_quality_score': min(100, word_count * 10)
        }


def create_query_assistant(api_key: Optional[str] = None) -> QueryAssistant:
    """Create a query assistant instance."""
    return QueryAssistant(api_key)



