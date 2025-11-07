"""
Perspective Balancer - Enforces balanced perspectives in source selection.
Ensures diverse viewpoints are represented.
"""

from typing import Dict, List, Optional
from collections import Counter
from apify import Actor

from src.diversity.bias_detector import BiasDetector, create_bias_detector


class PerspectiveBalancer:
    """
    Enforces balanced perspectives in source selection.
    Ensures diverse viewpoints are represented.
    """
    
    def __init__(self):
        """Initialize perspective balancer."""
        self.bias_detector = create_bias_detector()
    
    def balance_sources(
        self,
        sources: List[Dict],
        target_distribution: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Balance sources to ensure diverse perspectives.
        
        Args:
            sources: List of source dictionaries
            target_distribution: Optional target distribution (e.g., {'left': 0.3, 'right': 0.3, 'center': 0.4})
            
        Returns:
            Balanced source list
        """
        if not sources:
            return sources
        
        # Detect bias for all sources
        bias_results = self.bias_detector.detect_bias_batch(sources)
        
        # Add bias info to sources
        for i, source in enumerate(sources):
            source['bias_info'] = bias_results[i]
        
        # Default target distribution
        if target_distribution is None:
            target_distribution = {
                'left': 0.3,
                'right': 0.3,
                'center': 0.4
            }
        
        # Calculate current distribution
        current_distribution = self._calculate_distribution(bias_results)
        
        # Rebalance sources
        balanced_sources = self._rebalance_sources(
            sources,
            current_distribution,
            target_distribution
        )
        
        return balanced_sources
    
    def _calculate_distribution(self, bias_results: List[Dict]) -> Dict[str, float]:
        """
        Calculate current perspective distribution.
        
        Args:
            bias_results: List of bias detection results
            
        Returns:
            Distribution dictionary
        """
        total = len(bias_results)
        if total == 0:
            return {'left': 0, 'right': 0, 'center': 0, 'unknown': 0}
        
        political_leanings = [r['political_leaning'] for r in bias_results]
        
        return {
            'left': political_leanings.count('left') / total,
            'right': political_leanings.count('right') / total,
            'center': political_leanings.count('center') / total,
            'unknown': political_leanings.count('unknown') / total
        }
    
    def _rebalance_sources(
        self,
        sources: List[Dict],
        current_distribution: Dict[str, float],
        target_distribution: Dict[str, float]
    ) -> List[Dict]:
        """
        Rebalance sources to match target distribution.
        
        Args:
            sources: List of sources
            current_distribution: Current distribution
            target_distribution: Target distribution
            
        Returns:
            Rebalanced source list
        """
        # Group sources by political leaning
        sources_by_leaning = {
            'left': [],
            'right': [],
            'center': [],
            'unknown': []
        }
        
        for source in sources:
            leaning = source.get('bias_info', {}).get('political_leaning', 'unknown')
            sources_by_leaning[leaning].append(source)
        
        # Calculate target counts
        total_sources = len(sources)
        target_counts = {
            key: int(total_sources * value)
            for key, value in target_distribution.items()
        }
        
        # Adjust for rounding
        total_target = sum(target_counts.values())
        if total_target < total_sources:
            # Distribute remainder to largest category
            remainder = total_sources - total_target
            max_key = max(target_counts.items(), key=lambda x: x[1])[0]
            target_counts[max_key] += remainder
        
        # Select sources to match target distribution
        balanced = []
        
        for leaning, target_count in target_counts.items():
            available = sources_by_leaning[leaning]
            # Take up to target_count, prioritizing by relevance score
            selected = sorted(
                available,
                key=lambda s: s.get('relevance_score', 0.5),
                reverse=True
            )[:target_count]
            balanced.extend(selected)
        
        # Add remaining sources if not enough in each category
        remaining = []
        for leaning, sources_list in sources_by_leaning.items():
            used = [s for s in sources_list if s in balanced]
            remaining.extend([s for s in sources_list if s not in used])
        
        # Fill remaining slots with highest relevance sources
        remaining_sorted = sorted(
            remaining,
            key=lambda s: s.get('relevance_score', 0.5),
            reverse=True
        )
        
        balanced.extend(remaining_sorted[:total_sources - len(balanced)])
        
        return balanced[:total_sources]
    
    def get_balance_report(self, sources: List[Dict]) -> Dict:
        """
        Get balance report for source set.
        
        Args:
            sources: List of sources
            
        Returns:
            Balance report dictionary
        """
        bias_results = self.bias_detector.detect_bias_batch(sources)
        distribution = self._calculate_distribution(bias_results)
        
        # Calculate balance score (higher = more balanced)
        balance_score = self._calculate_balance_score(distribution)
        
        recommendations = self._generate_recommendations(distribution)
        
        return {
            'balance_score': balance_score,
            'distribution': distribution,
            'recommendations': recommendations,
            'source_count': len(sources)
        }
    
    def _calculate_balance_score(self, distribution: Dict[str, float]) -> float:
        """
        Calculate balance score (0-100).
        
        Args:
            distribution: Perspective distribution
            
        Returns:
            Balance score
        """
        # Ideal distribution: equal left, right, center
        ideal = {'left': 0.33, 'right': 0.33, 'center': 0.34}
        
        # Calculate deviation from ideal
        deviation = sum(
            abs(distribution.get(key, 0) - ideal.get(key, 0))
            for key in ['left', 'right', 'center']
        )
        
        # Score decreases with deviation
        balance_score = max(0, 100 - (deviation * 200))
        
        return round(balance_score, 1)
    
    def _generate_recommendations(self, distribution: Dict[str, float]) -> List[str]:
        """
        Generate recommendations for better balance.
        
        Args:
            distribution: Current distribution
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        left_ratio = distribution.get('left', 0)
        right_ratio = distribution.get('right', 0)
        center_ratio = distribution.get('center', 0)
        
        if left_ratio > 0.5:
            recommendations.append("Add more right-leaning and center sources for balance.")
        elif right_ratio > 0.5:
            recommendations.append("Add more left-leaning and center sources for balance.")
        elif center_ratio < 0.2:
            recommendations.append("Add more center/neutral sources for balanced perspective.")
        
        if left_ratio < 0.1 and right_ratio < 0.1:
            recommendations.append("Consider adding sources with clear political perspectives.")
        
        return recommendations


def create_perspective_balancer() -> PerspectiveBalancer:
    """Create a perspective balancer instance."""
    return PerspectiveBalancer()



