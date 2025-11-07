# Deep Search Actor - Implementation Requirements

## Document Overview

**Project**: Deep Search Actor for Apify Platform  
**Version**: 1.0.0  
**Date**: November 7, 2025  
**Status**: Requirements & Planning Phase

## Executive Summary

This document defines the complete implementation plan for developing a production-ready Deep Search Actor on the Apify platform. The Actor will provide affordable, efficient deep research capabilities comparable to Perplexity's Deep Research, while offering flexible deployment as a cloud-based microservice.

---

## 1. Technology Stack

### 1.1 Core Technologies

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Primary Language** | Python 3.11+ | Native Apify SDK support, rich AI/ML ecosystem |
| **Base Image** | `apify/actor-python:3.11` | Official Apify Python base with optimized runtime |
| **Development Framework** | Apify SDK Python | Built-in storage, scheduling, monitoring |

### 1.2 AI & Orchestration Layer

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Task Execution LLM** | DeepSeek R1 | Cost-effective reasoning for query breakdown and synthesis |
| **Reasoning LLM** | Claude Sonnet 4 | High-quality analysis and report generation |
| **Agent Framework** | Agno | Lightweight, fast orchestration (~10,000x faster than LangGraph) |
| **Agent Monitoring** | AgentOps (optional) | Real-time tracking and debugging |

**Agno Selection Rationale:**
- Performance-optimized for production workloads
- Model-agnostic (supports 23+ providers including DeepSeek, Anthropic)
- Minimal boilerplate with clean abstractions
- Native multimodal support (text, images)
- Built-in memory and state management
- Strong type validation with Pydantic

### 1.3 Search & Data Retrieval

| Component | API/Service | Purpose |
|-----------|------------|---------|
| **Primary Search** | Google Custom Search API | High-quality, comprehensive results |
| **Secondary Search** | Brave Search API | Privacy-focused, cost-effective alternative |
| **Tertiary Search** | Bing Search API | Additional coverage and redundancy |
| **Benchmark API** | Perplexity API | Quality comparison and validation |

### 1.4 Content Extraction

| Component | Tool | Purpose |
|-----------|------|---------|
| **Web Scraping** | Apify Web Scraper Actor | Structured data extraction |
| **HTML Parsing** | Beautiful Soup 4 | Lightweight HTML processing |
| **JavaScript Sites** | Playwright | Dynamic content handling |
| **Content Cleaning** | Crawl4AI (optional) | Markdown conversion, content cleanup |

### 1.5 Storage & Data Management

| Storage Type | Apify Service | Use Case |
|--------------|--------------|----------|
| **Structured Results** | Datasets | Final reports, metadata, structured outputs |
| **Files & Reports** | Key-Value Store | Full reports (MD/HTML/PDF), intermediate state |
| **Cache** | Key-Value Store | Search result caching (24-48h TTL) |
| **State Management** | Agno Session State | Research progress, context preservation |

---

## 2. Implementation Phases

### PHASE 1: Foundation & Core Research Engine

**Duration**: 2-3 weeks  
**Goal**: Implement basic iterative multi-query research engine

#### Requirements

**Functional Requirements:**
1. **Query Input Processing**
   - Accept natural language queries (minimum 10 chars, maximum 2000 chars)
   - Validate and sanitize user input
   - Extract intent and research scope
   - Input validation using Pydantic models

2. **Query Decomposition**
   - Use DeepSeek R1 to break down main query into 5-20 sub-queries
   - Apply query expansion techniques (synonyms, related concepts)
   - Prioritize sub-queries by relevance and information value
   - Store decomposition plan in key-value store

3. **Iterative Search Execution**
   - Execute sub-queries sequentially across multiple search APIs
   - Implement round-robin or intelligent API selection
   - Handle API rate limits with exponential backoff
   - Collect 10-100 sources depending on research depth

4. **Progress Tracking**
   - Log each search operation with timestamp
   - Store intermediate results after each search iteration
   - Calculate and report progress percentage
   - Enable resumability from failure points

**Technical Requirements:**
- Implement Agno Agent for query breakdown
- Create search API wrapper with retry logic
- Design state management for resumable execution
- Implement Actor lifecycle hooks (init, process, exit)

**Deliverables:**
- `src/agents/query_decomposer.py` - Query breakdown logic
- `src/search/multi_search_engine.py` - Search API integration
- `src/core/research_engine.py` - Main research orchestration
- `tests/test_phase1.py` - Unit tests for Phase 1
- Documentation: Phase 1 completion report

**Success Criteria:**
- Successfully breaks down 90%+ of test queries
- Executes 10+ sequential searches without failure
- Handles API failures gracefully with retries
- Maintains state across Actor restarts

---

### PHASE 2: Smart Source Analysis & Content Extraction

**Duration**: 2-3 weeks  
**Goal**: Implement intelligent source reading and relevance scoring

#### Requirements

**Functional Requirements:**
1. **Source Fetching**
   - Extract full content from URLs (not just snippets)
   - Handle paywalls and access restrictions gracefully
   - Support multiple content types (HTML, PDF, plain text)
   - Implement concurrent fetching (5-10 parallel requests)

2. **Content Processing**
   - Parse HTML and extract main content (remove ads, navbars)
   - Convert content to clean Markdown format
   - Extract metadata (title, author, publish date, domain)
   - Chunk long content into manageable sections (500-1000 tokens)

3. **Relevance Scoring**
   - Score sources by relevance to original query (0-100 scale)
   - Score by recency (newer = higher score, with decay function)
   - Score by authority (domain reputation, citations)
   - Calculate composite score and rank sources

4. **Content Analysis**
   - Use Claude Sonnet to extract key insights from top sources
   - Identify themes, patterns, and contradictions
   - Extract specific facts, statistics, and quotes
   - Build knowledge graph of concepts and relationships

**Technical Requirements:**
- Integrate Apify Web Scraper Actor via Actor.call()
- Implement content extraction pipeline with Playwright fallback
- Design scoring algorithms with configurable weights
- Create Agno Agent for content analysis with Claude

**Deliverables:**
- `src/extraction/content_fetcher.py` - URL content extraction
- `src/extraction/content_processor.py` - HTML/PDF processing
- `src/analysis/relevance_scorer.py` - Source scoring logic
- `src/agents/content_analyzer.py` - LLM-based analysis
- `tests/test_phase2.py` - Unit tests for Phase 2

**Success Criteria:**
- Extracts readable content from 85%+ of URLs
- Correctly identifies top 10 most relevant sources
- Processes 50+ sources in under 5 minutes
- Maintains content quality score above 80%

---

### PHASE 3: Intelligent Reasoning & Research Plan Refinement

**Duration**: 2 weeks  
**Goal**: Implement adaptive research planning with reasoning loops

#### Requirements

**Functional Requirements:**
1. **Initial Research Planning**
   - Generate research plan based on initial query
   - Define information goals and knowledge gaps
   - Create structured research roadmap with milestones
   - Estimate required searches and timeline

2. **Dynamic Plan Adjustment**
   - Analyze search results after each iteration
   - Identify new information gaps and opportunities
   - Refine subsequent search queries based on findings
   - Adapt research depth based on information quality

3. **Reasoning Engine**
   - Use DeepSeek R1 for step-by-step reasoning
   - Document reasoning process in structured format
   - Identify contradictions and require reconciliation
   - Build causal chains and argument structures

4. **Knowledge Gap Detection**
   - Track which aspects of query are well-covered
   - Identify under-researched areas requiring more sources
   - Prioritize filling critical knowledge gaps
   - Stop research when sufficient coverage achieved

**Technical Requirements:**
- Implement Agno Workflow for multi-step reasoning
- Design state machine for research plan evolution
- Create knowledge gap tracking system
- Implement stopping criteria (coverage threshold, time limit)

**Deliverables:**
- `src/planning/research_planner.py` - Research plan generation
- `src/reasoning/reasoning_engine.py` - Reasoning loop implementation
- `src/planning/gap_detector.py` - Knowledge gap analysis
- `src/agents/research_coordinator.py` - Plan refinement agent
- `tests/test_phase3.py` - Unit tests for Phase 3

**Success Criteria:**
- Generates comprehensive research plans for complex queries
- Adapts plan based on findings in 80%+ of cases
- Identifies knowledge gaps with 90%+ accuracy
- Produces logical reasoning chains for conclusions

---

### PHASE 4: Report Generation & Structured Output

**Duration**: 2 weeks  
**Goal**: Generate high-quality, well-structured research reports

#### Requirements

**Functional Requirements:**
1. **Report Structure**
   - Executive Summary (2-3 paragraphs, key takeaways)
   - Main Body (organized by themes/topics)
   - Detailed Analysis (synthesis of findings)
   - Sources Section (full bibliography with links)
   - Methodology Section (research process summary)

2. **Content Synthesis**
   - Use Claude Sonnet for report generation
   - Synthesize information from multiple sources
   - Maintain consistent tone and style
   - Include specific facts, statistics, and examples

3. **Citation Management**
   - Inline citations with numbered references
   - Full source details in bibliography
   - Track which sources contributed to each claim
   - Provide clickable links to original sources

4. **Multiple Output Formats**
   - Markdown (default, with proper formatting)
   - HTML (styled, responsive design)
   - JSON (structured data for API consumption)
   - PDF (optional, for download/printing)

**Technical Requirements:**
- Create report templates with Jinja2
- Implement citation tracking system
- Design report generation pipeline with Claude
- Support format conversion (MD → HTML → PDF)

**Deliverables:**
- `src/report/report_generator.py` - Main report generation
- `src/report/citation_manager.py` - Citation tracking
- `src/report/templates/` - Report templates (MD, HTML)
- `src/report/formatters.py` - Format conversion utilities
- `tests/test_phase4.py` - Unit tests for Phase 4

**Success Criteria:**
- Generates well-structured reports for all queries
- Maintains 100% citation accuracy
- Produces reports readable by non-experts
- Successfully outputs all required formats

---

### PHASE 5: Tiered Research Modes & Cost Optimization

**Duration**: 2 weeks  
**Goal**: Implement tiered pricing with cost-effective execution

#### Requirements

**Functional Requirements:**
1. **Quick Mode (2-3 min, $0.10-0.25)**
   - 5-10 searches
   - 10-20 sources analyzed
   - Brief report (500-1000 words)
   - Single-pass analysis (no reasoning loops)
   - Use case: Quick fact-checking, simple queries

2. **Standard Mode (5-10 min, $0.50-1.00)**
   - 20-30 searches
   - 30-50 sources analyzed
   - Standard report (1500-3000 words)
   - Basic reasoning loops (2-3 iterations)
   - Use case: General research, competitive analysis

3. **Deep Mode (15-30 min, $2.00-5.00)**
   - 50-100 searches
   - 100-200 sources analyzed
   - Comprehensive report (3000-8000 words)
   - Full reasoning loops (5-10 iterations)
   - Use case: Academic research, strategic planning

4. **Cost Tracking**
   - Track API calls and LLM token usage
   - Calculate actual cost per run
   - Provide cost breakdown in metadata
   - Enforce budget limits (stop if exceeded)

**Technical Requirements:**
- Implement mode-specific configuration presets
- Create cost tracking middleware
- Design budget enforcement logic
- Optimize API usage (caching, batching)

**Deliverables:**
- `src/modes/research_modes.py` - Mode configurations
- `src/cost/cost_tracker.py` - Cost tracking system
- `src/cost/budget_enforcer.py` - Budget limits
- `.actor/input_schema.json` - Updated with mode selection
- `tests/test_phase5.py` - Unit tests for Phase 5

**Success Criteria:**
- All modes complete within stated time ranges
- Actual costs within ±20% of estimates
- Budget limits enforced with 100% accuracy
- Mode quality meets defined standards

---

### PHASE 6: Smart Caching & Performance Optimization

**Duration**: 1-2 weeks  
**Goal**: Reduce costs and improve speed through intelligent caching

#### Requirements

**Functional Requirements:**
1. **Search Result Caching**
   - Cache search API results for 24-48 hours
   - Use query + API as cache key
   - Invalidate cache on demand or after TTL
   - Reduce duplicate searches by 70%+

2. **Content Caching**
   - Cache fetched URL content for 48 hours
   - Store processed/cleaned content separately
   - Implement cache warming for common domains
   - Share cache across multiple Actor runs

3. **Similarity Detection**
   - Detect similar queries using embeddings
   - Reuse cached research for similar queries
   - Partial result reuse (matching sub-queries)
   - Reduce redundant work by 40%+

4. **Cache Management**
   - Automatic cache expiration based on TTL
   - Manual cache invalidation API
   - Cache size limits (max 1GB per Actor)
   - Cache statistics and hit rate reporting

**Technical Requirements:**
- Implement cache layer with Apify Key-Value Store
- Design cache key generation with hashing
- Create similarity detection with embeddings
- Build cache statistics dashboard

**Deliverables:**
- `src/cache/cache_manager.py` - Cache operations
- `src/cache/similarity_detector.py` - Query similarity
- `src/cache/cache_stats.py` - Statistics tracking
- Documentation: Caching strategy guide
- `tests/test_phase6.py` - Unit tests for Phase 6

**Success Criteria:**
- Cache hit rate above 60% for repeated queries
- 50%+ reduction in API calls through caching
- No stale data served (proper TTL enforcement)
- Cache operations under 50ms latency

---

### PHASE 7: Real-Time Progress Streaming & User Experience

**Duration**: 1-2 weeks  
**Goal**: Provide transparent, real-time research progress updates

#### Requirements

**Functional Requirements:**
1. **Progress Updates**
   - Stream live updates during research execution
   - Include current operation (searching, reading, analyzing)
   - Show progress percentage and time remaining
   - Display found insights and key findings

2. **Status Messages**
   - Human-readable status messages
   - Categorized by severity (info, warning, error)
   - Include timestamps and operation context
   - Structured format for programmatic parsing

3. **WebSocket Streaming**
   - Implement WebSocket endpoint for live updates
   - Push events as research progresses
   - Handle client reconnection gracefully
   - Buffer messages if client disconnected

4. **Webhook Notifications**
   - Send progress updates to user-defined webhook URL
   - Include completion notifications with results link
   - Retry failed webhook deliveries (3 attempts)
   - Support multiple webhook destinations

**Technical Requirements:**
- Implement event emission system
- Create WebSocket server with Apify Actor.events
- Design webhook delivery with retry logic
- Build progress calculation algorithm

**Deliverables:**
- `src/streaming/progress_streamer.py` - Progress streaming
- `src/streaming/webhook_handler.py` - Webhook delivery
- `src/events/event_emitter.py` - Event system
- API documentation: Streaming endpoints
- `tests/test_phase7.py` - Unit tests for Phase 7

**Success Criteria:**
- Real-time updates with < 1 second latency
- 99% webhook delivery success rate
- Handles 100+ concurrent streaming clients
- Progress estimates accurate within ±15%

---

### PHASE 8: Multi-Source Citation System

**Duration**: 1 week  
**Goal**: Implement transparent, verifiable citation tracking

#### Requirements

**Functional Requirements:**
1. **Inline Citations**
   - Numbered citations in report text [1][2][3]
   - Support multiple sources per claim
   - Hover tooltips with source preview (HTML format)
   - Direct links to cited sections

2. **Source Bibliography**
   - Full bibliographic details for each source
   - Include: Title, URL, Author, Date, Domain, Access Date
   - Support multiple citation styles (APA, MLA, Chicago)
   - Generate formatted reference list

3. **Citation Tracking**
   - Track which sources support which claims
   - Score citation quality (primary vs secondary sources)
   - Identify unsupported claims (no citations)
   - Calculate source diversity score

4. **Source Verification**
   - Flag potentially unreliable sources
   - Identify contradicting sources
   - Provide confidence scores for claims
   - Link to fact-checking sites when available

**Technical Requirements:**
- Design citation data structure (claim → sources mapping)
- Implement citation formatter for multiple styles
- Create source quality scorer
- Build verification logic with domain reputation

**Deliverables:**
- `src/citations/citation_manager.py` - Citation tracking
- `src/citations/bibliography_generator.py` - Reference formatting
- `src/citations/source_verifier.py` - Source quality checks
- `src/citations/styles/` - Citation style templates
- `tests/test_phase8.py` - Unit tests for Phase 8

**Success Criteria:**
- 100% of factual claims have citations
- Citation accuracy verified on sample dataset
- Supports 3+ citation styles correctly
- Source quality scores align with expert assessment

---

### PHASE 9: Domain-Specific Research Plugins

**Duration**: 2 weeks  
**Goal**: Optimize research for specific domains and use cases

#### Requirements

**Functional Requirements:**
1. **Academic Research Plugin**
   - Prioritize peer-reviewed sources (arXiv, PubMed, Google Scholar)
   - Use academic citation style by default
   - Extract methodology and findings sections
   - Include DOI and citation counts

2. **Business Research Plugin**
   - Focus on market reports, company filings (SEC, earnings)
   - Include financial data and metrics
   - Analyze competitor information
   - Generate executive-friendly summaries

3. **Technical Research Plugin**
   - Prioritize documentation, GitHub repos, Stack Overflow
   - Include code examples and technical specs
   - Extract API documentation and usage patterns
   - Generate implementation guides

4. **News Research Plugin**
   - Focus on recent articles (last 30 days)
   - Include fact-checking site verification
   - Track story evolution over time
   - Identify primary vs secondary reporting

5. **Custom Domain Configuration**
   - User-defined source lists
   - Custom scoring weights
   - Domain-specific prompt templates
   - Specialized output formatting

**Technical Requirements:**
- Create plugin architecture with base class
- Implement domain-specific Agno agents
- Design source priority system
- Build plugin registration mechanism

**Deliverables:**
- `src/plugins/base_plugin.py` - Plugin base class
- `src/plugins/academic_plugin.py` - Academic research
- `src/plugins/business_plugin.py` - Business research
- `src/plugins/technical_plugin.py` - Technical research
- `src/plugins/news_plugin.py` - News research
- `src/plugins/plugin_manager.py` - Plugin registry
- `tests/test_phase9.py` - Unit tests for Phase 9

**Success Criteria:**
- Each plugin demonstrates 30%+ better source relevance
- Domain-specific outputs meet user expectations
- Plugin system supports easy extension
- Plugins can be combined (e.g., academic + technical)

---

### PHASE 10: Benchmarking & Quality Assurance

**Duration**: 1-2 weeks  
**Goal**: Validate performance against Perplexity and establish quality baselines

#### Requirements

**Functional Requirements:**
1. **Perplexity Comparison**
   - Run identical queries through Deep Search Actor and Perplexity API
   - Compare response times (target: within 20% of Perplexity)
   - Compare source counts and diversity
   - Evaluate report quality with LLM judge (gpt-4o:20b via Ollama)

2. **Quality Metrics**
   - Accuracy: Fact verification against ground truth
   - Completeness: Coverage of query aspects
   - Coherence: Logical flow and readability
   - Citation Quality: Source reliability and relevance
   - Speed: Time to completion vs complexity

3. **Automated Testing**
   - Build test suite with 50+ diverse queries
   - Include edge cases (ambiguous, complex, niche)
   - Automated regression testing on each release
   - Performance benchmarks (speed, cost, quality)

4. **Quality Scoring**
   - Use Ollama gpt-4o:20b for automated quality assessment
   - Score reports on 0-100 scale across dimensions
   - Compare scores against Perplexity baseline
   - Track quality trends over time

**Technical Requirements:**
- Implement Perplexity API integration
- Create benchmarking harness
- Design LLM-based evaluation prompts
- Build automated test pipeline

**Deliverables:**
- `tests/benchmark/perplexity_comparator.py` - Perplexity comparison
- `tests/benchmark/quality_scorer.py` - LLM-based scoring
- `tests/benchmark/test_suite.py` - Comprehensive test suite
- `tests/benchmark/ollama_judge.py` - Local Ollama integration
- `tests/benchmark/results/` - Benchmark results and reports
- Documentation: Benchmarking methodology
- `scripts/run_benchmarks.sh` - Automated benchmark execution

**Success Criteria:**
- Response time within 120% of Perplexity average
- Quality scores within 10% of Perplexity baseline
- 95%+ test pass rate on regression suite
- Automated benchmarks run in under 30 minutes

---

## 3. Apify Best Practices & Code Quality Standards

Based on Apify's official documentation and community guidelines, this project will follow these standards:

### 3.1 Actor Structure & Organization

**Directory Structure:**
```
deep-search-actor/
├── .actor/
│   ├── actor.json                 # Actor metadata and configuration
│   ├── input_schema.json          # Input validation and UI generation
│   └── output_schema.json         # Output structure definition
├── src/
│   ├── __init__.py
│   ├── main.py                    # Actor entry point
│   ├── agents/                    # Agno agents
│   ├── search/                    # Search API integrations
│   ├── extraction/                # Content extraction
│   ├── analysis/                  # Content analysis
│   ├── reasoning/                 # Reasoning engine
│   ├── report/                    # Report generation
│   ├── cache/                     # Caching layer
│   ├── streaming/                 # Progress streaming
│   ├── citations/                 # Citation management
│   ├── plugins/                   # Domain plugins
│   ├── cost/                      # Cost tracking
│   ├── modes/                     # Research modes
│   └── utils/                     # Shared utilities
├── tests/
│   ├── unit/                      # Unit tests
│   ├── integration/               # Integration tests
│   └── benchmark/                 # Benchmarking suite
├── scripts/
│   ├── run_benchmarks.sh          # Benchmark execution
│   └── deploy.sh                  # Deployment automation
├── Dockerfile                      # Container definition
├── requirements.txt               # Python dependencies
├── README.md                      # User documentation
├── CHANGELOG.md                   # Version history
└── LICENSE                        # Open-source license
```

### 3.2 Code Quality Standards

**Python Style:**
- Follow PEP 8 style guide
- Use type hints for all function signatures
- Maximum line length: 120 characters
- Use docstrings (Google style) for all public functions
- Code formatted with Black (line-length=120)
- Import sorting with isort
- Linting with Ruff or Flake8

**Error Handling:**
- Use try-except blocks for all external API calls
- Log errors with proper context (Actor.log.error)
- Fail gracefully with user-friendly error messages
- Implement retry logic with exponential backoff
- Never expose sensitive data in error messages

**Logging:**
- Use Apify's built-in logging (Actor.log)
- Log levels: DEBUG, INFO, WARNING, ERROR
- Include timestamps and operation context
- Log all external API calls
- Do not log sensitive data (API keys, user data)

### 3.3 Input Validation

**Requirements:**
- Define comprehensive input_schema.json with JSON Schema
- Use Pydantic models for runtime validation
- Provide helpful error messages for invalid inputs
- Set sensible defaults for all optional parameters
- Document all input fields with examples

**Input Schema Best Practices:**
- Use descriptive titles and descriptions
- Provide examples for complex fields
- Use enums for fixed value sets
- Set min/max constraints where applicable
- Group related fields with prefixGroup

### 3.4 Documentation Standards

**README.md Requirements:**
- Clear, concise description (2-3 paragraphs)
- Use simple language, avoid technical jargon
- Include usage examples with screenshots
- Document all input parameters
- Explain output format with examples
- Provide pricing/cost estimates
- Include troubleshooting section
- Link to relevant resources

**Code Documentation:**
- Docstrings for all public functions and classes
- Explain complex algorithms with comments
- Document API integrations and data formats
- Provide usage examples in docstrings

### 3.5 Testing Requirements

**Test Coverage:**
- Minimum 80% code coverage
- Unit tests for all core functions
- Integration tests for Actor workflows
- End-to-end tests for critical paths
- Performance/load tests for scalability

**Test Strategy:**
- Use pytest framework
- Mock external API calls in unit tests
- Use Apify's Actor.apify_client for integration tests
- Implement CI/CD pipeline (GitHub Actions)
- Run tests on every commit

### 3.6 Performance Optimization

**Best Practices:**
- Implement Docker layer caching (copy package.json before source)
- Use async/await for concurrent operations
- Implement connection pooling for APIs
- Minimize memory usage (stream large files)
- Clean up resources in finally blocks
- Monitor memory usage and optimize
- Use Apify's AutoscaledPool for parallel processing

### 3.7 Storage Best Practices

**Key-Value Store:**
- Use for: Single files, reports, state, cache
- Keys: Descriptive names (e.g., "final_report", "search_cache_123")
- Content-Type: Set appropriate MIME types
- Cleanup: Remove temporary data at end of run

**Dataset:**
- Use for: Multiple structured records
- Schema: Consistent across all records
- Push frequently: Don't accumulate in memory
- Include metadata: timestamps, source URLs

### 3.8 Security & Privacy

**Requirements:**
- Store API keys in Actor secrets (APIFY_API_TOKEN)
- Never log or output sensitive data
- Sanitize user inputs to prevent injection
- Use HTTPS for all external requests
- Respect robots.txt and website terms of service
- Implement rate limiting to avoid abuse
- Handle GDPR compliance for EU users

### 3.9 Versioning & Deployment

**Semantic Versioning:**
- MAJOR.MINOR format (e.g., 1.0, 1.1, 2.0)
- MAJOR: Breaking changes
- MINOR: New features, backwards compatible
- Tag releases in Git

**Deployment Process:**
1. Test locally with `apify run --purge`
2. Build Docker image and verify
3. Deploy to Apify platform
4. Test in staging environment
5. Publish to Apify Store (public Actors)
6. Monitor initial runs for issues

### 3.10 Maintenance & Support

**Ongoing Maintenance:**
- Reserve 2 hours/week for maintenance
- Monitor Actor runs for failures
- Review logs for errors and warnings
- Update dependencies quarterly
- Respond to user issues within 48 hours
- Test against website changes
- Update selectors when sites change

---

## 4. Local Testing & Benchmarking Requirements

### 4.1 Local Development Setup

**Requirements:**
```bash
# Prerequisites
- Python 3.11+
- Docker Desktop
- Ollama (for local LLM testing)
- Git

# Setup Steps
1. Clone repository
2. Create virtual environment: python -m venv venv
3. Activate: source venv/bin/activate (Unix) or venv\Scripts\activate (Windows)
4. Install dependencies: pip install -r requirements.txt
5. Install dev dependencies: pip install -r requirements-dev.txt
6. Set environment variables in .env file
7. Run local tests: pytest
```

### 4.2 Local Test Script Requirements

**Purpose:** Compare Deep Search Actor with Perplexity API using local Ollama model

**Script: `tests/benchmark/local_benchmark.py`**

**Requirements:**
1. **Test Queries**
   - Maintain test suite of 20+ diverse queries
   - Include: simple factual, complex analytical, niche topics
   - Store in `tests/benchmark/test_queries.json`

2. **Parallel Execution**
   - Run same query through Deep Search Actor (local mode)
   - Run same query through Perplexity API
   - Execute both simultaneously for fair comparison

3. **Metrics Collection**
   - Response time (seconds)
   - Number of sources used
   - Source quality scores
   - Report length (words)
   - Cost per query (estimated)
   - Token usage (input + output)

4. **Quality Assessment**
   - Use Ollama gpt-4o:20b for intelligent comparison
   - Score both outputs on:
     - Accuracy (0-100)
     - Completeness (0-100)
     - Clarity (0-100)
     - Citation Quality (0-100)
     - Overall Quality (0-100)

5. **Result Storage**
   - Save comparison results to temporary JSON file
   - Include: query, both outputs, metrics, scores
   - Generate comparison report (Markdown)
   - Create visualizations (charts, tables)

6. **Ollama Integration**
   - Use local Ollama instance (http://localhost:11434)
   - Model: gpt-4o:20b (or best available alternative)
   - Prompt: Structured comparison with specific criteria
   - Parse JSON response from Ollama

**Script Output:**
```
Benchmark Results Summary
========================

Test Queries: 20
Deep Search Actor Avg Time: 8.3s
Perplexity API Avg Time: 6.1s
Speed Ratio: 1.36x slower

Deep Search Actor Avg Quality: 87.4
Perplexity API Avg Quality: 91.2
Quality Gap: -3.8 points

Cost Comparison:
- Deep Search Actor: $0.42/query
- Perplexity API: $0.50/query
- Savings: 16%

Detailed results: tests/benchmark/results/benchmark_2025-11-07.json
Report: tests/benchmark/results/benchmark_2025-11-07.md
```

### 4.3 Continuous Benchmarking

**Requirements:**
- Run benchmarks on every release
- Track metrics over time (trend analysis)
- Alert if quality drops below threshold
- Publish benchmark results publicly (transparency)

---

## 5. Dependencies & Environment

### 5.1 Python Dependencies

**Core Dependencies:**
```
# Apify
apify>=1.7.0

# AI & Orchestration
agno>=1.0.0
anthropic>=0.20.0
openai>=1.0.0

# Search APIs
google-api-python-client>=2.0.0
requests>=2.31.0

# Content Extraction
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=4.9.0

# Data Processing
pandas>=2.0.0
pydantic>=2.0.0

# Async
aiohttp>=3.9.0
asyncio>=3.4.3

# Utilities
python-dotenv>=1.0.0
pyyaml>=6.0
```

**Development Dependencies:**
```
# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
pytest-mock>=3.11.0

# Code Quality
black>=23.7.0
isort>=5.12.0
ruff>=0.0.285

# Documentation
mkdocs>=1.5.0
mkdocs-material>=9.2.0
```

### 5.2 Environment Variables

**Required:**
```
# Apify
APIFY_TOKEN=<your_apify_token>

# LLM APIs
ANTHROPIC_API_KEY=<claude_key>
DEEPSEEK_API_KEY=<deepseek_key>

# Search APIs
GOOGLE_SEARCH_API_KEY=<google_key>
GOOGLE_SEARCH_ENGINE_ID=<engine_id>
BRAVE_SEARCH_API_KEY=<brave_key>
BING_SEARCH_API_KEY=<bing_key>

# Benchmark
PERPLEXITY_API_KEY=<perplexity_key>
```

**Optional:**
```
# Monitoring
AGENTOPS_API_KEY=<agentops_key>

# Logging
LOG_LEVEL=INFO
```

---

## 6. Success Criteria & KPIs

### 6.1 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Quick Mode Speed | < 3 min | Average completion time |
| Standard Mode Speed | < 10 min | Average completion time |
| Deep Mode Speed | < 30 min | Average completion time |
| Cache Hit Rate | > 60% | Cached queries / Total queries |
| API Success Rate | > 98% | Successful calls / Total calls |
| Actor Uptime | > 99.5% | Successful runs / Total runs |

### 6.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Report Quality Score | > 85/100 | LLM-based assessment |
| Citation Accuracy | > 99% | Manual verification sample |
| Source Relevance | > 80% | Relevance score distribution |
| User Satisfaction | > 4.5/5 | App Store rating |
| Fact Accuracy | > 95% | Fact-checking against ground truth |

### 6.3 Cost Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Quick Mode Cost | < $0.25 | Average cost per run |
| Standard Mode Cost | < $1.00 | Average cost per run |
| Deep Mode Cost | < $5.00 | Average cost per run |
| Cost Efficiency | > Perplexity | Cost per quality point |

### 6.4 Competitive Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Speed vs Perplexity | Within 150% | Response time comparison |
| Quality vs Perplexity | Within 90-110% | Quality score comparison |
| Cost vs Perplexity | 10-30% cheaper | Price per query comparison |
| Feature Parity | 100% | Feature checklist |

---

## 7. Risk Management

### 7.1 Technical Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| API rate limits | High | Implement multiple API providers, caching |
| LLM quality variance | Medium | Use prompt engineering, model fallbacks |
| Content extraction failures | Medium | Multiple scraping methods, graceful degradation |
| Memory/cost overruns | High | Budget enforcement, progress monitoring |

### 7.2 Business Risks

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Perplexity outperforms significantly | High | Continuous benchmarking, rapid iteration |
| High operational costs | High | Cost optimization, caching, pricing adjustments |
| Low user adoption | Medium | Marketing, documentation, free tier |
| API provider changes | Medium | Multiple providers, monitoring, quick adaptation |

---

## 8. Timeline & Milestones

### 8.1 Development Schedule

| Phase | Duration | Completion Date |
|-------|----------|-----------------|
| Phase 1: Foundation | 2-3 weeks | Week 3 |
| Phase 2: Source Analysis | 2-3 weeks | Week 6 |
| Phase 3: Reasoning | 2 weeks | Week 8 |
| Phase 4: Report Generation | 2 weeks | Week 10 |
| Phase 5: Tiered Modes | 2 weeks | Week 12 |
| Phase 6: Caching | 1-2 weeks | Week 14 |
| Phase 7: Streaming | 1-2 weeks | Week 16 |
| Phase 8: Citations | 1 week | Week 17 |
| Phase 9: Domain Plugins | 2 weeks | Week 19 |
| Phase 10: Benchmarking | 1-2 weeks | Week 21 |

**Total Estimated Duration**: 19-21 weeks (~5 months)

### 8.2 Key Milestones

- **Week 3**: Basic research engine functional
- **Week 6**: Content analysis pipeline complete
- **Week 10**: First complete reports generated
- **Week 12**: All pricing tiers operational
- **Week 16**: Production-ready UX with streaming
- **Week 19**: All domain plugins available
- **Week 21**: Beta launch on Apify Store

---

## 9. Post-Launch Activities

### 9.1 Monitoring & Optimization

- Monitor Actor runs daily for first month
- Collect user feedback and feature requests
- Optimize costs based on actual usage patterns
- A/B test different LLM configurations
- Improve quality based on user ratings

### 9.2 Marketing & Growth

- Publish Actor on Apify Store
- Create demo videos and tutorials
- Write blog posts about use cases
- Engage with Apify community on Discord
- Submit to Apify $1M Challenge
- Reach out to potential enterprise users

### 9.3 Feature Roadmap

**Q1 2026:**
- Multi-language support (translate reports)
- Image analysis capability (process charts, diagrams)
- Collaborative research (team workspaces)

**Q2 2026:**
- Voice input for research queries
- Scheduled research (auto-update reports)
- Research templates library

---

## 10. Appendices

### 10.1 Glossary

- **Actor**: Serverless cloud program on Apify platform
- **Agno**: Lightweight AI agent framework for Python
- **Dataset**: Apify storage for structured records
- **Key-Value Store**: Apify storage for files and objects
- **LLM**: Large Language Model (AI)
- **TTL**: Time To Live (cache expiration)
- **Webhook**: HTTP callback for notifications

### 10.2 References

- [Apify Documentation](https://docs.apify.com)
- [Apify Actor Best Practices](https://docs.apify.com/platform/actors/publishing)
- [Agno Framework](https://docs.agno.com)
- [Perplexity Deep Research](https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research)
- [DeepSeek API](https://platform.deepseek.com)

### 10.3 Contact & Support

- **Project Lead**: [Your Name]
- **Repository**: [GitHub URL]
- **Issues**: [GitHub Issues URL]
- **Email**: [Support Email]

---

## Document Approval

**Version**: 1.0.0  
**Status**: APPROVED FOR IMPLEMENTATION  
**Next Review**: After Phase 5 completion  

---

*This requirements document will be updated as the project evolves. All changes will be tracked in the version control system.*