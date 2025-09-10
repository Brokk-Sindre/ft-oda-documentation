# Unsupported OData Features

The Danish Parliamentary API (oda.ft.dk) implements **OData 3.0** with specific limitations and unsupported features. This page documents what doesn't work, why, and provides alternative approaches.

## OData Version Limitations

### OData 3.0 Only
The API strictly implements **OData 3.0** and does not support newer OData versions:

```bash
# L FAILS: OData 4.0 version headers cause 404 errors
curl -H "OData-Version: 4.0" "https://oda.ft.dk/api/Sag?%24top=1"
# Response: HTTP 404

#  WORKS: Default OData 3.0 implementation
curl "https://oda.ft.dk/api/Sag?%24top=1"
# Response: HTTP 200 with DataServiceVersion: 3.0 header
```

**Impact**: Modern OData 4.0+ features are unavailable.

## Unsupported Query Operations

### Advanced OData 4.0 Functions
These modern query functions are **not implemented**:

#### `$search` - Full-text Search
```bash
# L FAILS: HTTP 400 Bad Request
curl "https://oda.ft.dk/api/Sag?%24search=klima&%24top=2"
```

**Alternative**: Use `$filter` with `substringof()`:
```bash
#  WORKS: Text search using OData 3.0 functions
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=2"
```

#### `$apply` - Data Aggregation
```bash
# L FAILS: HTTP 400 Bad Request
curl "https://oda.ft.dk/api/Sag?%24apply=aggregate(id%20with%20count%20as%20total)"
```

**Alternative**: Client-side aggregation or multiple filtered queries:
```javascript
// Count cases by type
const typeA = await fetch('https://oda.ft.dk/api/Sag?$filter=typeid eq 1&$inlinecount=allpages');
const typeB = await fetch('https://oda.ft.dk/api/Sag?$filter=typeid eq 2&$inlinecount=allpages');

const countA = JSON.parse(typeA)['odata.count'];
const countB = JSON.parse(typeB)['odata.count'];
```

#### `$compute` - Computed Properties
```bash
# L FAILS: Connection timeout/error
curl "https://oda.ft.dk/api/Sag?%24compute=count() as total&%24top=1"
```

**Alternative**: Perform calculations client-side after data retrieval.

### Batch Operations

#### `$batch` Endpoint
The API does **not support** batch processing for multiple operations:

```bash
# L FAILS: HTTP 404 Not Found
curl "https://oda.ft.dk/api/%24batch"

# L FAILS: POST with multipart content
curl -X POST -H "Content-Type: multipart/mixed; boundary=batch" \
     "https://oda.ft.dk/api/%24batch" \
     --data-binary "@batch_request.txt"
```

**Impact**: 
- No ability to combine multiple operations in a single request
- Higher network overhead for multiple API calls
- No transaction support across operations

**Alternative**: Make individual HTTP requests:
```javascript
// Instead of batch request, make multiple calls
const [cases, actors, documents] = await Promise.all([
    fetch('https://oda.ft.dk/api/Sag?$top=10'),
    fetch('https://oda.ft.dk/api/Aktør?$top=10'),
    fetch('https://oda.ft.dk/api/Dokument?$top=10')
]);
```

## Write Operations

### All Modification Methods Rejected
Despite HTTP `Allow` headers advertising write support, **all write operations return HTTP 501**:

#### POST (Create)
```bash
# L HTTP 501 Not Implemented
curl -X POST "https://oda.ft.dk/api/Sag" \
     -H "Content-Type: application/json" \
     -d '{"titel": "Test case"}'
```

Response:
```json
{
  "odata.error": {
    "code": "POST requests are not supported.",
    "message": {
      "lang": "en-US",
      "value": "Creating entities is not supported for this entity set."
    }
  }
}
```

#### PUT (Replace)
```bash
# L HTTP 501 Not Implemented
curl -X PUT "https://oda.ft.dk/api/Sag(123)" \
     -H "Content-Type: application/json" \
     -d '{"titel": "Updated case"}'
```

#### PATCH (Partial Update)
```bash
# L HTTP 501 Not Implemented
curl -X PATCH "https://oda.ft.dk/api/Sag(123)" \
     -H "Content-Type: application/json" \
     -d '{"titel": "Partial update"}'
```

#### DELETE (Remove)
```bash
# L HTTP 501 Not Implemented
curl -X DELETE "https://oda.ft.dk/api/Sag(123)"
```

### Why Write Operations Are Blocked

1. **Government Data Integrity**: Parliamentary data must remain authentic and unmodified
2. **Public Access Model**: Read-only API ensures data consistency for all users
3. **Audit Trail Preservation**: Historical legislative records cannot be altered
4. **No Authentication System**: Without user authentication, write operations would be insecure

## Unsupported HTTP Methods

### OPTIONS Method
```bash
# L HTTP 405 Method Not Allowed
curl -X OPTIONS "https://oda.ft.dk/api/Sag"
```

**Issue**: The `Allow` header still shows unsupported methods:
```
Allow: GET,POST,PUT,PATCH,MERGE,DELETE
```

**Reality**: Only `GET` and `HEAD` methods actually work.

## Response Format Limitations

### XML Format Issues
While the API advertises XML support, using `$format=xml` can cause issues:

```bash
#   PROBLEMATIC: May return errors in some contexts
curl "https://oda.ft.dk/api/Sag?%24format=xml&%24top=1"
```

**Recommendation**: Use the default JSON format for best compatibility.

### Content-Type Inconsistencies
Error responses have inconsistent content types:

| Status | Error Type | Content-Type | Response Body |
|--------|------------|--------------|---------------|
| 400 | Bad OData syntax | None | Empty |
| 404 | Invalid entity | text/html | HTML error page |
| 404 | Invalid ID | None | Empty |
| 501 | Write operations | application/json | Structured error |

## Missing Monitoring Endpoints

Standard production monitoring endpoints are **not available**:

```bash
# L All return HTTP 404
curl "https://oda.ft.dk/health"
curl "https://oda.ft.dk/api/health"
curl "https://oda.ft.dk/ping"
curl "https://oda.ft.dk/api/status"
curl "https://oda.ft.dk/robots.txt"
```

**Alternative**: Use entity queries to check API health:
```javascript
// Health check using actual API endpoint
async function checkAPIHealth() {
    try {
        const response = await fetch('https://oda.ft.dk/api/Sag?$top=1');
        return response.status === 200;
    } catch (error) {
        return false;
    }
}
```

## No Real-time Capabilities

### Webhook Support
The API does **not support** push notifications or webhooks:

```bash
# L All return HTTP 404
curl "https://oda.ft.dk/webhook"
curl "https://oda.ft.dk/api/notifications"
curl "https://oda.ft.dk/api/subscribe"
curl "https://oda.ft.dk/rss"
```

**Alternative**: Implement polling strategies:
```javascript
// Poll for recent updates
async function pollForUpdates(entity, lastCheckTime) {
    const isoDate = lastCheckTime.toISOString().slice(0, 19);
    
    const response = await fetch(
        `https://oda.ft.dk/api/${entity}?$filter=opdateringsdato gt datetime'${isoDate}'&$orderby=opdateringsdato desc`
    );
    
    return response.json();
}

// Check every 10 minutes
setInterval(() => {
    pollForUpdates('Sag', new Date(Date.now() - 10 * 60 * 1000));
}, 10 * 60 * 1000);
```

## Query Limitations

### Maximum $top Value
The API enforces a **maximum of 100 records per request**:

```bash
# L Silently limited to 100 records
curl "https://oda.ft.dk/api/Sag?%24top=1000" | jq '.value | length'
# Returns: 100

#  Explicit 100 limit works
curl "https://oda.ft.dk/api/Sag?%24top=100" | jq '.value | length'  
# Returns: 100

#  Values under 100 work correctly
curl "https://oda.ft.dk/api/Sag?%24top=50" | jq '.value | length'
# Returns: 50
```

**Workaround**: Use pagination with `$skip`:
```javascript
// Get large datasets through pagination
async function getAllRecords(entity, pageSize = 100) {
    let allRecords = [];
    let skip = 0;
    
    while (true) {
        const response = await fetch(
            `https://oda.ft.dk/api/${entity}?$top=${pageSize}&$skip=${skip}`
        );
        const data = await response.json();
        
        if (data.value.length === 0) break;
        
        allRecords.push(...data.value);
        skip += pageSize;
    }
    
    return allRecords;
}
```

## Error Handling Gaps

### Silent Filter Failures
**Critical Issue**: Invalid filter field names are silently ignored and return the complete unfiltered dataset:

```bash
# L DANGEROUS: Returns ALL records instead of error
curl "https://oda.ft.dk/api/Sag?%24filter=invalid_field_name eq 'test'"
# Returns: 100 records (unfiltered)
```

**Detection Strategy**:
```javascript
// Check for unexpectedly large results
function validateFilterResults(data, expectedSubset = true) {
    if (expectedSubset && data.value.length === 100) {
        console.warn('Received 100 results - filter may have been ignored');
        console.warn('Verify filter field names in $metadata');
    }
}
```

### Empty Error Responses
HTTP 400 errors return empty response bodies with no error details:

```bash
# L Empty response body for bad syntax
curl "https://oda.ft.dk/api/Sag?%24expand=InvalidRelationship"
# Response: HTTP 400 with 0 bytes content
```

**Client-Side Error Handling**:
```javascript
async function makeAPIRequest(url) {
    const response = await fetch(url);
    
    switch(response.status) {
        case 400:
            throw new Error(`Bad Request: Check OData syntax in ${url}`);
        case 404:
            const contentType = response.headers.get('content-type');
            if (contentType?.includes('text/html')) {
                throw new Error(`Entity endpoint not found`);
            } else {
                throw new Error(`Entity ID not found`);
            }
        case 501:
            const errorBody = await response.json();
            throw new Error(`Operation not supported: ${errorBody.odata.error.message.value}`);
        default:
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
    }
    
    return response.json();
}
```

## Best Practices for Working with Limitations

### 1. Always Use URL Encoding
```bash
#  CORRECT: Use %24 instead of $
curl "https://oda.ft.dk/api/Sag?%24top=10"

# L WRONG: Literal $ characters may cause issues
curl "https://oda.ft.dk/api/Sag?\$top=10"
```

### 2. Implement Client-Side Validation
```javascript
// Validate filter field names against $metadata
async function validateFilter(entity, filterFields) {
    const metadataResponse = await fetch('https://oda.ft.dk/api/$metadata');
    const metadataXML = await metadataResponse.text();
    
    // Extract field names for entity (simplified example)
    const entityPattern = new RegExp(`EntityType Name="${entity}"[\\s\\S]*?</EntityType>`);
    const entityMatch = metadataXML.match(entityPattern);
    
    if (entityMatch) {
        const validFields = entityMatch[0].match(/Property Name="([^"]+)"/g) || [];
        const validFieldNames = validFields.map(f => f.match(/Name="([^"]+)"/)[1]);
        
        // Check if filter fields exist
        for (const field of filterFields) {
            if (!validFieldNames.includes(field)) {
                console.warn(`Warning: Field '${field}' not found in ${entity} entity`);
            }
        }
    }
}
```

### 3. Handle Large Datasets Efficiently
```javascript
// Stream processing for large datasets
async function* paginateAll(entity, options = {}) {
    let skip = 0;
    const top = Math.min(options.top || 100, 100);
    
    while (true) {
        const url = new URL(`https://oda.ft.dk/api/${entity}`);
        url.searchParams.set('$top', top.toString());
        url.searchParams.set('$skip', skip.toString());
        
        if (options.filter) url.searchParams.set('$filter', options.filter);
        if (options.select) url.searchParams.set('$select', options.select);
        if (options.expand) url.searchParams.set('$expand', options.expand);
        
        const response = await fetch(url.toString());
        const data = await response.json();
        
        if (data.value.length === 0) break;
        
        yield* data.value;
        skip += top;
        
        // Rate limiting
        await new Promise(resolve => setTimeout(resolve, 100));
    }
}
```

## Future Considerations

The Danish Parliamentary API is a **production government system** focused on stability and data integrity. Future enhancements are unlikely to include:

- **Write operations** (data integrity requirements)
- **OData 4.0 upgrade** (backward compatibility concerns)
- **Real-time push notifications** (polling architecture is sufficient)
- **Batch operations** (current individual request model works well)

For feature requests or API issues, contact: **folketinget@ft.dk** with subject "Åbne Data".

## Summary

The Danish Parliamentary API provides comprehensive read-only access to parliamentary data with specific limitations:

- **OData 3.0 only** - no modern 4.0+ features
- **Read-only access** - all write operations return HTTP 501  
- **100 record limit** per request - use pagination for larger datasets
- **Silent filter failures** - invalid field names return unfiltered data
- **No batch processing** - make individual requests
- **No real-time updates** - polling required

Despite these limitations, the API provides excellent access to 30+ years of Danish parliamentary data with strong performance and reliability.