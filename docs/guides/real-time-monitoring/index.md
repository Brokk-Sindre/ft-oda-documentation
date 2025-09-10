# Real-time Monitoring

Build responsive applications that track Danish parliamentary activities with near real-time data updates and intelligent change detection strategies.

## Overview

The Danish Parliamentary OData API provides exceptionally fresh data, making it ideal for building real-time monitoring applications. Parliamentary activities are reflected in the API within hours, enabling developers to create responsive dashboards, alert systems, and analytical tools that keep pace with the democratic process.

### Key Monitoring Capabilities

- **Hours-Fresh Updates**: Parliamentary data updated within hours of actual events
- **Same-Day Availability**: Current session activities reflected immediately
- **Comprehensive Coverage**: All 50+ entity types support real-time tracking
- **Change Detection**: Timestamp-based monitoring for efficient polling
- **Scalable Architecture**: Handle concurrent monitoring across multiple data streams

## Data Freshness Patterns

### Update Frequency Analysis

Based on comprehensive monitoring of the API, here are the observed update patterns:

```yaml
Active Parliamentary Sessions:
  - Voting Records: Updated within 30 minutes
  - Case Status: Updated within 1-2 hours
  - Meeting Schedules: Updated same day
  - Document Publications: Available within hours

Off-Session Periods:
  - Future Meetings: Scheduled weeks in advance
  - Administrative Updates: Daily batch processing
  - Data Corrections: Irregular but immediate
  - Historical Amendments: Rare but documented
```

### Real-time Data Examples

Recent monitoring reveals the API's responsiveness:

```json
{
  "entity": "Afstemning",
  "id": 10377,
  "opdateringsdato": "2025-09-09T12:30:12.000",
  "status": "Updated same day as vote"
}

{
  "entity": "Sag", 
  "id": 102903,
  "opdateringsdato": "2025-09-09T17:49:11.870",
  "status": "Updated within hours"
}

{
  "entity": "Møde",
  "id": "future_meeting",
  "dato": "2025-09-12T08:30:00.000",
  "status": "Scheduled in advance"
}
```

## Change Detection Strategies

### Timestamp-Based Monitoring

The most efficient approach for real-time monitoring uses the `opdateringsdato` field:

```javascript
// Poll for recent changes
async function getRecentChanges(entityType, hoursBack = 8) {
  const cutoff = new Date(Date.now() - hoursBack * 60 * 60 * 1000);
  const filter = `opdateringsdato gt datetime'${cutoff.toISOString()}'`;
  
  const response = await fetch(
    `https://oda.ft.dk/api/${entityType}?%24filter=${encodeURIComponent(filter)}&%24orderby=opdateringsdato desc`
  );
  
  return await response.json();
}

// Monitor multiple entity types
const monitoredEntities = ['Sag', 'Afstemning', 'Dokument', 'Møde'];
const changes = await Promise.all(
  monitoredEntities.map(entity => getRecentChanges(entity, 4))
);
```

### Delta Synchronization Pattern

For applications requiring complete synchronization:

```python
class ParliamentaryMonitor:
    def __init__(self):
        self.last_sync = {}
    
    async def sync_entity(self, entity_type):
        # Get last sync timestamp for this entity
        last_update = self.last_sync.get(entity_type, '1900-01-01T00:00:00.000')
        
        # Query for changes since last sync
        filter_clause = f"opdateringsdato gt datetime'{last_update}'"
        url = f"https://oda.ft.dk/api/{entity_type}?%24filter={filter_clause}"
        
        changes = await self.fetch_all_pages(url)
        
        if changes:
            # Update last sync timestamp
            latest = max(item['opdateringsdato'] for item in changes)
            self.last_sync[entity_type] = latest
            
        return changes
```

## Polling Strategies

### Adaptive Polling Intervals

Match your polling frequency to parliamentary activity patterns:

```javascript
class AdaptivePolling {
  constructor() {
    this.baseInterval = 5 * 60 * 1000; // 5 minutes
    this.maxInterval = 60 * 60 * 1000;  // 1 hour
    this.currentInterval = this.baseInterval;
  }
  
  adjustInterval(changeCount) {
    if (changeCount > 10) {
      // High activity - increase frequency
      this.currentInterval = Math.max(
        this.currentInterval / 2, 
        60 * 1000 // Minimum 1 minute
      );
    } else if (changeCount === 0) {
      // No changes - decrease frequency
      this.currentInterval = Math.min(
        this.currentInterval * 1.5,
        this.maxInterval
      );
    }
  }
  
  async startMonitoring() {
    while (true) {
      const changes = await this.checkForChanges();
      this.adjustInterval(changes.length);
      await this.sleep(this.currentInterval);
    }
  }
}
```

### Priority-Based Monitoring

Different entity types require different monitoring strategies:

| Priority | Entity Types | Interval | Use Case |
|----------|-------------|----------|-----------|
| High | Afstemning, Sag | 2-5 minutes | Live voting tracking |
| Medium | Dokument, Møde | 10-15 minutes | Document publication |
| Low | Aktør, Periode | 1-4 hours | Reference data updates |
| Minimal | EUSag, Sambehandlinger | Daily | Administrative data |

## Performance Considerations

### Efficient Query Patterns

Optimize your monitoring queries for performance:

```javascript
//  GOOD: Specific time windows with ordering
const recentVotes = await fetch(
  `https://oda.ft.dk/api/Afstemning?%24filter=opdateringsdato gt datetime'${cutoff}'&%24orderby=opdateringsdato desc&%24top=50`
);

//  GOOD: Monitor specific high-value entities
const activeCases = await fetch(
  `https://oda.ft.dk/api/Sag?%24filter=statusid eq 8 and opdateringsdato gt datetime'${cutoff}'`
);

// L AVOID: Broad queries without time filters
const allData = await fetch('https://oda.ft.dk/api/Sag'); // Too expensive

// L AVOID: Complex expansions in monitoring queries
const expanded = await fetch(
  `https://oda.ft.dk/api/Sag?%24expand=DokumentAktør/Dokument/Fil` // Too slow
);
```

### Rate Limiting and Concurrency

While the API has no explicit rate limits, follow best practices:

```javascript
class RateLimitedMonitor {
  constructor(maxConcurrent = 5, delayBetween = 100) {
    this.semaphore = new Semaphore(maxConcurrent);
    this.delay = delayBetween;
  }
  
  async monitorWithBackoff(entityType) {
    await this.semaphore.acquire();
    
    try {
      const result = await this.checkEntity(entityType);
      await this.sleep(this.delay);
      return result;
    } finally {
      this.semaphore.release();
    }
  }
}
```

## Alert and Notification Systems

### Event-Driven Architecture

Build responsive notification systems:

```javascript
class ParliamentaryAlertSystem {
  constructor() {
    this.subscribers = new Map();
    this.lastStates = new Map();
  }
  
  subscribe(eventType, callback) {
    if (!this.subscribers.has(eventType)) {
      this.subscribers.set(eventType, []);
    }
    this.subscribers.get(eventType).push(callback);
  }
  
  async processChanges(changes) {
    for (const change of changes) {
      const alerts = this.detectAlerts(change);
      
      for (const alert of alerts) {
        const callbacks = this.subscribers.get(alert.type) || [];
        await Promise.all(callbacks.map(cb => cb(alert, change)));
      }
    }
  }
  
  detectAlerts(change) {
    const alerts = [];
    
    // New vote alert
    if (change.entity === 'Afstemning' && this.isNew(change)) {
      alerts.push({
        type: 'new_vote',
        priority: 'high',
        data: change
      });
    }
    
    // Status change alert
    if (this.hasStatusChanged(change)) {
      alerts.push({
        type: 'status_change',
        priority: 'medium',
        data: change
      });
    }
    
    return alerts;
  }
}
```

### Webhook Simulation

Since the API doesn't support webhooks, simulate them with intelligent polling:

```python
class WebhookSimulator:
    def __init__(self, webhook_url):
        self.webhook_url = webhook_url
        self.change_detector = ChangeDetector()
    
    async def simulate_webhooks(self):
        while True:
            changes = await self.change_detector.get_changes()
            
            for change in changes:
                payload = {
                    'event': 'data_change',
                    'entity': change['entity_type'],
                    'id': change['id'],
                    'timestamp': change['opdateringsdato'],
                    'data': change
                }
                
                await self.send_webhook(payload)
            
            await asyncio.sleep(self.get_poll_interval())
    
    async def send_webhook(self, payload):
        async with aiohttp.ClientSession() as session:
            await session.post(self.webhook_url, json=payload)
```

## Building Monitoring Applications

### Dashboard Architecture

Structure your real-time parliamentary dashboard:

```javascript
class ParliamentaryDashboard {
  constructor() {
    this.monitor = new ParliamentaryMonitor();
    this.ui = new DashboardUI();
    this.cache = new MemoryCache();
  }
  
  async initialize() {
    // Set up real-time data streams
    this.monitor.subscribe('vote_changes', this.updateVotingPanel.bind(this));
    this.monitor.subscribe('case_updates', this.updateCaseStatus.bind(this));
    this.monitor.subscribe('meeting_changes', this.updateSchedule.bind(this));
    
    // Start monitoring
    await this.monitor.start();
  }
  
  updateVotingPanel(changes) {
    this.ui.updateComponent('voting-panel', {
      recentVotes: changes,
      lastUpdate: new Date().toISOString()
    });
  }
}
```

### Error Handling and Resilience

Build robust monitoring systems that handle API unavailability:

```javascript
class ResilientMonitor {
  constructor() {
    this.maxRetries = 3;
    this.backoffMs = 1000;
    this.circuitBreaker = new CircuitBreaker();
  }
  
  async monitorWithRetry(entityType) {
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        if (this.circuitBreaker.isOpen()) {
          throw new Error('Circuit breaker open');
        }
        
        const result = await this.fetchWithTimeout(entityType);
        this.circuitBreaker.recordSuccess();
        return result;
        
      } catch (error) {
        this.circuitBreaker.recordFailure();
        
        if (attempt === this.maxRetries) {
          throw error;
        }
        
        await this.sleep(this.backoffMs * Math.pow(2, attempt - 1));
      }
    }
  }
}
```

## Monitoring Specific Use Cases

### Legislative Tracking

Monitor the progress of specific legislation:

```javascript
async function trackLegislation(caseId) {
  const monitor = new CaseMonitor(caseId);
  
  monitor.on('status_change', (oldStatus, newStatus) => {
    console.log(`Case ${caseId}: ${oldStatus}  ${newStatus}`);
  });
  
  monitor.on('new_document', (document) => {
    console.log(`New document: ${document.titel}`);
  });
  
  monitor.on('vote_scheduled', (vote) => {
    console.log(`Vote scheduled: ${vote.dato}`);
  });
  
  await monitor.start();
}
```

### Committee Activity

Track specific committee activities:

```javascript
class CommitteeMonitor {
  constructor(committeeId) {
    this.committeeId = committeeId;
    this.activities = [];
  }
  
  async monitorMeetings() {
    const meetings = await this.getUpcomingMeetings();
    
    for (const meeting of meetings) {
      this.scheduleMonitoring(meeting);
    }
  }
  
  async getUpcomingMeetings() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    
    return await fetch(
      `https://oda.ft.dk/api/Møde?%24filter=dato gt datetime'${tomorrow.toISOString()}' and udvalg eq ${this.committeeId}`
    ).then(r => r.json());
  }
}
```

## API Limitations and Workarounds

### No Native Push Notifications

**Limitation**: The API provides no webhook, WebSocket, or Server-Sent Events support.

**Workaround**: Implement intelligent polling with adaptive intervals:

```javascript
// Efficient polling strategy
class SmartPoller {
  constructor() {
    this.intervals = {
      active_session: 2 * 60 * 1000,    // 2 minutes
      normal_hours: 15 * 60 * 1000,    // 15 minutes  
      off_hours: 60 * 60 * 1000,       // 1 hour
      weekends: 4 * 60 * 60 * 1000     // 4 hours
    };
  }
  
  getCurrentInterval() {
    const now = new Date();
    const hour = now.getHours();
    const day = now.getDay();
    
    if (day === 0 || day === 6) return this.intervals.weekends;
    if (hour < 8 || hour > 18) return this.intervals.off_hours;
    if (await this.isParliamentInSession()) return this.intervals.active_session;
    
    return this.intervals.normal_hours;
  }
}
```

### Timezone Ambiguity

**Limitation**: Timestamps lack timezone information (assume CET/CEST).

**Workaround**: Always handle timezone conversion:

```javascript
function parseParliamentaryTimestamp(timestamp) {
  // Danish timestamps are CET/CEST
  const date = new Date(timestamp);
  
  // Convert to UTC accounting for Danish timezone
  const isDST = isDaylightSavingTime(date);
  const offset = isDST ? -2 : -1; // CEST or CET
  
  return new Date(date.getTime() + (offset * 60 * 60 * 1000));
}
```

## Specific Monitoring Guides

Explore detailed implementations for specific monitoring scenarios:

### [Change Detection](change-detection.md)
Deep dive into efficient algorithms for detecting changes across all entity types, including delta synchronization patterns and conflict resolution strategies.

### [Daily Updates](daily-updates.md) 
Comprehensive guide to monitoring daily parliamentary activities, including batch processing patterns and overnight synchronization strategies.

### [Polling Strategies](polling-strategies.md)
Advanced polling techniques including adaptive intervals, priority queues, circuit breakers, and performance optimization for high-frequency monitoring.

## Best Practices Summary

1. **Use Timestamp Filtering**: Always filter by `opdateringsdato` for efficiency
2. **Implement Adaptive Polling**: Adjust frequency based on activity levels
3. **Handle Errors Gracefully**: Use circuit breakers and exponential backoff
4. **Cache Intelligently**: Reduce API calls with smart caching strategies  
5. **Monitor Performance**: Track response times and adjust strategies
6. **Respect the API**: Use reasonable polling intervals and concurrency limits
7. **Plan for Downtime**: Build resilient systems that handle API unavailability
8. **Consider Timezones**: Account for CET/CEST when processing timestamps

## Getting Started

Ready to build your real-time monitoring application? Start with these steps:

1. **[Set up basic polling](../../getting-started/first-query.md)** - Learn fundamental API querying
2. **[Implement change detection](change-detection.md)** - Build efficient monitoring loops
3. **[Add error handling](../../production/troubleshooting/index.md)** - Create resilient applications  
4. **[Optimize performance](../../api-reference/performance/index.md)** - Scale your monitoring system

The Danish Parliamentary API's exceptional data freshness makes it an ideal foundation for building responsive, real-time applications that keep citizens informed about their democratic processes.