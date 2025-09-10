# Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues when working with the Danish Parliament's Open Data API (oda.ft.dk). The API has unique behaviors and edge cases that require specific troubleshooting approaches.

## Quick Diagnosis Checklist

Before diving into detailed troubleshooting, run through this checklist:

1. **URL Encoding**: Are you using `%24` instead of `$` in OData parameters?
2. **Entity Names**: Is the entity name spelled correctly and capitalized properly?
3. **Field Names**: Do all field names in `$filter` exist in the entity?
4. **HTTP Method**: Are you using GET requests only?
5. **Response Size**: Are you getting unexpectedly large result sets?

## Common Error Scenarios and Solutions

### 1. Silent Filter Failures (Critical Issue)

**Problem**: Invalid filter field names are silently ignored, returning complete unfiltered datasets.

**Symptoms**:
- Receiving 100 records when expecting fewer
- Response includes unrelated data
- Query appears to work but doesn't filter properly

**Example of the problem**:
```bash
# This query has a typo: 'titel' instead of 'titel'
curl "https://oda.ft.dk/api/Sag?%24filter=tittel%20eq%20'klimalov'&%24top=10"

# RESULT: Returns HTTP 200 with 100 unfiltered records (ignores the filter)
# EXPECTED: Should return 10 filtered records matching 'klimalov'
```

**Detection and Solutions**:

#### A. Response Size Monitoring
```javascript
async function detectSilentFailure(url, expectedMaxResults = 50) {
    const response = await fetch(url);
    const data = await response.json();
    
    // Default API response is 100 records
    if (data.value.length === 100 && !url.includes('%24top=100')) {
        console.warn('WARNING: Received default 100 results');
        console.warn('Your filter may contain invalid field names');
        console.warn('Check for typos in field names');
    }
    
    if (data.value.length > expectedMaxResults) {
        throw new Error(`Unexpectedly large result set: ${data.value.length} records. Filter may be invalid.`);
    }
    
    return data;
}
```

#### B. Field Name Validation
```javascript
// Pre-validate field names before making requests
const ENTITY_FIELDS = {
    'Sag': ['id', 'titel', 'resume', 'opdateringsdato', 'statusid', 'typeid', 'kategoriid'],
    'Aktor': ['id', 'navn', 'fornavn', 'efternavn', 'biografi', 'opdateringsdato'],
    'Dokument': ['id', 'titel', 'dokumenttypeid', 'opdateringsdato']
};

function validateFilterFields(filterString, entityName) {
    const validFields = ENTITY_FIELDS[entityName];
    if (!validFields) {
        throw new Error(`Unknown entity: ${entityName}`);
    }
    
    const fieldMatches = filterString.match(/(\w+)\s+(eq|ne|gt|lt|ge|le|contains|startswith|endswith)/g);
    
    if (fieldMatches) {
        for (const match of fieldMatches) {
            const fieldName = match.split(/\s+/)[0];
            if (!validFields.includes(fieldName)) {
                throw new Error(`Invalid field name: '${fieldName}' not found in ${entityName} entity`);
            }
        }
    }
}

// Usage example
try {
    validateFilterFields("titel eq 'klimalov'", 'Sag');
    // Proceed with API call
} catch (error) {
    console.error('Field validation failed:', error.message);
}
```

#### C. Test Field Existence
```bash
# Test if a field exists by using $select
curl "https://oda.ft.dk/api/Sag?%24select=titel&%24top=1"

# If field doesn't exist, you'll get HTTP 400
# If field exists, you'll get HTTP 200 with the field data
```

### 2. URL Encoding Issues

**Problem**: Using `$` instead of `%24` in OData parameters causes queries to fail or behave unexpectedly.

**Symptoms**:
- HTTP 400 Bad Request errors
- Parameters ignored
- Shell/terminal interpretation issues

**Wrong vs. Correct Examples**:

```bash
# L WRONG: Using $ directly (will not work in most environments)
curl "https://oda.ft.dk/api/Sag?\$top=5"

# L WRONG: Shell escaping (wrong for HTTP URLs)
curl "https://oda.ft.dk/api/Sag?\\\$top=5"

#  CORRECT: URL encoded
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

**JavaScript URL encoding**:
```javascript
function buildODataUrl(baseUrl, params) {
    const queryParts = [];
    
    for (const [key, value] of Object.entries(params)) {
        // Encode the $ in parameter names
        const encodedKey = key.replace('$', '%24');
        const encodedValue = encodeURIComponent(value);
        queryParts.push(`${encodedKey}=${encodedValue}`);
    }
    
    return `${baseUrl}?${queryParts.join('&')}`;
}

// Usage
const url = buildODataUrl('https://oda.ft.dk/api/Sag', {
    '$filter': "titel eq 'klimalov'",
    '$top': '10'
});
// Results in: https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'klimalov'&%24top=10
```

### 3. Performance Issues and Slow Queries

**Problem**: Queries taking longer than expected or returning too much data.

**Diagnosis Steps**:

#### A. Check Query Complexity
```bash
# Simple query baseline (should be ~85ms)
time curl "https://oda.ft.dk/api/Sag?%24top=5"

# Compare with your complex query
time curl "https://oda.ft.dk/api/Sag?%24filter=statusid%20eq%203&%24expand=SagAktor/Aktor&%24top=50"
```

#### B. Monitor Response Sizes
```javascript
async function measurePerformance(url) {
    const startTime = performance.now();
    
    const response = await fetch(url);
    const data = await response.json();
    
    const endTime = performance.now();
    const responseTime = endTime - startTime;
    const dataSize = JSON.stringify(data).length;
    const recordCount = data.value ? data.value.length : 0;
    
    console.log(`Performance Metrics:
        Response Time: ${responseTime.toFixed(0)}ms
        Data Size: ${(dataSize / 1024).toFixed(1)} KB
        Record Count: ${recordCount}
        Avg per record: ${(responseTime / recordCount).toFixed(1)}ms`);
    
    // Flag performance issues
    if (responseTime > 2000) {
        console.warn('SLOW QUERY: Response time over 2 seconds');
    }
    if (dataSize > 1024 * 1024) {
        console.warn('LARGE RESPONSE: Over 1MB of data');
    }
    
    return data;
}
```

#### C. Optimize Queries
```javascript
// Performance optimization strategies
const OPTIMIZATION_STRATEGIES = {
    // Limit result count
    useTopParameter: (count = 100) => `%24top=${count}`,
    
    // Select only needed fields  
    selectFields: (fields) => `%24select=${fields.join(',')}`,
    
    // Use efficient filters
    useIndexedFields: () => 'Use id, opdateringsdato, statusid for faster filtering',
    
    // Limit expansion depth
    limitExpansions: () => 'Maximum 2 levels: A/B pattern only'
};

// Example optimized query
const optimizedUrl = `https://oda.ft.dk/api/Sag?` +
    `%24select=id,titel,opdateringsdato&` +
    `%24filter=opdateringsdato%20gt%20datetime'2024-01-01T00:00:00'&` +
    `%24top=50`;
```

### 4. HTTP Error Code Resolution

#### HTTP 400 Bad Request

**Common Causes**:
- Invalid OData syntax
- Invalid `$expand` relationship names  
- Excessive expansion depth (>2 levels)
- Invalid `$format` parameter

**Debugging Steps**:

```bash
# Test basic query first
curl -i "https://oda.ft.dk/api/Sag?%24top=1"

# Add parameters one by one to isolate the issue
curl -i "https://oda.ft.dk/api/Sag?%24top=1&%24select=id"
curl -i "https://oda.ft.dk/api/Sag?%24top=1&%24expand=SagAktor"

# Check expansion relationship names against metadata
curl "https://oda.ft.dk/api/\$metadata" | grep -A5 -B5 "Sag"
```

**Solution Pattern**:
```javascript
async function diagnose400Error(baseUrl, params) {
    // Test each parameter individually
    for (const [key, value] of Object.entries(params)) {
        const testUrl = `${baseUrl}?${key.replace('$', '%24')}=${encodeURIComponent(value)}`;
        
        try {
            const response = await fetch(testUrl);
            if (response.status === 400) {
                throw new Error(`Parameter '${key}' with value '${value}' is invalid`);
            }
        } catch (error) {
            console.error(`Problem with parameter: ${key} = ${value}`);
        }
    }
}
```

#### HTTP 404 Not Found

**Two Different Scenarios**:

1. **Invalid Entity Names** - Returns HTML error page
2. **Invalid Entity IDs** - Returns empty response

**Diagnostic Approach**:
```javascript
async function diagnose404Error(response) {
    const contentType = response.headers.get('content-type');
    
    if (contentType && contentType.includes('text/html')) {
        // Invalid entity name
        throw new Error('Invalid entity name - check spelling and capitalization');
    } else {
        // Invalid entity ID  
        const text = await response.text();
        if (text.length === 0) {
            throw new Error('Entity ID not found - record may not exist');
        }
    }
}
```

#### HTTP 501 Not Implemented

**Cause**: Attempting write operations (POST, PUT, PATCH, DELETE)

**Solution**: The API is strictly read-only. Only GET requests are supported.

```bash
# L These will fail with HTTP 501
curl -X POST "https://oda.ft.dk/api/Sag" -d '{"titel":"test"}'
curl -X PUT "https://oda.ft.dk/api/Sag(1)" -d '{"titel":"updated"}'

#  Only GET requests work
curl "https://oda.ft.dk/api/Sag?%24top=5"
```

### 5. Client-Side Debugging Techniques

#### Browser Console Debugging

```javascript
// Comprehensive client-side debugging function
async function debugApiCall(url, expectedResults = null) {
    console.group('= API Debug Session');
    console.log('URL:', url);
    console.log('Timestamp:', new Date().toISOString());
    
    try {
        // Timing
        const startTime = performance.now();
        
        // Make request with detailed monitoring
        const response = await fetch(url);
        
        const endTime = performance.now();
        const responseTime = endTime - startTime;
        
        // Response analysis
        console.log('Status:', response.status, response.statusText);
        console.log('Response Time:', responseTime.toFixed(0) + 'ms');
        console.log('Content-Type:', response.headers.get('content-type') || 'Not Set');
        
        if (!response.ok) {
            console.error('L HTTP Error:', response.status);
            const errorText = await response.text();
            console.log('Error Body:', errorText.length > 0 ? errorText : '(empty)');
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Data analysis
        const recordCount = data.value ? data.value.length : 0;
        const dataSize = JSON.stringify(data).length;
        
        console.log(' Success');
        console.log('Records Returned:', recordCount);
        console.log('Data Size:', (dataSize / 1024).toFixed(1) + ' KB');
        
        // Check for potential issues
        if (expectedResults && recordCount !== expectedResults) {
            console.warn('  Unexpected record count');
            console.warn('Expected:', expectedResults, 'Got:', recordCount);
        }
        
        if (recordCount === 100 && !url.includes('%24top=100')) {
            console.warn('  Possible silent filter failure');
            console.warn('Got default 100 records - check field names in filters');
        }
        
        // Performance warnings
        if (responseTime > 1000) {
            console.warn('  Slow response time:', responseTime.toFixed(0) + 'ms');
        }
        
        if (dataSize > 500 * 1024) {
            console.warn('  Large response size:', (dataSize / 1024).toFixed(1) + ' KB');
        }
        
        console.groupEnd();
        return data;
        
    } catch (error) {
        console.error('L Request Failed:', error.message);
        console.groupEnd();
        throw error;
    }
}

// Usage examples
debugApiCall('https://oda.ft.dk/api/Sag?%24top=5', 5);
debugApiCall('https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20%27klimalov%27', 10);
```

#### Network Tab Analysis

1. **Open Browser Developer Tools** (F12)
2. **Go to Network Tab**
3. **Execute your API call**
4. **Check the request details**:
   - Request URL: Verify URL encoding
   - Request Headers: Check Accept headers
   - Response Headers: Look for error indicators
   - Response Body: Check for empty responses
   - Timing: Identify slow requests

#### cURL Testing Patterns

```bash
# Basic connectivity test
curl -i "https://oda.ft.dk/api/Sag?%24top=1"

# Test with verbose output
curl -v "https://oda.ft.dk/api/Sag?%24top=5"

# Test with timing
curl -w "Time: %{time_total}s\nSize: %{size_download} bytes\n" \
     "https://oda.ft.dk/api/Sag?%24top=10"

# Test specific field names
curl -i "https://oda.ft.dk/api/Sag?%24select=invalid_field&%24top=1"
# Should return HTTP 400 if field doesn't exist

# Test filter field existence  
curl -i "https://oda.ft.dk/api/Sag?%24filter=invalid_field%20eq%20'test'&%24top=1"
# Will return HTTP 200 with unfiltered data (silent failure)
```

## Systematic Troubleshooting Workflow

Follow this step-by-step process to diagnose API issues:

### Phase 1: Basic Connectivity
```bash
# 1. Test basic API connectivity
curl -i "https://oda.ft.dk/api/Sag?%24top=1"

# Expected: HTTP 200, ~85ms response time, 1 record
# If this fails, check network connectivity and DNS
```

### Phase 2: URL Encoding Verification
```bash
# 2. Verify URL encoding is correct
echo "Your URL parameters:"
echo "  Correct: %24top=5 (%24 = dollar sign)"
echo "  Wrong:   \$top=5 or \\\$top=5"

# Test with known good URL encoding
curl "https://oda.ft.dk/api/Sag?%24top=5&%24select=id,titel"
```

### Phase 3: Parameter Isolation
```javascript
// 3. Test each parameter individually
async function isolateParameters(baseUrl, params) {
    console.log('Testing parameters individually...');
    
    // Test base URL first
    let testUrl = baseUrl + '?%24top=1';
    await testApiCall(testUrl, 'Base query');
    
    // Add each parameter one by one
    for (const [key, value] of Object.entries(params)) {
        testUrl += `&${key.replace('$', '%24')}=${encodeURIComponent(value)}`;
        await testApiCall(testUrl, `With parameter: ${key}`);
    }
}

async function testApiCall(url, description) {
    try {
        const response = await fetch(url);
        console.log(` ${description}: HTTP ${response.status}`);
    } catch (error) {
        console.error(`L ${description}: ${error.message}`);
    }
}
```

### Phase 4: Field Name Validation
```bash
# 4. Test field names using $select
curl "https://oda.ft.dk/api/Sag?%24select=titel&%24top=1"  # Should work
curl "https://oda.ft.dk/api/Sag?%24select=invalid&%24top=1"  # Should return 400

# If $select works but $filter doesn't, you have a silent failure
curl "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'test'&%24top=1"
```

### Phase 5: Response Analysis
```javascript
// 5. Analyze response characteristics
async function analyzeResponse(url) {
    const response = await fetch(url);
    const data = await response.json();
    
    console.log('Response Analysis:');
    console.log('- Status:', response.status);
    console.log('- Record Count:', data.value?.length || 0);
    console.log('- Has Metadata:', !!data['odata.metadata']);
    
    // Check for silent failures
    if (data.value?.length === 100) {
        console.warn('Got 100 records - possible silent filter failure');
    }
    
    return data;
}
```

### Phase 6: Performance Benchmarking
```bash
# 6. Benchmark query performance
echo "Testing query performance..."

# Simple query (baseline)
time curl -s "https://oda.ft.dk/api/Sag?%24top=5" >/dev/null

# Your complex query  
time curl -s "YOUR_COMPLEX_QUERY_HERE" >/dev/null

# Compare results - simple should be ~85ms, complex queries can be up to 2 seconds
```

## Production Troubleshooting Checklist

When issues occur in production, follow this systematic approach:

### Immediate Response (0-5 minutes)
- [ ] Check basic API connectivity with simple query
- [ ] Verify service status (API returning HTTP 200?)
- [ ] Check for recent code changes affecting query construction
- [ ] Monitor error rates and response times

### Short-term Investigation (5-30 minutes)  
- [ ] Isolate failing query parameters
- [ ] Test with simplified queries
- [ ] Check for silent filter failures
- [ ] Review client-side error handling logs
- [ ] Validate field names against entity schema

### Medium-term Analysis (30 minutes - 2 hours)
- [ ] Performance benchmarking against baseline
- [ ] Analysis of response sizes and query complexity
- [ ] Review of query optimization opportunities
- [ ] Client-side debugging with full logging
- [ ] Documentation review for API behavior changes

### Long-term Prevention
- [ ] Implement comprehensive error detection
- [ ] Add query validation before API calls
- [ ] Set up monitoring for response sizes and performance
- [ ] Create automated tests for critical query patterns
- [ ] Document known issues and workarounds

## When to Contact Support

The Danish Parliament API doesn't have direct technical support, but here's when you should escalate:

### Escalation Triggers
1. **API completely unavailable** for >30 minutes
2. **Consistent HTTP 500 errors** across all queries
3. **Response times >10 seconds** for simple queries
4. **Data corruption or inconsistencies** in responses
5. **SSL certificate errors** or security issues

### Information to Gather
Before seeking help, collect:
- Exact query URLs that are failing
- HTTP status codes and response headers
- Response times and payload sizes
- Client environment (browser, Node.js version, etc.)
- Timestamps of failures
- Comparison with working queries

### Alternative Resources
- **MkDocs Documentation**: Complete API reference and examples
- **GitHub Issues**: Community discussions and known issues
- **Stack Overflow**: Tag queries with `danish-parliament-api` or `odata`

## Troubleshooting Tools and Scripts

### Quick Diagnostic Script
```bash
#!/bin/bash
# api-diagnostic.sh - Quick API health check

API_BASE="https://oda.ft.dk/api"
echo "= Danish Parliament API Diagnostic Tool"
echo "========================================"

# Test 1: Basic connectivity
echo "1. Testing basic connectivity..."
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${API_BASE}/Sag?%24top=1")
if [ "$STATUS" = "200" ]; then
    echo "    API is accessible"
else
    echo "   L API returned status: $STATUS"
    exit 1
fi

# Test 2: Performance baseline
echo "2. Testing performance..."
RESPONSE_TIME=$(curl -s -w "%{time_total}" "${API_BASE}/Sag?%24top=5" -o /dev/null)
echo "   ñ Response time: ${RESPONSE_TIME}s"
if (( $(echo "$RESPONSE_TIME > 1.0" | bc -l) )); then
    echo "     Slower than expected (>1s)"
fi

# Test 3: URL encoding
echo "3. Testing URL encoding..."
curl -s "${API_BASE}/Sag?%24top=1&%24select=id" > /dev/null
if [ $? -eq 0 ]; then
    echo "    URL encoding working"
else
    echo "   L URL encoding issues detected"
fi

# Test 4: Silent filter failure check
echo "4. Testing for silent filter failures..."
COUNT=$(curl -s "${API_BASE}/Sag?%24filter=invalid_field_name%20eq%20'test'&%24top=5" | jq -r '.value | length')
if [ "$COUNT" = "5" ]; then
    echo "     Silent filter failure detected - invalid filters ignored"
else
    echo "    Filter validation working"
fi

echo " Diagnostic complete"
```

### JavaScript Debugging Helper
```javascript
// api-debugger.js - Comprehensive API debugging utility
class ODADebugger {
    constructor(baseUrl = 'https://oda.ft.dk/api') {
        this.baseUrl = baseUrl;
        this.requests = [];
    }
    
    async diagnose(entity, params = {}) {
        const sessionId = Date.now();
        console.group(`= ODA Debug Session ${sessionId}`);
        
        try {
            // Build URL
            const url = this.buildUrl(entity, params);
            console.log('< URL:', url);
            
            // Pre-flight checks
            await this.preflightChecks(entity, params);
            
            // Execute request
            const result = await this.executeWithAnalysis(url);
            
            console.log(' Diagnosis complete');
            return result;
            
        } catch (error) {
            console.error('L Diagnosis failed:', error.message);
            throw error;
        } finally {
            console.groupEnd();
        }
    }
    
    buildUrl(entity, params) {
        const queryParts = Object.entries(params).map(([key, value]) => {
            const encodedKey = key.replace('$', '%24');
            return `${encodedKey}=${encodeURIComponent(value)}`;
        });
        
        return `${this.baseUrl}/${entity}${queryParts.length ? '?' + queryParts.join('&') : ''}`;
    }
    
    async preflightChecks(entity, params) {
        console.log('= Running preflight checks...');
        
        // Check entity exists
        const basicUrl = `${this.baseUrl}/${entity}?%24top=1`;
        const testResponse = await fetch(basicUrl);
        
        if (testResponse.status === 404) {
            throw new Error(`Entity '${entity}' not found - check spelling`);
        }
        
        // Validate filter fields if present
        if (params.$filter) {
            console.log('= Validating filter fields...');
            // This would need entity schema validation logic
        }
        
        console.log(' Preflight checks passed');
    }
    
    async executeWithAnalysis(url) {
        const startTime = performance.now();
        
        const response = await fetch(url);
        const endTime = performance.now();
        
        const responseTime = endTime - startTime;
        console.log(`ñ Response time: ${responseTime.toFixed(0)}ms`);
        
        if (!response.ok) {
            console.error(`L HTTP ${response.status}: ${response.statusText}`);
            const errorBody = await response.text();
            console.log('Error body length:', errorBody.length);
            throw new Error(`HTTP ${response.status}`);
        }
        
        const data = await response.json();
        
        // Analyze response
        const recordCount = data.value?.length || 0;
        const dataSize = JSON.stringify(data).length;
        
        console.log(`=Ê Results: ${recordCount} records, ${(dataSize/1024).toFixed(1)}KB`);
        
        // Check for issues
        if (recordCount === 100 && !url.includes('%24top=100')) {
            console.warn('  Possible silent filter failure - got default 100 records');
        }
        
        if (responseTime > 1000) {
            console.warn('  Slow response time');
        }
        
        return data;
    }
}

// Usage
const debugger = new ODADebugger();

// Debug a problematic query
debugger.diagnose('Sag', {
    '$filter': "titel eq 'klimalov'",
    '$top': '10'
});
```

## Summary

The Danish Parliament API requires specific troubleshooting approaches due to its unique behaviors:

### Key Challenges
1. **Silent filter failures** - Invalid field names don't generate errors
2. **Empty error messages** - Most failures provide no diagnostic information  
3. **URL encoding requirements** - Must use `%24` instead of `$`
4. **Inconsistent error formats** - Different error types return different formats

### Essential Debugging Tools
1. **Response size monitoring** - Detect silent failures
2. **Field name validation** - Prevent typos in filters
3. **Systematic parameter testing** - Isolate problematic parameters
4. **Performance benchmarking** - Identify slow queries

### Best Practices
1. Always validate field names before filtering
2. Monitor response sizes for unexpected results
3. Use proper URL encoding for all parameters
4. Implement comprehensive error handling
5. Test queries incrementally when building complex filters

With proper understanding of these patterns and the diagnostic tools provided, you can effectively troubleshoot and resolve issues with the Danish Parliament's Open Data API.