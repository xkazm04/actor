"""
Diversity Scorer - Calculates source diversity metrics.
Measures geographic, temporal, perspective, source type, and domain diversity.
"""

from typing import Dict, List, Optional
from collections import Counter
from apify import Actor


class DiversityScorer:
    """
    Calculates diversity metrics for source sets.
    Measures multiple dimensions of diversity.
    """
    
    def __init__(self):
        """Initialize diversity scorer."""
        # Common TLDs for geographic diversity
        self.geographic_tlds = {
            '.com': 'us',
            '.co.uk': 'uk',
            '.de': 'de',
            '.fr': 'fr',
            '.jp': 'jp',
            '.cn': 'cn',
            '.au': 'au',
            '.ca': 'ca',
            '.in': 'in',
            '.br': 'br'
        }
        
        # Source type patterns
        self.source_type_patterns = {
            'news': ['news', 'reuters', 'bbc', 'cnn', 'guardian', 'nytimes'],
            'academic': ['.edu', 'arxiv', 'pubmed', 'jstor', 'scholar'],
            'blog': ['blog', 'medium', 'substack', 'wordpress'],
            'official': ['gov', '.org', 'official'],
            'social': ['twitter', 'facebook', 'linkedin', 'reddit']
        }
    
    def calculate_diversity_score(self, sources: List[Dict]) -> Dict:
        """
        Calculate overall diversity score for source set.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            Dictionary with diversity metrics and overall score
        """
        if not sources:
            return {
                'overall_score': 0,
                'geographic_diversity': 0,
                'temporal_diversity': 0,
                'perspective_diversity': 0,
                'source_type_diversity': 0,
                'domain_diversity': 0,
                'warnings': ['No sources provided']
            }
        
        metrics = {
            'geographic_diversity': self._calculate_geographic_diversity(sources),
            'temporal_diversity': self._calculate_temporal_diversity(sources),
            'perspective_diversity': self._calculate_perspective_diversity(sources),
            'source_type_diversity': self._calculate_source_type_diversity(sources),
            'domain_diversity': self._calculate_domain_diversity(sources)
        }
        
        # Calculate weighted overall score
        weights = {
            'geographic_diversity': 0.15,
            'temporal_diversity': 0.15,
            'perspective_diversity': 0.25,
            'source_type_diversity': 0.20,
            'domain_diversity': 0.25
        }
        
        overall_score = sum(
            metrics[key] * weights[key]
            for key in weights
        )
        
        # Generate warnings if diversity is low
        warnings = []
        if overall_score < 70:
            warnings.append(f"Low diversity score ({overall_score:.1f}/100). Consider adding more diverse sources.")
        
        if metrics['domain_diversity'] < 60:
            warnings.append("Too many sources from same domain. Diversify sources.")
        
        if metrics['perspective_diversity'] < 50:
            warnings.append("Limited perspective diversity. Include different viewpoints.")
        
        return {
            'overall_score': round(overall_score, 1),
            **metrics,
            'warnings': warnings,
            'source_count': len(sources)
        }
    
    def _calculate_geographic_diversity(self, sources: List[Dict]) -> float:
        """
        Calculate geographic diversity score.
        
        Args:
            sources: List of sources
            
        Returns:
            Score 0-100
        """
        if not sources:
            return 0
        
        regions = []
        for source in sources:
            url = source.get('url', '').lower()
            domain = source.get('domain', '').lower()
            
            # Extract TLD
            for tld, region in self.geographic_tlds.items():
                if tld in url or tld in domain:
                    regions.append(region)
                    break
        
        if not regions:
            return 50  # Default if can't determine
        
        unique_regions = len(set(regions))
        total_sources = len(sources)
        
        # Score based on unique regions vs total sources
        diversity_ratio = unique_regions / min(total_sources, 10)  # Cap at 10 regions
        return min(diversity_ratio * 100, 100)
    
    def _calculate_temporal_diversity(self, sources: List[Dict]) -> float:
        """
        Calculate temporal diversity score (mix of recent and historical).
        
        Args:
            sources: List of sources
            
        Returns:
            Score 0-100
        """
        if not sources:
            return 0
        
        # Extract years from URLs/titles (simplified)
        years = []
        for source in sources:
            url = source.get('url', '')
            title = source.get('title', '')
            snippet = source.get('snippet', '')
            
            # Look for 4-digit years
            import re
            year_matches = re.findall(r'\b(19|20)\d{2}\b', url + title + snippet)
            if year_matches:
                years.append(int(year_matches[0]))
        
        if not years:
            return 50  # Default if can't determine
        
        # Check spread of years
        if len(years) < 2:
            return 30
        
        year_range = max(years) - min(years)
        unique_years = len(set(years))
        
        # Score based on year range and unique years
        if year_range > 10:
            return min(80 + (unique_years / len(years)) * 20, 100)
        elif year_range > 5:
            return min(60 + (unique_years / len(years)) * 20, 100)
        else:
            return min(40 + (unique_years / len(years)) * 20, 100)
    
    def _calculate_perspective_diversity(self, sources: List[Dict]) -> float:
        """
        Calculate perspective diversity score.
        
        Args:
            sources: List of sources
            
        Returns:
            Score 0-100
        """
        if not sources:
            return 0
        
        # This is a simplified version - would use bias detector in production
        domains = [s.get('domain', '') for s in sources]
        unique_domains = len(set(domains))
        total_sources = len(sources)
        
        # More unique domains = more diverse perspectives
        diversity_ratio = unique_domains / total_sources if total_sources > 0 else 0
        return min(diversity_ratio * 100, 100)
    
    def _calculate_source_type_diversity(self, sources: List[Dict]) -> float:
        """
        Calculate source type diversity score.
        
        Args:
            sources: List of sources
            
        Returns:
            Score 0-100
        """
        if not sources:
            return 0
        
        source_types = []
        for source in sources:
            url = source.get('url', '').lower()
            domain = source.get('domain', '').lower()
            
            for source_type, patterns in self.source_type_patterns.items():
                if any(pattern in url or pattern in domain for pattern in patterns):
                    source_types.append(source_type)
                    break
        
        if not source_types:
            return 50  # Default
        
        unique_types = len(set(source_types))
        total_sources = len(sources)
        
        # Score based on unique types
        diversity_ratio = unique_types / min(total_sources, 5)  # Cap at 5 types
        return min(diversity_ratio * 100, 100)
    
    def _calculate_domain_diversity(self, sources: List[Dict]) -> float:
        """
        Calculate domain diversity score (not too many from same domain).
        
        Args:
            sources: List of sources
            
        Returns:
            Score 0-100
        """
        if not sources:
            return 0
        
        domains = [s.get('domain', '') for s in sources if s.get('domain')]
        if not domains:
            return 50
        
        domain_counts = Counter(domains)
        total_sources = len(domains)
        
        # Calculate entropy-like score
        # Lower score if one domain dominates
        max_count = max(domain_counts.values()) if domain_counts else 0
        max_ratio = max_count / total_sources if total_sources > 0 else 0
        
        # Score decreases if one domain has > 30% of sources
        if max_ratio > 0.5:
            return 30
        elif max_ratio > 0.3:
            return 60
        else:
            unique_domains = len(set(domains))
            return min(80 + (unique_domains / total_sources) * 20, 100)


def create_diversity_scorer() -> DiversityScorer:
    """Create a diversity scorer instance."""
    return DiversityScorer()



