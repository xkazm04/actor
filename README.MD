# Deep Search Actor - Basic Skeleton

A basic Python Actor skeleton demonstrating deep search capabilities on Apify platform.

## 🎯 What This Actor Does

This Actor performs in-depth research on any topic by:
1. Breaking down complex queries into sub-queries
2. Performing multiple iterative searches
3. Analyzing and synthesizing information from sources
4. Generating a comprehensive research report

## 📋 How It Works

### The Actor Flow

```
User Input → Initialize Actor → Process Query → Generate Report → Save Results
```

**Step-by-step:**

1. **Input**: User provides a research query and configuration
2. **Query Breakdown**: Main query is decomposed into focused sub-queries
3. **Iterative Search**: Each sub-query is searched, building knowledge progressively
4. **Source Analysis**: Content is fetched and analyzed for relevance
5. **Report Generation**: Findings are synthesized into a structured report
6. **Output**: Results saved to Apify dataset and key-value store

### Key Components

- **`deep_search_actor.py`**: Main Actor logic
- **`input_schema.json`**: Defines user inputs and UI
- **`Dockerfile`**: Container configuration
- **`requirements.txt`**: Python dependencies

## 🚀 Usage

### On Apify Platform

1. Create a new Actor in Apify Console
2. Upload these files
3. Build and run
4. Provide a research query

### Input Parameters

```json
{
  "query": "What are the latest developments in quantum computing?",
  "maxSearches": 5,
  "researchDepth": "standard",
  "outputFormat": "markdown"
}
```

### Output

The Actor produces:
- **Dataset**: Structured JSON with query, report, metadata
- **Key-value store**: Full report under "OUTPUT" key

## 🔧 Next Steps for Real Implementation

This is a **skeleton** - here's what you'd need to add:

### 1. Real Search Integration
```python
# Replace mock search with actual APIs:
- Google Custom Search API
- Brave Search API
- Bing Search API
- Or call other Apify Actors (Web Scraper, Google Search scraper)
```

### 2. LLM Integration
```python
# Add LLM calls for:
- Query breakdown (GPT-4, Claude, DeepSeek)
- Content analysis and summarization
- Report generation
```

### 3. Content Extraction
```python
# Use real scraping:
- Playwright for JavaScript-heavy sites
- Crawl4AI for content extraction
- Beautiful Soup for HTML parsing
- Call existing Apify scrapers
```

### 4. Advanced Features
- Caching to reduce costs
- Progress streaming
- Citation tracking
- Domain-specific research modes
- Quality scoring for sources

## 💡 Understanding Apify Actor Mechanism

### Core Pattern

All Apify Actors follow this pattern:

```python
from apify import Actor

async def main():
    async with Actor:
        # 1. Get input
        input_data = await Actor.get_input()
        
        # 2. Do work
        result = process(input_data)
        
        # 3. Save output
        await Actor.push_data(result)

# Run the Actor
asyncio.run(main())
```

### Storage Options

**Dataset** (for multiple results):
```python
await Actor.push_data({'item': 'data'})
```

**Key-Value Store** (for single files/objects):
```python
await Actor.set_value('OUTPUT', report)
```

### Logging

```python
Actor.log.info('Information message')
Actor.log.warning('Warning message')
Actor.log.error('Error message')
```

## 📊 Pricing Strategy

For the real Actor, consider:
- **Pay-per-event**: Charge per search performed ($0.02-0.05 per search)
- **Tiered pricing**: Quick/Standard/Deep modes at different price points
- **Compute time**: Apify charges for platform usage automatically

## 🎓 Resources

- [Apify Documentation](https://docs.apify.com)
- [Apify Python SDK](https://docs.apify.com/sdk/python)
- [Apify $1M Challenge](https://apify.com/challenge)

## 📝 License

This is a basic example for educational purposes. Customize and extend as needed!