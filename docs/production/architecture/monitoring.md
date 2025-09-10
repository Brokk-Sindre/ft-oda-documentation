# Production Monitoring

This guide covers comprehensive monitoring strategies for production applications consuming the Danish Parliamentary OData API, ensuring reliable operation and optimal performance.

## Overview

Effective monitoring of applications using the Danish Parliamentary API requires a multi-layered approach covering API health, application performance, infrastructure metrics, and business KPIs. Given the API's characteristics (response times 85ms-2s, 96,538+ cases, 18,139+ actors, 50+ entities), monitoring must account for varying response patterns and data volumes.

## API Health Monitoring

### Uptime and Availability Tracking

Monitor the core API endpoint availability with regular health checks:

```python
import requests
import time
from datetime import datetime
import logging

class ApiHealthMonitor:
    def __init__(self, base_url="https://oda.ft.dk/api"):
        self.base_url = base_url
        self.endpoints = {
            'cases': 'Sag',
            'actors': 'Aktør', 
            'votes': 'Afstemning',
            'documents': 'Dokument'
        }
        
    def check_endpoint_health(self, endpoint_name, endpoint_path, timeout=10):
        """Check health of specific API endpoint"""
        url = f"{self.base_url}/{endpoint_path}?%24top=1"
        start_time = time.time()
        
        try:
            response = requests.get(url, timeout=timeout)
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            return {
                'endpoint': endpoint_name,
                'status': 'healthy' if response.status_code == 200 else 'unhealthy',
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'timestamp': datetime.utcnow().isoformat(),
                'data_available': bool(response.json().get('value', []))
            }
        except requests.exceptions.Timeout:
            return {
                'endpoint': endpoint_name,
                'status': 'timeout',
                'status_code': None,
                'response_time_ms': timeout * 1000,
                'timestamp': datetime.utcnow().isoformat(),
                'error': 'Request timeout'
            }
        except Exception as e:
            return {
                'endpoint': endpoint_name,
                'status': 'error',
                'status_code': None,
                'response_time_ms': None,
                'timestamp': datetime.utcnow().isoformat(),
                'error': str(e)
            }
    
    def comprehensive_health_check(self):
        """Run health check on all monitored endpoints"""
        results = []
        for name, path in self.endpoints.items():
            results.append(self.check_endpoint_health(name, path))
        return results

# Usage example
monitor = ApiHealthMonitor()
health_status = monitor.comprehensive_health_check()

for status in health_status:
    if status['status'] != 'healthy':
        logging.warning(f"API issue detected: {status}")
```

### Service Dependency Monitoring

Create a dependency health dashboard:

```javascript
// JavaScript monitoring widget for web dashboards
class ApiStatusWidget {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.apiBase = 'https://oda.ft.dk/api';
        this.endpoints = ['Sag', 'Aktør', 'Afstemning', 'Dokument', 'Møde'];
        this.checkInterval = 30000; // 30 seconds
    }

    async checkApiHealth() {
        const results = [];
        
        for (const endpoint of this.endpoints) {
            const startTime = performance.now();
            
            try {
                const response = await fetch(
                    `${this.apiBase}/${endpoint}?%24top=1&%24select=id`,
                    { 
                        method: 'GET',
                        timeout: 10000 
                    }
                );
                
                const endTime = performance.now();
                const responseTime = Math.round(endTime - startTime);
                
                results.push({
                    endpoint,
                    status: response.ok ? 'healthy' : 'unhealthy',
                    statusCode: response.status,
                    responseTime,
                    timestamp: new Date().toISOString()
                });
            } catch (error) {
                results.push({
                    endpoint,
                    status: 'error',
                    error: error.message,
                    timestamp: new Date().toISOString()
                });
            }
        }
        
        return results;
    }

    renderStatus(results) {
        const statusHtml = results.map(result => {
            const statusClass = result.status === 'healthy' ? 'status-ok' : 'status-error';
            const responseTime = result.responseTime ? `${result.responseTime}ms` : 'N/A';
            
            return `
                <div class="api-endpoint ${statusClass}">
                    <span class="endpoint-name">${result.endpoint}</span>
                    <span class="response-time">${responseTime}</span>
                    <span class="status-indicator">${result.status}</span>
                </div>
            `;
        }).join('');

        this.container.innerHTML = `
            <div class="api-status-widget">
                <h3>API Health Status</h3>
                <div class="endpoints-list">${statusHtml}</div>
                <div class="last-updated">Last updated: ${new Date().toLocaleString()}</div>
            </div>
        `;
    }

    startMonitoring() {
        // Initial check
        this.checkApiHealth().then(results => this.renderStatus(results));
        
        // Periodic checks
        setInterval(async () => {
            const results = await this.checkApiHealth();
            this.renderStatus(results);
        }, this.checkInterval);
    }
}

// Initialize widget
const statusWidget = new ApiStatusWidget('api-status-container');
statusWidget.startMonitoring();
```

## Performance Monitoring

### Response Time Analysis

Track and analyze API response times across different query types:

```python
import statistics
from collections import defaultdict, deque
from datetime import datetime, timedelta

class PerformanceMonitor:
    def __init__(self, window_size=100):
        self.response_times = defaultdict(lambda: deque(maxlen=window_size))
        self.error_counts = defaultdict(int)
        self.request_counts = defaultdict(int)
        
    def record_request(self, endpoint, response_time_ms, status_code, query_complexity='simple'):
        """Record API request performance metrics"""
        timestamp = datetime.utcnow()
        
        # Track response times
        self.response_times[f"{endpoint}_{query_complexity}"].append({
            'time': response_time_ms,
            'timestamp': timestamp
        })
        
        # Track request counts
        self.request_counts[endpoint] += 1
        
        # Track errors
        if status_code >= 400:
            self.error_counts[endpoint] += 1
            
    def get_performance_stats(self, endpoint, query_complexity='simple'):
        """Get performance statistics for an endpoint"""
        key = f"{endpoint}_{query_complexity}"
        times = [r['time'] for r in self.response_times[key]]
        
        if not times:
            return None
            
        return {
            'count': len(times),
            'avg_ms': round(statistics.mean(times), 2),
            'median_ms': round(statistics.median(times), 2),
            'p95_ms': round(statistics.quantiles(times, n=20)[18], 2) if len(times) >= 20 else None,
            'p99_ms': round(statistics.quantiles(times, n=100)[98], 2) if len(times) >= 100 else None,
            'min_ms': min(times),
            'max_ms': max(times),
            'error_rate': self.error_counts[endpoint] / self.request_counts[endpoint] * 100
        }
    
    def check_performance_thresholds(self, endpoint, query_complexity='simple'):
        """Check if performance metrics exceed acceptable thresholds"""
        stats = self.get_performance_stats(endpoint, query_complexity)
        if not stats:
            return None
            
        alerts = []
        
        # Response time thresholds based on API characteristics (85ms-2s normal range)
        thresholds = {
            'simple': {'avg': 500, 'p95': 1000, 'p99': 2000},
            'complex': {'avg': 1000, 'p95': 2000, 'p99': 5000},
            'aggregation': {'avg': 2000, 'p95': 5000, 'p99': 10000}
        }
        
        threshold = thresholds.get(query_complexity, thresholds['simple'])
        
        if stats['avg_ms'] > threshold['avg']:
            alerts.append(f"Average response time ({stats['avg_ms']}ms) exceeds threshold ({threshold['avg']}ms)")
            
        if stats.get('p95_ms') and stats['p95_ms'] > threshold['p95']:
            alerts.append(f"95th percentile ({stats['p95_ms']}ms) exceeds threshold ({threshold['p95']}ms)")
            
        if stats['error_rate'] > 5.0:  # 5% error rate threshold
            alerts.append(f"Error rate ({stats['error_rate']:.2f}%) exceeds threshold (5%)")
            
        return alerts if alerts else None

# Example usage with request logging
monitor = PerformanceMonitor()

def make_monitored_request(endpoint, query_params, complexity='simple'):
    start_time = time.time()
    
    try:
        url = f"https://oda.ft.dk/api/{endpoint}?{query_params}"
        response = requests.get(url)
        response_time_ms = (time.time() - start_time) * 1000
        
        # Record performance metrics
        monitor.record_request(endpoint, response_time_ms, response.status_code, complexity)
        
        # Check for performance issues
        alerts = monitor.check_performance_thresholds(endpoint, complexity)
        if alerts:
            for alert in alerts:
                logging.warning(f"Performance alert for {endpoint}: {alert}")
        
        return response
        
    except Exception as e:
        response_time_ms = (time.time() - start_time) * 1000
        monitor.record_request(endpoint, response_time_ms, 500, complexity)
        raise
```

### Query Performance Classification

Classify and monitor different query complexity levels:

```python
class QueryComplexityAnalyzer:
    def __init__(self):
        self.complexity_patterns = {
            'simple': [
                r'\$top=[1-9]\d{0,1}$',  # Small top values
                r'\$select=\w+$',        # Single field selection
            ],
            'moderate': [
                r'\$top=[1-9]\d{2}$',    # Medium top values (100-999)
                r'\$filter=\w+\s+eq\s',  # Simple equality filters
                r'\$orderby=\w+$',       # Single field ordering
            ],
            'complex': [
                r'\$expand=',            # Any expansion
                r'\$filter=.*and.*or',   # Complex filter conditions
                r'\$top=[1-9]\d{3,}$',   # Large result sets (1000+)
            ],
            'aggregation': [
                r'\$apply=',             # OData aggregation
                r'groupby',              # Grouping operations
                r'aggregate',            # Aggregation functions
            ]
        }
    
    def classify_query(self, query_string):
        """Classify query complexity based on OData parameters"""
        import re
        
        for complexity, patterns in self.complexity_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_string, re.IGNORECASE):
                    return complexity
        
        return 'simple'  # Default classification

# Integration with monitoring
analyzer = QueryComplexityAnalyzer()

def execute_monitored_query(endpoint, query_params):
    complexity = analyzer.classify_query(query_params)
    return make_monitored_request(endpoint, query_params, complexity)
```

## Application-Level Monitoring

### Business KPI Tracking

Monitor application-specific metrics and business logic performance:

```python
class ApplicationMetrics:
    def __init__(self):
        self.metrics = defaultdict(list)
        
    def track_data_freshness(self, endpoint, latest_record_date):
        """Track how current the data is"""
        data_age_hours = (datetime.utcnow() - latest_record_date).total_seconds() / 3600
        
        self.metrics['data_freshness'].append({
            'endpoint': endpoint,
            'age_hours': data_age_hours,
            'timestamp': datetime.utcnow()
        })
        
        # Alert if data is stale (older than expected update frequency)
        expected_freshness = {
            'Sag': 24,      # Cases updated daily
            'Aktør': 168,   # Actors updated weekly
            'Afstemning': 24, # Votes updated daily
            'Dokument': 24,  # Documents updated daily
        }
        
        threshold = expected_freshness.get(endpoint, 24)
        if data_age_hours > threshold:
            logging.warning(f"Stale data detected in {endpoint}: {data_age_hours:.1f} hours old")
    
    def track_data_completeness(self, expected_count, actual_count, data_type):
        """Monitor data completeness and consistency"""
        completeness_rate = (actual_count / expected_count) * 100 if expected_count > 0 else 0
        
        self.metrics['data_completeness'].append({
            'data_type': data_type,
            'expected': expected_count,
            'actual': actual_count,
            'completeness_rate': completeness_rate,
            'timestamp': datetime.utcnow()
        })
        
        if completeness_rate < 95:  # Alert if completeness drops below 95%
            logging.error(f"Data completeness issue in {data_type}: {completeness_rate:.1f}%")
    
    def track_processing_pipeline(self, stage, processing_time_ms, records_processed):
        """Monitor data processing pipeline performance"""
        throughput = records_processed / (processing_time_ms / 1000) if processing_time_ms > 0 else 0
        
        self.metrics['pipeline_performance'].append({
            'stage': stage,
            'processing_time_ms': processing_time_ms,
            'records_processed': records_processed,
            'throughput_per_second': throughput,
            'timestamp': datetime.utcnow()
        })

# Example usage in data processing application
app_metrics = ApplicationMetrics()

def process_parliamentary_cases():
    start_time = time.time()
    
    # Fetch recent cases
    response = execute_monitored_query('Sag', '%24top=1000&%24orderby=opdateringsdato%20desc')
    cases = response.json().get('value', [])
    
    processing_time = (time.time() - start_time) * 1000
    
    # Track metrics
    if cases:
        latest_date = datetime.fromisoformat(cases[0]['opdateringsdato'].replace('Z', '+00:00'))
        app_metrics.track_data_freshness('Sag', latest_date)
    
    app_metrics.track_processing_pipeline('case_fetch', processing_time, len(cases))
    
    return cases
```

## Alert and Notification Systems

### Multi-Channel Alerting

Implement comprehensive alerting for different severity levels:

```python
import smtplib
import json
import requests
from enum import Enum
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning" 
    ERROR = "error"
    CRITICAL = "critical"

class AlertManager:
    def __init__(self, config):
        self.config = config
        self.alert_channels = {
            AlertSeverity.INFO: ['log'],
            AlertSeverity.WARNING: ['log', 'email'],
            AlertSeverity.ERROR: ['log', 'email', 'slack'],
            AlertSeverity.CRITICAL: ['log', 'email', 'slack', 'pagerduty']
        }
    
    def send_alert(self, severity, title, message, context=None):
        """Send alert through appropriate channels based on severity"""
        channels = self.alert_channels.get(severity, ['log'])
        
        alert_data = {
            'severity': severity.value,
            'title': title,
            'message': message,
            'context': context or {},
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'danish-parliament-api-monitor'
        }
        
        for channel in channels:
            try:
                if channel == 'log':
                    self._log_alert(alert_data)
                elif channel == 'email':
                    self._send_email_alert(alert_data)
                elif channel == 'slack':
                    self._send_slack_alert(alert_data)
                elif channel == 'pagerduty':
                    self._send_pagerduty_alert(alert_data)
            except Exception as e:
                logging.error(f"Failed to send alert via {channel}: {e}")
    
    def _log_alert(self, alert_data):
        """Log alert to application logs"""
        level = {
            'info': logging.info,
            'warning': logging.warning,
            'error': logging.error,
            'critical': logging.critical
        }.get(alert_data['severity'], logging.info)
        
        level(f"ALERT: {alert_data['title']} - {alert_data['message']}")
    
    def _send_slack_alert(self, alert_data):
        """Send alert to Slack webhook"""
        if not self.config.get('slack_webhook_url'):
            return
            
        color_map = {
            'info': '#36a64f',
            'warning': '#ff9500', 
            'error': '#ff0000',
            'critical': '#8B0000'
        }
        
        slack_message = {
            'attachments': [{
                'color': color_map.get(alert_data['severity'], '#36a64f'),
                'title': f"=¨ {alert_data['title']}",
                'text': alert_data['message'],
                'fields': [
                    {
                        'title': 'Severity',
                        'value': alert_data['severity'].upper(),
                        'short': True
                    },
                    {
                        'title': 'Service', 
                        'value': alert_data['service'],
                        'short': True
                    },
                    {
                        'title': 'Timestamp',
                        'value': alert_data['timestamp'],
                        'short': False
                    }
                ]
            }]
        }
        
        requests.post(self.config['slack_webhook_url'], json=slack_message)

# Usage with monitoring systems
alert_config = {
    'smtp_server': 'smtp.company.com',
    'smtp_port': 587,
    'email_username': 'alerts@company.com',
    'email_password': 'password',
    'alert_recipients': ['ops-team@company.com'],
    'slack_webhook_url': 'https://hooks.slack.com/services/...'
}

alert_manager = AlertManager(alert_config)

# Integration with performance monitoring
def check_and_alert_performance():
    for endpoint in ['Sag', 'Aktør', 'Afstemning']:
        alerts = monitor.check_performance_thresholds(endpoint)
        if alerts:
            for alert_message in alerts:
                alert_manager.send_alert(
                    AlertSeverity.WARNING,
                    f"Performance Issue: {endpoint}",
                    alert_message,
                    context={'endpoint': endpoint, 'metric_type': 'performance'}
                )
```

## Log Aggregation and Analysis

### Structured Logging

Implement structured logging for effective log aggregation:

```python
import json
import logging
from datetime import datetime

class StructuredLogger:
    def __init__(self, service_name="danish-parliament-api-client"):
        self.service_name = service_name
        self.logger = logging.getLogger(service_name)
        
        # Configure structured JSON logging
        handler = logging.StreamHandler()
        handler.setFormatter(JsonFormatter())
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_api_request(self, method, url, status_code, response_time_ms, 
                       response_size_bytes=None, error=None):
        """Log API request with structured data"""
        log_data = {
            'event_type': 'api_request',
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'request': {
                'method': method,
                'url': url,
                'parsed_url': self._parse_api_url(url)
            },
            'response': {
                'status_code': status_code,
                'response_time_ms': response_time_ms,
                'size_bytes': response_size_bytes
            },
            'success': 200 <= status_code < 400
        }
        
        if error:
            log_data['error'] = {
                'message': str(error),
                'type': type(error).__name__
            }
            self.logger.error(json.dumps(log_data))
        else:
            self.logger.info(json.dumps(log_data))
    
    def log_business_event(self, event_type, description, metadata=None):
        """Log business logic events"""
        log_data = {
            'event_type': event_type,
            'service': self.service_name,
            'timestamp': datetime.utcnow().isoformat(),
            'description': description,
            'metadata': metadata or {}
        }
        
        self.logger.info(json.dumps(log_data))
    
    def _parse_api_url(self, url):
        """Extract structured information from API URL"""
        import re
        from urllib.parse import urlparse, parse_qs
        
        parsed = urlparse(url)
        query_params = parse_qs(parsed.query)
        
        # Extract OData entity
        entity_match = re.search(r'/api/([^/?]+)', url)
        entity = entity_match.group(1) if entity_match else None
        
        return {
            'entity': entity,
            'query_params': {k: v[0] if len(v) == 1 else v for k, v in query_params.items()},
            'path': parsed.path
        }

class JsonFormatter(logging.Formatter):
    def format(self, record):
        # If the record message is already JSON, return it as-is
        try:
            json.loads(record.getMessage())
            return record.getMessage()
        except (json.JSONDecodeError, ValueError):
            # Standard log message, wrap in JSON
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'message': record.getMessage(),
                'logger': record.name,
                'module': record.module,
                'line': record.lineno
            }
            return json.dumps(log_data)

# Usage example
structured_logger = StructuredLogger()

def monitored_api_call(url):
    start_time = time.time()
    
    try:
        response = requests.get(url)
        response_time = (time.time() - start_time) * 1000
        
        structured_logger.log_api_request(
            method='GET',
            url=url,
            status_code=response.status_code,
            response_time_ms=round(response_time, 2),
            response_size_bytes=len(response.content)
        )
        
        return response
        
    except Exception as e:
        response_time = (time.time() - start_time) * 1000
        
        structured_logger.log_api_request(
            method='GET',
            url=url,
            status_code=0,
            response_time_ms=round(response_time, 2),
            error=e
        )
        raise
```

### Log Analysis Queries

Example queries for common log analysis scenarios using popular log aggregation tools:

```sql
-- Elasticsearch/OpenSearch queries for API monitoring

-- Average response time by endpoint (last 24 hours)
GET api-logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"event_type": "api_request"}},
        {"range": {"timestamp": {"gte": "now-24h"}}}
      ]
    }
  },
  "aggs": {
    "endpoints": {
      "terms": {"field": "request.parsed_url.entity"},
      "aggs": {
        "avg_response_time": {
          "avg": {"field": "response.response_time_ms"}
        }
      }
    }
  }
}

-- Error rate by status code (last 1 hour) 
GET api-logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"event_type": "api_request"}},
        {"range": {"timestamp": {"gte": "now-1h"}}}
      ]
    }
  },
  "aggs": {
    "status_codes": {
      "terms": {"field": "response.status_code"},
      "aggs": {
        "success_rate": {
          "bucket_script": {
            "buckets_path": {
              "total": "_count"
            },
            "script": "params.total"
          }
        }
      }
    }
  }
}

-- Slow queries (response time > 2000ms)
GET api-logs-*/_search
{
  "query": {
    "bool": {
      "must": [
        {"term": {"event_type": "api_request"}},
        {"range": {"response.response_time_ms": {"gt": 2000}}},
        {"range": {"timestamp": {"gte": "now-24h"}}}
      ]
    }
  },
  "sort": [{"response.response_time_ms": {"order": "desc"}}],
  "size": 100
}
```

## Capacity Planning and Resource Monitoring

### Infrastructure Metrics

Monitor system resources and capacity utilization:

```python
import psutil
import gc
from threading import Thread
import time

class ResourceMonitor:
    def __init__(self, check_interval=60):
        self.check_interval = check_interval
        self.monitoring = False
        self.metrics = []
        
    def start_monitoring(self):
        """Start background resource monitoring"""
        self.monitoring = True
        monitor_thread = Thread(target=self._monitor_loop, daemon=True)
        monitor_thread.start()
        
    def stop_monitoring(self):
        """Stop resource monitoring"""
        self.monitoring = False
        
    def _monitor_loop(self):
        """Background monitoring loop"""
        while self.monitoring:
            try:
                metrics = self._collect_metrics()
                self.metrics.append(metrics)
                
                # Keep only last 1000 measurements to prevent memory issues
                if len(self.metrics) > 1000:
                    self.metrics = self.metrics[-1000:]
                
                # Check for resource alerts
                self._check_resource_alerts(metrics)
                
                time.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"Error in resource monitoring: {e}")
                time.sleep(self.check_interval)
    
    def _collect_metrics(self):
        """Collect current system resource metrics"""
        import sys
        
        # Memory metrics
        memory = psutil.virtual_memory()
        process = psutil.Process()
        process_memory = process.memory_info()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        process_cpu = process.cpu_percent()
        
        # Disk metrics (for logging/caching)
        disk_usage = psutil.disk_usage('/')
        
        # Network metrics (if available)
        net_io = psutil.net_io_counters()
        
        # Python-specific metrics
        gc_stats = gc.get_stats()
        
        return {
            'timestamp': datetime.utcnow().isoformat(),
            'memory': {
                'system_total_gb': round(memory.total / (1024**3), 2),
                'system_available_gb': round(memory.available / (1024**3), 2),
                'system_used_percent': memory.percent,
                'process_rss_mb': round(process_memory.rss / (1024**2), 2),
                'process_vms_mb': round(process_memory.vms / (1024**2), 2)
            },
            'cpu': {
                'system_percent': cpu_percent,
                'process_percent': process_cpu,
                'load_average': psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            },
            'disk': {
                'total_gb': round(disk_usage.total / (1024**3), 2),
                'free_gb': round(disk_usage.free / (1024**3), 2),
                'used_percent': (disk_usage.used / disk_usage.total) * 100
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv,
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv
            } if net_io else None,
            'python': {
                'gc_collections': sum(stat['collections'] for stat in gc_stats),
                'active_threads': threading.active_count(),
                'python_version': sys.version.split()[0]
            }
        }
    
    def _check_resource_alerts(self, metrics):
        """Check resource metrics against thresholds"""
        # Memory alerts
        if metrics['memory']['system_used_percent'] > 90:
            alert_manager.send_alert(
                AlertSeverity.CRITICAL,
                "High Memory Usage",
                f"System memory usage at {metrics['memory']['system_used_percent']:.1f}%"
            )
        elif metrics['memory']['system_used_percent'] > 80:
            alert_manager.send_alert(
                AlertSeverity.WARNING,
                "Elevated Memory Usage", 
                f"System memory usage at {metrics['memory']['system_used_percent']:.1f}%"
            )
        
        # Process memory alerts
        if metrics['memory']['process_rss_mb'] > 1000:  # 1GB process memory
            alert_manager.send_alert(
                AlertSeverity.WARNING,
                "High Process Memory Usage",
                f"Process using {metrics['memory']['process_rss_mb']:.1f}MB RSS"
            )
        
        # CPU alerts
        if metrics['cpu']['system_percent'] > 90:
            alert_manager.send_alert(
                AlertSeverity.ERROR,
                "High CPU Usage",
                f"System CPU usage at {metrics['cpu']['system_percent']:.1f}%"
            )
        
        # Disk space alerts
        if metrics['disk']['used_percent'] > 90:
            alert_manager.send_alert(
                AlertSeverity.CRITICAL,
                "Low Disk Space",
                f"Disk usage at {metrics['disk']['used_percent']:.1f}%"
            )
    
    def get_resource_summary(self, hours=24):
        """Get resource usage summary for specified time period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        recent_metrics = [
            m for m in self.metrics 
            if datetime.fromisoformat(m['timestamp']) > cutoff_time
        ]
        
        if not recent_metrics:
            return None
            
        # Calculate averages and peaks
        memory_usage = [m['memory']['system_used_percent'] for m in recent_metrics]
        cpu_usage = [m['cpu']['system_percent'] for m in recent_metrics]
        process_memory = [m['memory']['process_rss_mb'] for m in recent_metrics]
        
        return {
            'period_hours': hours,
            'sample_count': len(recent_metrics),
            'memory': {
                'avg_system_percent': round(statistics.mean(memory_usage), 2),
                'peak_system_percent': max(memory_usage),
                'avg_process_mb': round(statistics.mean(process_memory), 2),
                'peak_process_mb': max(process_memory)
            },
            'cpu': {
                'avg_system_percent': round(statistics.mean(cpu_usage), 2),
                'peak_system_percent': max(cpu_usage)
            }
        }

# Start resource monitoring
resource_monitor = ResourceMonitor()
resource_monitor.start_monitoring()
```

## SLA Monitoring and Reporting

### Service Level Agreement Tracking

Implement SLA monitoring for API availability and performance:

```python
class SLAMonitor:
    def __init__(self):
        self.sla_targets = {
            'availability': 99.9,  # 99.9% uptime
            'response_time_p95': 2000,  # 95% of requests under 2s
            'response_time_p99': 5000,  # 99% of requests under 5s
            'error_rate': 1.0,  # Less than 1% error rate
        }
        self.measurements = defaultdict(list)
        
    def record_availability_measurement(self, endpoint, is_available, timestamp=None):
        """Record availability measurement"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        self.measurements['availability'].append({
            'endpoint': endpoint,
            'available': is_available,
            'timestamp': timestamp
        })
    
    def record_performance_measurement(self, endpoint, response_time_ms, 
                                     error_occurred=False, timestamp=None):
        """Record performance measurement"""
        if timestamp is None:
            timestamp = datetime.utcnow()
            
        self.measurements['performance'].append({
            'endpoint': endpoint,
            'response_time_ms': response_time_ms,
            'error': error_occurred,
            'timestamp': timestamp
        })
    
    def calculate_sla_compliance(self, period_hours=24):
        """Calculate SLA compliance for specified period"""
        cutoff_time = datetime.utcnow() - timedelta(hours=period_hours)
        
        # Filter measurements for period
        availability_data = [
            m for m in self.measurements['availability']
            if m['timestamp'] > cutoff_time
        ]
        
        performance_data = [
            m for m in self.measurements['performance']
            if m['timestamp'] > cutoff_time
        ]
        
        results = {
            'period_hours': period_hours,
            'measurement_period': {
                'start': cutoff_time.isoformat(),
                'end': datetime.utcnow().isoformat()
            }
        }
        
        # Calculate availability SLA
        if availability_data:
            total_checks = len(availability_data)
            successful_checks = sum(1 for m in availability_data if m['available'])
            availability_percent = (successful_checks / total_checks) * 100
            
            results['availability'] = {
                'actual_percent': round(availability_percent, 3),
                'target_percent': self.sla_targets['availability'],
                'compliant': availability_percent >= self.sla_targets['availability'],
                'total_checks': total_checks,
                'successful_checks': successful_checks,
                'downtime_minutes': self._calculate_downtime_minutes(availability_data)
            }
        
        # Calculate performance SLA
        if performance_data:
            response_times = [m['response_time_ms'] for m in performance_data if not m['error']]
            errors = sum(1 for m in performance_data if m['error'])
            total_requests = len(performance_data)
            error_rate = (errors / total_requests) * 100 if total_requests > 0 else 0
            
            if response_times:
                p95_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) >= 20 else max(response_times)
                p99_time = statistics.quantiles(response_times, n=100)[98] if len(response_times) >= 100 else max(response_times)
                
                results['performance'] = {
                    'response_time_p95_ms': round(p95_time, 2),
                    'response_time_p99_ms': round(p99_time, 2),
                    'p95_compliant': p95_time <= self.sla_targets['response_time_p95'],
                    'p99_compliant': p99_time <= self.sla_targets['response_time_p99'],
                    'error_rate_percent': round(error_rate, 2),
                    'error_rate_compliant': error_rate <= self.sla_targets['error_rate'],
                    'total_requests': total_requests,
                    'error_count': errors
                }
        
        return results
    
    def _calculate_downtime_minutes(self, availability_data):
        """Calculate total downtime in minutes"""
        # Sort by timestamp
        sorted_data = sorted(availability_data, key=lambda x: x['timestamp'])
        
        downtime_minutes = 0
        current_downtime_start = None
        
        for measurement in sorted_data:
            if not measurement['available'] and current_downtime_start is None:
                # Start of downtime period
                current_downtime_start = measurement['timestamp']
            elif measurement['available'] and current_downtime_start is not None:
                # End of downtime period
                downtime_duration = measurement['timestamp'] - current_downtime_start
                downtime_minutes += downtime_duration.total_seconds() / 60
                current_downtime_start = None
        
        # If still in downtime at end of period
        if current_downtime_start is not None:
            downtime_duration = datetime.utcnow() - current_downtime_start
            downtime_minutes += downtime_duration.total_seconds() / 60
            
        return round(downtime_minutes, 2)
    
    def generate_sla_report(self, period_hours=24):
        """Generate comprehensive SLA compliance report"""
        compliance = self.calculate_sla_compliance(period_hours)
        
        report = f"""
# SLA Compliance Report
**Period:** {compliance['measurement_period']['start']} to {compliance['measurement_period']['end']}
**Duration:** {period_hours} hours

## Availability SLA
"""
        
        if 'availability' in compliance:
            avail = compliance['availability']
            status = " COMPLIANT" if avail['compliant'] else "L NON-COMPLIANT"
            
            report += f"""
- **Status:** {status}
- **Actual Uptime:** {avail['actual_percent']}%
- **Target Uptime:** {avail['target_percent']}%
- **Total Checks:** {avail['total_checks']}
- **Successful Checks:** {avail['successful_checks']}
- **Total Downtime:** {avail['downtime_minutes']} minutes
"""
        
        if 'performance' in compliance:
            perf = compliance['performance']
            p95_status = "" if perf['p95_compliant'] else "L"
            p99_status = "" if perf['p99_compliant'] else "L"
            error_status = "" if perf['error_rate_compliant'] else "L"
            
            report += f"""
## Performance SLA

### Response Time
- **95th Percentile:** {p95_status} {perf['response_time_p95_ms']}ms (target: {self.sla_targets['response_time_p95']}ms)
- **99th Percentile:** {p99_status} {perf['response_time_p99_ms']}ms (target: {self.sla_targets['response_time_p99']}ms)

### Error Rate
- **Status:** {error_status} {perf['error_rate_percent']}% (target: d{self.sla_targets['error_rate']}%)
- **Total Requests:** {perf['total_requests']}
- **Error Count:** {perf['error_count']}
"""
        
        return report

# Usage with existing monitoring
sla_monitor = SLAMonitor()

# Integration with health checks
def enhanced_health_check():
    health_results = monitor.comprehensive_health_check()
    
    for result in health_results:
        # Record SLA measurements
        sla_monitor.record_availability_measurement(
            result['endpoint'],
            result['status'] == 'healthy'
        )
        
        if 'response_time_ms' in result:
            sla_monitor.record_performance_measurement(
                result['endpoint'],
                result['response_time_ms'],
                result['status'] != 'healthy'
            )

# Generate daily SLA reports
def generate_daily_sla_report():
    report = sla_monitor.generate_sla_report(24)
    
    # Send report via email or save to file
    with open(f"sla_report_{datetime.utcnow().strftime('%Y%m%d')}.md", 'w') as f:
        f.write(report)
    
    return report
```

## Incident Detection and Escalation

### Automated Incident Management

Implement automated incident detection and escalation procedures:

```python
from enum import Enum
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

class IncidentSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class IncidentStatus(Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"  
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"

@dataclass
class Incident:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    description: str = ""
    severity: IncidentSeverity = IncidentSeverity.LOW
    status: IncidentStatus = IncidentStatus.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    affected_services: List[str] = field(default_factory=list)
    context: dict = field(default_factory=dict)
    escalation_level: int = 0
    assigned_to: Optional[str] = None
    resolution_notes: Optional[str] = None

class IncidentManager:
    def __init__(self, alert_manager, sla_monitor):
        self.alert_manager = alert_manager
        self.sla_monitor = sla_monitor
        self.active_incidents = {}
        self.incident_history = []
        
        # Escalation rules
        self.escalation_rules = {
            IncidentSeverity.LOW: [30, 60, 120],      # Minutes before escalation
            IncidentSeverity.MEDIUM: [15, 30, 60],
            IncidentSeverity.HIGH: [10, 20, 30],
            IncidentSeverity.CRITICAL: [5, 10, 15]
        }
        
        # Auto-resolution timeouts (incidents resolved automatically if no new alerts)
        self.auto_resolution_timeouts = {
            IncidentSeverity.LOW: 60,      # 1 hour
            IncidentSeverity.MEDIUM: 30,   # 30 minutes
            IncidentSeverity.HIGH: 15,     # 15 minutes  
            IncidentSeverity.CRITICAL: 10  # 10 minutes
        }
    
    def detect_incidents(self):
        """Detect incidents from monitoring data"""
        incidents = []
        
        # Check API health incidents
        health_results = monitor.comprehensive_health_check()
        for result in health_results:
            if result['status'] != 'healthy':
                incident = self._create_health_incident(result)
                incidents.append(incident)
        
        # Check performance incidents
        for endpoint in ['Sag', 'Aktør', 'Afstemning', 'Dokument']:
            alerts = monitor.check_performance_thresholds(endpoint)
            if alerts:
                incident = self._create_performance_incident(endpoint, alerts)
                incidents.append(incident)
        
        # Check SLA violations
        sla_compliance = self.sla_monitor.calculate_sla_compliance(1)  # Last hour
        if 'availability' in sla_compliance and not sla_compliance['availability']['compliant']:
            incident = self._create_sla_incident('availability', sla_compliance['availability'])
            incidents.append(incident)
        
        if 'performance' in sla_compliance:
            perf = sla_compliance['performance']
            if not (perf['p95_compliant'] and perf['p99_compliant'] and perf['error_rate_compliant']):
                incident = self._create_sla_incident('performance', perf)
                incidents.append(incident)
        
        # Process detected incidents
        for incident in incidents:
            self.create_or_update_incident(incident)
    
    def create_or_update_incident(self, incident):
        """Create new incident or update existing one"""
        # Check if similar incident already exists
        existing_incident = self._find_similar_incident(incident)
        
        if existing_incident:
            # Update existing incident
            existing_incident.updated_at = datetime.utcnow()
            existing_incident.context.update(incident.context)
            
            # Escalate severity if needed
            if incident.severity.value > existing_incident.severity.value:
                existing_incident.severity = incident.severity
                self._send_escalation_alert(existing_incident, "Severity increased")
            
        else:
            # Create new incident
            self.active_incidents[incident.id] = incident
            self._send_incident_alert(incident, "New incident created")
            
            # Start escalation timer
            self._schedule_escalation(incident)
    
    def _create_health_incident(self, health_result):
        """Create incident from health check failure"""
        severity = IncidentSeverity.HIGH if health_result['status'] == 'error' else IncidentSeverity.MEDIUM
        
        return Incident(
            title=f"API Health Issue: {health_result['endpoint']}",
            description=f"Endpoint {health_result['endpoint']} is {health_result['status']}",
            severity=severity,
            affected_services=[health_result['endpoint']],
            context={
                'health_check': health_result,
                'incident_type': 'api_health'
            }
        )
    
    def _create_performance_incident(self, endpoint, alerts):
        """Create incident from performance issues"""
        return Incident(
            title=f"Performance Issue: {endpoint}",
            description=f"Performance degradation detected: {', '.join(alerts)}",
            severity=IncidentSeverity.MEDIUM,
            affected_services=[endpoint],
            context={
                'performance_alerts': alerts,
                'incident_type': 'performance'
            }
        )
    
    def _create_sla_incident(self, sla_type, sla_data):
        """Create incident from SLA violation"""
        severity = IncidentSeverity.HIGH if sla_type == 'availability' else IncidentSeverity.MEDIUM
        
        return Incident(
            title=f"SLA Violation: {sla_type.title()}",
            description=f"SLA compliance failure in {sla_type}",
            severity=severity,
            affected_services=['danish-parliament-api'],
            context={
                'sla_data': sla_data,
                'sla_type': sla_type,
                'incident_type': 'sla_violation'
            }
        )
    
    def _find_similar_incident(self, incident):
        """Find existing incident with similar characteristics"""
        for existing in self.active_incidents.values():
            if (existing.context.get('incident_type') == incident.context.get('incident_type') and
                set(existing.affected_services) & set(incident.affected_services) and
                existing.status not in [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]):
                return existing
        return None
    
    def _send_incident_alert(self, incident, action):
        """Send alert for incident event"""
        severity_map = {
            IncidentSeverity.LOW: AlertSeverity.INFO,
            IncidentSeverity.MEDIUM: AlertSeverity.WARNING,
            IncidentSeverity.HIGH: AlertSeverity.ERROR,
            IncidentSeverity.CRITICAL: AlertSeverity.CRITICAL
        }
        
        self.alert_manager.send_alert(
            severity_map[incident.severity],
            f"INCIDENT: {incident.title}",
            f"{action}\n\nDescription: {incident.description}\n"
            f"Affected Services: {', '.join(incident.affected_services)}\n"
            f"Incident ID: {incident.id}",
            context={
                'incident_id': incident.id,
                'incident_severity': incident.severity.name,
                'affected_services': incident.affected_services
            }
        )
    
    def resolve_incident(self, incident_id, resolution_notes=None):
        """Manually resolve an incident"""
        if incident_id in self.active_incidents:
            incident = self.active_incidents[incident_id]
            incident.status = IncidentStatus.RESOLVED
            incident.updated_at = datetime.utcnow()
            incident.resolution_notes = resolution_notes
            
            self._send_incident_alert(incident, "Incident resolved")
            
            # Move to history
            self.incident_history.append(incident)
            del self.active_incidents[incident_id]
    
    def get_incident_summary(self):
        """Get summary of current incident status"""
        active_count = len(self.active_incidents)
        severity_counts = defaultdict(int)
        
        for incident in self.active_incidents.values():
            severity_counts[incident.severity.name] += 1
        
        return {
            'active_incidents': active_count,
            'severity_breakdown': dict(severity_counts),
            'incidents': [
                {
                    'id': inc.id,
                    'title': inc.title,
                    'severity': inc.severity.name,
                    'status': inc.status.value,
                    'created_at': inc.created_at.isoformat(),
                    'affected_services': inc.affected_services
                }
                for inc in self.active_incidents.values()
            ]
        }

# Usage
incident_manager = IncidentManager(alert_manager, sla_monitor)

# Run incident detection periodically
def run_incident_detection():
    try:
        incident_manager.detect_incidents()
    except Exception as e:
        logging.error(f"Error in incident detection: {e}")

# Schedule incident detection every 5 minutes
import threading
def schedule_incident_detection():
    run_incident_detection()
    threading.Timer(300, schedule_incident_detection).start()

schedule_incident_detection()
```

## Monitoring Tools and Infrastructure

### Recommended Monitoring Stack

#### Docker Compose Setup for Complete Monitoring Stack

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  # Prometheus for metrics collection
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus:/etc/prometheus
      - prometheus_data:/prometheus
    networks:
      - monitoring

  # Grafana for visualization
  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
    ports:
      - "3000:3000"
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/var/lib/grafana/dashboards
      - ./monitoring/grafana/provisioning:/etc/grafana/provisioning
    networks:
      - monitoring

  # Elasticsearch for log storage
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    container_name: elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - elasticsearch_data:/usr/share/elasticsearch/data
    networks:
      - monitoring

  # Kibana for log analysis
  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    container_name: kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - monitoring

  # AlertManager for alert routing
  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    ports:
      - "9093:9093"
    volumes:
      - ./monitoring/alertmanager:/etc/alertmanager
    networks:
      - monitoring

  # Application metrics exporter
  app-exporter:
    build:
      context: .
      dockerfile: monitoring/Dockerfile.exporter
    container_name: app-exporter
    ports:
      - "8080:8080"
    environment:
      - API_BASE_URL=https://oda.ft.dk/api
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  elasticsearch_data:

networks:
  monitoring:
    driver: bridge
```

#### Prometheus Configuration

```yaml
# monitoring/prometheus/prometheus.yml
global:
  scrape_interval: 30s
  evaluation_interval: 30s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  - job_name: 'danish-parliament-api-monitor'
    static_configs:
      - targets: ['app-exporter:8080']
    scrape_interval: 30s
    metrics_path: /metrics

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

#### Prometheus Alert Rules

```yaml
# monitoring/prometheus/rules/api_alerts.yml
groups:
  - name: danish_parliament_api
    rules:
      # High response time alerts
      - alert: HighResponseTime
        expr: api_request_duration_p95 > 2000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High API response time detected"
          description: "95th percentile response time is {{ $value }}ms for endpoint {{ $labels.endpoint }}"

      - alert: CriticalResponseTime  
        expr: api_request_duration_p95 > 5000
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Critical API response time detected"
          description: "95th percentile response time is {{ $value }}ms for endpoint {{ $labels.endpoint }}"

      # Error rate alerts
      - alert: HighErrorRate
        expr: (rate(api_requests_total{status_code!~"2.."}[5m]) / rate(api_requests_total[5m])) * 100 > 5
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "High API error rate detected"
          description: "Error rate is {{ $value }}% for endpoint {{ $labels.endpoint }}"

      # Availability alerts
      - alert: APIUnavailable
        expr: up{job="danish-parliament-api-monitor"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "API monitoring service is down"
          description: "The API monitoring service has been down for more than 1 minute"

      # Data freshness alerts
      - alert: StaleData
        expr: api_data_age_hours > 24
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "Stale API data detected"
          description: "Data for {{ $labels.entity }} is {{ $value }} hours old"
```

#### Custom Metrics Exporter

```python
# monitoring/exporter.py
from prometheus_client import start_http_server, Counter, Histogram, Gauge
import time
import requests
from datetime import datetime
import logging

# Prometheus metrics
api_requests_total = Counter(
    'api_requests_total',
    'Total API requests',
    ['endpoint', 'status_code', 'method']
)

api_request_duration = Histogram(
    'api_request_duration_seconds',
    'API request duration',
    ['endpoint', 'method'],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

api_data_age_hours = Gauge(
    'api_data_age_hours',
    'Age of latest data in hours',
    ['entity']
)

api_available = Gauge(
    'api_available',
    'API endpoint availability (1=up, 0=down)',
    ['endpoint']
)

class ApiMetricsExporter:
    def __init__(self, api_base="https://oda.ft.dk/api"):
        self.api_base = api_base
        self.endpoints = {
            'cases': 'Sag',
            'actors': 'Aktør',
            'votes': 'Afstemning',
            'documents': 'Dokument'
        }
        
    def collect_metrics(self):
        """Collect metrics from Danish Parliament API"""
        for name, endpoint in self.endpoints.items():
            try:
                # Health check
                start_time = time.time()
                response = requests.get(
                    f"{self.api_base}/{endpoint}?%24top=1",
                    timeout=10
                )
                duration = time.time() - start_time
                
                # Update Prometheus metrics
                api_requests_total.labels(
                    endpoint=name,
                    status_code=response.status_code,
                    method='GET'
                ).inc()
                
                api_request_duration.labels(
                    endpoint=name,
                    method='GET'
                ).observe(duration)
                
                api_available.labels(endpoint=name).set(
                    1 if response.status_code == 200 else 0
                )
                
                # Check data freshness
                if response.status_code == 200:
                    data = response.json().get('value', [])
                    if data and 'opdateringsdato' in data[0]:
                        last_update = datetime.fromisoformat(
                            data[0]['opdateringsdato'].replace('Z', '+00:00')
                        )
                        age_hours = (datetime.utcnow().replace(tzinfo=last_update.tzinfo) - last_update).total_seconds() / 3600
                        api_data_age_hours.labels(entity=name).set(age_hours)
                
            except Exception as e:
                logging.error(f"Error collecting metrics for {name}: {e}")
                api_available.labels(endpoint=name).set(0)
    
    def start_collecting(self, interval=30):
        """Start metrics collection loop"""
        while True:
            try:
                self.collect_metrics()
            except Exception as e:
                logging.error(f"Error in metrics collection: {e}")
            
            time.sleep(interval)

if __name__ == '__main__':
    # Start Prometheus metrics server
    start_http_server(8080)
    
    # Start collecting metrics
    exporter = ApiMetricsExporter()
    exporter.start_collecting()
```

#### Grafana Dashboard Configuration

```json
{
  "dashboard": {
    "title": "Danish Parliament API Monitoring",
    "panels": [
      {
        "title": "API Availability",
        "type": "stat",
        "targets": [
          {
            "expr": "api_available",
            "legendFormat": "{{ endpoint }}"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        }
      },
      {
        "title": "Response Time (95th percentile)",
        "type": "graph",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(api_request_duration_seconds_bucket[5m]))",
            "legendFormat": "{{ endpoint }}"
          }
        ],
        "yAxes": [
          {
            "unit": "s",
            "label": "Response Time"
          }
        ]
      },
      {
        "title": "Request Rate",
        "type": "graph", 
        "targets": [
          {
            "expr": "rate(api_requests_total[5m])",
            "legendFormat": "{{ endpoint }}"
          }
        ]
      },
      {
        "title": "Error Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "(rate(api_requests_total{status_code!~\"2..\"}[5m]) / rate(api_requests_total[5m])) * 100",
            "legendFormat": "{{ endpoint }}"
          }
        ],
        "yAxes": [
          {
            "unit": "percent",
            "label": "Error Rate"
          }
        ]
      },
      {
        "title": "Data Freshness",
        "type": "graph",
        "targets": [
          {
            "expr": "api_data_age_hours",
            "legendFormat": "{{ entity }}"
          }
        ],
        "yAxes": [
          {
            "unit": "h",
            "label": "Hours"
          }
        ]
      }
    ],
    "time": {
      "from": "now-24h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## Best Practices and Recommendations

### Monitoring Strategy Recommendations

1. **Layered Monitoring Approach**
   - Infrastructure monitoring (CPU, memory, disk, network)
   - Application monitoring (response times, error rates, throughput)
   - Business logic monitoring (data quality, processing pipeline health)
   - User experience monitoring (end-to-end transaction success)

2. **Alert Fatigue Prevention**
   - Use appropriate alert thresholds based on API characteristics (85ms-2s response times)
   - Implement alert suppression during known maintenance windows
   - Group related alerts to avoid notification spam
   - Use escalation policies based on incident severity

3. **Performance Baseline Establishment**
   - Establish performance baselines during different load periods
   - Account for Danish Parliament session schedules affecting data update patterns
   - Monitor performance across different query complexities
   - Track seasonal variations in API usage

4. **Monitoring Data Retention**
   - Keep detailed metrics for 30 days for troubleshooting
   - Maintain aggregated metrics for 1 year for trend analysis
   - Store incident history for post-mortem analysis
   - Archive SLA reports for compliance documentation

5. **Dashboard Design Principles**
   - Create role-specific dashboards (operations, development, business)
   - Use clear visualizations that highlight anomalies
   - Include contextual information (expected ranges, SLA thresholds)
   - Enable drill-down capabilities for detailed analysis

This comprehensive monitoring strategy ensures reliable operation of production applications consuming the Danish Parliamentary API, providing visibility into performance, availability, and business impact while enabling proactive incident management and continuous optimization.