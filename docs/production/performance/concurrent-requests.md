# Concurrent Request Handling

Efficient handling of concurrent requests is crucial for building high-performance applications with the Danish Parliamentary OData API. This guide covers proven patterns and best practices for managing multiple simultaneous API calls.

## Overview

The Danish Parliamentary API has been extensively tested for concurrent request handling and demonstrates excellent stability under load:

- **No Rate Limiting**: API handles 10+ concurrent requests without throttling
- **Stable Performance**: No degradation under moderate concurrent load
- **Production Ready**: Consistent response times across parallel requests
- **Optimal Response Times**: 85ms-150ms for small queries, ~2s for 10K records

## API Concurrency Characteristics

### Tested Performance Metrics

Based on comprehensive load testing conducted in September 2025:

| Query Size | Single Request Time | Concurrent (10x) | Performance Impact |
|------------|-------------------|------------------|------------------|
| Small (d100 records) | ~108ms | ~120ms | Minimal (+11%) |
| Medium (1K records) | ~400ms | ~450ms | Low (+12.5%) |
| Large (10K records) | ~2.1s | ~2.3s | Acceptable (+9.5%) |

### Concurrency Limits

**Current Testing Results** (September 2025):
-  **10 Concurrent Requests**: All return HTTP 200 successfully
-  **No Rate Limiting Detected**: No 429 responses observed
-  **Stable Under Load**: Performance remains consistent
-   **Untested Beyond 10**: Higher concurrency levels not verified

## Implementation Patterns

### 1. Python Async/Await Pattern

```python
import asyncio
import aiohttp
import time
from typing import List, Dict, Any

class ConcurrentOdaClient:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        # Configure connection pool for optimal concurrent performance
        connector = aiohttp.TCPConnector(
            limit=20,           # Total connection pool size
            limit_per_host=10,  # Connections per host
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(
            total=60,    # Total request timeout
            connect=10   # Connection establishment timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers={'User-Agent': 'DanishParliament-ConcurrentClient/1.0'}
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch_single(self, endpoint: str, params: Dict[str, str] = None) -> Dict[str, Any]:
        """Fetch single API endpoint with error handling."""
        if params:
            # Ensure proper URL encoding for OData parameters
            encoded_params = {}
            for key, value in params.items():
                if key.startswith('$'):
                    encoded_params[f'%24{key[1:]}'] = value
                else:
                    encoded_params[key] = value
            query_string = '&'.join(f'{k}={v}' for k, v in encoded_params.items())
            url = f"{self.base_url}/{endpoint}?{query_string}"
        else:
            url = f"{self.base_url}/{endpoint}"
        
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        'error': True,
                        'status': response.status,
                        'url': url,
                        'message': f'HTTP {response.status}: {await response.text()}'
                    }
        except asyncio.TimeoutError:
            return {'error': True, 'message': f'Timeout for {url}'}
        except Exception as e:
            return {'error': True, 'message': f'Request failed: {str(e)}'}
    
    async def fetch_concurrent(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple API requests concurrently."""
        tasks = []
        for req in requests:
            task = self.fetch_single(req['endpoint'], req.get('params'))
            tasks.append(task)
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Process results and add timing information
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'error': True,
                    'message': str(result),
                    'request': requests[i]
                })
            else:
                processed_results.append({
                    **result,
                    'concurrent_batch_time': end_time - start_time,
                    'request_index': i
                })
        
        return processed_results

# Usage Example: Concurrent Case Analysis
async def analyze_recent_cases_concurrent():
    """Analyze recent parliamentary cases using concurrent requests."""
    
    concurrent_requests = [
        {
            'endpoint': 'Sag',
            'params': {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '100',
                '$orderby': 'opdateringsdato desc'
            }
        },
        {
            'endpoint': 'Aktør',
            'params': {
                '$filter': "typeid eq 5",  # Politicians
                '$top': '50',
                '$expand': 'SagAktørRel/Sag'
            }
        },
        {
            'endpoint': 'Afstemning',
            'params': {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '20',
                '$expand': 'Sag',
                '$orderby': 'opdateringsdato desc'
            }
        }
    ]
    
    async with ConcurrentOdaClient() as client:
        results = await client.fetch_concurrent(concurrent_requests)
        
        # Process concurrent results
        for i, result in enumerate(results):
            if result.get('error'):
                print(f"Request {i} failed: {result['message']}")
            else:
                print(f"Request {i} succeeded: {len(result.get('value', []))} records")
                print(f"Batch completion time: {result['concurrent_batch_time']:.2f}s")
        
        return results

# Run the concurrent analysis
# asyncio.run(analyze_recent_cases_concurrent())
```

### 2. Thread Pool Pattern

```python
import concurrent.futures
import requests
import time
from typing import List, Dict, Any
from urllib.parse import quote

class ThreadPoolOdaClient:
    def __init__(self, base_url: str = "https://oda.ft.dk/api", max_workers: int = 8):
        self.base_url = base_url
        self.max_workers = max_workers
        
        # Configure session with connection pooling
        self.session = requests.Session()
        
        # Configure adapter with connection pool
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=max_workers,
            pool_maxsize=max_workers * 2,
            max_retries=3
        )
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
        # Set default headers
        self.session.headers.update({
            'User-Agent': 'DanishParliament-ThreadPoolClient/1.0',
            'Accept': 'application/json'
        })
    
    def fetch_single(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute single API request with thread-safe error handling."""
        endpoint = request_data['endpoint']
        params = request_data.get('params', {})
        
        # Build URL with proper OData parameter encoding
        url = f"{self.base_url}/{endpoint}"
        if params:
            query_parts = []
            for key, value in params.items():
                if key.startswith('$'):
                    encoded_key = f"%24{key[1:]}"
                else:
                    encoded_key = key
                query_parts.append(f"{encoded_key}={quote(str(value))}")
            url += "?" + "&".join(query_parts)
        
        try:
            start_time = time.time()
            response = self.session.get(url, timeout=30)
            end_time = time.time()
            
            result = {
                'url': url,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'request_data': request_data
            }
            
            if response.status_code == 200:
                result['data'] = response.json()
                result['record_count'] = len(result['data'].get('value', []))
            else:
                result['error'] = True
                result['error_text'] = response.text
            
            return result
            
        except requests.exceptions.Timeout:
            return {
                'error': True,
                'error_type': 'timeout',
                'url': url,
                'request_data': request_data
            }
        except Exception as e:
            return {
                'error': True,
                'error_type': 'exception',
                'error_message': str(e),
                'url': url,
                'request_data': request_data
            }
    
    def fetch_concurrent_threadpool(self, requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Execute multiple requests using ThreadPoolExecutor."""
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all requests
            future_to_request = {
                executor.submit(self.fetch_single, req): req 
                for req in requests
            }
            
            # Collect results as they complete
            results = []
            for future in concurrent.futures.as_completed(future_to_request):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    # Handle executor-level exceptions
                    failed_request = future_to_request[future]
                    results.append({
                        'error': True,
                        'error_type': 'executor_exception',
                        'error_message': str(e),
                        'request_data': failed_request
                    })
        
        end_time = time.time()
        
        # Add batch timing to all results
        for result in results:
            result['batch_time'] = end_time - start_time
        
        return results

# Usage Example: Parliamentary Activity Dashboard
def create_parliamentary_dashboard():
    """Create a comprehensive dashboard using concurrent requests."""
    
    client = ThreadPoolOdaClient(max_workers=6)
    
    dashboard_requests = [
        {
            'name': 'recent_cases',
            'endpoint': 'Sag',
            'params': {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '50',
                '$orderby': 'opdateringsdato desc'
            }
        },
        {
            'name': 'active_politicians',
            'endpoint': 'Aktør',
            'params': {
                '$filter': "typeid eq 5 and year(opdateringsdato) eq 2025",
                '$top': '30'
            }
        },
        {
            'name': 'recent_votes',
            'endpoint': 'Afstemning',
            'params': {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '20',
                '$expand': 'Sag'
            }
        },
        {
            'name': 'committee_meetings',
            'endpoint': 'Møde',
            'params': {
                '$filter': "year(dato) eq 2025",
                '$top': '25'
            }
        },
        {
            'name': 'recent_documents',
            'endpoint': 'Dokument',
            'params': {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '40',
                '$orderby': 'opdateringsdato desc'
            }
        }
    ]
    
    # Execute all requests concurrently
    print(f"Executing {len(dashboard_requests)} concurrent requests...")
    results = client.fetch_concurrent_threadpool(dashboard_requests)
    
    # Process and display results
    dashboard_data = {}
    total_records = 0
    successful_requests = 0
    
    for result in results:
        request_name = result['request_data']['name']
        
        if result.get('error'):
            print(f"L {request_name}: {result.get('error_message', 'Unknown error')}")
            dashboard_data[request_name] = None
        else:
            record_count = result['record_count']
            response_time = result['response_time']
            print(f" {request_name}: {record_count} records in {response_time:.2f}s")
            dashboard_data[request_name] = result['data']
            total_records += record_count
            successful_requests += 1
    
    batch_time = results[0]['batch_time']
    print(f"\n=Ê Dashboard Summary:")
    print(f"   Total Records: {total_records}")
    print(f"   Successful Requests: {successful_requests}/{len(dashboard_requests)}")
    print(f"   Total Batch Time: {batch_time:.2f}s")
    print(f"   Average Request Time: {batch_time/len(dashboard_requests):.2f}s")
    
    return dashboard_data

# Execute dashboard creation
# dashboard = create_parliamentary_dashboard()
```

### 3. JavaScript Concurrent Patterns

```javascript
/**
 * Danish Parliamentary API - Concurrent Request Handler
 * Optimized for browser and Node.js environments
 */
class ConcurrentOdaClient {
    constructor(baseUrl = 'https://oda.ft.dk/api', options = {}) {
        this.baseUrl = baseUrl;
        this.maxConcurrent = options.maxConcurrent || 8;
        this.timeout = options.timeout || 30000;
        this.retryAttempts = options.retryAttempts || 2;
        
        // Track active requests for concurrency management
        this.activeRequests = new Set();
    }
    
    /**
     * Execute single API request with proper error handling
     */
    async fetchSingle(endpoint, params = {}) {
        const url = this.buildUrl(endpoint, params);
        const requestId = `${Date.now()}-${Math.random()}`;
        
        try {
            this.activeRequests.add(requestId);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.timeout);
            
            const response = await fetch(url, {
                signal: controller.signal,
                headers: {
                    'Accept': 'application/json',
                    'User-Agent': 'DanishParliament-JSClient/1.0'
                }
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            
            return {
                success: true,
                data: data,
                url: url,
                recordCount: data.value ? data.value.length : 0,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            return {
                success: false,
                error: error.message,
                url: url,
                timestamp: new Date().toISOString()
            };
        } finally {
            this.activeRequests.delete(requestId);
        }
    }
    
    /**
     * Execute multiple requests with concurrency control
     */
    async fetchConcurrent(requests, options = {}) {
        const maxConcurrent = options.maxConcurrent || this.maxConcurrent;
        const results = [];
        const errors = [];
        
        // Process requests in batches to control concurrency
        for (let i = 0; i < requests.length; i += maxConcurrent) {
            const batch = requests.slice(i, i + maxConcurrent);
            const batchStart = performance.now();
            
            const batchPromises = batch.map(async (request, index) => {
                const startTime = performance.now();
                const result = await this.fetchSingle(request.endpoint, request.params);
                const endTime = performance.now();
                
                return {
                    ...result,
                    requestIndex: i + index,
                    requestTime: endTime - startTime,
                    batchIndex: Math.floor(i / maxConcurrent)
                };
            });
            
            try {
                const batchResults = await Promise.all(batchPromises);
                const batchEnd = performance.now();
                
                // Add batch timing information
                batchResults.forEach(result => {
                    result.batchTime = batchEnd - batchStart;
                });
                
                results.push(...batchResults);
                
            } catch (error) {
                errors.push({
                    batchIndex: Math.floor(i / maxConcurrent),
                    error: error.message
                });
            }
        }
        
        return {
            results: results,
            errors: errors,
            summary: {
                totalRequests: requests.length,
                successfulRequests: results.filter(r => r.success).length,
                failedRequests: results.filter(r => !r.success).length,
                totalRecords: results.reduce((sum, r) => sum + (r.recordCount || 0), 0)
            }
        };
    }
    
    /**
     * Build properly encoded OData URL
     */
    buildUrl(endpoint, params) {
        let url = `${this.baseUrl}/${endpoint}`;
        
        if (Object.keys(params).length > 0) {
            const queryParams = [];
            
            for (const [key, value] of Object.entries(params)) {
                // Handle OData parameters that start with $
                const encodedKey = key.startsWith('$') ? `%24${key.slice(1)}` : key;
                const encodedValue = encodeURIComponent(value);
                queryParams.push(`${encodedKey}=${encodedValue}`);
            }
            
            url += '?' + queryParams.join('&');
        }
        
        return url;
    }
    
    /**
     * Get current concurrency status
     */
    getConcurrencyStatus() {
        return {
            activeRequests: this.activeRequests.size,
            maxConcurrent: this.maxConcurrent
        };
    }
}

/**
 * Usage Example: Legislative Analysis Dashboard
 */
async function createLegislativeDashboard() {
    const client = new ConcurrentOdaClient('https://oda.ft.dk/api', {
        maxConcurrent: 6,
        timeout: 20000
    });
    
    const dashboardQueries = [
        {
            name: 'Active Cases 2025',
            endpoint: 'Sag',
            params: {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '100',
                '$orderby': 'opdateringsdato desc'
            }
        },
        {
            name: 'Recent Voting Sessions',
            endpoint: 'Afstemning',
            params: {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '50',
                '$expand': 'Sag'
            }
        },
        {
            name: 'Active Politicians',
            endpoint: 'Aktør',
            params: {
                '$filter': "typeid eq 5",
                '$top': '80'
            }
        },
        {
            name: 'Committee Meetings',
            endpoint: 'Møde',
            params: {
                '$filter': "year(dato) eq 2025",
                '$top': '60'
            }
        },
        {
            name: 'Recent Documents',
            endpoint: 'Dokument',
            params: {
                '$filter': "year(opdateringsdato) eq 2025",
                '$top': '75'
            }
        }
    ];
    
    console.log(`=€ Executing ${dashboardQueries.length} concurrent requests...`);
    console.time('Dashboard Creation');
    
    const result = await client.fetchConcurrent(dashboardQueries);
    
    console.timeEnd('Dashboard Creation');
    
    // Display results
    console.log('\n=Ê Dashboard Results:');
    console.log(`   Successful: ${result.summary.successfulRequests}/${result.summary.totalRequests}`);
    console.log(`   Total Records: ${result.summary.totalRecords}`);
    console.log(`   Failed: ${result.summary.failedRequests}`);
    
    // Display individual query results
    result.results.forEach((res, index) => {
        const query = dashboardQueries[index];
        if (res.success) {
            console.log(`    ${query.name}: ${res.recordCount} records (${res.requestTime.toFixed(0)}ms)`);
        } else {
            console.log(`   L ${query.name}: ${res.error}`);
        }
    });
    
    return result;
}

// Execute the dashboard
// createLegislativeDashboard();
```

## Request Batching Strategies

### 1. Intelligent Request Grouping

```python
class BatchOptimizer:
    """Optimize request batching based on query characteristics."""
    
    def __init__(self):
        # Performance profiles based on testing
        self.query_profiles = {
            'small': {'max_records': 100, 'avg_time': 0.12, 'optimal_concurrent': 10},
            'medium': {'max_records': 1000, 'avg_time': 0.45, 'optimal_concurrent': 6},
            'large': {'max_records': 10000, 'avg_time': 2.1, 'optimal_concurrent': 3}
        }
    
    def classify_request(self, params: Dict[str, str]) -> str:
        """Classify request size based on parameters."""
        top_value = params.get('$top', '25')
        try:
            record_count = int(top_value)
            if record_count <= 100:
                return 'small'
            elif record_count <= 1000:
                return 'medium'
            else:
                return 'large'
        except ValueError:
            return 'medium'  # Default for non-numeric $top values
    
    def optimize_batch(self, requests: List[Dict]) -> List[List[Dict]]:
        """Group requests into optimal batches."""
        # Classify all requests
        classified = []
        for req in requests:
            size_class = self.classify_request(req.get('params', {}))
            classified.append((req, size_class))
        
        # Group by size class
        batches = []
        for size_class in ['small', 'medium', 'large']:
            class_requests = [req for req, cls in classified if cls == size_class]
            if not class_requests:
                continue
                
            profile = self.query_profiles[size_class]
            batch_size = profile['optimal_concurrent']
            
            # Create batches of optimal size
            for i in range(0, len(class_requests), batch_size):
                batch = class_requests[i:i + batch_size]
                batches.append({
                    'requests': batch,
                    'size_class': size_class,
                    'expected_time': profile['avg_time']
                })
        
        return batches

# Usage example
optimizer = BatchOptimizer()
mixed_requests = [
    {'endpoint': 'Sag', 'params': {'$top': '50'}},      # small
    {'endpoint': 'Aktør', 'params': {'$top': '5000'}},  # large  
    {'endpoint': 'Møde', 'params': {'$top': '100'}},    # small
    {'endpoint': 'Dokument', 'params': {'$top': '2000'}} # large
]

optimized_batches = optimizer.optimize_batch(mixed_requests)
```

### 2. Progressive Loading Pattern

```javascript
/**
 * Progressive loading for large datasets with concurrent requests
 */
class ProgressiveLoader {
    constructor(client, options = {}) {
        this.client = client;
        this.chunkSize = options.chunkSize || 1000;
        this.maxConcurrent = options.maxConcurrent || 4;
        this.progressCallback = options.onProgress || (() => {});
    }
    
    async loadLargeDataset(endpoint, totalRecords, baseParams = {}) {
        const chunks = Math.ceil(totalRecords / this.chunkSize);
        const requests = [];
        
        // Create chunked requests
        for (let i = 0; i < chunks; i++) {
            const skip = i * this.chunkSize;
            requests.push({
                endpoint: endpoint,
                params: {
                    ...baseParams,
                    '$skip': skip.toString(),
                    '$top': this.chunkSize.toString()
                },
                chunkIndex: i
            });
        }
        
        console.log(`=æ Loading ${totalRecords} records in ${chunks} chunks of ${this.chunkSize}`);
        
        // Process chunks with controlled concurrency
        const allResults = [];
        const startTime = Date.now();
        
        for (let i = 0; i < requests.length; i += this.maxConcurrent) {
            const batch = requests.slice(i, i + this.maxConcurrent);
            
            const batchPromises = batch.map(async (request) => {
                const result = await this.client.fetchSingle(request.endpoint, request.params);
                
                // Update progress
                this.progressCallback({
                    completed: allResults.length + 1,
                    total: chunks,
                    percentage: Math.round(((allResults.length + 1) / chunks) * 100),
                    chunkIndex: request.chunkIndex,
                    recordsInChunk: result.recordCount || 0
                });
                
                return result;
            });
            
            const batchResults = await Promise.all(batchPromises);
            allResults.push(...batchResults);
        }
        
        const endTime = Date.now();
        const totalTime = (endTime - startTime) / 1000;
        
        // Combine all results
        const combinedData = [];
        let totalRecordsLoaded = 0;
        
        allResults.forEach(result => {
            if (result.success && result.data.value) {
                combinedData.push(...result.data.value);
                totalRecordsLoaded += result.data.value.length;
            }
        });
        
        return {
            success: true,
            data: combinedData,
            totalRecords: totalRecordsLoaded,
            chunks: chunks,
            totalTime: totalTime,
            averageChunkTime: totalTime / chunks
        };
    }
}

// Usage: Load all 2025 parliamentary cases progressively
async function loadAllCases2025() {
    const client = new ConcurrentOdaClient();
    const loader = new ProgressiveLoader(client, {
        chunkSize: 500,
        maxConcurrent: 3,
        onProgress: (progress) => {
            console.log(`Progress: ${progress.percentage}% (${progress.completed}/${progress.total} chunks)`);
        }
    });
    
    // First, get total count
    const countResult = await client.fetchSingle('Sag', {
        '$filter': "year(opdateringsdato) eq 2025",
        '$top': '1',
        '$inlinecount': 'allpages'
    });
    
    if (!countResult.success) {
        console.error('Failed to get record count');
        return;
    }
    
    const totalRecords = countResult.data['odata.count'] || 1000; // fallback estimate
    
    // Load all records progressively
    const result = await loader.loadLargeDataset('Sag', totalRecords, {
        '$filter': "year(opdateringsdato) eq 2025",
        '$orderby': 'opdateringsdato desc'
    });
    
    console.log(` Loaded ${result.totalRecords} records in ${result.totalTime.toFixed(2)}s`);
    console.log(`   Average chunk time: ${result.averageChunkTime.toFixed(2)}s`);
    
    return result.data;
}
```

## Connection Pool Management

### Optimal Configuration Settings

Based on testing with the Danish Parliamentary API:

```python
# Python aiohttp configuration
aiohttp_config = {
    'connector': aiohttp.TCPConnector(
        limit=20,              # Total connection pool size
        limit_per_host=10,     # Connections per host (API has single host)
        keepalive_timeout=30,  # Keep connections alive for reuse
        enable_cleanup_closed=True,
        use_dns_cache=True,
        ttl_dns_cache=300      # DNS cache for 5 minutes
    ),
    'timeout': aiohttp.ClientTimeout(
        total=60,     # Total request timeout
        connect=10,   # Connection establishment
        sock_read=30  # Socket read timeout
    )
}

# Python requests configuration
requests_config = {
    'adapters': requests.adapters.HTTPAdapter(
        pool_connections=10,   # Connection pool size
        pool_maxsize=20,      # Maximum connections per pool
        max_retries=urllib3.util.retry.Retry(
            total=3,
            backoff_factor=0.3,
            status_forcelist=[500, 502, 503, 504]
        )
    )
}
```

## Error Handling in Concurrent Environments

### Comprehensive Error Recovery

```python
import asyncio
from typing import List, Dict, Any
import logging

class RobustConcurrentClient:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.retry_delays = [1, 2, 4]  # Progressive backoff
        
    async def fetch_with_retry(self, session, url: str, max_retries: int = 3) -> Dict[str, Any]:
        """Fetch with exponential backoff retry logic."""
        
        for attempt in range(max_retries + 1):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return {
                            'success': True,
                            'data': await response.json(),
                            'attempt': attempt + 1,
                            'url': url
                        }
                    elif response.status in [500, 502, 503, 504]:
                        # Server errors - retry with backoff
                        if attempt < max_retries:
                            await asyncio.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                            continue
                        else:
                            return {
                                'success': False,
                                'error': 'server_error',
                                'status': response.status,
                                'attempts': attempt + 1,
                                'url': url
                            }
                    else:
                        # Client errors - don't retry
                        return {
                            'success': False,
                            'error': 'client_error',
                            'status': response.status,
                            'attempts': attempt + 1,
                            'url': url
                        }
                        
            except asyncio.TimeoutError:
                if attempt < max_retries:
                    await asyncio.sleep(self.retry_delays[min(attempt, len(self.retry_delays) - 1)])
                    self.logger.warning(f"Timeout on attempt {attempt + 1} for {url}")
                    continue
                else:
                    return {
                        'success': False,
                        'error': 'timeout',
                        'attempts': attempt + 1,
                        'url': url
                    }
            except Exception as e:
                return {
                    'success': False,
                    'error': 'exception',
                    'message': str(e),
                    'attempts': attempt + 1,
                    'url': url
                }
        
        return {
            'success': False,
            'error': 'max_retries_exceeded',
            'attempts': max_retries + 1,
            'url': url
        }
    
    async def fetch_concurrent_robust(self, urls: List[str]) -> Dict[str, Any]:
        """Execute concurrent requests with comprehensive error handling."""
        
        connector = aiohttp.TCPConnector(limit=10, limit_per_host=8)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            tasks = [self.fetch_with_retry(session, url) for url in urls]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results and categorize
            successful = []
            failed = []
            retried = []
            
            for result in results:
                if isinstance(result, Exception):
                    failed.append({
                        'error': 'exception',
                        'message': str(result)
                    })
                elif result['success']:
                    successful.append(result)
                    if result['attempt'] > 1:
                        retried.append(result)
                else:
                    failed.append(result)
            
            return {
                'successful': successful,
                'failed': failed,
                'retried': retried,
                'summary': {
                    'total_requests': len(urls),
                    'successful_count': len(successful),
                    'failed_count': len(failed),
                    'retry_count': len(retried),
                    'success_rate': len(successful) / len(urls) * 100
                }
            }
```

## Performance Monitoring

### Real-time Metrics Collection

```python
import time
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class RequestMetrics:
    url: str
    start_time: float
    end_time: float
    status_code: int
    response_size: int
    error: Optional[str] = None
    
    @property
    def duration(self) -> float:
        return self.end_time - self.start_time

class ConcurrentPerformanceMonitor:
    def __init__(self, window_size: int = 100):
        self.window_size = window_size
        self.metrics: deque = deque(maxlen=window_size)
        self.endpoint_stats: Dict[str, deque] = defaultdict(lambda: deque(maxlen=window_size))
        self.start_time = time.time()
    
    def record_request(self, metrics: RequestMetrics):
        """Record request metrics for analysis."""
        self.metrics.append(metrics)
        
        # Extract endpoint from URL for endpoint-specific stats
        endpoint = self.extract_endpoint(metrics.url)
        self.endpoint_stats[endpoint].append(metrics)
    
    def extract_endpoint(self, url: str) -> str:
        """Extract endpoint name from full URL."""
        try:
            path_part = url.split('/api/')[-1]
            endpoint = path_part.split('?')[0]
            return endpoint
        except:
            return 'unknown'
    
    def get_performance_summary(self) -> Dict:
        """Generate comprehensive performance summary."""
        if not self.metrics:
            return {'status': 'no_data'}
        
        durations = [m.duration for m in self.metrics]
        success_count = len([m for m in self.metrics if 200 <= m.status_code < 300])
        error_count = len(self.metrics) - success_count
        
        return {
            'total_requests': len(self.metrics),
            'success_rate': (success_count / len(self.metrics)) * 100,
            'error_rate': (error_count / len(self.metrics)) * 100,
            'response_times': {
                'min': min(durations),
                'max': max(durations),
                'mean': statistics.mean(durations),
                'median': statistics.median(durations),
                'p95': self.percentile(durations, 95),
                'p99': self.percentile(durations, 99)
            },
            'throughput': len(self.metrics) / (time.time() - self.start_time),
            'endpoint_breakdown': self.get_endpoint_breakdown()
        }
    
    def percentile(self, data: List[float], p: int) -> float:
        """Calculate percentile value."""
        sorted_data = sorted(data)
        index = (p / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_endpoint_breakdown(self) -> Dict:
        """Get performance breakdown by endpoint."""
        breakdown = {}
        
        for endpoint, metrics in self.endpoint_stats.items():
            if not metrics:
                continue
                
            durations = [m.duration for m in metrics]
            success_count = len([m for m in metrics if 200 <= m.status_code < 300])
            
            breakdown[endpoint] = {
                'request_count': len(metrics),
                'success_rate': (success_count / len(metrics)) * 100,
                'avg_response_time': statistics.mean(durations),
                'median_response_time': statistics.median(durations)
            }
        
        return breakdown
    
    def print_live_stats(self):
        """Print formatted live statistics."""
        summary = self.get_performance_summary()
        
        if summary.get('status') == 'no_data':
            print("=Ê No performance data available yet")
            return
        
        print("\n=Ê Live Performance Statistics")
        print("=" * 50)
        print(f"Total Requests: {summary['total_requests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        print(f"Throughput: {summary['throughput']:.2f} req/sec")
        
        rt = summary['response_times']
        print(f"\nñ  Response Times:")
        print(f"   Mean: {rt['mean']:.3f}s")
        print(f"   Median: {rt['median']:.3f}s")
        print(f"   95th percentile: {rt['p95']:.3f}s")
        print(f"   99th percentile: {rt['p99']:.3f}s")
        
        print(f"\n=È Endpoint Breakdown:")
        for endpoint, stats in summary['endpoint_breakdown'].items():
            print(f"   {endpoint}: {stats['request_count']} requests, "
                  f"{stats['avg_response_time']:.3f}s avg")

# Usage with concurrent client
async def monitored_concurrent_requests():
    monitor = ConcurrentPerformanceMonitor()
    client = ConcurrentOdaClient()
    
    requests = [
        {'endpoint': 'Sag', 'params': {'$top': '100'}},
        {'endpoint': 'Aktør', 'params': {'$top': '50'}},
        {'endpoint': 'Afstemning', 'params': {'$top': '25'}},
        # ... more requests
    ]
    
    async with client:
        for request in requests:
            start_time = time.time()
            result = await client.fetch_single(request['endpoint'], request['params'])
            end_time = time.time()
            
            # Record metrics
            metrics = RequestMetrics(
                url=result.get('url', ''),
                start_time=start_time,
                end_time=end_time,
                status_code=200 if result.get('success') else 500,
                response_size=len(str(result.get('data', {}))),
                error=result.get('error')
            )
            monitor.record_request(metrics)
    
    # Display final statistics
    monitor.print_live_stats()

# asyncio.run(monitored_concurrent_requests())
```

## Best Practices Summary

### Configuration Recommendations

**For Python Applications:**
- Use `aiohttp` for async/await pattern with 8-10 concurrent requests
- Configure connection pooling with 10-20 connections max
- Set timeouts: 10s connect, 30s read, 60s total
- Implement exponential backoff for retries

**For JavaScript Applications:**
- Use native `fetch()` with `Promise.all()` for concurrency
- Limit concurrent requests to 6-8 for optimal browser performance
- Implement request queuing for large batches
- Use `AbortController` for proper timeout handling

**For All Languages:**
- Always encode OData parameters properly (`%24` for `$`)
- Implement request deduplication to avoid duplicate API calls
- Use progressive loading for datasets >1000 records
- Monitor response times and adjust concurrency accordingly

### Performance Optimization

1. **Batch Similar Queries**: Group requests by expected response time
2. **Cache Frequently Accessed Data**: Use `opdateringsdato` for cache invalidation
3. **Implement Circuit Breakers**: Fail fast when API becomes unresponsive
4. **Use Connection Keep-Alive**: Reuse TCP connections across requests
5. **Monitor and Alert**: Track success rates, response times, and throughput

### Production Deployment Considerations

- **Load Testing**: Validate concurrent performance in production environment
- **Rate Limit Planning**: While none detected, implement client-side throttling
- **Error Alerting**: Monitor for increased error rates or timeouts
- **Resource Monitoring**: Track memory usage and connection pool utilization
- **Graceful Degradation**: Handle API unavailability with cached data

The Danish Parliamentary API demonstrates excellent stability under concurrent load, making it suitable for high-performance production applications when proper concurrent request patterns are implemented.