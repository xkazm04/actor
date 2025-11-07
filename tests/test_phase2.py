"""
Unit tests for Phase 2: Smart Source Analysis & Content Extraction
"""

import pytest
from datetime import datetime, timezone
from src.extraction.content_fetcher import ContentFetcher
from src.extraction.content_processor import ContentProcessor
from src.analysis.relevance_scorer import RelevanceScorer
from src.agents.content_analyzer import ContentAnalyzer


class TestContentFetcher:
    """Test content fetcher."""
    
    @pytest.mark.asyncio
    async def test_fetcher_initialization(self):
        """Test fetcher initialization."""
        async with ContentFetcher(max_concurrent=5) as fetcher:
            assert fetcher.max_concurrent == 5
            assert fetcher.session is not None
    
    @pytest.mark.asyncio
    async def test_fetch_content_invalid_url(self):
        """Test fetching from invalid URL."""
        async with ContentFetcher() as fetcher:
            result = await fetcher.fetch_content("https://invalid-url-that-does-not-exist-12345.com")
            # Should handle gracefully
            assert result is None or isinstance(result, dict)


class TestContentProcessor:
    """Test content processor."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ContentProcessor()
        assert processor is not None
    
    def test_process_html(self):
        """Test HTML processing."""
        processor = ContentProcessor()
        
        html_content = {
            'url': 'https://example.com',
            'raw_html': '<html><head><title>Test Page</title></head><body><h1>Hello</h1><p>World</p></body></html>',
            'content_type': 'html',
            'metadata': {'domain': 'example.com'}
        }
        
        result = processor.process(html_content)
        
        assert result['url'] == 'https://example.com'
        assert result['status'] == 'success'
        assert 'markdown' in result
        assert 'metadata' in result
        assert 'chunks' in result
    
    def test_process_text(self):
        """Test text processing."""
        processor = ContentProcessor()
        
        text_content = {
            'url': 'https://example.com',
            'content': 'This is a test document with some content.',
            'content_type': 'text',
            'metadata': {}
        }
        
        result = processor.process(text_content)
        
        assert result['url'] == 'https://example.com'
        assert result['status'] == 'success'
        assert 'markdown' in result
    
    def test_chunk_content(self):
        """Test content chunking."""
        processor = ContentProcessor()
        
        # Create long content
        long_content = '\n\n'.join([f"Paragraph {i}" for i in range(100)])
        chunks = processor._chunk_content(long_content, max_tokens=100)
        
        assert len(chunks) > 0
        assert all('text' in chunk for chunk in chunks)
        assert all('token_count' in chunk for chunk in chunks)


class TestRelevanceScorer:
    """Test relevance scorer."""
    
    def test_scorer_initialization(self):
        """Test scorer initialization."""
        scorer = RelevanceScorer(
            relevance_weight=0.5,
            recency_weight=0.3,
            authority_weight=0.2
        )
        assert scorer.relevance_weight == 0.5
        assert scorer.recency_weight == 0.3
        assert scorer.authority_weight == 0.2
    
    def test_score_relevance(self):
        """Test relevance scoring."""
        scorer = RelevanceScorer()
        
        source = {
            'title': 'Artificial Intelligence Research',
            'snippet': 'This article discusses AI and machine learning',
            'url': 'https://example.com'
        }
        
        score = scorer._score_relevance(source, 'artificial intelligence')
        assert 0 <= score <= 1
    
    def test_score_authority(self):
        """Test authority scoring."""
        scorer = RelevanceScorer()
        
        # Test .edu domain
        source_edu = {'url': 'https://university.edu/article'}
        score_edu = scorer._score_authority(source_edu)
        assert score_edu > 0.7
        
        # Test regular domain
        source_regular = {'url': 'https://example.com/article'}
        score_regular = scorer._score_authority(source_regular)
        assert 0 <= score_regular <= 1
    
    def test_score_recency(self):
        """Test recency scoring."""
        scorer = RelevanceScorer()
        
        source = {'url': 'https://example.com'}
        
        # Test with recent date
        processed_content = {
            'metadata': {
                'publish_date': datetime.now(timezone.utc).isoformat()
            }
        }
        score_recent = scorer._score_recency(source, processed_content)
        assert score_recent > 0.9
        
        # Test without date
        score_no_date = scorer._score_recency(source, None)
        assert score_no_date == 0.5  # Default score
    
    def test_rank_sources(self):
        """Test source ranking."""
        scorer = RelevanceScorer()
        
        sources = [
            {'url': 'https://example1.com', 'title': 'AI Research', 'snippet': 'AI'},
            {'url': 'https://example2.com', 'title': 'Other Topic', 'snippet': 'Other'}
        ]
        
        ranked = scorer.rank_sources(sources, 'artificial intelligence')
        
        assert len(ranked) == 2
        assert all('score' in s for s in ranked)
        assert ranked[0]['score'] >= ranked[1]['score']  # Should be sorted descending


@pytest.mark.skip(reason="Requires API keys")
class TestContentAnalyzer:
    """Test content analyzer (requires API keys)."""
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization."""
        analyzer = ContentAnalyzer()
        assert analyzer.client is not None
    
    def test_analyze_content(self):
        """Test content analysis."""
        analyzer = ContentAnalyzer()
        
        content = {
            'url': 'https://example.com',
            'markdown': 'This is a test article about artificial intelligence.',
            'chunks': [{'text': 'This is a test article about artificial intelligence.'}]
        }
        
        analysis = analyzer.analyze_content(content, 'artificial intelligence')
        
        assert 'url' in analysis
        assert 'insights' in analysis
        assert 'themes' in analysis
        assert 'facts' in analysis


class TestIntegration:
    """Integration tests for Phase 2 components."""
    
    def test_content_pipeline(self):
        """Test full content processing pipeline."""
        processor = ContentProcessor()
        
        html_content = {
            'url': 'https://example.com',
            'raw_html': '<html><body><h1>Test</h1><p>Content</p></body></html>',
            'content_type': 'html',
            'metadata': {}
        }
        
        processed = processor.process(html_content)
        assert processed['status'] == 'success'
        
        # Score it
        scorer = RelevanceScorer()
        source = {'url': 'https://example.com', 'title': 'Test', 'snippet': 'Content'}
        score = scorer.score_source(source, 'test', processed)
        assert 0 <= score <= 100



