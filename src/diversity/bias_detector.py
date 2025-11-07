"""
Bias Detector - Detects and labels bias in sources.
Identifies political leaning, conflicts of interest, sponsored content, etc.
"""

from typing import Dict, List, Optional
from apify import Actor


class BiasDetector:
    """
    Detects bias and labels sources.
    Identifies political leaning, conflicts of interest, etc.
    """
    
    def __init__(self):
        """Initialize bias detector."""
        # Political leaning indicators (simplified)
        self.left_indicators = [
            'progressive', 'liberal', 'democrat', 'left-wing',
            'theguardian', 'nytimes', 'washingtonpost', 'cnn'
        ]
        
        self.right_indicators = [
            'conservative', 'republican', 'right-wing',
            'foxnews', 'breitbart', 'wsj', 'nationalreview'
        ]
        
        self.center_indicators = [
            'reuters', 'ap', 'bbc', 'pbs', 'npr', 'factcheck'
        ]
        
        # Sponsored/promotional indicators
        self.sponsored_indicators = [
            'sponsored', 'advertisement', 'ad', 'promoted',
            'paid', 'affiliate', 'partner'
        ]
        
        # Sensationalism indicators
        self.sensationalism_indicators = [
            'shocking', 'you won\'t believe', 'this will blow your mind',
            'breaking', 'urgent', 'exclusive', 'revealed'
        ]
    
    def detect_bias(self, source: Dict) -> Dict:
        """
        Detect bias in a source.
        
        Args:
            source: Source dictionary
            
        Returns:
            Bias detection results
        """
        url = source.get('url', '').lower()
        title = source.get('title', '').lower()
        snippet = source.get('snippet', '').lower()
        domain = source.get('domain', '').lower()
        
        text = f"{url} {title} {snippet} {domain}"
        
        bias_info = {
            'political_leaning': self._detect_political_leaning(text, domain),
            'is_sponsored': self._detect_sponsored(text),
            'is_sensationalist': self._detect_sensationalism(title, snippet),
            'content_type': self._detect_content_type(text),
            'confidence': 0.5
        }
        
        # Calculate confidence based on indicators found
        indicators_found = sum([
            1 if bias_info['political_leaning'] != 'unknown' else 0,
            1 if bias_info['is_sponsored'] else 0,
            1 if bias_info['is_sensationalist'] else 0,
            1 if bias_info['content_type'] != 'unknown' else 0
        ])
        
        bias_info['confidence'] = min(indicators_found / 4, 1.0)
        
        return bias_info
    
    def _detect_political_leaning(self, text: str, domain: str) -> str:
        """
        Detect political leaning.
        
        Args:
            text: Combined text from source
            domain: Source domain
            
        Returns:
            'left', 'right', 'center', or 'unknown'
        """
        left_score = sum(1 for indicator in self.left_indicators if indicator in text)
        right_score = sum(1 for indicator in self.right_indicators if indicator in text)
        center_score = sum(1 for indicator in self.center_indicators if indicator in text)
        
        if center_score > 0 and center_score >= max(left_score, right_score):
            return 'center'
        elif left_score > right_score:
            return 'left'
        elif right_score > left_score:
            return 'right'
        else:
            return 'unknown'
    
    def _detect_sponsored(self, text: str) -> bool:
        """
        Detect sponsored/promotional content.
        
        Args:
            text: Combined text from source
            
        Returns:
            True if sponsored
        """
        return any(indicator in text for indicator in self.sponsored_indicators)
    
    def _detect_sensationalism(self, title: str, snippet: str) -> bool:
        """
        Detect sensationalism/clickbait.
        
        Args:
            title: Source title
            snippet: Source snippet
            
        Returns:
            True if sensationalist
        """
        combined = f"{title} {snippet}"
        return any(indicator in combined for indicator in self.sensationalism_indicators)
    
    def _detect_content_type(self, text: str) -> str:
        """
        Detect content type (fact vs opinion).
        
        Args:
            text: Combined text from source
            
        Returns:
            'fact', 'opinion', or 'unknown'
        """
        opinion_indicators = ['opinion', 'editorial', 'commentary', 'viewpoint', 'analysis']
        fact_indicators = ['report', 'study', 'research', 'data', 'statistics']
        
        opinion_score = sum(1 for indicator in opinion_indicators if indicator in text)
        fact_score = sum(1 for indicator in fact_indicators if indicator in text)
        
        if fact_score > opinion_score:
            return 'fact'
        elif opinion_score > fact_score:
            return 'opinion'
        else:
            return 'unknown'
    
    def detect_bias_batch(self, sources: List[Dict]) -> List[Dict]:
        """
        Detect bias for multiple sources.
        
        Args:
            sources: List of source dictionaries
            
        Returns:
            List of bias detection results
        """
        return [self.detect_bias(source) for source in sources]
    
    def get_bias_summary(self, sources: List[Dict]) -> Dict:
        """
        Get bias summary for source set.
        
        Args:
            sources: List of sources
            
        Returns:
            Bias summary dictionary
        """
        bias_results = self.detect_bias_batch(sources)
        
        political_leanings = [r['political_leaning'] for r in bias_results]
        sponsored_count = sum(1 for r in bias_results if r['is_sponsored'])
        sensationalist_count = sum(1 for r in bias_results if r['is_sensationalist'])
        content_types = [r['content_type'] for r in bias_results]
        
        return {
            'total_sources': len(sources),
            'political_distribution': {
                'left': political_leanings.count('left'),
                'right': political_leanings.count('right'),
                'center': political_leanings.count('center'),
                'unknown': political_leanings.count('unknown')
            },
            'sponsored_count': sponsored_count,
            'sensationalist_count': sensationalist_count,
            'content_type_distribution': {
                'fact': content_types.count('fact'),
                'opinion': content_types.count('opinion'),
                'unknown': content_types.count('unknown')
            },
            'warnings': self._generate_bias_warnings(bias_results)
        }
    
    def _generate_bias_warnings(self, bias_results: List[Dict]) -> List[str]:
        """
        Generate warnings based on bias detection.
        
        Args:
            bias_results: List of bias detection results
            
        Returns:
            List of warning messages
        """
        warnings = []
        
        political_leanings = [r['political_leaning'] for r in bias_results]
        left_count = political_leanings.count('left')
        right_count = political_leanings.count('right')
        center_count = political_leanings.count('center')
        total = len(political_leanings)
        
        if total > 0:
            left_ratio = left_count / total
            right_ratio = right_count / total
            
            if left_ratio > 0.6:
                warnings.append("Sources heavily skewed toward left-leaning perspectives.")
            elif right_ratio > 0.6:
                warnings.append("Sources heavily skewed toward right-leaning perspectives.")
            elif center_count < total * 0.2:
                warnings.append("Limited center/neutral sources. Consider adding more balanced sources.")
        
        sponsored_count = sum(1 for r in bias_results if r['is_sponsored'])
        if sponsored_count > len(bias_results) * 0.2:
            warnings.append(f"High number of sponsored sources ({sponsored_count}). Verify independence.")
        
        sensationalist_count = sum(1 for r in bias_results if r['is_sensationalist'])
        if sensationalist_count > len(bias_results) * 0.3:
            warnings.append(f"Many sensationalist sources ({sensationalist_count}). Verify factual accuracy.")
        
        return warnings


def create_bias_detector() -> BiasDetector:
    """Create a bias detector instance."""
    return BiasDetector()



