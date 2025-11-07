"""
Unit tests for UX Improvement 5: Interactive Research Preview & Refinement
"""

import pytest
from src.interactive.preview_generator import PreviewGenerator
from src.interactive.pause_handler import PauseHandler
from src.interactive.refinement_engine import RefinementEngine
from src.interactive.state_manager import StateManager
from src.interactive.interactive_streamer import InteractiveStreamer


class TestPreviewGenerator:
    """Test preview generator."""
    
    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = PreviewGenerator()
        assert generator is not None
    
    @pytest.mark.asyncio
    async def test_generate_preview(self):
        """Test generating preview."""
        generator = PreviewGenerator()
        preview = await generator.generate_preview(
            query="test query",
            max_searches=10,
            research_depth="standard"
        )
        assert 'query' in preview
        assert 'research_plan' in preview
        assert 'estimated_time' in preview
        assert 'estimated_cost' in preview
    
    def test_estimate_time(self):
        """Test time estimation."""
        generator = PreviewGenerator()
        estimate = generator._estimate_time(10, "standard")
        assert 'seconds' in estimate
        assert 'minutes' in estimate
        assert estimate['seconds'] > 0
    
    def test_estimate_cost(self):
        """Test cost estimation."""
        generator = PreviewGenerator()
        estimate = generator._estimate_cost(10, "standard")
        assert 'usd' in estimate
        assert estimate['usd'] > 0


class TestPauseHandler:
    """Test pause handler."""
    
    def test_handler_initialization(self):
        """Test handler initialization."""
        handler = PauseHandler()
        assert handler.is_paused is False
    
    def test_pause(self):
        """Test pausing."""
        handler = PauseHandler()
        handler.pause("test reason")
        assert handler.is_paused is True
        assert handler.pause_reason == "test reason"
    
    def test_resume(self):
        """Test resuming."""
        handler = PauseHandler()
        handler.pause()
        result = handler.resume()
        assert result is True
        assert handler.is_paused is False
    
    def test_get_pause_info(self):
        """Test getting pause info."""
        handler = PauseHandler()
        handler.pause("test")
        info = handler.get_pause_info()
        assert info is not None
        assert info['is_paused'] is True


class TestRefinementEngine:
    """Test refinement engine."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = RefinementEngine()
        assert engine is not None
    
    def test_parse_refinement_request(self):
        """Test parsing refinement request."""
        engine = RefinementEngine()
        instructions = engine._parse_refinement_request("Add more about AI and machine learning")
        assert 'add_more_about' in instructions
    
    def test_identify_changes(self):
        """Test identifying changes."""
        engine = RefinementEngine()
        original = {'word_count': 1000}
        refined = {'word_count': 1200}
        changes = engine._identify_changes(original, refined)
        assert len(changes) > 0


class TestStateManager:
    """Test state manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        manager = StateManager()
        assert manager.run_id is not None
    
    @pytest.mark.asyncio
    async def test_save_and_load_state(self):
        """Test saving and loading state."""
        manager = StateManager()
        run_id = await manager.save_state(
            query="test query",
            progress=50.0,
            sources_found=[],
            analyses_complete=[],
            next_steps=[]
        )
        assert run_id == manager.get_run_id()
        
        loaded = await manager.load_state(run_id)
        assert loaded is not None
        assert loaded['query'] == "test query"
        assert loaded['progress'] == 50.0


class TestInteractiveStreamer:
    """Test interactive streamer."""
    
    def test_streamer_initialization(self):
        """Test streamer initialization."""
        streamer = InteractiveStreamer()
        assert streamer is not None
    
    def test_add_finding(self):
        """Test adding finding."""
        streamer = InteractiveStreamer()
        streamer.add_finding("Test finding")
        assert len(streamer.get_current_findings()) == 1
    
    def test_add_source(self):
        """Test adding source."""
        streamer = InteractiveStreamer()
        streamer.add_source({'url': 'https://example.com', 'title': 'Test'})
        assert len(streamer.get_current_sources()) == 1
    
    def test_get_interactive_summary(self):
        """Test getting interactive summary."""
        streamer = InteractiveStreamer()
        streamer.add_finding("Finding 1")
        streamer.add_source({'url': 'https://example.com'})
        summary = streamer.get_interactive_summary()
        assert 'findings_count' in summary
        assert 'sources_count' in summary


class TestIntegration:
    """Integration tests for UX Improvement 5."""
    
    @pytest.mark.asyncio
    async def test_preview_workflow(self):
        """Test preview workflow."""
        generator = PreviewGenerator()
        preview = await generator.generate_preview("test query")
        assert 'research_plan' in preview
    
    def test_pause_resume_workflow(self):
        """Test pause/resume workflow."""
        handler = PauseHandler()
        handler.pause("test")
        assert handler.is_paused_state()
        handler.resume()
        assert not handler.is_paused_state()
    
    @pytest.mark.asyncio
    async def test_state_management_workflow(self):
        """Test state management workflow."""
        manager = StateManager()
        await manager.save_state(
            query="test",
            progress=50.0,
            sources_found=[],
            analyses_complete=[],
            next_steps=[]
        )
        loaded = await manager.load_state()
        assert loaded is not None



