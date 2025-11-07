"""
Unit tests for Phase 10: Benchmarking & Quality Assurance
"""

import pytest
from src.quality.quality_metrics import QualityMetrics
from src.benchmarking.performance_monitor import PerformanceMonitor
from src.benchmarking.llm_judge import LLMJudge
from src.benchmarking.benchmark_runner import BenchmarkRunner


class TestQualityMetrics:
    """Test quality metrics."""
    
    def test_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = QualityMetrics()
        assert metrics.metrics == {}
    
    def test_calculate_accuracy_score(self):
        """Test accuracy score calculation."""
        metrics = QualityMetrics()
        claims = ["Claim 1", "Claim 2"]
        sources = [
            {'url': 'https://example.edu/article', 'domain': 'example.edu', 'title': 'Test'}
        ]
        
        result = metrics.calculate_accuracy_score(claims, sources)
        assert 'score' in result
        assert 'total_claims' in result
        assert 0 <= result['score'] <= 1
    
    def test_calculate_completeness_score(self):
        """Test completeness score calculation."""
        metrics = QualityMetrics()
        query = "test query"
        findings = {
            'key_findings': ['finding 1', 'finding 2'],
            'main_themes': ['theme 1']
        }
        
        result = metrics.calculate_completeness_score(query, findings)
        assert 'score' in result
        assert 0 <= result['score'] <= 1
    
    def test_calculate_coherence_score(self):
        """Test coherence score calculation."""
        metrics = QualityMetrics()
        report = "This is a test report. It has multiple sentences. Each sentence adds to the coherence."
        sections = {'intro': 'intro', 'body': 'body', 'conclusion': 'conclusion'}
        
        result = metrics.calculate_coherence_score(report, sections)
        assert 'score' in result
        assert 0 <= result['score'] <= 1
    
    def test_calculate_citation_quality_score(self):
        """Test citation quality score calculation."""
        metrics = QualityMetrics()
        citations = [
            {'url': 'https://example.edu/article', 'domain': 'example.edu'}
        ]
        
        result = metrics.calculate_citation_quality_score(citations)
        assert 'score' in result
        assert 0 <= result['score'] <= 1
    
    def test_calculate_overall_quality(self):
        """Test overall quality calculation."""
        metrics = QualityMetrics()
        accuracy = {'score': 0.8}
        completeness = {'score': 0.7}
        coherence = {'score': 0.9}
        citation_quality = {'score': 0.75}
        
        result = metrics.calculate_overall_quality(accuracy, completeness, coherence, citation_quality)
        assert 'overall_score' in result
        assert 0 <= result['overall_score'] <= 1
    
    def test_get_quality_report(self):
        """Test quality report generation."""
        metrics = QualityMetrics()
        query = "test query"
        findings = {'key_findings': ['finding']}
        report = "Test report"
        citations = [{'url': 'https://example.com'}]
        
        report_result = metrics.get_quality_report(query, findings, report, citations)
        assert 'overall_quality' in report_result
        assert 'accuracy' in report_result
        assert 'recommendations' in report_result


class TestPerformanceMonitor:
    """Test performance monitor."""
    
    def test_monitor_initialization(self):
        """Test monitor initialization."""
        monitor = PerformanceMonitor()
        assert monitor.start_time is None
    
    def test_start_and_end(self):
        """Test start and end monitoring."""
        monitor = PerformanceMonitor()
        monitor.start()
        assert monitor.start_time is not None
        
        monitor.end()
        assert monitor.end_time is not None
        assert monitor.get_total_time() > 0
    
    def test_add_milestone(self):
        """Test adding milestones."""
        monitor = PerformanceMonitor()
        monitor.start()
        monitor.add_milestone("test", "Test milestone")
        
        assert len(monitor.milestones) > 0
    
    def test_calculate_speed_score(self):
        """Test speed score calculation."""
        monitor = PerformanceMonitor()
        monitor.start()
        # Simulate some time passing
        import time
        time.sleep(0.1)
        monitor.end()
        
        result = monitor.calculate_speed_score("low")
        assert 'score' in result
        assert 0 <= result['score'] <= 1
    
    def test_get_performance_summary(self):
        """Test performance summary."""
        monitor = PerformanceMonitor()
        monitor.start()
        monitor.end()
        
        summary = monitor.get_performance_summary()
        assert 'total_time_seconds' in summary
        assert 'speed_score' in summary
    
    def test_compare_with_baseline(self):
        """Test baseline comparison."""
        monitor = PerformanceMonitor()
        monitor.start()
        monitor.end()
        
        comparison = monitor.compare_with_baseline(100.0, 1.0, 0.8)
        assert 'time_ratio' in comparison
        assert 'is_within_20_percent' in comparison


class TestLLMJudge:
    """Test LLM judge."""
    
    def test_judge_initialization(self):
        """Test judge initialization."""
        judge = LLMJudge()
        assert judge.provider is not None
    
    def test_evaluate_report_quality_fallback(self):
        """Test report quality evaluation (fallback)."""
        judge = LLMJudge()
        # Use fallback when LLM not available
        result = judge._fallback_evaluation("test", "test report", [])
        assert 'overall_score' in result
        assert 'accuracy_score' in result


class TestBenchmarkRunner:
    """Test benchmark runner."""
    
    def test_runner_initialization(self):
        """Test runner initialization."""
        runner = BenchmarkRunner()
        assert runner.quality_metrics is not None
    
    @pytest.mark.asyncio
    async def test_run_benchmark(self):
        """Test running benchmark."""
        runner = BenchmarkRunner()
        result = await runner.run_benchmark(
            query="test query",
            deep_search_result={
                'report': 'Test report',
                'sources': [],
                'findings': {},
                'citations': [],
                'performance': {},
                'cost_summary': {}
            }
        )
        assert 'query' in result
        assert 'deep_search' in result
    
    def test_compare_results(self):
        """Test result comparison."""
        runner = BenchmarkRunner()
        deep_search = {
            'quality_metrics': {'overall_quality': {'overall_score': 0.8}},
            'llm_evaluation': {'overall_score': 80},
            'performance': {'total_time_seconds': 100}
        }
        perplexity = {
            'llm_evaluation': {'overall_score': 85},
            'performance': {'total_time_seconds': 90}
        }
        
        comparison = runner._compare_results(deep_search, perplexity)
        assert 'quality_comparison' in comparison
        assert 'performance_comparison' in comparison


class TestIntegration:
    """Integration tests for Phase 10."""
    
    def test_quality_workflow(self):
        """Test complete quality workflow."""
        metrics = QualityMetrics()
        query = "test query"
        findings = {'key_findings': ['finding']}
        report = "Test report"
        citations = [{'url': 'https://example.com'}]
        
        quality_report = metrics.get_quality_report(query, findings, report, citations)
        assert 'overall_quality' in quality_report
    
    def test_performance_workflow(self):
        """Test complete performance workflow."""
        monitor = PerformanceMonitor()
        monitor.start()
        monitor.add_milestone("search", "Search completed")
        monitor.end()
        
        summary = monitor.get_performance_summary()
        assert 'total_time_seconds' in summary



