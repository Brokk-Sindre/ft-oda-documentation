# Silent Failures

Silent failures in the Danish Parliament's Open Data API (oda.ft.dk) represent the most critical challenge for developers building robust applications. Unlike typical REST APIs that return clear error messages for invalid parameters, the ODA API exhibits several patterns where errors are either ignored or handled inconsistently.

!!! danger "Critical Finding"
    The API's most dangerous behavior is **silently ignoring invalid filter field names**. This can result in returning complete unfiltered datasets instead of the expected filtered results, leading to performance issues and incorrect application behavior.

## What Are Silent Failures?

Silent failures occur when the API processes requests that contain errors but responds with HTTP 200 OK status codes instead of appropriate error codes. The client application receives what appears to be a successful response, but the actual query execution differs from what was intended.

### Types of Silent Failures

1. **Invalid Filter Field Names** - The most common and dangerous silent failure
2. **Empty Response Bodies on HTTP 400** - Missing error details when requests fail
3. **Inconsistent Error Formats** - Mixed HTML and empty responses for different error types

## Common Silent Failure Scenarios

### 1. Invalid Filter Field Names

**The Problem:**
When OData `$filter` parameters contain field names that don't exist in the target entity, the API silently ignores the entire filter and returns the complete unfiltered dataset.

**Example - Dangerous Silent Failure:**
```bash
# Query with typo in field name - should be "titel" not "title"
curl "https://oda.ft.dk/api/Sag?%24filter=title%20eq%20'klimaændringer'&%24top=5"
```

**Expected Result:**
- HTTP 400 Bad Request with error message about invalid field name
- Clear indication that "title" is not a valid field

**Actual Result:**
-  HTTP 200 OK (appears successful)
- L Returns 100+ unfiltered records instead of 0-5 filtered records
- L No indication that the filter was ignored
- L Potential performance impact from large response

**How to Detect:**
```bash
# Monitor response size - 100 records often indicates ignored filter
curl "https://oda.ft.dk/api/Sag?%24filter=nonexistent_field%20eq%20'test'&%24top=5" | jq '.value | length'
# Returns: 100 (default page size, not the requested 5)
```

### 2. Empty Response Bodies on HTTP 400

**The Problem:**
When OData syntax errors occur, the API correctly returns HTTP 400 Bad Request but provides no error message or diagnostic information in the response body.

**Example:**
```bash
# Invalid $expand with excessive nesting depth
curl -i "https://oda.ft.dk/api/Sag?%24expand=Sagskategori/Sagskategori/Sagskategori&%24top=1"
```

**Response:**
```
HTTP/1.1 400 Bad Request
Content-Length: 0
Content-Type: 

(empty response body)
```

**Impact:**
- Developers receive no actionable error information
- Debugging OData syntax issues becomes trial-and-error
- No guidance on what specifically caused the failure

### 3. Inconsistent 404 Error Formats

**The Problem:**
The API returns different response formats for different types of "not found" scenarios:
- Invalid entity names: HTML error page
- Invalid record IDs: Empty JSON response
- Invalid endpoints: Plain text or HTML

**Example - Invalid Entity:**
```bash
curl "https://oda.ft.dk/api/InvalidEntity"
```

**Response:**
```html
<!DOCTYPE html>
<html>
<head><title>404 Not Found</title></head>
<body>The resource you are looking for has been removed...</body>
</html>
```

**Example - Invalid Record ID:**
```bash
curl "https://oda.ft.dk/api/Sag(999999999)"
```

**Response:**
```json
{
  "odata.metadata": "https://oda.ft.dk/api/$metadata#Sag",
  "value": []
}
```

## Detection Strategies

### 1. Response Size Monitoring

Invalid filters typically result in default pagination (100 records) instead of your intended result count:

```python
import requests
import json

def detect_silent_filter_failure(url, expected_max_results=10):
    """Detect if filter was silently ignored by checking result count."""
    response = requests.get(url)
    data = response.json()
    
    result_count = len(data.get('value', []))
    
    # If we got way more results than expected, filter likely ignored
    if result_count > expected_max_results * 10:
        print(f"   WARNING: Got {result_count} results, filter may be ignored")
        return True
    
    return False

# Usage
url = "https://oda.ft.dk/api/Sag?%24filter=invalid_field%20eq%20'test'&%24top=5"
if detect_silent_filter_failure(url, expected_max_results=5):
    print("Possible silent filter failure detected")
```

### 2. Field Name Validation

Pre-validate field names against the entity schema:

```python
def validate_field_exists(entity_name, field_name):
    """Check if field exists in entity metadata."""
    metadata_url = f"https://oda.ft.dk/api/%24metadata"
    # Parse XML metadata to validate field names
    # Implementation depends on XML parsing library
    pass

# Pre-validate before building filters
if not validate_field_exists('Sag', 'title'):
    print("Invalid field name: 'title', use 'titel' instead")
```

### 3. Response Validation

Always validate that response structure matches expectations:

```javascript
function validateResponse(response, expectedFilters) {
    const data = response.data;
    
    // Check if we got suspiciously many results
    if (data.value.length >= 100 && expectedFilters.length > 0) {
        console.warn('  Large result set despite filters - possible silent failure');
    }
    
    // Validate response structure
    if (!data['odata.metadata']) {
        console.error('L Missing OData metadata - invalid response');
    }
    
    return data;
}
```

## Handling Silent Failures

### 1. Defensive Filtering

Always implement client-side validation before sending requests:

```python
class SafeODataClient:
    def __init__(self):
        # Pre-validated field mappings for common entities
        self.valid_fields = {
            'Sag': ['id', 'titel', 'opdateringsdato', 'statusid', 'typeid'],
            'Aktør': ['id', 'navn', 'efternavn', 'typeid'],
            # ... add more entities
        }
    
    def build_filter(self, entity, field, operator, value):
        if field not in self.valid_fields.get(entity, []):
            raise ValueError(f"Invalid field '{field}' for entity '{entity}'")
        
        return f"{field}%20{operator}%20'{value}'"
    
    def query(self, entity, filters=None, top=None):
        # Build safe URL with validated parameters
        url = f"https://oda.ft.dk/api/{entity}"
        params = []
        
        if filters:
            filter_str = '%20and%20'.join(filters)
            params.append(f"%24filter={filter_str}")
        
        if top:
            params.append(f"%24top={top}")
        
        if params:
            url += "?" + "&".join(params)
        
        return requests.get(url)
```

### 2. Result Count Validation

Implement automatic detection of ignored filters:

```typescript
interface QueryResult {
    'odata.metadata': string;
    value: any[];
}

class ODataClient {
    private async detectSilentFailure(
        response: QueryResult, 
        expectedMaxResults: number
    ): Promise<boolean> {
        const actualCount = response.value.length;
        
        // If we got default pagination size (100), filter likely ignored
        if (actualCount === 100 && expectedMaxResults < 50) {
            console.warn(`  Got ${actualCount} results, expected max ${expectedMaxResults}`);
            return true;
        }
        
        return false;
    }
    
    async query(url: string, expectedResults: number = 10): Promise<QueryResult> {
        const response = await fetch(url);
        const data = await response.json() as QueryResult;
        
        if (await this.detectSilentFailure(data, expectedResults)) {
            throw new Error('Possible silent filter failure - check field names');
        }
        
        return data;
    }
}
```

### 3. Error Response Parsing

Handle the inconsistent error response formats:

```python
def parse_api_error(response):
    """Parse various error response formats from the ODA API."""
    if response.status_code == 200:
        return None  # Successful response
    
    content_type = response.headers.get('content-type', '').lower()
    
    if response.status_code == 400:
        if len(response.content) == 0:
            return {
                'type': 'odata_syntax_error',
                'message': 'Invalid OData syntax (no details provided)',
                'suggestion': 'Check parameter encoding and syntax'
            }
    
    elif response.status_code == 404:
        if 'html' in content_type:
            return {
                'type': 'invalid_endpoint',
                'message': 'Entity or endpoint not found',
                'suggestion': 'Check entity name spelling and case'
            }
        else:
            return {
                'type': 'record_not_found',
                'message': 'No records match the specified ID',
                'suggestion': 'Verify the record ID exists'
            }
    
    # Default error handling
    return {
        'type': 'unknown_error',
        'status': response.status_code,
        'message': response.text[:200]  # First 200 chars
    }
```

## Best Practices for Client Applications

### 1. Implement Comprehensive Logging

```python
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def log_api_request(url: str, response_data: Dict[Any, Any], expected_count: int = None):
    """Log API requests with silent failure detection."""
    
    actual_count = len(response_data.get('value', []))
    
    # Log basic request info
    logger.info(f"API Request: {url}")
    logger.info(f"Response: {actual_count} records")
    
    # Detect potential silent failures
    if expected_count and actual_count > expected_count * 5:
        logger.warning(
            f"  POTENTIAL SILENT FAILURE: Expected ~{expected_count} records, "
            f"got {actual_count}. Check for filter field typos."
        )
    
    # Log suspicious patterns
    if actual_count == 100:
        logger.warning("Got exactly 100 records - possible default pagination due to ignored filter")
```

### 2. Create Field Name Constants

Prevent typos by using constants for field names:

```javascript
// OData field name constants
const SAG_FIELDS = {
    ID: 'id',
    TITEL: 'titel',  // Note: Danish spelling
    OPDATERINGSDATO: 'opdateringsdato',
    STATUS_ID: 'statusid',
    TYPE_ID: 'typeid'
};

const AKTOR_FIELDS = {
    ID: 'id',
    NAVN: 'navn',
    EFTERNAVN: 'efternavn',
    TYPE_ID: 'typeid'
};

// Usage - prevents typos that would cause silent failures
const filter = `%24filter=${SAG_FIELDS.TITEL}%20eq%20'klimaændringer'`;
```

### 3. Implement Response Validation

```python
from typing import List, Dict, Any
import warnings

class ResponseValidator:
    def __init__(self):
        self.expected_fields = {
            'Sag': ['id', 'titel', 'opdateringsdato'],
            'Aktør': ['id', 'navn', 'efternavn']
        }
    
    def validate_response(self, entity: str, data: Dict[Any, Any], 
                         filters_applied: List[str] = None) -> bool:
        """Validate API response and detect silent failures."""
        
        if not data.get('value'):
            return True  # Empty result is valid
        
        result_count = len(data['value'])
        
        # Check for suspiciously large result sets
        if filters_applied and result_count >= 100:
            warnings.warn(
                f"Large result set ({result_count}) despite filters. "
                f"Possible silent filter failure - verify field names: {filters_applied}",
                UserWarning
            )
        
        # Validate first record structure
        if data['value']:
            first_record = data['value'][0]
            expected_fields = self.expected_fields.get(entity, [])
            
            missing_fields = [f for f in expected_fields if f not in first_record]
            if missing_fields:
                warnings.warn(f"Missing expected fields: {missing_fields}")
        
        return True

# Usage
validator = ResponseValidator()
response_data = api_client.get('Sag', filters=['titel eq klimaændringer'])
validator.validate_response('Sag', response_data, ['titel'])
```

## Troubleshooting Silent Failures

### Diagnostic Checklist

When you suspect a silent failure, work through this checklist:

1. **Check Response Size**
   ```bash
   # Count results
   curl "https://oda.ft.dk/api/Sag?%24filter=your_filter&%24top=5" | jq '.value | length'
   # If result is > 5, filter likely ignored
   ```

2. **Verify Field Names**
   ```bash
   # Test with known good field
   curl "https://oda.ft.dk/api/Sag?%24filter=id%20gt%201&%24top=5"
   # Should return exactly 5 records
   ```

3. **Check URL Encoding**
   ```bash
   # Verify %24 is used instead of $
   echo "Correct: %24filter"
   echo "Wrong: \$filter"
   ```

4. **Test Without Filters**
   ```bash
   # Remove filters to isolate the issue
   curl "https://oda.ft.dk/api/Sag?%24top=5"
   ```

### Common Field Name Mistakes

| Incorrect | Correct | Entity |
|-----------|---------|--------|
| `title` | `titel` | Sag |
| `name` | `navn` | Aktør |
| `surname` | `efternavn` | Aktør |
| `updateDate` | `opdateringsdato` | Sag |
| `statusId` | `statusid` | Sag |

### Recovery Strategies

When you encounter a silent failure:

1. **Immediate Actions:**
   - Stop the current request to avoid performance impact
   - Log the full URL and response size
   - Check field names against entity documentation

2. **Debugging Steps:**
   ```python
   def debug_silent_failure(base_url, suspected_field):
       """Debug potential silent filter failure."""
       
       # Test 1: Query without filter
       no_filter = f"{base_url}?%24top=5"
       response1 = requests.get(no_filter)
       print(f"No filter: {len(response1.json()['value'])} results")
       
       # Test 2: Query with known good field
       good_filter = f"{base_url}?%24filter=id%20gt%201&%24top=5"
       response2 = requests.get(good_filter)
       print(f"Good filter: {len(response2.json()['value'])} results")
       
       # Test 3: Query with suspected bad field
       bad_filter = f"{base_url}?%24filter={suspected_field}%20eq%20'test'&%24top=5"
       response3 = requests.get(bad_filter)
       result_count = len(response3.json()['value'])
       
       if result_count > 10:
           print(f"L SILENT FAILURE: '{suspected_field}' is likely invalid")
       else:
           print(f" Field '{suspected_field}' appears valid")
   ```

3. **Prevention:**
   - Implement field validation before sending requests
   - Monitor response sizes in production
   - Set up alerts for unusually large API responses

## Code Examples with Proper URL Encoding

All examples use proper URL encoding (`%24` instead of `$`) as required by the ODA API:

### Python Example with Error Detection

```python
import requests
import logging
from typing import Optional, Dict, Any

class SafeODataClient:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.logger = logging.getLogger(__name__)
    
    def query_with_validation(self, entity: str, filter_expr: str = None, 
                             top: int = None, expected_max: int = 50) -> Dict[Any, Any]:
        """Query with automatic silent failure detection."""
        
        # Build URL with proper encoding
        url = f"{self.base_url}/{entity}"
        params = []
        
        if filter_expr:
            params.append(f"%24filter={filter_expr}")
        if top:
            params.append(f"%24top={top}")
        
        if params:
            url += "?" + "&".join(params)
        
        # Execute request
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        result_count = len(data.get('value', []))
        
        # Detect silent failure
        if filter_expr and result_count > expected_max:
            self.logger.warning(
                f"  Silent failure detected: got {result_count} results "
                f"with filter '{filter_expr}', expected max {expected_max}"
            )
            
            # Optionally raise exception
            raise ValueError(f"Possible silent filter failure - check field names in: {filter_expr}")
        
        return data

# Usage
client = SafeODataClient()

try:
    # This will detect the silent failure and raise an exception
    results = client.query_with_validation(
        entity='Sag',
        filter_expr='title%20eq%20\'test\'',  # Invalid field name
        top=5,
        expected_max=5
    )
except ValueError as e:
    print(f"Silent failure detected: {e}")
    # Handle the error appropriately
```

### JavaScript/TypeScript Example

```typescript
interface ODataResponse<T> {
    'odata.metadata': string;
    value: T[];
}

class SafeODataService {
    private baseUrl = 'https://oda.ft.dk/api';
    
    async queryWithValidation<T>(
        entity: string,
        options: {
            filter?: string;
            top?: number;
            expectedMaxResults?: number;
        } = {}
    ): Promise<ODataResponse<T>> {
        
        const { filter, top, expectedMaxResults = 50 } = options;
        
        // Build URL with proper encoding
        let url = `${this.baseUrl}/${entity}`;
        const params: string[] = [];
        
        if (filter) {
            params.push(`%24filter=${encodeURIComponent(filter)}`);
        }
        if (top) {
            params.push(`%24top=${top}`);
        }
        
        if (params.length > 0) {
            url += '?' + params.join('&');
        }
        
        // Execute request
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`API request failed: ${response.status} ${response.statusText}`);
        }
        
        const data: ODataResponse<T> = await response.json();
        
        // Detect silent failure
        if (filter && data.value.length > expectedMaxResults) {
            console.warn(
                `  Silent failure detected: got ${data.value.length} results ` +
                `with filter '${filter}', expected max ${expectedMaxResults}`
            );
            
            throw new Error(
                `Possible silent filter failure. Check field names in filter: ${filter}`
            );
        }
        
        return data;
    }
}

// Usage with error handling
const service = new SafeODataService();

async function safeSagQuery() {
    try {
        const results = await service.queryWithValidation('Sag', {
            filter: 'title eq \'test\'',  // Invalid field - will be caught
            top: 5,
            expectedMaxResults: 5
        });
        
        console.log(`Found ${results.value.length} cases`);
        
    } catch (error) {
        console.error('Query failed:', error.message);
        
        // Try with correct field name
        const correctedResults = await service.queryWithValidation('Sag', {
            filter: 'titel eq \'test\'',  // Correct Danish field name
            top: 5,
            expectedMaxResults: 5
        });
        
        console.log(`Corrected query found ${correctedResults.value.length} cases`);
    }
}
```

### Bash/cURL Debugging Scripts

```bash
#!/bin/bash
# debug_silent_failure.sh - Script to debug potential silent failures

BASE_URL="https://oda.ft.dk/api"
ENTITY="Sag"
SUSPECTED_FIELD="title"  # This should be "titel"

echo "= Debugging potential silent failure..."
echo "Entity: $ENTITY"
echo "Suspected field: $SUSPECTED_FIELD"
echo "----------------------------------------"

# Test 1: Query without filter (baseline)
echo "Test 1: No filter (baseline)"
NO_FILTER_URL="${BASE_URL}/${ENTITY}?%24top=5"
echo "URL: $NO_FILTER_URL"
BASELINE_COUNT=$(curl -s "$NO_FILTER_URL" | jq '.value | length')
echo "Results: $BASELINE_COUNT"
echo ""

# Test 2: Query with known good field
echo "Test 2: Known good field (id)"
GOOD_FILTER_URL="${BASE_URL}/${ENTITY}?%24filter=id%20gt%201&%24top=5"
echo "URL: $GOOD_FILTER_URL"
GOOD_COUNT=$(curl -s "$GOOD_FILTER_URL" | jq '.value | length')
echo "Results: $GOOD_COUNT"
echo ""

# Test 3: Query with suspected bad field
echo "Test 3: Suspected field ($SUSPECTED_FIELD)"
BAD_FILTER_URL="${BASE_URL}/${ENTITY}?%24filter=${SUSPECTED_FIELD}%20eq%20'test'&%24top=5"
echo "URL: $BAD_FILTER_URL"
BAD_COUNT=$(curl -s "$BAD_FILTER_URL" | jq '.value | length')
echo "Results: $BAD_COUNT"
echo ""

# Analysis
echo "= Analysis:"
if [ "$BAD_COUNT" -gt 10 ]; then
    echo "L SILENT FAILURE DETECTED!"
    echo "   The field '$SUSPECTED_FIELD' appears to be invalid."
    echo "   Expected: ~5 results"
    echo "   Actual: $BAD_COUNT results"
    echo "   The filter was likely ignored, returning unfiltered data."
    echo ""
    echo "=¡ Suggested fix:"
    echo "   Check the correct field name in the API documentation."
    echo "   For Sag entity, use 'titel' instead of 'title'."
else
    echo " Field appears to be valid"
    echo "   Results are within expected range."
fi
```

## Summary

Silent failures in the Danish Parliament's OData API represent a significant challenge that requires proactive detection and handling strategies. The most critical issue is the silent ignoring of invalid filter field names, which can lead to performance problems and incorrect application behavior.

**Key Takeaways:**

1. **Always validate response sizes** - Unexpectedly large result sets often indicate ignored filters
2. **Use proper URL encoding** - Always use `%24` instead of `$` in OData parameters
3. **Implement client-side field validation** - Pre-validate field names before sending requests
4. **Monitor and log API responses** - Set up automated detection of suspicious response patterns
5. **Handle inconsistent error formats** - Prepare for HTML, JSON, and empty response formats
6. **Use Danish field names** - Remember that field names use Danish spelling (e.g., `titel`, not `title`)

By understanding and preparing for these silent failure patterns, developers can build robust applications that reliably work with the Danish Parliament's API while avoiding common pitfalls.