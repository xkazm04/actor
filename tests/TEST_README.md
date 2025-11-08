# Actor Testing Guide

This guide provides incremental, phase-by-phase testing instructions for the Deep Search Actor. Each phase includes ready-to-use JSON inputs that validate the core principles and features of that phase.

## Overview

The Actor is organized into 10 core phases plus UX improvements. Test each phase sequentially to validate functionality before moving to the next.

---

## Phase 1: Foundation & Core Research Engine

**Core Principles:**
- Input validation (query length, research depth modes)
- Query decomposition into sub-queries
- Multi-search engine with API fallback
- Basic research orchestration

### Test Inputs

#### Test 1.1: Basic Query Validation
```json
{
  "query": "What are the latest developments in quantum computing?",
  "maxSearches": 10,
  "researchDepth": "quick"
}
```

**Expected:** Actor accepts input, validates query length, and begins research with quick mode (5-10 searches).

#### Test 1.2: Standard Depth Research
```json
{
  "query": "How does machine learning differ from traditional programming approaches?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Actor performs standard depth research (20-30 searches), decomposes query into multiple sub-queries.

#### Test 1.3: Deep Research Mode
```json
{
  "query": "What are the environmental impacts of renewable energy adoption worldwide?",
  "maxSearches": 50,
  "researchDepth": "deep"
}
```

**Expected:** Actor performs comprehensive research (50-100 searches), creates detailed sub-query breakdown.

#### Test 1.4: Query Sanitization
```json
{
  "query": "  What   is   artificial   intelligence?  ",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Expected:** Query is sanitized (excessive whitespace removed), research proceeds normally.

---

## Phase 2: Smart Source Analysis & Content Extraction

**Core Principles:**
- Content fetching from URLs
- HTML/text processing and chunking
- Relevance scoring (relevance, recency, authority)
- Source ranking

### Test Inputs

#### Test 2.1: Content Extraction
```json
{
  "query": "What are the health benefits of regular exercise?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Expected:** Actor fetches content from search results, processes HTML/text, extracts meaningful chunks.

#### Test 2.2: Authority Source Prioritization
```json
{
  "query": "What are the latest findings in climate change research?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Academic sources (.edu, .org) are scored higher, ranked near top of results.

#### Test 2.3: Recency Scoring
```json
{
  "query": "What are the latest developments in AI in 2025?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Expected:** Recent sources (2024-2025) are prioritized over older content.

---

## Phase 3: Intelligent Reasoning & Research Plan Refinement

**Core Principles:**
- Research plan creation with goals and milestones
- Knowledge gap detection
- Adaptive research continuation
- Progress assessment

### Test Inputs

#### Test 3.1: Research Planning
```json
{
  "query": "What are the pros and cons of remote work?",
  "maxSearches": 25,
  "researchDepth": "standard"
}
```

**Expected:** Actor creates initial research plan with goals, milestones, and estimated searches.

#### Test 3.2: Gap Detection & Adaptive Research
```json
{
  "query": "How do different programming languages compare in terms of performance and ease of use?",
  "maxSearches": 30,
  "researchDepth": "standard"
}
```

**Expected:** Actor detects knowledge gaps, continues research adaptively until coverage is sufficient.

#### Test 3.3: Early Completion
```json
{
  "query": "What is Python programming?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Actor detects sufficient coverage early, completes research before max_searches limit.

---

## Phase 4: Report Generation & Structured Output

**Core Principles:**
- Citation management and linking
- Multiple output formats (markdown, HTML, JSON)
- Bibliography generation (APA, MLA, Chicago)
- Structured report sections

### Test Inputs

#### Test 4.1: Markdown Report
```json
{
  "query": "What are the key features of TypeScript?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "outputFormat": "markdown"
}
```

**Expected:** Report generated in markdown format with inline citations [1][2] and bibliography.

#### Test 4.2: HTML Report
```json
{
  "query": "What are the benefits of cloud computing?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "outputFormat": "html"
}
```

**Expected:** Report generated in HTML format with styled citations and bibliography.

#### Test 4.3: JSON Report
```json
{
  "query": "What is the history of the internet?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "outputFormat": "json"
}
```

**Expected:** Report generated in structured JSON format with citations array and metadata.

#### Test 4.4: APA Citation Style
```json
{
  "query": "What are the effects of social media on mental health?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputFormat": "markdown",
  "themeOptions": {
    "academic": {
      "citationStyle": "APA"
    }
  }
}
```

**Expected:** Bibliography formatted in APA style with proper author-date citations.

---

## Phase 5: Tiered Research Modes & Cost Optimization

**Core Principles:**
- Cost tracking (LLM calls, search APIs, content fetching)
- Budget enforcement
- Mode-specific cost/time estimates
- Cost breakdown reporting

### Test Inputs

#### Test 5.1: Quick Mode Cost Tracking
```json
{
  "query": "What is React?",
  "maxSearches": 10,
  "researchDepth": "quick",
  "budgetLimit": 0.50
}
```

**Expected:** Actor tracks costs, stays within $0.50 budget, provides cost breakdown in results.

#### Test 5.2: Budget Enforcement
```json
{
  "query": "What are the comprehensive impacts of artificial intelligence on society?",
  "maxSearches": 100,
  "researchDepth": "deep",
  "budgetLimit": 1.00
}
```

**Expected:** Actor stops research when budget limit reached, reports budget exceeded.

#### Test 5.3: Cost Breakdown
```json
{
  "query": "What are the latest trends in web development?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Results include detailed cost breakdown: LLM calls, search API calls, content fetching.

---

## Phase 6: Smart Caching & Performance Optimization

**Core Principles:**
- Search result caching
- Content caching
- Similarity detection for query reuse
- Cache hit/miss statistics

### Test Inputs

#### Test 6.1: Cache Hit (Repeat Query)
```json
{
  "query": "What is machine learning?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Run this query twice.**  
**Expected:** Second run uses cached results, faster execution, cache statistics show hits.

#### Test 6.2: Similar Query Detection
```json
{
  "query": "What is artificial intelligence?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**After Test 6.1, run this similar query.**  
**Expected:** Actor detects similarity, reuses relevant cached content, improves performance.

#### Test 6.3: Cache Statistics
```json
{
  "query": "What are the benefits of exercise?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Expected:** Results include cache statistics: hit rate, miss rate, performance improvement.

---

## Phase 7: Real-Time Progress Streaming & User Experience

**Core Principles:**
- Progress events (percentage, current step, total steps)
- Status updates
- Webhook notifications
- Event history

### Test Inputs

#### Test 7.1: Progress Tracking
```json
{
  "query": "What are the key principles of design?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Actor emits progress events throughout execution (0%, 25%, 50%, 75%, 100%).

#### Test 7.2: Webhook Notifications
```json
{
  "query": "What is the history of photography?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "webhookUrl": "https://webhook.site/your-unique-id"
}
```

**Expected:** Webhook receives progress updates and completion notification with full results.

#### Test 7.3: Status Events
```json
{
  "query": "What are the latest developments in renewable energy?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Status events emitted for major milestones: "Query decomposed", "Searching sources", "Analyzing content", "Generating report".

---

## Phase 8: Multi-Source Citation System

**Core Principles:**
- Multiple citation styles (APA, MLA, Chicago, IEEE)
- Source verification (academic, fact-check)
- Citation quality scoring
- Citation coverage analysis

### Test Inputs

#### Test 8.1: Multiple Citation Styles
```json
{
  "query": "What are the environmental impacts of electric vehicles?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputFormat": "markdown",
  "themeOptions": {
    "academic": {
      "citationStyle": "APA"
    }
  }
}
```

**Expected:** Citations formatted in APA style, bibliography includes proper formatting.

#### Test 8.2: MLA Citation Style
```json
{
  "query": "What are the cultural impacts of social media?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputFormat": "markdown",
  "themeOptions": {
    "academic": {
      "citationStyle": "MLA"
    }
  }
}
```

**Expected:** Citations formatted in MLA style with "Works Cited" section.

#### Test 8.3: Source Verification
```json
{
  "query": "What are the verified health benefits of meditation?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Academic sources (.edu) and fact-check sites verified, quality scores included.

#### Test 8.4: Citation Coverage
```json
{
  "query": "What are the economic impacts of remote work?",
  "maxSearches": 25,
  "researchDepth": "standard"
}
```

**Expected:** Report includes citation coverage analysis: percentage of claims supported, unsupported claims identified.

---

## Phase 9: Domain-Specific Research Plugins

**Core Principles:**
- Domain detection (academic, news, technical, business)
- Plugin-specific source preferences
- Customized query decomposition
- Combined plugin configurations

### Test Inputs

#### Test 9.1: Academic Research Plugin
```json
{
  "query": "What are the latest findings in quantum computing research?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "researchTheme": "academic",
  "themeOptions": {
    "academic": {
      "citationStyle": "APA",
      "includeDOI": true,
      "minCitationCount": 5
    }
  }
}
```

**Expected:** Actor prioritizes academic sources (arXiv, PubMed, .edu), uses APA citations, includes DOIs.

#### Test 9.2: News Research Plugin
```json
{
  "query": "What are the latest developments in AI technology?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "researchTheme": "news",
  "themeOptions": {
    "news": {
      "recencyBias": "very_recent",
      "perspectiveDiversity": true,
      "factCheckRequired": true
    }
  }
}
```

**Expected:** Actor prioritizes recent news sources (Reuters, BBC), balances perspectives, fact-checks claims.

#### Test 9.3: Technical Research Plugin
```json
{
  "query": "How do I implement authentication in Node.js?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "researchTheme": "technical",
  "themeOptions": {
    "technical": {
      "includeCodeExamples": true,
      "documentationPriority": true
    }
  }
}
```

**Expected:** Actor prioritizes technical sources (GitHub, Stack Overflow, docs), includes code examples.

#### Test 9.4: Business Research Plugin
```json
{
  "query": "What is the market analysis for cloud computing services?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "researchTheme": "business",
  "themeOptions": {
    "business": {
      "includeFinancials": true,
      "competitorAnalysis": true,
      "marketSizeEstimates": true
    }
  }
}
```

**Expected:** Actor prioritizes business sources (SEC filings, Bloomberg), includes financial data and market analysis.

#### Test 9.5: Auto-Detect Theme
```json
{
  "query": "What are the latest research papers on machine learning?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "researchTheme": "auto_detect"
}
```

**Expected:** Actor auto-detects academic theme, applies appropriate plugin configuration.

---

## Phase 10: Benchmarking & Quality Assurance

**Core Principles:**
- Quality metrics (accuracy, completeness, coherence, citation quality)
- Performance monitoring
- LLM-based quality evaluation
- Benchmark comparisons

### Test Inputs

#### Test 10.1: Quality Metrics
```json
{
  "query": "What are the key principles of effective leadership?",
  "maxSearches": 20,
  "researchDepth": "standard"
}
```

**Expected:** Results include quality metrics: accuracy score, completeness score, coherence score, citation quality score.

#### Test 10.2: Performance Monitoring
```json
{
  "query": "What is the history of the internet?",
  "maxSearches": 15,
  "researchDepth": "standard"
}
```

**Expected:** Results include performance metrics: total time, speed score, milestone timings.

#### Test 10.3: Quality Report
```json
{
  "query": "What are the environmental benefits of renewable energy?",
  "maxSearches": 25,
  "researchDepth": "standard"
}
```

**Expected:** Results include comprehensive quality report with overall quality score and recommendations.

---

## UX Improvements Testing

### UX1: Smart Query Builder

**Core Principles:**
- Query templates (comparison, pros/cons, market analysis)
- Query validation and suggestions
- Interactive query assistance

#### Test UX1.1: Query Template - Comparison
```json
{
  "query": "Compare Python vs JavaScript",
  "maxSearches": 20,
  "researchDepth": "standard",
  "queryTemplate": "comparison"
}
```

**Expected:** Actor uses comparison template, structures report as comparison.

#### Test UX1.2: Query Template - Pros & Cons
```json
{
  "query": "What are the pros and cons of remote work?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "queryTemplate": "pros_cons"
}
```

**Expected:** Actor structures report with pros/cons sections.

#### Test UX1.3: Query Validation
```json
{
  "query": "AI",
  "maxSearches": 10,
  "researchDepth": "quick"
}
```

**Expected:** Actor validates query, suggests improvements for too-short query.

---

### UX2: Output Scope Customization

**Core Principles:**
- Customizable report sections
- Writing style options
- Report length presets

#### Test UX2.1: Custom Sections
```json
{
  "query": "What are the impacts of climate change?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputScope": {
    "reportLength": "comprehensive",
    "sections": {
      "executiveSummary": true,
      "keyFindings": true,
      "detailedAnalysis": true,
      "methodology": true,
      "expertOpinions": true,
      "statistics": true,
      "caseStudies": true,
      "futureTrends": true,
      "recommendations": true,
      "bibliography": true
    }
  }
}
```

**Expected:** Report includes all requested sections with comprehensive detail.

#### Test UX2.2: Writing Style
```json
{
  "query": "What is quantum computing?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputScope": {
    "writingStyle": {
      "tone": "academic",
      "readingLevel": "expert",
      "perspective": "objective"
    }
  }
}
```

**Expected:** Report written in academic tone, expert reading level, objective perspective.

---

### UX3: Interactive Mode

**Core Principles:**
- Preview mode (free)
- Pause and resume
- Refinement requests

#### Test UX3.1: Preview Mode
```json
{
  "query": "What are the latest AI developments?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "previewOnly": true
}
```

**Expected:** Actor generates preview without full execution, shows research plan and estimated costs.

#### Test UX3.2: Interactive Mode
```json
{
  "query": "What are the benefits of exercise?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "interactiveMode": true
}
```

**Expected:** Actor provides preview, allows pause/resume, supports refinement requests.

---

### UX5: Diversity Analysis

**Core Principles:**
- Source diversity analysis
- Perspective balancing
- Bias detection

#### Test UX5.1: Diversity Analysis
```json
{
  "query": "What are the impacts of social media on society?",
  "maxSearches": 25,
  "researchDepth": "standard",
  "enableDiversityAnalysis": true,
  "diversityThreshold": 70
}
```

**Expected:** Results include diversity analysis: source diversity score, domain distribution, perspective breakdown.

#### Test UX5.2: Perspective Balancing
```json
{
  "query": "What are the effects of climate change policies?",
  "maxSearches": 25,
  "researchDepth": "standard",
  "enablePerspectiveBalancing": true,
  "targetPerspectiveDistribution": {
    "left": 0.3,
    "right": 0.3,
    "center": 0.4
  }
}
```

**Expected:** Actor balances sources across perspectives, reports distribution achieved.

---

### UX6: Export Formats

**Core Principles:**
- Multiple export formats
- Format-specific options
- Sharing capabilities

#### Test UX6.1: Multiple Export Formats
```json
{
  "query": "What are the key features of TypeScript?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "outputFormat": "markdown",
  "exportFormats": ["pdf", "html", "json"]
}
```

**Expected:** Report exported in markdown, PDF, HTML, and JSON formats.

#### Test UX6.2: HTML Format Options
```json
{
  "query": "What is the history of computing?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "outputFormat": "html",
  "formatOptions": {
    "html": {
      "theme": "professional",
      "responsive": true,
      "printOptimized": true
    }
  }
}
```

**Expected:** HTML report uses professional theme, responsive design, print-optimized.

---

### UX8: Sharing & Collaboration

**Core Principles:**
- Shareable links
- Public/private sharing
- Password protection

#### Test UX8.1: Shareable Link
```json
{
  "query": "What are the latest trends in web development?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "enableSharing": true,
  "sharingOptions": {
    "shareableLink": true,
    "expirationDays": 30,
    "passwordProtected": false
  }
}
```

**Expected:** Results include shareable link with 30-day expiration.

#### Test UX8.2: Public Link
```json
{
  "query": "What are the benefits of open source software?",
  "maxSearches": 15,
  "researchDepth": "standard",
  "enableSharing": true,
  "sharingOptions": {
    "publicLink": true,
    "passwordProtected": false
  }
}
```

**Expected:** Results include permanent public link to report.

---

## Testing Checklist

Use this checklist to track your testing progress:

- [ ] Phase 1: Foundation & Core Research Engine
- [ ] Phase 2: Smart Source Analysis & Content Extraction
- [ ] Phase 3: Intelligent Reasoning & Research Plan Refinement
- [ ] Phase 4: Report Generation & Structured Output
- [ ] Phase 5: Tiered Research Modes & Cost Optimization
- [ ] Phase 6: Smart Caching & Performance Optimization
- [ ] Phase 7: Real-Time Progress Streaming & User Experience
- [ ] Phase 8: Multi-Source Citation System
- [ ] Phase 9: Domain-Specific Research Plugins
- [ ] Phase 10: Benchmarking & Quality Assurance
- [ ] UX1: Smart Query Builder
- [ ] UX2: Output Scope Customization
- [ ] UX3: Interactive Mode
- [ ] UX5: Diversity Analysis
- [ ] UX6: Export Formats
- [ ] UX8: Sharing & Collaboration

---

## Notes

1. **API Keys**: Some features require API keys (Google Search, Brave Search, Bing, Anthropic, OpenAI). Ensure these are configured in your Actor environment.

2. **Cost Considerations**: Deep research modes consume more API credits. Start with quick/standard modes for initial testing.

3. **Cache Testing**: For Phase 6, run queries multiple times or use similar queries to test caching behavior.

4. **Webhook Testing**: For Phase 7, use a webhook testing service like webhook.site to receive notifications.

5. **Expected Results**: Focus on validating that core principles work. Exact content may vary based on current web sources.

6. **Error Handling**: Test with invalid inputs to ensure graceful error handling (e.g., invalid URLs, exceeded budgets).

---

## Quick Start

1. Start with **Phase 1, Test 1.1** - Basic query validation
2. Progress sequentially through each phase
3. Validate core principles before moving to next phase
4. Use UX tests to validate user experience features
5. Complete Phase 10 to validate overall quality and performance

Good luck with your testing! 🚀

