"""
Reasoning Engine - Uses DeepSeek R1 for step-by-step reasoning.
Documents reasoning process and builds causal chains.
"""

import os
import json
from typing import List, Dict, Optional
from anthropic import Anthropic
from apify import Actor


class ReasoningStep:
    """Model for a reasoning step."""
    
    def __init__(self, step_number: int, reasoning: str, conclusion: str, evidence: List[str]):
        self.step_number = step_number
        self.reasoning = reasoning
        self.conclusion = conclusion
        self.evidence = evidence
    
    def to_dict(self):
        """Convert to dictionary."""
        return {
            'step_number': self.step_number,
            'reasoning': self.reasoning,
            'conclusion': self.conclusion,
            'evidence': self.evidence
        }


class ReasoningEngine:
    """
    Performs step-by-step reasoning using DeepSeek R1 or Claude.
    Builds logical chains and identifies contradictions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize reasoning engine.
        
        Args:
            api_key: API key for LLM. If None, reads from environment.
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key required. Set DEEPSEEK_API_KEY or ANTHROPIC_API_KEY")
        
        try:
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-sonnet-4-20250514"
        except Exception:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                self.model = "deepseek-chat"
            except Exception as e:
                raise ValueError(f"Failed to initialize LLM client: {e}")
    
    def reason_about_findings(
        self,
        query: str,
        findings: Dict,
        max_steps: int = 5
    ) -> Dict:
        """
        Perform step-by-step reasoning about research findings.
        
        Args:
            query: Original research query
            findings: Dictionary with key findings, themes, facts
            max_steps: Maximum reasoning steps
            
        Returns:
            Dictionary with reasoning chain and conclusions
        """
        key_findings = findings.get('key_findings', [])
        facts = findings.get('key_facts', [])
        contradictions = findings.get('contradictions', [])
        
        prompt = f"""Perform step-by-step reasoning to answer this research query: "{query}"

Key Findings:
{json.dumps(key_findings[:15], indent=2)}

Facts Collected:
{json.dumps(facts[:20], indent=2)}

Contradictions Found:
{json.dumps(contradictions, indent=2)}

Your task:
1. Break down the reasoning into {max_steps} logical steps
2. For each step, explain your reasoning and draw a conclusion
3. Cite evidence (findings/facts) that support each step
4. Identify and reconcile any contradictions
5. Build a causal chain leading to final conclusions

Return a JSON object with:
{{
  "reasoning_steps": [
    {{
      "step_number": 1,
      "reasoning": "explanation of reasoning",
      "conclusion": "conclusion drawn",
      "evidence": ["evidence1", "evidence2"]
    }}
  ],
  "final_conclusions": ["conclusion1", "conclusion2"],
  "contradictions_resolved": ["how contradiction1 was resolved"],
  "confidence_level": "high/medium/low"
}}

Return ONLY valid JSON, no markdown formatting."""

        try:
            if hasattr(self.client, 'messages'):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=3000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text if response.content else ""
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=3000
                )
                content = response.choices[0].message.content
            
            # Parse JSON
            content = self._clean_json_response(content)
            reasoning_data = json.loads(content)
            
            # Convert to ReasoningStep objects
            reasoning_steps = []
            for step_data in reasoning_data.get('reasoning_steps', []):
                step = ReasoningStep(
                    step_number=step_data.get('step_number', 0),
                    reasoning=step_data.get('reasoning', ''),
                    conclusion=step_data.get('conclusion', ''),
                    evidence=step_data.get('evidence', [])
                )
                reasoning_steps.append(step)
            
            return {
                'reasoning_steps': [step.to_dict() for step in reasoning_steps],
                'final_conclusions': reasoning_data.get('final_conclusions', []),
                'contradictions_resolved': reasoning_data.get('contradictions_resolved', []),
                'confidence_level': reasoning_data.get('confidence_level', 'medium'),
                'status': 'success'
            }
            
        except Exception as e:
            Actor.log.error(f"Reasoning failed: {e}")
            return {
                'reasoning_steps': [],
                'final_conclusions': [],
                'contradictions_resolved': [],
                'confidence_level': 'low',
                'status': 'error',
                'error': str(e)
            }
    
    def identify_contradictions(self, findings: List[Dict]) -> List[Dict]:
        """
        Identify contradictions across multiple findings.
        
        Args:
            findings: List of analysis dictionaries from different sources
            
        Returns:
            List of identified contradictions
        """
        all_facts = []
        for finding in findings:
            facts = finding.get('facts', [])
            all_facts.extend(facts)
        
        if len(all_facts) < 2:
            return []
        
        prompt = f"""Identify contradictions in these facts from different sources:

Facts:
{json.dumps(all_facts[:30], indent=2)}

Return a JSON array of contradictions:
[
  {{
    "fact1": "first fact",
    "fact2": "contradicting fact",
    "source1": "source URL",
    "source2": "source URL",
    "explanation": "why they contradict"
  }}
]

Return ONLY valid JSON, no markdown formatting."""

        try:
            if hasattr(self.client, 'messages'):
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text if response.content else ""
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                content = response.choices[0].message.content
            
            content = self._clean_json_response(content)
            contradictions = json.loads(content)
            
            return contradictions if isinstance(contradictions, list) else []
            
        except Exception as e:
            Actor.log.warning(f"Contradiction detection failed: {e}")
            return []
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response from LLM."""
        content = content.strip()
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()


def reason_about_findings(query: str, findings: Dict) -> Dict:
    """
    Convenience function to perform reasoning.
    
    Args:
        query: Research query
        findings: Research findings dictionary
        
    Returns:
        Reasoning result dictionary
    """
    engine = ReasoningEngine()
    return engine.reason_about_findings(query, findings)



