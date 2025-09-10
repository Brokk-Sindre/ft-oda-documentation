# Polling Strategies

Effective polling strategies are crucial for building responsive, efficient monitoring systems for the Danish Parliament API. This guide provides comprehensive strategies for implementing intelligent polling systems that balance real-time requirements with API performance and respectful usage.

## Polling Fundamentals

### What is API Polling?

Polling involves repeatedly querying the API at intervals to detect changes in parliamentary data. The Danish Parliament API's excellent performance characteristics (85-150ms response times) make it well-suited for various polling approaches.

### Key Performance Characteristics

Based on extensive performance testing, the API delivers:

- **Small queries (d50 records)**: ~85-100ms response time
- **Medium queries (51-500 records)**: 100-300ms response time
- **Large queries (500-1000 records)**: 300-500ms response time
- **Very large queries (1000-10000 records)**: 2-3 seconds response time
- **No observed rate limits**: Excellent stability under load
- **100-record pagination limit**: Use `$skip` for larger datasets

### Core Polling Principles

1. **Respect the Service**: No rate limits doesn't mean unlimited usage
2. **Optimize for Change Detection**: Use timestamps for efficiency
3. **Handle Failures Gracefully**: Implement robust error handling
4. **Balance Freshness vs Performance**: Match polling frequency to need
5. **Cache Intelligently**: Minimize redundant requests

## Fixed Interval Polling

### Basic Fixed Interval Implementation

Fixed interval polling queries the API at regular intervals regardless of activity:

```python
import time
import requests
from datetime import datetime, timezone
from typing import Dict, List, Optional

class FixedIntervalPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api", interval: int = 300):
        self.base_url = base_url
        self.interval = interval  # seconds
        self.last_check = None
        
    def poll_entity(self, entity: str, query_params: Dict[str, str] = None) -> List[Dict]:
        """Poll a specific entity with fixed interval"""
        url = f"{self.base_url}/{entity}"
        
        # Add default pagination and selection
        params = {
            "$top": "100",
            "$select": "id,opdateringsdato",
            "$orderby": "opdateringsdato desc"
        }
        
        if query_params:
            params.update(query_params)
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            self.last_check = datetime.now(timezone.utc)
            return data.get('value', [])
            
        except requests.RequestException as e:
            print(f"Polling error for {entity}: {e}")
            return []
    
    def start_polling(self, entities: List[str], callback=None):
        """Start fixed interval polling for multiple entities"""
        print(f"Starting fixed interval polling every {self.interval} seconds")
        
        while True:
            for entity in entities:
                print(f"Polling {entity} at {datetime.now()}")
                records = self.poll_entity(entity)
                
                if callback:
                    callback(entity, records)
                
                time.sleep(1)  # Brief pause between entities
            
            time.sleep(self.interval)

# Usage example
poller = FixedIntervalPoller(interval=300)  # 5-minute intervals

def handle_updates(entity_name, records):
    print(f"Found {len(records)} records in {entity_name}")
    # Process records...

# Monitor key entities every 5 minutes
entities_to_monitor = ["Sag", "Afstemning", "Dokument"]
poller.start_polling(entities_to_monitor, handle_updates)
```

### Fixed Interval Pros and Cons

**Advantages:**
- Simple to implement and understand
- Predictable resource usage
- Consistent data freshness guarantees

**Disadvantages:**
- May miss rapid changes between intervals
- Inefficient during low-activity periods
- Fixed overhead regardless of activity

### Best Use Cases

- **Background monitoring** with predictable update patterns
- **Historical data collection** where slight delays are acceptable  
- **Resource-constrained environments** requiring predictable load

## Adaptive Polling Strategies

### Smart Frequency Adjustment

Adaptive polling adjusts intervals based on detected activity:

```python
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, List
import requests

class AdaptivePoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.min_interval = 30   # 30 seconds minimum
        self.max_interval = 1800  # 30 minutes maximum  
        self.current_interval = 300  # Start at 5 minutes
        self.last_activity = {}
        self.backoff_factor = 1.5
        
    def calculate_next_interval(self, entity: str, had_changes: bool) -> int:
        """Dynamically adjust polling interval based on activity"""
        if had_changes:
            # Increase frequency when changes detected
            self.current_interval = max(
                self.min_interval, 
                int(self.current_interval / self.backoff_factor)
            )
            self.last_activity[entity] = datetime.now(timezone.utc)
        else:
            # Decrease frequency when no changes
            time_since_activity = datetime.now(timezone.utc) - self.last_activity.get(
                entity, datetime.now(timezone.utc)
            )
            
            if time_since_activity > timedelta(hours=1):
                self.current_interval = min(
                    self.max_interval,
                    int(self.current_interval * self.backoff_factor)
                )
        
        return self.current_interval
    
    def detect_changes(self, entity: str, current_records: List[Dict]) -> bool:
        """Detect if records have changed since last poll"""
        if not current_records:
            return False
            
        # Check latest update timestamp
        latest_update = max(
            record.get('opdateringsdato', '') 
            for record in current_records
        )
        
        last_seen = self.last_activity.get(f"{entity}_timestamp", '')
        has_changes = latest_update > last_seen
        
        if has_changes:
            self.last_activity[f"{entity}_timestamp"] = latest_update
            
        return has_changes
    
    def adaptive_poll(self, entity: str, callback=None) -> int:
        """Poll entity and return next interval"""
        url = f"{self.base_url}/{entity}"
        params = {
            "$top": "50",
            "$select": "id,opdateringsdato,titel",
            "$orderby": "opdateringsdato desc"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            records = response.json().get('value', [])
            has_changes = self.detect_changes(entity, records)
            
            if callback and has_changes:
                callback(entity, records)
            
            next_interval = self.calculate_next_interval(entity, has_changes)
            
            print(f"{entity}: {'Changes detected' if has_changes else 'No changes'} "
                  f"- next poll in {next_interval}s")
            
            return next_interval
            
        except requests.RequestException as e:
            print(f"Error polling {entity}: {e}")
            # Return longer interval on error
            return min(self.max_interval, self.current_interval * 2)

# Usage example
adaptive_poller = AdaptivePoller()

def process_changes(entity_name, records):
    print(f"Processing {len(records)} changed records from {entity_name}")
    # Handle updates...

# Adaptive polling loop
entity = "Sag"
while True:
    interval = adaptive_poller.adaptive_poll(entity, process_changes)
    time.sleep(interval)
```

## Parliamentary Schedule-Based Polling

### Session-Aware Polling

The Danish Parliament follows predictable schedules. Optimize polling around parliamentary activities:

```python
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional
import calendar

class ParliamentarySchedulePoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        
        # Parliamentary session patterns (based on typical schedules)
        self.session_days = [0, 1, 2, 3, 4]  # Monday-Friday
        self.session_hours = {
            'morning': (9, 12),    # 9 AM - 12 PM
            'afternoon': (13, 18), # 1 PM - 6 PM
            'evening': (19, 22)    # 7 PM - 10 PM (voting sessions)
        }
        
        # Break periods with reduced activity
        self.break_periods = {
            'summer': ((6, 15), (8, 15)),  # Mid June - Mid August
            'christmas': ((12, 20), (1, 10)), # Dec 20 - Jan 10
            'easter': 'calculated_annually'
        }
    
    def is_session_time(self, dt: datetime = None) -> Dict[str, bool]:
        """Determine if parliament is likely in session"""
        if dt is None:
            dt = datetime.now(timezone.utc)
        
        # Convert to Copenhagen time (CET/CEST)
        copenhagen_time = dt.replace(tzinfo=timezone.utc).astimezone()
        
        is_session_day = copenhagen_time.weekday() in self.session_days
        current_hour = copenhagen_time.hour
        
        in_session_hours = any(
            start <= current_hour <= end 
            for start, end in self.session_hours.values()
        )
        
        in_break_period = self.is_break_period(copenhagen_time)
        
        return {
            'is_session_day': is_session_day,
            'in_session_hours': in_session_hours,
            'in_break_period': in_break_period,
            'likely_active': is_session_day and in_session_hours and not in_break_period
        }
    
    def is_break_period(self, dt: datetime) -> bool:
        """Check if current time is during parliamentary break"""
        month, day = dt.month, dt.day
        
        # Summer break
        if (month == 6 and day >= 15) or month == 7 or (month == 8 and day <= 15):
            return True
            
        # Christmas break  
        if (month == 12 and day >= 20) or (month == 1 and day <= 10):
            return True
            
        return False
    
    def get_optimal_interval(self, base_interval: int = 300) -> int:
        """Calculate optimal polling interval based on parliamentary schedule"""
        session_info = self.is_session_time()
        
        if session_info['likely_active']:
            # High activity expected - poll more frequently
            return max(60, base_interval // 3)  # Every 1-2 minutes
        elif session_info['is_session_day'] and not session_info['in_break_period']:
            # Session day but outside active hours - moderate polling
            return base_interval  # Standard interval
        elif session_info['in_break_period']:
            # Parliamentary break - minimal polling
            return base_interval * 6  # Every 30 minutes
        else:
            # Weekend - reduced polling
            return base_interval * 2  # Every 10 minutes
    
    def schedule_aware_poll(self, entities: List[str], callback=None):
        """Poll with schedule-aware intervals"""
        while True:
            current_time = datetime.now(timezone.utc)
            session_info = self.is_session_time(current_time)
            interval = self.get_optimal_interval()
            
            print(f"\n=== Polling at {current_time} ===")
            print(f"Session status: {session_info}")
            print(f"Next poll in: {interval} seconds")
            
            # Priority polling during active sessions
            if session_info['likely_active']:
                # Poll voting-related entities first during active sessions
                priority_entities = ['Afstemning', 'Stemme']
                for entity in priority_entities:
                    if entity in entities:
                        self.poll_entity(entity, callback)
                        time.sleep(1)  # Brief pause
                
                # Then poll other entities
                for entity in entities:
                    if entity not in priority_entities:
                        self.poll_entity(entity, callback)
                        time.sleep(1)
            else:
                # Standard polling during low activity
                for entity in entities:
                    self.poll_entity(entity, callback)
                    time.sleep(2)  # Longer pause between entities
            
            time.sleep(interval)
    
    def poll_entity(self, entity: str, callback=None) -> List[Dict]:
        """Poll a single entity"""
        url = f"{self.base_url}/{entity}"
        params = {
            "$top": "100",
            "$select": "id,opdateringsdato,titel",
            "$orderby": "opdateringsdato desc"
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            records = response.json().get('value', [])
            
            if callback:
                callback(entity, records)
            
            return records
            
        except requests.RequestException as e:
            print(f"Error polling {entity}: {e}")
            return []

# Usage example
schedule_poller = ParliamentarySchedulePoller()

def handle_session_data(entity_name, records):
    session_status = schedule_poller.is_session_time()
    priority = "HIGH" if session_status['likely_active'] else "NORMAL"
    
    print(f"[{priority}] {entity_name}: {len(records)} records")
    
    # Process with appropriate priority
    if priority == "HIGH" and entity_name in ['Afstemning', 'Stemme']:
        # Immediate processing for voting data during sessions
        process_immediately(entity_name, records)
    else:
        # Queue for batch processing
        queue_for_processing(entity_name, records)

def process_immediately(entity, records):
    print(f"IMMEDIATE: Processing {len(records)} {entity} records")
    # Handle real-time processing...

def queue_for_processing(entity, records):
    print(f"QUEUED: {len(records)} {entity} records for batch processing")
    # Add to processing queue...

# Start schedule-aware polling
entities_to_monitor = ["Sag", "Afstemning", "Stemme", "Dokument"]
schedule_poller.schedule_aware_poll(entities_to_monitor, handle_session_data)
```

## Rate Limiting and Respectful Polling

### Implementing Client-Side Rate Limiting

Even without API-enforced limits, implement respectful usage patterns:

```python
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List
import requests

class RespectfulPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.request_times = []
        self.max_requests_per_minute = 60  # Self-imposed limit
        self.max_requests_per_hour = 1000
        self.request_lock = threading.Lock()
        
    def can_make_request(self) -> bool:
        """Check if request is within rate limits"""
        now = datetime.now()
        
        with self.request_lock:
            # Clean old requests
            self.request_times = [
                req_time for req_time in self.request_times 
                if now - req_time < timedelta(hours=1)
            ]
            
            # Check hourly limit
            if len(self.request_times) >= self.max_requests_per_hour:
                return False
            
            # Check per-minute limit
            recent_requests = [
                req_time for req_time in self.request_times
                if now - req_time < timedelta(minutes=1)
            ]
            
            return len(recent_requests) < self.max_requests_per_minute
    
    def wait_for_rate_limit(self):
        """Wait until next request can be made"""
        while not self.can_make_request():
            time.sleep(1)
    
    def make_respectful_request(self, url: str, params: Dict = None) -> Dict:
        """Make request with rate limiting"""
        self.wait_for_rate_limit()
        
        with self.request_lock:
            self.request_times.append(datetime.now())
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            raise
    
    def respectful_poll(self, entity: str, query_params: Dict = None) -> List[Dict]:
        """Poll entity with rate limiting"""
        url = f"{self.base_url}/{entity}"
        
        default_params = {
            "$top": "100",
            "$select": "id,opdateringsdato,titel",
            "$orderby": "opdateringsdato desc"
        }
        
        if query_params:
            default_params.update(query_params)
        
        try:
            data = self.make_respectful_request(url, default_params)
            return data.get('value', [])
        except Exception as e:
            print(f"Respectful polling failed for {entity}: {e}")
            return []
    
    def get_rate_limit_status(self) -> Dict:
        """Get current rate limit status"""
        now = datetime.now()
        
        recent_minute = [
            req_time for req_time in self.request_times
            if now - req_time < timedelta(minutes=1)
        ]
        
        recent_hour = [
            req_time for req_time in self.request_times
            if now - req_time < timedelta(hours=1)
        ]
        
        return {
            'requests_last_minute': len(recent_minute),
            'requests_last_hour': len(recent_hour),
            'minute_limit': self.max_requests_per_minute,
            'hour_limit': self.max_requests_per_hour,
            'can_request': self.can_make_request()
        }

# Usage example
respectful_poller = RespectfulPoller()

def monitor_with_rate_limiting():
    entities = ["Sag", "Afstemning", "Dokument"]
    
    for entity in entities:
        status = respectful_poller.get_rate_limit_status()
        print(f"Rate limit status: {status}")
        
        if status['can_request']:
            records = respectful_poller.respectful_poll(entity)
            print(f"Polled {entity}: {len(records)} records")
        else:
            print(f"Rate limit reached, waiting...")
            respectful_poller.wait_for_rate_limit()
        
        time.sleep(2)  # Additional courtesy delay

monitor_with_rate_limiting()
```

## Entity-Specific Optimization

### Optimized Polling by Entity Type

Different entities have different update patterns:

```python
from typing import Dict, List, Optional
import requests
from datetime import datetime, timezone

class EntityOptimizedPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        
        # Entity-specific polling configurations
        self.entity_configs = {
            'Sag': {
                'interval': 600,  # 10 minutes - cases change less frequently
                'fields': 'id,titel,typeid,statusid,opdateringsdato',
                'top': 100,
                'priority': 'medium'
            },
            'Afstemning': {
                'interval': 180,  # 3 minutes - voting sessions are time-critical
                'fields': 'id,nummer,konklusion,vedtaget,opdateringsdato',
                'top': 50,
                'priority': 'high'
            },
            'Stemme': {
                'interval': 120,  # 2 minutes - individual votes change rapidly
                'fields': 'id,typeid,afstemningid,aktørid,opdateringsdato',
                'top': 200,
                'priority': 'high'
            },
            'Dokument': {
                'interval': 900,  # 15 minutes - documents change less often
                'fields': 'id,titel,dokumenttypeid,opdateringsdato',
                'top': 50,
                'priority': 'low'
            },
            'Aktør': {
                'interval': 3600,  # 1 hour - actor info changes rarely
                'fields': 'id,typeid,navn,opdateringsdato',
                'top': 100,
                'priority': 'low'
            }
        }
    
    def get_entity_query(self, entity: str) -> Dict:
        """Get optimized query parameters for entity"""
        config = self.entity_configs.get(entity, {})
        
        return {
            '$select': config.get('fields', 'id,opdateringsdato'),
            '$top': str(config.get('top', 100)),
            '$orderby': 'opdateringsdato desc'
        }
    
    def poll_entity_optimized(self, entity: str) -> Dict:
        """Poll entity with optimized parameters"""
        url = f"{self.base_url}/{entity}"
        params = self.get_entity_query(entity)
        
        start_time = datetime.now()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            end_time = datetime.now()
            response_time = (end_time - start_time).total_seconds() * 1000
            
            data = response.json()
            records = data.get('value', [])
            
            config = self.entity_configs.get(entity, {})
            
            return {
                'entity': entity,
                'records': records,
                'count': len(records),
                'response_time_ms': response_time,
                'next_poll_interval': config.get('interval', 300),
                'priority': config.get('priority', 'medium'),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except requests.RequestException as e:
            return {
                'entity': entity,
                'error': str(e),
                'records': [],
                'count': 0,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    def multi_entity_poll(self, entities: List[str]) -> Dict[str, Dict]:
        """Poll multiple entities with optimization"""
        results = {}
        
        # Sort by priority (high priority first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        sorted_entities = sorted(
            entities,
            key=lambda e: priority_order.get(
                self.entity_configs.get(e, {}).get('priority', 'medium'), 1
            )
        )
        
        for entity in sorted_entities:
            result = self.poll_entity_optimized(entity)
            results[entity] = result
            
            # Brief pause between entities, longer for low priority
            if result.get('priority') == 'high':
                time.sleep(0.5)
            elif result.get('priority') == 'medium':
                time.sleep(1)
            else:
                time.sleep(2)
        
        return results

# Usage example
optimizer = EntityOptimizedPoller()

def optimized_monitoring():
    entities_to_monitor = ["Afstemning", "Stemme", "Sag", "Dokument"]
    
    while True:
        print(f"\n=== Optimized polling cycle at {datetime.now()} ===")
        
        results = optimizer.multi_entity_poll(entities_to_monitor)
        
        for entity, result in results.items():
            if 'error' in result:
                print(f"L {entity}: Error - {result['error']}")
            else:
                print(f" {entity}: {result['count']} records "
                      f"({result['response_time_ms']:.1f}ms) "
                      f"[{result['priority']} priority]")
        
        # Wait based on shortest interval of monitored entities
        min_interval = min(
            optimizer.entity_configs.get(entity, {}).get('interval', 300)
            for entity in entities_to_monitor
        )
        
        print(f"Waiting {min_interval} seconds until next cycle...")
        time.sleep(min_interval)

optimized_monitoring()
```

## Exponential Backoff and Error Handling

### Robust Error Handling with Backoff

```python
import time
import random
from typing import Dict, List, Optional
import requests
from datetime import datetime, timezone

class RobustPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.max_retries = 3
        self.base_delay = 1  # seconds
        self.max_delay = 300  # 5 minutes
        self.jitter_factor = 0.1
        
    def exponential_backoff(self, attempt: int) -> float:
        """Calculate delay with exponential backoff and jitter"""
        delay = min(self.base_delay * (2 ** attempt), self.max_delay)
        jitter = delay * self.jitter_factor * random.random()
        return delay + jitter
    
    def poll_with_retry(self, entity: str, params: Dict = None) -> Optional[Dict]:
        """Poll entity with exponential backoff retry logic"""
        url = f"{self.base_url}/{entity}"
        
        default_params = {
            '$top': '100',
            '$select': 'id,opdateringsdato',
            '$orderby': 'opdateringsdato desc'
        }
        
        if params:
            default_params.update(params)
        
        last_error = None
        
        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(
                    url, 
                    params=default_params, 
                    timeout=30
                )
                response.raise_for_status()
                
                # Success - reset any error tracking
                return {
                    'success': True,
                    'data': response.json(),
                    'attempt': attempt + 1,
                    'entity': entity,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
            except requests.exceptions.Timeout:
                last_error = "Request timeout"
                print(f"Timeout polling {entity} (attempt {attempt + 1})")
                
            except requests.exceptions.ConnectionError:
                last_error = "Connection error"
                print(f"Connection error polling {entity} (attempt {attempt + 1})")
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code >= 500:
                    # Server errors - retry
                    last_error = f"Server error: {e.response.status_code}"
                    print(f"Server error polling {entity} (attempt {attempt + 1}): {e.response.status_code}")
                else:
                    # Client errors - don't retry
                    return {
                        'success': False,
                        'error': f"Client error: {e.response.status_code}",
                        'entity': entity,
                        'permanent_failure': True,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
            
            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                print(f"Unexpected error polling {entity} (attempt {attempt + 1}): {e}")
            
            # Don't delay after final attempt
            if attempt < self.max_retries:
                delay = self.exponential_backoff(attempt)
                print(f"Waiting {delay:.1f}s before retry...")
                time.sleep(delay)
        
        # All retries exhausted
        return {
            'success': False,
            'error': last_error,
            'entity': entity,
            'attempts': self.max_retries + 1,
            'permanent_failure': False,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def circuit_breaker_poll(self, entity: str, failure_threshold: int = 5) -> Dict:
        """Polling with circuit breaker pattern"""
        if not hasattr(self, 'circuit_state'):
            self.circuit_state = {}
        
        entity_state = self.circuit_state.get(entity, {
            'failures': 0,
            'last_failure': None,
            'state': 'closed',  # closed, open, half-open
            'last_success': datetime.now(timezone.utc)
        })
        
        # Check circuit breaker state
        if entity_state['state'] == 'open':
            # Check if we should try half-open
            if entity_state['last_failure']:
                time_since_failure = (
                    datetime.now(timezone.utc) - entity_state['last_failure']
                ).total_seconds()
                
                if time_since_failure > 300:  # 5 minutes
                    entity_state['state'] = 'half-open'
                    print(f"Circuit breaker for {entity}: HALF-OPEN (testing)")
                else:
                    print(f"Circuit breaker for {entity}: OPEN (failing fast)")
                    return {
                        'success': False,
                        'error': 'Circuit breaker open',
                        'entity': entity,
                        'circuit_open': True,
                        'timestamp': datetime.now(timezone.utc).isoformat()
                    }
        
        # Attempt the poll
        result = self.poll_with_retry(entity)
        
        if result['success']:
            # Success - reset circuit breaker
            entity_state['failures'] = 0
            entity_state['state'] = 'closed'
            entity_state['last_success'] = datetime.now(timezone.utc)
            print(f"Circuit breaker for {entity}: CLOSED (healthy)")
            
        else:
            # Failure - increment counter
            entity_state['failures'] += 1
            entity_state['last_failure'] = datetime.now(timezone.utc)
            
            if entity_state['failures'] >= failure_threshold:
                entity_state['state'] = 'open'
                print(f"Circuit breaker for {entity}: OPEN (too many failures)")
        
        self.circuit_state[entity] = entity_state
        return result

# Usage example
robust_poller = RobustPoller()

def resilient_monitoring():
    entities = ["Sag", "Afstemning", "Dokument"]
    
    while True:
        print(f"\n=== Resilient polling at {datetime.now()} ===")
        
        for entity in entities:
            result = robust_poller.circuit_breaker_poll(entity)
            
            if result['success']:
                records = result['data'].get('value', [])
                print(f" {entity}: {len(records)} records "
                      f"(attempt {result.get('attempt', 1)})")
            else:
                if result.get('circuit_open'):
                    print(f"=4 {entity}: Circuit breaker open")
                elif result.get('permanent_failure'):
                    print(f"L {entity}: Permanent failure - {result['error']}")
                else:
                    print(f"= {entity}: Temporary failure - {result['error']}")
            
            time.sleep(1)  # Brief pause between entities
        
        time.sleep(60)  # Wait 1 minute between cycles

resilient_monitoring()
```

## Async and Multi-threaded Polling

### Asynchronous Polling Implementation

```python
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone

class AsyncPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.session = None
        self.max_concurrent = 10
        
    async def __aenter__(self):
        """Async context manager entry"""
        connector = aiohttp.TCPConnector(limit=self.max_concurrent)
        timeout = aiohttp.ClientTimeout(total=30)
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        )
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def poll_entity_async(self, entity: str, params: Dict = None) -> Dict:
        """Asynchronously poll a single entity"""
        url = f"{self.base_url}/{entity}"
        
        default_params = {
            '$top': '100',
            '$select': 'id,opdateringsdato,titel',
            '$orderby': 'opdateringsdato desc'
        }
        
        if params:
            default_params.update(params)
        
        start_time = time.time()
        
        try:
            async with self.session.get(url, params=default_params) as response:
                response.raise_for_status()
                data = await response.json()
                
                end_time = time.time()
                response_time = (end_time - start_time) * 1000
                
                return {
                    'entity': entity,
                    'success': True,
                    'data': data,
                    'count': len(data.get('value', [])),
                    'response_time_ms': response_time,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
                
        except Exception as e:
            return {
                'entity': entity,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
    
    async def poll_multiple_async(self, entities: List[str]) -> List[Dict]:
        """Poll multiple entities concurrently"""
        tasks = [
            self.poll_entity_async(entity) 
            for entity in entities
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle any exceptions in results
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append({
                    'entity': entities[i],
                    'success': False,
                    'error': str(result),
                    'timestamp': datetime.now(timezone.utc).isoformat()
                })
            else:
                processed_results.append(result)
        
        return processed_results
    
    async def continuous_async_polling(self, entities: List[str], interval: int = 300):
        """Continuously poll entities asynchronously"""
        while True:
            print(f"\n=== Async polling cycle at {datetime.now()} ===")
            
            cycle_start = time.time()
            results = await self.poll_multiple_async(entities)
            cycle_time = (time.time() - cycle_start) * 1000
            
            successful_polls = sum(1 for r in results if r['success'])
            total_records = sum(r.get('count', 0) for r in results if r['success'])
            
            print(f"Cycle completed in {cycle_time:.1f}ms")
            print(f"Success rate: {successful_polls}/{len(entities)}")
            print(f"Total records: {total_records}")
            
            for result in results:
                if result['success']:
                    print(f" {result['entity']}: {result['count']} records "
                          f"({result['response_time_ms']:.1f}ms)")
                else:
                    print(f"L {result['entity']}: {result['error']}")
            
            await asyncio.sleep(interval)

# Threaded polling for mixed sync/async environments
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class ThreadedPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.max_workers = 5
        
    def poll_entity_sync(self, entity: str) -> Dict:
        """Synchronous entity polling for thread pool"""
        import requests
        
        url = f"{self.base_url}/{entity}"
        params = {
            '$top': '100',
            '$select': 'id,opdateringsdato,titel',
            '$orderby': 'opdateringsdato desc'
        }
        
        start_time = time.time()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            end_time = time.time()
            
            return {
                'entity': entity,
                'success': True,
                'data': data,
                'count': len(data.get('value', [])),
                'response_time_ms': (end_time - start_time) * 1000,
                'thread_id': threading.current_thread().ident
            }
            
        except Exception as e:
            return {
                'entity': entity,
                'success': False,
                'error': str(e),
                'thread_id': threading.current_thread().ident
            }
    
    def threaded_poll(self, entities: List[str]) -> List[Dict]:
        """Poll multiple entities using thread pool"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all polling tasks
            future_to_entity = {
                executor.submit(self.poll_entity_sync, entity): entity
                for entity in entities
            }
            
            results = []
            for future in as_completed(future_to_entity):
                entity = future_to_entity[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    results.append({
                        'entity': entity,
                        'success': False,
                        'error': str(e)
                    })
            
            return results

# Usage examples
async def run_async_polling():
    """Example of async polling usage"""
    entities = ["Sag", "Afstemning", "Stemme", "Dokument"]
    
    async with AsyncPoller() as poller:
        await poller.continuous_async_polling(entities, interval=180)

def run_threaded_polling():
    """Example of threaded polling usage"""
    poller = ThreadedPoller()
    entities = ["Sag", "Afstemning", "Dokument"]
    
    while True:
        print(f"\n=== Threaded polling at {datetime.now()} ===")
        
        start_time = time.time()
        results = poller.threaded_poll(entities)
        total_time = (time.time() - start_time) * 1000
        
        print(f"All polls completed in {total_time:.1f}ms")
        
        for result in results:
            if result['success']:
                print(f" {result['entity']}: {result['count']} records "
                      f"({result['response_time_ms']:.1f}ms) "
                      f"[Thread {result['thread_id']}]")
            else:
                print(f"L {result['entity']}: {result['error']}")
        
        time.sleep(300)  # 5-minute intervals

# Choose your approach:
# asyncio.run(run_async_polling())  # For async environments
# run_threaded_polling()            # For traditional sync code
```

## Performance Monitoring

### Polling Performance Metrics

```python
import time
import statistics
from collections import defaultdict, deque
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional
import json

class PollingMonitor:
    def __init__(self, history_duration: int = 3600):  # 1 hour
        self.history_duration = history_duration  # seconds
        self.metrics = defaultdict(lambda: {
            'response_times': deque(),
            'success_count': 0,
            'error_count': 0,
            'total_requests': 0,
            'last_success': None,
            'last_error': None,
            'record_counts': deque()
        })
        
    def record_poll_result(self, entity: str, response_time_ms: float, 
                          success: bool, record_count: int = 0, error: str = None):
        """Record polling result for monitoring"""
        now = datetime.now(timezone.utc)
        entity_metrics = self.metrics[entity]
        
        # Add timestamped data
        entity_metrics['response_times'].append((now, response_time_ms))
        entity_metrics['record_counts'].append((now, record_count))
        entity_metrics['total_requests'] += 1
        
        if success:
            entity_metrics['success_count'] += 1
            entity_metrics['last_success'] = now
        else:
            entity_metrics['error_count'] += 1
            entity_metrics['last_error'] = {'time': now, 'error': error}
        
        # Clean old data
        self._cleanup_old_data(entity)
    
    def _cleanup_old_data(self, entity: str):
        """Remove metrics older than history duration"""
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=self.history_duration)
        entity_metrics = self.metrics[entity]
        
        # Clean response times
        while (entity_metrics['response_times'] and 
               entity_metrics['response_times'][0][0] < cutoff_time):
            entity_metrics['response_times'].popleft()
        
        # Clean record counts
        while (entity_metrics['record_counts'] and 
               entity_metrics['record_counts'][0][0] < cutoff_time):
            entity_metrics['record_counts'].popleft()
    
    def get_entity_stats(self, entity: str) -> Dict:
        """Get comprehensive stats for an entity"""
        if entity not in self.metrics:
            return {'entity': entity, 'no_data': True}
        
        entity_metrics = self.metrics[entity]
        
        # Calculate response time statistics
        recent_times = [time for _, time in entity_metrics['response_times']]
        
        if recent_times:
            response_stats = {
                'avg_response_ms': statistics.mean(recent_times),
                'median_response_ms': statistics.median(recent_times),
                'min_response_ms': min(recent_times),
                'max_response_ms': max(recent_times),
                'p95_response_ms': self._percentile(recent_times, 95),
                'p99_response_ms': self._percentile(recent_times, 99)
            }
        else:
            response_stats = {}
        
        # Calculate success rate
        total = entity_metrics['total_requests']
        success_rate = (entity_metrics['success_count'] / total * 100) if total > 0 else 0
        
        # Calculate record count statistics
        recent_counts = [count for _, count in entity_metrics['record_counts']]
        record_stats = {}
        if recent_counts:
            record_stats = {
                'avg_records': statistics.mean(recent_counts),
                'max_records': max(recent_counts),
                'min_records': min(recent_counts),
                'total_records_retrieved': sum(recent_counts)
            }
        
        return {
            'entity': entity,
            'success_rate_pct': round(success_rate, 2),
            'total_requests': total,
            'success_count': entity_metrics['success_count'],
            'error_count': entity_metrics['error_count'],
            'last_success': entity_metrics['last_success'],
            'last_error': entity_metrics['last_error'],
            'response_times': response_stats,
            'record_statistics': record_stats,
            'data_points': len(recent_times),
            'monitoring_duration_hours': self.history_duration / 3600
        }
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile"""
        if not data:
            return 0
        sorted_data = sorted(data)
        index = (len(sorted_data) - 1) * percentile / 100
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def get_overall_health(self) -> Dict:
        """Get overall polling system health"""
        all_stats = {}
        total_requests = 0
        total_successes = 0
        all_response_times = []
        
        for entity in self.metrics:
            stats = self.get_entity_stats(entity)
            all_stats[entity] = stats
            
            total_requests += stats['total_requests']
            total_successes += stats['success_count']
            
            if 'response_times' in stats and stats['response_times']:
                all_response_times.extend([
                    time for _, time in self.metrics[entity]['response_times']
                ])
        
        overall_success_rate = (total_successes / total_requests * 100) if total_requests > 0 else 0
        
        health_status = 'healthy'
        if overall_success_rate < 95:
            health_status = 'degraded'
        if overall_success_rate < 80:
            health_status = 'unhealthy'
        
        avg_response_time = statistics.mean(all_response_times) if all_response_times else 0
        
        return {
            'overall_health': health_status,
            'overall_success_rate_pct': round(overall_success_rate, 2),
            'total_requests': total_requests,
            'entities_monitored': len(self.metrics),
            'avg_response_time_ms': round(avg_response_time, 2),
            'entity_details': all_stats,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
    
    def generate_report(self) -> str:
        """Generate human-readable monitoring report"""
        health = self.get_overall_health()
        
        report = []
        report.append(f"=== Polling System Health Report ===")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Overall Status: {health['overall_health'].upper()}")
        report.append(f"Success Rate: {health['overall_success_rate_pct']}%")
        report.append(f"Average Response Time: {health['avg_response_time_ms']}ms")
        report.append(f"Entities Monitored: {health['entities_monitored']}")
        report.append(f"Total Requests: {health['total_requests']}")
        report.append("")
        
        report.append("=== Entity Details ===")
        for entity, stats in health['entity_details'].items():
            if stats.get('no_data'):
                report.append(f"{entity}: No data available")
                continue
                
            status = "=â" if stats['success_rate_pct'] >= 95 else "=á" if stats['success_rate_pct'] >= 80 else "=4"
            
            report.append(f"{status} {entity}:")
            report.append(f"  Success Rate: {stats['success_rate_pct']}% ({stats['success_count']}/{stats['total_requests']})")
            
            if stats.get('response_times'):
                rt = stats['response_times']
                report.append(f"  Response Times: avg={rt.get('avg_response_ms', 0):.1f}ms, "
                             f"p95={rt.get('p95_response_ms', 0):.1f}ms")
            
            if stats.get('record_statistics'):
                rs = stats['record_statistics']
                report.append(f"  Records: avg={rs.get('avg_records', 0):.1f}, "
                             f"total={rs.get('total_records_retrieved', 0)}")
            
            if stats['last_error']:
                last_error_time = stats['last_error']['time'].strftime('%H:%M:%S')
                report.append(f"  Last Error: {last_error_time} - {stats['last_error']['error']}")
            
            report.append("")
        
        return "\n".join(report)

# Usage with polling system
class MonitoredPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.monitor = PollingMonitor()
        
    def poll_with_monitoring(self, entity: str) -> Dict:
        """Poll entity with comprehensive monitoring"""
        import requests
        
        url = f"{self.base_url}/{entity}"
        params = {
            '$top': '100',
            '$select': 'id,opdateringsdato,titel',
            '$orderby': 'opdateringsdato desc'
        }
        
        start_time = time.time()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            data = response.json()
            record_count = len(data.get('value', []))
            
            # Record successful poll
            self.monitor.record_poll_result(
                entity=entity,
                response_time_ms=response_time,
                success=True,
                record_count=record_count
            )
            
            return {
                'success': True,
                'entity': entity,
                'data': data,
                'response_time_ms': response_time,
                'record_count': record_count
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            # Record failed poll
            self.monitor.record_poll_result(
                entity=entity,
                response_time_ms=response_time,
                success=False,
                error=str(e)
            )
            
            return {
                'success': False,
                'entity': entity,
                'error': str(e),
                'response_time_ms': response_time
            }
    
    def monitored_polling_loop(self, entities: List[str], interval: int = 300):
        """Main polling loop with monitoring"""
        while True:
            print(f"\n=== Polling cycle at {datetime.now()} ===")
            
            for entity in entities:
                result = self.poll_with_monitoring(entity)
                
                if result['success']:
                    print(f" {entity}: {result['record_count']} records "
                          f"({result['response_time_ms']:.1f}ms)")
                else:
                    print(f"L {entity}: {result['error']} "
                          f"({result['response_time_ms']:.1f}ms)")
                
                time.sleep(1)  # Brief pause between entities
            
            # Print monitoring report every 10 cycles
            if hasattr(self, 'cycle_count'):
                self.cycle_count += 1
            else:
                self.cycle_count = 1
            
            if self.cycle_count % 10 == 0:
                print("\n" + "="*50)
                print(self.monitor.generate_report())
                print("="*50)
            
            time.sleep(interval)

# Example usage
monitored_poller = MonitoredPoller()
entities_to_monitor = ["Sag", "Afstemning", "Dokument"]
monitored_poller.monitored_polling_loop(entities_to_monitor, interval=180)
```

## Caching Integration

### Smart Caching with Timestamps

```python
import time
import json
import sqlite3
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from pathlib import Path

class CachedPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api", 
                 cache_db_path: str = "polling_cache.db"):
        self.base_url = base_url
        self.cache_db_path = cache_db_path
        self.init_cache_db()
        
    def init_cache_db(self):
        """Initialize SQLite cache database"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS poll_cache (
                    entity TEXT,
                    cache_key TEXT,
                    data TEXT,
                    timestamp TIMESTAMP,
                    max_updated TIMESTAMP,
                    record_count INTEGER,
                    PRIMARY KEY (entity, cache_key)
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON poll_cache(timestamp)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_max_updated 
                ON poll_cache(max_updated)
            ''')
    
    def generate_cache_key(self, entity: str, params: Dict) -> str:
        """Generate cache key from entity and parameters"""
        # Sort params for consistent keys
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{entity}?{param_str}"
    
    def get_cached_data(self, entity: str, params: Dict, 
                       max_age_seconds: int = 300) -> Optional[Dict]:
        """Retrieve cached data if still valid"""
        cache_key = self.generate_cache_key(entity, params)
        cutoff_time = datetime.now(timezone.utc) - timedelta(seconds=max_age_seconds)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                'SELECT * FROM poll_cache WHERE entity = ? AND cache_key = ? AND timestamp > ?',
                (entity, cache_key, cutoff_time)
            )
            
            row = cursor.fetchone()
            if row:
                return {
                    'data': json.loads(row['data']),
                    'timestamp': datetime.fromisoformat(row['timestamp']),
                    'max_updated': datetime.fromisoformat(row['max_updated']),
                    'record_count': row['record_count'],
                    'from_cache': True
                }
        
        return None
    
    def cache_data(self, entity: str, params: Dict, data: Dict):
        """Store data in cache with metadata"""
        cache_key = self.generate_cache_key(entity, params)
        
        # Extract max update timestamp from records
        records = data.get('value', [])
        max_updated = None
        
        if records:
            update_times = [
                record.get('opdateringsdato', '') 
                for record in records
                if record.get('opdateringsdato')
            ]
            if update_times:
                max_updated = max(update_times)
        
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute(
                '''INSERT OR REPLACE INTO poll_cache 
                   (entity, cache_key, data, timestamp, max_updated, record_count)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (
                    entity,
                    cache_key, 
                    json.dumps(data),
                    datetime.now(timezone.utc).isoformat(),
                    max_updated or datetime.now(timezone.utc).isoformat(),
                    len(records)
                )
            )
    
    def should_poll(self, entity: str, params: Dict, 
                   cache_max_age: int = 300) -> bool:
        """Determine if polling is needed or cache can be used"""
        cached_data = self.get_cached_data(entity, params, cache_max_age)
        
        if not cached_data:
            return True  # No cache, need to poll
        
        # Check if we have very recent cache
        cache_age = (datetime.now(timezone.utc) - cached_data['timestamp']).total_seconds()
        if cache_age < 30:  # Less than 30 seconds old
            return False
        
        # For frequently changing entities, poll more often
        if entity in ['Afstemning', 'Stemme'] and cache_age > 120:  # 2 minutes
            return True
            
        # For stable entities, longer cache times
        if entity in ['Aktør', 'Dokument'] and cache_age < 900:  # 15 minutes
            return False
        
        return True
    
    def intelligent_poll(self, entity: str, params: Dict = None, 
                        cache_max_age: int = 300) -> Dict:
        """Poll with intelligent caching"""
        if params is None:
            params = {
                '$top': '100',
                '$select': 'id,opdateringsdato,titel',
                '$orderby': 'opdateringsdato desc'
            }
        
        # Check if polling is needed
        if not self.should_poll(entity, params, cache_max_age):
            cached_data = self.get_cached_data(entity, params, cache_max_age)
            if cached_data:
                print(f"=Â  {entity}: Using cached data ({cached_data['record_count']} records)")
                return cached_data
        
        # Perform actual poll
        import requests
        
        url = f"{self.base_url}/{entity}"
        
        start_time = time.time()
        
        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            data = response.json()
            records = data.get('value', [])
            
            # Cache the response
            self.cache_data(entity, params, data)
            
            print(f"< {entity}: Fresh data retrieved ({len(records)} records, {response_time:.1f}ms)")
            
            return {
                'data': data,
                'timestamp': datetime.now(timezone.utc),
                'record_count': len(records),
                'response_time_ms': response_time,
                'from_cache': False
            }
            
        except Exception as e:
            # Try to return stale cache data on error
            stale_data = self.get_cached_data(entity, params, max_age_seconds=3600)  # 1 hour
            if stale_data:
                print(f"   {entity}: API error, using stale cache - {str(e)}")
                stale_data['stale_cache'] = True
                return stale_data
            
            raise Exception(f"Poll failed and no cache available: {e}")
    
    def cache_stats(self) -> Dict:
        """Get cache statistics"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Overall stats
            cursor = conn.execute('SELECT COUNT(*) as total FROM poll_cache')
            total = cursor.fetchone()['total']
            
            # Stats by entity
            cursor = conn.execute('''
                SELECT entity, COUNT(*) as count, 
                       AVG(record_count) as avg_records,
                       MAX(timestamp) as latest_cache
                FROM poll_cache 
                GROUP BY entity
            ''')
            
            by_entity = {
                row['entity']: {
                    'cached_queries': row['count'],
                    'avg_record_count': round(row['avg_records'], 1),
                    'latest_cache': row['latest_cache']
                }
                for row in cursor.fetchall()
            }
            
            # Cache age distribution
            now = datetime.now(timezone.utc)
            cursor = conn.execute('SELECT timestamp FROM poll_cache')
            timestamps = [datetime.fromisoformat(row['timestamp']) for row in cursor.fetchall()]
            
            age_buckets = {'< 5min': 0, '5-15min': 0, '15-60min': 0, '> 1hr': 0}
            for ts in timestamps:
                age_minutes = (now - ts).total_seconds() / 60
                if age_minutes < 5:
                    age_buckets['< 5min'] += 1
                elif age_minutes < 15:
                    age_buckets['5-15min'] += 1
                elif age_minutes < 60:
                    age_buckets['15-60min'] += 1
                else:
                    age_buckets['> 1hr'] += 1
        
        return {
            'total_cached_queries': total,
            'by_entity': by_entity,
            'age_distribution': age_buckets,
            'cache_file_size_mb': Path(self.cache_db_path).stat().st_size / (1024*1024)
        }

# Usage example
cached_poller = CachedPoller()

def intelligent_polling_demo():
    entities = ["Sag", "Afstemning", "Dokument", "Aktør"]
    
    for cycle in range(20):  # 20 polling cycles
        print(f"\n=== Intelligent Polling Cycle {cycle + 1} ===")
        
        for entity in entities:
            try:
                result = cached_poller.intelligent_poll(entity)
                cache_status = "CACHE" if result.get('from_cache') else "FRESH"
                
                if result.get('stale_cache'):
                    cache_status = "STALE"
                
                print(f"[{cache_status}] {entity}: {result['record_count']} records")
                
            except Exception as e:
                print(f"L {entity}: {e}")
            
            time.sleep(1)
        
        # Show cache stats every 5 cycles
        if (cycle + 1) % 5 == 0:
            print("\n--- Cache Statistics ---")
            stats = cached_poller.cache_stats()
            print(f"Total cached queries: {stats['total_cached_queries']}")
            print(f"Cache file size: {stats['cache_file_size_mb']:.1f} MB")
            print("Age distribution:", stats['age_distribution'])
        
        time.sleep(60)  # 1-minute cycles

intelligent_polling_demo()
```

## Production Deployment Strategies

### High-Availability Polling Architecture

For production environments, consider these architectural patterns:

```python
import os
import json
import redis
from typing import Dict, List, Optional
from datetime import datetime, timezone
import logging

class ProductionPoller:
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=0,
            decode_responses=True
        )
        self.instance_id = os.getenv('INSTANCE_ID', 'default')
        self.setup_logging()
        
    def setup_logging(self):
        """Configure structured logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(f'PollingService-{self.instance_id}')
    
    def acquire_polling_lock(self, entity: str, lock_duration: int = 300) -> bool:
        """Distributed locking for multi-instance deployment"""
        lock_key = f"polling_lock:{entity}"
        lock_value = f"{self.instance_id}:{datetime.now().timestamp()}"
        
        # Try to acquire lock
        acquired = self.redis_client.set(
            lock_key, 
            lock_value, 
            nx=True,  # Only set if not exists
            ex=lock_duration  # Expire after lock_duration seconds
        )
        
        if acquired:
            self.logger.info(f"Acquired polling lock for {entity}")
            return True
        else:
            current_holder = self.redis_client.get(lock_key)
            self.logger.debug(f"Lock held by {current_holder} for {entity}")
            return False
    
    def release_polling_lock(self, entity: str):
        """Release distributed lock"""
        lock_key = f"polling_lock:{entity}"
        self.redis_client.delete(lock_key)
        self.logger.info(f"Released polling lock for {entity}")
    
    def distributed_poll(self, entities: List[str]) -> Dict:
        """Poll entities with distributed locking"""
        results = {}
        
        for entity in entities:
            if self.acquire_polling_lock(entity):
                try:
                    result = self.poll_entity_production(entity)
                    results[entity] = result
                    
                    # Store result in Redis for other instances
                    self.store_poll_result(entity, result)
                    
                finally:
                    self.release_polling_lock(entity)
            else:
                # Try to get cached result from another instance
                cached_result = self.get_cached_poll_result(entity)
                if cached_result:
                    results[entity] = cached_result
                    self.logger.info(f"Using cached result for {entity}")
                else:
                    results[entity] = {'error': 'Unable to acquire lock and no cache available'}
        
        return results
    
    def poll_entity_production(self, entity: str) -> Dict:
        """Production-grade entity polling with full error handling"""
        import requests
        from requests.adapters import HTTPAdapter
        from requests.packages.urllib3.util.retry import Retry
        
        # Configure retry strategy
        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            status_forcelist=[429, 500, 502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS"],
            backoff_factor=1
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        url = f"{self.base_url}/{entity}"
        params = {
            '$top': '100',
            '$select': 'id,opdateringsdato,titel',
            '$orderby': 'opdateringsdato desc'
        }
        
        start_time = time.time()
        
        try:
            response = session.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000
            
            data = response.json()
            record_count = len(data.get('value', []))
            
            self.logger.info(
                f"Polled {entity}: {record_count} records in {response_time:.1f}ms"
            )
            
            return {
                'success': True,
                'entity': entity,
                'data': data,
                'record_count': record_count,
                'response_time_ms': response_time,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'instance_id': self.instance_id
            }
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            
            self.logger.error(
                f"Failed to poll {entity}: {str(e)} (took {response_time:.1f}ms)"
            )
            
            return {
                'success': False,
                'entity': entity,
                'error': str(e),
                'response_time_ms': response_time,
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'instance_id': self.instance_id
            }
    
    def store_poll_result(self, entity: str, result: Dict):
        """Store poll result in Redis for sharing between instances"""
        key = f"poll_result:{entity}"
        self.redis_client.setex(
            key, 
            300,  # 5-minute expiry
            json.dumps(result)
        )
    
    def get_cached_poll_result(self, entity: str) -> Optional[Dict]:
        """Retrieve cached poll result from Redis"""
        key = f"poll_result:{entity}"
        cached = self.redis_client.get(key)
        
        if cached:
            return json.loads(cached)
        return None
    
    def health_check(self) -> Dict:
        """Health check endpoint for load balancers"""
        try:
            # Test API connectivity
            response = requests.get(
                f"{self.base_url}/Sag",
                params={'$top': '1', '$select': 'id'},
                timeout=10
            )
            api_healthy = response.status_code == 200
            
            # Test Redis connectivity
            redis_healthy = self.redis_client.ping()
            
            return {
                'healthy': api_healthy and redis_healthy,
                'api_status': 'ok' if api_healthy else 'error',
                'redis_status': 'ok' if redis_healthy else 'error',
                'instance_id': self.instance_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            return {
                'healthy': False,
                'error': str(e),
                'instance_id': self.instance_id,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }

# Kubernetes deployment example
kubernetes_deployment = '''
apiVersion: apps/v1
kind: Deployment
metadata:
  name: parliamentary-poller
spec:
  replicas: 3
  selector:
    matchLabels:
      app: parliamentary-poller
  template:
    metadata:
      labels:
        app: parliamentary-poller
    spec:
      containers:
      - name: poller
        image: your-registry/parliamentary-poller:latest
        env:
        - name: REDIS_HOST
          value: "redis-service"
        - name: REDIS_PORT
          value: "6379"
        - name: INSTANCE_ID
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: redis-service
spec:
  selector:
    app: redis
  ports:
  - port: 6379
    targetPort: 6379
'''

# Usage example
production_poller = ProductionPoller()

def production_polling_service():
    entities = ["Sag", "Afstemning", "Stemme", "Dokument"]
    
    while True:
        try:
            # Perform health check
            health = production_poller.health_check()
            if not health['healthy']:
                production_poller.logger.error(f"Health check failed: {health}")
                time.sleep(30)  # Wait before retry
                continue
            
            # Perform distributed polling
            results = production_poller.distributed_poll(entities)
            
            # Log summary
            successful_polls = sum(1 for r in results.values() if r.get('success', False))
            production_poller.logger.info(
                f"Polling cycle complete: {successful_polls}/{len(entities)} successful"
            )
            
            # Wait before next cycle
            time.sleep(180)  # 3-minute cycles
            
        except KeyboardInterrupt:
            production_poller.logger.info("Shutting down gracefully...")
            break
        except Exception as e:
            production_poller.logger.error(f"Polling service error: {e}")
            time.sleep(60)  # Wait before retry

if __name__ == "__main__":
    production_polling_service()
```

## Best Practices Summary

### Polling Strategy Recommendations

1. **Choose the Right Strategy**:
   - **Fixed Interval**: Simple applications with predictable needs
   - **Adaptive**: Applications with varying activity patterns
   - **Schedule-Aware**: Real-time parliamentary monitoring
   - **Cached**: Resource-constrained or high-volume applications

2. **Performance Optimization**:
   - Use `$select` to limit fields
   - Implement pagination for large datasets
   - Monitor response times and adjust intervals
   - Use connection pooling for high-volume polling

3. **Error Handling**:
   - Implement exponential backoff
   - Use circuit breaker patterns
   - Have fallback mechanisms
   - Log errors for monitoring

4. **Respectful Usage**:
   - Implement client-side rate limiting
   - Use reasonable polling intervals
   - Cache responses when possible
   - Monitor your usage patterns

5. **Production Considerations**:
   - Distribute polling across instances
   - Implement health checks
   - Use structured logging
   - Monitor system metrics

The Danish Parliament API's excellent performance characteristics make it suitable for various polling strategies. Choose the approach that best matches your application's requirements for data freshness, resource usage, and complexity.

---

*This guide is based on extensive performance testing of the Danish Parliament API (oda.ft.dk) conducted in September 2025. Performance characteristics may vary based on network conditions and API server load.*