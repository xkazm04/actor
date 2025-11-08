"""
Test Library for Deep Search Actor

This library provides tools for testing the deployed Actor using the Apify Client SDK.

Components:
- connector.py: Shared connector for interacting with the Actor
- config.json: Configuration file (actor ID, token, etc.)
- queries.json: All test queries organized by test ID
- run_test.py: Test runner script

Usage:
    from library.connector import ActorConnector
    from library.run_test import TestRunner
    
    # Using connector directly
    connector = ActorConnector()
    result = connector.run_actor({"query": "test"})
    
    # Using test runner
    runner = TestRunner()
    result = runner.run_test("phase1.1")
"""

__all__ = ['ActorConnector', 'TestRunner']

