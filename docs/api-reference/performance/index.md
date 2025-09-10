# Performance

The Danish Parliament API is designed for high performance and reliability, serving thousands of requests daily while maintaining consistent response times.

## Overview

The API provides excellent performance characteristics for most use cases:

- **Average Response Time**: 85ms - 2 seconds
- **Availability**: 99.9% uptime
- **Concurrent Requests**: Handles multiple simultaneous requests efficiently
- **No Rate Limiting**: Currently no enforced rate limits

## Key Performance Topics

### [Response Times](response-times.md)
Understand typical response times for different query types and what factors affect performance.

### [Query Limits](query-limits.md)
Learn about query size limits, maximum result counts, and pagination requirements.

### [Optimization](optimization.md)
Best practices for optimizing your queries to achieve maximum performance.

## Quick Performance Tips

### 1. Use Pagination
Always paginate large result sets to avoid timeouts:
```
?$top=100&$skip=0
```

### 2. Select Only Needed Fields
Use `$select` to reduce response size:
```
?$select=id,titel,statusid
```

### 3. Avoid Deep Expansions
Limit `$expand` depth to maintain performance:
```
?$expand=Sagsstatus  // Good
?$expand=Sagsstatus($expand=...)  // Avoid deep nesting
```

### 4. Cache Responses
Implement client-side caching for relatively static data like metadata and classification systems.

## Performance Benchmarks

| Query Type | Typical Response Time | Max Results |
|------------|----------------------|-------------|
| Simple entity list | 85-200ms | 1000 |
| Filtered query | 100-500ms | 1000 |
| Single expansion | 200-800ms | 500 |
| Multiple expansions | 500-2000ms | 100 |
| Complex filters | 1-3 seconds | 100 |

## Monitoring Performance

Track these metrics in your application:

1. **Response Times**: Monitor average and p95 latency
2. **Error Rates**: Track 5xx errors and timeouts
3. **Data Freshness**: Check last update timestamps
4. **Query Efficiency**: Measure records retrieved vs. needed

## Handling Performance Issues

If you experience performance problems:

1. **Simplify Queries**: Remove unnecessary expansions and filters
2. **Reduce Page Size**: Use smaller `$top` values
3. **Implement Retry Logic**: Handle transient failures gracefully
4. **Cache Aggressively**: Store frequently accessed data locally
5. **Monitor Patterns**: Identify and optimize slow queries

## Performance Guarantees

While the API generally performs well, note:

- No formal SLA is provided
- Response times may vary during peak periods
- Large queries may timeout after 30 seconds
- Historical data queries may be slower

## Best Practices Summary

✅ **DO:**
- Use pagination for all queries
- Select only required fields
- Implement client-side caching
- Handle errors gracefully
- Monitor your usage patterns

❌ **DON'T:**
- Request all fields unnecessarily
- Use deep nested expansions
- Ignore pagination
- Make excessive concurrent requests
- Rely on consistent sub-second responses

## Related Topics

- [Query Optimization](optimization.md) - Detailed optimization techniques
- [Pagination Strategies](../../production/performance/pagination-strategies.md) - Advanced pagination patterns
- [Caching](../../production/architecture/caching.md) - Caching implementation guide
- [Error Handling](../errors/index.md) - Handling performance-related errors