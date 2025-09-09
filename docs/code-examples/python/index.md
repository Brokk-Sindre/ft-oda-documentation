---
title: Python Client Library - Danish Parliament API Code Examples
description: Production-ready Python client for the Danish Parliament API (oda.ft.dk) with error handling, pagination, and async support. Complete code examples and tutorials.
keywords: python api client, danish parliament api python, oda.ft.dk python, parliamentary data python, api wrapper python
---

# Python Client Library

A production-ready Python client for the Danish Parliament API (oda.ft.dk) with comprehensive error handling, pagination support, and async capabilities.

## Installation

```bash
pip install requests  # Required dependency
# For async support:
pip install aiohttp
```

## Quick Start

```python
from danish_parliament_api import DanishParliamentAPI

# Initialize client
api = DanishParliamentAPI()

# Get recent cases
cases = api.get_cases(top=10)
print(f"Found {len(cases['value'])} cases")

# Search for climate legislation
climate_cases = api.get_cases(filter_expr="substringof('klima', titel)")
print(f"Climate cases: {len(climate_cases['value'])}")

# Get voting records for a politician
votes = api.get_voting_records("Frank Aaen")
print(f"Found {len(votes)} votes")
```

## Features

- **Production-Ready**: Comprehensive error handling and retry logic
- **Pagination Support**: Automatic handling of large datasets
- **Type Hints**: Full type annotations for better IDE support
- **Async Support**: Both sync and async clients available
- **Rate Limiting**: Built-in request throttling
- **Caching**: Optional response caching

## Client Libraries

1. **[Basic Client](basic-client.md)** - Complete synchronous client
2. **[Pagination](pagination.md)** - Large dataset handling
3. **[Error Handling](error-handling.md)** - Robust error patterns
4. **[Async Client](async-client.md)** - Concurrent requests

## Examples

### Parliamentary Monitoring
```python
# Monitor recent activity
recent_changes = api.get_recent_changes(hours_back=4)
for case in recent_changes['value']:
    print(f"Updated: {case['titel']} at {case['opdateringsdato']}")
```

### Voting Analysis
```python
# Get all votes by party in a specific session
votes = api.get_voting_session_details(12345, expand_actors=True)
party_votes = api.analyze_party_voting(votes)
```

### Document Tracking
```python
# Find documents with file attachments
docs = api.get_documents_with_files(
    filter_expr="substringof('budget', titel)"
)
```

## Error Handling

The client handles all common API errors:

- **HTTP 400**: Invalid OData syntax - provides detailed error message
- **HTTP 404**: Invalid entity or ID - graceful fallback
- **HTTP 501**: Unsupported operations - clear error messages
- **Network errors**: Automatic retry with exponential backoff
- **Rate limiting**: Built-in throttling to respect API limits

## Best Practices

1. **Use pagination** for large datasets (max 100 records per request)
2. **Always URL encode** OData parameters (`%24` not `$`)
3. **Handle empty results** gracefully
4. **Use field selection** (`$select`) for better performance
5. **Cache responses** when appropriate