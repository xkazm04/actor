"""
Similarity Detector - Detects similar queries using embeddings.
Enables reuse of cached research for similar queries.
"""

import hashlib
from typing import List, Dict, Optional, Tuple
from apify import Actor


class SimilarityDetector:
    """
    Detects similar queries to enable cache reuse.
    Uses simple keyword-based similarity (can be enhanced with embeddings).
    """
    
    def __init__(self, similarity_threshold: float = 0.7):
        """
        Initialize similarity detector.
        
        Args:
            similarity_threshold: Minimum similarity score (0-1) to consider queries similar
        """
        self.similarity_threshold = similarity_threshold
    
    def calculate_similarity(self, query1: str, query2: str) -> float:
        """
        Calculate similarity between two queries.
        Uses Jaccard similarity on word sets.
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            Similarity score (0-1)
        """
        # Normalize queries
        words1 = set(query1.lower().split())
        words2 = set(query2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        # Remove common stop words for better matching
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
        words1 = words1 - stop_words
        words2 = words2 - stop_words
        
        if not words1 or not words2:
            return 0.0
        
        # Calculate Jaccard similarity
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        similarity = intersection / union
        return similarity
    
    def find_similar_queries(
        self,
        query: str,
        cached_queries: List[str],
        max_results: int = 5
    ) -> List[Tuple[str, float]]:
        """
        Find similar queries from cached queries.
        
        Args:
            query: Query to find similarities for
            cached_queries: List of cached query strings
            max_results: Maximum number of results to return
            
        Returns:
            List of (query, similarity_score) tuples, sorted by similarity
        """
        similarities = []
        
        for cached_query in cached_queries:
            similarity = self.calculate_similarity(query, cached_query)
            if similarity >= self.similarity_threshold:
                similarities.append((cached_query, similarity))
        
        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        return similarities[:max_results]
    
    def are_similar(self, query1: str, query2: str) -> bool:
        """
        Check if two queries are similar.
        
        Args:
            query1: First query
            query2: Second query
            
        Returns:
            True if similar, False otherwise
        """
        similarity = self.calculate_similarity(query1, query2)
        return similarity >= self.similarity_threshold
    
    def extract_key_terms(self, query: str) -> List[str]:
        """
        Extract key terms from query for matching.
        
        Args:
            query: Query string
            
        Returns:
            List of key terms
        """
        words = query.lower().split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'when', 'where'}
        key_terms = [w for w in words if w not in stop_words and len(w) > 2]
        return key_terms
    
    def generate_query_hash(self, query: str) -> str:
        """
        Generate hash for query (for exact matching).
        
        Args:
            query: Query string
            
        Returns:
            Hash string
        """
        normalized = query.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()


def detect_similar_queries(
    query: str,
    cached_queries: List[str],
    threshold: float = 0.7
) -> List[Tuple[str, float]]:
    """
    Convenience function to detect similar queries.
    
    Args:
        query: Query to find similarities for
        cached_queries: List of cached queries
        threshold: Similarity threshold
        
    Returns:
        List of similar queries with scores
    """
    detector = SimilarityDetector(similarity_threshold=threshold)
    return detector.find_similar_queries(query, cached_queries)



