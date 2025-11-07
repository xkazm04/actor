"""
Preview Generator - Generates free preview before research execution.
Shows research plan, expected sources, estimated time and cost.
"""

from typing import Dict, List, Optional
from apify import Actor

from src.agents.query_decomposer import QueryDecomposer
from src.search.multi_search_engine import MultiSearchEngine
from src.cost.cost_tracker import get_cost_tracker


class PreviewGenerator:
    """
    Generates research preview before execution.
    Provides free preview of research plan, sources, and estimates.
    """
    
    def __init__(self):
        """Initialize preview generator."""
        self.decomposer = QueryDecomposer()
        self.search_engine = MultiSearchEngine()
        self.cost_tracker = get_cost_tracker()
    
    async def generate_preview(
        self,
        query: str,
        max_searches: int = 20,
        research_depth: str = "standard"
    ) -> Dict:
        """
        Generate research preview.
        
        Args:
            query: Research query
            max_searches: Maximum number of searches
            research_depth: Research depth mode
            
        Returns:
            Preview dictionary with plan, sources, estimates
        """
        Actor.log.info(f"Generating preview for query: {query}")
        
        preview = {
            'query': query,
            'research_plan': None,
            'expected_sources': [],
            'estimated_time': None,
            'estimated_cost': None,
            'output_structure': None
        }
        
        try:
            # Decompose query to get research plan
            import asyncio
            loop = asyncio.get_event_loop()
            sub_queries = await loop.run_in_executor(
                None,
                self.decomposer.decompose,
                query,
                max_searches
            )
            
            preview['research_plan'] = {
                'total_searches': len(sub_queries),
                'sub_queries': [sq.query for sq in sub_queries[:10]],  # First 10
                'categories': list(set(sq.category for sq in sub_queries if sq.category))
            }
            
            # Get sample sources for first few queries
            sample_sources = []
            for sub_query in sub_queries[:3]:  # First 3 queries
                try:
                    results = await self.search_engine.search(
                        query=sub_query.query,
                        num_results=5
                    )
                    sample_sources.extend([r.model_dump() for r in results[:3]])
                except Exception as e:
                    Actor.log.warning(f"Failed to get sample sources for {sub_query.query}: {e}")
            
            preview['expected_sources'] = sample_sources[:10]  # Top 10 sample sources
            
            # Estimate time and cost
            preview['estimated_time'] = self._estimate_time(len(sub_queries), research_depth)
            preview['estimated_cost'] = self._estimate_cost(len(sub_queries), research_depth)
            
            # Generate output structure preview
            preview['output_structure'] = self._generate_output_structure_preview()
            
        except Exception as e:
            Actor.log.warning(f"Preview generation failed: {e}")
            preview['error'] = str(e)
        
        return preview
    
    def _estimate_time(self, num_searches: int, research_depth: str) -> Dict:
        """
        Estimate research time.
        
        Args:
            num_searches: Number of searches
            research_depth: Research depth mode
            
        Returns:
            Time estimate dictionary
        """
        # Base time per search (seconds)
        base_time_per_search = 30
        
        # Depth multipliers
        depth_multipliers = {
            'quick': 0.5,
            'standard': 1.0,
            'deep': 2.0
        }
        
        multiplier = depth_multipliers.get(research_depth, 1.0)
        estimated_seconds = num_searches * base_time_per_search * multiplier
        
        return {
            'seconds': estimated_seconds,
            'minutes': estimated_seconds / 60,
            'formatted': f"{estimated_seconds / 60:.1f} minutes"
        }
    
    def _estimate_cost(self, num_searches: int, research_depth: str) -> Dict:
        """
        Estimate research cost.
        
        Args:
            num_searches: Number of searches
            research_depth: Research depth mode
            
        Returns:
            Cost estimate dictionary
        """
        # Base cost per search (USD)
        base_cost_per_search = 0.02
        
        # Depth multipliers
        depth_multipliers = {
            'quick': 0.5,
            'standard': 1.0,
            'deep': 2.5
        }
        
        multiplier = depth_multipliers.get(research_depth, 1.0)
        estimated_cost = num_searches * base_cost_per_search * multiplier
        
        return {
            'usd': estimated_cost,
            'formatted': f"${estimated_cost:.2f}"
        }
    
    def _generate_output_structure_preview(self) -> Dict:
        """
        Generate output structure preview.
        
        Returns:
            Output structure dictionary
        """
        return {
            'sections': [
                'Executive Summary',
                'Introduction',
                'Main Findings',
                'Detailed Analysis',
                'Conclusions',
                'Bibliography'
            ],
            'estimated_word_count': '1000-2000 words',
            'estimated_sources': '10-20 sources',
            'formats': ['Markdown', 'HTML', 'JSON']
        }


def create_preview_generator() -> PreviewGenerator:
    """Create a preview generator instance."""
    return PreviewGenerator()



