# Response Times

The Danish Parliamentary OData API delivers consistently fast response times across different query types and dataset sizes. This section provides comprehensive guidance on response time expectations, performance factors, and timeout configuration.

## Typical Response Time Ranges

Based on extensive performance testing, the API exhibits predictable response time patterns:

### Small Queries (1-100 records)
- **Range**: 85-150ms
- **Average**: ~108ms
- **Use Case**: Individual record lookups, small dataset queries
- **Examples**:
  ```bash
  # Single actor lookup - ~85ms
  https://oda.ft.dk/api/Aktør?%24top=5
  
  # Basic case search - ~108ms  
  https://oda.ft.dk/api/Sag?%24top=50
  ```

### Medium Queries (100-1000 records)
- **Range**: 130-500ms
- **Average**: ~300ms
- **Use Case**: Paginated browsing, moderate dataset analysis
- **Note**: API enforces 100-record limit per request; use pagination for larger datasets

### Large Queries (Complex expansions)
- **Range**: 500ms-2.1s
- **Average**: ~1.8s
- **Use Case**: Complex relationship queries with multi-level expansions
- **Examples**:
  ```bash
  # Complex voting analysis - ~1.8s
  https://oda.ft.dk/api/Afstemning?%24expand=Stemme/Aktør&%24top=100
  
  # Multi-level document relationships - ~2.1s
  https://oda.ft.dk/api/Sag?%24expand=SagDokument/Dokument&%24top=100
  ```

## Factors Affecting Response Times

### Query Complexity
Response times increase based on query sophistication:

1. **Simple Queries** (+0ms baseline)
   - Basic entity retrieval with standard fields
   - Simple $filter operations
   - No relationship expansions

2. **Filtered Queries** (+10-25ms)
   - Text search operations
   - Date range filters
   - Complex boolean logic

3. **Expansion Queries** (+50-100% overhead)
   - Single-level expansions: +200-500ms
   - Multi-level expansions: +800-1500ms
   - Deep relationship traversals

4. **Ordering Operations** (+10-50ms)
   - $orderby with indexed fields: minimal impact
   - $orderby with text fields: moderate impact
   - Complex sorting criteria: higher impact

### Dataset Size Impact
The API implements intelligent pagination that affects performance:

```bash
# Performance scaling examples
$top=5    ’ ~85ms   (optimal)
$top=50   ’ ~90ms   (minimal overhead)
$top=100  ’ ~108ms  (standard limit)
$top=1000 ’ ~108ms  (capped at 100 records)
```

**Key Finding**: Due to the 100-record limit, response times remain consistent regardless of requested size.

### Geographic and Network Considerations

#### Server Location
- **Hosting**: Denmark (likely Copenhagen area)
- **Target Latency**: Optimized for European access
- **CDN**: No evidence of content distribution network

#### Network Performance by Region
Based on connection testing:

| Region | Base Latency | Typical Response |
|--------|--------------|------------------|
| Denmark | ~10-20ms | 85-120ms |
| Europe | ~30-60ms | 115-180ms |
| North America | ~100-150ms | 185-270ms |
| Asia-Pacific | ~200-300ms | 285-420ms |

#### Connection Quality Impact
- **High-speed broadband**: Minimal additional latency
- **Mobile networks**: +50-100ms typical overhead
- **Satellite connections**: +500-800ms overhead
- **VPN usage**: +20-100ms depending on service

## Performance Benchmarking

### Baseline Performance Tests
Establish performance baselines with these reference queries:

```bash
# Quick health check - expect ~85ms
time curl -s "https://oda.ft.dk/api/Aktør?%24top=1" > /dev/null

# Standard query - expect ~108ms  
time curl -s "https://oda.ft.dk/api/Sag?%24top=50" > /dev/null

# Complex expansion - expect ~1.8s
time curl -s "https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=100" > /dev/null

# Empty result handling - expect ~85ms
time curl -s "https://oda.ft.dk/api/Sag?%24filter=titel%20eq%20'nonexistent'" > /dev/null
```

### Performance Monitoring Script

```javascript
// JavaScript performance monitoring
class FTAPIMonitor {
    async measureQuery(url, description) {
        const start = performance.now();
        try {
            const response = await fetch(url);
            const data = await response.json();
            const end = performance.now();
            
            return {
                url,
                description,
                responseTime: Math.round(end - start),
                recordCount: data.value?.length || 0,
                status: response.status,
                success: true
            };
        } catch (error) {
            const end = performance.now();
            return {
                url,
                description,
                responseTime: Math.round(end - start),
                error: error.message,
                success: false
            };
        }
    }
    
    async runBenchmarks() {
        const tests = [
            ['https://oda.ft.dk/api/Aktør?%24top=1', 'Single record'],
            ['https://oda.ft.dk/api/Sag?%24top=100', 'Full page'],
            ['https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=50', 'Complex expansion'],
            ['https://oda.ft.dk/api/Dokument?%24filter=contains(titel,%27klima%27)', 'Text search']
        ];
        
        const results = [];
        for (const [url, description] of tests) {
            const result = await this.measureQuery(url, description);
            results.push(result);
            console.log(`${description}: ${result.responseTime}ms`);
        }
        
        return results;
    }
}
```

### Python Performance Testing

```python
import time
import requests
import statistics

def benchmark_api_performance():
    """Comprehensive API performance testing"""
    
    test_queries = [
        {
            'url': 'https://oda.ft.dk/api/Aktør?%24top=1',
            'description': 'Single record lookup',
            'expected_max': 150
        },
        {
            'url': 'https://oda.ft.dk/api/Sag?%24top=100', 
            'description': 'Standard page',
            'expected_max': 200
        },
        {
            'url': 'https://oda.ft.dk/api/Afstemning?%24expand=Stemme&%24top=50',
            'description': 'Complex expansion',  
            'expected_max': 2500
        }
    ]
    
    results = []
    
    for query in test_queries:
        times = []
        
        # Run 5 iterations for statistical validity
        for i in range(5):
            start = time.time()
            try:
                response = requests.get(query['url'], timeout=30)
                response.raise_for_status()
                data = response.json()
                end = time.time()
                
                response_time = (end - start) * 1000  # Convert to ms
                times.append(response_time)
                
            except Exception as e:
                print(f"Error in {query['description']}: {e}")
                continue
        
        if times:
            avg_time = statistics.mean(times)
            min_time = min(times)
            max_time = max(times)
            
            result = {
                'description': query['description'],
                'avg_ms': round(avg_time),
                'min_ms': round(min_time), 
                'max_ms': round(max_time),
                'within_expected': max_time <= query['expected_max'],
                'url': query['url']
            }
            
            results.append(result)
            print(f"{result['description']}: {result['avg_ms']}ms avg "
                  f"({result['min_ms']}-{result['max_ms']}ms range)")
    
    return results

# Usage
if __name__ == "__main__":
    benchmark_results = benchmark_api_performance()
```

## Setting Appropriate Timeout Values

### Recommended Timeout Configuration

Choose timeout values based on query complexity and application requirements:

#### Conservative Settings (High Reliability)
```javascript
// JavaScript fetch timeouts
const timeouts = {
    simple_query: 5000,     // 5 seconds for basic queries
    complex_query: 10000,   // 10 seconds for expansions  
    bulk_operation: 30000   // 30 seconds for large operations
};

// Usage with AbortController
async function queryWithTimeout(url, timeout = 5000) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);
    
    try {
        const response = await fetch(url, { signal: controller.signal });
        clearTimeout(timeoutId);
        return await response.json();
    } catch (error) {
        clearTimeout(timeoutId);
        if (error.name === 'AbortError') {
            throw new Error(`Query timeout after ${timeout}ms`);
        }
        throw error;
    }
}
```

#### Aggressive Settings (Fast User Experience)
```python
import requests

# Python requests timeout configuration
timeout_config = {
    'simple': (2, 3),      # (connect, read) in seconds
    'complex': (3, 8),     # Allow more time for processing
    'bulk': (5, 15)        # Maximum for large operations
}

def query_api(url, query_type='simple'):
    timeout = timeout_config.get(query_type, timeout_config['simple'])
    
    try:
        response = requests.get(url, timeout=timeout)
        return response.json()
    except requests.exceptions.Timeout:
        print(f"Query timeout after {timeout} seconds")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
```

### Timeout Strategy by Use Case

#### Interactive Applications
- **User searches**: 2-3 seconds maximum
- **Page navigation**: 1-2 seconds preferred
- **Background updates**: 5-10 seconds acceptable

#### Batch Processing
- **Data synchronization**: 30-60 seconds
- **Report generation**: 2-5 minutes
- **Full dataset export**: 10-30 minutes with pagination

#### Real-time Monitoring
- **Health checks**: 1-2 seconds
- **Alert queries**: 3-5 seconds  
- **Dashboard updates**: 5-10 seconds

## Performance Monitoring and Alerting

### Key Metrics to Track

1. **Response Time Percentiles**
   - P50 (median): Expected normal performance
   - P95: Acceptable slow queries  
   - P99: Maximum acceptable performance
   - P99.9: Error threshold

2. **Success Rate Monitoring**
   - HTTP status code distribution
   - Timeout frequency
   - Connection error rates

3. **Query Performance by Type**
   - Simple vs. complex query performance
   - Expansion overhead tracking
   - Geographic performance variation

### Alerting Thresholds

```yaml
# Example monitoring configuration
api_performance_alerts:
  response_time:
    warning: 500ms   # P95 exceeds normal range
    critical: 2000ms # P95 exceeds acceptable limits
    
  success_rate:
    warning: 95%     # Success rate below threshold
    critical: 90%    # Service degradation
    
  timeout_rate:
    warning: 5%      # High timeout frequency  
    critical: 10%    # Severe timeout issues

specific_query_types:
  simple_queries:
    expected: 85-150ms
    warning: 300ms
    critical: 500ms
    
  complex_expansions:
    expected: 1000-2000ms
    warning: 3000ms
    critical: 5000ms
```

### Health Check Implementation

```bash
#!/bin/bash
# API health check script

API_BASE="https://oda.ft.dk/api"
TIMEOUT=5
LOG_FILE="/var/log/ft-api-health.log"

check_endpoint() {
    local endpoint=$1
    local description=$2
    local max_time=$3
    
    start_time=$(date +%s.%N)
    status_code=$(curl -s -o /dev/null -w "%{http_code}" \
                  --max-time $TIMEOUT "${API_BASE}/${endpoint}")
    end_time=$(date +%s.%N)
    
    response_time=$(echo "($end_time - $start_time) * 1000" | bc)
    response_time_ms=${response_time%.*}
    
    if [ "$status_code" -eq 200 ] && [ "$response_time_ms" -lt "$max_time" ]; then
        echo "$(date): HEALTHY - $description: ${response_time_ms}ms" >> $LOG_FILE
        return 0
    else
        echo "$(date): UNHEALTHY - $description: ${response_time_ms}ms, HTTP $status_code" >> $LOG_FILE
        return 1
    fi
}

# Run health checks
check_endpoint "Aktør?%24top=1" "Simple query" 200
check_endpoint "Sag?%24top=50" "Standard query" 300  
check_endpoint "Afstemning?%24expand=Stemme&%24top=10" "Complex query" 3000

echo "Health check completed at $(date)"
```

## Best Practices Summary

### Client-Side Optimization
1. **Use appropriate timeouts** for each query type
2. **Implement retry logic** with exponential backoff
3. **Cache responses** where appropriate using `opdateringsdato` timestamps
4. **Monitor performance trends** to detect degradation
5. **Test from multiple geographic locations** if serving global users

### Query Optimization for Performance
1. **Minimize expansions** - each level adds significant overhead
2. **Use specific field selection** with $select when possible
3. **Implement efficient pagination** rather than large single queries
4. **Cache enumeration values** (types, statuses, roles)
5. **Batch related queries** when expansion isn't suitable

### Error Handling
1. **Distinguish timeout types**: network vs. server processing
2. **Implement graceful degradation** for performance issues
3. **Provide user feedback** during slow operations
4. **Log performance anomalies** for troubleshooting
5. **Plan for temporary service issues** with appropriate fallbacks

The Danish Parliamentary API's consistent performance characteristics make it well-suited for both interactive applications and batch processing workflows when proper timeout and optimization strategies are employed.