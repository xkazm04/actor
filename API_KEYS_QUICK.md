# Quick API Keys Setup for Testing

## Minimum Required Keys

To run the basic test (`phase1.1`), you need:

### 1. LLM API Key (Required)
```bash
ANTHROPIC_API_KEY=sk-ant-api03-YOUR_KEY_HERE
```

**Get it from**: https://console.anthropic.com/

### 2. Search API (Required)

**Primary: Serp API** (Recommended)
```bash
SERP_API_KEY=YOUR_SERP_API_KEY
```

**Fallbacks** (Optional but recommended):
- **Google Search**: `GOOGLE_SEARCH_API_KEY` + `GOOGLE_SEARCH_ENGINE_ID`
- **Brave Search**: `BRAVE_SEARCH_API_KEY`
- **Bing Search**: `BING_SEARCH_API_KEY`

## Setting in Apify Console

1. Go to your Actor: https://console.apify.com/actors/YOUR_ACTOR_ID
2. Click **Settings** → **Environment Variables**
3. Add each key-value pair
4. Save and rebuild Actor

## Testing

After setting keys, run:
```bash
python tests/library/run_test.py phase1.1
```

## Common Issues

**"invalid x-api-key"** → Check your Anthropic API key format (should start with `sk-ant-`)

**"No search APIs configured"** → Add `SERP_API_KEY` (primary) or fallback search API keys

See `API_KEYS.md` for detailed setup instructions.

