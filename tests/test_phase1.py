"""
Unit tests for Phase 1: Foundation & Core Research Engine
"""

import pytest
from src.utils.models import QueryInput, SubQuery, SearchResult
from src.agents.query_decomposer import QueryDecomposer
from src.search.multi_search_engine import MultiSearchEngine, SearchAPI


class TestQueryInput:
    """Test query input validation."""
    
    def test_valid_input(self):
        """Test valid query input."""
        input_data = QueryInput(
            query="What is artificial intelligence?",
            max_searches=10,
            research_depth="standard"
        )
        assert input_data.query == "What is artificial intelligence?"
        assert input_data.max_searches == 10
    
    def test_query_min_length(self):
        """Test query minimum length validation."""
        with pytest.raises(Exception):
            QueryInput(query="short")
    
    def test_query_max_length(self):
        """Test query maximum length validation."""
        long_query = "a" * 2001
        with pytest.raises(Exception):
            QueryInput(query=long_query)
    
    def test_query_sanitization(self):
        """Test query sanitization removes excessive whitespace."""
        input_data = QueryInput(query="  What   is   AI?  ")
        assert input_data.query == "What is AI?"


class TestSubQuery:
    """Test SubQuery model."""
    
    def test_sub_query_creation(self):
        """Test creating a SubQuery."""
        sub_query = SubQuery(
            query="Test query",
            priority=1,
            category="test",
            reasoning="Test reasoning"
        )
        assert sub_query.query == "Test query"
        assert sub_query.priority == 1


class TestSearchResult:
    """Test SearchResult model."""
    
    def test_search_result_creation(self):
        """Test creating a SearchResult."""
        result = SearchResult(
            url="https://example.com",
            title="Example",
            snippet="Example snippet",
            source_api="google"
        )
        assert result.url == "https://example.com"
        assert result.source_api == "google"


class TestMultiSearchEngine:
    """Test multi-search engine."""
    
    def test_engine_initialization(self):
        """Test search engine initialization."""
        engine = MultiSearchEngine()
        assert engine is not None
    
    def test_get_available_apis(self):
        """Test getting available APIs."""
        engine = MultiSearchEngine()
        # Without API keys, should return empty list or handle gracefully
        available = engine._get_available_apis()
        assert isinstance(available, list)


# Integration tests would require API keys and actual API calls
# These should be run separately with proper credentials

@pytest.mark.skip(reason="Requires API keys")
class TestQueryDecomposer:
    """Test query decomposer (requires API keys)."""
    
    @pytest.mark.asyncio
    async def test_decompose_query(self):
        """Test query decomposition."""
        decomposer = QueryDecomposer()
        sub_queries = await decomposer.decompose("What is AI?", max_sub_queries=5)
        assert len(sub_queries) > 0
        assert all(isinstance(sq, SubQuery) for sq in sub_queries)


@pytest.mark.skip(reason="Requires API keys")
class TestSearchIntegration:
    """Test search integration (requires API keys)."""
    
    @pytest.mark.asyncio
    async def test_search_execution(self):
        """Test search execution."""
        engine = MultiSearchEngine()
        results = await engine.search("test query", num_results=5)
        assert isinstance(results, list)
        assert all(isinstance(r, SearchResult) for r in results)



