"""
Unit tests for Phase 5: Tiered Research Modes & Cost Optimization
"""

import pytest
from src.modes.research_modes import ResearchModes, ResearchModeConfig
from src.cost.cost_tracker import CostTracker
from src.cost.budget_enforcer import BudgetEnforcer


class TestResearchModes:
    """Test research modes."""
    
    def test_get_mode_quick(self):
        """Test getting quick mode."""
        mode = ResearchModes.get_mode("quick")
        assert mode is not None
        assert mode.name == "quick"
        assert mode.max_searches == 10
    
    def test_get_mode_standard(self):
        """Test getting standard mode."""
        mode = ResearchModes.get_mode("standard")
        assert mode is not None
        assert mode.name == "standard"
        assert mode.max_searches == 30
    
    def test_get_mode_deep(self):
        """Test getting deep mode."""
        mode = ResearchModes.get_mode("deep")
        assert mode is not None
        assert mode.name == "deep"
        assert mode.max_searches == 100
    
    def test_get_mode_invalid(self):
        """Test getting invalid mode."""
        mode = ResearchModes.get_mode("invalid")
        assert mode is None
    
    def test_get_all_modes(self):
        """Test getting all modes."""
        modes = ResearchModes.get_all_modes()
        assert "quick" in modes
        assert "standard" in modes
        assert "deep" in modes
    
    def test_apply_mode_to_input(self):
        """Test applying mode to input."""
        input_data = {"query": "test"}
        updated = ResearchModes.apply_mode_to_input("quick", input_data)
        assert updated['max_searches'] == 10
        assert updated['research_mode'] == "quick"


class TestCostTracker:
    """Test cost tracker."""
    
    def test_tracker_initialization(self):
        """Test tracker initialization."""
        tracker = CostTracker()
        assert tracker.total_cost == 0.0
        assert len(tracker.costs) == 0
    
    def test_track_llm_call(self):
        """Test tracking LLM call."""
        tracker = CostTracker()
        tracker.track_llm_call("claude-sonnet-4", 1000, 500, "test")
        assert tracker.total_cost > 0
        assert len(tracker.costs) == 1
    
    def test_track_search_call(self):
        """Test tracking search call."""
        tracker = CostTracker()
        tracker.track_search_call("google", "search")
        assert tracker.total_cost > 0
        assert len(tracker.costs) == 1
    
    def test_track_content_fetch(self):
        """Test tracking content fetch."""
        tracker = CostTracker()
        tracker.track_content_fetch(5)
        assert tracker.total_cost > 0
    
    def test_get_cost_breakdown(self):
        """Test getting cost breakdown."""
        tracker = CostTracker()
        tracker.track_llm_call("claude-sonnet-4", 1000, 500)
        tracker.track_search_call("google")
        
        breakdown = tracker.get_cost_breakdown()
        assert breakdown['total_cost'] > 0
        assert 'by_type' in breakdown
        assert 'llm_calls' in breakdown
        assert breakdown['llm_calls'] == 1
        assert breakdown['search_calls'] == 1
    
    def test_get_summary(self):
        """Test getting summary."""
        tracker = CostTracker()
        tracker.track_llm_call("claude-sonnet-4", 1000, 500)
        
        summary = tracker.get_summary()
        assert 'total_cost' in summary
        assert 'total_operations' in summary
        assert 'duration_minutes' in summary


class TestBudgetEnforcer:
    """Test budget enforcer."""
    
    def test_enforcer_initialization(self):
        """Test enforcer initialization."""
        enforcer = BudgetEnforcer(budget_limit=1.0)
        assert enforcer.budget_limit == 1.0
        assert not enforcer.is_enforced()
    
    def test_check_budget_within_limit(self):
        """Test checking budget within limit."""
        tracker = CostTracker()
        enforcer = BudgetEnforcer(budget_limit=1.0, cost_tracker=tracker)
        
        assert enforcer.check_budget() == True
        assert not enforcer.is_enforced()
    
    def test_check_budget_exceeded(self):
        """Test checking budget when exceeded."""
        tracker = CostTracker()
        tracker.track_llm_call("claude-sonnet-4", 1000000, 500000)  # High cost
        
        enforcer = BudgetEnforcer(budget_limit=0.01, cost_tracker=tracker)
        assert enforcer.check_budget() == False
        assert enforcer.is_enforced()
    
    def test_get_remaining_budget(self):
        """Test getting remaining budget."""
        tracker = CostTracker()
        tracker.track_llm_call("claude-sonnet-4", 1000, 500)
        
        enforcer = BudgetEnforcer(budget_limit=1.0, cost_tracker=tracker)
        remaining = enforcer.get_remaining_budget()
        assert remaining is not None
        assert remaining < 1.0
    
    def test_get_budget_usage_percentage(self):
        """Test getting budget usage percentage."""
        tracker = CostTracker()
        enforcer = BudgetEnforcer(budget_limit=1.0, cost_tracker=tracker)
        
        percentage = enforcer.get_budget_usage_percentage()
        assert percentage is not None
        assert 0 <= percentage <= 100


class TestIntegration:
    """Integration tests for Phase 5."""
    
    def test_mode_cost_estimation(self):
        """Test mode cost estimation."""
        quick_mode = ResearchModes.QUICK
        assert quick_mode.estimated_cost_min <= quick_mode.estimated_cost_max
        
        standard_mode = ResearchModes.STANDARD
        assert standard_mode.estimated_cost_min <= standard_mode.estimated_cost_max
        
        deep_mode = ResearchModes.DEEP
        assert deep_mode.estimated_cost_min <= deep_mode.estimated_cost_max
        
        # Deep should cost more than quick
        assert deep_mode.estimated_cost_min > quick_mode.estimated_cost_max
    
    def test_mode_time_estimation(self):
        """Test mode time estimation."""
        quick_mode = ResearchModes.QUICK
        assert quick_mode.estimated_time_min <= quick_mode.estimated_time_max
        
        deep_mode = ResearchModes.DEEP
        assert deep_mode.estimated_time_min <= deep_mode.estimated_time_max
        
        # Deep should take longer than quick
        assert deep_mode.estimated_time_min > quick_mode.estimated_time_max



