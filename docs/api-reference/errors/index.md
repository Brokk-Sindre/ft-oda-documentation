# Error Handling

The Danish Parliament API employs unique error handling patterns that differ from typical REST APIs. Understanding these patterns is crucial for building robust applications that can handle edge cases and provide appropriate user feedback.

## Overview

The ODA API uses a hybrid error handling approach combining traditional HTTP status codes with some non-standard behaviors. Most notably, **the API silently ignores invalid filter field names rather than returning errors**, which can lead to unexpected results.

## Error Categories

### HTTP Status Codes

The API returns standard HTTP status codes for most error conditions:

| Status Code | Meaning | Typical Causes |
|-------------|---------|----------------|
| `200` | Success | Query executed successfully |
| `400` | Bad Request | Invalid OData syntax, malformed parameters |
| `404` | Not Found | Invalid entity names or non-existent record IDs |
| `500` | Server Error | Rare internal server issues |

### Silent Failures

**  CRITICAL DISCOVERY**: The most significant finding from API research is that invalid filter field names are **silently ignored**.

```bash
# This query contains a typo in the field name
curl "https://oda.ft.dk/api/Sag?%24filter=invalid_field_name%20eq%20'test'&%24top=5"

# RESULT: Returns HTTP 200 with complete unfiltered dataset (100+ records)
# EXPECTED: HTTP 400 error or validation message
# ACTUAL: Invalid filter is ignored, all records returned
```

**Impact**: 
- Returns complete unfiltered datasets instead of filtered results
- Can lead to performance issues due to large response sizes
- Makes debugging filter queries extremely difficult
- No indication that the filter was invalid

## Common Error Scenarios

### 1. Invalid Entity Names

**Request:**
```bash
curl "https://oda.ft.dk/api/InvalidEntity"
```

**Response:**
- Status: `404 Not Found`
- Content-Type: `text/html`
- Body: HTML error page with "404 - File or directory not found"

### 2. Non-Existent Entity IDs

**Request:**
```bash
curl "https://oda.ft.dk/api/Sag(999999999)"
```

**Response:**
- Status: `404 Not Found`
- Content-Type: Not set
- Body: Empty (0 bytes)

### 3. Invalid OData Syntax

**Request:**
```bash
curl "https://oda.ft.dk/api/Sag?%24filter=invalid%20syntax%20here"
```

**Response:**
- Status: `400 Bad Request`
- Content-Type: Not set
- Body: Empty (0 bytes)

### 4. Invalid Relationship Expansions

**Request:**
```bash
curl "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation"
```

**Response:**
- Status: `400 Bad Request`
- Content-Type: Not set
- Body: Empty (0 bytes)

### 5. Excessive Expansion Depth

**Request:**
```bash
curl "https://oda.ft.dk/api/Sag?%24expand=A/B/C"
```

**Response:**
- Status: `400 Bad Request`
- Response Time: ~44ms (fast failure)
- Maximum supported depth: 2 levels (A/B pattern)

## Critical Error Handling Gaps

### No Error Messages

Most API errors return empty response bodies with no explanatory content:

- **HTTP 400 errors**: Empty response (0 bytes)
- **HTTP 404 errors**: Either empty response or generic HTML error page
- **No structured error information**: No JSON error objects with details

### Inconsistent Error Formats

The API returns different formats for different error types:
- Invalid entities: HTML error pages
- Invalid entity IDs: Empty responses
- Invalid OData parameters: Empty responses

### Misleading HTTP Headers

Some responses include misleading information:
- `Allow` headers list unsupported HTTP methods (POST, PUT, DELETE)
- Cache headers force no-cache even for error responses

## Silent Failure Detection

Since invalid filters fail silently, implement these detection strategies:

### Response Size Monitoring

```javascript
async function detectSilentFailure(url, expectedMaxResults = 50) {
    const response = await fetch(url);
    const data = await response.json();
    
    // Default API response is 100 records
    if (data.value.length === 100 && !url.includes('$top=100')) {
        console.warn('Received default 100 results - filter may have been ignored');
        console.warn('Check filter field names for typos');
    }
    
    if (data.value.length > expectedMaxResults) {
        console.warn(`Unexpectedly large result set: ${data.value.length} records`);
    }
    
    return data;
}
```

### Field Name Validation

```javascript
// Validate field names against known entity schema
const VALID_SAG_FIELDS = ['id', 'titel', 'resume', 'opdateringsdato', 'statusid'];

function validateFilterFields(filterString, validFields) {
    const fieldMatches = filterString.match(/(\w+)\s+(eq|ne|gt|lt|ge|le)/g);
    
    if (fieldMatches) {
        for (const match of fieldMatches) {
            const fieldName = match.split(/\s+/)[0];
            if (!validFields.includes(fieldName)) {
                throw new Error(`Invalid field name: ${fieldName}`);
            }
        }
    }
}
```

## Best Practices

### Always Use URL Encoding

The API requires proper URL encoding for all OData parameters:

```bash
# L WRONG: Will not work correctly
curl "https://oda.ft.dk/api/Sag?\$top=5"

#  CORRECT: Use %24 for $
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

### Implement Comprehensive Error Handling

```javascript
async function robustApiCall(url) {
    try {
        const response = await fetch(url);
        
        // Check HTTP status codes
        if (response.status === 400) {
            throw new Error('Invalid query parameters - check OData syntax');
        }
        if (response.status === 404) {
            throw new Error('Entity not found or invalid ID');
        }
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Detect potential silent filter failures
        if (data.value.length === 100 && !url.includes('%24top=100')) {
            console.warn('Possible silent filter failure - received default 100 results');
        }
        
        return data;
        
    } catch (networkError) {
        // Handle network-level errors
        console.error('Network error:', networkError.message);
        throw new Error('API request failed - check network connectivity');
    }
}
```

### Validate Queries Before Execution

1. **Check Entity Names**: Verify against the metadata endpoint
2. **Validate Field Names**: Cross-reference with entity documentation  
3. **Test Filter Syntax**: Use simple queries to verify field names work
4. **Monitor Response Sizes**: Watch for unexpectedly large datasets

### Handle Empty Results Gracefully

```javascript
function handleApiResponse(data) {
    if (!data.value || data.value.length === 0) {
        // Empty results are normal - not an error condition
        return { results: [], message: 'No matching records found' };
    }
    
    return { results: data.value, count: data.value.length };
}
```

## Performance Implications

Silent filter failures can cause significant performance issues:

- **Unfiltered datasets**: May return 10,000+ records instead of expected 10-100
- **Increased bandwidth**: Large responses consume unnecessary network resources  
- **Client processing delays**: Applications may hang processing unexpected data volumes
- **API server load**: Generating large responses impacts server performance

## Warning Indicators

Watch for these signs of silent failures:

1. **Response size**: Default 100 records when expecting fewer
2. **Response time**: Slower than expected for simple queries
3. **Memory usage**: Client applications consuming excessive memory
4. **Pagination**: Receiving full datasets when filters should limit results

## Related Documentation

- **[HTTP Status Codes](http-codes.md)** - Detailed breakdown of all HTTP response codes
- **[Silent Failures](silent-failures.md)** - Comprehensive guide to detecting and handling silent failures
- **[Troubleshooting](troubleshooting.md)** - Step-by-step debugging guide for common issues
- **[Performance Optimization](../performance/index.md)** - Strategies to minimize the impact of large responses

## Summary

The Danish Parliament API's unique error handling requires special attention:

-  **Standard HTTP codes** for most errors
- L **Silent filter failures** for invalid field names  
- L **Empty error messages** provide no debugging information
-  **Fast failure** for clearly invalid requests
-   **Inconsistent formats** across different error types

Understanding these patterns is essential for building production-ready applications that can detect and handle the API's non-standard error behaviors.