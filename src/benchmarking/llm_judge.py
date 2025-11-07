"""
LLM Judge - Uses LLM to evaluate report quality.
Can use Ollama (gpt-4o:20b) or other LLM providers.
"""

from typing import Dict, Optional
import os
from apify import Actor


class LLMJudge:
    """
    Uses LLM to evaluate report quality.
    Supports Ollama and other LLM providers.
    """
    
    def __init__(self, provider: str = "ollama", model: str = "gpt-4o:20b"):
        """
        Initialize LLM judge.
        
        Args:
            provider: LLM provider (ollama, anthropic, openai)
            model: Model name
        """
        self.provider = provider
        self.model = model
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize LLM client based on provider."""
        if self.provider == "ollama":
            try:
                import ollama
                self.client = ollama
                Actor.log.info(f"Initialized Ollama client with model {self.model}")
            except ImportError:
                Actor.log.warning("Ollama not available, falling back to simple scoring")
                self.client = None
        elif self.provider == "anthropic":
            try:
                from anthropic import Anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = Anthropic(api_key=api_key)
                else:
                    Actor.log.warning("ANTHROPIC_API_KEY not set")
            except ImportError:
                Actor.log.warning("Anthropic SDK not available")
        elif self.provider == "openai":
            try:
                from openai import OpenAI
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = OpenAI(api_key=api_key)
                else:
                    Actor.log.warning("OPENAI_API_KEY not set")
            except ImportError:
                Actor.log.warning("OpenAI SDK not available")
    
    def evaluate_report_quality(
        self,
        query: str,
        report: str,
        sources: List[Dict]
    ) -> Dict:
        """
        Evaluate report quality using LLM.
        
        Args:
            query: Original research query
            report: Generated report
            sources: List of sources used
            
        Returns:
            Quality evaluation dictionary
        """
        if not self.client:
            return self._fallback_evaluation(query, report, sources)
        
        prompt = self._create_evaluation_prompt(query, report, sources)
        
        try:
            if self.provider == "ollama":
                response = self.client.generate(
                    model=self.model,
                    prompt=prompt
                )
                evaluation_text = response.get('response', '')
            elif self.provider == "anthropic":
                response = self.client.messages.create(
                    model=self.model if self.model != "gpt-4o:20b" else "claude-sonnet-4-20250514",
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                evaluation_text = response.content[0].text if response.content else ""
            elif self.provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.model if self.model != "gpt-4o:20b" else "gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                evaluation_text = response.choices[0].message.content if response.choices else ""
            else:
                return self._fallback_evaluation(query, report, sources)
            
            return self._parse_evaluation(evaluation_text)
            
        except Exception as e:
            Actor.log.warning(f"LLM evaluation failed: {e}")
            return self._fallback_evaluation(query, report, sources)
    
    def _create_evaluation_prompt(self, query: str, report: str, sources: List[Dict]) -> str:
        """Create evaluation prompt for LLM."""
        return f"""Evaluate the quality of this research report on a scale of 0-100.

Query: {query}

Report:
{report}

Sources Used: {len(sources)}

Evaluate the report on these dimensions:
1. Accuracy (0-25): Are the facts correct and well-supported?
2. Completeness (0-25): Does it cover all aspects of the query?
3. Coherence (0-25): Is it well-structured and easy to follow?
4. Citation Quality (0-25): Are sources reliable and relevant?

Provide your evaluation as JSON:
{{
  "accuracy_score": <0-25>,
  "completeness_score": <0-25>,
  "coherence_score": <0-25>,
  "citation_quality_score": <0-25>,
  "overall_score": <0-100>,
  "strengths": ["strength1", "strength2"],
  "weaknesses": ["weakness1", "weakness2"],
  "recommendations": ["rec1", "rec2"]
}}

Return ONLY valid JSON, no markdown formatting."""
    
    def _parse_evaluation(self, evaluation_text: str) -> Dict:
        """Parse LLM evaluation response."""
        import json
        import re
        
        # Extract JSON from response
        json_match = re.search(r'\{[\s\S]*\}', evaluation_text)
        if json_match:
            try:
                evaluation = json.loads(json_match.group())
                return {
                    'accuracy_score': evaluation.get('accuracy_score', 0),
                    'completeness_score': evaluation.get('completeness_score', 0),
                    'coherence_score': evaluation.get('coherence_score', 0),
                    'citation_quality_score': evaluation.get('citation_quality_score', 0),
                    'overall_score': evaluation.get('overall_score', 0),
                    'strengths': evaluation.get('strengths', []),
                    'weaknesses': evaluation.get('weaknesses', []),
                    'recommendations': evaluation.get('recommendations', []),
                    'evaluated_by': f"{self.provider}:{self.model}"
                }
            except json.JSONDecodeError:
                pass
        
        return self._fallback_evaluation("", "", [])
    
    def _fallback_evaluation(self, query: str, report: str, sources: List[Dict]) -> Dict:
        """Fallback evaluation when LLM is not available."""
        # Simple heuristic-based evaluation
        word_count = len(report.split())
        source_count = len(sources)
        
        # Basic scores
        accuracy_score = min(20, source_count * 2)  # Up to 20 points
        completeness_score = min(25, word_count // 50)  # Up to 25 points
        coherence_score = 18  # Base score
        citation_quality_score = min(25, source_count * 2)  # Up to 25 points
        
        overall_score = accuracy_score + completeness_score + coherence_score + citation_quality_score
        
        return {
            'accuracy_score': accuracy_score,
            'completeness_score': completeness_score,
            'coherence_score': coherence_score,
            'citation_quality_score': citation_quality_score,
            'overall_score': overall_score,
            'strengths': ['Report generated successfully'],
            'weaknesses': ['LLM evaluation not available'],
            'recommendations': ['Enable LLM judge for detailed evaluation'],
            'evaluated_by': 'fallback'
        }


def create_llm_judge(provider: str = "ollama", model: str = "gpt-4o:20b") -> LLMJudge:
    """Create an LLM judge instance."""
    return LLMJudge(provider, model)



