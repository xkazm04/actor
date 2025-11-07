"""
Diversity Manager - Orchestrates diversity scoring, bias detection, and perspective balancing.
Main interface for source diversity features.
"""

from typing import Dict, List, Optional
from apify import Actor

from src.diversity.diversity_scorer import DiversityScorer, create_diversity_scorer
from src.diversity.bias_detector import BiasDetector, create_bias_detector
from src.diversity.perspective_balancer import PerspectiveBalancer, create_perspective_balancer


class DiversityManager:
    """
    Orchestrates diversity scoring, bias detection, and perspective balancing.
    Main interface for source diversity features.
    """
    
    def __init__(self):
        """Initialize diversity manager."""
        self.diversity_scorer = create_diversity_scorer()
        self.bias_detector = create_bias_detector()
        self.perspective_balancer = create_perspective_balancer()
    
    def analyze_diversity(
        self,
        sources: List[Dict],
        enable_balancing: bool = False,
        target_distribution: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze diversity of source set.
        
        Args:
            sources: List of source dictionaries
            enable_balancing: Whether to balance perspectives
            target_distribution: Optional target distribution for balancing
            
        Returns:
            Diversity analysis dictionary
        """
        if not sources:
            return {
                'diversity_score': 0,
                'bias_summary': {},
                'balance_report': {},
                'warnings': ['No sources provided'],
                'sources': []
            }
        
        # Calculate diversity score
        diversity_metrics = self.diversity_scorer.calculate_diversity_score(sources)
        
        # Detect bias
        bias_summary = self.bias_detector.get_bias_summary(sources)
        
        # Balance perspectives if enabled
        balanced_sources = sources
        balance_report = None
        if enable_balancing:
            balanced_sources = self.perspective_balancer.balance_sources(
                sources,
                target_distribution
            )
            balance_report = self.perspective_balancer.get_balance_report(balanced_sources)
        
        # Combine warnings
        all_warnings = diversity_metrics.get('warnings', [])
        all_warnings.extend(bias_summary.get('warnings', []))
        if balance_report:
            all_warnings.extend(balance_report.get('recommendations', []))
        
        return {
            'diversity_score': diversity_metrics.get('overall_score', 0),
            'diversity_metrics': diversity_metrics,
            'bias_summary': bias_summary,
            'balance_report': balance_report,
            'warnings': all_warnings,
            'sources': balanced_sources if enable_balancing else sources,
            'original_count': len(sources),
            'balanced_count': len(balanced_sources) if enable_balancing else len(sources)
        }
    
    def score_source_diversity(self, sources: List[Dict]) -> Dict:
        """
        Score source diversity.
        
        Args:
            sources: List of sources
            
        Returns:
            Diversity score dictionary
        """
        return self.diversity_scorer.calculate_diversity_score(sources)
    
    def detect_source_bias(self, sources: List[Dict]) -> Dict:
        """
        Detect bias in sources.
        
        Args:
            sources: List of sources
            
        Returns:
            Bias summary dictionary
        """
        return self.bias_detector.get_bias_summary(sources)
    
    def balance_perspectives(
        self,
        sources: List[Dict],
        target_distribution: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Balance perspectives in source set.
        
        Args:
            sources: List of sources
            target_distribution: Optional target distribution
            
        Returns:
            Balanced source list
        """
        return self.perspective_balancer.balance_sources(sources, target_distribution)


# Global diversity manager instance
_diversity_manager: Optional[DiversityManager] = None


def get_diversity_manager() -> DiversityManager:
    """Get global diversity manager instance."""
    global _diversity_manager
    if _diversity_manager is None:
        _diversity_manager = DiversityManager()
    return _diversity_manager



