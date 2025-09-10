# Case Progress Tracking

Track legislative cases through the Danish Parliamentary system from introduction to final decision using comprehensive OData API queries and automated monitoring systems.

## Overview

The Danish Parliament processes over 96,000 cases with 68 distinct status types, representing one of the most detailed legislative tracking systems available. This guide shows how to monitor case progression through parliamentary stages, detect status changes, and build automated progress tracking systems.

## Case Lifecycle Architecture

### Status System Hierarchy

The Danish Parliamentary system uses a complex multi-layer classification:

- **68 Case Statuses** (`Sagsstatus`) - From proposal to final decision
- **13 Case Types** (`Sagstype`) - Legislative vs administrative processes
- **Case Steps** (`Sagstrin`) - Individual procedural stages
- **Case Step Status** (`Sagstrinsstatus`) - Progress within each step
- **Case Step Types** (`Sagstrinstype`) - Procedural stage categories

### Key Status Categories

```javascript
// Major status transitions in Danish Parliament
const statusCategories = {
  initiation: [
    "Modtaget",           // Received
    "1. behandling",      // First reading
    "Fremsat"            // Proposed
  ],
  committee: [
    "Henvist til udvalg", // Referred to committee
    "Under behandling",   // Under consideration
    "Udvalgsbehandling"   // Committee processing
  ],
  voting: [
    "2. behandling",      // Second reading  
    "3. behandling",      // Third reading
    "Afstemning"         // Vote
  ],
  outcomes: [
    "Vedtaget",          // Adopted
    "Forkastet",         // Rejected
    "Bortfaldet",        // Lapsed
    "Tilbagetaget"       // Withdrawn
  ]
};
```

## Status Tracking Implementation

### Real-time Status Monitoring

Monitor case status changes with automated polling:

```python
import requests
import time
from datetime import datetime, timedelta

class CaseProgressTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.last_update = datetime.now() - timedelta(hours=1)
        
    def get_recent_changes(self):
        """Get cases updated in the last hour"""
        since = self.last_update.strftime("%Y-%m-%dT%H:%M:%S")
        
        url = f"{self.base_url}/Sag"
        params = {
            "$filter": f"opdateringsdato gt datetime'{since}'",
            "$expand": "Sagsstatus,Sagstrin,Sagskategori",
            "$orderby": "opdateringsdato desc",
            "$top": "100"
        }
        
        response = requests.get(url, params=params)
        return response.json().get('value', [])
    
    def track_status_changes(self, case_ids):
        """Monitor specific cases for status changes"""
        id_filter = " or ".join([f"id eq {cid}" for cid in case_ids])
        
        url = f"{self.base_url}/Sag"
        params = {
            "$filter": id_filter,
            "$expand": "Sagsstatus,Sagstrin/Sagstrinsstatus",
            "$select": "id,titel,statusid,opdateringsdato"
        }
        
        response = requests.get(url, params=params)
        return response.json().get('value', [])

# Usage example
tracker = CaseProgressTracker()
recent_changes = tracker.get_recent_changes()

for case in recent_changes:
    print(f"Case {case['id']}: {case['titel'][:60]}...")
    print(f"Status: {case.get('Sagsstatus', {}).get('status', 'Unknown')}")
    print(f"Updated: {case['opdateringsdato']}")
    print("---")
```

### Progressive Case Filtering

Filter cases by their progress stage:

```python
def get_cases_by_stage(stage):
    """Get cases at specific legislative stage"""
    stage_filters = {
        'introduced': "substringof('Fremsat', Sagsstatus/status)",
        'committee': "substringof('udvalg', Sagsstatus/status)",
        'voting': "substringof('behandling', Sagsstatus/status)",
        'completed': "Sagsstatus/status eq 'Vedtaget' or Sagsstatus/status eq 'Forkastet'"
    }
    
    url = f"https://oda.ft.dk/api/Sag"
    params = {
        "$filter": stage_filters.get(stage, ""),
        "$expand": "Sagsstatus,Sagstrin",
        "$orderby": "opdateringsdato desc",
        "$top": "50"
    }
    
    response = requests.get(url, params=params)
    return response.json().get('value', [])

# Get all cases currently in committee
committee_cases = get_cases_by_stage('committee')
```

## Case Step Tracking

### Understanding Case Steps (`Sagstrin`)

Case steps represent individual procedural stages within a case lifecycle:

```python
def get_case_steps(case_id):
    """Get all procedural steps for a specific case"""
    url = f"https://oda.ft.dk/api/Sagstrin"
    params = {
        "$filter": f"sagid eq {case_id}",
        "$expand": "Sagstrinsstatus,Sagstrinstype,SagstrinAktør/Aktør",
        "$orderby": "dato asc"
    }
    
    response = requests.get(url, params=params)
    steps = response.json().get('value', [])
    
    return [{
        'step_id': step['id'],
        'title': step.get('titel', ''),
        'date': step.get('dato'),
        'status': step.get('Sagstrinsstatus', {}).get('status'),
        'type': step.get('Sagstrinstype', {}).get('type'),
        'actors': [actor['Aktør']['navn'] for actor in step.get('SagstrinAktør', [])]
    } for step in steps]

# Example usage
case_steps = get_case_steps(12345)
for step in case_steps:
    print(f"{step['date']}: {step['title']}")
    print(f"  Status: {step['status']}")
    print(f"  Actors: {', '.join(step['actors'])}")
```

### Step Progression Analysis

Track how cases move through procedural steps:

```python
def analyze_step_progression(case_id):
    """Analyze the progression timeline of a case"""
    steps = get_case_steps(case_id)
    
    timeline = []
    for i, step in enumerate(steps):
        duration = None
        if i > 0:
            prev_date = datetime.fromisoformat(steps[i-1]['date'].replace('Z', '+00:00'))
            curr_date = datetime.fromisoformat(step['date'].replace('Z', '+00:00'))
            duration = (curr_date - prev_date).days
            
        timeline.append({
            'step': step['title'],
            'date': step['date'],
            'days_since_previous': duration,
            'status': step['status']
        })
    
    return timeline

# Analyze progression
progression = analyze_step_progression(12345)
for item in progression:
    days = f" (+{item['days_since_previous']} days)" if item['days_since_previous'] else ""
    print(f"{item['date'][:10]}: {item['step']}{days}")
```

## Vote Scheduling and Outcome Tracking

### Tracking Voting Sessions

Monitor when cases are scheduled for voting and track outcomes:

```python
def get_upcoming_votes():
    """Get cases scheduled for voting"""
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
    
    url = "https://oda.ft.dk/api/Afstemning"
    params = {
        "$expand": "Møde,Stemme",
        "$filter": f"Møde/dato gt datetime'{tomorrow}'",
        "$orderby": "Møde/dato asc",
        "$top": "50"
    }
    
    response = requests.get(url, params=params)
    return response.json().get('value', [])

def track_voting_outcomes(case_id):
    """Track voting outcomes for a specific case"""
    url = "https://oda.ft.dk/api/Afstemning"
    params = {
        "$expand": "Stemme/Aktør",
        "$filter": f"sagstrinid eq {case_id}",
        "$orderby": "dato desc"
    }
    
    response = requests.get(url, params=params)
    votes = response.json().get('value', [])
    
    outcomes = []
    for vote in votes:
        outcome = {
            'date': vote.get('dato'),
            'result': vote.get('vedtaget'),
            'conclusion': vote.get('konklusion'),
            'vote_breakdown': {}
        }
        
        # Count votes by type
        for ballot in vote.get('Stemme', []):
            vote_type = ballot.get('typeid')
            outcome['vote_breakdown'][vote_type] = outcome['vote_breakdown'].get(vote_type, 0) + 1
        
        outcomes.append(outcome)
    
    return outcomes
```

### JavaScript Vote Tracking

```javascript
class VoteTracker {
    constructor() {
        this.baseUrl = 'https://oda.ft.dk/api';
    }
    
    async getVotingCalendar(days = 7) {
        const fromDate = new Date();
        const toDate = new Date(fromDate.getTime() + (days * 24 * 60 * 60 * 1000));
        
        const url = `${this.baseUrl}/Afstemning`;
        const params = new URLSearchParams({
            '$expand': 'Møde',
            '$filter': `Møde/dato ge datetime'${fromDate.toISOString()}' and Møde/dato le datetime'${toDate.toISOString()}'`,
            '$orderby': 'Møde/dato asc',
            '$top': '100'
        });
        
        const response = await fetch(`${url}?${params}`);
        const data = await response.json();
        
        return data.value.map(vote => ({
            id: vote.id,
            date: vote.Møde?.dato,
            title: vote.titel,
            meetingId: vote.mødeid,
            caseStepId: vote.sagstrinid
        }));
    }
    
    async getCaseVotingHistory(caseId) {
        // Get all case steps first
        const stepsUrl = `${this.baseUrl}/Sagstrin`;
        const stepsParams = new URLSearchParams({
            '$filter': `sagid eq ${caseId}`,
            '$select': 'id'
        });
        
        const stepsResponse = await fetch(`${stepsUrl}?${stepsParams}`);
        const stepsData = await stepsResponse.json();
        const stepIds = stepsData.value.map(s => s.id);
        
        if (stepIds.length === 0) return [];
        
        // Get voting records for these steps
        const votesUrl = `${this.baseUrl}/Afstemning`;
        const stepFilter = stepIds.map(id => `sagstrinid eq ${id}`).join(' or ');
        const votesParams = new URLSearchParams({
            '$filter': stepFilter,
            '$expand': 'Stemme/Aktør',
            '$orderby': 'dato desc'
        });
        
        const votesResponse = await fetch(`${votesUrl}?${votesParams}`);
        const votesData = await votesResponse.json();
        
        return votesData.value.map(vote => ({
            id: vote.id,
            date: vote.dato,
            adopted: vote.vedtaget,
            conclusion: vote.konklusion,
            voteCount: vote.Stemme?.length || 0
        }));
    }
}

// Usage
const tracker = new VoteTracker();
tracker.getVotingCalendar(14).then(calendar => {
    console.log('Upcoming votes:', calendar);
});
```

## Document Publication Milestones

### Tracking Document Flow

Monitor document publication as cases progress:

```python
def get_case_documents(case_id, track_timeline=True):
    """Get all documents associated with a case"""
    url = "https://oda.ft.dk/api/SagDokument"
    params = {
        "$filter": f"sagid eq {case_id}",
        "$expand": "Dokument/Dokumenttype,Dokument/Dokumentstatus",
        "$orderby": "Dokument/dato desc"
    }
    
    response = requests.get(url, params=params)
    relations = response.json().get('value', [])
    
    documents = []
    for rel in relations:
        doc = rel.get('Dokument', {})
        documents.append({
            'id': doc.get('id'),
            'title': doc.get('titel', ''),
            'date': doc.get('dato'),
            'type': doc.get('Dokumenttype', {}).get('type'),
            'status': doc.get('Dokumentstatus', {}).get('status'),
            'update_date': doc.get('opdateringsdato')
        })
    
    if track_timeline:
        # Sort by date to create timeline
        documents.sort(key=lambda x: x['date'] or '')
        
    return documents

def detect_publication_milestones(case_id):
    """Detect key document publication milestones"""
    documents = get_case_documents(case_id)
    
    milestones = {
        'proposal_published': None,
        'committee_report': None,
        'amendment_deadline': None,
        'final_text': None
    }
    
    for doc in documents:
        doc_type = doc['type'].lower() if doc['type'] else ''
        
        if 'forslag' in doc_type and not milestones['proposal_published']:
            milestones['proposal_published'] = doc['date']
        elif 'betænkning' in doc_type and not milestones['committee_report']:
            milestones['committee_report'] = doc['date']
        elif 'vedtagelse' in doc_type and not milestones['final_text']:
            milestones['final_text'] = doc['date']
    
    return milestones
```

## Automated Progress Monitoring Systems

### Complete Monitoring Dashboard

Build a comprehensive case tracking system:

```python
class ParliamentaryDashboard:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.tracked_cases = []
        
    def add_cases_to_track(self, case_ids):
        """Add cases to monitoring list"""
        self.tracked_cases.extend(case_ids)
        self.tracked_cases = list(set(self.tracked_cases))  # Remove duplicates
        
    def get_dashboard_data(self):
        """Get complete dashboard overview"""
        if not self.tracked_cases:
            return {}
            
        # Build filter for all tracked cases
        case_filter = " or ".join([f"id eq {cid}" for cid in self.tracked_cases])
        
        url = f"{self.base_url}/Sag"
        params = {
            "$filter": case_filter,
            "$expand": "Sagsstatus,Sagstrin,SagAktør/Aktør",
            "$select": "id,titel,statusid,afgørelsesdato,opdateringsdato"
        }
        
        response = requests.get(url, params=params)
        cases = response.json().get('value', [])
        
        dashboard = {
            'total_cases': len(cases),
            'by_status': {},
            'recent_updates': [],
            'upcoming_deadlines': [],
            'cases': []
        }
        
        for case in cases:
            status = case.get('Sagsstatus', {}).get('status', 'Unknown')
            dashboard['by_status'][status] = dashboard['by_status'].get(status, 0) + 1
            
            case_data = {
                'id': case['id'],
                'title': case['titel'][:80] + '...' if len(case['titel']) > 80 else case['titel'],
                'status': status,
                'last_updated': case['opdateringsdato'],
                'decision_date': case.get('afgørelsesdato'),
                'actors': [actor['Aktør']['navn'] for actor in case.get('SagAktør', [])][:5]
            }
            
            dashboard['cases'].append(case_data)
            
            # Track recent updates (last 24 hours)
            if case['opdateringsdato']:
                update_date = datetime.fromisoformat(case['opdateringsdato'].replace('Z', '+00:00'))
                if (datetime.now(update_date.tzinfo) - update_date).total_seconds() < 86400:
                    dashboard['recent_updates'].append(case_data)
        
        return dashboard
    
    def generate_progress_report(self):
        """Generate detailed progress report"""
        dashboard = self.get_dashboard_data()
        
        report = f"""
Parliamentary Case Tracking Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERVIEW:
- Total Cases Tracked: {dashboard['total_cases']}
- Recent Updates (24h): {len(dashboard['recent_updates'])}

STATUS BREAKDOWN:
"""
        
        for status, count in dashboard['by_status'].items():
            percentage = (count / dashboard['total_cases']) * 100
            report += f"- {status}: {count} cases ({percentage:.1f}%)\n"
        
        report += "\nRECENT ACTIVITY:\n"
        for case in dashboard['recent_updates']:
            report += f"- Case {case['id']}: {case['title']}\n"
            report += f"  Status: {case['status']}\n"
            report += f"  Updated: {case['last_updated'][:19]}\n\n"
        
        return report

# Usage example
dashboard = ParliamentaryDashboard()
dashboard.add_cases_to_track([12345, 12346, 12347])
print(dashboard.generate_progress_report())
```

### Webhook Integration

Set up automated notifications for status changes:

```python
import json
from datetime import datetime
import requests

class ProgressNotifier:
    def __init__(self, webhook_url=None):
        self.webhook_url = webhook_url
        self.last_known_states = {}
        
    def check_and_notify(self, case_ids):
        """Check for changes and send notifications"""
        current_states = self.get_current_states(case_ids)
        changes = []
        
        for case_id, state in current_states.items():
            if case_id in self.last_known_states:
                old_state = self.last_known_states[case_id]
                if old_state['status'] != state['status']:
                    changes.append({
                        'case_id': case_id,
                        'title': state['title'],
                        'old_status': old_state['status'],
                        'new_status': state['status'],
                        'change_time': state['updated']
                    })
            
            self.last_known_states[case_id] = state
        
        if changes and self.webhook_url:
            self.send_notifications(changes)
        
        return changes
    
    def get_current_states(self, case_ids):
        """Get current status for all cases"""
        case_filter = " or ".join([f"id eq {cid}" for cid in case_ids])
        
        url = "https://oda.ft.dk/api/Sag"
        params = {
            "$filter": case_filter,
            "$expand": "Sagsstatus",
            "$select": "id,titel,statusid,opdateringsdato"
        }
        
        response = requests.get(url, params=params)
        cases = response.json().get('value', [])
        
        states = {}
        for case in cases:
            states[case['id']] = {
                'title': case['titel'],
                'status': case.get('Sagsstatus', {}).get('status', 'Unknown'),
                'updated': case['opdateringsdato']
            }
        
        return states
    
    def send_notifications(self, changes):
        """Send webhook notifications for changes"""
        payload = {
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
            'summary': f"{len(changes)} case(s) changed status"
        }
        
        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"Failed to send notification: {e}")

# Usage
notifier = ProgressNotifier(webhook_url="https://hooks.slack.com/your-webhook")
changes = notifier.check_and_notify([12345, 12346, 12347])
```

## Performance Optimization for Bulk Tracking

### Efficient Bulk Queries

Optimize API usage when tracking many cases:

```python
class OptimizedCaseTracker:
    def __init__(self):
        self.base_url = "https://oda.ft.dk/api"
        self.batch_size = 50  # API limit is 100, use 50 for safety
        
    def batch_case_queries(self, case_ids):
        """Process cases in optimized batches"""
        results = []
        
        for i in range(0, len(case_ids), self.batch_size):
            batch = case_ids[i:i + self.batch_size]
            batch_filter = " or ".join([f"id eq {cid}" for cid in batch])
            
            url = f"{self.base_url}/Sag"
            params = {
                "$filter": batch_filter,
                "$expand": "Sagsstatus",
                "$select": "id,titel,statusid,opdateringsdato",
                "$top": str(self.batch_size)
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                batch_results = response.json().get('value', [])
                results.extend(batch_results)
                
                # Brief pause to avoid rate limiting
                time.sleep(0.1)
                
            except requests.exceptions.RequestException as e:
                print(f"Batch {i//self.batch_size + 1} failed: {e}")
                continue
        
        return results
    
    def get_bulk_status_summary(self, case_ids):
        """Get status summary for large numbers of cases"""
        cases = self.batch_case_queries(case_ids)
        
        summary = {
            'total_processed': len(cases),
            'by_status': {},
            'last_updated': None,
            'update_distribution': {}
        }
        
        latest_update = None
        for case in cases:
            # Status counting
            status = case.get('Sagsstatus', {}).get('status', 'Unknown')
            summary['by_status'][status] = summary['by_status'].get(status, 0) + 1
            
            # Track latest update
            if case['opdateringsdato']:
                update_date = datetime.fromisoformat(case['opdateringsdato'].replace('Z', '+00:00'))
                if not latest_update or update_date > latest_update:
                    latest_update = update_date
                
                # Update distribution by day
                day_key = update_date.strftime('%Y-%m-%d')
                summary['update_distribution'][day_key] = summary['update_distribution'].get(day_key, 0) + 1
        
        summary['last_updated'] = latest_update.isoformat() if latest_update else None
        
        return summary

# Track 500 cases efficiently
tracker = OptimizedCaseTracker()
large_case_list = list(range(10000, 10500))  # Example case IDs
summary = tracker.get_bulk_status_summary(large_case_list)
print(f"Tracked {summary['total_processed']} cases")
print("Status distribution:", summary['by_status'])
```

### Caching and Incremental Updates

Implement efficient caching for repeated queries:

```python
import sqlite3
import json

class CachedProgressTracker:
    def __init__(self, db_path="case_cache.db"):
        self.db_path = db_path
        self.init_database()
        
    def init_database(self):
        """Initialize SQLite cache database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS case_cache (
                case_id INTEGER PRIMARY KEY,
                title TEXT,
                status TEXT,
                last_updated TEXT,
                data_json TEXT,
                cache_time TEXT
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_cached_cases(self, case_ids, max_age_hours=1):
        """Get cases from cache if recent enough"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        cutoff_str = cutoff.isoformat()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ",".join(["?" for _ in case_ids])
        cursor.execute(f"""
            SELECT case_id, data_json, cache_time 
            FROM case_cache 
            WHERE case_id IN ({placeholders}) 
            AND cache_time > ?
        """, case_ids + [cutoff_str])
        
        cached = {}
        for row in cursor.fetchall():
            case_id, data_json, cache_time = row
            cached[case_id] = json.loads(data_json)
        
        conn.close()
        
        # Find cases that need fresh data
        needs_update = [cid for cid in case_ids if cid not in cached]
        
        return cached, needs_update
    
    def update_cache(self, cases_data):
        """Update cache with fresh case data"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cache_time = datetime.now().isoformat()
        
        for case in cases_data:
            cursor.execute("""
                INSERT OR REPLACE INTO case_cache 
                (case_id, title, status, last_updated, data_json, cache_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                case['id'],
                case.get('titel', ''),
                case.get('Sagsstatus', {}).get('status', ''),
                case.get('opdateringsdato', ''),
                json.dumps(case),
                cache_time
            ))
        
        conn.commit()
        conn.close()
    
    def get_cases_with_cache(self, case_ids):
        """Get cases using cache optimization"""
        cached_data, needs_update = self.get_cached_cases(case_ids)
        
        all_cases = list(cached_data.values())
        
        if needs_update:
            # Fetch only uncached cases
            tracker = OptimizedCaseTracker()
            fresh_data = tracker.batch_case_queries(needs_update)
            self.update_cache(fresh_data)
            all_cases.extend(fresh_data)
        
        return all_cases

# Usage with caching
cached_tracker = CachedProgressTracker()
cases = cached_tracker.get_cases_with_cache([12345, 12346, 12347])
```

## Advanced Analytics and Reporting

### Progress Velocity Analysis

Analyze how quickly cases move through the system:

```python
def analyze_case_velocity(case_ids, lookback_days=90):
    """Analyze case progression speed"""
    cutoff_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
    
    case_filter = " or ".join([f"id eq {cid}" for cid in case_ids])
    
    # Get cases with their steps
    url = "https://oda.ft.dk/api/Sag"
    params = {
        "$filter": f"({case_filter}) and opdateringsdato gt datetime'{cutoff_date}'",
        "$expand": "Sagstrin",
        "$select": "id,titel,fremsatdato,opdateringsdato"
    }
    
    response = requests.get(url, params=params)
    cases = response.json().get('value', [])
    
    velocity_stats = {
        'total_cases': len(cases),
        'avg_days_active': 0,
        'fastest_progression': None,
        'slowest_progression': None,
        'step_velocity': {}
    }
    
    days_active_list = []
    
    for case in cases:
        if case.get('fremsatdato') and case.get('opdateringsdato'):
            start = datetime.fromisoformat(case['fremsatdato'].replace('Z', '+00:00'))
            last_update = datetime.fromisoformat(case['opdateringsdato'].replace('Z', '+00:00'))
            days_active = (last_update - start).days
            
            days_active_list.append(days_active)
            
            case_info = {
                'id': case['id'],
                'title': case['titel'][:50] + '...',
                'days': days_active
            }
            
            if not velocity_stats['fastest_progression'] or days_active < velocity_stats['fastest_progression']['days']:
                velocity_stats['fastest_progression'] = case_info
                
            if not velocity_stats['slowest_progression'] or days_active > velocity_stats['slowest_progression']['days']:
                velocity_stats['slowest_progression'] = case_info
    
    if days_active_list:
        velocity_stats['avg_days_active'] = sum(days_active_list) / len(days_active_list)
        velocity_stats['median_days_active'] = sorted(days_active_list)[len(days_active_list) // 2]
    
    return velocity_stats

# Analyze velocity for recent cases
recent_cases = list(range(150000, 150100))  # Recent case ID range
velocity = analyze_case_velocity(recent_cases)
print(f"Average case duration: {velocity['avg_days_active']:.1f} days")
```

## Best Practices

### Error Handling and Resilience

```python
import logging
from functools import wraps

def retry_on_failure(max_retries=3, delay=1):
    """Decorator for retrying failed API calls"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        logging.error(f"Final attempt failed for {func.__name__}: {e}")
                        raise
                    logging.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    time.sleep(delay * (attempt + 1))
            return None
        return wrapper
    return decorator

@retry_on_failure(max_retries=3, delay=2)
def robust_case_query(case_ids):
    """Robust case querying with automatic retries"""
    case_filter = " or ".join([f"id eq {cid}" for cid in case_ids[:50]])  # Limit batch size
    
    url = "https://oda.ft.dk/api/Sag"
    params = {
        "$filter": case_filter,
        "$expand": "Sagsstatus",
        "$select": "id,titel,statusid,opdateringsdato"
    }
    
    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()
    return response.json().get('value', [])
```

### Rate Limiting Compliance

```python
class RateLimitedTracker:
    def __init__(self, requests_per_minute=30):
        self.requests_per_minute = requests_per_minute
        self.request_times = []
        
    def wait_if_needed(self):
        """Ensure we don't exceed rate limits"""
        now = time.time()
        
        # Remove requests older than 1 minute
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= self.requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            if sleep_time > 0:
                time.sleep(sleep_time)
                # Clean up old requests after waiting
                self.request_times = [t for t in self.request_times if time.time() - t < 60]
        
        self.request_times.append(time.time())
    
    def make_request(self, url, params):
        """Make rate-limited request"""
        self.wait_if_needed()
        response = requests.get(url, params=params)
        return response
```

## Summary

This guide provides comprehensive tools for tracking legislative case progress through the Danish Parliament system. Key capabilities include:

- **Real-time status monitoring** with 68 distinct status types
- **Case step tracking** through procedural stages
- **Automated progress notifications** via webhooks
- **Bulk tracking optimization** for monitoring large case sets
- **Document publication milestones** tracking
- **Voting schedule and outcome monitoring**
- **Performance optimization** with caching and rate limiting
- **Progress velocity analysis** for understanding system dynamics

The Danish Parliamentary API's detailed status system enables precise tracking of legislative progress from initial proposal through final adoption or rejection, making it possible to build sophisticated monitoring and analysis systems for parliamentary activity.