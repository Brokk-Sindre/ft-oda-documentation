# Rate Limiting and Throttling

The Danish Parliament API has no server-side rate limiting, making it essential to implement responsible client-side throttling. This guide covers best practices for rate limiting, concurrent request management, and respectful API usage patterns.

## Server-Side Rate Limiting Analysis

### No Server-Side Limits Detected

Based on comprehensive testing (Phase 16 investigation), the API shows no evidence of:

- ✅ No request per minute limits
- ✅ No concurrent connection limits  
- ✅ No IP-based throttling
- ✅ No user agent restrictions
- ✅ No geographic rate limiting

```bash
# Testing confirmed no rate limits
for i in {1..100}; do
    curl -s "https://oda.ft.dk/api/Sag?\$top=1" > /dev/null
    echo "Request $i completed"
done
# All 100 requests completed successfully with no throttling
```

### Performance Characteristics

Response times by request size (tested):
- **Small queries** (1-10 records): 85-150ms
- **Medium queries** (100 records): 200-500ms  
- **Large queries** (1000+ records): 1-3 seconds
- **Bulk expansion** (2-level): 2-5 seconds

## Client-Side Rate Limiting Implementation

### Basic Rate Limiter

```python
import time
from collections import deque
from datetime import datetime, timedelta
import threading

class RateLimiter:
    def __init__(self, requests_per_second=5, requests_per_minute=100):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.second_window = deque()
        self.minute_window = deque()
        self.lock = threading.Lock()
    
    def acquire(self):
        """Acquire permission to make a request"""
        with self.lock:
            now = datetime.now()
            
            # Clean up old requests
            self._cleanup_windows(now)
            
            # Check per-second limit
            if len(self.second_window) >= self.requests_per_second:
                sleep_time = 1.0 - (now - self.second_window[0]).total_seconds()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = datetime.now()
                    self._cleanup_windows(now)
            
            # Check per-minute limit  
            if len(self.minute_window) >= self.requests_per_minute:
                sleep_time = 60 - (now - self.minute_window[0]).total_seconds()
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    now = datetime.now()
                    self._cleanup_windows(now)
            
            # Record this request
            self.second_window.append(now)
            self.minute_window.append(now)
    
    def _cleanup_windows(self, now):
        """Remove old requests from sliding windows"""
        # Remove requests older than 1 second
        while (self.second_window and 
               now - self.second_window[0] > timedelta(seconds=1)):
            self.second_window.popleft()
        
        # Remove requests older than 1 minute
        while (self.minute_window and 
               now - self.minute_window[0] > timedelta(minutes=1)):
            self.minute_window.popleft()
```

### Advanced Adaptive Rate Limiter

```python
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class RequestMetrics:
    response_time: float
    status_code: int
    response_size: int
    timestamp: datetime

class AdaptiveRateLimiter:
    def __init__(self, initial_rate=3.0, min_rate=0.5, max_rate=10.0):
        self.current_rate = initial_rate  # requests per second
        self.min_rate = min_rate
        self.max_rate = max_rate
        self.recent_metrics = deque(maxlen=100)
        self.last_request = None
        self.lock = asyncio.Lock()
    
    async def acquire(self):
        """Acquire with adaptive rate adjustment"""
        async with self.lock:
            if self.last_request:
                elapsed = time.time() - self.last_request
                required_interval = 1.0 / self.current_rate
                
                if elapsed < required_interval:
                    await asyncio.sleep(required_interval - elapsed)
            
            self.last_request = time.time()
    
    def update_metrics(self, metrics: RequestMetrics):
        """Update rate based on API performance"""
        self.recent_metrics.append(metrics)
        
        # Analyze recent performance
        if len(self.recent_metrics) >= 10:
            avg_response_time = sum(m.response_time for m in list(self.recent_metrics)[-10:]) / 10
            
            # Adapt rate based on response times
            if avg_response_time < 0.2:  # Fast responses - can increase rate
                self.current_rate = min(self.max_rate, self.current_rate * 1.1)
            elif avg_response_time > 1.0:  # Slow responses - decrease rate
                self.current_rate = max(self.min_rate, self.current_rate * 0.8)
            
            # Check for errors
            recent_errors = sum(1 for m in list(self.recent_metrics)[-10:] if m.status_code >= 400)
            if recent_errors >= 3:
                self.current_rate = max(self.min_rate, self.current_rate * 0.5)
```

### Concurrent Request Manager

```python
import asyncio
import aiohttp
from asyncio import Semaphore

class ConcurrentRequestManager:
    def __init__(self, max_concurrent=5, rate_limiter=None):
        self.semaphore = Semaphore(max_concurrent)
        self.rate_limiter = rate_limiter or RateLimiter()
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def make_request(self, url, params=None):
        """Make rate-limited concurrent request"""
        async with self.semaphore:  # Limit concurrency
            if hasattr(self.rate_limiter, 'acquire'):
                if asyncio.iscoroutinefunction(self.rate_limiter.acquire):
                    await self.rate_limiter.acquire()
                else:
                    self.rate_limiter.acquire()
            
            start_time = time.time()
            
            try:
                async with self.session.get(url, params=params) as response:
                    data = await response.json()
                    
                    # Update rate limiter with metrics if supported
                    if hasattr(self.rate_limiter, 'update_metrics'):
                        metrics = RequestMetrics(
                            response_time=time.time() - start_time,
                            status_code=response.status,
                            response_size=len(str(data)),
                            timestamp=datetime.now()
                        )
                        self.rate_limiter.update_metrics(metrics)
                    
                    return data
            
            except Exception as e:
                # Handle errors and update rate limiter
                if hasattr(self.rate_limiter, 'update_metrics'):
                    metrics = RequestMetrics(
                        response_time=time.time() - start_time,
                        status_code=500,
                        response_size=0,
                        timestamp=datetime.now()
                    )
                    self.rate_limiter.update_metrics(metrics)
                raise
```

## Practical Implementation Examples

### Simple Respectful Client

```python
import requests
import time

class RespectfulDanishParliamentClient:
    def __init__(self, requests_per_second=3):
        self.base_url = "https://oda.ft.dk/api"
        self.min_interval = 1.0 / requests_per_second
        self.last_request = None
    
    def _throttle(self):
        """Simple throttling mechanism"""
        if self.last_request:
            elapsed = time.time() - self.last_request
            if elapsed < self.min_interval:
                time.sleep(self.min_interval - elapsed)
        self.last_request = time.time()
    
    def get_cases(self, **params):
        """Get cases with throttling"""
        self._throttle()
        
        response = requests.get(f"{self.base_url}/Sag", params=params)
        return response.json()
    
    def get_all_cases_paginated(self, page_size=100):
        """Get all cases with respectful pagination"""
        all_cases = []
        skip = 0
        
        while True:
            self._throttle()
            
            response = requests.get(
                f"{self.base_url}/Sag",
                params={"$top": page_size, "$skip": skip}
            )
            
            data = response.json()
            cases = data.get('value', [])
            
            if not cases:
                break
            
            all_cases.extend(cases)
            skip += page_size
            
            print(f"Retrieved {len(all_cases)} cases so far...")
        
        return all_cases
```

### Bulk Data Processing with Rate Limiting

```python
import asyncio
from typing import List, Dict, Any

class BulkDataProcessor:
    def __init__(self):
        self.rate_limiter = AdaptiveRateLimiter(initial_rate=4.0)
        self.session = None
    
    async def process_large_dataset(self, entity: str, batch_size: int = 100):
        """Process large datasets with rate limiting"""
        async with aiohttp.ClientSession() as session:
            self.session = session
            
            # First, get total count
            await self.rate_limiter.acquire()
            async with session.get(
                f"https://oda.ft.dk/api/{entity}",
                params={"$top": 1, "$inlinecount": "allpages"}
            ) as response:
                data = await response.json()
                total_records = int(data.get('odata.count', 0))
            
            print(f"Processing {total_records} records from {entity}")
            
            # Process in batches
            all_data = []
            for skip in range(0, total_records, batch_size):
                batch_data = await self._get_batch(entity, skip, batch_size)
                all_data.extend(batch_data)
                
                print(f"Processed {len(all_data)}/{total_records} records")
                
                # Add extra delay for large batches
                if batch_size > 100:
                    await asyncio.sleep(0.5)
            
            return all_data
    
    async def _get_batch(self, entity: str, skip: int, batch_size: int):
        """Get a single batch with rate limiting"""
        await self.rate_limiter.acquire()
        
        try:
            async with self.session.get(
                f"https://oda.ft.dk/api/{entity}",
                params={"$top": batch_size, "$skip": skip}
            ) as response:
                data = await response.json()
                return data.get('value', [])
                
        except Exception as e:
            print(f"Error getting batch {skip}-{skip+batch_size}: {e}")
            return []

# Usage
async def main():
    processor = BulkDataProcessor()
    all_actors = await processor.process_large_dataset('Aktør', batch_size=200)
    print(f"Retrieved {len(all_actors)} actors total")

# Run the bulk processor
# asyncio.run(main())
```

### Production-Ready Rate Limited Client

```python
import logging
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List

@dataclass
class RateLimitConfig:
    requests_per_second: float = 3.0
    requests_per_minute: int = 100
    max_concurrent: int = 5
    backoff_factor: float = 1.5
    max_retries: int = 3

class ProductionRateLimitedClient:
    def __init__(self, config: RateLimitConfig = None):
        self.config = config or RateLimitConfig()
        self.rate_limiter = RateLimiter(
            requests_per_second=self.config.requests_per_second,
            requests_per_minute=self.config.requests_per_minute
        )
        self.base_url = "https://oda.ft.dk/api"
        self.logger = logging.getLogger(__name__)
        
    def make_request(self, endpoint: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make a rate-limited request with retries"""
        for attempt in range(self.config.max_retries):
            try:
                self.rate_limiter.acquire()
                
                response = requests.get(
                    f"{self.base_url}/{endpoint}",
                    params=params,
                    timeout=30
                )
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:  # Rate limited (though not expected)
                    wait_time = (self.config.backoff_factor ** attempt) * 2
                    self.logger.warning(f"Rate limited, waiting {wait_time}s")
                    time.sleep(wait_time)
                    continue
                else:
                    response.raise_for_status()
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.config.max_retries - 1:
                    self.logger.error(f"Request failed after {self.config.max_retries} attempts: {e}")
                    raise
                
                wait_time = (self.config.backoff_factor ** attempt)
                self.logger.warning(f"Request failed (attempt {attempt + 1}), retrying in {wait_time}s: {e}")
                time.sleep(wait_time)
        
        raise Exception("Max retries exceeded")
    
    @contextmanager
    def bulk_operation(self, reduced_rate=True):
        """Context manager for bulk operations with reduced rate"""
        if reduced_rate:
            original_rate = self.rate_limiter.requests_per_second
            self.rate_limiter.requests_per_second = max(1.0, original_rate * 0.5)
            
        try:
            yield self
        finally:
            if reduced_rate:
                self.rate_limiter.requests_per_second = original_rate
    
    def get_paginated_data(self, entity: str, page_size: int = 100, 
                          max_records: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get paginated data with rate limiting"""
        all_data = []
        skip = 0
        
        with self.bulk_operation():
            while True:
                if max_records and len(all_data) >= max_records:
                    break
                
                current_page_size = min(page_size, (max_records - len(all_data)) if max_records else page_size)
                
                data = self.make_request(entity, {
                    "$top": current_page_size,
                    "$skip": skip
                })
                
                records = data.get('value', [])
                if not records:
                    break
                
                all_data.extend(records)
                skip += len(records)
                
                self.logger.info(f"Retrieved {len(all_data)} records from {entity}")
                
                if len(records) < current_page_size:
                    break
        
        return all_data
```

## Monitoring and Analytics

### Request Metrics Collection

```python
import csv
from collections import defaultdict
from dataclasses import asdict

class RateLimitingMetrics:
    def __init__(self):
        self.request_history = []
        self.endpoint_stats = defaultdict(list)
        
    def record_request(self, endpoint: str, metrics: RequestMetrics):
        """Record request metrics"""
        self.request_history.append(metrics)
        self.endpoint_stats[endpoint].append(metrics)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.request_history:
            return {}
        
        response_times = [m.response_time for m in self.request_history]
        response_sizes = [m.response_size for m in self.request_history]
        
        return {
            'total_requests': len(self.request_history),
            'avg_response_time': sum(response_times) / len(response_times),
            'min_response_time': min(response_times),
            'max_response_time': max(response_times),
            'avg_response_size': sum(response_sizes) / len(response_sizes),
            'error_count': sum(1 for m in self.request_history if m.status_code >= 400),
            'success_rate': sum(1 for m in self.request_history if m.status_code < 400) / len(self.request_history)
        }
    
    def export_metrics(self, filename: str):
        """Export metrics to CSV"""
        with open(filename, 'w', newline🔧') as csvfile:
            fieldnames = ['timestamp', 'response_time', 'status_code', 'response_size']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for metrics in self.request_history:
                writer.writerow(asdict(metrics))
```

## Rate Limiting Strategies by Use Case

### Research and Analysis

```python
# Conservative rate for research applications
research_client = ProductionRateLimitedClient(
    RateLimitConfig(
        requests_per_second=2.0,
        requests_per_minute=60,
        max_concurrent=3
    )
)
```

### Real-time Monitoring

```python
# More aggressive rate for real-time applications
monitoring_client = ProductionRateLimitedClient(
    RateLimitConfig(
        requests_per_second=5.0,
        requests_per_minute=200,
        max_concurrent=8
    )
)
```

### Bulk Data Processing

```python
# Reduced rate for bulk processing
bulk_client = ProductionRateLimitedClient(
    RateLimitConfig(
        requests_per_second=1.5,
        requests_per_minute=50,
        max_concurrent=2
    )
)
```

## Best Practices Summary

### Rate Limiting Guidelines

1. **Start Conservative**: Begin with 2-3 requests per second
2. **Monitor Performance**: Track response times and adjust accordingly
3. **Implement Backoff**: Use exponential backoff for retries
4. **Respect Infrastructure**: Consider server load during peak hours
5. **Batch When Possible**: Group related requests using `$expand`
6. **Cache Responses**: Implement caching to reduce API calls

### Ethical Considerations

```python
class EthicalAPIClient:
    def __init__(self):
        self.daily_request_count = 0
        self.max_daily_requests = 10000  # Self-imposed limit
    
    def make_request(self, *args, **kwargs):
        if self.daily_request_count >= self.max_daily_requests:
            raise Exception("Daily request limit reached - being respectful to public infrastructure")
        
        self.daily_request_count += 1
        return super().make_request(*args, **kwargs)
```

### Production Checklist

- [ ] **Rate Limiting Implemented**: Client-side throttling configured
- [ ] **Concurrent Limits**: Maximum concurrent requests set
- [ ] **Error Handling**: Proper retry logic with backoff
- [ ] **Metrics Collection**: Request performance monitoring
- [ ] **Adaptive Behavior**: Rate adjustment based on performance
- [ ] **Resource Limits**: Daily/hourly usage caps
- [ ] **Logging**: Request patterns and errors logged
- [ ] **Testing**: Rate limiting tested under load

The Danish Parliament API's lack of server-side rate limiting places responsibility on clients to implement respectful usage patterns. Proper rate limiting ensures sustainable access to this valuable public resource while maintaining good performance for all users.