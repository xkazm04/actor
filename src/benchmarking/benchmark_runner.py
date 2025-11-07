"""
Benchmark Runner - Compares Deep Search Actor with Perplexity.
Runs benchmarks and generates comparison reports.
"""

from typing import Dict, List, Optional
from datetime import datetime
import asyncio
from apify import Actor

from src.quality.quality_metrics import QualityMetrics
from src.benchmarking.performance_monitor import PerformanceMonitor
from src.benchmarking.llm_judge import LLMJudge


class BenchmarkRunner:
    """
    Runs benchmarks comparing Deep Search Actor with Perplexity.
    """
    
    def __init__(self):
        """Initialize benchmark runner."""
        self.quality_metrics = QualityMetrics()
        self.llm_judge = LLMJudge()
    
    async def run_benchmark(
        self,
        query: str,
        deep_search_result: Dict,
        perplexity_result: Optional[Dict] = None
    ) -> Dict:
        """
        Run benchmark comparison.
        
        Args:
            query: Test query
            deep_search_result: Deep Search Actor result
            perplexity_result: Optional Perplexity result for comparison
            
        Returns:
            Benchmark comparison dictionary
        """
        benchmark = {
            'query': query,
            'timestamp': datetime.now().isoformat(),
            'deep_search': {},
            'perplexity': {},
            'comparison': {}
        }
        
        # Evaluate Deep Search Actor result
        deep_search_eval = self._evaluate_result(
            query,
            deep_search_result.get('report', ''),
            deep_search_result.get('sources', []),
            deep_search_result.get('findings', {}),
            deep_search_result.get('citations', []),
            deep_search_result.get('performance', {}),
            deep_search_result.get('cost_summary', {})
        )
        benchmark['deep_search'] = deep_search_eval
        
        # Evaluate Perplexity result if available
        if perplexity_result:
            perplexity_eval = self._evaluate_perplexity_result(
                query,
                perplexity_result
            )
            benchmark['perplexity'] = perplexity_eval
            
            # Compare results
            comparison = self._compare_results(deep_search_eval, perplexity_eval)
            benchmark['comparison'] = comparison
        
        return benchmark
    
    def _evaluate_result(
        self,
        query: str,
        report: str,
        sources: List[Dict],
        findings: Dict,
        citations: List[Dict],
        performance: Dict,
        cost_summary: Dict
    ) -> Dict:
        """Evaluate a single result."""
        # Quality metrics
        quality_report = self.quality_metrics.get_quality_report(
            query=query,
            findings=findings,
            report=report,
            citations=citations
        )
        
        # LLM judge evaluation
        llm_evaluation = self.llm_judge.evaluate_report_quality(
            query=query,
            report=report,
            sources=sources
        )
        
        return {
            'quality_metrics': quality_report,
            'llm_evaluation': llm_evaluation,
            'performance': performance,
            'cost': cost_summary,
            'source_count': len(sources),
            'citation_count': len(citations),
            'report_length': len(report.split())
        }
    
    def _evaluate_perplexity_result(
        self,
        query: str,
        perplexity_result: Dict
    ) -> Dict:
        """Evaluate Perplexity result."""
        # Extract data from Perplexity result
        report = perplexity_result.get('answer', '')
        sources = perplexity_result.get('sources', [])
        
        # LLM evaluation
        llm_evaluation = self.llm_judge.evaluate_report_quality(
            query=query,
            report=report,
            sources=sources
        )
        
        return {
            'llm_evaluation': llm_evaluation,
            'performance': perplexity_result.get('performance', {}),
            'source_count': len(sources),
            'report_length': len(report.split())
        }
    
    def _compare_results(
        self,
        deep_search: Dict,
        perplexity: Dict
    ) -> Dict:
        """Compare Deep Search and Perplexity results."""
        deep_quality = deep_search.get('quality_metrics', {}).get('overall_quality', {})
        deep_llm = deep_search.get('llm_evaluation', {})
        deep_perf = deep_search.get('performance', {})
        
        perplexity_llm = perplexity.get('llm_evaluation', {})
        perplexity_perf = perplexity.get('performance', {})
        
        comparison = {
            'quality_comparison': {
                'deep_search_score': deep_quality.get('overall_score', 0.0) * 100,
                'perplexity_score': perplexity_llm.get('overall_score', 0),
                'difference': (deep_quality.get('overall_score', 0.0) * 100) - perplexity_llm.get('overall_score', 0),
                'within_10_percent': abs((deep_quality.get('overall_score', 0.0) * 100) - perplexity_llm.get('overall_score', 0)) <= 10
            },
            'performance_comparison': {
                'deep_search_time': deep_perf.get('total_time_seconds', 0),
                'perplexity_time': perplexity_perf.get('total_time_seconds', 0),
                'time_ratio': deep_perf.get('total_time_seconds', 0) / max(perplexity_perf.get('total_time_seconds', 1), 1),
                'within_20_percent': self._check_within_percentage(
                    deep_perf.get('total_time_seconds', 0),
                    perplexity_perf.get('total_time_seconds', 0),
                    0.2
                )
            },
            'source_comparison': {
                'deep_search_sources': deep_search.get('source_count', 0),
                'perplexity_sources': perplexity.get('source_count', 0),
                'source_diversity': 'N/A'  # Could be enhanced
            }
        }
        
        return comparison
    
    def _check_within_percentage(self, value1: float, value2: float, percentage: float) -> bool:
        """Check if value1 is within percentage of value2."""
        if value2 == 0:
            return False
        ratio = value1 / value2
        return (1 - percentage) <= ratio <= (1 + percentage)
    
    async def run_test_suite(
        self,
        test_queries: List[str],
        run_perplexity: bool = False
    ) -> Dict:
        """
        Run benchmark test suite.
        
        Args:
            test_queries: List of test queries
            run_perplexity: Whether to run Perplexity comparisons
            
        Returns:
            Test suite results
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'total_queries': len(test_queries),
            'benchmarks': [],
            'summary': {}
        }
        
        for query in test_queries:
            Actor.log.info(f"Running benchmark for query: {query}")
            # Note: In real implementation, would run Deep Search Actor and Perplexity
            # For now, create placeholder benchmark
            benchmark = await self.run_benchmark(
                query=query,
                deep_search_result={},  # Would be actual result
                perplexity_result={} if run_perplexity else None
            )
            results['benchmarks'].append(benchmark)
        
        # Calculate summary statistics
        results['summary'] = self._calculate_summary(results['benchmarks'])
        
        return results
    
    def _calculate_summary(self, benchmarks: List[Dict]) -> Dict:
        """Calculate summary statistics from benchmarks."""
        if not benchmarks:
            return {}
        
        deep_scores = []
        perplexity_scores = []
        deep_times = []
        perplexity_times = []
        
        for benchmark in benchmarks:
            deep_quality = benchmark.get('deep_search', {}).get('quality_metrics', {}).get('overall_quality', {})
            deep_scores.append(deep_quality.get('overall_score', 0.0) * 100)
            
            deep_perf = benchmark.get('deep_search', {}).get('performance', {})
            deep_times.append(deep_perf.get('total_time_seconds', 0))
            
            if 'perplexity' in benchmark:
                perplexity_llm = benchmark.get('perplexity', {}).get('llm_evaluation', {})
                perplexity_scores.append(perplexity_llm.get('overall_score', 0))
                
                perplexity_perf = benchmark.get('perplexity', {}).get('performance', {})
                perplexity_times.append(perplexity_perf.get('total_time_seconds', 0))
        
        summary = {
            'deep_search': {
                'avg_quality_score': sum(deep_scores) / len(deep_scores) if deep_scores else 0,
                'avg_time_seconds': sum(deep_times) / len(deep_times) if deep_times else 0
            }
        }
        
        if perplexity_scores:
            summary['perplexity'] = {
                'avg_quality_score': sum(perplexity_scores) / len(perplexity_scores),
                'avg_time_seconds': sum(perplexity_times) / len(perplexity_times) if perplexity_times else 0
            }
            
            summary['comparison'] = {
                'quality_difference': summary['deep_search']['avg_quality_score'] - summary['perplexity']['avg_quality_score'],
                'time_ratio': summary['deep_search']['avg_time_seconds'] / max(summary['perplexity']['avg_time_seconds'], 1),
                'within_10_percent_quality': abs(summary['deep_search']['avg_quality_score'] - summary['perplexity']['avg_quality_score']) <= 10,
                'within_20_percent_time': 0.8 <= summary['deep_search']['avg_time_seconds'] / max(summary['perplexity']['avg_time_seconds'], 1) <= 1.2
            }
        
        return summary


def create_benchmark_runner() -> BenchmarkRunner:
    """Create a benchmark runner instance."""
    return BenchmarkRunner()



