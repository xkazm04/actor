"""
Unit tests for Phase 3: Intelligent Reasoning & Research Plan Refinement
"""

import pytest
from src.planning.research_planner import ResearchPlanner, ResearchPlan
from src.planning.gap_detector import KnowledgeGapDetector
from src.reasoning.reasoning_engine import ReasoningEngine
from src.agents.research_coordinator import ResearchCoordinator


class TestResearchPlan:
    """Test ResearchPlan model."""
    
    def test_plan_creation(self):
        """Test creating a research plan."""
        plan = ResearchPlan(
            query="Test query",
            goals=["Goal 1", "Goal 2"],
            milestones=[{"name": "Milestone 1", "description": "Desc", "searches_required": 5}],
            estimated_searches=10
        )
        assert plan.query == "Test query"
        assert len(plan.goals) == 2
        assert len(plan.milestones) == 1


class TestKnowledgeGapDetector:
    """Test knowledge gap detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = KnowledgeGapDetector()
        assert detector is not None
    
    def test_extract_aspects(self):
        """Test aspect extraction from query."""
        detector = KnowledgeGapDetector()
        
        aspects = detector._extract_aspects("What is artificial intelligence?")
        assert len(aspects) > 0
        assert 'definition_and_scope' in aspects
    
    def test_assess_coverage(self):
        """Test coverage assessment."""
        detector = KnowledgeGapDetector()
        
        coverage = detector._assess_coverage(
            'definition_and_scope',
            ['AI is defined as...'],
            ['Artificial Intelligence'],
            [{'fact': 'AI definition'}]
        )
        
        assert 'score' in coverage
        assert 'evidence_count' in coverage
        assert 0 <= coverage['score'] <= 1
    
    def test_detect_gaps(self):
        """Test gap detection."""
        detector = KnowledgeGapDetector()
        
        findings = {
            'key_findings': ['Finding 1'],
            'main_themes': ['Theme 1'],
            'key_facts': [{'fact': 'Fact 1'}]
        }
        
        gap_analysis = detector.detect_gaps(
            "What is AI?",
            findings,
            sources_analyzed=5
        )
        
        assert 'gaps' in gap_analysis
        assert 'overall_coverage' in gap_analysis
        assert 'sufficient_coverage' in gap_analysis
    
    def test_should_continue_research(self):
        """Test research continuation decision."""
        detector = KnowledgeGapDetector()
        
        gap_analysis = {
            'overall_coverage': 0.5,
            'gaps': [{'priority': 'high'}]
        }
        
        should_continue = detector.should_continue_research(
            gap_analysis,
            completed_searches=5,
            max_searches=20
        )
        
        assert isinstance(should_continue, bool)
        
        # Test with sufficient coverage
        gap_analysis_good = {
            'overall_coverage': 0.9,
            'gaps': []
        }
        should_continue_good = detector.should_continue_research(
            gap_analysis_good,
            completed_searches=10,
            max_searches=20
        )
        # Should stop when coverage is good
        assert should_continue_good == False


class TestResearchCoordinator:
    """Test research coordinator."""
    
    def test_coordinator_initialization(self):
        """Test coordinator initialization."""
        try:
            coordinator = ResearchCoordinator()
            assert coordinator is not None
        except Exception:
            # May fail if API keys not set
            pytest.skip("Research coordinator requires API keys")
    
    def test_assess_progress(self):
        """Test progress assessment."""
        coordinator = ResearchCoordinator()
        
        findings = {
            'key_findings': ['Finding 1'],
            'main_themes': ['Theme 1'],
            'key_facts': []
        }
        
        assessment = coordinator.assess_progress(
            "Test query",
            findings,
            sources_analyzed=5,
            completed_searches=10,
            max_searches=20
        )
        
        assert 'gap_analysis' in assessment
        assert 'should_continue' in assessment
        assert 'recommendations' in assessment


@pytest.mark.skip(reason="Requires API keys")
class TestResearchPlanner:
    """Test research planner (requires API keys)."""
    
    def test_planner_initialization(self):
        """Test planner initialization."""
        planner = ResearchPlanner()
        assert planner.client is not None
    
    def test_create_initial_plan(self):
        """Test creating initial plan."""
        planner = ResearchPlanner()
        plan = planner.create_initial_plan("What is artificial intelligence?", max_searches=10)
        
        assert plan is not None
        assert plan.query == "What is artificial intelligence?"
        assert len(plan.goals) > 0


@pytest.mark.skip(reason="Requires API keys")
class TestReasoningEngine:
    """Test reasoning engine (requires API keys)."""
    
    def test_engine_initialization(self):
        """Test engine initialization."""
        engine = ReasoningEngine()
        assert engine.client is not None
    
    def test_reason_about_findings(self):
        """Test reasoning about findings."""
        engine = ReasoningEngine()
        
        findings = {
            'key_findings': ['Finding 1', 'Finding 2'],
            'key_facts': [{'fact': 'Fact 1'}],
            'contradictions': []
        }
        
        reasoning = engine.reason_about_findings("Test query", findings)
        
        assert 'reasoning_steps' in reasoning
        assert 'final_conclusions' in reasoning
        assert 'confidence_level' in reasoning


class TestIntegration:
    """Integration tests for Phase 3."""
    
    def test_gap_detection_pipeline(self):
        """Test gap detection pipeline."""
        detector = KnowledgeGapDetector()
        
        findings = {
            'key_findings': ['AI is machine intelligence'],
            'main_themes': ['Artificial Intelligence'],
            'key_facts': []
        }
        
        gap_analysis = detector.detect_gaps(
            "What is artificial intelligence?",
            findings,
            sources_analyzed=3
        )
        
        assert gap_analysis['overall_coverage'] >= 0
        assert isinstance(gap_analysis['gaps'], list)



