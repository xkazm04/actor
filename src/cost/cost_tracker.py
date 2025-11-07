"""
Cost Tracker - Tracks API calls and LLM token usage.
Calculates actual costs and provides cost breakdowns.
"""

from typing import Dict, List, Optional
from datetime import datetime
from apify import Actor


class CostTracker:
    """
    Tracks costs for API calls and LLM usage.
    Calculates total cost and provides breakdowns.
    """
    
    # Cost estimates (per 1K tokens or per call)
    COSTS = {
        # LLM costs (per 1K tokens)
        'claude_sonnet_4_input': 0.003,  # $3 per 1M tokens
        'claude_sonnet_4_output': 0.015,  # $15 per 1M tokens
        'deepseek_chat_input': 0.00014,  # $0.14 per 1M tokens
        'deepseek_chat_output': 0.00028,  # $0.28 per 1M tokens
        
        # Search API costs (per call)
        'google_search': 0.005,  # $5 per 1000 queries
        'brave_search': 0.001,   # $1 per 1000 queries
        'bing_search': 0.001,   # $1 per 1000 queries
        
        # Content extraction (estimated)
        'content_fetch': 0.0001,  # Per URL fetch
    }
    
    def __init__(self):
        """Initialize cost tracker."""
        self.costs: List[Dict] = []
        self.total_cost = 0.0
        self.start_time = datetime.now()
    
    def track_llm_call(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int,
        operation: str = "unknown"
    ):
        """
        Track an LLM API call.
        
        Args:
            model: Model name (e.g., 'claude-sonnet-4', 'deepseek-chat')
            input_tokens: Number of input tokens
            output_tokens: Number of output tokens
            operation: Operation description
        """
        # Determine cost per 1K tokens
        model_key = model.lower().replace('-', '_')
        input_cost_key = f'{model_key}_input'
        output_cost_key = f'{model_key}_output'
        
        input_cost_per_1k = self.COSTS.get(input_cost_key, 0.001)  # Default
        output_cost_per_1k = self.COSTS.get(output_cost_key, 0.002)  # Default
        
        # Calculate costs
        input_cost = (input_tokens / 1000) * input_cost_per_1k
        output_cost = (output_tokens / 1000) * output_cost_per_1k
        total_cost = input_cost + output_cost
        
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'llm_call',
            'model': model,
            'operation': operation,
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'input_cost': input_cost,
            'output_cost': output_cost,
            'total_cost': total_cost
        }
        
        self.costs.append(cost_entry)
        self.total_cost += total_cost
        
        Actor.log.debug(f"LLM call cost: ${total_cost:.4f} ({operation})")
    
    def track_search_call(self, api: str, operation: str = "search"):
        """
        Track a search API call.
        
        Args:
            api: API name (google, brave, bing)
            operation: Operation description
        """
        cost_key = f'{api}_search'
        cost_per_call = self.COSTS.get(cost_key, 0.001)  # Default
        
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'search_call',
            'api': api,
            'operation': operation,
            'cost': cost_per_call
        }
        
        self.costs.append(cost_entry)
        self.total_cost += cost_per_call
        
        Actor.log.debug(f"Search call cost: ${cost_per_call:.4f} ({api})")
    
    def track_content_fetch(self, url_count: int = 1):
        """
        Track content fetching operations.
        
        Args:
            url_count: Number of URLs fetched
        """
        cost_per_fetch = self.COSTS.get('content_fetch', 0.0001)
        total_cost = cost_per_fetch * url_count
        
        cost_entry = {
            'timestamp': datetime.now().isoformat(),
            'type': 'content_fetch',
            'url_count': url_count,
            'cost': total_cost
        }
        
        self.costs.append(cost_entry)
        self.total_cost += total_cost
    
    def get_cost_breakdown(self) -> Dict:
        """
        Get detailed cost breakdown.
        
        Returns:
            Dictionary with cost breakdown
        """
        breakdown = {
            'total_cost': self.total_cost,
            'total_operations': len(self.costs),
            'by_type': {},
            'by_operation': {},
            'llm_calls': 0,
            'search_calls': 0,
            'content_fetches': 0,
            'total_tokens_input': 0,
            'total_tokens_output': 0
        }
        
        for cost_entry in self.costs:
            cost_type = cost_entry.get('type', 'unknown')
            operation = cost_entry.get('operation', 'unknown')
            
            # Aggregate by type
            if cost_type not in breakdown['by_type']:
                breakdown['by_type'][cost_type] = {'count': 0, 'cost': 0.0}
            breakdown['by_type'][cost_type]['count'] += 1
            breakdown['by_type'][cost_type]['cost'] += cost_entry.get('total_cost', cost_entry.get('cost', 0))
            
            # Aggregate by operation
            if operation not in breakdown['by_operation']:
                breakdown['by_operation'][operation] = {'count': 0, 'cost': 0.0}
            breakdown['by_operation'][operation]['count'] += 1
            breakdown['by_operation'][operation]['cost'] += cost_entry.get('total_cost', cost_entry.get('cost', 0))
            
            # Count specific operations
            if cost_type == 'llm_call':
                breakdown['llm_calls'] += 1
                breakdown['total_tokens_input'] += cost_entry.get('input_tokens', 0)
                breakdown['total_tokens_output'] += cost_entry.get('output_tokens', 0)
            elif cost_type == 'search_call':
                breakdown['search_calls'] += 1
            elif cost_type == 'content_fetch':
                breakdown['content_fetches'] += cost_entry.get('url_count', 0)
        
        return breakdown
    
    def get_summary(self) -> Dict:
        """
        Get cost summary.
        
        Returns:
            Summary dictionary
        """
        breakdown = self.get_cost_breakdown()
        duration = (datetime.now() - self.start_time).total_seconds() / 60  # minutes
        
        return {
            'total_cost': round(self.total_cost, 4),
            'total_operations': breakdown['total_operations'],
            'duration_minutes': round(duration, 2),
            'cost_per_minute': round(self.total_cost / max(duration, 0.1), 4),
            'llm_calls': breakdown['llm_calls'],
            'search_calls': breakdown['search_calls'],
            'total_tokens': breakdown['total_tokens_input'] + breakdown['total_tokens_output']
        }
    
    def reset(self):
        """Reset cost tracker."""
        self.costs = []
        self.total_cost = 0.0
        self.start_time = datetime.now()


# Global cost tracker instance
_cost_tracker: Optional[CostTracker] = None


def get_cost_tracker() -> CostTracker:
    """Get global cost tracker instance."""
    global _cost_tracker
    if _cost_tracker is None:
        _cost_tracker = CostTracker()
    return _cost_tracker



