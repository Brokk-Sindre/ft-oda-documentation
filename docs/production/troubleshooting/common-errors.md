# Common Errors and Solutions

This comprehensive guide covers the most frequent errors encountered when working with the Danish Parliament's Open Data API (oda.ft.dk) in production environments, along with proven solutions and prevention strategies.

!!! danger "Critical Issue: Silent Filter Failures"
    The API's most dangerous behavior is **silently ignoring invalid filter field names**. This returns complete unfiltered datasets instead of expected filtered results, potentially causing performance issues and incorrect application behavior.

## Quick Error Reference

| Error Type | HTTP Code | Response Time | Impact | Solution |
|------------|-----------|---------------|--------|----------|
| Invalid Filter Fields | 200 OK | ~100ms | **Critical** | Validate field names, monitor result counts |
| Invalid Expansions | 400 | ~44ms | Medium | Check relationship names against metadata |
| Invalid Entity Names | 404 | ~85ms | Low | Verify endpoint spelling |
| URL Encoding Issues | 400/404 | ~50ms | High | Always use `%24` instead of `$` |
| Network Timeouts | N/A | >30s | High | Implement retry logic with backoff |

## 1. Most Common Error Types and Causes

### Silent Filter Failures (Critical Priority)

**Problem:** Invalid field names in `$filter` parameters are silently ignored, returning complete unfiltered datasets.

**Example of Silent Failure:**
```bash
# Query with typo: "title" instead of "titel"
curl "https://oda.ft.dk/api/Sag?%24filter=title%20eq%20'klimaændringer'&%24top=5"
```

**What Happens:**
-  Returns HTTP 200 OK (appears successful)
- L Ignores the filter completely
- L Returns ~100 records instead of 0-5 expected
- L No error indication in response

**Detection Strategy:**
```javascript
async function detectSilentFilterFailure(url, expectedMaxResults) {
    const response = await fetch(url);
    const data = await response.json();
    
    // Check if we got the default 100 records when expecting fewer
    if (data.value.length === 100 && expectedMaxResults < 100) {
        console.warn('Possible silent filter failure detected');
        console.warn(`Expected d${expectedMaxResults} results, got ${data.value.length}`);
        return true;
    }
    
    return false;
}
```

**Prevention:**
```javascript
// Validate field names against known entity schema
const validSagFields = ['id', 'titel', 'resume', 'afstemningskonklusion', 'baggrundsmateriale'];

function validateFilterFields(filterString, validFields) {
    const fieldNames = filterString.match(/(\w+)\s+(eq|ne|gt|lt|ge|le)/g) || [];
    
    for (const match of fieldNames) {
        const field = match.split(/\s+/)[0];
        if (!validFields.includes(field)) {
            throw new Error(`Invalid field name in filter: ${field}`);
        }
    }
}
```

### URL Encoding Errors (High Priority)

**Problem:** Using literal `$` characters in OData parameters instead of `%24` encoding.

**Wrong Approach:**
```bash
# This will fail or behave unexpectedly
curl "https://oda.ft.dk/api/Sag?$filter=titel eq 'test'&$top=5"
```

**Correct Approach:**
```bash
# Always use %24 for $ in OData parameters
curl "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'test'&%24top=5"
```

**JavaScript URL Encoding Solution:**
```javascript
class ODataQueryBuilder {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.params = new URLSearchParams();
    }
    
    filter(expression) {
        this.params.set('$filter', expression);
        return this;
    }
    
    top(count) {
        this.params.set('$top', count.toString());
        return this;
    }
    
    build() {
        const encodedParams = this.params.toString().replace(/\$/g, '%24');
        return `${this.baseUrl}?${encodedParams}`;
    }
}

// Usage
const url = new ODataQueryBuilder('https://oda.ft.dk/api/Sag')
    .filter("titel eq 'klimaændringer'")
    .top(10)
    .build();
```

### Invalid Expansion Relationships

**Problem:** Using non-existent relationship names in `$expand` parameters.

**Example Error:**
```bash
curl "https://oda.ft.dk/api/Sag?%24expand=NonExistentRelation"
```

**Response:**
```
HTTP/1.1 400 Bad Request
Content-Length: 0
```

**Solution - Relationship Validation:**
```javascript
// Map of valid expansions for each entity
const validExpansions = {
    'Sag': ['Sagstrin', 'Sagskategori', 'SagAktør', 'SagDokument'],
    'Aktør': ['AktørType', 'SagAktør', 'DokumentAktør'],
    'Dokument': ['Fil', 'DokumentAktør', 'SagDokument']
};

function validateExpansion(entityName, expansions) {
    const validForEntity = validExpansions[entityName] || [];
    const requestedExpansions = expansions.split(',').map(e => e.trim());
    
    for (const expansion of requestedExpansions) {
        const baseExpansion = expansion.split('/')[0]; // Handle nested expansions
        if (!validForEntity.includes(baseExpansion)) {
            throw new Error(`Invalid expansion '${baseExpansion}' for entity ${entityName}`);
        }
    }
}
```

## 2. Silent Failure Detection and Prevention

### Automated Detection System

```javascript
class SilentFailureDetector {
    constructor(apiBase) {
        this.apiBase = apiBase;
        this.metrics = {
            suspiciousResults: 0,
            totalQueries: 0
        };
    }
    
    async query(endpoint, params = {}) {
        this.metrics.totalQueries++;
        
        const url = this.buildUrl(endpoint, params);
        const response = await fetch(url);
        const data = await response.json();
        
        // Detection patterns
        const suspiciousPatterns = [
            this.detectFilterIgnored(params, data),
            this.detectUnexpectedResultCount(params, data),
            this.detectDefaultPageSize(data)
        ];
        
        if (suspiciousPatterns.some(Boolean)) {
            this.metrics.suspiciousResults++;
            console.warn('Silent failure detected:', {
                url,
                patterns: suspiciousPatterns.filter(Boolean),
                resultCount: data.value.length
            });
        }
        
        return data;
    }
    
    detectFilterIgnored(params, data) {
        return params.$filter && data.value.length === 100 
            ? 'Filter may have been ignored - got default page size' 
            : null;
    }
    
    detectUnexpectedResultCount(params, data) {
        const topValue = params.$top;
        return topValue && data.value.length > topValue 
            ? `Expected max ${topValue} results, got ${data.value.length}` 
            : null;
    }
    
    detectDefaultPageSize(data) {
        return data.value.length === 100 
            ? 'Got exactly 100 results (default page size)' 
            : null;
    }
}
```

### Prevention Strategies

**1. Field Name Validation:**
```javascript
async function validateFieldsAgainstMetadata(entityName, fields) {
    const metadataUrl = 'https://oda.ft.dk/api/$metadata';
    const response = await fetch(metadataUrl);
    const metadata = await response.text();
    
    // Parse XML metadata to extract valid field names
    const parser = new DOMParser();
    const doc = parser.parseFromString(metadata, 'application/xml');
    
    const entityType = doc.querySelector(`EntityType[Name="${entityName}"]`);
    const validFields = Array.from(entityType.querySelectorAll('Property'))
        .map(prop => prop.getAttribute('Name'));
    
    for (const field of fields) {
        if (!validFields.includes(field)) {
            throw new Error(`Invalid field '${field}' for entity ${entityName}`);
        }
    }
}
```

**2. Result Size Monitoring:**
```javascript
function createResultSizeMonitor(warningThreshold = 1000) {
    return {
        monitor(query, results) {
            if (results.length > warningThreshold) {
                console.warn(`Large result set: ${results.length} records for query:`, query);
                console.warn('This may indicate an ignored filter parameter');
            }
        }
    };
}
```

## 3. HTTP Error Code Interpretation and Handling

### Complete Error Response Mapping

```javascript
class ApiErrorHandler {
    static handleResponse(response, requestUrl) {
        switch (response.status) {
            case 200:
                // Success, but check for silent failures
                return this.handleSuccess(response, requestUrl);
            
            case 400:
                return this.handle400(response);
            
            case 404:
                return this.handle404(response, requestUrl);
            
            case 500:
                return this.handle500(response);
            
            case 501:
                return this.handle501(response);
            
            default:
                return this.handleUnknown(response);
        }
    }
    
    static async handle400(response) {
        const body = await response.text();
        
        if (body.trim() === '') {
            throw new Error('Bad Request: Invalid OData syntax. Common causes: ' +
                'invalid $expand relationships, excessive expansion depth (>2 levels), ' +
                'malformed $filter expressions');
        }
        
        throw new Error(`Bad Request: ${body}`);
    }
    
    static async handle404(response, requestUrl) {
        const body = await response.text();
        
        if (body.includes('<!DOCTYPE html>')) {
            throw new Error('Entity not found: Check entity name spelling in URL');
        } else if (body.trim() === '') {
            throw new Error('Record not found: Invalid ID or record does not exist');
        }
        
        throw new Error(`Not Found: ${body || 'Resource not available'}`);
    }
    
    static async handle501(response) {
        const body = await response.text();
        throw new Error('Operation not supported: The API is read-only. ' +
            'POST, PUT, PATCH, and DELETE operations are not allowed.');
    }
}
```

## 4. OData Parameter Errors and Solutions

### Parameter Validation System

```javascript
class ODataValidator {
    static validateTop(value) {
        const num = parseInt(value);
        if (isNaN(num) || num < 1) {
            throw new Error('$top must be a positive integer');
        }
        if (num > 1000) {
            console.warn('$top values >1000 may be ignored by the API');
        }
        return num;
    }
    
    static validateSkip(value) {
        const num = parseInt(value);
        if (isNaN(num) || num < 0) {
            throw new Error('$skip must be a non-negative integer');
        }
        return num;
    }
    
    static validateFilter(expression) {
        // Check for common syntax errors
        const patterns = [
            { regex: /\beq\s+[^'"]/, error: 'String values must be quoted in filters' },
            { regex: /\s(and|or)\s*$/, error: 'Filter expression ends with logical operator' },
            { regex: /[^=!<>]\s*=\s*[^=]/, error: 'Use "eq" instead of "=" in OData filters' }
        ];
        
        for (const pattern of patterns) {
            if (pattern.regex.test(expression)) {
                throw new Error(`Filter validation error: ${pattern.error}`);
            }
        }
    }
    
    static validateExpand(expression, entityName) {
        const maxDepth = 2;
        const expansions = expression.split(',');
        
        for (const expansion of expansions) {
            const depth = expansion.split('/').length;
            if (depth > maxDepth) {
                throw new Error(`Expansion depth ${depth} exceeds maximum ${maxDepth}: ${expansion}`);
            }
        }
    }
}
```

### Common Parameter Patterns

```javascript
// Safe OData query builder with validation
class SafeODataBuilder {
    constructor(baseUrl, entityName) {
        this.baseUrl = baseUrl;
        this.entityName = entityName;
        this.params = {};
    }
    
    select(fields) {
        if (Array.isArray(fields)) {
            this.params.$select = fields.join(',');
        } else {
            this.params.$select = fields;
        }
        return this;
    }
    
    filter(expression) {
        ODataValidator.validateFilter(expression);
        this.params.$filter = expression;
        return this;
    }
    
    top(count) {
        this.params.$top = ODataValidator.validateTop(count);
        return this;
    }
    
    skip(count) {
        this.params.$skip = ODataValidator.validateSkip(count);
        return this;
    }
    
    expand(relationships) {
        ODataValidator.validateExpand(relationships, this.entityName);
        this.params.$expand = relationships;
        return this;
    }
    
    build() {
        const params = new URLSearchParams();
        
        for (const [key, value] of Object.entries(this.params)) {
            params.set(key, value.toString());
        }
        
        // Properly encode $ characters
        const queryString = params.toString().replace(/\$/g, '%24');
        return `${this.baseUrl}/${this.entityName}?${queryString}`;
    }
}
```

## 5. Network Connectivity and Timeout Errors

### Robust HTTP Client Implementation

```javascript
class RobustApiClient {
    constructor(baseUrl, options = {}) {
        this.baseUrl = baseUrl;
        this.options = {
            timeout: 30000,
            retryAttempts: 3,
            retryDelay: 1000,
            ...options
        };
    }
    
    async request(url, options = {}) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), this.options.timeout);
        
        try {
            const response = await this.retryRequest(url, {
                ...options,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            return response;
            
        } catch (error) {
            clearTimeout(timeoutId);
            throw this.enhanceError(error, url);
        }
    }
    
    async retryRequest(url, options, attempt = 1) {
        try {
            const response = await fetch(url, options);
            
            if (!response.ok && this.shouldRetry(response.status) && attempt < this.options.retryAttempts) {
                await this.delay(this.options.retryDelay * attempt);
                return this.retryRequest(url, options, attempt + 1);
            }
            
            return response;
            
        } catch (error) {
            if (attempt < this.options.retryAttempts && this.isRetryableError(error)) {
                await this.delay(this.options.retryDelay * attempt);
                return this.retryRequest(url, options, attempt + 1);
            }
            throw error;
        }
    }
    
    shouldRetry(status) {
        return status >= 500 || status === 429; // Server errors and rate limiting
    }
    
    isRetryableError(error) {
        return error.name === 'AbortError' || 
               error.message.includes('network') ||
               error.message.includes('timeout') ||
               error.message.includes('ENOTFOUND');
    }
    
    enhanceError(error, url) {
        if (error.name === 'AbortError') {
            return new Error(`Request timeout after ${this.options.timeout}ms: ${url}`);
        }
        
        if (error.message.includes('ENOTFOUND')) {
            return new Error(`DNS resolution failed for: ${url}`);
        }
        
        if (error.message.includes('ECONNREFUSED')) {
            return new Error(`Connection refused: ${url}`);
        }
        
        return error;
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### Network Error Diagnostics

```javascript
class NetworkDiagnostics {
    static async diagnoseConnectivity(apiUrl) {
        const tests = [
            this.testDNSResolution(apiUrl),
            this.testHTTPSHandshake(apiUrl),
            this.testBasicRequest(apiUrl),
            this.testApiResponse(apiUrl)
        ];
        
        const results = await Promise.allSettled(tests);
        return this.formatDiagnosticReport(results);
    }
    
    static async testDNSResolution(url) {
        const hostname = new URL(url).hostname;
        // In Node.js, you could use dns.resolve()
        // In browser, this is handled automatically by fetch
        return { test: 'DNS Resolution', status: 'automatic' };
    }
    
    static async testHTTPSHandshake(url) {
        const start = Date.now();
        try {
            const response = await fetch(url, { method: 'HEAD' });
            return {
                test: 'HTTPS Handshake',
                status: response.ok ? 'success' : 'failed',
                duration: Date.now() - start,
                details: `HTTP ${response.status}`
            };
        } catch (error) {
            return {
                test: 'HTTPS Handshake',
                status: 'failed',
                duration: Date.now() - start,
                error: error.message
            };
        }
    }
    
    static async testBasicRequest(url) {
        try {
            const response = await fetch(`${url}/Sag?%24top=1`);
            return {
                test: 'Basic API Request',
                status: response.ok ? 'success' : 'failed',
                statusCode: response.status
            };
        } catch (error) {
            return {
                test: 'Basic API Request',
                status: 'failed',
                error: error.message
            };
        }
    }
    
    static async testApiResponse(url) {
        try {
            const response = await fetch(`${url}/Sag?%24top=1`);
            const data = await response.json();
            return {
                test: 'API Response Parsing',
                status: data.value ? 'success' : 'failed',
                dataReceived: !!data.value
            };
        } catch (error) {
            return {
                test: 'API Response Parsing',
                status: 'failed',
                error: error.message
            };
        }
    }
}
```

## 6. Authentication and Authorization Errors

### No Authentication Required

The Danish Parliament API requires **no authentication**. However, developers may encounter related issues:

**Common Misconceptions:**
```javascript
// L WRONG: Adding unnecessary authentication headers
fetch('https://oda.ft.dk/api/Sag', {
    headers: {
        'Authorization': 'Bearer token',  // Not needed!
        'X-API-Key': 'key'              // Not needed!
    }
});

//  CORRECT: No authentication headers needed
fetch('https://oda.ft.dk/api/Sag');
```

**Corporate Network Issues:**
```javascript
// Check for proxy or firewall interference
class CorporateNetworkHandler {
    static async testDirectAccess() {
        try {
            const response = await fetch('https://oda.ft.dk/api/Sag?%24top=1');
            return response.ok;
        } catch (error) {
            if (error.message.includes('407')) {
                throw new Error('Proxy authentication required - configure corporate proxy settings');
            }
            if (error.message.includes('blocked')) {
                throw new Error('Corporate firewall may be blocking access to oda.ft.dk');
            }
            throw error;
        }
    }
}
```

## 7. Data Validation and Integrity Errors

### Danish Character Handling

```javascript
class DanishTextValidator {
    static validateEncoding(text) {
        // Check for proper UTF-8 encoding of Danish characters
        const danishChars = /[æøåÆØÅ]/;
        const corruptedChars = /[ÃÂ¦Ã¸Ã¥]/; // Common corruption patterns
        
        if (corruptedChars.test(text)) {
            throw new Error('Text appears to have encoding corruption - ensure UTF-8 handling');
        }
        
        return danishChars.test(text);
    }
    
    static cleanHtmlContent(htmlString) {
        if (!htmlString) return '';
        
        // Remove HTML tags but preserve content
        return htmlString
            .replace(/<[^>]*>/g, '') // Remove HTML tags
            .replace(/&nbsp;/g, ' ') // Convert &nbsp; to space
            .replace(/&amp;/g, '&')  // Convert &amp; to &
            .replace(/&lt;/g, '<')   // Convert &lt; to <
            .replace(/&gt;/g, '>')   // Convert &gt; to >
            .trim();
    }
}
```

### Data Consistency Checks

```javascript
class DataIntegrityValidator {
    static validateRelationshipConsistency(parentEntity, childEntities) {
        const parentId = parentEntity.id;
        
        for (const child of childEntities) {
            const foreignKeyField = this.getForeignKeyField(child);
            if (child[foreignKeyField] !== parentId) {
                console.warn(`Relationship inconsistency: Child ${child.id} ` +
                    `has ${foreignKeyField}=${child[foreignKeyField]}, expected ${parentId}`);
            }
        }
    }
    
    static validateDateFields(entity) {
        const dateFields = ['opdateringsdato', 'dato', 'modtagelsesdato'];
        
        for (const field of dateFields) {
            if (entity[field]) {
                const date = new Date(entity[field]);
                if (isNaN(date.getTime())) {
                    throw new Error(`Invalid date format in field ${field}: ${entity[field]}`);
                }
                
                // Check for reasonable date ranges
                const now = new Date();
                const year1950 = new Date('1950-01-01');
                
                if (date > now) {
                    console.warn(`Future date found in ${field}: ${entity[field]}`);
                }
                if (date < year1950) {
                    console.warn(`Very old date found in ${field}: ${entity[field]}`);
                }
            }
        }
    }
}
```

## 8. Performance-Related Errors and Bottlenecks

### Query Performance Monitoring

```javascript
class PerformanceMonitor {
    constructor() {
        this.metrics = [];
    }
    
    async measureQuery(queryFunction, metadata) {
        const start = performance.now();
        let result, error = null;
        
        try {
            result = await queryFunction();
        } catch (e) {
            error = e;
        }
        
        const duration = performance.now() - start;
        const metric = {
            ...metadata,
            duration,
            timestamp: new Date(),
            success: !error,
            error: error?.message,
            resultCount: result?.value?.length || 0
        };
        
        this.metrics.push(metric);
        this.analyzePerformance(metric);
        
        if (error) throw error;
        return result;
    }
    
    analyzePerformance(metric) {
        // Slow query detection
        if (metric.duration > 5000) {
            console.warn('Slow query detected:', metric);
        }
        
        // Large result set detection
        if (metric.resultCount > 1000) {
            console.warn('Large result set:', metric);
        }
        
        // Pattern analysis
        const recentMetrics = this.metrics.slice(-10);
        const avgDuration = recentMetrics.reduce((sum, m) => sum + m.duration, 0) / recentMetrics.length;
        
        if (metric.duration > avgDuration * 2) {
            console.warn('Query significantly slower than recent average:', {
                current: metric.duration,
                average: avgDuration
            });
        }
    }
    
    getReport() {
        return {
            totalQueries: this.metrics.length,
            averageDuration: this.metrics.reduce((sum, m) => sum + m.duration, 0) / this.metrics.length,
            slowQueries: this.metrics.filter(m => m.duration > 2000).length,
            failedQueries: this.metrics.filter(m => !m.success).length,
            largeResults: this.metrics.filter(m => m.resultCount > 1000).length
        };
    }
}
```

### Performance Optimization Strategies

```javascript
class PerformanceOptimizer {
    static optimizeQuery(query) {
        const suggestions = [];
        
        // Check for unnecessary fields
        if (!query.includes('$select')) {
            suggestions.push({
                type: 'select',
                message: 'Consider using $select to limit fields and reduce response size',
                example: '$select=id,titel,opdateringsdato'
            });
        }
        
        // Check for large top values
        const topMatch = query.match(/\$top=(\d+)/);
        if (topMatch && parseInt(topMatch[1]) > 100) {
            suggestions.push({
                type: 'pagination',
                message: 'Large $top values may impact performance. Consider pagination',
                example: 'Use $top=100 with $skip for pagination'
            });
        }
        
        // Check expansion depth
        const expandMatch = query.match(/\$expand=([^&]+)/);
        if (expandMatch) {
            const expansions = expandMatch[1].split(',');
            const deepExpansions = expansions.filter(exp => exp.includes('/'));
            
            if (deepExpansions.length > 0) {
                suggestions.push({
                    type: 'expansion',
                    message: 'Deep expansions may impact performance',
                    example: 'Consider separate queries for complex relationships'
                });
            }
        }
        
        return suggestions;
    }
    
    static createBatchProcessor(apiClient, batchSize = 5) {
        return async function processBatch(queries) {
            const results = [];
            
            for (let i = 0; i < queries.length; i += batchSize) {
                const batch = queries.slice(i, i + batchSize);
                const batchPromises = batch.map(query => 
                    apiClient.query(query).catch(error => ({ error, query }))
                );
                
                const batchResults = await Promise.all(batchPromises);
                results.push(...batchResults);
                
                // Add delay between batches to avoid overwhelming the server
                if (i + batchSize < queries.length) {
                    await new Promise(resolve => setTimeout(resolve, 100));
                }
            }
            
            return results;
        };
    }
}
```

## 9. Error Recovery and Retry Strategies

### Comprehensive Retry System

```javascript
class RetryStrategy {
    constructor(options = {}) {
        this.options = {
            maxAttempts: 3,
            baseDelay: 1000,
            maxDelay: 30000,
            backoffFactor: 2,
            jitter: true,
            ...options
        };
    }
    
    async execute(fn, context = {}) {
        let lastError;
        
        for (let attempt = 1; attempt <= this.options.maxAttempts; attempt++) {
            try {
                const result = await fn();
                
                if (attempt > 1) {
                    console.log(`Request succeeded on attempt ${attempt}`);
                }
                
                return result;
                
            } catch (error) {
                lastError = error;
                
                if (!this.shouldRetry(error, attempt)) {
                    break;
                }
                
                const delay = this.calculateDelay(attempt);
                console.warn(`Attempt ${attempt} failed, retrying in ${delay}ms:`, error.message);
                
                await this.delay(delay);
            }
        }
        
        throw new Error(`All ${this.options.maxAttempts} attempts failed. Last error: ${lastError.message}`);
    }
    
    shouldRetry(error, attempt) {
        if (attempt >= this.options.maxAttempts) {
            return false;
        }
        
        // Don't retry client errors (400-499)
        if (error.message.includes('400')) {
            return false;
        }
        
        // Retry server errors and network issues
        const retryablePatterns = [
            /timeout/i,
            /network/i,
            /500/,
            /502/,
            /503/,
            /504/,
            /ENOTFOUND/,
            /ECONNRESET/,
            /ECONNREFUSED/
        ];
        
        return retryablePatterns.some(pattern => pattern.test(error.message));
    }
    
    calculateDelay(attempt) {
        let delay = this.options.baseDelay * Math.pow(this.options.backoffFactor, attempt - 1);
        delay = Math.min(delay, this.options.maxDelay);
        
        if (this.options.jitter) {
            delay *= (0.5 + Math.random() * 0.5); // Add 0-50% jitter
        }
        
        return Math.floor(delay);
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
}
```

### Circuit Breaker Pattern

```javascript
class CircuitBreaker {
    constructor(options = {}) {
        this.options = {
            failureThreshold: 5,
            resetTimeout: 60000,
            monitoringWindow: 300000, // 5 minutes
            ...options
        };
        
        this.state = 'CLOSED'; // CLOSED, OPEN, HALF_OPEN
        this.failures = [];
        this.lastFailureTime = null;
        this.nextAttempt = null;
    }
    
    async execute(fn) {
        if (this.state === 'OPEN') {
            if (Date.now() < this.nextAttempt) {
                throw new Error('Circuit breaker is OPEN - requests blocked');
            }
            
            this.state = 'HALF_OPEN';
        }
        
        try {
            const result = await fn();
            
            if (this.state === 'HALF_OPEN') {
                this.state = 'CLOSED';
                this.failures = [];
            }
            
            return result;
            
        } catch (error) {
            this.recordFailure();
            
            if (this.state === 'HALF_OPEN') {
                this.state = 'OPEN';
                this.nextAttempt = Date.now() + this.options.resetTimeout;
            }
            
            throw error;
        }
    }
    
    recordFailure() {
        const now = Date.now();
        this.failures.push(now);
        this.lastFailureTime = now;
        
        // Remove old failures outside monitoring window
        const cutoff = now - this.options.monitoringWindow;
        this.failures = this.failures.filter(time => time > cutoff);
        
        // Check if we should open the circuit
        if (this.failures.length >= this.options.failureThreshold) {
            this.state = 'OPEN';
            this.nextAttempt = now + this.options.resetTimeout;
            console.warn(`Circuit breaker OPENED due to ${this.failures.length} failures`);
        }
    }
}
```

## 10. Production Error Monitoring and Alerting

### Comprehensive Error Tracking System

```javascript
class ProductionErrorMonitor {
    constructor(options = {}) {
        this.options = {
            alertThreshold: 10,
            alertWindow: 300000, // 5 minutes
            logErrors: true,
            sendAlerts: true,
            ...options
        };
        
        this.errors = [];
        this.metrics = {
            totalErrors: 0,
            errorsByType: {},
            errorsByEndpoint: {},
            recentErrors: []
        };
    }
    
    recordError(error, context = {}) {
        const errorRecord = {
            timestamp: new Date(),
            message: error.message,
            type: this.categorizeError(error),
            endpoint: context.endpoint,
            query: context.query,
            userAgent: navigator.userAgent,
            stack: error.stack
        };
        
        this.errors.push(errorRecord);
        this.updateMetrics(errorRecord);
        
        if (this.options.logErrors) {
            console.error('API Error recorded:', errorRecord);
        }
        
        this.checkAlertThreshold();
        
        return errorRecord;
    }
    
    categorizeError(error) {
        const message = error.message.toLowerCase();
        
        if (message.includes('timeout')) return 'TIMEOUT';
        if (message.includes('network')) return 'NETWORK';
        if (message.includes('400')) return 'CLIENT_ERROR';
        if (message.includes('404')) return 'NOT_FOUND';
        if (message.includes('500')) return 'SERVER_ERROR';
        if (message.includes('silent failure')) return 'SILENT_FAILURE';
        
        return 'OTHER';
    }
    
    updateMetrics(errorRecord) {
        this.metrics.totalErrors++;
        
        // Update error type counts
        const type = errorRecord.type;
        this.metrics.errorsByType[type] = (this.metrics.errorsByType[type] || 0) + 1;
        
        // Update endpoint error counts
        if (errorRecord.endpoint) {
            const endpoint = errorRecord.endpoint;
            this.metrics.errorsByEndpoint[endpoint] = (this.metrics.errorsByEndpoint[endpoint] || 0) + 1;
        }
        
        // Maintain recent errors list
        this.metrics.recentErrors.unshift(errorRecord);
        if (this.metrics.recentErrors.length > 100) {
            this.metrics.recentErrors = this.metrics.recentErrors.slice(0, 100);
        }
        
        // Clean old errors
        const cutoff = Date.now() - this.options.alertWindow;
        this.errors = this.errors.filter(err => err.timestamp.getTime() > cutoff);
    }
    
    checkAlertThreshold() {
        const recentErrors = this.errors.filter(
            err => Date.now() - err.timestamp.getTime() < this.options.alertWindow
        );
        
        if (recentErrors.length >= this.options.alertThreshold) {
            this.sendAlert({
                type: 'HIGH_ERROR_RATE',
                count: recentErrors.length,
                window: this.options.alertWindow / 1000,
                errors: recentErrors.slice(0, 5) // Send first 5 errors as examples
            });
        }
    }
    
    sendAlert(alertData) {
        if (!this.options.sendAlerts) return;
        
        console.error('=¨ ALERT:', alertData);
        
        // In production, integrate with alerting systems:
        // - Slack/Discord webhooks
        // - Email notifications
        // - Monitoring services (DataDog, New Relic, etc.)
        // - Custom alerting APIs
    }
    
    getHealthReport() {
        const now = Date.now();
        const last24h = this.errors.filter(err => now - err.timestamp.getTime() < 86400000);
        
        return {
            timestamp: new Date(),
            totalErrors: this.metrics.totalErrors,
            errorsLast24h: last24h.length,
            errorsByType: this.metrics.errorsByType,
            topErrorEndpoints: Object.entries(this.metrics.errorsByEndpoint)
                .sort(([,a], [,b]) => b - a)
                .slice(0, 5),
            recentErrors: this.metrics.recentErrors.slice(0, 10)
        };
    }
}
```

### Integration Example

```javascript
// Production-ready API client with comprehensive error handling
class ProductionApiClient {
    constructor(baseUrl) {
        this.baseUrl = baseUrl;
        this.errorMonitor = new ProductionErrorMonitor();
        this.circuitBreaker = new CircuitBreaker();
        this.retryStrategy = new RetryStrategy();
        this.performanceMonitor = new PerformanceMonitor();
    }
    
    async query(endpoint, params = {}) {
        const context = { endpoint, query: JSON.stringify(params) };
        
        return this.performanceMonitor.measureQuery(async () => {
            return this.circuitBreaker.execute(async () => {
                return this.retryStrategy.execute(async () => {
                    try {
                        const url = this.buildUrl(endpoint, params);
                        const response = await fetch(url);
                        
                        if (!response.ok) {
                            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                        }
                        
                        const data = await response.json();
                        
                        // Check for silent failures
                        if (this.detectSilentFailure(params, data)) {
                            const error = new Error('Silent failure detected: filter may have been ignored');
                            this.errorMonitor.recordError(error, context);
                            console.warn('Silent failure detected, but continuing with data');
                        }
                        
                        return data;
                        
                    } catch (error) {
                        this.errorMonitor.recordError(error, context);
                        throw error;
                    }
                });
            });
        }, context);
    }
    
    detectSilentFailure(params, data) {
        return params.$filter && 
               data.value && 
               data.value.length === 100;
    }
    
    buildUrl(endpoint, params) {
        const urlParams = new URLSearchParams();
        
        for (const [key, value] of Object.entries(params)) {
            urlParams.set(key, value.toString());
        }
        
        const queryString = urlParams.toString().replace(/\$/g, '%24');
        return `${this.baseUrl}/${endpoint}?${queryString}`;
    }
    
    getStatus() {
        return {
            errors: this.errorMonitor.getHealthReport(),
            performance: this.performanceMonitor.getReport(),
            circuitBreaker: {
                state: this.circuitBreaker.state,
                failures: this.circuitBreaker.failures.length
            }
        };
    }
}
```

## Summary

This comprehensive error handling guide covers all major error patterns in the Danish Parliament API. The key takeaways for production systems are:

1. **Always validate filter field names** to prevent silent failures
2. **Use proper URL encoding** (`%24` instead of `$`)
3. **Implement retry logic** for network and server errors
4. **Monitor response sizes** to detect ignored filters
5. **Use circuit breakers** to prevent cascading failures
6. **Track error metrics** for proactive monitoring
7. **Handle Danish characters** with proper UTF-8 encoding
8. **Validate expansion relationships** before queries
9. **Implement timeouts and cancellation** for long-running requests
10. **Plan for rate limiting** even though none currently exists

Remember: The API's silent filter failure behavior is its most dangerous characteristic. Always validate your queries and monitor result patterns in production environments.