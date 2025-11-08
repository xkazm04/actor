#!/usr/bin/env python3
"""
Test Runner for Deep Search Actor

Usage:
    python run_test.py <test_id>
    python run_test.py phase1.1
    python run_test.py --list
    python run_test.py --phase Phase1
    python run_test.py --all

Examples:
    # Run a specific test
    python run_test.py phase1.1
    
    # List all available tests
    python run_test.py --list
    
    # Run all tests in a phase
    python run_test.py --phase Phase1
    
    # Run all tests
    python run_test.py --all
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import time

from connector import ActorConnector


class TestRunner:
    """Test runner for executing Actor tests."""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize test runner.
        
        Args:
            config_path: Path to config.json file
        """
        self.connector = ActorConnector(config_path)
        self.queries_path = Path(__file__).parent / "queries.json"
        self.queries = self._load_queries()
    
    def _load_queries(self) -> List[Dict[str, Any]]:
        """Load test queries from JSON file."""
        with open(self.queries_path, 'r') as f:
            return json.load(f)
    
    def get_test(self, test_id: str) -> Optional[Dict[str, Any]]:
        """
        Get test by ID.
        
        Args:
            test_id: Test ID (e.g., 'phase1.1')
            
        Returns:
            Test dictionary or None if not found
        """
        for test in self.queries:
            if test['testId'] == test_id:
                return test
        return None
    
    def list_tests(self, phase: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tests, optionally filtered by phase.
        
        Args:
            phase: Optional phase filter (e.g., 'Phase 1' or 'phase1')
            
        Returns:
            List of test dictionaries
        """
        if phase:
            # Normalize phase name for matching
            phase_normalized = phase.lower().replace(' ', '')
            return [
                t for t in self.queries 
                if t['phase'].lower().replace(' ', '') == phase_normalized
                or t['phase'].lower() == phase.lower()
            ]
        return self.queries
    
    def run_test(self, test_id: str, verbose: bool = True) -> Dict[str, Any]:
        """
        Run a single test.
        
        Args:
            test_id: Test ID to run
            verbose: Print progress messages
            
        Returns:
            Test result dictionary
        """
        test = self.get_test(test_id)
        if not test:
            raise ValueError(f"Test '{test_id}' not found")
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running Test: {test['testId']}")
            print(f"Phase: {test['phase']}")
            print(f"Name: {test['name']}")
            print(f"Description: {test['description']}")
            print(f"{'='*60}\n")
            print(f"Input: {json.dumps(test['input'], indent=2)}")
            print(f"\nStarting Actor run...")
        
        start_time = time.time()
        
        try:
            # Run the Actor
            run_result = self.connector.run_actor(test['input'])
            
            # Get results
            results = {
                'testId': test_id,
                'testName': test['name'],
                'phase': test['phase'],
                'runId': run_result['runId'],
                'status': run_result['status'],
                'startTime': datetime.fromtimestamp(start_time).isoformat(),
                'duration': time.time() - start_time,
                'runResult': run_result
            }
            
            # Fetch dataset items if available
            if run_result.get('defaultDatasetId'):
                try:
                    dataset_items = self.connector.get_dataset_items(
                        run_result['defaultDatasetId']
                    )
                    results['datasetItems'] = dataset_items
                    results['datasetItemCount'] = len(dataset_items)
                except Exception as e:
                    results['datasetError'] = str(e)
            
            # Fetch key-value store output if available
            if run_result.get('defaultKeyValueStoreId'):
                try:
                    output = self.connector.get_key_value_store_value(
                        run_result['defaultKeyValueStoreId']
                    )
                    results['output'] = output
                except Exception as e:
                    results['outputError'] = str(e)
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Test Completed: {test_id}")
                print(f"Status: {results['status']}")
                print(f"Duration: {results['duration']:.2f} seconds")
                print(f"Run ID: {results['runId']}")
                if results.get('datasetItemCount'):
                    print(f"Dataset Items: {results['datasetItemCount']}")
                print(f"{'='*60}\n")
            
            return results
            
        except Exception as e:
            error_result = {
                'testId': test_id,
                'testName': test['name'],
                'phase': test['phase'],
                'status': 'FAILED',
                'error': str(e),
                'startTime': datetime.fromtimestamp(start_time).isoformat(),
                'duration': time.time() - start_time
            }
            
            if verbose:
                print(f"\n{'='*60}")
                print(f"Test Failed: {test_id}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")
            
            return error_result
    
    def run_phase(self, phase: str, verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run all tests in a phase.
        
        Args:
            phase: Phase name (e.g., 'Phase 1')
            verbose: Print progress messages
            
        Returns:
            List of test result dictionaries
        """
        tests = self.list_tests(phase)
        if not tests:
            print(f"No tests found for phase: {phase}")
            return []
        
        results = []
        for test in tests:
            result = self.run_test(test['testId'], verbose=verbose)
            results.append(result)
            # Small delay between tests
            time.sleep(1)
        
        return results
    
    def run_all(self, verbose: bool = True) -> List[Dict[str, Any]]:
        """
        Run all tests.
        
        Args:
            verbose: Print progress messages
            
        Returns:
            List of test result dictionaries
        """
        results = []
        for test in self.queries:
            result = self.run_test(test['testId'], verbose=verbose)
            results.append(result)
            # Small delay between tests
            time.sleep(1)
        
        return results
    
    def print_summary(self, results: List[Dict[str, Any]]):
        """Print summary of test results."""
        total = len(results)
        passed = sum(1 for r in results if r.get('status') == 'SUCCEEDED')
        failed = sum(1 for r in results if r.get('status') == 'FAILED')
        
        print(f"\n{'='*60}")
        print("Test Summary")
        print(f"{'='*60}")
        print(f"Total Tests: {total}")
        print(f"Passed: {passed}")
        print(f"Failed: {failed}")
        print(f"{'='*60}\n")
        
        if failed > 0:
            print("Failed Tests:")
            for result in results:
                if result.get('status') == 'FAILED':
                    print(f"  - {result['testId']}: {result.get('error', 'Unknown error')}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run tests against the Deep Search Actor',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    
    parser.add_argument(
        'test_id',
        nargs='?',
        help='Test ID to run (e.g., phase1.1)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List all available tests'
    )
    parser.add_argument(
        '--phase',
        help='Run all tests in a phase (e.g., "Phase 1")'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='Run all tests'
    )
    parser.add_argument(
        '--config',
        help='Path to config.json file'
    )
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Suppress verbose output'
    )
    
    args = parser.parse_args()
    
    runner = TestRunner(config_path=args.config)
    
    try:
        if args.list:
            # List all tests
            tests = runner.list_tests()
            print(f"\nAvailable Tests ({len(tests)} total):\n")
            for test in tests:
                print(f"  {test['testId']:15} | {test['phase']:15} | {test['name']}")
            print()
            
        elif args.phase:
            # Run all tests in a phase
            print(f"Running all tests in {args.phase}...")
            results = runner.run_phase(args.phase, verbose=not args.quiet)
            runner.print_summary(results)
            
        elif args.all:
            # Run all tests
            print("Running all tests...")
            results = runner.run_all(verbose=not args.quiet)
            runner.print_summary(results)
            
        elif args.test_id:
            # Run single test
            result = runner.run_test(args.test_id, verbose=not args.quiet)
            if result.get('status') == 'FAILED':
                sys.exit(1)
        else:
            parser.print_help()
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()

