"""
Test Suite - Comprehensive test queries for benchmarking.
Includes diverse queries covering different domains and complexity levels.
"""

# Test queries for benchmarking
TEST_QUERIES = [
    # Academic queries
    "What are the latest developments in quantum computing?",
    "How does machine learning work in neural networks?",
    "What is the current state of climate change research?",
    
    # News queries
    "What are the latest developments in AI regulation?",
    "What happened in the tech industry this week?",
    "What are the current global economic trends?",
    
    # Technical queries
    "How to implement authentication in Python Flask?",
    "What are best practices for Kubernetes deployment?",
    "How does React hooks work?",
    
    # Business queries
    "What is the market outlook for electric vehicles?",
    "How are tech companies performing this quarter?",
    "What are the latest trends in startup funding?",
    
    # Complex queries
    "What are the ethical implications of artificial intelligence in healthcare?",
    "How does quantum computing differ from classical computing?",
    "What are the environmental impacts of cryptocurrency mining?",
    
    # Niche queries
    "What is the history of the Byzantine Empire?",
    "How do black holes form and evolve?",
    "What are the latest developments in CRISPR gene editing?",
    
    # Ambiguous queries
    "Tell me about Python",
    "What is AI?",
    "Explain blockchain",
    
    # Multi-part queries
    "What are the causes, effects, and solutions for climate change?",
    "How does the immune system work and what are common disorders?",
    "What are the benefits and risks of social media?",
]

# Edge case queries
EDGE_CASE_QUERIES = [
    "",  # Empty query (should be handled)
    "a" * 2000,  # Very long query
    "???",  # Special characters only
    "123456789",  # Numbers only
    "What is the meaning of life?",  # Philosophical
    "How to make a sandwich?",  # Simple/trivial
]

# Domain-specific query sets
ACADEMIC_QUERIES = [
    q for q in TEST_QUERIES if any(keyword in q.lower() for keyword in ['research', 'study', 'development', 'quantum', 'machine learning', 'climate'])
]

NEWS_QUERIES = [
    q for q in TEST_QUERIES if any(keyword in q.lower() for keyword in ['latest', 'current', 'this week', 'trends', 'regulation'])
]

TECHNICAL_QUERIES = [
    q for q in TEST_QUERIES if any(keyword in q.lower() for keyword in ['how to', 'implement', 'best practices', 'python', 'kubernetes', 'react'])
]

BUSINESS_QUERIES = [
    q for q in TEST_QUERIES if any(keyword in q.lower() for keyword in ['market', 'companies', 'funding', 'economic'])
]


def get_test_queries(category: str = "all") -> list:
    """
    Get test queries by category.
    
    Args:
        category: Query category (all, academic, news, technical, business, edge_cases)
        
    Returns:
        List of test queries
    """
    if category == "academic":
        return ACADEMIC_QUERIES
    elif category == "news":
        return NEWS_QUERIES
    elif category == "technical":
        return TECHNICAL_QUERIES
    elif category == "business":
        return BUSINESS_QUERIES
    elif category == "edge_cases":
        return EDGE_CASE_QUERIES
    else:
        return TEST_QUERIES


def get_all_test_queries() -> list:
    """Get all test queries including edge cases."""
    return TEST_QUERIES + EDGE_CASE_QUERIES



