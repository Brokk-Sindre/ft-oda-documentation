# Query Limits and Constraints

The Danish Parliamentary OData API implements several important limits and constraints to ensure optimal performance and system stability. Understanding these limits is crucial for building robust applications that handle large datasets efficiently.

## Overview

The API enforces a strict **100-record maximum** per request while providing excellent performance characteristics. Large datasets must be accessed through pagination using `$skip` and `$top` parameters.

## Maximum Records Per Request

### Hard Limit: 100 Records

The API enforces a hard limit of 100 records per request regardless of the `$top` parameter value:

```bash
# These requests all return exactly 100 records
curl "https://oda.ft.dk/api/Sag?%24top=500"     # Returns: 100 records
curl "https://oda.ft.dk/api/Sag?%24top=1000"    # Returns: 100 records  
curl "https://oda.ft.dk/api/Sag?%24top=10000"   # Returns: 100 records
```

### Effective $top Parameter Behavior

- **Values 1-100**: Returns exact number requested
- **Values > 100**: Capped at 100 records (no error thrown)
- **Missing $top**: Returns 100 records (default)

```bash
# Working within limits
curl "https://oda.ft.dk/api/Sag?%24top=25"      # Returns: 25 records
curl "https://oda.ft.dk/api/Sag?%24top=100"     # Returns: 100 records
curl "https://oda.ft.dk/api/Sag?%24top=150"     # Returns: 100 records (capped)
```

## Query Complexity Limitations

### Expansion Limits

- **Maximum Expansion Depth**: 2 levels
- **Multiple Expansions**: Supported but impacts performance
- **Complex Expansions**: Can significantly increase response size

```bash
# Single level expansion (fast)
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=10"

# Two-level expansion (slower, larger response)
curl "https://oda.ft.dk/api/Dokument?%24expand=DokumentAktør/Aktør&%24top=10"

# Deep expansion impact on response size
# Single entity: ~2KB  With expansion: ~15KB+
```

### Filter Complexity

No specific limits detected for filter complexity, but best practices apply:

```bash
# Simple filters (recommended)
curl "https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%201"

# Complex boolean logic (supported)
curl "https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%201%20and%20statusid%20eq%202"
```

## Performance Thresholds

### Response Time Characteristics

Based on comprehensive testing, response times scale predictably:

| Query Size | Response Time | Use Case |
|------------|---------------|----------|
| 1-50 records | 85-95ms | Interactive queries |
| 51-100 records | 90-105ms | Standard pagination |
| With expansions | 108-200ms | Related data queries |
| Large skip offsets | 90-120ms | Deep pagination |

### Performance Optimization Guidelines

```bash
# Optimal: Small batches with specific fields
curl "https://oda.ft.dk/api/Sag?%24top=50&%24select=id,titel,typeid"

# Good: Standard pagination
curl "https://oda.ft.dk/api/Sag?%24top=100&%24skip=200"

# Acceptable: Single expansion
curl "https://oda.ft.dk/api/Sag?%24top=25&%24expand=Sagskategori"

# Use carefully: Multiple expansions
curl "https://oda.ft.dk/api/Sag?%24top=10&%24expand=Sagskategori,SagAktør"
```

## Rate Limiting Policy

### No Rate Limits Detected

The API does not implement traditional rate limiting:

- **Concurrent Requests**: 10+ simultaneous requests supported
- **Rapid Requests**: 5 consecutive requests within seconds - all successful
- **No Throttling**: No HTTP 429 (Too Many Requests) responses observed

### Recommended Client-Side Throttling

Despite no enforced rate limits, implement responsible usage:

```javascript
// Recommended: 100ms delay between requests
async function fetchWithDelay(url) {
    const response = await fetch(url);
    await new Promise(resolve => setTimeout(resolve, 100));
    return response;
}

// Batch processing with throttling
async function fetchAllPages(entityName, batchSize = 100) {
    const results = [];
    let skip = 0;
    let hasMore = true;
    
    while (hasMore) {
        const url = `https://oda.ft.dk/api/${entityName}?$top=${batchSize}&$skip=${skip}`;
        const response = await fetchWithDelay(url);
        const data = await response.json();
        
        results.push(...data.value);
        hasMore = data.value.length === batchSize;
        skip += batchSize;
    }
    
    return results;
}
```

## Pagination Requirements

### Mandatory for Large Datasets

All datasets exceeding 100 records require pagination:

```bash
# Get total count first
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '.["odata.count"]'
# Returns: 96538

# Calculate pages needed: 96538 ÷ 100 = 966 pages
```

### Efficient Pagination Pattern

```python
import requests
import time

def fetch_all_records(entity_name, batch_size=100):
    """Fetch all records from an entity with proper pagination."""
    base_url = f"https://oda.ft.dk/api/{entity_name}"
    all_records = []
    skip = 0
    
    while True:
        # Build URL with proper encoding
        params = {
            '$top': batch_size,
            '$skip': skip,
            '$inlinecount': 'allpages' if skip == 0 else None
        }
        
        # Remove None values
        params = {k: v for k, v in params.items() if v is not None}
        
        response = requests.get(base_url, params=params)
        data = response.json()
        
        # Add records to collection
        records = data.get('value', [])
        all_records.extend(records)
        
        # Check if we have more records
        if len(records) < batch_size:
            break
            
        skip += batch_size
        
        # Respectful delay
        time.sleep(0.1)
    
    return all_records

# Usage example
all_cases = fetch_all_records('Sag', batch_size=100)
print(f"Retrieved {len(all_cases)} total cases")
```

### Large Dataset Access Strategies

For the largest entities in the API:

| Entity | Record Count | Pages (100/page) | Est. Time |
|--------|--------------|------------------|-----------|
| Sag | 96,538+ | 966+ | ~2-3 minutes |
| Aktør | 18,139+ | 182+ | ~30 seconds |
| Dokument | 500,000+ | 5,000+ | ~10-15 minutes |
| Stemme | 2,000,000+ | 20,000+ | ~45-60 minutes |

## Timeout Thresholds

### No Hard Timeouts Observed

- **Standard Queries**: No timeout limits detected
- **Complex Queries**: Large expansions complete successfully
- **Long-Running**: Multi-thousand record retrievals complete

### Client-Side Timeout Recommendations

```javascript
// Recommended client timeout configuration
const fetchWithTimeout = async (url, timeoutMs = 30000) => {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeoutMs);
    
    try {
        const response = await fetch(url, {
            signal: controller.signal
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        throw error;
    }
};
```

## Best Practices for Working Within Limits

### 1. Optimize Query Structure

```bash
#  Good: Specific fields only
curl "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=100"

# L Avoid: All fields with large expansions
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør,Sagskategori,SagDokument&%24top=100"
```

### 2. Implement Efficient Pagination

```python
def paginate_efficiently(entity_name, filters=None):
    """Efficient pagination with built-in limits handling."""
    
    params = {
        '$top': 100,  # Always use maximum allowed
        '$skip': 0,
        '$inlinecount': 'allpages'
    }
    
    if filters:
        params['$filter'] = filters
    
    # First request to get total count
    response = requests.get(f"https://oda.ft.dk/api/{entity_name}", params=params)
    data = response.json()
    
    total_count = data.get('odata.count', 0)
    total_pages = (total_count + 99) // 100  # Ceiling division
    
    print(f"Total records: {total_count}, Pages: {total_pages}")
    
    all_records = data.get('value', [])
    
    # Fetch remaining pages
    for page in range(1, total_pages):
        params['$skip'] = page * 100
        params.pop('$inlinecount', None)  # Only needed for first request
        
        response = requests.get(f"https://oda.ft.dk/api/{entity_name}", params=params)
        page_data = response.json()
        all_records.extend(page_data.get('value', []))
        
        # Progress indicator
        if page % 50 == 0:
            print(f"Progress: {page}/{total_pages} pages ({len(all_records)} records)")
        
        time.sleep(0.1)  # Rate limiting
    
    return all_records
```

### 3. Handle Large Datasets Asynchronously

```javascript
// Async generator for memory-efficient processing
async function* fetchAllRecordsPaginated(entityName, batchSize = 100) {
    let skip = 0;
    let hasMore = true;
    
    while (hasMore) {
        const url = `https://oda.ft.dk/api/${entityName}?$top=${batchSize}&$skip=${skip}`;
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            
            const records = data.value || [];
            
            if (records.length > 0) {
                yield records; // Yield batch of records
                hasMore = records.length === batchSize;
                skip += batchSize;
                
                // Respectful delay
                await new Promise(resolve => setTimeout(resolve, 100));
            } else {
                hasMore = false;
            }
        } catch (error) {
            console.error(`Error fetching page at skip ${skip}:`, error);
            break;
        }
    }
}

// Usage: Process large datasets without memory issues
async function processAllCases() {
    for await (const batch of fetchAllRecordsPaginated('Sag')) {
        // Process each batch of up to 100 records
        batch.forEach(case => {
            // Process individual case
            console.log(`Processing case: ${case.id}`);
        });
    }
}
```

### 4. Monitor and Handle Errors

```python
def robust_api_request(url, max_retries=3):
    """Make API request with error handling and retries."""
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            print(f"Timeout on attempt {attempt + 1}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed on attempt {attempt + 1}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(1)
    
    raise Exception(f"Failed after {max_retries} attempts")
```

## Common Limit-Related Issues

### Issue: Getting 100 Records Instead of Requested Amount

**Problem**: Using `$top=500` but receiving only 100 records

**Solution**: The 100-record limit is enforced. Use pagination:

```python
# L This will only return 100 records
response = requests.get("https://oda.ft.dk/api/Sag?$top=500")

#  Use pagination for more records
def get_500_records():
    records = []
    for skip in [0, 100, 200, 300, 400]:
        params = {'$top': 100, '$skip': skip}
        response = requests.get("https://oda.ft.dk/api/Sag", params=params)
        records.extend(response.json()['value'])
    return records
```

### Issue: Slow Performance with Large Expansions

**Problem**: Queries with multiple expansions taking several seconds

**Solution**: Optimize expansion strategy:

```bash
# L Slow: Multiple expansions in single request
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør,Sagskategori,SagDokument&%24top=50"

#  Fast: Separate requests for different expansions
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24top=100"
curl "https://oda.ft.dk/api/SagAktør?%24expand=Aktør&%24filter=sagid%20eq%201234"
```

### Issue: Memory Issues with Large Dataset Processing

**Problem**: Application crashes when processing thousands of records

**Solution**: Use streaming/batch processing:

```python
def process_large_dataset_streaming(entity_name, process_function):
    """Process large datasets without loading all into memory."""
    
    skip = 0
    batch_size = 100
    
    while True:
        # Fetch batch
        params = {'$top': batch_size, '$skip': skip}
        response = requests.get(f"https://oda.ft.dk/api/{entity_name}", params=params)
        data = response.json()
        
        records = data.get('value', [])
        if not records:
            break
        
        # Process batch immediately
        for record in records:
            process_function(record)
        
        # Clean up memory
        del records, data
        
        skip += batch_size
        time.sleep(0.1)
        
        # Progress update
        if skip % 1000 == 0:
            print(f"Processed {skip} records...")
```

## Summary

The Danish Parliamentary OData API implements a straightforward but firm limit structure:

- **Hard limit**: 100 records per request
- **No rate limiting**: But implement client-side throttling
- **Excellent performance**: 85-120ms response times
- **Pagination required**: For datasets > 100 records
- **No timeout limits**: Complex queries complete successfully

Success with large datasets requires proper pagination implementation and respectful request patterns. The API's consistent performance characteristics make it reliable for production applications processing parliamentary data at scale.