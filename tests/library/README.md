# Test Library Configuration

## Setup

1. **Configure Actor Connection**
   - Set `APIFY_TOKEN` environment variable (recommended for security)
   - Or set `apifyToken` in `config.json` (not recommended for production)

2. **Install Dependencies**
   ```bash
   pip install apify-client
   ```

## Configuration File (config.json)

```json
{
  "actorId": "YOUR_ACTOR_ID",
  "actorVersion": "latest",
  "apifyToken": null,
  "timeout": 3600,
  "waitForFinish": true,
  "webhookUrl": null
}
```

- `actorId`: Your Actor ID on Apify platform
- `actorVersion`: Actor version to use (default: "latest")
- `apifyToken`: Apify API token (set to `null` and use `APIFY_TOKEN` env var instead for security)
- `timeout`: Maximum wait time in seconds (default: 3600)
- `waitForFinish`: Wait for Actor to finish (default: true)
- `webhookUrl`: Optional webhook URL for notifications

**⚠️ Security Note**: Never commit API tokens to version control! Always use `APIFY_TOKEN` environment variable.

## Usage

### Run a Single Test

```bash
python tests/library/run_test.py phase1.1
```

### List All Tests

```bash
python tests/library/run_test.py --list
```

### Run All Tests in a Phase

```bash
python tests/library/run_test.py --phase "Phase 1"
```

### Run All Tests

```bash
python tests/library/run_test.py --all
```

### Using the Connector Directly

```python
from tests.library.connector import ActorConnector

connector = ActorConnector()
result = connector.run_actor({
    "query": "What is machine learning?",
    "maxSearches": 15,
    "researchDepth": "standard"
})

# Get dataset items
items = connector.get_dataset_items(result['defaultDatasetId'])

# Get output from key-value store
output = connector.get_key_value_store_value(result['defaultKeyValueStoreId'])
```

### Using the Test Runner

```python
from tests.library.run_test import TestRunner

runner = TestRunner()

# Run a specific test
result = runner.run_test("phase1.1")

# List tests
tests = runner.list_tests()

# Run all tests in a phase
results = runner.run_phase("Phase 1")

# Run all tests
results = runner.run_all()
```

## Test Queries

All test queries are stored in `queries.json` with the following structure:

```json
{
  "testId": "phase1.1",
  "phase": "Phase 1",
  "name": "Basic Query Validation",
  "description": "Actor accepts input, validates query length...",
  "input": {
    "query": "...",
    "maxSearches": 10,
    "researchDepth": "quick"
  }
}
```

## Test IDs

Tests are organized by phase:
- `phase1.1` through `phase1.4`: Phase 1 tests
- `phase2.1` through `phase2.3`: Phase 2 tests
- `phase3.1` through `phase3.3`: Phase 3 tests
- `phase4.1` through `phase4.4`: Phase 4 tests
- `phase5.1` through `phase5.3`: Phase 5 tests
- `phase6.1` through `phase6.3`: Phase 6 tests
- `phase7.1` through `phase7.3`: Phase 7 tests
- `phase8.1` through `phase8.4`: Phase 8 tests
- `phase9.1` through `phase9.5`: Phase 9 tests
- `phase10.1` through `phase10.3`: Phase 10 tests
- `ux1.1` through `ux1.3`: UX1 tests
- `ux2.1` through `ux2.2`: UX2 tests
- `ux3.1` through `ux3.2`: UX3 tests
- `ux5.1` through `ux5.2`: UX5 tests
- `ux6.1` through `ux6.2`: UX6 tests
- `ux8.1` through `ux8.2`: UX8 tests

## Output

Test results include:
- Test metadata (testId, testName, phase)
- Run information (runId, status)
- Timing information (startTime, duration)
- Dataset items (if available)
- Key-value store output (if available)
- Error information (if failed)

## Notes

1. Make sure your Actor is deployed and accessible before running tests
2. Set appropriate timeout values for long-running tests
3. Use webhook URLs for async testing if needed
4. Tests include small delays between runs to avoid rate limiting

