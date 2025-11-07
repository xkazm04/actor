"""
Query Decomposer Agent using Agno framework.
Breaks down main queries into focused sub-queries using DeepSeek R1.
"""

import os
import json
from typing import List, Optional
from anthropic import Anthropic
from src.utils.models import SubQuery


class QueryDecomposer:
    """
    Decomposes research queries into sub-queries using LLM reasoning.
    Uses DeepSeek R1 via Anthropic API (or direct DeepSeek API if available).
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the query decomposer.
        
        Args:
            api_key: API key for LLM provider. If None, reads from environment.
        """
        # Try DeepSeek API first, fallback to Anthropic Claude
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("ANTHROPIC_API_KEY")
        
        if not self.api_key:
            raise ValueError("API key required. Set DEEPSEEK_API_KEY or ANTHROPIC_API_KEY environment variable.")
        
        # Use Anthropic client (supports Claude models)
        # For DeepSeek R1, we'll use OpenAI-compatible client if needed
        try:
            self.client = Anthropic(api_key=self.api_key)
            self.model = "claude-sonnet-4-20250514"  # Fallback to Claude if DeepSeek not available
        except Exception:
            # Fallback: try OpenAI-compatible client for DeepSeek
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key, base_url="https://api.deepseek.com")
                self.model = "deepseek-chat"
            except Exception as e:
                raise ValueError(f"Failed to initialize LLM client: {e}")
    
    def decompose(self, main_query: str, max_sub_queries: int = 20) -> List[SubQuery]:
        """
        Break down a main query into focused sub-queries.
        
        Args:
            main_query: The main research query
            max_sub_queries: Maximum number of sub-queries to generate (5-20)
            
        Returns:
            List of SubQuery objects, prioritized by relevance
        """
        max_sub_queries = max(5, min(max_sub_queries, 20))
        
        prompt = f"""You are a research assistant that breaks down complex queries into focused sub-queries.

Main Query: {main_query}

Your task:
1. Break down this query into {max_sub_queries} focused sub-queries
2. Each sub-query should explore a specific aspect or angle
3. Prioritize sub-queries by information value (1=highest priority)
4. Include queries that cover: definitions, current state, recent developments, expert opinions, challenges, applications, and related topics
5. Use query expansion techniques (synonyms, related concepts)

Return a JSON array with this structure:
[
  {{
    "query": "sub-query text",
    "priority": 1-10,
    "category": "category name (e.g., 'definitions', 'current_state', 'recent_developments')",
    "reasoning": "why this sub-query is important"
  }}
]

Return ONLY valid JSON, no markdown formatting."""

        try:
            # Call LLM (synchronous call, will be wrapped in async context)
            if hasattr(self.client, 'messages'):
                # Anthropic API
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text if response.content else ""
            elif hasattr(self.client, 'chat'):
                # OpenAI-compatible API (DeepSeek)
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=2000
                )
                content = response.choices[0].message.content
            else:
                raise ValueError("Unsupported client type")
            
            # Parse JSON response
            # Clean up markdown code blocks if present
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            sub_queries_data = json.loads(content)
            
            # Convert to SubQuery objects
            sub_queries = []
            for sq_data in sub_queries_data[:max_sub_queries]:
                sub_queries.append(SubQuery(
                    query=sq_data.get("query", ""),
                    priority=sq_data.get("priority", 5),
                    category=sq_data.get("category"),
                    reasoning=sq_data.get("reasoning")
                ))
            
            # Sort by priority (ascending, so 1 is highest)
            sub_queries.sort(key=lambda x: x.priority)
            
            return sub_queries
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse LLM response as JSON: {e}")
        except Exception as e:
            raise RuntimeError(f"Query decomposition failed: {e}")


# Convenience function for async usage
async def decompose_query(query: str, max_sub_queries: int = 20) -> List[SubQuery]:
    """
    Convenience function to decompose a query.
    
    Args:
        query: Main research query
        max_sub_queries: Maximum number of sub-queries
        
    Returns:
        List of SubQuery objects
    """
    import asyncio
    decomposer = QueryDecomposer()
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, decomposer.decompose, query, max_sub_queries)

