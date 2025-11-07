"""
Research Planner - Generates initial research plans and adapts them dynamically.
Creates structured research roadmaps with milestones and information goals.
"""

import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from anthropic import Anthropic
from apify import Actor


class ResearchPlan:
    """Model for research plan structure."""
    
    def __init__(self, query: str, goals: List[str], milestones: List[Dict], estimated_searches: int):
        self.query = query
        self.goals = goals
        self.milestones = milestones
        self.estimated_searches = estimated_searches
        self.created_at = datetime.now().isoformat()
        self.adjustments = []
    
    def to_dict(self):
        """Convert plan to dictionary."""
        return {
            'query': self.query,
            'goals': self.goals,
            'milestones': self.milestones,
            'estimated_searches': self.estimated_searches,
            'created_at': self.created_at,
            'adjustments': self.adjustments
        }


class ResearchPlanner:
    """
    Generates and manages research plans.
    Creates initial plans and adapts them based on findings.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize research planner.
        
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
    
    def create_initial_plan(self, query: str, max_searches: int = 20) -> ResearchPlan:
        """
        Generate initial research plan based on query.
        
        Args:
            query: Research query
            max_searches: Maximum number of searches planned
            
        Returns:
            ResearchPlan object
        """
        prompt = f"""Create a comprehensive research plan for this query: "{query}"

Your task:
1. Identify 5-10 information goals (what we need to learn)
2. Create 3-5 research milestones (key checkpoints)
3. Estimate the number of searches needed (5-{max_searches})
4. Identify potential knowledge gaps upfront

Return a JSON object with this structure:
{{
  "goals": ["goal1", "goal2", ...],
  "milestones": [
    {{
      "name": "milestone name",
      "description": "what we'll achieve",
      "searches_required": 5
    }}
  ],
  "estimated_searches": 20,
  "knowledge_gaps": ["gap1", "gap2", ...]
}}

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
            
            # Parse JSON
            content = self._clean_json_response(content)
            plan_data = json.loads(content)
            
            plan = ResearchPlan(
                query=query,
                goals=plan_data.get('goals', []),
                milestones=plan_data.get('milestones', []),
                estimated_searches=min(plan_data.get('estimated_searches', max_searches), max_searches)
            )
            
            Actor.log.info(f"Created research plan with {len(plan.goals)} goals and {len(plan.milestones)} milestones")
            return plan
            
        except Exception as e:
            Actor.log.error(f"Failed to create research plan: {e}")
            # Fallback to simple plan
            return ResearchPlan(
                query=query,
                goals=[f"Understand {query}"],
                milestones=[{"name": "Initial Research", "description": "Gather basic information", "searches_required": max_searches}],
                estimated_searches=max_searches
            )
    
    def refine_plan(
        self,
        current_plan: ResearchPlan,
        findings: Dict,
        completed_searches: int
    ) -> ResearchPlan:
        """
        Refine research plan based on findings.
        
        Args:
            current_plan: Current research plan
            findings: Dictionary with key findings, themes, gaps
            completed_searches: Number of searches completed
            
        Returns:
            Refined ResearchPlan
        """
        key_findings = findings.get('key_findings', [])
        knowledge_gaps = findings.get('knowledge_gaps', [])
        themes = findings.get('main_themes', [])
        
        prompt = f"""Refine this research plan based on current findings.

Original Query: {current_plan.query}
Completed Searches: {completed_searches}/{current_plan.estimated_searches}

Current Findings:
{json.dumps(key_findings[:10], indent=2)}

Identified Knowledge Gaps:
{json.dumps(knowledge_gaps, indent=2)}

Themes Covered:
{json.dumps(themes, indent=2)}

Your task:
1. Assess what has been learned
2. Identify remaining knowledge gaps
3. Suggest refined search queries for remaining gaps
4. Adjust milestones if needed
5. Estimate remaining searches needed

Return a JSON object with:
{{
  "assessment": "what we've learned so far",
  "remaining_gaps": ["gap1", "gap2", ...],
  "refined_queries": ["query1", "query2", ...],
  "adjusted_milestones": [...],
  "remaining_searches": 5
}}

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
            refinement = json.loads(content)
            
            # Update plan with refinements
            current_plan.adjustments.append({
                'timestamp': datetime.now().isoformat(),
                'completed_searches': completed_searches,
                'refinement': refinement
            })
            
            # Add refined queries as new sub-queries if needed
            refined_queries = refinement.get('refined_queries', [])
            if refined_queries:
                Actor.log.info(f"Plan refined: {len(refined_queries)} new queries suggested")
            
            return current_plan
            
        except Exception as e:
            Actor.log.warning(f"Plan refinement failed: {e}")
            return current_plan
    
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


def create_research_plan(query: str, max_searches: int = 20) -> ResearchPlan:
    """
    Convenience function to create a research plan.
    
    Args:
        query: Research query
        max_searches: Maximum searches
        
    Returns:
        ResearchPlan object
    """
    planner = ResearchPlanner()
    return planner.create_initial_plan(query, max_searches)



