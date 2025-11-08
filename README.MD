# Deep Search Actor

An intelligent research automation system that transforms complex queries into comprehensive, well-sourced reports through iterative exploration and synthesis.

## Core Philosophy

Traditional search engines return lists of links. Deep Search Actor performs **research**—it explores, analyzes, synthesizes, and presents findings as a cohesive narrative with proper citations and quality assurance.

## How It Works

### The Research Process

1. **Query Decomposition**: Breaks complex questions into focused sub-queries
2. **Iterative Exploration**: Searches multiple sources, building knowledge progressively
3. **Intelligent Analysis**: Evaluates source quality, relevance, and recency
4. **Adaptive Refinement**: Detects knowledge gaps and continues research until comprehensive
5. **Synthesis & Reporting**: Combines findings into structured, well-cited reports

### Key Principles

**🎯 Depth Over Breadth**
- Performs multiple iterative searches rather than single queries
- Adapts research scope based on knowledge gaps detected
- Continues until comprehensive coverage is achieved

**🔍 Quality Over Quantity**
- Prioritizes authoritative sources (academic, verified, recent)
- Scores sources by relevance, recency, and authority
- Filters out low-quality or irrelevant content

**🧠 Intelligent Reasoning**
- Uses LLMs to understand context and relationships
- Detects contradictions and synthesizes multiple perspectives
- Generates insights beyond simple aggregation

**📚 Proper Attribution**
- Tracks all sources with citations
- Supports multiple citation styles (APA, MLA, Chicago, IEEE)
- Links claims to supporting evidence

**⚡ Performance & Cost Optimization**
- Caches results to avoid redundant API calls
- Tracks costs and enforces budget limits
- Provides tiered research modes (quick/standard/deep)

**🎨 Domain-Aware Research**
- Adapts to research context (academic, news, technical, business)
- Prioritizes domain-appropriate sources
- Customizes analysis approach by theme

## Research Modes

**Quick** (5-10 searches, ~$0.10-0.25)
- Fast answers for straightforward questions
- Ideal for quick fact-checking or overviews

**Standard** (20-30 searches, ~$0.50-1.00)
- Balanced depth and speed
- Suitable for most research needs

**Deep** (50-100 searches, ~$2.00-5.00)
- Comprehensive exploration
- For complex topics requiring thorough analysis

## Features

### Core Capabilities
- **Multi-source search** across Google, Brave, Bing APIs
- **Content extraction** from web pages with HTML/text processing
- **Relevance scoring** based on query match, recency, authority
- **Knowledge gap detection** to ensure comprehensive coverage
- **Report generation** in multiple formats (Markdown, HTML, JSON)

### Advanced Features
- **Smart caching** to reduce costs and improve speed
- **Progress streaming** with real-time updates and webhooks
- **Citation management** with multiple style support
- **Domain plugins** for academic, news, technical, business research
- **Quality metrics** for accuracy, completeness, and coherence
- **Diversity analysis** to detect bias and balance perspectives

### User Experience
- **Query templates** for common research patterns (comparison, pros/cons, market analysis)
- **Interactive mode** with preview, pause, and refinement capabilities
- **Customizable output** with configurable sections and writing styles
- **Export formats** including PDF, DOCX, HTML, JSON
- **Sharing capabilities** with public/private links

## Usage

### Basic Example

```json
{
  "query": "What are the latest developments in quantum computing?",
  "maxSearches": 20,
  "researchDepth": "standard",
  "outputFormat": "markdown"
}
```

### Advanced Example

```json
{
  "query": "Compare Python vs JavaScript for web development",
  "maxSearches": 25,
  "researchDepth": "standard",
  "queryTemplate": "comparison",
  "researchTheme": "technical",
  "outputScope": {
    "reportLength": "comprehensive",
    "sections": {
      "executiveSummary": true,
      "keyFindings": true,
      "detailedAnalysis": true,
      "recommendations": true
    }
  },
  "budgetLimit": 1.50
}
```

## Output

The Actor produces:

- **Structured Report**: Comprehensive research report with citations
- **Quality Metrics**: Accuracy, completeness, coherence scores
- **Performance Data**: Execution time, cost breakdown, cache statistics
- **Source Analysis**: Diversity metrics, citation coverage, quality assessment

## Architecture Principles

**Modular Design**: Each phase (search, analysis, reasoning, reporting) is independently testable and replaceable

**Resumable Execution**: Research state can be saved and resumed from failure points

**Cost Transparency**: All operations tracked with detailed cost breakdowns

**Quality Assurance**: Built-in benchmarking and quality metrics

**Extensibility**: Plugin system for domain-specific research approaches

## Testing

See `tests/TEST_README.md` for comprehensive phase-by-phase testing guide with ready-to-use JSON inputs.

## Requirements

- Python 3.11+
- API keys for search engines (Google, Brave, Bing)
- LLM API access (Anthropic Claude or OpenAI-compatible)
- See `rquirements.txt` for full dependency list

## License

This Actor is designed for research automation and can be customized for specific use cases.

---

**Transform questions into research. Transform research into knowledge.**
