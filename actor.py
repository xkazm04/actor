"""
Deep Search Actor - Main Entry Point
Phase 1 Implementation: Foundation & Core Research Engine

This file serves as the entry point for Apify Actor execution.
The main logic is in src/main.py
"""

from src.main import main
import asyncio

# Entry point - Apify calls this when the Actor starts
if __name__ == '__main__':
    asyncio.run(main())