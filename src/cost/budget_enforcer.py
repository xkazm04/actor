"""
Budget Enforcer - Enforces budget limits and stops execution if exceeded.
"""

from typing import Optional
from apify import Actor

from src.cost.cost_tracker import CostTracker, get_cost_tracker


class BudgetEnforcer:
    """
    Enforces budget limits during research execution.
    Stops execution if budget is exceeded.
    """
    
    def __init__(self, budget_limit: Optional[float] = None, cost_tracker: Optional[CostTracker] = None):
        """
        Initialize budget enforcer.
        
        Args:
            budget_limit: Maximum budget in USD (None = no limit)
            cost_tracker: Cost tracker instance (None = use global)
        """
        self.budget_limit = budget_limit
        self.cost_tracker = cost_tracker or get_cost_tracker()
        self.enforced = False
    
    def check_budget(self, operation: str = "check") -> bool:
        """
        Check if budget is still available.
        
        Args:
            operation: Operation description
            
        Returns:
            True if budget available, False if exceeded
        """
        if self.budget_limit is None:
            return True
        
        current_cost = self.cost_tracker.total_cost
        
        if current_cost >= self.budget_limit:
            if not self.enforced:
                Actor.log.warning(
                    f"Budget limit exceeded: ${current_cost:.4f} >= ${self.budget_limit:.4f}. "
                    f"Stopping execution."
                )
                self.enforced = True
            return False
        
        # Warn if approaching limit
        if current_cost >= self.budget_limit * 0.9:
            Actor.log.warning(
                f"Approaching budget limit: ${current_cost:.4f} / ${self.budget_limit:.4f} "
                f"({(current_cost / self.budget_limit * 100):.1f}%)"
            )
        
        return True
    
    def get_remaining_budget(self) -> Optional[float]:
        """
        Get remaining budget.
        
        Returns:
            Remaining budget in USD, or None if no limit
        """
        if self.budget_limit is None:
            return None
        
        remaining = self.budget_limit - self.cost_tracker.total_cost
        return max(remaining, 0.0)
    
    def get_budget_usage_percentage(self) -> Optional[float]:
        """
        Get budget usage percentage.
        
        Returns:
            Usage percentage (0-100), or None if no limit
        """
        if self.budget_limit is None:
            return None
        
        return min((self.cost_tracker.total_cost / self.budget_limit) * 100, 100.0)
    
    def is_enforced(self) -> bool:
        """Check if budget has been enforced (exceeded)."""
        return self.enforced


def create_budget_enforcer(budget_limit: Optional[float] = None) -> BudgetEnforcer:
    """
    Create a budget enforcer.
    
    Args:
        budget_limit: Maximum budget in USD
        
    Returns:
        BudgetEnforcer instance
    """
    return BudgetEnforcer(budget_limit)



