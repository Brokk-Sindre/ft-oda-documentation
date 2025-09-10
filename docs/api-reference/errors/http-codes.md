# HTTP Status Codes

This page documents the HTTP status codes returned by the Danish Parliament's Open Data API (oda.ft.dk) and how to handle them properly in your applications.

## Overview

The ODA API uses standard HTTP status codes to indicate the success or failure of API requests. However, there are some important nuances and unexpected behaviors that developers must understand for proper error handling.

!!! warning "Critical Finding: Silent Filter Failures"
    The API returns HTTP 200 OK even when filter parameters contain invalid field names. Invalid filters are silently ignored and return the complete unfiltered dataset. This can lead to unexpectedly large responses and performance issues.

## Status Codes Reference

### 200 OK - Successful Requests

**When it occurs:**
- Valid API requests with proper OData syntax
- **Important**: Also returned when filters contain invalid field names (unexpected behavior)
- Empty result sets (no matching data found)

**Response characteristics:**
- Valid JSON response with proper OData structure
- Fast response times (85-108ms average)
- Complete metadata included

**Example successful request:**
```bash
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

**Response:**
```json
{
  "odata.metadata": "https://oda.ft.dk/api/$metadata#Sag",
  "value": [
    {
      "id": 12345,
      "titel": "Forslag til folketingsbeslutning...",
      "opdateringsdato": "2024-03-15T10:30:00Z"
    }
  ]
}
```

**Example with invalid filter (problematic behavior):**
```bash
# This returns 200 OK but ignores the invalid field name
curl "https://oda.ft.dk/api/Sag?%24filter=invalid_field%20eq%20'test'&%24top=100"
```

!!! danger "Silent Failure Risk"
    When you make a typo in field names within `$filter` parameters, the API will:
    
    - Return HTTP 200 OK (appears successful)
    - Silently ignore the invalid filter
    - Return the complete unfiltered dataset
    - Potentially cause performance issues with large responses
    
    Always verify your field names and monitor result counts!

**How to handle 200 responses:**
```javascript
const response = await fetch(url);
if (response.ok) {
    const data = await response.json();
    
    // Check if you got more results than expected
    // (might indicate ignored filter)
    if (data.value.length === 100 && !url.includes('$top=100')) {
        console.warn('Filter may have been ignored - got default result count');
    }
    
    return data;
}
```

### 400 Bad Request - Invalid Query Parameters

**When it occurs:**
- Invalid OData syntax in query parameters
- Invalid `$expand` relationship names
- Malformed `$filter` expressions
- Invalid `$format` parameter values
- Excessive expansion depth (more than 2 levels)

**Response characteristics:**
- **Empty response body** (0 bytes)
- Fast error response (~44ms)
- No detailed error message provided

**Examples that trigger 400 errors:**
```bash
# Invalid expansion relationship
curl "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation"

# Too many expansion levels (>2)
curl "https://oda.ft.dk/api/Sag?%24expand=A/B/C"

# Invalid format parameter
curl "https://oda.ft.dk/api/Sag?%24format=invalidformat"
```

**How to handle 400 responses:**
```javascript
if (response.status === 400) {
    throw new Error('Invalid query parameters - check $expand and $filter syntax');
}
```

### 404 Not Found - Resource Not Found

The API returns 404 errors in two different scenarios with different response formats:

#### Invalid Entity Endpoints
**When it occurs:**
- Non-existent entity names in the URL path
- Misspelled entity names

**Response characteristics:**
- **HTML error page** with user-friendly message
- Content-Type: text/html
- Clean error page with standard 404 messaging

**Example:**
```bash
curl "https://oda.ft.dk/api/InvalidEntity"
```

**Response (HTML):**
```html
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>404 - File or directory not found.</title>
</head>
<body>
  <div id="header"><h1>Server Error</h1></div>
  <div id="content">
    <h2>404 - File or directory not found.</h2>
    <h3>The resource you are looking for might have been removed, 
         had its name changed, or is temporarily unavailable.</h3>
  </div>
</body>
</html>
```

#### Invalid Entity IDs
**When it occurs:**
- Valid entity name but non-existent ID
- Requesting specific records that don't exist

**Response characteristics:**
- **Empty response body** (0 bytes)
- No content type header
- Silent failure with no error message

**Example:**
```bash
curl "https://oda.ft.dk/api/Sag(999999999)"
```

**How to handle 404 responses:**
```javascript
if (response.status === 404) {
    // Check if response has content (HTML error page)
    const text = await response.text();
    if (text.includes('File or directory not found')) {
        throw new Error('Invalid entity name - check API endpoint spelling');
    } else {
        throw new Error('Entity ID not found - record may not exist');
    }
}
```

### 405 Method Not Allowed - Unsupported HTTP Methods

**When it occurs:**
- Using HTTP OPTIONS method
- The API only supports GET requests for data retrieval

**Response characteristics:**
- HTTP 405 status
- May include misleading `Allow` headers

!!! warning "Misleading Allow Headers"
    The API returns `Allow: GET,POST,PUT,PATCH,MERGE,DELETE` headers, but only GET requests actually work. Write operations return HTTP 501 (see below).

**Example:**
```bash
curl -X OPTIONS "https://oda.ft.dk/api/Sag"
```

### 501 Not Implemented - Write Operations

**When it occurs:**
- Attempting POST, PUT, PATCH, or DELETE operations
- The API is strictly read-only

**Response characteristics:**
- Proper structured OData JSON error format
- Clear error messages explaining the limitation
- Fast response (~300ms)

**Examples:**
```bash
# All of these return HTTP 501
curl -X POST "https://oda.ft.dk/api/Sag" -d '{"titel":"test"}'
curl -X PUT "https://oda.ft.dk/api/Sag(1)" -d '{"titel":"updated"}'
curl -X PATCH "https://oda.ft.dk/api/Sag(1)" -d '{"titel":"patched"}'
curl -X DELETE "https://oda.ft.dk/api/Sag(1)"
```

**Response format:**
```json
{
  "odata.error": {
    "code": "",
    "message": {
      "lang": "en-US",
      "value": "Creating entities is not supported for this entity set."
    }
  }
}
```

## Complete Error Handling Pattern

Here's a comprehensive error handling approach for the ODA API:

```javascript
async function fetchFromODA(url) {
    try {
        const response = await fetch(url);
        
        // Handle specific status codes
        if (response.status === 400) {
            throw new Error('Invalid query parameters - check $expand and $filter syntax');
        }
        
        if (response.status === 404) {
            const text = await response.text();
            if (text.includes('File or directory not found')) {
                throw new Error('Invalid entity name - check API endpoint spelling');
            } else {
                throw new Error('Entity ID not found - record may not exist');
            }
        }
        
        if (response.status === 405) {
            throw new Error('HTTP method not supported - use GET requests only');
        }
        
        if (response.status === 501) {
            throw new Error('Write operations not supported - API is read-only');
        }
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Check for potential silent filter failures
        if (data.value && data.value.length === 100 && !url.includes('$top=100')) {
            console.warn('Warning: Got 100 results - filter may have been ignored due to typo');
        }
        
        return data;
        
    } catch (error) {
        console.error('API request failed:', error.message);
        throw error;
    }
}
```

## Status Codes Not Observed

During extensive testing, the following status codes were **not** encountered:

- **401 Unauthorized** - Not applicable (no authentication required)
- **403 Forbidden** - Not applicable (public API)
- **429 Too Many Requests** - No rate limiting detected
- **500 Internal Server Error** - Stable service with no server errors observed
- **502/503/504** - No gateway or service unavailability errors

## Best Practices

### 1. Monitor Result Counts
```javascript
// Check if you got unexpected result volumes
if (data.value.length >= 100 && expectedLess) {
    console.warn('Large result set - verify filters are working correctly');
}
```

### 2. Validate Field Names
```javascript
// Use $select to verify field existence before filtering
const testUrl = `${baseUrl}?$select=${fieldName}&$top=1`;
const testResponse = await fetch(testUrl);
if (testResponse.status === 400) {
    throw new Error(`Field '${fieldName}' does not exist`);
}
```

### 3. Handle Different 404 Types
```javascript
if (response.status === 404) {
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('text/html')) {
        // Invalid entity name
        throw new Error('Check entity name spelling in URL');
    } else {
        // Invalid entity ID
        throw new Error('Record with this ID does not exist');
    }
}
```

### 4. Implement Retry Logic for Stability
```javascript
async function fetchWithRetry(url, maxRetries = 3) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
        try {
            const response = await fetch(url);
            if (response.ok) return await response.json();
            
            // Don't retry client errors (4xx)
            if (response.status >= 400 && response.status < 500) {
                throw new Error(`Client error: ${response.status}`);
            }
            
            throw new Error(`Server error: ${response.status}`);
            
        } catch (error) {
            if (attempt === maxRetries) throw error;
            await new Promise(resolve => setTimeout(resolve, 1000 * attempt));
        }
    }
}
```

## Troubleshooting Guide

| Problem | Likely Cause | Solution |
|---------|--------------|----------|
| Getting too many results | Invalid filter field name | Verify field names exist using `$select` |
| HTTP 400 on expansion | Invalid relationship name | Check entity relationships in documentation |
| HTTP 400 on deep expansion | Too many expansion levels | Limit expansion to 2 levels (A/B pattern) |
| HTTP 404 with HTML | Wrong entity name | Check spelling of entity name in URL |
| HTTP 404 with empty response | Invalid entity ID | Verify the record ID exists |
| HTTP 501 on write operations | Attempting data modification | API is read-only - use GET requests only |

The Danish Parliament's ODA API provides a robust and stable service with consistent error handling patterns. Understanding these status codes and their implications will help you build reliable applications that properly handle both successful responses and various error conditions.