# Production Troubleshooting

Comprehensive guide to diagnosing and resolving issues with Danish Parliamentary OData API applications in production environments. This documentation is based on extensive testing and real-world usage patterns.

## Quick Diagnostic Checklist

**Before diving deep, verify these common issues:**

- [ ] **URL Encoding**: Using `%24` instead of `$` for OData parameters
- [ ] **Response Size**: Check if getting 100 records when expecting more (API caps at 100)
- [ ] **Filter Fields**: Verify field names in `$filter` parameters (typos silently ignored)
- [ ] **Network**: Confirm HTTPS connectivity and DNS resolution
- [ ] **UTF-8 Encoding**: Ensure proper handling of Danish characters (æ, ø, å)

## Troubleshooting Methodology

### 1. Systematic Diagnostic Approach

**Step 1: Isolate the Problem**
```bash
# Test basic API connectivity
curl -w "\nHTTP_STATUS:%{http_code}\nTIME_TOTAL:%{time_total}" \
  "https://oda.ft.dk/api/Sag?%24top=1"

# Expected: HTTP 200, ~100ms response time
```

**Step 2: Validate Query Structure**
```bash
# Check OData parameter encoding
curl "https://oda.ft.dk/api/Sag?\$top=5"        # WRONG - will fail
curl "https://oda.ft.dk/api/Sag?%24top=5"       # CORRECT - will work
```

**Step 3: Monitor Response Characteristics**
```bash
# Check for silent filter failures
curl "https://oda.ft.dk/api/Sag?%24filter=invalidfield eq 'test'" | jq '.value | length'
# If returns >1000 records, filter was silently ignored
```

### 2. Performance Baseline Verification

**Expected Response Times:**
- Small queries (d50 records): 85-150ms
- Medium queries (51-100 records): 90-300ms  
- Large queries (100+ records): 90ms-2s (capped at 100)
- Complex expansions: 200ms-3s depending on depth

**Performance Test Script:**
```bash
#!/bin/bash
echo "Testing API performance baselines..."

echo "Small query test:"
time curl -s "https://oda.ft.dk/api/Sag?%24top=5" > /dev/null

echo "Medium query test:"  
time curl -s "https://oda.ft.dk/api/Sag?%24top=100" > /dev/null

echo "Expansion test:"
time curl -s "https://oda.ft.dk/api/Sag?%24expand=SagAktør&%24top=10" > /dev/null
```

## Common Production Issues

### Issue Category 1: Query Construction Problems

#### Problem: OData Parameters Not Working
**Symptoms:**
- Getting default results instead of filtered/limited results
- API appears to ignore `$top`, `$filter`, `$orderby` parameters

**Root Cause:** URL encoding issues - shell escaping doesn't work for OData parameters

**Solution:**
```bash
# WRONG - Shell escaping fails silently
curl "https://oda.ft.dk/api/Sag?\$top=5"

# CORRECT - URL encode dollar signs
curl "https://oda.ft.dk/api/Sag?%24top=5"

# In code - ensure proper encoding
const apiUrl = `https://oda.ft.dk/api/Sag?${encodeURIComponent('$top')}=5`;
```

#### Problem: Getting All Records Instead of Filtered Results
**Symptoms:**
- Filter appears correct but returns complete dataset
- No error message, just unexpectedly large response
- Performance degradation due to large response size

**Root Cause:** **CRITICAL API BEHAVIOR** - Invalid filter field names are silently ignored

**Solution:**
```bash
# This returns ALL records (silent failure)
curl "https://oda.ft.dk/api/Sag?%24filter=wrongfieldname eq 'test'"

# Verify field names in entity metadata
curl "https://oda.ft.dk/api/\$metadata" | grep -A 10 "EntityType.*Sag"

# Correct field name
curl "https://oda.ft.dk/api/Sag?%24filter=titel contains 'klimaændring'"
```

**Prevention Strategy:**
- Always validate filter field names against entity metadata
- Monitor response sizes for unexpectedly large datasets
- Implement client-side validation for common field name typos

### Issue Category 2: Response Size and Pagination Issues

#### Problem: Only Getting 100 Records Despite Higher $top Value
**Symptoms:**
- Requesting 500+ records but only receiving 100
- No error message or indication of capping

**Root Cause:** API silently caps all responses at 100 records maximum

**Solution:**
```javascript
// Implement proper pagination
async function getAllRecords(baseUrl, totalNeeded) {
    const records = [];
    let skip = 0;
    const pageSize = 100; // API maximum
    
    while (records.length < totalNeeded) {
        const url = `${baseUrl}?%24top=${pageSize}&%24skip=${skip}`;
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.value.length === 0) break;
        
        records.push(...data.value);
        skip += pageSize;
        
        // Respect API performance - add delay between requests
        await new Promise(resolve => setTimeout(resolve, 100));
    }
    
    return records;
}
```

### Issue Category 3: Performance and Timeout Issues

#### Problem: Slow Query Responses
**Diagnostic Steps:**
```bash
# Test response time with timing
curl -w "\nTime: %{time_total}s" "https://oda.ft.dk/api/Sag?%24expand=SagAktør&%24top=100"

# If >3s, optimize query:
# 1. Remove unnecessary expansions
# 2. Reduce record count
# 3. Add specific field selection
curl "https://oda.ft.dk/api/Sag?%24select=id,titel&%24top=50"
```

**Performance Optimization Pattern:**
```javascript
class OptimizedApiClient {
    constructor() {
        this.performanceThresholds = {
            fast: 200,      // ms
            acceptable: 1000, // ms
            slow: 3000      // ms
        };
    }
    
    async queryWithPerformanceMonitoring(url) {
        const startTime = performance.now();
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            const duration = performance.now() - startTime;
            
            if (duration > this.performanceThresholds.slow) {
                console.warn(`Slow query detected: ${duration.toFixed(0)}ms for ${url}`);
            }
            
            // Check for silent filter failures
            if (data.value && data.value.length > 1000) {
                console.warn('Large dataset returned - possible filter failure');
            }
            
            return data;
        } catch (error) {
            const duration = performance.now() - startTime;
            console.error(`Query failed after ${duration.toFixed(0)}ms: ${error.message}`);
            throw error;
        }
    }
}
```

### Issue Category 4: HTTP Error Responses

#### Problem: HTTP 400 Bad Request Errors
**Common Causes:**
- Invalid `$expand` parameters (non-existent relationships)
- Malformed OData syntax in queries
- Deep nested expansions (>3 levels)

**Diagnostic Approach:**
```bash
# Test for invalid expansion
curl -w "\nHTTP_STATUS:%{http_code}" \
  "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation"
# Returns: HTTP 400

# Test expansion depth limit
curl -w "\nHTTP_STATUS:%{http_code}" \
  "https://oda.ft.dk/api/Sag?%24expand=SagAktør/Aktør/SomeDeepRelation/EvenDeeper"
# May return: HTTP 400
```

**Solution:**
```javascript
// Implement robust error handling
async function safeApiQuery(url) {
    try {
        const response = await fetch(url);
        
        if (!response.ok) {
            switch (response.status) {
                case 400:
                    throw new Error(`Bad Request: Check OData syntax and expansion parameters`);
                case 404:
                    throw new Error(`Not Found: Invalid entity name or record ID`);
                case 501:
                    throw new Error(`Not Implemented: API is read-only (POST/PUT/DELETE not supported)`);
                default:
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
        }
        
        return await response.json();
    } catch (error) {
        console.error(`API Error for ${url}:`, error.message);
        throw error;
    }
}
```

#### Problem: HTTP 404 Not Found Errors
**Common Causes:**
- Typo in entity name
- Requesting non-existent record ID
- Invalid API endpoint path

**Solution:**
```bash
# Verify entity names
curl "https://oda.ft.dk/api/\$metadata" | grep -o 'EntitySet Name="[^"]*"' | sort

# Test record existence before complex queries
curl -w "\nHTTP_STATUS:%{http_code}" \
  "https://oda.ft.dk/api/Sag(123456)"
```

### Issue Category 5: Data Quality and Character Encoding

#### Problem: Danish Characters Not Displaying Correctly
**Symptoms:**
- æ, ø, å appearing as question marks or boxes
- Garbled text in API responses
- UTF-8 encoding issues

**Solution:**
```javascript
// Ensure proper UTF-8 handling
const response = await fetch(apiUrl, {
    headers: {
        'Accept': 'application/json; charset=utf-8',
        'Content-Type': 'application/json; charset=utf-8'
    }
});

// Verify encoding in response
const data = await response.json();
console.log('Encoding test:', data.value[0].titel); // Should display Danish characters correctly
```

```python
# Python UTF-8 handling
import requests
import json

response = requests.get(
    'https://oda.ft.dk/api/Sag?%24top=1',
    headers={'Accept': 'application/json; charset=utf-8'}
)
response.encoding = 'utf-8'  # Ensure UTF-8 decoding

data = response.json()
print(f"Title: {data['value'][0]['titel']}")  # Should display Danish characters
```

## Monitoring and Alerting Strategies

### Performance Monitoring

**Key Metrics to Track:**
- Response times by query type
- Response size distribution
- Error rate by HTTP status code
- Silent filter failure detection (unexpectedly large responses)

**Monitoring Script Example:**
```javascript
class ApiMonitor {
    constructor() {
        this.metrics = {
            responseTime: [],
            errorCount: 0,
            largeResponseCount: 0
        };
    }
    
    async monitorQuery(url) {
        const startTime = Date.now();
        
        try {
            const response = await fetch(url);
            const data = await response.json();
            const responseTime = Date.now() - startTime;
            
            this.metrics.responseTime.push(responseTime);
            
            // Alert on performance degradation
            if (responseTime > 5000) {
                this.alert('PERFORMANCE', `Slow response: ${responseTime}ms for ${url}`);
            }
            
            // Alert on potential silent filter failures
            if (data.value && data.value.length > 1000) {
                this.metrics.largeResponseCount++;
                this.alert('DATA_SIZE', `Large response detected: ${data.value.length} records`);
            }
            
            return data;
        } catch (error) {
            this.metrics.errorCount++;
            this.alert('ERROR', `Query failed: ${error.message}`);
            throw error;
        }
    }
    
    alert(type, message) {
        console.warn(`[${new Date().toISOString()}] ${type}: ${message}`);
        // Integrate with your monitoring system here
    }
}
```

### Health Check Implementation

```javascript
// Comprehensive API health check
async function healthCheck() {
    const checks = [
        {
            name: 'Basic Connectivity',
            test: () => fetch('https://oda.ft.dk/api/Sag?%24top=1')
        },
        {
            name: 'Performance Baseline',
            test: async () => {
                const start = performance.now();
                await fetch('https://oda.ft.dk/api/Sag?%24top=5');
                const duration = performance.now() - start;
                if (duration > 1000) throw new Error(`Slow response: ${duration.toFixed(0)}ms`);
                return duration;
            }
        },
        {
            name: 'Filter Functionality',
            test: async () => {
                const response = await fetch('https://oda.ft.dk/api/Sag?%24filter=id gt 1000&%24top=5');
                const data = await response.json();
                if (data.value.length === 0) throw new Error('Filter returned no results');
                return data.value.length;
            }
        }
    ];
    
    const results = [];
    for (const check of checks) {
        try {
            const result = await check.test();
            results.push({ name: check.name, status: 'PASS', result });
        } catch (error) {
            results.push({ name: check.name, status: 'FAIL', error: error.message });
        }
    }
    
    return results;
}
```

## Escalation and Support

### Self-Service Diagnostic Steps

Before escalating issues, complete these diagnostic steps:

1. **Verify Basic Connectivity**
   ```bash
   curl -I https://oda.ft.dk/api/Sag
   # Expected: HTTP 200 with OData headers
   ```

2. **Test URL Encoding**
   ```bash
   # Verify %24 encoding works
   curl "https://oda.ft.dk/api/Sag?%24top=1" | jq '.value | length'
   # Expected: 1
   ```

3. **Check Filter Field Names**
   ```bash
   # Download metadata for field validation
   curl "https://oda.ft.dk/api/\$metadata" > metadata.xml
   # Search for entity definitions and property names
   ```

4. **Monitor Response Sizes**
   ```bash
   # Check for silent filter failures
   YOUR_QUERY_HERE | jq '.value | length'
   # If >100, investigate query construction
   ```

### When to Escalate

**Escalate immediately for:**
- API returning HTTP 5xx errors
- Response times >10 seconds consistently
- Complete API unavailability
- Data corruption or inconsistencies

**Document for escalation:**
- Exact API URLs causing issues
- HTTP status codes and response times
- Error messages (if any)
- Frequency and impact assessment
- Diagnostic steps already completed

### Documentation and Knowledge Management

**Issue Documentation Template:**
```markdown
## Issue: [Brief Description]

**Date/Time:** [When first observed]
**Severity:** [High/Medium/Low]
**Impact:** [Systems/users affected]

**Symptoms:**
- [Specific behaviors observed]
- [Error messages received]
- [Performance metrics]

**Root Cause:**
[What investigation revealed]

**Resolution:**
[Steps taken to resolve]

**Prevention:**
[Changes made to prevent recurrence]

**Related Issues:**
[Links to similar problems]
```

## Quick Reference Guide

### Critical API Behaviors
- **Maximum 100 records** returned per query (silently capped)
- **Invalid filter fields** silently ignored (returns all records)
- **URL encoding required**: Use `%24` instead of `$`
- **Read-only API**: All write operations return HTTP 501
- **No rate limiting** detected in testing

### Performance Expectations
- Small queries (d50 records): 85-150ms
- Full page (100 records): 90-300ms
- Complex expansions: 200ms-3s
- No timeout limits observed (tested up to 10,000 records)

### Error Code Quick Reference
| HTTP Code | Meaning | Action |
|-----------|---------|--------|
| 400 | Bad Request | Check OData syntax, expansion parameters |
| 404 | Not Found | Verify entity names, record IDs |
| 501 | Not Implemented | Don't use POST/PUT/DELETE operations |

## Next Steps

For specific troubleshooting scenarios, see:

- **[Common Errors](common-errors.md)** - Detailed error scenarios and solutions
- **[Diagnostic Commands](diagnostic-commands.md)** - Ready-to-use diagnostic scripts
- **[Support](support.md)** - Contact information and escalation procedures

For proactive monitoring setup, see:
- **[Query Optimization](../performance/query-optimization.md)** - Performance tuning strategies
- **[Concurrent Requests](../performance/concurrent-requests.md)** - Load testing and scaling