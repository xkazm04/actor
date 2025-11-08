#!/usr/bin/env python3
"""
Example usage of the test library

This script demonstrates how to use the test library components.
"""

from connector import ActorConnector
from run_test import TestRunner
import json


def example_connector():
    """Example: Using the connector directly."""
    print("=" * 60)
    print("Example: Using ActorConnector directly")
    print("=" * 60)
    
    connector = ActorConnector()
    
    # Run a custom query
    input_data = {
        "query": "What is machine learning?",
        "maxSearches": 10,
        "researchDepth": "quick"
    }
    
    print(f"\nRunning Actor with input: {json.dumps(input_data, indent=2)}")
    result = connector.run_actor(input_data)
    
    print(f"\nRun Result:")
    print(f"  Run ID: {result['runId']}")
    print(f"  Status: {result['status']}")
    
    # Get dataset items
    if result.get('defaultDatasetId'):
        items = connector.get_dataset_items(result['defaultDatasetId'])
        print(f"  Dataset Items: {len(items)}")
    
    # Get output
    if result.get('defaultKeyValueStoreId'):
        output = connector.get_key_value_store_value(result['defaultKeyValueStoreId'])
        print(f"  Output retrieved: {type(output)}")


def example_test_runner():
    """Example: Using the test runner."""
    print("\n" + "=" * 60)
    print("Example: Using TestRunner")
    print("=" * 60)
    
    runner = TestRunner()
    
    # List all tests
    print("\n1. Listing all tests:")
    tests = runner.list_tests()
    print(f"   Found {len(tests)} tests")
    
    # List tests in a phase
    print("\n2. Listing Phase 1 tests:")
    phase_tests = runner.list_tests("Phase 1")
    for test in phase_tests:
        print(f"   - {test['testId']}: {test['name']}")
    
    # Get a specific test
    print("\n3. Getting test phase1.1:")
    test = runner.get_test("phase1.1")
    if test:
        print(f"   Test: {test['name']}")
        print(f"   Description: {test['description']}")
    
    # Run a test (commented out to avoid actual execution)
    # print("\n4. Running test phase1.1:")
    # result = runner.run_test("phase1.1")
    # print(f"   Status: {result['status']}")


def example_custom_test():
    """Example: Running a custom test."""
    print("\n" + "=" * 60)
    print("Example: Running custom test")
    print("=" * 60)
    
    connector = ActorConnector()
    
    # Custom test input
    custom_input = {
        "query": "What are the benefits of Python programming?",
        "maxSearches": 15,
        "researchDepth": "standard",
        "outputFormat": "markdown"
    }
    
    print(f"\nCustom Input: {json.dumps(custom_input, indent=2)}")
    print("\n(To actually run, uncomment the line below)")
    # result = connector.run_actor(custom_input)
    # print(f"Run ID: {result['runId']}")


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("Test Library Examples")
    print("=" * 60)
    
    # Run examples
    example_connector()
    example_test_runner()
    example_custom_test()
    
    print("\n" + "=" * 60)
    print("Examples completed!")
    print("=" * 60)
    print("\nTo run actual tests, use:")
    print("  python run_test.py phase1.1")
    print("  python run_test.py --list")
    print("  python run_test.py --phase 'Phase 1'")

