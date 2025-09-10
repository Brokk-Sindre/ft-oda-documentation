# Caching Strategies

This guide covers comprehensive caching strategies for building high-performance applications with the Danish Parliamentary OData API. Despite the API's anti-caching headers, intelligent caching is essential for production applications due to the API's response characteristics and data update patterns.

## Understanding API Caching Limitations

### Server-Side Cache Headers

The Danish Parliamentary API implements aggressive anti-caching policies:

```http
Cache-Control: no-cache
Pragma: no-cache  
Expires: -1
```

**Critical Limitations:**

- L **No ETag Support**: No entity tags for conditional requests
- L **No Last-Modified Headers**: Missing modification timestamps  
- L **No Conditional Requests**: `If-None-Match`/`If-Modified-Since` ignored
- L **No Compression**: `Accept-Encoding` headers ignored, no gzip support
- L **No HTTP Caching**: Server forces fresh requests for all queries

### Performance Characteristics

Understanding response times is crucial for caching strategy:

| Query Size | Response Time | Use Case |
|------------|---------------|-----------|
| Small (d100 records) | 85-150ms | Real-time queries |
| Medium (1000 records) | 300-500ms | Dashboard data |
| Large (10,000 records) | 2-3 seconds | Bulk analysis |

**Key Insight**: Even "fast" queries benefit from caching when building interactive applications.

## Client-Side Caching Strategies

### Browser Cache Implementation

Despite no-cache headers, implement client-side caching using JavaScript:

```javascript
class ParliamentaryDataCache {
    constructor(ttlMinutes = 15) {
        this.cache = new Map();
        this.ttl = ttlMinutes * 60 * 1000; // Convert to milliseconds
    }
    
    async get(url, forceRefresh = false) {
        const cacheKey = url;
        const cached = this.cache.get(cacheKey);
        
        // Check if cached data is still valid
        if (!forceRefresh && cached && 
            (Date.now() - cached.timestamp) < this.ttl) {
            console.log('Cache hit:', cacheKey);
            return cached.data;
        }
        
        // Fetch fresh data
        console.log('Cache miss, fetching:', cacheKey);
        const response = await fetch(url);
        const data = await response.json();
        
        // Cache the response
        this.cache.set(cacheKey, {
            data: data,
            timestamp: Date.now()
        });
        
        return data;
    }
    
    invalidate(pattern) {
        // Remove entries matching pattern
        for (const [key] of this.cache) {
            if (key.includes(pattern)) {
                this.cache.delete(key);
                console.log('Cache invalidated:', key);
            }
        }
    }
    
    clear() {
        this.cache.clear();
        console.log('Cache cleared completely');
    }
}

// Usage example
const apiCache = new ParliamentaryDataCache(30); // 30-minute TTL

async function getCases(filter, useCache = true) {
    const url = `https://oda.ft.dk/api/Sag?$filter=${encodeURIComponent(filter)}`;
    return await apiCache.get(url, !useCache);
}
```

### Python Client Caching

Implement server-side caching in Python applications:

```python
import requests
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class ParliamentaryApiCache:
    def __init__(self, ttl_minutes: int = 15):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_seconds = ttl_minutes * 60
        
    def _is_expired(self, timestamp: float) -> bool:
        return time.time() - timestamp > self.ttl_seconds
    
    def get(self, url: str, force_refresh: bool = False) -> Dict[str, Any]:
        """Get data with caching"""
        if not force_refresh and url in self.cache:
            cached_item = self.cache[url]
            if not self._is_expired(cached_item['timestamp']):
                print(f"Cache hit: {url}")
                return cached_item['data']
        
        # Fetch fresh data
        print(f"Cache miss, fetching: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Cache the response
        self.cache[url] = {
            'data': data,
            'timestamp': time.time()
        }
        
        return data
    
    def invalidate_pattern(self, pattern: str):
        """Remove cached entries containing pattern"""
        keys_to_remove = [k for k in self.cache.keys() if pattern in k]
        for key in keys_to_remove:
            del self.cache[key]
            print(f"Cache invalidated: {key}")
    
    def clear(self):
        """Clear all cached data"""
        self.cache.clear()
        print("Cache cleared completely")

# Usage with parliamentary data patterns
cache = ParliamentaryApiCache(ttl_minutes=20)

def get_recent_cases(year: int = 2025) -> Dict[str, Any]:
    """Get recent cases with caching"""
    filter_expr = f"year(opdateringsdato) eq {year}"
    url = f"https://oda.ft.dk/api/Sag?$filter={filter_expr}&$top=100"
    return cache.get(url)

def get_politician_votes(politician_name: str) -> Dict[str, Any]:
    """Get politician voting records with caching"""
    filter_expr = f"substringof('{politician_name}', navn)"
    url = f"https://oda.ft.dk/api/Aktør?$filter={filter_expr}&$expand=Stemme"
    return cache.get(url)
```

## Application-Level Caching Patterns

### Smart Cache Keys

Design intelligent cache keys for parliamentary data:

```python
def generate_cache_key(entity: str, filters: Dict[str, Any], 
                      expansions: List[str] = None) -> str:
    """Generate consistent cache keys for parliamentary queries"""
    key_parts = [entity]
    
    # Sort filters for consistent keys
    if filters:
        filter_parts = []
        for k, v in sorted(filters.items()):
            if isinstance(v, str):
                filter_parts.append(f"{k}={v}")
            else:
                filter_parts.append(f"{k}={json.dumps(v, sort_keys=True)}")
        key_parts.append("filters=" + "&".join(filter_parts))
    
    # Add expansions
    if expansions:
        key_parts.append("expand=" + ",".join(sorted(expansions)))
    
    return "|".join(key_parts)

# Examples
cases_key = generate_cache_key("Sag", {"year": 2025}, ["Afstemning"])
# Result: "Sag|filters=year=2025|expand=Afstemning"

politician_key = generate_cache_key("Aktør", {"navn": "Frank Aaen"})  
# Result: "Aktør|filters=navn=Frank Aaen"
```

### Time-Based Cache Invalidation

Use `opdateringsdato` timestamps for intelligent cache invalidation:

```javascript
class SmartParliamentaryCache {
    constructor() {
        this.cache = new Map();
        this.lastUpdateCheck = new Map(); // Track when we last checked for updates
        this.checkInterval = 15 * 60 * 1000; // Check for updates every 15 minutes
    }
    
    async getWithUpdateCheck(baseUrl, cacheKey) {
        const now = Date.now();
        const lastCheck = this.lastUpdateCheck.get(cacheKey) || 0;
        
        // If we haven't checked recently, verify data is still current
        if ((now - lastCheck) > this.checkInterval) {
            await this.checkForUpdates(baseUrl, cacheKey);
            this.lastUpdateCheck.set(cacheKey, now);
        }
        
        return this.cache.get(cacheKey)?.data;
    }
    
    async checkForUpdates(baseUrl, cacheKey) {
        const cached = this.cache.get(cacheKey);
        if (!cached) return;
        
        // Query for any records newer than our cached data
        const latestUpdateUrl = `${baseUrl}?$orderby=opdateringsdato desc&$top=1&$select=opdateringsdato`;
        
        try {
            const response = await fetch(latestUpdateUrl);
            const data = await response.json();
            
            if (data.value && data.value.length > 0) {
                const latestUpdate = new Date(data.value[0].opdateringsdato);
                const cachedUpdate = new Date(cached.lastUpdate);
                
                if (latestUpdate > cachedUpdate) {
                    console.log(`Data updated since cache, invalidating: ${cacheKey}`);
                    this.cache.delete(cacheKey);
                }
            }
        } catch (error) {
            console.warn('Update check failed:', error.message);
        }
    }
}
```

## Database Caching Solutions

### Redis Implementation

For high-performance applications, implement Redis caching:

```python
import redis
import json
import time
from typing import Optional, Dict, Any

class RedisParliamentaryCache:
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 default_ttl: int = 900):  # 15 minutes default
        self.redis_client = redis.Redis(host=redis_host, port=redis_port, 
                                       decode_responses=True)
        self.default_ttl = default_ttl
        self.key_prefix = "ft_api:"
    
    def _make_key(self, key: str) -> str:
        """Create prefixed Redis key"""
        return f"{self.key_prefix}{key}"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data"""
        redis_key = self._make_key(key)
        cached_data = self.redis_client.get(redis_key)
        
        if cached_data:
            try:
                return json.loads(cached_data)
            except json.JSONDecodeError:
                # Invalid JSON, remove the key
                self.redis_client.delete(redis_key)
                return None
        return None
    
    def set(self, key: str, data: Dict[str, Any], ttl: Optional[int] = None) -> None:
        """Cache data with TTL"""
        redis_key = self._make_key(key)
        ttl = ttl or self.default_ttl
        
        # Add metadata
        cache_item = {
            'data': data,
            'cached_at': time.time(),
            'ttl': ttl
        }
        
        self.redis_client.setex(redis_key, ttl, json.dumps(cache_item))
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern"""
        search_pattern = f"{self.key_prefix}*{pattern}*"
        keys = self.redis_client.keys(search_pattern)
        
        if keys:
            return self.redis_client.delete(*keys)
        return 0
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get caching statistics"""
        all_keys = self.redis_client.keys(f"{self.key_prefix}*")
        
        return {
            'total_keys': len(all_keys),
            'memory_usage': self.redis_client.memory_usage(),
            'redis_info': self.redis_client.info('memory')
        }

# Usage example
cache = RedisParliamentaryCache()

def get_parliamentary_data(entity: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """Get parliamentary data with Redis caching"""
    cache_key = generate_cache_key(entity, filters)
    
    # Try cache first
    cached_data = cache.get(cache_key)
    if cached_data:
        print(f"Redis cache hit: {cache_key}")
        return cached_data['data']
    
    # Fetch from API
    url = build_api_url(entity, filters)
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    
    # Cache for future use (longer TTL for static data)
    ttl = 3600 if 'opdateringsdato' in str(filters) else 900  # 1 hour vs 15 minutes
    cache.set(cache_key, data, ttl)
    
    print(f"Data fetched and cached: {cache_key}")
    return data
```

### SQLite Local Cache

For desktop applications, use SQLite for persistent caching:

```python
import sqlite3
import json
import time
from typing import Optional, Dict, Any
from pathlib import Path

class SqliteParliamentaryCache:
    def __init__(self, db_path: str = "parliamentary_cache.db"):
        self.db_path = Path(db_path)
        self._init_db()
    
    def _init_db(self):
        """Initialize cache database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS cache_entries (
                key TEXT PRIMARY KEY,
                data TEXT NOT NULL,
                cached_at REAL NOT NULL,
                ttl INTEGER NOT NULL,
                last_accessed REAL NOT NULL
            )
        """)
        
        # Create index for cleanup operations
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_cached_at ON cache_entries(cached_at)
        """)
        
        conn.commit()
        conn.close()
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Get cached data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT data, cached_at, ttl FROM cache_entries 
            WHERE key = ? AND (cached_at + ttl) > ?
        """, (key, time.time()))
        
        result = cursor.fetchone()
        
        if result:
            # Update last accessed time
            cursor.execute("""
                UPDATE cache_entries SET last_accessed = ? WHERE key = ?
            """, (time.time(), key))
            conn.commit()
            
            try:
                data = json.loads(result[0])
                conn.close()
                return data
            except json.JSONDecodeError:
                # Invalid JSON, remove the entry
                cursor.execute("DELETE FROM cache_entries WHERE key = ?", (key,))
                conn.commit()
        
        conn.close()
        return None
    
    def set(self, key: str, data: Dict[str, Any], ttl: int = 900):
        """Cache data with TTL"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO cache_entries 
            (key, data, cached_at, ttl, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        """, (key, json.dumps(data), time.time(), ttl, time.time()))
        
        conn.commit()
        conn.close()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM cache_entries WHERE (cached_at + ttl) < ?
        """, (time.time(),))
        
        deleted = cursor.rowcount
        conn.commit()
        conn.close()
        
        return deleted
```

## Cache Invalidation Strategies

### Real-Time Change Detection

Implement intelligent cache invalidation using `opdateringsdato` timestamps:

```python
class ChangeDetectionCache:
    def __init__(self):
        self.cache = {}
        self.entity_last_update = {}  # Track last known update per entity type
        
    async def get_with_change_detection(self, entity_type: str, 
                                      cache_key: str, 
                                      fetch_func) -> Dict[str, Any]:
        """Get data with automatic cache invalidation on changes"""
        
        # Check if entity type has been updated since last check
        if await self._entity_has_updates(entity_type):
            print(f"Updates detected for {entity_type}, invalidating related cache")
            self._invalidate_entity_cache(entity_type)
        
        # Return cached data if available
        if cache_key in self.cache:
            return self.cache[cache_key]['data']
        
        # Fetch and cache new data
        data = await fetch_func()
        self.cache[cache_key] = {
            'data': data,
            'entity_type': entity_type,
            'cached_at': time.time()
        }
        
        return data
    
    async def _entity_has_updates(self, entity_type: str) -> bool:
        """Check if entity has been updated since last check"""
        url = f"https://oda.ft.dk/api/{entity_type}?$orderby=opdateringsdato desc&$top=1&$select=opdateringsdato"
        
        try:
            response = await fetch(url)
            data = await response.json()
            
            if data.value and data.value.length > 0:
                latest_update = data.value[0].opdateringsdato
                last_known = self.entity_last_update.get(entity_type)
                
                # Update our tracking
                self.entity_last_update[entity_type] = latest_update
                
                # Return true if we found a newer update
                return last_known and latest_update > last_known
        except Exception as e:
            console.warn(f"Change detection failed for {entity_type}: {e}")
            return False
        
        return False
    
    def _invalidate_entity_cache(self, entity_type: str):
        """Remove all cached entries for an entity type"""
        keys_to_remove = [
            key for key, value in self.cache.items() 
            if value['entity_type'] == entity_type
        ]
        
        for key in keys_to_remove:
            del self.cache[key]
```

## Performance Optimization Through Caching

### Multi-Tier Caching Architecture

Implement layered caching for optimal performance:

```python
class MultiTierParliamentaryCache:
    def __init__(self):
        # Tier 1: In-memory cache (fastest)
        self.memory_cache = {}
        self.memory_max_size = 100
        
        # Tier 2: Redis cache (fast, persistent across requests)  
        self.redis_cache = RedisParliamentaryCache()
        
        # Tier 3: SQLite cache (persistent across restarts)
        self.sqlite_cache = SqliteParliamentaryCache()
        
        # Tier 4: API (slowest, always fresh)
        self.api_base = "https://oda.ft.dk/api"
    
    async def get(self, cache_key: str, api_url: str, 
                 ttl_memory: int = 300,    # 5 minutes in memory
                 ttl_redis: int = 900,     # 15 minutes in Redis  
                 ttl_sqlite: int = 3600) -> Dict[str, Any]:   # 1 hour in SQLite
        """Get data through multi-tier cache"""
        
        # Tier 1: Memory cache
        if cache_key in self.memory_cache:
            entry = self.memory_cache[cache_key]
            if time.time() - entry['timestamp'] < ttl_memory:
                print(f"Memory cache hit: {cache_key}")
                return entry['data']
            else:
                del self.memory_cache[cache_key]
        
        # Tier 2: Redis cache
        redis_data = self.redis_cache.get(cache_key)
        if redis_data:
            print(f"Redis cache hit: {cache_key}")
            # Store in memory for next time
            self._store_memory(cache_key, redis_data['data'])
            return redis_data['data']
        
        # Tier 3: SQLite cache  
        sqlite_data = self.sqlite_cache.get(cache_key)
        if sqlite_data:
            print(f"SQLite cache hit: {cache_key}")
            # Store in upper tiers
            self._store_memory(cache_key, sqlite_data)
            self.redis_cache.set(cache_key, sqlite_data, ttl_redis)
            return sqlite_data
        
        # Tier 4: API fetch
        print(f"All cache miss, fetching from API: {cache_key}")
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Store in all tiers
        self._store_memory(cache_key, data)
        self.redis_cache.set(cache_key, data, ttl_redis)
        self.sqlite_cache.set(cache_key, data, ttl_sqlite)
        
        return data
    
    def _store_memory(self, key: str, data: Dict[str, Any]):
        """Store data in memory cache with LRU eviction"""
        if len(self.memory_cache) >= self.memory_max_size:
            # Remove oldest entry
            oldest_key = min(self.memory_cache.keys(), 
                           key=lambda k: self.memory_cache[k]['timestamp'])
            del self.memory_cache[oldest_key]
        
        self.memory_cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
```

## Cache Warming and Preloading

### Intelligent Preloading

Preload commonly accessed parliamentary data:

```javascript
class ParliamentaryCacheWarmer {
    constructor(cache) {
        this.cache = cache;
        this.warmupSchedule = new Map();
    }
    
    async warmupCommonQueries() {
        """Preload frequently accessed parliamentary data"""
        
        const warmupQueries = [
            // Current year legislation
            {
                url: 'https://oda.ft.dk/api/Sag?$filter=year(opdateringsdato) eq 2025&$top=100',
                key: 'current_year_cases',
                priority: 'high'
            },
            
            // Recent voting sessions  
            {
                url: 'https://oda.ft.dk/api/Afstemning?$orderby=opdateringsdato desc&$top=50',
                key: 'recent_votes',
                priority: 'high'
            },
            
            // Active politicians
            {
                url: 'https://oda.ft.dk/api/Aktør?$filter=slutdato eq null&$top=200',
                key: 'active_politicians',
                priority: 'medium'
            },
            
            // Committee information
            {
                url: 'https://oda.ft.dk/api/Aktør?$filter=typeid eq 4',
                key: 'committees',
                priority: 'low'  
            }
        ];
        
        // Execute warmup queries by priority
        for (const priority of ['high', 'medium', 'low']) {
            const priorityQueries = warmupQueries.filter(q => q.priority === priority);
            
            await Promise.all(
                priorityQueries.map(async (query) => {
                    try {
                        console.log(`Warming up cache: ${query.key}`);
                        await this.cache.get(query.url);
                    } catch (error) {
                        console.warn(`Cache warmup failed for ${query.key}:`, error.message);
                    }
                })
            );
            
            // Brief pause between priority levels
            if (priority !== 'low') {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
        
        console.log('Cache warmup completed');
    }
    
    scheduleRegularWarmup(intervalMinutes = 60) {
        """Schedule regular cache warming"""
        setInterval(() => {
            this.warmupCommonQueries();
        }, intervalMinutes * 60 * 1000);
    }
    
    async smartWarmup(userActivity) {
        """Warm cache based on user activity patterns"""
        const predictions = this.predictUserNeeds(userActivity);
        
        for (const prediction of predictions) {
            if (prediction.confidence > 0.7) { // High confidence predictions only
                try {
                    await this.cache.get(prediction.url);
                    console.log(`Predictive cache load: ${prediction.description}`);
                } catch (error) {
                    console.warn(`Predictive cache failed: ${error.message}`);
                }
            }
        }
    }
    
    predictUserNeeds(activity) {
        """Predict likely next queries based on user behavior"""
        const predictions = [];
        
        // If user viewed a politician, they might want their voting record
        if (activity.lastViewed?.type === 'politician') {
            predictions.push({
                url: `https://oda.ft.dk/api/Stemme?$filter=aktørid eq ${activity.lastViewed.id}&$expand=Afstemning`,
                confidence: 0.8,
                description: `Voting records for ${activity.lastViewed.name}`
            });
        }
        
        // If user viewed a case, they might want related documents
        if (activity.lastViewed?.type === 'case') {
            predictions.push({
                url: `https://oda.ft.dk/api/Dokument?$filter=sagid eq ${activity.lastViewed.id}`,
                confidence: 0.75,
                description: `Documents for case ${activity.lastViewed.title}`
            });
        }
        
        return predictions;
    }
}
```

## Monitoring and Metrics

### Cache Performance Tracking

Implement comprehensive cache monitoring:

```python
import time
from typing import Dict, Any
from dataclasses import dataclass, field
from collections import defaultdict

@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    total_requests: int = 0
    total_response_time: float = 0.0
    cache_size: int = 0
    evictions: int = 0
    error_count: int = 0
    hit_rate_by_entity: Dict[str, Dict[str, int]] = field(default_factory=lambda: defaultdict(lambda: {'hits': 0, 'misses': 0}))

class CacheMonitor:
    def __init__(self):
        self.metrics = CacheMetrics()
        self.start_time = time.time()
    
    def record_hit(self, cache_key: str, entity_type: str = None):
        """Record cache hit"""
        self.metrics.hits += 1
        self.metrics.total_requests += 1
        
        if entity_type:
            self.metrics.hit_rate_by_entity[entity_type]['hits'] += 1
    
    def record_miss(self, cache_key: str, entity_type: str = None, 
                   response_time: float = None):
        """Record cache miss"""
        self.metrics.misses += 1
        self.metrics.total_requests += 1
        
        if response_time:
            self.metrics.total_response_time += response_time
            
        if entity_type:
            self.metrics.hit_rate_by_entity[entity_type]['misses'] += 1
    
    def record_error(self, error_type: str, cache_key: str = None):
        """Record cache error"""
        self.metrics.error_count += 1
    
    def get_hit_rate(self) -> float:
        """Calculate overall hit rate"""
        if self.metrics.total_requests == 0:
            return 0.0
        return self.metrics.hits / self.metrics.total_requests
    
    def get_average_response_time(self) -> float:
        """Calculate average API response time for misses"""
        if self.metrics.misses == 0:
            return 0.0
        return self.metrics.total_response_time / self.metrics.misses
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Generate comprehensive performance report"""
        uptime = time.time() - self.start_time
        
        entity_hit_rates = {}
        for entity, stats in self.metrics.hit_rate_by_entity.items():
            total = stats['hits'] + stats['misses']
            entity_hit_rates[entity] = {
                'hit_rate': stats['hits'] / total if total > 0 else 0.0,
                'total_requests': total
            }
        
        return {
            'overall_hit_rate': self.get_hit_rate(),
            'total_requests': self.metrics.total_requests,
            'cache_hits': self.metrics.hits,
            'cache_misses': self.metrics.misses,
            'average_api_response_time_ms': self.get_average_response_time() * 1000,
            'error_rate': self.metrics.error_count / max(self.metrics.total_requests, 1),
            'uptime_hours': uptime / 3600,
            'cache_size': self.metrics.cache_size,
            'evictions': self.metrics.evictions,
            'entity_performance': entity_hit_rates
        }
    
    def log_performance_summary(self):
        """Log performance summary"""
        report = self.get_performance_report()
        
        print("=== Cache Performance Report ===")
        print(f"Overall Hit Rate: {report['overall_hit_rate']:.2%}")
        print(f"Total Requests: {report['total_requests']:,}")
        print(f"Average API Response: {report['average_api_response_time_ms']:.0f}ms")
        print(f"Error Rate: {report['error_rate']:.2%}")
        print(f"Cache Size: {report['cache_size']:,} entries")
        
        if report['entity_performance']:
            print("\n--- Per-Entity Performance ---")
            for entity, stats in report['entity_performance'].items():
                print(f"{entity}: {stats['hit_rate']:.2%} hit rate "
                     f"({stats['total_requests']:,} requests)")
```

## Production Deployment Patterns

### Environment-Specific Caching

Configure caching based on deployment environment:

```python
import os
from enum import Enum

class CacheEnvironment(Enum):
    DEVELOPMENT = "dev"
    STAGING = "staging"
    PRODUCTION = "prod"

class EnvironmentAwareCacheConfig:
    def __init__(self, environment: CacheEnvironment = None):
        self.environment = environment or self._detect_environment()
        self.config = self._get_config()
    
    def _detect_environment(self) -> CacheEnvironment:
        """Auto-detect environment from environment variables"""
        env = os.getenv('CACHE_ENVIRONMENT', 'development').lower()
        
        if env in ['prod', 'production']:
            return CacheEnvironment.PRODUCTION
        elif env in ['staging', 'stage']:
            return CacheEnvironment.STAGING
        else:
            return CacheEnvironment.DEVELOPMENT
    
    def _get_config(self) -> Dict[str, Any]:
        """Get environment-specific cache configuration"""
        configs = {
            CacheEnvironment.DEVELOPMENT: {
                'default_ttl': 300,      # 5 minutes - short for development
                'max_cache_size': 50,    # Small cache for dev
                'enable_redis': False,   # Local only
                'enable_sqlite': True,   # Persistent across restarts
                'warmup_enabled': False, # No warmup in dev
                'metrics_enabled': True  # Debug metrics
            },
            
            CacheEnvironment.STAGING: {
                'default_ttl': 900,      # 15 minutes
                'max_cache_size': 200,   # Medium cache
                'enable_redis': True,    # Test Redis setup  
                'enable_sqlite': True,   # Backup persistence
                'warmup_enabled': True,  # Test warmup logic
                'metrics_enabled': True  # Full metrics
            },
            
            CacheEnvironment.PRODUCTION: {
                'default_ttl': 1800,     # 30 minutes - longer for production
                'max_cache_size': 1000,  # Large cache
                'enable_redis': True,    # Primary cache
                'enable_sqlite': False,  # Redis only for performance
                'warmup_enabled': True,  # Essential for performance
                'metrics_enabled': True  # Monitor everything
            }
        }
        
        return configs[self.environment]
    
    def get_redis_config(self) -> Dict[str, Any]:
        """Get Redis-specific configuration"""
        base_config = {
            'host': os.getenv('REDIS_HOST', 'localhost'),
            'port': int(os.getenv('REDIS_PORT', 6379)),
            'db': int(os.getenv('REDIS_DB', 0))
        }
        
        if self.environment == CacheEnvironment.PRODUCTION:
            base_config.update({
                'connection_pool_max_connections': 20,
                'socket_keepalive': True,
                'health_check_interval': 30
            })
        
        return base_config
```

## Best Practices and Recommendations

### Caching Strategy Guidelines

1. **TTL Selection Based on Data Type**:
   - **Static Reference Data** (committees, periods): 24 hours
   - **Semi-Static Data** (politician profiles): 6 hours  
   - **Active Data** (recent cases, votes): 15-30 minutes
   - **Real-time Data** (today's activity): 5 minutes

2. **Cache Key Design**:
   - Include all query parameters in key generation
   - Use consistent parameter ordering
   - Handle special characters in filter values
   - Version cache keys when API structure changes

3. **Memory Management**:
   - Implement LRU eviction for memory caches
   - Monitor cache hit rates per entity type
   - Set reasonable size limits based on available memory
   - Use compression for large cached responses

4. **Error Handling**:
   - Graceful degradation when cache is unavailable
   - Retry logic for cache operations  
   - Fallback to API when cache errors occur
   - Log cache errors for monitoring

5. **Performance Optimization**:
   - Batch cache operations when possible
   - Use async/await for non-blocking cache access
   - Implement cache warming for critical queries
   - Monitor and alert on poor hit rates

### Common Anti-Patterns to Avoid

L **Over-caching**: Don't cache every single API call - focus on expensive operations

L **Under-invalidation**: Not updating cache when underlying data changes

L **Cache Stampede**: Multiple processes fetching same data simultaneously when cache expires

L **Ignoring Errors**: Silent cache failures that degrade user experience

L **Memory Leaks**: Unbounded cache growth without proper eviction

 **Instead**: Implement selective caching with proper TTLs, change detection, request coalescing, error handling, and bounded cache sizes.

## Conclusion

Despite the Danish Parliamentary API's aggressive no-cache headers, intelligent client-side caching is essential for building responsive applications. The key is balancing data freshness with performance using the `opdateringsdato` timestamps for change detection and implementing multi-tier caching architectures suited to your application's needs.

By following the patterns and examples in this guide, you can achieve significant performance improvements while ensuring your application always reflects the most current parliamentary data.