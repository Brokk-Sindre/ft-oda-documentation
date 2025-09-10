# Change Detection in the Danish Parliament API

Detecting changes in the Danish Parliamentary OData API enables real-time monitoring of legislative activity, political developments, and institutional updates. This comprehensive guide covers strategies, techniques, and implementation patterns for building robust change detection systems.

## Overview

The Danish Parliament API provides several mechanisms for change detection:

- **Timestamp-based detection** using `opdateringsdato` fields
- **Incremental synchronization** through ordered queries
- **Entity-specific monitoring** for targeted change tracking
- **Batch vs real-time approaches** for different use cases

## Change Detection Fundamentals

### Core Timestamp Fields

All major entities include standardized timestamp fields for change detection:

| Field | Type | Purpose | Availability |
|-------|------|---------|--------------|
| `opdateringsdato` | DateTime | Last modification timestamp | All entities |
| `dato` | DateTime | Creation/event date | Most entities |
| `frigivelsesdato` | DateTime | Release/publication date | Documents |
| `afgørelsesdato` | DateTime | Decision date | Cases |

### Entity Coverage

Change detection is available across all major entity types:

- **Sag** (Cases) - 96,538+ legislative matters
- **Aktør** (Actors) - 18,139+ political actors
- **Dokument** (Documents) - Hundreds of thousands of documents
- **Afstemning** (Voting) - Voting sessions and results
- **Stemme** (Votes) - Individual vote records

## Timestamp-Based Change Detection

### Basic Change Detection Query

Monitor recent changes across any entity using the `opdateringsdato` field:

```bash
# Get all cases updated since yesterday
curl "https://oda.ft.dk/api/Sag?%24filter=opdateringsdato%20gt%20datetime'2025-09-08T00:00:00'&%24orderby=opdateringsdato%20desc&%24top=100"

# Get actors updated in the last hour
curl "https://oda.ft.dk/api/Akt%C3%B8r?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T16:00:00'&%24orderby=opdateringsdato%20desc"

# Monitor document updates
curl "https://oda.ft.dk/api/Dokument?%24filter=opdateringsdato%20gt%20datetime'2025-09-09T12:00:00'&%24orderby=opdateringsdato%20desc&%24top=50"
```

### Python Implementation - Basic Change Detection

```python
import requests
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional

class ParliamentChangeDetector:
    """
    Basic change detection for Danish Parliament API
    """
    
    def __init__(self, base_url: str = "https://oda.ft.dk/api"):
        self.base_url = base_url
        self.last_check_times = {}
        
    def get_changes_since(self, entity: str, since: datetime, 
                         fields: Optional[str] = None, 
                         expand: Optional[str] = None) -> List[Dict]:
        """
        Get all changes to an entity since a specific timestamp
        
        Args:
            entity: Entity name (Sag, Aktør, Dokument, etc.)
            since: Datetime to check changes since
            fields: Optional comma-separated list of fields to select
            expand: Optional related entities to expand
            
        Returns:
            List of changed entities
        """
        since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "$filter": f"opdateringsdato gt datetime'{since_iso}'",
            "$orderby": "opdateringsdato desc",
            "$top": "100"
        }
        
        if fields:
            params["$select"] = fields
        if expand:
            params["$expand"] = expand
            
        url = f"{self.base_url}/{entity}"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('value', [])
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def monitor_entity_changes(self, entity: str, 
                              poll_interval: int = 300,
                              fields: Optional[str] = None) -> None:
        """
        Continuously monitor changes to an entity
        
        Args:
            entity: Entity to monitor
            poll_interval: Seconds between polls (default 5 minutes)
            fields: Optional fields to select
        """
        if entity not in self.last_check_times:
            # Start from 1 hour ago for initial run
            self.last_check_times[entity] = datetime.now() - timedelta(hours=1)
        
        while True:
            try:
                last_check = self.last_check_times[entity]
                changes = self.get_changes_since(entity, last_check, fields)
                
                if changes:
                    print(f"\n=== {len(changes)} changes detected in {entity} ===")
                    for change in changes:
                        update_time = change.get('opdateringsdato')
                        entity_id = change.get('id')
                        title = change.get('titel', change.get('navn', 'N/A'))
                        print(f"ID: {entity_id} | Updated: {update_time} | Title: {title[:80]}")
                    
                    # Update last check time to most recent change
                    latest_update = datetime.fromisoformat(
                        changes[0]['opdateringsdato'].replace('Z', '+00:00')
                    )
                    self.last_check_times[entity] = latest_update
                else:
                    print(f"No changes detected in {entity} since {last_check}")
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"Error monitoring {entity}: {e}")
                time.sleep(poll_interval)

# Usage example
detector = ParliamentChangeDetector()

# Monitor case changes with essential fields only
detector.monitor_entity_changes(
    entity="Sag",
    poll_interval=600,  # Check every 10 minutes
    fields="id,titel,opdateringsdato,statusid,typeid"
)
```

### JavaScript Implementation - Browser/Node.js

```javascript
class ParliamentChangeDetector {
    constructor(baseUrl = 'https://oda.ft.dk/api') {
        this.baseUrl = baseUrl;
        this.lastCheckTimes = {};
    }
    
    /**
     * Get changes since a specific timestamp
     */
    async getChangesSince(entity, since, options = {}) {
        const sinceISO = since.toISOString().slice(0, 19);
        
        const params = new URLSearchParams({
            '$filter': `opdateringsdato gt datetime'${sinceISO}'`,
            '$orderby': 'opdateringsdato desc',
            '$top': '100'
        });
        
        if (options.fields) params.set('$select', options.fields);
        if (options.expand) params.set('$expand', options.expand);
        
        const url = `${this.baseUrl}/${entity}?${params}`;
        
        try {
            const response = await fetch(url);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            return data.value || [];
        } catch (error) {
            console.error('API Error:', error);
            throw error;
        }
    }
    
    /**
     * Monitor entity changes with callback
     */
    async startMonitoring(entity, callback, options = {}) {
        const pollInterval = options.pollInterval || 300000; // 5 minutes
        
        if (!this.lastCheckTimes[entity]) {
            // Start from 1 hour ago
            this.lastCheckTimes[entity] = new Date(Date.now() - 3600000);
        }
        
        const poll = async () => {
            try {
                const lastCheck = this.lastCheckTimes[entity];
                const changes = await this.getChangesSince(entity, lastCheck, options);
                
                if (changes.length > 0) {
                    await callback(changes, entity);
                    
                    // Update last check time to most recent change
                    const latestUpdate = new Date(changes[0].opdateringsdato);
                    this.lastCheckTimes[entity] = latestUpdate;
                }
            } catch (error) {
                console.error(`Error monitoring ${entity}:`, error);
            }
            
            setTimeout(poll, pollInterval);
        };
        
        await poll();
    }
}

// Usage example
const detector = new ParliamentChangeDetector();

// Monitor cases with callback
detector.startMonitoring('Sag', (changes, entity) => {
    console.log(`${changes.length} changes detected in ${entity}`);
    changes.forEach(change => {
        console.log(`ID: ${change.id}, Updated: ${change.opdateringsdato}, Title: ${change.titel?.slice(0, 80)}`);
    });
}, {
    pollInterval: 600000, // 10 minutes
    fields: 'id,titel,opdateringsdato,statusid'
});
```

## Entity-Specific Change Monitoring

### Legislative Case Monitoring

Track changes to parliamentary cases with specific focus on status transitions:

```python
class CaseChangeDetector(ParliamentChangeDetector):
    """
    Specialized change detection for parliamentary cases
    """
    
    def __init__(self):
        super().__init__()
        self.case_status_cache = {}
    
    def get_case_changes_with_context(self, since: datetime) -> List[Dict]:
        """
        Get case changes with expanded context information
        """
        return self.get_changes_since(
            entity="Sag",
            since=since,
            fields="id,titel,opdateringsdato,statusid,typeid,offentlighedskode",
            expand="Sagsstatus,Sagstype"
        )
    
    def detect_status_changes(self, since: datetime) -> List[Dict]:
        """
        Detect cases that have changed status
        """
        changes = self.get_case_changes_with_context(since)
        status_changes = []
        
        for case in changes:
            case_id = case['id']
            current_status = case.get('statusid')
            
            if case_id in self.case_status_cache:
                old_status = self.case_status_cache[case_id]
                if old_status != current_status:
                    status_changes.append({
                        'case_id': case_id,
                        'title': case.get('titel'),
                        'old_status': old_status,
                        'new_status': current_status,
                        'status_name': case.get('Sagsstatus', {}).get('status'),
                        'updated': case.get('opdateringsdato')
                    })
            
            # Update cache
            self.case_status_cache[case_id] = current_status
        
        return status_changes
    
    def monitor_high_priority_cases(self, case_ids: List[int]) -> List[Dict]:
        """
        Monitor specific high-priority cases for any changes
        """
        id_filter = " or ".join([f"id eq {case_id}" for case_id in case_ids])
        
        params = {
            "$filter": f"({id_filter})",
            "$expand": "Sagsstatus,Sagstype",
            "$orderby": "opdateringsdato desc"
        }
        
        url = f"{self.base_url}/Sag"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('value', [])
        else:
            raise Exception(f"API Error: {response.status_code}")

# Usage
case_detector = CaseChangeDetector()

# Monitor for status changes
status_changes = case_detector.detect_status_changes(
    since=datetime.now() - timedelta(hours=24)
)

for change in status_changes:
    print(f"Case {change['case_id']} status changed from {change['old_status']} to {change['new_status']}")
    print(f"  Title: {change['title'][:100]}")
    print(f"  New Status: {change['status_name']}")
```

### Actor Change Monitoring

Track changes to political actors with focus on biographical updates and role changes:

```python
class ActorChangeDetector(ParliamentChangeDetector):
    """
    Specialized monitoring for political actors
    """
    
    def get_politician_changes(self, since: datetime) -> List[Dict]:
        """
        Monitor changes to politicians specifically (typeid = 5)
        """
        since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "$filter": f"typeid eq 5 and opdateringsdato gt datetime'{since_iso}'",
            "$select": "id,navn,fornavn,efternavn,gruppenavnkort,opdateringsdato,startdato,slutdato",
            "$expand": "Aktørtype",
            "$orderby": "opdateringsdato desc"
        }
        
        url = f"{self.base_url}/Aktør"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('value', [])
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def detect_new_politicians(self, since: datetime) -> List[Dict]:
        """
        Detect newly added politicians
        """
        politicians = self.get_politician_changes(since)
        
        # Politicians where start date is recent and matches update date
        new_politicians = []
        for politician in politicians:
            start_date = politician.get('startdato')
            update_date = politician.get('opdateringsdato')
            
            if start_date and update_date:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                update_dt = datetime.fromisoformat(update_date.replace('Z', '+00:00'))
                
                # If started recently and updated around the same time
                if abs((start_dt - update_dt).days) <= 1 and start_dt >= since:
                    new_politicians.append(politician)
        
        return new_politicians
    
    def detect_departing_politicians(self, since: datetime) -> List[Dict]:
        """
        Detect politicians who have recently ended their terms
        """
        politicians = self.get_politician_changes(since)
        
        departing = []
        for politician in politicians:
            end_date = politician.get('slutdato')
            if end_date:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                if end_dt >= since:
                    departing.append(politician)
        
        return departing

# Usage
actor_detector = ActorChangeDetector()

# Monitor new politicians
new_politicians = actor_detector.detect_new_politicians(
    since=datetime.now() - timedelta(days=7)
)

for politician in new_politicians:
    print(f"New politician: {politician['navn']} ({politician['gruppenavnkort']})")
    print(f"  Started: {politician['startdato']}")
```

### Document Change Monitoring

Track new documents and document updates with content analysis:

```python
class DocumentChangeDetector(ParliamentChangeDetector):
    """
    Specialized monitoring for parliamentary documents
    """
    
    def get_recent_documents(self, since: datetime, doc_type: Optional[int] = None) -> List[Dict]:
        """
        Get recently published or updated documents
        """
        since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
        
        filter_parts = [f"opdateringsdato gt datetime'{since_iso}'"]
        if doc_type:
            filter_parts.append(f"typeid eq {doc_type}")
        
        params = {
            "$filter": " and ".join(filter_parts),
            "$select": "id,titel,dato,frigivelsesdato,opdateringsdato,typeid,offentlighedskode",
            "$expand": "Dokumenttype",
            "$orderby": "opdateringsdato desc",
            "$top": "50"
        }
        
        url = f"{self.base_url}/Dokument"
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data.get('value', [])
        else:
            raise Exception(f"API Error: {response.status_code}")
    
    def detect_new_publications(self, since: datetime) -> List[Dict]:
        """
        Detect documents that were newly published (frigivelsesdato recent)
        """
        documents = self.get_recent_documents(since)
        
        new_publications = []
        for doc in documents:
            release_date = doc.get('frigivelsesdato')
            if release_date:
                release_dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                if release_dt >= since:
                    new_publications.append(doc)
        
        return new_publications
    
    def monitor_document_types(self, doc_types: List[int], since: datetime) -> Dict[int, List[Dict]]:
        """
        Monitor specific document types for changes
        
        Args:
            doc_types: List of document type IDs to monitor
            since: Check for changes since this time
            
        Returns:
            Dictionary mapping document type ID to list of changed documents
        """
        results = {}
        
        for doc_type in doc_types:
            documents = self.get_recent_documents(since, doc_type)
            if documents:
                results[doc_type] = documents
        
        return results

# Document type constants
DOC_TYPES = {
    'INQUIRIES': 5,
    'MINISTERIAL_STATEMENTS': 3,
    'EU_NOTES': 6,
    'REPORTS': 1,
    'MEMOS': 10
}

# Usage
doc_detector = DocumentChangeDetector()

# Monitor specific document types
doc_changes = doc_detector.monitor_document_types(
    doc_types=[DOC_TYPES['INQUIRIES'], DOC_TYPES['EU_NOTES']],
    since=datetime.now() - timedelta(hours=12)
)

for doc_type, documents in doc_changes.items():
    type_name = [k for k, v in DOC_TYPES.items() if v == doc_type][0]
    print(f"\n{len(documents)} new {type_name}:")
    for doc in documents[:5]:  # Show first 5
        print(f"  {doc['titel'][:80]}... (Updated: {doc['opdateringsdato']})")
```

## Incremental Data Synchronization

### Efficient Incremental Sync Strategy

```python
class IncrementalSyncManager:
    """
    Manage incremental synchronization of parliamentary data
    """
    
    def __init__(self, storage_handler):
        self.api = ParliamentChangeDetector()
        self.storage = storage_handler
        self.sync_state = self.load_sync_state()
    
    def load_sync_state(self) -> Dict:
        """Load last synchronization timestamps"""
        return self.storage.get_sync_state() or {}
    
    def save_sync_state(self):
        """Save current synchronization state"""
        self.storage.save_sync_state(self.sync_state)
    
    def sync_entity(self, entity: str, batch_size: int = 100) -> Dict:
        """
        Perform incremental sync for a specific entity
        
        Returns:
            Summary of sync operation
        """
        last_sync = self.sync_state.get(entity)
        if not last_sync:
            # First sync - start from 7 days ago
            last_sync = datetime.now() - timedelta(days=7)
        else:
            last_sync = datetime.fromisoformat(last_sync)
        
        print(f"Starting incremental sync for {entity} from {last_sync}")
        
        changes = self.api.get_changes_since(entity, last_sync)
        
        if not changes:
            return {'entity': entity, 'processed': 0, 'errors': 0}
        
        # Process in batches
        processed = 0
        errors = 0
        latest_update = last_sync
        
        for i in range(0, len(changes), batch_size):
            batch = changes[i:i + batch_size]
            
            try:
                self.storage.upsert_records(entity, batch)
                processed += len(batch)
                
                # Track latest update time
                for record in batch:
                    update_time = datetime.fromisoformat(
                        record['opdateringsdato'].replace('Z', '+00:00')
                    )
                    if update_time > latest_update:
                        latest_update = update_time
                
            except Exception as e:
                print(f"Error processing batch for {entity}: {e}")
                errors += len(batch)
        
        # Update sync state
        self.sync_state[entity] = latest_update.isoformat()
        self.save_sync_state()
        
        return {
            'entity': entity,
            'processed': processed,
            'errors': errors,
            'last_sync': latest_update.isoformat()
        }
    
    def full_incremental_sync(self, entities: List[str]) -> Dict:
        """
        Perform incremental sync across multiple entities
        """
        results = {}
        
        for entity in entities:
            try:
                result = self.sync_entity(entity)
                results[entity] = result
                print(f" {entity}: {result['processed']} records processed")
                
                # Rate limiting - small delay between entities
                time.sleep(1)
                
            except Exception as e:
                print(f"L {entity}: Sync failed - {e}")
                results[entity] = {'error': str(e)}
        
        return results

# Storage handler example (implement based on your database)
class DatabaseStorageHandler:
    def get_sync_state(self):
        # Load from database
        pass
    
    def save_sync_state(self, state):
        # Save to database
        pass
    
    def upsert_records(self, entity, records):
        # Insert or update records in database
        pass

# Usage
storage = DatabaseStorageHandler()
sync_manager = IncrementalSyncManager(storage)

# Sync critical entities
entities_to_sync = ['Sag', 'Aktør', 'Dokument', 'Afstemning']
results = sync_manager.full_incremental_sync(entities_to_sync)
```

## Change Event Classification and Priority Systems

### Change Event Classification

```python
from enum import Enum
from typing import NamedTuple

class ChangeType(Enum):
    CREATE = "create"
    UPDATE = "update"
    STATUS_CHANGE = "status_change"
    CONTENT_CHANGE = "content_change"
    RELATIONSHIP_CHANGE = "relationship_change"

class ChangePriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

class ChangeEvent(NamedTuple):
    entity_type: str
    entity_id: int
    change_type: ChangeType
    priority: ChangePriority
    timestamp: datetime
    details: Dict
    metadata: Dict

class ChangeClassifier:
    """
    Classify and prioritize change events
    """
    
    def __init__(self):
        self.priority_rules = {
            # High priority patterns
            'voting_results': {
                'entity': 'Afstemning',
                'priority': ChangePriority.CRITICAL,
                'conditions': ['afstemningstype']
            },
            'case_decisions': {
                'entity': 'Sag',
                'priority': ChangePriority.HIGH,
                'conditions': ['afgørelsesdato', 'afgørelse']
            },
            'new_legislation': {
                'entity': 'Sag',
                'priority': ChangePriority.HIGH,
                'conditions': ['typeid', 'titel'],
                'keywords': ['lov', 'forslag']
            },
            'minister_statements': {
                'entity': 'Dokument',
                'priority': ChangePriority.HIGH,
                'conditions': ['typeid == 3']  # Ministerial statements
            }
        }
    
    def classify_change(self, entity_type: str, old_record: Dict, 
                       new_record: Dict) -> ChangeEvent:
        """
        Classify a change event based on before/after comparison
        """
        entity_id = new_record.get('id')
        timestamp = datetime.fromisoformat(
            new_record.get('opdateringsdato', '').replace('Z', '+00:00')
        )
        
        # Determine change type
        if old_record is None:
            change_type = ChangeType.CREATE
        else:
            change_type = self._determine_change_type(old_record, new_record)
        
        # Determine priority
        priority = self._determine_priority(entity_type, old_record, new_record)
        
        # Extract change details
        details = self._extract_change_details(old_record, new_record)
        
        # Metadata
        metadata = {
            'fields_changed': list(details.keys()) if old_record else ['all'],
            'source': 'api_monitoring'
        }
        
        return ChangeEvent(
            entity_type=entity_type,
            entity_id=entity_id,
            change_type=change_type,
            priority=priority,
            timestamp=timestamp,
            details=details,
            metadata=metadata
        )
    
    def _determine_change_type(self, old_record: Dict, new_record: Dict) -> ChangeType:
        """Determine the type of change that occurred"""
        
        # Check for status changes in cases
        if 'statusid' in old_record and 'statusid' in new_record:
            if old_record['statusid'] != new_record['statusid']:
                return ChangeType.STATUS_CHANGE
        
        # Check for content changes
        content_fields = ['titel', 'resume', 'afgørelse', 'begrundelse']
        for field in content_fields:
            if (field in old_record and field in new_record and 
                old_record[field] != new_record[field]):
                return ChangeType.CONTENT_CHANGE
        
        return ChangeType.UPDATE
    
    def _determine_priority(self, entity_type: str, old_record: Dict, 
                          new_record: Dict) -> ChangePriority:
        """Determine priority based on change rules"""
        
        # Apply priority rules
        for rule_name, rule in self.priority_rules.items():
            if rule['entity'] == entity_type:
                if self._matches_rule(rule, new_record):
                    return rule['priority']
        
        # Default priorities by entity type
        entity_priorities = {
            'Afstemning': ChangePriority.HIGH,
            'Sag': ChangePriority.MEDIUM,
            'Dokument': ChangePriority.MEDIUM,
            'Aktør': ChangePriority.LOW
        }
        
        return entity_priorities.get(entity_type, ChangePriority.LOW)
    
    def _matches_rule(self, rule: Dict, record: Dict) -> bool:
        """Check if a record matches a priority rule"""
        conditions = rule.get('conditions', [])
        keywords = rule.get('keywords', [])
        
        # Check field conditions
        for condition in conditions:
            if '==' in condition:
                field, value = condition.split('==')
                field = field.strip()
                value = value.strip()
                if str(record.get(field)) != value:
                    return False
            else:
                # Field must exist
                if condition not in record:
                    return False
        
        # Check keyword conditions
        if keywords:
            text_fields = ['titel', 'navn', 'resume']
            text_content = ' '.join([
                str(record.get(field, '')) for field in text_fields
            ]).lower()
            
            if not any(keyword.lower() in text_content for keyword in keywords):
                return False
        
        return True
    
    def _extract_change_details(self, old_record: Dict, new_record: Dict) -> Dict:
        """Extract details of what changed"""
        if old_record is None:
            return {'action': 'created', 'new_values': new_record}
        
        changes = {}
        for key, new_value in new_record.items():
            old_value = old_record.get(key)
            if old_value != new_value:
                changes[key] = {
                    'old': old_value,
                    'new': new_value
                }
        
        return changes

# Usage
classifier = ChangeClassifier()

# Example classification
old_case = {'id': 123, 'statusid': 5, 'titel': 'Klimalov'}
new_case = {'id': 123, 'statusid': 11, 'titel': 'Klimalov', 'opdateringsdato': '2025-09-09T15:30:00'}

change_event = classifier.classify_change('Sag', old_case, new_case)

print(f"Change Type: {change_event.change_type}")
print(f"Priority: {change_event.priority}")
print(f"Details: {change_event.details}")
```

### Priority-Based Processing Queue

```python
import heapq
from queue import Queue
from threading import Thread
import json

class PriorityChangeProcessor:
    """
    Process change events based on priority
    """
    
    def __init__(self, num_workers: int = 3):
        self.priority_queue = []
        self.workers = []
        self.running = False
        self.handlers = {}
        self.num_workers = num_workers
    
    def register_handler(self, priority: ChangePriority, handler_func):
        """Register a handler function for a specific priority"""
        self.handlers[priority] = handler_func
    
    def add_change_event(self, event: ChangeEvent):
        """Add a change event to the processing queue"""
        # Priority queue uses min-heap, so we negate priority for max priority first
        priority_value = -event.priority.value
        heapq.heappush(self.priority_queue, (priority_value, event.timestamp, event))
    
    def start_processing(self):
        """Start worker threads to process changes"""
        self.running = True
        
        for i in range(self.num_workers):
            worker = Thread(target=self._worker_loop, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
    
    def stop_processing(self):
        """Stop processing"""
        self.running = False
    
    def _worker_loop(self, worker_id: int):
        """Worker thread loop"""
        while self.running:
            if self.priority_queue:
                try:
                    priority_value, timestamp, event = heapq.heappop(self.priority_queue)
                    self._process_event(event, worker_id)
                except IndexError:
                    # Queue empty
                    time.sleep(0.1)
            else:
                time.sleep(0.1)
    
    def _process_event(self, event: ChangeEvent, worker_id: int):
        """Process a single change event"""
        try:
            handler = self.handlers.get(event.priority)
            if handler:
                print(f"Worker {worker_id}: Processing {event.priority.name} priority event - {event.entity_type}:{event.entity_id}")
                handler(event)
            else:
                print(f"No handler for priority {event.priority.name}")
                
        except Exception as e:
            print(f"Error processing event {event.entity_id}: {e}")

# Example handlers
def handle_critical_changes(event: ChangeEvent):
    """Handle critical priority changes - immediate alerts"""
    print(f"=¨ CRITICAL: {event.entity_type} {event.entity_id}")
    print(f"   Change: {event.change_type}")
    print(f"   Time: {event.timestamp}")
    # Send immediate notifications, alerts, etc.

def handle_high_priority_changes(event: ChangeEvent):
    """Handle high priority changes - fast processing"""
    print(f"  HIGH: {event.entity_type} {event.entity_id}")
    # Update caches, trigger workflows, etc.

def handle_medium_priority_changes(event: ChangeEvent):
    """Handle medium priority changes - regular processing"""
    print(f"9 MEDIUM: {event.entity_type} {event.entity_id}")
    # Regular database updates, batch processing, etc.

def handle_low_priority_changes(event: ChangeEvent):
    """Handle low priority changes - batch processing"""
    print(f"=Ý LOW: {event.entity_type} {event.entity_id}")
    # Bulk processing, analytics, etc.

# Setup processor
processor = PriorityChangeProcessor(num_workers=3)
processor.register_handler(ChangePriority.CRITICAL, handle_critical_changes)
processor.register_handler(ChangePriority.HIGH, handle_high_priority_changes)
processor.register_handler(ChangePriority.MEDIUM, handle_medium_priority_changes)
processor.register_handler(ChangePriority.LOW, handle_low_priority_changes)

processor.start_processing()

# Add events (would be called from your change detection system)
# processor.add_change_event(change_event)
```

## Real-Time vs Batch Change Detection Trade-offs

### Real-Time Monitoring (High Frequency)

**Advantages:**
- Immediate detection of changes
- Real-time alerts and notifications
- Up-to-the-minute data freshness
- Suitable for critical monitoring

**Disadvantages:**
- Higher API request volume
- Increased server load
- More complex error handling
- Potential rate limiting issues

**Recommended for:**
- Voting session monitoring
- Critical case status changes
- Breaking news alerts
- Time-sensitive applications

```python
# Real-time monitoring example (1-5 minute intervals)
class RealTimeMonitor(ParliamentChangeDetector):
    def __init__(self, poll_interval: int = 60):  # 1 minute
        super().__init__()
        self.poll_interval = poll_interval
        self.alert_handlers = []
    
    def add_alert_handler(self, handler):
        self.alert_handlers.append(handler)
    
    def start_real_time_monitoring(self, entities: List[str]):
        """Start real-time monitoring with immediate alerts"""
        for entity in entities:
            Thread(target=self._monitor_entity_real_time, 
                  args=(entity,), daemon=True).start()
    
    def _monitor_entity_real_time(self, entity: str):
        last_check = datetime.now() - timedelta(minutes=5)
        
        while True:
            try:
                changes = self.get_changes_since(entity, last_check)
                
                if changes:
                    # Immediate processing
                    for change in changes:
                        for handler in self.alert_handlers:
                            handler(entity, change)
                    
                    last_check = datetime.fromisoformat(
                        changes[0]['opdateringsdato'].replace('Z', '+00:00')
                    )
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                print(f"Real-time monitoring error for {entity}: {e}")
                time.sleep(self.poll_interval)

# Real-time alert handler
def real_time_alert_handler(entity: str, change: Dict):
    print(f"=4 REAL-TIME ALERT: {entity} {change['id']} updated at {change['opdateringsdato']}")
    # Send webhooks, push notifications, etc.
```

### Batch Processing (Lower Frequency)

**Advantages:**
- More efficient API usage
- Better resource utilization
- Reduced server load
- Easier error handling and recovery

**Disadvantages:**
- Delayed change detection
- Less responsive to urgent changes
- May miss rapid state changes

**Recommended for:**
- Historical data analysis
- Bulk synchronization
- Non-time-critical applications
- Analytics and reporting

```python
# Batch processing example (hourly/daily)
class BatchChangeProcessor(ParliamentChangeDetector):
    def __init__(self):
        super().__init__()
        self.batch_size = 1000
        self.processing_queue = []
    
    def schedule_batch_sync(self, entities: List[str], interval_hours: int = 6):
        """Schedule regular batch synchronization"""
        def batch_job():
            while True:
                start_time = datetime.now()
                print(f"Starting batch sync at {start_time}")
                
                try:
                    since = start_time - timedelta(hours=interval_hours + 1)  # Small overlap
                    
                    all_changes = {}
                    for entity in entities:
                        changes = self.get_changes_since(entity, since)
                        if changes:
                            all_changes[entity] = changes
                    
                    if all_changes:
                        self._process_batch_changes(all_changes)
                        print(f"Batch sync completed: {sum(len(changes) for changes in all_changes.values())} total changes")
                    else:
                        print("No changes detected in batch sync")
                
                except Exception as e:
                    print(f"Batch sync error: {e}")
                
                # Sleep until next interval
                time.sleep(interval_hours * 3600)
        
        batch_thread = Thread(target=batch_job, daemon=True)
        batch_thread.start()
        return batch_thread
    
    def _process_batch_changes(self, all_changes: Dict[str, List[Dict]]):
        """Process all changes in batch mode"""
        for entity, changes in all_changes.items():
            print(f"Processing {len(changes)} changes for {entity}")
            
            # Process in chunks
            for i in range(0, len(changes), self.batch_size):
                chunk = changes[i:i + self.batch_size]
                self._process_chunk(entity, chunk)
    
    def _process_chunk(self, entity: str, chunk: List[Dict]):
        """Process a chunk of changes"""
        # Bulk database operations, analytics updates, etc.
        print(f"  Processing chunk of {len(chunk)} {entity} records")
```

### Hybrid Approach

Combine real-time monitoring for critical entities with batch processing for others:

```python
class HybridChangeDetector:
    """
    Hybrid approach: real-time for critical, batch for others
    """
    
    def __init__(self):
        self.real_time_monitor = RealTimeMonitor(poll_interval=120)  # 2 minutes
        self.batch_processor = BatchChangeProcessor()
        
        # Critical entities for real-time monitoring
        self.critical_entities = ['Afstemning']  # Voting sessions
        
        # Regular entities for batch processing
        self.batch_entities = ['Aktør', 'Dokument']
        
        # Medium priority entities (moderate frequency)
        self.medium_entities = ['Sag']  # Cases - 10 minute intervals
    
    def start_hybrid_monitoring(self):
        """Start hybrid monitoring system"""
        
        # Real-time monitoring for critical entities
        self.real_time_monitor.add_alert_handler(self._critical_change_handler)
        self.real_time_monitor.start_real_time_monitoring(self.critical_entities)
        
        # Medium frequency monitoring for cases
        medium_monitor = RealTimeMonitor(poll_interval=600)  # 10 minutes
        medium_monitor.start_real_time_monitoring(self.medium_entities)
        
        # Batch processing for regular entities
        self.batch_processor.schedule_batch_sync(self.batch_entities, interval_hours=6)
        
        print("Hybrid monitoring system started")
        print(f"Real-time: {self.critical_entities}")
        print(f"Medium frequency: {self.medium_entities}")  
        print(f"Batch: {self.batch_entities}")
    
    def _critical_change_handler(self, entity: str, change: Dict):
        """Handle critical real-time changes"""
        print(f"=¨ CRITICAL CHANGE DETECTED: {entity} {change['id']}")
        # Send immediate alerts, webhooks, notifications
```

## Change History Tracking and Audit Trails

### Change History Storage

```python
import sqlite3
from typing import Optional

class ChangeHistoryTracker:
    """
    Track and store change history for audit trails
    """
    
    def __init__(self, db_path: str = "change_history.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize change history database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS change_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_type TEXT NOT NULL,
                entity_id INTEGER NOT NULL,
                change_type TEXT NOT NULL,
                change_priority TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                old_values TEXT,
                new_values TEXT,
                change_details TEXT,
                metadata TEXT,
                processed BOOLEAN DEFAULT FALSE,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_entity_timestamp 
            ON change_history(entity_type, entity_id, timestamp)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON change_history(timestamp)
        """)
        
        conn.commit()
        conn.close()
    
    def record_change(self, event: ChangeEvent, old_record: Optional[Dict] = None):
        """Record a change event in the history"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO change_history (
                entity_type, entity_id, change_type, change_priority,
                timestamp, old_values, new_values, change_details, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            event.entity_type,
            event.entity_id,
            event.change_type.value,
            event.priority.name,
            event.timestamp.isoformat(),
            json.dumps(old_record) if old_record else None,
            json.dumps(event.details.get('new_values', {})),
            json.dumps(event.details),
            json.dumps(event.metadata)
        ))
        
        conn.commit()
        conn.close()
    
    def get_entity_history(self, entity_type: str, entity_id: int, 
                          limit: int = 100) -> List[Dict]:
        """Get change history for a specific entity"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM change_history 
            WHERE entity_type = ? AND entity_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """, (entity_type, entity_id, limit))
        
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_recent_changes(self, hours: int = 24, 
                          priority: Optional[ChangePriority] = None) -> List[Dict]:
        """Get recent changes with optional priority filter"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(hours=hours)).isoformat()
        
        query = "SELECT * FROM change_history WHERE timestamp > ?"
        params = [since]
        
        if priority:
            query += " AND change_priority = ?"
            params.append(priority.name)
        
        query += " ORDER BY timestamp DESC LIMIT 1000"
        
        cursor.execute(query, params)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip(columns, row)) for row in rows]
    
    def get_change_statistics(self, days: int = 7) -> Dict:
        """Get change statistics for the last N days"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        # Overall statistics
        cursor.execute("""
            SELECT 
                entity_type,
                change_type,
                change_priority,
                COUNT(*) as count
            FROM change_history 
            WHERE timestamp > ?
            GROUP BY entity_type, change_type, change_priority
            ORDER BY count DESC
        """, (since,))
        
        stats = cursor.fetchall()
        
        # Daily activity
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as daily_count
            FROM change_history 
            WHERE timestamp > ?
            GROUP BY DATE(timestamp)
            ORDER BY date
        """, (since,))
        
        daily_activity = cursor.fetchall()
        
        conn.close()
        
        return {
            'period_days': days,
            'detailed_stats': [
                {
                    'entity_type': row[0],
                    'change_type': row[1], 
                    'priority': row[2],
                    'count': row[3]
                } for row in stats
            ],
            'daily_activity': [
                {'date': row[0], 'count': row[1]} for row in daily_activity
            ]
        }

# Usage with integrated change detection
class AuditedChangeDetector(ParliamentChangeDetector):
    """
    Change detector with full audit trail
    """
    
    def __init__(self):
        super().__init__()
        self.history_tracker = ChangeHistoryTracker()
        self.classifier = ChangeClassifier()
        self.entity_cache = {}  # Store previous states for comparison
    
    def monitor_with_audit(self, entity: str, poll_interval: int = 300):
        """Monitor changes with complete audit trail"""
        
        if entity not in self.last_check_times:
            self.last_check_times[entity] = datetime.now() - timedelta(hours=1)
        
        while True:
            try:
                last_check = self.last_check_times[entity]
                changes = self.get_changes_since(entity, last_check)
                
                for change in changes:
                    entity_id = change['id']
                    cache_key = f"{entity}:{entity_id}"
                    
                    # Get previous state from cache
                    old_record = self.entity_cache.get(cache_key)
                    
                    # Classify the change
                    change_event = self.classifier.classify_change(
                        entity, old_record, change
                    )
                    
                    # Record in audit trail
                    self.history_tracker.record_change(change_event, old_record)
                    
                    # Update cache
                    self.entity_cache[cache_key] = change
                    
                    print(f"Audited change: {entity}:{entity_id} - {change_event.priority.name}")
                
                if changes:
                    latest_update = datetime.fromisoformat(
                        changes[0]['opdateringsdato'].replace('Z', '+00:00')
                    )
                    self.last_check_times[entity] = latest_update
                
                time.sleep(poll_interval)
                
            except Exception as e:
                print(f"Audit monitoring error for {entity}: {e}")
                time.sleep(poll_interval)

# Usage
audited_detector = AuditedChangeDetector()

# Start monitoring with full audit trail
audited_detector.monitor_with_audit('Sag', poll_interval=300)

# Query audit history
history = audited_detector.history_tracker.get_entity_history('Sag', 123456)
for record in history[:5]:
    print(f"{record['timestamp']}: {record['change_type']} - {record['change_priority']}")

# Get statistics
stats = audited_detector.history_tracker.get_change_statistics(days=7)
print(f"Change statistics for last 7 days:")
for stat in stats['detailed_stats'][:10]:
    print(f"  {stat['entity_type']} {stat['change_type']}: {stat['count']} changes")
```

## Performance Optimization for Large-Scale Change Detection

### Optimized Query Strategies

```python
class OptimizedChangeDetector:
    """
    Performance-optimized change detection for large-scale operations
    """
    
    def __init__(self):
        self.api_base = "https://oda.ft.dk/api"
        self.field_cache = {}
        self.rate_limiter = self._create_rate_limiter()
    
    def _create_rate_limiter(self):
        """Simple rate limiter to avoid API overload"""
        import time
        
        class RateLimiter:
            def __init__(self, max_requests=30, time_window=60):
                self.max_requests = max_requests
                self.time_window = time_window
                self.requests = []
            
            def wait_if_needed(self):
                now = time.time()
                # Remove old requests outside time window
                self.requests = [req_time for req_time in self.requests 
                               if now - req_time < self.time_window]
                
                if len(self.requests) >= self.max_requests:
                    sleep_time = self.time_window - (now - self.requests[0]) + 1
                    if sleep_time > 0:
                        time.sleep(sleep_time)
                
                self.requests.append(now)
        
        return RateLimiter()
    
    def get_changes_optimized(self, entity: str, since: datetime,
                            essential_fields_only: bool = True,
                            batch_size: int = 100) -> List[Dict]:
        """
        Get changes with optimized queries for performance
        """
        since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
        
        # Use essential fields only for performance
        fields = self._get_essential_fields(entity) if essential_fields_only else None
        
        params = {
            "$filter": f"opdateringsdato gt datetime'{since_iso}'",
            "$orderby": "opdateringsdato desc",
            "$top": str(batch_size)
        }
        
        if fields:
            params["$select"] = fields
        
        self.rate_limiter.wait_if_needed()
        
        url = f"{self.api_base}/{entity}"
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json().get('value', [])
        else:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    def _get_essential_fields(self, entity: str) -> str:
        """Get essential fields for each entity type"""
        essential_fields = {
            'Sag': 'id,titel,opdateringsdato,statusid,typeid,offentlighedskode',
            'Aktør': 'id,navn,opdateringsdato,typeid,gruppenavnkort',
            'Dokument': 'id,titel,opdateringsdato,typeid,dato,offentlighedskode',
            'Afstemning': 'id,nummer,opdateringsdato,vedtaget,sagid',
            'Stemme': 'id,typeid,opdateringsdato,aktørid,afstemningid'
        }
        
        return essential_fields.get(entity, 'id,opdateringsdato')
    
    def bulk_change_detection(self, entities: List[str], 
                            since: datetime,
                            max_workers: int = 3) -> Dict[str, List[Dict]]:
        """
        Perform bulk change detection across multiple entities in parallel
        """
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        def fetch_entity_changes(entity):
            try:
                changes = self.get_changes_optimized(entity, since)
                return entity, changes
            except Exception as e:
                print(f"Error fetching {entity}: {e}")
                return entity, []
        
        results = {}
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_entity = {
                executor.submit(fetch_entity_changes, entity): entity 
                for entity in entities
            }
            
            for future in as_completed(future_to_entity):
                entity, changes = future.result()
                results[entity] = changes
                
                if changes:
                    print(f" {entity}: {len(changes)} changes detected")
                else:
                    print(f"9 {entity}: No changes")
        
        return results
    
    def memory_efficient_processing(self, entity: str, since: datetime,
                                  processor_func, chunk_size: int = 100):
        """
        Process changes in memory-efficient chunks
        """
        skip = 0
        total_processed = 0
        
        while True:
            # Get chunk
            since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
            
            params = {
                "$filter": f"opdateringsdato gt datetime'{since_iso}'",
                "$orderby": "opdateringsdato desc",
                "$skip": str(skip),
                "$top": str(chunk_size),
                "$select": self._get_essential_fields(entity)
            }
            
            self.rate_limiter.wait_if_needed()
            
            response = requests.get(f"{self.api_base}/{entity}", params=params, timeout=30)
            
            if response.status_code != 200:
                break
            
            chunk = response.json().get('value', [])
            
            if not chunk:
                break
            
            # Process chunk
            try:
                processor_func(chunk)
                total_processed += len(chunk)
                print(f"Processed {len(chunk)} {entity} records (total: {total_processed})")
            except Exception as e:
                print(f"Error processing chunk: {e}")
            
            # If chunk is smaller than chunk_size, we've reached the end
            if len(chunk) < chunk_size:
                break
            
            skip += chunk_size
        
        return total_processed

# Example processor function
def batch_update_processor(chunk: List[Dict]):
    """Example processor for batch updates"""
    # Bulk database updates, cache updates, etc.
    entity_ids = [item['id'] for item in chunk]
    print(f"  Processing batch of IDs: {entity_ids[:5]}...")  # Show first 5
    
    # Example: Bulk database update
    # database.bulk_upsert('cases', chunk)
    
    # Example: Bulk cache update
    # cache.update_multiple(chunk)

# Usage
optimizer = OptimizedChangeDetector()

# Bulk detection across entities
entities = ['Sag', 'Aktør', 'Dokument']
since = datetime.now() - timedelta(hours=6)

all_changes = optimizer.bulk_change_detection(entities, since, max_workers=3)

# Memory efficient processing for large datasets
total = optimizer.memory_efficient_processing(
    entity='Sag',
    since=datetime.now() - timedelta(days=1),
    processor_func=batch_update_processor,
    chunk_size=50
)
print(f"Total processed: {total} records")
```

### Caching Strategies

```python
import pickle
import hashlib
from pathlib import Path

class CachedChangeDetector(OptimizedChangeDetector):
    """
    Change detector with intelligent caching
    """
    
    def __init__(self, cache_dir: str = "./cache"):
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_ttl = 300  # 5 minutes
    
    def _get_cache_key(self, entity: str, params: Dict) -> str:
        """Generate cache key from entity and parameters"""
        params_str = json.dumps(sorted(params.items()))
        hash_obj = hashlib.md5(f"{entity}:{params_str}".encode())
        return hash_obj.hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{cache_key}.cache"
    
    def _is_cache_valid(self, cache_path: Path) -> bool:
        """Check if cache is still valid based on TTL"""
        if not cache_path.exists():
            return False
        
        cache_age = time.time() - cache_path.stat().st_mtime
        return cache_age < self.cache_ttl
    
    def get_changes_cached(self, entity: str, since: datetime, **kwargs) -> List[Dict]:
        """
        Get changes with caching support
        """
        since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            'entity': entity,
            'since': since_iso,
            **kwargs
        }
        
        cache_key = self._get_cache_key(entity, params)
        cache_path = self._get_cache_path(cache_key)
        
        # Try to load from cache
        if self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'rb') as f:
                    cached_data = pickle.load(f)
                    print(f"Cache hit for {entity} (key: {cache_key[:8]})")
                    return cached_data
            except Exception as e:
                print(f"Cache read error: {e}")
        
        # Cache miss or invalid - fetch from API
        print(f"Cache miss for {entity} - fetching from API")
        changes = self.get_changes_optimized(entity, since, **kwargs)
        
        # Store in cache
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(changes, f)
        except Exception as e:
            print(f"Cache write error: {e}")
        
        return changes
    
    def clear_cache(self, pattern: str = "*"):
        """Clear cache files matching pattern"""
        removed = 0
        for cache_file in self.cache_dir.glob(f"{pattern}.cache"):
            cache_file.unlink()
            removed += 1
        
        print(f"Cleared {removed} cache files")
        return removed
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        cache_files = list(self.cache_dir.glob("*.cache"))
        
        total_size = sum(f.stat().st_size for f in cache_files)
        valid_files = sum(1 for f in cache_files if self._is_cache_valid(f))
        
        return {
            'total_files': len(cache_files),
            'valid_files': valid_files,
            'expired_files': len(cache_files) - valid_files,
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }

# Usage
cached_detector = CachedChangeDetector(cache_dir="./api_cache")

# First call - cache miss
changes1 = cached_detector.get_changes_cached('Sag', datetime.now() - timedelta(hours=1))

# Second call within TTL - cache hit  
changes2 = cached_detector.get_changes_cached('Sag', datetime.now() - timedelta(hours=1))

# Check cache statistics
stats = cached_detector.get_cache_stats()
print(f"Cache stats: {stats}")
```

## Error Handling and Recovery from Missed Changes

### Robust Error Handling

```python
import logging
from typing import Optional
from enum import Enum

class ErrorType(Enum):
    API_TIMEOUT = "api_timeout"
    API_ERROR = "api_error"
    NETWORK_ERROR = "network_error"
    PARSE_ERROR = "parse_error"
    STORAGE_ERROR = "storage_error"

class ChangeDetectionError(Exception):
    def __init__(self, error_type: ErrorType, message: str, 
                 original_exception: Optional[Exception] = None):
        self.error_type = error_type
        self.original_exception = original_exception
        super().__init__(message)

class ResilientChangeDetector(ParliamentChangeDetector):
    """
    Change detector with comprehensive error handling and recovery
    """
    
    def __init__(self, max_retries: int = 3, backoff_factor: float = 2.0):
        super().__init__()
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor
        self.failed_requests = []
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def get_changes_with_retry(self, entity: str, since: datetime,
                              attempt: int = 0) -> Optional[List[Dict]]:
        """
        Get changes with exponential backoff retry logic
        """
        try:
            since_iso = since.strftime("%Y-%m-%dT%H:%M:%S")
            
            params = {
                "$filter": f"opdateringsdato gt datetime'{since_iso}'",
                "$orderby": "opdateringsdato desc",
                "$top": "100",
                "$select": self._get_essential_fields(entity)
            }
            
            url = f"{self.base_url}/{entity}"
            
            # Add timeout and retry-friendly settings
            response = requests.get(
                url, 
                params=params, 
                timeout=(10, 30),  # connection, read timeout
                headers={'User-Agent': 'ParliamentMonitor/1.0'}
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('value', [])
            elif response.status_code == 429:  # Rate limited
                raise ChangeDetectionError(
                    ErrorType.API_ERROR,
                    f"Rate limited: {response.status_code}"
                )
            elif response.status_code >= 500:  # Server error
                raise ChangeDetectionError(
                    ErrorType.API_ERROR,
                    f"Server error: {response.status_code}"
                )
            else:
                raise ChangeDetectionError(
                    ErrorType.API_ERROR,
                    f"API error: {response.status_code} - {response.text}"
                )
        
        except requests.exceptions.Timeout as e:
            raise ChangeDetectionError(
                ErrorType.API_TIMEOUT,
                f"API timeout for {entity}",
                e
            )
        except requests.exceptions.ConnectionError as e:
            raise ChangeDetectionError(
                ErrorType.NETWORK_ERROR,
                f"Network error for {entity}",
                e
            )
        except json.JSONDecodeError as e:
            raise ChangeDetectionError(
                ErrorType.PARSE_ERROR,
                f"JSON parse error for {entity}",
                e
            )
        except Exception as e:
            raise ChangeDetectionError(
                ErrorType.API_ERROR,
                f"Unexpected error for {entity}: {e}",
                e
            )
    
    def monitor_with_recovery(self, entity: str, poll_interval: int = 300):
        """
        Monitor with automatic error recovery and gap detection
        """
        consecutive_failures = 0
        max_consecutive_failures = 5
        
        if entity not in self.last_check_times:
            self.last_check_times[entity] = datetime.now() - timedelta(hours=1)
        
        while True:
            try:
                last_check = self.last_check_times[entity]
                
                # Try to get changes with retry
                changes = self._get_changes_with_exponential_backoff(entity, last_check)
                
                if changes:
                    # Check for gaps in data
                    self._check_for_missed_changes(entity, changes, last_check)
                    
                    # Process changes
                    self._process_changes_safely(entity, changes)
                    
                    # Update last check time
                    latest_update = datetime.fromisoformat(
                        changes[0]['opdateringsdato'].replace('Z', '+00:00')
                    )
                    self.last_check_times[entity] = latest_update
                    
                    self.logger.info(f"Successfully processed {len(changes)} changes for {entity}")
                
                # Reset failure counter on success
                consecutive_failures = 0
                
            except ChangeDetectionError as e:
                consecutive_failures += 1
                
                self.logger.error(f"Change detection error for {entity}: {e} (failure #{consecutive_failures})")
                
                # Record failed request for analysis
                self.failed_requests.append({
                    'entity': entity,
                    'error_type': e.error_type.value,
                    'message': str(e),
                    'timestamp': datetime.now().isoformat(),
                    'consecutive_failures': consecutive_failures
                })
                
                # If too many consecutive failures, extend the sleep time
                if consecutive_failures >= max_consecutive_failures:
                    extended_sleep = poll_interval * (consecutive_failures - max_consecutive_failures + 1)
                    self.logger.warning(f"Extended sleep for {entity}: {extended_sleep}s due to repeated failures")
                    time.sleep(extended_sleep)
                    continue
                
            except Exception as e:
                consecutive_failures += 1
                self.logger.error(f"Unexpected error monitoring {entity}: {e}")
                
            # Regular polling interval
            time.sleep(poll_interval)
    
    def _get_changes_with_exponential_backoff(self, entity: str, since: datetime) -> List[Dict]:
        """
        Get changes with exponential backoff retry
        """
        for attempt in range(self.max_retries):
            try:
                return self.get_changes_with_retry(entity, since, attempt)
                
            except ChangeDetectionError as e:
                if attempt == self.max_retries - 1:
                    # Final attempt failed
                    raise e
                
                # Calculate backoff delay
                delay = (self.backoff_factor ** attempt) + random.uniform(0, 1)
                
                self.logger.warning(f"Attempt {attempt + 1} failed for {entity}: {e}. Retrying in {delay:.2f}s")
                time.sleep(delay)
        
        # Should not reach here
        raise ChangeDetectionError(ErrorType.API_ERROR, f"Max retries exceeded for {entity}")
    
    def _check_for_missed_changes(self, entity: str, changes: List[Dict], 
                                 last_check: datetime):
        """
        Check if we might have missed changes due to gaps
        """
        if not changes:
            return
        
        # Check for time gaps that might indicate missed data
        oldest_change = datetime.fromisoformat(
            changes[-1]['opdateringsdato'].replace('Z', '+00:00')
        )
        
        gap = oldest_change - last_check
        
        # If there's a significant gap, we might have missed changes
        if gap.total_seconds() > 3600:  # More than 1 hour gap
            self.logger.warning(f"Potential data gap detected for {entity}: {gap}")
            
            # Try to fill the gap with additional query
            try:
                gap_changes = self._fetch_gap_data(entity, last_check, oldest_change)
                if gap_changes:
                    self.logger.info(f"Recovered {len(gap_changes)} potentially missed changes for {entity}")
                    # Merge with existing changes (remove duplicates by ID)
                    existing_ids = {change['id'] for change in changes}
                    new_changes = [c for c in gap_changes if c['id'] not in existing_ids]
                    changes.extend(new_changes)
                    
            except Exception as e:
                self.logger.error(f"Failed to recover gap data for {entity}: {e}")
    
    def _fetch_gap_data(self, entity: str, start_time: datetime, 
                       end_time: datetime) -> List[Dict]:
        """
        Fetch data for a specific time range to fill gaps
        """
        start_iso = start_time.strftime("%Y-%m-%dT%H:%M:%S")
        end_iso = end_time.strftime("%Y-%m-%dT%H:%M:%S")
        
        params = {
            "$filter": f"opdateringsdato gt datetime'{start_iso}' and opdateringsdato lt datetime'{end_iso}'",
            "$orderby": "opdateringsdato desc",
            "$top": "200"  # Larger limit for gap recovery
        }
        
        url = f"{self.base_url}/{entity}"
        response = requests.get(url, params=params, timeout=30)
        
        if response.status_code == 200:
            return response.json().get('value', [])
        else:
            raise Exception(f"Gap recovery failed: {response.status_code}")
    
    def _process_changes_safely(self, entity: str, changes: List[Dict]):
        """
        Process changes with error isolation
        """
        successful = 0
        failed = 0
        
        for change in changes:
            try:
                # Your change processing logic here
                self._process_single_change(entity, change)
                successful += 1
                
            except Exception as e:
                failed += 1
                self.logger.error(f"Failed to process change {change.get('id')} for {entity}: {e}")
        
        if failed > 0:
            self.logger.warning(f"Processing completed for {entity}: {successful} successful, {failed} failed")
    
    def _process_single_change(self, entity: str, change: Dict):
        """
        Process a single change - implement your logic here
        """
        # Example processing
        change_id = change.get('id')
        update_time = change.get('opdateringsdato')
        
        # Your processing logic here:
        # - Database updates
        # - Cache updates  
        # - Notifications
        # - Analytics
        
        pass
    
    def get_error_summary(self) -> Dict:
        """
        Get summary of errors encountered
        """
        if not self.failed_requests:
            return {'total_errors': 0}
        
        error_counts = {}
        recent_errors = []
        
        cutoff = datetime.now() - timedelta(hours=24)
        
        for error in self.failed_requests:
            error_type = error['error_type']
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
            
            error_time = datetime.fromisoformat(error['timestamp'])
            if error_time >= cutoff:
                recent_errors.append(error)
        
        return {
            'total_errors': len(self.failed_requests),
            'error_counts': error_counts,
            'recent_24h': len(recent_errors),
            'recent_errors': recent_errors[-10:]  # Last 10 recent errors
        }

# Usage
resilient_detector = ResilientChangeDetector(max_retries=3, backoff_factor=2.0)

# Start resilient monitoring
resilient_detector.monitor_with_recovery('Sag', poll_interval=300)

# Check error summary
error_summary = resilient_detector.get_error_summary()
print(f"Error summary: {error_summary}")
```

### Data Integrity Validation

```python
class DataIntegrityValidator:
    """
    Validate data integrity in change detection
    """
    
    def __init__(self):
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict:
        """Setup validation rules for each entity type"""
        return {
            'Sag': {
                'required_fields': ['id', 'titel', 'opdateringsdato'],
                'id_field': 'id',
                'timestamp_field': 'opdateringsdato',
                'validation_functions': [
                    self._validate_case_data,
                ]
            },
            'Aktør': {
                'required_fields': ['id', 'navn', 'opdateringsdato'],
                'id_field': 'id',
                'timestamp_field': 'opdateringsdato',
                'validation_functions': [
                    self._validate_actor_data,
                ]
            },
            'Dokument': {
                'required_fields': ['id', 'titel', 'opdateringsdato'],
                'id_field': 'id', 
                'timestamp_field': 'opdateringsdato',
                'validation_functions': [
                    self._validate_document_data,
                ]
            }
        }
    
    def validate_changes(self, entity: str, changes: List[Dict]) -> Dict:
        """
        Validate a list of changes for data integrity
        
        Returns:
            Validation summary with any issues found
        """
        if entity not in self.validation_rules:
            return {'status': 'skipped', 'reason': 'no_validation_rules'}
        
        rules = self.validation_rules[entity]
        issues = []
        valid_changes = []
        
        for i, change in enumerate(changes):
            change_issues = []
            
            # Check required fields
            for field in rules['required_fields']:
                if field not in change or change[field] is None:
                    change_issues.append(f"Missing required field: {field}")
            
            # Validate ID field
            id_value = change.get(rules['id_field'])
            if id_value is not None and not isinstance(id_value, int):
                change_issues.append(f"Invalid ID type: {type(id_value)}")
            
            # Validate timestamp
            timestamp_value = change.get(rules['timestamp_field'])
            if timestamp_value:
                try:
                    datetime.fromisoformat(timestamp_value.replace('Z', '+00:00'))
                except ValueError:
                    change_issues.append(f"Invalid timestamp format: {timestamp_value}")
            
            # Run custom validation functions
            for validation_func in rules['validation_functions']:
                try:
                    custom_issues = validation_func(change)
                    change_issues.extend(custom_issues)
                except Exception as e:
                    change_issues.append(f"Validation error: {e}")
            
            if change_issues:
                issues.append({
                    'index': i,
                    'id': id_value,
                    'issues': change_issues
                })
            else:
                valid_changes.append(change)
        
        return {
            'status': 'completed',
            'total_changes': len(changes),
            'valid_changes': len(valid_changes),
            'invalid_changes': len(issues),
            'issues': issues,
            'valid_data': valid_changes
        }
    
    def _validate_case_data(self, case: Dict) -> List[str]:
        """Validate case-specific data"""
        issues = []
        
        # Check for reasonable title length
        title = case.get('titel', '')
        if len(title) > 1000:
            issues.append("Title unusually long (>1000 chars)")
        elif len(title) < 5:
            issues.append("Title unusually short (<5 chars)")
        
        # Check status ID is reasonable
        status_id = case.get('statusid')
        if status_id is not None and (status_id < 1 or status_id > 100):
            issues.append(f"Unusual status ID: {status_id}")
        
        # Check type ID is reasonable  
        type_id = case.get('typeid')
        if type_id is not None and (type_id < 1 or type_id > 50):
            issues.append(f"Unusual type ID: {type_id}")
        
        return issues
    
    def _validate_actor_data(self, actor: Dict) -> List[str]:
        """Validate actor-specific data"""
        issues = []
        
        # Check name is present and reasonable
        name = actor.get('navn', '')
        if not name or len(name.strip()) == 0:
            issues.append("Empty or missing name")
        elif len(name) > 200:
            issues.append("Name unusually long (>200 chars)")
        
        # Check type ID
        type_id = actor.get('typeid')
        if type_id is not None and (type_id < 1 or type_id > 20):
            issues.append(f"Invalid actor type ID: {type_id}")
        
        return issues
    
    def _validate_document_data(self, document: Dict) -> List[str]:
        """Validate document-specific data"""
        issues = []
        
        # Check title
        title = document.get('titel', '')
        if not title or len(title.strip()) == 0:
            issues.append("Empty or missing title")
        
        # Check dates are in reasonable order
        doc_date = document.get('dato')
        release_date = document.get('frigivelsesdato')
        update_date = document.get('opdateringsdato')
        
        try:
            if doc_date and release_date:
                doc_dt = datetime.fromisoformat(doc_date.replace('Z', '+00:00'))
                release_dt = datetime.fromisoformat(release_date.replace('Z', '+00:00'))
                
                if release_dt < doc_dt:
                    issues.append("Release date before document date")
            
            if update_date and doc_date:
                update_dt = datetime.fromisoformat(update_date.replace('Z', '+00:00'))
                doc_dt = datetime.fromisoformat(doc_date.replace('Z', '+00:00'))
                
                if update_dt < doc_dt:
                    issues.append("Update date before document date")
        
        except ValueError as e:
            issues.append(f"Date parsing error: {e}")
        
        return issues

# Enhanced resilient detector with validation
class ValidatedChangeDetector(ResilientChangeDetector):
    """
    Change detector with data integrity validation
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.validator = DataIntegrityValidator()
        self.validation_stats = {}
    
    def _process_changes_safely(self, entity: str, changes: List[Dict]):
        """
        Enhanced change processing with validation
        """
        # Validate changes first
        validation_result = self.validator.validate_changes(entity, changes)
        
        # Update validation statistics
        if entity not in self.validation_stats:
            self.validation_stats[entity] = {
                'total_processed': 0,
                'total_invalid': 0,
                'total_issues': 0
            }
        
        stats = self.validation_stats[entity]
        stats['total_processed'] += validation_result['total_changes']
        stats['total_invalid'] += validation_result['invalid_changes']
        stats['total_issues'] += len(validation_result['issues'])
        
        if validation_result['invalid_changes'] > 0:
            self.logger.warning(f"Data validation issues found for {entity}: {validation_result['invalid_changes']} invalid out of {validation_result['total_changes']}")
            
            # Log specific issues for debugging
            for issue in validation_result['issues'][:5]:  # Log first 5 issues
                self.logger.warning(f"  ID {issue['id']}: {', '.join(issue['issues'])}")
        
        # Process only valid changes
        valid_changes = validation_result['valid_data']
        super()._process_changes_safely(entity, valid_changes)
        
        self.logger.info(f"Processed {len(valid_changes)} valid changes for {entity}")
    
    def get_validation_stats(self) -> Dict:
        """Get validation statistics"""
        return {
            'by_entity': self.validation_stats,
            'summary': {
                'total_processed': sum(stats['total_processed'] for stats in self.validation_stats.values()),
                'total_invalid': sum(stats['total_invalid'] for stats in self.validation_stats.values()),
                'total_issues': sum(stats['total_issues'] for stats in self.validation_stats.values())
            }
        }

# Usage
validated_detector = ValidatedChangeDetector(max_retries=3)

# Monitor with validation
validated_detector.monitor_with_recovery('Sag', poll_interval=300)

# Get validation statistics
validation_stats = validated_detector.get_validation_stats()
print(f"Validation stats: {validation_stats}")
```

## Integration with Notification and Alert Systems

### Webhook Integration

```python
import json
import requests
from typing import List, Dict, Callable

class WebhookNotificationSystem:
    """
    Send change notifications via webhooks
    """
    
    def __init__(self):
        self.webhooks = {}
        self.retry_config = {
            'max_retries': 3,
            'backoff_factor': 2,
            'timeout': 10
        }
    
    def register_webhook(self, name: str, url: str, 
                        filter_func: Optional[Callable] = None,
                        headers: Optional[Dict[str, str]] = None):
        """
        Register a webhook endpoint
        
        Args:
            name: Webhook identifier
            url: Webhook URL
            filter_func: Optional function to filter which changes to send
            headers: Optional HTTP headers
        """
        self.webhooks[name] = {
            'url': url,
            'filter_func': filter_func,
            'headers': headers or {'Content-Type': 'application/json'},
            'stats': {
                'sent': 0,
                'failed': 0,
                'last_sent': None,
                'last_error': None
            }
        }
    
    def send_change_notification(self, webhook_name: str, 
                               change_event: ChangeEvent) -> bool:
        """
        Send a change notification to a specific webhook
        """
        if webhook_name not in self.webhooks:
            raise ValueError(f"Webhook {webhook_name} not registered")
        
        webhook = self.webhooks[webhook_name]
        
        # Apply filter if configured
        if webhook['filter_func'] and not webhook['filter_func'](change_event):
            return True  # Filtered out, but not an error
        
        # Prepare payload
        payload = {
            'event_type': 'change_detected',
            'timestamp': datetime.now().isoformat(),
            'change': {
                'entity_type': change_event.entity_type,
                'entity_id': change_event.entity_id,
                'change_type': change_event.change_type.value,
                'priority': change_event.priority.name,
                'timestamp': change_event.timestamp.isoformat(),
                'details': change_event.details,
                'metadata': change_event.metadata
            }
        }
        
        # Send with retry logic
        for attempt in range(self.retry_config['max_retries']):
            try:
                response = requests.post(
                    webhook['url'],
                    json=payload,
                    headers=webhook['headers'],
                    timeout=self.retry_config['timeout']
                )
                
                if response.status_code in [200, 201, 202]:
                    webhook['stats']['sent'] += 1
                    webhook['stats']['last_sent'] = datetime.now().isoformat()
                    return True
                else:
                    raise Exception(f"HTTP {response.status_code}: {response.text}")
                    
            except Exception as e:
                if attempt == self.retry_config['max_retries'] - 1:
                    # Final attempt failed
                    webhook['stats']['failed'] += 1
                    webhook['stats']['last_error'] = str(e)
                    print(f"Webhook {webhook_name} failed after {self.retry_config['max_retries']} attempts: {e}")
                    return False
                else:
                    # Wait before retry
                    delay = self.retry_config['backoff_factor'] ** attempt
                    time.sleep(delay)
        
        return False
    
    def broadcast_change(self, change_event: ChangeEvent):
        """
        Send change notification to all registered webhooks
        """
        results = {}
        
        for webhook_name in self.webhooks:
            try:
                success = self.send_change_notification(webhook_name, change_event)
                results[webhook_name] = 'success' if success else 'failed'
            except Exception as e:
                results[webhook_name] = f'error: {e}'
        
        return results
    
    def get_webhook_stats(self) -> Dict:
        """Get statistics for all webhooks"""
        stats = {}
        for name, webhook in self.webhooks.items():
            stats[name] = {
                'url': webhook['url'],
                'stats': webhook['stats']
            }
        return stats

# Priority filters for webhooks
def critical_only_filter(change_event: ChangeEvent) -> bool:
    """Only send critical priority changes"""
    return change_event.priority == ChangePriority.CRITICAL

def voting_changes_filter(change_event: ChangeEvent) -> bool:
    """Only send voting-related changes"""
    return change_event.entity_type in ['Afstemning', 'Stemme']

def high_priority_cases_filter(change_event: ChangeEvent) -> bool:
    """Only send high priority case changes"""
    return (change_event.entity_type == 'Sag' and 
            change_event.priority in [ChangePriority.HIGH, ChangePriority.CRITICAL])

# Usage
webhook_system = WebhookNotificationSystem()

# Register different webhooks with filters
webhook_system.register_webhook(
    'critical_alerts',
    'https://alerts.example.com/webhook',
    filter_func=critical_only_filter,
    headers={'Authorization': 'Bearer token123', 'Content-Type': 'application/json'}
)

webhook_system.register_webhook(
    'voting_monitor',
    'https://voting.example.com/webhook',
    filter_func=voting_changes_filter
)

webhook_system.register_webhook(
    'case_updates',
    'https://cases.example.com/webhook',
    filter_func=high_priority_cases_filter
)
```

### Email Alert System

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List

class EmailAlertSystem:
    """
    Send change alerts via email
    """
    
    def __init__(self, smtp_host: str, smtp_port: int = 587,
                 username: str = None, password: str = None):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.alert_templates = self._setup_templates()
    
    def _setup_templates(self) -> Dict:
        """Setup email templates for different change types"""
        return {
            'critical': {
                'subject': '=¨ CRITICAL: Parliamentary Change Alert - {entity_type} {entity_id}',
                'template': '''
                <h2 style="color: red;">Critical Parliamentary Change Detected</h2>
                <p><strong>Entity:</strong> {entity_type} ID {entity_id}</p>
                <p><strong>Change Type:</strong> {change_type}</p>
                <p><strong>Priority:</strong> {priority}</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Details:</strong></p>
                <pre>{details}</pre>
                '''
            },
            'high': {
                'subject': '  HIGH: Parliamentary Change - {entity_type} {entity_id}',
                'template': '''
                <h2 style="color: orange;">High Priority Parliamentary Change</h2>
                <p><strong>Entity:</strong> {entity_type} ID {entity_id}</p>
                <p><strong>Change Type:</strong> {change_type}</p>
                <p><strong>Timestamp:</strong> {timestamp}</p>
                <p><strong>Summary:</strong> {summary}</p>
                '''
            },
            'summary': {
                'subject': 'Parliamentary Changes Summary - {date}',
                'template': '''
                <h2>Daily Parliamentary Changes Summary</h2>
                <p><strong>Date:</strong> {date}</p>
                <p><strong>Total Changes:</strong> {total_changes}</p>
                
                <h3>By Priority:</h3>
                <ul>
                {priority_summary}
                </ul>
                
                <h3>By Entity Type:</h3>
                <ul>
                {entity_summary}
                </ul>
                
                <h3>Notable Changes:</h3>
                {notable_changes}
                '''
            }
        }
    
    def send_change_alert(self, change_event: ChangeEvent, 
                         recipients: List[str]) -> bool:
        """
        Send email alert for a change event
        """
        try:
            # Select template based on priority
            if change_event.priority == ChangePriority.CRITICAL:
                template_key = 'critical'
            elif change_event.priority == ChangePriority.HIGH:
                template_key = 'high'
            else:
                return True  # Don't send emails for medium/low priority
            
            template = self.alert_templates[template_key]
            
            # Format template
            subject = template['subject'].format(
                entity_type=change_event.entity_type,
                entity_id=change_event.entity_id
            )
            
            # Prepare change details for display
            details_text = json.dumps(change_event.details, indent=2, ensure_ascii=False)
            
            # Get summary based on change type
            summary = self._generate_change_summary(change_event)
            
            body = template['template'].format(
                entity_type=change_event.entity_type,
                entity_id=change_event.entity_id,
                change_type=change_event.change_type.value.title(),
                priority=change_event.priority.name,
                timestamp=change_event.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                details=details_text,
                summary=summary
            )
            
            return self._send_email(recipients, subject, body)
            
        except Exception as e:
            print(f"Error sending change alert email: {e}")
            return False
    
    def send_daily_summary(self, changes: List[ChangeEvent], 
                          recipients: List[str], date: str = None) -> bool:
        """
        Send daily summary of all changes
        """
        try:
            if not date:
                date = datetime.now().strftime('%Y-%m-%d')
            
            # Analyze changes
            total_changes = len(changes)
            
            priority_counts = {}
            entity_counts = {}
            notable_changes = []
            
            for change in changes:
                # Count by priority
                priority_counts[change.priority.name] = priority_counts.get(change.priority.name, 0) + 1
                
                # Count by entity
                entity_counts[change.entity_type] = entity_counts.get(change.entity_type, 0) + 1
                
                # Collect notable changes (high/critical priority)
                if change.priority in [ChangePriority.HIGH, ChangePriority.CRITICAL]:
                    notable_changes.append(change)
            
            # Format priority summary
            priority_summary = '\n'.join([
                f"<li>{priority}: {count} changes</li>"
                for priority, count in sorted(priority_counts.items())
            ])
            
            # Format entity summary
            entity_summary = '\n'.join([
                f"<li>{entity}: {count} changes</li>"
                for entity, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True)
            ])
            
            # Format notable changes
            notable_html = ""
            for change in notable_changes[:10]:  # Top 10 notable changes
                summary = self._generate_change_summary(change)
                notable_html += f"""
                <div style="border-left: 3px solid orange; padding-left: 10px; margin: 10px 0;">
                    <strong>{change.entity_type} {change.entity_id}</strong> - {change.priority.name}<br>
                    <em>{change.timestamp.strftime('%H:%M')}</em><br>
                    {summary}
                </div>
                """
            
            template = self.alert_templates['summary']
            
            subject = template['subject'].format(date=date)
            body = template['template'].format(
                date=date,
                total_changes=total_changes,
                priority_summary=priority_summary,
                entity_summary=entity_summary,
                notable_changes=notable_html if notable_html else "<p>No notable changes today.</p>"
            )
            
            return self._send_email(recipients, subject, body)
            
        except Exception as e:
            print(f"Error sending daily summary email: {e}")
            return False
    
    def _generate_change_summary(self, change_event: ChangeEvent) -> str:
        """Generate human-readable summary of a change"""
        entity_type = change_event.entity_type
        change_type = change_event.change_type.value
        details = change_event.details
        
        if entity_type == 'Sag':
            if 'statusid' in details:
                old_status = details['statusid'].get('old')
                new_status = details['statusid'].get('new')
                return f"Case status changed from {old_status} to {new_status}"
            elif change_type == 'create':
                return "New parliamentary case created"
            else:
                return "Parliamentary case updated"
        
        elif entity_type == 'Afstemning':
            if change_type == 'create':
                return "New voting session created"
            else:
                return "Voting session updated"
        
        elif entity_type == 'Dokument':
            if change_type == 'create':
                return "New document published"
            else:
                return "Document updated"
        
        elif entity_type == 'Aktør':
            if change_type == 'create':
                return "New political actor added"
            else:
                return "Political actor information updated"
        
        return f"{entity_type} {change_type}d"
    
    def _send_email(self, recipients: List[str], subject: str, body: str) -> bool:
        """
        Send email using SMTP
        """
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = self.username
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.username and self.password:
                    server.login(self.username, self.password)
                
                server.send_message(msg)
            
            return True
            
        except Exception as e:
            print(f"SMTP error: {e}")
            return False

# Usage
email_system = EmailAlertSystem(
    smtp_host='smtp.gmail.com',
    smtp_port=587,
    username='your-email@gmail.com',
    password='your-app-password'
)

# Send critical change alert
critical_recipients = ['admin@example.com', 'alerts@example.com']
# email_system.send_change_alert(critical_change_event, critical_recipients)

# Send daily summary
summary_recipients = ['team@example.com']
# email_system.send_daily_summary(daily_changes, summary_recipients)
```

### Integrated Notification Manager

```python
class NotificationManager:
    """
    Centralized notification management for change detection
    """
    
    def __init__(self):
        self.webhook_system = WebhookNotificationSystem()
        self.email_system = None  # Configure as needed
        self.notification_rules = []
        self.stats = {
            'notifications_sent': 0,
            'webhooks_sent': 0,
            'emails_sent': 0,
            'errors': 0
        }
    
    def setup_email(self, smtp_config: Dict):
        """Setup email notifications"""
        self.email_system = EmailAlertSystem(**smtp_config)
    
    def add_notification_rule(self, name: str, condition_func: Callable,
                            webhook_names: List[str] = None,
                            email_recipients: List[str] = None):
        """
        Add a notification rule
        
        Args:
            name: Rule name
            condition_func: Function that returns True if notification should be sent
            webhook_names: List of webhook names to trigger
            email_recipients: List of email recipients
        """
        self.notification_rules.append({
            'name': name,
            'condition_func': condition_func,
            'webhook_names': webhook_names or [],
            'email_recipients': email_recipients or [],
            'stats': {'triggered': 0, 'sent': 0, 'failed': 0}
        })
    
    def process_change_event(self, change_event: ChangeEvent):
        """
        Process a change event and send appropriate notifications
        """
        for rule in self.notification_rules:
            try:
                if rule['condition_func'](change_event):
                    rule['stats']['triggered'] += 1
                    
                    # Send webhooks
                    webhook_success = True
                    for webhook_name in rule['webhook_names']:
                        try:
                            success = self.webhook_system.send_change_notification(
                                webhook_name, change_event
                            )
                            if success:
                                self.stats['webhooks_sent'] += 1
                            else:
                                webhook_success = False
                        except Exception as e:
                            print(f"Webhook error for rule {rule['name']}: {e}")
                            webhook_success = False
                            self.stats['errors'] += 1
                    
                    # Send emails
                    email_success = True
                    if rule['email_recipients'] and self.email_system:
                        try:
                            success = self.email_system.send_change_alert(
                                change_event, rule['email_recipients']
                            )
                            if success:
                                self.stats['emails_sent'] += 1
                            else:
                                email_success = False
                        except Exception as e:
                            print(f"Email error for rule {rule['name']}: {e}")
                            email_success = False
                            self.stats['errors'] += 1
                    
                    if webhook_success and email_success:
                        rule['stats']['sent'] += 1
                        self.stats['notifications_sent'] += 1
                    else:
                        rule['stats']['failed'] += 1
                        
            except Exception as e:
                print(f"Error processing rule {rule['name']}: {e}")
                rule['stats']['failed'] += 1
                self.stats['errors'] += 1
    
    def get_notification_stats(self) -> Dict:
        """Get notification statistics"""
        rule_stats = {}
        for rule in self.notification_rules:
            rule_stats[rule['name']] = rule['stats']
        
        return {
            'overall_stats': self.stats,
            'rule_stats': rule_stats,
            'webhook_stats': self.webhook_system.get_webhook_stats()
        }

# Notification condition functions
def critical_voting_condition(change_event: ChangeEvent) -> bool:
    """Critical voting-related changes"""
    return (change_event.entity_type == 'Afstemning' and 
            change_event.priority == ChangePriority.CRITICAL)

def new_legislation_condition(change_event: ChangeEvent) -> bool:
    """New legislative proposals"""
    if change_event.entity_type != 'Sag':
        return False
    
    # Check if it's a new case with legislation keywords
    if change_event.change_type == ChangeType.CREATE:
        title = change_event.details.get('new_values', {}).get('titel', '').lower()
        legislation_keywords = ['lov', 'forslag', 'lovforslag']
        return any(keyword in title for keyword in legislation_keywords)
    
    return False

def minister_activity_condition(change_event: ChangeEvent) -> bool:
    """Ministerial document activity"""
    if change_event.entity_type != 'Dokument':
        return False
    
    # Check if it's a ministerial document (type 3)
    doc_type = change_event.details.get('new_values', {}).get('typeid')
    return doc_type == 3  # Ministerial statements

# Setup comprehensive notification system
def setup_parliament_notifications():
    """Setup comprehensive parliamentary notification system"""
    
    notification_manager = NotificationManager()
    
    # Setup email (configure with your SMTP settings)
    # notification_manager.setup_email({
    #     'smtp_host': 'smtp.example.com',
    #     'smtp_port': 587,
    #     'username': 'alerts@example.com',
    #     'password': 'password'
    # })
    
    # Register webhooks
    notification_manager.webhook_system.register_webhook(
        'slack_critical',
        'https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK',
        filter_func=critical_only_filter
    )
    
    notification_manager.webhook_system.register_webhook(
        'discord_voting',
        'https://discord.com/api/webhooks/YOUR/WEBHOOK',
        filter_func=voting_changes_filter
    )
    
    # Add notification rules
    notification_manager.add_notification_rule(
        'critical_voting_alerts',
        critical_voting_condition,
        webhook_names=['slack_critical'],
        email_recipients=['admin@parliament-monitor.com']
    )
    
    notification_manager.add_notification_rule(
        'new_legislation_tracking',
        new_legislation_condition,
        webhook_names=['slack_critical'],
        email_recipients=['legislation@parliament-monitor.com']
    )
    
    notification_manager.add_notification_rule(
        'ministerial_updates',
        minister_activity_condition,
        webhook_names=['discord_voting']
    )
    
    return notification_manager

# Integration with change detection
class NotificationEnabledDetector(ValidatedChangeDetector):
    """
    Change detector with integrated notifications
    """
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.notification_manager = setup_parliament_notifications()
        self.classifier = ChangeClassifier()
    
    def _process_single_change(self, entity: str, change: Dict):
        """
        Enhanced change processing with notifications
        """
        # Get previous state if available (for change classification)
        old_record = None  # You might want to implement state caching
        
        # Classify the change
        change_event = self.classifier.classify_change(entity, old_record, change)
        
        # Send notifications
        self.notification_manager.process_change_event(change_event)
        
        # Continue with regular processing
        super()._process_single_change(entity, change)
    
    def get_comprehensive_stats(self) -> Dict:
        """Get comprehensive statistics including notifications"""
        base_stats = {
            'error_summary': self.get_error_summary(),
            'validation_stats': self.get_validation_stats()
        }
        
        notification_stats = self.notification_manager.get_notification_stats()
        
        return {
            **base_stats,
            'notification_stats': notification_stats
        }

# Usage
comprehensive_detector = NotificationEnabledDetector(max_retries=3)

# Start monitoring with full notifications
comprehensive_detector.monitor_with_recovery('Sag', poll_interval=300)

# Get comprehensive statistics
stats = comprehensive_detector.get_comprehensive_stats()
print(f"Comprehensive stats: {json.dumps(stats, indent=2)}")
```

## Conclusion

This comprehensive guide provides a complete framework for building robust change detection systems for the Danish Parliamentary OData API. The implementation covers:

- **Basic to advanced change detection** using timestamp-based queries
- **Entity-specific monitoring** with specialized detectors for cases, actors, and documents
- **Incremental synchronization** for efficient data management
- **Change classification and prioritization** for intelligent processing
- **Real-time vs batch processing** trade-offs and hybrid approaches
- **Complete audit trails** for change history tracking
- **Performance optimization** strategies for large-scale operations
- **Comprehensive error handling** with retry logic and data validation
- **Integrated notification systems** with webhooks and email alerts

The modular design allows you to implement components based on your specific requirements, from simple real-time monitoring to enterprise-scale change detection systems with full audit trails and notification capabilities.

Key implementation recommendations:

1. **Start simple** with basic timestamp-based detection
2. **Add validation** to ensure data integrity
3. **Implement error handling** for production robustness
4. **Use caching** to optimize API usage
5. **Choose appropriate polling intervals** based on your requirements
6. **Set up monitoring** to track system health and performance
7. **Implement notifications** for critical changes only to avoid alert fatigue

This foundation enables building sophisticated parliamentary monitoring applications that can track legislative changes, political developments, and institutional updates in real-time while maintaining high reliability and performance.