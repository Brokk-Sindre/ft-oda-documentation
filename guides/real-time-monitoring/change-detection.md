# Change Detection Using Opdateringsdato

Master the `opdateringsdato` (update date) field to build sophisticated change detection systems that leverage the Danish Parliament API's exceptional real-time capabilities with hours-fresh updates.

## Understanding Opdateringsdato

The `opdateringsdato` field is present across all 50+ entities in the Danish Parliament API and serves as the universal timestamp for when any record was last modified. This enables precise change tracking across the entire parliamentary system.

### Key Characteristics
- **Universal Presence** - Every entity includes `opdateringsdato`
- **High Precision** - Timestamps to millisecond accuracy
- **Real-Time Updates** - Reflects changes within 3-8 hours
- **Batch Processing** - Related records often share identical timestamps
- **Forward Dating** - Future events (meetings) are pre-populated

### Timestamp Format
```
2025-09-09T17:49:11.87
```
- ISO 8601 format with millisecond precision
- Times appear to be in Danish local time (CET/CEST)
- No explicit timezone indicators in the data

## Implementation Framework

### Core Change Detection Engine

```python
import requests
import urllib.parse
from datetime import datetime, timedelta
from collections import defaultdict
import json
import sqlite3

class ChangeDetectionEngine:
    def __init__(self, database_path="change_tracking.db"):
        self.base_url = "https://oda.ft.dk/api/"
        self.db_path = database_path
        self.initialize_database()
        
    def initialize_database(self):
        """Initialize SQLite database for tracking changes"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_tracking (
                entity_name TEXT,
                record_id INTEGER,
                last_seen_update TEXT,
                first_detected TEXT,
                change_count INTEGER DEFAULT 1,
                latest_data TEXT,
                PRIMARY KEY (entity_name, record_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS change_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entity_name TEXT,
                record_id INTEGER,
                change_timestamp TEXT,
                detected_at TEXT,
                change_type TEXT,
                previous_data TEXT,
                new_data TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def detect_changes_since_timestamp(self, entity_name, since_timestamp, max_records=1000):
        """Detect all changes since a specific timestamp"""
        
        # Format timestamp for OData query
        if isinstance(since_timestamp, datetime):
            timestamp_str = since_timestamp.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            timestamp_str = since_timestamp
            
        params = {
            '$filter': f'opdateringsdato gt datetime\'{timestamp_str}\'',
            '$orderby': 'opdateringsdato desc',
            '$top': max_records
        }
        
        # Add relevant expansions based on entity type
        expansion_map = {
            'Sag': 'Sagsstatus,Sagstype,Sagskategori,Periode',
            'Afstemning': 'Sag,Afstemningstype,Stemme',
            'Aktör': 'Aktörtype,Periode',
            'Dokument': 'Dokumenttype,Dokumentstatus,Fil',
            'Møde': 'Mødetype,Mødestatus,Periode',
            'Stemme': 'Aktör,Afstemning,Stemmetype'
        }
        
        if entity_name in expansion_map:
            params['$expand'] = expansion_map[entity_name]
        
        url = f"{self.base_url}{entity_name}?" + urllib.parse.urlencode(params)
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error detecting changes for {entity_name}: {e}")
            return None
    
    def track_record_changes(self, entity_name, record_data):
        """Track changes to individual records"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        record_id = record_data.get('id')
        current_update_time = record_data.get('opdateringsdato', '')
        current_data_json = json.dumps(record_data, sort_keys=True)
        
        if not record_id or not current_update_time:
            conn.close()
            return None
        
        # Check if we've seen this record before
        cursor.execute('''
            SELECT last_seen_update, change_count, latest_data 
            FROM change_tracking 
            WHERE entity_name = ? AND record_id = ?
        ''', (entity_name, record_id))
        
        existing_record = cursor.fetchone()
        change_detected = False
        change_type = 'unknown'
        
        if existing_record:
            last_update, change_count, previous_data_json = existing_record
            
            # Check if this is actually a change
            if current_update_time != last_update:
                change_detected = True
                change_type = 'modification'
                
                # Update tracking record
                cursor.execute('''
                    UPDATE change_tracking 
                    SET last_seen_update = ?, change_count = ?, latest_data = ?
                    WHERE entity_name = ? AND record_id = ?
                ''', (current_update_time, change_count + 1, current_data_json, entity_name, record_id))
                
                # Log the change
                cursor.execute('''
                    INSERT INTO change_log 
                    (entity_name, record_id, change_timestamp, detected_at, change_type, previous_data, new_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (entity_name, record_id, current_update_time, datetime.now().isoformat(), 
                      change_type, previous_data_json, current_data_json))
        else:
            # New record
            change_detected = True
            change_type = 'creation'
            
            cursor.execute('''
                INSERT INTO change_tracking 
                (entity_name, record_id, last_seen_update, first_detected, latest_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (entity_name, record_id, current_update_time, datetime.now().isoformat(), current_data_json))
            
            # Log the creation
            cursor.execute('''
                INSERT INTO change_log 
                (entity_name, record_id, change_timestamp, detected_at, change_type, new_data)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (entity_name, record_id, current_update_time, datetime.now().isoformat(), 
                  change_type, current_data_json))
        
        conn.commit()
        conn.close()
        
        return {
            'change_detected': change_detected,
            'change_type': change_type,
            'record_id': record_id,
            'update_timestamp': current_update_time
        }
    
    def analyze_change_patterns(self, entity_name, days_back=7):
        """Analyze change patterns from tracked data"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get changes from the last N days
        cutoff_date = datetime.now() - timedelta(days=days_back)
        
        cursor.execute('''
            SELECT change_timestamp, change_type, COUNT(*) as change_count
            FROM change_log 
            WHERE entity_name = ? AND detected_at > ?
            GROUP BY DATE(change_timestamp), change_type
            ORDER BY change_timestamp DESC
        ''', (entity_name, cutoff_date.isoformat()))
        
        daily_patterns = cursor.fetchall()
        
        # Get hourly distribution
        cursor.execute('''
            SELECT strftime('%H', change_timestamp) as hour, COUNT(*) as count
            FROM change_log 
            WHERE entity_name = ? AND detected_at > ?
            GROUP BY hour
            ORDER BY hour
        ''', (entity_name, cutoff_date.isoformat()))
        
        hourly_distribution = cursor.fetchall()
        
        # Get most frequently changed records
        cursor.execute('''
            SELECT record_id, change_count 
            FROM change_tracking 
            WHERE entity_name = ? AND change_count > 1
            ORDER BY change_count DESC
            LIMIT 10
        ''', (entity_name,))
        
        frequently_changed = cursor.fetchall()
        
        conn.close()
        
        pattern_analysis = {
            'entity_name': entity_name,
            'analysis_period_days': days_back,
            'daily_patterns': [
                {'date': row[0], 'change_type': row[1], 'count': row[2]} 
                for row in daily_patterns
            ],
            'hourly_distribution': [
                {'hour': int(row[0]), 'count': row[1]} 
                for row in hourly_distribution
            ],
            'frequently_changed_records': [
                {'record_id': row[0], 'change_count': row[1]} 
                for row in frequently_changed
            ]
        }
        
        return pattern_analysis
```

### Advanced Change Analysis

```python
class AdvancedChangeAnalyzer(ChangeDetectionEngine):
    
    def detect_field_level_changes(self, entity_name, record_id):
        """Analyze what specific fields changed in a record"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get the last two versions of this record
        cursor.execute('''
            SELECT previous_data, new_data, change_timestamp
            FROM change_log 
            WHERE entity_name = ? AND record_id = ? AND change_type = 'modification'
            ORDER BY detected_at DESC
            LIMIT 1
        ''', (entity_name, record_id))
        
        latest_change = cursor.fetchone()
        conn.close()
        
        if not latest_change:
            return None
        
        previous_data_str, new_data_str, change_timestamp = latest_change
        
        try:
            previous_data = json.loads(previous_data_str)
            new_data = json.loads(new_data_str)
        except json.JSONDecodeError:
            return None
        
        field_changes = {
            'record_id': record_id,
            'entity_name': entity_name,
            'change_timestamp': change_timestamp,
            'changed_fields': [],
            'added_fields': [],
            'removed_fields': []
        }
        
        # Compare all fields
        all_fields = set(previous_data.keys()) | set(new_data.keys())
        
        for field in all_fields:
            if field in previous_data and field in new_data:
                if previous_data[field] != new_data[field]:
                    field_changes['changed_fields'].append({
                        'field_name': field,
                        'previous_value': previous_data[field],
                        'new_value': new_data[field]
                    })
            elif field in new_data:
                field_changes['added_fields'].append({
                    'field_name': field,
                    'new_value': new_data[field]
                })
            elif field in previous_data:
                field_changes['removed_fields'].append({
                    'field_name': field,
                    'previous_value': previous_data[field]
                })
        
        return field_changes
    
    def identify_batch_updates(self, entity_name, time_window_minutes=5):
        """Identify batch updates (multiple records updated simultaneously)"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get recent changes grouped by timestamp
        cursor.execute('''
            SELECT change_timestamp, COUNT(*) as record_count, GROUP_CONCAT(record_id) as record_ids
            FROM change_log 
            WHERE entity_name = ? AND detected_at > datetime('now', '-1 day')
            GROUP BY change_timestamp
            HAVING record_count > 1
            ORDER BY record_count DESC
        ''', (entity_name,))
        
        batch_updates = []
        
        for row in cursor.fetchall():
            timestamp, record_count, record_ids_str = row
            
            batch_info = {
                'timestamp': timestamp,
                'affected_records': record_count,
                'record_ids': [int(id_str) for id_str in record_ids_str.split(',')],
                'batch_type': 'simultaneous_update'
            }
            
            # Analyze batch characteristics
            if record_count > 100:
                batch_info['significance'] = 'major_batch_operation'
            elif record_count > 20:
                batch_info['significance'] = 'significant_batch_update'
            else:
                batch_info['significance'] = 'minor_batch_update'
            
            batch_updates.append(batch_info)
        
        conn.close()
        
        return {
            'entity_name': entity_name,
            'batch_updates_detected': len(batch_updates),
            'batches': batch_updates
        }
    
    def track_status_transitions(self, case_id):
        """Track status transitions for a specific case"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get all changes for this case
        cursor.execute('''
            SELECT change_timestamp, new_data
            FROM change_log 
            WHERE entity_name = 'Sag' AND record_id = ?
            ORDER BY change_timestamp ASC
        ''', (case_id,))
        
        changes = cursor.fetchall()
        conn.close()
        
        status_transitions = []
        previous_status = None
        
        for timestamp, data_json in changes:
            try:
                data = json.loads(data_json)
                
                # Extract status information (could be direct field or nested)
                current_status = None
                
                if 'statusid' in data:
                    current_status = data['statusid']
                elif 'Sagsstatus' in data and data['Sagsstatus']:
                    current_status = data['Sagsstatus'].get('status', 'Unknown')
                
                if current_status and current_status != previous_status:
                    status_transitions.append({
                        'timestamp': timestamp,
                        'from_status': previous_status,
                        'to_status': current_status,
                        'transition_type': 'status_change'
                    })
                    previous_status = current_status
                    
            except json.JSONDecodeError:
                continue
        
        return {
            'case_id': case_id,
            'total_transitions': len(status_transitions),
            'transitions': status_transitions
        }
    
    def detect_anomalous_update_patterns(self, entity_name):
        """Detect unusual update patterns that might indicate issues"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        anomaly_analysis = {
            'entity_name': entity_name,
            'analysis_timestamp': datetime.now().isoformat(),
            'anomalies_detected': [],
            'normal_patterns': {},
            'recommendations': []
        }
        
        # Check for records with unusually high change frequency
        cursor.execute('''
            SELECT record_id, change_count, first_detected
            FROM change_tracking 
            WHERE entity_name = ? AND change_count > 10
            ORDER BY change_count DESC
        ''', (entity_name,))
        
        high_change_records = cursor.fetchall()
        
        for record_id, change_count, first_detected in high_change_records:
            days_tracked = (datetime.now() - datetime.fromisoformat(first_detected)).days
            changes_per_day = change_count / max(1, days_tracked)
            
            if changes_per_day > 2:  # More than 2 changes per day
                anomaly_analysis['anomalies_detected'].append({
                    'type': 'high_frequency_changes',
                    'record_id': record_id,
                    'change_count': change_count,
                    'changes_per_day': changes_per_day,
                    'severity': 'high' if changes_per_day > 5 else 'medium'
                })
        
        # Check for unusual time patterns
        cursor.execute('''
            SELECT strftime('%H', change_timestamp) as hour, COUNT(*) as count
            FROM change_log 
            WHERE entity_name = ? AND detected_at > datetime('now', '-7 days')
            GROUP BY hour
        ''', (entity_name,))
        
        hourly_counts = dict(cursor.fetchall())
        
        # Identify unusual hours (outside normal business hours with significant activity)
        unusual_hours = []
        for hour_str, count in hourly_counts.items():
            hour = int(hour_str)
            # Consider 22:00 - 06:00 as unusual hours for parliamentary activity
            if (hour >= 22 or hour <= 6) and count > 5:
                unusual_hours.append({
                    'hour': hour,
                    'change_count': count
                })
        
        if unusual_hours:
            anomaly_analysis['anomalies_detected'].append({
                'type': 'unusual_time_pattern',
                'unusual_hours': unusual_hours,
                'severity': 'medium'
            })
        
        # Generate recommendations
        if len(anomaly_analysis['anomalies_detected']) > 0:
            anomaly_analysis['recommendations'].append(
                "Review high-frequency change records for data quality issues"
            )
            
            if unusual_hours:
                anomaly_analysis['recommendations'].append(
                    "Investigate off-hours activity patterns for automated processes"
                )
        
        conn.close()
        
        return anomaly_analysis
```

## Real-Time Change Streaming

### Change Event Stream

```python
import asyncio
import json
from datetime import datetime

class ChangeEventStream:
    
    def __init__(self):
        self.change_detector = AdvancedChangeAnalyzer()
        self.subscribers = []
        self.stream_active = False
        
    def subscribe(self, callback_function, entity_filter=None, change_type_filter=None):
        """Subscribe to change events"""
        subscriber = {
            'callback': callback_function,
            'entity_filter': entity_filter,
            'change_type_filter': change_type_filter,
            'subscription_id': len(self.subscribers)
        }
        
        self.subscribers.append(subscriber)
        return subscriber['subscription_id']
    
    def unsubscribe(self, subscription_id):
        """Remove a subscriber"""
        self.subscribers = [s for s in self.subscribers if s['subscription_id'] != subscription_id]
    
    async def start_change_stream(self, entities_to_monitor, poll_interval_seconds=300):
        """Start streaming change events"""
        
        self.stream_active = True
        last_check_times = {entity: datetime.now() for entity in entities_to_monitor}
        
        while self.stream_active:
            try:
                for entity_name in entities_to_monitor:
                    # Check for changes since last check
                    since_time = last_check_times[entity_name]
                    changes_data = self.change_detector.detect_changes_since_timestamp(
                        entity_name, since_time
                    )
                    
                    if changes_data and changes_data.get('value'):
                        changes = changes_data['value']
                        
                        # Process each change
                        for change_record in changes:
                            change_tracking = self.change_detector.track_record_changes(
                                entity_name, change_record
                            )
                            
                            if change_tracking and change_tracking['change_detected']:
                                # Create change event
                                change_event = {
                                    'entity_name': entity_name,
                                    'record_id': change_tracking['record_id'],
                                    'change_type': change_tracking['change_type'],
                                    'timestamp': change_tracking['update_timestamp'],
                                    'detected_at': datetime.now().isoformat(),
                                    'record_data': change_record
                                }
                                
                                # Notify subscribers
                                await self.notify_subscribers(change_event)
                        
                        # Update last check time
                        if changes:
                            latest_update = max(
                                datetime.fromisoformat(change['opdateringsdato'].replace('T', ' ').replace('Z', ''))
                                for change in changes
                                if 'opdateringsdato' in change
                            )
                            last_check_times[entity_name] = latest_update
                
                # Wait before next poll
                await asyncio.sleep(poll_interval_seconds)
                
            except Exception as e:
                print(f"Error in change stream: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def notify_subscribers(self, change_event):
        """Notify all matching subscribers of a change event"""
        
        for subscriber in self.subscribers:
            try:
                # Apply filters
                if subscriber['entity_filter'] and change_event['entity_name'] not in subscriber['entity_filter']:
                    continue
                    
                if subscriber['change_type_filter'] and change_event['change_type'] not in subscriber['change_type_filter']:
                    continue
                
                # Call subscriber callback
                if asyncio.iscoroutinefunction(subscriber['callback']):
                    await subscriber['callback'](change_event)
                else:
                    subscriber['callback'](change_event)
                    
            except Exception as e:
                print(f"Error notifying subscriber: {e}")
    
    def stop_stream(self):
        """Stop the change event stream"""
        self.stream_active = False
```

## Practical Applications

### Legislative Monitor

```python
class LegislativeChangeMonitor:
    
    def __init__(self):
        self.change_stream = ChangeEventStream()
        self.setup_monitoring()
        
    def setup_monitoring(self):
        """Setup legislative change monitoring"""
        
        # Subscribe to case changes
        self.change_stream.subscribe(
            callback_function=self.handle_case_changes,
            entity_filter=['Sag'],
            change_type_filter=['creation', 'modification']
        )
        
        # Subscribe to voting changes
        self.change_stream.subscribe(
            callback_function=self.handle_voting_changes,
            entity_filter=['Afstemning', 'Stemme']
        )
        
    async def handle_case_changes(self, change_event):
        """Handle changes to legislative cases"""
        
        case_data = change_event['record_data']
        case_title = case_data.get('titel', 'Unknown')
        
        # Analyze significance
        significance_keywords = ['lovforslag', 'beslutning', 'vedtaget', 'forkastet']
        is_significant = any(keyword in case_title.lower() for keyword in significance_keywords)
        
        if is_significant:
            print(f"\n🏛️ SIGNIFICANT LEGISLATIVE CHANGE")
            print(f"Case ID: {change_event['record_id']}")
            print(f"Title: {case_title}")
            print(f"Change Type: {change_event['change_type']}")
            print(f"Timestamp: {change_event['timestamp']}")
            
            # Could trigger alerts, notifications, etc.
            
    async def handle_voting_changes(self, change_event):
        """Handle changes to voting records"""
        
        print(f"\n🗳️ VOTING ACTIVITY UPDATE")
        print(f"Entity: {change_event['entity_name']}")
        print(f"Record ID: {change_event['record_id']}")
        print(f"Change: {change_event['change_type']}")
        print(f"Time: {change_event['timestamp']}")
    
    async def start_monitoring(self):
        """Start the monitoring system"""
        
        entities_to_monitor = ['Sag', 'Afstemning', 'Stemme', 'Dokument']
        
        print("Starting legislative change monitoring...")
        await self.change_stream.start_change_stream(
            entities_to_monitor, 
            poll_interval_seconds=300  # Check every 5 minutes
        )
```

### Research Change Tracker

```python
class ResearchChangeTracker:
    
    def __init__(self, research_keywords, output_file="research_changes.json"):
        self.keywords = research_keywords
        self.output_file = output_file
        self.change_detector = AdvancedChangeAnalyzer()
        self.tracked_changes = []
        
    def check_research_relevance(self, record_data):
        """Check if a record is relevant to research keywords"""
        
        searchable_text = ""
        
        # Collect searchable text from record
        if 'titel' in record_data:
            searchable_text += record_data['titel'].lower() + " "
        if 'beskrivelse' in record_data:
            searchable_text += record_data['beskrivelse'].lower() + " "
        if 'konklusion' in record_data:
            searchable_text += record_data['konklusion'].lower() + " "
        
        # Check for keyword matches
        matched_keywords = []
        for keyword in self.keywords:
            if keyword.lower() in searchable_text:
                matched_keywords.append(keyword)
        
        return matched_keywords
    
    def track_research_changes(self, entity_names, hours_back=24):
        """Track changes relevant to research over specified period"""
        
        research_changes = []
        
        for entity_name in entity_names:
            since_time = datetime.now() - timedelta(hours=hours_back)
            changes_data = self.change_detector.detect_changes_since_timestamp(
                entity_name, since_time
            )
            
            if changes_data and changes_data.get('value'):
                for record in changes_data['value']:
                    matched_keywords = self.check_research_relevance(record)
                    
                    if matched_keywords:
                        research_change = {
                            'entity_name': entity_name,
                            'record_id': record.get('id'),
                            'matched_keywords': matched_keywords,
                            'title': record.get('titel', record.get('navn', 'Unknown')),
                            'update_timestamp': record.get('opdateringsdato'),
                            'detected_at': datetime.now().isoformat(),
                            'record_summary': {
                                'id': record.get('id'),
                                'title': record.get('titel', record.get('navn', 'Unknown')),
                                'status': record.get('status', 'Unknown')
                            }
                        }
                        
                        research_changes.append(research_change)
        
        # Save to file
        self.save_research_changes(research_changes)
        
        return research_changes
    
    def save_research_changes(self, changes):
        """Save research changes to file"""
        
        try:
            # Load existing data
            try:
                with open(self.output_file, 'r') as f:
                    existing_data = json.load(f)
            except FileNotFoundError:
                existing_data = []
            
            # Add new changes
            existing_data.extend(changes)
            
            # Save updated data
            with open(self.output_file, 'w') as f:
                json.dump(existing_data, f, indent=2, ensure_ascii=False)
                
            print(f"Saved {len(changes)} research-relevant changes to {self.output_file}")
            
        except Exception as e:
            print(f"Error saving research changes: {e}")
```

This comprehensive change detection system using `opdateringsdato` provides the foundation for building sophisticated real-time monitoring applications that can track parliamentary activity with exceptional precision and timeliness.