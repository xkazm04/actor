"""
Theme Detector - Automatically detects research theme from query.
Analyzes query keywords to determine if research is academic, news, business, or technical.
"""

from typing import Dict, Optional, Tuple
from enum import Enum
from apify import Actor


class ResearchTheme(Enum):
    """Research theme types."""
    ACADEMIC = "academic"
    NEWS = "news"
    BUSINESS = "business"
    TECHNICAL = "technical"
    GENERAL = "general"


class ThemeDetector:
    """
    Detects research theme from query using keyword analysis.
    Determines if research is academic, news, business, or technical.
    """
    
    def __init__(self):
        """Initialize theme detector."""
        # Academic keywords
        self.academic_keywords = [
            'study', 'research', 'paper', 'journal', 'academic', 'scholar',
            'thesis', 'dissertation', 'peer-reviewed', 'publication',
            'literature review', 'methodology', 'hypothesis', 'experiment',
            'findings', 'conclusion', 'citation', 'reference'
        ]
        
        # News keywords
        self.news_keywords = [
            'breaking', 'latest', 'today', 'happened', 'recent', 'update',
            'news', 'report', 'announcement', 'event', 'incident',
            'developments', 'current', 'ongoing', 'just', 'now'
        ]
        
        # Business keywords
        self.business_keywords = [
            'market', 'revenue', 'competitive', 'roi', 'profit', 'sales',
            'business', 'company', 'industry', 'financial', 'investment',
            'strategy', 'growth', 'market share', 'customer', 'product',
            'service', 'pricing', 'competitor', 'analysis'
        ]
        
        # Technical keywords
        self.technical_keywords = [
            'implementation', 'code', 'api', 'framework', 'library',
            'technical', 'developer', 'programming', 'software', 'system',
            'architecture', 'algorithm', 'database', 'server', 'deployment',
            'configuration', 'documentation', 'tutorial', 'how to'
        ]
    
    def detect_theme(self, query: str) -> Tuple[ResearchTheme, float]:
        """
        Detect research theme from query.
        
        Args:
            query: Research query
            
        Returns:
            Tuple of (detected_theme, confidence_score)
        """
        query_lower = query.lower()
        
        # Count keyword matches for each theme
        academic_score = sum(1 for keyword in self.academic_keywords if keyword in query_lower)
        news_score = sum(1 for keyword in self.news_keywords if keyword in query_lower)
        business_score = sum(1 for keyword in self.business_keywords if keyword in query_lower)
        technical_score = sum(1 for keyword in self.technical_keywords if keyword in query_lower)
        
        # Calculate confidence scores
        total_keywords = len(query_lower.split())
        scores = {
            ResearchTheme.ACADEMIC: academic_score / max(total_keywords, 1),
            ResearchTheme.NEWS: news_score / max(total_keywords, 1),
            ResearchTheme.BUSINESS: business_score / max(total_keywords, 1),
            ResearchTheme.TECHNICAL: technical_score / max(total_keywords, 1)
        }
        
        # Find theme with highest score
        max_score = max(scores.values())
        detected_theme = max(scores.items(), key=lambda x: x[1])[0]
        
        # If no clear theme, use general
        if max_score < 0.1:
            detected_theme = ResearchTheme.GENERAL
            confidence = 0.5
        else:
            confidence = min(max_score * 2, 1.0)  # Scale confidence
        
        return detected_theme, confidence
    
    def detect_with_explanation(self, query: str) -> Dict:
        """
        Detect theme with explanation.
        
        Args:
            query: Research query
            
        Returns:
            Dictionary with theme, confidence, and explanation
        """
        theme, confidence = self.detect_theme(query)
        
        query_lower = query.lower()
        matched_keywords = []
        
        # Find matched keywords
        all_keywords = {
            ResearchTheme.ACADEMIC: self.academic_keywords,
            ResearchTheme.NEWS: self.news_keywords,
            ResearchTheme.BUSINESS: self.business_keywords,
            ResearchTheme.TECHNICAL: self.technical_keywords
        }
        
        for keyword in all_keywords.get(theme, []):
            if keyword in query_lower:
                matched_keywords.append(keyword)
        
        explanation = f"Detected {theme.value} theme based on keywords: {', '.join(matched_keywords[:5])}"
        
        return {
            'theme': theme.value,
            'confidence': confidence,
            'matched_keywords': matched_keywords[:10],
            'explanation': explanation
        }


def create_theme_detector() -> ThemeDetector:
    """Create a theme detector instance."""
    return ThemeDetector()



