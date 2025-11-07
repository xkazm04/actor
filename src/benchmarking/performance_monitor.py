"""
Performance Monitor - Tracks response times, costs, and performance metrics.
Monitors Actor performance and compares against baselines.
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta
from apify import Actor


class PerformanceMonitor:
    """
    Monitors Actor performance metrics.
    Tracks response times, costs, and compares against baselines.
    """
    
    def __init__(self):
        """Initialize performance monitor."""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.milestones: List[Dict] = []
    
    def start(self):
        """Start performance monitoring."""
        self.start_time = datetime.now()
        self.milestones = []
        self._add_milestone("start", "Research started")
    
    def end(self):
        """End performance monitoring."""
        self.end_time = datetime.now()
        self._add_milestone("end", "Research completed")
    
    def _add_milestone(self, name: str, description: str):
        """Add a performance milestone."""
        milestone = {
            'name': name,
            'description': description,
            'timestamp': datetime.now().isoformat(),
            'elapsed_seconds': (datetime.now() - self.start_time).total_seconds() if self.start_time else 0.0
        }
        self.milestones.append(milestone)
    
    def add_milestone(self, name: str, description: str):
        """Add a custom milestone."""
        self._add_milestone(name, description)
    
    def get_total_time(self) -> float:
        """
        Get total execution time in seconds.
        
        Returns:
            Total time in seconds
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return 0.0
    
    def get_milestone_time(self, milestone_name: str) -> Optional[float]:
        """
        Get time for a specific milestone.
        
        Args:
            milestone_name: Name of milestone
            
        Returns:
            Time in seconds or None
        """
        for milestone in self.milestones:
            if milestone['name'] == milestone_name:
                return milestone['elapsed_seconds']
        return None
    
    def calculate_speed_score(
        self,
        complexity: str = "medium",
        target_times: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate speed score based on complexity.
        
        Args:
            complexity: Complexity level (low, medium, high)
            target_times: Optional target times for each complexity
            
        Returns:
            Speed metrics dictionary
        """
        if target_times is None:
            target_times = {
                'low': 60,      # 1 minute
                'medium': 300,  # 5 minutes
                'high': 900     # 15 minutes
            }
        
        total_time = self.get_total_time()
        target_time = target_times.get(complexity, target_times['medium'])
        
        # Score: 1.0 if within target, decreases linearly
        if total_time <= target_time:
            speed_score = 1.0
        else:
            # Penalty for exceeding target
            excess = total_time - target_time
            penalty = min(excess / target_time, 0.5)  # Max 50% penalty
            speed_score = max(0.5, 1.0 - penalty)
        
        return {
            'score': speed_score,
            'total_time_seconds': total_time,
            'target_time_seconds': target_time,
            'complexity': complexity,
            'percentage': speed_score * 100,
            'within_target': total_time <= target_time
        }
    
    def get_performance_summary(
        self,
        cost_summary: Optional[Dict] = None,
        complexity: str = "medium"
    ) -> Dict:
        """
        Get comprehensive performance summary.
        
        Args:
            cost_summary: Optional cost summary
            complexity: Complexity level
            
        Returns:
            Performance summary dictionary
        """
        total_time = self.get_total_time()
        speed_metrics = self.calculate_speed_score(complexity)
        
        summary = {
            'timestamp': datetime.now().isoformat(),
            'total_time_seconds': total_time,
            'total_time_formatted': str(timedelta(seconds=int(total_time))),
            'speed_score': speed_metrics,
            'milestones': self.milestones,
            'milestone_count': len(self.milestones)
        }
        
        if cost_summary:
            summary['cost'] = cost_summary
        
        return summary
    
    def compare_with_baseline(
        self,
        baseline_time: float,
        baseline_cost: Optional[float] = None,
        current_cost: Optional[float] = None
    ) -> Dict:
        """
        Compare current performance with baseline.
        
        Args:
            baseline_time: Baseline execution time in seconds
            baseline_cost: Optional baseline cost
            current_cost: Optional current cost
            
        Returns:
            Comparison metrics dictionary
        """
        current_time = self.get_total_time()
        time_ratio = current_time / baseline_time if baseline_time > 0 else 0.0
        time_difference = current_time - baseline_time
        
        comparison = {
            'baseline_time_seconds': baseline_time,
            'current_time_seconds': current_time,
            'time_ratio': time_ratio,
            'time_difference_seconds': time_difference,
            'time_percentage': time_ratio * 100,
            'is_faster': current_time < baseline_time,
            'is_within_20_percent': 0.8 <= time_ratio <= 1.2
        }
        
        if baseline_cost is not None and current_cost is not None:
            cost_ratio = current_cost / baseline_cost if baseline_cost > 0 else 0.0
            cost_difference = current_cost - baseline_cost
            
            comparison['baseline_cost'] = baseline_cost
            comparison['current_cost'] = current_cost
            comparison['cost_ratio'] = cost_ratio
            comparison['cost_difference'] = cost_difference
            comparison['cost_percentage'] = cost_ratio * 100
            comparison['is_cheaper'] = current_cost < baseline_cost
        
        return comparison


def create_performance_monitor() -> PerformanceMonitor:
    """Create a performance monitor instance."""
    return PerformanceMonitor()



