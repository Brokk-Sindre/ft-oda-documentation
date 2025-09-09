# Pagination Documentation

The Danish Parliament API implements efficient pagination with a **hard limit of 100 records per request**. This guide covers all pagination strategies, performance characteristics, and best practices for accessing large datasets.

## Core Pagination Parameters

### $top Parameter - Record Limit

The `$top` parameter limits the number of records returned:

| `$top` Value | Records Returned | Response Time |
|--------------|------------------|---------------|
| `1-50` | Exact count | ~85ms |
| `51-100` | Exact count | ~90ms |
| `101+` | **100 (capped)** | ~90ms |

!!! danger "Hard Limit: 100 Records Maximum"
    **Any `$top` value greater than 100 returns exactly 100 records**. This is a hard server-side limit that cannot be bypassed.
    
    ```bash
    # These all return 100 records:
    curl "https://oda.ft.dk/api/Sag?%24top=101"    # Returns 100
    curl "https://oda.ft.dk/api/Sag?%24top=1000"   # Returns 100  
    curl "https://oda.ft.dk/api/Sag?%24top=10000"  # Returns 100
    ```

### $skip Parameter - Offset Control

The `$skip` parameter skips a specified number of records:

```bash
# Basic pagination pattern
curl "https://oda.ft.dk/api/Sag?%24skip=0&%24top=100"    # Records 1-100
curl "https://oda.ft.dk/api/Sag?%24skip=100&%24top=100"  # Records 101-200  
curl "https://oda.ft.dk/api/Sag?%24skip=200&%24top=100"  # Records 201-300
```

### $inlinecount Parameter - Total Count

Get the total number of records matching your query:

```bash
# Include total count in response
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=10"
```

Response includes total count:
```json
{
  "odata.count": "96538",
  "value": [
    // 10 records
  ]
}
```

## Real Dataset Examples

### Sag (Cases) - 96,538+ Records

**Challenge**: Access all parliamentary cases efficiently

```bash
# Get total case count
curl "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq '.["odata.count"]'
# Result: "96538"

# Calculate pages needed: 96,538 ÷ 100 = 966 pages
# Pages: 0, 100, 200, 300... 96,500
```

**Complete Access Strategy**:
```bash
#!/bin/bash
# Access all 96,538 cases efficiently
for skip in {0..96500..100}; do
    echo "Fetching records $((skip+1)) to $((skip+100))"
    curl -s "https://oda.ft.dk/api/Sag?%24skip=$skip&%24top=100" | jq '.value'
    sleep 0.1  # Rate limiting
done
```

### Aktør (Actors) - 18,139+ Records

**182 pages of actors (politicians, committees, ministries)**:

```bash
# Calculate pagination for actors
total_actors=18139
pages=$(( (total_actors + 99) / 100 ))  # Ceiling division = 182 pages

for page in $(seq 0 $((pages-1))); do
    skip=$((page * 100))
    curl -s "https://oda.ft.dk/api/Aktør?%24skip=$skip&%24top=100"
done
```

### Stemme (Votes) - Millions of Records

**Largest entity - requires strategic filtering**:

```bash
# Don't try to get all votes - filter first!
# Get votes for specific voting session
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%2012345&%24top=100"

# Get votes by specific politician
curl "https://oda.ft.dk/api/Stemme?%24filter=Aktør/navn%20eq%20'Frank%20Aaen'&%24expand=Aktør&%24top=100"
```

## Efficient Pagination Patterns

### Pattern 1: Complete Dataset Access

```python
# Python: Access complete dataset with pagination
import requests
import time

def get_all_records(entity_name, filter_expr=None):
    """Get all records from an entity using pagination"""
    base_url = "https://oda.ft.dk/api/"
    all_records = []
    skip = 0
    batch_size = 100
    
    while True:
        # Build URL with pagination
        url = f"{base_url}{entity_name}?$top={batch_size}&$skip={skip}"
        if filter_expr:
            url += f"&$filter={filter_expr}"
        
        # Make request
        response = requests.get(url)
        data = response.json()
        
        # Add records to collection
        records = data.get('value', [])
        all_records.extend(records)
        
        # Check if we've reached the end
        if len(records) < batch_size:
            break
            
        skip += batch_size
        time.sleep(0.1)  # Rate limiting
    
    return all_records

# Usage examples
all_cases = get_all_records('Sag')
climate_cases = get_all_records('Sag', "substringof('klima',titel)")
```

### Pattern 2: Streaming Access

```javascript
// JavaScript: Stream large datasets
async function* streamRecords(entityName, options = {}) {
    const { batchSize = 100, filter, expand } = options;
    let skip = 0;
    
    while (true) {
        const params = new URLSearchParams();
        params.append('$top', batchSize);
        params.append('$skip', skip);
        
        if (filter) params.append('$filter', filter);
        if (expand) params.append('$expand', expand);
        
        const response = await fetch(`https://oda.ft.dk/api/${entityName}?${params}`);
        const data = await response.json();
        
        const records = data.value || [];
        
        // Yield each record
        for (const record of records) {
            yield record;
        }
        
        // Check if we've reached the end
        if (records.length < batchSize) {
            break;
        }
        
        skip += batchSize;
        await new Promise(resolve => setTimeout(resolve, 100)); // Rate limiting
    }
}

// Usage
for await (const case of streamRecords('Sag', { filter: "year(opdateringsdato) eq 2025" })) {
    console.log(case.titel);
}
```

### Pattern 3: Parallel Batch Processing

```python
# Python: Parallel processing of known dataset size
import asyncio
import aiohttp
from math import ceil

async def fetch_batch(session, entity, skip, top=100):
    """Fetch a single batch of records"""
    url = f"https://oda.ft.dk/api/{entity}?$skip={skip}&$top={top}"
    async with session.get(url) as response:
        data = await response.json()
        return data.get('value', [])

async def get_all_parallel(entity_name, total_records, batch_size=100, max_concurrent=5):
    """Get all records using parallel requests"""
    total_batches = ceil(total_records / batch_size)
    
    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def fetch_with_semaphore(skip):
            async with semaphore:
                return await fetch_batch(session, entity_name, skip, batch_size)
        
        # Create tasks for all batches
        tasks = [
            fetch_with_semaphore(skip) 
            for skip in range(0, total_records, batch_size)
        ]
        
        # Execute all tasks and collect results
        batches = await asyncio.gather(*tasks)
        
        # Flatten results
        all_records = []
        for batch in batches:
            all_records.extend(batch)
            
        return all_records

# Usage - Get all 18,139 actors in parallel
actors = await get_all_parallel('Aktør', 18139)
```

## Performance Characteristics

### Response Time Analysis (Tested)

Based on comprehensive testing of the live API:

| Query Type | Response Time | Notes |
|------------|---------------|-------|
| `$top=1-50` | ~85ms | Optimal for small queries |
| `$top=51-100` | ~90ms | Standard pagination size |
| `$skip=0-1000` | ~90ms | No penalty for small skips |
| `$skip=10000+` | ~90ms | Excellent performance even with large offsets |
| Complex filters | +10-20ms | Minimal filter overhead |
| Multi-level expansion | ~1.8s | Significant overhead for deep relationships |

### Pagination vs. Filtering Performance

```bash
# Fast: Pagination without expansion
time curl -s "https://oda.ft.dk/api/Sag?%24skip=10000&%24top=100" > /dev/null
# Result: ~0.09s

# Medium: Pagination with simple expansion  
time curl -s "https://oda.ft.dk/api/Sag?%24skip=1000&%24top=100&%24expand=Sagskategori" > /dev/null
# Result: ~0.3s

# Slow: Complex multi-level expansion
time curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=100" > /dev/null  
# Result: ~1.8s
```

## Real-Time Data Access Patterns

### Recent Updates Strategy

Instead of paginating through all data, filter for recent changes:

```bash
# Get today's updates (much more efficient than full pagination)  
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T00:00:00'&%24orderby=opdateringsdato%20desc&%24top=100"

# Last 24 hours of parliamentary activity
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-08T18:00:00'&%24inlinecount=allpages&%24top=100"
```

### Entity-Specific Pagination Strategies

#### Large Entities (Require Pagination)
```bash
# Sag (Cases): 96,538 records - Always paginate
curl "https://oda.ft.dk/api/Sag?%24skip=0&%24top=100"

# Aktør (Actors): 18,139 records - 182 pages
curl "https://oda.ft.dk/api/Aktør?%24skip=0&%24top=100"  

# Stemme (Votes): Millions - Filter first, then paginate
curl "https://oda.ft.dk/api/Stemme?%24filter=afstemningid%20eq%2012345&%24skip=0&%24top=100"
```

#### Medium Entities (Selective Pagination)
```bash
# Dokument: Large but often filtered by type
curl "https://oda.ft.dk/api/Dokument?%24filter=Dokumenttype/type%20eq%20'Lovforslag'&%24skip=0&%24top=100"
```

#### Small Entities (Rarely Need Pagination)  
```bash
# Aktørtype: Only ~15 records
curl "https://oda.ft.dk/api/Aktørtype"

# Afstemningstype: Only ~5 voting types  
curl "https://oda.ft.dk/api/Afstemningstype"
```

## Advanced Pagination Techniques

### Count-First Strategy

Always check total count before beginning large operations:

```bash
# Step 1: Get total count
total=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')
echo "Total records: $total"

# Step 2: Calculate pages needed  
pages=$(( (total + 99) / 100 ))
echo "Pages required: $pages"

# Step 3: Paginate efficiently
for skip in $(seq 0 100 $((total - 1))); do
    curl -s "https://oda.ft.dk/api/Sag?%24skip=$skip&%24top=100"
done
```

### Filtered Pagination

Combine filtering with pagination for targeted data access:

```bash
# Climate legislation pagination (much smaller dataset)
curl -s "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24inlinecount=allpages&%24top=1"
# Result: {"odata.count": "89", "value": [...]}

# Only 1 page needed for climate cases!
curl "https://oda.ft.dk/api/Sag?%24filter=substringof('klima',titel)&%24top=100"
```

### Year-Based Pagination Strategy

For historical analysis, paginate by year to manage large datasets:

```python
# Python: Year-by-year access pattern
def get_cases_by_year(year, max_records=None):
    """Get all cases for a specific year with optional limit"""
    filter_expr = f"year(opdateringsdato) eq {year}"
    
    # Get count for this year
    count_url = f"https://oda.ft.dk/api/Sag?$filter={filter_expr}&$inlinecount=allpages&$top=1"
    response = requests.get(count_url)
    total_count = int(response.json()['odata.count'])
    
    print(f"Year {year}: {total_count} cases")
    
    if max_records:
        total_count = min(total_count, max_records)
    
    # Paginate through year's data
    records = []
    for skip in range(0, total_count, 100):
        batch_url = f"https://oda.ft.dk/api/Sag?$filter={filter_expr}&$skip={skip}&$top=100"
        batch_response = requests.get(batch_url)
        batch_data = batch_response.json().get('value', [])
        records.extend(batch_data)
        
        if len(batch_data) < 100:  # End of data
            break
    
    return records

# Usage: Get all cases from 2025
cases_2025 = get_cases_by_year(2025)
print(f"Retrieved {len(cases_2025)} cases from 2025")
```

## Error Handling in Pagination

### Detection of Pagination Issues

```python
# Python: Robust pagination error handling
def paginate_safely(entity, batch_size=100, max_retries=3):
    skip = 0
    all_records = []
    consecutive_errors = 0
    
    while consecutive_errors < max_retries:
        try:
            url = f"https://oda.ft.dk/api/{entity}?$skip={skip}&$top={batch_size}"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                print(f"HTTP {response.status_code} at skip={skip}")
                consecutive_errors += 1
                continue
                
            data = response.json()
            batch = data.get('value', [])
            
            if not batch:  # End of data
                print(f"Completed: {len(all_records)} total records")
                break
                
            all_records.extend(batch) 
            skip += batch_size
            consecutive_errors = 0  # Reset error counter
            
            # Progress indicator
            if skip % 1000 == 0:
                print(f"Progress: {len(all_records)} records retrieved")
                
        except requests.RequestException as e:
            print(f"Request error at skip={skip}: {e}")
            consecutive_errors += 1
            time.sleep(2 ** consecutive_errors)  # Exponential backoff
    
    return all_records
```

## Best Practices Summary

1. **Respect the 100-record limit** - Plan pagination accordingly
2. **Use `$inlinecount=allpages`** to calculate total pages needed  
3. **Filter before paginating** to reduce dataset size
4. **Monitor response times** - Complex expansion can be slow
5. **Implement rate limiting** - Be respectful of the API
6. **Handle errors gracefully** - Network issues can occur
7. **Use parallel processing** cautiously to avoid overwhelming the server
8. **Consider real-time patterns** - Recent updates are more efficient than full dataset access

## Common Pagination Patterns Reference

### Basic Sequential Pagination
```bash
for skip in {0..1000..100}; do
    curl "https://oda.ft.dk/api/Sag?%24skip=$skip&%24top=100"
done
```

### Filtered Sequential Pagination  
```bash
filter="year(opdateringsdato)%20eq%202025"
for skip in {0..400..100}; do
    curl "https://oda.ft.dk/api/Sag?%24filter=$filter&%24skip=$skip&%24top=100"
done
```

### Count-First Pagination
```bash
# Get total count
count=$(curl -s "https://oda.ft.dk/api/Sag?%24inlinecount=allpages&%24top=1" | jq -r '.["odata.count"]')

# Paginate based on actual count
for skip in $(seq 0 100 $((count - 1))); do
    curl "https://oda.ft.dk/api/Sag?%24skip=$skip&%24top=100"
done
```

The Danish Parliament API's pagination system is highly efficient and reliable. With the 100-record limit and strategic pagination patterns, you can access the complete 74+ year archive of Danish democratic data effectively.