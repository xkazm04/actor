# API Keys Configuration Guide

This guide explains which API keys are required for the Deep Search Actor and how to configure them.

## Required API Keys

### 1. LLM API Keys (Required)

The Actor uses LLM APIs for query decomposition, reasoning, and report generation. You need **at least one** of these:

#### Option A: Anthropic Claude (Recommended)
- **Environment Variable**: `ANTHROPIC_API_KEY`
- **Where to get it**: https://console.anthropic.com/
- **Used for**: Query decomposition, reasoning, report generation, content analysis
- **Format**: `sk-ant-api03-...` (starts with `sk-ant-`)

#### Option B: DeepSeek API
- **Environment Variable**: `DEEPSEEK_API_KEY`
- **Where to get it**: https://platform.deepseek.com/
- **Used for**: Query decomposition, reasoning (as fallback)
- **Format**: Usually starts with `sk-...`

**Note**: The Actor prefers `DEEPSEEK_API_KEY` but falls back to `ANTHROPIC_API_KEY` if DeepSeek is not available.

### 2. Search API Keys (At least one required)

The Actor needs at least one search API to fetch results. **Serp API is the primary search method** - other APIs are used as fallbacks.

#### Serp API (Primary - Recommended)
- **Environment Variable**: `SERP_API_KEY`
- **Where to get it**: https://serpapi.com/
- **Used for**: Primary search method (provides Google search results via API)
- **Limits**: Free tier: 100 searches/month, paid plans available
- **Format**: Usually starts with `...` (get from SerpApi dashboard)
- **Note**: This is the PRIMARY search method. Other APIs are fallbacks.

#### Google Custom Search API (Fallback)
- **Environment Variables**: 
  - `GOOGLE_SEARCH_API_KEY`
  - `GOOGLE_SEARCH_ENGINE_ID`
- **Where to get it**: 
  1. Go to https://console.cloud.google.com/
  2. Create a project or select existing
  3. Enable "Custom Search API"
  4. Create credentials → API Key
  5. Create a Custom Search Engine at https://programmablesearchengine.google.com/
  6. Get your Search Engine ID (CX)
- **Limits**: 100 queries/day free tier, 10 results per request

#### Brave Search API
- **Environment Variable**: `BRAVE_SEARCH_API_KEY`
- **Where to get it**: https://brave.com/search/api/
- **Limits**: Free tier available, 20 results per request
- **Format**: Usually starts with `BSA...`

#### Bing Search API
- **Environment Variable**: `BING_SEARCH_API_KEY`
- **Where to get it**: 
  1. Go to https://portal.azure.com/
  2. Create "Bing Search v7" resource
  3. Get your subscription key
- **Limits**: Free tier: 3,000 queries/month, 50 results per request
- **Format**: Usually a 32-character alphanumeric string

## Minimum Configuration

For basic functionality, you need:

1. **One LLM API key** (either `ANTHROPIC_API_KEY` or `DEEPSEEK_API_KEY`)
2. **At least one search API**:
   - **Primary**: `SERP_API_KEY` (recommended)
   - **Fallbacks**: Google, Brave, or Bing (optional but recommended for redundancy)

## Recommended Configuration

For best results and redundancy:

1. **LLM**: `ANTHROPIC_API_KEY` (for Claude Sonnet 4)
2. **Search APIs**: 
   - **Primary**: `SERP_API_KEY` (required)
   - **Fallbacks**: Configure Google, Brave, and/or Bing for redundancy

## Setting Environment Variables

### On Apify Platform

1. Go to your Actor settings in Apify Console
2. Navigate to **Environment Variables** section
3. Add each key-value pair:
   ```
   ANTHROPIC_API_KEY = sk-ant-api03-...
   SERP_API_KEY = your-serp-api-key
   GOOGLE_SEARCH_API_KEY = your-google-key (optional fallback)
   GOOGLE_SEARCH_ENGINE_ID = your-engine-id (optional fallback)
   BRAVE_SEARCH_API_KEY = BSA... (optional fallback)
   BING_SEARCH_API_KEY = your-bing-key (optional fallback)
   ```

### For Local Testing

#### Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-api03-..."
$env:GOOGLE_SEARCH_API_KEY = "your-key"
$env:GOOGLE_SEARCH_ENGINE_ID = "your-id"
```

#### Windows CMD:
```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-...
set GOOGLE_SEARCH_API_KEY=your-key
set GOOGLE_SEARCH_ENGINE_ID=your-id
```

#### Linux/Mac:
```bash
export ANTHROPIC_API_KEY="sk-ant-api03-..."
export GOOGLE_SEARCH_API_KEY="your-key"
export GOOGLE_SEARCH_ENGINE_ID="your-id"
```

### Using .env file (for local development)

Create a `.env` file in the project root:
```env
ANTHROPIC_API_KEY=sk-ant-api03-...
DEEPSEEK_API_KEY=sk-...
GOOGLE_SEARCH_API_KEY=your-google-key
GOOGLE_SEARCH_ENGINE_ID=your-engine-id
BRAVE_SEARCH_API_KEY=BSA...
BING_SEARCH_API_KEY=your-bing-key
```

Then load it with `python-dotenv` (already in requirements).

## Troubleshooting

### Error: "invalid x-api-key"

This error typically means:
1. **Wrong API key format** - Check that your API key is correct
2. **Expired or revoked key** - Generate a new key
3. **Wrong environment variable name** - Verify spelling matches exactly
4. **API key not set** - Ensure environment variable is set in Actor settings

### Error: "No search APIs configured"

This means none of the search API keys are set. You need at least one:
- **Primary**: `SERP_API_KEY` (recommended)
- **Fallbacks** (optional but recommended):
  - `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`
  - OR `BRAVE_SEARCH_API_KEY`
  - OR `BING_SEARCH_API_KEY`

### Error: "API key required. Set DEEPSEEK_API_KEY or ANTHROPIC_API_KEY"

This means no LLM API key is configured. Set either:
- `ANTHROPIC_API_KEY` (recommended)
- OR `DEEPSEEK_API_KEY`

## Quick Setup Checklist

- [ ] Get Anthropic API key from https://console.anthropic.com/
- [ ] Set `ANTHROPIC_API_KEY` in Actor environment variables
- [ ] Get Serp API key from https://serpapi.com/ (Primary search method)
- [ ] Set `SERP_API_KEY` in Actor environment variables
- [ ] (Optional) Get fallback search API keys:
  - [ ] Google: API key + Engine ID
  - [ ] OR Brave: API key
  - [ ] OR Bing: API key
- [ ] Set fallback search API keys in Actor environment variables
- [ ] Test with a simple query

## Cost Considerations

- **Anthropic Claude**: Pay-per-use, ~$0.003 per 1K input tokens
- **Serp API**: Free tier: 100 searches/month, then pay-per-use (varies by plan)
- **Google Search**: 100 free queries/day, then $5 per 1,000 queries (fallback only)
- **Brave Search**: Free tier available, paid plans available (fallback only)
- **Bing Search**: 3,000 free queries/month, then pay-per-use (fallback only)

## Security Notes

⚠️ **Never commit API keys to version control!**
- Use environment variables
- Use Apify's secure environment variable storage
- Rotate keys regularly
- Use separate keys for development and production

