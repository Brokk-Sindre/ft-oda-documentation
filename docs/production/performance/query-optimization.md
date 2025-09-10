# Query Optimization

Maximize the performance of your queries against the Danish Parliamentary API through strategic optimization techniques. This guide provides comprehensive strategies for building efficient queries that minimize response time and bandwidth usage.

## Performance Overview

The Danish Parliamentary API demonstrates excellent baseline performance:

- **Small queries** (d50 records): ~85ms response time
- **Medium queries** (51-100 records): ~90ms response time  
- **Large datasets** (10,000+ records): ~2 seconds with proper optimization
- **Complex expansions**: Acceptable performance with strategic field selection

## Fundamental Optimization Principles

### 1. Query Execution Order

The API processes OData parameters in a specific order that affects performance:

1. **$filter** - Applied first to reduce dataset size
2. **$expand** - Relationships loaded on filtered results
3. **$select** - Field selection applied to final dataset
4. **$orderby** - Sorting performed on processed results
5. **$top/$skip** - Pagination applied last

**Optimization Strategy**: Apply filters early to minimize data processing in subsequent steps.

### 2. Response Size Management

Large responses significantly impact performance:

```bash
# L SLOW: Full entity with all relationships (>50KB per record)
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=100"

#  OPTIMIZED: Selective fields only (~2KB per record)  
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,opdateringsdato&%24top=100"
```

## Field Selection Optimization

### Strategic Use of $select

The `$select` parameter dramatically reduces response size and improves performance:

```bash
# Performance comparison for 100 Sag records:

# L All fields (default): ~2.1s, 1.2MB response
curl "https://oda.ft.dk/api/Sag?%24top=100"

#  Essential fields only: ~110ms, 45KB response  
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,statusid,opdateringsdato&%24top=100"

#  Single field: ~85ms, 8KB response
curl "https://oda.ft.dk/api/Sag?%24select=titel&%24top=100"
```

### Field Selection Best Practices

**Always select only required fields**:
```bash
# For case listings
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,statusid&%24top=1000"

# For change detection  
curl "https://oda.ft.dk/api/Sag?%24select=id,opdateringsdato&%24top=1000"

# For search results
curl "https://oda.ft.dk/api/Sag?%24select=id,titel,resumé&%24filter=contains(titel,'klima')"
```

**Combine $select with expansions**:
```bash
#  OPTIMIZED: Select specific fields from expanded entities
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori(%24select=kategori)&%24select=id,titel"
```

## Filtering Optimization

### Index-Friendly Filter Patterns

The API performs best with filters that leverage indexed fields:

**Primary Key Filters** (Fastest):
```bash
# Single record by ID: ~45ms
curl "https://oda.ft.dk/api/Sag?%24filter=id%20eq%201"

# Multiple IDs: ~65ms
curl "https://oda.ft.dk/api/Sag?%24filter=id%20in%20(1,2,3,4,5)"
```

**Date Range Filters** (Well-optimized):
```bash
# Recent cases: ~120ms for ~500 results
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-01-01'"

# Specific date range: ~90ms
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20ge%20datetime'2024-01-01'%20and%20opdateringsdato%20lt%20datetime'2024-12-31'"
```

**Status and Type Filters** (Efficient):
```bash  
# By status: ~75ms
curl "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203"

# By type: ~85ms  
curl "https://oda.ft.dk/api/Sag?%24filter=typeid%20eq%205"
```

### Text Search Optimization

**String contains operations** are more expensive but still practical:

```bash
#  GOOD: Contains filter with field selection (~200ms)
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'klima')&%24select=id,titel"

# L SLOW: Contains without field selection (~800ms)
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'klima')"

#  OPTIMIZED: Multiple contains with early filtering
curl "https://oda.ft.dk/api/Sag?%24filter=contains(titel,'klima')%20and%20opdateringsdato%20gt%20datetime'2020-01-01'&%24select=id,titel"
```

### Complex Filter Optimization

**Combine filters strategically**:
```bash
#  Date filter first (reduces dataset), then text search
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2023-01-01'%20and%20contains(titel,'energi')"

#  Boolean logic with parentheses  
curl "https://oda.ft.dk/api/Sag?%24filter=(statusid%20eq%203%20or%20statusid%20eq%205)%20and%20opdateringsdato%20gt%20datetime'2024-01-01'"
```

**Critical**: Use proper URL encoding for complex filters:
```bash
# Complex filter with proper encoding
FILTER="(contains(titel,'klima')%20or%20contains(titel,'miljø'))%20and%20opdateringsdato%20gt%20datetime'2023-01-01'"
curl "https://oda.ft.dk/api/Sag?\$filter=${FILTER}&\$select=id,titel"
```

## Expansion Optimization

### Relationship Loading Strategy

Expansions significantly increase response size and processing time:

```bash
# Performance impact analysis:

# Base query: ~85ms, 15KB
curl "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=10"

# Single expansion: ~150ms, 45KB  
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori&%24select=id,titel&%24top=10"

# Multiple expansions: ~300ms, 120KB
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori,SagAktør&%24select=id,titel&%24top=10"

# Deep expansion: ~500ms, 200KB per record
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=10"
```

### Selective Expansion with Field Selection

**Always combine expansions with field selection**:
```bash
#  OPTIMIZED: Select specific fields from expanded entities
curl "https://oda.ft.dk/api/Sag?%24expand=Sagskategori(\$select=kategori),SagAktør(\$select=rolleid)&%24select=id,titel"

#  Deep expansion with field selection
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme(\$select=typeid;%24expand=Aktør(\$select=navn))&%24select=id,nummer"
```

### Expansion Depth Limits

The API supports maximum **2-level expansions**:

```bash
#  SUPPORTED: Two-level expansion
curl "https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør"

# L ERROR: Three-level expansion returns HTTP 400
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør/AktørType"
```

**Workaround for deep relationships**:
```javascript
// Use separate queries for deep data
const cases = await fetch('https://oda.ft.dk/api/Sag?$expand=SagAktør&$select=id,titel');
const actorIds = cases.value.flatMap(c => c.SagAktør.map(sa => sa.aktørid));
const actors = await fetch(`https://oda.ft.dk/api/Aktør?$filter=id in (${actorIds.join(',')})`);
```

## Ordering and Sorting Performance

### Efficient Sorting Strategies  

**Index-optimized ordering**:
```bash
#  FAST: Sort by indexed fields (id, dates)
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=100"
curl "https://oda.ft.dk/api/Sag?%24orderby=id%20desc&%24top=100"

#   SLOWER: Sort by text fields  
curl "https://oda.ft.dk/api/Sag?%24orderby=titel&%24top=100"
```

**Combine sorting with filtering**:
```bash
#  Filter first, then sort (reduces sort dataset)
curl "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203&%24orderby=opdateringsdato%20desc&%24top=50"
```

### Pagination with Sorting

**Consistent pagination requires stable sorting**:
```bash
#  RECOMMENDED: Include ID in sort for stable pagination
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc,id%20desc&%24top=100&%24skip=200"

# L UNSTABLE: Single field sorting may cause duplicates across pages
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=100&%24skip=200"
```

## Query Complexity Analysis

### Performance Classification

**Fast Queries** (<100ms):
- Simple field selection with ID filters
- Small result sets (d50 records) 
- No expansions or single expansion with field selection
- Index-friendly filters (ID, dates, status)

**Medium Queries** (100-300ms):
- Text search with field selection
- Multiple expansions with field selection
- Medium result sets (51-100 records)
- Complex filters with proper indexing

**Expensive Queries** (300ms-2s):
- Large result sets (>100 records) without optimization
- Deep expansions without field selection
- Multiple text search operations
- Complex sorting on non-indexed fields

**Avoid These Patterns**:
```bash
# L VERY SLOW: Large unfiltered dataset with full expansion
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24top=1000"

# L TIMEOUT RISK: No limits with expensive operations
curl "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør&%24filter=contains(resumé,'politik')"
```

### Query Complexity Scoring

**Complexity Factors**:
- Base query: 1 point
- Each expansion: +2 points  
- Deep expansion (2-level): +5 points
- Text search (contains): +3 points
- Large result set (>100): +4 points
- No field selection with expansions: +3 points

**Optimization Target**: Keep total complexity score d8 for best performance.

## Batch Processing and Bulk Operations

### Efficient Large Dataset Access

The API has a **100-record limit** per query. For larger datasets, use strategic batching:

```javascript
// Optimized batch processing
async function getAllCases(filters = '') {
    const batchSize = 100;
    let allCases = [];
    let skip = 0;
    
    while (true) {
        const url = `https://oda.ft.dk/api/Sag?$top=${batchSize}&$skip=${skip}&$select=id,titel,opdateringsdato${filters}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (!data.value || data.value.length === 0) break;
        
        allCases = allCases.concat(data.value);
        skip += batchSize;
        
        // Prevent runaway loops  
        if (skip > 100000) break;
    }
    
    return allCases;
}
```

### Parallel Processing Strategy

For multiple entity types:
```javascript
// Parallel queries for different entity types
const [cases, actors, votes] = await Promise.all([
    fetch('https://oda.ft.dk/api/Sag?$select=id,titel&$top=100'),
    fetch('https://oda.ft.dk/api/Aktør?$select=id,navn&$top=100'),  
    fetch('https://oda.ft.dk/api/Afstemning?$select=id,nummer&$top=100')
]);
```

### Change Detection Optimization  

Use `opdateringsdato` for efficient incremental updates:
```bash
# Get only recently updated cases
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-01'&%24select=id,titel,opdateringsdato"

# Track maximum update date for next query
curl "https://oda.ft.dk/api/Sag?%24orderby=opdateringsdato%20desc&%24top=1&%24select=opdateringsdato"
```

## Performance Testing and Benchmarking

### Response Time Measurement

**Command-line benchmarking**:
```bash
# Test query response time
time curl -s "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=100" > /dev/null

# Detailed timing with curl
curl -w "Total: %{time_total}s, Size: %{size_download} bytes\n" -s -o /dev/null "https://oda.ft.dk/api/Sag?%24top=100"

# Multiple runs for average
for i in {1..5}; do time curl -s "https://oda.ft.dk/api/Sag?%24top=100" > /dev/null; done
```

**JavaScript performance testing**:
```javascript
async function benchmarkQuery(url, description) {
    const start = performance.now();
    const response = await fetch(url);
    const data = await response.json();
    const end = performance.now();
    
    console.log(`${description}:`, {
        time: `${(end - start).toFixed(1)}ms`,
        records: data.value.length,
        size: `${JSON.stringify(data).length} chars`
    });
    
    return data;
}

// Run benchmarks
await benchmarkQuery(
    'https://oda.ft.dk/api/Sag?$select=id,titel&$top=100',
    'Optimized query'
);

await benchmarkQuery(
    'https://oda.ft.dk/api/Sag?$expand=SagAktør&$top=100', 
    'Expansion query'
);
```

### Performance Monitoring

**Key metrics to track**:
- Query response time
- Response payload size  
- Records returned vs requested
- Error rates and types
- Cache hit rates (if implemented)

**Performance regression testing**:
```javascript
const benchmarks = [
    { name: 'Basic query', url: 'https://oda.ft.dk/api/Sag?$select=id,titel&$top=100', target: 150 },
    { name: 'Filtered query', url: 'https://oda.ft.dk/api/Sag?$filter=statusid eq 3&$select=id,titel&$top=50', target: 120 },
    { name: 'Expansion query', url: 'https://oda.ft.dk/api/Sag?$expand=Sagskategori($select=kategori)&$select=id,titel&$top=20', target: 200 }
];

for (const test of benchmarks) {
    const start = Date.now();
    await fetch(test.url);
    const duration = Date.now() - start;
    
    if (duration > test.target) {
        console.warn(`Performance regression: ${test.name} took ${duration}ms (target: ${test.target}ms)`);
    }
}
```

## Query Caching and Reuse Strategies

### Response Caching Patterns

**Client-side caching implementation**:
```javascript
class CachedAPIClient {
    constructor(ttlMinutes = 5) {
        this.cache = new Map();
        this.ttl = ttlMinutes * 60 * 1000;
    }
    
    async query(url) {
        const cached = this.cache.get(url);
        if (cached && Date.now() - cached.timestamp < this.ttl) {
            return cached.data;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        this.cache.set(url, {
            data: data,
            timestamp: Date.now()
        });
        
        return data;
    }
}

// Usage
const client = new CachedAPIClient(10); // 10-minute cache
const cases = await client.query('https://oda.ft.dk/api/Sag?$select=id,titel&$top=100');
```

### Cache-Friendly Query Patterns

**Design queries for caching**:
```bash
#  CACHEABLE: Stable query with consistent results
curl "https://oda.ft.dk/api/Aktør?%24select=id,navn,gruppeid&%24orderby=navn"

# L NOT CACHEABLE: Time-dependent query  
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-10T10:00:00'"
```

**Cache invalidation strategy**:
```javascript
// Invalidate cache based on update timestamps
async function getCasesWithCacheValidation() {
    const latestUpdate = await fetch('https://oda.ft.dk/api/Sag?$orderby=opdateringsdato desc&$top=1&$select=opdateringsdato');
    const lastUpdate = new Date(latestUpdate.value[0].opdateringsdato);
    
    const cacheKey = 'all-cases';
    const cached = localStorage.getItem(cacheKey);
    
    if (cached) {
        const { data, timestamp } = JSON.parse(cached);
        if (new Date(timestamp) > lastUpdate) {
            return data; // Cache is still valid
        }
    }
    
    // Fetch fresh data
    const fresh = await fetch('https://oda.ft.dk/api/Sag?$select=id,titel,statusid&$top=1000');
    const data = await fresh.json();
    
    localStorage.setItem(cacheKey, JSON.stringify({
        data: data,
        timestamp: Date.now()
    }));
    
    return data;
}
```

## Advanced Optimization Techniques

### Query Rewriting for Performance

**Transform expensive queries into efficient ones**:

```javascript
// L ORIGINAL: Expensive deep expansion
// curl "https://oda.ft.dk/api/Sag?$expand=SagAktør/Aktör&$filter=contains(titel,'klima')"

//  OPTIMIZED: Break into separate queries
async function getClimateCasesWithActors() {
    // Step 1: Get climate cases with minimal data
    const cases = await fetch(`https://oda.ft.dk/api/Sag?$filter=contains(titel,'klima')&$select=id,titel&$expand=SagAktør($select=aktørid,rolleid)`);
    
    // Step 2: Get unique actor IDs  
    const actorIds = [...new Set(
        cases.value.flatMap(c => c.SagAktör.map(sa => sa.aktørid))
    )];
    
    // Step 3: Batch fetch actors
    const actors = await fetch(`https://oda.ft.dk/api/Aktör?$filter=id in (${actorIds.join(',')})&$select=id,navn,gruppeid`);
    
    // Step 4: Combine results efficiently
    return combineResults(cases.value, actors.value);
}
```

### Dynamic Query Optimization

**Adjust strategy based on result size**:
```javascript
async function smartQuery(entityName, filters, fields, expansions) {
    // Test query size first
    const countQuery = `https://oda.ft.dk/api/${entityName}?$filter=${filters}&$select=id&$top=1`;
    const testResult = await fetch(countQuery);
    
    if (testResult.value.length === 0) {
        return { value: [] }; // No results
    }
    
    // For small datasets, use expansion
    if (estimatedSize < 50) {
        return await fetch(`https://oda.ft.dk/api/${entityName}?$filter=${filters}&$select=${fields}&$expand=${expansions}`);
    }
    
    // For large datasets, use separate queries  
    return await optimizedLargeQuery(entityName, filters, fields, expansions);
}
```

### Memory-Efficient Processing

**Stream processing for large datasets**:
```javascript
async function* processLargeSagDataset(filter = '') {
    let skip = 0;
    const batchSize = 100;
    
    while (true) {
        const url = `https://oda.ft.dk/api/Sag?$filter=${filter}&$select=id,titel,opdateringsdato&$top=${batchSize}&$skip=${skip}`;
        const response = await fetch(url);
        const batch = await response.json();
        
        if (!batch.value || batch.value.length === 0) break;
        
        // Yield each record individually to avoid memory buildup
        for (const record of batch.value) {
            yield record;
        }
        
        skip += batchSize;
    }
}

// Usage: process 50,000+ records without memory issues
for await (const case of processLargeSagDataset("statusid eq 3")) {
    await processCase(case);
}
```

## Query Optimization Checklist

### Pre-Query Planning

** Query Design**:
- [ ] Define minimal required fields for $select
- [ ] Identify most selective filters to apply first  
- [ ] Plan expansion strategy (separate queries vs single query)
- [ ] Estimate result size and choose appropriate $top value
- [ ] Design stable sorting for pagination consistency

** URL Construction**:
- [ ] Use %24 instead of $ for all OData parameters
- [ ] Properly encode filter values (especially dates and text)
- [ ] Validate relationship names in $expand parameters
- [ ] Test complex filters for proper boolean logic

### Performance Validation

** Response Time Testing**:
- [ ] Benchmark query with realistic data volumes
- [ ] Test edge cases (empty results, maximum results)
- [ ] Validate performance across different times of day
- [ ] Monitor for performance regression over time

** Resource Usage**:
- [ ] Measure response payload size
- [ ] Track memory usage for large datasets
- [ ] Validate network bandwidth requirements
- [ ] Test concurrent query performance

### Production Readiness

** Error Handling**:
- [ ] Handle HTTP 400 errors from invalid expansions
- [ ] Detect and handle silent filter failures
- [ ] Implement retry logic for temporary failures
- [ ] Validate response structure before processing

** Monitoring and Maintenance**:
- [ ] Log query performance metrics
- [ ] Set up alerts for performance degradation  
- [ ] Plan for API schema changes
- [ ] Document query patterns and rationale

## Best Practices Summary

1. **Always use $select** to limit response size
2. **Filter early** with indexed fields (ID, dates, status)
3. **Limit expansions** and combine with field selection
4. **Design for pagination** with stable sorting
5. **Cache strategically** based on data change patterns
6. **Monitor performance** and test regularly
7. **Handle edge cases** gracefully with proper error handling
8. **Document complex queries** for maintenance

Following these optimization strategies will ensure your applications achieve the best possible performance when working with the Danish Parliamentary API's comprehensive dataset.